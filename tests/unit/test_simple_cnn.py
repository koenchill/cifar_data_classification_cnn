from __future__ import annotations

import pickle
from pathlib import Path

import pytest
import torch
import yaml

from cifar_cnn.models.simple_cnn import (
    SimpleCNN,
    assert_compatible_input,
    count_parameters,
    describe_architecture,
    load_state_dict,
    save_state_dict,
)


def test_layer_constructors_match_guide() -> None:
    net = SimpleCNN()
    assert net.conv1.in_channels == 3 and net.conv1.out_channels == 32
    assert net.conv1.kernel_size == (3, 3) and net.conv1.padding == (1, 1)
    assert net.conv2.in_channels == 32 and net.conv2.out_channels == 64
    assert net.conv3.in_channels == 64 and net.conv3.out_channels == 64
    assert net.fc1.in_features == 64 * 4 * 4 and net.fc1.out_features == 64
    assert net.fc2.in_features == 64 and net.fc2.out_features == 10
    assert net.pool.kernel_size == 2 and net.pool.stride == 2


def test_forward_shape_logits() -> None:
    net = SimpleCNN()
    x = torch.randn(4, 3, 32, 32)
    y = net(x)
    assert y.shape == (4, 10)
    assert torch.isfinite(y).all()


def test_backward_gradients_finite() -> None:
    net = SimpleCNN()
    x = torch.randn(2, 3, 32, 32, requires_grad=True)
    loss = net(x).sum()
    loss.backward()
    assert x.grad is not None and torch.isfinite(x.grad).all()
    for p in net.parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all()


def test_parameter_count_documented() -> None:
    n = count_parameters(SimpleCNN())
    # Exact count for this architecture (no bias omissions): verify stability.
    assert n == 122_570
    summary = describe_architecture()
    assert summary["name"] == "SimpleCNN"
    assert "state_dict" in summary["trusted_artifact"]


def test_serialization_round_trip(tmp_path: Path) -> None:
    net = SimpleCNN()
    path = tmp_path / "cnn_model.pth"
    save_state_dict(net, path)
    restored = SimpleCNN()
    load_state_dict(restored, path)
    x = torch.randn(1, 3, 32, 32)
    with torch.no_grad():
        assert torch.allclose(net(x), restored(x))


def test_config_yaml_compatible_with_model() -> None:
    cfg = yaml.safe_load(Path("configs/model/simple_cnn.yaml").read_text(encoding="utf-8"))
    assert cfg["batch_norm"] is False
    assert cfg["dropout"] is False
    assert cfg["layers"]["fc1"]["in_features"] == 1024
    assert cfg["output"] == "logits"
    net = SimpleCNN()
    assert net.fc1.in_features == cfg["layers"]["fc1"]["in_features"]


def test_malformed_shape_fails_closed() -> None:
    with pytest.raises(ValueError, match="Expected input shape"):
        assert_compatible_input(torch.randn(2, 3, 28, 28))
    net = SimpleCNN()
    with pytest.raises(RuntimeError):
        net(torch.randn(2, 3, 28, 28))


def test_tampered_artifact_hash_fails_closed(tmp_path: Path) -> None:
    net = SimpleCNN()
    path = tmp_path / "cnn_model.pth"
    save_state_dict(net, path)
    with pytest.raises(ValueError, match="hash mismatch"):
        load_state_dict(SimpleCNN(), path, expected_sha256="0" * 64)
    # Unreadable / non-state_dict payload
    path.write_bytes(b"not-a-valid-torch-state-dict")
    with pytest.raises(
        (RuntimeError, OSError, ValueError, TypeError, EOFError, pickle.UnpicklingError)
    ):
        load_state_dict(SimpleCNN(), path)


def test_incompatible_state_dict_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "bad.pth"
    torch.save({"not_a_weight": torch.tensor([1.0])}, path)
    with pytest.raises(RuntimeError):
        load_state_dict(SimpleCNN(), path)
