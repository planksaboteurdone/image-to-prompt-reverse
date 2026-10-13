"""Abstract backend contract. Every reverse-prompt engine implements this."""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class CaptionBackend(ABC):
    """A caption/tag engine.

    Inputs:
        image: HxWx3 uint8 RGB ndarray.
        mode: engine-specific hint ("fast" | "best" | "classic").
    Outputs:
        caption(): single natural-language prompt string.
        tags():    short aesthetic/character tags (may be empty).
    Side effects:
        Loads weights lazily on first call. May allocate GPU memory.
    Concurrency:
        Not thread-safe. One instance per process/thread.
    """

    name: str = "base"

    @abstractmethod
    def caption(self, image: np.ndarray, mode: str = "best") -> str: ...

    def tags(self, image: np.ndarray) -> list[str]:
        return []

    def unload(self) -> None:
        """Release weights. Override if the backend holds GPU tensors."""
        return None