<!-- COSMI-PIPELINE/3:blender -->
# Blender Image-to-3D｜{{subject_label}}
{{model_input}}
參數：{{parameters_path}}
輸出：{{output_path}}/
{{rig_plan}}
{{action_plan}}
依已核准立繪製作該角色的完整網格、材質、骨架、蒙皮及動作（依 `skeleton_actions.md`：85 動作含蹲下 4 支與角色七槽裝備掛點；蹲下攻擊／道具／投擲／捕獲須先站立再播站立 clip）；保留臉部、服裝與配飾辨識細節（不含 UMA 創造的 NPC）。
依 blender-anime-character 技能逐件確認衣物、吊掛飾物及髮束的固定端與自由端，測試世界重力、運動慣性、回擺及穿模，並驗證匯出動畫。
先以代表角色做固定曝光臉部對照及同動作回擺量測，驗證後逐角調整並更新模型目錄。
檢查各視角、關節變形與貼圖，重開 .blend 並重匯入 .glb 驗證。
交付 models/{{asset_id}}.blend、models/{{asset_id}}.glb、rig/、animations/、previews/ 與 manifest.json。
