## 1. 安裝 payload 與檢查器

- [x] 1.1 落實「安裝 payload 與 LF 契約」及 Template payload preserves executable line endings：讓 INSTALL.md 與 GOLDEN_TEMPLATE.md 複製並驗收 .gitattributes、*.sh text eol=lf 與無 CRLF shell bytes；以 git check-attr --all entrypoints/hooks/checkpoint-counter.sh、位元組掃描及自檢清單 read-back 驗證。
- [x] 1.2 依「passdown-lint 命令契約」實作 Installation lint is deterministic：新增 tools/passdown-lint.py 的 --root 與 --json 介面、穩定 error code、archive 排除及無 traceback 失敗路徑；以乾淨 repo 的文字/JSON 模式 exit 0 與 JSON round-trip 驗證。
- [x] 1.3 為 passdown-lint.py 建立可重複的故障 fixture 測試，覆蓋缺 .gitattributes、壞 hook JSON、CURRENT 佔位符、不存在本地連結、缺 memory anchor 與 CRLF shell 六種 exit 1 行為；以 unittest 或暫存目錄測試輸出 code、path、message 驗證。

## 2. Agent 入口與 hook 可信度

- [x] 2.1 落實「驗證狀態矩陣」及 Hook automation claims are evidence-gated：在 entrypoints/hooks/README.md 以 agent/event/output/visibility/status/date 六欄整理 cc、codex、agy，並同步收斂 PROTOCOLS.md 的自動化宣稱；以搜尋確認未 verified 的事件不再被稱為全自動或機制化注入。
- [x] 2.2 安裝本 repo 的 Codex 專案層 hook 並保留下游範本：新增 .codex/hooks.json、校正 entrypoints/hooks/codex-hooks.json.example 的官方事件與輸出格式，讓 SessionStart 與 Externally counted checkpoint reminders 在兩種目錄佈局都找到正確檔案；以 JSON parser、codex doctor --json、直接執行 hook command 與 trust 說明 read-back 驗證，fresh task 尚未證明 context 可見前維持 component-tested。
- [x] 2.3 落實「agy 入口 fallback」及 Agent entrypoints are verified after installation：在 INSTALL.md 與 entrypoints/README.md 定義 .agents/AGENTS.md fresh-session 驗證、失敗後根目錄 AGENTS.md fallback、去除雙正本及最終有效路徑回報；以兩條成功路徑與雙失敗路徑的人工驗收腳本逐項核對。

## 3. Context 與 checkpoint 規則

- [x] 3.1 落實「Context 門檻量測與 fallback」及 Context saturation thresholds use observable signals：在 DISPATCH.md 記錄每個 agent 的 CT 使用率量測來源與查證日期，CONSTITUTION.md 只對可量測 agent 啟用 60%/70%，其餘以 15 輪強制存檔；以內容測試確認禁止模型從名目容量或內省推算百分比。
- [x] 3.2 校正 Externally counted checkpoint reminders 的實作與文件：讓 checkpoint-counter.sh 的 plain/JSON 輸出與各 hook 範本一致、缺檔或非數字從零開始、10/20 邊界才輸出，並明確區分 SessionStart 自動重置與 agy 協定重置；以 sh -n 及 9、10、11、20 次的暫存計數測試驗證。

## 4. 記憶錨點與整合驗收

- [x] 4.1 落實「範例錨點表示法」及 Portable memory anchors：把 PROTOCOLS.md、handoff/_template.md、sessions/_template.md 的假 parseHeader link 改成 inline-code literal，正式錨點仍要求可解析的 repo 相對 link；以 Markdown link 掃描確認三個 src/parser.js 假斷鏈消失，並用故障 fixture 確認真實缺檔仍失敗。
- [x] 4.2 把 Installation lint is deterministic 接進 INSTALL.md 第 5 節與 GOLDEN_TEMPLATE.md 自檢，同時在 CONSTITUTION.md 檔案地圖接入 tools/ 與 .codex/ 部署實體的讀取時機；以逐項 read-back 確認新檔符合既有 File map completeness spec 且安裝流程會實際執行 lint。
- [x] 4.3 執行整體驗收：解析所有 hook JSON、對所有 shell 腳本跑 sh -n、執行 lint 正反案例、codex doctor --json、Markdown link 掃描、spectra analyze 與 spectra validate；除 codex doctor 外的命令 exit 0，doctor 的 checks.config.load.status 必須為 ok（sandbox auth/network/terminal 結果另列、不當成 hook config 失敗），且 Spectra 無 Critical/Warning才可勾選。
- [x] 4.4 依規則修改授權補 memory/decisions.md 決策、更新 handoff/CURRENT.md、建立本次 session log 並視長期價值更新 sessions/INDEX.md；read-back 確認 Direct Memory Source 指向最新 log、無佔位符且所有 Context Index 路徑存在。

## 5. 純 Markdown payload 邊界修正

- [x] 5.1 落實「來源端 passdown-lint 命令契約」：INSTALL 不複製 tools/，安裝 agent 從來源以 --root 驗證不含 tools/ 的目標，且 README、GOLDEN_TEMPLATE、CONSTITUTION、proposal/design/spec 與測試一致說明 lint 不在日常交接執行；以無 tools/ fixture、完整 unittest、lint 與 Spectra validate 驗證。
