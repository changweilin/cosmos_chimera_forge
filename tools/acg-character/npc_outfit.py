"""Builds the NPC wardrobe slots (region pieces, era trims and, from npc_cut.py, the cut garments) on one baked race base and exports them for Unity (ADR-0015,
cosmos_chimera docs/design/npc-uma-looks.md row 17, #服裝).

Usage: blender -b Logs/npc/<id>.blend --python tools/acg-character/npc_outfit.py -- --fbx <game>/_UMA/Npc/Outfit/<id>.fbx
           [--preview <out.png>]

Each slot is what the procedural NpcMeshes draws for it (Signature for "piece_<region>", the era block of Dress for
"trim_<era>"), refitted to this base's own body: cloth that hugs the body is a shell lifted off the base's skin, so it
fits each race and sex without a runtime fit; rigid bits (buttons, beads, a lantern) sit on the skin's measured surface.
Sizes are in the procedural units: the base's height h and head radius hr (crown to chin / 1.98). Everything worn on
the trunk clears the widest cut garment (procedural fit 1.2, the wasteland cut), so a piece never sinks into whatever
cut the resident wears.

Like the hair (npc_hair.py), every mesh carries a shape key of the same name as every base key that moves it: a vertex
moves as the body skin nearest it does (inverse-distance mean of its NEAREST skin vertices), so fat, muscle and the
skeleton's proportions reshape the piece with the body. Bone weights come the same way, at most 4. Colour is a shader
parameter in Unity: each part's material is named for its recipe colour (OUTFIT_ROLES), the mesh carries no colour.

A cut slot also carries its own parameter keys (npc_cut.KEYS: hem, ease, fall, flare), built as the same mesh at the
parameter's high end. Cloth below the hip takes its bone weights from the nearest skin like everything else: the race
DNA moves and scales the thigh bones (hip width, bulk), and cloth weighted partly to the pelvis let the legs and the
trousers under it push through. Not here: head-worn bits (the lava brow band, the crystal brow gem:
procedural, as the headwear).

The wings, tails and capes of npc_appendage.py (and the storm cape, "piece_Storm") go in the same FBX for the base's own
race, weighted to swing chains added to the rig instead of to the skin they hang past.

Pre: the .blend was saved by race.py (base with its shape keys). Post: the FBX holds the rig (with the "sw_" chains) and
one mesh per slot, "piece_<Region>" / "trim_<Era>", the npc_cut.SLOTS names and npc_appendage.slots_for(race); --preview renders every slot (or those --slots names) front
and back. Side effects: edits the open scene in
memory only (never saved); overwrites the outputs.
"""
import argparse
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.kdtree import KDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import acg_render  # noqa: E402
import npc_hair  # noqa: E402

NEAREST = 6
KEY_FLOOR_M = 1e-4
# Procedural NpcMeshes fit (cloth ease over the trunk) of the loosest cut is 1.2 (npc_cut tops at npc_ease 1); pieces and
# trims ride just outside it, or they flicker through the top where the two meet.
OUTER_FIT = 1.22
# Cloth thickness of shell pieces (metres) and the clearance of rigid bits off the cloth surface.
CLOTH_M = 0.003
CLEAR_M = 0.003
# Material per recipe colour (NpcUmaRecipe.ColourNames) or fixed tone; Unity tints each by name (NpcUmaRaces.OutfitRoles).
OUTFIT_ROLES = ("accent", "accentdark", "leather", "leatherlight", "metal", "glow", "bone", "fur", "dark",
                "cloth", "clothlow", "clothdark", "cloth2", "cloth2shade", "cloth2dark", "braid")
TORSO = ("pelvis", "spine_01", "spine_02", "spine_03", "clavicle_l", "clavicle_r", "neck_01")
HAND = ("hand_l", "hand_r") + tuple("%s_0%d_%s" % (f, i, s) for f in ("thumb", "index", "middle", "ring", "pinky")
                                    for i in (1, 2, 3) for s in ("l", "r"))


def _args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--fbx", required=True)
    p.add_argument("--preview")
    p.add_argument("--slots", help="comma-separated slot name prefixes to build (default: all)")
    return p.parse_args(argv)


class Fig:
    """The base's skin (MakeHuman helpers excluded) and the procedural rig's landmarks measured on it.

    Blender axes: up +z, front -y, the character's left +x (bones *_l). NpcMeshes' "L" side is the character's left too.
    """

    def __init__(self, rig, body):
        self.rig, self.body = rig, body
        helpers = {body.vertex_groups[n].index for n in ("HelperGeometry", "JointCubes") if n in body.vertex_groups}
        bones = set(rig.data.bones.keys())
        names = {g.index: g.name for g in body.vertex_groups if g.name in bones}
        self.skin = [v.index for v in body.data.vertices if not any(g.group in helpers and g.weight > 0 for g in v.groups)]
        vs = body.data.vertices
        self.co = np.array([tuple(vs[i].co) for i in self.skin])
        self.no = np.array([tuple(vs[i].normal) for i in self.skin])
        self.w = [{names[g.group]: g.weight for g in vs[i].groups if g.group in names and g.weight > 0.01} for i in self.skin]
        self.local = {i: k for k, i in enumerate(self.skin)}
        self.polys = [[self.local[i] for i in p.vertices] for p in body.data.polygons if all(i in self.local for i in p.vertices)]
        self.torso = np.array([sum(w.get(b, 0.0) for b in TORSO) > 0.5 for w in self.w])
        self.hand = np.array([sum(w.get(b, 0.0) for b in HAND) > 0.5 for w in self.w])
        self.head_of = {b.name: rig.matrix_world @ b.head_local for b in rig.data.bones}
        self.tail_of = {b.name: rig.matrix_world @ b.tail_local for b in rig.data.bones}
        self.h = float(self.co[:, 2].max())
        on_head = np.array([w.get("head", 0.0) > 0.3 for w in self.w])
        hz = self.co[on_head]
        front = hz[(np.abs(hz[:, 0]) < 0.02) & (hz[:, 1] < self.head_of["head"].y)]
        self.hr = (hz[:, 2].max() - front[:, 2].min()) / 1.98
        # Procedural landmarks (NpcMeshes.Rig.Pose): Neck sits 0.03 h over the Chest, the top of the trunk; the shoulder
        # joints 0.02 h under it; Hip is the hip joint height; Waist 35 % up from Hip to Chest.
        self.neck = self.head_of["neck_01"].z
        self.chest = self.neck - 0.03 * self.h
        self.hip = self.head_of["thigh_l"].z
        self.waist = self.hip + 0.35 * (self.chest - self.hip)
        self.hip_x = abs(self.head_of["thigh_l"].x)
        tree = KDTree(len(self.co))
        for k, p in enumerate(self.co):
            tree.insert(p, k)
        tree.balance()
        self.tree = tree
        t = KDTree(int(self.torso.sum()))
        self.torso_idx = np.nonzero(self.torso)[0]
        for j, k in enumerate(self.torso_idx):
            t.insert(self.co[k], j)
        t.balance()
        self.torso_tree = t

    def axis_y(self, z):
        """Front-back centre of the trunk at height z."""
        band = self.torso & (np.abs(self.co[:, 2] - z) < 0.015)
        ys = self.co[band, 1]
        return 0.5 * (ys.min() + ys.max())

    def front(self, x, z, trunk=True):
        """The skin's most forward point near (x, z): the chest a button or bead rests on (any skin if not trunk)."""
        band = (self.torso if trunk else True) & (np.abs(self.co[:, 2] - z) < 0.012) & (np.abs(self.co[:, 0] - x) < 0.012)
        k = np.nonzero(band)[0]
        k = k[np.argmin(self.co[k, 1])]
        return Vector(self.co[k]), Vector(self.no[k])

    def eased(self, k, fit):
        """Skin vertex k pushed out from the trunk's centre line as a cloth of ease `fit` hangs (NpcMeshes rings)."""
        p = Vector(self.co[k])
        c = Vector((0.0, self.axis_y(p.z), p.z))
        return c + (p - c) * fit

    def arm_frac(self, p, side):
        a, b = self.head_of["upperarm_" + side], self.head_of["hand_" + side]
        d = b - a
        return (p - a).dot(d) / d.length_squared

    def bone_axis_dist(self, k, bone):
        a, b = self.head_of[bone], self.tail_of[bone]
        p = Vector(self.co[k])
        d = b - a
        t = max(0.0, min(1.0, (p - a).dot(d) / d.length_squared))
        return (p - (a + d * t)).length


class Part:
    def __init__(self, role, near="all"):
        self.role, self.near = role, near
        self.verts, self.faces = [], []


def _shell(fig, pred, lift, role, thickness=CLOTH_M, near="all", folds=0.0, fold_freq=7.0):
    """The skin faces whose every vertex passes pred(k), each vertex moved to lift(k) (a Vector), then given thickness.
    folds adds a ripple of that depth around the trunk axis, so a collar or capelet reads as cloth rather than paint."""
    keep = {k for k in range(len(fig.co)) if pred(k)}
    polys = [p for p in fig.polys if all(k in keep for k in p)]
    used = sorted({k for p in polys for k in p})
    at = {k: i for i, k in enumerate(used)}
    part = Part(role, near)
    for k in used:
        p = lift(k)
        if folds:
            a = math.atan2(p.x, -(p.y - fig.axis_y(p.z)))
            p = p + Vector(fig.no[k]) * folds * (0.5 + 0.5 * math.sin(fold_freq * a))
        part.verts.append(p)
    part.faces = [tuple(at[k] for k in p) for p in polys]
    if not part.faces:
        raise SystemExit("empty shell for %s" % role)
    part.thickness = thickness
    return part


def _sphere(at, radii, role, u=12, v=8, near="all"):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    for vert in bm.verts:
        vert.co = Vector((vert.co.x * radii[0], vert.co.y * radii[1], vert.co.z * radii[2])) + at
    return _from_bm(bm, role, near)


def _tube(a, b, r0, r1, role, n=8, near="all"):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r0, radius2=r1, depth=1.0)
    d = b - a
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    m = Matrix.Translation((a + b) * 0.5) @ rot @ Matrix.Diagonal((1.0, 1.0, d.length, 1.0))
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    return _from_bm(bm, role, near)


def _panel(a, b, c, normal, depth, role):
    """A thin triangular plate on the cloth: front face a b c, backed `depth` behind along -normal."""
    back = [p - normal * depth for p in (a, b, c)]
    part = Part(role)
    part.verts = [a, b, c] + back
    part.faces = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    if (b - a).cross(c - a).dot(normal) < 0:
        part.faces = [tuple(reversed(f)) for f in part.faces]
    return part


def _from_bm(bm, role, near):
    part = Part(role, near)
    part.verts = [v.co.copy() for v in bm.verts]
    at = {v: i for i, v in enumerate(bm.verts)}
    part.faces = [tuple(at[v] for v in f.verts) for f in bm.faces]
    bm.free()
    return part


# ---- what each slot is (NpcMeshes Signature and the era block of Dress) ------------------------------------------


def _profile(fig, c, n, half, mask, bins=48):
    """The trunk's cross-section in the plane through c with normal n: for each of `bins` directions in the plane, the
    farthest skin (within `half` of the plane, among `mask`) from c. Returns the in-plane axes and the radii."""
    n = n.normalized()
    u = (Vector((0.0, -1.0, 0.0)) - n * n.y * -1.0).normalized() if abs(n.y) < 0.9 else Vector((1.0, 0.0, 0.0))
    v = n.cross(u).normalized()
    rel = fig.co - np.array(c)
    off = rel @ np.array(n)
    sel = mask & (np.abs(off) <= max(half, 0.012))
    q = rel[sel] - np.outer(off[sel], np.array(n))
    ang = np.arctan2(q @ np.array(v), q @ np.array(u))
    r = np.linalg.norm(q, axis=1)
    k = ((ang + math.pi) / (2 * math.pi) * bins).astype(int) % bins
    radii = np.zeros(bins)
    np.maximum.at(radii, k, r)
    have = np.nonzero(radii)[0]
    if len(have) < bins // 3:
        raise SystemExit("trunk section at %s has too few skin vertices" % tuple(round(x, 3) for x in c))
    # Directions with no skin (between sparse rows) take the circular interpolation of their neighbours.
    xs = np.concatenate([have - bins, have, have + bins])
    radii = np.interp(np.arange(bins), xs, np.tile(radii[have], 3))
    # A ring around the trunk never dips into a hollow: no direction is shorter than its neighbours' mean, nor than the
    # section's convex envelope, which the cut tops (npc_cut._support) are measured on.
    radii = np.maximum(radii, 0.5 * (np.roll(radii, 1) + np.roll(radii, -1)))
    a = (np.arange(bins) + 0.5) / bins * 2 * math.pi - math.pi
    dirs = np.outer(np.cos(a), np.array(u)) + np.outer(np.sin(a), np.array(v))
    radii = np.maximum(radii, (q @ dirs.T).max(axis=0))
    return u, v, radii


def _ring(c, n, u, v, radii, fit, out, folds=0.0, freq=7.0, shift=0.0):
    bins = len(radii)
    pts = []
    for i in range(bins):
        a = (i + 0.5) / bins * 2 * math.pi - math.pi
        r = radii[i] * fit + out + folds * (0.5 + 0.5 * math.sin(freq * a))
        pts.append(c + n.normalized() * shift + (u * math.cos(a) + v * math.sin(a)) * r)
    return pts


def _loft(rings, role, thickness=CLOTH_M, centre=None, near="all"):
    """Closed rings (same count) joined into a tube, given cloth thickness; faces look away from `centre`'s axis."""
    part = Part(role, near)
    m = len(rings[0])
    for ring in rings:
        part.verts.extend(ring)
    for i in range(len(rings) - 1):
        for k in range(m):
            a, b = i * m + k, i * m + (k + 1) % m
            part.faces.append((a, b, b + m, a + m))
    part.thickness = thickness
    part.centre = centre
    return part


def _hoop(fig, c, n, half, fit, out, role, folds=0.0, freq=7.0, mask=None):
    """A band of cloth wound round the trunk in the plane (c, n), `half` wide each side: a belt, a sash, a scarf."""
    mask = fig.torso if mask is None else mask
    u, v, radii = _profile(fig, c, n, half, mask)
    rings = [_ring(c, n, u, v, radii, fit, out + bulge, folds, freq, s)
             for s, bulge in ((-half, 0.0), (0.0, 0.002), (half, 0.0))]
    return _loft(rings, role, centre=c)


def _flat(fig, z):
    return Vector((0.0, fig.axis_y(z), z)), Vector((0.0, 0.0, 1.0))


def _band(fig, z, half, fit, role, out=0.0, folds=0.0, freq=7.0):
    c, n = _flat(fig, z)
    return _hoop(fig, c, n, half, fit, CLEAR_M + out, role, folds, freq)


def _capelet(fig):
    """Verdant: a shoulder cape from the collar to 0.13 h under the Chest, widening to the hem (NpcMeshes Signature,
    rings at Chest - 0.13 h .. half way to the Neck), and the hood worn down on the nape. Measured on the trunk alone,
    so in the T bind pose the arms leave through it at the shoulder; lowered, they pass under its sides."""
    h = fig.h
    hem, top = fig.chest - 0.13 * h, fig.chest + 0.5 * (fig.neck - fig.chest)
    rings = []
    for i in range(7):
        t = i / 6
        z = top + (hem - top) * t
        c, n = _flat(fig, z)
        u, v, radii = _profile(fig, c, n, 0.015, fig.torso)
        rings.append(_ring(c, n, u, v, radii, OUTER_FIT, CLEAR_M + 0.03 * h * t ** 1.5, 0.004 * t, 9.0))
    parts = [_loft(rings, "accent", centre=_flat(fig, fig.chest)[0])]
    nape = fig.head_of["neck_01"]
    back = fig.co[fig.torso & (np.abs(fig.co[:, 2] - nape.z) < 0.02) & (np.abs(fig.co[:, 0]) < 0.03), 1].max()
    parts.append(_sphere(Vector((0.0, back + 0.2 * fig.hr, nape.z)), (0.7 * fig.hr, 0.6 * fig.hr, 0.55 * fig.hr), "accentdark"))
    return parts


def _sash(fig):
    """Lava: a sash from the left shoulder across the chest to the right hip and round the back (NpcMeshes: tube of
    radius 0.03 h from ShoulderL to HipR)."""
    h = fig.h
    a = fig.head_of["upperarm_l"] + Vector((-0.02 * h, 0.0, 0.03 * h))
    b = Vector((-fig.hip_x, fig.axis_y(fig.hip), fig.hip + 0.02 * h))
    d = (b - a).normalized()
    t = -a.x / (b.x - a.x)
    z = a.z + (b.z - a.z) * t
    c = Vector((0.0, fig.axis_y(z), z))
    n = d.cross(Vector((0.0, 1.0, 0.0))).normalized()
    return [_hoop(fig, c, n, 0.03 * h, OUTER_FIT, CLEAR_M + 0.008 * h, "accent")]


def _ice(fig):
    """Ice: a fur collar at the neck's root (NpcMeshes: hoop at Neck - 0.008 h, tube 0.03 h) and gloves."""
    h = fig.h
    z = fig.neck - 0.008 * h
    # Resting on the shoulder slope up to the neck, in tufts all round so it reads as fur rather than a padded tube.
    rings = []
    for dz, out in ((-0.035 * h, 0.006 * h), (-0.015 * h, 0.016 * h), (0.006 * h, 0.012 * h), (0.016 * h, 0.004 * h)):
        c, n = _flat(fig, z + dz)
        u, v, radii = _profile(fig, c, n, 0.012, fig.torso)
        rings.append(_ring(c, n, u, v, radii, OUTER_FIT if dz < 0 else 1.0, CLEAR_M + out, 0.006 * h, 18.0))
    collar = _loft(rings, "fur", centre=_flat(fig, z)[0])

    def hand(k):
        p = Vector(fig.co[k])
        if fig.hand[k]:
            return True
        side = "l" if p.x > 0 else "r"
        return fig.w[k].get("lowerarm_" + side, 0.0) > 0.5 and fig.arm_frac(p, side) >= 0.9

    gloves = _shell(fig, hand, lambda k: Vector(fig.co[k]) + Vector(fig.no[k]) * 0.004, "leatherlight")
    return [collar, gloves]


def _crystal(fig):
    """Crystal: a broad belt between Hip and Waist and a strap hanging at the left hip (NpcMeshes Signature)."""
    h = fig.h
    z = fig.hip + 0.6 * (fig.waist - fig.hip)
    belt = _band(fig, z, 0.012 * h, OUTER_FIT, "accent", out=0.002)
    z = fig.hip + 0.03 * h
    p, n = fig.front(fig.hip_x, z, trunk=False)
    c = Vector((0.0, fig.axis_y(z), z))
    top = c + (p - c) * OUTER_FIT + n * (CLEAR_M + 0.022 * h)
    strap = _tube(top, top + Vector((0.01 * h, -0.005 * h, -0.2 * h)), 0.022 * h, 0.03 * h, "accent", n=10)
    return [belt, strap]


def _twilight(fig):
    """Twilight: a sash knotted between Hip and Waist and a lantern hung at the right hip (NpcMeshes Signature)."""
    h = fig.h
    z = fig.hip + 0.7 * (fig.waist - fig.hip)
    sash = _band(fig, z, 0.011 * h, OUTER_FIT, "accent", out=0.002)
    side = fig.co[fig.torso & (np.abs(fig.co[:, 2] - fig.hip) < 0.015) & (fig.co[:, 0] < 0), 0].min()
    hang = Vector((side * OUTER_FIT - 0.01 * h, fig.axis_y(fig.hip) - 0.04 * h, fig.hip - 0.03 * h))
    cord = _tube(hang, hang - Vector((0, 0, 0.07 * h)), 0.004 * h, 0.004 * h, "leather", n=6)
    lamp = _sphere(hang - Vector((0, 0, 0.1 * h)), (0.03 * h, 0.03 * h, 0.04 * h), "glow")
    return [sash, cord, lamp]


def _ocean(fig):
    """Ocean: a sarong tied between Hip and Waist, its knot and two short tails at the front left (NpcMeshes Signature;
    procedural -x is the figure's left, +x here). The head cloth stays a procedural part."""
    h = fig.h
    z = fig.hip + 0.4 * (fig.waist - fig.hip)
    sarong = _band(fig, z, 0.014 * h, OUTER_FIT, "accent", out=0.002)
    knot, _ = _front_point(fig, 0.35 * fig.hip_x, z, OUTER_FIT, CLEAR_M + 0.012 * h)
    parts = [sarong, _sphere(knot, (0.022 * h, 0.016 * h, 0.02 * h), "accentdark", 8, 6)]
    for s in (-1, 1):
        parts.append(_tube(knot, knot + Vector((s * 0.012 * h, -0.006 * h, -0.11 * h)), 0.012 * h, 0.008 * h, "accent", n=8))
    return parts


def _gale(fig):
    """Gale: a wide beaded collar lying on the shoulders, three rings stepping out and down (NpcMeshes Signature)."""
    h, parts = fig.h, []
    for k, role in enumerate(("accent", "cloth2", "accentdark")):
        z = fig.neck - (0.012 + 0.014 * k) * h
        parts.append(_band(fig, z, 0.0055 * h, 1.0, role, out=0.004 * h * k + 0.004 * h, folds=0.002 * h, freq=24.0))
    return parts


def _radiant(fig):
    """Radiant: a long shawl from the left shoulder across the chest to the right hip and round the back (like the lava
    sash, about 1.1 x as wide), and its end hanging down the back from the left shoulder (NpcMeshes Signature). The turban
    stays a procedural part."""
    h = fig.h
    a = fig.head_of["upperarm_l"] + Vector((-0.02 * h, 0.0, 0.03 * h))
    b = Vector((-fig.hip_x, fig.axis_y(fig.hip), fig.hip + 0.03 * h))
    d = (b - a).normalized()
    t = -a.x / (b.x - a.x)
    z = a.z + (b.z - a.z) * t
    c = Vector((0.0, fig.axis_y(z), z))
    n = d.cross(Vector((0.0, 1.0, 0.0))).normalized()
    shawl = _hoop(fig, c, n, 0.034 * h, OUTER_FIT, CLEAR_M + 0.003 * h, "accent")
    sh = fig.head_of["upperarm_l"]
    x = 0.6 * sh.x
    band = fig.torso & (np.abs(fig.co[:, 2] - (sh.z - 0.02 * h)) < 0.02) & (np.abs(fig.co[:, 0] - x) < 0.03)
    back = Vector((x, fig.co[band, 1].max() + CLEAR_M + 0.012 * h, sh.z - 0.01 * h))
    tail = _tube(back, back + Vector((-0.01 * h, 0.02 * h, -0.24 * h)), 0.04 * h, 0.03 * h, "accentdark", n=8)
    return [shawl, tail]


def _metropolis(fig):
    """Metropolis: a short stand collar at the neck's root and a strap on each shoulder (NpcMeshes Signature). The
    earpiece stays a procedural part."""
    h = fig.h
    collar = _band(fig, fig.neck - 0.004 * h, 0.016 * h, 1.0, "clothdark", out=0.006 * h)
    parts = [collar]
    for side in ("l", "r"):
        parts.append(_pad(fig, side, "accent", 0.004 * h, 0.01 * h))
    return parts


def _front_point(fig, x, z, fit, out):
    p, n = fig.front(x, z)
    c = Vector((0.0, fig.axis_y(z), z))
    return c + (p - c) * fit + n * out, n


def _primal(fig):
    """Primal: five bone beads in an arc across the chest (NpcMeshes Dress, ArchEra.Primal, fit 1.12)."""
    h, parts = fig.h, []
    for i in range(-2, 3):
        z = fig.chest - 0.02 * h - 0.006 * h * (4 - i * i)
        p, _ = _front_point(fig, i * 0.028 * h, z, 1.12, CLEAR_M + 0.011 * h * 0.6)
        parts.append(_sphere(p, (0.011 * h,) * 3, "bone", 8, 6))
    return parts


def _buttons(fig, fit):
    h, parts = fig.h, []
    for i in range(3):
        z = fig.chest - 0.07 * h - i * 0.045 * h
        p, _ = _front_point(fig, 0.0, z, fit, CLEAR_M + 0.004 * h)
        parts.append(_sphere(p, (0.01 * h, 0.006 * h, 0.01 * h), "metal", 8, 6))
    return parts


def _pad(fig, side, role, rise, out):
    """A shoulder plate over one shoulder (steampunk brass, wasteland scrap): the top of the shoulder lifted off the skin."""
    joint = fig.head_of["upperarm_" + side]

    def pred(k):
        p = Vector(fig.co[k])
        w = fig.w[k]
        if w.get("upperarm_" + side, 0.0) + w.get("clavicle_" + side, 0.0) < 0.5:
            return False
        t = fig.arm_frac(p, side)
        return -0.12 <= t <= 0.3 and p.z >= joint.z - 0.02 * fig.h

    def lift(k):
        p = Vector(fig.co[k])
        t = max(0.0, fig.arm_frac(p, side))
        return p + Vector(fig.no[k]) * (out + rise * (1.0 - (t / 0.3) ** 2))

    return _shell(fig, pred, lift, role, thickness=0.004)


def _industrial(fig):
    # Industrial and steampunk coats are common (CutOdds): the buttons sit on a coat's ease (Coat fit >= 1.17).
    return _buttons(fig, 1.17)


def _steampunk(fig):
    return _buttons(fig, 1.17) + [_pad(fig, "l", "metal", 0.02 * fig.h, 0.025 * fig.h)]


def _future(fig):
    """Future: a metal plate on the chest (NpcMeshes Dress, ArchEra.Future; future clothes do not glow), on a coat's ease
    like the industrial buttons."""
    h = fig.h
    z = fig.chest - 0.07 * h
    pts = []
    for x, dz in ((0.03 * h, 0.03 * h), (-0.03 * h, 0.03 * h), (0.0, -0.02 * h)):
        p, n = _front_point(fig, x, z + dz, 1.17, CLEAR_M + 0.002)
        pts.append((p, n))
    n = sum((q for _, q in pts), Vector()).normalized()
    return [_panel(pts[0][0], pts[1][0], pts[2][0], n, 0.003, "metal")]


def _wasteland(fig):
    """Wasteland: a scarf wound thick at the neck with one end hanging, and a dark pad on the right shoulder
    (NpcMeshes Dress, ArchEra.Wasteland, fit 1.2)."""
    h = fig.h
    z = fig.neck - 0.005 * h
    scarf = _band(fig, z, 0.022 * h, 1.0, "accent", out=0.016 * h, folds=0.006 * h, freq=5.0)
    end_top, _ = _front_point(fig, -0.5 * fig.hr, z - 0.025 * h, OUTER_FIT, 0.02 * h)
    end = _tube(end_top, end_top + Vector((-0.2 * fig.hr, -0.01 * h, -0.2 * h)), 0.02 * h, 0.012 * h, "accent", n=7)
    return [scarf, end, _pad(fig, "r", "dark", 0.014 * h, 0.022 * h)]


SLOTS = {
    "piece_Verdant": _capelet,
    "piece_Lava": _sash,
    "piece_Ice": _ice,
    "piece_Crystal": _crystal,
    "piece_Twilight": _twilight,
    "piece_Ocean": _ocean,
    "piece_Gale": _gale,
    "piece_Radiant": _radiant,
    "piece_Metropolis": _metropolis,
    "trim_Primal": _primal,
    "trim_Industrial": _industrial,
    "trim_Steampunk": _steampunk,
    "trim_Future": _future,
    "trim_Wasteland": _wasteland,
}


# ---- meshing, keys, weights ---------------------------------------------------------------------------------------


def _solid(part):
    """Part geometry as a closed bmesh: shells and the cape get their cloth thickness; a lined part (the cape) puts its
    lining material on the faces that look toward the body."""
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in part.verts]
    for f in part.faces:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    bm.normal_update()
    t = getattr(part, "thickness", 0.0)
    out = getattr(part, "outward", None)
    centre = getattr(part, "centre", None)
    axis = getattr(part, "axis", None)
    if axis is not None:
        # A tube round a slanted limb (sleeve, trouser leg): outward is away from the limb's own line.
        a, d = axis

        def radial(p):
            q = p - a
            return q - d * q.dot(d)

        flip = sum(f.normal.dot(radial(f.calc_center_median())) for f in bm.faces) < 0
    elif centre is not None:
        flip = sum(f.normal.dot((f.calc_center_median() - centre) * Vector((1.0, 1.0, 0.0))) for f in bm.faces) < 0
    else:
        flip = out is not None and sum((f.normal for f in bm.faces), Vector()).dot(out) < 0
    if flip:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
        bm.normal_update()
    if t:
        bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=t)
        bm.normal_update()
    return bm


def _assemble(name, parts, mats):
    verts, faces, fmat, near = [], [], [], []
    roles = []
    for part in parts:
        bm = _solid(part)
        base = len(verts)
        verts.extend(v.co.copy() for v in bm.verts)
        near.extend([part.near] * len(bm.verts))
        at = {v: base + i for i, v in enumerate(bm.verts)}
        lining = getattr(part, "lining", None)
        for f in bm.faces:
            faces.append(tuple(at[v] for v in f.verts))
            # The lining faces the body (a cape's -y side) or, on a wing membrane or feather, its lining_dir.
            role = lining if lining and f.normal.dot(getattr(part, "lining_dir", Vector((0.0, -1.0, 0.0)))) > 0 else part.role
            if role not in roles:
                roles.append(role)
            fmat.append(roles.index(role))
        bm.free()
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    for role in roles:
        me.materials.append(mats[role])
    me.polygons.foreach_set("material_index", fmat)
    me.validate()
    for p in me.polygons:
        p.use_smooth = True
    # UMA's slot builder wants a UV set; colour is a shader parameter, so one point serves.
    uv = me.uv_layers.new(name="UVMap")
    for loop in uv.data:
        loop.uv = (0.5, 0.5)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob, near


def _nearest(fig, ob, near):
    """Per vertex: its NEAREST skin vertices (indices into fig.co) and inverse-square-distance weights summing to 1.
    A part tagged "torso" (the cape) follows only the trunk, so its hem is not pulled along by the legs it hangs past."""
    idx, wts = [], []
    for v, tag in zip(ob.data.vertices, near):
        if tag == "torso":
            found = [(None, int(fig.torso_idx[j]), d) for _, j, d in fig.torso_tree.find_n(v.co, NEAREST)]
        else:
            found = fig.tree.find_n(v.co, NEAREST)
        w = np.array([1.0 / max(d, 1e-4) ** 2 for _, _, d in found])
        idx.append([j for _, j, _ in found])
        wts.append(w / w.sum())
    return np.array(idx), np.array(wts)


def _keys(fig, ob, idx, wts):
    """Shape keys of the same name as every body key that moves this mesh by KEY_FLOOR_M or more."""
    keys = fig.body.data.shape_keys.key_blocks
    n = len(fig.body.data.vertices)
    basis = np.empty(n * 3)
    keys[0].data.foreach_get("co", basis)
    basis = basis.reshape(n, 3)[fig.skin]
    co = np.array([tuple(v.co) for v in ob.data.vertices])
    ob.shape_key_add(name="Basis", from_mix=False)
    kept = 0
    buf = np.empty(n * 3)
    for kb in keys[1:]:
        kb.data.foreach_get("co", buf)
        delta = buf.reshape(n, 3)[fig.skin] - basis
        moved = (delta[idx] * wts[:, :, None]).sum(axis=1)
        if np.abs(moved).max() < KEY_FLOOR_M:
            continue
        sk = ob.shape_key_add(name=kb.name, from_mix=False)
        sk.data.foreach_set("co", (co + moved).ravel())
        sk.value = 0.0
        kept += 1
    return kept


def _weights(fig, ob, idx, wts):
    groups = {}
    for vi in range(len(ob.data.vertices)):
        acc = {}
        for j, x in zip(idx[vi], wts[vi]):
            for b, w in fig.w[j].items():
                acc[b] = acc.get(b, 0.0) + w * x
        for b, w in acc.items():
            if b not in groups:
                groups[b] = ob.vertex_groups.new(name=b)
            groups[b].add([vi], w, "REPLACE")
    ob.parent = fig.rig
    ob.modifiers.new("Armature", "ARMATURE").object = fig.rig
    acg_render._limit_weights(ob, set(fig.rig.data.bones.keys()), 4)


def _param_keys(fig, ob, name, build, params, low, mats):
    """One shape key per parameter with a range (npc_cut.KEYS): the slot rebuilt with that parameter at its high end
    and the others low. Same builder, same topology, so the vertices correspond one to one."""
    import npc_cut
    kept = 0
    for p, (lo, hi) in params.items():
        if hi <= lo:
            continue
        values = dict(low)
        values[p] = hi
        tmp, _ = _assemble(name + "_tmp", build(fig, **values), mats)
        if len(tmp.data.vertices) != len(ob.data.vertices):
            raise SystemExit("%s: %s changes the topology (%d vs %d vertices)" % (name, p, len(tmp.data.vertices),
                                                                                 len(ob.data.vertices)))
        co = np.empty(len(tmp.data.vertices) * 3)
        tmp.data.vertices.foreach_get("co", co)
        me = tmp.data
        bpy.data.objects.remove(tmp)
        bpy.data.meshes.remove(me)
        sk = ob.shape_key_add(name=npc_cut.KEYS[p], from_mix=False)
        sk.data.foreach_set("co", co)
        sk.value = 0.0
        kept += 1
    return kept


def _preview(fig, obs, path):
    """Workbench sheet: every slot on the body, front and back."""
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "MATERIAL"
    sc.render.resolution_x, sc.render.resolution_y = 600, 800
    cam = bpy.data.objects.new("outfit_cam", bpy.data.cameras.new("outfit_cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = fig.h * 1.1
    fig.body.data.materials[0].diffuse_color = (0.85, 0.72, 0.62, 1)
    # The inverted-hull outline renders as a solid skin in Workbench and swallows everything within its width.
    for m in fig.body.modifiers:
        if m.type == "SOLIDIFY":
            m.show_render = False
    # race.py leaves every key at 1 in the .blend; Unity starts them at 0, as the slots' keys are.
    for k in fig.body.data.shape_keys.key_blocks[1:]:
        k.value = 0.0
    tones = {"accent": (0.75, 0.25, 0.2), "accentdark": (0.5, 0.15, 0.12), "leather": (0.35, 0.24, 0.16),
             "leatherlight": (0.5, 0.36, 0.26), "metal": (0.78, 0.6, 0.25), "glow": (0.5, 1.0, 1.0), "bone": (0.92, 0.88, 0.78),
             "fur": (0.94, 0.92, 0.88), "dark": (0.23, 0.21, 0.2), "cloth": (0.3, 0.45, 0.62), "clothlow": (0.26, 0.4, 0.55),
             "clothdark": (0.24, 0.36, 0.5), "cloth2": (0.55, 0.5, 0.4), "cloth2shade": (0.5, 0.45, 0.36),
             "cloth2dark": (0.33, 0.3, 0.24), "braid": (0.6, 0.2, 0.16)}
    for role, c in tones.items():
        m = bpy.data.materials.get("npc_wear_" + role)
        m.diffuse_color = c + (1.0,)
    # npc_appendage roles: a name and an optional percentage.
    family = {"body": (0.72, 0.52, 0.38), "mane": (0.3, 0.2, 0.14), "plume": (0.5, 0.36, 0.26), "angel": (0.96, 0.95, 0.91),
              "angeltip": (1.0, 0.99, 0.96), "angelcovert": (0.93, 0.9, 0.85), "claw": (0.16, 0.13, 0.14),
              "vampire": (0.12, 0.09, 0.13), "vampirelining": (0.48, 0.12, 0.16)}
    for m in bpy.data.materials:
        role = m.name[len("npc_wear_"):] if m.name.startswith("npc_wear_") else None
        name = role.rstrip("0123456789") if role else None
        if name in family and role not in tones:
            k = int(role[len(name):] or 100) / 100
            m.diffuse_color = tuple(min(1.0, x * k) for x in family[name]) + (1.0,)
    for o in bpy.data.objects:
        if o.type == "MESH" and o not in obs and o.parent == fig.rig and o != fig.body and o.name.startswith("prop_"):
            o.hide_render = True
    base = os.path.splitext(path)[0]
    centre = Vector((0.0, 0.0, fig.h * 0.5))
    for ob in obs:
        for o in obs:
            o.hide_render = o != ob
        for yaw in (0, 180):
            a = math.radians(yaw)
            d = Vector((-math.sin(a), -math.cos(a), 0))
            cam.location = centre + d * 4
            cam.rotation_euler = (math.radians(90), 0, math.atan2(d.x, -d.y))
            sc.render.filepath = "%s_%s_%d.png" % (base, ob.name, yaw)
            bpy.ops.render.render(write_still=True)


def main():
    a = _args()
    rig, body = npc_hair._body()
    fig = Fig(rig, body)
    mats = {}
    for role in OUTFIT_ROLES:
        mats[role] = bpy.data.materials.get("npc_wear_" + role) or bpy.data.materials.new("npc_wear_" + role)
    import npc_cut
    import npc_appendage
    slots = {name: (build, {}) for name, build in SLOTS.items()}
    slots.update(npc_cut.SLOTS)
    race = os.path.basename(bpy.data.filepath).split("_")[1]
    swung = npc_appendage.slots_for(race)
    if a.slots:
        want = tuple(a.slots.split(","))
        slots = {n: v for n, v in slots.items() if n.startswith(want)}
        swung = {n: v for n, v in swung.items() if n.startswith(want)}
    obs, report = [], []
    for name, (build, params) in slots.items():
        low = {p: r[0] for p, r in params.items()}
        ob, near = _assemble(name, build(fig, **low), mats)
        idx, wts = _nearest(fig, ob, near)
        kept = _keys(fig, ob, idx, wts)
        kept += _param_keys(fig, ob, name, build, params, low, mats)
        _weights(fig, ob, idx, wts)
        obs.append(ob)
        report.append("%s:%d/%d" % (name, len(ob.data.vertices), kept))
    chains = []
    for name, build in swung.items():
        slot = build(fig)
        for part in slot.parts:
            for role in (part.role, getattr(part, "lining", None)):
                if role and role not in mats:
                    mats[role] = bpy.data.materials.get("npc_wear_" + role) or bpy.data.materials.new("npc_wear_" + role)
            # _assemble copies `near` per vertex; these parts are weighted by chain, so it carries the part itself.
            part.near = part
        ob, owners = _assemble(name, slot.parts, mats)
        owner = npc_appendage.weigh(ob, slot, owners)
        kept = npc_appendage.keys(fig, ob, slot, owner)
        ob.parent = fig.rig
        ob.modifiers.new("Armature", "ARMATURE").object = fig.rig
        chains += slot.chains
        obs.append(ob)
        report.append("%s:%d/%d/%d" % (name, len(ob.data.vertices), kept, len(slot.chains)))
    if chains:
        import acg_swing
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode="EDIT")
        acg_swing._add_bones(rig, chains)
        bpy.ops.object.mode_set(mode="OBJECT")
    if a.preview:
        _preview(fig, obs, a.preview)
    npc_hair._export(rig, obs, a.fbx)
    print("NPC_OUTFIT_OK", os.path.basename(a.fbx), "h=%.3f hr=%.3f" % (fig.h, fig.hr), " ".join(report))


if __name__ == "__main__":
    main()
