# cosmos_chimera 搬移暫存區

本目錄存放待搬移至相鄰 `../cosmos_chimera` 遊戲專案的 P5-12 檔案（含 `_incoming`、`_catalog`、`docs/design/creatures.md` 與 `tools/tests/test_move_balance.py`），以及 `_base/` 三方合併基準快照與 [manifest.json](manifest.json)。

## 內建防護與機制

1. **防衝突機制**：
   - **Pre-flight 檢查**：驗證 `staged_sha256`、確認目標 Git 無 merge/rebase/cherry-pick 進行中、檢查目標路徑無未提交髒檔（`-RequireCleanRepo` 可要求全庫乾淨），`-Commit` 亦禁止 index 中混有其他未提交檔案。
   - **三方合併（3-way merge）**：`update` 檔案若在目標專案已有其他非重疊修改（`expected_base_sha256` 不符），自動以 `_base/` 基準執行 `git merge-file` 合併；若發生重疊行衝突則立即中止，不寫入任何檔案。
   - **自動回滾（Rollback）**：寫入、格式化或驗證失敗時，自動還原所有覆蓋前備份並刪除本次新建檔案。
2. **搬移後格式化（`-Format`，或隨 `-Commit` 自動啟用）**：
   - 依目標專案 `.editorconfig` / `.gitattributes` 統一為 UTF-8（無 BOM）、LF 換行、結尾單一換行；非 `.md` 去除行尾空白；`.json` 嚴格檢查並正規化為 2-space 縮排。
3. **格式化 Commit（`-Commit`）**：
   - 自動先執行格式化與資料/平衡驗證（除非明確加上 `-SkipChecks`），通過後僅針對 manifest 內的 13 個檔案依 Conventional Commits 格式建立獨立 commit（不夾帶目標專案其他既有修改）。

## 使用方式

```powershell
# 1. 預覽檢查（包含三方合併偵測與預定 commit 訊息，不寫入目標目錄）
powershell -ExecutionPolicy Bypass -File tools/migrate_cosmos_chimera_staging.ps1 -DryRun -Commit

# 2. 複製搬移至 ../cosmos_chimera、格式化並執行驗證（不建立 commit）
powershell -ExecutionPolicy Bypass -File tools/migrate_cosmos_chimera_staging.ps1 -Format -RunChecks

# 3. 複製搬移、格式化、驗證並建立 Conventional Commit
powershell -ExecutionPolicy Bypass -File tools/migrate_cosmos_chimera_staging.ps1 -Commit

# 4. 搬移後清除本暫存區已搬移檔案（可搭配 -Commit）
powershell -ExecutionPolicy Bypass -File tools/migrate_cosmos_chimera_staging.ps1 -Move -Commit
```
