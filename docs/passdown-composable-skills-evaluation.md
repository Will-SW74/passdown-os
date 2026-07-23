# Passdown 與 Composable Skills 融合評估

## 結論

Passdown OS 不應被外部工程方法 skills 取代，也不應吞進它們的實作。兩者適合用鬆耦合方式組合：

- Passdown 負責跨 session、跨 agent、跨工具仍可讀取的持久接力狀態。
- 工程方法 skills 負責 TDD、除錯、規格、實作、審查等單次工作的執行方法。
- `suggested_skills` 只記錄下一步可能需要的能力，不安裝、不派發、不複製第三方指令。

本版以三個獨立 skill 呈現生命週期：`setup-passdown` 建立狀態目錄、`resume-passdown` 驗證與恢復、`handoff-passdown` 持久化交班。它們可單獨使用，也可串成 setup → handoff → resume。

## 責任分層

| 層次 | 負責內容 | 不負責內容 |
| --- | --- | --- |
| Passdown continuity | CURRENT、session logs、決策、已知問題、下一個具體步驟、復原與 read-back | TDD、除錯、code review、spec 撰寫或程式實作 |
| Engineering-method skills | 執行一個明確方法，例如先寫失敗測試、系統化除錯或安全審查 | 成為跨工具的唯一專案記憶或改寫 Passdown schema |
| Optional project systems | Spectra、issue tracker、ADR、commit、CI 等既有 artifact | Passdown 的必要 runtime 依賴 |

外部集合如 [mattpocock/skills](https://github.com/mattpocock/skills) 可作為工程方法能力來源；Passdown 只保存名稱、具體理由與可用性，並以 URL 或專案相對路徑引用相關 artifact。此 repository 不 vendor、fork、重發或內嵌第三方 skill 內容。

## Keep / Adapt / Remove

| 項目 | 決定 | 理由與落點 |
| --- | --- | --- |
| CURRENT | Keep | 保留唯一目前狀態入口；必須含可執行且可驗證的下一步。 |
| Session logs | Adapt | 保留 append-only 歷史，但改為 durable state 有變化時才寫，不因每輪對話強制產生空 log。 |
| Decisions / known issues memory | Keep | 只追加會影響後續工作的決策、可重現問題與已驗證 workaround。 |
| Recovery | Keep | 依 front matter 的 `updated_at` 與 `handoff_id` 決定；只能由單一較新且完整的 log 重建 CURRENT。 |
| Context thresholds | Remove as requirement | context 百分比與對話輪數只作提示，不是跨工具可攜的硬門檻。 |
| Fixed agent names | Remove | `agent_id` 是自由字串；沒有身份資訊時才使用 `unknown`。 |
| Dispatch / mandatory subagents | Remove | Passdown 不啟動 agent、不要求 subagent，也不假設某個 vendor 的 routing API。 |
| Self-verification | Adapt | 每次寫入都必須 read-back；只有破壞性、安全敏感或架構決策要求獨立第二意見。 |
| Composable routing | Add | 以 grounded suggestions 連接下一步與可選 skill；缺少或改名不阻擋狀態讀取。 |

## 九個融合面向

### 1. CURRENT

`handoff/CURRENT.md` 是唯一目前狀態入口，保存 active work、停留點、下一步、anchors、blockers 與 suggested skills。它不取代規格或 issue，只引用它們。setup 必須把範例改成實際狀態並移除 `template_example`。

### 2. Logs

每個 durable handoff 建立一個 session log，並與 CURRENT 共用同一 `handoff_id`。handoff 先寫 log、再寫 CURRENT，使中斷後仍有可恢復來源。只有說明性對話而沒有 durable change 時，不新增 log。

### 3. Memory

`memory/decisions.md` 與 `memory/known-issues.md` 是低頻、長期資訊。只有新決策、被否決且會再次影響工作的替代方案、可重現問題或已驗證 workaround 才追加；一般工作摘要留在 session log。

### 4. Recovery

resume 先讀 constitution 與 CURRENT，再檢查 session logs。若單一較新 log 完整且時間可解析，便以該 log 作唯一來源重建 CURRENT；若 identifier 衝突、欄位不足、anchor 無效或來源不唯一，回報 `recovery-required`，不得猜測合併。

### 5. Context thresholds

固定 context 百分比、對話輪數與 token 門檻無法跨 agent 工具可靠取得，因此降為 advisory signal。真正觸發 handoff 的條件是 durable state 改變、切換 agent 或 work item、準備壓縮 context，或使用者明確要求交班。

### 6. Agent names

`agent_id` 接受自由字串，例如 `codex`、`claude-code`、`antigravity` 或團隊自訂名稱。schema 不維護 vendor allowlist，也不把模型等級或 subagent 身份當成恢復前提。

### 7. Dispatch

Passdown 提供 routing 資訊，不執行 dispatch。接收端可以使用建議的 skill、另一個能滿足相同理由的 skill，或不用 skill 繼續工作。任何選擇都不需要改動 durable schema。

### 8. Self-verification

setup、handoff 與 recovery 的每次寫入都要重新讀取並檢查檔案、欄位、identifier、placeholder 與本機 anchors。一般 Markdown 狀態更新可自行驗證；高風險工作才升級為獨立第二意見。

### 9. Composable skill routing

每筆 suggestion 只含：

- `name`：能力名稱。
- `reason`：與具體下一步或 named blocker 的關係。
- `availability`：只能是 `available` 或 `unverified`。

每筆 context anchor 只含 `ref` 與 `purpose`。`ref` 是 project-root-relative path 或 HTTP(S) URL；`purpose` 說明它為何影響下一步。交班不複製 spec、plan、ADR、issue、commit、diff 或第三方 skill 全文。

## 典型組合

1. `setup-passdown` 在尚未初始化的專案建立純 Markdown 狀態。
2. agent 執行工程方法 skill，例如依規格寫失敗測試。
3. `handoff-passdown` 保存測試結果、blocker、下一步，並將相關規格記成 anchor。
4. 若下一步適合某個已知 skill，記錄 grounded suggestion；無法確認安裝時標為 `unverified`。
5. 下一個 agent 執行 `resume-passdown`。即使建議 skill 不存在，也能讀取完整狀態，並自行選擇相容方法。

## 排除範圍

本版不處理 marketplace 發布、原生 plugin 封裝、hook、daemon、外部 tracker 同步、舊版資料 migration、skill 自動安裝或第三方指令鏡像。這些能力若日後需要，應另立 change，且不能改變純 Markdown 狀態可獨立存取的性質。
