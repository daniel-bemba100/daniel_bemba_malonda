"""Text statistics — word count, character count, line count."""


class TextStatistics:
    """Computes statistics for a given text string."""

    @staticmethod
    def compute(text: str) -> dict[str, int]:
        """Return a dict with 'lines', 'words', 'chars', 'chars_no_spaces'."""
        lines = text.count("\n") + 1 if text else 0
        words = len(text.split()) if text else 0
        chars = len(text)
        chars_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
        return {
            "lines": lines,
            "words": words,
            "chars": chars,
            "chars_no_spaces": chars_no_spaces,
        }

    @staticmethod
    def summary(text: str) -> str:
        """Return a human-readable summary string."""
        stats = TextStatistics.compute(text)
        return (
            f"Lines: {stats['lines']}  │  "
            f"Words: {stats['words']}  │  "
            f"Chars: {stats['chars']}"
        )
