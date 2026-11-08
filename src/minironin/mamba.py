"""Mamba-style selective state-space language model for MINIRONIN."""
from __future__ import annotations
import math
import torch
from torch import nn
from torch.nn import functional as F


class MambaBlock(nn.Module):
    def __init__(self, d_model: int = 512, d_state: int = 16, d_conv: int = 4, expand: int = 2):
        super().__init__()
        self.d_model = d_model
        self.d_inner = d_model * expand
        self.d_state = d_state
        self.dt_rank = max(1, math.ceil(d_model / 16))
        self.norm = nn.LayerNorm(d_model)
        self.in_proj = nn.Linear(d_model, 2 * self.d_inner, bias=False)
        self.conv1d = nn.Conv1d(self.d_inner, self.d_inner, kernel_size=d_conv,
                                groups=self.d_inner, padding=d_conv - 1, bias=True)
        self.x_proj = nn.Linear(self.d_inner, self.dt_rank + 2 * d_state, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, self.d_inner, bias=True)
        self.A_log = nn.Parameter(torch.log(torch.arange(1, d_state + 1, dtype=torch.float32)
                                            .view(1, d_state).repeat(self.d_inner, 1)))
        self.D = nn.Parameter(torch.ones(self.d_inner))
        self.out_proj = nn.Linear(self.d_inner, d_model, bias=False)
        nn.init.normal_(self.in_proj.weight, std=0.02)
        nn.init.normal_(self.x_proj.weight, std=0.02)
        nn.init.normal_(self.dt_proj.weight, std=0.02)
        nn.init.constant_(self.dt_proj.bias, -4.0)
        nn.init.normal_(self.out_proj.weight, std=0.02 / math.sqrt(22))

    def forward(self, residual: torch.Tensor) -> torch.Tensor:
        x = self.norm(residual)
        xz = self.in_proj(x)
        x_branch, z = xz.chunk(2, dim=-1)
        # Left-padded depthwise convolution, cropped to preserve causality.
        conv = self.conv1d(x_branch.transpose(1, 2))[..., :x_branch.shape[1]]
        x_branch = F.silu(conv.transpose(1, 2))
        params = self.x_proj(x_branch)
        dt_raw, B, C = torch.split(params, [self.dt_rank, self.d_state, self.d_state], dim=-1)
        dt = F.softplus(self.dt_proj(dt_raw)).clamp(max=1.0)
        A = -torch.exp(self.A_log).to(dtype=x_branch.dtype)
        decay = torch.exp(dt.unsqueeze(-1) * A.view(1, 1, self.d_inner, self.d_state))
        # Parallel affine scan for the diagonal selective state recurrence.
        prefix = torch.cumprod(decay, dim=1).clamp_min(1e-8)
        drive = dt.unsqueeze(-1) * B.unsqueeze(2) * x_branch.unsqueeze(-1)
        state = prefix * torch.cumsum(drive / prefix, dim=1)
        y = (state * C.unsqueeze(2)).sum(dim=-1) + self.D.view(1, 1, -1) * x_branch
        y = y * F.silu(z)
        return residual + self.out_proj(y)


class MambaRoninLM(nn.Module):
    """Decoder-only Mamba LM; tied token/output embeddings and byte vocabulary."""
    def __init__(self, vocab_size: int = 23000, context_length: int = 512,
                 d_model: int = 512, n_layers: int = 22, d_state: int = 16,
                 d_conv: int = 4, expand: int = 2):
        super().__init__()
        self.config = {
            "architecture": "mamba-selective-scan-v1",
            "vocab_size": vocab_size, "context_length": context_length,
            "d_model": d_model, "n_layers": n_layers, "d_state": d_state,
            "d_conv": d_conv, "expand": expand,
        }
        self.context_length = context_length
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.blocks = nn.ModuleList(MambaBlock(d_model, d_state, d_conv, expand)
                                    for _ in range(n_layers))
        self.final_norm = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
        self.lm_head.weight = self.token_embedding.weight
        nn.init.normal_(self.token_embedding.weight, std=0.02)

    def forward(self, input_ids: torch.Tensor, labels: torch.Tensor | None = None,
                vocab_limit: int | None = None):
        if input_ids.ndim != 2:
            raise ValueError("input_ids must have shape [batch, sequence]")
        if input_ids.shape[1] > self.context_length:
            raise ValueError("sequence exceeds configured context")
        x = self.token_embedding(input_ids)
        for block in self.blocks:
            x = block(x)
        x = self.final_norm(x)
        weight = self.lm_head.weight if vocab_limit is None else self.lm_head.weight[:vocab_limit]
        logits = F.linear(x, weight)
        loss = None
        if labels is not None:
            if labels.shape != input_ids.shape:
                raise ValueError("labels must match input_ids")
            loss = F.cross_entropy(logits[:, :-1].contiguous().view(-1, logits.shape[-1]),
                                   labels[:, 1:].contiguous().view(-1))
        return logits, loss

    def parameter_count(self) -> int:
        return sum(p.numel() for p in self.parameters())
