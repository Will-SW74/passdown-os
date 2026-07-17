#!/usr/bin/env python3
"""passdown-lint 的標準函式庫回歸測試。"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("passdown-lint.py").resolve()


class PassdownLintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.create_valid_fixture()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_text(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return path

    def create_valid_fixture(self) -> None:
        self.write_text(".gitattributes", "* text=auto\n*.sh text eol=lf\n")
        self.write_text(".gitignore", "sessions/.toolcount\n")
        for name in (
            "CONSTITUTION.md",
            "PROTOCOLS.md",
            "DISPATCH.md",
            "GOLDEN_TEMPLATE.md",
            "INSTALL.md",
        ):
            self.write_text(name, f"# {name}\n")
        self.write_text("PROJECT_MANIFEST.md", "# Project Manifest\nPassdown OS\n")
        self.write_text(
            "handoff/CURRENT.md",
            "# Current\n- **Direct Memory Source**: `sessions/current.md`\n",
        )
        self.write_text("sessions/current.md", "# Session\n")
        self.write_text(
            "entrypoints/hooks/checkpoint-counter.sh",
            "#!/bin/sh\necho ok\n",
        )
        self.write_text(
            "entrypoints/hooks/sample.json.example",
            json.dumps(
                {
                    "hooks": {
                        "PostToolUse": [
                            {
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": "sh entrypoints/hooks/checkpoint-counter.sh",
                                    }
                                ]
                            }
                        ]
                    }
                }
            ),
        )
        self.write_text("README.md", "[Current](handoff/CURRENT.md)\n")
        self.write_text(
            "sessions/INDEX.md",
            "# Session Index\n\n"
            "| Date | Session | Summary |\n"
            "| --- | --- | --- |\n"
            "| 2026-07-17 | [current.md](./current.md) | Current work |\n",
        )

    def run_lint(self) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result, json.loads(result.stdout)

    def assert_error(self, expected_code: str) -> None:
        result, payload = self.run_lint()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertFalse(payload["ok"])
        errors = payload["errors"]
        self.assertTrue(all({"code", "path", "message"} <= set(item) for item in errors))
        self.assertIn(expected_code, {item["code"] for item in errors})

    def test_valid_fixture_passes_and_json_shape_is_stable(self) -> None:
        result, payload = self.run_lint()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(set(payload), {"ok", "root", "checks", "errors"})
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["errors"], [])
        self.assertFalse((self.root / "tools").exists())

    def test_missing_gitattributes_fails(self) -> None:
        (self.root / ".gitattributes").unlink()
        self.assert_error("MISSING_REQUIRED")

    def test_invalid_hook_json_fails(self) -> None:
        self.write_text("entrypoints/hooks/sample.json.example", "{broken")
        self.assert_error("HOOK_JSON_INVALID")

    def test_current_placeholder_fails(self) -> None:
        self.write_text(
            "handoff/CURRENT.md",
            "# Current\n<next concrete step>\n- **Direct Memory Source**: `sessions/current.md`\n",
        )
        self.assert_error("PLACEHOLDER_REMAINS")

    def test_missing_markdown_link_fails(self) -> None:
        self.write_text("README.md", "[Missing](docs/missing.md)\n")
        self.assert_error("LINK_TARGET_MISSING")

    def test_markdown_self_link_fails(self) -> None:
        self.write_text("README.md", "[Self](README.md)\n")
        self.assert_error("LINK_SELF_REFERENCE")

    def test_session_index_placeholder_row_fails(self) -> None:
        self.write_text(
            "sessions/INDEX.md",
            "| 日期 | Session | Summary |\n"
            "| --- | --- | --- |\n"
            "| 範例 | example.md | Example |\n",
        )
        self.assert_error("INDEX_PLACEHOLDER_ROW")

    def test_session_index_missing_target_fails(self) -> None:
        self.write_text(
            "sessions/INDEX.md",
            "| 日期 | Session | Summary |\n"
            "| --- | --- | --- |\n"
            "| 2026-07-17 | [missing.md](./missing.md) | Missing |\n",
        )
        self.assert_error("INDEX_TARGET_MISSING")

    def test_session_index_without_link_fails(self) -> None:
        self.write_text(
            "sessions/INDEX.md",
            "| 日期 | Session | Summary |\n"
            "| --- | --- | --- |\n"
            "| 2026-07-17 | current.md | Missing link syntax |\n",
        )
        self.assert_error("INDEX_ROW_LINK_COUNT")

    def test_session_index_target_outside_sessions_fails(self) -> None:
        self.write_text(
            "sessions/INDEX.md",
            "| 日期 | Session | Summary |\n"
            "| --- | --- | --- |\n"
            "| 2026-07-17 | [README.md](../README.md) | Outside sessions |\n",
        )
        self.assert_error("INDEX_TARGET_INVALID")

    def test_session_index_duplicate_target_fails(self) -> None:
        self.write_text(
            "sessions/INDEX.md",
            "| 日期 | Session | Summary |\n"
            "| --- | --- | --- |\n"
            "| 2026-07-17 | [current.md](./current.md) | First |\n"
            "| 2026-07-17 | [current.md](./current.md) | Duplicate |\n",
        )
        self.assert_error("INDEX_TARGET_DUPLICATE")

    def test_missing_direct_memory_anchor_fails(self) -> None:
        (self.root / "sessions/current.md").unlink()
        self.assert_error("ANCHOR_TARGET_MISSING")

    def test_crlf_shell_fails(self) -> None:
        script = self.root / "entrypoints/hooks/checkpoint-counter.sh"
        script.write_bytes(b"#!/bin/sh\r\necho ok\r\n")
        self.assert_error("SHELL_CRLF")


if __name__ == "__main__":
    unittest.main()
