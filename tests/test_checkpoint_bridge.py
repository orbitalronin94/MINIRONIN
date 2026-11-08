import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from checkpoint_bridge import inspect_checkpoint, read_checkpoint


def test_inspect_reports_hash_config_and_tensor_shapes(tmp_path):
    checkpoint_path = tmp_path / "checkpoint.pt"
    torch.save({
        "model_state_dict": {
            "weight": torch.tensor([[1.0, 2.0], [3.0, 4.0]]),
            "counter": torch.tensor([1, 2], dtype=torch.long),
        },
        "model_config": {"d_model": 2, "n_layers": 1},
        "completed_steps": 123,
        "parameter_count": 6,
        "active_vocabulary": 257,
    }, checkpoint_path)

    report = inspect_checkpoint(checkpoint_path)
    assert len(report["sha256"]) == 64
    assert report["completed_steps"] == 123
    assert report["parameter_count_observed"] == 6
    assert report["tensor_inventory"]["weight"]["shape"] == [2, 2]
    assert report["tensor_inventory"]["weight"]["finite"] is True


def test_checkpoint_loader_rejects_missing_model_state(tmp_path):
    checkpoint_path = tmp_path / "bad.pt"
    torch.save({"model_config": {}}, checkpoint_path)
    try:
        read_checkpoint(checkpoint_path)
    except ValueError as exc:
        assert "model_state_dict" in str(exc)
    else:
        raise AssertionError("expected invalid checkpoint to be rejected")
