"""File picker - click to browse for firmware binaries."""

from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk


class FilePicker(ctk.CTkFrame):
    """Drop zone / file picker for firmware binaries."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        on_file_selected: Callable[[Path], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_file_selected = on_file_selected
        self._selected_path: Optional[Path] = None

        self._label = ctk.CTkLabel(
            self,
            text="Drop firmware file here or click to browse",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        self._label.pack(pady=20, padx=20, expand=True)

        self._file_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
        )
        self._file_label.pack(pady=(0, 20))

        self.configure(
            fg_color=("gray85", "gray20"),
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=8,
        )
        self._highlight(False)

        self.bind("<Button-1>", self._on_click)
        self._label.bind("<Button-1>", self._on_click)

    def _on_click(self, event: object) -> None:
        path = ctk.filedialog.askopenfilename(
            title="Select firmware binary",
            filetypes=[
                ("Binary files", "*.bin *.img *.fw *.rom"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self._set_file(Path(path))

    def _highlight(self, on: bool) -> None:
        self.configure(border_color=("gray50", "gray40") if on else ("gray70", "gray30"))

    def _set_file(self, path: Path) -> None:
        self._selected_path = path
        size_mb = path.stat().st_size / (1024 * 1024)
        self._file_label.configure(text=f"Selected: {path.name} ({size_mb:.1f} MB)")
        self._on_file_selected(path)

    def get_path(self) -> Optional[Path]:
        """Return currently selected file path."""
        return self._selected_path

    def clear(self) -> None:
        """Clear selection."""
        self._selected_path = None
        self._file_label.configure(text="")
