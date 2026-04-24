#!/usr/bin/env python
"""manage.py — project management utilities."""

import argparse
import os
import sys
import subprocess
import zipfile
import datetime
from typing import Optional, Set

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ROOT = os.path.dirname(os.path.abspath(__file__))

GARBAGE_DIRS: Set[str] = {
    "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".ipynb_checkpoints", ".pytype",
    "cython_debug", ".eggs", "*.egg-info", ".tox",
    ".nox", "htmlcov", "build", "dist",
}

GARBAGE_EXTENSIONS: Set[str] = {
    ".pyc", ".pyo", ".pyd", ".cover", ".mo", ".pot"
}

EXCLUDE_FROM_ZIP: Set[str] = {
    "dumpzip", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".ipynb_checkpoints",
    ".eggs", ".tox", ".nox", "htmlcov", "build", "dist",
    ".git", ".venv", "venv", "env",
}

EXCLUDE_EXTENSIONS_FROM_ZIP: Set[str] = {
    ".pyc", ".pyo", ".pyd"
}

BINARY_EXTENSIONS: Set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico",
    ".svg", ".pdf", ".zip", ".gz", ".tar", ".bz2",
    ".7z", ".rar", ".exe", ".dll", ".so", ".dylib",
    ".bin", ".db", ".sqlite", ".sqlite3", ".woff",
    ".woff2", ".ttf", ".otf", ".eot", ".mp3", ".mp4",
    ".wav", ".ogg", ".flac", ".pkl", ".pickle", ".npy",
    ".npz", ".pyc", ".pyo", ".pyd",
}


def _is_text_file(path: str) -> bool:
    """Return True if the file is likely a text file."""
    if (
        os.path.splitext(path)[1].lower()
        in BINARY_EXTENSIONS
    ):
        return False
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
        return b"\x00" not in chunk
    except OSError:
        return False


def _iter_project_files(
    exclude_dirs: Optional[Set[str]] = None,
):
    """Yield (dirpath, filename) for every file under ROOT."""
    exclude = exclude_dirs or set()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Prune excluded dirs in-place so os.walk doesn't
        # recurse into them
        dirnames[:] = [
            d for d in dirnames
            if d not in exclude
            and not d.endswith(".egg-info")
        ]
        for filename in filenames:
            yield dirpath, filename


def _print_tree(
    path: str,
    indent: int,
    exclude: Set[str],
) -> None:
    try:
        entries = sorted(
            os.scandir(path),
            key=lambda e: (not e.is_dir(), e.name),
        )
    except PermissionError:
        return

    for entry in entries:
        if (
            entry.name in exclude
            or entry.name.endswith(".egg-info")
        ):
            continue
        if entry.is_dir(follow_symlinks=False):
            print(
                f"{'    ' * indent}├── {entry.name}/"
            )
            _print_tree(entry.path, indent + 1, exclude)
        else:
            print(
                f"{'    ' * indent}├── {entry.name}"
            )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> None:
    """Start the Streamlit app."""
    subprocess.run(
        ["streamlit", "run", "streamlit.py"],
        cwd=ROOT,
        check=True,
    )


def cmd_init(args: argparse.Namespace) -> None:
    """Run first-time initialisation."""
    print("Running Alembic migrations...")
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=ROOT,
        check=True,
    )
    _fix_db_permissions()
    _seed_admin_user()
    print("Initialisation complete.")


def _fix_db_permissions() -> None:
    import re
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
    db_url = os.environ.get(
        "DATABASE_URL", "sqlite:///./app.db"
    )
    m = re.match(r"sqlite:///(.+)", db_url)
    if not m:
        return
    db_path = m.group(1)
    if not os.path.isabs(db_path):
        db_path = os.path.join(ROOT, db_path)
    if os.path.exists(db_path):
        os.chmod(db_path, 0o664)
        print(f"Set permissions 664 on {db_path}")


def _seed_admin_user() -> None:
    from db.session import SessionLocal
    from repositories.user_repository import UserRepository

    with SessionLocal() as session:
        repo = UserRepository(session)
        if repo.get_by_username("admin") is not None:
            print("Admin user already exists — skipping.")
            return
        repo.create(
            username="admin",
            email="admin@admin.com",
            password="admin",
            roles=["admin"],
        )
        session.commit()
        print("Admin user created (username: admin, password: admin).")


def cmd_dumpzip(args: argparse.Namespace) -> None:
    """Create a timestamped zip of the project in ./dumpzip/."""
    dump_dir = os.path.join(ROOT, "dumpzip")
    os.makedirs(dump_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    zip_name = f"project_{timestamp}.zip"
    zip_path = os.path.join(dump_dir, zip_name)

    with zipfile.ZipFile(
        zip_path, "w", zipfile.ZIP_DEFLATED
    ) as zf:
        for dirpath, filename in _iter_project_files(
            exclude_dirs=EXCLUDE_FROM_ZIP
        ):
            if args.exclude_env and filename == ".env":
                continue
            ext = os.path.splitext(filename)[1].lower()
            if ext in EXCLUDE_EXTENSIONS_FROM_ZIP:
                continue
            full_path = os.path.join(dirpath, filename)
            arcname = os.path.relpath(full_path, ROOT)
            zf.write(full_path, arcname)

    print(f"Created: {zip_path}")


def cmd_tree(args: argparse.Namespace) -> None:
    """Print the project file tree."""
    exclude: Set[str] = {
        "__pycache__", ".git", ".pytest_cache",
        ".mypy_cache", ".ruff_cache",
        ".ipynb_checkpoints", "dumpzip", ".venv",
        "venv", "env", ".eggs", "htmlcov",
    }
    print(os.path.basename(ROOT) + "/")
    _print_tree(ROOT, 0, exclude)


def cmd_clear(args: argparse.Namespace) -> None:
    """Remove cache and garbage files/folders."""
    import shutil
    removed = 0

    for dirpath, dirnames, filenames in os.walk(
        ROOT, topdown=True
    ):
        # Remove garbage dirs
        to_remove = [
            d for d in dirnames
            if d in GARBAGE_DIRS
            or d.endswith(".egg-info")
        ]
        for d in to_remove:
            full = os.path.join(dirpath, d)
            print(
                f"Removing dir:  "
                f"{os.path.relpath(full, ROOT)}"
            )
            shutil.rmtree(full, ignore_errors=True)
            removed += 1
        dirnames[:] = [
            d for d in dirnames if d not in to_remove
        ]

        # Remove garbage files
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in GARBAGE_EXTENSIONS:
                full = os.path.join(dirpath, filename)
                print(
                    f"Removing file: "
                    f"{os.path.relpath(full, ROOT)}"
                )
                os.remove(full)
                removed += 1

    print(f"Done — {removed} item(s) removed.")


def cmd_setup_env(args: argparse.Namespace) -> None:
    """Set OPENAI_API_KEY in .env, copying template if needed."""
    import re
    import shutil

    template = os.path.join(ROOT, ".env.example")
    target = os.path.join(ROOT, ".env")

    if not os.path.exists(target):
        if not os.path.exists(template):
            print("Error: .env.example not found.")
            sys.exit(1)
        shutil.copy2(template, target)
        print("Copied .env.example → .env")

    with open(target, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(
        r"^(OPENAI_API_KEY\s*=\s*).*$",
        rf"\g<1>{args.openai_key}",
        content,
        flags=re.MULTILINE,
    )

    with open(target, "w", encoding="utf-8") as f:
        f.write(content)

    print("Set OPENAI_API_KEY in .env")


def cmd_trim_trailing_spaces(
    args: argparse.Namespace,
) -> None:
    """Remove trailing whitespace and normalize CRLF in all text files."""
    SKIP_DIRS: Set[str] = {
        "__pycache__", ".git", ".venv", "venv", "env",
        "dumpzip", ".pytest_cache", ".mypy_cache",
        ".ruff_cache", ".ipynb_checkpoints",
    }
    changed = 0

    for dirpath, filename in _iter_project_files(
        exclude_dirs=SKIP_DIRS
    ):
        full_path = os.path.join(dirpath, filename)
        if not _is_text_file(full_path):
            continue
        try:
            with open(
                full_path,
                "r",
                encoding="utf-8",
                errors="replace",
                newline="",
            ) as f:
                original = f.read()
        except OSError:
            continue

        normalized = original.replace(
            "\r\n", "\n"
        ).replace("\r", "\n")
        lines = normalized.splitlines(keepends=True)
        cleaned_lines = [
            line.rstrip(" \t")
            + ("\n" if line.endswith("\n") else "")
            for line in lines
        ]
        cleaned = "".join(cleaned_lines)

        if cleaned != original:
            with open(
                full_path, "w", encoding="utf-8"
            ) as f:
                f.write(cleaned)
            print(
                f"Trimmed: "
                f"{os.path.relpath(full_path, ROOT)}"
            )
            changed += 1

    print(f"Done — {changed} file(s) modified.")


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

COMMANDS = {
    "run": cmd_run,
    "init": cmd_init,
    "setup_env": cmd_setup_env,
    "dumpzip": cmd_dumpzip,
    "tree": cmd_tree,
    "clear": cmd_clear,
    "trim_trailing_spaces": cmd_trim_trailing_spaces,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="manage.py",
        description="Project management utilities.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "run",
        help="Start the Streamlit app",
    )
    subparsers.add_parser(
        "init",
        help="Run first-time initialisation (alembic migrations)",
    )

    p_env = subparsers.add_parser(
        "setup_env",
        help="Copy .env.example to .env and set OPENAI_API_KEY",
    )
    p_env.add_argument(
        "--openai-key",
        required=True,
        metavar="KEY",
        help="Your OpenAI API key",
    )

    p_zip = subparsers.add_parser(
        "dumpzip",
        help="Create a timestamped zip of the project in ./dumpzip/",
    )
    p_zip.add_argument(
        "--exclude_env",
        action="store_true",
        help="Omit the .env file from the zip",
    )

    subparsers.add_parser(
        "tree",
        help="Print the project file tree",
    )
    subparsers.add_parser(
        "clear",
        help="Remove cache/garbage files and folders",
    )
    subparsers.add_parser(
        "trim_trailing_spaces",
        help="Remove trailing whitespace and normalize CRLF in all text files",
    )

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    COMMANDS[args.command](args)
