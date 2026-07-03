# hooks — cc 的 SessionStart 自動注入（選用）

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

## 為什麼沒有做「Session 結束提醒」hook

查證過官方 hooks 文件後的結論：`Stop` hook 是**每個回合**Claude 停止回應時都觸發，不是「session 結束」才觸發——拿來提醒結束協定會變成每回合騷擾一次；`SessionEnd` hook 則只能做清理、無法把提醒送回對話。所以結束協定目前仍靠 CLAUDE.md 入口段落的強制性條文 + 使用者口頭觸發（例如說「收工」）。若之後 cc 提供更合適的觸發點，再補進來。

## 其他 agent 呢？

本 hook 只覆蓋 cc。codex 與 agy 是否有等效的 session-start 注入機制**未確認**——查證後若有，比照本資料夾格式補一份，並更新本 README。
