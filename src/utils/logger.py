"""Application-wide logging configuration."""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure the root logger with a clean console handler."""
    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers on re-init
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
