"""Document model — tracks the state of a single open file."""

from pathlib import Path

from src.config.constants import AppConstants


class Document:
    """Represents an open document with its metadata.

    This is a pure data object with no Qt dependency, making it
    easy to test independently.
    """

    def __init__(self, path: str | None = None, encoding: str = AppConstants.DEFAULT_ENCODING):
        self._path: str | None = path
        self._encoding: str = encoding
        self._is_modified: bool = False
        self._language_override: str | None = None

    # ── Properties ──────────────────────────────────────────────

    @property
    def path(self) -> str | None:
        return self._path

    @path.setter
    def path(self, value: str | None) -> None:
        self._path = value
        self._language_override = None # Reset override when path changes

    @property
    def encoding(self) -> str:
        return self._encoding

    @encoding.setter
    def encoding(self, value: str) -> None:
        self._encoding = value

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    @is_modified.setter
    def is_modified(self, value: bool) -> None:
        self._is_modified = value

    @property
    def filename(self) -> str:
        """Return the display name (basename or 'Untitled')."""
        if self._path:
            return Path(self._path).name
        return "Untitled"

    @property
    def title(self) -> str:
        """Return a formatted window/tab title with modification indicator."""
        prefix = "● " if self._is_modified else ""
        return f"{prefix}{self.filename}"

    @property
    def language(self) -> str:
        """Infer syntax language from file extension or use override."""
        if self._language_override:
            return self._language_override
        if not self._path:
            return "plain"
        ext = Path(self._path).suffix.lower()
        return AppConstants.EXTENSION_LANGUAGE_MAP.get(ext, "plain")

    @language.setter
    def language(self, value: str) -> None:
        self._language_override = value

    def __repr__(self) -> str:
        return f"Document(path={self._path!r}, modified={self._is_modified})"
