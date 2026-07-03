# Passdown OS — Protocols（按需協定細節）

本檔是 [`CONSTITUTION.md`](CONSTITUTION.md) 的細節篇：**效力完全相同，只是不需要每次 session 都讀**。每章開頭標明「什麼時候讀」，被核心檔或情境指到時再讀對應章節即可，不要一次讀全檔。

| 章節 | 什麼時候讀 |
| --- | --- |
| 與 Spectra 的關係 | 專案使用（或決定不使用）Spectra 時；對 change/task 管理方式有疑問時 |
| Task 切分範例詳解 | 對「這個 task 算不算夠小」拿不準時 |
| 記憶索引與接力協定 | 要填寫或讀取 Context Index / Memory Anchor 欄位時 |
| 衝突處理 | 遇到 passdown-os 檔案的 git merge conflict 時 |
| Git Commit 與分支策略 | 開始一個非瑣碎任務前、或要合併分支時 |
| 本機記憶同步 | 執行 Session 結束協定第 6 步、或要整批匯入本機記憶時 |
| 維護規則 | sessions/ 或 memory/ 檔案累積變多時；想修改框架規則檔時 |

## 與 Spectra 的關係

本框架**疊加**在 Spectra（`openspec/`）之上，不取代它：

- **WHAT**（做什麼、驗收條件）— 交給 Spectra 的 spec / proposal / design / tasks 管理。
- **WHO / WHEN**（誰、什麼時候接手、接手時怎麼快速還原狀態）— 由本框架（`passdown-os/`）管理。

任務切分沿用 Spectra 既有紀律，不重複發明：
- 單一 task（`tasks.md` 中的一項）原本預估 > 1 小時則拆分。但在 AI 協作中，更核心的限制是 **Context Window 預算**（見 `CONSTITUTION.md` 的 Task 切分與 Context 預算準則）。
- 單一 change 的待辦項目 > 15 個 → 考慮拆成多個 change。
- 大範圍或有風險的變更，先用 `/spectra-propose` 產生 proposal/design/tasks，再用 `/spectra-apply` 實作。

本框架另新增一條 Spectra 沒有的規則：`CONSTITUTION.md` 的「Context 存量與防禦性壓縮規則」章節。

### 不使用 Spectra 時的替代方案

若本專案不使用 Spectra（沒有 `openspec/` 目錄），以下規則自動替代：
- 「Active change」→ 直接在 `handoff/CURRENT.md` 的「Active change」欄位用自由文字描述目前正在做的事，不需要指向 `openspec/changes/`。
- Session 開始協定第 4 步（`spectra list --parked`）→ 跳過。
- Session 結束協定第 1 步（更新 `tasks.md` 勾選）→ 用 `CURRENT.md` 或專案自己的 task 管理方式（`TODO.md`、issue tracker 等）替代。
- Session 結束協定第 8 步（`/spectra-commit`）→ 用一般的 `git add` + `git commit` 替代。
- Task 切分準則照常適用，task 清單記在 `handoff/CURRENT.md` 的 `Where we left off` 段落、或專案自己的 `TODO.md` / issue tracker 裡。

## Task 切分範例詳解

（四項判斷標準本體見 `CONSTITUTION.md`；本章是「拿不準時」的對照範例。）

**Coding 專案**：不是「每個 function 做成一個 module」——那是架構顆粒度，不是 task 顆粒度。task 的單位是「一個行為改變 + 它的驗證方式」，可能小於一個 function（例如「幫 `parseHeader` 加上空字串的邊界處理，並補一個對應測試」），也可能大於一個 function（例如「新增一個 endpoint，含 handler + 驗證 + 一個整合測試」）。判斷依據是「這個改動能不能被單獨驗證、單獨 review、單獨 commit」，不是程式碼結構長怎樣。

**非 coding 專案**：把「function」換成「一個可獨立審閱的產出物」：
- **寫文件類**：task =「寫完某一節，內容涵蓋指定範圍，且沒有佔位字樣」，不是「把整份文件寫完」。
- **決策 / 研究類**：task =「針對某個問題，比較至少兩個方案並做出結論，寫成一筆決策記錄」。
- **設計類**：task =「產出一版可以拿去給人看的草稿/原型，聚焦單一畫面或單一流程」。
- **流程 / 規則類**：task =「定義一條規則 + 一個可以判斷是否遵守的檢查方式」。

核心邏輯都一樣：把「這個 task 做完了嗎？」變成一個任何人（或另一個 agent）都能不靠記憶、直接檢查出答案的問題。

## 記憶索引與接力協定 (Memory Index & Resume Protocol)

如果一個 Task 較為複雜，不得不跨多個 Session/Agent 接力，或者對話中途因 Context 飽和需要開啟新 Session（重置 Context），為了保證 Resume 時不會因遺忘而「重複工作」、「認錯目標」或「產生幻覺」，必須遵循以下記憶接力協定：

### 1. 寫入：在結束 Session 前建立「記憶錨點」
在覆寫 `handoff/CURRENT.md` 和寫入 `sessions/` 時，必須在 **Context Index / Memory Anchor** 欄位標記精確的記憶索引：
- **直接記憶源 (Direct Memory Source)**：明確列出與此任務最直接相關的最近 1-2 次 `sessions/*.md` 檔案路徑與名稱。
- **程式碼錨點 (Code Symbol Anchor)**：利用 markdown link 語法指向當前正在修改、或下一個接手者必須立刻去讀的程式碼位置，必須精確到 **行號與符號**。例如：`[parseHeader](file:///C:/project/parser.js#L42-L55)`。
- **臨時想法與 Scratchpad**：如果當前對話（Context）面臨被壓縮（如 `/compact`）或重新啟動，必須在當次 Session Log 中加入一個 `Scratchpad` 區段，用白話文記錄「目前腦袋裡正在想的、尚未寫成程式碼的邏輯細節與下一步猜想」。

### 2. 讀取：在開始 Session 時追蹤「記憶索引」
接手的 Agent 在讀完 `CURRENT.md` 後，**必須循著 `Context Index` 中列出的記憶源與程式碼錨點**：
- 第一時間用你環境裡的**檔案讀取工具**（各 agent 名稱不同，例如 cc 的 `Read`、agy 的 `view_file`，用對應的那個）直接開啟被指定的 1-2 個最近 session 紀錄以還原思路。
- 同樣用檔案讀取工具直接跳轉到指定的代碼錨點行號，閱讀當前最新的代碼狀態。
- **嚴禁**在未讀取指定的記憶錨點前，自行瞎猜或用全域搜尋工具無差別掃無關檔案。

## 衝突處理

當兩個 agent 幾乎同時結束 session（例如在不同 branch 或不同機器上工作），可能會對同一個檔案產生 git merge conflict。處理原則：

- **`handoff/CURRENT.md`**：以時間戳較新的版本為準。合併時保留雙方的 Blockers 與 context 資訊，不要直接丟棄較舊的那份。
- **`sessions/*.md`**：檔名含時間戳與 agent 代號，理論上不會衝突。若真的同名（極不可能），在 slug 末尾加 `-2` 區分。
- **`memory/*.md`**（`decisions.md`、`known-issues.md` 等）：這些檔案是 append-only 設計，衝突時雙方的新增條目都保留，不要丟棄任何一方。

## Git Commit 與分支策略 (Git & Branching Strategy)

為了避免頻繁的交接與對話存檔產生大量零碎的 git commit，導致主分支 (main/master) 的 commit 歷史雜亂，必須遵守以下 Git 紀律：

1. **分支隔離**：AI Agent 執行任何非瑣碎任務時，**必須在獨立的 Feature Branch 上工作**（例如 `agent/<change-slug>` 或 `feature/<task-name>`），禁止直接在 main/master 分支進行頻繁交接。
2. **頻繁 Local Commit**：在 Feature Branch 上，每次執行「Session 結束協定」時，Agent 應該將所有修改（包含專案代碼、`CURRENT.md`、新產生的 `sessions/*.md`）直接 commit。Commit message 格式建議為：`<agent>: <slug> - <summary>`（例如 `cc: fix-auth-bug - complete token parsing and save session log`）。
3. **壓扁合併 (Squash & Merge)**：當任務完全結束，變更要併回 main/master 或 dev 分支時，必須採用 **Squash and Merge** 的方式合併。
   - **效果**：這會將 Feature Branch 上的數十個 AI 工作碎屑 commit 壓扁成一個乾淨的、人類可讀的高階 commit（例如 `feat: support JWT token authentication`）。
   - **記憶保留**：由於 `passdown-os/sessions/` 與 `passdown-os/memory/` 底下的所有 Markdown 文件都是以物理檔案形式存在，即使 Git commit 被 Squash，這些精確的歷史工作日誌與決策檔案**依然會被 100% 保留在 main 分支的最新檔案樹中**，完美的 Recall 機制不受影響，同時又維持了 Git 線圖的整潔。

## 本機記憶同步（強制，每次 session 結束都要檢查）

**原則：任何工具的本機私有記憶都只是暫存或輔助，`passdown-os/` 才是三個 agent 共用的權威記錄。** 這條規則對 codex / cc / agy 三者**同等適用**，不是只針對某一個工具：凡是任何一個 agent 在自己的 home 目錄底下（不論是整理過的「記憶」功能，還是原始的「session 逐字稿」）留下了跟本專案相關、會影響後續判斷的內容，都必須在 session 結束前寫回 `passdown-os/`，否則就等於這件事只有那個工具自己知道、其他兩個 agent 交接時完全看不到——這正是本框架要避免的事。

各 agent 已知的本機私有記憶來源（**同時涵蓋「記憶」與「session 逐字稿」兩種，各 agent 都要回寫自己這份**）：
- **cc（Claude Code）**：`~/.claude/projects/<hash>/memory/*.md`（整理過的 auto memory）與 `~/.claude/projects/<hash>/*.jsonl`（原始 session 逐字稿）
- **codex（OpenAI Codex CLI）**：`~/.codex/sessions/`（本機 session 記錄）
- **agy（Google Antigravity）**：`~/.gemini/antigravity-cli/brain/<conversation-id>/.system_generated/logs/`（`transcript.jsonl` 為精簡版、`transcript_full.jsonl` 為完整版）。注意 AGY 的記錄是以 conversation 為單位，每次對話有獨立的 `conversation-id`。AGY 目前沒有像 cc 那樣的整理過的 auto memory 功能——需要保留的內容必須在 session 結束時手動摘要回寫進 `passdown-os/`。

新工具加入時，比照上述格式在這裡補一列，不要假設「沒列出來就不用回寫」。

流程：

1. **檢查**：session 結束前，回想這次是否對自己工具的本機記憶系統寫入了新內容（例如 Claude Code 依自身指示存了 user/feedback/project 類型 memory）。
2. **摘要回寫**：把其中跟本專案相關、值得讓另外兩個 agent 也知道的內容，用一般文字（不是原始格式）寫進 `passdown-os/`——多數情況直接寫進本次的 `sessions/*.md` log 即可；若是持久性決策則寫進 `memory/decisions.md`；若是專案慣例則寫進 `memory/conventions.md` / decisions.md。
3. **大量/整批匯入**（換電腦、換工具、或某個工具的本機記憶即將遺失時才需要）：
   - 把原始資料複製進 `passdown-os/imports/`（此資料夾內容預設不進版控，見 `.gitignore`）。
   - 檢查並移除敏感資訊：API key、token、cookie、密碼、個人帳號、絕對路徑、與專案無關的私人對話。移除了什麼，記一筆到 [`memory/redaction-log.md`](memory/redaction-log.md)。
   - 把去敏感後、真正有價值的內容，摘要進正規位置（`sessions/`、`memory/decisions.md`、`memory/known-issues.md`），不要把原始檔案直接留在 `imports/` 裡當記憶來源——`imports/` 只是暫存清洗區。

換句話說：**每次**都要做「檢查 + 輕量摘要回寫」（步驟 1-2）；只有在整批搬家/換工具的情境才需要走完整的匯入清洗流程（步驟 3）。

## 維護規則

### sessions/ 歸檔

當 `sessions/`（不含 `archive/`）累積超過約 20 份檔案時，當次接手的 agent 應該：
1. 把重要內容摘要進 `memory/decisions.md`（若尚未記錄）。
2. 把舊檔案搬進 `sessions/archive/`。

這個概念呼應 Spectra 自己對 `openspec/changes/archive/` 的處理方式。

### memory/ 檔案上限

`memory/decisions.md`、`known-issues.md`、`conventions.md` 任一檔超過約 **30 條（或約 400 行）**時，當次接手的 agent 應該精簡：
1. 合併明顯重複的條目；把已被取代、不再有參考價值的舊條目搬進 `memory/archive/<原檔名>-YYYYMMDD.md`（資料夾不存在就建立）。
2. `decisions.md` 是只增不改設計——搬移時**整條原樣搬走**，不改寫內容，並在原檔對應位置留一行指向 archive 檔。

### 檔案修改權限分層

- **agent 可自行修改**（日常工作本來就要寫的內容檔）：`handoff/`、`sessions/`、`memory/`（append 為主）、`imports/`。
- **動前先問使用者**（框架規則本體）：`CONSTITUTION.md`、`PROTOCOLS.md`、`GOLDEN_TEMPLATE.md`、`DISPATCH.md`、`RUBRICS.md`、`prompts/`、`entrypoints/`。經使用者同意修改後，同步在 `memory/decisions.md` 記一筆原因。唯一例外：`DISPATCH.md` 第 7 節的 agent 查證表是「內容」不是「規則」，agent 查證到新值後可自行更新（並在 session log 註明）。
