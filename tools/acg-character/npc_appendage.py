"""Wings, tails and capes of the NPC races as wardrobe slots with their own swing chains (ADR-0015, cosmos_chimera
docs/design/npc-uma-looks.md row 15, #翼尾披風). Imported by npc_outfit.py, which builds them into the same outfit FBX.

Each slot is what the procedural NpcMeshes draws (Tail, WorldTail, Wings, Cape), in its sizes (the base's height h and
arm, leg and trunk measures taken on this base's skin), rooted on this base's back. Unlike the garments, a slot does
not follow the skin it hangs past: every vertex is weighted to a "sw_<item>_<k>_<i>" bone chain (acg_swing naming, the
chain's zero-weight "_end" bone gives the solver the tip) under one body bone, and its body shape keys move it as the
skin at its chain's root moves. Unity's SpringBones swings the chains (stiffness by prefix: tails and wings keep their
modelled shape, capes hang).

Slots: "wings_<Race>" (angel, avian, tengu: folded feathers; demon, dragonkin: membrane), "tail_<Race>" (lizardfolk,
dragonkin, werewolf, demon, avian, simian, oxhead, horseface, shrimpfolk), "cape_Vampire" (with a standing collar), and
"piece_Storm" (the storm region's cape, built here for every base so it gets its chains too).

Colour roles (Unity NpcUmaRaces.OutfitColour): "body", "mane" (the recipe's skin and hair colours), "plume" (skin toward
hair, 0.55: the feather tips), fixed tones "angel", "angeltip", "angelcovert", "claw", "vampire", "vampirelining"; a
number after the name is a percentage on that colour ("body62": skin x 0.62).
"""
import math

import bmesh
import numpy as np
from mathutils import Vector

import npc_outfit as O

FEATHER_M = 0.0012
MEMBRANE_M = 0.0015
CAPE_M = 0.004


def _B(x, y, z):
    """A procedural offset (NpcMeshes: up +y, front +z) in Blender axes (up +z, front -y). x keeps its sign: every shape
    here is drawn for both sides or is symmetric enough that a mirror does not matter."""
    return Vector((x, -z, y))


def _tone(name, scale):
    k = int(round(scale * 100))
    return name if k == 100 else "%s%d" % (name, k)


def _scaled(role, k):
    """`role` with its percentage multiplied by k ("body62", 0.8 -> "body50")."""
    name = role.rstrip("0123456789")
    return _tone(name, int(role[len(name):] or 100) / 100 * k)


class Frame:
    """The procedural Rig measures NpcMeshes uses for these parts, taken on this base."""

    def __init__(self, fig):
        self.fig = fig
        self.h = fig.h
        band = fig.torso & (np.abs(fig.co[:, 2] - fig.chest) < 0.015)
        ys = fig.co[band, 1]
        self.trunk_z = 0.5 * float(ys.max() - ys.min())
        self.chest = Vector((0.0, fig.axis_y(fig.chest), fig.chest))
        self.arm_r = self._radius("upperarm_l")
        self.leg_r = self._radius("calf_l")

    def _radius(self, bone):
        k = np.array([w.get(bone, 0.0) > 0.6 for w in self.fig.w])
        ds = [self.fig.bone_axis_dist(i, bone) for i in np.nonzero(k)[0]]
        return float(np.median(ds))

    def back(self, z, sink=0.01):
        """The middle of the back's skin at height z, `sink` inside it so a root never shows its cut end."""
        fig = self.fig
        band = fig.torso & (np.abs(fig.co[:, 2] - z) < 0.015) & (np.abs(fig.co[:, 0]) < 0.03)
        return Vector((0.0, float(fig.co[band, 1].max()) - sink, z))


# ---- geometry (NpcMeshes.Fig) -------------------------------------------------------------------------------------


def _bezier(p0, p1, p2, t):
    u = 1.0 - t
    return p0 * (u * u) + p1 * (2 * u * t) + p2 * (t * t)


def _oriented(part, faces, hint):
    """Faces turned so their normal agrees with hint(face centre) (a vector or a function of the centre)."""
    for f in faces:
        ps = [part.verts[i] for i in f]
        n = (ps[1] - ps[0]).cross(ps[-1] - ps[0])
        c = sum(ps, Vector()) / len(ps)
        h = hint(c) if callable(hint) else hint
        part.faces.append(tuple(f) if n.dot(h) >= 0 else tuple(reversed(f)))


def _lock(p0, p1, p2, centre, width, thick, role, segments=5, sides=6, tip_share=0.0):
    """NpcMeshes Fig.Lock: a quadratic curve swept by an ellipse that swells past the root and closes to a point."""
    part = O.Part(role)
    last_wide = Vector((1.0, 0.0, 0.0))
    mids = []
    for i in range(segments + 1):
        t = i / segments
        p = _bezier(p0, p1, p2, t)
        tangent = (p1 - p0) * (2 * (1 - t)) + (p2 - p1) * (2 * t)
        tangent = tangent.normalized() if tangent.length > 1e-9 else Vector((0.0, 0.0, -1.0))
        wide = tangent.cross(p - centre)
        wide = last_wide if wide.length_squared < 1e-10 else wide.normalized()
        wide = (wide - tangent * wide.dot(tangent)).normalized()
        last_wide = wide
        deep = wide.cross(tangent)
        swell = (1 - t * t) * (0.8 + 0.4 * math.sin(math.pi * t))
        swell = max(swell, tip_share * (1 - t))
        for k in range(sides):
            a = k * math.pi * 2 / sides
            part.verts.append(p + (wide * math.cos(a) * width + deep * math.sin(a) * thick) * max(swell, 0.02))
        mids.append(p)
    quads = []
    for i in range(segments):
        for k in range(sides):
            n = (k + 1) % sides
            quads.append((i * sides + k, i * sides + n, (i + 1) * sides + n, (i + 1) * sides + k))
    cap = len(part.verts)
    part.verts.append(p0.copy())
    fans = [(cap, k, (k + 1) % sides) for k in range(sides)]

    def out(c):
        best = min(range(len(mids)), key=lambda j: (mids[j] - c).length)
        return c - mids[best]

    _oriented(part, quads, out)
    _oriented(part, fans, p0 - _bezier(p0, p1, p2, 0.1))
    return part


def _sheet(pts, rows, cols, front, role, lining, thickness):
    """NpcMeshes Fig.Sheet as a thin solid: rows x cols points, faces toward `front`, the other side in `lining`."""
    part = O.Part(role)
    part.verts = [p.copy() for p in pts]
    quads = [(i * cols + k, i * cols + k + 1, (i + 1) * cols + k + 1, (i + 1) * cols + k)
             for i in range(rows - 1) for k in range(cols - 1)]
    _oriented(part, quads, front)
    part.thickness = thickness
    part.lining = lining
    part.lining_dir = -front
    return part


def _feather(root, tip, back, width, lead, tone, tip_tone):
    """NpcMeshes Fig.Feather: a pointed vane cupped toward `back`; the root two thirds in `tone`, the tip in tip_tone."""
    along = tip - root
    length = along.length
    if length < 1e-4:
        return []
    d = along / length
    across = back.cross(d)
    across = across.normalized() if across.length > 1e-9 else Vector((1.0, 0.0, 0.0))
    up = d.cross(across).normalized()
    profile = (0.4, 1.0, 0.82, 0.0)
    rows = []
    for i, k in enumerate(profile):
        t = i / 3
        shaft = root + along * t + up * (length * 0.07 * 4 * t * (1 - t))
        w = width * k
        rows.append([shaft - across * w * lead - up * w * 0.18, shaft, shaft + across * w - up * w * 0.18])
    base = _sheet([p for r in rows[:3] for p in r], 3, 3, up, tone, _scaled(tone, 0.86), FEATHER_M)
    end = _sheet([p for r in rows[2:] for p in r], 2, 3, up, tip_tone, _scaled(tip_tone, 0.86), FEATHER_M)
    return [base, end]


def _panel(a, b, c, role, depth=0.003):
    n = (b - a).cross(c - a)
    return O._panel(a, b, c, n.normalized() if n.length > 1e-9 else Vector((0.0, -1.0, 0.0)), depth, role)


# ---- slots --------------------------------------------------------------------------------------------------------


class Slot:
    """Parts plus the chains they swing on: [(parent bone, [joints root..tip], [bone names])]. `blend` lets a vertex
    share two neighbouring chains (a cape's columns); `rigid` parts ride the parent bone only (a collar)."""

    def __init__(self, parts, chains, blend=False):
        self.parts, self.chains, self.blend = parts, chains, blend


def _chain(item, k, parent, joints):
    return parent, joints, ["%s%s_%d_%d" % ("sw_", item, k, i) for i in range(len(joints) - 1)]


def _wings_feathered(race):
    def build(fig):
        f = Frame(fig)
        h = f.h
        angel = race == "angel"
        feather, tip_tone, covert = ("angel", "angeltip", "angelcovert") if angel else ("body", "plume", "body106")
        span, drop = (0.3 * h, 0.6 * h) if angel else (0.19 * h, 0.42 * h)
        fw = (0.075 if angel else 0.056) * h
        back = f.back(fig.chest - 0.04 * h)
        parts, chains = [], []
        for k, s in enumerate((-1, 1)):
            root = back + _B(s * 0.05 * h, 0.02 * h, 0.0)
            wrist = back + _B(s * span, 0.15 * h, -0.09 * h)
            elbow = back + _B(s * span * 0.55, 0.02 * h, -0.05 * h)
            outside = _B(s * 0.4, 0.05, -1.0).normalized()
            arm_mid = elbow + _B(0.0, 0.1 * h, 0.0)
            parts.append(_lock(root, arm_mid, wrist, back, f.arm_r * 1.25, f.arm_r * 0.9,
                               "angelcovert" if angel else "body", 5, 6, 0.6))
            primaries, secondaries = 6, 7
            for i in range(primaries + secondaries):
                primary = i < primaries
                t = i / (primaries - 1) if primary else (i - primaries + 1) / secondaries
                at = (wrist.lerp(wrist.lerp(elbow, 0.35), t) if primary
                      else wrist.lerp(elbow, 0.35).lerp(root, t))
                reach = drop * (1 - 0.06 * t) if primary else drop * (0.9 - 0.42 * t)
                fan = 0.12 - 0.06 * t if primary else 0.04 * (1 - t)
                d = _B(s * fan, -1.0, -0.18 + 0.1 * t).normalized()
                tip = at + d * reach
                tip.z = max(tip.z, 0.08 * h)
                lift = outside * (0.0025 * h * (primaries + secondaries - i))
                tone = feather if i % 2 == 0 else _scaled(feather, 0.94)
                parts += _feather(at + lift, tip + lift, outside, fw * 0.95 if primary else fw, 0.55 if primary else 0.85,
                                  tone, tip_tone)
            for i in range(8):
                t = i / 7
                at = wrist.lerp(root, t) + Vector((0.0, 0.0, 0.01 * h))
                tip = at + _B(s * 0.05, -1.0, -0.12).normalized() * drop * (0.3 - 0.08 * t)
                lift = outside * (0.045 * h + 0.002 * h * i)
                tone = covert if i % 2 == 0 else _scaled(covert, 0.95)
                parts += _feather(at + lift, tip + lift, outside, fw * 1.1, 0.9, tone, covert)
            chains.append(_chain("wing", k, "spine_03", [root, _bezier(root, arm_mid, wrist, 0.5), wrist]))
        return Slot(parts, chains)
    return build


def _wings_membrane(race):
    def build(fig):
        f = Frame(fig)
        h = f.h
        size = (0.46 if race == "demon" else 0.3) * h
        back = f.back(fig.chest - 0.04 * h)
        bone = f.arm_r * 0.75
        parts, chains = [], []
        for k, s in enumerate((-1, 1)):
            outside = _B(s * 0.45, 0.1, -1.0).normalized()
            elbow = back + _B(s * size * 0.38, size * 0.12, -size * 0.15)
            wrist = back + _B(s * size * 0.8, size * 0.42, -size * 0.32)
            parts.append(_lock(back, elbow, wrist, back - outside, bone, bone, "body80", 4, 6, 0.6))
            claw = wrist + _B(s * size * 0.06, size * 0.12, size * 0.02)
            parts.append(_lock(wrist, claw + _B(0.0, 0.03 * size, 0.0), claw + _B(s * size * 0.03, -0.02 * size, 0.05 * size),
                               wrist, bone * 0.7, bone * 0.7, "claw", 3, 5))
            tips = [wrist + _B(s * size * 0.32, size * 0.22, -size * 0.06)]
            for i in range(3):
                tips.append(wrist + _B(s * size * (0.6 - 0.32 * i), -size * (0.42 + 0.36 * i), -size * (0.22 + 0.05 * i)))
            hip = back + _B(s * size * 0.08, -size * 0.55, 0.0)
            tips.append(hip)
            bends = []
            for i in range(5):
                bends.append(wrist.lerp(tips[i], 0.5) + outside * (0.06 * size) + _B(s * 0.04 * size, 0.04 * size, 0.0))
                if i < 4:
                    parts.append(_lock(wrist, bends[i], tips[i], wrist - outside, bone * 0.55, bone * 0.55, "body80", 4, 5))
            rows = cols = 5
            for fi in range(-1, 4):
                edge_mid = ((back if fi < 0 else tips[fi]) + tips[fi + 1]) * 0.5
                scallop = 0.12 if fi < 0 else 0.04 if fi == 3 else 0.07
                pts = []
                for i in range(rows):
                    t = i / (rows - 1)
                    l0 = _bezier(wrist, elbow, back, t) if fi < 0 else _bezier(wrist, bends[fi], tips[fi], t)
                    l1 = back.lerp(hip, t) if fi + 1 == 4 else _bezier(wrist, bends[fi + 1], tips[fi + 1], t)
                    for c in range(cols):
                        v = c / (cols - 1)
                        belly = 4 * v * (1 - v)
                        pts.append(l0.lerp(l1, v) + (wrist - edge_mid) * (scallop * belly * t * t)
                                   - outside * (0.05 * size * belly * math.sin(math.pi * t)))
                parts.append(_sheet(pts, rows, cols, outside, "body62", "body50", MEMBRANE_M))
            last = _bezier(wrist, elbow, back, 0.45)
            for fi in range(4):
                nxt = _bezier(wrist, bends[fi], tips[fi], 0.45)
                parts.append(_panel(wrist, last, nxt, "body62", MEMBRANE_M))
                last = nxt
            chains.append(_chain("wing", k, "spine_03", [back + _B(s * 0.04 * h, 0.0, 0.0), elbow, wrist]))
        return Slot(parts, chains)
    return build


def _tail(race):
    def build(fig):
        f = Frame(fig)
        h = f.h
        frm = f.back(fig.hip + 0.02 * h, sink=0.3 * f.leg_r)
        side = frm + _B(1.0, 0.0, 0.0)
        parts = []
        if race in ("lizardfolk", "dragonkin"):
            thick = f.leg_r * (1.5 if race == "dragonkin" else 1.15)
            a = frm + _B(0.0, -0.1 * h, -0.16 * h)
            c = a + _B(0.04 * h, -0.14 * h, -0.2 * h)
            d = Vector((c.x + 0.05 * h, c.y + 0.2 * h, max(0.04, c.z - 0.08 * h)))
            m1, m2 = a.lerp(c, 0.2), (c + d) * 0.5 + _B(0.0, 0.01 * h, 0.0)
            parts += [_lock(frm, m1, c, side, thick, thick, "body", 5, 8, 0.75),
                      _lock(c, m2, d, c + _B(1.0, 0.0, 0.0), thick * 0.56, thick * 0.56, "body88", 4, 7)]
            joints = [frm, _bezier(frm, m1, c, 0.5), c, _bezier(c, m2, d, 0.5), d]
        elif race == "werewolf":
            tip = frm + _B(0.0, -0.12 * h, -0.3 * h)
            parts.append(O._sphere((frm + tip) * 0.5, (f.leg_r * 1.3, 0.17 * h, 0.1 * h), "body92", 14, 10))
            joints = [frm, frm.lerp(tip, 0.5), tip]
        elif race == "demon":
            a = frm + _B(0.05 * h, -0.2 * h, -0.2 * h)
            c = a + _B(0.08 * h, 0.06 * h, -0.16 * h)
            parts.append(_lock(frm, a, c, side, f.arm_r * 0.55, f.arm_r * 0.55, "body", 6, 6, 0.55))
            parts.append(_panel(c + _B(0.0, 0.05 * h, 0.0), c + _B(0.03 * h, -0.03 * h, -0.05 * h),
                                c + _B(-0.03 * h, -0.03 * h, 0.02 * h), "body80"))
            joints = [frm, _bezier(frm, a, c, 1 / 3), _bezier(frm, a, c, 2 / 3), c]
        elif race == "avian":
            for i in range(-3, 4):
                quill = frm + _B(i * 0.012 * h, 0.01 * h * (3 - abs(i)), 0.0)
                tip = frm + _B(i * 0.055 * h, -0.15 * h + abs(i) * 0.012 * h, -0.26 * h + abs(i) * 0.03 * h)
                parts += _feather(quill, tip, _B(0.0, 0.6, -0.4).normalized(), 0.03 * h, 0.8,
                                  "body86" if i % 2 == 0 else "body95", "plume")
            end = frm + _B(0.0, -0.15 * h, -0.26 * h)
            joints = [frm, frm.lerp(end, 0.5), end]
        elif race == "simian":
            a = frm + _B(0.02 * h, -0.18 * h, -0.12 * h)
            m = a + _B(0.06 * h, -0.12 * h, -0.14 * h)
            e = m + _B(0.03 * h, 0.14 * h, -0.06 * h)
            m2 = m + (m - a) * 0.3
            parts += [_lock(frm, a, m, side, f.arm_r * 0.5, f.arm_r * 0.5, "body", 5, 7, 0.6),
                      _lock(m, m2, e, side, f.arm_r * 0.4, f.arm_r * 0.4, "body90", 4, 6)]
            joints = [frm, _bezier(frm, a, m, 0.5), m, _bezier(m, m2, e, 0.5), e]
        elif race in ("oxhead", "horseface"):
            horse = race == "horseface"
            tip = frm + _B(0.0, -(0.3 if horse else 0.34) * h, -(0.12 if horse else 0.07) * h)
            if horse:
                mid = frm + _B(0.0, -0.05 * h, -0.1 * h)
                parts.append(_lock(frm, mid, tip, side, f.leg_r * 0.9, f.leg_r * 0.6, "mane", 5, 7))
                joints = [frm, _bezier(frm, mid, tip, 1 / 3), _bezier(frm, mid, tip, 2 / 3), tip]
            else:
                parts.append(O._tube(frm, tip, f.arm_r * 0.3, f.arm_r * 0.2, "body", n=6))
                parts.append(O._sphere(tip, (f.arm_r * 0.6, f.arm_r * 0.6, f.arm_r * 1.1), "mane80", 10, 6))
                joints = [frm, frm.lerp(tip, 1 / 3), frm.lerp(tip, 2 / 3), tip + _B(0.0, -f.arm_r * 1.1, 0.0)]
        elif race == "shrimpfolk":
            hub = frm + _B(0.0, -0.12 * h, -0.1 * h)
            parts.append(O._tube(frm, hub, f.leg_r * 0.8, f.leg_r * 0.5, "body", n=8))
            for i in range(-2, 3):
                tip = hub + _B(i * 0.05 * h, -0.1 * h + abs(i) * 0.015 * h, -0.08 * h)
                parts.append(_panel(hub + _B(-0.02 * h, 0.0, 0.0), hub + _B(0.02 * h, 0.0, 0.0), tip,
                                    _tone("body", 1 - 0.05 * abs(i))))
            joints = [frm, hub, hub + _B(0.0, -0.1 * h, -0.08 * h)]
        else:
            raise SystemExit("no tail for " + race)
        return Slot(parts, [_chain("tail", 0, "pelvis", joints)])
    return build


def _drape(item, fall, outer, lining, collar):
    """NpcMeshes.Cape: cloth from the back of the shoulders, wrapping the upper back, falling in 3.5 folds that open
    toward the hem; five chains down its columns."""
    def build(fig):
        h = fig.h
        rows, cols, folds = 7, 15, 3.5
        sl, sr = fig.head_of["upperarm_l"], fig.head_of["upperarm_r"]
        yb = fig.axis_y(fig.chest)
        back = fig.co[fig.torso & (np.abs(fig.co[:, 2] - fig.chest) < 0.02), 1].max()
        top_y = yb + (back - yb) * 0.4
        hem_z = max(0.05 * h, fig.chest * (1 - fall))

        def at(u, v):
            arc = math.sin(math.pi * u)
            x = sl.x + (sr.x - sl.x) * u
            top = Vector((x, top_y + (back + 0.01 * h - top_y) * arc + 0.02 * h, sl.z + 0.02 * h + 0.015 * h * arc))
            hem = Vector((x * 1.45, top.y + 0.12 * h + 0.04 * h * arc, hem_z))
            fold = math.sin(u * math.pi * 2 * folds + 0.4)
            p = top.lerp(hem, v)
            p.y += 0.035 * h * math.sin(math.pi * min(1.0, v * 1.6)) * arc
            p.y += 0.022 * h * fold * v
            p.z += 0.018 * h * fold * v * v
            return p

        pts = [at(k / (cols - 1), i / (rows - 1)) for i in range(rows) for k in range(cols)]
        cloth = _sheet(pts, rows, cols, Vector((0.0, 1.0, 0.0)), outer, lining, CAPE_M)
        parts = [cloth]
        if collar:
            hr = fig.hr
            neck = fig.head_of["neck_01"]
            for s in (-1, 1):
                root = neck + _B(s * hr * 0.75, -0.01 * h, -hr * 0.2)
                p = _panel(root + _B(0.0, 0.0, hr * 0.7), root + _B(-s * hr * 0.6, 0.0, -hr * 0.6),
                           root + _B(s * hr * 0.45, hr * 1.25, -hr * 0.1), lining)
                p.rigid = "spine_03"
                parts.append(p)
        chains = [_chain(item, k, "spine_03", [at(u, v / 3) for v in range(4)]) for k, u in enumerate((0.1, 0.3, 0.5, 0.7, 0.9))]
        return Slot(parts, chains, blend=True)
    return build


TAILS = ("lizardfolk", "dragonkin", "werewolf", "demon", "avian", "simian", "oxhead", "horseface", "shrimpfolk")
FEATHERED = ("angel", "avian", "tengu")
MEMBRANE = ("demon", "dragonkin")


def slots_for(race):
    """{slot name: builder(fig) -> Slot} for a base of `race` (lower case, as in its id)."""
    title = race.capitalize()
    out = {"piece_Storm": _drape("capestorm", 0.75, "accent", "accentdark", False)}
    if race in FEATHERED:
        out["wings_" + title] = _wings_feathered(race)
    if race in MEMBRANE:
        out["wings_" + title] = _wings_membrane(race)
    if race in TAILS:
        out["tail_" + title] = _tail(race)
    if race == "vampire":
        out["cape_Vampire"] = _drape("cape", 0.9, "vampire", "vampirelining", True)
    return out


# ---- weights and keys -------------------------------------------------------------------------------------------


def _along(p, joints):
    """Distance from p to the polyline and the position along it in segments (0 at the root)."""
    best = (float("inf"), 0.0)
    for j in range(len(joints) - 1):
        a, b = joints[j], joints[j + 1]
        d = b - a
        t = max(0.0, min(1.0, (p - a).dot(d) / max(d.length_squared, 1e-12)))
        dist = (p - (a + d * t)).length
        if dist < best[0]:
            best = (dist, j + t)
    return best


def _chain_weights(s, parent, names):
    """Hair's scheme (acg_swing.hair): full weight past mid-segment, shared with the bone above before it."""
    n = len(names)
    s = min(s, n - 0.001)
    i = int(s)
    f = s - i
    if f >= 0.5:
        return {names[i]: 1.0}
    return {names[i]: 0.5 + f, (names[i - 1] if i > 0 else parent): 0.5 - f}


def weigh(ob, slot, part_of_vertex):
    """Vertex groups: each vertex on its nearest chain (two neighbouring chains if slot.blend), rigid parts on their
    bone. Returns the chain index each vertex follows most (for its keys)."""
    groups = {}
    owner = []
    for vi, v in enumerate(ob.data.vertices):
        part = part_of_vertex[vi]
        acc = {}
        rigid = getattr(part, "rigid", None)
        if rigid:
            acc = {rigid: 1.0}
            near = [(0.0, 0)]
        else:
            near = sorted((_along(v.co, c[1])[0], k) for k, c in enumerate(slot.chains))
            use = near[:2] if slot.blend and len(near) > 1 else near[:1]
            if len(use) == 2:
                d0, d1 = use[0][0], use[1][0]
                share = [d1 / max(d0 + d1, 1e-9), d0 / max(d0 + d1, 1e-9)]
            else:
                share = [1.0]
            for (_, k), x in zip(use, share):
                parent, joints, names = slot.chains[k]
                for b, w in _chain_weights(_along(v.co, joints)[1], parent, names).items():
                    acc[b] = acc.get(b, 0.0) + w * x
        top = sorted(acc.items(), key=lambda bw: -bw[1])[:4]
        total = sum(w for _, w in top)
        for b, w in top:
            if b not in groups:
                groups[b] = ob.vertex_groups.new(name=b)
            groups[b].add([vi], w / total, "REPLACE")
        owner.append(near[0][1])
    return owner


def keys(fig, ob, slot, owner):
    """Body keys: every vertex moves as the skin at its chain's root does (inverse-square mean of the NEAREST trunk
    vertices there), so a wing or tail keeps its shape and rides the back as fat and muscle move it."""
    anchors = []
    for parent, joints, names in slot.chains:
        found = [(int(fig.torso_idx[j]), d) for _, j, d in fig.torso_tree.find_n(joints[0], O.NEAREST)]
        w = np.array([1.0 / max(d, 1e-4) ** 2 for _, d in found])
        anchors.append(([j for j, _ in found], w / w.sum()))
    kb = fig.body.data.shape_keys.key_blocks
    n = len(fig.body.data.vertices)
    basis = np.empty(n * 3)
    kb[0].data.foreach_get("co", basis)
    basis = basis.reshape(n, 3)[fig.skin]
    co = np.array([tuple(v.co) for v in ob.data.vertices])
    ob.shape_key_add(name="Basis", from_mix=False)
    buf = np.empty(n * 3)
    own = np.array(owner)
    kept = 0
    for k in kb[1:]:
        k.data.foreach_get("co", buf)
        delta = buf.reshape(n, 3)[fig.skin] - basis
        per = np.array([(delta[idx] * w[:, None]).sum(axis=0) for idx, w in anchors])
        moved = per[own]
        if np.abs(moved).max() < O.KEY_FLOOR_M:
            continue
        sk = ob.shape_key_add(name=k.name, from_mix=False)
        sk.data.foreach_set("co", (co + moved).ravel())
        sk.value = 0.0
        kept += 1
    return kept
