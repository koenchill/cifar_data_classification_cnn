"""Phase 10: ONNX export + dynamic-batch parity."""

from __future__ import annotations

from pathlib import Path

import torch

from cifar_cnn.inference.onnx_export import (
    OnnxExportSpec,
    check_onnx_parity,
    export_onnx,
)
from cifar_cnn.models.simple_cnn import SimpleCNN


def test_onnx_parity_dynamic_batch(tmp_path: Path) -> None:
    model = SimpleCNN()
    onnx_path = tmp_path / "simple.onnx"
    export_onnx(model, onnx_path, spec=OnnxExportSpec(opset=17, dynamic_batch=True))
    assert onnx_path.is_file() and onnx_path.stat().st_size > 0
    report = check_onnx_parity(model, onnx_path, batch_sizes=(1, 2, 4), tolerance=1e-4)
    assert report.passed, report.to_dict()
    assert 1 in report.batch_sizes and 4 in report.batch_sizes


def test_onnx_parity_matches_pytorch_logits(tmp_path: Path) -> None:
    model = SimpleCNN()
    path = tmp_path / "m.onnx"
    export_onnx(model, path)
    report = check_onnx_parity(model, path, batch_sizes=(1,), tolerance=1e-5)
    assert report.max_abs_diff <= 1e-5
    x = torch.randn(1, 3, 32, 32)
    with torch.no_grad():
        assert model(x).shape == (1, 10)
