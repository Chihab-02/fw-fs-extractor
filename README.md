# Firmware FS Extractor

A desktop GUI application that extracts embedded Linux filesystems (squashfs, cramfs, ext2, UBI) from firmware binaries. Built for reverse engineering and firmware analysis.

## Features

- **Signature scanning**: Detects embedded filesystems and binaries via binwalk
- **One-click extraction**: Extracts squashfs, cramfs, ext2, and other formats
- **Background processing**: Extraction runs in worker threads without blocking the UI
- **Progress feedback**: Real-time log output and progress bar
- **Results browser**: Open extracted folder or browse top-level contents

## Prerequisites

- **Python 3.10+**
- **pybinwalk**: Python bindings for Binwalk v3 (included in requirements). Scan works on Windows; extraction may require fallback.
- **Extraction on Windows**: pybinwalk's extraction has a known bug on Windows. For full extraction:
  - Install [Rust](https://rustup.rs), then: `cargo install binwalk`
  - Or use WSL/Linux (binwalk works best there)

## Installation

```bash
cd "Reverse Engineering tool"
pip install -r requirements.txt
```

## Usage

```bash
python -m src.main
```

Or from the project root:

```bash
python src/main.py
```

1. Click the drop zone or use "Drop firmware file here or click to browse" to select a firmware binary
2. Click **Scan & Extract**
3. Monitor progress in the log panel
4. When complete, use **Open folder** to view extracted files, or **Browse tree** to see contents inline

## Output

Extracted files are placed in `output/<firmware_name>_extracted/` by default. Binwalk creates subdirectories for each extracted partition (e.g. `squashfs-root/`).

## Build standalone executable (optional)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "FirmwareExtractor" src/main.py
```

The built executable will be in `dist/`. Note: binwalk must still be installed on the target system, or consider bundling it.

## License

MIT
