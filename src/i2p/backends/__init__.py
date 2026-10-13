"""Caption backends. Each implements CaptionBackend and self-registers."""
from i2p.backends.base import CaptionBackend
from i2p.backends.registry import get_backend, register_backend

__all__ = ["CaptionBackend", "get_backend", "register_backend"]