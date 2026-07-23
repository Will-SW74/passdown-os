# hooks — 三大 agent 的機制化防線（必裝）

> **必裝，不是選配（框架決策 PDOS-D-20260721-1）**：`INSTALL.md` 第 0.1 節會因為 hooks 的執行環境缺件就中止整個安裝，理由是「半套框架（有規則、沒 hooks）會讓機制化防線靜默失效，比不裝更危險」。既然缺前置條件就不准裝，hooks 本身不可能是選配。

本資料夾提供 cc / codex / agy 三者的 hook 範本與驗證工具，涵蓋以下自動化與機制化串接：

1. **SessionStart (開班自動注入)**：session 一開就把 `CURRENT.md` 塞進 context，並預建 session log slot——agent 忘不忘記讀，交接內容都在眼前。
2. ~~**PostToolUse 檢查點計數器**~~：已停用並刪除（2026-07-23）——實測發現頻繁 edit 導致 context 膨脹，token 成本遠超防護價值。
3. **SessionEnd / Git Pre-commit (結班驗證與警示)**：
   - [`session-end-check.sh`](session-end-check.sh)：SessionEnd 觸發時自動檢查 `.active_lock` 是否忘記摘牌，並執行逐字稿歸檔。
   - [`validate-handoff.sh`](validate-handoff.sh)：完整性檢查工具，確認 CURRENT.md 欄位、`Direct Memory Source` 指向的 log 檔與 `.active_lock` 狀態。
   - [`pre-commit-pdos.sh`](pre-commit-pdos.sh)：Git pre-commit 門禁範本，防止未完成 Passdown OS 結束協定即提交程式碼。

| Agent | 設定位置 | 範本與工具 |
| --- | --- | --- |
| cc | `.claude/settings.json` | [`settings.json.example`](settings.json.example)（SessionStart + SessionEnd） |
| codex | `.codex/hooks.json` | [`codex-hooks.json.example`](codex-hooks.json.example)（SessionStart + SessionEnd） |
| agy | `.agents/hooks.json` | [`agy-hooks.json.example`](agy-hooks.json.example)（PreInvocation） |

## 交接班 hooks 串接機制

- **開班流程 (Start Handoff Hook)**: 觸發 `session-start.sh`（Windows 透過 `run-posix-hook.ps1`），檢查 `.active_lock` 並注入最新 `CURRENT.md`。
- **結班/交接流程 (End Handoff Hook)**: 觸發 `session-end-check.sh`，若偵測到 `.active_lock` 仍掛載，發出警示提醒執行手動摘牌與記錄，避免孤兒會話鎖；同時呼叫 `archive-transcript.sh`。
- **Git Commit 門禁 (Pre-commit Hook)**: 可將 `pre-commit-pdos.sh` 複製至 `.git/hooks/pre-commit`，在提交變更前自動執行 `validate-handoff.sh`。

## 安裝與驗證

1. 依使用的 Agent，將範本 JSON 內容合併至 `.claude/settings.json`、`.codex/hooks.json` 或 `.agents/hooks.json`。
2. 啟動新對話驗證開班注入是否生效。
3. 執行 `./validate-handoff.sh` 驗證交接完整性。
