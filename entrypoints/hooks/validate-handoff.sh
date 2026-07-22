#!/bin/sh
# Passdown OS 交接班完整性自動驗證工具
# Why: 機制化執行 CONSTITUTION 6.7 節 Read-back 驗證與 6.9 節摘牌檢查，
# 可供手動執行、SessionEnd 呼叫或 Git pre-commit 門禁使用（PDOS-D-20260722-1）。

repo_root=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$repo_root" ]; then
  repo_root=$(pwd)
fi

if [ -d "$repo_root/passdown-os/sessions" ]; then
  framework_root="$repo_root/passdown-os"
elif [ -d "$repo_root/sessions" ]; then
  framework_root="$repo_root"
else
  echo "[Passdown OS 錯誤] 找不到 passdown-os 框架目錄！"
  exit 1
fi

current_file="$framework_root/handoff/CURRENT.md"

echo "=== 開始 Passdown OS 交接班完整性檢查 ==="
errors=0

# 1. 檢查 CURRENT.md 是否存在
if [ ! -f "$current_file" ]; then
  echo "[FAIL] 找不到 handoff/CURRENT.md 檔案"
  errors=$((errors + 1))
else
  echo "[PASS] handoff/CURRENT.md 存在"
  
  # 2. 檢查是否存在未填寫的預設佔位符
  if grep -q "<佔位文字>" "$current_file"; then
    echo "[FAIL] CURRENT.md 仍含有未填寫的 '<佔位文字>' 佔位符"
    errors=$((errors + 1))
  else
    echo "[PASS] CURRENT.md 無佔位符殘留"
  fi

  # 3. 檢查 Direct Memory Source 第一項引用的 session log 是否存在
  log_source=$(grep -A 5 "Direct Memory Source" "$current_file" | grep -o 'sessions/[^` )]*' | head -n 1)
  if [ -n "$log_source" ]; then
    target_log="$framework_root/$log_source"
    if [ -f "$target_log" ]; then
      echo "[PASS] Direct Memory Source 引用的 session log 確實存在: $log_source"

      # 4. 檢查是否有對應的逐字稿檔案 (transcripts/*.jsonl)
      base_log_name=$(basename "$log_source" .md)
      transcript_file="$framework_root/transcripts/${base_log_name}.jsonl"
      if [ -f "$transcript_file" ]; then
        echo "[PASS] 相對應的逐字稿檔案存在: transcripts/${base_log_name}.jsonl"
      else
        echo "[WARN] 尚未發現相對應的逐字稿檔案 (transcripts/${base_log_name}.jsonl)，嘗試自動觸發歸檔..."
        script_dir=$(dirname "$0")
        if [ -f "$script_dir/archive-transcript.sh" ]; then
          sh "$script_dir/archive-transcript.sh" 2>/dev/null
        fi
        if [ -f "$transcript_file" ]; then
          echo "[PASS] 自動歸檔成功: transcripts/${base_log_name}.jsonl"
        else
          echo "[INFO] 若本專案採逐字稿模式 B（追蹤），請記得確認 transcripts/ 歸檔"
        fi
      fi

    else
      echo "[FAIL] Direct Memory Source 指向的 session log 不存在: $log_source"
      errors=$((errors + 1))
    fi
  else
    echo "[WARN] CURRENT.md 未能解析出 Direct Memory Source 的 log 路徑"
  fi
fi

# 5. 檢查會話鎖 active_lock
if [ -f "$framework_root/sessions/.active_lock" ]; then
  lock_content=$(cat "$framework_root/sessions/.active_lock" 2>/dev/null)
  echo "[WARN] .active_lock 仍掛在 sessions/ 中 (內容: $lock_content)。若是交接結班請記得摘牌！"
else
  echo "[PASS] .active_lock 已正常摘牌"
fi

echo "=========================================="
if [ "$errors" -gt 0 ]; then
  echo "[結果] 發現 $errors 個交接缺失，請修正後再提交 commit。"
  exit 1
else
  echo "[結果] 交接班完整性檢查通過！"
  exit 0
fi
