## Why

Claude Code 在 Windows fresh clone 的實測指出，現有 Codex hook、交接路徑規則與 payload lint 仍有可重現的韌性缺口。雖然目前 lint 與單元測試皆通過，這些邊界沒有被測試覆蓋，會造成 hook 靜默失效、交接誤判或合法文件被誤報。

## What Changes

- 強化 Codex Windows hook：可靠定位 Git Bash、找不到執行環境時靜默退出，且 SessionStart 即使無法重置計數器仍必須輸出 CURRENT.md 或明確警告。
- 明定 Context Index 的兩種路徑基準：Direct Memory Source 的反引號路徑以 Passdown OS 根為基準；Markdown link 以來源 Markdown 檔所在目錄為基準。
- 將訊號 B 的候選檔案限制為符合 session log 命名格式的 Markdown，排除 INDEX.md、_template.md 與其他非 log 文件。
- 擴充 payload lint，檢查 UTF-8 BOM，並在 placeholder 掃描前排除 inline code；同步補齊回歸測試與 Windows 無 BOM 寫檔指引。
- 明文記錄 checkpoint counter 在平行 PostToolUse 下可能少算的 advisory 限制，並以測試固定 JSON 輸出必須可解析的合約。

## Capabilities

### New Capabilities

- `codex-hook-resilience`: Codex Windows SessionStart 與 PostToolUse hook 的執行環境探測、降級行為及可測試合約。
- `payload-integrity-linting`: Passdown OS payload 的 UTF-8 無 BOM 與 placeholder 掃描規則。

### Modified Capabilities

- `handoff-integrity`: 明定記憶錨點路徑基準及訊號 B 的 session log 候選集合。
- `session-liveness-signals`: 明定 checkpoint JSON 輸出合約及平行計數的 advisory 限制。

## Impact

- Affected specs: `codex-hook-resilience`, `payload-integrity-linting`, `handoff-integrity`, `session-liveness-signals`
- Affected code:
  - New: `entrypoints/hooks/codex-windows-hook.py`, `tools/test_codex_windows_hooks.py`
  - Modified: `.codex/hooks.json`, `entrypoints/hooks/codex-hooks.json.example`, `entrypoints/hooks/checkpoint-counter.sh`, `entrypoints/hooks/README.md`, `CONSTITUTION.md`, `PROTOCOLS.md`, `INSTALL.md`, `tools/passdown-lint.py`, `tools/test_passdown_lint.py`
  - Removed: none
- No external API or dependency change; Python remains an existing Codex installation prerequisite.
