<!-- COSMI-PIPELINE/3:blender -->
# Blender Prompt-to-3D｜{{subject_label}}
{{model_input}}
參數：{{parameters_path}}
輸出：{{output_path}}/
{{rig_plan}}
{{action_plan}}
依純文字外觀與圖鑑製作該宙獸的完整網格、材質、骨架、蒙皮及動作（依 `skeleton_actions.md`：68 動作含蹲下 4 支、追隨與 BOSS 主控，`Socket_Weapon_R`/`L` 空掛點且不繪製武器與虛擬大手；蹲下攻擊／互動須先站立再播站立 clip）；保留臉部／感知器官與體表構造的辨識細節，無需補繪立繪。
檢查各視角、關節變形與貼圖，重開 .blend 並重匯入 .glb 驗證。
交付 models/{{asset_id}}.blend、models/{{asset_id}}.glb、rig/、animations/、previews/ 與 manifest.json。
