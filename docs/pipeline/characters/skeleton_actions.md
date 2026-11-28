# 角色骨架與動作規格（`characters`）

> 對應資料來源：`catalog.js`（v2.17.0 `ACTIONS.character`、`WEAPON_ANIM_GROUPS`、`SKELETON_SPECS.character`）、`tasks.js`（`character-model-rig` v5.4.0）、`Data/character-anims/character-anims.json`（`cosmimera-character-anim/1`）。  
> 更新日期：2026-11-28（共 **142** 支動作：新增 **51** 支 10 類武器共用動作組與劍盾格擋同步攻擊＋水中潛行／飛行／攀爬 **6** 支＋蹲下 **4** 支＋主控戰鬥 **31** 支＋既有 **50** 支完整相容；對齊 T-pose、MPFB `game_engine`、`sw_*` 彈簧骨、`Idle_Art`、16 個 `CharacterAnimatorDriver` 參數與 ADR-0015 撤回）。

---

## 1. 骨架體系與七槽角色專屬裝備（Unity Humanoid／MPFB `game_engine`）

- **適用範圍（ADR-0015 已撤回）**：本 Humanoid／MPFB（`game_engine`）高模產線僅適用於**玩家主角與可控英雄**（`chr_roen` 等）；路人、訓練家與任務 NPC 維持純程式化 `NpcMeshes`，不製作 UMA 或獨立高模動作。
- **骨骼上限與綁定基準**：≤ 75 骨骼，**T-pose** 綁定（`bind_pose: "t_pose"`）；立繪擺拍展示 clip `Idle_Art` 須另外匯出為獨立僅骨架 FBX（`<id>_acg@Idle_Art.fbx`）。
- **雙命名相容（`AcgCharacterImport.cs`）**：
  - **標準 Unity Humanoid 命名**：`Hips` → `Spine` → `Chest` → `UpperChest` → `Neck` → `Head`；`Shoulder` → `Arm` → `ForeArm` → `Hand`（含手指三節 `Thumb` / `Index` / `Middle` / `Ring` / `Little`）；`UpLeg` → `Leg` → `Foot` → `Toes`
  - **MPFB `game_engine` 命名**：`pelvis` → `spine_01..03` → `neck_01` → `head`；`upperarm_l/r` → `lowerarm_l/r` → `hand_l/r`；`thigh_l/r` → `calf_l/r` → `foot_l/r`
- **彈簧物理與左側道具屬性**：
  - 頭髮、裙襬、披風物理鏈改用 `sw_*` 前綴（如 `sw_hair_*`、`sw_skirt*`），末端接零權重 `..._end` 骨由 `SpringBones.cs` 與 `AcgSpringImport.cs` 驅動（非彈簧鏈附屬骨保留 `Extra_*`）。
  - 左側手持收服道具網格（`cube`／`bead`／`talisman`）須於 Blender／FBX 標註 user properties `acg_prop` 與 `acg_hidden`（供 `AcgPropImport.cs` 識別）。
- **插槽骨（Sockets · 7 個，對應全遊戲唯一的角色七槽裝備系統）**：
  - `Socket_HandR_Prop`（`main_hand` 主手武器／礦鎬／釣竿／廚具／收服器掛點）
  - `Socket_HandL_Prop`（`off_hand` 副手武器／盾牌／手持道具／冒險手冊掛點）
  - `Socket_Head_Armor`（`head` 頭盔防具掛點，對應 2× 防具詞綴／數值擴充）
  - `Socket_Hands_Armor`（`hands` 手套／護手防具掛點，對應 2× 防具詞綴／數值擴充）
  - `Socket_Back_Pack`（背包／披風掛點；另含 `upper` 上身護甲、`lower` 下身護甲由蒙皮更換，`accessory` 飾品無獨立網格）
  - `Socket_Throw`（投擲收服道具／道具出手基準點）
  - `Socket_Head_FX`（頭頂／共鳴狀態／情緒特效掛點）
- **裝備歸屬、雙持過濾與 Runtime Animator 16 參數**：
  - 全部 7 個裝備槽位（`main_hand`、`off_hand`、`head`、`upper`、`hands`、`lower`、`accessory`）皆由玩家角色穿戴與持握，宙獸無個人裝備。
  - `CharacterAnimatorDriver` 共用 16 個 Animator 參數：`Speed`, `IsGrounded`, `IsCrouching`, `InCombat`, `IsBlocking`, `IsRolling`, `IsStaggered`, `IsGuardBroken`, `WeaponAnimGroup`（`0..9`，對應下表 10 類武器共用動作組）, `Attack`, `BlockAttack`（劍盾於格擋中同步攻擊觸發器）, `MoveSetSwitch`, `StandUp`（`CrouchPosture` 120 ms 起身過渡）, `CrouchJump`, `UseItem`, `ThrowCapture`。
  - 角色預設產出支援全持握模式（`two_handed`／`dual_wield`／`one_hand_shield`）；若指定單一 `grip_mode`，則依 `Data/character-anims/character-anims.json` 過濾 `_r`/`_l`、通用攻擊與各武器動作組 clip（`dual_wield` 僅用 `_r`/`_l`＋雙持適用武器組＋全模式 clip，其餘僅用無 `_r`/`_l` 通用 clip 與對應武器組）。

### 1.1 10 類共用武器動作組（`WEAPON_ANIM_GROUPS`）

| `WeaponAnimGroup` | index | 共用武器類型 (`weapon_types`) | 與空手共用 | 格擋同步攻擊 | 說明 |
|---|---:|---|:---:|:---:|---|
| `unarmed_fist` | 0 | `unarmed`, `fist_katar` | ✓ | | 空手與拳套／拳劍共用近身搏擊與突進拳勢 |
| `sword_1h` | 1 | `sword_1h` | | ✓ | 單手劍／彎刀；搭盾時可於格擋中觸發 `BlockAttack` 同步攻擊（傷害 50%） |
| `sword_2h` | 2 | `greatsword` | | | 雙手大劍重型揮砍與縱劈動作組 |
| `axe_1h` | 3 | `axe_1h`, `mace_1h` | | | 單手斧與單手錘共用重揮與砸擊動作組 |
| `axe_hammer_2h` | 4 | `greataxe_hammer` | | | 雙手巨斧與重錘共用蓄力旋揮與砸地動作組 |
| `dagger_wand_1h` | 5 | `dagger_claw`, `thrown_shuriken`, `wand_gun` | | | 匕首、飛刃與手銃／短魔杖共用單手靈巧揮甩動作組 |
| `staff_2h` | 6 | `magic_staff` | | | 雙手長法杖導引與施法舉杖動作組 |
| `spear_2h` | 7 | `twinblade_staff`, `spear_halberd`, `javelin` | | | 雙頭刃杖、長槍戟與標槍共用刺擊、橫掃與投擲動作組 |
| `bow_shield_offhand` | 8 | `hand_crossbow`, `repeater_bow`, `longbow` | | | 手弩、連弩與長弓共用舉弓瞄準與齊射動作組（手弩可搭盾） |
| `staff_cannon_2h` | 9 | `heavy_crossbow_cannon` | | | 重弩重砲共用雙手肩扛架設與後座射擊動作組 |

---

## 2. 動作清單（30 fps · 共 142 支）

> 標記 `[武器組新增]` 為 v2.17 新增之 10 類武器共用動作組與劍盾格擋同步攻擊 **51** 支；`[立體移動新增]` 為 v2.16 新增之潛水／飛行／攀爬 **6** 支；`[主控新增]` 為「玩家主控作戰＋兩隻宙獸追隨／供招」機制擴充的 31 支動作；`[蹲下新增]` 為 v2.15 新增的 4 支蹲下動作；既有 50 支 clip ID 全數保留相容。  
> **蹲下與起身銜接規範**：蹲下狀態僅額外製作 `chr_crouch_move`、`chr_crouch_roll`、`chr_crouch_jump`、`chr_crouch_block` 四支低姿動作；蹲下時發動攻擊（`chr_atk_*`／`chr_sup_*`）、使用道具（`chr_item_use_*`）、投擲或捕獲（`chr_throw_*`）、佈署場地或召喚／指令等動作，**須先經 `StandUp`（120 ms）回歸站姿後再接續對應標準站立 clip**，不另製作獨立蹲下攻擊／道具／投擲／捕獲動畫。

### 2.1 基礎移動與穿越（22 支）

| clip | 說明 | 幀數 | loop | RM | 事件@幀 | 備註 |
|---|---|---:|:---:|:---:|---|---|
| `chr_idle` | 待機（2 秒短週期呼吸律動） | 60 | ✓ | | | 既有 |
| `chr_idle_long` | 長時間靜止週期動作（4 秒定力循環） | 120 | ✓ | | | 既有 |
| `chr_walk` | 走路 | 32 | ✓ | | `ev_footstep@8, ev_footstep@24` | 既有 |
| `chr_run` | 奔跑 | 22 | ✓ | | `ev_footstep@5, ev_footstep@16` | 既有 |
| `chr_sneak_idle` | 潛行待機 | 60 | ✓ | | | 既有 |
| `chr_sneak_move` | 潛行移動 | 40 | ✓ | | | 既有 |
| `chr_crouch_move` | 蹲下移動（壓低重心緩行） | 38 | ✓ | | `ev_footstep@10, ev_footstep@29` | `[蹲下新增]` |
| `chr_crouch_roll` | 蹲下翻滾（低姿翻滾閃避，無敵幀） | 20 | | ✓ | `ev_end_lock@16` | `[蹲下新增]` |
| `chr_crouch_jump` | 蹲下跳躍（低姿蓄力起跳／滯空／落地） | 30 | | | | `[蹲下新增]` |
| `chr_roll_dodge` | 翻滾閃避（無敵幀） | 20 | | ✓ | `ev_end_lock@16` | 既有 |
| `chr_jump` | 跳躍（起跳／滯空／落地） | 30 | | | | 既有 |
| `chr_swim_idle` | 水面漂浮待機 | 60 | ✓ | | | 既有 |
| `chr_swim_move` | 游泳移動 | 36 | ✓ | | | 既有 |
| `chr_dive_idle` | 潛水懸停待機 | 60 | ✓ | | | `[立體移動新增]` |
| `chr_dive_move` | 潛水游動（立體水下推進） | 36 | ✓ | | | `[立體移動新增]` |
| `chr_fly_idle` | 飛行／浮空懸停待機 | 60 | ✓ | | | `[立體移動新增]` |
| `chr_fly_move` | 飛行／浮空移動 | 32 | ✓ | | | `[立體移動新增]` |
| `chr_climb_idle` | 攀爬靜止懸掛（岩壁待機） | 60 | ✓ | | | `[立體移動新增]` |
| `chr_climb_move` | 攀爬移動（四肢交替上攀） | 32 | ✓ | | | `[立體移動新增]` |
| `chr_glide` | 滑翔滯空（乘風／高空移動） | 45 | ✓ | | | 既有 |
| `chr_mount_idle` | 騎乘待機（坐姿握鞍） | 60 | ✓ | | | 既有 |
| `chr_mount_run` | 騎乘奔跑（騎乘衝刺） | 24 | ✓ | | | 既有 |

### 2.2 主控戰鬥狀態、格擋與受擊（12 支）

| clip | 說明 | 幀數 | loop | RM | 事件@幀 | 備註 |
|---|---|---:|:---:|:---:|---|---|
| `chr_block` | 格擋（舉起→維持→放下） | 30 | | | | 既有 |
| `chr_crouch_block` | 蹲下格擋（低重心舉武／舉盾防禦） | 28 | | | | `[蹲下新增]` |
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

### 2.8 各武器共用動作組與劍盾格擋同步攻擊（51 支）

| clip | `weapon_anim_group` | 說明 | 幀數 | loop | RM | 事件@幀 | 適用 `grip_mode` / 距離 |
|---|---|---|---:|:---:|:---:|---|---|
| `chr_wpn_unarmed_fist_idle` | `unarmed_fist` | 空手／拳劍待機（共用） | 60 | ✓ | | | `dual_wield`, `one_hand_shield` / `any` |
| `chr_wpn_unarmed_fist_block` | `unarmed_fist` | 空手／拳劍架招格擋（共用） | 28 | | | | `dual_wield`, `one_hand_shield` / `any` |
| `chr_atk_unarmed_fist_front` | `unarmed_fist` | 空手／拳劍連拳直擊（共用） | 20 | | | `ev_hit@8` | `dual_wield`, `one_hand_shield` / `melee` |
| `chr_atk_unarmed_fist_sweep` | `unarmed_fist` | 空手／拳劍迴旋橫掃（共用） | 24 | | | `ev_hit@10` | `dual_wield`, `one_hand_shield` / `melee` |
| `chr_atk_unarmed_fist_dash` | `unarmed_fist` | 空手／拳劍突進衝拳（共用） | 22 | | ✓ | `ev_hit@9` | `dual_wield`, `one_hand_shield` / `melee` |
| `chr_wpn_sword_1h_idle` | `sword_1h` | 單手劍待機 | 60 | ✓ | | | `dual_wield`, `one_hand_shield` / `any` |
| `chr_wpn_sword_1h_block` | `sword_1h` | 單手劍／劍盾格擋 | 28 | | | | `dual_wield`, `one_hand_shield` / `any` |
| `chr_atk_sword_1h_front` | `sword_1h` | 單手劍正面斬擊 | 24 | | | `ev_hit@10` | `dual_wield`, `one_hand_shield` / `melee` |
| `chr_atk_sword_1h_sweep` | `sword_1h` | 單手劍弧線橫斬 | 28 | | | `ev_hit@12` | `dual_wield`, `one_hand_shield` / `melee` |
| `chr_atk_sword_1h_dash` | `sword_1h` | 單手劍踏步突刺 | 26 | | ✓ | `ev_hit@11` | `dual_wield`, `one_hand_shield` / `melee` |
| `chr_atk_sword_shield_guard_front` | `sword_1h` | 劍盾格擋反擊（舉盾持守同步直刺，傷害減半） | 24 | | | `ev_hit@10` | `one_hand_shield` / `melee` |
| `chr_atk_sword_shield_guard_sweep` | `sword_1h` | 劍盾格擋反擊（舉盾持守護身橫斬，傷害減半） | 26 | | | `ev_hit@12` | `one_hand_shield` / `melee` |
| `chr_atk_sword_shield_guard_dash` | `sword_1h` | 劍盾格擋突刺（舉盾前衝同步刺擊，傷害減半） | 26 | | ✓ | `ev_hit@11` | `one_hand_shield` / `melee` |
| `chr_wpn_sword_2h_idle` | `sword_2h` | 大劍雙手待機 | 60 | ✓ | | | `two_handed` / `any` |
| `chr_wpn_sword_2h_block` | `sword_2h` | 大劍雙手橫架格擋 | 32 | | | | `two_handed` / `any` |
| `chr_atk_sword_2h_front` | `sword_2h` | 大劍雙手縱劈 | 30 | | | `ev_hit@14` | `two_handed` / `melee` |
| `chr_atk_sword_2h_sweep` | `sword_2h` | 大劍大範圍橫掃 | 34 | | | `ev_hit@16` | `two_handed` / `melee` |
| `chr_atk_sword_2h_dash` | `sword_2h` | 大劍踏步突進重劈 | 30 | | ✓ | `ev_hit@14` | `two_handed` / `melee` |
| `chr_wpn_axe_1h_idle` | `axe_1h` | 單手斧／錘待機 | 60 | ✓ | | | `dual_wield`, `one_hand_shield` / `any` |
| `chr_wpn_axe_1h_block` | `axe_1h` | 單手斧／錘格擋 | 28 | | | | `dual_wield`, `one_hand_shield` / `any` |
| `chr_atk_axe_1h_front` | `axe_1h` | 單手斧／錘前劈重砸 | 26 | | | `ev_hit@12` | `dual_wield`, `one_hand_shield` / `melee` |
| `chr_atk_axe_1h_sweep` | `axe_1h` | 單手斧／錘橫揮 | 30 | | | `ev_hit@14` | `dual_wield`, `one_hand_shield` / `melee` |
| `chr_atk_axe_1h_dash` | `axe_1h` | 單手斧／錘衝鋒劈擊 | 28 | | ✓ | `ev_hit@12` | `dual_wield`, `one_hand_shield` / `melee` |
| `chr_wpn_axe_hammer_2h_idle` | `axe_hammer_2h` | 雙手巨斧／重錘待機 | 60 | ✓ | | | `two_handed` / `any` |
| `chr_wpn_axe_hammer_2h_block` | `axe_hammer_2h` | 雙手巨斧／重錘架撐格擋 | 34 | | | | `two_handed` / `any` |
| `chr_atk_axe_hammer_2h_front` | `axe_hammer_2h` | 雙手巨斧／重錘全力下砸 | 34 | | | `ev_hit@16` | `two_handed` / `melee` |
| `chr_atk_axe_hammer_2h_sweep` | `axe_hammer_2h` | 雙手巨斧／重錘重旋橫掃 | 36 | | | `ev_hit@18` | `two_handed` / `melee` |
| `chr_atk_axe_hammer_2h_dash` | `axe_hammer_2h` | 雙手巨斧／重錘突進砸地 | 32 | | ✓ | `ev_hit@15` | `two_handed` / `melee` |
| `chr_wpn_dagger_wand_1h_idle` | `dagger_wand_1h` | 匕首／飛刃／手銃待機 | 60 | ✓ | | | `dual_wield`, `one_hand_shield` / `any` |
| `chr_wpn_dagger_wand_1h_block` | `dagger_wand_1h` | 匕首／短持靈巧招架 | 26 | | | | `dual_wield`, `one_hand_shield` / `any` |
| `chr_atk_dagger_wand_1h_front` | `dagger_wand_1h` | 匕首二連穿刺 | 20 | | | `ev_hit@8` | `dual_wield`, `one_hand_shield` / `melee` |
| `chr_atk_dagger_wand_1h_sweep` | `dagger_wand_1h` | 匕首迴身弧斬 | 24 | | | `ev_hit@10` | `dual_wield`, `one_hand_shield` / `melee` |
| `chr_atk_dagger_wand_1h_ranged` | `dagger_wand_1h` | 飛刃／手銃／魔杖單手射擊 | 24 | | | `ev_spawn_fx@11` | `dual_wield`, `one_hand_shield` / `ranged` |
| `chr_wpn_staff_2h_idle` | `staff_2h` | 雙手法杖待機 | 60 | ✓ | | | `two_handed` / `any` |
| `chr_atk_staff_2h_line` | `staff_2h` | 雙手法杖直線施法 | 30 | | | `ev_spawn_fx@14` | `two_handed` / `ranged` |
| `chr_atk_staff_2h_cone` | `staff_2h` | 雙手法杖扇面詠唱 | 30 | | | `ev_spawn_fx@14` | `two_handed` / `ranged` |
| `chr_atk_staff_2h_arc` | `staff_2h` | 雙手法杖高舉拋射 | 34 | | | `ev_spawn_fx@18` | `two_handed` / `ranged` |
| `chr_wpn_spear_2h_idle` | `spear_2h` | 槍戟／長柄／標槍待機 | 60 | ✓ | | | 全模式 / `any` |
| `chr_wpn_spear_2h_block` | `spear_2h` | 槍戟／長柄橫欄格擋 | 30 | | | | 全模式 / `any` |
| `chr_atk_spear_2h_front` | `spear_2h` | 槍戟／雙頭刃直刺 | 26 | | | `ev_hit@12` | 全模式 / `melee` |
| `chr_atk_spear_2h_sweep` | `spear_2h` | 槍戟／雙頭刃長柄橫掃 | 30 | | | `ev_hit@14` | 全模式 / `melee` |
| `chr_atk_spear_2h_dash` | `spear_2h` | 槍戟疾衝突刺 | 28 | | ✓ | `ev_hit@12` | 全模式 / `melee` |
| `chr_atk_spear_2h_ranged` | `spear_2h` | 標槍助跑投擲／長柄能量投射 | 28 | | | `ev_spawn_fx@14` | 全模式 / `ranged` |
| `chr_wpn_bow_idle` | `bow_shield_offhand` | 弓／弩搭箭瞄準待機 | 60 | ✓ | | | 全模式 / `any` |
| `chr_atk_bow_line` | `bow_shield_offhand` | 弓／弩直線射擊 | 26 | | | `ev_spawn_fx@12` | 全模式 / `ranged` |
| `chr_atk_bow_cone` | `bow_shield_offhand` | 弓／弩多矢扇射 | 28 | | | `ev_spawn_fx@13` | 全模式 / `ranged` |
| `chr_atk_bow_arc` | `bow_shield_offhand` | 弓／弩曲射齊發 | 30 | | | `ev_spawn_fx@15` | 全模式 / `ranged` |
| `chr_wpn_cannon_2h_idle` | `staff_cannon_2h` | 重弩重砲肩扛待機 | 60 | ✓ | | | `two_handed` / `any` |
| `chr_atk_cannon_2h_line` | `staff_cannon_2h` | 重弩重砲貫穿直射 | 34 | | | `ev_spawn_fx@16` | `two_handed` / `ranged` |
| `chr_atk_cannon_2h_cone` | `staff_cannon_2h` | 重弩重砲擴散砲擊 | 34 | | | `ev_spawn_fx@16` | `two_handed` / `ranged` |
| `chr_atk_cannon_2h_arc` | `staff_cannon_2h` | 重弩重砲曲射砲擊 | 36 | | | `ev_spawn_fx@18` | `two_handed` / `ranged` |
