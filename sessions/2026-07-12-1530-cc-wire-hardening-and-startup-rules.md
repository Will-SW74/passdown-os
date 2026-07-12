# Session log — 2026-07-12 15:30 — cc — wire-hardening-and-startup-rules

**Agent:** cc
**Started from:** 使用者要求 review Gemini (agy) 落地的 v0.2 hardening，並修正 cc review 發現的接線問題 + 新增五項啟動紀律。（前次交接缺 log——本框架先前的演進都記在專案外的 transcript，未依自身協定留 session log。）

## What happened

1. **接線修正**：四個 v0.2 新檔（PROJECT_MANIFEST / CHECKLIST_HANDOFF / sessions/INDEX / memory/local-agent-sync）補進 CONSTITUTION 檔案地圖與開始/結束協定路由。
2. **會話鎖閉環**：`.active_lock` 改為「開始查牌→掛牌、結束摘牌」的完整循環，殘留鎖＝異常中斷訊號（開始協定第 1、5 步；結束協定新增第 9 步）。鎖與 `.toolcount` 進 `.gitignore`。
3. **計數器機制化**：查證確認 codex（`.codex/hooks.json`）與 agy（`.agents/hooks.json`）2026 年起都支援 hooks。新增 `entrypoints/hooks/codex-hooks.json.example`、`agy-hooks.json.example`、`checkpoint-counter.sh`；PROTOCOLS「持續存檔機制」改寫為 hook 機制化 + 紀律備援兩層。
4. **啟動紀律**（使用者指示）：CONSTITUTION 新增第 11 節（zh-TW + UTF-8）、第 10 節註解升級為一律必須、60% 存檔線改為先提醒使用者優先重開 session、本機記憶回寫必附時間戳。三個 entrypoints 範本同步加入口級提示。
5. **順手修**：PROTOCOLS 引用「開始協定第 4 步」因 Gemini 插入鎖步驟已失準——所有跨檔步驟引用改為名稱引用。

## Context Index / Memory Anchor

- 決策詳情：`memory/decisions.md`「2026-07-12 — v0.2 hardening 的接線修正與啟動紀律」
- 規則正本：`CONSTITUTION.md` 第 5、6、10、11 節；`PROTOCOLS.md`「持續存檔機制」
- hooks 安裝：`entrypoints/hooks/README.md`

## Scratchpad（未竟事項）

- agy 的 PreInvocation stdout 是否注入 context **未確認**，範本已標註，安裝時需實測並回寫結果到 hooks/README.md。
- `DISPATCH.md` 第 7 節查證表 codex / agy 仍為 `<待填>`。
- 本 log 是範本專案自我演進的紀錄；套用到新專案時依 GOLDEN_TEMPLATE 移除。
