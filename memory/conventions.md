# Conventions

記錄不屬於 Spectra spec 範圍但影響日常判斷的專案慣例（例如命名規則、工具選擇、風格偏好）。

原則：每條慣例必須有標題，說明慣例本身以及為什麼這樣定，方便之後判斷是否適用。「框架預設」會帶到新專案保留；「專案自訂」帶到新專案會清空並重新累積。

## 框架預設文風與產出慣例（跨專案保留）

- 保持對話風格，不寫客套廢話、廣編稿、教科書或制式報告。
- 若有判斷或推論，交代足以讓人核對的理由；若摘述使用者的話，用原話。
- **Review 報告統一輸出路徑（PDOS-D-20260722-2）**：三個 Agent (codex / cc / agy) 產生任何專案、Task 或 Code Review 報告時，一律統一放置於專案根目錄下的 `review_result/` 資料夾（檔名建議包含日期與主題，如 `YYYY-MM-DD-code-review.md`），方便集中查閱與稽核。
- **框架單一真源：框架碼在母庫、專案資料在 root（PDOS-D-20260722-3）**：安裝後的 `passdown-os/` 混了框架碼與專案資料。**框架碼**（`entrypoints/`、scripts、`CONSTITUTION.md`、`PROTOCOLS.md` 等可重用機制）真源在**母庫**；專案端可熱修救急，但熱修必須 backport 回母庫並 push，否則下一個 install／clone 會重踩同坑。**專案資料**（`handoff/`、`sessions/`、`memory/`、`decisions.md`、`transcripts/`）真源只在專案端、永不上母庫——每 session 寫這些是「用」不是「修」。

## 專案自訂慣例

