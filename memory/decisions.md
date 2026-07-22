# Decisions

只增不改的決策紀錄（ADR-lite）。每筆條目標題格式：`## D-YYYYMMDD-N — <決策標題>`（N＝當日流水號，從 1 起算）——這個 **決策 ID** 是全框架的精準引用鍵：程式碼註解、session log 的 `Decisions made` 欄位、CURRENT.md 都用它指回本檔特定條目（例如註解寫 `// D-20260712-2：時間戳比對必然誤判，故用語意檢查`）。若某個決策後來被推翻，用新條目記錄並註明「取代 D-YYYYMMDD-N」，不要刪除或改寫舊條目。

> **兩個命名空間，不要混淆（PDOS-D-20260721-1）**：安裝到新專案時本檔會被**清空**（見 `GOLDEN_TEMPLATE.md` 重置表），專案從 `D-YYYYMMDD-N` 重新編號。因此**框架自身的決策**改用 `PDOS-` 前綴（`PDOS-D-YYYYMMDD-N`），被複製到各專案的框架文件（`CONSTITUTION.md`、`PROTOCOLS.md`、`INSTALL.md` 等）引用框架決策時一律帶前綴，指向**本框架母庫**的本檔，而非專案自己的 `memory/decisions.md`。
>
> 未加前綴的歷史條目（`D-20260712-*`、`D-20260713-*`）維護原 ID 不改寫（本檔只增不改），但同樣屬於框架命名空間；框架文件內若引用到它們，讀者請到母庫查閱。**專案自己的決策一律不加前綴。**

## PDOS-D-20260722-2 — Review 報告統一輸出至 review_result/

**Decision:** 三個 Agent (codex / cc / agy) 在專案進行任何 Tasks、Specs 或 Code Review 產出的報告檔案，一律統一存放於專案根目錄的 `review_result/` 資料夾中（檔名包含日期與主題，如 `YYYY-MM-DD-code-review.md`），方便集中查閱與歷史存檔。

**Why:** 防止各 Agent 自由存放報告於不同子目錄（如 `openspec/changes/...`），導致報告散落、難以跨 session 與跨工具集中檢閱。

**Agent:** agy（2026-07-22 12:35）

## PDOS-D-20260721-3 — 分支判準改為「有無基線可保護／是否可能作廢」；結束協定的 commit 改為無條件

**Decision:** (1) `PROTOCOLS.md` 分支隔離的判準從「任務瑣不瑣碎」改為 **「有沒有可運作的基線要保護」＋「這次工作有沒有可能整個作廢」**：尚無實作程式碼時的基線建立（規格／設計／文件／骨架）可直接在 main；已有基線後的實作變更、以及結論可能是「此路不通」的探索（spike／PoC）必須開 branch。(2) `CONSTITUTION.md` 結束協定第 8 步從「**視情況**執行 commit」改為**一律 commit**，並明訂 **push 由使用者決定，agent 不得在未經指示下 push**。(3) 開始協定第 1 步加一項：採逐字稿模式 B 的專案，開場檢查並提交上個 session 遺留的孤兒 `.jsonl`。

**Why:** (1) 「非瑣碎」與「該不該隔離」是兩件不同的事。實例：一次 39 項任務的規格重寫極不瑣碎，但當時專案連一行實作程式碼都沒有——沒有 baseline 可弄壞，也不可能整份作廢，開 branch 買不到任何東西。舊規則要求開 branch，實務上整個 session 九次 commit 全部直接進 main，於是規則變成「寫了沒人遵守」，比沒有規則更糟。(2) 「視情況」把判斷權交給 agent，而 agent 偶爾會判錯；未 commit 的交接內容在換機器時等於不存在，而誤判的代價（多一個 no-op commit）遠小於漏 commit。(3) SessionEnd hook 在 agent 最後一次回應之後才觸發，commit 只能發生在 agent 還能行動時——**任何 session 都無法提交自己的結尾**，這是固定點不是疏失，只能由下一個 session 收尾。

**Alternatives considered:**
- 分支規則維持原樣，要求 agent 嚴格遵守 — 否決：規則本身的判準就錯了，強制遵守只會讓文件工作付出無謂成本。
- 讓 SessionEnd hook 自己 `add + commit + push` 以封死孤兒逐字稿 — 否決：換來「無人監督下自動 push」的風險面，而缺的那段只是收工對話，考古價值最低；且憑證掃描要寫進腳本、push 失敗時狀態不明。開始協定加一項檢查成本低得多。

**Agent:** cc（2026-07-21 22:15）

## PDOS-D-20260721-2 — 逐字稿改為「排除／追蹤」雙模式，導入時擇一

**Decision:** `transcripts/` 不再只有「gitignored」一條路，改為兩種模式：**A 排除（預設，維持原行為）**與 **B 追蹤（`.jsonl` 入版控）**。選擇判準、設定步驟（移除 `.gitignore` 排除規則、加 `.gitattributes` 的 `*.jsonl -text`、憑證掃描指令）、體積與不可逆風險，全部寫進 `transcripts/README.md`。`INSTALL.md` 第 3 節新增一步：安裝時**問使用者一次**（repo 是否私有、跨機靠 git 還是資料夾同步），不得自行預設。`PROTOCOLS.md`「Commit 前安全檢查」的 `*.jsonl` 全面禁令補上模式 B 的例外——否則規則與新模式直接矛盾。

**Why:** 原設計把「不入版控」寫死，理由是 (a) 含未清洗敏感資訊、(b) 可攜靠資料夾同步整個專案。(b) 是一個**未被檢驗的假設**：實際案例（gt_auto_tester，2026-07-21）的跨機工作流是 `git pull`，資料夾同步完全不在流程內，於是逐字稿實質上永遠不會離開原機器——使用者換到另一台機器就無法回查「哪個環節出包」，而這正是逐字稿存在的唯一理由。對一個**私有、單人、靠 git 跨機**的 repo，把開發全程納入版控是 git 的正當用途，(a) 的威脅模型（repo 可能被外人看到）並不成立。與其讓每個這類專案各自寫例外，不如讓框架正面支援兩種模式並強迫在導入時做出選擇。

**Alternatives considered:**
- 維持單一預設，讓需要的專案自己在 `memory/decisions.md` 記例外 — 否決：每個專案重複推導同一套安全要求（掃描、`.gitattributes`、不可逆風險），且極可能漏掉 `*.jsonl -text`（漏了就在 checkout 時被 autocrlf 改寫位元組，考古保真度靜默失效）。框架該把這些沉澱下來。
- 直接把預設改成「追蹤」 — 否決：對可能公開或有外部協作者的 repo 是實質風險，且 B→A 補救不了。預設應維持保守，由專案主動 opt-in。
- 提供自動化的去敏感化再入版控 — 否決：可靠的逐字稿去敏感化做不到（自訂格式 token、對話中的密碼都無法窮舉），宣稱做得到反而危險。README 已明文聲明掃描只降低風險、不消除風險。

**Agent:** cc（2026-07-21 21:45）

## PDOS-D-20260721-1 — hooks 由「建議安裝」升為必裝；依賴 hook 的協定步驟改以「是否生效」為判準

**Decision:** (1) `INSTALL.md` 第 3 節的 hooks 從「建議安裝」改為**必裝**，並補上安裝後驗收步驟（設定檔可解析、計數器冒煙測試、告知 SessionStart/SessionEnd 需下個 session 驗證）；使用者明確拒裝時必須在 `CURRENT.md` 的 Open items 留記錄。`entrypoints/hooks/README.md` 標題同步從「選用但強烈建議」改為「必裝」。(2) `PROTOCOLS.md`「逐字稿歸檔」與 `CHECKLIST_HANDOFF.md` 對應項的判準，從**agent 種類**（cc 有 hook／agy・codex 沒有）改為**本專案的 hook 是否真的生效**：先看 `transcripts/` 有沒有出現本次檔案，沒有就一律手動補，並補上 cc 的本機逐字稿路徑。

**Why:** 兩處自相矛盾造成實際損失。第 0.1 節因 hooks 的執行環境缺件就中止整個安裝，理由明寫「半套框架（有規則、沒 hooks）會讓機制化防線靜默失效，比不裝更危險」——既然缺前置條件就不准裝，第 3 節卻寫「建議安裝」，邏輯不成立。實際案例（gt_auto_tester，2026-07-21）正是落在第 0.1 節警告的狀態：規則裝了、hooks 沒裝。而「有沒有自動歸檔」被寫成 agent 屬性（cc 有／agy・codex 沒有），但它其實是**安裝狀態屬性**；於是「cc + hook 未安裝」這個組合在正本與檢查表中**兩個分支都不屬於**，逐字稿歸檔整步靜默無動作，直到使用者發現 `transcripts/` 只有 agy 的檔案。

**Alternatives considered:**
- 只補 cc 的手動 fallback，hooks 維持「建議安裝」— 否決：那只治症狀。根因是「協定步驟依賴一個選配元件」這個結構，不修的話其他依賴 hook 的機制（PostToolUse 檢查點、PreCompact 提醒、SessionStart 注入）同樣會在半套安裝下靜默失效。
- hooks 改必裝但不加 fallback — 否決：使用者仍可事後移除、hook 也可能安裝了卻沒生效，協定不該假設 hook 一定跑過。兩者並行才是縱深防禦。

**Agent:** cc（2026-07-21 20:55）

## D-20260713-4 — 認知獨立與自然文風採分層索引，不做成 skill

**Decision:** (1) 認知獨立是所有 agent、所有任務型態的核心行為，故在 CONSTITUTION 誠實條款只放短原則；完整操作正本放 `RUBRICS.md` 第 6 節，以「證據／重現／遺漏路徑／真實影響／修正代價」五問判斷。DISPATCH、prompts 與 cc subagent 定義只放任務情境補充並回指 RUBRICS，不複製五問。(2) 自然文風在 CONSTITUTION 語言紀律放一句每次必讀的摘要，詳細正本放 `memory/conventions.md`「框架預設文風」；GOLDEN/INSTALL 將此區標成跨專案保留，只清空專案自訂慣例。(3) 不建立 skill：常駐行為不能依賴被顯式呼叫才生效的能力。

**Why:** agy 在處理其他 agent 的 finding 時曾因沿用對方前提與嚴重度而過度修正；相反地，若只要求「反思」，又容易變成逢人必反或無限分析。分層路由能讓所有 agent 每次看到短原則，只在接手、研究、review 或有爭議時載入完整判準，控制起始 CT 並避免規則雙源。文風同理：日常只載入一句，人味細節按需讀取。

**Agent:** codex（2026-07-13 01:22）

## D-20260713-3 — 消化 codex 二次 review：sh 探測二層化、鎖降級為 advisory＋識別碼複查、spec 同步

**Decision:** (1) INSTALL 0.1 的 `sh` 探測改兩層：PATH 上找不到時，從 `git` 位置推導 `<Git根>\bin\sh.exe`／`usr\bin\sh.exe`——找到＝「已安裝但不在 PATH」，中止但給「加 PATH」的準確指示，不誤導使用者重裝（Windows 常態：git 在 PATH、sh 不在）。(2) 會話鎖誠實降級為 **advisory 防護**並補強：鎖內容加 4-8 碼唯一識別碼（分鐘級時間不夠唯一）、寫後立即讀回驗證持有權、首次寫專案檔前複查持有權、變了即停——check-then-write 競態窗口明文記為已知極限（純 Markdown 下無 atomic create，否決用 mkdir 原子鎖：跨文件改動大、且勸告層級已符合單使用者調度的實際威脅模型）。(3) `handoff-integrity` 正式 spec 的鎖情境同步拆為五個（無鎖／活鎖確認→停止／死鎖確認→復原後換鎖／持有權變更→停止／收尾摘牌），消除「照 spec 實作會直接覆寫活鎖」的繞過漏洞。

**Why:** codex 二次 review 三項發現全數屬實：門檻會冤枉已裝 Git Bash 的 Windows 使用者（實測重現）；「concurrency guard」宣稱超過 check-then-write 的實際能力，違反誠實條款；spec 與 CONSTITUTION 新語意脫鉤，形成規則雙源矛盾。

**Agent:** cc（2026-07-13 02:20）

## D-20260713-2 — 會話鎖升級為並行防護（看到活鎖先問使用者，不可直接覆寫）

**Decision:** 開始協定第 1 步的殘留鎖處理，由「一律視為上次異常中斷 → 修復 → 覆寫」改為**先分辨活鎖與死鎖**：讀出鎖內的 agent 代號與時間向使用者確認；對方還在工作 → 立刻停止、不動任何檔案，等對方摘牌；確認無人在跑才進復原流程並覆寫。PROTOCOLS「衝突處理」章新增「同機並行」小節，明文使用者側紀律（同一時間一個 agent，交接靠 CURRENT.md 換棒）。

**Why:** 2026-07-13 實戰事故：cc 與 agy 平行編輯同一工作目錄，造成四處衝突（重置條款被還原、引用制 regression、CURRENT 指標錯位、依賴宣稱矛盾）。原鎖語意把「正在工作的 agent」誤判成「上次沒收尾的屍體」，不但不擋反而會蓋掉活人的牌。CURRENT.md 的文字提醒是紀律擋不住並行；鎖是既有機制，補一個「先問再覆寫」的分辨步驟即成為 advisory mutex，成本近零。

**Alternatives considered:**
- 純靠時間閾值自動分辨（鎖 < N 小時＝活）— 否決：長 session 與忘摘牌無法可靠區分，誤判代價高；問使用者一次最準。
- 檔案系統強制鎖（flock 等）— 否決：跨工具不通用，違反純 Markdown 零依賴原則。

**Agent:** cc（2026-07-13 01:50）

## D-20260713-1 — 環境門檻硬性化：Git＋Git Bash＋Python 缺一即中止部署

**Decision:** 回應 codex review（P1：agy hook 依賴 Python 未聲明；P2：無 Git Bash 時 hooks 無完整 fallback），使用者明文裁決：**不提供第二條路**。INSTALL.md 新增第 0.1 節硬性環境門檻——部署前必須探測 `git --version`、`sh -c "echo ok"`、`python --version` 三項，任一失敗即**中止部署**並請使用者裝好再來（Windows 只有 `py` 沒有 `python` 視同不合格）。hooks README 移除 PowerShell 降級範本；README 首段「零依賴」修正為「框架本體零依賴，hooks 自動化需 Git＋Python 硬前置」。同時採 codex 建議補自動化誠實分級（PROTOCOLS 層級一）：cc/codex 全自動、agy 半自動（PreInvocation 不能歸零，session 重置靠開始協定第 1 步）。

**Why:** 多套 shell/語言版本的 hook 腳本必然彼此 drift（同邏輯三份誰改誰忘）；半套安裝（有規則沒 hooks）會讓機制化防線靜默失效，比不裝更危險。把環境要求擋在門口是兩害相權取其輕。

**Alternatives considered:**
- 提供 PowerShell／Node／Python 三版本腳本 — 否決：維護成本與 drift 風險（使用者裁決「不給第二條路」）。
- 缺件時降級為紀律模式繼續安裝 — 否決：靜默失效最危險，使用者明確要求中止等補裝。

**Agent:** cc（2026-07-13 01:10）

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
