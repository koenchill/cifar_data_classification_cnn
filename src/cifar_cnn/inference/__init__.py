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

__all__ = [
    "BundleIntegrityError",
    "BundleMetadata",
    "OnnxExportSpec",
    "ParityReport",
    "check_onnx_parity",
    "export_onnx",
    "load_bundle_torch_model",
    "pack_bundle",
    "read_current_pointer",
    "rollback_bundle",
    "set_current_pointer",
    "verify_bundle",
]
