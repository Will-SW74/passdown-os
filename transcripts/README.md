# transcripts/ — 逐字稿本機歸檔區（gitignored）

本資料夾存放各 agent 工具的**原始對話逐字稿**，是記憶體系的最後一層考古材料。

## 定位（先讀懂這三點）

1. **不入版控**：本資料夾內容（README 與 .gitkeep 除外）已被 `.gitignore` 排除——這與 PROTOCOLS「Commit 前安全檢查」的 `*.jsonl` 禁令一致。逐字稿可能包含 credentials、API key、本機路徑、私人對話與專有資料；未清洗的快照**絕不能 commit、push 或分享**。
2. **可攜靠資料夾同步**：git clone 不會帶到這裡的內容；要跨機帶走，用雲端硬碟／USB 同步整個專案資料夾。
3. **只是考古材料，不是記憶正本**：日常交接靠 `sessions/*.md` 提煉版 log（那才 100% 在 repo 裡）。逐字稿只在「提煉版看不出當初脈絡」的極少數情況才需要回翻；要把逐字稿內容提煉進正式記憶，仍然走 `imports/` 清洗流程（去敏感化＋記 redaction-log）。

## 命名約定

`YYYY-MM-DD-HHmm-<agent>-<識別>.jsonl`

- 日期時間＝工具 task/session 的開始時間；Codex 由 rollout 名稱推導，不可解析時使用來源建立時間。
- `<識別>`：cc 與 Codex 自動歸檔通常用 session id 前 8 碼；不安全或缺少時用來源 basename hash 前 8 碼。

## 怎麼歸檔

- **cc（自動）**：安裝 `entrypoints/hooks/` 的 SessionEnd hook（`archive-transcript.sh`），session 結束時自動複製當次逐字稿到這裡。
- **codex（持續快照）**：安裝 `.codex/hooks.json` 的 `Stop` hook；每個 assistant turn 結束時由 `archive-codex-transcript.py` 原子更新同一 task 的快照。`Stop` 是 turn-scoped，**不是 SessionEnd**；目前已驗證的 Codex 介面沒有 SessionEnd event。
- **agy（手動）**：執行結束協定時，從 `~/.gemini/antigravity-cli/brain/<conversation-id>/...` 複製當次逐字稿並依命名約定改名。

## Codex task 與 Passdown session 的邊界

一個 Codex task/thread 固定對應一份 raw transcript snapshot。Resume 同一 task 會繼續更新同一檔；若下一次 Passdown 工作需要獨立 raw transcript，請開新的 Codex task，並在新 task 重新確認 `/hooks` 信任。Markdown `sessions/*.md` 仍是一回工作一份的提煉交接，不受此限制。
