## 1. Codex Windows Hook Adapter

- [x] 1.1 依「Use a testable Windows hook adapter」與「Preserve fail-open hook semantics」實作 `entrypoints/hooks/codex-windows-hook.py` 的 `session-start --root`，交付 **Windows SessionStart remains observable during recoverable filesystem failures**：計數器重置失敗或 CURRENT.md 缺失時仍輸出內容或明確警告且無 traceback；以 `python tools/test_codex_windows_hooks.py` 的成功、重置失敗及缺檔案例驗證。
- [x] 1.2 完成 adapter 的 `checkpoint --root` shell 探測，交付 **Windows PostToolUse locates Git Bash without assuming one git.exe layout**：依序接受 PATH `sh`、Git 祖先的 `bin/sh.exe`、`usr/bin/sh.exe`，shim 無候選時 exit 0；以 `python tools/test_codex_windows_hooks.py` 的 PATH、cmd、mingw64 與 shim 案例驗證 subprocess 參數及 exit code。
- [x] 1.3 更新 `.codex/hooks.json` 與 `entrypoints/hooks/codex-hooks.json.example`，交付 **Source and downstream Codex hook layouts use the same adapter contract**：來源使用 root `.`、下游使用 root `passdown-os`，POSIX 與 Stop 命令不變；以 Python JSON parse、命令欄位 assertions 與 `git diff` 人工核對驗證。

## 2. Payload Integrity Linting

- [x] 2.1 依「Validate managed text bytes before semantic lint」在 `tools/passdown-lint.py` 加入受管文字 bytes 掃描，交付 **Managed payload text is UTF-8 without BOM**：BOM 回報 `UTF8_BOM`、排除目錄不掃描、正常 UTF-8 不報錯；以 `python tools/test_passdown_lint.py` 的 shell、Markdown、excluded transcript 與 clean payload fixtures 驗證。
- [x] 2.2 在 placeholder 掃描前移除 HTML comments 與單行 inline code，交付 **Literal inline code does not trigger placeholder errors**：inline `<repo>` 通過、一般文字 `<next-step>` 仍回報 `PLACEHOLDER_REMAINS`；以 `python tools/test_passdown_lint.py` 的正反案例驗證。
- [x] 2.3 修正 `INSTALL.md` 的 Windows 寫檔紀律，交付 **Windows writing guidance produces UTF-8 without BOM**：PowerShell 7 使用 `utf8NoBOM`、Windows PowerShell 5.1 使用 `System.Text.UTF8Encoding(false)`，且不再宣稱 `-Encoding utf8` 無 BOM；以文件內容 assertion 與實際產出 bytes 不含 `EF BB BF` 的測試命令驗證。

## 3. Handoff Semantics

- [x] 3.1 依「Separate path bases by representation」更新 `PROTOCOLS.md`，交付 **Portable memory anchors**：Direct Memory Source 明定 Passdown-root-relative，Markdown link 明定 source-file-relative，來源與下游範例皆能解析且命名 symbol；以 `python tools/passdown-lint.py --root .` 與範例 target 路徑人工核對驗證。
- [x] 3.2 更新 `CONSTITUTION.md` 的訊號 B，交付 **Semantic handoff integrity check**：候選只含 `sessions/YYYY-MM-DD-HHmm-<agent>-<slug>.md`，明確排除 INDEX、template、archive 與其他 Markdown；以文件情境表核對 INDEX/template mtime 不影響 newest-log 選擇，並執行 `spectra analyze fix-claude-review-findings --json` 驗證規範一致性。

## 4. Advisory Checkpoint Contract

- [x] 4.1 依「Keep checkpoint counting advisory under concurrency」更新 `entrypoints/hooks/README.md`、`PROTOCOLS.md` 與必要的 `entrypoints/hooks/checkpoint-counter.sh` 註解或 encoding，交付 **Externally counted checkpoint reminders**：文件不宣稱平行精確計數，`--json` 在 10/20 可解析且非門檻無 stdout；以 `python tools/test_codex_windows_hooks.py` 執行 9/10/11/20、corrupt counter、JSON quote/backslash 安全案例驗證。

## 5. 整體驗證

- [x] 5.1 執行 `python tools/test_codex_windows_hooks.py`、`python tools/test_passdown_lint.py`、`python tools/test_codex_transcript_archiver.py`、`python tools/passdown-lint.py --root .`、兩份 hook JSON parse 與 scoped `git diff --check`，確認新增 adapter、lint、既有 transcript archiver 與文件均無回歸，任何失敗均在本 change 範圍內修到通過。
- [x] 5.2 執行 `spectra validate fix-claude-review-findings` 與 `spectra analyze fix-claude-review-findings --json`，確認 proposal、design、四份 specs 與 tasks 全部一致且無 Critical／Warning，並人工確認沒有修改 transcript archiver、官方 hooks URL或 `34bc559` 的來源／下游路徑界線。
