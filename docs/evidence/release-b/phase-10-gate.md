# Phase 10 Exit Gate

| Field | Value |
|---|---|
| Phase | 10 — Governed Model Bundle, ONNX, and AI Release Gate |
| Date | 2026-08-01 |
| Result | `passed` |
| Approver | koenchill (model owner) |
| Release | **B closed** |

## Deliverables

| Deliverable | Present |
|---|---|
| ONNX export + parity | `src/cifar_cnn/inference/onnx_export.py`, `phase-10-onnx-parity.json` |
| Signed bundle | `models/bundles/simple_cnn-1.0.x` + `phase-10-bundle-manifest.json` |
| Tamper/rollback tests | `tests/unit/test_bundle_tamper.py` |
| AI release decision | `phase-10-ai-release-decision.md` |
| Deps | `onnx==1.17.0`, `onnxruntime==1.22.0` in `pyproject.toml` |

## Verify

```text
pytest -q tests -k "onnx_parity or bundle_tamper"
python scripts/pack_bundle.py
```

## Exit gate

- [x] Load/dynamic-batch/parity/metadata/signature/tamper/rollback tests pass
- [x] High unresolved AI risks do not block B offline; AIR-05 prod-blocked until Phase 11
- [x] Release B complete

## Notes

HMAC uses `CIFAR_CNN_BUNDLE_HMAC_KEY` when set; otherwise a documented dev-only key.
