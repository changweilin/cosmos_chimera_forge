<!-- COSMI-PIPELINE/3:passive_vfx -->
# 本被動技效果提示動畫
對象：{{subject_id}}
只依當前被動技的名稱、屬性、發揮影響力之觸發時機（如攻擊強化於發動攻擊時、防禦強化於被攻擊時、異常類於成功造成對手異常狀態時）、提示樣式與星級強度製作輕量視覺提示。
核心規則：本特效**純屬表現層視覺提示，不影響戰鬥系統規則層**（`visual_only: true`、`affects_combat_rules: false`、`hit_stop_ms: 0`、無震屏與動作鎖定），且**不連續重疊出現**（單次 350–800 ms 不循環、`non_overlapping: true`、`retrigger_policy: "ignore_while_active"`、`min_interval_ms: 1500`–`2000`、`max_concurrent_per_unit: 1`），低遮擋且不覆蓋主招判定體或敵方前搖預警圈。
必要的示範持有者資訊僅限體型與掛點（玩家主控端 `Socket_Head_FX`/`Socket_HandR_Prop`/`Socket_HandL_Prop` 或腳底原點；宙獸追隨／BOSS 主控端 `Socket_Core_FX`/`Socket_Ground_FX`）；未選持有者時不包含宙獸資訊。
輸出本被動技的 `pfx_*_spec.json`、四格分鏡、分層拆解與單次播放序列圖（不循環）。
