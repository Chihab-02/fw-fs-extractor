"""Binwalk wrapper - pybinwalk for scan; pybinwalk or subprocess for extract (fallback on Windows)."""

import shutil
import subprocess
from pathlib import Path
from typing import Callable

try:
    import pybinwalk
    HAS_PYBINWALK = True
except ImportError:
    HAS_PYBINWALK = False


def run_scan(
    firmware_path: Path,
    on_line: Callable[[str], None],
    on_complete: Callable[[list[dict]], None],
    cancelled: Callable[[], bool],
) -> None:
    """
    Run binwalk signature scan on firmware using pybinwalk.
    Calls on_line for each result; on_complete with list of {offset, description}.
    """
    if not HAS_PYBINWALK:
        on_line("ERROR: pybinwalk not found. Install with: pip install pybinwalk")
        on_complete([])
        return

    results: list[dict] = []
    try:
        bw = pybinwalk.Binwalk()
        for result in bw.scan_path(str(firmware_path)):
            if cancelled():
                break
            line = f"0x{result.offset:08X}  {result.name}  {result.description}"
            on_line(line)
            results.append({"offset": result.offset, "description": result.description})
    except Exception as e:
        on_line(f"ERROR: {e}")
    finally:
        on_complete(results)


def _extract_via_subprocess(
    firmware_path: Path,
    output_dir: Path,
    on_line: Callable[[str], None],
    on_complete: Callable[[Path], None],
    cancelled: Callable[[], bool],
) -> bool:
    """Try extraction via binwalk CLI. Returns True if binwalk was found and run."""
    cmd = shutil.which("binwalk")
    if not cmd:
        return False

    output_dir.mkdir(parents=True, exist_ok=True)
    args = [cmd, "-e", "-C", str(output_dir), str(firmware_path)]

    try:
        on_line("Extracting via binwalk CLI...")
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        for line in iter(proc.stdout.readline, ""):
            if cancelled():
                proc.terminate()
                proc.wait(timeout=5)
                break
            line = line.rstrip()
            if line:
                on_line(line)
        proc.wait(timeout=300)
    except Exception as e:
        on_line(f"ERROR: {e}")
    return True


def run_extract(
    firmware_path: Path,
    output_dir: Path,
    on_line: Callable[[str], None],
    on_complete: Callable[[Path], None],
    cancelled: Callable[[], bool],
) -> None:
    """
    Run binwalk extract on firmware.
    Uses pybinwalk if configure works; falls back to subprocess binwalk on Windows
    (pybinwalk extraction has a known configure bug on Windows).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Try pybinwalk first (works on Linux; configure fails on Windows)
    if HAS_PYBINWALK:
        try:
            on_line("Extracting embedded filesystems...")
            bw = pybinwalk.Binwalk.configure(
                target_file_name=str(firmware_path.resolve()),
                output_directory=str(output_dir.resolve()),
            )
            analysis = bw.analyze_path(bw.base_target_file, do_extraction=True)

            for sig in analysis.file_map:
                if cancelled():
                    break
                on_line(f"0x{sig.offset:08X}  {sig.name}  {sig.description}")

            for sig_id, extraction in analysis.extractions.items():
                if extraction.success:
                    on_line(f"Extracted: {extraction.output_directory}")
                else:
                    on_line(f"Extraction skipped: {sig_id}")
            on_complete(output_dir)
            return
        except RuntimeError as e:
            if "BinwalkError" in str(e):
                on_line("pybinwalk extraction unsupported on this platform, trying binwalk CLI...")
            else:
                on_line(f"ERROR: {e}")
                on_complete(output_dir)
                return
        except Exception as e:
            on_line(f"ERROR: {e}")
            on_complete(output_dir)
            return

    # Fallback: subprocess binwalk (requires: cargo install binwalk, or Linux)
    if _extract_via_subprocess(firmware_path, output_dir, on_line, on_complete, cancelled):
        on_complete(output_dir)
        return

    on_line(
        "Extraction failed. On Windows: install binwalk via 'cargo install binwalk' "
        "(Rust required), or use WSL/Linux for full extraction support."
    )
    on_complete(output_dir)
