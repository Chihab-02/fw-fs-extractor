"""Results view - extracted files browser and Open folder button."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import customtkinter as ctk


class ResultsView(ctk.CTkFrame):
    """Shows extracted output path with Open folder and browse tree."""

    def __init__(self, parent: ctk.CTkBaseClass, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self._output_path: Optional[Path] = None

        self._path_label = ctk.CTkLabel(
            self,
            text="Extracted: (none)",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._path_label.pack(fill="x", padx=10, pady=(10, 5))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 5))

        self._open_btn = ctk.CTkButton(
            btn_frame,
            text="Open folder",
            command=self._open_folder,
        )
        self._open_btn.pack(side="left", padx=(0, 5))

        # Collapsible tree / file list
        self._tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._tree_expanded = False
        self._tree_btn = ctk.CTkButton(
            self._tree_frame,
            text="Browse tree \u25BC",
            width=100,
            command=self._toggle_tree,
        )
        self._tree_btn.pack(side="left")
        self._tree_frame.pack(fill="x", padx=10, pady=(0, 5))

        self._tree_container = ctk.CTkScrollableFrame(
            self,
            height=100,
            fg_color=("gray90", "gray15"),
        )

    def _toggle_tree(self) -> None:
        """Expand/collapse the file tree view."""
        self._tree_expanded = not self._tree_expanded
        if self._tree_expanded:
            self._tree_btn.configure(text="Browse tree \u25B2")
            self._tree_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            self._refresh_tree()
        else:
            self._tree_btn.configure(text="Browse tree \u25BC")
            self._tree_container.pack_forget()

    def _refresh_tree(self) -> None:
        """Populate tree with top-level contents of output dir."""
        for w in self._tree_container.winfo_children():
            w.destroy()
        if not self._output_path or not self._output_path.exists():
            return
        try:
            items = sorted(self._output_path.iterdir())
            for item in items[:50]:  # Limit to 50 items
                icon = "📁" if item.is_dir() else "📄"
                label = ctk.CTkLabel(
                    self._tree_container,
                    text=f"  {icon} {item.name}",
                    font=ctk.CTkFont(size=11),
                    anchor="w",
                )
                label.pack(fill="x", padx=5, pady=2)
            if len(items) > 50:
                lab = ctk.CTkLabel(
                    self._tree_container,
                    text=f"  ... and {len(items) - 50} more",
                    font=ctk.CTkFont(size=11),
                    text_color="gray",
                )
                lab.pack(fill="x", padx=5, pady=2)
        except OSError:
            pass

    def set_output_path(self, path: Path) -> None:
        """Set and display the extraction output path."""
        self._output_path = path
        self._path_label.configure(text=f"Extracted: {path}")
        if self._tree_expanded:
            self._refresh_tree()

    def _open_folder(self) -> None:
        """Open output folder in system file manager."""
        if not self._output_path or not self._output_path.exists():
            return
        path = str(self._output_path.resolve())
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
