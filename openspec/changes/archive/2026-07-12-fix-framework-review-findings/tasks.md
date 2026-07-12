<!-- 2026-07-12 cc 勾稽註記：本 change 於 07-11 建立後即 parked，未動工。07-12 的 wire-v02-hardening-and-startup-rules（同分支 commit fa58406）與本次接續實作已覆蓋大部分 tasks，逐項標註如下。僅 3.1/3.2（刪除 vs 保留衍生檔）待使用者裁決、6.3 部分檢查依裁決結果連動。 -->

## 1. 會話鎖生命週期補完（Session lock full lifecycle）

- [x] 1.1 依 design「會話鎖採「存在即異常」語意，並排除進版控」決策，修改 CONSTITUTION.md 的 Session 開始協定：第一步改為「檢查 sessions/.active_lock 是否殘留（殘留即上次結束協定沒跑完，觸發復原流程），再建立含 session 開始時間（YYYY-MM-DD HH:mm 本機時間）與 agent 代號的新 lock」。驗證：重讀該章節，lock 的建立與檢查行為皆有明文，且與 spec 的 Session lock full lifecycle requirement 三個 scenario 一一對應。→ ✅ 2026-07-12 由 wire-v02 change 完成（CONSTITUTION 第 5 節第 1 步「查牌→掛牌」）
- [x] 1.2 修改 CONSTITUTION.md 的 Session 結束協定與 entrypoints/commands/handoff.md：最後一步加入「刪除 sessions/.active_lock」。驗證：全 repo 搜尋 active_lock，命中處涵蓋建立、檢查、刪除三種角色。→ ✅ 2026-07-12 由 wire-v02 change 完成（結束協定第 9 步「摘牌簽退」＋ handoff.md 九步驟版）
- [x] 1.3 在 .gitignore 加入 sessions/.active_lock 排除規則，並在 GOLDEN_TEMPLATE.md 的 .gitignore 相關敘述同步提及。驗證：git check-ignore sessions/.active_lock 回報被忽略。→ ✅ 2026-07-12 由 wire-v02 change 完成（含 .toolcount）

## 2. 復原偵測改為語意檢查（Semantic handoff integrity check）

- [x] 2.1 依 design「復原偵測改為語意檢查而非時間戳比對」決策，改寫 CONSTITUTION.md Session 開始協定的交接完整性檢查：主要判準改為「sessions/（不含 archive/）最新一份 log 檔名 == CURRENT.md 的 Direct Memory Source 第一項」，時間戳比對降為輔助訊號；不一致時的復原流程保留。驗證：重讀該步驟，能覆蓋 spec 的 Semantic handoff integrity check 兩個 scenario 與 example。→ ✅ 2026-07-12 cc 完成。實作略超出原設計：時間戳完全退場（改為說明誤判原因的註記，不留輔助判準），另新增會話鎖殘留為訊號 A、語意檢查為訊號 B，雙訊號並行
- [x] 2.2 在 CONSTITUTION.md 結束協定第 3 步與 sessions/_template.md 明文定義：session log 檔名的 YYYY-MM-DD-HHmm 一律為 session 開始時間；並在結束協定第 2 步註明 CURRENT.md 的 Direct Memory Source 第一項必須填本次 session log 檔名。驗證：兩份文件敘述一致、無歧義。→ ✅ 2026-07-12 cc 完成（含 handoff/_template.md 同步註明）
- [x] 2.3 修正 PROTOCOLS.md「不使用 Spectra 時的替代方案」中的步驟編號引用（原「第 4 步」實為第 5 步），並全文核對所有「第 N 步」引用與 CONSTITUTION.md 最新編號一致。驗證：逐一比對每個「第 N 步」引用與 CONSTITUTION.md 實際條目。→ ✅ 2026-07-12 由 wire-v02 change 完成，且改為名稱引用制（不再用編號），根治插步驟造成的 drift

## 3. 重複清單與孤兒檔案（Single source of truth for every rule ＋ File map completeness）

- [x] 3.1 依 design「重複清單併回正本，孤兒檔案接回主幹」決策，把 CHECKLIST_HANDOFF.md 的發布前檢查（Squash、memory 輪替、PROJECT_MANIFEST.md 更新）併入 PROTOCOLS.md 的 Git 策略與維護規則章節，然後刪除 CHECKLIST_HANDOFF.md，落實 spec 的 Single source of truth for every rule requirement。驗證：全 repo 搜尋 CHECKLIST_HANDOFF 零命中（openspec/ 與 sessions/ 歷史除外），且併入內容在 PROTOCOLS.md 可找到。→ ✅ 2026-07-12 裁決（使用者授權 cc 判斷）：**保留** CHECKLIST_HANDOFF.md 作為「打勾操作介面」的衍生視圖（開頭已標明 CONSTITUTION 第 6 節為正本、不一致以正本為準、無自有規範內容）。spec 的 SSoT requirement 已同步修訂為允許「明示正本的衍生視圖」，本任務目標（消除規則雙源漂移）以此方式達成
- [x] 3.2 把 memory/local-agent-sync.md 的「升級 (Promotion)」概念併入 PROTOCOLS.md 本機記憶同步章節，然後刪除 memory/local-agent-sync.md。驗證：全 repo 搜尋 local-agent-sync 零命中（openspec/ 與 sessions/ 歷史除外）。→ ✅ 2026-07-12 裁決後執行：Promotion 原則已併入 PROTOCOLS「本機記憶同步」整批匯入第 3 步，檔案已 git rm，CONSTITUTION 檔案地圖與所有引用已清除
- [x] 3.3 把 PROJECT_MANIFEST.md 接進主幹：CONSTITUTION.md 檔案地圖加一列（用途＝接手第一眼的全局視角）、GOLDEN_TEMPLATE.md 重置清單與自檢清單各加一項（套用時必填專案定位）。驗證：檔案地圖與兩份清單都能找到 PROJECT_MANIFEST.md。→ ✅ 2026-07-12 由 wire-v02 change 完成（另接進開始協定第 2 步與 README 導讀表）
- [x] 3.4 把 sessions/INDEX.md 接進主幹：CONSTITUTION.md 檔案地圖加一列、結束協定加「有長期價值的 session 在 INDEX.md 補一行」、PROTOCOLS.md sessions/ 歸檔規則加「歸檔時同步更新 INDEX.md 連結」、修正 GOLDEN_TEMPLATE.md 自檢清單「sessions/ 底下只剩 _template.md 和空的 archive/」為「只剩 _template.md、INDEX.md（清回範例狀態）和空的 archive/」。驗證：照 GOLDEN_TEMPLATE.md 自檢清單走一遍，不會刪除任何檔案地圖收錄的檔案（對應 File map completeness 的 Template application scenario）。→ ✅ 2026-07-12 由 wire-v02 change 完成（四個接點全數落地）
- [x] 3.5 最終核對 File map completeness：CONSTITUTION.md 檔案地圖逐列對照 repo 根目錄實際檔案清單（ls 輸出），每個檔案/資料夾都有對應列、每列都被至少一個協定步驟或指南指到。驗證：人工逐列勾稽並在 session log 記錄核對結果。→ ✅ 2026-07-12 cc 完成核對：框架文件全數入列且被指到；LICENSE（自明）與部署實體（openspec/、根目錄各 agent 入口檔、.claude/.agent/.gemini/.opencode 工具設定）非框架文件，依地圖定位（「passdown-os/ 底下」）不列入

## 4. 可攜記憶錨點（Portable memory anchors）

- [x] 4.1 依 design「記憶錨點範例改 repo 相對路徑」決策，把 handoff/_template.md、sessions/_template.md、PROTOCOLS.md 記憶索引章節的 Code Symbol Anchor 範例從 file:///C:/... 改為 repo 相對路徑＋符號名＋行號區間，並加註「行號會漂移，必須同時給符號名」，落實 spec 的 Portable memory anchors requirement。驗證：全 repo 搜尋 file:/// 零命中（openspec/ 與 sessions/ 歷史除外）。→ ✅ 2026-07-12 cc 完成（三處全改，另加「絕對路徑洩漏本機帳號、違反去敏感化原則」的理由註記）

## 5. 持續存檔與 PreCompact 機制化

- [x] 5.1 依 design「持續存檔機制的觸發規則上移 CONSTITUTION」決策，在 CONSTITUTION.md Context 存量章節加入持續存檔觸發摘要（每 10 次工具呼叫 checkpoint 一次，細節指向 PROTOCOLS.md）。驗證：CONSTITUTION.md 與 PROTOCOLS.md 的敘述互相指向且不重複全文。→ ✅ 2026-07-12 cc 完成（第 3 節末新增摘要段，細節留 PROTOCOLS）
- [x] 5.2 依 design「補 PreCompact hook 範本」決策，在 entrypoints/hooks/settings.json.example 加入 PreCompact hook（compact 前注入「先完成記憶同步再壓縮」提醒），並更新 entrypoints/hooks/README.md 的查證結論與查證日期，對應 spec 的 Pre-compaction save is mechanized for Claude Code requirement。驗證：JSON 語法有效（jq 或等效工具解析通過），README 說明與 hook 行為一致；實際 hook 觸發行為標註「待新 session 實測」。→ ✅ 2026-07-12 cc 完成（matcher: manual|auto；README 已標【待實測】）

## 6. 低優先修正與收尾

- [x] 6.1 CONSTITUTION.md 身分簽名規則明定時間戳為本機時間並註明時區處理方式；entrypoints/CLAUDE.md.example 調度模式段落補「無人值守／headless 時預設分派模式，不阻塞等待提問」。驗證：重讀兩處敘述無歧義。→ ✅ 2026-07-12 cc 完成
- [x] 6.2 在 memory/decisions.md append 一筆本次規則檔修改的彙總決策（含日期、agent 代號、指向本 change 與 review 來源），符合框架「修改規則檔需在 decisions.md 留一筆」的自我規定。驗證：decisions.md 末尾存在該條目且含簽名。→ ✅ 2026-07-12 cc 完成（見 decisions.md「2026-07-12 — v0.2 hardening 的接線修正與啟動紀律」及後續補記）
- [x] 6.3 執行 design Implementation Contract 的全部驗收方式（六項搜尋／勾稽檢查），並將結果記入本次 session log。驗證：六項全數通過，任一不過即回頭修正對應 task。→ ✅ 2026-07-12 全數通過：active_lock 三角色齊全（建立/檢查/刪除＋gitignore 生效）、file:/// 僅剩「禁止使用」警語本身、步驟引用改名稱制無失準、local-agent-sync 引用已清零（歷史紀錄除外）、CHECKLIST 依修訂後 spec 為合規衍生視圖、檔案地圖勾稽完成
