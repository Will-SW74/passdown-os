# Passdown OS — 跨 AI Agent 協作框架

> *Passdown*：軍隊與護理界的「交班日誌」——離班的人寫給接班的人，讓下一班不用猜就能接手。

讓 Claude Code / Codex / Antigravity（或任何組合的 AI agent）在同一個專案上無縫接力的**純 Markdown** 框架：管 session 之間怎麼交接、記憶存哪裡、判斷怎麼做。零依賴、無 daemon、無資料庫——整包複製進專案就能用。

*A pure-Markdown, zero-dependency framework for seamless handoffs between AI coding agents (Claude Code / Codex / Antigravity / any). It governs session-to-session handoff protocols, shared memory, context-budget economics, and externalized judgment rubrics — so a cheap model tomorrow inherits the discipline of an expensive model today. Docs are currently in Traditional Chinese.*

## 交接流程一圖看懂

```mermaid
flowchart TD
    subgraph S1["Session N（cc / codex / agy 任一）"]
        A1["開始：讀 CONSTITUTION.md ＋ CURRENT.md<br/>（cc 裝了 hook 會自動注入）"] --> A2{"復原偵測：<br/>CURRENT.md 與最新 log<br/>時間戳一致？"}
        A2 -- "log 較新 → 上次交接沒跑完" --> A2b["先讀最新 log<br/>修復 CURRENT.md"] --> A3
        A2 -- 一致 --> A3["循 Context Index 錨點<br/>讀指定 session log 與程式碼行號"]
        A3 --> A4["動工（micro-task）"]
        A4 --> A5{"存檔線？<br/>task 完成／切子系統／<br/>60% CT／15 輪"}
        A5 -- 未觸發 --> A4
    end
    A5 -- "觸發（70% 為硬紅線）" --> E1
    subgraph E["Session 結束協定（cc 可打 /handoff 一鍵觸發）"]
        E1["覆寫 handoff/CURRENT.md<br/>（Next step 具體到不用猜）"] --> E2["新增 sessions/ log<br/>（Scratchpad 記下未竟思路）"]
        E2 --> E3["決策 → memory/decisions.md<br/>坑 → known-issues.md<br/>本機私有記憶回寫"]
        E3 --> E4["Read-back 驗證：<br/>無佔位符、錨點路徑存在"]
        E4 --> E5["commit（feature branch）"]
    end
    E5 --> F[("passdown-os/<br/>唯一權威記錄<br/>（純 Markdown、進版控）")]
    F -- 交班 --> B1["Session N+1：另一個 agent、<br/>或明天的自己——不用猜、不重工"]
    B1 -.-> A1
```

## 導入新專案

1. 把本 repo 的內容放進專案根目錄的 `passdown-os/` 資料夾（clone 後複製，或加為 subtree）。
2. 跑 [`GOLDEN_TEMPLATE.md`](GOLDEN_TEMPLATE.md) 的「套用後自檢清單」重置狀態檔。
3. 依 [`entrypoints/README.md`](entrypoints/README.md) 設定各 agent 入口檔；用 cc 的話順手裝上 SessionStart hook 與 `/handoff` 指令。

## 從哪裡開始讀

| 你是誰 | 讀什麼 |
| --- | --- |
| 剛接手的 agent（每次 session 開始） | [`CONSTITUTION.md`](CONSTITUTION.md) → [`handoff/CURRENT.md`](handoff/CURRENT.md)，依 Session 開始協定往下 |
| 遇到特定情境（git 衝突、記憶同步、維護） | [`PROTOCOLS.md`](PROTOCOLS.md) 對應章節（被指到才讀） |
| 要交辦任務 / 派 subagent | [`DISPATCH.md`](DISPATCH.md) ＋ [`prompts/`](prompts/README.md) 範本 |
| 對「做不做、停不停、算不算完成」猶豫 | [`RUBRICS.md`](RUBRICS.md) |
| 要把框架複製到新專案的人 | [`GOLDEN_TEMPLATE.md`](GOLDEN_TEMPLATE.md)，入口檔設定見 [`entrypoints/README.md`](entrypoints/README.md) |

完整檔案地圖見 `CONSTITUTION.md` 的「檔案地圖」章節。

## 規則檔的分工

- **CONSTITUTION.md** — session **之間**的核心協定（每次必讀）：交接、context 紅線、task 切分、卡關、誠實條款。
- **PROTOCOLS.md** — 核心協定的細節篇（效力相同，被指到才讀）：Spectra 整合、記憶接力、Git 策略、衝突處理、本機記憶同步、維護規則。
- **DISPATCH.md** — session **之內**：怎麼調度模型與 subagent、交辦、回報、升降級、驗證。cc 的自動化實作見 `entrypoints/claude-agents/`。
- **RUBRICS.md** — 決策點：把「需要判斷力」的時刻寫成可照做的 checklist。
