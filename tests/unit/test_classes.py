from __future__ import annotations

from cifar_cnn.data.constants import CIFAR10_CLASSES, NUM_CLASSES


def test_cifar10_classes_exact_order() -> None:
    assert CIFAR10_CLASSES == (
        "airplane",
        "automobile",
        "bird",
        "cat",
        "deer",
        "dog",
        "frog",
        "horse",
        "ship",
        "truck",
    )
    assert NUM_CLASSES == 10
