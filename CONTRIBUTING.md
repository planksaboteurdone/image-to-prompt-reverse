# Contributing to image-to-prompt-reverse

Thanks for wanting to peel the tater with us. This repo is a Windows desktop
tool that takes an image and reverse-engineers a text prompt that could have
generated it — captioning, aesthetic tagging, CLIP interrogation, and
BLIP/Florence-style caption fusion, all wrapped in a PySide6 GUI.

## Dev setup

```powershell
git clone https://github.com/<you>/image-to-prompt-reverse
cd image-to-prompt-reverse
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

Weights are pulled on first run into `models/weights/` (gitignored). If you're
behind a proxy, set `I2P_HF_ENDPOINT` in `config/local.yaml`.

## Branch model

- `main` — release-ready, tag per version (`v2026.03`, `v2026.04`).
- `dev` — integration. PRs target this unless it's a hotfix.
- `feat/<scope>` — e.g. `feat/florence-fusion`, `feat/wd14-tagger`.

## Style

- `ruff` + `black` (line length 100). Run `pre-commit install` once.
- Type hints are mandatory on public functions. `mypy --strict` on `src/i2p/core`.
- No bare `except:`. Log with `i2p.utils.logging.get_logger(__name__)`.
- Backends live under `src/i2p/backends/` and must implement
  `CaptionBackend` (`src/i2p/backends/base.py`). New backends get a smoke test.

## Adding a backend

1. Subclass `CaptionBackend`.
2. Register it in `src/i2p/backends/registry.py`.
3. Add a fixture image under `tests/fixtures/` and a test in
   `tests/test_backends.py` that asserts the returned prompt is non-empty and
   under the token budget.

## PR checklist

- [ ] `pytest -q` passes
- [ ] `ruff check src tests` clean
- [ ] New backend has a registry entry + test
- [ ] CHANGELOG entry under `## Unreleased`
- [ ] No weights, no output images, no `config/local.yaml` committed

## Reporting bugs

Open an issue with: version (`i2p --version`), GPU/CPU, image sample (or a
reproducible noise image), and the full `logs/i2p.log` tail. Do not attach
NSFW test images — use a crop.