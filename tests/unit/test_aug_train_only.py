"""Phase 07: train-only augmentation; eval transforms stay unaugmented."""

from __future__ import annotations

from pathlib import Path

import torch
import yaml
from fake_cifar import FakeCIFAR10
from torch.utils.data import DataLoader, Subset
from torchvision.transforms import (
    ColorJitter,
    Normalize,
    RandomCrop,
    RandomHorizontalFlip,
    ToTensor,
)

from cifar_cnn.data.transforms import (
    build_eval_transform,
    build_guide_transform,
    build_train_augment_transform,
    describe_train_augment_transform,
)
from cifar_cnn.models.ablation import (
    ABLATION_VARIANTS,
    TensorTrainAugmentDataset,
    run_ablation_suite,
    write_ablation_report,
)
from cifar_cnn.models.improved_cnn import ImprovedCNN
from cifar_cnn.models.simple_cnn import SimpleCNN, count_parameters


def test_aug_train_only_compose_has_crop_flip_not_on_eval() -> None:
    train_tf = build_train_augment_transform(color_jitter=False)
    eval_tf = build_eval_transform()
    guide_tf = build_guide_transform()

    train_types = [type(t) for t in train_tf.transforms]
    assert RandomCrop in train_types
    assert RandomHorizontalFlip in train_types
    assert ToTensor in train_types
    assert Normalize in train_types
    assert ColorJitter not in train_types

    eval_types = [type(t) for t in eval_tf.transforms]
    assert RandomCrop not in eval_types
    assert RandomHorizontalFlip not in eval_types
    assert ColorJitter not in eval_types
    assert eval_types == [type(t) for t in guide_tf.transforms]

    desc = describe_train_augment_transform()
    assert desc["augmentation"] is True
    assert desc["applies_to"] == ["train_only"]
    assert "test" in desc["forbidden_for"]


def test_aug_train_only_optional_color_jitter() -> None:
    tf = build_train_augment_transform(color_jitter=True)
    assert any(isinstance(t, ColorJitter) for t in tf.transforms)


def test_improved_cnn_forward_and_flags() -> None:
    net = ImprovedCNN(batch_norm=True, dropout=True, dropout_p=0.3)
    x = torch.randn(2, 3, 32, 32)
    y = net(x)
    assert y.shape == (2, 10)
    assert torch.isfinite(y).all()
    assert not isinstance(net.bn1, torch.nn.Identity)
    plain = ImprovedCNN(batch_norm=False, dropout=False)
    assert isinstance(plain.bn1, torch.nn.Identity)
    assert isinstance(plain.drop, torch.nn.Identity)
    # Improved with BN typically has more params than SimpleCNN.
    assert count_parameters(net) > count_parameters(SimpleCNN())


def test_ablation_protocol_reproduces_and_eval_unaugmented(tmp_path: Path) -> None:
    base_train = Subset(FakeCIFAR10(train=True), list(range(64)))
    base_eval = Subset(FakeCIFAR10(train=True), list(range(64, 96)))

    def make_loaders(train_augment: bool):
        train_ds = TensorTrainAugmentDataset(base_train, augment=train_augment)
        eval_ds = TensorTrainAugmentDataset(base_eval, augment=False)
        return (
            DataLoader(train_ds, batch_size=8, shuffle=False),
            DataLoader(eval_ds, batch_size=8, shuffle=False),
        )

    a = run_ablation_suite(make_loaders, seed=42, epochs=2, max_batches=2)
    b = run_ablation_suite(make_loaders, seed=42, epochs=2, max_batches=2)
    assert [r.name for r in a] == [v.name for v in ABLATION_VARIANTS]
    for ra, rb in zip(a, b, strict=True):
        assert abs(ra.final_eval_loss - rb.final_eval_loss) <= 1e-5
        assert abs(ra.final_train_loss - rb.final_train_loss) <= 1e-5

    report = write_ablation_report(tmp_path / "ablation.json", a)
    assert report.is_file()


def test_train_augment_yaml_forbids_eval_aug() -> None:
    cfg = yaml.safe_load(Path("configs/data/train_augment.yaml").read_text(encoding="utf-8"))
    assert cfg["augmentation_on_eval"] is False
    assert "test" in cfg["forbidden_for"]
