# Session: 2026-07-17 12:40 (codex)

## Started from

- Active change: `openspec/changes/close-consolidated-review-gaps/`
- Task resumed: 修正 Python lint 與純 Markdown payload 的邊界，說明 Codex hooks
- Context resumed: `sessions/2026-07-16-1327-codex-close-review-gaps.md`

## What happened

- 確認原實作把 `tools/` 列入下游 payload，與純 Markdown 核心定位衝突。
- 保留 Git／Python 安裝硬門檻，但改由安裝 agent 從來源 repo 執行 lint，目標不攜帶 tools/，日常交接不執行 Python。
- 調整 lint fixture，證明完全沒有 tools/ 的目標仍可通過；7 個正反案例測試通過。
- 保留 Codex SessionStart 與 PostToolUse hooks 作為選配 adapter，並依官方 trust 與 developer-context 契約說明用途。

## Failed attempts（不要重複的死路）

- 首次整合驗證命令使用 Bash 的 `{proposal.md,design.md,tasks.md}` 展開語法，PowerShell parser 直接拒絕且未執行任何測試；改成明確列出路徑後通過。
- Spectra analyze 初次因 task 未逐字引用 design topic「來源端 passdown-lint 命令契約」產生一個 Warning；已同步 task 名稱。

## Decisions made

- D-20260717-1 — Python lint 留在來源端，不進入純 Markdown payload。

## Files touched

- [README.md](../README.md)、[INSTALL.md](../INSTALL.md)、[GOLDEN_TEMPLATE.md](../GOLDEN_TEMPLATE.md)、[CONSTITUTION.md](../CONSTITUTION.md)
- [passdown-lint.py](../tools/passdown-lint.py)、[test_passdown_lint.py](../tools/test_passdown_lint.py)
- [Spectra change](../openspec/changes/close-consolidated-review-gaps/proposal.md)
- [decisions.md](../memory/decisions.md)、[CURRENT.md](../handoff/CURRENT.md)、[INDEX.md](./INDEX.md)

## Next step

- 在 fresh Codex task 執行 `/hooks`，trust `.codex/hooks.json`，驗證 SessionStart 與第 10 次 PostToolUse 是否真的進入 developer context，再 archive change。
- Context Anchors for next agent:
  - **Direct Memory Source**: `sessions/2026-07-17-1240-codex-restore-markdown-payload.md`
  - **Code Symbol Anchor**: [passdown-lint.py](../tools/passdown-lint.py) 的 `REQUIRED_PATHS`；[Codex hooks](../.codex/hooks.json) 的 `SessionStart` 與 `PostToolUse`

## Scratchpad (Mental Model / Unfinished Thoughts)

- lint 與 hook 是兩個獨立工具：lint 只驗收安裝，hook 才在 lifecycle 自動執行。

## Transcript（選填）

- 無

## Blockers / open questions

- Codex hooks 的模型可見性仍需 fresh task 與 `/hooks` trust 實測。
