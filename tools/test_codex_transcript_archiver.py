"""Codex transcript archiver 的標準函式庫回歸測試。"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "entrypoints" / "hooks" / "archive-codex-transcript.py"
SPEC = importlib.util.spec_from_file_location("codex_transcript_archiver", SCRIPT)
ARCHIVER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(ARCHIVER)


class CodexTranscriptArchiverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.transcripts = self.project / "passdown-os" / "transcripts"
        self.transcripts.mkdir(parents=True)
        (self.project / "passdown-os" / "CONSTITUTION.md").write_text("marker", encoding="utf-8")
        self.source = self.root / "rollout-2026-07-17T13-30-40-019f6e8e-1ebc-76f2-b719-93570b8661df.jsonl"

    def payload(self, **overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "session_id": "019f6e8e-1ebc-76f2-b719-93570b8661df",
            "transcript_path": str(self.source),
            "cwd": str(self.project),
            "hook_event_name": "Stop",
        }
        value.update(overrides)
        return value

    def run_cli(self, payload: object) -> subprocess.CompletedProcess[str]:
        data = payload if isinstance(payload, str) else json.dumps(payload)
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=data,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_first_stop_copies_opaque_bytes_with_expected_name(self) -> None:
        content = b'{"opaque": "\xff\x00"}\n'
        self.source.write_bytes(content)
        result = self.run_cli(self.payload())
        destination = self.transcripts / "2026-07-17-1330-codex-019f6e8e.jsonl"
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(content, destination.read_bytes())

    def test_later_stop_replaces_same_snapshot(self) -> None:
        self.source.write_bytes(b"a" * 100)
        self.assertEqual(0, self.run_cli(self.payload()).returncode)
        self.source.write_bytes(b"b" * 200)
        result = self.run_cli(self.payload())
        snapshots = list(self.transcripts.glob("*.jsonl"))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(1, len(snapshots))
        self.assertEqual(b"b" * 200, snapshots[0].read_bytes())

    def test_source_repo_root_layout_is_supported(self) -> None:
        # 來源 repo 的部署 hook 不會有巢狀 passdown-os/，所以用 mock 鎖定腳本位置驗證此明確例外。
        source_project = self.root / "source-repo"
        (source_project / "entrypoints" / "hooks").mkdir(parents=True)
        (source_project / "transcripts").mkdir()
        (source_project / "CONSTITUTION.md").write_text("marker", encoding="utf-8")
        deployed_script = source_project / "entrypoints" / "hooks" / SCRIPT.name
        deployed_script.write_text("placeholder", encoding="utf-8")
        self.source.write_bytes(b"source-layout")
        with mock.patch.object(ARCHIVER, "__file__", str(deployed_script)):
            destination = ARCHIVER.archive(self.payload(cwd=str(source_project)))
        self.assertEqual(b"source-layout", destination.read_bytes())

    def test_empty_session_id_uses_source_basename_hash(self) -> None:
        self.source = self.root / "custom-transcript.jsonl"
        self.source.write_bytes(b"opaque")
        expected_id = hashlib.sha256(self.source.name.encode("utf-8")).hexdigest()[:8]
        result = self.run_cli(self.payload(session_id=""))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(1, len(list(self.transcripts.glob(f"*-codex-{expected_id}.jsonl"))))

    def test_malformed_json_fails_with_single_line_diagnostic(self) -> None:
        result = self.run_cli("{not json")
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(1, len(result.stderr.rstrip().splitlines()))
        self.assertEqual([], list(self.transcripts.glob("*.jsonl")))

    def test_non_stop_event_is_rejected(self) -> None:
        self.source.write_bytes(b"secret")
        result = self.run_cli(self.payload(hook_event_name="PostToolUse"))
        self.assertNotEqual(0, result.returncode)
        self.assertNotIn("secret", result.stderr)

    def test_null_transcript_path_is_rejected(self) -> None:
        result = self.run_cli(self.payload(transcript_path=None))
        self.assertNotEqual(0, result.returncode)
        self.assertIn("transcript path", result.stderr.lower())

    def test_directory_source_is_rejected(self) -> None:
        result = self.run_cli(self.payload(transcript_path=str(self.root)))
        self.assertNotEqual(0, result.returncode)

    def test_non_passdown_cwd_is_rejected(self) -> None:
        self.source.write_bytes(b"secret")
        other = self.root / "other"
        other.mkdir()
        result = self.run_cli(self.payload(cwd=str(other)))
        self.assertNotEqual(0, result.returncode)
        self.assertEqual([], list(other.rglob("*.jsonl")))

    def test_replace_failure_preserves_existing_snapshot(self) -> None:
        self.source.write_bytes(b"new")
        destination = self.transcripts / "2026-07-17-1330-codex-019f6e8e.jsonl"
        destination.write_bytes(b"old")
        with mock.patch.object(ARCHIVER.os, "replace", side_effect=PermissionError("denied")):
            with self.assertRaises(ARCHIVER.ArchiveError):
                ARCHIVER.archive(self.payload())
        self.assertEqual(b"old", destination.read_bytes())
        self.assertEqual([], list(self.transcripts.glob("*.tmp")))


if __name__ == "__main__":
    unittest.main()
