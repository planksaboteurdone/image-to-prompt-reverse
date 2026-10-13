"""Result types returned by the pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ReverseResult:
    image: Path
    prompt: str
    tags: list[str] = field(default_factory=list)
    backend: str = ""
    confidence: float = 0.0
    latency_ms: float = 0.0
    raw: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "image": str(self.image),
            "prompt": self.prompt,
            "tags": self.tags,
            "backend": self.backend,
            "confidence": round(self.confidence, 4),
            "latency_ms": round(self.latency_ms, 2),
        }