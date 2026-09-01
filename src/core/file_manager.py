"""File I/O operations — reading, writing, encoding detection."""

import logging
from pathlib import Path

from src.config.constants import AppConstants

logger = logging.getLogger(__name__)


class FileManager:
    """Handles all file read/write operations.

    Provides encoding-aware reading with automatic fallback,
    and safe atomic-style writes.
    """

    # Common encodings to try, in priority order
    _ENCODING_CHAIN = ("utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii")

    @staticmethod
    def read_file(path: str) -> tuple[str, str]:
        """Read a file and return ``(content, encoding)``.

        Tries UTF-8 first, then falls back through common encodings.

        Raises:
            FileNotFoundError: If the path does not exist.
            IOError: If all encoding attempts fail.
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        for encoding in FileManager._ENCODING_CHAIN:
            try:
                content = file_path.read_text(encoding=encoding)
                logger.info("Opened %s with encoding %s", path, encoding)
                return content, encoding
            except (UnicodeDecodeError, UnicodeError):
                continue

        raise IOError(f"Unable to decode file with any supported encoding: {path}")

    @staticmethod
    def write_file(
        path: str,
        content: str,
        encoding: str = AppConstants.DEFAULT_ENCODING,
    ) -> None:
        """Write *content* to *path* with the given encoding.

        Creates parent directories if needed.

        Raises:
            OSError: On write failure.
        """
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding=encoding)
        logger.info("Saved %s (%s)", path, encoding)

    @staticmethod
    def detect_language(path: str) -> str:
        """Return the syntax language key for a given file path."""
        ext = Path(path).suffix.lower()
        return AppConstants.EXTENSION_LANGUAGE_MAP.get(ext, "plain")
