## Context

三份 review 橫跨 2026-07-11 至 2026-07-16。現行 main 已透過兩個 archived changes 完成會話鎖閉環、語意式交接完整性檢查、sessions/INDEX.md 與 transcripts/ 接線、時間戳語意及章節引用修正；本 change 只處理在目前檔案中仍可重現的缺口。

目前 INSTALL.md 的 payload 清單漏列 .gitattributes，而 hooks 全部依賴 POSIX shell。PROTOCOLS.md 同時把 cc/codex 稱為全自動，entrypoints/hooks/README.md 卻保留 PreCompact、Windows SessionEnd 與部分 PostToolUse 注入待實測。CONSTITUTION.md 的 60%/70% 規則也沒有把「有外部量測」與「模型無法可靠內省」分開。這些問題共同造成安裝成功與防線實際生效之間的落差。

## Goals / Non-Goals

**Goals:**

- 讓框架 payload 在 Windows 與 POSIX checkout 都保留 shell 腳本 LF。
- 讓每個啟用 agent 的入口與 hook 都有明確的驗證步驟、驗證狀態和失敗 fallback。
- 讓 context 百分比門檻只依賴可查證量測；無量測時仍有可執行的輪數代理。
- 提供一個可重複執行的安裝檢查命令，取代只靠目視的必要檔案、JSON、錨點與佔位符檢查。
- 消除三處 Code Symbol Anchor 範例造成的假斷鏈。

**Non-Goals:**

- 不新增英文版、VERSION、CHANGELOG、CONTRIBUTING、issue template 或一行式遠端安裝器。
- 不把檔案地圖搬出 CONSTITUTION.md，不移除 sessions/INDEX.md，也不改 CURRENT.md 與 session log 的寫入順序。
- 不宣稱完成無法在本次環境實機觸發的 cc、codex 或 agy hook；未實測項目維持未確認。
- 不加入 gitleaks、trufflehog 或其他外部依賴，也不新增 pre-commit hook。
- 不加入 session 越界讀取自報欄位或 CURRENT.prev.md 備份。

## Decisions

### 安裝 payload 與 LF 契約

INSTALL.md 的根目錄 payload 必須包含 .gitattributes，GOLDEN_TEMPLATE.md 必須把它列為不可遺失的規則檔與自檢項。檢查器同時確認 .gitattributes 含有 *.sh text eol=lf，並掃描框架內 shell 腳本不得含 CRLF。

選擇在既有 .gitattributes 上建立契約，而不是讓每個 hook 自行去除 CR，因為換行正規化屬版本控制邊界責任，分散到每個腳本會重複且無法保護未來新增的 shell 檔。

### 驗證狀態矩陣

entrypoints/hooks/README.md 以 agent、事件、輸出格式、預期可見位置、驗證狀態、驗證日期六欄記錄 hook 狀態。狀態只允許 verified、component-tested、unverified 三種：

- verified：已在真實 agent session 觸發，且模型回應可證明內容進入 context。
- component-tested：腳本或假 JSON 可執行，但未證明真實 lifecycle event 與模型可見性。
- unverified：尚無可重現證據。

PROTOCOLS.md 只能把 verified 的事件稱為機制化注入；component-tested 與 unverified 必須描述成候選防線，並保留紀律 fallback。INSTALL.md 對每個啟用的 agent 執行矩陣列出的驗證，失敗時回報具體事件，不得把整體安裝標為完全驗收。

本 repo 自己使用的 Codex hooks 安裝在 .codex/hooks.json；下游安裝範本仍是 entrypoints/hooks/codex-hooks.json.example。兩者使用同一事件與輸出契約，但命令路徑分別對應「框架即 repo 根目錄」及「目標專案下的 passdown-os 子目錄」。專案層 hook 必須由 Codex trust 後才執行，codex doctor 僅證明設定可載入，不能取代 fresh task 的 context 可見性驗證。

### Context 門檻量測與 fallback

DISPATCH.md 的 agent 查證表新增 CT 使用率量測來源與驗證日期。CONSTITUTION.md 的 60%/70% 門檻只在該列有可操作、當下可查證的量測來源時生效。沒有量測來源時，15 輪對話是強制存檔線；已驗證的外部 tool-call checkpoint 只作較早提醒，不能換算成百分比。

不以模型自我估計百分比，也不從名目 CT 容量推算當前使用率，因為兩者都不能提供可重現的觸發證據。

### agy 入口 fallback

安裝 agy 時先依 entrypoints/README.md 的候選路徑部署 .agents/AGENTS.md，開 fresh session 驗證入口段落是否被主動遵循。驗證失敗時，安裝程式把同一段合併到專案根目錄 AGENTS.md，再開 fresh session 重驗。最終回報必須寫明實際生效路徑；不得同時保留兩份未標示正本的 Passdown OS 段落。

此決策比永久雙寫兩個入口檔更能避免規則雙源漂移。

### passdown-lint 命令契約

新增 tools/passdown-lint.py，只使用 Python 標準函式庫。介面為 python tools/passdown-lint.py [--root PATH] [--json]；預設 root 是目前 repo。成功輸出摘要並回傳 0，任何必要檢查失敗時逐項列出穩定檢查代碼與相對路徑並回傳 1。--json 輸出物件包含 ok、root、checks、errors，其中每個 error 包含 code、path、message。

必要檢查範圍：

- 安裝 payload 必要檔案存在，且 .gitattributes 含 LF 規則。
- 所有 entrypoints/hooks/*.json.example 可被 JSON parser 讀取，所引用的 repo 相對腳本存在。
- handoff/CURRENT.md 與 PROJECT_MANIFEST.md 沒有角括號佔位符。
- 非 archive 的 Markdown 本地連結目標存在；URL、純錨點與明確標成 literal example 的文字不當成檔案。
- handoff/CURRENT.md 的 Direct Memory Source 與 Context Index 所列 repo 相對目標存在。
- entrypoints/hooks/*.sh 不含 CRLF。

INSTALL.md 把此命令列為第 5 節必要驗收；日常使用仍是選配，不改變框架的執行期零依賴定位。若 Python 門檻未通過，安裝本來就必須中止，因此不另設靜默降級。

### 範例錨點表示法

PROTOCOLS.md、handoff/_template.md、sessions/_template.md 的 parseHeader 範例改為 inline-code literal，而非可點擊 Markdown link。正式填入的 Code Symbol Anchor 仍必須是 repo 相對 Markdown link，且指向存在的檔案；檢查器只豁免被 inline code 包住的教學範例。

這保留範例可讀性，也讓一般 Markdown link checker 與 passdown-lint.py 得到一致結果。

## Implementation Contract

**Operator-visible behavior**

- 依 INSTALL.md 安裝後，目標 passdown-os/.gitattributes 必定存在，且 shell 腳本 checkout 為 LF。
- 安裝回報逐一列出每個啟用 agent 的入口路徑與 hook 事件狀態，不以單一「hooks 已安裝」概括未驗證事件。
- 沒有 CT 使用率量測來源的 agent 在第 15 輪必須進入存檔流程；文件不得要求它猜測 60% 或 70%。
- 執行 python tools/passdown-lint.py 對乾淨樣板回傳 0；刪除 .gitattributes、把 hook JSON 改壞、在 CURRENT.md 留佔位符、加入不存在的本地連結或把 shell 腳本改成 CRLF 時回傳 1。

**Interfaces and data shapes**

- CLI：python tools/passdown-lint.py [--root PATH] [--json]。
- JSON：ok 為 boolean、root 為字串、checks 為執行過的檢查代碼陣列、errors 為物件陣列；error 必含 code、path、message。
- Hook 狀態：verified、component-tested、unverified。
- CT 查證欄位：名目容量、實用上限、使用率量測來源、查證日期、備註。

**Failure behavior**

- lint 找不到 root 或無法讀必要檔案時輸出具體 error 並回傳 1，不丟未處理 traceback。
- agy 候選入口驗證失敗時自動改用根目錄 AGENTS.md 再驗證；第二次仍失敗則安裝回報為未驗收，不宣稱入口生效。
- hook event 無法在當前環境觸發時標為 unverified，不用 component test 推論模型可見性。
- lint 不掃 openspec/changes/archive、sessions/archive、references 與 transcripts 的歷史內容，避免歷史紀錄與原始資料造成假陽性。

**Acceptance criteria**

- python tools/passdown-lint.py 與 python tools/passdown-lint.py --json 都在乾淨樣板通過，且 JSON 可再次由標準 JSON parser 解析。
- 對上述五種故障各建立暫存副本測試，確認命中預期檢查代碼且 exit code 為 1。
- sh -n 通過所有 entrypoints/hooks/*.sh；所有 hook example 通過 JSON 解析。
- rg 掃描正式文件不再出現可解析為真實連結的 parseHeader 範例。
- spectra validate close-consolidated-review-gaps 與 spectra analyze close-consolidated-review-gaps 不含 Critical 或 Warning。

**Scope boundaries**

- 實作範圍只含 proposal Impact 所列檔案，以及規則變更要求的 memory/decisions.md、handoff/CURRENT.md、sessions/INDEX.md 與一份新 session log；.codex/hooks.json 是本 repo 的部署實體，不會被 INSTALL.md 當成下游 payload 直接複製。
- 不修改既有 archived change、歷史 session log 或兩份正式 spec 的非本 change requirement。
- 不以無法取得的外部 agent session 偽造 verified 狀態。

## Risks / Trade-offs

- [Risk] 安裝檢查器會讓純 Markdown 專案看似增加 Python 依賴 → Mitigation：Python 已是 INSTALL.md 的硬性 agy hook 門檻；檢查器只在安裝與維護時執行，框架日常協定仍是 Markdown。
- [Risk] fresh-session hook 驗證可能需要人工觀察模型是否看到內容 → Mitigation：矩陣把 component test 與真實 context 驗證分開，無證據就維持 unverified。
- [Risk] Markdown link parser 可能誤判複雜語法 → Mitigation：只支援框架實際使用的 inline links，排除 URL、純錨點、archive 與 inline-code literals，並以具體 fixture 測試。
- [Risk] 單一 change 觸及多份文件 → Mitigation：所有改動都服從「安裝完成不等於防線生效」這一共同契約，tasks 依 payload、驗證矩陣、門檻、lint、整合驗收分組。
