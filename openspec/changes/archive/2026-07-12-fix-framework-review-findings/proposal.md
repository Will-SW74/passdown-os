## Why

本 change 源自 **2026-07-11 由 cc 對 passdown-os 框架所做的全面架構 review**（review 於 branch review-fixes 上進行，涵蓋 CONSTITUTION / PROTOCOLS / DISPATCH / RUBRICS / GOLDEN_TEMPLATE / entrypoints 全部規則檔）。該次 review 發現：前兩輪修正（cc review、gpt review）補進來的機制有多處「沒有接回主幹」——會話鎖只做半套、四個新增檔案成為孤兒、同一份清單存三份已開始 drift、復原偵測邏輯存在先天誤判風險。這些問題會直接削弱框架最核心的承諾（交接不遺失、規則可被機制保證執行），必須在框架被複製到更多專案之前修正。

## What Changes

依 review 發現的優先序，本 change 包含以下修正：

**高優先（機制斷裂或邏輯矛盾）**

1. **補完 .active_lock 會話鎖機制**：CONSTITUTION.md 的 Session 開始協定目前只規定「寫入 sessions/.active_lock」，但全框架沒有任何地方讀取或刪除它。修正為完整生命週期——開始時檢查殘留 lock（存在即代表上次結束協定沒跑完，觸發復原）、結束協定最後一步刪除 lock、並將 sessions/.active_lock 加入 .gitignore 避免跨機 merge conflict。
2. **修正復原偵測的誤判風險**：結束協定先寫 handoff/CURRENT.md 再寫 session log，導致「log 比 CURRENT.md 新 = 交接沒跑完」的時間戳比對必然誤判；且 log 檔名時間戳語意（session 開始時間 vs 寫檔時間）從未定義。改為語意檢查：比對 sessions/ 最新一份 log 是否就是 CURRENT.md 的 Direct Memory Source 所指向的那份，並明文定義檔名時間戳為 session 開始時間。
3. **處理四個孤兒檔案**：CHECKLIST_HANDOFF.md（與結束協定重複，併回正本後移除）、memory/local-agent-sync.md（與 PROTOCOLS.md 本機記憶同步章節重複，併回後移除）、PROJECT_MANIFEST.md（接進 CONSTITUTION.md 檔案地圖與 GOLDEN_TEMPLATE.md 套用清單）、sessions/INDEX.md（接進 Session 結束協定與 sessions/ 歸檔流程，並修正 GOLDEN_TEMPLATE.md 自檢清單中「sessions/ 底下只剩 _template.md 和空的 archive/」會誤刪 INDEX.md 的矛盾）。
4. **修正章節編號 drift**：PROTOCOLS.md 的「不使用 Spectra 時的替代方案」仍指向「Session 開始協定第 4 步」，實際已因會話鎖步驟插入而變為第 5 步。

**中優先（設計穩健度）**

5. **Code Symbol Anchor 改用 repo 相對路徑**：handoff/_template.md 與 sessions/_template.md 及 PROTOCOLS.md 的範例目前使用絕對路徑（file:///C:/...），跨機交接必斷、且違反框架自己的去敏感化原則。
6. **持續存檔機制的觸發規則上移**：該規則是無條件觸發的強制義務，卻放在被指到才讀的 PROTOCOLS.md；將觸發摘要上移至 CONSTITUTION.md，細節留在 PROTOCOLS.md。
7. **補上 PreCompact hook**：entrypoints/hooks/README.md 只查證過 Stop 與 SessionEnd 不適用，漏掉 cc 的 PreCompact hook——它正好能機制化「壓縮前必須先完成記憶同步」規則，比模型自估 context 百分比可靠。

**低優先**

8. 簽名時間戳明定時區處理方式；entrypoints/CLAUDE.md.example 的調度模式提問補「無人值守時預設分派模式」；GOLDEN_TEMPLATE.md 自檢清單補 PROJECT_MANIFEST.md 填寫項。

## Capabilities

### New Capabilities

- `handoff-integrity`: session 交接完整性保證——會話鎖的完整生命週期（建立、檢查、刪除）、交接完整性偵測（語意檢查取代時間戳比對）、規則單一來源原則（每條規則只有一份正本，重複清單必須併回）、檔案地圖完整性（框架內每個檔案都必須被檔案地圖收錄且被至少一個協定步驟指到）。

### Modified Capabilities

（無——本專案尚無既有 spec）

## Impact

- Affected specs: 新增 openspec/specs/handoff-integrity/spec.md
- Affected code:
  - Modified: CONSTITUTION.md、PROTOCOLS.md、GOLDEN_TEMPLATE.md、.gitignore、PROJECT_MANIFEST.md、sessions/INDEX.md、handoff/_template.md、sessions/_template.md、entrypoints/hooks/README.md、entrypoints/hooks/settings.json.example、entrypoints/commands/handoff.md、entrypoints/CLAUDE.md.example
  - New: 無
  - Removed: CHECKLIST_HANDOFF.md、memory/local-agent-sync.md
