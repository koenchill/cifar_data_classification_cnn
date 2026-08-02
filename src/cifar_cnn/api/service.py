"""Prediction orchestration with confidence policy."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn.functional as F
from PIL import Image

from cifar_cnn.api.runtime import LoadedModel
from cifar_cnn.api.schemas import ClassScore, PredictResponse
from cifar_cnn.evaluation.safety import ConfidencePolicy, decide_from_probs, policy_summary
from cifar_cnn.inference.preprocess import pil_to_batch_tensor

_DISCLAIMERS = list(policy_summary()["non_claims"])


def predict_image(
    loaded: LoadedModel,
    image: Image.Image,
    *,
    top_k: int,
    request_id: str,
) -> PredictResponse:
    batch = pil_to_batch_tensor(image)
    with torch.inference_mode():
        logits = loaded.model(batch)[0]
        probs = F.softmax(logits, dim=0)
    decision = decide_from_probs(probs, policy=ConfidencePolicy())
    ordered = torch.argsort(probs, descending=True)
    k = min(top_k, int(probs.numel()))
    top_scores: list[ClassScore] = []
    for i in range(k):
        idx = int(ordered[i].item())
        name = loaded.classes[idx] if idx < len(loaded.classes) else str(idx)
        top_scores.append(
            ClassScore(class_id=idx, class_name=name, probability=float(probs[idx].item()))
        )
    top1_name = (
        loaded.classes[decision.top1_class]
        if decision.top1_class < len(loaded.classes)
        else str(decision.top1_class)
    )
    return PredictResponse(
        model_id=loaded.model_id,
        model_version=loaded.model_version,
        top1_class=decision.top1_class,
        top1_class_name=top1_name,
        top1_confidence=decision.top1_confidence,
        decision=decision.decision,
        low_confidence=decision.decision == "low_confidence",
        uncertain=decision.decision == "uncertain",
        top_k=top_scores,
        reasons=list(decision.reasons),
        disclaimers=_DISCLAIMERS,
        request_id=request_id,
    )


def metadata_payload(loaded: LoadedModel) -> dict[str, Any]:
    policy = ConfidencePolicy()
    return {
        "model_id": loaded.model_id,
        "model_version": loaded.model_version,
        "classes": loaded.classes,
        "input": {
            "content_types": ["image/png", "image/jpeg"],
            "dimensions": [32, 32],
            "layout": "HWC RGB",
            "tensor_layout": "NCHW",
        },
        "confidence_policy": {
            "low_confidence_threshold": policy.low_confidence_threshold,
            "uncertain_margin": policy.uncertain_margin,
        },
        "disclaimers": _DISCLAIMERS,
    }
