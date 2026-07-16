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

> **agy 入口仍需逐專案驗證**：先把唯一一份 `## Passdown OS` 段落放到 `.agents/AGENTS.md`，開 fresh agy session，直接要求它指出本專案的 Session 開始協定入口。能引用 `passdown-os/CONSTITUTION.md` 與 `handoff/CURRENT.md` 才算該路徑生效。若沒有，從 `.agents/AGENTS.md` 移除該段後，將同一段合併到根目錄 `AGENTS.md`，再開另一個 fresh session 重驗。最後只保留已證明生效的一份；兩個位置都無法證明時，標記 `unverified`，不得宣稱 agy 已接入。

### agy 入口驗收分支

| 驗收結果 | 最終狀態 | 必須回報 |
| --- | --- | --- |
| `.agents/AGENTS.md` 在 fresh session 生效 | 只保留 `.agents/AGENTS.md` 的 Passdown OS 段落 | `effective entrypoint: .agents/AGENTS.md` |
| 第一條失敗、根目錄 `AGENTS.md` 生效 | 從 `.agents/AGENTS.md` 移除該段，只保留根目錄版本 | `effective entrypoint: AGENTS.md (fallback)` |
| 兩條都無法證明 | 不把任一路徑寫成已生效；保留使用者指定的一份候選並標 `unverified` | 兩次 fresh-session 驗證結果與後續人工調查項目 |

## cc SessionStart hook（選用，建議安裝）

[`hooks/`](hooks/README.md) 提供 cc 的 SessionStart hook 設定範本：每次新 session（含 `/clear` 與 compact 後）自動把 `passdown-os/handoff/CURRENT.md` 注入 context，把「agent 自覺讀交接」變成機制保證。已實測驗證（2026-07）。安裝方式見該資料夾 README。

## cc `/handoff` 指令（選用，建議安裝）

[`commands/handoff.md`](commands/handoff.md) 是 cc 的自訂斜線指令：複製到專案的 `.claude/commands/` 後，收工時打 `/handoff` 就會確定性地觸發完整的 Session 結束協定（含 read-back 驗證與逐步回報）。搭配 SessionStart hook 使用，交接的頭尾就都從「靠紀律」變成「靠機制」。

## cc 自動調度範本組（選用）

[`claude-agents/`](claude-agents/README.md) 底下是 cc 專用的 subagent 定義檔（searcher/implementer/researcher/reviewer/verifier），把 `DISPATCH.md` 的模型調度守則自動化。要啟用的話，把五個 agent 檔複製到新專案的 `.claude/agents/`，並使用 `CLAUDE.md.example` 裡含「調度模式」段落的完整版本。不用 cc、或不想用自動調度時可整個跳過，不影響框架其餘部分。
