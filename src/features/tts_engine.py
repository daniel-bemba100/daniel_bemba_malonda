"""Text-to-Speech engine with clean, professional Google-quality reading.

Architecture:
 - Primary engine: gTTS (Google Text-to-Speech) → generates MP3 per sentence
   → played back via ffplay subprocess.  Same neural voice quality as the
   export feature.
 - Offline fallback: espeak subprocess (for when there is no internet).
 - Text is pre-processed to strip symbols that should not be read aloud.
 - Sentences are spoken one-by-one so:
     • Each sentence is clear with natural inter-sentence pauses.
     • The stop button works instantly (kill the ffplay/espeak subprocess).
"""

import logging
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

from src.config.constants import AppConstants

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
#  Text Preprocessing
# ──────────────────────────────────────────────────────────────

# Characters that TTS should never pronounce but that serve as
# natural pause boundaries.  We replace them with commas so the
# engine pauses briefly.
_PAUSE_SYMBOLS = re.compile(r'[;:\-–—/\\|]')

# Characters that should be silently stripped (no pause).
_STRIP_SYMBOLS = re.compile(r'[#*&@^~`<>{}()\[\]""''\u200b\u00a0]')

# Quotes that are NOT contractions (standalone or around words)
_STANDALONE_QUOTES = re.compile(r"(?<!\w)['\"]|['\"](?!\w)")

# Collapse multiple whitespace / newlines into a single space.
_WHITESPACE = re.compile(r'\s+')

# Detect sentence boundaries (period, question mark, exclamation mark
# optionally followed by closing quotes or parentheses, then whitespace
# or end-of-string).
_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')

# Numbered / bulleted list items: "1.", "2)", "a.", "-", "•"
_LIST_MARKER = re.compile(r'^\s*(?:\d+[.)]\s*|[a-zA-Z][.)]\s*|[-•]\s*)')

# Ellipsis normalization
_ELLIPSIS = re.compile(r'\.{2,}')

# Repeated punctuation (e.g. "!!!" -> "!")
_REPEATED_PUNCT = re.compile(r'([!?.])\1+')

# URLs
_URL = re.compile(r'https?://\S+|www\.\S+', re.IGNORECASE)

# Email addresses
_EMAIL = re.compile(r'\S+@\S+\.\S+')


def preprocess_text(text: str) -> str:
    """Clean *text* so it reads naturally when spoken aloud.

    The goal is to produce plain, speakable prose:
    - Remove symbols that would be pronounced awkwardly.
    - Preserve periods, commas, question-/exclamation marks for pauses.
    - Collapse whitespace.
    """
    if not text:
        return ""

    # Replace URLs with a placeholder
    text = _URL.sub('link', text)

    # Replace email addresses
    text = _EMAIL.sub('email address', text)

    # Normalize ellipsis to a single period
    text = _ELLIPSIS.sub('.', text)

    # Reduce repeated punctuation
    text = _REPEATED_PUNCT.sub(r'\1', text)

    # Remove list markers
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = _LIST_MARKER.sub('', line)
        cleaned_lines.append(line)
    text = ' '.join(cleaned_lines)

    # Replace pause-worthy symbols with a comma (the engine will pause)
    text = _PAUSE_SYMBOLS.sub(',', text)

    # Silently remove symbols that have no spoken equivalent
    text = _STRIP_SYMBOLS.sub(' ', text)

    # Remove quotes that are NOT contractions (e.g. "hello" but keep they're)
    text = _STANDALONE_QUOTES.sub(' ', text)

    # Collapse whitespace
    text = _WHITESPACE.sub(' ', text).strip()

    # Clean up comma-space runs produced by replacements (",,," -> ",")
    text = re.sub(r',(\s*,)+', ',', text)
    # Remove leading/trailing commas from sentences
    text = re.sub(r'(^|[.!?]\s*),\s*', r'\1', text)

    return text


def split_sentences(text: str) -> list[str]:
    """Split *text* into a list of sentences for piecemeal reading."""
    sentences = _SENTENCE_SPLIT.split(text)
    # Filter out blanks and very short fragments
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 1]


# ──────────────────────────────────────────────────────────────
#  TTS Engine
# ──────────────────────────────────────────────────────────────

class TTSEngine:
    """Encapsulates all text-to-speech functionality.

    Preferred backend order:
      1. gTTS + ffplay      (Google neural voice — professional quality)
      2. espeak subprocess   (offline fallback)
    """

    def __init__(self, parent: QWidget) -> None:
        self._parent = parent
        self._engine_name = "none"
        self._read_worker: Optional[QThread] = None

        # Check available backends in order of quality
        has_gtts = False
        try:
            from gtts import gTTS  # noqa: F401
            has_gtts = True
        except ImportError:
            pass

        ffplay_path = shutil.which("ffplay")
        espeak_path = shutil.which("espeak-ng") or shutil.which("espeak")

        if has_gtts and ffplay_path:
            self._engine_name = "gtts"
            self._ffplay_path = ffplay_path
            logger.info("Using Google TTS engine (gTTS + ffplay)")
        elif espeak_path:
            self._engine_name = "espeak"
            self._espeak_path = espeak_path
            logger.info("Using espeak subprocess engine (%s)", espeak_path)
        else:
            try:
                import pyttsx3  # noqa: F401
                self._engine_name = "pyttsx3"
                logger.info("Using pyttsx3 fallback engine")
            except ImportError:
                logger.warning("No TTS engine is available.")

        # Keep espeak path for offline fallback even if gTTS is primary
        self._espeak_path = espeak_path or ""

    def say(self, text: str) -> None:
        """Speak *text* aloud in a background thread."""
        if self._engine_name == "none":
            QMessageBox.warning(
                self._parent, "TTS Unavailable",
                "No Text-to-Speech engine is installed on this system.\n"
                "Install gTTS: pip install gTTS\n"
                "Or espeak-ng: sudo apt install espeak-ng",
            )
            return

        text = text.strip()
        if not text:
            return

        # Stop any currently playing audio first
        self.stop()

        cleaned = preprocess_text(text)
        sentences = split_sentences(cleaned)
        if not sentences:
            sentences = [cleaned] if cleaned else []

        if not sentences:
            return

        if self._engine_name == "gtts":
            self._read_worker = GoogleTTSReadWorker(
                sentences, self._ffplay_path, self._espeak_path,
            )
        elif self._engine_name == "espeak":
            self._read_worker = EspeakReadWorker(
                sentences, self._espeak_path,
            )
        else:
            self._read_worker = Pyttsx3ReadWorker(sentences)

        self._read_worker.start()

    def stop(self) -> None:
        """Immediately stop any in-progress reading."""
        if self._read_worker is not None:
            self._read_worker.request_stop()
            # Give it a moment to clean up, then force-quit if needed
            if not self._read_worker.wait(500):
                self._read_worker.terminate()
                self._read_worker.wait(200)
            self._read_worker = None

    def is_speaking(self) -> bool:
        return self._read_worker is not None and self._read_worker.isRunning()

    # ── Audio Export ─────────────────────────────────────────

    def export_to_mp3(self, text: str) -> None:
        """Convert text to MP3 using gTTS in a background thread."""
        if not text.strip():
            logger.warning("No text to convert")
            QMessageBox.warning(self._parent, "Export", "No text to convert.")
            return

        try:
            from gtts import gTTS  # noqa: F401
        except ImportError:
            logger.error("gTTS not installed — cannot export audio")
            QMessageBox.critical(
                self._parent, "Export Error",
                "gTTS is not installed. Please run 'pip install gTTS'.",
            )
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self._parent, "Save Audio", "",
            "MP3 Files (*.mp3);;All Files (*)",
        )
        if not save_path:
            return

        from PyQt6.QtWidgets import QProgressDialog
        from PyQt6.QtCore import Qt

        self._progress = QProgressDialog(
            "Converting text to audio...", "Cancel", 0, 100, self._parent,
        )
        self._progress.setWindowTitle("Exporting Audio")
        self._progress.setWindowModality(Qt.WindowModality.WindowModal)
        self._progress.setAutoClose(True)
        self._progress.setAutoReset(True)
        self._progress.setValue(0)
        self._progress.show()

        self._export_worker = TTSExportWorker(text, save_path)
        self._export_worker.progress.connect(self._progress.setValue)
        self._export_worker.finished.connect(self._on_export_finished)
        self._export_worker.error.connect(self._on_export_error)
        self._progress.canceled.connect(self._export_worker.cancel)

        self._export_worker.start()

    def _on_export_finished(self, save_path: str) -> None:
        if self._progress:
            self._progress.setValue(100)
        logger.info("Audio exported to %s", save_path)
        QMessageBox.information(
            self._parent, "Export Complete",
            f"Audio successfully exported to:\n{save_path}",
        )

    def _on_export_error(self, error_msg: str) -> None:
        if self._progress:
            self._progress.cancel()
        logger.error("TTS export failed: %s", error_msg)
        QMessageBox.critical(
            self._parent, "Export Error",
            f"An error occurred during export:\n{error_msg}",
        )


# ──────────────────────────────────────────────────────────────
#  Google TTS Read Worker  (primary — professional quality)
# ──────────────────────────────────────────────────────────────

class GoogleTTSReadWorker(QThread):
    """Reads sentences using Google TTS (gTTS) + ffplay.

    For each sentence:
      1. gTTS generates an MP3 in a temp file.
      2. ffplay plays it back (no window, quiet mode).
      3. Temp file is cleaned up immediately after playback.

    Benefits:
      • Same professional Google neural voice as the export feature.
      • Instant stop — kill the ffplay subprocess.
      • Sentence-by-sentence for natural rhythm.
    If gTTS fails (no internet), falls back to espeak for that sentence.
    """

    def __init__(self, sentences: list[str], ffplay_path: str,
                 espeak_fallback_path: str = ""):
        super().__init__()
        self._sentences = sentences
        self._ffplay_path = ffplay_path
        self._espeak_fallback = espeak_fallback_path
        self._stop_requested = False
        self._process: Optional[subprocess.Popen] = None
        self._mutex = QMutex()
        self._temp_files: list[str] = []

    def request_stop(self) -> None:
        self._stop_requested = True
        with QMutexLocker(self._mutex):
            if self._process is not None:
                try:
                    os.killpg(os.getpgid(self._process.pid), signal.SIGKILL)
                except (ProcessLookupError, OSError):
                    try:
                        self._process.kill()
                    except Exception:
                        pass
        # Clean up any remaining temp files
        self._cleanup_temp_files()

    def _cleanup_temp_files(self) -> None:
        """Remove all temporary MP3 files."""
        for f in self._temp_files:
            try:
                if os.path.exists(f):
                    os.unlink(f)
            except OSError:
                pass
        self._temp_files.clear()

    def run(self) -> None:
        try:
            from gtts import gTTS
        except ImportError:
            logger.error("gTTS not available for reading")
            return

        try:
            for sentence in self._sentences:
                if self._stop_requested:
                    break

                # Generate MP3 for this sentence
                tmp_file = None
                try:
                    tmp_fd, tmp_path = tempfile.mkstemp(
                        suffix='.mp3', prefix='tts_'
                    )
                    os.close(tmp_fd)
                    tmp_file = tmp_path
                    self._temp_files.append(tmp_path)

                    if self._stop_requested:
                        break

                    tts = gTTS(text=sentence, lang='en', tld='us', slow=False)
                    tts.save(tmp_path)

                    if self._stop_requested:
                        break

                    # Play the MP3 with ffplay
                    cmd = [
                        self._ffplay_path,
                        '-nodisp',      # No video window
                        '-autoexit',    # Exit when done
                        '-loglevel', 'quiet',  # No console output
                        tmp_path,
                    ]

                    with QMutexLocker(self._mutex):
                        if self._stop_requested:
                            break
                        self._process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            preexec_fn=os.setsid,
                        )

                    self._process.wait()

                    with QMutexLocker(self._mutex):
                        self._process = None

                except Exception as e:
                    if self._stop_requested:
                        break
                    logger.warning(
                        "gTTS failed for sentence, falling back to espeak: %s",
                        e,
                    )
                    # Fallback to espeak for this sentence
                    if self._espeak_fallback:
                        self._speak_espeak(sentence)
                finally:
                    # Clean up this sentence's temp file
                    if tmp_file and os.path.exists(tmp_file):
                        try:
                            os.unlink(tmp_file)
                            if tmp_file in self._temp_files:
                                self._temp_files.remove(tmp_file)
                        except OSError:
                            pass

                if self._stop_requested:
                    break

                # Brief inter-sentence pause for natural rhythm
                time.sleep(0.15)

        except Exception as e:
            if not self._stop_requested:
                logger.error("GoogleTTSReadWorker error: %s", e)
        finally:
            self._cleanup_temp_files()

    def _speak_espeak(self, sentence: str) -> None:
        """Fallback: speak a single sentence via espeak."""
        if not self._espeak_fallback or self._stop_requested:
            return
        cmd = [
            self._espeak_fallback,
            '-v', 'en-us', '-s', '145', '-p', '45',
            '-a', '95', '-g', '8', '--', sentence,
        ]
        with QMutexLocker(self._mutex):
            if self._stop_requested:
                return
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid,
            )
        self._process.wait()
        with QMutexLocker(self._mutex):
            self._process = None


# ──────────────────────────────────────────────────────────────
#  espeak Subprocess Worker  (offline fallback)
# ──────────────────────────────────────────────────────────────

class EspeakReadWorker(QThread):
    """Reads sentences one-by-one via espeak subprocess.

    Used as offline fallback when gTTS/ffplay are not available.
    """

    def __init__(self, sentences: list[str], espeak_path: str):
        super().__init__()
        self._sentences = sentences
        self._espeak_path = espeak_path
        self._stop_requested = False
        self._process: Optional[subprocess.Popen] = None
        self._mutex = QMutex()

    def request_stop(self) -> None:
        self._stop_requested = True
        with QMutexLocker(self._mutex):
            if self._process is not None:
                try:
                    os.killpg(os.getpgid(self._process.pid), signal.SIGKILL)
                except (ProcessLookupError, OSError):
                    try:
                        self._process.kill()
                    except Exception:
                        pass

    def run(self) -> None:
        try:
            for sentence in self._sentences:
                if self._stop_requested:
                    break

                cmd = [
                    self._espeak_path,
                    '-v', 'en-us',
                    '-s', '145',
                    '-p', '45',
                    '-a', '95',
                    '-g', '8',
                    '--',
                    sentence,
                ]

                with QMutexLocker(self._mutex):
                    if self._stop_requested:
                        break
                    self._process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        preexec_fn=os.setsid,
                    )

                self._process.wait()

                with QMutexLocker(self._mutex):
                    self._process = None

                if self._stop_requested:
                    break

                # Brief inter-sentence pause for natural rhythm
                time.sleep(0.25)

        except Exception as e:
            if not self._stop_requested:
                logger.error("EspeakReadWorker error: %s", e)


# ──────────────────────────────────────────────────────────────
#  pyttsx3 Fallback Worker  (last resort)
# ──────────────────────────────────────────────────────────────

class Pyttsx3ReadWorker(QThread):
    """Reads sentences using pyttsx3, one at a time for stoppability."""

    def __init__(self, sentences: list[str]):
        super().__init__()
        self._sentences = sentences
        self._stop_requested = False
        self._engine = None

    def request_stop(self) -> None:
        self._stop_requested = True
        if self._engine is not None:
            try:
                self._engine.stop()
            except Exception:
                pass

    def run(self) -> None:
        try:
            import pyttsx3
            self._engine = pyttsx3.init()

            # Tuning for smoother output
            self._engine.setProperty('rate', 140)
            self._engine.setProperty('volume', 0.95)

            # Find an American English voice
            voices = self._engine.getProperty('voices')
            for voice in voices:
                vid = voice.id.lower()
                if 'en-us' in vid or 'en_us' in vid:
                    self._engine.setProperty('voice', voice.id)
                    break

            for sentence in self._sentences:
                if self._stop_requested:
                    break
                self._engine.say(sentence)
                self._engine.runAndWait()

                if self._stop_requested:
                    break

        except Exception as e:
            if not self._stop_requested:
                logger.error("Pyttsx3ReadWorker error: %s", e)
        finally:
            if self._engine is not None:
                try:
                    self._engine.stop()
                except Exception:
                    pass
                self._engine = None


# ──────────────────────────────────────────────────────────────
#  gTTS Export Worker
# ──────────────────────────────────────────────────────────────

class TTSExportWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, text: str, save_path: str):
        super().__init__()
        self.text = text
        self.save_path = save_path
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            from gtts import gTTS
            import shutil as _shutil

            # Pre-process the text for cleaner export too
            cleaned = preprocess_text(self.text)

            # Split text into chunks to provide progress updates
            chunks = [c.strip() for c in cleaned.split('\n') if c.strip()]
            if not chunks:
                chunks = [cleaned] if cleaned else []
            if not chunks:
                self.error.emit("No valid text to convert.")
                return

            total_chunks = len(chunks)
            tmp_path = Path("output_temp.mp3")

            if tmp_path.exists():
                tmp_path.unlink()

            with open(tmp_path, 'wb') as outfile:
                for i, chunk in enumerate(chunks):
                    if self._is_cancelled:
                        break

                    tts = gTTS(text=chunk, lang="en", tld="us")
                    tts.write_to_fp(outfile)

                    percent = int(((i + 1) / total_chunks) * 100)
                    self.progress.emit(percent)

            if self._is_cancelled:
                if tmp_path.exists():
                    tmp_path.unlink()
                return

            _shutil.copy(str(tmp_path), self.save_path)
            tmp_path.unlink(missing_ok=True)

            self.finished.emit(self.save_path)

        except Exception as e:
            self.error.emit(str(e))
