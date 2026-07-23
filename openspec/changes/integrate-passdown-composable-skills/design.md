## Context

Passdown OS 的核心價值是把跨 session 與跨 agent 的狀態寫回專案，形成可追溯、可復原的共享真相；一般 handoff skill 則偏向把單次對話壓縮成暫存文件。兩者可以互補，但現有 Passdown 規則包含固定 agent 代號、context 百分比、每次必寫 log 與強制調度政策，使其不易作為小型、工具中立的 Agent Skill 被採用。

本 change 在目前只有 Spectra 骨架的 repository 中建立可重用的第一版技能與模板。使用者、下一個接手 agent，以及維護 Passdown 模板的人都是此設計的利害關係人。實作必須維持純 Markdown、零執行期依賴，且不得複製第三方 skill 內容。

## Goals / Non-Goals

**Goals:**

- 以 setup、resume、handoff 三個明確入口提供完整但可拆用的持久交班生命週期。
- 保留 CURRENT、session logs、decisions、known issues、復原、具體下一步與 read-back 驗證。
- 允許交班引用既有 artifacts，並以名稱與理由建議下一個 agent 使用的 skills。
- 將原本的全域硬規則縮成工具中立、事件驅動、風險分級的最小協定。
- 產出可供後續實作與人工驗收的融合評估基準。

**Non-Goals:**

- 不內建 TDD、除錯、spec、ticket、實作或 code review 工作流。
- 不偵測或安裝第三方 skills，也不保證建議的 skill 在下一個環境可用。
- 不建立 plugin、marketplace package、hook、daemon、資料庫或特定 agent 專用自動化。
- 不自動遷移既有 Passdown OS repository；第一版只提供可審查的映射與安全導入方式。

## Decisions

### 三段生命週期 Skills 與單一共享資產來源

`setup-passdown` 負責安全初始化，`resume-passdown` 負責讀取與復原，`handoff-passdown` 負責持久化與驗證。三者分開，讓使用者只安裝或呼叫需要的入口；由 setup skill 的 assets 保存唯一模板來源，resume 與 handoff 只定義操作契約，不再各自複製模板。

替代方案是建立單一大型 `passdown` skill，但其觸發條件會同時涵蓋初始化、接手與結束，容易誤觸且不利於單獨演進，因此不採用。

### 最小持久狀態與 handoff_id 復原

`handoff/CURRENT.md` 保存當前狀態，`sessions/` 保存有持久影響的歷史，`memory/decisions.md` 與 `memory/known-issues.md` 保存跨工作項目的長期知識。CURRENT 與 session log 共用不可重複的 `handoff_id`；resume 以 identifier 與 `updated_at` 判定一致性，不依賴檔名排序或 agent 私有記憶。

當最新完整 session log 比 CURRENT 新且內容足以重建時，resume 依該 log 修復 CURRENT 並 read-back；資料不完整、identifier 衝突或路徑不存在時，resume 回報 recovery-required blocker，不猜測狀態。

替代方案是只保存單一 handoff 文件，雖較簡單，但不能區分現在狀態與稽核歷史，也無法可靠處理中斷寫入，因此不採用。

### 事件驅動紀錄取代每輪強制 log

handoff 只有在程式、artifact、決策、blocker、下一步或專案方向發生持久變化時新增 session log。純問答且未改變持久狀態時，可不新增 log，但仍須回報「無持久狀態變更」且不得改寫 CURRENT。

固定 context 百分比與對話輪數改為非規範性提示；真正的規範性觸發點是切換 agent、切換工作項目、即將壓縮、使用者要求交班或產生持久狀態變更。

### Suggested skills 採名稱、理由與可用性狀態

CURRENT 與 session log 的 `Suggested skills` 條目包含 `name`、`reason` 與 `availability`。`availability` 僅允許 `available` 或 `unverified`：當前環境能列出該 skill 時標為 available，否則標為 unverified，不得宣稱已安裝。每筆建議都必須對應下一步或 blocker；沒有適合項目時使用空清單。

Artifact references 僅保存 project-root-relative path 或 URL，以及它對下一步的用途，不複製 spec、ADR、issue、commit 或第三方 skill 的全文。

### 工具中立與風險分級政策

agent 身分使用自由字串 `agent_id`，不硬編碼 codex、cc 或 agy。subagent、模型層級、fresh-context 驗證與 context 門檻是可選策略；只有破壞性變更、架構決策及安全敏感工作要求獨立第二意見。一般 Markdown 交班採同一 agent 的 read-back 即可。

此決策保留高風險工作的嚴謹度，又避免簡單工作支付固定的多 agent 協調成本。

### 安全初始化與 read-back 驗證

setup 只在目標不存在時建立 `passdown-os/`。若目標已存在，skill 必須列出衝突並停止覆寫；若必要檔案完整，則執行驗證並回報已初始化。所有寫入完成後都重新讀取必要檔案，檢查 front matter、必要欄位、placeholder、引用路徑與 handoff identifier。

替代方案是自動 merge 現有目錄，但 Markdown 語意合併無法保證不丟失使用者規則，第一版不承擔此風險。

## Implementation Contract

### Observable behavior

- 呼叫 `setup-passdown` 後，新專案根目錄出現一個可直接提交版控的 `passdown-os/`，包含 constitution、初始化 CURRENT、handoff template、session template、decisions 與 known issues。
- 呼叫 `resume-passdown` 後，使用者取得 Active work、Where left off、Next concrete step、Context anchors、Blockers 與 Suggested skills 的精簡摘要；一致性失敗時會得到具體 recovery-required 原因。
- 呼叫 `handoff-passdown` 後，有持久變更的工作會產生同一 `handoff_id` 的 CURRENT 與 session log，必要的 decision 或 known issue 會寫入長期記憶；無持久變更時不製造空 log。

### Interface and data shape

CURRENT 與 session template MUST 包含以下欄位：

- `handoff_id`: 由 ISO 8601 UTC 時間、agent_id 與 3 至 5 個小寫英文詞組成的唯一值。
- `updated_at`: ISO 8601 時間。
- `agent_id`: 寫入者的工具或模型識別字串；無法取得時使用 `unknown` 並明確標示。
- `active_work`
- `where_we_left_off`
- `next_concrete_step`
- `context_anchors`: 每筆含 path 或 URL 與用途。
- `blockers`
- `suggested_skills`: 每筆含 name、reason、availability。
- session log 另含 `work_performed`、`verification` 與 `unfinished_reason`。

`next_concrete_step` MUST 是單一、可執行且可驗收的動作；不得為 placeholder、空白或僅寫「繼續處理」。

### Failure modes

- 目標已有不相容的 `passdown-os/`：setup 列出衝突檔案並停止，不覆寫。
- 必要檔案、欄位或 anchor 缺失：resume 回報缺失項目並停止自動接手。
- 最新 log 與 CURRENT 不一致但無法確定較新真相：resume 設定 recovery-required blocker，不合成資訊。
- handoff 寫入任一步失敗：回報已寫與未寫項目；若 CURRENT 與 log 只有一方成功，下一次 resume 必須能偵測不一致。
- 建議的 skill 無法在當前環境驗證：保存為 `unverified`，不得阻擋交班。

### Acceptance criteria

- 在空白 fixture 執行 setup 流程後，所有必要檔案存在、無 placeholder，第二次執行不改寫檔案內容。
- 以一致的 CURRENT 與 session log 執行 resume 流程，摘要逐欄吻合來源內容。
- 建立一份比 CURRENT 新且內容完整的 session log 後，resume 能重建 CURRENT，且 read-back 後兩者 `handoff_id` 相同。
- 建立缺欄位或衝突 identifier 的 log 後，resume 回報 recovery-required 且不猜測修復。
- 執行有持久變更的 handoff 流程後，CURRENT、log、anchors 與 suggested skills 全部通過 read-back；執行無持久變更案例時 sessions 數量不增加。
- 融合評估文件逐項說明原 Passdown 規則的 keep、adapt 或 remove 決定，並記錄與 composable skills 的責任邊界。

### Scope boundaries

In scope：三個 SKILL.md、setup 共用模板、融合評估文件及其人工 fixture 驗收。

Out of scope：第三方 skill 安裝、外部 tracker 整合、hook、自動 context 量測、plugin 發布、既有專案自動 migration，以及 Passdown 以外的工程方法實作。

## Risks / Trade-offs

- [Markdown 無 schema runtime] → 在 skills 中定義必要欄位與 read-back checklist，並以 fixture 情境驗收。
- [事件驅動 log 可能漏記] → 明列六種持久變更與五種交班觸發點；模糊時以寫 log 為安全預設。
- [第三方 skill 名稱日後改變] → 保存 availability 狀態與理由，不保存第三方內部路徑或內容。
- [精簡規則降低原框架的強制性] → 高風險工作仍保留獨立驗證要求，評估文件記錄被降級規則與理由。
- [三個 skills 可能出現行為漂移] → setup assets 是資料格式唯一來源，resume 與 handoff 均引用同一欄位契約。

## Migration Plan

1. 先完成三個 skills、模板與評估文件，於空白 fixture 驗收。
2. 既有 Passdown 使用者依評估文件手動映射欄位；第一版不原地覆寫。
3. 若採用後需要 rollback，移除新 skills；已生成的 `passdown-os/` 為純 Markdown，可保留、手動刪除或回復 Git commit。

## Open Questions

第一版沒有阻擋實作的 open question。Marketplace、plugin 封裝與自動 migration 留待獨立 change 評估。
