#!/bin/sh
# passdown-os 逐字稿自動歸檔 — 掛在 cc 的 SessionEnd hook 使用
#
# 為什麼需要：cc 的逐字稿存在 ~/.claude/projects/<hash>/*.jsonl，工具可能清理、
# 換機器帶不走、也跟 sessions/ 的 log 對不上號。本腳本在 session 結束時把當次
# 逐字稿複製進專案的 passdown-os/transcripts/（gitignored，不入版控），
# 讓完整互動記錄跟著專案資料夾走。
#
# 機制：SessionEnd hook 的 stdin 會收到一份 JSON，內含 transcript_path 與
# session_id 欄位。優先用 jq 解析；沒有 jq 時退回 sed 粗抽——
# 【待實測】Windows 路徑在 JSON 中是雙反斜線（C:\\Users\\...），sed fallback
# 抽出後 cp 是否能吃，需在真實 SessionEnd 觸發時驗證一次。

input=$(cat)

if command -v jq >/dev/null 2>&1; then
  tp=$(printf '%s' "$input" | jq -r '.transcript_path // empty')
  sid=$(printf '%s' "$input" | jq -r '.session_id // empty')
else
  tp=$(printf '%s' "$input" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
  sid=$(printf '%s' "$input" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
  # sed 抽出的 Windows 路徑帶雙反斜線，還原成單反斜線讓 cp 能用
  tp=$(printf '%s' "$tp" | sed 's/\\\\/\\/g')
fi

# 找不到逐字稿就靜默結束——hook 不該因此打斷 session 收尾
[ -n "$tp" ] && [ -f "$tp" ] || exit 0

# 目的地：優先用 hook 提供的專案根目錄環境變數，其次用目前工作目錄。
# 兩種佈局都支援：一般專案是 <root>/passdown-os/transcripts；
# 範本庫自己（框架即根目錄）則是 <root>/transcripts。
base="${CLAUDE_PROJECT_DIR:-.}"
if [ -d "$base/passdown-os/transcripts" ]; then
  dest_dir="$base/passdown-os/transcripts"
elif [ -d "$base/transcripts" ]; then
  dest_dir="$base/transcripts"
else
  exit 0   # 專案沒啟用歸檔區就不做事
fi

# 命名：日期時間-cc-<session id 前 8 碼>；與 sessions/ log 同前綴、按時間可對應
short_id=$(printf '%s' "$sid" | cut -c1-8)
[ -n "$short_id" ] || short_id="unknown"
cp "$tp" "$dest_dir/$(date +%Y-%m-%d-%H%M)-cc-${short_id}.jsonl" 2>/dev/null

exit 0
