# Phase 09 Champion Decision Record

| Field | Value |
|---|---|
| Rule | `release-b-champion-v1` (`configs/model/champion_selection.yaml`) |
| Official test used in selection | **No** |
| Smoke dataset | FakeCIFAR10 validation subset |
| Reviews | model_owner + ai_risk (smoke approvals recorded in JSON) |

## Declared criteria (frozen)

1. Reject candidates outside size/latency/param envelope  
2. Rank remaining by `val_macro_f1` ↓, `val_accuracy` ↓, `val_ece` ↑, `latency_ms` ↑, `size_mb` ↑  
3. Any official-test field in inputs → hard fail (`ChampionSelectionError`)

## Transfer path documentation

See `docs/model_cards/resnet18_transfer.md` and `describe_transfer_stack()` for weights URL,
BSD-3 / ImageNet terms note, CIFAR stem adaptation, classifier replacement, and freeze modes.

## Machine-readable outputs

- `phase-09-comparison.json` — val metrics, footprint, robustness pass rate  
- `phase-09-champion-decision.json` — champion id, ranking, rejected alternatives, rationale  

## Capacity / envelope

Envelope allows ≤50 MB, ≤500 ms CPU smoke latency, ≤15 M params. ResNet18CIFAR fits size/params;
if latency exceeds envelope on a host, rule rejects it and capacity must be revised deliberately
(not silently).

## Non-claims

FakeCIFAR smoke ranking is protocol evidence, not a production CIFAR-10 champion claim.
Offline pretrained fine-tune + real val split required before Release B promotion (Phase 10).
