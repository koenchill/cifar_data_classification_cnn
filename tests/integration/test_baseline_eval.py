"""Integration: baseline eval (10k), gallery, dual-path model save."""

from __future__ import annotations

from pathlib import Path

import torch
from fake_cifar import FakeCIFAR10
from torch.utils.data import Subset

from cifar_cnn.data.constants import TEST_SIZE
from cifar_cnn.data.loaders import GuideDataConfig, build_guide_loaders
from cifar_cnn.evaluation import (
    evaluate_accuracy,
    load_baseline_model,
    paths_have_identical_bytes,
    save_baseline_model,
    save_prediction_gallery,
    write_metrics,
)
from cifar_cnn.models.simple_cnn import SimpleCNN
from cifar_cnn.training import TrainConfig, train_loop


def test_baseline_eval_ten_thousand(tmp_path: Path) -> None:
    trainset = FakeCIFAR10(train=True)
    testset = FakeCIFAR10(train=False)
    assert len(testset) == TEST_SIZE
    trainloader, testloader = build_guide_loaders(
        GuideDataConfig(batch_size=64, download=False),
        train_subset=Subset(trainset, list(range(128))),
        test_subset=testset,
    )
    model = SimpleCNN()
    train_loop(
        model,
        trainloader,
        TrainConfig(
            epochs=1,
            smoke_max_batches=2,
            log_every_n_batches=1,
            artifact_dir=str(tmp_path / "train"),
        ),
    )
    result = evaluate_accuracy(model, testloader, expected_total=TEST_SIZE)
    assert result.total == 10_000
    assert "10000 test images" in result.message
    assert 0.0 <= result.accuracy_pct <= 100.0
    metrics = write_metrics(tmp_path / "metrics.json", result)
    assert metrics.is_file()


def test_gallery_artifact(tmp_path: Path) -> None:
    testset = FakeCIFAR10(train=False)
    _, testloader = build_guide_loaders(
        GuideDataConfig(batch_size=8, download=False),
        train_subset=FakeCIFAR10(train=True),
        test_subset=testset,
    )
    path = tmp_path / "gallery.png"
    save_prediction_gallery(SimpleCNN(), testloader, path)
    assert path.is_file() and path.stat().st_size > 1000


def test_model_save_dual_paths_and_load(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    model = SimpleCNN()
    # Touch a distinct weight so load is meaningful.
    with torch.no_grad():
        model.fc2.bias.fill_(0.123)
    repo, guide = save_baseline_model(
        model,
        repo_path=tmp_path / "models" / "cnn_model.pth",
        guide_path=tmp_path / "cnn_model.pth",
    )
    assert repo.is_file() and guide.is_file()
    assert paths_have_identical_bytes(repo, guide)
    restored = SimpleCNN()
    load_baseline_model(restored, guide)
    x = torch.randn(1, 3, 32, 32)
    with torch.no_grad():
        assert torch.allclose(model(x), restored(x))
