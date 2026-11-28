"""Builds the everyday-object part kits and delivers them to the game repo (cosmos_chimera ADR-0016).

blender -b --factory-startup --python tools/object-kit/build.py -- [--functions Hoe,Barrel] [--eras Primal,Future]
        [--regions Ocean,Gale|none] [--skip-shared] [--no-export] [--render <dir>]

Per (function, era) writes Assets/_Project/Art/Objects/<Family>/<Function>/<Function>_<Era>.fbx holding every slot
variant as an object named <slot>_v<k> (k < 6), all in the function frame, and updates
Assets/_Project/Art/Objects/object-kit.json (slots, triangle counts, budget). Fails loudly when any assembled
combination can exceed the budget. --render writes one lineup sheet per function: 8 era columns x 3 combos.
Four-planet forms (kit_forms.regional) go to <Function>_<Era>_<Region>.fbx and functions.<F>.regions.<Region>.<Era>.
"""
import argparse
import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit_forms  # noqa: E402
import glob  # noqa: E402
import importlib  # noqa: E402

# Each forms_<group>.py registers its functions into kit_forms.FUNCTIONS on import; sorted so the order is fixed.
for _path in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "forms_*.py"))):
    importlib.import_module(os.path.splitext(os.path.basename(_path))[0])
from kit_lib import ERAS, REGIONS, VARIANTS, Part, finish, morph, rng_for  # noqa: E402

GENERATOR_VERSION = 1
BUDGET = {"carried": 600, "scene": 1500, "machine": 4000}
_FORGE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GAME = os.environ.get("COSMIMERA_GAME") or os.path.join(os.path.dirname(_FORGE), "cosmos_chimera")
OUT = os.path.join(GAME, "Assets", "_Project", "Art", "Objects")


def build_one(name, era, region=None):
    """Builds all slot variants of one (function, era[, region]) into a fresh collection; returns (collection, tris table).
    The shared form keeps its original rng keys, so adding regions never changes a delivered shared kit."""
    spec = kit_forms.FUNCTIONS[name]
    form = kit_forms.REGIONAL[name][region] if region else spec["form"]
    key = (name, era, region) if region else (name, era)
    coll = bpy.data.collections.new("%s_%s_%s" % (name, era, region or "shared"))
    bpy.context.scene.collection.children.link(coll)
    tris = {}
    distinct = {}
    for slot in spec["slots"]:
        for cut in (False, True):
            obs, tris[slot] = [], []
            seen = set()
            for k in range(VARIANTS):
                part = Part(era, rng_for(*key, slot, k), rng_for(*key, "frame"), region)
                form(part, slot)
                morph(part, k, cut)
                if not part.bm.faces:
                    raise SystemExit("empty slot %s/%s/%s v%d" % (name, era, slot, k))
                ob, t = finish(part, "%s_v%d" % (slot, k), coll)
                obs.append(ob)
                tris[slot].append(t)
                seen.add(tuple(round(c, 4) for v in ob.data.vertices for c in v.co))
            distinct[slot] = len(seen)
            if len(seen) > 1 or cut:
                break
            for ob in obs:
                mesh = ob.data
                bpy.data.objects.remove(ob)
                bpy.data.meshes.remove(mesh)
    return coll, tris, distinct


def triangulate(coll):
    """Unity's FBX importer discards non-planar n-gons as self-intersecting (holes in the part); Blender
    splits them cleanly. Triangle count is unchanged: the budget already counts triangles."""
    for o in coll.objects:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        bm.to_mesh(o.data)
        bm.free()


def export(coll, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    triangulate(coll)
    bpy.ops.export_scene.fbx(filepath=path, collection=coll.name, object_types={"MESH"}, mesh_smooth_type="FACE",
                             use_mesh_modifiers=False, bake_anim=False, add_leaf_bones=False, path_mode="RELATIVE",
                             embed_textures=False, colors_type="LINEAR", apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y")


def render_sheet(name, colls, out_dir, region=None):
    """8 era columns x 3 variant combos, 3/4 ortho view, preview toon materials."""
    sc = bpy.context.scene
    sheet = bpy.data.collections.new("sheet_" + name)
    sc.collection.children.link(sheet)
    spec = kit_forms.FUNCTIONS[name]
    lo = Vector((1e9,) * 3)
    hi = Vector((-1e9,) * 3)
    for coll in colls.values():
        for o in coll.objects:
            for c in o.bound_box:
                lo = Vector(map(min, lo, Vector(c)))
                hi = Vector(map(max, hi, Vector(c)))
    size = hi - lo
    cell = max(size.x, size.y, size.z * 0.6) * 1.5
    rowh = size.z * 1.25 + cell * 0.2
    for ci, era in enumerate(ERAS):
        coll = colls[era]
        for row in range(3):
            pick = rng_for("sheet", name, row)
            for slot in spec["slots"]:
                k = pick.randrange(VARIANTS)
                src = coll.objects["%s:%s_v%d" % (era if region is None else "%s@%s" % (era, region), slot, k)]
                o = bpy.data.objects.new("%s_%s_%d_%s" % (name, era, row, slot), src.data)
                o.matrix_world = Matrix.Translation((ci * cell, 0, -row * rowh))
                sheet.objects.link(o)
        txt = bpy.data.curves.new("lbl_" + era, "FONT")
        txt.body = era
        txt.size = cell * 0.13
        txt.align_x = "CENTER"
        t = bpy.data.objects.new("lbl_" + era, txt)
        t.location = (ci * cell, 0, hi.z + cell * 0.12)
        t.rotation_euler = (math.radians(90), 0, math.radians(25))
        sheet.objects.link(t)
    for coll in colls.values():
        coll.hide_render = True
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 2400
    sc.render.resolution_y = 1100
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("kit")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.32, 0.36, 0.4, 1)
    sc.world = w
    if "kit_sun" not in bpy.data.objects:
        sun = bpy.data.objects.new("kit_sun", bpy.data.lights.new("kit_sun", "SUN"))
        sun.data.energy = 3.0
        sun.rotation_euler = (math.radians(45), 0, math.radians(-35))
        sc.collection.objects.link(sun)
    cam = bpy.data.objects.get("kit_cam") or bpy.data.objects.new("kit_cam", bpy.data.cameras.new("kit_cam"))
    if cam.name not in sc.collection.objects:
        sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    width = 8 * cell
    height = 3 * rowh + cell * 0.3
    cam.data.ortho_scale = max(width * 1.05, height * 1.05 * 2400 / 1100)
    centre = Vector((3.5 * cell, 0, (hi.z + cell * 0.2 - 2 * rowh + lo.z) / 2))
    yaw, pitch = math.radians(-25), math.radians(14)
    d = Vector((math.sin(-yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    cam.location = centre + d * 50
    cam.rotation_euler = (math.radians(90) - pitch, 0, -yaw)
    sc.camera = cam
    os.makedirs(out_dir, exist_ok=True)
    sc.render.filepath = os.path.join(out_dir, "objects-%s%s.png" % (name, "-" + region if region else ""))
    bpy.ops.render.render(write_still=True)
    bpy.data.collections.remove(sheet)
    for coll in colls.values():
        coll.hide_render = False
    return sc.render.filepath


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--functions", default=",".join(kit_forms.FUNCTIONS))
    ap.add_argument("--eras", default=",".join(ERAS))
    ap.add_argument("--regions", default=",".join(REGIONS), help="'none' builds only the shared forms")
    ap.add_argument("--skip-shared", action="store_true")
    ap.add_argument("--no-export", action="store_true")
    ap.add_argument("--render")
    a = ap.parse_args(argv)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    manifest_path = os.path.join(OUT, "object-kit.json")
    manifest = {"generator_version": GENERATOR_VERSION, "variants": VARIANTS, "budget": BUDGET, "functions": {}}
    if os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as f:
            old = json.load(f)
        if old.get("generator_version") == GENERATOR_VERSION:
            manifest["functions"] = old.get("functions", {})
    over = []
    regions = [] if a.regions == "none" else a.regions.split(",")
    for name in a.functions.split(","):
        spec = kit_forms.FUNCTIONS[name]
        entry = manifest["functions"].setdefault(name, {"family": spec["family"], "size": spec["size"],
                                                         "slots": list(spec["slots"]), "eras": {}})
        targets = [] if a.skip_shared else [None]
        targets += [r for r in regions if r in kit_forms.REGIONAL.get(name, {})]
        for region in targets:
            eras = entry["eras"] if region is None else entry.setdefault("regions", {}).setdefault(region, {})
            colls = {}
            for era in a.eras.split(","):
                coll, tris, distinct = build_one(name, era, region)
                same = [k for k, n in distinct.items() if n < 2]
                if same:
                    print("SAME %s %s %s %s" % (name, era, region or "", same))
                colls[era] = coll
                worst = sum(max(v) for v in tris.values())
                rel = "%s/%s/%s_%s%s.fbx" % (spec["family"], name, name, era, "_" + region if region else "")
                eras[era] = {"file": rel, "tris": tris, "max_assembled": worst, "distinct": distinct}
                if worst > BUDGET[spec["size"]]:
                    over.append("%s/%s/%s: %d > %d %s" % (name, era, region or "shared", worst, BUDGET[spec["size"]],
                                                          {k: max(v) for k, v in tris.items()}))
                if not a.no_export:
                    export(coll, os.path.join(OUT, rel))
                # Object names are global in a .blend: free "<slot>_v<k>" for the next era's export.
                tag = era if region is None else "%s@%s" % (era, region)
                for o in coll.objects:
                    o.data.name = "%s:%s" % (tag, o.data.name)
                    o.name = "%s:%s" % (tag, o.name)
                print("KIT %s %s %s max_assembled=%d" % (name, era, region or "shared", worst))
            if a.render and len(colls) == len(ERAS):
                print("SHEET", render_sheet(name, colls, a.render, region))
            for coll in colls.values():
                for o in list(coll.objects):
                    bpy.data.objects.remove(o)
                bpy.data.collections.remove(coll)
    if not a.no_export:
        os.makedirs(OUT, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
    if over:
        raise SystemExit("triangle budget exceeded:\n  " + "\n  ".join(over))


if __name__ == "__main__":
    main()
