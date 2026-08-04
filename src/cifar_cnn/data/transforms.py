"""Guide-exact CIFAR-10 transforms plus additive train-only augmentation."""

from __future__ import annotations

from typing import Literal

from torchvision import transforms

from cifar_cnn.data.constants import (
    IMAGENET_MEAN,
    IMAGENET_STD,
    NORMALIZE_MEAN,
    NORMALIZE_STD,
)

NormalizeMode = Literal["guide", "imagenet"]


def _mean_std(normalize: NormalizeMode) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    if normalize == "imagenet":
        return IMAGENET_MEAN, IMAGENET_STD
    return NORMALIZE_MEAN, NORMALIZE_STD


def build_guide_transform(*, normalize: NormalizeMode = "guide") -> transforms.Compose:
    """Return ToTensor + Normalize. Default matches the student guide (0.5).

    Evaluation/test must use the same normalize mode as training — no augmentation.
    """
    mean, std = _mean_std(normalize)
    return transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ]
    )


def build_eval_transform(*, normalize: NormalizeMode = "guide") -> transforms.Compose:
    """Explicit eval/test transform alias — never includes augmentation."""
    return build_guide_transform(normalize=normalize)


def build_train_augment_transform(
    *,
    color_jitter: bool = False,
    cutout: bool = False,
    cutout_p: float = 0.5,
    pad: int = 4,
    flip_p: float = 0.5,
    normalize: NormalizeMode = "guide",
) -> transforms.Compose:
    """Training-only augmentation (crop/flip; optional color jitter / cutout).

    Must not be applied to val-eval or official test loaders.
    """
    mean, std = _mean_std(normalize)
    ops: list[object] = [
        transforms.RandomCrop(32, padding=pad),
        transforms.RandomHorizontalFlip(p=flip_p),
    ]

    if color_jitter:
        ops.append(
            transforms.ColorJitter(
                brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1
            )
        )
    ops.append(transforms.ToTensor())
    if cutout:
        # RandomErasing approximates Cutout on tensor images (train only).
        ops.append(
            transforms.RandomErasing(
                p=cutout_p, scale=(0.02, 0.25), ratio=(0.3, 3.3), value=0
            )
        )
    ops.append(transforms.Normalize(mean, std))
    return transforms.Compose(ops)


def describe_guide_transform(*, normalize: NormalizeMode = "guide") -> dict[str, object]:
    """Machine-readable lineage for the baseline transform chain."""
    mean, std = _mean_std(normalize)
    return {
        "compose": [
            {"name": "ToTensor"},
            {
                "name": "Normalize",
                "mean": list(mean),
                "std": list(std),
                "mode": normalize,
            },
        ],
        "augmentation": False,
        "applies_to": ["train", "test", "val_eval"],
    }


def describe_train_augment_transform(
    *,
    color_jitter: bool = False,
    cutout: bool = False,
    cutout_p: float = 0.5,
    normalize: NormalizeMode = "guide",
) -> dict[str, object]:
    mean, std = _mean_std(normalize)
    compose: list[dict[str, object]] = [
        {"name": "RandomCrop", "size": 32, "padding": 4},
        {"name": "RandomHorizontalFlip", "p": 0.5},
    ]
    if color_jitter:
        compose.append(
            {
                "name": "ColorJitter",
                "brightness": 0.2,
                "contrast": 0.2,
                "saturation": 0.2,
                "hue": 0.1,
            }
        )
    compose.append({"name": "ToTensor"})
    if cutout:
        compose.append(
            {
                "name": "RandomErasing",
                "p": cutout_p,
                "scale": [0.02, 0.25],
                "note": "cutout-style train-only occlusion",
            }
        )
    compose.append(
        {
            "name": "Normalize",
            "mean": list(mean),
            "std": list(std),
            "mode": normalize,
        }
    )
    return {
        "compose": compose,
        "augmentation": True,
        "applies_to": ["train_only"],
        "forbidden_for": ["test", "val_eval"],
    }
