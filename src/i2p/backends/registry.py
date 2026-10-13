"""Backend registry — entry-point discovery + explicit registration."""
from __future__ import annotations

from importlib.metadata import entry_points

from i2p.backends.base import CaptionBackend
from i2p.config.schema import AppConfig
from i2p.utils.logging import get_logger

log = get_logger(__name__)
_REGISTRY: dict[str, type[CaptionBackend]] = {}


def register_backend(name: str, cls: type[CaptionBackend]) -> None:
    if name in _REGISTRY and _REGISTRY[name] is not cls:
        log.warning("backend %r re-registered by %s", name, cls.__module__)
    _REGISTRY[name] = cls


def _discover() -> None:
    for ep in entry_points(group="i2p.backends"):
        try:
            cls = ep.load()
            register_backend(ep.name, cls)
        except Exception as exc:  # noqa: BLE001 — a broken plugin must not kill the app
            log.error("failed to load backend %s: %s", ep.name, exc)


def get_backend(name: str, config: AppConfig) -> CaptionBackend:
    if not _REGISTRY:
        _discover()
    if name not in _REGISTRY:
        raise KeyError(f"unknown backend {name!r}; known: {sorted(_REGISTRY)}")
    return _REGISTRY[name](config)