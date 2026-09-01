"""Application-wide constants and default configuration values."""


class AppConstants:
    """Centralized application constants."""

    # Application identity
    APP_NAME = "UPC Notepad"
    APP_VERSION = "2.0.0"
    APP_AUTHOR = "Daniel Bemba Malonda"
    ORG_NAME = "UPC"
    WINDOW_TITLE_TEMPLATE = "{filename} — {app_name}"

    # Editor defaults
    DEFAULT_FONT_FAMILY = "JetBrains Mono"
    FALLBACK_FONT_FAMILY = "Courier New"
    DEFAULT_FONT_SIZE = 13
    MIN_FONT_SIZE = 8
    MAX_FONT_SIZE = 72
    TAB_STOP_SPACES = 4

    # File handling
    FILE_FILTER = (
        "All Files (*);;"
        "Text Files (*.txt);;"
        "Python Files (*.py);;"
        "JSON Files (*.json);;"
        "HTML Files (*.html *.htm);;"
        "CSS Files (*.css);;"
        "JavaScript Files (*.js);;"
        "Markdown Files (*.md);;"
        "SQL Files (*.sql);;"
        "XML Files (*.xml);;"
        "YAML Files (*.yaml *.yml);;"
        "Log Files (*.log)"
    )
    MAX_RECENT_FILES = 10
    DEFAULT_ENCODING = "utf-8"

    # Auto-save
    AUTO_SAVE_INTERVAL_MS = 60_000  # 60 seconds

    # TTS defaults
    TTS_LOCALE = "en_US"
    TTS_RATE = -0.25
    TTS_VOLUME = 1.0
    TTS_PITCH = 0.0

    # Theme
    DEFAULT_THEME = "dark"

    # Syntax highlighting — extension to language mapping
    EXTENSION_LANGUAGE_MAP = {
        ".py": "python",
        ".pyw": "python",
        ".json": "json",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".js": "javascript",
        ".ts": "javascript",
        ".md": "markdown",
        ".markdown": "markdown",
        ".sql": "sql",
        ".xml": "xml",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".txt": "plain",
        ".log": "plain",
        ".sh": "bash",
        ".bash": "bash",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".java": "java",
        ".rs": "rust",
        ".go": "go",
        ".rb": "ruby",
        ".php": "php",
    }
