"""Config loader — merges default.yaml, user config, and env overrides."""
from __future__ import annotations

import os
from pathlib import Path

import yaml

from i2p.config.schema import AppConfig

_DEFAULT = Path(__file__).parent / "default.yaml"


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path: Path | None = None) -> AppConfig:
    """Load config. Order: default.yaml -> user yaml -> env overrides."""
    with _DEFAULT.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    user_path = path or _env_config_path()
    if user_path and user_path.exists():
        with user_path.open("r", encoding="utf-8") as fh:
            raw = _deep_merge(raw, yaml.safe_load(fh) or {})

    if dev := os.getenv("I2P_DEVICE"):
        raw["device"] = dev
    if lvl := os.getenv("I2P_LOG_LEVEL"):
        raw.setdefault("logging", {})["level"] = lvl

    return AppConfig.model_validate(raw)


def _env_config_path() -> Path | None:
    if p := os.getenv("I2P_CONFIG"):
        return Path(p)
    local = Path("config/local.yaml")
    return local if local.exists() else None