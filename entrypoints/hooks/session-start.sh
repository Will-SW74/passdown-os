#!/bin/sh
# Passdown OS SessionStart 共用腳本。
# Why：把 CURRENT 注入、計數歸零、pre-commit 門禁自癒、以及 session log slot 預建
# 集中在同一份 POSIX 邏輯，Windows 只負責找到 Git Bash，避免為不同 shell/agent
# 複製業務規則而產生 drift（PDOS-D-20260722-1）。
#
# 參數：
#   --agent <code>  本次 agent 代號（cc|codex|agy），用於 log 檔名與內文；預設 unknown。
#   --new-log       只在真正「開新 session」(startup) 事件傳入；建立本 session 的 log slot。
#                   clear|compact|resume 等 re-fire 不得傳入，否則每次壓縮都會洗出重複 log。

agent="unknown"
new_log=0
while [ $# -gt 0 ]; do
  case "$1" in
    --agent) agent="${2:-unknown}"; shift 2 ;;
    --agent=*) agent="${1#--agent=}"; shift ;;
    --new-log) new_log=1; shift ;;
    *) shift ;;
  esac
done

# Why：Codex 可能從 repo 子目錄啟動；以 Git root 定位才能讓 hook 不依賴當下 cwd。
repo_root=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$repo_root" ]; then
  repo_root=$(pwd)
fi

# 同時支援「框架安裝在專案/passdown-os」與「框架母庫本身」兩種佈局。
if [ -d "$repo_root/passdown-os/sessions" ]; then
  framework_root="$repo_root/passdown-os"
elif [ -d "$repo_root/sessions" ]; then
  framework_root="$repo_root"
else
  echo '（警告：找不到 passdown-os 框架，請檢查安裝位置）'
  exit 0
fi

# Why：Git pre-commit 門禁若靠 .git/hooks/（不受版控），任何 clone/pull 都帶不過去 → 門禁一再失效。
# 改用受版控的 core.hooksPath，並在每次 SessionStart 冪等自癒：以 framework_root 推導 hooks 目錄
# 相對 repo_root 的路徑（母庫本身為 entrypoints/hooks；安裝在專案則為 passdown-os/entrypoints/hooks），
# 確保任一 agent、任一機器開新 session 後門禁一定就位（PDOS-D-20260722-3）。
hooks_dir="$framework_root/entrypoints/hooks"
if [ -f "$hooks_dir/pre-commit" ] && [ -n "$repo_root" ]; then
  hooks_rel=${hooks_dir#"$repo_root"/}
  if [ "$hooks_rel" != "$hooks_dir" ] && \
     [ "$(git -C "$repo_root" config --get core.hooksPath 2>/dev/null)" != "$hooks_rel" ]; then
    git -C "$repo_root" config core.hooksPath "$hooks_rel" 2>/dev/null \
      && echo "[passdown-os] 已自癒 Git pre-commit 門禁（core.hooksPath=$hooks_rel）。"
  fi
fi

# Why：session log 過去只在「結束協定」建立，靠 agent 自律開檔容易遺漏。
# 於 startup（僅此一次）預建 log slot，把「靠 agent 自律」升級為「hook 強制預建」，
# 並寫 .active_session 指標讓 agent 解析「當前 log」是哪一份（PDOS-D-20260722-7）。
if [ "$new_log" = "1" ]; then
  sessions_dir="$framework_root/sessions"
  template="$sessions_dir/_template.md"
  stamp=$(date '+%Y-%m-%d-%H%M')
  header_time=$(date '+%Y-%m-%d %H:%M')
  # slug 先給 "session" 佔位；結束協定時 agent 改成描述本次工作的 3-5 詞並填內文。
  log_file="$sessions_dir/${stamp}-${agent}-session.md"
  if [ ! -f "$log_file" ]; then
    {
      printf '# Session: %s (%s)\n' "$header_time" "$agent"
      printf '<!-- hook 於 startup 預建的 slot；結束協定時填寫，並把檔名 slug 由 session 改成描述本次工作的 3-5 詞 -->\n'
      tail -n +2 "$template" 2>/dev/null
    } > "$log_file" 2>/dev/null \
      && echo "[passdown-os] 已預建本 session log slot：sessions/${stamp}-${agent}-session.md（結束協定時填寫並改 slug）。"
  fi
  # 指標檔與 .active_lock 同性質：執行期暫存、不進版控。
  printf '%s' "${stamp}-${agent}-session.md" > "$sessions_dir/.active_session" 2>/dev/null
fi

echo '=== passdown-os 交接內容（SessionStart hook 自動注入）==='
if [ -f "$framework_root/handoff/CURRENT.md" ]; then
  cat "$framework_root/handoff/CURRENT.md"
else
  echo '（警告：找不到 handoff/CURRENT.md，請檢查框架是否就位）'
fi
echo '--- 以上即 CURRENT.md 全文；請依 passdown-os/CONSTITUTION.md 執行 Session 開始協定其餘步驟。'
