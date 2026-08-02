"""Experiment tracking: human log + JSONL/CSV (+ optional TensorBoard)."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TextIO

from cifar_cnn.training.authz import assert_artifact_write_allowed


def git_sha_or_none() -> str | None:
    """Best-effort HEAD SHA via ``.git`` files (no subprocess)."""
    git_dir = Path(".git")
    head = git_dir / "HEAD"
    if not head.is_file():
        return None
    text = head.read_text(encoding="utf-8").strip()
    if text.startswith("ref:"):
        ref = text.split(" ", 1)[1].strip()
        ref_path = git_dir / ref
        if ref_path.is_file():
            return ref_path.read_text(encoding="utf-8").strip() or None
        return None
    return text or None


@dataclass
class RunIdentity:
    run_id: str
    identity: str
    model: str = "SimpleCNN"
    git_sha: str | None = None


class ExperimentTracker:
    """Append-only metrics with attached run identity."""

    def __init__(
        self,
        artifact_dir: str | Path,
        run: RunIdentity,
        *,
        cwd: Path | None = None,
    ) -> None:
        self.dir = Path(artifact_dir)
        self.run = run
        self.cwd = cwd
        assert_artifact_write_allowed(
            self.dir / "metrics.jsonl", identity=run.identity, cwd=cwd
        )
        self.dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.dir / "metrics.jsonl"
        self.csv_path = self.dir / "metrics.csv"
        self.log_path = self.dir / "train.log"
        self.tb_dir = self.dir / "tensorboard"
        self.tb_dir.mkdir(parents=True, exist_ok=True)
        self._tb = self._maybe_summary_writer()
        self._csv_initialized = self.csv_path.is_file()
        self._log: TextIO = self.log_path.open("a", encoding="utf-8")
        self.log(
            f"run_start run_id={run.run_id} identity={run.identity} "
            f"model={run.model} git_sha={run.git_sha or 'unknown'}"
        )

    def _maybe_summary_writer(self) -> Any:
        try:
            from torch.utils.tensorboard import SummaryWriter

            return SummaryWriter(log_dir=str(self.tb_dir))  # type: ignore[no-untyped-call]
        except Exception:
            stub = self.tb_dir / "scalars.jsonl"
            stub.touch(exist_ok=True)
            return None

    def log(self, message: str) -> None:
        ts = datetime.now(UTC).isoformat()
        line = f"[{ts}] {message}"
        self._log.write(line + "\n")
        self._log.flush()

    def log_metrics(self, step: int, metrics: dict[str, float], *, epoch: int) -> None:
        record = {
            "ts": datetime.now(UTC).isoformat(),
            "run_id": self.run.run_id,
            "identity": self.run.identity,
            "model": self.run.model,
            "git_sha": self.run.git_sha,
            "epoch": epoch,
            "step": step,
            **metrics,
        }
        with self.jsonl_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")

        fieldnames = list(record.keys())
        write_header = not self._csv_initialized
        with self.csv_path.open("a", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
                self._csv_initialized = True
            writer.writerow(record)

        if self._tb is not None:
            for key, value in metrics.items():
                self._tb.add_scalar(key, value, global_step=step)
        else:
            with (self.tb_dir / "scalars.jsonl").open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"step": step, "epoch": epoch, **metrics}) + "\n")

        metric_str = " ".join(f"{k}={v:.6f}" for k, v in metrics.items())
        self.log(f"epoch={epoch} step={step} {metric_str}")

    def close(self) -> None:
        self.log("run_end")
        self._log.close()
        if self._tb is not None:
            self._tb.close()
