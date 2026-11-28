# 生活器物部件產生器（cosmos_chimera ADR-0016、P1-19b）

依「功能 × 時代 × 部件槽 × 變體」用 Blender 產生低面數部件，交付到遊戲 repo 的 `Assets/_Project/Art/Objects/`。規格見遊戲 repo `docs/design/everyday-objects.md`；功能目錄見 `everyday-objects-catalog.md`。

```
blender -b --factory-startup --python tools/object-kit/build.py -- [--functions Hoe,Barrel] [--eras Primal,Future] [--no-export] [--render <dir>]
```
- 輸出：每個（功能、時代）一個 `<Family>/<Function>/<Function>_<Era>.fbx`，內含 `<slot>_v<k>`（k = 0–5）各一個物件，全部在同一個功能座標系（Z 向上、正面 -Y，原點在握把或落地點）。遊戲端每槽取一個變體放在同一原點即可組裝。
- 四星球形體（Q-A38，`everyday-objects.md#四星球形體`）：`kit_forms.regional(name, region)` 註冊的形體另外輸出 `<Function>_<Era>_<Region>.fbx`（`Ocean`／`Gale`／`Radiant`／`Metropolis`），manifest 記在 `functions.<F>.regions.<Region>.<Era>`；`--regions none` 只建共用版、`--skip-shared` 只建地區版（共用版 rng key 不含地區，加地區不會改到已交付的共用 FBX）。預覽圖為 `objects-<Function>-<Region>.png`。地區工藝（材質角色）見 `kit_lib.REGION_STYLE`，須與遊戲 `ObjectMeshes.RegionCraft` 一致。
- `object-kit.json`：部件槽、各變體三角形數、`max_assembled`（每槽取最大者相加）、`distinct`（每槽有幾個不同的變體）。任一組合超出預算（手持 600、擺設 1500、機械 4000）時，建置失敗。
- `--render`：每個功能一張 `objects-<Function>.png`，8 個時代 × 3 組隨機組合，用卡通預覽材質。
- 遊戲端門檻：`Bootstrap/Tests/EditMode/ObjectKitImportTests`。

## 結構
| 檔案 | 內容 |
|---|---|
| `kit_lib.py` | 幾何基本形（box、cyl、lathe、ring、tube、plate）；各時代工藝語彙 `STYLE`（倒角、表面雜訊、材質角色）；時代綁帶 `band`（繩、鐵箍、黃銅、螺栓、鉚釘、發光縫、鐵絲、符文）；收尾 `finish` |
| `kit_forms.py` | 每個功能的 8 個時代等價形體 |
| `forms_<組>.py` | 其他功能組的形體（家具、燈具、工具、容器、機械、載具 `forms_vehicle`、塑像 `forms_figure`、樂器與學術 `forms_instrument`…）；`build.py` 自動匯入，用 `kit_forms.function` 註冊。載具的原點在車體中央下方的地面（船在水線、飛行器在吊艙下方地面），行進方向 +X、側面朝 -Y；役畜與轎夫不在部件內 |
| `forms_region_<批>.py` | 四星球形體：先導批 `forms_region_pilot.py`（9 個功能）、柄具 `forms_region_hafted.py`（8 個手工具，沿用先導的地區柄／接合／柄尾）；桿具 `forms_region_rods.py`（釣竿、紡錘、筆刷、手杖、笛、號角；機構依時代分三層，形體依地區）；家具 `forms_region_furniture.py`（7 個功能，沿用共用版各時代的檯面高度：海洋靈屋與角形鞍頂、疾風雕凳與泥柱祭壇、日耀圓頂亭與蓮座、鋼鐵依時代）；容器 `forms_region_vessel.py`（13 個功能，沿用共用版尺寸：海洋竹桶、藤編、炒鍋與 tudung 罩、tumpeng 托盤；疾風葫蘆、盤編籃、三腳鍋、塔吉鍋、長嘴茶壺；日耀黃銅 lota 與 handi、ghanta 鈴、thali；鋼鐵依時代）；燈具 `forms_region_lamp.py`（6 個功能；光源槽一律發光：手工時代火焰、機械時代火焰或燈泡、高科技時代的光）；地區招牌語彙 `lash`／`horn`（海洋）、`pegs`／`zig`（疾風）、`dome`／`petals`（日耀）、`fins`／`steps`（鋼鐵）；殼體器依時代分三層機構（手工／機械／高科技） |
| `build.py` | 建置、預算檢查、FBX 匯出、manifest、預覽圖 |

## 規則
- **可重現**：亂數一律用 `rng_for(...)`（key 字串的 crc32），不用 Python 的 `hash()`。
- **共用尺寸**：會被其他部件槽依賴的尺寸（桶高、半徑、握柄長度），一律用 `F(p, …)` 從（功能、時代）的 frame 亂數流抽取。各槽的 `J(p, …)` 只用在局部細節。若在接合尺寸上用了 `J`，蓋子會浮在桶身上方。
- **變體**：每槽 6 個，來源有兩個：局部抖動，以及 `morph` 的剖面調制（沿部件自身高度鼓起或收腰，兩端固定，接合面不動）。
- **材質**：物件材質命名為 `m_<名稱>`（如 `m_wood`、`m_brass`、`m_glow_rune`），遊戲端依名稱與地區配色重新上色。預覽色票 `PALETTE` 只用於預覽圖。
- **頂點色 COLOR_0**（線性值）：R 凹處（壓暗）、G 凸邊（磨損提亮）、B 毀損遮罩（遊戲端依 `Damage` 設門檻）、A 1。
- **新增功能**：在 `kit_forms.py` 用 `@function(name, family, slots, size)` 註冊。`name` 必須是遊戲 `ObjectFunction` 的成員，部件槽數必須等於 `ObjectCatalog.SlotCount`，否則門檻測試會失敗。
