"""Structured audit events — never include tokens, secrets, or image bytes."""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any

_logger = logging.getLogger("cifar_cnn.audit")


@dataclass
class AuditEvent:
    event_id: str
    ts: float
    action: str
    outcome: str
    subject: str | None = None
    status_code: int | None = None
    detail: str | None = None
    model_id: str | None = None
    content_type: str | None = None
    byte_length: int | None = None
    request_id: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, Any]:
        data = asdict(self)
        # Defense in depth: drop any accidental sensitive keys
        for banned in ("token", "authorization", "image", "password", "secret"):
            data.pop(banned, None)
            data["extras"].pop(banned, None)
        return data


class AuditSink:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def emit(self, event: AuditEvent) -> None:
        self.events.append(event)
        _logger.info("audit %s", json.dumps(event.to_public_dict(), sort_keys=True))

    def reset(self) -> None:
        self.events.clear()


_sink = AuditSink()


def get_audit_sink() -> AuditSink:
    return _sink


def new_request_id() -> str:
    return uuid.uuid4().hex


def audit(
    action: str,
    outcome: str,
    *,
    subject: str | None = None,
    status_code: int | None = None,
    detail: str | None = None,
    model_id: str | None = None,
    content_type: str | None = None,
    byte_length: int | None = None,
    request_id: str | None = None,
    **extras: Any,
) -> AuditEvent:
    event = AuditEvent(
        event_id=uuid.uuid4().hex,
        ts=time.time(),
        action=action,
        outcome=outcome,
        subject=subject,
        status_code=status_code,
        detail=detail,
        model_id=model_id,
        content_type=content_type,
        byte_length=byte_length,
        request_id=request_id,
        extras=extras,
    )
    get_audit_sink().emit(event)
    return event
