"""Orchestrator - coordinates scan then extract, runs in background, forwards events to GUI."""

import queue
import threading
from pathlib import Path
from typing import Callable, Optional

from src.engine.extractor import extract_firmware
from src.engine.scanner import scan_firmware


# Event types for GUI thread
PROGRESS = "progress"
SCAN_COMPLETE = "scan_complete"
EXTRACT_COMPLETE = "extract_complete"
CANCELLED = "cancelled"
ERROR = "error"


class Orchestrator:
    """Runs scan + extract in worker thread, pushes events to queue for GUI."""

    def __init__(self, event_queue: queue.Queue) -> None:
        self._queue = event_queue
        self._cancelled = threading.Event()
        self._worker: Optional[threading.Thread] = None

    def _put(self, event_type: str, **kwargs: object) -> None:
        self._queue.put((event_type, kwargs))

    def _on_progress(self, phase: str, percent: int, message: str) -> None:
        self._put(PROGRESS, phase=phase, percent=percent, message=message)

    def _on_scan_complete(self, results: list[dict]) -> None:
        self._put(SCAN_COMPLETE, results=results)

    def _on_extract_complete(self, path: Path) -> None:
        self._put(EXTRACT_COMPLETE, path=path)

    def run(self, firmware_path: Path, output_dir: Path) -> None:
        """Start scan + extract in background. Events go to event_queue."""
        self._cancelled.clear()

        def cancelled() -> bool:
            return self._cancelled.is_set()

        def worker() -> None:
            try:
                # Phase 1: Scan
                def on_scan_done(results: list[dict]) -> None:
                    self._put(SCAN_COMPLETE, results=results)

                scan_thread = scan_firmware(
                    firmware_path,
                    on_progress=self._on_progress,
                    on_complete=on_scan_done,
                    cancelled=cancelled,
                )
                scan_thread.start()
                scan_thread.join()
                if cancelled():
                    self._put(CANCELLED)
                    return

                # Phase 2: Extract
                extract_thread = extract_firmware(
                    firmware_path,
                    output_dir,
                    on_progress=self._on_progress,
                    on_complete=self._on_extract_complete,
                    cancelled=cancelled,
                )
                extract_thread.start()
                extract_thread.join()
                if cancelled():
                    self._put(CANCELLED)
            except Exception as e:
                self._put(ERROR, message=str(e))

        self._worker = threading.Thread(target=worker, daemon=True)
        self._worker.start()

    def cancel(self) -> None:
        """Signal worker to cancel."""
        self._cancelled.set()
