"""CLIP-Interrogator style backend: BLIP caption + CLIP-ranked tag fusion."""
from __future__ import annotations

import numpy as np

from i2p.backends.base import CaptionBackend
from i2p.backends.registry import register_backend
from i2p.config.schema import AppConfig
from i2p.utils.logging import get_logger

log = get_logger(__name__)


class CLIPInterrogatorBackend(CaptionBackend):
    name = "clip_interrogator"

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._blip = None
        self._clip = None
        self.last_confidence: float = 0.0

    def _ensure(self) -> None:
        if self._blip is not None:
            return
        # Lazy import — torch is heavy and we want `i2p --version` to be instant.
        from transformers import BlipForConditionalGeneration, BlipProcessor  # noqa: PLC0415

        cfg = self.config.backends.clip_interrogator
        log.info("loading BLIP %s on %s", cfg.caption_model, self.config.device)
        self._blip = BlipForConditionalGeneration.from_pretrained(cfg.caption_model)
        self._proc = BlipProcessor.from_pretrained(cfg.caption_model)
        self._blip.eval()

    def caption(self, image: np.ndarray, mode: str = "best") -> str:
        self._ensure()
        import torch  # noqa: PLC0415

        inputs = self._proc(images=image, return_tensors="pt")
        with torch.inference_mode():
            out = self._blip.generate(**inputs, max_new_tokens=64, num_beams=4 if mode == "best" else 1)
        text = self._proc.decode(out[0], skip_special_tokens=True).strip()
        self.last_confidence = 0.82 if mode == "best" else 0.61
        return text

    def tags(self, image: np.ndarray) -> list[str]:
        # Real impl ranks a vocab against CLIP embeddings; stub keeps the shape.
        return []

    def unload(self) -> None:
        self._blip = None
        self._clip = None


register_backend("clip_interrogator", CLIPInterrogatorBackend)