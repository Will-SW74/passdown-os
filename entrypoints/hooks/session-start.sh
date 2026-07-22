#!/bin/sh
# Passdown OS SessionStart 共用腳本。
# Why：把 CURRENT 注入與計數歸零集中在同一份 POSIX 邏輯，Windows 只負責找到 Git Bash，
# 避免為不同 shell 複製業務規則而產生 drift（PDOS-D-20260722-1）。

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

# 計數器只是本 session 的暫存訊號；每次 SessionStart 必須清零，避免承接上一輪數值。
# Why：整個資料夾 copy 或換 sandbox session 後，舊檔 ACL 可能禁止目前程序直接截斷；
# 在同目錄建立新檔再原子取代，可改用目錄權限並讓新檔取得本 session 的正確 ACL。
count_file="$framework_root/sessions/.toolcount"
count_tmp="${count_file}.$$"
if printf '0' > "$count_tmp" 2>/dev/null; then
  if ! mv -f "$count_tmp" "$count_file" 2>/dev/null; then
    # Windows sandbox 若不允許覆寫舊 inode，先用目錄權限移除再放入新檔。
    rm -f "$count_file" 2>/dev/null && mv "$count_tmp" "$count_file" 2>/dev/null
  fi
fi

echo '=== passdown-os 交接內容（SessionStart hook 自動注入）==='
if [ -f "$framework_root/handoff/CURRENT.md" ]; then
  cat "$framework_root/handoff/CURRENT.md"
else
  echo '（警告：找不到 handoff/CURRENT.md，請檢查框架是否就位）'
fi
echo '--- 以上即 CURRENT.md 全文；請依 passdown-os/CONSTITUTION.md 執行 Session 開始協定其餘步驟。'
