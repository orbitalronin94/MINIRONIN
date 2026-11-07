"""Configuration for the first MINIRONIN ~10M parameter baseline."""
from dataclasses import asdict, dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class ModelConfig:
    vocab_size: int = 23_000
    context_length: int = 512
    n_layers: int = 6
    d_model: int = 256
    n_heads: int = 8
    d_ff: int = 768
    dropout: float = 0.0
    layer_norm_eps: float = 1e-5

    def validate(self) -> None:
        if self.d_model % self.n_heads:
            raise ValueError("d_model must be divisible by n_heads")
        if min(self.vocab_size, self.context_length, self.n_layers,
               self.d_model, self.n_heads, self.d_ff) <= 0:
            raise ValueError("model dimensions must be positive")
        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("dropout must be in [0, 1)")

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2) + "\\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "ModelConfig":
        config = cls(**json.loads(Path(path).read_text(encoding="utf-8")))
        config.validate()
        return config
