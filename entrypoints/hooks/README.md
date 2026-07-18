# hooks — 三大 agent 的機制化防線（選用但強烈建議）

本資料夾提供 cc / codex / agy 三者的 hook 範本，涵蓋三種候選防線：
1. **SessionStart／PreInvocation 交接注入**：session 一開就輸出 `CURRENT.md`；只有完成下方矩陣的真實 context 驗證後，才可稱為機制化注入。
2. **PostToolUse 檢查點計數器**（[`checkpoint-counter.sh`](checkpoint-counter.sh)）：由外部腳本數工具呼叫次數，每滿 10 次輸出存檔提醒。外部計數本身可機械驗證，但提醒是否進入模型 context 必須按 agent 分別實測。
3. **逐字稿歸檔／快照**：cc 用 SessionEnd；Codex 用 turn-scoped `Stop` 呼叫 [`archive-codex-transcript.py`](archive-codex-transcript.py) 持續更新同一 task 的 raw snapshot。Codex 已驗證介面沒有 SessionEnd，不得混稱。

| Agent | 設定位置 | 範本 |
| --- | --- | --- |
| cc | `.claude/settings.json` | [`settings.json.example`](settings.json.example)（SessionStart + 計數器） |
| codex | `.codex/hooks.json` | [`codex-hooks.json.example`](codex-hooks.json.example)（SessionStart + 計數器 + Stop transcript snapshot） |
| agy | `.agents/hooks.json` | [`agy-hooks.json.example`](agy-hooks.json.example)（PreInvocation + 計數器） |

Passdown OS 原始 repo 另有 [`.codex/hooks.json`](../../.codex/hooks.json) 作為本 repo 自己的部署實體，路徑直接指向 `handoff/` 與 `sessions/`；上表的 codex 範本則是給下游專案使用，路徑指向其 `passdown-os/` 子目錄。安裝或更新後，在 fresh Codex task 先用 `/hooks` 檢視來源並信任，再驗證 SessionStart 與第 10 次 PostToolUse 是否真的進入 developer context。

## 驗證狀態矩陣

狀態只有三種：`verified`＝真實 lifecycle event 觸發，且 agent 回應證明內容已進模型 context；`component-tested`＝命令、JSON 或假輸入已通過，但尚未證明真實 event 的模型可見性；`unverified`＝尚無可重現證據。只有 `verified` 可稱為「機制化注入」。

| Agent | Event | 輸出格式 | 預期可見位置 | 狀態 | 驗證日期／證據 |
| --- | --- | --- | --- | --- | --- |
| cc | SessionStart | plain stdout（CURRENT.md 全文） | model context | `verified` | 2026-07，既有 fresh session 實測紀錄 |
| cc | PostToolUse | JSON `hookSpecificOutput.additionalContext` | model context | `component-tested` | 2026-07-12，計數腳本與 JSON component test |
| cc | PreCompact | plain stdout | model context 或 transcript（待確認） | `unverified` | 尚未在 fresh session 觸發 |
| cc | SessionEnd | shell side effect（歸檔逐字稿） | `transcripts/` | `component-tested` | 2026-07-12，假 JSON 與 POSIX 路徑通過；Windows 真實 event 未驗證 |
| codex | SessionStart | plain stdout（CURRENT.md 全文） | developer context | `component-tested` | 2026-07-16，官方介面與命令 component test；fresh Codex task 待驗證 |
| codex | PostToolUse | JSON `hookSpecificOutput.additionalContext` | developer context | `component-tested` | 2026-07-16，官方介面與計數腳本 component test；fresh Codex task 待驗證 |
| codex | Stop | file side effect（持續更新 raw transcript snapshot） | `transcripts/` | `verified` | 2026-07-18，Windows fresh CLI task 經 `/hooks` trust 後產生 68-record snapshot；session id、JSONL parse 與 source byte prefix 均驗證 |
| agy | PreInvocation | JSON `additionalContext` | agent prompt | `verified` | 2026-07-13，agy 真實環境實測紀錄 |
| agy | PostToolUse | plain stdout | agent prompt（待確認） | `unverified` | 尚未證明 `checkpoint-counter.sh` plain output 會注入 |

## cc 的 SessionStart 自動注入

已完成真實 session 驗證的 cc SessionStart hook 會在每次新 session（含 `/clear` 與 compact 後）把 `passdown-os/handoff/CURRENT.md` 全文注入 context 開頭。這個 event 可視為機制化防線；同檔其他 event 仍依上方矩陣各自判定，不因 SessionStart 通過就一起升級。

## 安裝

1. 打開（或建立）新專案的 `.claude/settings.json`。
2. 把 [`settings.json.example`](settings.json.example) 的 `hooks` 區塊合併進去（已有其他 hooks 就把 `SessionStart` 陣列項目加進既有結構）。
3. 開一個新的 cc session 驗證：開場問一句「你的 context 裡有沒有 SessionStart hook 注入的交接內容？」——能引用 CURRENT.md 內容即成功。

設定檔屬於專案層級（`.claude/settings.json` 可進版控，全隊共用）；只想自己用就放 `.claude/settings.local.json`。

## 平台注意事項

- **環境前置是硬性的（D-20260713-1）**：本資料夾所有 hook 都以 POSIX `sh`（Git Bash）執行，agy 注入 hook 另需 `python` 在 PATH 上。這些是 `INSTALL.md` 第 0.1 節的**強制門檻**——缺任一項，安裝程序會直接中止、請使用者裝好再部署。**不提供 PowerShell 或其他降級版本**：多套 shell 版本必然彼此 drift，半套 hooks 又會讓機制化防線靜默失效，兩害取其小就是把要求擋在門口。
- **Codex on Windows**：計數器的 `commandWindows` 不假設裸 `sh` 已在 PATH，而是用 Python 從 `git.exe` 位置推導同一套 Git Bash 的 `bin/sh.exe`；逐字稿 archiver 則直接使用同一份跨平台 Python script。INSTALL 的 Git Bash 與 Python 門檻仍全部適用。
- matcher 刻意不含 `resume`：恢復的 session 已保有原 context，重複注入只是浪費 token。

## SessionEnd hook：逐字稿自動歸檔（2026-07-12 加入）

`settings.json.example` 含一個 `SessionEnd` hook，呼叫 [`archive-transcript.sh`](archive-transcript.sh)：session 結束時自動把當次 cc 逐字稿複製到 `passdown-os/transcripts/`（gitignored 歸檔區，見該資料夾 README）。機制：SessionEnd 的 stdin JSON 帶有 `transcript_path` 與 `session_id`，腳本取出後照 `日期時間-cc-<id前8碼>.jsonl` 命名歸檔。

- **驗證方法**：結束一個 session（或 `/clear`）後檢查 `passdown-os/transcripts/` 是否出現新 `.jsonl`。
- **已實測（2026-07-12）**：無 jq 環境的 sed fallback＋POSIX 路徑，假 JSON 實跑通過（歸檔與命名正確）。**【待實測】**：真實 SessionEnd 觸發時 Windows 雙反斜線路徑（`C:\\Users\\...`）的還原——實測後更新本段。
- agy 仍沒有本範本已驗證的等效自動機制，依 `PROTOCOLS.md`「逐字稿歸檔」小節手動複製。

## Codex Stop hook：逐字稿持續快照（2026-07-18 驗證）

`codex-hooks.json.example` 的 `Stop` hook 會把 hook stdin 原封不動交給 `archive-codex-transcript.py`。Archiver 驗證 event、來源 regular file 與 Passdown cwd markers 後，將來源 opaque bytes 寫進同目錄 temporary file，再原子替換 `passdown-os/transcripts/YYYY-MM-DD-HHmm-codex-<id8>.jsonl`。相同 Codex task 的每個 Stop 都更新同一檔。來源 repo 自用的 `.codex/hooks.json` 指向 root layout；同一 script 只在確認自身位於該 repo 的 `entrypoints/hooks/` 時允許此 layout。

- `Stop` 是每個 assistant turn 結束時觸發，**不是 session 結束**；已驗證的 Codex hooks 介面沒有 SessionEnd。
- 一個 Codex task/thread 對應一份 raw snapshot；resume 會繼續更新同檔。下一次工作若要獨立逐字稿，請開新 Codex task。
- `.jsonl` 是可能包含 credentials、本機路徑、私人對話與專有資料的 gitignored 敏感檔，未清洗前不得 commit、push 或分享。
- 安裝或修改 `.codex/hooks.json`／archiver 後，要在 **fresh Codex task** 執行 `/hooks` review/trust。跑完一個 turn並看到 snapshot 更新，才可把該部署 lifecycle 狀態升為 `verified`；unit test 或假 stdin 只算 `component-tested`。

## PreCompact hook（壓縮前的最後防線，2026-07-12 加入）

`settings.json.example` 另含一個 `PreCompact` hook：在 cc 執行 compact（手動 `/compact` 或自動觸發）**之前**輸出提醒。這是候選防線；目前狀態為 `unverified`，因為 stdout 是否進入模型 context（或僅顯示於 transcript）尚未在 fresh session 證明。未驗證前，CONSTITUTION 的壓縮前同步規則仍靠明文協定執行。

## 為什麼沒有做「Session 結束提醒」hook

查證過官方 hooks 文件後的結論：`Stop` hook 是**每個回合**Claude 停止回應時都觸發，不是「session 結束」才觸發——拿來提醒結束協定會變成每回合騷擾一次；`SessionEnd` hook 則只能做清理、無法把提醒送回對話。所以結束協定目前仍靠 CLAUDE.md 入口段落的強制性條文 + 使用者口頭觸發（例如說「收工」）。若之後 cc 提供更合適的觸發點，再補進來。

## codex 與 agy 的等效機制（2026-07-12 查證）

兩者目前都提供 lifecycle hooks，但「平台支援」不等於「本範本每個 event 已驗證」：

- **codex（OpenAI Codex CLI）**：官方介面支援 `hooks.json`（`~/.codex/` 全域或 `<repo>/.codex/` 專案層）或 `config.toml` 內的 `[hooks]` 表；本機 `codex-cli 0.142.4` 的 `hooks` feature 為 stable。SessionStart plain stdout 依官方契約會成為 developer context，PostToolUse 可用 JSON `additionalContext`。但本範本尚需 fresh Codex task 證明實際可見性，因此矩陣先列 `component-tested`。非受管 hook 首次執行前需在 Codex `/hooks` 信任，內容變更後要重新信任。下游範本：[`codex-hooks.json.example`](codex-hooks.json.example)；本 repo 部署實體：[`.codex/hooks.json`](../../.codex/hooks.json)。
- **agy（Google Antigravity）**：支援 JSON hooks（`<專案>/.agents/hooks.json` 或 `~/.gemini/antigravity-cli/hooks.json`）。事件含 `PreInvocation`、`PostInvocation`、`PreToolUse`、`PostToolUse`、`Stop`；已確認：PreInvocation 必須透過 stdout 輸出 JSON 格式的 `additionalContext` 欄位才能成功併入 agent prompt。因此範本 `agy-hooks.json.example` 已改用 Python 指令將 CURRENT.md 的內容序列化為 JSON 輸出（2026-07-13 實測驗證）。

### 計數器 hook 的注入細節（安裝時務必驗證）

`checkpoint-counter.sh` 支援 plain 與 `--json` 兩種輸出。各工具對 PostToolUse stdout 的處理不同：
- **cc / codex**：範本使用 `--json`，輸出 `{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"..."}}`；component test 通過不代表 lifecycle 注入已驗證。
- **agy**：範本目前使用 plain stdout；模型可見性仍為 `unverified`，不得推定 `applyHookOutputToInput` 一定生效。

計數器採單次 read-increment-write，沒有跨 process 鎖定；平行 PostToolUse 可能讀到同一舊值並互相覆寫。因此數字與每 10 次提醒都只供 checkpoint 提示，不是精確 telemetry。`--json` 在非 checkpoint 次數不輸出 stdout；提醒文字中的雙引號與反斜線會先 escape，component tests 會解析 9、10、11、20 與特殊字元案例。

Codex Windows 的 `codex-windows-hook.py` 先使用 PATH 上的有效 `sh`；找不到時才從有效 `git.exe` 的祖先探測 `bin/sh.exe` 與 `usr/bin/sh.exe`。仍找不到 shell 時會靜默 fail-open，不阻斷 PostToolUse。

驗證方法都一樣：裝好後跑 10+ 次工具呼叫，問 agent「你有沒有看到 checkpoint 提醒？」——看得到才算裝成功。

資料來源：[Codex hooks 官方文件](https://learn.chatgpt.com/docs/hooks)、[Antigravity CLI agent hooks 開發者指南](https://medium.com/google-cloud/a-developers-guide-to-agent-hooks-in-antigravity-cli-4c1440febd11)。
