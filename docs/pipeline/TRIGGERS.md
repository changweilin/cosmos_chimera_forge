# 簡易觸發語句

先指定 `<kind>`：角色 `characters`（不含 UMA 創造的 NPC）、宙獸 `creatures`、招式 `moves`。不得從根目錄 `prompts/` 寫入新檔；角色使用 `characters/_prompts/`（`prompt-to-image` ＋ `image-to-3D`），宙獸使用 `creatures/_prompts/`（`prompt-to-3D`），招式使用 `moves/_prompts/`（`prompt-to-3D` VFX）。
管線開工（或已有 GLB 產出）時，將 `<kind>/_designed_prompts/<design_id>.prompt.md`（純視覺特徵 Prompt，宙獸分述四型態一致性、各型態特徵、型態演化關係，每型態獨立產出一個 `.glb`）移入 `<kind>/<id>/`；若版本或步驟有調整，將更改內容追加於該 `.prompt.md`。`<kind>/<id>/` 只保留 `*.prompt.md` 與當前審核階段或已通過的檔案，已結束步驟或舊有版本僅保留最新完整版。
先選定資產與參數，再交給可讀取 Drive 的 AI；外觀、參數及圖片以指定檔案為準。

- 主動技 3D VFX（Prompt-to-3D）：讀取 `cosmos_chimera_forge/moves/_prompts/01b_move_vfx.prompt.md`，使用指定主動技資產設定與輸出路徑。
- 被動技提示 VFX（Prompt-to-3D）：讀取 `cosmos_chimera_forge/moves/_prompts/01c_passive_vfx.prompt.md`，使用指定被動技資產設定與輸出路徑（僅於被動效果發揮影響力時短暫提示，不影響戰鬥系統、不連續重疊）。
- 外觀設定：讀取 `cosmos_chimera_forge/<kind>/_prompts/00_appearance.prompt.md`，依附上的素材執行。
- 角色立繪（Prompt-to-Image，僅角色）：讀取 `cosmos_chimera_forge/characters/_prompts/01_portrait.prompt.md`，使用指定資產的 appearance.md 和 parameters.json 執行。
- 角色立繪審查（僅角色）：讀取 `cosmos_chimera_forge/characters/_prompts/02_review_portrait.prompt.md`，檢查指定的立繪目錄。
- 角色 AI Blender（Image-to-3D）：讀取 `cosmos_chimera_forge/characters/_prompts/03b_blender.prompt.md`，使用已核准立繪（看圖 AI 畫）由 AI 操作 Blender 建模、綁骨與動作。
- 宙獸 AI Blender（Prompt-to-3D）：讀取 `cosmos_chimera_forge/creatures/_prompts/03b_blender.prompt.md`，直接依純文字外觀與 parameters.json 由 AI 操作 Blender 原創建模、綁骨與動作（無需立繪）。圖鑑統一使用 `creatures/<id>/<id>_<stage>_05_wiki.md` 的既有檔案，缺少時才建立，不重複生成。
- 最終審查：讀取 `cosmos_chimera_forge/<kind>/_prompts/04_review_3d.prompt.md`，檢查模型與對應立繪（角色 Image-to-3D）；宙獸 Prompt-to-3D 無需立繪。

HTML 中選步驟，按「讀取本步驟 .md／複製執行」可產生已填入目前資產的版本。原始 `.md` 的 `{{欄位}}` 由 HTML 代入；直接交給 AI 時須提供實際路徑與設定。讀取本身不會自動啟動外部 AI。