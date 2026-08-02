"""Model architectures and champion selection."""

from cifar_cnn.models.champion import (
    CandidateMetrics,
    ChampionDecision,
    ChampionSelectionError,
    SelectionRule,
    select_champion,
    write_champion_decision,
)
from cifar_cnn.models.improved_cnn import ImprovedCNN, describe_improved_architecture
from cifar_cnn.models.resnet_transfer import (
    build_resnet18_cifar,
    describe_transfer_stack,
)
from cifar_cnn.models.simple_cnn import (
    SimpleCNN,
    count_parameters,
    load_state_dict,
    save_state_dict,
)

__all__ = [
    "CandidateMetrics",
    "ChampionDecision",
    "ChampionSelectionError",
    "ImprovedCNN",
    "SelectionRule",
    "SimpleCNN",
    "build_resnet18_cifar",
    "count_parameters",
    "describe_improved_architecture",
    "describe_transfer_stack",
    "load_state_dict",
    "save_state_dict",
    "select_champion",
    "write_champion_decision",
]
