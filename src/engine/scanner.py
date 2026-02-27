"""Signature scanner - wraps binwalk scan with progress callbacks."""

import threading
from pathlib import Path
from typing import Callable, Optional

from src.utils.binwalk_wrapper import run_scan


def scan_firmware(
    firmware_path: Path,
    on_progress: Callable[[str, int, str], None],
    on_complete: Callable[[list[dict]], None],
    cancelled: Callable[[], bool],
) -> threading.Thread:
    """
    Scan firmware in a background thread.
    on_progress(phase, percent, message); on_complete(scan_results).
    Returns the thread (caller should start it).
    """
    lines: list[str] = []

    def on_line(line: str) -> None:
        lines.append(line)
        # Estimate progress: we don't know total, use 0-50% during scan
        on_progress("scan", min(50, 10 + len(lines) % 40), line)

    def on_scan_done(results: list[dict]) -> None:
        on_progress("scan", 100, "Scan complete.")
        on_complete(results)

    thread = threading.Thread(
        target=run_scan,
        args=(firmware_path, on_line, on_scan_done, cancelled),
        daemon=True,
    )
    return thread
