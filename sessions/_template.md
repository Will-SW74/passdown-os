# Session: YYYY-MM-DD HH:mm (<agent: codex|cc|agy>)
<!-- 檔名與此處的日期時間一律填 session「開始」時間，不是寫檔時間 -->

## Started from

- Active change: <openspec/changes/<slug>/ 或「無」>
- Task resumed: <tasks.md 中的哪一項，或「新開始的工作」>
- Context resumed: <例如 sessions/YYYY-MM-DD-HHmm-cc-slug.md，或是「新開始，無前次紀錄」>

## What happened

- <做了什麼，條列>

## Failed attempts（不要重複的死路）

- <本次試過但失敗的做法：試了什麼、為什麼不行（錯誤訊息／原因）。不論最終有沒有成功繞過都要記——下一個接手者看了就不會重跑。沒有則寫「無」>

## Decisions made

- <以決策 ID 引用 memory/decisions.md 對應條目，例如「D-20260712-2 — 復原偵測改語意檢查」；沒有則寫「無」>

## Files touched

- <變更到的檔案路徑，建議使用 markdown link 指向檔案>

## Next step

- <交給下一個接手者的具體下一步>
- Context Anchors for next agent:
  - **Direct Memory Source**: <本 session 檔案名稱，或指示下一個 agent 接班必讀的 session 紀錄>
  - **Code Symbol Anchor**: <例如 [parseHeader](src/parser.js#L42-L55)；一律 repo 相對路徑（不可用 file:/// 絕對路徑，跨機必斷）；行號會漂移，必須同時給符號名>

## Scratchpad (Mental Model / Unfinished Thoughts)

> [!NOTE]
> 如果本次對話已經快消耗完 Context Window 預算（或已達到實用限制，準備開新對話接力），請在此處詳細記錄當前尚未寫進代碼的點子、邏輯細節、猜想、或是下一步除錯思路。若沒有跨 session 接力需求，此處可寫「無」或留空。

- <在此處寫下你腦海中的細部邏輯，防止在重啟對話時丟失 Context 記憶>

## Transcript（選填）

- <若專案啟用 transcripts/ 歸檔：本次逐字稿檔名，例如 transcripts/YYYY-MM-DD-HHmm-cc-xxxxxxxx.jsonl；未啟用或尚未歸檔則寫「無」>

## Blockers / open questions

- <none | 具體描述>
