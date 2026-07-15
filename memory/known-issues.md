# Known Issues

記錄已知的坑、workaround、或「試過但行不通」的做法，避免不同 agent 重複踩同一個雷。

用法：每條一個小標題，說明問題現象、原因（若已知）、目前的 workaround。

### Windows clone 後出現 70+ 個「幻影修改」＋ sh hooks 可能靜默壞掉

**症狀:** 在另一台 Windows 機器 `git clone`／`git pull` 後，還沒動任何檔案，`git status` 就顯示大量 `.agent/`、`.claude/`、`.gemini/`、`.opencode/` 底下的檔案被修改；`git diff` 看實際內容卻是空的。另外 `.sh` hook 腳本若被 checkout 成 CRLF，Git Bash 執行會炸 `$'\r': command not found`，計數器／逐字稿歸檔 hooks 靜默失效。
**原因:** 這批 scaffolding 檔案早期以不一致的換行字元入庫；各機器 `core.autocrlf` 設定不同時，git 在 checkout/diff 時產生純換行差異的假修改。
**Workaround（已根治，2026-07-13 cc）:** repo 已加入 `.gitattributes`（`* text=auto`＋`*.sh text eol=lf`）並執行 `git add --renormalize .` 重新正規化入庫。**若某台舊機器 pull 之後仍看到幻影修改**：跑一次 `git add --renormalize . && git status` 即歸零（或重新 clone 最乾淨）。之後不會再發生。

## 範例格式（可刪除，供參考）

### <問題描述>

**症狀:** <觀察到的現象>
**原因:** <若已知>
**Workaround:** <目前的處理方式>
