const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '../..');
const catalogSrc = fs.readFileSync(path.join(root, 'catalog.js'), 'utf8');
const context = { window: {} };
vm.runInNewContext(catalogSrc, context);
const C = context.window.COSMI_CATALOG;

const LEGACY_CHARACTER_IDS = [
  'idle', 'idle_long', 'walk', 'run', 'sneak_idle', 'sneak_move', 'roll_dodge', 'jump',
  'block', 'hit_react', 'knockdown', 'getup', 'command_point', 'command_attack',
  'command_recall', 'summon', 'recall', 'item_use_self', 'item_use_other', 'field_deploy',
  'backpack_open', 'talk_idle', 'talk_gesture', 'pet_xs', 'pet_s', 'pet_m', 'pet_l', 'pet_xl',
  'throw_card', 'throw_bead', 'throw_cube', 'victory', 'defeated'
];

const LEGACY_CREATURE_IDS = [
  'idle', 'idle_long', 'walk', 'run', 'sneak', 'block', 'dodge_miss', 'hit_react', 'faint',
  'atk_melee_front', 'atk_melee_sweep', 'atk_melee_burst', 'atk_ranged_line',
  'atk_ranged_cone', 'atk_ranged_arc', 'sup_self', 'sup_ally', 'field_deploy',
  'petted', 'summon_appear', 'recall_vanish', 'capture_struggle',
  'overload_enter', 'overload_exit', 'hatch', 'victory'
];

function extractGetClipCategory() {
  const forgeSrc = fs.readFileSync(path.join(root, 'forge.js'), 'utf8');
  const match = forgeSrc.match(/function getClipCategory\(clipName\)\s*\{[\s\S]*?\n  \}/);
  assert.ok(match, 'getClipCategory should exist in forge.js');
  const fnCtx = {};
  vm.runInNewContext(match[0], fnCtx);
  return fnCtx.getClipCategory;
}

test('ACTIONS preserves all legacy clip IDs and expands character & creature sets', () => {
  assert.equal(C.version, '2.15.0');
  const chrIds = C.ACTIONS.character.map(a => a.id);
  const crIds = C.ACTIONS.creature.map(a => a.id);

  for (const id of LEGACY_CHARACTER_IDS) {
    assert.ok(chrIds.includes(id), `missing legacy character clip: ${id}`);
  }
  for (const id of LEGACY_CREATURE_IDS) {
    assert.ok(crIds.includes(id), `missing legacy creature clip: ${id}`);
  }

  for (const id of ['moveset_switch', 'moveset_forced_switch', 'weapon_draw', 'weapon_sheathe', 'perfect_block', 'atk_melee_front', 'atk_melee_front_r', 'sup_self']) {
    assert.ok(chrIds.includes(id), `missing v2.12 character clip: ${id}`);
  }
  for (const id of ['follow_idle', 'follow_dash', 'link_channel', 'relay_enter', 'boss_moveset_switch', 'boss_summon_follower']) {
    assert.ok(crIds.includes(id), `missing v2.12 creature clip: ${id}`);
  }
  for (const id of ['crouch_move', 'crouch_roll', 'crouch_jump', 'crouch_block']) {
    assert.ok(chrIds.includes(id), `missing v2.15 crouch character clip: ${id}`);
    assert.ok(crIds.includes(id), `missing v2.15 crouch creature clip: ${id}`);
  }

  assert.equal(chrIds.length, 85);
  assert.equal(crIds.length, 68);
  assert.ok(C.GRIP_MODES && C.GRIP_MODES.two_handed && C.GRIP_MODES.dual_wield && C.GRIP_MODES.one_hand_shield);
  assert.match(C.GRIP_MODES.crouch_rule, /先站立/);
});

test('ACTIONS entries have unique snake_case IDs, valid frame counts, and well-formed events', () => {
  for (const role of ['character', 'creature']) {
    const list = C.ACTIONS[role];
    const seen = new Set();
    for (const clip of list) {
      assert.match(clip.id, /^[a-z][a-z0-9_]*$/, `${role}.${clip.id} must be snake_case`);
      assert.ok(!seen.has(clip.id), `duplicate ${role} clip id: ${clip.id}`);
      seen.add(clip.id);
      assert.equal(typeof clip.zh, 'string');
      assert.ok(clip.zh.trim().length > 0, `${role}.${clip.id} missing zh`);
      assert.ok(Number.isInteger(clip.f) && clip.f > 0, `${role}.${clip.id} invalid frame count`);
      if (clip.ev) {
        assert.ok(Array.isArray(clip.ev));
        for (const ev of clip.ev) {
          const m = ev.match(/^([a-z_]+)@(\d+)$/);
          assert.ok(m, `${role}.${clip.id} invalid event format: ${ev}`);
          const frame = Number(m[2]);
          assert.ok(frame >= 0 && frame <= clip.f, `${role}.${clip.id} event frame out of range: ${ev}`);
        }
      }
    }
  }
});

test('every character and creature clip maps to a known UI category in forge.js', () => {
  const getClipCategory = extractGetClipCategory();
  const knownCategories = new Set([
    '基礎移動', '戰鬥受擊', '指令召喚', '主動技攻擊', '輔助場地', '道具背包', '生活採集', '互動撫摸'
  ]);
  for (const c of C.ACTIONS.character) {
    const cat = getClipCategory(`chr_${c.id}`);
    assert.ok(knownCategories.has(cat), `chr_${c.id} fell into ${cat}`);
  }
  for (const c of C.ACTIONS.creature) {
    const cat = getClipCategory(`cr_adult_${c.id}`);
    assert.ok(knownCategories.has(cat), `cr_adult_${c.id} fell into ${cat}`);
  }
});

test('creature-model-rig filters clips by allowed grip_mode and includes virtual giant hand rules', () => {
  const tasksSrc = fs.readFileSync(path.join(root, 'tasks.js'), 'utf8');
  const tCtx = { window: { COSMI_CATALOG: C } };
  vm.runInNewContext(tasksSrc, tCtx);
  const task = tCtx.window.COSMI_TASKS.find(t => t.id === 'creature-model-rig');
  assert.ok(task, 'creature-model-rig should exist');
  const allIds = C.ACTIONS.creature.map(a => a.id);

  const dualPrompt = task.build({
    header: '[COSMIMERA-TASK]',
    task: { id: 'creature-model-rig' },
    taskId: 'mdl-test',
    subjectId: 'moon_night_pup',
    concept: { locked: { stages: [{ stage: 'adult', grip_mode: 'dual_wield', signature_move: { range_class: 'melee' } }] } },
    opts: { scope: 'single', stage: 'adult', grip_mode: 'auto', weapon_scope: 'all_allowed', actions_creature: allIds }
  });
  assert.match(dualPrompt, /虛擬大手/);
  assert.match(dualPrompt, /不繪製、不包含任何武器、盾牌或虛擬大手/);
  assert.match(dualPrompt, /技能仍由宙獸本體發出/);
  assert.match(dualPrompt, /Socket_Weapon_R/);
  assert.match(dualPrompt, /Socket_Weapon_L/);
  assert.match(dualPrompt, /cr_adult_atk_melee_front_r/);
  assert.match(dualPrompt, /cr_adult_atk_ranged_line_l/);
  assert.doesNotMatch(dualPrompt, /`cr_adult_atk_melee_front`/);
  assert.doesNotMatch(dualPrompt, /`cr_adult_atk_ranged_line`/);

  const shieldRangedOnly = task.build({
    header: '[COSMIMERA-TASK]',
    task: { id: 'creature-model-rig' },
    taskId: 'mdl-test-2',
    subjectId: 'sun_mirror_chick',
    concept: { locked: { stages: [{ stage: 'juvenile', grip_mode: 'one_hand_shield', signature_move: { range_class: 'long' } }] } },
    opts: { scope: 'single', stage: 'juvenile', grip_mode: 'auto', weapon_scope: 'signature_only', actions_creature: allIds }
  });
  assert.match(shieldRangedOnly, /`one_hand_shield`/);
  assert.match(shieldRangedOnly, /cr_juvenile_atk_ranged_line/);
  assert.doesNotMatch(shieldRangedOnly, /cr_juvenile_atk_melee_front/);
  assert.doesNotMatch(shieldRangedOnly, /_atk_ranged_line_r/);
  assert.match(shieldRangedOnly, /cr_juvenile_follow_idle/);
  assert.match(shieldRangedOnly, /cr_juvenile_boss_summon_follower/);
  assert.match(shieldRangedOnly, /cr_juvenile_crouch_move/);
  assert.match(shieldRangedOnly, /cr_juvenile_crouch_roll/);
  assert.match(shieldRangedOnly, /cr_juvenile_crouch_jump/);
  assert.match(shieldRangedOnly, /cr_juvenile_crouch_block/);
  assert.match(shieldRangedOnly, /蹲下與起身銜接規範/);
  assert.match(shieldRangedOnly, /先站立回歸站姿/);
});

test('character-model-rig emits 7-slot sockets and filters clips by grip_mode', () => {
  const tasksSrc = fs.readFileSync(path.join(root, 'tasks.js'), 'utf8');
  const tCtx = { window: { COSMI_CATALOG: C } };
  vm.runInNewContext(tasksSrc, tCtx);
  const task = tCtx.window.COSMI_TASKS.find(t => t.id === 'character-model-rig');
  assert.ok(task, 'character-model-rig should exist');
  const allIds = C.ACTIONS.character.map(a => a.id);

  const allPrompt = task.build({
    header: '[COSMIMERA-TASK]',
    task: { id: 'character-model-rig' },
    taskId: 'chr-mdl-all',
    subjectId: 'chr_test',
    concept: {},
    opts: { grip_mode: 'all', weapon_scope: 'all_allowed', actions_character: allIds }
  });
  assert.match(allPrompt, /Socket_Head_Armor/);
  assert.match(allPrompt, /Socket_Hands_Armor/);
  assert.match(allPrompt, /chr_moveset_switch/);
  assert.match(allPrompt, /chr_atk_melee_front`/);
  assert.match(allPrompt, /chr_atk_melee_front_r`/);

  const dualPrompt = task.build({
    header: '[COSMIMERA-TASK]',
    task: { id: 'character-model-rig' },
    taskId: 'chr-mdl-dual',
    subjectId: 'chr_test',
    concept: {},
    opts: { grip_mode: 'dual_wield', weapon_scope: 'all_allowed', actions_character: allIds }
  });
  assert.match(dualPrompt, /chr_atk_melee_front_r`/);
  assert.doesNotMatch(dualPrompt, /`chr_atk_melee_front`/);

  const shieldPrompt = task.build({
    header: '[COSMIMERA-TASK]',
    task: { id: 'character-model-rig' },
    taskId: 'chr-mdl-shield',
    subjectId: 'chr_test',
    concept: {},
    opts: { grip_mode: 'one_hand_shield', weapon_scope: 'all_allowed', actions_character: allIds }
  });
  assert.match(shieldPrompt, /`chr_atk_melee_front`/);
  assert.doesNotMatch(shieldPrompt, /chr_atk_melee_front_r/);
  assert.match(shieldPrompt, /chr_crouch_move/);
  assert.match(shieldPrompt, /chr_crouch_roll/);
  assert.match(shieldPrompt, /chr_crouch_jump/);
  assert.match(shieldPrompt, /chr_crouch_block/);
  assert.match(shieldPrompt, /蹲下與起身銜接規範/);
  assert.match(shieldPrompt, /先站立回歸站姿/);
});

test('Data character-anims and creature-grip-anims JSON match catalog.js v2.15.0', () => {
  const chrAnims = JSON.parse(fs.readFileSync(path.join(root, 'Data/character-anims/character-anims.json'), 'utf8'));
  const crAnims = JSON.parse(fs.readFileSync(path.join(root, 'Data/creature-grip-anims/creature-grip-anims.json'), 'utf8'));

  assert.equal(chrAnims.length, 3);
  const chrCatalogIds = new Set(C.ACTIONS.character.map(a => a.id));
  const chrCovered = new Set();
  const crouchIds = ['crouch_move', 'crouch_roll', 'crouch_jump', 'crouch_block'];
  for (const entry of chrAnims) {
    assert.equal(entry.spec, 'cosmimera-character-anim/1');
    assert.match(entry.pose_rules.crouch_rule, /先站立回歸站姿/);
    const clipIds = new Set(entry.clips.map(c => c.action_id));
    for (const req of crouchIds) {
      assert.ok(clipIds.has(req), `${entry.id} missing crouch character clip: ${req}`);
    }
    for (const c of entry.clips) {
      assert.ok(chrCatalogIds.has(c.action_id), `unknown character clip in JSON: ${c.action_id}`);
      chrCovered.add(c.action_id);
    }
  }
  assert.equal(chrCovered.size, chrCatalogIds.size);

  assert.equal(crAnims.length, 3);
  const crCatalogIds = new Set(C.ACTIONS.creature.map(a => a.id));
  const requiredNew = ['follow_idle', 'follow_dash', 'link_channel', 'relay_enter', 'boss_moveset_switch', 'boss_summon_follower', ...crouchIds];
  for (const entry of crAnims) {
    assert.match(entry.pose_rules.crouch_rule, /先回歸站立姿態/);
    const clipIds = new Set(entry.clips.map(c => c.action_id));
    for (const req of requiredNew) {
      assert.ok(clipIds.has(req), `${entry.id} missing creature clip: ${req}`);
    }
    for (const id of clipIds) {
      assert.ok(crCatalogIds.has(id), `unknown creature clip in JSON: ${id}`);
    }
  }
});
