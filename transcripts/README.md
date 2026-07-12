# transcripts/ — 逐字稿本機歸檔區（gitignored）

本資料夾存放各 agent 工具的**原始對話逐字稿**，是記憶體系的最後一層考古材料。

## 定位（先讀懂這三點）

1. **不入版控**：本資料夾內容（README 與 .gitkeep 除外）已被 `.gitignore` 排除——這與 PROTOCOLS「Commit 前安全檢查」的 `*.jsonl` 禁令一致。逐字稿含未清洗的敏感資訊（API key、路徑、私人對話），**絕不能**推上 git。
2. **可攜靠資料夾同步**：git clone 不會帶到這裡的內容；要跨機帶走，用雲端硬碟／USB 同步整個專案資料夾。
3. **只是考古材料，不是記憶正本**：日常交接靠 `sessions/*.md` 提煉版 log（那才 100% 在 repo 裡）。逐字稿只在「提煉版看不出當初脈絡」的極少數情況才需要回翻；要把逐字稿內容提煉進正式記憶，仍然走 `imports/` 清洗流程（去敏感化＋記 redaction-log）。

## 命名約定

`YYYY-MM-DD-HHmm-<agent>-<識別>.jsonl`

- 日期時間＝session 開始時間，與 `sessions/` log 檔名同前綴——**兩邊按時間排序即可一一對應**（這就是逐字稿的 index）。
- `<識別>`：cc 自動歸檔用 session id 前 8 碼；手動歸檔建議直接用該次 session log 的 slug。

## 怎麼歸檔

- **cc（自動）**：安裝 `entrypoints/hooks/` 的 SessionEnd hook（`archive-transcript.sh`），session 結束時自動複製當次逐字稿到這裡。
- **codex / agy（手動）**：執行結束協定「本機記憶同步」步驟時，順手從 `PROTOCOLS.md` 造冊的本機路徑（codex：`~/.codex/sessions/`；agy：`~/.gemini/antigravity-cli/brain/<conversation-id>/...`）複製當次逐字稿過來，照命名約定改名。
