"""Resource path resolution that works in both dev and PyInstaller modes."""

import sys
from pathlib import Path


def get_project_root() -> Path:
    """Return the project root directory.

    When bundled with PyInstaller, ``sys._MEIPASS`` is the temp extraction dir.
    In development, we walk up from this file.
    """
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller bundle
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent.parent


def resource_path(relative: str) -> Path:
    """Resolve a path relative to the project root."""
    return get_project_root() / relative


def icon_path(name: str = "upc.png") -> Path:
    """Shorthand for icon resources."""
    return resource_path(f"resources/icons/{name}")


def theme_path(name: str) -> Path:
    """Shorthand for theme stylesheet resources."""
    return resource_path(f"resources/themes/{name}.qss")
