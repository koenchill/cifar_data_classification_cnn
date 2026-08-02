"""Inference export, governed bundles, and integrity verification."""

from cifar_cnn.inference.bundle import (
    BundleIntegrityError,
    BundleMetadata,
    load_bundle_torch_model,
    pack_bundle,
    read_current_pointer,
    rollback_bundle,
    set_current_pointer,
    verify_bundle,
)
from cifar_cnn.inference.onnx_export import (
    OnnxExportSpec,
    ParityReport,
    check_onnx_parity,
    export_onnx,
)
from cifar_cnn.inference.preprocess import get_inference_transform, pil_to_batch_tensor

__all__ = [
    "BundleIntegrityError",
    "BundleMetadata",
    "OnnxExportSpec",
    "ParityReport",
    "check_onnx_parity",
    "export_onnx",
    "get_inference_transform",
    "load_bundle_torch_model",
    "pack_bundle",
    "pil_to_batch_tensor",
    "read_current_pointer",
    "rollback_bundle",
    "set_current_pointer",
    "verify_bundle",
]
