"""ONNX export and PyTorch↔ONNX parity checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import onnx
import torch
import torch.nn as nn
from torch import Tensor

DEFAULT_OPSET = 17
INPUT_NAME = "input"
OUTPUT_NAME = "logits"


@dataclass(frozen=True)
class OnnxExportSpec:
    opset: int = DEFAULT_OPSET
    input_name: str = INPUT_NAME
    output_name: str = OUTPUT_NAME
    dynamic_batch: bool = True
    input_shape: tuple[int, int, int, int] = (1, 3, 32, 32)


@dataclass
class ParityReport:
    max_abs_diff: float
    mean_abs_diff: float
    passed: bool
    tolerance: float
    batch_sizes: list[int]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def export_onnx(
    model: nn.Module,
    path: str | Path,
    *,
    spec: OnnxExportSpec | None = None,
) -> Path:
    """Export model to ONNX with documented names and optional dynamic batch."""
    spec = spec or OnnxExportSpec()
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    model = model.eval().cpu()
    dummy = torch.randn(*spec.input_shape)
    dynamic_axes = None
    if spec.dynamic_batch:
        dynamic_axes = {
            spec.input_name: {0: "batch"},
            spec.output_name: {0: "batch"},
        }
    torch.onnx.export(
        model,
        (dummy,),
        str(out),
        input_names=[spec.input_name],
        output_names=[spec.output_name],
        dynamic_axes=dynamic_axes,
        opset_version=spec.opset,
        do_constant_folding=True,
        dynamo=False,
    )
    # Structural validate
    onnx_model = onnx.load(str(out))
    onnx.checker.check_model(onnx_model)
    return out


def _ort_session(path: Path) -> Any:
    import onnxruntime as ort

    return ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])


def onnx_infer(path: str | Path, batch: Tensor, *, input_name: str = INPUT_NAME) -> Tensor:
    session = _ort_session(Path(path))
    arr = batch.detach().cpu().numpy().astype(np.float32)
    outs = session.run(None, {input_name: arr})
    return torch.from_numpy(outs[0])


@torch.no_grad()
def check_onnx_parity(
    model: nn.Module,
    onnx_path: str | Path,
    *,
    batch_sizes: tuple[int, ...] = (1, 4),
    tolerance: float = 1e-4,
    input_name: str = INPUT_NAME,
) -> ParityReport:
    model = model.eval().cpu()
    max_diff = 0.0
    sum_diff = 0.0
    n = 0
    notes: list[str] = [
        f"opset documented as {DEFAULT_OPSET}",
        f"input={input_name} output={OUTPUT_NAME}",
        "dynamic batch axis enabled on export",
    ]
    for bs in batch_sizes:
        x = torch.randn(bs, 3, 32, 32)
        pt = model(x)
        ort_out = onnx_infer(onnx_path, x, input_name=input_name)
        diff = (pt - ort_out).abs()
        max_diff = max(max_diff, float(diff.max().item()))
        sum_diff += float(diff.sum().item())
        n += int(diff.numel())
    mean_diff = sum_diff / max(n, 1)
    passed = max_diff <= tolerance
    if not passed:
        notes.append(f"parity failed: max_abs_diff={max_diff} > {tolerance}")
    return ParityReport(
        max_abs_diff=max_diff,
        mean_abs_diff=mean_diff,
        passed=passed,
        tolerance=tolerance,
        batch_sizes=list(batch_sizes),
        notes=notes,
    )
