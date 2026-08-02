"""Model architectures."""

from cifar_cnn.models.simple_cnn import (
    SimpleCNN,
    count_parameters,
    load_state_dict,
    save_state_dict,
)

__all__ = ["SimpleCNN", "count_parameters", "load_state_dict", "save_state_dict"]
