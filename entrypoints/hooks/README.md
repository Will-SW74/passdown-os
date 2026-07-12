# hooks — 三大 agent 的機制化防線（選用但強烈建議）

本資料夾提供 cc / codex / agy 三者的 hook 範本，涵蓋兩種機制：
1. **SessionStart 自動注入**：session 一開就把 `CURRENT.md` 塞進 context——agent 忘不忘記讀，交接內容都在眼前。
2. **PostToolUse 檢查點計數器**（[`checkpoint-counter.sh`](checkpoint-counter.sh)）：由外部腳本數工具呼叫次數，每滿 10 次注入存檔提醒——把 `PROTOCOLS.md`「持續存檔機制」從紀律變成機制（模型自數不可靠，外部計數才可靠）。

| Agent | 設定位置 | 範本 |
| --- | --- | --- |
| cc | `.claude/settings.json` | [`settings.json.example`](settings.json.example)（SessionStart） |
| codex | `.codex/hooks.json` | [`codex-hooks.json.example`](codex-hooks.json.example)（SessionStart + 計數器） |
| agy | `.agents/hooks.json` | [`agy-hooks.json.example`](agy-hooks.json.example)（PreInvocation + 計數器） |

## cc 的 SessionStart 自動注入

把「靠 agent 自覺讀 CURRENT.md」變成「機制保證一定讀到」：cc 的 SessionStart hook 會在每次新 session（含 `/clear` 與 compact 後）自動把 `passdown-os/handoff/CURRENT.md` 全文注入 context 開頭。agent 忘不忘記執行開始協定，交接內容都已經在它眼前——這是本框架「協定紀律」的第一道機制化防線。

## 安裝

1. 打開（或建立）新專案的 `.claude/settings.json`。
2. 把 [`settings.json.example`](settings.json.example) 的 `hooks` 區塊合併進去（已有其他 hooks 就把 `SessionStart` 陣列項目加進既有結構）。
3. 開一個新的 cc session 驗證：開場問一句「你的 context 裡有沒有 SessionStart hook 注入的交接內容？」——能引用 CURRENT.md 內容即成功。

設定檔屬於專案層級（`.claude/settings.json` 可進版控，全隊共用）；只想自己用就放 `.claude/settings.local.json`。

## 平台注意事項

- hook command 是 POSIX shell 語法。**Windows 上 cc 預設用 Git Bash 執行 hook**（cc 本身就建議裝 Git Bash），沒有 Git Bash 時會降級到 PowerShell——屆時上面的 `$CLAUDE_PROJECT_DIR`／`cat ... 2>/dev/null` 語法會失效。若你的環境確定沒有 Git Bash，改用：

```json
{
  "type": "command",
  "shell": "powershell",
  "command": "Write-Output '=== passdown-os 交接內容（SessionStart hook 自動注入）==='; Get-Content \"$env:CLAUDE_PROJECT_DIR/passdown-os/handoff/CURRENT.md\" -Encoding UTF8",
  "timeout": 10
}
```

- matcher 刻意不含 `resume`：恢復的 session 已保有原 context，重複注入只是浪費 token。

## PreCompact hook（壓縮前的最後防線，2026-07-12 加入）

`settings.json.example` 另含一個 `PreCompact` hook：在 cc 執行 compact（手動 `/compact` 或自動觸發）**之前**輸出提醒，機制化 CONSTITUTION 第 3 節「準備壓縮前必須先完成記憶同步」的規則——這正好補上「模型自估 context 百分比不可靠」的缺口。**【待實測】**PreCompact 的 stdout 是否注入模型 context（或僅顯示於 transcript）尚未在新 session 驗證；實測後請更新本段。

## 為什麼沒有做「Session 結束提醒」hook

查證過官方 hooks 文件後的結論：`Stop` hook 是**每個回合**Claude 停止回應時都觸發，不是「session 結束」才觸發——拿來提醒結束協定會變成每回合騷擾一次；`SessionEnd` hook 則只能做清理、無法把提醒送回對話。所以結束協定目前仍靠 CLAUDE.md 入口段落的強制性條文 + 使用者口頭觸發（例如說「收工」）。若之後 cc 提供更合適的觸發點，再補進來。

## codex 與 agy 的等效機制（2026-07-12 查證）

兩者現在**都有** lifecycle hooks，不再只能靠紀律：

- **codex（OpenAI Codex CLI）**：支援 `hooks.json`（`~/.codex/` 全域或 `<repo>/.codex/` 專案層）或 `config.toml` 內的 `[hooks]` 表。事件含 `SessionStart`（startup/resume/clear）、`UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`Stop` 等。**SessionStart 的 stdout 會作為 developer context 注入模型**——等效於 cc 的注入機制。注意：非受管 hook 首次執行前需要在 codex 內信任（trust），hook 內容變更後要重新信任。範本：[`codex-hooks.json.example`](codex-hooks.json.example)。
- **agy（Google Antigravity）**：支援 JSON hooks（`<專案>/.agents/hooks.json` 或 `~/.gemini/antigravity-cli/hooks.json`）。事件含 `PreInvocation`、`PostInvocation`、`PreToolUse`、`PostToolUse`、`Stop`；hook 輸出可經 `additionalContext` 併入 agent prompt。**【未確認】**PreInvocation 純文字 stdout 是否等同注入——安裝時請實測（開新對話問 agent 有沒有看到 CURRENT.md 內容），並把結果更新回本 README。範本：[`agy-hooks.json.example`](agy-hooks.json.example)。

### 計數器 hook 的注入細節（安裝時務必驗證）

`checkpoint-counter.sh` 用純文字 stdout 輸出提醒。各工具對 PostToolUse stdout 的處理不同：
- **cc**：PostToolUse 的純文字 stdout 預設只進 transcript、不注入模型；要注入需改用 JSON 輸出 `{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"..."}}`（以官方 hooks 文件為準）。
- **codex**：官方文件記載 PostToolUse 支援 `additionalContext` 注入。
- **agy**：依 `applyHookOutputToInput` 機制併入，實測為準。

驗證方法都一樣：裝好後跑 10+ 次工具呼叫，問 agent「你有沒有看到 checkpoint 提醒？」——看得到才算裝成功。

資料來源：[Codex hooks 官方文件](https://developers.openai.com/codex/hooks)、[Codex CLI hooks 完整指南](https://codex.danielvaughan.com/2026/04/15/codex-cli-hooks-complete-guide-events-policy-patterns/)、[Antigravity CLI agent hooks 開發者指南](https://medium.com/google-cloud/a-developers-guide-to-agent-hooks-in-antigravity-cli-4c1440febd11)。
