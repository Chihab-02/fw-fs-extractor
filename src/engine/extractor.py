"""Filesystem extractor - wraps binwalk extract with progress callbacks."""

import threading
from pathlib import Path
from typing import Callable

from src.utils.binwalk_wrapper import run_extract


def extract_firmware(
    firmware_path: Path,
    output_dir: Path,
    on_progress: Callable[[str, int, str], None],
    on_complete: Callable[[Path], None],
    cancelled: Callable[[], bool],
) -> threading.Thread:
    """
    Extract firmware in a background thread.
    on_progress(phase, percent, message); on_complete(output_path).
    Returns the thread (caller should start it).
    """
    def on_line(line: str) -> None:
        # Estimate: extraction typically 50-100%
        on_progress("extract", 75, line)

    def on_extract_done(path: Path) -> None:
        on_progress("extract", 100, "Extraction complete.")
        on_complete(path)

    thread = threading.Thread(
        target=run_extract,
        args=(firmware_path, output_dir, on_line, on_extract_done, cancelled),
        daemon=True,
    )
    return thread
