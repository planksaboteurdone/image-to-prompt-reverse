"""Allow `python -m i2p` to launch the CLI."""
from i2p.cli import main

if __name__ == "__main__":
    raise SystemExit(main())