# 宙獸骨架與動作規格（`creatures`）

> 對應資料來源：`catalog.js`（v2.17.0 `BODY_PLANS`、`SKELETON_SPECS.creature`、`ACTIONS.creature`、`GRIP_MODES`）、`tasks.js`（`creature-model-rig` v5.3.0）、`Data/creature-grip-anims/creature-grip-anims.json`（`cosmimera-creature-grip-anim/1`）。  
> 更新日期：2026-11-28（共 **69** 支動作：同步 `fist_katar` 武器清單＋攀爬 `climb` **1** 支＋完整 21 類封閉 `body_plan` 表、`Socket_EggCore` 孵化對位、`hatch_emerge` 完整 JSON 規格＋蹲下 4 支＋追隨者／BOSS 主控 **6** 支＋既有相容）。

---

## 1. 骨架體系（Generic Rig）與 21 類封閉 `body_plan`

- **骨骼上限**：≤ 120 骨骼（推薦 ≤ 60 骨骼）。
- **核心層級**：`Root`（地面原點 pivot）→ `Hips` → `Spine_01..n` → `Neck` → `Head`
- **四肢與附屬**：四肢以 `L_` / `R_` 為前綴；尾部 `Tail_01..n`；翅膀 `Wing_L_01..n` / `Wing_R_01..n`
- **插槽骨（Sockets · 9 個）**：
  - `Socket_Mouth`（口部吐息／咬擊／進食點）
  - `Socket_Head`（頭部裝飾／視線基準點）
  - `Socket_Front`（前方技能發射點）
  - `Socket_Core_FX`（核心能量／超載／共鳴供招特效點）
  - `Socket_PetTouch`（撫摸互動對位點）
  - `Socket_Ground_FX`（地面陣法／衝擊波點）
  - `Socket_EggCore`（孵化破殼 `hatch_emerge` 與宙獸蛋對位核心點）
  - `Socket_Weapon_R`、`Socket_Weapon_L`（**預留空掛點**，位於身體兩側安全間距）

### 1.1 21 類封閉體態原型（`body_plan`，與 `morphology_tags` 正交）

| `body_plan` | 解剖與骨架基準 (`anatomy-profiles.js`) | `body_plan` | 解剖與骨架基準 (`anatomy-profiles.js`) |
|---|---|---|---|
| `humanoid` | 人型雙足 (`biped`) | `radial` | 放射對稱／星形 (`tentacled`) |
| `beast` | 四足／走獸 (`quadruped`) | `plant` | 植生根莖／藤蔓 (`plant`) |
| `avian` | 鳥翼雙足 (`avian`) | `fungus` | 菌蕈傘蓋／菌絲 (`plant`) |
| `saurian` | 爬行龍形／鱷蜥 (`quadruped`) | `machine` | 機械齒輪連桿 (`mechanism`／依足數升級機甲) |
| `serpent` | 無肢蛇蟒長條 (`serpentine`) | `artifact` | 浮空器物／秘寶擬態 (`object`) |
| `amphibian` | 兩棲伏臥跳躍 (`quadruped`) | `matter` | 礦晶岩土浮體 (`object`) |
| `fish` | 無步足純泳鰭 (`aquatic`) | `fluid` | 液態非牛頓流體 (`amorphous`) |
| `insect` | 六足節肢昆蟲 (`hexapod`) | `spirit` | 靈體氣態能量投影 (`amorphous`) |
| `crustacean` | 八足及以上甲殼 (`octopod`) | `amorphous` | 變形膠質史萊姆 (`amorphous`) |
| `mollusk` | 軟體貝螺滑行 (`amorphous`) | `swarm` | 微小個體群聚體 (`amorphous`) |
| `cephalopod` | 頭足放射觸腕 (`tentacled`) | | |

---

## 2. 裝備歸屬、追隨者／BOSS 主控與持有模式規範（`GRIP_MODES`）

> **核心鐵則**：裝備全部改為角色專屬（7 槽位），玩家角色直接於 `Socket_HandR_Prop`／`Socket_HandL_Prop` 持握武器與盾牌；召喚後的宙獸無個人裝備，改為**純粹本體追隨作戰＋供招共鳴**（BOSS 戰由一隻宙獸外觀擔任主控角色並搭配第二隻追隨者／車輪戰替補）。依 `craft-grip.schema.json`，每隻宙獸型態固定配置**唯一 1 組**允許之 `grip_mode`（`maxItems: 1`）。保留虛擬大手與 `Socket_Weapon_R`／`Socket_Weapon_L` 空掛點規格供遺留／BOSS 演出參考，技能仍由宙獸本體發出（`Socket_Front`／`Socket_Mouth`／`Socket_Core_FX`）；因此宙獸本體模型與骨架動畫**不繪製、不包含任何武器、盾牌或虛擬大手**。

| 持有模式 (`grip_mode`) | 掛點配置 | 對應獨立武器／動作參考（勿繪於本體） | 本體動作節奏 | 過濾規則 |
|---|---|---|---|---|
| `two_handed`（雙手武器） | `Socket_Weapon_R`（主手）＋ `Socket_Weapon_L`（雙手輔助）空掛點 | 近戰：雙頭刃／長棍、長槍／戟、雙手大劍、巨斧／巨錘<br>遠程：連弩／獵弓、長弓、法杖、重弩／巨砲杖 | 重心沉穩，做出重型蓄力、大弧度揮身與射擊後座動作 | 使用通用攻擊 clip（無 `_r`/`_l`） |
| `dual_wield`（雙持單手） | `Socket_Weapon_R`（主手）＋ `Socket_Weapon_L`（副手）空掛點 | 近戰：匕首／拳爪、拳套／拳劍（`fist_katar`，與空手共用 `unarmed_fist`）、單手劍／彎刀、單手斧、單手錘<br>遠程：飛刃／手裡劍、手弩、短杖／魔導銃、投矛 | 低重心敏捷側身，依 `_r` 與 `_l` 交替左右前探扭轉 | 近戰／突進／遠程改用 `_r` / `_l` 交替 clip |
| `one_hand_shield`（單手＋盾） | `Socket_Weapon_R`（主手單手武器）＋ `Socket_Weapon_L`（副手盾牌）空掛點 | 近戰／遠程同單手武器；副手盾牌：圓盾、鳶盾、塔盾、木圓盾、符紋盾、長方木盾 | 左側穩固護前、右側俐落發力或微探後座 | 使用通用攻擊 clip（無 `_r`/`_l`） |

---

## 3. 動作清單（30 fps · 共 69 支，clip 命名為 `cr_<stage>_<id>`）

> 標記 `[立體移動新增]` 為 v2.16 新增之 `climb` 攀爬 1 支；`[新增]` 為 v2.11 新增的 19 支；`[雙持新增]` 為 12 支雙持左右交替；`[追隨/BOSS新增]` 為 v2.12 新增之 6 支；`[蹲下新增]` 為 v2.15 新增的 4 支蹲下動作。  
> **蹲下與起身銜接規範**：蹲下狀態僅額外製作 `crouch_move`、`crouch_roll`、`crouch_jump`、`crouch_block` 四支低姿動作（維持無武器本體與 `Socket_Weapon_R`/`L` 空掛點安全間距）；蹲下時發動攻擊、輔助／場地／生活能力、或與道具／投擲／捕獲等互動動作銜接時，**須先回歸站立姿態後再接續標準站立 clip**，不另製作獨立蹲下攻擊或互動動畫。

### 3.1 移動、穿越與騎乘（17 支）

| clip ID | 說明 | 幀數 | loop | RM | 事件@幀 | 備註 |
|---|---|---:|:---:|:---:|---|---|
| `idle` | 待機（2 秒短週期呼吸律動） | 60 | ✓ | | | 既有 |
| `idle_long` | 長時間靜止週期動作（4 秒定力循環） | 120 | ✓ | | | 既有 |
| `walk` | 移動 | 32 | ✓ | | `ev_footstep@8` | 既有 |
| `run` | 奔跑 | 20 | ✓ | | `ev_footstep@5` | 既有 |
| `sneak` | 潛行 | 40 | ✓ | | | 既有 |
| `climb` | 攀爬／岩壁移動（依 `body_plan` 附著攀登） | 32 | ✓ | | `ev_footstep@5` | `[立體移動新增]` |
| `crouch_move` | 蹲下移動（低伏潛行移動） | 38 | ✓ | | `ev_footstep@10, ev_footstep@29` | `[蹲下新增]` |
| `crouch_roll` | 蹲下翻滾（低姿翻滾閃避，無敵幀） | 18 | | ✓ | `ev_end_lock@14` | `[蹲下新增]` |
| `crouch_jump` | 蹲下跳躍（低伏蓄力起跳／滯空／落地） | 30 | | | | `[蹲下新增]` |
| `jump` | 跳躍（起跳／滯空／落地） | 30 | | | | `[新增]` |
| `roll_dodge` | 翻滾閃避（主控無敵幀） | 18 | | ✓ | `ev_end_lock@14` | `[新增]` |
| `swim` | 游泳／水面移動 | 36 | ✓ | | | `[新增]` |
| `dive` | 潛水／水下移動 | 36 | ✓ | | | `[新增]` |
| `fly_idle` | 飛行／懸浮待機 | 60 | ✓ | | | `[新增]` |
| `fly_move` | 飛行／滑翔移動 | 32 | ✓ | | | `[新增]` |
| `mount_idle` | 被騎乘待機（穩定承載姿態） | 60 | ✓ | | | `[新增]` |
| `mount_run` | 被騎乘奔跑（高速載騎衝刺） | 22 | ✓ | | `ev_footstep@5` | `[新增]` |

### 3.2 格擋、受擊與 BOSS 狀態（10 支）

| clip ID | 說明 | 幀數 | loop | RM | 事件@幀 | 備註 |
|---|---|---:|:---:|:---:|---|---|
| `block` | 格擋 | 30 | | | | 既有 |
| `crouch_block` | 蹲下格擋（低伏防禦架勢） | 28 | | | | `[蹲下新增]` |
| `block_hit` | 格擋受擊（防禦震退回饋） | 16 | | | `ev_spawn_fx@2` | `[新增]` |
| `perfect_block` | 完美格擋（150ms 彈反震擊） | 22 | | | `ev_spawn_fx@4, ev_hit@6, ev_end_lock@16` | `[新增]` |
| `guard_break` | 破防硬直（架勢條滿崩解 1.5s） | 45 | | | | `[新增]` |
| `stagger` | 失衡硬直（受破招／重擊暈眩） | 45 | | | | `[新增]` |
| `dodge_miss` | 閃避（MISS 殘影） | 14 | | ✓ | | 既有 |
| `hit_react` | 受擊 | 15 | | | | 既有 |
| `faint` | 倒下 | 40 | | | | 既有 |
| `boss_enrage` | BOSS 狂暴（階段轉換威嚇咆哮） | 48 | | | `ev_spawn_fx@18` | `[新增]` |

### 3.3 主動技攻擊與武器持握交替（20 支）

| clip ID | 說明 | 幀數 | loop | RM | 事件@幀 | 適用 `grip_mode` / 距離 | 備註 |
|---|---|---:|:---:|:---:|---|---|---|
| `atk_melee_front` | 近戰：正前 | 26 | | | `ev_hit@12, ev_end_lock@20` | `two_handed`, `one_hand_shield` / `melee` | 既有 |
| `atk_melee_front_r` | 雙持近戰（右手）：正前快斬 | 22 | | | `ev_hit@9, ev_end_lock@16` | `dual_wield` / `melee` | `[雙持新增]` |
| `atk_melee_front_l` | 雙持近戰（左手）：正前快斬 | 22 | | | `ev_hit@9, ev_end_lock@16` | `dual_wield` / `melee` | `[雙持新增]` |
| `atk_melee_sweep` | 近戰：橫掃 | 30 | | | `ev_hit@14, ev_end_lock@24` | `two_handed`, `one_hand_shield` / `melee` | 既有 |
| `atk_melee_sweep_r` | 雙持近戰（右手）：橫掃 | 25 | | | `ev_hit@11, ev_end_lock@19` | `dual_wield` / `melee` | `[雙持新增]` |
| `atk_melee_sweep_l` | 雙持近戰（左手）：橫掃 | 25 | | | `ev_hit@11, ev_end_lock@19` | `dual_wield` / `melee` | `[雙持新增]` |
| `atk_melee_burst` | 近戰：擴散 | 34 | | | `ev_spawn_fx@16, ev_hit@18` | 全模式 / `melee` | 既有 |
| `atk_dash` | 突進：直線衝鋒攻擊 | 28 | | ✓ | `ev_hit@12, ev_end_lock@22` | `two_handed`, `one_hand_shield` | `[新增]` |
| `atk_dash_r` | 雙持突進（右手）：疾風突刺 | 24 | | ✓ | `ev_hit@10, ev_end_lock@18` | `dual_wield` | `[雙持新增]` |
| `atk_dash_l` | 雙持突進（左手）：疾風突刺 | 24 | | ✓ | `ev_hit@10, ev_end_lock@18` | `dual_wield` | `[雙持新增]` |
| `atk_ranged_line` | 射擊：直線 | 30 | | | `ev_spawn_fx@14` | `two_handed`, `one_hand_shield` / `ranged` | 既有 |
| `atk_ranged_line_r` | 雙持遠程（右手）：直線射擊／擲射 | 24 | | | `ev_spawn_fx@11, ev_end_lock@18` | `dual_wield` / `ranged` | `[雙持新增]` |
| `atk_ranged_line_l` | 雙持遠程（左手）：直線射擊／擲射 | 24 | | | `ev_spawn_fx@11, ev_end_lock@18` | `dual_wield` / `ranged` | `[雙持新增]` |
| `atk_ranged_cone` | 射擊：扇形 | 30 | | | `ev_spawn_fx@14` | `two_handed`, `one_hand_shield` / `ranged` | 既有 |
| `atk_ranged_cone_r` | 雙持遠程（右手）：扇形散射 | 26 | | | `ev_spawn_fx@12, ev_end_lock@20` | `dual_wield` / `ranged` | `[雙持新增]` |
| `atk_ranged_cone_l` | 雙持遠程（左手）：扇形散射 | 26 | | | `ev_spawn_fx@12, ev_end_lock@20` | `dual_wield` / `ranged` | `[雙持新增]` |
| `atk_ranged_arc` | 射擊：拋物線 | 34 | | | `ev_spawn_fx@18` | `two_handed`, `one_hand_shield` / `ranged` | 既有 |
| `atk_ranged_arc_r` | 雙持遠程（右手）：拋物線擲射 | 28 | | | `ev_spawn_fx@14, ev_end_lock@22` | `dual_wield` / `ranged` | `[雙持新增]` |
| `atk_ranged_arc_l` | 雙持遠程（左手）：拋物線擲射 | 28 | | | `ev_spawn_fx@14, ev_end_lock@22` | `dual_wield` / `ranged` | `[雙持新增]` |
| `atk_burst_target` | 遠程：指定目標點爆破引導 | 34 | | | `ev_spawn_fx@16, ev_hit@18` | 全模式 / `ranged` | `[新增]` |

### 3.4 輔助、場地、生態生活與演出（16 支）

| clip ID | 說明 | 幀數 | loop | RM | 事件@幀 | 備註 |
|---|---|---:|:---:|:---:|---|---|
| `sup_self` | 輔助：自身 | 36 | | | `ev_spawn_fx@18` | 既有 |
| `sup_ally` | 輔助：他者 | 36 | | | `ev_spawn_fx@18` | 既有 |
| `field_deploy` | 佈署場地 | 48 | | | `ev_spawn_fx@28` | 既有 |
| `field_utility` | 發動生活能力（操縱天氣／破障／生火） | 42 | | | `ev_spawn_fx@20` | `[新增]` |
| `wild_alert` | 野生警戒／領域威嚇 | 36 | | | `ev_spawn_fx@12` | `[新增]` |
| `sleep_rest` | 休眠／營地休息 | 90 | ✓ | | | `[新增]` |
| `eat_feed` | 進食／接受餵食 | 48 | | | `ev_spawn_fx@24` | `[新增]` |
| `petted` | 接受撫摸（依體型對位 `Socket_PetTouch`） | 60 | | | | 既有 |
| `summon_appear` | 被召喚登場 | 36 | | | | 既有 |
| `recall_vanish` | 被收回 | 24 | | | | 既有 |
| `capture_struggle` | 被收服時掙扎 | 45 | | | | 既有 |
| `hatch_emerge` | 破蛋而出（自蜷縮 pose 對齊 `Socket_EggCore`） | 210 | | | `ev_spawn_fx@0, ev_spawn_fx@60, ev_end_lock@200` | v2.13 |
| `overload_enter` | 進入超載 | 60 | | | `ev_spawn_fx@20` | 既有 |
| `overload_exit` | 超載結束 | 36 | | | | 既有 |
| `hatch` | 破蛋而出（僅幼年 `juvenile`） | 72 | | | | 既有 |
| `victory` | 勝利 | 60 | | | | 既有 |

### 3.5 追隨者作戰、共鳴供招與 BOSS 主控演出（6 支）

| clip ID | 說明 | 幀數 | loop | RM | 事件@幀 | 主要掛點 | 備註 |
|---|---|---:|:---:|:---:|---|---|---|
| `follow_idle` | 追隨者待機（貼身護衛姿態） | 60 | ✓ | | | `Socket_Core_FX` | `[追隨/BOSS新增]` |
| `follow_dash` | 追隨者疾步跟進（跟隨主控趕路／補位） | 22 | | ✓ | | `Socket_Ground_FX` | `[追隨/BOSS新增]` |
| `link_channel` | 共鳴供招（作為主控當前招式組來源時微光呼應） | 40 | ✓ | | `ev_spawn_fx@10` | `Socket_Core_FX` | `[追隨/BOSS新增]` |
| `relay_enter` | 車輪戰輪替上場（替補追隨者衝入戰場） | 32 | | | `ev_spawn_fx@14` | `Socket_Ground_FX` | `[追隨/BOSS新增]` |
| `boss_moveset_switch` | BOSS 主控切換招式組（切換本體／追隨者招式） | 26 | | | `ev_spawn_fx@10, ev_end_lock@18` | `Socket_Core_FX` | `[追隨/BOSS新增]` |
| `boss_summon_follower` | BOSS 號召／喚出追隨者（第二隻或車輪戰替補） | 36 | | | `ev_spawn_fx@16` | `Socket_Ground_FX` | `[追隨/BOSS新增]` |
