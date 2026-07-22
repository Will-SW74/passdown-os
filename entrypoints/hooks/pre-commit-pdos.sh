#!/bin/sh
# Passdown OS Git Pre-commit 門禁腳本
# Why: 防止在變更程式碼時忘記完成 Passdown OS 結束協定，確保交接記錄進版控（PDOS-D-20260722-1）。

repo_root=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$repo_root" ]; then
  repo_root=$(pwd)
fi

# 尋找 validate-handoff.sh
validate_script=""
if [ -f "$repo_root/passdown-os/entrypoints/hooks/validate-handoff.sh" ]; then
  validate_script="$repo_root/passdown-os/entrypoints/hooks/validate-handoff.sh"
elif [ -f "$repo_root/entrypoints/hooks/validate-handoff.sh" ]; then
  validate_script="$repo_root/entrypoints/hooks/validate-handoff.sh"
fi

if [ -n "$validate_script" ]; then
  sh "$validate_script"
  exit $?
else
  exit 0
fi
