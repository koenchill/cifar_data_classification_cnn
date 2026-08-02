"""Loaded model runtime for the API process."""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch.nn as nn

from cifar_cnn.data.constants import CIFAR10_CLASSES
from cifar_cnn.inference.bundle import BundleIntegrityError, load_bundle_torch_model, verify_bundle


@dataclass
class LoadedModel:
    model: nn.Module
    model_id: str
    model_version: str
    classes: list[str]
    metadata: dict[str, Any]
    bundle_path: str


class ModelRuntime:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._loaded: LoadedModel | None = None
        self._last_error: str | None = None

    @property
    def ready(self) -> bool:
        return self._loaded is not None

    @property
    def last_error(self) -> str | None:
        return self._last_error

    def get(self) -> LoadedModel | None:
        return self._loaded

    def load_bundle(self, bundle_path: str | Path) -> LoadedModel:
        root = Path(bundle_path)
        try:
            verify_bundle(root)
            model = load_bundle_torch_model(root)
            meta = json.loads((root / "metadata.json").read_text(encoding="utf-8"))
            classes_payload = json.loads((root / "classes.json").read_text(encoding="utf-8"))
            classes = list(classes_payload.get("classes") or CIFAR10_CLASSES)
            loaded = LoadedModel(
                model=model,
                model_id=str(meta.get("bundle_id") or root.name),
                model_version=str(meta.get("version") or root.name),
                classes=classes,
                metadata=meta,
                bundle_path=str(root.resolve()),
            )
        except (BundleIntegrityError, OSError, KeyError, json.JSONDecodeError, RuntimeError) as exc:
            self._last_error = type(exc).__name__
            raise
        with self._lock:
            self._loaded = loaded
            self._last_error = None
        return loaded

    def set_for_tests(self, loaded: LoadedModel) -> None:
        with self._lock:
            self._loaded = loaded
            self._last_error = None
