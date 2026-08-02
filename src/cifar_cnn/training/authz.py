"""Artifact write authorization for training/eval/release identities."""

from __future__ import annotations

from pathlib import Path

# Deny-by-default roots per identity.
IDENTITY_WRITE_ROOTS: dict[str, tuple[str, ...]] = {
    "training": ("artifacts/",),
    "eval": ("artifacts/", "docs/evidence/"),
    "release": ("models/", "artifacts/release/"),
}


class ArtifactWriteDenied(PermissionError):
    """Raised when an identity attempts an unauthorized artifact write."""


def normalize_rel_path(path: str | Path, *, cwd: Path | None = None) -> Path:
    base = (cwd or Path.cwd()).resolve()
    p = Path(path)
    if ".." in p.parts:
        raise ArtifactWriteDenied("Path traversal denied")
    resolved = (p if p.is_absolute() else base / p).resolve()
    try:
        return resolved.relative_to(base)
    except ValueError as exc:
        raise ArtifactWriteDenied(f"Refusing write outside workspace: {path}") from exc


def assert_artifact_write_allowed(
    path: str | Path,
    *,
    identity: str,
    cwd: Path | None = None,
) -> Path:
    """Fail closed unless ``identity`` may write ``path`` under allowed roots."""
    if identity not in IDENTITY_WRITE_ROOTS:
        raise ArtifactWriteDenied(f"Unknown identity: {identity}")

    rel = normalize_rel_path(path, cwd=cwd)
    rel_posix = rel.as_posix()
    blocked_prefixes = ("src/", "tests/", ".git/", ".github/")
    if any(rel_posix == p.rstrip("/") or rel_posix.startswith(p) for p in blocked_prefixes):
        raise ArtifactWriteDenied(
            f"Identity '{identity}' denied write to code/VCS path '{rel_posix}'"
        )

    allowed = IDENTITY_WRITE_ROOTS[identity]
    if not any(rel_posix == r.rstrip("/") or rel_posix.startswith(r) for r in allowed):
        raise ArtifactWriteDenied(
            f"Identity '{identity}' may not write '{rel_posix}' "
            f"(allowed roots: {allowed})"
        )
    return rel
