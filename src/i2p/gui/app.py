"""PySide6 desktop shell for image-to-prompt-reverse."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from i2p.config.loader import load_config
from i2p.core.pipeline import ReversePipeline


class _Worker(QThread):
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, pipe: ReversePipeline, image: Path, backend: str) -> None:
        super().__init__()
        self.pipe, self.image, self.backend = pipe, image, backend

    def run(self) -> None:
        try:
            self.done.emit(self.pipe.run(self.image, backend=self.backend).prompt)
        except Exception as exc:  # noqa: BLE001 — surface