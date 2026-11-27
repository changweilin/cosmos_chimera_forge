const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const forge = fs.readFileSync(path.join(root, 'forge.js'), 'utf8');
const pipelineSource = fs.readFileSync(path.join(root, 'pipeline.js'), 'utf8');
const drive = fs.readFileSync(path.join(root, 'drive-storage.js'), 'utf8');

function flowModule() {
  const context = { window: {} };
  vm.runInNewContext(fs.readFileSync(path.join(root, 'task-flow.js'), 'utf8'), context);
  return context.window.COSMI_TASK_FLOW;
}
function pipelineModule() {
  const context = {
    window: { localStorage: { getItem: () => null } },
    document: {
      getElementById: () => null,
      addEventListener: () => {}
    },
    console
  };
  vm.runInNewContext(pipelineSource, context);
  return context.window.COSMI_PIPELINE;
}
test('category must be selected before route; route must be selected before nodes', () => {
  const flow = flowModule();
  assert.equal(flow.selectRoute(null, 'image'), null);
  assert.equal(flow.selectStep(null, 'appearance'), null);
  const chosen = flow.selectCategory('creature');
  assert.equal(chosen.category, 'creature');
  assert.equal(chosen.route, null);
  assert.equal(chosen.step, null);
  assert.equal(flow.selectStep(chosen, 'appearance'), null);
  assert.equal(flow.selectRoute(chosen, 'image'), null);
  const routed = flow.selectRoute(chosen, 'text');
  assert.equal(routed.route, 'text');
  assert.equal(routed.step, 'appearance');
  assert.equal(flow.selectStep(routed, 'image_colab'), null);
  assert.equal(flow.selectStep(routed, 'prompt_3d').step, 'prompt_3d');
  const chr = flow.selectCategory('character');
  assert.equal(flow.selectRoute(chr, 'text'), null);
  assert.equal(flow.selectRoute(chr, 'image').step, 'appearance');
  const move = flow.selectRoute(flow.selectCategory('move'), 'move');
  assert.equal(move.step, 'encyclopedia');
  assert.equal(flow.selectRoute(flow.selectCategory('move'), 'image'), null);
});
test('each category renders its single linear pipeline diagram', () => {
  const flow = flowModule();
  assert.deepEqual(Array.from(flow.diagram('character'), r => r.steps[0].id), ['appearance', 'portrait', 'review_portrait', 'image_blender', 'review_3d']);
  assert.deepEqual(Array.from(flow.diagram('creature'), r => r.steps[0].id), ['appearance', 'prompt_3d', 'review_3d']);
  assert.deepEqual(Array.from(flow.diagram('move'), r => r.steps[0].id), ['encyclopedia', 'move_vfx', 'passive_vfx']);
});
test('task graph is horizontally scrollable and category selection needs no route switch', () => {
  assert.match(html, /<h2>任務流程圖<\/h2>/);
  assert.match(html, /\.task-flow-list \{ display:flex !important; flex-direction:row/);
  assert.match(html, /overflow-x:auto/);
  assert.match(html, /flow-lanes/); 
  assert.match(html, /flow-parallel-tracks/);
  assert.doesNotMatch(html, /id="taskRoutes"/);
  assert.match(forge, /function chooseCategory\(category\)/);
  assert.doesNotMatch(forge, /function chooseRoute\(route\)/);
  assert.match(forge, /taskFlow\.diagram\(kind\)/);
  assert.match(forge, /onclick:\(\)=>chooseFlow\(kind,route,step.id\)/);
  assert.match(forge, /window\.matchMedia(?:\?\.)?\(/);
  assert.match(html, /\.task-flow-list \{[^}]*flex-wrap:nowrap !important;/);
  assert.match(forge, /window\.scrollTo\(/);
});
test('appearance is derived from current concept data, without duplicate input', () => {
  const pipeline = pipelineModule();
  const context = {
    concept: {name_zh: '測試角色', body_type: ['高挑'], appearance_palette: ['冷色']},
    opts: {stage: 'adult'},
    notes: '增加金色線條'
  };
  const result = pipeline.appearance(context);
  assert.match(result, /name_zh: 測試角色/);
  assert.match(result, /appearance_palette/);
  assert.match(result, /補充／修改: 增加金色線條/);
  assert.doesNotMatch(html, /id="pipelineAppearance"/);
  assert.doesNotMatch(pipelineSource, /pipelineAppearance/);
  assert.doesNotMatch(drive, /pipelineAppearance/);
  assert.doesNotMatch(drive, /\.appearance\.md"/);
});
test('format JSON is located below Prompt output, with save and load controls', () => {
  const promptAt = html.indexOf('<textarea id="prompt"');
  const formatAt = html.indexOf('id="pipelineParameters"');
  const favoritesAt = html.indexOf('id="favoritesSection"');
  assert.ok(promptAt >= 0 && promptAt < formatAt && formatAt < favoritesAt);
  for (const id of ['pipelineParameters', 'pipelineSaveSettings', 'pipelineLoadSettings']) {
    assert.equal((html.match(new RegExp('id="' + id + '"', 'g')) || []).length, 1);
  }
  assert.match(drive, /已儲存格式參數/);
  assert.match(drive, /已載入格式參數/);
});

test('concept editor follows selected character concept flow and stage inventory is present', () => {
  assert.match(html, /id="conceptSection"/);
  assert.match(html, /id="concept"/);
  assert.match(html, /id="flowStageInventory" hidden/);
  assert.match(html, /id="flowStageInventoryItems"/);
  assert.match(forge, /function renderFlowStageInventory\(\)/);
  assert.match(forge, /const flow = currentFlow\(\)/);
  assert.match(forge, /conceptBox\.hidden = !showConcept/);
  assert.match(forge, /inventory\.hidden = !flow \|\| showConcept/);
  assert.match(forge, /renderTasks\(\); renderFlowStageInventory\(\);/);
  assert.match(forge, /if \(!\$\("#concept"\)\?\.hidden\) renderConcepts\(\)/);
  assert.match(forge, /const key = subject \+ "\\|" \+ form/);
});
