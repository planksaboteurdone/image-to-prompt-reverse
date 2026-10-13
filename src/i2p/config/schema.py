"""Typed config schema. Pydantic v2 — fails loud on bad YAML."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class BackendConfig(BaseModel):
    enabled: bool = True
    model_config = {"extra": "allow"}


class CLIPInterrogatorConfig(BackendConfig):
    clip_model: str = "ViT-L-14/openai"
    caption_model: str = "blip-large"
    flavor: Literal["fast", "best", "classic"] = "best"


class WD14TaggerConfig(BackendConfig):
    model: str = "SmilingWolf/wd-v1-4-convnext-tagger-v2"
    threshold: float = Field(0.35, ge=0.0, le=1.0)


class BackendsConfig(BaseModel):
    clip_interrogator: CLIPInterrogatorConfig = CLIPInterrogatorConfig()
    wd14_tagger: WD14TaggerConfig = WD14TaggerConfig()


class PipelineConfig(BaseModel):
    fusion: Literal["weighted", "concat", "first"] = "weighted"
    max_tokens: int = Field(77, gt=0, le=512)
    strip_artist_tags: bool = False
    dedupe: bool = True


class GUIConfig(BaseModel):
    theme: Literal["dark", "light"] = "dark"
    thumbnail_size: int = Field(256, gt=0)
    autosave_history: bool = True
    history_path: Path = Path("outputs/history.jsonl")


class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    file: Path = Path("logs/i2p.log")


class AppConfig(BaseModel):
    device: Literal["auto", "cuda", "cpu", "mps"] = "auto"
    precision: Literal["fp16", "bf16", "fp32"] = "fp16"
    cache_dir: Path = Path(".cache/i2p")
    backends: BackendsConfig = BackendsConfig()
    pipeline: PipelineConfig = PipelineConfig()
    gui: GUIConfig = GUIConfig()
    logging: LoggingConfig = LoggingConfig()

    @field_validator("cache_dir")
    @classmethod
    def _ensure_cache_dir(cls, v: Path) -> Path:
        v.mkdir(parents=True, exist_ok=True)
        return v