"""ReversePipeline — orchestrates loader -> backend -> fusion -> postprocess."""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np

from i2p.backends.base import CaptionBackend
from i2p.backends.registry import get_backend
from i2p.config.schema import AppConfig
from i2p.core.result import ReverseResult
from i2p.services.image_loader import load_image
from i2p.utils.logging import get_logger
from i2p.utils.text import clean_prompt, dedupe_tags, truncate_tokens

log = get_logger(__name__)


class ReversePipeline:
    """End-to-end reverse-prompt pipeline. Stateless across calls; caches backends."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._backend_cache: dict[str, CaptionBackend] = {}

    def _backend(self, name: str) -> CaptionBackend:
        if name not in self._backend_cache:
            self._backend_cache[name] = get_backend(name, self.config)
        return self._backend_cache[name]

    def run(self, image: Path, backend: str = "clip_interrogator", mode: str = "best") -> ReverseResult:
        t0 = time.perf_counter()
        arr: np.ndarray = load_image(image)
        be = self._backend(backend)
        caption = be.caption(arr, mode=mode)
        tags = be.tags(arr) if hasattr(be, "tags") else []

        prompt = clean_prompt(caption)
        if self.config.pipeline.dedupe:
            tags = dedupe_tags(tags)
        prompt = truncate_tokens(prompt, self.config.pipeline.max_tokens)

        return ReverseResult(
            image=image,
            prompt=prompt,
            tags=tags,
            backend=backend,
            confidence=getattr(be, "last_confidence", 0.0),
            latency_ms=(time.perf_counter() - t0) * 1000.0,
        )

    def run_multi(self, image: Path, backends: list[str], mode: str = "best") -> ReverseResult:
        """Run N backends and fuse. Fusion strategy from config.pipeline.fusion."""
        results = [self.run(image, backend=b, mode=mode) for b in backends]
        if not results:
            raise ValueError("no backends produced output")
        if self.config.pipeline.fusion == "first":
            return results[0]
        if self.config.pipeline.fusion == "concat":
            merged = " ".join(r.prompt for r in results)
        else:  # weighted
            weights = np.array([max(r.confidence, 0.01) for r in results])
            weights = weights / weights.sum()
            ranked = sorted(zip(results, weights), key=lambda t: -t[1])
            merged = " ".join(r.prompt for r, _ in ranked)
        head = results[0]
        head.prompt = clean_prompt(merged)
        head.raw = {r.backend: r.prompt for r in results}
        return head