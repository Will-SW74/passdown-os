# Passdown OS — Protocols（按需協定細節）

本檔是 [`CONSTITUTION.md`](CONSTITUTION.md) 的細節篇：**效力完全相同，只是不需要每次 session 都讀**。每章開頭標明「什麼時候讀」，被核心檔或情境指到時再讀對應章節即可，不要一次讀全檔。

| 章節 | 什麼時候讀 |
| --- | --- |
| 與 Spectra 的關係 | 專案使用（或決定不使用）Spectra 時；對 change/task 管理方式有疑問時 |
| Task 切分範例詳解 | 對「這個 task 算不算夠小」拿不準時 |
| 持續存檔機制 | 長期對話中為了防範意外遺失脈絡時 |
| 記憶索引與接力協定 | 要填寫或讀取 Context Index / Memory Anchor 欄位時 |
| 衝突處理 | 遇到 passdown-os 檔案的 git merge conflict 時 |
| Git Commit 與分支策略 | 開始一項工作前（判斷該不該開 branch）、或要合併分支時 |
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
- Session 開始協定的「`spectra list --parked`」步驟 → 跳過。
- Session 結束協定的「更新 `tasks.md` 勾選」步驟 → 用 `CURRENT.md` 或專案自己的 task 管理方式（`TODO.md`、issue tracker 等）替代。
- Session 結束協定的「`/spectra-commit`」步驟 → 用一般的 `git add` + `git commit` 替代。
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

## 持續存檔機制 (Continuous Logging) — 已停用
<!-- 2026-07-23 停用：checkpoint hook 的頻繁 edit 造成 context 膨脹，token 成本遠超防護價值 -->

> **已停用（2026-07-23）**：原設計為每 10 次工具呼叫由 PostToolUse hook 觸發 session log append。實測發現在長 session 中，checkpoint 的頻繁 edit 讓 context 持續膨脹（session 檔被改 12 次、CURRENT.md 被改 7 次，佔全部檔案操作 45%），token 成本遠超其防護價值。PostToolUse checkpoint hook 已從所有範本移除，紀律版亦不再要求。改回只依賴 Session 結束協定做一次性交接。
>
> 若意外斷線導致交接遺失，殘留的 `.active_lock` 會觸發下次開始協定的復原流程——這已足夠。

## 記憶索引與接力協定 (Memory Index & Resume Protocol)

如果一個 Task 較為複雜，不得不跨多個 Session/Agent 接力，或者對話中途因 Context 飽和需要開啟新 Session（重置 Context），為了保證 Resume 時不會因遺忘而「重複工作」、「認錯目標」或「產生幻覺」，必須遵循以下記憶接力協定：

### 1. 寫入：在結束 Session 前建立「記憶錨點」
在覆寫 `handoff/CURRENT.md` 和寫入 `sessions/` 時，必須在 **Context Index / Memory Anchor** 欄位標記精確的記憶索引：
- **直接記憶源 (Direct Memory Source)**：明確列出與此任務最直接相關的最近 1-2 次 `sessions/*.md` 檔案路徑與名稱。
- **程式碼錨點 (Code Symbol Anchor)**：利用 markdown link 語法指向當前正在修改、或下一個接手者必須立刻去讀的程式碼位置，必須精確到 **行號與符號**。例如：`[parseHeader](src/parser.js#L42-L55)`。**一律使用 repo 相對路徑**——絕對路徑（`file:///C:/...`）換一台機器或換使用者就斷，且會洩漏本機帳號路徑，違反本框架的去敏感化原則。行號會隨程式碼演進漂移，所以**必須同時給符號名**（function/class 名），行號只是加速定位的輔助。
- **臨時想法與 Scratchpad**：如果當前對話（Context）面臨被壓縮（如 `/compact`）或重新啟動，必須在當次 Session Log 中加入一個 `Scratchpad` 區段，用白話文記錄「目前腦袋裡正在想的、尚未寫成程式碼的邏輯細節與下一步猜想」。

### 2. 讀取：在開始 Session 時追蹤「記憶索引」
接手的 Agent 在讀完 `CURRENT.md` 後，**必須循著 `Context Index` 中列出的記憶源與程式碼錨點**：
- 第一時間用你環境裡的**檔案讀取工具**（各 agent 名稱不同，例如 cc 的 `Read`、agy 的 `view_file`，用對應的那個）直接開啟被指定的 1-2 個最近 session 紀錄以還原思路。
- 同樣用檔案讀取工具直接跳轉到指定的代碼錨點行號，閱讀當前最新的代碼狀態。
- **嚴禁**在未讀取指定的記憶錨點前，自行瞎猜或用全域搜尋工具無差別掃無關檔案。

## 衝突處理

**同機並行（最危險，優先預防）**：兩個 agent 同時在**同一個工作目錄**開工，是本框架防不了的情境——git 紀律只保護「不同 branch」，擋不住 live 共改。防線是開始協定第 1 步的會話鎖並行檢查：看到別人的鎖先問使用者，確認對方還在跑就停止等待（**勸告性防護**——同時啟動的極小競態窗口靠「寫後讀回＋寫檔前複查」緩解，詳見 `CONSTITUTION.md` 第 5 節的誠實聲明）。使用者側的紀律：**同一時間只讓一個 agent 動 repo，交接靠 CURRENT.md 換棒**——想「順便問另一個 agent」時，先讓現任跑完結束協定摘牌。

當兩個 agent 幾乎同時結束 session（例如在不同 branch 或不同機器上工作），可能會對同一個檔案產生 git merge conflict。處理原則：

- **`handoff/CURRENT.md`**：以時間戳較新的版本為準。合併時保留雙方的 Blockers 與 context 資訊，不要直接丟棄較舊的那份。
- **`sessions/*.md`**：檔名含時間戳與 agent 代號，理論上不會衝突。若真的同名（極不可能），在 slug 末尾加 `-2` 區分。
- **`memory/*.md`**（`decisions.md`、`known-issues.md` 等）：這些檔案是 append-only 設計，衝突時雙方的新增條目都保留，不要丟棄任何一方。

## Git Commit 與分支策略 (Git & Branching Strategy)

為了避免頻繁的交接與對話存檔產生大量零碎的 git commit，導致主分支 (main/master) 的 commit 歷史雜亂，必須遵守以下 Git 紀律：

1. **分支隔離**：判準是 **「有沒有一個可運作的基線要保護」＋「這次工作有沒有可能整個作廢」**，不是「任務瑣不瑣碎」（PDOS-D-20260721-3）。

   **可以直接在 main/master 上做**：
   - 專案**還沒有可運作的實作**時的基線建立——規格、設計、文件、框架設定、專案骨架。沒有 baseline 可破壞，錯了就往前修一個 commit（這正是文件工作的自然演進方式），branch 買不到任何東西。

   **必須開獨立 Feature Branch**（例如 `agent/<change-slug>` 或 `feature/<task-name>`）：
   - 已經有可運作的基線之後的**實作變更**——main 上有東西可以被弄壞了。
   - **結論可能是「此路不通」的探索**，典型如 spike／PoC／效能驗證。這類工作的價值在於「可能要整段丟掉」，正是 branch 存在的理由。
   - 需要他人 review 才能合併、或多線並行時。

   **判斷不了就問使用者一次**，不要靠「感覺這個算不算瑣碎」。

   > **為什麼改**：舊版寫「任何非瑣碎任務都必須開 branch」，但「非瑣碎」與「該不該隔離」是兩件事。一個 39 項任務的規格重寫非常不瑣碎，卻完全沒有 baseline 可保護、也不可能整份作廢；照舊規則要開 branch，實務上沒人這樣做，於是規則變成寫了沒人遵守——那比沒有規則更糟。
2. **頻繁 Local Commit**：在 Feature Branch 上，每次執行「Session 結束協定」時，Agent 應該將所有修改（包含專案代碼、`CURRENT.md`、新產生的 `sessions/*.md`）直接 commit。Commit message 格式建議為：`<agent>: <slug> - <summary>`（例如 `cc: fix-auth-bug - complete token parsing and save session log`）。
3. **Commit 前安全檢查（每次 commit 都要）**：
   - **本機記憶原始檔不入版控**：確認 staged files 中沒有 `*.raw`、`*.sqlite`、`*.db` 等原始記憶檔，以及**位置不對的** `*.jsonl`。`imports/` 由 `.gitignore` 擋住；`transcripts/` 是逐字稿的**唯一**合法存放區。這道檢查抓的是**漏到其他位置**的原始檔（例如誤把工具逐字稿複製到 `sessions/` 或專案根目錄）——那些一律不得入版控。
     - **例外：`transcripts/` 採「追蹤模式」的專案**（見 [`transcripts/README.md`](transcripts/README.md) 的兩種模式，PDOS-D-20260721-2）。此時 `transcripts/*.jsonl` **允許** staged，但每次新增前**必須**跑該檔記載的憑證樣式掃描，命中即停。其他位置的 `.jsonl` 仍然一律禁止。
   - **敏感資訊掃描**：確認 staged 的文字檔（尤其 `.md`）內容不含 API key、token、密碼、個人帳號。發現即移除，並在 [`memory/redaction-log.md`](memory/redaction-log.md) 記一筆移除了什麼。
4. **壓扁合併 (Squash & Merge)**：當任務完全結束，變更要併回 main/master 或 dev 分支時，必須採用 **Squash and Merge** 的方式合併。
   - **效果**：這會將 Feature Branch 上的數十個 AI 工作碎屑 commit 壓扁成一個乾淨的、人類可讀的高階 commit（例如 `feat: support JWT token authentication`）。
   - **記憶保留**：由於 `passdown-os/sessions/` 與 `passdown-os/memory/` 底下的所有 Markdown 文件都是以物理檔案形式存在，即使 Git commit 被 Squash，這些精確的歷史工作日誌與決策檔案**依然會被 100% 保留在 main 分支的最新檔案樹中**，完美的 Recall 機制不受影響，同時又維持了 Git 線圖的整潔。

## 本機記憶同步（強制，每次 session 結束都要檢查）

（回寫的每一條內容都必須依 `CONSTITUTION.md` 第 8 節簽名規則附上 agent 代號與時間戳。）

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
   - 把去敏感後、真正有價值的內容，摘要進正規位置（`sessions/`、`memory/decisions.md`、`memory/known-issues.md`），不要把原始檔案直接留在 `imports/` 裡當記憶來源——`imports/` 只是暫存清洗區。**升級（Promotion）原則**：不要複製貼上原始紀錄，必須「摘要與結構化」——舊的 raw text 要提煉成可執行的準則（actionable guidelines），符合本框架的閱讀習慣。

換句話說：**每次**都要做「檢查 + 輕量摘要回寫」（步驟 1-2）；只有在整批搬家/換工具的情境才需要走完整的匯入清洗流程（步驟 3）。

### 逐字稿歸檔（專案啟用 `transcripts/` 後，每次 session 結束都做）

若專案啟用了 `transcripts/` 歸檔區，執行本章記憶同步時順手歸檔當次逐字稿，讓「每次互動的完整記錄」留在專案裡。

**逐字稿是否入版控有兩種模式，由專案在導入時擇一**（預設排除模式；詳細判準、切換方式與安全要求見 [`transcripts/README.md`](transcripts/README.md)，PDOS-D-20260721-2）。**歸檔動作本身兩種模式都一樣**，差別只在事後 commit 時 `.jsonl` 進不進版控。

**判準是「本專案的自動歸檔 hook 是否真的生效」，不是「用哪個 agent」（框架決策 PDOS-D-20260721-1）**。安裝狀態是專案屬性不是 agent 屬性——同一個 agent 在 A 專案裝了 hook、在 B 專案沒裝。**先確認再決定走哪條路**：

1. **確認本次是否已自動歸檔**：看 `transcripts/` 有沒有出現對應本次 session 的檔案。（cc 亦可先查 `<target>/.claude/settings.json` 是否含 `SessionEnd` hook。）
2. **已自動歸檔** → 完成，不需手動。目前只有 cc 有自動路徑（`entrypoints/hooks/archive-transcript.sh`）。
3. **沒有自動歸檔**（hook 未安裝、被移除、或安裝了卻沒生效）→ **一律手動補**，不分 agent。從本機路徑複製當次逐字稿到 `transcripts/`，命名 `YYYY-MM-DD-HHmm-<agent>-<slug>.jsonl`（與本次 session log 同前綴）：
   - cc：`~/.claude/projects/<專案路徑 hash>/<session-id>.jsonl`
   - codex：`~/.codex/sessions/`
   - agy：`~/.gemini/antigravity-cli/brain/<conversation-id>/...`
   - 手動補做時在 session log 的 Transcript 欄註明「手動歸檔」與原因；若逐字稿是 session 結束前複製的，明確標示它**不含最後一段對話**。

- 定位提醒：逐字稿是最後一層考古材料，不是記憶正本——交接仍靠 `sessions/*.md` 提煉版；要把逐字稿內容升級進正式記憶，走 `imports/` 清洗流程。

## 維護規則

### sessions/ 歸檔

當 `sessions/`（不含 `archive/`）累積超過約 20 份檔案時，當次接手的 agent 應該：
1. 把重要內容摘要進 `memory/decisions.md`（若尚未記錄）。
2. 把舊檔案搬進 `sessions/archive/`。
3. 同步更新 `sessions/INDEX.md`：被搬走的檔案若有索引條目，把連結路徑補上 `archive/` 前綴，不要留下斷鏈。

這個概念呼應 Spectra 自己對 `openspec/changes/archive/` 的處理方式。

### memory/ 檔案分層與上限
<!-- cc review 修正：建立 memory 檔案的明確分層 (生效中 vs 歷史紀錄) 與歸檔機制，避免核心決策檔案無限制增長 -->

隨著時間推進，記憶檔案可能會無限增長，變成新一輪「要讀多少才夠」的問題。因此 `memory/decisions.md`、`known-issues.md`、`conventions.md` 等檔案必須採取分層與輪替策略：

1. **閾值觸發**：當任一檔案超過約 **30 條（或約 400 行）**時，當次接手的 agent 必須進行精簡與摘要。
2. **分層結構**：把主檔案明確分成兩層：
   - **生效中規則 (Active Rules)**：目前仍然適用且下一個接手者必須知道的決策或坑。永遠不會太長，過時的必須移除。
   - **決策歷史紀錄 (Historical Log)**：可以無限長，但需明確標示成「僅供追溯，session 開始不必讀」。
3. **歸檔舊紀錄**：若連「決策歷史紀錄」也太長，將最舊的一半內容摘要壓縮進 `memory/archive/<原檔名>-YYYYMMDD.md`，只在主檔留近期內容，並在原檔對應位置留一行指向 archive 檔。

### 檔案修改權限分層

- **agent 可自行修改**（日常工作本來就要寫的內容檔）：`handoff/`、`sessions/`、`memory/`（append 為主）、`imports/`。
- **動前先問使用者**（框架規則本體）：`CONSTITUTION.md`、`PROTOCOLS.md`、`GOLDEN_TEMPLATE.md`、`DISPATCH.md`、`RUBRICS.md`、`prompts/`、`entrypoints/`。經使用者同意修改後，同步在 `memory/decisions.md` 記一筆原因。唯一例外：`DISPATCH.md` 第 7 節的 agent 查證表是「內容」不是「規則」，agent 查證到新值後可自行更新（並在 session log 註明）。
