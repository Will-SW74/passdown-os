## Context

passdown-os 是一個純 Markdown 的跨 AI Agent 交接框架，本身沒有可執行程式碼——它的「行為」由規則檔（CONSTITUTION.md、PROTOCOLS.md 等）與 agent 對規則的遵循構成。2026-07-11 的架構 review（cc 執行）發現：前兩輪 review 修正補進來的機制多處沒有接回主幹，形成「寫了規則但永遠不會被執行」的死機制。本 change 的本質是讓每一條規則都能回答「誰、在哪一步、被什麼指到才會執行它」。

現狀約束：

- CONSTITUTION.md 的檔案地圖宣告「除 handoff/CURRENT.md 外，其他檔案都是被指到才讀」——因此任何不在檔案地圖、也沒被協定步驟指到的檔案，等同不存在。
- 框架的修改權限分層規定：規則檔本體（CONSTITUTION.md、PROTOCOLS.md、GOLDEN_TEMPLATE.md、entrypoints/ 等）動前需使用者同意。本 change 已由使用者於 2026-07-11 明確授權。
- 修改規則檔後，依框架自身規定需在 memory/decisions.md 留一筆原因。

## Goals / Non-Goals

**Goals:**

- 讓 .active_lock 會話鎖具備完整生命週期，成為交接完整性偵測的主要機制。
- 消除復原偵測的先天誤判：以語意檢查（最新 log 是否即 CURRENT.md 所指向者）取代分鐘級時間戳比對。
- 消除規則重複：每條規則只有一份正本；CHECKLIST_HANDOFF.md 與 memory/local-agent-sync.md 併回正本後移除。
- 讓 PROJECT_MANIFEST.md 與 sessions/INDEX.md 被接進檔案地圖與對應協定步驟，或不再存在——不允許孤兒檔案。
- 修正所有已知的編號 drift 與 GOLDEN_TEMPLATE.md 自檢清單矛盾。
- 記憶錨點範例改為 repo 相對路徑，確保跨機交接可用。
- 補上 PreCompact hook 範本，把「壓縮前先存檔」從紀律變成機制。

**Non-Goals:**

- 不改動框架的核心協定結構（Session 開始/結束協定的整體流程、Context 紅線數值、調度守則、rubrics 判準）——本 change 只修「機制接通」問題，不重新設計協定。
- 不實作 codex / agy 的等效 hook 機制（維持「未確認」標註，留待實測）。
- 不處理 DISPATCH.md 第 7 節查證表的待填值（那是內容不是規則）。
- 不引入任何非 Markdown 的工具依賴（框架零依賴原則不變）。

## Decisions

### 會話鎖採「存在即異常」語意，並排除進版控

lock 檔的唯一用途是偵測「上次 session 沒跑完結束協定」：開始協定檢查到 sessions/.active_lock 已存在 → 觸發復原流程；結束協定最後一步刪除 lock。lock 加入 .gitignore——替代方案是讓 lock 進版控以便跨機偵測，但這會讓兩台機器的正常並行工作互相誤報且產生 merge conflict，故捨棄。跨機的完整性偵測交給下一條決策的語意檢查。

### 復原偵測改為語意檢查而非時間戳比對

「sessions/ 最新一份 log 的檔名，是否等於 handoff/CURRENT.md 的 Direct Memory Source 第一項」——一致即交接完整。這消除了寫入順序造成的必然誤判，也天然免疫時區問題。時間戳比對降級為輔助訊號。同時明文定義：session log 檔名的時間戳一律為 session 開始時間。替代方案「調換結束協定第 2、3 步順序」只能緩解不能根治（分鐘粒度下同分鐘寫入仍不可判定），故捨棄。

### 重複清單併回正本，孤兒檔案接回主幹

CHECKLIST_HANDOFF.md 的交接檢查項與 CONSTITUTION.md 結束協定重複 → 其發布前檢查（squash、memory 輪替、manifest 更新）併入 PROTOCOLS.md 的 Git 策略與維護規則章節後，整檔移除。memory/local-agent-sync.md 與 PROTOCOLS.md 本機記憶同步章節重複 → 其「升級 (Promotion)」概念併入該章節後移除。PROJECT_MANIFEST.md 保留，接進檔案地圖（定位：接手第一眼的全局視角，GOLDEN_TEMPLATE 套用時必填）。sessions/INDEX.md 保留，接進結束協定（有長期價值的 session 才加一行）與 sessions/ 歸檔流程（歸檔時同步更新索引連結），並修正 GOLDEN_TEMPLATE 自檢清單的誤刪矛盾。

### 持續存檔機制的觸發規則上移 CONSTITUTION

強制且無條件觸發的規則必須放在每次必讀的檔案。CONSTITUTION.md 的 Context 存量章節加一句觸發摘要（每 10 次工具呼叫 checkpoint 一次），細節與理由留在 PROTOCOLS.md。

### 補 PreCompact hook 範本

entrypoints/hooks/settings.json.example 增加 PreCompact hook：在 compact（auto 或 manual）前注入提醒「先完成記憶同步再壓縮」。hooks/README.md 補充查證結論。這是目前 cc 唯一能機制化 Context 紅線體系的觸發點。

### 記憶錨點範例改 repo 相對路徑

handoff/_template.md、sessions/_template.md、PROTOCOLS.md 的 Code Symbol Anchor 範例從 file:///C:/... 絕對路徑改為 repo 相對路徑加行號（如 src/parser.js 第 42-55 行的 parseHeader），並註明「行號會漂移，必須同時給符號名」。

## Implementation Contract

本 change 為純規則文件修正，無 runtime/build 效果，但有「tooling 效果」（hook 設定檔），故仍列出合約：

- **行為**：套用後，(a) 任一 agent 依 Session 開始協定執行時，能以 lock 存在與否＋語意檢查判定上次交接是否完整；(b) /handoff 指令跑完後 sessions/.active_lock 不存在、sessions/INDEX.md 視情況多一行；(c) 安裝 PreCompact hook 的專案在 compact 前會看到存檔提醒。
- **介面／資料形狀**：sessions/.active_lock 內容為單行 session 開始時間（YYYY-MM-DD HH:mm，本機時間）＋agent 代號；session log 檔名時間戳定義為 session 開始時間；CURRENT.md 的 Direct Memory Source 第一項必須是最新一份 session log 的檔名。
- **失敗模式**：lock 殘留 → 開始協定進入復原流程（讀最新 log、修復 CURRENT.md、刪除殘留 lock 後繼續）；語意檢查不一致 → 同樣進入復原流程；兩者皆為明示處理，不允許靜默略過。
- **驗收方式**：(1) 全 repo 文字搜尋 active_lock，命中處必須涵蓋建立、檢查、刪除、gitignore 四種角色；(2) 搜尋 CHECKLIST_HANDOFF 與 local-agent-sync 應零命中（除 sessions/ 歷史紀錄與本 change 文件）；(3) CONSTITUTION.md 檔案地圖逐列核對 repo 根目錄實際檔案清單，無遺漏；(4) PROTOCOLS.md 中所有「第 N 步」引用與 CONSTITUTION.md 實際編號一致；(5) 全 repo 搜尋 file:/// 應零命中（除本 change 與歷史紀錄）；(6) GOLDEN_TEMPLATE.md 自檢清單照做一遍不會刪除任何被檔案地圖收錄的檔案。
- **範圍邊界**：in scope＝proposal Impact 列出的檔案；out of scope＝openspec/ 目錄、memory/ 內容條目（decisions.md 僅append 一筆本次決策紀錄）、prompts/ 與 claude-agents/ 範本。

## Risks / Trade-offs

- [lock 不進版控，跨機殘留偵測不到] → 語意檢查作為第二道防線，兩道機制互補覆蓋單機與跨機情境。
- [規則檔同時大改多處，接手 agent 短期內新舊記憶混雜] → 在 memory/decisions.md 記一筆彙總決策，並在本 change 的 session log 中列出全部改動點。
- [PreCompact hook 行為依 cc 版本而異] → hook README 標註查證日期與版本，沿用框架既有的「查證表」慣例。
- [移除 CHECKLIST_HANDOFF.md 對已習慣該檔的使用者是 breaking] → 併入後在 PROTOCOLS.md 對應章節保留同等內容，README 導引不再指向已移除檔案（原本也未指向，實際影響為零）。
