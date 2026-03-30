#!/usr/bin/env python
"""
manage.py — project management utilities.

Usage:
    python manage.py <command>

Commands:
    run                   Start the Streamlit app
    init                  Run first-time initialisation (alembic migrations)
    dumpzip               Create a timestamped zip of the project in ./dumpzip/
    tree                  Print the project file tree
    clear                 Remove cache/garbage files and folders
    trim_trailing_spaces  Remove trailing whitespace from all text files
"""

import os
import sys
import subprocess
import zipfile
import datetime

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ROOT = os.path.dirname(os.path.abspath(__file__))

GARBAGE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
                ".ipynb_checkpoints", ".pytype", "cython_debug", ".eggs",
                "*.egg-info", ".tox", ".nox", "htmlcov", "build", "dist"}

GARBAGE_EXTENSIONS = {".pyc", ".pyo", ".pyd", ".cover", ".mo", ".pot"}

EXCLUDE_FROM_ZIP = {
    "dumpzip", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".ipynb_checkpoints", ".eggs", ".tox", ".nox", "htmlcov", "build", "dist",
    ".git", ".venv", "venv", "env",
}

EXCLUDE_EXTENSIONS_FROM_ZIP = {".pyc", ".pyo", ".pyd"}

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
    ".pdf", ".zip", ".gz", ".tar", ".bz2", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".bin",
    ".db", ".sqlite", ".sqlite3",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".mp3", ".mp4", ".wav", ".ogg", ".flac",
    ".pkl", ".pickle", ".npy", ".npz",
    ".pyc", ".pyo", ".pyd",
}


def _is_text_file(path: str) -> bool:
    """Return True if the file is likely a text file."""
    if os.path.splitext(path)[1].lower() in BINARY_EXTENSIONS:
        return False
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
        return b"\x00" not in chunk
    except OSError:
        return False


def _iter_project_files(exclude_dirs: set | None = None):
    """Yield (dirpath, filename) for every file under ROOT."""
    exclude = exclude_dirs or set()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Prune excluded dirs in-place so os.walk doesn't recurse into them
        dirnames[:] = [
            d for d in dirnames
            if d not in exclude and not d.endswith(".egg-info")
        ]
        for filename in filenames:
            yield dirpath, filename


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_run():
    """Start the Streamlit app."""
    subprocess.run(["streamlit", "run", "streamlit.py"], cwd=ROOT, check=True)


def cmd_init():
    """Run first-time initialisation."""
    print("Running Alembic migrations...")
    subprocess.run(["alembic", "upgrade", "head"], cwd=ROOT, check=True)
    print("Initialisation complete.")


def cmd_dumpzip():
    """Create a timestamped zip of the project in ./dumpzip/."""
    dump_dir = os.path.join(ROOT, "dumpzip")
    os.makedirs(dump_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"project_{timestamp}.zip"
    zip_path = os.path.join(dump_dir, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, filename in _iter_project_files(exclude_dirs=EXCLUDE_FROM_ZIP):
            if os.path.splitext(filename)[1].lower() in EXCLUDE_EXTENSIONS_FROM_ZIP:
                continue
            full_path = os.path.join(dirpath, filename)
            arcname = os.path.relpath(full_path, ROOT)
            zf.write(full_path, arcname)

    print(f"Created: {zip_path}")


def cmd_tree(indent: int = 0, path: str | None = None, exclude: set | None = None):
    """Print the project file tree."""
    if path is None:
        path = ROOT
        exclude = {"__pycache__", ".git", ".pytest_cache", ".mypy_cache",
                   ".ruff_cache", ".ipynb_checkpoints", "dumpzip",
                   ".venv", "venv", "env", ".eggs", "htmlcov"}
        print(os.path.basename(ROOT) + "/")

    try:
        entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name))
    except PermissionError:
        return

    for entry in entries:
        if entry.name in exclude or entry.name.endswith(".egg-info"):
            continue
        prefix = "    " * indent + ("├── " if indent >= 0 else "")
        if entry.is_dir(follow_symlinks=False):
            print(f"{'    ' * indent}├── {entry.name}/")
            cmd_tree(indent + 1, entry.path, exclude)
        else:
            print(f"{'    ' * indent}├── {entry.name}")


def cmd_clear():
    """Remove cache and garbage files/folders."""
    import shutil
    removed = 0

    for dirpath, dirnames, filenames in os.walk(ROOT, topdown=True):
        # Remove garbage dirs
        to_remove = [d for d in dirnames if d in GARBAGE_DIRS or d.endswith(".egg-info")]
        for d in to_remove:
            full = os.path.join(dirpath, d)
            print(f"Removing dir:  {os.path.relpath(full, ROOT)}")
            shutil.rmtree(full, ignore_errors=True)
            removed += 1
        dirnames[:] = [d for d in dirnames if d not in to_remove]

        # Remove garbage files
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() in GARBAGE_EXTENSIONS:
                full = os.path.join(dirpath, filename)
                print(f"Removing file: {os.path.relpath(full, ROOT)}")
                os.remove(full)
                removed += 1

    print(f"Done — {removed} item(s) removed.")


def cmd_trim_trailing_spaces():
    """Remove trailing whitespace from all text files."""
    SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "env", "dumpzip",
                 ".pytest_cache", ".mypy_cache", ".ruff_cache", ".ipynb_checkpoints"}
    changed = 0

    for dirpath, filename in _iter_project_files(exclude_dirs=SKIP_DIRS):
        full_path = os.path.join(dirpath, filename)
        if not _is_text_file(full_path):
            continue
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                original = f.read()
        except OSError:
            continue

        lines = original.splitlines(keepends=True)
        cleaned_lines = [line.rstrip(" \t") + ("\n" if line.endswith("\n") else "") for line in lines]
        cleaned = "".join(cleaned_lines)

        if cleaned != original:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print(f"Trimmed: {os.path.relpath(full_path, ROOT)}")
            changed += 1

    print(f"Done — {changed} file(s) modified.")


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

COMMANDS = {
    "run": cmd_run,
    "init": cmd_init,
    "dumpzip": cmd_dumpzip,
    "tree": cmd_tree,
    "clear": cmd_clear,
    "trim_trailing_spaces": cmd_trim_trailing_spaces,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(1)
    COMMANDS[sys.argv[1]]()
