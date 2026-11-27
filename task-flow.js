// The task chooser mirrors the asset pipeline; keep it independent of DOM and task templates.
(function () {
  "use strict";
  const categories = Object.freeze([
    { id: "character", zh: "角色", icon: "👤", concept: "character-concept", model: "character-model-rig" },
    { id: "creature", zh: "宙獸", icon: "🐉", concept: "creature-concept", model: "creature-model-rig" },
    { id: "move", zh: "主動技", icon: "✨", concept: "move-vfx", passive: "passive-vfx", model: null }
  ]);
  const flow = Object.freeze({
    character: [
      { id: "appearance", stage: "appearance", task: "concept", name: "外觀設定與生成圖鑑", detail: "設計角色外觀與辨識特徵（不含 UMA 創造的 NPC），並依概念參數建立角色專屬獨立圖鑑（存於 characters/<id>/），不混入 3D 或交付指令。", output: "<id>_00_appearance.md、<id>_05_wiki.md" },
      { id: "portrait", stage: "portrait", task: "concept", name: "生成立繪（Prompt-to-Image）", detail: "正面基準圖 → 多視角三視圖 ＋ 動態主立繪；可選手動複製或 Drive 自動模式。", output: "立繪圖片" },
      { id: "review_portrait", stage: "review_portrait", task: "concept", name: "立繪審查", detail: "核對各視角一致性與缺陷；通過後才允許圖片建模。", output: "立繪審查紀錄" },
      { id: "image_blender", stage: "blender", task: "model", name: "AI + Blender（Image-to-3D）", detail: "使用已核准立繪（看圖 AI 畫），由 AI 操作 Blender 建模、綁骨、製作動作及檢查。", output: ".glb ＋ .blend、骨架、動作、QA" },
      { id: "review_3d", stage: "review_3d", task: "model", name: "最終驗收", detail: "檢查模型與已核准立繪、材質、骨架、動作及 manifest；人工確認後才歸檔。", output: "最終審查紀錄" }
    ],
    creature: [
      { id: "appearance", stage: "appearance", task: "concept", name: "外觀設定與生成圖鑑", detail: "先確定原創宙獸外觀與辨識特徵，並建立目前型態獨立 Markdown 圖鑑；無需生成立繪。", output: "<id>_<stage>_00_appearance.md、<id>_<stage>_05_wiki.md" },
      { id: "prompt_3d", stage: "blender", task: "model", name: "AI + Blender（Prompt-to-3D）", detail: "直接以文字（AI 直接畫）在 Blender 原創建模、綁骨、製作動作並輸出 .glb／.blend；引用獨立圖鑑。", output: ".glb ＋ .blend；關聯 wiki 路徑" },
      { id: "review_3d", stage: "review_3d", task: "model", name: "最終驗收", detail: "檢查已完成的 3D 模型、材質、骨架、動作與 manifest；Prompt-to-3D 無需補立繪，缺 .glb／.blend 不得通過。", output: "最終審查紀錄" }
    ],
    move: [
      { id: "encyclopedia", stage: "encyclopedia", task: "concept", name: "生成主動技圖鑑", detail: "先按主動技的屬性、功能、外觀與動作需求生成獨立 Markdown 圖鑑，存於 moves/<id>/。", output: "moves/<id>/<id>_05_wiki.md" },
      { id: "move_vfx", stage: "move_vfx", task: "concept", name: "主動技 3D 特效設計（Prompt-to-3D）", detail: "獨立主動技圖鑑條目：設定屬性、形狀與強度，生成規格、六格分鏡、分層拆解、序列圖與 .fbx。施放者僅用於示範。", output: "spec.json、storyboard、layers、flipbook、.fbx" },
      { id: "passive_vfx", stage: "passive_vfx", task: "passive", name: "被動技 3D 效果提示設計（Prompt-to-3D）", detail: "獨立被動技圖鑑條目：僅於被動效果發揮影響力時短暫提示，不影響戰鬥系統、不連續重疊；生成規格、四格分鏡、分層拆解與序列圖。", output: "pfx_*_spec.json、storyboard、layers、flipbook" }
    ]
  });
  function category(id) { return categories.find(c => c.id === id) || null; }
  function defaultRoute(kind) {
    return kind === "move" ? "move" : kind === "creature" ? "text" : kind === "character" ? "image" : null;
  }
  function steps(kind, route) {
    if (!category(kind)) return [];
    if (kind === "move") return (!route || route === "move") ? flow.move : [];
    if (kind === "character") return (!route || route === "image") ? flow.character : [];
    if (kind === "creature") return (!route || route === "text") ? flow.creature : [];
    return [];
  }
  function resolve(kind, route, stepId) {
    const c = category(kind);
    const activeRoute = route || defaultRoute(kind);
    const selected = steps(kind, activeRoute).find(s => s.id === stepId);
    if (!c || !selected) return null;
    return { category: kind, route: activeRoute, step: stepId,
      taskId: selected.task === "model" ? c.model : selected.task === "passive" ? c.passive : c.concept, ...selected };
  }
  function infer(taskId, stage, opts) {
    const c = categories.find(x => x.concept === taskId || x.model === taskId || x.passive === taskId);
    if (!c) return null;
    if (c.id === "move") return { category: "move", route: "move", step: taskId === "passive-vfx" || stage === "passive_vfx" ? "passive_vfx" : "move_vfx" };
    const route = defaultRoute(c.id);
    const list = steps(c.id, route);
    let step = stage === "blender" ? (c.id === "creature" ? "prompt_3d" : "image_blender") :
      list.some(x => x.id === stage) ? stage : "appearance";
    return { category: c.id, route, step };
  }
  function diagram(kind) {
    const list = steps(kind, defaultRoute(kind));
    return list.map((step, i) => ({
      type: "step",
      shared: kind !== "move" && (i === 0 || i === list.length - 1),
      steps: [step]
    }));
  }
  // Explicit chooser state machine: category must be chosen before route and node.
  function selectCategory(kind) {
    return category(kind) ? { category: kind, route: null, step: null } : null;
  }
  function selectRoute(choice, route) {
    if (!choice || !category(choice.category)) return null;
    const kind = choice.category;
    if (route !== defaultRoute(kind)) return null;
    return { category: kind, route, step: kind === "move" ? "encyclopedia" : "appearance" };
  }
  function selectStep(choice, step) {
    const selected = choice && choice.route && resolve(choice.category, choice.route, step);
    return selected ? { category: choice.category, route: choice.route, step } : null;
  }
  window.COSMI_TASK_FLOW = Object.freeze({ categories, steps, diagram, resolve, infer, selectCategory, selectRoute, selectStep });
})();
