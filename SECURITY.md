# Security Policy

## Supported versions

| Version      | Supported |
|--------------|-----------|
| 2026.x       | ✅        |
| 2025.x       | ❌        |

## Reporting a vulnerability

Email `security@image-to-prompt-reverse.dev` (PGP key in `docs/pgp.asc`).
Do **not** open a public issue for anything exploitable. We respond within
72 hours.

## Threat model

image-to-prompt-reverse is a **local, offline-first** desktop tool. It does
not phone home. The attack surface we care about:

- **Model weight loading** — `safetensors` only by default. `torch.load` is
  gated behind `I2P_ALLOW_PICKLE=1` and logs a loud warning, because pickle
  deserialization is arbitrary code execution. Don't ship a `.bin`.
- **Image parsing** — Pillow is pinned; we disable the `EPS`/`FLI` plugins
  that have historically had RCEs. See `src/i2p/services/image_loader.py`.
- **Plugin backends** — third-party backends are imported via entry points
  and run in the same process. Only install plugins you trust.
- **Config injection** — `config/local.yaml` is user-owned; we never eval it.

## Out of scope

- Prompt content itself. The tool reverse-engineers prompts; what you do with
  the output is your business.
- NSFW classification accuracy. We surface a score, we don't judge.

## Hardening tips

- Run with `--no-network` to hard-disable the HF downloader.
- Keep `models/weights/` on a read-only mount if you're paranoid.
- Verify weight checksums against `models/manifest.json`.