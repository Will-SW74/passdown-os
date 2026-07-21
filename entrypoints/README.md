# Entrypoints — Agent 入口設定檔範本

每個 AI Agent 工具都有自己的「入口設定檔」，agent 啟動時會自動讀取。把 `passdown-os/` 的入口段落放進對應的設定檔，agent 就會在每次 session 開始時自動依照 CONSTITUTION.md 的協定運作。

## 怎麼用

1. 複製對應的 `.example` 檔案到新專案的正確位置（見下表）。
2. 移除 `.example` 副檔名。
3. 若該檔案已存在，把範本裡的 `## Passdown OS` 段落**附加**到現有檔案末尾即可。

## 各 Agent 對應的入口檔

| Agent | 範本 | 放置位置 | 說明 |
| --- | --- | --- | --- |
| **cc**（Claude Code） | `CLAUDE.md.example` | 專案根目錄 `CLAUDE.md` | Claude Code 啟動時自動讀取 |
| **codex**（OpenAI Codex CLI） | `CODEX.md.example` | 專案根目錄 `AGENTS.md` | Codex CLI 啟動時自動讀取 |
| **agy**（Google Antigravity） | `AGENTS.md.example` | 專案根目錄 `.agents/AGENTS.md`（或根目錄 `AGENTS.md`） | AGY 啟動時自動讀取 |

> **Note**: codex 和 agy 都可能讀取 `AGENTS.md`，如果同時使用這兩個工具且共用同一個 `AGENTS.md`，只需放入一份入口段落即可——內容對所有 agent 通用。

> **未確認**：agy 是否自動讀取 `.agents/AGENTS.md` 未在本框架實測過。首次導入新專案時建議實測一次：開新 agy 對話，看它是否主動遵循入口段落；若沒有，改放專案根目錄 `AGENTS.md`。實測結果請回寫更新本表。

## cc SessionStart hook（必裝，見 D-20260721-1）

[`hooks/`](hooks/README.md) 提供 cc 的 SessionStart hook 設定範本：每次新 session（含 `/clear` 與 compact 後）自動把 `passdown-os/handoff/CURRENT.md` 注入 context，把「agent 自覺讀交接」變成機制保證。已實測驗證（2026-07）。安裝方式見該資料夾 README。

## cc `/handoff` 指令（選用，建議安裝）

[`commands/handoff.md`](commands/handoff.md) 是 cc 的自訂斜線指令：複製到專案的 `.claude/commands/` 後，收工時打 `/handoff` 就會確定性地觸發完整的 Session 結束協定（含 read-back 驗證與逐步回報）。搭配 SessionStart hook 使用，交接的頭尾就都從「靠紀律」變成「靠機制」。

## cc 自動調度範本組（選用）

[`claude-agents/`](claude-agents/README.md) 底下是 cc 專用的 subagent 定義檔（searcher/implementer/researcher/reviewer/verifier），把 `DISPATCH.md` 的模型調度守則自動化。要啟用的話，把五個 agent 檔複製到新專案的 `.claude/agents/`，並使用 `CLAUDE.md.example` 裡含「調度模式」段落的完整版本。不用 cc、或不想用自動調度時可整個跳過，不影響框架其餘部分。
