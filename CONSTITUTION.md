# Passdown OS — Constitution

本文件是 **codex / cc / agy** 三個 agent 在本專案共同遵守的最高規則。每次新對話（session）開始時，先讀本文件一次，再讀 [`handoff/CURRENT.md`](handoff/CURRENT.md)。細節篇在 [`PROTOCOLS.md`](PROTOCOLS.md)——**效力相同，被指到才讀**。本文件不常變動；若要修改，先在 `memory/decisions.md` 記一筆原因。

## 1. 角色 <a name="roles"></a>

- **codex** = OpenAI Codex CLI
- **cc** = Claude Code
- **agy** = Google Antigravity

三者平權，沒有誰是「主」誰是「副」。任何一方都可能是上一個接手者，也可能是下一個。因此：**你留下的每一份記錄，都要假設是寫給另外兩個工具看的**，不要用只有自己看得懂的縮寫或依賴自己那次對話的隱藏脈絡。

## 2. 檔案地圖 <a name="file-map"></a>

`passdown-os/` 底下每個檔案/資料夾的用途與「什麼時候該讀」：

| 檔案/資料夾 | 用途 | 什麼時候讀 |
| --- | --- | --- |
| `README.md` | 目錄總覽與快速導引 | 只在第一次接觸本框架時 |
| `PROJECT_MANIFEST.md` | 專案 DNA：名稱、目標、版本、支援的 agent、當前焦點與入口 | 第一次接觸本專案時最先讀；里程碑或專案狀態大變時由接手 agent 更新 |
| `CONSTITUTION.md` | 最高規則來源（核心，每次必讀） | 每次新 session 開始，讀一次 |
| `PROTOCOLS.md` | 協定細節篇（Spectra 整合、Task 切分範例、記憶接力、衝突處理、Git 策略、本機記憶同步、維護規則） | 被本檔指到、或遇到對應情境時讀該章節 |
| `DISPATCH.md` | 模型/subagent 調度守則（交辦三要素、回報合約、升降級路徑、驗證不自驗） | 要派 subagent、交辦任務、或評估要不要換模型/agent 時 |
| `RUBRICS.md` | 判斷 checklist（何時升級／算完成／問使用者／換路／驗品質），各附正反例 | 對「做不做、停不停、算不算完成」猶豫時 |
| `prompts/` | 任務交辦填空範本（搜尋/實作/重構/研究/審查） | 要交辦任務時，配合 `DISPATCH.md` 使用 |
| `handoff/CURRENT.md` | 唯一「現在該做什麼」的入口，每次覆寫 | 每次新 session 開始，緊接在 `CONSTITUTION.md` 之後 |
| `handoff/_template.md` | `CURRENT.md` 的填寫模板 | 只在要覆寫 `CURRENT.md` 時參考格式 |
| `CHECKLIST_HANDOFF.md` | Session 結束協定的硬性核對清單（本檔第 6 節的衍生檢查表，正本以第 6 節為準） | 每次執行 Session 結束協定時，開著逐項核對 |
| `sessions/*.md` | 歷史 session 紀錄，稽核/除錯用 | 只在 `CURRENT.md` 明確指向某一篇、或要追查歷史決策時才讀；不要一次讀全部 |
| `sessions/_template.md` | session log 的填寫模板 | 只在要新增 session log 時參考格式 |
| `sessions/INDEX.md` | 重要 session 的索引（快速跳轉的知識圖譜入口） | 要追溯歷史時**先讀索引再精準跳轉**，不要掃 `sessions/` 全目錄；結束協定判定本次有長期價值時補一行 |
| `sessions/archive/` | 超過保留門檻、已摘要進 `decisions.md` 的舊 session | 幾乎不需要讀，除非在做歷史考古 |
| `memory/decisions.md` | 跨 session 的重大決策紀錄（含理由） | 想確認「這個設計為什麼是這樣」時查閱；`CURRENT.md` 或其他文件明確指過來時才讀 |
| `memory/conventions.md` | 專案慣例 | 不確定某個風格/做法是否有既定慣例時查閱 |
| `memory/known-issues.md` | 已知坑與 workaround | 遇到看起來眼熟的問題時，先查這裡再花時間除錯 |
| `memory/glossary.md` | 名詞/縮寫表 | 看到不認得的縮寫時查閱 |
| `memory/redaction-log.md` | 本機記憶匯入時的去敏感化紀錄 | 只在執行「本機記憶同步」的整批匯入流程時相關 |
| `imports/` | 本機原始記憶暫存清洗區 | 只在整批遷移本機記憶時使用，平常不需要看 |
| `references/` | 已合併進正本、僅供歷史參考的舊草稿 | 幾乎不需要讀，正式規則一律以 `CONSTITUTION.md` 為準 |
| `INSTALL.md` | **給 agent 的安裝指南**：使用者要你把本框架裝進某專案時的完整執行程序（複製清單、汙染排除、重置、入口與 hooks 設定、驗收） | 使用者說「把 passdown-os 套用／安裝到專案」時，照此執行 |
| `GOLDEN_TEMPLATE.md` | 套用時「哪些檔案要重置、哪些規則不可動」的對照表（`INSTALL.md` 執行中會指到） | 執行 `INSTALL.md` 第 2、5 步時查閱 |
| `entrypoints/` | 各 agent 入口設定檔範本、cc 專用的 `claude-agents/` subagent 範本組與 `hooks/` 自動注入設定 | 只在新專案要設定 agent 入口／安裝 cc 自動調度或 hook 時查閱 |

除了 `handoff/CURRENT.md`，其他所有檔案都是「被指到才讀」的參考資料，不是「主動掃描找下一步」的來源——這是刻意設計，避免每次接手都要把整個目錄讀過一遍。

本框架疊加在 Spectra（`openspec/`）之上：WHAT 歸 Spectra，WHO/WHEN 歸 `passdown-os/`。整合細節與**不使用 Spectra 時的替代方案** → 見 `PROTOCOLS.md`「與 Spectra 的關係」。

## 3. Context 存量與防禦性壓縮規則 <a name="context-rules"></a>

不要等到 context window 滿了才整理，因為**撰寫交接與存檔本身也需要消耗可觀的 token**。若在 CT 快滿時才寫交接，容易引發寫到一半被自動壓縮、遺失脈絡或 Token 溢出。符合以下任一條件時，必須主動執行「Session 結束協定」：

1. **完成一個 task**（不論大小）。
2. **即將切換到不相關的檔案群 / 子系統**。
3. **即將切換 agent**（例如使用者說要換另一個工具接手）。
4. **主動防禦存檔線（60% 滿 / 約 15 輪對話）**：對話長度達到當前 Agent Context 的 60% 或對話達 15 輪時。此時先執行結束協定存檔，接著**直接提醒使用者**：「context 已達存檔線，交接已寫好，建議重開一個全新 session 接手執行本專案」。**優先做法是由使用者重開新 session**（全新 context 品質最好，也最不會有壓縮遺失）；只有使用者明確表示要在原對話繼續時，才啟動壓縮機制（例如 cc 的 `/compact`）。不可未提醒使用者就自行壓縮，也不可不存檔硬撐。
5. **強制硬紅線（70% 滿）**：一旦 context 達到 70%，**必須立刻停止所有開發工作，將剩下的 30% 預算全部用於執行「Session 結束協定」存檔**。絕不可在超過 70% 滿的 context 中繼續撰寫新代碼或進行複雜 debug。
6. **防範自動截斷（Sliding Window）**：若所使用的 Agent 底層會自動進行無感知的歷史截斷或自動摘要（如部分 web-based 或自研的 agent 框架），則不論 CT 大小，**對話一律限制在 12-15 輪內**，時間一到立刻存檔並請使用者**重置/開啟全新對話**，防止舊決策或 debug 脈絡被底層悄悄丟棄。
7. **準備手動讓對話被壓縮/摘要前**（必須先完成記憶同步，壓縮後細節會遺失）。

交接的最小單位可以小於一個 Spectra task。

各輪數門檻的用途區分（多條同時適用時以先到者為準）：**10 輪／20 輪**是「規劃 task 大小」的目標值（見下方 Task 切分準則）；**15 輪或 60% 滿**是「執行中主動存檔」的觸發線；**12-15 輪**是「會自動截斷的環境」的硬性重開線。

除了上述整段式存檔線，另有**持續存檔 checkpoint**（無條件適用）：約每 10 次工具呼叫，就在本次 session log append 一行當前進度——已安裝 hook 的環境會由 hook 自動計數提醒。細節與 hook 安裝方式見 `PROTOCOLS.md`「持續存檔機制」。

## 4. Task 切分與 Context 預算準則 <a name="task-rules"></a>
<!-- cc review 修正：將寫死的 token 數字（如 cc≈200k）抽離，統一由 DISPATCH.md 查證，避免規則與數字耦合 -->

一個 task 要夠小，判斷標準是以下四項，缺一不可，而不是套用固定的檔案/程式碼結構規則：

1. **可驗證** — 有明確的「完成長怎樣」：能檢查出「做完了嗎？」這個問題的答案，而不是「處理好 XX」這種模糊描述。
2. **獨立** — 完成這個 task 不需要等另一個未完成的 task 先做完。若真的有先後關係，那是「順序」問題，仍可以拆成兩個獨立 task，只是有先後順序。
3. **單一關注點** — 只改一件事、一個檔案/一個子系統，不是「順便把三件事一起做掉」。
4. **Context 預算制（核心限制）** — **Task 的規模必須與接手 Agent 的 Context Window (CT) 深度掛鉤**。在對話長度達到該 Agent 的「實用上限（通常為 40% ~ 50% 滿）」前，必須能夠完整完成並驗證該 Task。
   - **對於小 CT Agents（請查閱 DISPATCH.md 當前數值表）**：必須使用**微型 Task (Micro-tasking)**。改動範圍應控制在 1-2 個檔案內，預期對話在 10 輪以內結束。
   - **對於大 CT Agents（請查閱 DISPATCH.md 當前數值表）**：可以採用**中型 Task**。但即使 CT 很大，也不應讓單一 Task 預期對話超過 20 輪，以防 Agent 思考發散或混淆細節。
   - 上述 CT 數值僅為撰寫當時的參考值，會隨各工具版本與訂閱方案變動——**以當下環境查證為準，不可憑舊記憶假設**（各 agent 的實測值維護在 `DISPATCH.md` 第 7 節的查證表）。
   - **動態拆分**：在執行過程中，一旦發現遇到預期之外的 bug 或複雜重構，導致對話輪數迅速上升、Context 消耗過快（已達 CT 一半以上），**必須立即停止工作，執行「Session 結束協定」將當前進度存檔並將剩餘部分拆成新 Task**，絕不可在快飽和的 Context 中硬撐。

對「這個 task 算不算夠小」拿不準時 → 見 `PROTOCOLS.md`「Task 切分範例詳解」（coding 與非 coding 專案的正反例）。

## 5. Session 開始協定（固定順序） <a name="session-start"></a>
<!-- cc review 修正 v2：會話鎖改為完整閉環（進門查牌 → 掛牌 → 結束協定最後一步摘牌），並補上 PROJECT_MANIFEST 的首次接觸路由 -->

1. **檢查並掛上會話鎖（強制首個動作）**：
   - **先檢查** `sessions/.active_lock` 是否存在。**存在** → 代表上一個 session 沒有正常跑完結束協定（可能中斷、context 溢出、或忘了收尾），記下這個事實，第 5 步復原協定會用到。
   - 接著（無論剛才存不存在）**覆寫** `.active_lock`，內容為：本次 agent 代號 + session 開始時間（`YYYY-MM-DD HH:mm`）。
   - 注意：這個鎖**不是記錄，是「值班牌」**——掛牌上工、下班摘牌（見結束協定最後一步）。真正的記錄永遠在 `sessions/*.md`，刪鎖不會遺失任何交接內容。此檔已列入 `.gitignore`，屬本機暫存，不進版控。
2. **首次接觸本專案時**，先讀 [`PROJECT_MANIFEST.md`](PROJECT_MANIFEST.md)（30 秒掌握專案定位、版本與入口）；已熟悉本專案則跳過。
3. 讀本文件（`CONSTITUTION.md`）— 每次對話只需讀一次。
4. 讀 [`handoff/CURRENT.md`](handoff/CURRENT.md) — 掌握目前在哪個 change、做到哪、下一步是什麼。（cc 若已安裝 SessionStart hook，CURRENT.md 全文會自動注入在 context 開頭，此步驟視為完成、不需重讀。）
5. **交接完整性檢查（復原協定）**——兩個訊號，任一觸發就先修復再動工：
   - **訊號 A（會話鎖殘留）**：第 1 步發現殘留的 `.active_lock` → 直接視為「上次未正常收尾」，先讀 `sessions/`（不含 `archive/`）最新一份 log，據此把 CURRENT.md 修復成真實狀態。
   - **訊號 B（語意不一致）**：檢查 `sessions/`（不含 `archive/`；忽略 `.active_lock`、`.toolcount` 等 dotfile，只看 `*.md`）最新一份 log 的檔名，是否就是 CURRENT.md 的 `Direct Memory Source` **第一項**所指向的那份：
     - 最新 log **不是** Direct Memory Source 所指（存在一份更新、未被 CURRENT.md 收錄的 log）→ 上次結束協定沒跑完整（寫了 log 但沒更新 CURRENT.md）。先讀那份最新 log，據此修復 CURRENT.md，再繼續往下。
     - Direct Memory Source 指向的 log **不存在** → 上次少寫了 session log 或 CURRENT.md 填錯。不需回補，但在本次 session log 的 `Started from` 註明「前次交接缺 log」。
     - 註：**不用時間戳先後做主判準**——結束協定「先寫 CURRENT.md、後寫 log」的固定順序，會讓 log 永遠看起來比較新，時間戳比對必然誤判。log 檔名中的日期與 `HHmm` 一律指 **session 開始時間**（不是寫檔時間），僅供人類排序閱讀。
   - 兩個訊號都沒觸發 → 交接完整，直接往下。
6. 執行 `spectra list --parked`，確認目前 active / parked 的 changes 是否與 CURRENT.md 描述一致（不使用 Spectra 的專案 → 依 `PROTOCOLS.md` 替代方案跳過）。
7. 若 CURRENT.md 指向某個 active change，讀該 change 的 `tasks.md`，找到第一個未勾選項目，從那裡開始。若 CURRENT.md 的 `Context Index` 有指定記憶錨點，依 `PROTOCOLS.md`「記憶索引與接力協定」讀取後再動工。
8. **不要**一開始就讀 `sessions/` 底下所有歷史檔案 — 那是稽核 / debug 用的資料，不是接手所需的最小資訊。要追溯歷史時，先看 [`sessions/INDEX.md`](sessions/INDEX.md) 索引再精準跳轉；只有當 CURRENT.md 裡的 `Context Index`、`decisions.md` 或 INDEX.md 明確指向某一篇 session log 時（或依第 5 步復原協定的需要）才去讀。

## 6. Session 結束協定（強制執行） <a name="session-end"></a>

這是本框架最核心的規則：**任何工具的私有本機記憶都不是可信的唯一記錄，`passdown-os/` 才是。** 不論這次 session 做的事大小、不論是否覺得「這次沒什麼好記的」，結束前都必須完整跑完以下步驟（cc 已安裝 `/handoff` 指令的專案，使用者打 `/handoff` 即觸發本協定）。執行時開著 [`CHECKLIST_HANDOFF.md`](CHECKLIST_HANDOFF.md) 逐項核對：

1. 若有做完的 task，更新對應 change 的 `tasks.md` 勾選狀態。
2. 覆寫（不是新增）[`handoff/CURRENT.md`](handoff/CURRENT.md)，反映最新真實狀態。`Context Index` 欄位的填法見 `PROTOCOLS.md`「記憶索引與接力協定」。**`Direct Memory Source` 第一項必須填本次 session log 的檔名**（第 3 步即將建立的那份）——開始協定的交接完整性檢查（訊號 B）靠這個指標運作。
3. 用 [`sessions/_template.md`](sessions/_template.md) 在 `sessions/` 新增一份本次 session 的 log，檔名格式：`YYYY-MM-DD-HHmm-<agent>-<slug>.md`，其中日期與 `HHmm` 一律填 **session 開始時間**（不是寫檔時間）。其中 `<slug>` 用小寫英文 + 短橫線，3-5 個詞，描述本次 session 主要做的事（例如 `setup-auth-middleware`、`fix-csv-parser-edge-case`、`review-api-design`）。**這一步不可省略**——即使本次 session 沒有產出程式碼變更（例如只是討論、只是回答問題），只要對專案的理解或方向有影響，也要留一份簡短 log。若本次 session 具長期參考價值（重大決策、架構變動、複雜 debug 的解法），同時在 [`sessions/INDEX.md`](sessions/INDEX.md) 補一行索引（日常瑣事不必）。
4. 若本次做了跨 spec、影響後續判斷的決策（例如選了某個技術方案、放棄某個做法），在 `memory/decisions.md` 補一筆。
5. 若發現了值得記住的坑或 workaround，補進 `memory/known-issues.md`。
6. **本機記憶同步檢查（強制）**：檢查本次 session 是否有內容被寫進了目前工具自己的私有記憶系統（例如 Claude Code 的 `~/.claude/.../memory/` auto memory、Codex 的本機 session 記錄）。若有，依 `PROTOCOLS.md`「本機記憶同步」章節，把重點內容鏡射一份回 `passdown-os/`（sessions/ 或 memory/），**回寫的每一條都依第 8 節簽名規則附上 agent 代號與時間戳**，不能讓任何決策或事實只存在單一工具看得到的地方。若本次 session 沒有寫入任何本機私有記憶，這步驟視為已確認、無需動作。
7. **Read-back 驗證（不可自認完成）**：重新讀取剛覆寫的 CURRENT.md 與剛新增的 session log，逐項確認：(a) 檔案確實存在且內容完整；(b) `Next concrete step` 是具體可執行的一句話，不是 `<佔位文字>` 或空白；(c) `Context Index` 指向的檔案路徑真實存在。任一項不過就修到過為止——「我寫了」不等於「寫對了」。
8. 視情況執行 `/spectra-commit` 提交本次變更相關的檔案（不使用 Spectra → 一般 `git add` + `git commit`；分支與 commit 紀律見 `PROTOCOLS.md`「Git Commit 與分支策略」）。
9. **摘牌簽退（最後一步）**：確認第 2、3、7 步都完成後，**刪除 `sessions/.active_lock`**（若存在 `.toolcount` 計數檔可一併刪除）。刪除鎖就是「本次 session 正常收尾」的實體簽退訊號——鎖裡只有開始時間，這資訊 session log 檔名本來就有，刪它不會遺失任何記錄。**沒摘牌，下一個接手者就會把本次視為異常中斷並啟動復原協定。**

上述步驟做不完（例如被迫中斷）時，至少要完成第 2、3 步（覆寫 CURRENT.md + 留一份 session log）再刪除 `.active_lock`，確保下一個接手者不會完全看不到這次發生過什麼事。連這都來不及（直接斷線）時，殘留的 `.active_lock` 正是下一位接手者啟動復原協定的訊號——這正是它存在的目的。

## 7. 卡關 / 升級規則 <a name="blocker-rules"></a>

觸發條件（滿足任一即觸發，不憑感覺判斷「合理次數」）：

1. 需求不確定，且符合 [`RUBRICS.md`](RUBRICS.md)「何時停下來問使用者」的任一判準。
2. **同一件事重試已達兩輪仍失敗**（第一次正常嘗試不計；之後每次換做法重來算一輪）。重試第二輪前，先過一遍 `RUBRICS.md` 第 4 節的「換路訊號」——有時該做的不是再試，是退回上一個決策點換方向。
3. 需要升級模型/agent 但已達 [`DISPATCH.md`](DISPATCH.md) 升降級路徑的頂端。

觸發後：把問題寫進 `handoff/CURRENT.md` 的 **Blockers** 欄位，清楚描述卡在哪、已經試過什麼（含失敗軌跡），然後停下來，不要用猜測硬做下去。下一個接手者（人類或 agent）看到 Blockers 欄位就知道要先處理這個。

## 8. 身分簽名規則 <a name="signature-rules"></a>

所有寫進 `sessions/`、`handoff/CURRENT.md`、`memory/decisions.md` 的條目，都要標註：
- Agent 短代號（codex / cc / agy）
- 時間戳（`YYYY-MM-DD HH:mm`）——一律使用執行環境的**本機時間**；跨時區協作的專案，在條目後附註 UTC 偏移（例如 `2026-07-12 19:00 +08:00`）

方便之後追溯「這個判斷是誰在什麼情況下做的」。

## 9. 誠實條款 <a name="honesty-rules"></a>
<!-- cc review 修正：加入越界讀取自報機制，以可審計性取代嚴格禁止，以便未來調整不合理的規則邊界 -->

- **不編造**：模型名稱、參數、路徑、指令、外部工具的行為——查證後才寫；查不到就明確標「**未確認**」，並註明可以去哪裡查（例如 usage 儀表板、官方文件）。寧可留空標註，不可填一個看起來合理的猜測。
- **回報忠實**：測試失敗就說失敗並附輸出；步驟被跳過就說被跳過；做不到就說做不到＋已試過什麼。不可用「應該可以」「大致完成」掩蓋沒驗證的部分。
- **承認極限**：拆解、驗證、多樣本評審補得了執行品質；模糊需求與品味判斷補不了——遇到就寫明處理方式（升級模型、問使用者、或明說做不到），不硬做。
- **越界讀取自報**：如果你為了保險起見，讀取了不在允許範圍內或未被明確指向的檔案，必須在交接時誠實記錄「本次讀取超出範圍：讀了 X，原因 Y」。不苛責越界，但必須留存紀錄以供後續優化規則。

## 10. 程式碼註解紀律（必須，非建議） <a name="defensive-commenting"></a>
<!-- 使用者指示升級：由「特殊邏輯才註解」改為「所有 code 一律必須註解」，服務於學習與跨 agent review -->

**通用規則（適用於任何有寫 code 的專案，包含 vibe coding）**：任何新增或修改的程式碼，一律**必須（MUST）**加上正體中文註解，說明關鍵邏輯的「為什麼這樣寫」（Why），而不只是「這行在做什麼」（What）。這是硬性規定，原因有二：

1. **使用者要透過註解學習**：使用者會閱讀你寫的 code 來理解思路；沒有註解的 code 對使用者是黑箱，等於剝奪了學習機會。
2. **跨 agent review 的生存線**：接手的 Agent 只有當下的 Context，不會為了一個 function 去翻所有歷史 session log。別的 agent review 或重構時，需要從註解知道你當下為什麼這樣寫，才不會誤判成冗餘代碼而刪除。

**特殊邏輯加強版**：非標準實作、踩坑後的 Workaround、缺乏明確架構下的 Vibe Coding 產物，註解必須**更詳盡**——寫清楚踩了什麼坑、為什麼標準做法不行、這段不能怎麼改。你的註解是保護這段 code 存活與被正確理解的唯一防線。

## 11. 語言與編碼紀律（一啟動即生效） <a name="lang-encoding"></a>
<!-- 使用者指示新增：從 session 第一個回覆起就適用 -->

1. **正體中文（zh-TW）**：所有對話回覆、交接文件（`CURRENT.md`、session log、`memory/` 各檔）、程式碼註解，一律使用正體中文。程式碼本身、指令、專有名詞、檔名保留原文即可，不必硬翻。
2. **UTF-8 編碼**：所有寫入的文字檔案一律使用 UTF-8（無 BOM）。Windows 環境特別注意：PowerShell 5.1 的 `Out-File` / `Set-Content` 預設輸出 UTF-16，**必須明確指定 `-Encoding utf8`**；寫檔後若發現中文變亂碼，先檢查編碼再檢查內容。

其他情境（git 衝突、分支紀律、檔案歸檔與精簡、修改框架規則的權限）→ 遇到時讀 `PROTOCOLS.md` 對應章節，該檔開頭有觸發時機對照表。
