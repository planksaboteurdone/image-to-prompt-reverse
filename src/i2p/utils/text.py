"""Prompt cleanup — the boring stuff that makes output usable."""
from __future__ import annotations

import re

import ftfy

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"\s+([,.!?])")
_TRAILING = re.compile(r"[,;\s]+$")


def clean_prompt(text: str) -> str:
    text = ftfy.fix_text(text)
    text = _WS.sub(" ", text).strip()
    text = _PUNCT.sub(r"\1", text)
    text = _TRAILING.sub("", text)
    return text


def dedupe_tags(tags: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        key = t.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(t.strip())
    return out


def truncate_tokens(text: str, max_tokens: int) -> str:
    """Cheap whitespace-based truncation. Good enough for CLIP's 77-token budget."""
    words = text.split()
    if len(words) <= max_tokens:
        return text
    return " ".join(words[:max_tokens]).rstrip(",; ")