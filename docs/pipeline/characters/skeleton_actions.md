# 角色骨架與動作規格（`characters`）

> 對應資料來源：`catalog.js`（v2.12.0 `ACTIONS.character`）、`tasks.js`（`character-model-rig` v5.1.0）、`Data/character-anims/character-anims.json`（`cosmimera-character-anim/1`）。  
> 更新日期：2026-11-26（共 **81** 支動作：主控戰鬥七槽裝備／格擋彈反／拔收武器／招式組切換與 22 支主控攻擊輔助共 **31** 支新增動作＋既有 **50** 支完整相容）。

---

## 1. 骨架體系與七槽角色專屬裝備（Unity Humanoid）

- **骨骼上限**：≤ 75 骨骼，採 Unity Humanoid 標準命名：
  - 核心軀幹：`Hips` → `Spine` → `Chest` → `UpperChest` → `Neck` → `Head`
  - 四肢：`Shoulder` → `Arm` → `ForeArm` → `Hand`（含手指三節 `Thumb` / `Index` / `Middle` / `Ring` / `Little`）；`UpLeg` → `Leg` → `Foot` → `Toes`
  - 附屬物理：`Extra_*`（頭髮、披風、飾帶等）
- **插槽骨（Sockets · 7 個，對應全遊戲唯一的角色七槽裝備系統）**：
  - `Socket_HandR_Prop`（`weapon` 主手武器／礦鎬／釣竿／廚具／收服器掛點）
  - `Socket_HandL_Prop`（`weapon` 副手武器／盾牌／冒險手冊掛點）
  - `Socket_Head_Armor`（`head` 頭盔防具掛點，對應 2× 防具詞綴／數值擴充）
  - `Socket_Hands_Armor`（`hands` 手套／護手防具掛點，對應 2× 防具詞綴／數值擴充）
  - `Socket_Back_Pack`（背包／披風掛點；另含 `body` 胸甲、`legs` 腿甲由蒙皮更換，`accessory` 飾品無獨立網格）
  - `Socket_Throw`（投擲收服道具／道具出手基準點）
  - `Socket_Head_FX`（頭頂／共鳴狀態／情緒特效掛點）
- **裝備歸屬與雙持過濾規則**：
  - 全部 7 個裝備槽位（`weapon`、`head`、`body`、`hands`、`legs`、`accessory`、`backpack`）皆由玩家角色穿戴與持握，宙獸無個人裝備。
  - 角色預設產出支援全持握模式（`two_handed`／`dual_wield`／`one_hand_shield`）；若指定單一 `grip_mode`，則依 `Data/character-anims/character-anims.json` 過濾 `_r`/`_l` 與通用攻擊 clip（`dual_wield` 僅用 `_r`/`_l`＋全模式 clip，其餘僅用無 `_r`/`_l` 通用 clip）。

---

## 2. 動作清單（30 fps · 共 81 支）

> 標記 `[主控新增]` 為本次因應「玩家主控作戰＋兩隻宙獸追隨／供招」機制擴充的 31 支動作；既有 50 支 clip ID 全數保留相容。

### 2.1 基礎移動與穿越（13 支）

| clip | 說明 | 幀數 | loop | RM | 事件@幀 | 備註 |
|---|---|---:|:---:|:---:|---|---|
| `chr_idle` | 待機（2 秒短週期呼吸律動） | 60 | ✓ | | | 既有 |
| `chr_idle_long` | 長時間靜止週期動作（4 秒定力循環） | 120 | ✓ | | | 既有 |
| `chr_walk` | 走路 | 32 | ✓ | | `ev_footstep@8, ev_footstep@24` | 既有 |
| `chr_run` | 奔跑 | 22 | ✓ | | `ev_footstep@5, ev_footstep@16` | 既有 |
| `chr_sneak_idle` | 潛行待機 | 60 | ✓ | | | 既有 |
| `chr_sneak_move` | 潛行移動 | 40 | ✓ | | | 既有 |
| `chr_roll_dodge` | 翻滾閃避（無敵幀） | 20 | | ✓ | `ev_end_lock@16` | 既有 |
| `chr_jump` | 跳躍（起跳／滯空／落地） | 30 | | | | 既有 |
| `chr_swim_idle` | 水面漂浮待機 | 60 | ✓ | | | 既有 |
| `chr_swim_move` | 游泳移動 | 36 | ✓ | | | 既有 |
| `chr_glide` | 滑翔滯空（乘風／高空移動） | 45 | ✓ | | | 既有 |
| `chr_mount_idle` | 騎乘待機（坐姿握鞍） | 60 | ✓ | | | 既有 |
| `chr_mount_run` | 騎乘奔跑（騎乘衝刺） | 24 | ✓ | | | 既有 |

### 2.2 主控戰鬥狀態、格擋與受擊（11 支）

| clip | 說明 | 幀數 | loop | RM | 事件@幀 | 備註 |
|---|---|---:|:---:|:---:|---|---|
| `chr_block` | 格擋（舉起→維持→放下） | 30 | | | | 既有 |
| `chr_block_hit` | 格擋受擊（防禦震退回饋） | 16 | | | `ev_spawn_fx@2` | `[主控新增]` |
| `chr_perfect_block` | 完美格擋（150ms 彈反震擊） | 22 | | | `ev_spawn_fx@4, ev_hit@6, ev_end_lock@16` | `[主控新增]` |
| `chr_guard_break` | 破防硬直（架勢條滿崩解 1.5s） | 45 | | | | `[主控新增]` |
| `chr_stagger` | 失衡硬直（受破招／重擊暈眩） | 45 | | | | `[主控新增]` |
| `chr_dodge_miss` | 閃避（MISS 殘影） | 14 | | ✓ | | `[主控新增]` |
| `chr_weapon_draw` | 拔出武器（進入主控戰鬥） | 18 | | | `ev_spawn_fx@6` | `[主控新增]` |
| `chr_weapon_sheathe` | 收回武器（脫戰歸鞘） | 18 | | | | `[主控新增]` |
| `chr_hit_react` | 受擊 | 15 | | | | 既有 |
| `chr_knockdown` | 倒地 | 30 | | | | 既有 |
| `chr_getup` | 起身 | 30 | | | | 既有 |

### 2.3 主控主動技與共鳴支援（22 支）

| clip | 說明 | 幀數 | loop | RM | 事件@幀 | 適用 `grip_mode` / 距離 | 備註 |
|---|---|---:|:---:|:---:|---|---|---|
| `chr_atk_melee_front` | 近戰：正前（主控玩家施招） | 26 | | | `ev_hit@12, ev_end_lock@20` | `two_handed`, `one_hand_shield` / `melee` | `[主控新增]` |
| `chr_atk_melee_front_r` | 雙持近戰（右手）：正前快斬 | 22 | | | `ev_hit@9, ev_end_lock@16` | `dual_wield` / `melee` | `[主控新增]` |
| `chr_atk_melee_front_l` | 雙持近戰（左手）：正前快斬 | 22 | | | `ev_hit@9, ev_end_lock@16` | `dual_wield` / `melee` | `[主控新增]` |
| `chr_atk_melee_sweep` | 近戰：橫掃（主控玩家施招） | 30 | | | `ev_hit@14, ev_end_lock@24` | `two_handed`, `one_hand_shield` / `melee` | `[主控新增]` |
| `chr_atk_melee_sweep_r` | 雙持近戰（右手）：橫掃 | 25 | | | `ev_hit@11, ev_end_lock@19` | `dual_wield` / `melee` | `[主控新增]` |
| `chr_atk_melee_sweep_l` | 雙持近戰（左手）：橫掃 | 25 | | | `ev_hit@11, ev_end_lock@19` | `dual_wield` / `melee` | `[主控新增]` |
| `chr_atk_melee_burst` | 近戰：周身擴散（主控玩家施招） | 34 | | | `ev_spawn_fx@16, ev_hit@18` | 全模式 / `melee` | `[主控新增]` |
| `chr_atk_dash` | 突進：直線衝鋒攻擊 | 28 | | ✓ | `ev_hit@12, ev_end_lock@22` | `two_handed`, `one_hand_shield` | `[主控新增]` |
| `chr_atk_dash_r` | 雙持突進（右手）：疾風突刺 | 24 | | ✓ | `ev_hit@10, ev_end_lock@18` | `dual_wield` | `[主控新增]` |
| `chr_atk_dash_l` | 雙持突進（左手）：疾風突刺 | 24 | | ✓ | `ev_hit@10, ev_end_lock@18` | `dual_wield` | `[主控新增]` |
| `chr_atk_ranged_line` | 射擊：直線（主控玩家施招） | 30 | | | `ev_spawn_fx@14` | `two_handed`, `one_hand_shield` / `ranged` | `[主控新增]` |
| `chr_atk_ranged_line_r` | 雙持遠程（右手）：直線射擊／擲射 | 24 | | | `ev_spawn_fx@11, ev_end_lock@18` | `dual_wield` / `ranged` | `[主控新增]` |
| `chr_atk_ranged_line_l` | 雙持遠程（左手）：直線射擊／擲射 | 24 | | | `ev_spawn_fx@11, ev_end_lock@18` | `dual_wield` / `ranged` | `[主控新增]` |
| `chr_atk_ranged_cone` | 射擊：扇形（主控玩家施招） | 30 | | | `ev_spawn_fx@14` | `two_handed`, `one_hand_shield` / `ranged` | `[主控新增]` |
| `chr_atk_ranged_cone_r` | 雙持遠程（右手）：扇形散射 | 26 | | | `ev_spawn_fx@12, ev_end_lock@20` | `dual_wield` / `ranged` | `[主控新增]` |
| `chr_atk_ranged_cone_l` | 雙持遠程（左手）：扇形散射 | 26 | | | `ev_spawn_fx@12, ev_end_lock@20` | `dual_wield` / `ranged` | `[主控新增]` |
| `chr_atk_ranged_arc` | 射擊：拋物線（主控玩家施招） | 34 | | | `ev_spawn_fx@18` | `two_handed`, `one_hand_shield` / `ranged` | `[主控新增]` |
| `chr_atk_ranged_arc_r` | 雙持遠程（右手）：拋物線擲射 | 28 | | | `ev_spawn_fx@14, ev_end_lock@22` | `dual_wield` / `ranged` | `[主控新增]` |
| `chr_atk_ranged_arc_l` | 雙持遠程（左手）：拋物線擲射 | 28 | | | `ev_spawn_fx@14, ev_end_lock@22` | `dual_wield` / `ranged` | `[主控新增]` |
| `chr_atk_burst_target` | 遠程：指定目標點爆破引導 | 34 | | | `ev_spawn_fx@16, ev_hit@18` | 全模式 / `ranged` | `[主控新增]` |
| `chr_sup_self` | 輔助：自身（玩家共鳴施放） | 36 | | | `ev_spawn_fx@18` | 全模式 | `[主控新增]` |
| `chr_sup_ally` | 輔助：他者（支援追隨宙獸） | 36 | | | `ev_spawn_fx@18` | 全模式 | `[主控新增]` |

### 2.4 指令、召喚與招式組切換（8 支）

| clip | 說明 | 幀數 | loop | RM | 事件@幀 | 備註 |
|---|---|---:|:---:|:---:|---|---|
| `chr_moveset_switch` | 切換招式組合（共鳴換手，2s 鎖定） | 20 | | | `ev_spawn_fx@8, ev_end_lock@14` | `[主控新增]` |
| `chr_moveset_forced_switch` | 強制切換招式組合（追隨宙獸倒下輪替） | 22 | | | `ev_spawn_fx@6, ev_end_lock@16` | `[主控新增]` |
| `chr_command_point` | 命令：指向目標 | 24 | | | `ev_release@10` | 既有 |
| `chr_command_attack` | 命令：全力進攻 | 24 | | | `ev_release@10` | 既有 |
| `chr_command_recall` | 命令：後退集合 | 24 | | | `ev_release@10` | 既有 |
| `chr_command_overload` | 命令：觸發超載進化 | 30 | | | `ev_spawn_fx@14` | 既有 |
| `chr_summon` | 召喚宙獸 | 36 | | | `ev_spawn_fx@18` | 既有 |
| `chr_recall` | 收回宙獸 | 30 | | | `ev_spawn_fx@14` | 既有 |

### 2.5 道具、背包與投擲收服（8 支）

| clip | 說明 | 幀數 | loop | RM | 事件@幀 | 備註 |
|---|---|---:|:---:|:---:|---|---|
| `chr_item_use_self` | 使用道具（自身） | 40 | | | `ev_spawn_fx@24` | 既有 |
| `chr_item_use_other` | 使用道具（他者／宙獸） | 40 | | | `ev_release@20` | 既有 |
| `chr_field_deploy` | 佈署場地 | 48 | | | `ev_spawn_fx@30` | 既有 |
| `chr_backpack_open` | 使用背包（取下→翻找→收回） | 60 | | | | 既有 |
| `chr_handbook_open` | 翻閱冒險手冊／圖鑑 | 60 | ✓ | | | 既有 |
| `chr_throw_card` | 投擲：符籙卡片（雙指甩出） | 24 | | | `ev_release@12` | 既有 |
| `chr_throw_bead` | 投擲：琉璃珠（下手拋擲） | 28 | | | `ev_release@15` | 既有 |
| `chr_throw_cube` | 投擲：魔術方塊（轉動後上手投） | 32 | | | `ev_release@18` | 既有 |

### 2.6 生活採集、營火與鍛造（10 支）

| clip | 說明 | 幀數 | loop | RM | 事件@幀 | 備註 |
|---|---|---:|:---:|:---:|---|---|
| `chr_interact_pickup` | 近身互動／拾取素材 | 24 | | | `ev_release@10` | 既有 |
| `chr_gather_forage` | 採集植物／散佈物（彎腰採摘） | 42 | | | `ev_release@22` | 既有 |
| `chr_mine_pick` | 礦鎬採礦（揮鎬敲擊礦脈） | 36 | | | `ev_hit@16, ev_spawn_fx@16` | 既有 |
| `chr_fish_cast` | 釣魚：拋竿 | 30 | | | `ev_release@16` | 既有 |
| `chr_fish_wait` | 釣魚：持竿待機 | 60 | ✓ | | | 既有 |
| `chr_fish_reel` | 釣魚：拉竿收魚 | 36 | | | `ev_spawn_fx@20` | 既有 |
| `chr_cook_camp` | 營火料理（生火／翻炒烹飪） | 60 | ✓ | | `ev_spawn_fx@30` | 既有 |
| `chr_craft_forge` | 生活製作／鍛造加工 | 48 | ✓ | | `ev_hit@18, ev_spawn_fx@18` | 既有 |
| `chr_trap_place` | 佈置／回收採集陷阱 | 40 | | | `ev_spawn_fx@22` | 既有 |
| `chr_revive_ally` | 營火復甦／治療昏厥宙獸 | 54 | | | `ev_spawn_fx@28` | 既有 |

### 2.7 對話、撫摸與結算（9 支）

| clip | 說明 | 幀數 | loop | RM | 事件@幀 | 備註 |
|---|---|---:|:---:|:---:|---|---|
| `chr_talk_idle` | 對話待機 | 90 | ✓ | | | 既有 |
| `chr_talk_gesture` | 對話手勢 | 45 | | | | 既有 |
| `chr_pet_xs` | 撫摸 XS 體型（托在掌心輕撫） | 60 | | | `ev_spawn_fx@30` | 既有 |
| `chr_pet_s` | 撫摸 S 體型（蹲下摸頭） | 60 | | | `ev_spawn_fx@30` | 既有 |
| `chr_pet_m` | 撫摸 M 體型（彎腰） | 60 | | | `ev_spawn_fx@30` | 既有 |
| `chr_pet_l` | 撫摸 L 體型（抬手摸頸） | 60 | | | `ev_spawn_fx@30` | 既有 |
| `chr_pet_xl` | 撫摸 XL 體型（宙獸低頭，雙手撫摸） | 72 | | | `ev_spawn_fx@36` | 既有 |
| `chr_victory` | 勝利 | 60 | | | | 既有 |
| `chr_defeated` | 戰敗 | 45 | | | | 既有 |
