"""Small decoder-only Transformer implemented for MINIRONIN.

Architecture is independently implemented using PyTorch primitives. The design
is GPT-like: learned positions, pre-LN blocks, causal self-attention, GELU MLP,
and tied token/output embeddings.
"""
import torch
from torch import nn
from torch.nn import functional as F

from .config import ModelConfig


class CausalSelfAttention(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.n_heads = config.n_heads
        self.head_dim = config.d_model // config.n_heads
        self.qkv = nn.Linear(config.d_model, 3 * config.d_model, bias=True)
        self.proj = nn.Linear(config.d_model, config.d_model, bias=True)
        self.attn_dropout = config.dropout
        self.resid_dropout = nn.Dropout(config.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, length, width = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        shape = (batch, length, self.n_heads, self.head_dim)
        q = q.view(shape).transpose(1, 2)
        k = k.view(shape).transpose(1, 2)
        v = v.view(shape).transpose(1, 2)
        y = F.scaled_dot_product_attention(
            q, k, v,
            attn_mask=None,
            dropout_p=self.attn_dropout if self.training else 0.0,
            is_causal=True,
        )
        y = y.transpose(1, 2).contiguous().view(batch, length, width)
        return self.resid_dropout(self.proj(y))

    def forward_cached(
        self, x: torch.Tensor, past_key_value: tuple[torch.Tensor, torch.Tensor] | None = None
    ) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        """Process new tokens and return the concatenated per-layer KV cache.

        All cached keys precede or include the current query positions, so
        non-causal SDPA is correct here; applying is_causal=True to a one-token
        query would use upper-left alignment and mask valid past keys.
        """
        batch, length, width = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        shape = (batch, length, self.n_heads, self.head_dim)
        q = q.view(shape).transpose(1, 2)
        k = k.view(shape).transpose(1, 2)
        v = v.view(shape).transpose(1, 2)
        if past_key_value is not None:
            past_k, past_v = past_key_value
            k = torch.cat((past_k, k), dim=-2)
            v = torch.cat((past_v, v), dim=-2)
        if past_key_value is None:
            # The initial prompt is a full sequence and must remain causal.
            attention_mask = None
            is_causal = True
        elif length == 1:
            # A single new token may attend to every cached key and itself.
            attention_mask = None
            is_causal = False
        else:
            # For multi-token chunks, allow cached keys plus only prior/current
            # tokens in this chunk (SDPA's is_causal=True is upper-left aligned).
            past_length = past_key_value[0].shape[-2]
            query_positions = past_length + torch.arange(length, device=x.device)
            key_positions = torch.arange(k.shape[-2], device=x.device)
            attention_mask = key_positions.unsqueeze(0) <= query_positions.unsqueeze(1)
            is_causal = False
        y = F.scaled_dot_product_attention(
            q, k, v, attn_mask=attention_mask,
            dropout_p=self.attn_dropout if self.training else 0.0,
            is_causal=is_causal,
        )
        y = y.transpose(1, 2).contiguous().view(batch, length, width)
        return self.resid_dropout(self.proj(y)), (k, v)


class MLP(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.fc_in = nn.Linear(config.d_model, config.d_ff, bias=True)
        self.fc_out = nn.Linear(config.d_ff, config.d_model, bias=True)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(self.fc_out(F.gelu(self.fc_in(x))))


class TransformerBlock(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.ln_1 = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
        self.attn = CausalSelfAttention(config)
        self.ln_2 = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
        self.mlp = MLP(config)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x

    def forward_cached(
        self, x: torch.Tensor,
        past_key_value: tuple[torch.Tensor, torch.Tensor] | None = None,
    ) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        attention, present = self.attn.forward_cached(self.ln_1(x), past_key_value)
        x = x + attention
        x = x + self.mlp(self.ln_2(x))
        return x, present


class MiniRoninLM(nn.Module):
    """Causal language model; labels are shifted internally for next-token loss."""

    def __init__(self, config: ModelConfig | None = None):
        super().__init__()
        self.config = config or ModelConfig()
        self.config.validate()
        self.token_embedding = nn.Embedding(self.config.vocab_size, self.config.d_model)
        self.position_embedding = nn.Embedding(self.config.context_length, self.config.d_model)
        self.embedding_dropout = nn.Dropout(self.config.dropout)
        self.blocks = nn.ModuleList(
            TransformerBlock(self.config) for _ in range(self.config.n_layers)
        )
        self.final_norm = nn.LayerNorm(
            self.config.d_model, eps=self.config.layer_norm_eps
        )
        self.lm_head = nn.Linear(self.config.d_model, self.config.vocab_size, bias=False)
        self.lm_head.weight = self.token_embedding.weight
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            nn.init.ones_(module.weight)
            nn.init.zeros_(module.bias)

    def forward(
        self,
        input_ids: torch.Tensor,
        labels: torch.Tensor | None = None,
        vocab_limit: int | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        if input_ids.ndim != 2:
            raise ValueError("input_ids must have shape [batch, sequence]")
        batch, length = input_ids.shape
        if length > self.config.context_length:
            raise ValueError(
                f"sequence length {length} exceeds context {self.config.context_length}"
            )
        positions = torch.arange(length, device=input_ids.device).unsqueeze(0)
        x = self.token_embedding(input_ids) + self.position_embedding(positions)
        x = self.embedding_dropout(x)
        for block in self.blocks:
            x = block(x)
        if vocab_limit is not None and not 1 <= vocab_limit <= self.config.vocab_size:
            raise ValueError("vocab_limit must be between 1 and configured vocab_size")
        hidden = self.final_norm(x)
        output_weight = (
            self.lm_head.weight if vocab_limit is None
            else self.lm_head.weight[:vocab_limit]
        )
        logits = F.linear(hidden, output_weight)
        loss = None
        if labels is not None:
            if labels.shape != input_ids.shape:
                raise ValueError("labels must have the same shape as input_ids")
            if vocab_limit is not None and int(labels.max()) >= vocab_limit:
                raise ValueError("labels contain token IDs outside vocab_limit")
            loss = F.cross_entropy(
                logits[:, :-1, :].contiguous().view(-1, logits.size(-1)),
                labels[:, 1:].contiguous().view(-1),
            )
        return logits, loss

    def forward_cached(
        self,
        input_ids: torch.Tensor,
        past_key_values: tuple[tuple[torch.Tensor, torch.Tensor], ...] | None = None,
    ) -> tuple[torch.Tensor, tuple[tuple[torch.Tensor, torch.Tensor], ...]]:
        """Incremental inference with learned absolute positions and per-layer KV cache.

        The caller must reset the cache when its sliding context window advances.
        This preserves the exact positional semantics of the uncached forward path.
        """
        if input_ids.ndim != 2:
            raise ValueError("input_ids must have shape [batch, sequence]")
        batch, length = input_ids.shape
        past_length = 0 if past_key_values is None else past_key_values[0][0].shape[-2]
        if past_key_values is not None and len(past_key_values) != len(self.blocks):
            raise ValueError("KV cache layer count does not match model")
        if past_length + length > self.config.context_length:
            raise ValueError("KV cache exceeds context; reset it and pass the sliding window")
        positions = torch.arange(past_length, past_length + length, device=input_ids.device).unsqueeze(0)
        x = self.token_embedding(input_ids) + self.position_embedding(positions)
        x = self.embedding_dropout(x)
        presents = []
        for index, block in enumerate(self.blocks):
            past = None if past_key_values is None else past_key_values[index]
            x, present = block.forward_cached(x, past)
            presents.append(present)
        logits = F.linear(self.final_norm(x), self.lm_head.weight[:257])
        return logits, tuple(presents)

    def parameter_count(self, trainable_only: bool = True) -> int:
        return sum(
            p.numel() for p in self.parameters()
            if not trainable_only or p.requires_grad
        )
