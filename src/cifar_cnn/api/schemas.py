"""API request/response models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Decision = Literal["accept", "low_confidence", "uncertain"]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


class ReadyResponse(BaseModel):
    ready: bool
    model_id: str | None = None
    reason: str | None = None


class MetadataResponse(BaseModel):
    model_id: str
    model_version: str
    classes: list[str]
    input: dict[str, Any]
    confidence_policy: dict[str, float]
    disclaimers: list[str]


class ClassScore(BaseModel):
    class_id: int
    class_name: str
    probability: float


class PredictResponse(BaseModel):
    model_id: str
    model_version: str
    top1_class: int
    top1_class_name: str
    top1_confidence: float
    decision: Decision
    low_confidence: bool = False
    uncertain: bool = False
    top_k: list[ClassScore] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    disclaimers: list[str] = Field(default_factory=list)
    request_id: str


class ErrorBody(BaseModel):
    detail: str
    request_id: str | None = None
