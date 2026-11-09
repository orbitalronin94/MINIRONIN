"""Decoder-only Transformer for MAXIRONIN.

The vocabulary/output matrix is tied. All model parameters are trainable.
Gradient checkpointing keeps the 37-layer CPU experiment within runner memory.
"""
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint

from .config import MaxRoninConfig


class CausalSelfAttention(nn.Module):
    def __init__(self, config: MaxRoninConfig):
        super().__init__()
        self.n_heads = config.n_heads
        self.head_dim = config.d_model // config.n_heads
        self.qkv = nn.Linear(config.d_model, 3 * config.d_model, bias=True)
        self.proj = nn.Linear(config.d_model, config.d_model, bias=True)
        self.dropout = config.dropout

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, length, width = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        shape = (batch, length, self.n_heads, self.head_dim)
        q = q.view(shape).transpose(1, 2)
        k = k.view(shape).transpose(1, 2)
        v = v.view(shape).transpose(1, 2)
        y = F.scaled_dot_product_attention(
            q, k, v, attn_mask=None,
            dropout_p=self.dropout if self.training else 0.0,
            is_causal=True,
        )
        y = y.transpose(1, 2).contiguous().view(batch, length, width)
        return self.proj(y)


class MLP(nn.Module):
    def __init__(self, config: MaxRoninConfig):
        super().__init__()
        self.fc_in = nn.Linear(config.d_model, config.d_ff, bias=True)
        self.fc_out = nn.Linear(config.d_ff, config.d_model, bias=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc_out(F.gelu(self.fc_in(x)))


class TransformerBlock(nn.Module):
    def __init__(self, config: MaxRoninConfig):
        super().__init__()
        self.ln_1 = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
        self.attn = CausalSelfAttention(config)
        self.ln_2 = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
        self.mlp = MLP(config)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x


class MaxRoninLM(nn.Module):
    def __init__(self, config: MaxRoninConfig | None = None):
        super().__init__()
        self.config = config or MaxRoninConfig()
        self.config.validate()
        self.token_embedding = nn.Embedding(self.config.vocab_size, self.config.d_model)
        self.position_embedding = nn.Embedding(self.config.context_length, self.config.d_model)
        self.blocks = nn.ModuleList(
            TransformerBlock(self.config) for _ in range(self.config.n_layers)
        )
        self.final_norm = nn.LayerNorm(self.config.d_model, eps=self.config.layer_norm_eps)
        self.lm_head = nn.Linear(self.config.d_model, self.config.vocab_size, bias=False)
        if self.config.tie_embeddings:
            self.lm_head.weight = self.token_embedding.weight
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(module: nn.Module) -> None:
        if isinstance(module, (nn.Linear, nn.Embedding)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if isinstance(module, nn.Linear) and module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.LayerNorm):
            nn.init.ones_(module.weight)
            nn.init.zeros_(module.bias)

    def parameter_count(self, trainable_only: bool = True) -> int:
        return sum(
            p.numel() for p in self.parameters()
            if not trainable_only or p.requires_grad
        )

    def forward(self, input_ids: torch.Tensor,
                labels: torch.Tensor | None = None) -> tuple[torch.Tensor, torch.Tensor | None]:
        if input_ids.ndim != 2:
            raise ValueError("input_ids must have shape [batch, sequence]")
        _, length = input_ids.shape
        if length > self.config.context_length:
            raise ValueError("sequence exceeds configured context")
        positions = torch.arange(length, device=input_ids.device).unsqueeze(0)
        x = self.token_embedding(input_ids) + self.position_embedding(positions)
        for block in self.blocks:
            if self.training and self.config.gradient_checkpointing:
                x = checkpoint(block, x, use_reentrant=False)
            else:
                x = block(x)
        logits = F.linear(self.final_norm(x), self.lm_head.weight)
        loss = None
        if labels is not None:
            if labels.shape != input_ids.shape:
                raise ValueError("labels must match input_ids")
            loss = F.cross_entropy(
                logits[:, :-1, :].contiguous().view(-1, logits.size(-1)),
                labels[:, 1:].contiguous().view(-1),
            )
        return logits, loss
