"""Inference preprocessing for PIL images (guide-exact normalize)."""

from __future__ import annotations

from PIL import Image
from torch import Tensor
from torchvision import transforms

from cifar_cnn.data.transforms import build_guide_transform

_TRANSFORM: transforms.Compose | None = None


def get_inference_transform() -> transforms.Compose:
    global _TRANSFORM
    if _TRANSFORM is None:
        _TRANSFORM = build_guide_transform()
    return _TRANSFORM


def pil_to_batch_tensor(image: Image.Image) -> Tensor:
    """Convert a validated RGB 32x32 PIL image to a batched float tensor."""
    tensor = get_inference_transform()(image)
    if not isinstance(tensor, Tensor):
        raise TypeError("Inference transform must return a Tensor")
    return tensor.unsqueeze(0)
