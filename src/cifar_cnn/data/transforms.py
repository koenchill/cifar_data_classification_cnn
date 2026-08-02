"""Guide-exact CIFAR-10 transforms plus additive train-only augmentation."""

from __future__ import annotations

from torchvision import transforms

from cifar_cnn.data.constants import NORMALIZE_MEAN, NORMALIZE_STD


def build_guide_transform() -> transforms.Compose:
    """Return the student-guide Compose: ToTensor + Normalize(0.5).

    Evaluation/test must use this same transform — no augmentation.
    """
    return transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(NORMALIZE_MEAN, NORMALIZE_STD),
        ]
    )


def build_eval_transform() -> transforms.Compose:
    """Explicit eval/test transform alias — never includes augmentation."""
    return build_guide_transform()


def build_train_augment_transform(
    *,
    color_jitter: bool = False,
    pad: int = 4,
    flip_p: float = 0.5,
) -> transforms.Compose:
    """Training-only augmentation (crop/flip; optional color jitter).

    Must not be applied to val-eval or official test loaders.
    """
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
    ops.extend(
        [
            transforms.ToTensor(),
            transforms.Normalize(NORMALIZE_MEAN, NORMALIZE_STD),
        ]
    )
    return transforms.Compose(ops)


def describe_guide_transform() -> dict[str, object]:
    """Machine-readable lineage for the baseline transform chain."""
    return {
        "compose": [
            {"name": "ToTensor"},
            {
                "name": "Normalize",
                "mean": list(NORMALIZE_MEAN),
                "std": list(NORMALIZE_STD),
            },
        ],
        "augmentation": False,
        "applies_to": ["train", "test", "val_eval"],
    }


def describe_train_augment_transform(*, color_jitter: bool = False) -> dict[str, object]:
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
    compose.extend(
        [
            {"name": "ToTensor"},
            {
                "name": "Normalize",
                "mean": list(NORMALIZE_MEAN),
                "std": list(NORMALIZE_STD),
            },
        ]
    )
    return {
        "compose": compose,
        "augmentation": True,
        "applies_to": ["train_only"],
        "forbidden_for": ["test", "val_eval"],
    }
