## Summary

整合三份獨立 review，修補 Passdown OS 目前仍存在的導入、hook 可信度、context 門檻與機械驗證缺口。

## Motivation

既有 archived changes 已解決會話鎖、懸空引用、INDEX、transcripts 與時區等多數舊問題，但目前安裝流程仍會漏掉保護 shell 換行的 .gitattributes，且規則文件對 hook 注入與 context 百分比的描述強於實測證據。這會讓使用者在安裝完成後誤以為機制化防線已生效，實際卻可能只寫入 transcript、未被入口檔載入，或在 Windows checkout 後因 CRLF 失效。

## Proposed Solution

- 建立可驗收的安裝完整性契約：複製 .gitattributes、保留 *.sh text eol=lf，並逐一驗證啟用 agent 的入口檔、SessionStart/PreInvocation 注入、checkpoint 提醒、PreCompact 與逐字稿歸檔。
- 對尚未完成實機驗證的 hook 明確標示狀態；只有在輸出已證實進入模型 context 時，文件才可宣稱「機制化注入」或「全自動」。
- 將 60%/70% context 門檻改成有外部量測來源時才生效；沒有可查證量測來源時，以 15 輪對話與外部工具呼叫 checkpoint 作為可執行代理。
- 為 agy 入口檔加入安裝時讀取驗證與根目錄 AGENTS.md fallback，避免 .agents/AGENTS.md 未被載入時靜默失效。
- 將官方支援的專案層 Codex hook 實際安裝到本 repo 的 .codex/hooks.json；保留 entrypoints/hooks/codex-hooks.json.example 作為下游專案範本，兩者分別驗證。
- 新增純 Python 標準函式庫的來源端安裝檢查器，驗證必要檔案、LF 屬性、模板佔位符、記憶錨點目標與 hook JSON；由安裝 agent 從來源 repo 對目標執行，不複製進下游 payload，也不在日常交接執行。
- 將三處範例 Code Symbol Anchor 改成不會被 Markdown link checker 當成真實檔案的表示法，並由檢查器拒絕範例假斷鏈。

## Alternatives Considered

- 全面採納三份 review 的所有建議：拒絕；英文版、VERSION/CHANGELOG、社群檔案、一行式發布與 FILEMAP 拆分屬產品發展或架構選擇，不是本次可靠性缺陷的共同根因。
- 重排 CURRENT 與 session log 的寫入順序並加入完成旗標：拒絕；現行正式 spec 已採「Direct Memory Source 對最新 log」的語意檢查，能避開時間戳與寫入順序誤判。
- 讓 lint 成為下游 payload 或交接執行期依賴：拒絕；框架核心仍以純 Markdown 運作，Python 檢查器只存在於來源 repo，供安裝與維護 agent 驗收。

## Capabilities

### New Capabilities

- installation-integrity: 定義範本複製、跨平台換行、agent 入口與 hook 實測、以及安裝檢查器的可驗收契約。

### Modified Capabilities

- session-liveness-signals: 讓 context 門檻與 checkpoint 自動化宣稱受外部量測及實測狀態約束。
- handoff-integrity: 讓記憶錨點範例不產生假斷鏈，並把錨點存在性納入可重複的機械驗證。

## Impact

- Affected specs: installation-integrity, session-liveness-signals, handoff-integrity
- Affected code:
  - New: tools/passdown-lint.py, tools/test_passdown_lint.py, .codex/hooks.json
  - Modified: INSTALL.md, GOLDEN_TEMPLATE.md, CONSTITUTION.md, PROTOCOLS.md, DISPATCH.md, entrypoints/README.md, entrypoints/hooks/README.md, entrypoints/hooks/checkpoint-counter.sh, entrypoints/hooks/codex-hooks.json.example, entrypoints/hooks/agy-hooks.json.example, handoff/_template.md, sessions/_template.md, .gitattributes
  - Removed: none
