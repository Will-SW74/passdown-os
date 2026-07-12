# Decisions

只增不改的決策紀錄（ADR-lite）。每筆條目標題格式：`## D-YYYYMMDD-N — <決策標題>`（N＝當日流水號，從 1 起算）——這個 **決策 ID** 是全框架的精準引用鍵：程式碼註解、session log 的 `Decisions made` 欄位、CURRENT.md 都用它指回本檔特定條目（例如註解寫 `// D-20260712-2：時間戳比對必然誤判，故用語意檢查`）。若某個決策後來被推翻，用新條目記錄並註明「取代 D-YYYYMMDD-N」，不要刪除或改寫舊條目。

## D-20260712-6 — 逐字稿歸檔區（gitignored）與決策 ID 連結約定

**Decision:** (1) 新增 `transcripts/` 逐字稿本機歸檔區：gitignored 不入版控（與 commit 安全檢查的 `*.jsonl` 禁令相容），可攜靠雲端/USB 同步資料夾；cc 由 SessionEnd hook（`archive-transcript.sh`，利用 hook stdin 的 `transcript_path`）全自動歸檔，codex/agy 於結束協定手動複製；命名與 sessions/ log 同時間前綴，按時間排序即為對應索引。(2) 決策條目改用 `D-YYYYMMDD-N` 編號，程式碼註解、session log、CURRENT.md 以 ID 精準引用——完成「code 註解 → 決策 → session log →（考古時）逐字稿」的完整還原鏈，前三層 100% 在 repo 內。

**Why:** 使用者要求「每次互動都留下記錄且跟著專案走」＋「註解可回查是哪個記憶讓它這樣做」。逐字稿原本只在工具本機（會被清理、跨機帶不走、與 log 對不上號）；決策引用原本靠日期＋標題人工對應，不夠精準。

**Alternatives considered:**
- 逐字稿清洗後入版控 — 否決：與 `*.jsonl` 禁令衝突、每次收尾多一道清洗工序、repo 體積失控。
- 逐字稿維持只在工具本機（僅靠路徑造冊） — 否決：可追溯但脆弱，不符「跟著資料夾走」的需求。

**Agent:** cc（2026-07-12 21:40）

## D-20260712-5 — 對照舊 AI_MEMORY 規格：補天條與 commit 安全檢查

**Decision:** 使用者以舊專案的 AI_MEMORY/AGENT_MEMORY 規格逐條對照本框架，確認絕大部分已實作且多數更機制化（SSoT 可攜、里程碑主動同步、壓縮前同步、pull 式按需讀取、session 索引等）。補上兩個真實缺口：(1) **天條**——session log 必記所有失敗嘗試與死路（不論最終成敗），CONSTITUTION 第 6 節第 3 步＋sessions/_template.md 新增 Failed attempts 欄位；(2) **Commit 前安全檢查**——PROTOCOLS Git 章新增第 3 條：staged 不得含 `*.raw`/`*.jsonl`/`*.sqlite`/`*.db` 原始記憶檔、不得含 API key/token/密碼（發現即移除並記 redaction-log）。另確認一項**刻意的設計差異**：舊版要求「repo＋工具內部記憶雙寫」，本框架刻意採單向回寫（私有→repo，內部記憶為暫存不維護），目的相同、更簡單，不視為缺口。

**Why:** 舊規格的兩條是實戰教訓（失敗路徑被重跑、原始逐字稿與密鑰誤入版控），且不與現有規則重複——現有失敗軌跡要求只覆蓋「卡關」與「升級」情境，一般成功繞過的死路沒人記。

**Alternatives considered:**
- .gitignore 加全域 `*.jsonl`/`*.db` pattern — 否決：會誤傷一般專案的合法資料檔，規則層檢查即可。

**Agent:** cc（2026-07-12 21:00）

## D-20260712-4 — 新增 INSTALL.md：agent 自主安裝程序

**Decision:** 新增 `INSTALL.md`，明確以 AI agent 為讀者的安裝程序：使用者只需給來源路徑＋一句話，agent 全程自己執行複製（含「範本庫自身狀態」的汙染排除清單：.git/、openspec/、根目錄入口檔實體、工具設定目錄、實際 session log）、重置、入口檔與 hooks 安裝、驗收回報。`GOLDEN_TEMPLATE.md` 重新定位為「重置表＋不可動規則」的對照資料，由 INSTALL.md 引用，兩檔互補不重複。

**Why:** 原本的 GOLDEN_TEMPLATE.md 是寫給人的（「把目錄複製到新專案」主詞是使用者），agent 讀了不知道來源在哪、哪些檔案不能搬、重置該自己做——不符合「丟給 agent 一句話就裝好」的使用預期。且範本庫根目錄如今同時是一個活專案（有 openspec/、工具部署實體），沒有排除清單的話 agent 會把範本庫的狀態複製進新專案。

**Alternatives considered:**
- 直接改寫 GOLDEN_TEMPLATE.md 成 agent 視角 — 否決：重置表與「規則不可動」清單對人工安裝仍有價值，拆成「程序（INSTALL）＋資料（GOLDEN_TEMPLATE）」符合本框架衍生視圖原則且各自單一職責。

**Agent:** cc（2026-07-12 20:30）

## D-20260712-3 — 衍生檔裁決：留 CHECKLIST、刪 local-agent-sync（混合方案）

**Decision:** 使用者授權 cc 裁決衍生檔去留，採混合方案：(1) **保留** `CHECKLIST_HANDOFF.md`——它是結束協定的「打勾操作介面」，有正本（CONSTITUTION 第 6 節）沒有的獨立用途；已標明正本、無自有規範內容。(2) **刪除** `memory/local-agent-sync.md`——純為 PROTOCOLS「本機記憶同步」章的簡略複述，唯一獨有概念（Promotion 提煉原則）已併回 PROTOCOLS 整批匯入第 3 步。同時修訂 `handoff-integrity` spec 的 SSoT requirement：允許「明示正本、遇不一致以正本為準、不含自有規範」的衍生視圖。另刪除 `review-fixes` 分支指標（其內容為目前分支直系祖先，零損失）。`fix-framework-review-findings` change 以 17/17 完成 archive。

**Why:** 「單一來源」的目的是消除規則漂移，不是消滅所有第二份檔案——衍生視圖只要（a）明示正本（b）遇衝突讓位（c）不新增規則，就不產生漂移風險；而純複述檔案沒有這三性以外的價值，直接刪除最乾淨。

**Alternatives considered:**
- 兩檔都刪（07-11 change 原案）— 否決：CHECKLIST 的打勾介面在結束協定執行時有實際操作價值。
- 兩檔都留 — 否決：local-agent-sync 無獨立價值，留著就是第二份要維護的複本。

**Agent:** cc（2026-07-12 20:00）

## D-20260712-2 — 消化 07-11 parked change：語意檢查取代時間戳、可攜錨點、PreCompact

**Decision:** 取回（unpark）2026-07-11 的 `fix-framework-review-findings` change 並逐項勾稽：13/17 已由當日實作覆蓋，另落實其四項獨有發現——(1) 復原偵測主判準改為「sessions/ 最新 log 檔名 == CURRENT.md Direct Memory Source 第一項」的語意檢查，時間戳比對完全退場（結束協定「先寫 CURRENT 後寫 log」的固定順序使時間戳比對必然誤判）；log 檔名時間戳明定為 session 開始時間。(2) 記憶錨點範例全面改 repo 相對路徑（`file:///C:/...` 跨機必斷且洩漏本機帳號）。(3) 持續存檔觸發摘要上移 CONSTITUTION 第 3 節（無條件義務不能只放在被指到才讀的檔案）；補 cc 的 PreCompact hook 範本（待實測標註）。(4) 簽名時間戳明定本機時間＋UTC 偏移註記；CLAUDE.md.example 補 headless 預設分派模式。**懸而未決**：3.1/3.2（刪除 CHECKLIST_HANDOFF / local-agent-sync 併回正本 vs 保留為標明正本的衍生檔）與 07-12 已實作方案衝突，留待使用者裁決。

**Why:** parked change 存於 `.git/spectra-app/`（不進版控且不可見），若不取回消化，其獨有發現會永久遺失——這正是本框架要防止的「記憶只存在單一位置」問題的活案例。

**Alternatives considered:**
- 直接 archive 舊 change（視為被新工作取代）— 否決：四項獨有發現有真實價值，且時間戳誤判是正確性問題不是風格問題。

**Agent:** cc（2026-07-12 19:40）

## D-20260712-1 — v0.2 hardening 的接線修正與啟動紀律

**Decision:** (1) 把 gpt review 新增的四個檔案（`PROJECT_MANIFEST.md`、`CHECKLIST_HANDOFF.md`、`sessions/INDEX.md`、`memory/local-agent-sync.md`）正式接進 `CONSTITUTION.md` 檔案地圖與開始/結束協定的讀取路由——此前它們是沒有任何檔案指向的孤兒，在「被指到才讀」的框架裡等於不存在。(2) `.active_lock` 會話鎖改為完整閉環：開始時「查牌→掛牌」、結束協定最後一步「摘牌簽退」，鎖殘留即為異常中斷訊號；鎖與 `.toolcount` 進 `.gitignore`。(3) 持續存檔計數器誠實分為兩層：hook 機制化（cc/codex/agy 三者 2026-07 查證均支援 hooks，新增 codex/agy hooks 範本與 `checkpoint-counter.sh`）與紀律啟發式備援。(4) 新增啟動紀律：正體中文 zh-TW、UTF-8 編碼（CONSTITUTION 第 11 節）、程式碼註解由「特殊邏輯才必須」升級為「一律必須」（第 10 節）。(5) 60% 存檔線觸發後改為「先提醒使用者、優先重開新 session」，不可自行壓縮。(6) 衍生檔（CHECKLIST、local-agent-sync）標明正本出處，防止規則雙源漂移；PROTOCOLS 對協定步驟的引用由編號改為名稱，防止再次因插入步驟而失準。

**Why:** cc review 指出 Gemini 落地的 v0.2 hardening「補了正確的內容，但沒接上框架的神經系統」；使用者另指示五項啟動紀律（zh-TW、UTF-8、註解必加、本機記憶回寫附時間戳、壓縮前提醒使用者）。

**Alternatives considered:**
- 移除 `.active_lock`（承認擋不住自覺問題）— 否決：改成閉環後它有真實的偵測價值（殘留＝異常中斷），且成本極低。
- 把計數器包裝成強制機制 — 否決：模型自數不可靠，違反誠實條款；改為 hook 機制化 + 紀律備援雙層。

**Agent:** cc（2026-07-12）

## 範例格式（可刪除，供參考）

## D-YYYYMMDD-N — <決策標題>

**Decision:** <決策內容>

**Why:** <為什麼這樣決定>

**Alternatives considered:**
- <考慮過但否決的方案> — <否決原因>

**Agent:** <codex|cc|agy>
