"""Append-only JSONL history for the GUI and CLI batch runs."""
from __future__ import annotations

import json
from pathlib import Path

from i2p.core.result import ReverseResult
from i2p.utils.logging import get_logger

log = get_logger(__name__)


class HistoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, result: ReverseResult) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")

    def tail(self, n: int = 50) -> list[dict]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines[-n:]]