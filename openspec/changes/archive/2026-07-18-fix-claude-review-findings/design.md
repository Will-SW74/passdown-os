## Context

目前 Codex Windows hook 把 SessionStart 與 Git Bash 推導寫成兩份 JSON 內的 Python one-liner。這種形式難以單元測試：SessionStart 在計數檔父目錄不存在時會在輸出交接內容前中止；PostToolUse 只接受 Git 位於 `<Git根>/cmd/git.exe` 的單一佈局，遇到 `mingw64/bin/git.exe`、shim 或缺檔會拋例外。另一方面，交接文件把反引號路徑與 Markdown link 都稱為 repo-relative，但 lint 對兩者採不同解析基準；payload lint 也尚未機械執行無 BOM 規則。

本 change 以 Claude Code 的 fresh Windows review 為輸入，保留現有 hooks 與 lint 的 fail-open、零外部依賴方向，並補上可以在 CI 或本機重現的邊界測試。

## Goals / Non-Goals

**Goals:**

- 讓 Codex Windows SessionStart 與 PostToolUse 的行為可由 Python 單元測試覆蓋，且環境缺件時不產生未處理例外。
- 讓文件中的記憶錨點基準與 lint 實際解析方式一致。
- 讓訊號 B 只比較真正的 session log，不把索引或模板當成最新紀錄。
- 讓 payload lint 機械拒絕 UTF-8 BOM，同時允許 inline code 內的示例型角括號字串。
- 誠實記錄 checkpoint counter 在平行 PostToolUse 下可能少算，並固定 JSON 輸出必須可解析。

**Non-Goals:**

- 不修改 Codex Stop transcript archiving、task/thread 命名或 snapshot 格式。
- 不把 advisory checkpoint counter 升級成跨程序強鎖，也不承諾平行呼叫下精確計數。
- 不變更已由 `34bc559` 明定的來源 repo 與下游 payload 路徑界線。
- 不替換或移除已由 OpenAI 官方 manual 確認的 hooks 文件網址。
- 不在本 change 內把 component-tested lifecycle 狀態升級為 verified。

## Decisions

### Use a testable Windows hook adapter

新增 `entrypoints/hooks/codex-windows-hook.py`，以 `session-start --root <path>` 與 `checkpoint --root <path>` 兩個子命令取代兩份 hook JSON 裡不可測的 Python one-liner。來源 repo 傳入 `.`，下游範本傳入 `passdown-os`；POSIX hook 命令維持原狀。相較於繼續複製長 one-liner，獨立 adapter 可共享兩種佈局、提供函式級測試，且隨既有 `entrypoints/hooks/` payload 一起部署。

### Preserve fail-open hook semantics

`session-start` 對 `.toolcount` 的重置採 best-effort：重置失敗要輸出警告，但仍繼續讀取並輸出 CURRENT.md；CURRENT.md 不存在或不可讀時輸出既有警告語意，程序不得以未處理例外終止。`checkpoint` 先接受 PATH 上可執行的 `sh`，再從 `git.exe` 的祖先目錄依序探測 `bin/sh.exe` 與 `usr/bin/sh.exe`；所有候選都不存在時靜默 exit 0。這保留「hook 不打斷主要工作」原則，同時避免把配置錯誤偽裝成成功注入。

### Separate path bases by representation

Direct Memory Source 的反引號路徑維持以 Passdown OS 根目錄解析；Markdown link 明定以包含該 link 的 Markdown 檔父目錄解析。PROTOCOLS 的 Code Symbol Anchor 範例必須以 `handoff/CURRENT.md` 實際所在位置示範，並保留 symbol name，不再使用會解析到錯誤位置的裸 `src/...` 範例。

訊號 B 的候選集合只接受 `sessions/YYYY-MM-DD-HHmm-<agent>-<slug>.md`，且排除 `sessions/archive/`。`INDEX.md`、`_template.md`、dotfiles 與其他 Markdown 不參與 newest-log 判定。

### Validate managed text bytes before semantic lint

`passdown-lint` 在語意檢查前讀取受管文字檔 bytes；只要開頭是 UTF-8 BOM 就回報穩定錯誤碼 `UTF8_BOM`。掃描範圍涵蓋 lint 已處理的 Markdown、hook JSON、shell 與 Python payload，並沿用現有排除目錄，避免掃描 transcripts、imports、archive 與工具快取。placeholder 檢查先移除 HTML comments 與單行 inline code spans，再尋找剩餘角括號佔位符；真正留在一般文字中的 placeholder 仍然失敗。

INSTALL 的 Windows 寫檔紀律改為區分 PowerShell 7 的 `utf8NoBOM` 與 Windows PowerShell 5.1 的 `System.Text.UTF8Encoding(false)` 寫法，不再宣稱 5.1 的 `-Encoding utf8` 會產生無 BOM。

### Keep checkpoint counting advisory under concurrency

保留現有 read-increment-write 計數器，不導入鎖檔或平台專屬同步原語。README、PROTOCOLS 或對應 spec 必須明定平行 PostToolUse 可能互相覆寫，因此 checkpoint 是 advisory 而非精確 telemetry。`--json` 模式的固定輸出合約由測試使用 JSON parser 驗證；提醒文字若日後加入雙引號或反斜線，實作必須同步加入 escaping 或讓測試失敗，不能只靠人工注意。

## Implementation Contract

- **Windows hook interface:** `codex-windows-hook.py` 接受子命令 `session-start` 或 `checkpoint`，以及必填 `--root`。未知子命令或缺少參數由 argparse 回傳非零；已進入合法子命令後的環境缺檔、重置失敗與 shell 缺失遵守 fail-open 規則。
- **SessionStart observable behavior:** 即使 `<root>/sessions/.toolcount` 無法建立或覆寫，stdout 仍包含 CURRENT.md 內容；若 CURRENT.md 無法取得，stdout 仍包含明確警告。可恢復的檔案系統錯誤不得產生 Python traceback。
- **PostToolUse observable behavior:** PATH 上的有效 `sh` 優先；否則 adapter 從有效 `git.exe` 祖先探測 `bin/sh.exe`、`usr/bin/sh.exe`。找不到 shell 時不呼叫 subprocess 並回傳 0；找到後把 `<root>/entrypoints/hooks/checkpoint-counter.sh --json` 原樣交給 shell。
- **Lint output:** 任一受管文字檔以 `EF BB BF` 開頭時，lint 回報 `UTF8_BOM` 與 repo-relative path；inline code 中的 `<repo>` 不產生 `PLACEHOLDER_REMAINS`，一般文字中的 `<repo>` 仍產生該錯誤。
- **Handoff semantics:** 訊號 B 只比較符合 session log 命名格式的候選；Direct Memory Source 反引號與 Markdown link 各依其公開基準解析。
- **Checkpoint contract:** `checkpoint-counter.sh --json` 在第 10、20 等門檻輸出可由標準 JSON parser 解析、event name 為 `PostToolUse` 且 additionalContext 非空的物件；平行呼叫精確性不在保證範圍。
- **Acceptance criteria:** `python tools/test_codex_windows_hooks.py`、`python tools/test_passdown_lint.py`、`python tools/passdown-lint.py --root .`、hook JSON parse、`spectra validate fix-claude-review-findings` 與 `spectra analyze fix-claude-review-findings --json` 全部通過；analyze 不得留下 Critical 或 Warning。
- **Scope boundary:** 實作只改 proposal Impact 列出的 hooks、協定文件、lint 與測試；不得順手調整 transcript archiver、其他 agent 的 lifecycle 狀態或已驗證的官方文件連結。

## Risks / Trade-offs

- [Windows shell 探測仍可能遇到未知封裝佈局] → 先信任 PATH 上的有效 `sh`，再掃描 git 祖先中的兩個官方常見位置；無法證明時 fail-open 並保留 INSTALL 硬門檻。
- [新增 Python adapter 增加一個 payload 檔案] → Python 已是 Codex transcript hook 的既有前置條件，且 adapter 集中取代兩份重複 one-liner。
- [廣泛 BOM 掃描可能碰到非文字資產] → 僅掃描明列的受管文字副檔名並沿用 lint 排除目錄。
- [忽略 inline code 可能讓刻意放在反引號中的未填 placeholder 通過] → 這是接受的取捨；反引號內容視為 literal 示例，真正需要替換的欄位必須存在一般文字。
- [checkpoint 在高並行環境仍可能少算] → 明確降格為 advisory，避免以複雜跨平台鎖換取不必要的精確 telemetry。

## Migration Plan

1. 新增 adapter 與測試，再切換來源 repo 及下游 hook JSON 的 Windows 命令。
2. 更新 lint 與其回歸測試，確認現有 payload 沒有 BOM。
3. 更新 CONSTITUTION、PROTOCOLS、INSTALL 與 hooks README，讓規範、限制與實作一致。
4. 執行完整驗證；若 Windows adapter 造成回歸，可回復 hook JSON 與新增 adapter，不影響 POSIX hooks 或 transcript Stop hook。

## Open Questions

無；實作界線與降級行為已由本設計固定。
