"""Minimal future AI audit metadata without raw clinical payload logging."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID


@dataclass(frozen=True)
class AIAuditMetadata:
    request_id: UUID
    user_id: int
    role: str
    request_type: str
    model_version: str | None = None
    preprocessing_version: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Return only non-sensitive operational metadata."""

        return {
            "request_id": str(self.request_id),
            "user_id": self.user_id,
            "role": self.role,
            "request_type": self.request_type,
            "model_version": self.model_version,
            "preprocessing_version": self.preprocessing_version,
            "timestamp": self.timestamp.isoformat(),
            "metadata": dict(self.metadata),
        }
