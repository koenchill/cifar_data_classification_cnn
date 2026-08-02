from __future__ import annotations

from cifar_cnn.data.lineage import build_lineage_record


def test_lineage_record_contains_guide_contract_fields() -> None:
    record = build_lineage_record(root="./data")
    assert record["dataset"] == "CIFAR-10"
    assert record["source"] == "torchvision.datasets.CIFAR10"
    assert record["sizes"]["train"] == 50_000
    assert record["sizes"]["test"] == 10_000
    assert record["transforms"]["augmentation"] is False
    assert "model-affecting" in record["change_control"]
