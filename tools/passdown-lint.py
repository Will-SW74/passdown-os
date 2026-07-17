#!/usr/bin/env python3
"""Passdown OS 安裝與交接完整性檢查器。"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlparse


REQUIRED_PATHS = (
    ".gitattributes",
    ".gitignore",
    "CONSTITUTION.md",
    "PROTOCOLS.md",
    "DISPATCH.md",
    "GOLDEN_TEMPLATE.md",
    "INSTALL.md",
    "PROJECT_MANIFEST.md",
    "handoff/CURRENT.md",
    "sessions/INDEX.md",
    "entrypoints/hooks/checkpoint-counter.sh",
)

EXCLUDED_PARTS = (
    ("openspec", "changes", "archive"),
    ("sessions", "archive"),
    ("references",),
    ("transcripts",),
)

CHECKS = (
    "required-paths",
    "shell-line-endings",
    "hook-json",
    "placeholders",
    "markdown-links",
    "session-index",
    "memory-anchors",
)

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
ANGLE_PLACEHOLDER_RE = re.compile(r"<[^>\r\n]+>")
SHELL_ATTRIBUTE_RE = re.compile(r"(?m)^\s*\*\.sh\s+text\s+eol=lf(?:\s|$)")


@dataclass(frozen=True)
class LintError:
    code: str
    path: str
    message: str


class PassdownLint:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.errors: list[LintError] = []

    def add_error(self, code: str, path: Path | str, message: str) -> None:
        if isinstance(path, Path):
            try:
                display_path = path.resolve().relative_to(self.root).as_posix()
            except (OSError, ValueError):
                display_path = path.as_posix()
        else:
            display_path = path
        self.errors.append(LintError(code, display_path, message))

    def read_text(self, path: Path) -> str | None:
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.add_error("READ_ERROR", path, f"無法以 UTF-8 讀取：{exc}")
            return None

    def is_excluded(self, path: Path) -> bool:
        try:
            parts = path.relative_to(self.root).parts
        except ValueError:
            return True
        return any(parts[: len(prefix)] == prefix for prefix in EXCLUDED_PARTS)

    def check_required_paths(self) -> None:
        for relative in REQUIRED_PATHS:
            path = self.root / relative
            if not path.exists():
                self.add_error("MISSING_REQUIRED", relative, "缺少安裝 payload 必要檔案")

    def check_shell_line_endings(self) -> None:
        attributes_path = self.root / ".gitattributes"
        if attributes_path.is_file():
            content = self.read_text(attributes_path)
            if content is not None and not SHELL_ATTRIBUTE_RE.search(content):
                self.add_error(
                    "GITATTR_SH_LF",
                    attributes_path,
                    "缺少 *.sh text eol=lf 規則",
                )

        hooks_dir = self.root / "entrypoints" / "hooks"
        if not hooks_dir.is_dir():
            return
        for script in sorted(hooks_dir.glob("*.sh")):
            try:
                if b"\r\n" in script.read_bytes():
                    self.add_error("SHELL_CRLF", script, "shell 腳本含 CRLF，必須正規化為 LF")
            except OSError as exc:
                self.add_error("READ_ERROR", script, f"無法讀取 shell bytes：{exc}")

    def iter_hook_json(self) -> Iterable[Path]:
        hooks_dir = self.root / "entrypoints" / "hooks"
        if hooks_dir.is_dir():
            yield from sorted(hooks_dir.glob("*.json.example"))
        installed_codex = self.root / ".codex" / "hooks.json"
        if installed_codex.is_file():
            yield installed_codex

    def check_hook_json(self) -> None:
        for path in self.iter_hook_json():
            content = self.read_text(path)
            if content is None:
                continue
            try:
                document = json.loads(content)
            except json.JSONDecodeError as exc:
                self.add_error(
                    "HOOK_JSON_INVALID",
                    path,
                    f"hook JSON 無法解析（line {exc.lineno}, column {exc.colno}）",
                )
                continue
            for command in self.walk_commands(document):
                for script_path in self.extract_hook_scripts(command):
                    resolved = self.resolve_hook_script(script_path)
                    if not resolved.is_file():
                        self.add_error(
                            "HOOK_SCRIPT_MISSING",
                            path,
                            f"hook command 指向不存在的腳本：{script_path}",
                        )

    def walk_commands(self, value: object) -> Iterable[str]:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"command", "commandWindows", "command_windows"} and isinstance(child, str):
                    yield child
                else:
                    yield from self.walk_commands(child)
        elif isinstance(value, list):
            for child in value:
                yield from self.walk_commands(child)

    @staticmethod
    def extract_hook_scripts(command: str) -> Iterable[str]:
        # shlex 的 POSIX 模式可保留本專案 hook commands 的路徑 token；解析失敗時改用 regex。
        try:
            tokens = shlex.split(command, posix=True)
        except ValueError:
            tokens = re.findall(r"(?:passdown-os/)?entrypoints/hooks/[\w./-]+\.sh", command)
        for token in tokens:
            normalized = token.strip("\"'")
            if normalized.endswith(".sh") and "entrypoints/hooks/" in normalized:
                start = normalized.index("entrypoints/hooks/")
                yield normalized[start:]

    def resolve_hook_script(self, script_path: str) -> Path:
        return self.root / Path(script_path)

    def check_placeholders(self) -> None:
        for relative in ("handoff/CURRENT.md", "PROJECT_MANIFEST.md"):
            path = self.root / relative
            if not path.is_file():
                continue
            content = self.read_text(path)
            if content is None:
                continue
            without_comments = HTML_COMMENT_RE.sub("", content)
            for match in ANGLE_PLACEHOLDER_RE.finditer(without_comments):
                self.add_error(
                    "PLACEHOLDER_REMAINS",
                    path,
                    f"仍有角括號佔位符：{match.group(0)}",
                )

    def iter_markdown(self) -> Iterable[Path]:
        for path in sorted(self.root.rglob("*.md")):
            if not self.is_excluded(path):
                yield path

    def check_markdown_links(self) -> None:
        for markdown in self.iter_markdown():
            content = self.read_text(markdown)
            if content is None:
                continue
            searchable = HTML_COMMENT_RE.sub("", content)
            searchable = INLINE_CODE_RE.sub("", searchable)
            for target in MARKDOWN_LINK_RE.findall(searchable):
                resolved = self.resolve_markdown_target(markdown, target)
                if resolved is not None and resolved == markdown.resolve():
                    self.add_error(
                        "LINK_SELF_REFERENCE",
                        markdown,
                        f"Markdown link 不得指回同一檔案：{target}",
                    )
                elif resolved is not None and not resolved.exists():
                    self.add_error(
                        "LINK_TARGET_MISSING",
                        markdown,
                        f"本地 Markdown link 目標不存在：{target}",
                    )

    def resolve_markdown_target(self, source: Path, target: str) -> Path | None:
        target = target.strip().strip("<>")
        if not target or target.startswith("#"):
            return None
        parsed = urlparse(target)
        if parsed.scheme or parsed.netloc:
            return None
        path_text = unquote(parsed.path).replace("\\", "/")
        if not path_text:
            return None
        return (source.parent / Path(path_text)).resolve()

    def check_session_index(self) -> None:
        index_path = self.root / "sessions" / "INDEX.md"
        if not index_path.is_file():
            return
        content = self.read_text(index_path)
        if content is None:
            return

        seen_targets: set[Path] = set()
        header_seen = False
        for line_number, line in enumerate(content.splitlines(), start=1):
            if not line.lstrip().startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if not cells:
                continue
            # 第一個表格列是欄名；分隔列可能含 Markdown 對齊冒號，兩者都不是資料。
            if not header_seen:
                header_seen = True
                continue
            if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            if cells[0] in {"範例", "..."} or "..." in cells:
                self.add_error(
                    "INDEX_PLACEHOLDER_ROW",
                    index_path,
                    f"session index 第 {line_number} 行仍是範例或省略佔位列",
                )
                continue

            targets = MARKDOWN_LINK_RE.findall(line)
            if len(targets) != 1:
                self.add_error(
                    "INDEX_ROW_LINK_COUNT",
                    index_path,
                    f"session index 第 {line_number} 行必須恰有一個 Markdown link",
                )
                continue
            resolved = self.resolve_markdown_target(index_path, targets[0])
            if resolved is None or resolved.parent != index_path.parent.resolve() or resolved.suffix.lower() != ".md":
                self.add_error(
                    "INDEX_TARGET_INVALID",
                    index_path,
                    f"session index 第 {line_number} 行必須指向 sessions/ 內的 Markdown 檔案",
                )
                continue
            if not resolved.is_file():
                self.add_error(
                    "INDEX_TARGET_MISSING",
                    index_path,
                    f"session index 第 {line_number} 行目標不存在：{targets[0]}",
                )
            if resolved in seen_targets:
                self.add_error(
                    "INDEX_TARGET_DUPLICATE",
                    index_path,
                    f"session index 第 {line_number} 行重複指向：{targets[0]}",
                )
            seen_targets.add(resolved)

    def check_memory_anchors(self) -> None:
        current_path = self.root / "handoff" / "CURRENT.md"
        if not current_path.is_file():
            return
        content = self.read_text(current_path)
        if content is None:
            return
        for line in content.splitlines():
            if "Direct Memory Source" not in line:
                continue
            for target in re.findall(r"`([^`]+)`", line):
                if target.startswith(("sessions/", "memory/", "handoff/")):
                    resolved = self.root / Path(target.split("#", 1)[0])
                    if not resolved.exists():
                        self.add_error(
                            "ANCHOR_TARGET_MISSING",
                            current_path,
                            f"Direct Memory Source 目標不存在：{target}",
                        )

    def run(self) -> list[LintError]:
        self.check_required_paths()
        self.check_shell_line_endings()
        self.check_hook_json()
        self.check_placeholders()
        self.check_markdown_links()
        self.check_session_index()
        self.check_memory_anchors()
        return self.errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="檢查 Passdown OS 安裝與交接完整性")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Passdown OS 根目錄")
    parser.add_argument("--json", action="store_true", dest="json_output", help="輸出 JSON")
    return parser


def render_text(root: Path, errors: list[LintError]) -> str:
    if not errors:
        return f"passdown-lint: OK ({len(CHECKS)} checks, root={root})"
    lines = [f"passdown-lint: FAILED ({len(errors)} error(s), root={root})"]
    lines.extend(f"- [{error.code}] {error.path}: {error.message}" for error in errors)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    # Windows 的 redirected stdout 會沿用系統 code page；JSON 契約固定輸出 UTF-8。
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        errors = [LintError("ROOT_INVALID", str(root), "root 不存在或不是目錄")]
    else:
        errors = PassdownLint(root).run()

    if args.json_output:
        payload = {
            "ok": not errors,
            "root": str(root),
            "checks": list(CHECKS),
            "errors": [asdict(error) for error in errors],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_text(root, errors))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
