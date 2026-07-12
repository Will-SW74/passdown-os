# claude-agents — cc 專用的自動調度 subagent 範本組

這是 [`DISPATCH.md`](../../DISPATCH.md) 調度守則在 Claude Code（cc）上的**自動化實作**：把「什麼任務派給什麼等級的模型」編譯成 cc 的 subagent 定義檔，主對話（指揮官）依路由表自動分派，便宜模型跑髒活、主對話只收結論。

## 安裝

1. 把本資料夾底下的五個 agent 檔（不含本 README）複製到專案根目錄的 `.claude/agents/`。
2. 確認專案 `CLAUDE.md` 已含「調度模式」段落（見 [`../CLAUDE.md.example`](../CLAUDE.md.example)）。
3. 重啟 cc session 後，用 `/agents` 確認五個 subagent 已被載入。

## 路由表

| 任務型態 | subagent | model | 對應交辦範本 |
| --- | --- | --- | --- |
| 搜尋/定位 | `searcher` | haiku | `prompts/search.md` |
| 實作/重構 | `implementer` | sonnet | `prompts/implement.md` / `refactor.md` |
| 研究/方案比較 | `researcher` | sonnet | `prompts/research.md` |
| 審查 | `reviewer` | opus | `prompts/review.md` |
| 交付前 read-back 驗證 | `verifier` | haiku | —（合約內嵌） |

升降級依 `DISPATCH.md` 第 5 節：subagent 錯 1 次 → 上一階模型重派（附錯誤內容）；同一子任務連錯 2 次 → 帶完整失敗軌跡收回主對話自做或問使用者。

## 兩個設計要點（改動前先理解）

1. **model 用別名（haiku/sonnet/opus），不寫死版本號**——別名會解析到當下環境的現行版本，避免模型更新後範本變成過時地雷（呼應 CONSTITUTION 誠實條款：不憑記憶填型號）。
2. **subagent 是冷啟動的**：它看不到主對話的任何脈絡。所以 (a) 每個定義檔已內嵌回報合約，不依賴 subagent 自己去讀 `passdown-os/`；(b) 指揮官交辦時，必須把填好的交辦單內容（目標與動機／範圍／驗收條件）完整放進派工 prompt 裡，只丟一句「去修 bug」等於丟掉整套制度。
3. **框架引用使用專案根目錄相對的純文字路徑**：這些定義檔會從 `passdown-os/entrypoints/claude-agents/` 複製到 `<project>/.claude/agents/`，檔案深度會改變。因此一律寫 `passdown-os/RUBRICS.md`，不要改成以定義檔位置解析的 Markdown 相對連結；來源裡可點擊，不代表安裝後仍可攜。
