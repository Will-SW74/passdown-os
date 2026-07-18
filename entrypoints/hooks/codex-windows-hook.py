#!/usr/bin/env python3
"""Windows adapter for Passdown OS Codex hooks."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


def _configure_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is None:
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        # Encoding setup is best-effort; hook behavior must remain observable.
        pass


def _reset_counter(counter: Path) -> None:
    counter.write_text("0", encoding="ascii")


def _display_path(root: Path, relative: str) -> str:
    if root == Path("."):
        return relative
    return (root / relative).as_posix()


def session_start(root: Path) -> int:
    """Reset the counter best-effort and always emit handoff context or a warning."""

    counter = root / "sessions" / ".toolcount"
    try:
        _reset_counter(counter)
    except (OSError, ValueError):
        print(
            f"（警告：無法重置 {_display_path(root, 'sessions/.toolcount')}，"
            "檢查點計數將以既有狀態繼續）"
        )

    handoff = root / "handoff" / "CURRENT.md"
    print("=== passdown-os 交接內容（SessionStart hook）===")
    try:
        content = handoff.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        print(f"（警告：無法讀取 {_display_path(root, 'handoff/CURRENT.md')}，請檢查框架是否就位）")
    else:
        print(content)

    constitution = _display_path(root, "CONSTITUTION.md")
    print(f"--- 以上即 CURRENT.md 全文；請依 {constitution} 執行 Session 開始協定其餘步驟。")
    return 0


def _regular_file(value: str | None) -> Path | None:
    if not value:
        return None
    candidate = Path(value)
    try:
        return candidate if candidate.is_file() else None
    except OSError:
        return None


def _find_shell() -> Path | None:
    shell = _regular_file(shutil.which("sh"))
    if shell is not None:
        return shell

    git = _regular_file(shutil.which("git"))
    if git is None:
        return None

    for ancestor in (git.parent, *git.parents):
        for relative in (Path("bin") / "sh.exe", Path("usr") / "bin" / "sh.exe"):
            candidate = ancestor / relative
            try:
                if candidate.is_file():
                    return candidate
            except OSError:
                continue
    return None


def checkpoint(root: Path) -> int:
    """Run the shared checkpoint script when a valid Git Bash shell exists."""

    shell = _find_shell()
    script = root / "entrypoints" / "hooks" / "checkpoint-counter.sh"
    if shell is None or not script.is_file():
        return 0
    try:
        return subprocess.call([str(shell), str(script), "--json"])
    except OSError:
        return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    session_parser = subparsers.add_parser("session-start", help="emit Passdown OS handoff context")
    session_parser.add_argument("--root", required=True, type=Path, help="Passdown OS root directory")

    checkpoint_parser = subparsers.add_parser("checkpoint", help="run the shared checkpoint counter")
    checkpoint_parser.add_argument("--root", required=True, type=Path, help="Passdown OS root directory")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _configure_stdout()
    args = _build_parser().parse_args(argv)
    if args.command == "session-start":
        return session_start(args.root)
    if args.command == "checkpoint":
        return checkpoint(args.root)
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
