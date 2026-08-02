"""Governed model bundle: pack, hash, HMAC-sign, verify, rollback pointer."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import shutil
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn

from cifar_cnn.data.constants import CIFAR10_CLASSES, NORMALIZE_MEAN, NORMALIZE_STD
from cifar_cnn.inference.onnx_export import (
    OnnxExportSpec,
    check_onnx_parity,
    export_onnx,
)
from cifar_cnn.models.simple_cnn import SimpleCNN, save_state_dict

# Dev/CI HMAC key only — production must inject CIFAR_CNN_BUNDLE_HMAC_KEY.
_DEV_HMAC_KEY = b"cifar-cnn-dev-bundle-hmac-not-for-production"


class BundleIntegrityError(ValueError):
    """Raised when a bundle fails hash or signature verification."""


@dataclass
class BundleMetadata:
    bundle_id: str
    version: str
    model_name: str
    champion_id: str
    created_utc: str
    class_order: list[str] = field(default_factory=lambda: list(CIFAR10_CLASSES))
    normalization: dict[str, list[float]] = field(
        default_factory=lambda: {
            "mean": list(NORMALIZE_MEAN),
            "std": list(NORMALIZE_STD),
        }
    )
    input_constraints: dict[str, Any] = field(
        default_factory=lambda: {
            "shape": [None, 3, 32, 32],
            "dtype": "float32",
            "layout": "NCHW",
        }
    )
    onnx: dict[str, Any] = field(default_factory=dict)
    metrics_summary: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)
    identities: dict[str, str] = field(default_factory=dict)
    non_production: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def resolve_hmac_key(explicit: bytes | None = None) -> bytes:
    if explicit is not None:
        return explicit
    env = os.environ.get("CIFAR_CNN_BUNDLE_HMAC_KEY")
    if env:
        return env.encode("utf-8")
    return _DEV_HMAC_KEY


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def write_sbom_stub(path: Path, *, model_name: str, version: str) -> Path:
    """Minimal CycloneDX-like component list (not a full generator)."""
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat(),
            "component": {
                "type": "machine-learning-model",
                "name": model_name,
                "version": version,
            },
        },
        "components": [
            {"type": "library", "name": "torch", "version": torch.__version__},
            {"type": "library", "name": "onnx", "version": "1.17.0"},
            {"type": "library", "name": "onnxruntime", "version": "1.22.0"},
        ],
        "note": "Stub SBOM for Release B evidence; regenerate with full tooling in Release C+",
    }
    path.write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8")
    return path


def build_manifest(bundle_dir: Path, *, files: list[str]) -> dict[str, Any]:
    entries = []
    for rel in sorted(files):
        p = bundle_dir / rel
        entries.append({"path": rel, "sha256": sha256_file(p), "bytes": p.stat().st_size})
    return {
        "bundle_dir": bundle_dir.name,
        "files": entries,
        "algorithm": "sha256",
        "signature_alg": "HMAC-SHA256",
    }


def sign_envelope(envelope: dict[str, Any], *, key: bytes | None = None) -> str:
    digest = hmac.new(resolve_hmac_key(key), _canonical_json(envelope), hashlib.sha256)
    return digest.hexdigest()


def verify_bundle(
    bundle_dir: str | Path,
    *,
    key: bytes | None = None,
) -> dict[str, Any]:
    """Fail closed on missing signature, hash mismatch, or tamper."""
    root = Path(bundle_dir)
    manifest_path = root / "manifest.json"
    sig_path = root / "manifest.sig"
    if not manifest_path.is_file() or not sig_path.is_file():
        raise BundleIntegrityError("Bundle missing manifest.json or manifest.sig")
    envelope = json.loads(manifest_path.read_text(encoding="utf-8"))
    if "manifest" not in envelope:
        raise BundleIntegrityError("Invalid manifest envelope")
    expected_sig = sig_path.read_text(encoding="utf-8").strip()
    actual_sig = sign_envelope(envelope, key=key)
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise BundleIntegrityError("Bundle signature mismatch")
    for entry in envelope["manifest"].get("files", []):
        rel = entry["path"]
        path = root / rel
        if not path.is_file():
            raise BundleIntegrityError(f"Missing bundled file: {rel}")
        digest = sha256_file(path)
        if digest != entry["sha256"]:
            raise BundleIntegrityError(f"Hash mismatch for {rel}")
    return {
        "ok": True,
        "bundle": root.name,
        "files": len(envelope["manifest"].get("files", [])),
    }


def pack_bundle(
    model: nn.Module,
    bundle_dir: str | Path,
    *,
    bundle_id: str,
    version: str,
    model_name: str = "SimpleCNN",
    champion_id: str = "simple_cnn_baseline",
    metrics_summary: dict[str, Any] | None = None,
    identities: dict[str, str] | None = None,
    key: bytes | None = None,
    run_parity: bool = True,
) -> Path:
    """Create a versioned, hashed, HMAC-signed model bundle."""
    root = Path(bundle_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    pt_path = root / "model.pt"
    onnx_path = root / "model.onnx"
    save_state_dict(model, pt_path)
    spec = OnnxExportSpec()
    export_onnx(model, onnx_path, spec=spec)

    parity = None
    if run_parity:
        parity = check_onnx_parity(model, onnx_path)
        if not parity.passed:
            raise BundleIntegrityError(
                f"ONNX parity failed max_abs_diff={parity.max_abs_diff}"
            )

    meta = BundleMetadata(
        bundle_id=bundle_id,
        version=version,
        model_name=model_name,
        champion_id=champion_id,
        created_utc=datetime.now(UTC).isoformat(),
        onnx={
            "opset": spec.opset,
            "input_name": spec.input_name,
            "output_name": spec.output_name,
            "dynamic_batch": spec.dynamic_batch,
            "parity": parity.to_dict() if parity else None,
        },
        metrics_summary=metrics_summary or {},
        limitations=[
            "Educational CIFAR-10 domain only; non-production",
            "Softmax confidence is not proof of correctness",
            "HMAC signature uses CI/dev key unless CIFAR_CNN_BUNDLE_HMAC_KEY is set",
        ],
        identities=identities
        or {
            "training": "training",
            "eval": "eval",
            "release": "release",
            "model_owner": "koenchill",
        },
    )
    (root / "metadata.json").write_text(
        json.dumps(meta.to_dict(), indent=2) + "\n", encoding="utf-8"
    )
    (root / "classes.json").write_text(
        json.dumps({"classes": list(CIFAR10_CLASSES)}, indent=2) + "\n",
        encoding="utf-8",
    )
    # Named bom.json (not sbom*.json) so repo .gitignore does not drop it.
    write_sbom_stub(root / "bom.json", model_name=model_name, version=version)

    payload_files = [
        "model.pt",
        "model.onnx",
        "metadata.json",
        "classes.json",
        "bom.json",
    ]

    envelope = {"manifest": build_manifest(root, files=payload_files)}
    (root / "manifest.json").write_text(
        json.dumps(envelope, indent=2) + "\n", encoding="utf-8"
    )
    (root / "manifest.sig").write_text(
        sign_envelope(envelope, key=key) + "\n", encoding="utf-8"
    )
    verify_bundle(root, key=key)
    return root


def set_current_pointer(bundles_root: str | Path, version_dir_name: str) -> Path:
    root = Path(bundles_root)
    root.mkdir(parents=True, exist_ok=True)
    pointer = root / "CURRENT"
    pointer.write_text(version_dir_name + "\n", encoding="utf-8")
    return pointer


def read_current_pointer(bundles_root: str | Path) -> str:
    pointer = Path(bundles_root) / "CURRENT"
    if not pointer.is_file():
        raise FileNotFoundError(f"No CURRENT pointer under {bundles_root}")
    return pointer.read_text(encoding="utf-8").strip()


def rollback_bundle(
    bundles_root: str | Path,
    previous_version: str,
    *,
    key: bytes | None = None,
) -> Path:
    """Point CURRENT at a previous verified bundle version (rollback)."""
    root = Path(bundles_root)
    target = root / previous_version
    verify_bundle(target, key=key)
    return set_current_pointer(root, previous_version)



def load_bundle_torch_model(
    bundle_dir: str | Path,
    *,
    key: bytes | None = None,
) -> nn.Module:
    verify_bundle(bundle_dir, key=key)
    model = SimpleCNN()
    state = torch.load(  # nosec B614
        Path(bundle_dir) / "model.pt", map_location="cpu", weights_only=True
    )
    model.load_state_dict(state)
    model.eval()
    return model
