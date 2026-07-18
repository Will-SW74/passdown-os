#!/bin/sh
# passdown-os 檢查點計數器 — 掛在各工具的 PostToolUse hook 使用
#
# 為什麼需要這個腳本：模型無法可靠地「自數」自己已經呼叫了幾次工具（內省不可信），
# 所以改由外部 hook 在每次工具呼叫後遞增一個計數檔。每滿 10 次，就輸出一段提醒文字。
# 外部計數不靠模型自覺；提醒是否進入 agent context 則依 hooks/README.md 的驗證矩陣判定。
#
# 前提：hook 執行時的工作目錄是專案根目錄（cc / codex 預設如此）。
#       若你的工具不是，把下面的 base 改成絕對路徑。
# 注意：sessions/.toolcount 已列入 .gitignore，屬本機暫存；
#       cc / codex 由 SessionStart hook 重置為 0；agy 依 Session Start Protocol 重置。

# 解析參數
FORMAT="plain"
for arg in "$@"; do
  case "$arg" in
    --json) FORMAT="json" ;;
  esac
done

# This counter is intentionally advisory. Concurrent hooks can read the same
# value and overwrite one another; do not use it as exact telemetry.
# Escape JSON-sensitive reminder characters so future wording changes cannot
# silently produce an invalid hook payload.
json_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

# 兩種佈局都支援：一般專案是 <root>/passdown-os/sessions；範本庫自己（框架即根目錄）是 <root>/sessions
base="${CLAUDE_PROJECT_DIR:-.}"
if [ -d "$base/passdown-os/sessions" ]; then
  COUNT_FILE="$base/passdown-os/sessions/.toolcount"
elif [ -d "$base/sessions" ]; then
  COUNT_FILE="$base/sessions/.toolcount"
else
  exit 0   # 找不到框架就不做事，hook 不該報錯打斷工作
fi

# 只用 shell built-in 讀取，確保 Git Bash 未加入 PATH 時仍可運作。
# 檔案不存在或內容不是數字時歸零（防呆：避免髒資料讓算術運算炸掉）。
n=""
if [ -r "$COUNT_FILE" ]; then
  IFS= read -r n < "$COUNT_FILE" || :
fi
case "$n" in
  ''|*[!0-9]*) n=0 ;;
esac

n=$((n + 1))
printf '%s' "$n" > "$COUNT_FILE" 2>/dev/null

# 每滿 10 次輸出提醒。stdout 是否注入 context 依各工具而定：
#   cc / codex 的 PostToolUse 需用 JSON additionalContext（見 hooks/README.md）以利注入 context；
#   純文字輸出在部分工具只會顯示在 transcript——安裝時請照 README 對應你的工具調整。
if [ $((n % 10)) -eq 0 ]; then
  msg="[passdown-os checkpoint] 本 session 已累計 ${n} 次工具呼叫：請先在 sessions/ 的當前 log append 一行進度（見 PROTOCOLS.md「持續存檔機制」），再繼續工作。"
  if [ "$FORMAT" = "json" ]; then
    escaped_msg=$(json_escape "$msg")
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s"}}\n' "$escaped_msg"
  else
    echo "$msg"
  fi
fi
