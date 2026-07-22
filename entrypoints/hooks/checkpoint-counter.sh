#!/bin/sh
# passdown-os 檢查點計數器 — 掛在各工具的 PostToolUse hook 使用
#
# 為什麼需要這個腳本：模型無法可靠地「自數」自己已經呼叫了幾次工具（內省不可信），
# 所以改由外部 hook 在每次工具呼叫後遞增一個計數檔。每滿 10 次，就輸出一段提醒文字，
# 由各工具的 hook 機制注入 agent 的 context——這才是真正「不靠自覺」的持續存檔觸發器。
#
# Why：Codex 可能從 repo 子目錄啟動，因此優先由 Git root 定位；cc 的
# CLAUDE_PROJECT_DIR 仍保留較高優先權，避免改變既有 cc 行為。
# 注意：sessions/.toolcount 已列入 .gitignore，屬本機暫存；
#       SessionStart hook 應把它重置為 0（見各工具的 hooks 範本）。

# 解析參數
FORMAT="plain"
for arg in "$@"; do
  case "$arg" in
    --json) FORMAT="json" ;;
  esac
done

# 兩種佈局都支援：一般專案是 <root>/passdown-os/sessions；範本庫自己（框架即根目錄）是 <root>/sessions
if [ -n "$CLAUDE_PROJECT_DIR" ]; then
  base="$CLAUDE_PROJECT_DIR"
else
  base=$(git rev-parse --show-toplevel 2>/dev/null)
  if [ -z "$base" ]; then
    base="."
  fi
fi
if [ -d "$base/passdown-os/sessions" ]; then
  COUNT_FILE="$base/passdown-os/sessions/.toolcount"
elif [ -d "$base/sessions" ]; then
  COUNT_FILE="$base/sessions/.toolcount"
else
  exit 0   # 找不到框架就不做事，hook 不該報錯打斷工作
fi

# 讀取現值；檔案不存在或內容不是數字時歸零（防呆：避免髒資料讓算術運算炸掉）
n=$(cat "$COUNT_FILE" 2>/dev/null)
case "$n" in
  ''|*[!0-9]*) n=0 ;;
esac

n=$((n + 1))
# Why：不同 sandbox session 可能無法截斷上一輪建立的檔；同目錄原子取代可讓 ACL 跟著
# 當前 session 重建，也避免工具並行時讀到半寫入內容。
COUNT_TMP="${COUNT_FILE}.$$"
if printf '%s' "$n" > "$COUNT_TMP" 2>/dev/null; then
  if ! mv -f "$COUNT_TMP" "$COUNT_FILE" 2>/dev/null; then
    rm -f "$COUNT_FILE" 2>/dev/null && mv "$COUNT_TMP" "$COUNT_FILE" 2>/dev/null
  fi
fi

# 每滿 10 次輸出提醒。stdout 是否注入 context 依各工具而定：
#   cc / codex 的 PostToolUse 需用 JSON additionalContext（見 hooks/README.md）以利注入 context；
#   純文字輸出在部分工具只會顯示在 transcript——安裝時請照 README 對應你的工具調整。
if [ $((n % 10)) -eq 0 ]; then
  # Why：SessionStart hook 於 startup 會把「當前 log」檔名寫進 .active_session；
  #      這裡讀出來讓提醒具名指向真實檔案，而非空泛的「當前 log」（PDOS-D-20260722-7）。
  sess_dir=$(dirname "$COUNT_FILE")
  active=$(cat "$sess_dir/.active_session" 2>/dev/null)
  case "$active" in
    ''|*[!0-9A-Za-z._-]*) target="sessions/ 的當前 log" ;;
    *) target="sessions/${active}" ;;
  esac
  msg="[passdown-os checkpoint] 本 session 已累計 ${n} 次工具呼叫：請先在 ${target} append 一行進度（見 PROTOCOLS.md「持續存檔機制」），再繼續工作。"
  if [ "$FORMAT" = "json" ]; then
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s"}}\n' "$msg"
  else
    echo "$msg"
  fi
fi
