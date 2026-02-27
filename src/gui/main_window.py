"""Main application window."""

import queue
from pathlib import Path
from typing import Optional

import customtkinter as ctk

from src.engine.orchestrator import Orchestrator
from src.gui.file_picker import FilePicker
from src.gui.progress_panel import ProgressPanel
from src.gui.results_view import ResultsView


class MainWindow:
    """Main application window with file picker, progress, and results."""

    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.root.title("Firmware FS Extractor")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)

        self._event_queue: queue.Queue = queue.Queue()
        self._orchestrator: Optional[Orchestrator] = None

        # Top: file picker
        self._file_picker = FilePicker(
            root,
            on_file_selected=lambda _: None,
        )
        self._file_picker.pack(fill="x", padx=20, pady=(20, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(root, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 10))

        self._extract_btn = ctk.CTkButton(
            btn_frame,
            text="Scan & Extract",
            command=self._on_extract,
        )
        self._extract_btn.pack(side="left", padx=(0, 5))

        self._cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self._on_cancel,
            state="disabled",
        )
        self._cancel_btn.pack(side="left")

        # Progress panel
        self._progress_panel = ProgressPanel(root)
        self._progress_panel.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Results view
        self._results_view = ResultsView(root)
        self._results_view.pack(fill="x", padx=20, pady=(0, 20))

        self._poll_events()

    def _on_extract(self) -> None:
        path = self._file_picker.get_path()
        if not path or not path.exists():
            return

        output_dir = Path("output") / f"{path.stem}_extracted"
        output_dir = output_dir.resolve()

        self._progress_panel.reset()
        self._extract_btn.configure(state="disabled")
        self._cancel_btn.configure(state="normal")

        self._orchestrator = Orchestrator(self._event_queue)
        self._orchestrator.run(path, output_dir)

    def _on_cancel(self) -> None:
        if self._orchestrator:
            self._orchestrator.cancel()
        self._cancel_btn.configure(state="disabled")

    def _poll_events(self) -> None:
        """Process orchestrator events from queue (GUI-thread safe)."""
        try:
            while True:
                event_type, kwargs = self._event_queue.get_nowait()
                if event_type == "progress":
                    self._progress_panel.set_progress(
                        kwargs["percent"],
                        kwargs.get("message", ""),
                    )
                    if kwargs.get("message"):
                        self._progress_panel.append_log(kwargs["message"])
                elif event_type == "scan_complete":
                    self._progress_panel.append_log("Scan complete. Extracting...")
                elif event_type == "extract_complete":
                    self._results_view.set_output_path(kwargs["path"])
                    self._extract_btn.configure(state="normal")
                    self._cancel_btn.configure(state="disabled")
                    self._progress_panel.append_log("Done.")
                elif event_type == "cancelled":
                    self._progress_panel.append_log("Cancelled.")
                    self._extract_btn.configure(state="normal")
                    self._cancel_btn.configure(state="disabled")
                elif event_type == "error":
                    self._progress_panel.append_log(f"ERROR: {kwargs.get('message', '')}")
                    self._extract_btn.configure(state="normal")
                    self._cancel_btn.configure(state="disabled")
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)
