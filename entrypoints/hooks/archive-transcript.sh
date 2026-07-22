#!/bin/sh
# passdown-os 逐字稿自動歸檔 — 支援 cc / codex / agy 三大 agent
#
# 為什麼需要：各 agent 的逐字稿存在全域對話紀錄區（如 ~/.claude/projects/、~/.gemini/antigravity-cli/brain/、~/.codex/sessions/），
# 換機器帶不走、也跟 sessions/ 的 log 對不上號。本腳本在 session 結束時把當次逐字稿複製進專案的 passdown-os/transcripts/，
# 讓完整互動記錄跟著專案資料夾走（PDOS-D-20260722-1）。

repo_root=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$repo_root" ]; then
  repo_root=$(pwd)
fi

if [ -d "$repo_root/passdown-os/transcripts" ]; then
  dest_dir="$repo_root/passdown-os/transcripts"
elif [ -d "$repo_root/transcripts" ]; then
  dest_dir="$repo_root/transcripts"
else
  exit 0
fi

tp=""
agent="unknown"
sid=""

# 1. 嘗試由 stdin 讀取 JSON（cc SessionEnd 等事件）
if [ ! -t 0 ]; then
  input=$(cat)
  if command -v jq >/dev/null 2>&1; then
    tp=$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null)
    sid=$(printf '%s' "$input" | jq -r '.session_id // empty' 2>/dev/null)
  else
    tp=$(printf '%s' "$input" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    sid=$(printf '%s' "$input" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    tp=$(printf '%s' "$tp" | sed 's/\\\\/\\/g')
  fi
  [ -n "$tp" ] && agent="cc"
fi

# 2. 若非 cc stdin 傳入，嘗試定位 Antigravity (agy) 最新逐字稿
if [ -z "$tp" ] || [ ! -f "$tp" ]; then
  home_dir="${HOME:-$USERPROFILE}"
  agy_brain="$home_dir/.gemini/antigravity-cli/brain"
  if [ -d "$agy_brain" ]; then
    # 尋找最新 mtime 的 transcript.jsonl
    latest_agy=$(find "$agy_brain" -name "transcript.jsonl" -type f -printf "%T@ %p\n" 2>/dev/null | sort -nr | head -n 1 | cut -d' ' -f2-)
    if [ -f "$latest_agy" ]; then
      tp="$latest_agy"
      agent="agy"
    fi
  fi
fi

# 3. 若仍未找到，嘗試定位 Codex (codex) 最新逐字稿
if [ -z "$tp" ] || [ ! -f "$tp" ]; then
  home_dir="${HOME:-$USERPROFILE}"
  codex_sessions="$home_dir/.codex/sessions"
  if [ -d "$codex_sessions" ]; then
    latest_codex=$(find "$codex_sessions" -name "*.jsonl" -type f -printf "%T@ %p\n" 2>/dev/null | sort -nr | head -n 1 | cut -d' ' -f2-)
    if [ -f "$latest_codex" ]; then
      tp="$latest_codex"
      agent="codex"
    fi
  fi
fi

[ -n "$tp" ] && [ -f "$tp" ] || exit 0

# 命名一律綁「被複製的 transcript 自身 session_id」，與內容同源；杜絕多 agent 交錯時
# 「檔名取最新 log、內容取本 session」的張冠李戴（PDOS-D-20260722-6）。
framework_root=$(dirname "$dest_dir")
short_id=$(printf '%s' "$sid" | cut -c1-8)
if [ -n "$short_id" ]; then
  target_file="$dest_dir/$(date +%Y-%m-%d-%H%M)-${agent}-${short_id}.jsonl"
else
  # 只有無 session_id（agy/codex 的 mtime 尋檔路徑）才退回最新 log 名
  latest_log=$(ls -1t "$framework_root/sessions/"*.md 2>/dev/null | grep -v 'INDEX.md' | grep -v '_template.md' | head -n 1)
  if [ -n "$latest_log" ]; then
    target_file="$dest_dir/$(basename "$latest_log" .md).jsonl"
  else
    target_file="$dest_dir/$(date +%Y-%m-%d-%H%M)-${agent}-transcript.jsonl"
  fi
fi

cp "$tp" "$target_file" 2>/dev/null
exit 0
