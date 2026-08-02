"""Guide-exact CIFAR-10 transforms (Step 1)."""

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
