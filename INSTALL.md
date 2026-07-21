# INSTALL — 給 agent 的安裝指南

**本檔的讀者是 AI agent（cc / codex / agy 或任何工具）。** 當使用者要你「把 passdown-os 套用／安裝到某個專案」時，照本檔執行。原則：**全程你自己動手**——複製、重置、設定、驗收都是你的事，不要把任何一步丟回給使用者做；只有本檔明確標「問使用者」的地方才提問，而且各問一次就好。

（本檔管「怎麼執行安裝」；[`GOLDEN_TEMPLATE.md`](GOLDEN_TEMPLATE.md) 管「哪些檔案要重置、哪些規則不可動」——兩檔互補，執行中會指到它。）

## 0. 環境門檻與基本確認

### 0.1 環境門檻（硬性——過不了就中止部署，沒有第二條路）

在做任何複製動作**之前**，先逐一探測以下環境能力（D-20260713-1：使用者明文裁決，缺任一即中止，**不提供降級、不跳過、不自行找替代方案**）：

1. **Git**：執行 `git --version` 必須成功。
2. **Git Bash / POSIX sh**（hooks 腳本的執行環境）：先執行 `sh -c "echo ok"`。**失敗時不要立刻判定未安裝**——Windows 上 Git 常見的安裝狀態是「`git` 在 PATH、`sh.exe` 不在」。此時做第二層探測：從 `git` 的位置推導 Git 安裝根目錄（例如 `where git` 得到 `C:\Program Files\Git\cmd\git.exe` → 根目錄為 `C:\Program Files\Git`），檢查 `<Git根>\bin\sh.exe` 或 `<Git根>\usr\bin\sh.exe` 是否存在並能執行 `-c "echo ok"`：
   - **兩層都找不到** → Git Bash 真的沒裝，中止並請使用者安裝。
   - **第二層找到了** → 元件已安裝但 **不在 PATH**。**仍然中止**（codex／agy 的 hooks 直接呼叫裸的 `sh`，PATH 上找不到就會靜默失效），但診斷要準確：告訴使用者「Git Bash 已安裝，只需把 `<Git根>\bin` 加入 PATH」，**不要**叫人重裝已存在的東西。加完 PATH 後重跑本門檻。
     - **Windows 環境變數刷新注意**：Windows 的環境變數變更後，當前已經在執行中的 Agent 終端機/Session **不會自動重新載入新的環境變數**。Agent 可以手動在當前 PowerShell 中藉由 `$env:Path += ";C:\Program Files\Git\bin"`（依實際 Git 根目錄調整）暫時補上，或者必須請使用者重新啟動 Agent（重開對話/重開 IDE）以繼承新的 PATH 設定。
3. **Python**（agy 注入 hook 的依賴）：執行 `python --version` 必須成功。注意：Windows 上若只有 `py` 啟動器而沒有 `python` 指令，**視同不合格**——hooks 範本呼叫的是 `python`，請使用者安裝時勾選「Add python.exe to PATH」。

**任一項失敗 → 立刻中止部署**，向使用者回報：(a) 缺了哪幾項；(b) 安裝來源（Git 含 Git Bash：git-scm.com；Python：python.org，安裝時勾 Add to PATH）；(c) 明確說「裝好之後再叫我一次，我從頭執行本安裝」。**不要**在缺件狀態下部署任何部分——半套框架（有規則、沒 hooks）會讓機制化防線靜默失效，比不裝更危險。

### 0.2 確認來源與目標

1. **來源（source）**：本框架所在位置。使用者通常會給本機路徑（例如某個 `_templates/passdown-os/`）或 git URL（先 clone 到暫存目錄再當來源）。沒給就問使用者。
2. **目標（target）**：使用者專案的根目錄。通常就是你目前的工作目錄；不確定就問一次。

## 1. 複製「框架本體」——注意，來源目錄裡不是每個東西都能搬

把以下清單從來源複製到 `<target>/passdown-os/`（目錄不存在就建立）：

- 根目錄文件：`CONSTITUTION.md`、`PROTOCOLS.md`、`DISPATCH.md`、`RUBRICS.md`、`GOLDEN_TEMPLATE.md`、`CHECKLIST_HANDOFF.md`、`PROJECT_MANIFEST.md`、`README.md`、`INSTALL.md`、`LICENSE`、`.gitignore`
- 資料夾：`prompts/`、`entrypoints/`、`handoff/`、`memory/`、`references/`
- `sessions/`：只搬 `_template.md`、`INDEX.md`、`archive/.gitkeep`
- `imports/`：只搬 `README.md`、`.gitkeep`
- `transcripts/`：只搬 `README.md`、`.gitkeep`（實際逐字稿 `.jsonl` 絕不搬）

**絕對不要複製**（這些是範本庫「自己作為一個專案」累積的狀態，帶過去就污染新專案）：

- `.git/`、`openspec/`、`.spectra.yaml`（範本庫自己的版控與 Spectra 工作區）
- 來源根目錄的 `CLAUDE.md`、`AGENTS.md`、`GEMINI.md` 與 `.claude/`、`.agent/`、`.gemini/`、`.codex/`、`.opencode/`（範本庫自己的工具部署實體——新專案的入口檔要從 `entrypoints/` 範本重新生成，見第 3 步）
- `sessions/` 底下的實際 log 檔（`YYYY-MM-DD-*.md`）
- `sessions/.active_lock`、`sessions/.toolcount`（單機執行期暫存）

**Windows 唯讀檔案與 `.git` 清理注意事項**：
在複製過程中，若需要原地清理來源或刪除 `.git/` 目錄，Windows 下的 PowerShell `Remove-Item -Recurse -Force` 常因 pack 檔案具有唯讀屬性而報錯。建議採用以下做法之一解決：
1. 採用「開新資料夾，只複製白名單檔案」的白名單做法，避免原地刪除 `.git`。
2. 在 PowerShell 中先移除該目錄下所有檔案的唯讀屬性，再執行刪除：
   `Get-ChildItem -Path <path> -Recurse -Force | ForEach-Object { $_.Attributes = 'Normal' }; Remove-Item -Path <path> -Recurse -Force`
3. 使用 `cmd /c rmdir /s /q <path>` 強制刪除。

## 2. 重置狀態檔（你自己改，不是叫使用者改）

打開 [`GOLDEN_TEMPLATE.md`](GOLDEN_TEMPLATE.md)「必須重置為初始狀態的檔案」表，逐列執行。重點：

- `handoff/CURRENT.md` → 依 `handoff/_template.md` 重寫成「剛導入、尚無 active change」的初始狀態。
- `memory/` 各檔 → 依 GOLDEN_TEMPLATE 逐項重置；其中 `memory/conventions.md` 保留「框架預設文風」，只清空「專案自訂慣例」。
- `PROJECT_MANIFEST.md` → 填新專案的名稱、目標、版本、支援的 agent。**填不出來的欄位（專案目標、版本）問使用者一次**；能從專案現有檔案（package.json、README 等）推斷的自己推斷並註明來源。
- `sessions/INDEX.md` → 清空索引列表、只留表頭。
- `DISPATCH.md` 第 7 節查證表 → 清回 `<待填>` 或填當下實測值。

## 3. 安裝入口檔與 hooks

1. **確認要啟用哪些 agent**：使用者指明就照辦；沒指明→從專案現況推斷（有 `.claude/` 就有 cc、有 `AGENTS.md` 可能有 codex），推斷不了就問一次。
2. **入口檔**：依 [`entrypoints/README.md`](entrypoints/README.md) 的對應表，把對應範本的「## Passdown OS」段落合併進目標專案根目錄的入口檔（`CLAUDE.md`／`AGENTS.md` 等）——檔案已存在就 append 到末尾，不存在就建立。
3. **hooks（必裝，不是選配）**：依 [`entrypoints/hooks/README.md`](entrypoints/hooks/README.md)，為**每一個啟用的 agent** 安裝：
   - cc：`settings.json.example` 的 hooks 區塊合併進 `<target>/.claude/settings.json`；`entrypoints/commands/handoff.md` 複製到 `<target>/.claude/commands/`；要自動調度就把 `entrypoints/claude-agents/` 複製到 `<target>/.claude/agents/`。
   - codex：`codex-hooks.json.example` → `<target>/.codex/hooks.json`，**提醒使用者首次執行需在 codex 內 trust**。
   - agy：`agy-hooks.json.example` → `<target>/.agents/hooks.json`，注入行為需實測（見該檔註記）。

   **為什麼是必裝（框架決策 PDOS-D-20260721-1）**：第 0.1 節已經因為 hooks 的執行環境（Git Bash、Python）缺件就**中止整個安裝**，並明文寫著「半套框架（有規則、沒 hooks）會讓機制化防線靜默失效，比不裝更危險」。既然缺了 hooks 的前置條件就不准裝，hooks 本身自然不可能是選配——過去寫成「建議安裝」與第 0.1 節自相矛盾，實際造成過「規則裝了、hooks 沒裝」的半套狀態，且該狀態下依賴 hook 的協定步驟會靜默不執行。

   **安裝後必須驗收**（不可只寫檔就宣稱完成）：
   - 設定檔能被解析（cc：`.claude/settings.json` 是合法 JSON，且原有設定未被覆蓋）。
   - 冒煙測試 `sh entrypoints/hooks/checkpoint-counter.sh --json` 正常結束。
   - 明確告訴使用者：**SessionStart 與 SessionEnd 需在下一個 session 才能驗證**，並給出驗收方法（開場問 agent「你 context 裡有沒有 SessionStart hook 注入的交接內容？」，能引用 `CURRENT.md` 即成功）。
   - 若使用者明確拒裝 hooks，**必須**在 `handoff/CURRENT.md` 的 Open items 記一筆「hooks 未安裝，依賴 hook 的協定步驟需全部手動執行」，讓後續 agent 看得到——不可默默略過。
4. **Spectra**：目標專案有 `openspec/` 就不用動；沒有就依 `PROTOCOLS.md`「不使用 Spectra 時的替代方案」——不需要為了本框架去裝 Spectra。

## 4. 寫檔紀律（安裝過程全程適用）

- 所有檔案一律 **UTF-8**（Windows 的 PowerShell `Out-File`/`Set-Content` 預設 UTF-16，必須 `-Encoding utf8`；用你環境的檔案寫入工具通常沒這問題）。
- 文件內的路徑一律 **repo 相對路徑**，不寫絕對路徑。

## 5. 驗收（不可自認完成）

1. 逐項跑 [`GOLDEN_TEMPLATE.md`](GOLDEN_TEMPLATE.md)「套用後自檢清單」，每一項核對實際檔案。
2. Read-back：重新讀取剛寫的 `CURRENT.md` 與 `PROJECT_MANIFEST.md`，確認沒有 `<佔位文字>` 殘留、沒有從範本庫帶過來的舊專案內容。
3. 向使用者回報一份清單：裝了什麼、放在哪、跳過了什麼與原因（例如「未啟用 codex，故未安裝 .codex/hooks.json」）、哪些項目需要使用者後續動作（例如 codex trust、agy 實測）。
