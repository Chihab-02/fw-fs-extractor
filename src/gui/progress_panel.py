"""Progress bar and log viewer."""

import math

import customtkinter as ctk


class ProgressPanel(ctk.CTkFrame):
    """Progress bar and scrollable log output."""

    def __init__(self, parent: ctk.CTkBaseClass, **kwargs) -> None:
        super().__init__(parent, **kwargs)

        self._status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._status_label.pack(fill="x", padx=10, pady=(10, 5))

        self._progress = ctk.CTkProgressBar(self)
        self._progress.pack(fill="x", padx=10, pady=(0, 10))
        self._progress.set(0)

        self._pulse_phase = 0.0
        self._indeterminate = False

        log_label = ctk.CTkLabel(self, text="Log:", font=ctk.CTkFont(size=12, weight="bold"))
        log_label.pack(anchor="w", padx=10, pady=(5, 5))

        self._log_text = ctk.CTkTextbox(
            self,
            height=150,
            font=ctk.CTkFont(family="Consolas", size=11),
        )
        self._log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def set_progress(self, percent: int, message: str = "") -> None:
        """Update progress bar (0-100) and status message."""
        self._indeterminate = False
        self._progress.set(percent / 100.0)
        if message:
            self._status_label.configure(text=message[:80])

    def set_indeterminate(self, active: bool) -> None:
        """When active, progress bar pulses to show ongoing work (no real progress)."""
        self._indeterminate = active
        if not active:
            self._progress.set(0.7)

    def tick_pulse(self) -> None:
        """Advance indeterminate progress animation. Call periodically when extracting."""
        if not self._indeterminate:
            return
        self._pulse_phase += 0.08
        if self._pulse_phase > 1.0:
            self._pulse_phase = 0.0
        value = 0.5 + 0.45 * (0.5 + 0.5 * math.sin(self._pulse_phase * 3.14159 * 2))
        self._progress.set(value)

    def append_log(self, line: str) -> None:
        """Append a line to the log."""
        self._log_text.insert("end", line + "\n")
        self._log_text.see("end")

    def clear_log(self) -> None:
        """Clear log content."""
        self._log_text.delete("1.0", "end")

    def reset(self) -> None:
        """Reset progress and log."""
        self._indeterminate = False
        self._progress.set(0)
        self._status_label.configure(text="")
        self.clear_log()
