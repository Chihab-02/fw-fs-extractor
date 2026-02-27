"""Entry point - launches the Firmware FS Extractor GUI."""

import customtkinter as ctk

from src.gui.main_window import MainWindow


def main() -> None:
    """Launch the main application window."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    MainWindow(app)
    app.mainloop()


if __name__ == "__main__":
    main()
