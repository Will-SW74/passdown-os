# Session 索引 (Session Index)
<!-- gpt review 修正：建立 Session 索引，讓 AI 不必掃描全部 session，只需透過索引與錨點精準閱讀 -->

為了避免 Agent 在需要追溯歷史時掃描整個 `sessions/` 目錄，請在此處維護重要 Session 的索引。
當一個 Session 結束時，如果它包含了對專案有長期價值的決策、重大的架構變動或複雜的 Debug 過程，請在下方加上一行連結與簡介。

## 索引列表

| 日期 | Session 檔案連結 | 主要內容摘要 / 關鍵字 |
| --- | --- | --- |
| 範例 | 2026-07-10-1200-cc-setup-auth.md | 實作 JWT Auth 流程，解決了 token refresh 的 edge case |
| 2026-07-12 | [2026-07-12-1530-cc-wire-hardening-and-startup-rules.md](./2026-07-12-1530-cc-wire-hardening-and-startup-rules.md) | 框架大修全記錄：接線修正、會話鎖閉環、語意檢查、逐字稿歸檔、決策 ID（D-20260712-1～6）、CT 查證 |
| 2026-07-13 | [2026-07-13-0010-agy-resolve-antigravity-hook-standards.md](./2026-07-13-0010-agy-resolve-antigravity-hook-standards.md) | 解決 Google Antigravity 平台的 PreInvocation Hook 輸出標準與計數器重置 Bug |
| 2026-07-13 | [2026-07-13-0020-agy-apply-codex-review-fixes.md](./2026-07-13-0020-agy-apply-codex-review-fixes.md) | 消化並套用 Codex 審查修正：P1 計數器 JSON 格式支援、Antigravity 重置防線、P2 失效連結修復 |
| 2026-07-13 | [2026-07-13-0030-agy-resolve-spec-contradictions.md](./2026-07-13-0030-agy-resolve-spec-contradictions.md) | 解決二次審查規格矛盾：計數器重置細則對接、handoff-integrity 的 Purpose 描述補齊 |
| 2026-07-13 | [2026-07-13-0035-agy-final-cc-hook-alignment-and-review.md](./2026-07-13-0035-agy-final-cc-hook-alignment-and-review.md) | 補齊 cc 的 SessionStart 歸零機制，使全平台 reset 行為符合規格之最終審查 |
| 2026-07-13 | [2026-07-13-0109-codex-close-review-findings.md](./2026-07-13-0109-codex-close-review-findings.md) | 關閉最終 review findings：同步 advisory lock 正式 spec、修正 stale-lock 復原訊號、刷新交接狀態 |
| ... | ... | ... |

*(請注意：日常瑣碎的除錯或例行公事不需要加入此索引。本索引旨在建立一個可快速跳轉的「知識圖譜」。)*
