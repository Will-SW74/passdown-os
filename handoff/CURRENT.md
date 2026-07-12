# Current State

_Last updated: 2026-07-13 00:20 by cc_

## Active change

`openspec/changes/wire-v02-hardening-and-startup-rules`（18/19）——僅剩 task 6.1：於 agy 環境實測 hooks 注入後回寫結果，即可 archive。

## Where we left off

2026-07-12 全日由 cc 完成框架大修並全數 push 上 main（origin 同步）：v0.2 接線修正＋啟動紀律、消化 07-11 parked change（語意檢查、可攜錨點、PreCompact）、衍生檔裁決（留 CHECKLIST／刪 local-agent-sync）、INSTALL.md（agent 自主安裝）、天條＋commit 安全檢查、transcripts/ 逐字稿歸檔區＋決策 ID 約定（D-20260712-1～6）、DISPATCH CT 查證表填值、期末架構 review（修掉 counter 腳本佈局 bug、README 流程圖 stale、GOLDEN 不變規則清單漏項）。分支只剩 main，git 線圖乾淨。

## Next concrete step

依 INSTALL.md 把框架裝進一個真實專案跑一輪實戰——過程中順帶完成三項【待實測】：(1) agy hooks 注入（開新 agy 對話問它看不看得到 CURRENT.md → 回寫 hooks README → 勾 wire-v02 task 6.1 → archive 該 change）；(2) cc PreCompact stdout 行為；(3) archive-transcript.sh 在真實 SessionEnd 的 Windows 路徑還原。

## Context Index / Memory Anchors

- **Direct Memory Source**: `sessions/2026-07-12-1530-cc-wire-hardening-and-startup-rules.md`
- **決策紀錄**: `memory/decisions.md` D-20260712-1 ～ D-20260712-6
- **Code Symbol Anchor**: [CONSTITUTION.md](../CONSTITUTION.md) 第 5-6 節（開始/結束協定）、[archive-transcript.sh](../entrypoints/hooks/archive-transcript.sh)、[checkpoint-counter.sh](../entrypoints/hooks/checkpoint-counter.sh)（皆為雙佈局路徑解析）

## Blockers

none（三項不阻斷的【待實測】見 Next concrete step 與 `entrypoints/hooks/README.md` 標註）
