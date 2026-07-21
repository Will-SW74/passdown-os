# 交接與發布檢查清單 (Handoff & Release Checklist)
<!-- gpt review 修正：建立硬性的發布/交接檢查清單，確保不會遺漏關鍵步驟 -->

> **本檔是 `CONSTITUTION.md` 第 6 節「Session 結束協定」的衍生核對清單**——步驟細節與兩者不一致時，以 CONSTITUTION.md 為準。這裡只列「打勾用」的濃縮版。

這是一份硬性規定 (Hard Checklist)，確保每一次交接都不會遺漏關鍵步驟。

## Session 結束/交接前檢查 (Handoff Checklist)
在結束對話前，請確實逐一核對：
- [ ] **CURRENT.md 已更新**：是否已反映最新進度，且 `Next concrete step` 不是空話？
- [ ] **Session Log 已建立**：是否已在 `sessions/` 寫入一份以時間戳與 agent 為檔名的日誌？
- [ ] **失敗嘗試已回寫（天條）**：本次所有失敗的嘗試與死路是否已記進 log 的 Failed attempts 欄位？（正本：CONSTITUTION 第 6 節第 3 步）
- [ ] **INDEX 已考慮**：本次若有長期參考價值（重大決策/架構變動/複雜 debug），是否已在 `sessions/INDEX.md` 補一行？（日常瑣事不必）
- [ ] **Context Index 已精確指定**：`CURRENT.md` 中是否有提供指向相關 session log 或代碼行號的精確錨點？
- [ ] **本機記憶已同步**：是否已將自己工具內的私有記憶重點回寫到 `passdown-os` 中，且每條都附了 agent 代號與時間戳？
- [ ] **逐字稿已歸檔**：若專案啟用了 `transcripts/`，是否已**實際確認** `transcripts/` 出現本次 session 的檔案？**判準是 hook 有沒有生效，不是用哪個 agent**——沒出現就一律手動複製並以與 log 相同的前綴命名，不因「我是 cc、我應該有 hook」而略過。（正本：PROTOCOLS「逐字稿歸檔」）
- [ ] **決策已紀錄**：本次有任何影響架構或約定俗成的決策，是否已寫入 `memory/decisions.md`？
- [ ] **Read-back 驗證**：是否已重新讀取自己剛寫下的交接檔案，並確認格式與內容都正確無誤？
- [ ] **摘牌簽退**：以上全部完成後，是否已刪除 `sessions/.active_lock`？（這是「正常收尾」的實體訊號，必須是最後一步）

## 發布前檢查 (Release Checklist)
如果是完成了一個 Milestone 或準備合併回主分支：
- [ ] **已 commit（無條件，非「視情況」）**：本次變更是否已 commit？沒有變更時 commit 為 no-op，仍要跑過這一步而不是事前判斷「值不值得」。（正本：CONSTITUTION 第 6 節第 8 步）**push 由使用者決定，未經指示不要 push。**
- [ ] **Commit 安全檢查已過**：staged files 無 `*.raw`／`*.sqlite`／`*.db` 原始記憶檔、無**位置不對的** `*.jsonl`、無 API key／token／密碼？（採逐字稿模式 B 的專案，`transcripts/*.jsonl` 允許 staged，但需先跑憑證掃描；其他位置的 `.jsonl` 一律禁止。正本：PROTOCOLS「Git Commit 與分支策略」第 3 條）
- [ ] **分支判準已確認**：本次工作若涉及「已有可運作基線之後的實作」或「結論可能作廢的探索（spike／PoC）」，是否在獨立 Feature Branch 上？若是，所有 AI 碎屑 Commit 是否都將以 Squash 合併？（尚無實作程式碼的基線建立可直接在 main——正本：PROTOCOLS 分支隔離）
- [ ] **Memory 檔案輪替**：檢查 `memory/decisions.md` 等檔案是否超過 30 條或 400 行，需要進行歸檔？
- [ ] **專案 Manifest 更新**：`PROJECT_MANIFEST.md` 的版本號與當前狀態是否需要更新？
