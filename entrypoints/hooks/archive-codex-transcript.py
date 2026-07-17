#!/usr/bin/env python3
"""為 Passdown OS 持續保存目前 Codex task 的逐字稿快照。"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


ROLLOUT_TIME = re.compile(r"rollout-(\d{4}-\d{2}-\d{2})T(\d{2})-(\d{2})-")


class ArchiveError(RuntimeError):
    """可安全顯示給使用者、且不包含逐字稿內容的歸檔錯誤。"""


def _snapshot_timestamp(source: Path) -> str:
    # 優先使用 rollout 名稱中的啟動時間，確保同一 task 每次 Stop 都命中相同檔名。
    match = ROLLOUT_TIME.search(source.name)
    if match:
        return f"{match.group(1)}-{match.group(2)}{match.group(3)}"
    return datetime.fromtimestamp(source.stat().st_ctime).strftime("%Y-%m-%d-%H%M")


def _snapshot_identifier(session_id: Any, source: Path) -> str:
    # 只保留跨平台檔名安全字元；完全無安全字元時才用 basename hash，避免路徑資訊外洩。
    safe = ""
    if isinstance(session_id, str):
        safe = re.sub(r"[^A-Za-z0-9]", "", session_id)
    if safe:
        return safe[:8].lower()
    return hashlib.sha256(source.name.encode("utf-8")).hexdigest()[:8]


def _passdown_root(project: Path) -> Path:
    # 下游 payload 固定在 passdown-os/；來源 repo 自用 hook 則允許 repo root，但必須確認腳本也在該 root 內。
    nested = project / "passdown-os"
    if (nested / "CONSTITUTION.md").is_file() and (nested / "transcripts").is_dir():
        return nested

    source_script = project / "entrypoints" / "hooks" / Path(__file__).name
    try:
        is_source_layout = source_script.resolve() == Path(__file__).resolve()
    except OSError:
        is_source_layout = False
    if is_source_layout and (project / "CONSTITUTION.md").is_file() and (project / "transcripts").is_dir():
        return project
    raise ArchiveError("cwd is not a Passdown OS project")


def archive(payload: Mapping[str, Any]) -> Path:
    # 先完成所有輸入與專案 marker 驗證，避免錯誤 hook cwd 將資料寫到非預期位置。
    if not isinstance(payload, Mapping):
        raise ArchiveError("hook input must be a JSON object")
    if payload.get("hook_event_name") != "Stop":
        raise ArchiveError("hook event must be Stop")

    transcript_path = payload.get("transcript_path")
    if not isinstance(transcript_path, str) or not transcript_path.strip():
        raise ArchiveError("no transcript path was provided")
    source = Path(transcript_path).expanduser()
    if not source.is_file():
        raise ArchiveError("transcript source is not a regular file")

    cwd_value = payload.get("cwd")
    if not isinstance(cwd_value, str) or not cwd_value.strip():
        raise ArchiveError("no project cwd was provided")
    passdown = _passdown_root(Path(cwd_value).expanduser())
    destination_dir = passdown / "transcripts"

    timestamp = _snapshot_timestamp(source)
    identifier = _snapshot_identifier(payload.get("session_id"), source)
    destination = destination_dir / f"{timestamp}-codex-{identifier}.jsonl"

    # 暫存檔放在目的目錄，讓 os.replace 保持同一檔案系統上的原子語意。
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{destination.stem}-", suffix=".tmp", dir=destination_dir, delete=False
        ) as output:
            temporary = Path(output.name)
            with source.open("rb") as input_file:
                shutil.copyfileobj(input_file, output)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, destination)
        temporary = None
    except (OSError, ValueError) as exc:
        raise ArchiveError(f"unable to update transcript snapshot: {type(exc).__name__}") from exc
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
    return destination


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        archive(payload)
        return 0
    except json.JSONDecodeError:
        print("codex transcript archive failed: malformed JSON input", file=sys.stderr)
    except ArchiveError as exc:
        print(f"codex transcript archive failed: {exc}", file=sys.stderr)
    except Exception as exc:  # Hook 邊界採防禦性攔截，絕不輸出逐字稿內容或來源路徑。
        print(f"codex transcript archive failed: unexpected {type(exc).__name__}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
