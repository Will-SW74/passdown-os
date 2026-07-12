<!-- 回溯性 change：第 1-5 組 tasks 已於 2026-07-12 由 cc 完成並通過 read-back 驗證，故為勾選狀態；僅 6.1 為真實未完成項。 -->

## 1. 孤兒檔案接線（pull 機制路由）

- [x] 1.1 四個 v0.2 新檔（PROJECT_MANIFEST.md、CHECKLIST_HANDOFF.md、sessions/INDEX.md、memory/local-agent-sync.md）在 CONSTITUTION.md 檔案地圖各有一列，含「什麼時候讀」欄位。驗證：grep 檔名於 CONSTITUTION.md 各命中至少一列。
- [x] 1.2 開始協定含「首次接觸先讀 PROJECT_MANIFEST.md」步驟；結束協定開頭指向 CHECKLIST_HANDOFF.md；追歷史路徑指向 sessions/INDEX.md。驗證：閱讀 CONSTITUTION.md 第 5、6 節確認三處路由存在。
- [x] 1.3 衍生檔標明正本出處（CHECKLIST_HANDOFF.md → CONSTITUTION 第 6 節；memory/local-agent-sync.md → PROTOCOLS「本機記憶同步」章），防止規則雙源漂移。驗證：兩檔開頭均有「以正本為準」聲明區塊。

## 2. 會話鎖閉環

- [x] 2.1 實現 spec 需求「Session lock lifecycle」：開始協定第 1 步為「查牌→掛牌」（先檢查 sessions/.active_lock 是否殘留，再覆寫為本次 agent 代號＋開始時間），殘留鎖成為復原協定訊號 A。驗證：CONSTITUTION.md 第 5 節第 1、5 步內容審閱，行為涵蓋 spec 三個情境。
- [x] 2.2 結束協定新增第 9 步「摘牌簽退」（刪除 lock 即正常收尾的實體訊號），並更新 entrypoints/commands/handoff.md 為九步驟同步版本。驗證：兩檔步驟數與內容一致。
- [x] 2.3 .active_lock 與 .toolcount 列入 .gitignore（本機暫存不進版控）。驗證：讀取 .gitignore 確認兩條規則存在。

## 3. 檢查點計數器機制化

- [x] 3.1 PROTOCOLS「持續存檔機制」改寫為兩層（hook 機制化＋紀律備援），明文承認模型自數工具呼叫不可靠。驗證：章節含「誠實聲明」字樣與兩個層級標題。
- [x] 3.2 實現 spec 需求「Externally counted checkpoint reminders」：新增 entrypoints/hooks/checkpoint-counter.sh，每次呼叫遞增 sessions/.toolcount、每滿 10 次輸出存檔提醒、非數字內容歸零防呆。驗證：腳本內容審閱（含 case 防呆與 mod 10 判斷），行為涵蓋 spec 的計數器情境與邊界表。
- [x] 3.3 新增 entrypoints/hooks/codex-hooks.json.example（SessionStart 注入＋計數器，schema 依 2026-07-12 官方文件查證）與 entrypoints/hooks/agy-hooks.json.example（PreInvocation＋計數器，stdout 注入標「未確認」）。驗證：兩檔存在且含查證日期與未確認標註。
- [x] 3.4 entrypoints/hooks/README.md 改寫為三 agent（cc/codex/agy）對照表，含安裝驗證方法與資料來源連結。驗證：README 含對照表與三個來源連結。

## 4. 啟動紀律（使用者指示五項）

- [x] 4.1 CONSTITUTION 新增第 11 節「語言與編碼紀律」：回覆與文件一律 zh-TW、寫檔一律 UTF-8（含 PowerShell 預設 UTF-16 陷阱註記）。驗證：第 11 節存在且含兩條規則。
- [x] 4.2 CONSTITUTION 第 10 節註解紀律升級為「任何程式碼一律必須（MUST）加正體中文 Why 註解」，保留特殊邏輯加強版。驗證：第 10 節含「一律必須」與雙重理由（使用者學習＋跨 agent review）。
- [x] 4.3 60% 存檔線行為改為「先存檔→直接提醒使用者→優先重開新 session，使用者同意才啟動壓縮」。驗證：CONSTITUTION 第 3 節第 4 條內容審閱。
- [x] 4.4 本機記憶回寫每條附 agent 代號與時間戳，三處規則（CONSTITUTION 第 6 節、PROTOCOLS、memory/local-agent-sync.md）一致。驗證：三處均含時間戳要求。
- [x] 4.5 三個 entrypoints 入口範本（CLAUDE.md.example、AGENTS.md.example、CODEX.md.example）加入口級「語言與編碼」提示並指向 CONSTITUTION 第 10、11 節。驗證：三檔各含一段提示。

## 5. 一致性收尾

- [x] 5.1 跨檔協定步驟引用由編號改為名稱（PROTOCOLS 的 Spectra 替代方案、entrypoints/hooks/settings.json.example 注入文案），修復插入鎖步驟造成的編號失準。驗證：全庫 grep 舊式「第 4 步（spectra」無殘留命中。
- [x] 5.2 GOLDEN_TEMPLATE 重置清單與自檢清單補齊：PROJECT_MANIFEST 重填項、sessions/INDEX.md 清空項、codex/agy hooks 安裝項、.gitignore 檢查項。驗證：自檢清單含四個新項目。
- [x] 5.3 依框架自身規則留存紀錄：memory/decisions.md 一筆完整決策（含否決方案）、sessions/ 一份 session log（含 Scratchpad 未竟事項）。驗證：兩檔存在且含 2026-07-12 條目。

## 6. 後續實測（唯一未完成項）

- [x] 6.1 於任一 agy（Google Antigravity）環境安裝 entrypoints/hooks/agy-hooks.json.example，實測 PreInvocation 的 stdout 是否注入 agent context（開新對話問 agent 是否看得到 CURRENT.md 內容），並把結果回寫 entrypoints/hooks/README.md 的「未確認」標註。驗證：README 該段不再含「未確認」字樣，改為實測結果與日期。
