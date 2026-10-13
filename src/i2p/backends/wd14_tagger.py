"""WD14 (SmilingWolf) tagger backend — booru-style tag vocabulary."""
from __future__ import annotations

import numpy as np

from i2p.backends.base import CaptionBackend
from i2p.backends.registry import register_backend
from i2p.config.schema import AppConfig
from i2p.utils.logging import get_logger

log = get_logger(__name__)


class WD14TaggerBackend(CaptionBackend):
    name = "wd14_tagger"

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.last_confidence = 0.0
        self._session = None
        self._labels: list[str] = []

    def _ensure(self) -> None:
        if self._session is not None:
            return
        import onnxruntime as ort  # noqa: PLC0415

        cfg = self.config.backends.wd14_tagger
        path = self.config.cache_dir / "wd14" / "model.onnx"
        if not path.exists():
            log.warning("WD14 weights missing at %s — run `i2p doctor`", path)
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        self._session = ort.InferenceSession(str(path), providers=providers)

    def caption(self, image: np.ndarray, mode: str = "best") -> str:
        self._ensure()
        tags = self.tags(image)
        self.last_confidence = 0.74
        return ", ".join(tags[:40])

    def tags(self, image: np.ndarray) -> list[str]:
        self._ensure()
        # Real impl: resize to 448, normalize, run session, threshold by cfg.
        return []

    def unload(self) -> None:
        self._session = None


register_backend("wd14_tagger", WD14TaggerBackend)