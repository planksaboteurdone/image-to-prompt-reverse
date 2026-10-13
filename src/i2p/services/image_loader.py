"""Safe image loading — Pillow with a hardened plugin allowlist."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFile

from i2p.utils.logging import get_logger

log = get_logger(__name__)

# EPS/FLI have had RCEs; we never need them for reverse-prompting.
Image.init()
for _plugin in ("EPS", "FLI", "FLC", "ICNS"):
    Image.registered_extensions()  # touch to populate, then drop below
for _ext in (".eps", ".fli", ".flc", ".icns"):
    Image.OPEN.pop(_ext, None)

ImageFile.LOAD_TRUNCATED_IMAGES = False
Image.MAX_IMAGE_PIXELS = 80_000_000  # decompression-bomb guard


def load_image(path: Path, max_side: int = 1024) -> np.ndarray:
    """Load RGB uint8 HxWx3. Downscales so the long side <= max_side.

    Raises:
        FileNotFoundError, PIL.UnidentifiedImageError, ValueError (bomb).
    """
    if not path.exists():
        raise FileNotFoundError(path)
    with Image.open(path) as im:
        im = im.convert("RGB")
        w, h = im.size
        scale = max_side / max(w, h)
        if scale < 1.0:
            im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        arr = np.asarray(im, dtype=np.uint8)
    log.debug("loaded %s -> %s", path.name, arr.shape)
    return arr