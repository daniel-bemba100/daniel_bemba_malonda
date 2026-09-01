"""Syntax highlighter supporting multiple languages."""

from PyQt6.QtCore import QRegularExpression, Qt
from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QTextDocument


def _fmt(color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
    """Create a QTextCharFormat with the given style."""
    fmt = QTextCharFormat()
    fmt.setForeground(QColor(color))
    if bold:
        fmt.setFontWeight(QFont.Weight.Bold)
    if italic:
        fmt.setFontItalic(True)
    return fmt


# ── Dark-theme color palette (Monokai-inspired) ────────────────

STYLES = {
    "keyword":    _fmt("#F92672", bold=True),
    "builtin":    _fmt("#66D9EF"),
    "string":     _fmt("#E6DB74"),
    "comment":    _fmt("#75715E", italic=True),
    "number":     _fmt("#AE81FF"),
    "decorator":  _fmt("#A6E22E", italic=True),
    "class_name": _fmt("#A6E22E", bold=True),
    "func_name":  _fmt("#66D9EF"),
    "operator":   _fmt("#F92672"),
    "brace":      _fmt("#F8F8F2"),
    "self":       _fmt("#FD971F", italic=True),
    "tag":        _fmt("#F92672", bold=True),
    "attribute":  _fmt("#A6E22E"),
    "value":      _fmt("#E6DB74"),
    "selector":   _fmt("#F92672"),
    "property":   _fmt("#66D9EF"),
}


# ── Language rule sets ──────────────────────────────────────────

def _python_rules() -> list[tuple[str, QTextCharFormat]]:
    keywords = [
        "False", "None", "True", "and", "as", "assert", "async", "await",
        "break", "class", "continue", "def", "del", "elif", "else",
        "except", "finally", "for", "from", "global", "if", "import",
        "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise",
        "return", "try", "while", "with", "yield", "match", "case",
    ]
    builtins = [
        "abs", "all", "any", "bin", "bool", "bytearray", "bytes",
        "callable", "chr", "classmethod", "compile", "complex", "dict",
        "dir", "divmod", "enumerate", "eval", "exec", "filter", "float",
        "format", "frozenset", "getattr", "globals", "hasattr", "hash",
        "hex", "id", "input", "int", "isinstance", "issubclass", "iter",
        "len", "list", "locals", "map", "max", "memoryview", "min",
        "next", "object", "oct", "open", "ord", "pow", "print",
        "property", "range", "repr", "reversed", "round", "set",
        "setattr", "slice", "sorted", "staticmethod", "str", "sum",
        "super", "tuple", "type", "vars", "zip",
    ]
    rules = []
    rules += [(rf"\b{kw}\b", STYLES["keyword"]) for kw in keywords]
    rules += [(rf"\b{bi}\b", STYLES["builtin"]) for bi in builtins]
    rules += [
        (r"\bself\b", STYLES["self"]),
        (r"\bcls\b", STYLES["self"]),
        (r"@\w+", STYLES["decorator"]),
        (r"\bclass\s+(\w+)", STYLES["class_name"]),
        (r"\bdef\s+(\w+)", STYLES["func_name"]),
        (r"\b[0-9]+\.?[0-9]*([eE][+-]?[0-9]+)?\b", STYLES["number"]),
        (r"0[xX][0-9A-Fa-f]+\b", STYLES["number"]),
        (r"0[oO][0-7]+\b", STYLES["number"]),
        (r"0[bB][01]+\b", STYLES["number"]),
        (r'\"\"\"[^\"]*\"\"\"', STYLES["string"]),
        (r"\'\'\'[^\']*\'\'\'", STYLES["string"]),
        (r'"[^"\\]*(\\.[^"\\]*)*"', STYLES["string"]),
        (r"'[^'\\]*(\\.[^'\\]*)*'", STYLES["string"]),
        (r"#[^\n]*", STYLES["comment"]),
        (r"[+\-*/%=<>!&|^~]", STYLES["operator"]),
        (r"[\{\}\(\)\[\]]", STYLES["brace"]),
    ]
    return rules


def _json_rules() -> list[tuple[str, QTextCharFormat]]:
    return [
        (r'"[^"\\]*(\\.[^"\\]*)*"\s*:', STYLES["keyword"]),
        (r'"[^"\\]*(\\.[^"\\]*)*"', STYLES["string"]),
        (r"\b(true|false|null)\b", STYLES["builtin"]),
        (r"\b-?[0-9]+\.?[0-9]*([eE][+-]?[0-9]+)?\b", STYLES["number"]),
        (r"[\{\}\[\],:]", STYLES["brace"]),
    ]


def _html_rules() -> list[tuple[str, QTextCharFormat]]:
    return [
        (r"</?[a-zA-Z][a-zA-Z0-9]*", STYLES["tag"]),
        (r"/?>", STYLES["tag"]),
        (r'\b[a-zA-Z\-]+(?==)', STYLES["attribute"]),
        (r'"[^"]*"', STYLES["string"]),
        (r"'[^']*'", STYLES["string"]),
        (r"<!--.*?-->", STYLES["comment"]),
    ]


def _css_rules() -> list[tuple[str, QTextCharFormat]]:
    return [
        (r"[.#]?[a-zA-Z_][\w\-]*(?=\s*\{)", STYLES["selector"]),
        (r"[a-zA-Z\-]+(?=\s*:)", STYLES["property"]),
        (r'"[^"]*"', STYLES["string"]),
        (r"'[^']*'", STYLES["string"]),
        (r"\b[0-9]+\.?[0-9]*(px|em|rem|%|vh|vw|s|ms)?\b", STYLES["number"]),
        (r"#[0-9A-Fa-f]{3,8}\b", STYLES["number"]),
        (r"/\*.*?\*/", STYLES["comment"]),
    ]


def _javascript_rules() -> list[tuple[str, QTextCharFormat]]:
    keywords = [
        "async", "await", "break", "case", "catch", "class", "const",
        "continue", "debugger", "default", "delete", "do", "else",
        "export", "extends", "finally", "for", "from", "function", "if",
        "import", "in", "instanceof", "let", "new", "of", "return",
        "static", "super", "switch", "this", "throw", "try", "typeof",
        "var", "void", "while", "with", "yield",
    ]
    builtins = [
        "Array", "Boolean", "Date", "Error", "Function", "JSON", "Map",
        "Math", "Number", "Object", "Promise", "Proxy", "RegExp", "Set",
        "String", "Symbol", "console", "document", "window",
        "true", "false", "null", "undefined", "NaN", "Infinity",
    ]
    rules = []
    rules += [(rf"\b{kw}\b", STYLES["keyword"]) for kw in keywords]
    rules += [(rf"\b{bi}\b", STYLES["builtin"]) for bi in builtins]
    rules += [
        (r"\b[0-9]+\.?[0-9]*([eE][+-]?[0-9]+)?\b", STYLES["number"]),
        (r'"[^"\\]*(\\.[^"\\]*)*"', STYLES["string"]),
        (r"'[^'\\]*(\\.[^'\\]*)*'", STYLES["string"]),
        (r"`[^`]*`", STYLES["string"]),
        (r"//[^\n]*", STYLES["comment"]),
        (r"/\*.*?\*/", STYLES["comment"]),
        (r"[+\-*/%=<>!&|^~?:]", STYLES["operator"]),
        (r"[\{\}\(\)\[\]]", STYLES["brace"]),
    ]
    return rules


def _sql_rules() -> list[tuple[str, QTextCharFormat]]:
    keywords = [
        "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE",
        "SET", "DELETE", "CREATE", "TABLE", "ALTER", "DROP", "INDEX",
        "JOIN", "INNER", "LEFT", "RIGHT", "OUTER", "ON", "AND", "OR",
        "NOT", "IN", "BETWEEN", "LIKE", "IS", "NULL", "AS", "ORDER",
        "BY", "GROUP", "HAVING", "LIMIT", "OFFSET", "UNION", "ALL",
        "DISTINCT", "EXISTS", "CASE", "WHEN", "THEN", "ELSE", "END",
        "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "CONSTRAINT",
        "DEFAULT", "AUTO_INCREMENT", "VARCHAR", "INT", "TEXT", "BOOLEAN",
        "FLOAT", "DATE", "DATETIME", "TIMESTAMP",
    ]
    rules = [(rf"\b{kw}\b", STYLES["keyword"]) for kw in keywords]
    # Case-insensitive duplicates
    rules += [(rf"\b{kw.lower()}\b", STYLES["keyword"]) for kw in keywords]
    rules += [
        (r"'[^'\\]*(\\.[^'\\]*)*'", STYLES["string"]),
        (r'"[^"\\]*(\\.[^"\\]*)*"', STYLES["string"]),
        (r"\b[0-9]+\.?[0-9]*\b", STYLES["number"]),
        (r"--[^\n]*", STYLES["comment"]),
        (r"/\*.*?\*/", STYLES["comment"]),
    ]
    return rules


def _markdown_rules() -> list[tuple[str, QTextCharFormat]]:
    return [
        (r"^#{1,6}\s.*$", STYLES["keyword"]),
        (r"\*\*[^*]+\*\*", _fmt("#F8F8F2", bold=True)),
        (r"\*[^*]+\*", _fmt("#F8F8F2", italic=True)),
        (r"`[^`]+`", STYLES["string"]),
        (r"^\s*[-*+]\s", STYLES["operator"]),
        (r"^\s*\d+\.\s", STYLES["number"]),
        (r"\[.*?\]\(.*?\)", STYLES["builtin"]),
    ]


_LANGUAGE_RULES = {
    "python": _python_rules,
    "json": _json_rules,
    "html": _html_rules,
    "css": _css_rules,
    "javascript": _javascript_rules,
    "sql": _sql_rules,
    "markdown": _markdown_rules,
}


class SyntaxHighlighter(QSyntaxHighlighter):
    """Multi-language syntax highlighter.

    Call ``set_language(lang)`` to switch the active rule set.
    """

    def __init__(self, document: QTextDocument, language: str = "plain"):
        super().__init__(document)
        self._rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self.set_language(language)

    def set_language(self, language: str) -> None:
        """Switch to the rule set for *language*."""
        self._rules = []
        rule_factory = _LANGUAGE_RULES.get(language)
        if rule_factory:
            for pattern, fmt in rule_factory():
                regex = QRegularExpression(pattern)
                self._rules.append((regex, fmt))
        self.rehighlight()

    def highlightBlock(self, text: str) -> None:
        for regex, fmt in self._rules:
            it = regex.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
