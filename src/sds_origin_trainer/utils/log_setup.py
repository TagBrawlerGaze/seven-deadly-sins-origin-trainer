from __future__ import annotations

import logging
import sys
from pathlib import Path


def setup_logging(log_dir: Path | None = None, level: int = logging.INFO) -> None:
    fmt = "%(asctime)s %(levelname)-7s %(name)-24s %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_dir / "trainer.log", encoding="utf-8"))
    logging.basicConfig(level=level, format=fmt, handlers=handlers, force=True)