## 1. 共用狀態模板

- [x] 1.1 依「三段生命週期 Skills 與單一共享資產來源」及「Interface and data shape」建立 setup assets，使 Safe project initialization 可從唯一模板來源產生 constitution、CURRENT、handoff、session、decisions 與 known-issues；以逐檔 read-back 確認 proposal 列出的七個 asset 路徑存在且沒有未解析 placeholder。
- [x] 1.2 在 CURRENT 與 session 模板落實 Durable current-state contract 及「最小持久狀態與 handoff_id 復原」，使所有必要欄位、唯一 identifier、可驗收 next step、anchors 與 session 專屬欄位具有一致格式；以內容審查逐欄對照 spec，並用一組具體 handoff 資料填寫模板確認不需新增欄位。

## 2. 生命週期 Skills

- [x] 2.1 實作 `.agents/skills/setup-passdown/SKILL.md` 的安全初始化、相容安裝驗證與衝突停止流程，交付 Safe project initialization、「安全初始化與 read-back 驗證」及 Read-back verification；以空白目標、完整既有目標、不相容既有目標三個人工 fixture 驗證建立、冪等與不覆寫行為。
- [x] 2.2 實作 `.agents/skills/resume-passdown/SKILL.md` 的讀取順序、一致性摘要及 Deterministic resume and recovery，使完整較新 log 可重建 CURRENT、含糊衝突只產生 recovery-required；以一致、較新完整 log、缺欄位衝突三個 fixture 比對輸出與檔案 mutation。
- [x] 2.3 實作 `.agents/skills/handoff-passdown/SKILL.md` 的 Event-driven handoff logging 與「事件驅動紀錄取代每輪強制 log」，使六類持久變更新增一筆共享 `handoff_id` 的 log，而純問答不改 CURRENT 或 sessions；以有變更與無變更 fixture 比對 handoff 前後檔案數量、identifier 及內容。

## 3. 可組合技能路由與政策

- [x] 3.1 在模板、handoff 與 resume 流程落實 Grounded skill suggestions、「Suggested skills 採名稱、理由與可用性狀態」及 Artifact references without duplication，使建議只含 name、reason、availability，引用只含 project-root-relative path 或 URL 與用途；以 available、unverified、空建議、local artifact、external URL 五個案例逐欄審查輸出，確認未複製來源全文。
- [x] 3.2 在 constitution 與三個 skills 落實 Routing remains optional and non-blocking 及「工具中立與風險分級政策」，使自由 `agent_id`、缺少建議 skill 與不同相容 skill 都不阻擋交班，且獨立第二意見只對高風險工作為必要；以兩個非 codex agent_id 與一個缺少建議 skill 的 fixture 確認 resume 仍完整輸出狀態與 references。
- [x] 3.3 建立 `docs/passdown-composable-skills-evaluation.md`，逐項評估原 Passdown 規則為 keep、adapt 或 remove，說明 Third-party implementation boundary、責任分層與不匯入第三方實作；以內容審查確認文件涵蓋 CURRENT、logs、memory、recovery、context 門檻、agent 名稱、調度、自驗及 composable skill routing 九個主題。

## 4. 契約驗收與邊界檢查

- [x] 4.1 依「Observable behavior」及「Acceptance criteria」完整走查 setup → handoff → resume 與較新 log recovery，確認產生檔案、摘要欄位、共享 identifier、無變更不寫 log 及 deterministic repair 均符合 spec；在 task 完成記錄中附上每個 fixture 的輸入狀態、觀察結果與通過判定。
- [x] 4.2 依「Failure modes」製造既有目標衝突、缺失 anchor、含糊 identifier 與 partial write，確認每種失敗都列出具體原因且不猜測或覆寫；完成後執行 `spectra analyze integrate-passdown-composable-skills --json` 與 `spectra validate integrate-passdown-composable-skills`，並審查實作只落在「Scope boundaries」列出的檔案與行為內。

## Verification records

### Task 4.1 — lifecycle and recovery fixture

- Input: blank target, one durable handoff, receiving agent resume, one newer complete log, then a no-durable-change handoff evaluation.
- Observed: setup created all six required files; handoff added exactly one log; CURRENT and log shared an identifier; ordinary resume returned `ready`; the newer complete log deterministically rebuilt CURRENT and returned `recovered`; no-change evaluation preserved the session count.
- Result: pass. Read-back also found no template marker and retained one executable, verifiable next step.

### Task 4.2 — failure fixtures

- Existing target conflict: reported all six missing required files, stopped, and preserved the existing sentinel byte-for-byte.
- Missing anchor: reported `specs/does-not-exist.md`, returned recovery-required, and left CURRENT unchanged.
- Ambiguous identifier: reported both conflicting identifiers at the equal timestamp, returned recovery-required, and did not synthesize state.
- Partial write: reported that the session log exists while CURRENT is missing and that the next resume requires recovery.
- Result: pass. Every fixture exposed a concrete reason and no fixture guessed, merged, or overwrote authoritative state.

### Final checks

- All three skill directories passed the official `quick_validate.py` validator.
- `spectra validate integrate-passdown-composable-skills` passed.
- `spectra analyze integrate-passdown-composable-skills --json` reported clean coverage, consistency, and gaps; its 14 ambiguity findings are non-blocking suggestions to add more scenario examples.
- Scope review found only the three packaged skill directories and their shared setup assets, the evaluation document, and this task completion record. Each `agents/openai.yaml` is generated presentation metadata within its corresponding skill package.
