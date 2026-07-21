# passdown-os/ 作為黃金樣板

本專案的 `passdown-os/` 目錄被定位為**可重複使用的黃金樣板**：純 Markdown、無工具依賴，設計上就是為了整包複製到新專案使用。這份文件說明怎麼複製、複製之後哪些東西要重置、哪些不變。

> **你是 AI agent、且使用者要你執行安裝？** 直接照 [`INSTALL.md`](INSTALL.md) 做——那是給 agent 的可執行安裝程序（含複製排除清單與驗收步驟），執行中會回頭引用本檔的重置表與自檢清單。

## 怎麼套用到新專案

1. 把整個 `passdown-os/` 目錄複製到新專案的根目錄。
2. 依照下方「必須重置的檔案」清單，把裡面跟本專案（Passdown OS 原始專案）相關的具體內容清掉，換成新專案自己的狀態。
3. 依照「規則本身不變的部分」清單，確認 `CONSTITUTION.md` 的核心協定原封不動保留。
4. 在新專案設定各 agent 的入口檔：從 `entrypoints/` 複製對應範本到新專案的正確位置並改名（哪個 agent 對應哪個檔案、放哪裡，見 [`entrypoints/README.md`](entrypoints/README.md) 的對應表）。
5. 若新專案也使用 Spectra（`openspec/`），`passdown-os/` 可以直接疊加使用，不需要調整；若新專案不用 Spectra，把 `PROTOCOLS.md` 裡「與 Spectra 的關係」章節改寫成新專案實際採用的 spec/需求管理方式（或說明「本專案沒有額外的 spec 工具，passdown-os/ 是唯一的協作規則來源」）。
6. 若新專案是非 coding 專案，`CONSTITUTION.md` 的「Task 切分準則」章節已經涵蓋文件/決策研究/設計/流程規則四種情境，不需要另外調整；有更特殊的產出形式（例如影音、資料標註）時，依同樣邏輯（可驗證、獨立、單一關注點）自行補一段範例即可。

## 必須重置為初始狀態的檔案

這些檔案在本專案裡已經累積了 Passdown OS 原始專案 專屬的內容，複製到新專案時必須清空重寫，不能原封不動帶過去：

| 檔案 | 重置方式 |
| --- | --- |
| `PROJECT_MANIFEST.md` | 重填新專案的名稱、目標、版本、支援的 agent 與當前焦點（此檔是接手者第一眼看的專案 DNA） |
| `handoff/CURRENT.md` | 用 `handoff/_template.md` 的格式重寫，內容改成新專案「剛導入 passdown-os/、尚無 active change」的初始狀態 |
| `memory/decisions.md` | 清空所有條目，只保留檔案開頭的格式說明 |
| `memory/conventions.md` | 保留「框架預設文風」；只清空「專案自訂慣例」條目，等新專案累積自己的慣例再填 |
| `memory/known-issues.md` | 清空成範例格式 |
| `memory/glossary.md` | 換成新專案自己的縮寫/名詞表（例如新專案若用到不同的三個 agent 或不同代號，要重新定義） |
| `memory/redaction-log.md` | 清空成範例格式 |
| `sessions/*.md`（`_template.md` 與 `INDEX.md` 除外） | 全部移除或歸檔，新專案從零開始累積自己的 session 記錄 |
| `sessions/INDEX.md` | 清空索引列表，只保留表頭與說明 |
| `sessions/archive/` | 清空 |
| `imports/` | 清空成只有 `README.md` + `.gitkeep`（保持 gitignore 規則） |
| `transcripts/` | 清空成只有 `README.md` + `.gitkeep`（逐字稿屬原專案，絕不帶到新專案） |
| `references/` | 清空；只有在新專案自己也有類似的舊草稿要合併時才會用到這個資料夾 |
| `DISPATCH.md` 第 7 節的 agent 查證表 | 重填新環境的實測值（或清回 `<待填>`）——這張表是「內容」，其餘章節是「規則」不動 |

## 規則本身不變的部分

以下是框架的核心協定，複製到新專案時應該原封不動保留（除非新專案有明確理由要調整，且調整前應比照本框架自己的規則，在 `memory/decisions.md` 留一筆決策紀錄說明為什麼）：

- `CONSTITUTION.md` 的「角色」章節結構（三個平權 agent 的概念，只是代號可能不同）
- 「Task 切分準則」的三個判斷標準（可驗證、獨立、單一關注點）與 Context Window 預算限制與動態拆分原則
- 「Session 開始協定」與「Session 結束協定」的固定順序與強制性語氣
- 「本機記憶同步」章節的兩層設計（每次都要做的輕量檢查 vs. 換工具/換電腦才需要的整批匯入清洗）
- 「卡關 / 升級規則」「身分簽名規則」「衝突處理」「Git 與分支策略」「誠實條款」「維護規則」（含檔案修改權限分層）等章節的內容與精神（分佈於 `CONSTITUTION.md` 與 `PROTOCOLS.md`）
- `memory/conventions.md` 的「框架預設文風」（專案自訂慣例則照上表清空）
- `PROTOCOLS.md`（協定細節篇，「與 Spectra 的關係」章節依步驟 5 調整除外）、`DISPATCH.md`（調度守則，第 7 節查證表除外）、`RUBRICS.md`（判斷 rubrics）、`prompts/` 與 `entrypoints/claude-agents/` 底下全部範本、`README.md` 導引
- `handoff/_template.md`、`sessions/_template.md` 兩份模板的欄位結構
- `.gitignore` 裡的忽略規則：`imports/*`、`sessions/.active_lock`、`sessions/.toolcount`（換成新專案路徑時語法不變）
  - **`transcripts/*` 是例外，不屬於「不變」的部分**：它取決於專案選了哪種逐字稿模式（見 `transcripts/README.md`，PDOS-D-20260721-2）。模式 A（預設）保留該排除規則；模式 B 移除它，並在 repo 根加 `.gitattributes` 的 `*.jsonl -text`。
- `entrypoints/` 底下的範本（內容不變，只需複製到新專案對應位置並改名）

## 為什麼這樣分

「必須重置」的都是**內容**（這個專案實際做到哪、記了什麼決策），「不變」的都是**規則**（怎麼協作、怎麼切 task、怎麼交接）。這正是本框架在 `CONSTITUTION.md` 開頭就強調的原則：`passdown-os/` 記的是「怎麼做」，不是「做了什麼」的內容本身要跨專案通用；「做了什麼」永遠是單一專案的事，換專案就要歸零。

## 套用後自檢清單

複製 `passdown-os/` 到新專案後，用此清單確認一切就緒：

- [ ] `PROJECT_MANIFEST.md` 已重填新專案的定位、版本與支援 agent
- [ ] `handoff/CURRENT.md` 已改成新專案初始狀態（參考 `handoff/_template.md`）
- [ ] `memory/decisions.md` 已清空條目，只保留格式說明
- [ ] `memory/conventions.md` 已保留「框架預設文風」，並清空「專案自訂慣例」條目
- [ ] `memory/known-issues.md` 已清空條目，只保留格式說明
- [ ] `memory/glossary.md` 已換成新專案自己的名詞表
- [ ] `memory/redaction-log.md` 已清空條目，只保留格式說明
- [ ] `sessions/` 底下只剩 `_template.md`、清空的 `INDEX.md` 和空的 `archive/`（含 `.gitkeep`）
- [ ] `imports/` 只有 `README.md` + `.gitkeep`
- [ ] `references/` 已清空（或只保留新專案相關的舊草稿）
- [ ] `.gitignore` 已就位（確認 `imports/*` 被忽略）
- [ ] 各 agent 入口檔已設定（從 `entrypoints/` 複製對應範本到專案根目錄）
- [ ] `PROTOCOLS.md` 的「與 Spectra 的關係」章節已依實際狀況調整（用 Spectra → 不動；不用 → 參考「不使用 Spectra 時的替代方案」段落）
- [ ] `CONSTITUTION.md` 的「角色」章節的 agent 代號已依實際使用的工具調整
- [ ] `PROTOCOLS.md` / `DISPATCH.md` / `RUBRICS.md` / `prompts/` / `README.md` 原樣保留，僅 `DISPATCH.md` 第 7 節查證表已重填新環境的值（或清回 `<待填>`）
- [ ] 若使用 cc 且要啟用自動調度：`entrypoints/claude-agents/` 的五個 agent 檔已複製到新專案 `.claude/agents/`，且 `CLAUDE.md` 含「調度模式」段落（不啟用則跳過此項）
- [ ] 若使用 cc：`entrypoints/hooks/settings.json.example` 的 hooks 區塊已合併進新專案 `.claude/settings.json`，並開新 session 驗證注入成功（**必裝**，框架決策 PDOS-D-20260721-1；未裝時必須在 `CURRENT.md` 的 Open items 記一筆，且所有依賴 hook 的協定步驟改為手動）
- [ ] 若使用 cc：`entrypoints/commands/handoff.md` 已複製到新專案 `.claude/commands/`（收工打 `/handoff` 觸發結束協定；建議安裝）
- [ ] 若使用 codex：`entrypoints/hooks/codex-hooks.json.example` 已放到新專案 `.codex/hooks.json` 並在 codex 內信任（**必裝**；含 SessionStart 注入與檢查點計數器）
- [ ] 若使用 agy：`entrypoints/hooks/agy-hooks.json.example` 已放到新專案 `.agents/hooks.json` 並實測注入成功（**必裝**）
- [ ] `.gitignore` 含 `sessions/.active_lock` 與 `sessions/.toolcount`（會話鎖與計數器是本機暫存，不進版控）
