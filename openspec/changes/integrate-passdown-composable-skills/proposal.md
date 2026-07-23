## Why

Passdown OS 已能保存跨 session、跨 agent 的持久狀態，但目前以整套框架與強制協定呈現，與小型、可組合的 Agent Skills 工作流銜接成本較高。第一版融合應把持久接力能力包裝成可按需呼叫的生命週期 skills，同時保留其相對於一次性 handoff 文件的差異化價值。

## What Changes

- 新增 `setup-passdown`、`resume-passdown`、`handoff-passdown` 三個可獨立呼叫且可組合的 Agent Skills。
- 建立精簡版 Passdown 專案狀態模板，保留 CURRENT、session log、decisions、known issues、具體下一步、記憶錨點與復原檢查。
- 在 handoff 產物加入 suggested skills，讓下一個 agent 可銜接 TDD、除錯、code review 或其他已安裝 skill，而不複製第三方 skill 內容。
- 將固定 agent 名稱、固定 context 百分比、每輪必寫 log、強制 subagent 與不可自驗等規則降為可攜式預設或風險分級政策。
- 新增融合評估與相容性文件，記錄保留、調整及排除項目。

## Non-Goals

- 不匯入、fork 或重新發布 `mattpocock/skills` 的內容。
- 不讓 Passdown OS 負責 spec、TDD、除錯、實作或 code review 等工程方法本身。
- 不要求 Spectra、特定 issue tracker、daemon、資料庫或單一 AI 工具才能使用。
- 本 change 不處理 marketplace 發布、原生 Codex plugin 或 Claude Code plugin 封裝。

## Capabilities

### New Capabilities

- `passdown-lifecycle`: 專案可透過 setup、resume、handoff 三個階段建立、讀取、驗證及持久化跨 agent 的最小交班狀態。
- `composable-skill-routing`: 交班可引用既有 artifact 並建議下一個 agent 使用的 skills，而不複製或綁定第三方 skill 實作。

### Modified Capabilities

（無）

## Impact

- Affected specs: `passdown-lifecycle`、`composable-skill-routing`
- Affected code:
  - New:
    - `.agents/skills/setup-passdown/SKILL.md`
    - `.agents/skills/setup-passdown/assets/passdown-os/CONSTITUTION.md`
    - `.agents/skills/setup-passdown/assets/passdown-os/handoff/CURRENT.md`
    - `.agents/skills/setup-passdown/assets/passdown-os/handoff/_template.md`
    - `.agents/skills/setup-passdown/assets/passdown-os/sessions/_template.md`
    - `.agents/skills/setup-passdown/assets/passdown-os/memory/decisions.md`
    - `.agents/skills/setup-passdown/assets/passdown-os/memory/known-issues.md`
    - `.agents/skills/resume-passdown/SKILL.md`
    - `.agents/skills/handoff-passdown/SKILL.md`
    - `docs/passdown-composable-skills-evaluation.md`
  - Modified: none
  - Removed: none
- External systems: 可選擇引用任何已安裝的 Agent Skills；不新增執行期依賴。
