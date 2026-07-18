"""Codex Windows hook adapter regression tests."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "entrypoints" / "hooks" / "codex-windows-hook.py"
SPEC = importlib.util.spec_from_file_location("codex_windows_hook", SCRIPT)
ADAPTER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(ADAPTER)


class CodexWindowsSessionStartTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "passdown-os"
        (self.root / "sessions").mkdir(parents=True)
        (self.root / "handoff").mkdir()

    def run_cli(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "session-start", "--root", str(self.root)],
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_counter_reset_and_handoff_injection_succeed(self) -> None:
        (self.root / "handoff" / "CURRENT.md").write_text("handoff body", encoding="utf-8")

        result = self.run_cli()

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("0", (self.root / "sessions" / ".toolcount").read_text(encoding="ascii"))
        self.assertIn("handoff body", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_counter_reset_failure_still_emits_handoff(self) -> None:
        (self.root / "handoff" / "CURRENT.md").write_text("recoverable handoff", encoding="utf-8")
        output = io.StringIO()

        with mock.patch.object(ADAPTER, "_reset_counter", side_effect=PermissionError("denied")):
            with contextlib.redirect_stdout(output):
                result = ADAPTER.session_start(self.root)

        self.assertEqual(0, result)
        self.assertIn("無法重置", output.getvalue())
        self.assertIn("recoverable handoff", output.getvalue())
        self.assertNotIn("Traceback", output.getvalue())

    def test_missing_handoff_emits_warning_without_traceback(self) -> None:
        result = self.run_cli()

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("無法讀取", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


class CodexWindowsCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "passdown-os"
        self.script = self.root / "entrypoints" / "hooks" / "checkpoint-counter.sh"
        self.script.parent.mkdir(parents=True)
        self.script.write_text("#!/bin/sh\n", encoding="utf-8")

    def make_file(self, relative: str) -> Path:
        path = Path(self.temp.name) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"")
        return path

    def assert_checkpoint_call(self, expected_shell: Path, which_values: dict[str, str | None]) -> None:
        with mock.patch.object(ADAPTER.shutil, "which", side_effect=lambda name: which_values.get(name)):
            with mock.patch.object(ADAPTER.subprocess, "call", return_value=7) as call:
                result = ADAPTER.checkpoint(self.root)

        self.assertEqual(7, result)
        call.assert_called_once_with([str(expected_shell), str(self.script), "--json"])

    def test_path_shell_is_preferred(self) -> None:
        shell = self.make_file("path/bin/sh.exe")
        git = self.make_file("Git/cmd/git.exe")
        self.assert_checkpoint_call(shell, {"sh": str(shell), "git": str(git)})

    def test_cmd_git_layout_finds_bin_shell(self) -> None:
        git = self.make_file("Git/cmd/git.exe")
        shell = self.make_file("Git/bin/sh.exe")
        self.assert_checkpoint_call(shell, {"sh": None, "git": str(git)})

    def test_mingw64_git_layout_finds_usr_bin_shell(self) -> None:
        git = self.make_file("Git/mingw64/bin/git.exe")
        shell = self.make_file("Git/usr/bin/sh.exe")
        self.assert_checkpoint_call(shell, {"sh": None, "git": str(git)})

    def test_shim_without_shell_exits_zero_without_subprocess(self) -> None:
        git = self.make_file("shims/git.exe")
        with mock.patch.object(ADAPTER.shutil, "which", side_effect=lambda name: None if name == "sh" else str(git)):
            with mock.patch.object(ADAPTER.subprocess, "call") as call:
                result = ADAPTER.checkpoint(self.root)

        self.assertEqual(0, result)
        call.assert_not_called()

    def test_subprocess_oserror_is_fail_open(self) -> None:
        shell = self.make_file("path/bin/sh.exe")
        with mock.patch.object(ADAPTER.shutil, "which", return_value=str(shell)):
            with mock.patch.object(ADAPTER.subprocess, "call", side_effect=FileNotFoundError("gone")):
                self.assertEqual(0, ADAPTER.checkpoint(self.root))


class CheckpointCounterScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project"
        self.root = self.project / "passdown-os"
        self.sessions = self.root / "sessions"
        self.sessions.mkdir(parents=True)
        self.counter = self.sessions / ".toolcount"
        self.script = self.root / "entrypoints" / "hooks" / "checkpoint-counter.sh"
        self.script.parent.mkdir(parents=True)
        self.script.write_bytes((ROOT / "entrypoints" / "hooks" / "checkpoint-counter.sh").read_bytes())
        self.shell = ADAPTER._find_shell()
        if self.shell is None:
            self.skipTest("no valid sh executable is available")

    def run_counter(self, initial: str, script: Path | None = None) -> subprocess.CompletedProcess[str]:
        self.counter.write_text(initial, encoding="ascii")
        environment = os.environ.copy()
        environment["CLAUDE_PROJECT_DIR"] = self.project.as_posix()
        return subprocess.run(
            [str(self.shell), (script or self.script).as_posix(), "--json"],
            cwd=self.project,
            env=environment,
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def assert_checkpoint_payload(self, output: str) -> str:
        payload = json.loads(output)
        hook_output = payload["hookSpecificOutput"]
        self.assertEqual("PostToolUse", hook_output["hookEventName"])
        self.assertIsInstance(hook_output["additionalContext"], str)
        self.assertTrue(hook_output["additionalContext"])
        return hook_output["additionalContext"]

    def test_json_boundaries_9_10_11_and_20(self) -> None:
        cases = (("8", "9", False), ("9", "10", True), ("10", "11", False), ("19", "20", True))
        for initial, expected, emits_checkpoint in cases:
            with self.subTest(expected=expected):
                result = self.run_counter(initial)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(expected, self.counter.read_text(encoding="ascii"))
                if emits_checkpoint:
                    self.assert_checkpoint_payload(result.stdout)
                else:
                    self.assertEqual("", result.stdout)

    def test_corrupt_counter_restarts_at_one_without_output(self) -> None:
        result = self.run_counter("not-a-number")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("1", self.counter.read_text(encoding="ascii"))
        self.assertEqual("", result.stdout)

    def test_json_escapes_quotes_and_backslashes_in_reminder(self) -> None:
        source_lines = self.script.read_text(encoding="utf-8").splitlines()
        replacement = r'''  msg='checkpoint "quoted" C:\temp' '''.rstrip()
        modified_lines = [replacement if line.startswith("  msg=") else line for line in source_lines]
        special_script = self.script.with_name("checkpoint-counter-special.sh")
        special_script.write_text("\n".join(modified_lines) + "\n", encoding="utf-8", newline="\n")

        result = self.run_counter("9", special_script)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('checkpoint "quoted" C:\\temp', self.assert_checkpoint_payload(result.stdout))


class CodexHookConfigurationTests(unittest.TestCase):
    def load_hooks(self, relative: str) -> dict[str, object]:
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def command(self, document: dict[str, object], event: str, field: str) -> str:
        hooks = document["hooks"]
        assert isinstance(hooks, dict)
        event_groups = hooks[event]
        assert isinstance(event_groups, list)
        group = event_groups[0]
        assert isinstance(group, dict)
        handlers = group["hooks"]
        assert isinstance(handlers, list)
        handler = handlers[0]
        assert isinstance(handler, dict)
        value = handler[field]
        assert isinstance(value, str)
        return value

    def test_windows_commands_use_layout_specific_adapter_roots(self) -> None:
        source = self.load_hooks(".codex/hooks.json")
        downstream = self.load_hooks("entrypoints/hooks/codex-hooks.json.example")

        self.assertEqual(
            "python entrypoints/hooks/codex-windows-hook.py session-start --root .",
            self.command(source, "SessionStart", "commandWindows"),
        )
        self.assertEqual(
            "python entrypoints/hooks/codex-windows-hook.py checkpoint --root .",
            self.command(source, "PostToolUse", "commandWindows"),
        )
        self.assertEqual(
            "python passdown-os/entrypoints/hooks/codex-windows-hook.py session-start --root passdown-os",
            self.command(downstream, "SessionStart", "commandWindows"),
        )
        self.assertEqual(
            "python passdown-os/entrypoints/hooks/codex-windows-hook.py checkpoint --root passdown-os",
            self.command(downstream, "PostToolUse", "commandWindows"),
        )

    def test_posix_and_stop_commands_remain_unchanged(self) -> None:
        source = self.load_hooks(".codex/hooks.json")
        downstream = self.load_hooks("entrypoints/hooks/codex-hooks.json.example")

        self.assertEqual(
            "sh entrypoints/hooks/checkpoint-counter.sh --json",
            self.command(source, "PostToolUse", "command"),
        )
        self.assertEqual(
            "python3 entrypoints/hooks/archive-codex-transcript.py",
            self.command(source, "Stop", "command"),
        )
        self.assertEqual(
            "python entrypoints/hooks/archive-codex-transcript.py",
            self.command(source, "Stop", "commandWindows"),
        )
        self.assertEqual(
            "sh passdown-os/entrypoints/hooks/checkpoint-counter.sh --json",
            self.command(downstream, "PostToolUse", "command"),
        )
        self.assertEqual(
            "python3 passdown-os/entrypoints/hooks/archive-codex-transcript.py",
            self.command(downstream, "Stop", "command"),
        )
        self.assertEqual(
            "python passdown-os/entrypoints/hooks/archive-codex-transcript.py",
            self.command(downstream, "Stop", "commandWindows"),
        )


if __name__ == "__main__":
    unittest.main()
