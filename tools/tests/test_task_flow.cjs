const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');

function loadFlow() {
  const ctx = { window: {} };
  vm.runInNewContext(fs.readFileSync(path.join(root,'task-flow.js'),'utf8'),ctx);
  return ctx.window.COSMI_TASK_FLOW;
}

test('three entry categories are character, creature, move', () => {
  const flow = loadFlow();
  assert.deepEqual(Array.from(flow.categories,c=>c.id),['character','creature','move']);
  assert.equal(flow.resolve('move','move','move_vfx').taskId,'move-vfx');
  assert.equal(flow.resolve('move','move','passive_vfx').taskId,'passive-vfx');
  assert.equal(flow.steps('move','move').length,3);
  assert.equal(flow.steps('move','move')[0].id,'encyclopedia');
});
test('character route keeps prompt-to-image and AI+Blender image-to-3D only', () => {
  const flow=loadFlow();
  const steps=Array.from(flow.steps('character','image'),s=>s.id);
  assert.deepEqual(steps,['appearance','portrait','review_portrait','image_blender','review_3d']);
  assert.equal(flow.resolve('character','image','image_blender').taskId,'character-model-rig');
  assert.equal(flow.resolve('character','image','image_colab'),null);
  assert.deepEqual(Array.from(flow.steps('character','text')),[]);
});
test('creature route keeps prompt-to-3D only without portraits or colab', () => {
  const flow=loadFlow();
  const steps=Array.from(flow.steps('creature','text'),s=>s.id);
  assert.deepEqual(steps,['appearance','prompt_3d','review_3d']);
  assert.equal(flow.resolve('creature','text','prompt_3d').stage,'blender');
  assert.deepEqual(Array.from(flow.steps('creature','image')),[]);
  assert.equal(flow.resolve('character','text','portrait_3d'),null);
  assert.equal(flow.resolve('character','text','image_colab'),null);
});
test('encyclopedia is integrated into appearance for character/creature and standalone for move', () => {
  const flow=loadFlow();
  assert.equal(flow.resolve('character','image','encyclopedia'),null);
  assert.match(flow.resolve('character','image','appearance').output,/05_wiki\.md/);
  assert.equal(flow.resolve('creature','text','encyclopedia'),null);
  assert.match(flow.resolve('creature','text','appearance').output,/05_wiki\.md/);
  assert.equal(flow.resolve('move','move','encyclopedia').stage,'encyclopedia');
  assert.deepEqual(Array.from(flow.diagram('character'),r=>r.steps[0].id),['appearance','portrait','review_portrait','image_blender','review_3d']);
  assert.deepEqual(Array.from(flow.diagram('creature'),r=>r.steps[0].id),['appearance','prompt_3d','review_3d']);
  assert.equal(flow.selectRoute(flow.selectCategory('move'),'move').step,'encyclopedia');
});
test('legacy task and stage can be mapped to simplified flow', () => {
  const flow=loadFlow();
  assert.equal(flow.infer('move-vfx','portrait').step,'move_vfx');
  assert.equal(flow.infer('passive-vfx','passive_vfx').step,'passive_vfx');
  assert.equal(flow.infer('character-concept','portrait').step,'portrait');
  assert.equal(flow.infer('character-model-rig','blender',{source_pack:'chr-existing'}).step,'image_blender');
  assert.equal(flow.infer('creature-model-rig','blender',{source_pack:'',input_img:''}).step,'prompt_3d');
});
test('page loads flow before forge and includes category, route, step and detail containers', () => {
  const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
  assert.ok(html.indexOf('src="task-flow.js"') < html.indexOf('src="forge.js"'));
  for(const id of ['taskCategories','tasks','taskFlowDetail']) assert.match(html,new RegExp('id="'+id+'"'));
  assert.doesNotMatch(html,/id="taskRoutes"/);
});
test('prompt-to-3D does not require post-model portrait', () => {
  const code=fs.readFileSync(path.join(root,'pipeline.js'),'utf8');
  assert.doesNotMatch(code,/stage === "portrait_3d"/);
  assert.match(code,/Prompt-to-3D 無需補繪立繪/);
  assert.match(code,/nativeBuild/);
});

test('redundant task navigation and portrait auto controls are removed', () => {
  const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
  const forge=fs.readFileSync(path.join(root,'forge.js'),'utf8');
  const pipeline=fs.readFileSync(path.join(root,'pipeline.js'),'utf8');
  assert.doesNotMatch(html,/id="btnGoDesignedFromSubhead"/);
  assert.doesNotMatch(html,/id="portraitAutoRun"/);
  assert.doesNotMatch(forge,/\$\("#btnGoDesignedFromSubhead"\)/);
  assert.doesNotMatch(pipeline,/\$\("portraitAutoRun"\)/);
  assert.match(html,/id="settingsSignOut"/);
});
test('category controls use text and do not display a route toggle', () => {
  const forge=fs.readFileSync(path.join(root,'forge.js'),'utf8');
  assert.match(forge,/}, c\.zh\)\)\)/);
  assert.doesNotMatch(forge,/function chooseRoute\(/);
  assert.doesNotMatch(forge,/flow-lane-label|flow-alternatives-label/); 
  assert.match(forge,/class:"flow-parallel-track"/);
});

test('production build ships the task chooser module', () => {
  const build=fs.readFileSync(path.join(root,'tools/build-site.mjs'),'utf8');
  assert.ok(build.includes("'task-flow.js'"));
});
test('portrait uses native copy or Drive upload, never a missing template', () => {
  const drive=fs.readFileSync(path.join(root,'drive-storage.js'),'utf8');
  // Verify both handlers follow the selected mode, independent of indentation.
  const savePrompt=drive.slice(drive.indexOf('$("driveSavePrompt").addEventListener'),drive.indexOf('$("driveLoadPrompt").addEventListener'));
  const pipelineRead=drive.slice(drive.indexOf('$("pipelineRead").addEventListener'),drive.indexOf('$("pipelineSaveSettings").addEventListener'));
  assert.match(savePrompt,/\$\("pipelineStage"\)\.value === "portrait"\s*&&\s*!window\.COSMI_PIPELINE\?\.isPortraitAuto\(\)/);
  assert.match(pipelineRead,/if\s*\(\s*\$\("pipelineStage"\)\.value === "portrait"\s*\)/);
  assert.match(pipelineRead,/if\s*\(\s*!window\.COSMI_PIPELINE\?\.isPortraitAuto\(\)\s*\)\s*\{\s*\$\("copy"\)\.click\(\);\s*return;/);
  assert.match(pipelineRead,/await write\(\s*path,\s*new Blob\(\[text\],\s*\{\s*type:\s*"text\/markdown"/);
});
test('typed anatomy profiles are shipped and connected to 3D prompts', () => {
  const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
  const build=fs.readFileSync(path.join(root,'tools/build-site.mjs'),'utf8');
  const pipeline=fs.readFileSync(path.join(root,'pipeline.js'),'utf8');
  const profiles=fs.readFileSync(path.join(root,'anatomy-profiles.js'),'utf8');
  assert.match(html,/src="anatomy-profiles.js"/);
  assert.ok(build.includes("'anatomy-profiles.js'"));
  assert.ok(html.indexOf('src="anatomy-profiles.js"') < html.indexOf('src="forge.js"'));
  assert.match(pipeline,/COSMI_ANATOMY\?\.plan/);
  assert.match(profiles,/winged_quadruped/);
  assert.match(profiles,/humanoid_mecha/);
});

test('mechanical limb counts retain rigid mecha routes in browser', () => {
  const ctx={window:{}};
  vm.runInNewContext(fs.readFileSync(path.join(root,'anatomy-profiles.js'),'utf8'),ctx);
  const plan=ctx.window.COSMI_ANATOMY.plan;
  for(const [legs, expected] of [[2,'humanoid_mecha'],[4,'quadruped_mecha'],[6,'multi_leg_mecha'],[8,'multi_leg_mecha']]) {
    assert.equal(plan('creature',{base_parents:['科幻機械·機甲/外骨骼'],limbs:{legs}},'image').anatomy,expected);
  }
  assert.equal(plan('creature',{base_parents:['科幻機械·機甲/外骨骼'],anatomy:'humanoid_mecha',limbs:{legs:4}},'image').anatomy,'humanoid_mecha');
});

test('browser anatomy planner respects mixed origins and explicit wings', () => {
  const ctx={window:{}};
  vm.runInNewContext(fs.readFileSync(path.join(root,'anatomy-profiles.js'),'utf8'),ctx);
  const plan=ctx.window.COSMI_ANATOMY.plan;
  const winged=plan('creature',{base_parents:['生物·哺乳類'],limbs:{legs:4,wings:2}},'image');
  assert.equal(winged.anatomy,'winged_quadruped');
  const machine=plan('creature',{base_parents:['科幻機械·機甲/外骨骼']},'text');
  assert.equal(machine.anatomy,'humanoid_mecha');
  assert.equal(machine.input_mode,'text');
  const mixed=plan('creature',{base_parents:['生物·哺乳類','幻想生物·異界/異形']},'image');
  assert.equal(mixed.anatomy,'hybrid');
  assert.equal(mixed.review_required,true);
});

test('minimal rail diagram exposes simplified linear tracks per category', () => {
  const flow=loadFlow();
  assert.deepEqual(Array.from(flow.diagram('character'),r=>r.steps[0].id),
    ['appearance','portrait','review_portrait','image_blender','review_3d']);
  assert.deepEqual(Array.from(flow.diagram('creature'),r=>r.steps[0].id),
    ['appearance','prompt_3d','review_3d']);
  const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
  const forge=fs.readFileSync(path.join(root,'forge.js'),'utf8');
  assert.match(html,/\.task-flow-list \.flow-parallel-tracks/);
  assert.match(html,/\.task-flow-list \.flow-lane, \.task-flow-list \.flow-parallel-track \{[^}]*border:0/);
  assert.doesNotMatch(forge,/lane\.label|segment\.label/);
});

test('concept fields keep label buttons and options in one row on desktop tablet and phone', () => {
  const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
  const forge=fs.readFileSync(path.join(root,'forge.js'),'utf8');
  assert.match(forge,/class: "field concept-field"/);
  assert.match(forge,/"data-concept-field": key/);
  assert.match(forge,/el\("label", \{ for: controlId, title: f\.label/);
  assert.match(html,/#forgeView #concept \.concept-field \{[\s\S]*?display:grid !important;/);
  assert.match(html,/#forgeView #concept \.concept-field \{[\s\S]*?grid-template-columns:[^;]+!important;/);
  assert.match(html,/#forgeView #concept \{[^}]*overflow-x:auto/);
  assert.match(html,/#forgeView #concept \.concept-field > \.chips \{[\s\S]*?flex-wrap:nowrap/);
  assert.match(html,/@media \(max-width:699px\) \{\s*#forgeView #concept \.concept-field/);
});
