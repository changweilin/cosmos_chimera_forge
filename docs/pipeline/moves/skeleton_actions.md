# 招式施放動作與特效骨架掛點規格（`moves`）

> 對應資料來源：`Data/schemas/move.schema.json`、`catalog.js`（v2.17.0 `VFX`、`ACTIONS.character`、`ACTIONS.creature`、`GRIP_MODES`、`WEAPON_ANIM_GROUPS`）、`tasks.js`（`move-vfx`）。  
> 更新日期：2026-11-28（對齊「玩家主控＋宙獸追隨／供招＋BOSS 宙獸主控」雙端施放機制、10 類武器共用動作組 `WeaponAnimGroup` 與單手劍盾格擋同步攻擊 `chr_atk_sword_shield_guard_*`，同步 v2.17.0 動作擴充）。

---

## 1. 雙端施放掛點與裝備邊界

- **玩家主控（Player Master）施放掛點**：玩家切換使用追隨宙獸的招式組，由人類主控骨架播對應 `chr_atk_*` / `chr_sup_*` / `chr_field_deploy` 並從玩家掛點發出 VFX：
  - `Socket_HandR_Prop` / `Socket_HandL_Prop`（武器／盾牌揮斬與投射發射端）
  - `Socket_Front`（角色身體正前／直線／扇形／突進起始方向，依賴手部與身體軸線對齊）
  - `Socket_Head_FX`（頭頂狀態／共鳴換手光環／自我輔助起點）
- **宙獸追隨者／BOSS 主控（Creature Follower / BOSS Master）施放掛點**：宙獸不配備個人武器或盾牌，招式 VFX 一律由宙獸本體插槽骨發出：
  - `Socket_Front`（正前／直線／扇形／近戰衝擊起點）
  - `Socket_Mouth`（口部吐息／咆哮／光束起點）
  - `Socket_Core_FX`（自身／他者輔助、核心聚能、共鳴供招光環、目標點引導）
  - `Socket_Ground_FX`（場地展開、地面擴散波、落點警示印記、車輪戰登場印記）
- **武器與尺度規範**：角色依七槽裝備實裝武器／盾牌網格；宙獸本體無武器／無虛擬大手網格（`Socket_Weapon_R`／`Socket_Weapon_L` 僅作遺留／BOSS 演出參考）。招式 VFX 本體須通用於兩端施放者，尺寸依施放者體型（角色基準／宙獸 `XS`–`XL`）在 `spec.json` `geometry.note` 寫明縮放倍率。

---

## 2. 招式形態與雙端施放動作對照

| `move.schema.json` 形態參數 | VFX `shape` | 施放者動作 (`chr_` / `cr_`) | 雙持 (`dual_wield`) 交替動作 | 幀數／事件／RM | 玩家／宙獸主要發射掛點 | 備註 |
|---|---|---|---|---|---|---|
| `shape: "front"` | `melee_front` | `atk_melee_front` | `atk_melee_front_r` / `_l` | 26f (`22f` 雙持) · `ev_hit`, `ev_end_lock` | 玩家 `Socket_HandR_Prop` / 宙獸 `Socket_Front` | 近戰正前打擊 |
| `shape: "sweep"` | `melee_sweep` | `atk_melee_sweep` | `atk_melee_sweep_r` / `_l` | 30f (`25f` 雙持) · `ev_hit`, `ev_end_lock` | 玩家 `Socket_HandR_Prop` / 宙獸 `Socket_Front` | 近戰扇形橫掃 |
| `shape: "burst"`, `origin: "caster"` | `melee_burst` | `atk_melee_burst` | `atk_melee_burst`（共用） | 34f · `ev_spawn_fx@16`, `ev_hit@18` | 玩家 `Socket_Head_FX` / 宙獸 `Socket_Core_FX` | 以施放者為中心擴散 |
| `shape: "burst"`, `origin: "target"` | `melee_burst`（遠程目標點） | `atk_burst_target` | `atk_burst_target`（共用） | 34f · `ev_spawn_fx@16`, `ev_hit@18` | 施放端引導 → 目標 `Ground` | 限 `mid`/`long` 距，先出目標點警示印記再爆破 |
| `shape: "line"`, `movement: "dash"` | `ranged_line`（突進路徑） | `atk_dash` | `atk_dash_r` / `_l` | 28f (`24f` 雙持) · **RM=✓** · `ev_hit`, `ev_end_lock` | `Socket_Front` / 宙獸 `Socket_Ground_FX` | 帶位移突進衝鋒（`base_range_mm` 1..36000） |
| `shape: "line"`, `movement: "none"` | `ranged_line` | `atk_ranged_line` | `atk_ranged_line_r` / `_l` | 30f (`24f` 雙持) · `ev_spawn_fx` | 玩家 `Socket_HandR_Prop` / 宙獸 `Socket_Front` / `Mouth` | 直線投射／射線 |
| `shape: "cone"` | `ranged_cone` | `atk_ranged_cone` | `atk_ranged_cone_r` / `_l` | 30f (`26f` 雙持) · `ev_spawn_fx` | `Socket_Front` / 宙獸 `Socket_Mouth` | 扇形散射／吐息 |
| `shape: "arc"` | `ranged_arc` | `atk_ranged_arc` | `atk_ranged_arc_r` / `_l` | 34f (`28f` 雙持) · `ev_spawn_fx` | 玩家 `Socket_HandR_Prop` / 宙獸 `Socket_Front` | 拋物線投擲／落點指示 |
| `shape: "self"` | `support_self` | `sup_self` | `sup_self`（共用） | 36f · `ev_spawn_fx@18` | 玩家 `Socket_Head_FX` / 宙獸 `Socket_Core_FX` | 自身增益／護盾／回復 |
| `shape: "ally"` | `support_ally` | `sup_ally` | `sup_ally`（共用） | 36f · `ev_spawn_fx@18` | 玩家 `Socket_Head_FX` / 宙獸 `Socket_Core_FX` | 友方目標增益／治療 |
| `shape: "field"` | `field` | `field_deploy` | `field_deploy`（共用） | 48f · `ev_spawn_fx@30` (人) / `28` (獸) | `Socket_Ground_FX`（玩家位置／宙獸地面） | 持續場地（依 `field_duration_ms` 週期跳動） |

---

## 3. 實戰／切換／BOSS 關聯通用特效與動作節奏

除上述 9 種招式形態外，通用特效與施放時序須對齊以下動作事件：

- **招式組切換／強制輪替（`chr_moveset_switch` / `chr_moveset_forced_switch`）**：20f `ev_spawn_fx@8`（2 秒切換鎖定共鳴波紋）／22f `ev_spawn_fx@6`（追隨宙獸倒下強制切手警示閃光）。
- **追隨供招／車輪戰上場（`cr_link_channel` / `cr_relay_enter`）**：40f loop `ev_spawn_fx@10`（連結供招流光呼應）／32f `ev_spawn_fx@14`（替補宙獸衝場落地陣紋）。
- **BOSS 主控切換與號召（`boss_moveset_switch` / `boss_summon_follower` / `boss_enrage`）**：26f `ev_spawn_fx@10`／36f `ev_spawn_fx@16`（喚出第二隻或車輪戰替補）／48f `ev_spawn_fx@18`（全周威嚇衝擊波）。
- **完美格擋彈反（`perfect_block`）／格擋受擊（`block_hit`）**：22f `ev_spawn_fx@4, ev_hit@6`／16f `ev_spawn_fx@2`（防禦盾波與震退粒子）。
- **生活能力／生態／超載**：`field_utility`（42f `ev_spawn_fx@20`）、`wild_alert`（36f `ev_spawn_fx@12`）、`eat_feed`（48f `ev_spawn_fx@24`）、`command_overload`（30f `ev_spawn_fx@14`）對應 `overload_enter`（60f `ev_spawn_fx@20`）。
- **蹲下起身施放銜接**：角色或宙獸處於蹲下狀態發動主動技、輔助／場地、使用道具、投擲或捕獲等動作時，須先站立回歸站姿再觸發上述標準站立 `atk_*`／`sup_*`／`field_deploy` clip，不另製作獨立蹲下施放動作。
