## Why

> **註記：本 change 為回溯性記錄（retroactive documentation）**——實作已於 2026-07-12 在本分支完成，本 change 目的是把「為什麼這樣改」的思路留在 Spectra 正規流程中，供後續 agent 追溯。

cc review 指出 Gemini (agy) 落地的 v0.2 hardening 存在三個結構性缺陷：(1) 新增的四個檔案（PROJECT_MANIFEST.md、CHECKLIST_HANDOFF.md、sessions/INDEX.md、memory/local-agent-sync.md）沒有被任何核心檔指向——在本框架「被指到才讀」的 pull 機制下，沒被指到等於不存在；(2) `.active_lock` 會話鎖只有「掛牌」沒有「檢查」與「摘牌」，是一個沒人驗證的儀式，且未進 .gitignore；(3) 持續存檔計數器宣稱「不靠內省」，實際上仍要求模型自數工具呼叫次數，違反誠實條款。同時使用者指示新增五項啟動紀律（正體中文、UTF-8、程式碼註解必加、本機記憶回寫附時間戳、壓縮前先提醒使用者）。

## What Changes

- **孤兒檔案接線**：四個 v0.2 新檔補進 CONSTITUTION.md 檔案地圖，並嵌入協定實際步驟（PROJECT_MANIFEST 為開始協定第 2 步、CHECKLIST_HANDOFF 掛結束協定開頭、sessions/INDEX.md 接進「追歷史先看索引」、local-agent-sync 接進記憶同步步驟）；衍生檔標明正本出處，防止規則雙源漂移。
- **會話鎖閉環**：`.active_lock` 改為「進門查牌 → 掛牌 → 結束協定最後一步（新增第 9 步）摘牌簽退」的完整循環；殘留鎖成為復原協定的訊號 A；鎖與 `.toolcount` 進 .gitignore。
- **計數器兩層化**：PROTOCOLS「持續存檔機制」改寫為「hook 機制化（建議）＋紀律啟發式（備援）」；查證確認 codex 與 agy 2026 年起均支援 lifecycle hooks，新增兩份 hooks 範本與外部計數腳本 checkpoint-counter.sh。
- **啟動紀律**：CONSTITUTION 新增第 11 節（zh-TW ＋ UTF-8）；第 10 節註解紀律由「特殊邏輯才必須」升級為「一律必須」；60% 存檔線改為「先提醒使用者、優先重開新 session」；本機記憶回寫每條附 agent 代號與時間戳；三個 entrypoints 入口範本同步加入口級提示。
- **順手修**：跨檔的協定步驟引用由編號改為名稱（Gemini 插入鎖步驟後「第 4 步」等引用已失準）；GOLDEN_TEMPLATE 重置清單與自檢清單補齊新檔案。

## Non-Goals

- 不重做框架架構——cc review 結論是「設計骨架 A 級，問題在接線層」，因此只修接線與紀律，不動核心協定的結構。
- 不將計數器包裝成強制機制（否決理由：模型自數不可靠，違反誠實條款）；改為 hook 機制化＋紀律備援雙層。
- 不移除 `.active_lock`（曾考慮：承認擋不住自覺問題、直接拿掉）——改成閉環後它有真實偵測價值（殘留＝異常中斷），成本極低，故保留並補完。
- agy 的 PreInvocation stdout 是否注入 context 未實測，範本已標「未確認」——這是本 change 唯一保留為未勾選的 task，於任一 agy 環境安裝 hooks 時實測並回寫結果。

## Capabilities

### New Capabilities

- `session-liveness-signals`: 會話鎖（`.active_lock`）與檢查點計數器（`.toolcount`）的完整生命週期契約——掛牌/摘牌/殘留偵測、外部計數觸發存檔提醒。這是本次修訂中唯一新增的「可驗證系統行為」；其餘變更為框架規則文件的接線與紀律條文，不構成 spec 級 capability。

### Modified Capabilities

（無——本專案 openspec/specs/ 目前無既有 spec。）

## Impact

- Affected specs: 無（本專案尚無 spec）
- Affected code:
  - New: passdown-os/entrypoints/hooks/codex-hooks.json.example、passdown-os/entrypoints/hooks/agy-hooks.json.example、passdown-os/entrypoints/hooks/checkpoint-counter.sh、passdown-os/sessions/2026-07-12-1530-cc-wire-hardening-and-startup-rules.md
  - Modified: passdown-os/CONSTITUTION.md、passdown-os/PROTOCOLS.md、passdown-os/CHECKLIST_HANDOFF.md、passdown-os/GOLDEN_TEMPLATE.md、passdown-os/README.md、passdown-os/.gitignore、passdown-os/memory/decisions.md、passdown-os/memory/local-agent-sync.md、passdown-os/entrypoints/CLAUDE.md.example、passdown-os/entrypoints/AGENTS.md.example、passdown-os/entrypoints/CODEX.md.example、passdown-os/entrypoints/commands/handoff.md、passdown-os/entrypoints/hooks/README.md、passdown-os/entrypoints/hooks/settings.json.example
  - Removed: 無
