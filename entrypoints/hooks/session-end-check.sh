#!/bin/sh
# Passdown OS SessionEnd 交接班檢查與清理共用腳本
# Why: 集中 SessionEnd 事件處置邏輯，包含檢查是否正常摘牌與觸發逐字稿歸檔，
# 防止未完成 Session 結束協定即離開對話（PDOS-D-20260722-1）。

# Why: 透過 Git 定位專案根目錄，確保從子目錄啟動時仍能正確找到 passdown-os 路徑
repo_root=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$repo_root" ]; then
  repo_root=$(pwd)
fi

# 支援「專案子目錄/passdown-os」與「母庫獨立目錄」兩種部署結構
if [ -d "$repo_root/passdown-os/sessions" ]; then
  framework_root="$repo_root/passdown-os"
elif [ -d "$repo_root/sessions" ]; then
  framework_root="$repo_root"
else
  exit 0
fi

# Why: 讀取 stdin 以傳遞給逐字稿歸檔腳本（如 cc SessionEnd 傳遞的 JSON）
input=$(cat)

# 1. 檢查 active_lock：若檔依然存在，代表未執行「摘牌簽退」步驟
if [ -f "$framework_root/sessions/.active_lock" ]; then
  lock_info=$(cat "$framework_root/sessions/.active_lock" 2>/dev/null)
  echo "[Passdown OS Hook 警告] 偵測到未摘牌的會話鎖 (.active_lock): $lock_info" >&2
  echo "[Passdown OS Hook 警告] 請確認是否已完成 Session 結束協定（更新 CURRENT.md, 建立 session log, 並摘牌）。" >&2
fi

# 2. 執行逐字稿歸檔（若存在 archive-transcript.sh 且環境支援）
script_dir=$(dirname "$0")
if [ -f "$script_dir/archive-transcript.sh" ]; then
  printf '%s' "$input" | sh "$script_dir/archive-transcript.sh" 2>/dev/null
fi

exit 0
