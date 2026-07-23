---
description: 執行 Passdown OS 的 Session 結束協定（交接存檔＋read-back 驗證）
---

現在執行 `passdown-os/CONSTITUTION.md` 的「Session 結束協定」，九個步驟一步不漏（可搭配 `passdown-os/CHECKLIST_HANDOFF.md` 核對）：

1. 更新已完成 task 的勾選狀態（`tasks.md` 或專案的 task 管理處）。
2. 覆寫 `passdown-os/handoff/CURRENT.md`（用 `handoff/_template.md` 格式），反映本次 session 結束後的真實狀態；`Next concrete step` 必須具體到下一個接手者不需要再猜。
3. 用 `sessions/_template.md` 新增本次 session log（檔名 `YYYY-MM-DD-HHmm-<agent>-<slug>.md`）；若本次對話快滿或有未寫完的思路，`Scratchpad` 區段要認真寫。本次若有長期參考價值，同時在 `sessions/INDEX.md` 補一行索引。
4. 有影響後續判斷的決策 → 補進 `memory/decisions.md`。
5. 有踩到的坑或 workaround → 補進 `memory/known-issues.md`。
6. 本機記憶同步檢查：本次是否寫入了工具私有記憶（cc auto memory 等）？有 → 依 `PROTOCOLS.md`「本機記憶同步」摘要回寫，每條附 agent 代號與時間戳。
7. Read-back 驗證：重新讀取剛寫的 CURRENT.md 與 session log，確認內容完整、無佔位符、錨點路徑存在。不過就修到過。
8. 視情況 commit（分支紀律見 `PROTOCOLS.md`「Git Commit 與分支策略」）。
9. 摘牌簽退：確認以上完成後，刪除 `sessions/.active_lock`。這是「正常收尾」的實體訊號，必須是最後一步。

全部完成後，回報一份簡短清單：每一步做了什麼或為何不適用（例如「第 4 步：本次無新決策」），不可整段略過不提。
