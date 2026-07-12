# INSTALL — 給 agent 的安裝指南

**本檔的讀者是 AI agent（cc / codex / agy 或任何工具）。** 當使用者要你「把 passdown-os 套用／安裝到某個專案」時，照本檔執行。原則：**全程你自己動手**——複製、重置、設定、驗收都是你的事，不要把任何一步丟回給使用者做；只有本檔明確標「問使用者」的地方才提問，而且各問一次就好。

（本檔管「怎麼執行安裝」；[`GOLDEN_TEMPLATE.md`](GOLDEN_TEMPLATE.md) 管「哪些檔案要重置、哪些規則不可動」——兩檔互補，執行中會指到它。）

## 0. 先確認兩件事

1. **來源（source）**：本框架所在位置。使用者通常會給本機路徑（例如某個 `_templates/passdown-os/`）或 git URL（先 clone 到暫存目錄再當來源）。沒給就問使用者。
2. **目標（target）**：使用者專案的根目錄。通常就是你目前的工作目錄；不確定就問一次。

## 1. 複製「框架本體」——注意，來源目錄裡不是每個東西都能搬

把以下清單從來源複製到 `<target>/passdown-os/`（目錄不存在就建立）：

- 根目錄文件：`CONSTITUTION.md`、`PROTOCOLS.md`、`DISPATCH.md`、`RUBRICS.md`、`GOLDEN_TEMPLATE.md`、`CHECKLIST_HANDOFF.md`、`PROJECT_MANIFEST.md`、`README.md`、`INSTALL.md`、`LICENSE`、`.gitignore`
- 資料夾：`prompts/`、`entrypoints/`、`handoff/`、`memory/`、`references/`
- `sessions/`：只搬 `_template.md`、`INDEX.md`、`archive/.gitkeep`
- `imports/`：只搬 `README.md`、`.gitkeep`

**絕對不要複製**（這些是範本庫「自己作為一個專案」累積的狀態，帶過去就污染新專案）：

- `.git/`、`openspec/`、`.spectra.yaml`（範本庫自己的版控與 Spectra 工作區）
- 來源根目錄的 `CLAUDE.md`、`AGENTS.md`、`GEMINI.md` 與 `.claude/`、`.agent/`、`.gemini/`、`.codex/`、`.opencode/`（範本庫自己的工具部署實體——新專案的入口檔要從 `entrypoints/` 範本重新生成，見第 3 步）
- `sessions/` 底下的實際 log 檔（`YYYY-MM-DD-*.md`）
- `sessions/.active_lock`、`sessions/.toolcount`（單機執行期暫存）

## 2. 重置狀態檔（你自己改，不是叫使用者改）

打開 [`GOLDEN_TEMPLATE.md`](GOLDEN_TEMPLATE.md)「必須重置為初始狀態的檔案」表，逐列執行。重點：

- `handoff/CURRENT.md` → 依 `handoff/_template.md` 重寫成「剛導入、尚無 active change」的初始狀態。
- `memory/` 各檔 → 清空條目、只留格式說明。
- `PROJECT_MANIFEST.md` → 填新專案的名稱、目標、版本、支援的 agent。**填不出來的欄位（專案目標、版本）問使用者一次**；能從專案現有檔案（package.json、README 等）推斷的自己推斷並註明來源。
- `sessions/INDEX.md` → 清空索引列表、只留表頭。
- `DISPATCH.md` 第 7 節查證表 → 清回 `<待填>` 或填當下實測值。

## 3. 安裝入口檔與 hooks

1. **確認要啟用哪些 agent**：使用者指明就照辦；沒指明→從專案現況推斷（有 `.claude/` 就有 cc、有 `AGENTS.md` 可能有 codex），推斷不了就問一次。
2. **入口檔**：依 [`entrypoints/README.md`](entrypoints/README.md) 的對應表，把對應範本的「## Passdown OS」段落合併進目標專案根目錄的入口檔（`CLAUDE.md`／`AGENTS.md` 等）——檔案已存在就 append 到末尾，不存在就建立。
3. **hooks（建議安裝）**：依 [`entrypoints/hooks/README.md`](entrypoints/hooks/README.md)：
   - cc：`settings.json.example` 的 hooks 區塊合併進 `<target>/.claude/settings.json`；`entrypoints/commands/handoff.md` 複製到 `<target>/.claude/commands/`；要自動調度就把 `entrypoints/claude-agents/` 複製到 `<target>/.claude/agents/`。
   - codex：`codex-hooks.json.example` → `<target>/.codex/hooks.json`，**提醒使用者首次執行需在 codex 內 trust**。
   - agy：`agy-hooks.json.example` → `<target>/.agents/hooks.json`，注入行為需實測（見該檔註記）。
4. **Spectra**：目標專案有 `openspec/` 就不用動；沒有就依 `PROTOCOLS.md`「不使用 Spectra 時的替代方案」——不需要為了本框架去裝 Spectra。

## 4. 寫檔紀律（安裝過程全程適用）

- 所有檔案一律 **UTF-8**（Windows 的 PowerShell `Out-File`/`Set-Content` 預設 UTF-16，必須 `-Encoding utf8`；用你環境的檔案寫入工具通常沒這問題）。
- 文件內的路徑一律 **repo 相對路徑**，不寫絕對路徑。

## 5. 驗收（不可自認完成）

1. 逐項跑 [`GOLDEN_TEMPLATE.md`](GOLDEN_TEMPLATE.md)「套用後自檢清單」，每一項核對實際檔案。
2. Read-back：重新讀取剛寫的 `CURRENT.md` 與 `PROJECT_MANIFEST.md`，確認沒有 `<佔位文字>` 殘留、沒有從範本庫帶過來的舊專案內容。
3. 向使用者回報一份清單：裝了什麼、放在哪、跳過了什麼與原因（例如「未啟用 codex，故未安裝 .codex/hooks.json」）、哪些項目需要使用者後續動作（例如 codex trust、agy 實測）。
