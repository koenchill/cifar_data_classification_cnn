"""Phase 06: checkpoint resume, seeded runs, artifact authz."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
import torch
from torch.utils.data import DataLoader, TensorDataset

from cifar_cnn.models.simple_cnn import SimpleCNN
from cifar_cnn.training.authz import ArtifactWriteDenied, assert_artifact_write_allowed
from cifar_cnn.training.checkpoint import CheckpointManager, atomic_torch_save
from cifar_cnn.training.config import ConfigValidationError, ControlledTrainConfig
from cifar_cnn.training.controlled import controlled_train_loop, seed_everything
from cifar_cnn.training.trainer import build_optimizer


def _loader(n: int = 32, batch_size: int = 8) -> DataLoader:
    x = torch.randn(n, 3, 32, 32)
    y = torch.randint(0, 10, (n,))
    return DataLoader(TensorDataset(x, y), batch_size=batch_size, shuffle=False)


def test_config_validation_rejects_bad_identity() -> None:
    with pytest.raises(ConfigValidationError):
        ControlledTrainConfig(identity="hacker").validate()


def test_unauthorized_mutation_denied(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "models").mkdir()
    assert_artifact_write_allowed("artifacts/run/x.pt", identity="training", cwd=tmp_path)
    with pytest.raises(ArtifactWriteDenied):
        assert_artifact_write_allowed("models/cnn_model.pth", identity="training", cwd=tmp_path)
    with pytest.raises(ArtifactWriteDenied):
        assert_artifact_write_allowed("../outside.pt", identity="training", cwd=tmp_path)


def test_atomic_checkpoint_replace(tmp_path: Path) -> None:
    path = tmp_path / "artifacts" / "c.pt"
    path.parent.mkdir(parents=True)
    atomic_torch_save({"ok": 1}, path)
    assert path.is_file()
    assert not path.with_name(path.name + ".tmp").exists()


def test_checkpoint_resume_and_best_restore(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    art = tmp_path / "artifacts" / "ctrl"
    loader = _loader()
    cfg = ControlledTrainConfig(
        epochs=2,
        smoke_max_batches=2,
        log_every_n_batches=1,
        artifact_dir=str(art),
        early_stop_patience=5,
        scheduler="none",
        run_id="resume-a",
        seed=0,
    )
    model = SimpleCNN()
    result = controlled_train_loop(model, loader, cfg, valloader=loader)
    assert result.last_checkpoint and Path(result.last_checkpoint).is_file()
    assert result.best_checkpoint and Path(result.best_checkpoint).is_file()

    # Resume from last and train one more epoch.
    model2 = SimpleCNN()
    cfg2 = replace(
        cfg,
        epochs=3,
        resume_from=result.last_checkpoint,
        run_id="resume-b",
        artifact_dir=str(art / "resume"),
    )
    result2 = controlled_train_loop(model2, loader, cfg2, valloader=loader)
    assert result2.resumed_from_epoch == 1
    assert result2.epochs_trained >= 1

    # Best-model restoration: manager restores weights that match saved best.
    mgr = CheckpointManager(art, identity="training", cwd=tmp_path)
    fresh = SimpleCNN()
    opt = build_optimizer(fresh)
    state = mgr.restore(result.best_checkpoint, model=fresh, optimizer=opt)
    assert "model_state_dict" in state
    x = torch.randn(1, 3, 32, 32)
    with torch.no_grad():
        # model was restored to best at end of first loop
        assert torch.allclose(model(x), fresh(x))


def test_seeded_runs_match_within_tolerance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    loader = _loader(n=48, batch_size=8)

    def run_once(run_id: str) -> list[float]:
        seed_everything(123)
        model = SimpleCNN()
        # Identical init: re-seed then reconstruct
        seed_everything(123)
        model = SimpleCNN()
        cfg = ControlledTrainConfig(
            epochs=2,
            smoke_max_batches=3,
            log_every_n_batches=1,
            artifact_dir=str(tmp_path / "artifacts" / run_id),
            seed=123,
            scheduler="none",
            early_stop_patience=10,
            run_id=run_id,
            deterministic=True,
        )
        result = controlled_train_loop(model, loader, cfg, valloader=loader)
        return [row["val_loss"] for row in result.history]

    a = run_once("seed-a")
    b = run_once("seed-b")
    assert len(a) == len(b) == 2
    for x, y in zip(a, b, strict=True):
        assert abs(x - y) <= 1e-5
