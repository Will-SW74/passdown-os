# transcripts/ — 逐字稿歸檔區

本資料夾存放各 agent 工具的**原始對話逐字稿**，是記憶體系的最後一層考古材料。

## 兩種模式：導入時擇一，不要放著不決定（PDOS-D-20260721-2）

逐字稿要不要進版控，取決於**專案的威脅模型與跨機方式**，沒有一體適用的答案。導入框架時就決定，並把決定寫進 `memory/decisions.md`——因為兩者的切換成本不對稱（見下方警告）。

| | **模式 A：排除（預設）** | **模式 B：追蹤** |
| --- | --- | --- |
| `.gitignore` | 保留 `transcripts/*` 排除規則 | 移除該排除規則 |
| 跨機可攜 | 靠雲端硬碟／USB 同步整個專案資料夾 | **`git clone` / `git pull` 即帶走** |
| 適用 | repo 可能公開、有外部協作者、或含法遵敏感內容 | **私有 repo、單人或小型信任團隊、跨機靠 git** |
| 風險 | 低 | 逐字稿內容進入 git 歷史，且**難以事後移除** |

### 怎麼選

**選模式 B 的條件（全部成立才行）**：

1. repo 是 **private**，且可預見的未來不會轉公開。
2. 跨機／接力**靠 git**，不靠資料夾同步——這是模式 A 的可攜假設，不成立的話逐字稿實質上永遠不會離開原機器，「回頭查哪個環節出包」在別台機器上就無解。
3. 願意在**每次** commit 新增 `.jsonl` 前跑憑證掃描（下方指令）。

**任一條不成立就用模式 A。** 特別注意第 1 點是「可預見的未來」不是「現在」——見下方警告。

> ### ⚠ 切換成本不對稱，這是選擇時最容易低估的一點
>
> **A → B 很容易**（改 `.gitignore` 就好）；**B → A 補救不了**。
>
> 事後改回 `.gitignore` 只會停止**新增**，已經進入 git 歷史的逐字稿仍在，任何有 repo 存取權的人都拿得到。真要移除必須 `git filter-repo` 或 BFG **重寫歷史**，然後所有既有 clone 都得重新拉。
>
> **所以真正的紅線是：repo 轉公開之前，先處理歷史。** 不是「轉公開時改一下 .gitignore」。

### 模式 B 的設定

1. **移除排除規則**：把 `.gitignore` 裡的 `transcripts/*`（含 `!transcripts/README.md`、`!transcripts/.gitkeep` 兩行負向規則）拿掉。
2. **保住位元組保真**：在 repo 根目錄 `.gitattributes` 加一行——

   ```gitattributes
   # 逐字稿是考古材料，autocrlf 會在 checkout 時改寫位元組
   *.jsonl -text
   ```

   沒這行的話，Windows 上 `core.autocrlf` 會把 LF 換成 CRLF，歸檔內容在 checkout 時就被改掉了，考古保真度直接失效。
3. **每次 commit 新增 `.jsonl` 前掃描**，命中即停、改走 `imports/` 清洗流程：

   ```bash
   grep -ohE "sk-ant-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----" transcripts/*.jsonl
   ```

   **誠實聲明**：這是樣式比對，只能抓已知格式的憑證，**不保證抓得到全部**——自訂格式的 token、貼在對話裡的密碼、內部系統的識別碼都可能漏網。它降低風險，不消除風險；模式 B 的安全性最終仍建立在「repo 保持私有」這個前提上。
4. **在 `memory/decisions.md` 記一筆**，寫明選了模式 B、成立前提、以及上方的不可逆風險。

### 體積

單一 session 的逐字稿約 0.1–2 MB，`.jsonl` 不易 delta 壓縮。長期高頻使用時 repo 會持續變大；到了不能接受的程度可考慮只保留近 N 次、或改走 Git LFS。

## 不變的定位：只是考古材料，不是記憶正本

**兩種模式都一樣**：日常交接靠 `sessions/*.md` 提煉版 log（那 100% 在 repo 裡）。逐字稿只在「提煉版看不出當初脈絡」的極少數情況才需要回翻；要把逐字稿內容提煉進正式記憶，仍然走 `imports/` 清洗流程（去敏感化＋記 redaction-log）。

**推論**：模式 B 不是「有了逐字稿就可以少寫 log」的藉口。session log 的 `Failed attempts` 欄位（CONSTITUTION 天條）仍然是回答「哪個環節出包」的第一手工具，逐字稿是它的後備而非替代。

## 命名約定

`YYYY-MM-DD-HHmm-<agent>-<識別>.jsonl`

- 日期時間＝session 開始時間，與 `sessions/` log 檔名同前綴——**兩邊按時間排序即可一一對應**（這就是逐字稿的 index）。
- `<識別>`：cc 自動歸檔用 session id 前 8 碼；手動歸檔建議直接用該次 session log 的 slug。

## 怎麼歸檔

歸檔動作**與模式無關**，兩種模式都要做：

- **已裝自動歸檔 hook（目前僅 cc）**：`entrypoints/hooks/archive-transcript.sh` 由 SessionEnd hook 觸發，session 結束時自動複製當次逐字稿到這裡。
- **沒有自動歸檔時（hook 未裝、被移除、或沒生效）**：執行結束協定「本機記憶同步」步驟時手動複製，照命名約定改名。本機路徑見 `PROTOCOLS.md`「逐字稿歸檔」小節（cc：`~/.claude/projects/<專案路徑 hash>/<session-id>.jsonl`；codex：`~/.codex/sessions/`；agy：`~/.gemini/antigravity-cli/brain/<conversation-id>/...`）。

判準是「`transcripts/` 有沒有真的出現本次檔案」，不是「用哪個 agent」（PDOS-D-20260721-1）。
