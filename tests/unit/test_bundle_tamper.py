"""Phase 10: bundle hash/signature tamper and rollback."""

from __future__ import annotations

from pathlib import Path

import pytest

from cifar_cnn.inference.bundle import (
    BundleIntegrityError,
    load_bundle_torch_model,
    pack_bundle,
    read_current_pointer,
    rollback_bundle,
    set_current_pointer,
    verify_bundle,
)
from cifar_cnn.models.simple_cnn import SimpleCNN


def test_bundle_tamper_detected(tmp_path: Path) -> None:
    key = b"unit-test-hmac-key"
    model = SimpleCNN()
    bundle = pack_bundle(
        model,
        tmp_path / "v1",
        bundle_id="test",
        version="1.0.0",
        key=key,
    )
    assert verify_bundle(bundle, key=key)["ok"] is True

    # Tamper with weights
    pt = bundle / "model.pt"
    pt.write_bytes(pt.read_bytes() + b"\x00")
    with pytest.raises(BundleIntegrityError, match="Hash mismatch"):
        verify_bundle(bundle, key=key)


def test_bundle_tamper_signature_mismatch(tmp_path: Path) -> None:
    key = b"unit-test-hmac-key"
    bundle = pack_bundle(
        SimpleCNN(),
        tmp_path / "v1",
        bundle_id="test",
        version="1.0.0",
        key=key,
    )
    (bundle / "manifest.sig").write_text("00" * 32 + "\n", encoding="utf-8")
    with pytest.raises(BundleIntegrityError, match="signature mismatch"):
        verify_bundle(bundle, key=key)


def test_bundle_tamper_rollback_and_load(tmp_path: Path) -> None:
    key = b"unit-test-hmac-key"
    root = tmp_path / "bundles"
    v1 = pack_bundle(
        SimpleCNN(),
        root / "simple_cnn-1.0.0",
        bundle_id="simple_cnn",
        version="1.0.0",
        key=key,
    )
    v2 = pack_bundle(
        SimpleCNN(),
        root / "simple_cnn-1.0.1",
        bundle_id="simple_cnn",
        version="1.0.1",
        key=key,
    )
    set_current_pointer(root, v2.name)
    assert read_current_pointer(root) == v2.name
    rollback_bundle(root, v1.name, key=key)
    assert read_current_pointer(root) == v1.name
    model = load_bundle_torch_model(root / read_current_pointer(root), key=key)

    import torch

    with torch.no_grad():
        y = model(torch.randn(1, 3, 32, 32))
    assert y.shape == (1, 10)
