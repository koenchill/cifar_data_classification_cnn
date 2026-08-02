"""Model architectures."""

from cifar_cnn.models.improved_cnn import ImprovedCNN, describe_improved_architecture
from cifar_cnn.models.simple_cnn import (
    SimpleCNN,
    count_parameters,
    load_state_dict,
    save_state_dict,
)

__all__ = [
    "ImprovedCNN",
    "SimpleCNN",
    "count_parameters",
    "describe_improved_architecture",
    "load_state_dict",
    "save_state_dict",
]
