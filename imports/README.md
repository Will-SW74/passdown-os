# 本機原始記憶暫存清洗區 (Imports)
<!-- gpt review 修正：建立明確的本機記憶清洗與升級流程說明 -->

本資料夾 (`imports/`) 是用來處理 **Local Agent Memory Sync (本機記憶同步)** 的暫存區域。

## 什麼時候會用到這裡？
當你需要執行「整批匯入」本機記憶（例如從 `~/.claude/projects/<hash>/memory/` 或 `~/.gemini/antigravity-cli/...`），因為換電腦、換工具、或某個工具的本機記憶即將遺失時，才會使用本資料夾。

日常的 session 結束不需要用到這裡（日常只需輕量摘要回寫到 `sessions/` 或 `memory/decisions.md`）。

## 清洗流程
1. **匯入**：將原始的本機記憶檔案複製到此處。
2. **去敏 (Redaction)**：移除所有 API Key、Token、Cookie、密碼、絕對路徑與私人資訊。
3. **紀錄**：將去敏過程中移除了什麼資訊，記錄到 `memory/redaction-log.md`。
4. **摘要升級 (Promotion)**：將去敏後真正有價值的決策或坑，摘要寫入 `memory/decisions.md` 或 `memory/known-issues.md`。
5. **清理**：完成後，應將這裡的原始檔案刪除或移至不進版控的備份區，不要把它們當作永久的記憶來源。

> ⚠️ 注意：本資料夾預設不進入 Git 版控（見 `.gitignore`），請勿在此處放置專案的核心程式碼或文件。
