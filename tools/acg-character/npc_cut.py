"""The NPC cut slots: tops, skirts, trousers, boots and the small sleeve slots (ADR-0015, cosmos_chimera
docs/design/npc-uma-looks.md row 17, #服裝, Q-A26 = A). Built by npc_outfit.py into the same FBX as the pieces and trims.

What each slot is follows the procedural NpcMeshes.Dress and Overgarment, refitted to this base's body:
- "top_<Cut>_<Sleeve>": the upper garment's trunk (hem, braid band, belt) and its sleeves (Bare / Short / Long), plus what
  makes the cut read (coat lapels and the open front, the poncho, the vest's open fronts, the wrap's sash). One slot per
  cut and sleeve length a resident can draw (CUTS["top"]); the era's hem length and ease are the shape keys
  "npc_hem" and "npc_ease" (0 = the cut's shortest and closest, 1 its longest and loosest); the braid band's width is
  "npc_border" (0 = the thinnest band, 1 the widest; the robe's band is on its skirt).
- "skirt_<Cut>": the robe, dress and wrap skirts; "npc_fall" (length) and "npc_flare" are shape keys.
- "legs_Tight" / "legs_Loose": trousers at the procedural ease 1.08 (mercantile, future) and 1.3 (the rest).
- "boots_<era>": boots of the lower era's height; the future pair in the trousers' tone.
- "puff_Mercantile" (puffed shoulders), "cuff_Twilight" (wide cuffs) and
  "sleeve_Wasteland" (the one long right sleeve): small slots worn over a top, so the tops need no era copies.

Rings are measured cross-sections of the base's skin (npc_outfit._profile), so every slot fits its race and sex. A slot's
geometry is a function of its key parameters with a fixed topology: the basis is built at each parameter's low end and
each key at its high end, so a weight between interpolates linearly.

Pre: imported by npc_outfit.py on a scene race.py saved. Post: SLOTS maps slot names to (build, params); build(fig,
**values) returns npc_outfit Parts. Side effects: none (geometry only).
"""
import json
import math
import os

import numpy as np
from mathutils import Vector

import npc_outfit as O

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = json.load(open(os.path.join(HERE, "npc", "outfit_slots.json"), encoding="utf-8"))["cuts"]
TRUNK_BINS = 32
LIMB_BINS = 12
# Share of the hem band (NpcMeshes Dress `border`, lerp(0.07, 0.32, Textile01)) at its middle textile: where the robe's
# top, which has no braid of its own (its skirt carries it) and so no border key, keeps its band.
BORDER = 0.18
# Shape key of each parameter on the slots that vary it.
# Boot leather off the skin (metres).
BOOT_M = 0.007
KEYS = {"hem": "npc_hem", "ease": "npc_ease", "fall": "npc_fall", "flare": "npc_flare", "border": "npc_border"}


def _mask(fig, prefixes, side):
    """Skin weighted more than half to the bones of one side whose names start with `prefixes`."""
    key = (prefixes, side)
    cache = fig.__dict__.setdefault("_cut_masks", {})
    if key not in cache:
        cache[key] = np.array([sum(w for b, w in fw.items() if b.endswith("_" + side) and b.startswith(prefixes)) > 0.5
                               for fw in fig.w])
    return cache[key]


def _below_arms(fig):
    if not hasattr(fig, "_cut_low"):
        arms = _mask(fig, ("upperarm", "lowerarm", "hand"), "l") | _mask(fig, ("upperarm", "lowerarm", "hand"), "r")
        fig._cut_low = ~arms & ~fig.hand
    return fig._cut_low


def _basis(n):
    """The in-plane axes npc_outfit._profile uses for a plane of normal n, so rings built either way line up."""
    n = n.normalized()
    u = (Vector((0.0, -1.0, 0.0)) + n * n.y).normalized() if abs(n.y) < 0.9 else Vector((1.0, 0.0, 0.0))
    return u, n.cross(u).normalized()


def _support(fig, c, n, mask, bins, half=0.015):
    """For each ring direction in the plane (c, n), how far the skin of `mask` within `half` of the plane reaches
    along it (its support function): a convex envelope, so a ring round both legs never dips into the gap between
    them, and it is defined however sparse the skin. Directions the skin does not reach take half the median."""
    n = n.normalized()
    u, v = _basis(n)
    rel = fig.co - np.array(c)
    off = rel @ np.array(n)
    sel = mask & (np.abs(off) <= half)
    # Sparse limbs (a goblin's shin, a digitigrade calf) can leave a thin slab empty: widen it before giving up.
    for _ in range(3):
        if sel.sum() >= bins:
            break
        half *= 2.0
        sel = mask & (np.abs(off) <= half)
    if not sel.any():
        raise SystemExit("no skin near the plane at %s" % (tuple(round(x, 3) for x in c),))
    q = rel[sel] - np.outer(off[sel], np.array(n))
    a = (np.arange(bins) + 0.5) / bins * 2 * math.pi - math.pi
    dirs = np.outer(np.cos(a), np.array(u)) + np.outer(np.sin(a), np.array(v))
    radii = (q @ dirs.T).max(axis=0)
    floor = 0.5 * float(np.median(radii[radii > 0])) if (radii > 0).any() else 0.01
    return u, v, np.maximum(radii, floor)


def _flat_profile(fig, centre, z, mask, bins=TRUNK_BINS):
    c = Vector((0.0, centre.y, z))
    n = Vector((0.0, 0.0, 1.0))
    u, v, radii = _support(fig, c, n, mask, bins)
    return c, n, u, v, radii


def _torso_ring(fig, z, scale, out, bins=TRUNK_BINS):
    c, n = O._flat(fig, z)
    _, _, u, v, radii = _flat_profile(fig, c, z, fig.torso, bins)
    return O._ring(c, n, u, v, radii, scale, out)


def _halfwidth(fig, z):
    band = fig.torso & (np.abs(fig.co[:, 2] - z) < 0.015)
    return float(np.abs(fig.co[band, 0]).max())


def _on_cloth(fig, x, z, fit, out):
    """The point of the top's trunk cloth (its ring at z: the trunk's envelope x fit, off by CLEAR_M) facing front at
    x, pushed `out` further: lapels, vest fronts and the coat's open front lie on the cloth, not on the skin under it."""
    c, n = O._flat(fig, z)
    _, _, u, v, radii = _flat_profile(fig, c, z, fig.torso, 96)
    pts = O._ring(c, n, u, v, radii, fit, O.CLEAR_M)
    front = [p for p in pts if p.y < c.y]
    p = min(front, key=lambda q: abs(q.x - x))
    d = (p - c)
    d.z = 0.0
    d.normalize()
    return p + d * out, d


def _hanging(fig, centre, z, bins=TRUNK_BINS, step=0.02):
    """The legs' envelope at z as cloth hung from the hip sees it: in each direction the widest the skin reaches anywhere
    from the hip down to z. A hem or skirt key slides each ring along a straight chord between its two ends; the thighs
    taper concavely, so a ring sized to the envelope at its own height alone would cut into them part way."""
    cache = fig.__dict__.setdefault("_cut_hang", {})
    radii = None
    zz = fig.hip
    while True:
        k = round(zz, 4)
        if k not in cache:
            cache[k] = _flat_profile(fig, centre, max(zz, 0.02 * fig.h), _below_arms(fig), bins)[4]
        radii = cache[k] if radii is None else np.maximum(radii, cache[k])
        if zz <= z:
            return radii
        zz = max(z, zz - step)


def _limb_ring(fig, at, d, mask, scale, out):
    u, v, radii = _support(fig, at, d, mask, LIMB_BINS, 0.012)
    return O._ring(at, d, u, v, radii, scale, out)


def _tube_part(rings, role, a, d, near="all"):
    part = O._loft(rings, role, near=near)
    part.axis = (a, d.normalized())
    return part


# ---- tops ---------------------------------------------------------------------------------------------------------


def _trunk(fig, hem, fit, border, band_role="braid"):
    """The upper garment from collar to hem (NpcMeshes Dress rings): measured on the trunk above the hip, round both
    legs below it, widening toward the hem (hemFlare 1 + hem / 2) and never inside the legs' own envelope. The braid
    band takes `border` of the hem's drop below the hip (NpcMeshes Dress `border`)."""
    h = fig.h
    hip_c, n = O._flat(fig, fig.hip)
    _, _, u, v, hip_r = _flat_profile(fig, hip_c, fig.hip, fig.torso)
    hem_z = fig.hip - fig.hip * hem

    def low(f):
        z = fig.hip + (hem_z - fig.hip) * f
        radii = np.maximum(hip_r * fit * (1.0 + 0.5 * hem * f), _hanging(fig, hip_c, z) * 1.12)
        return O._ring(Vector((0.0, hip_c.y, z)), n, u, v, radii, 1.0, O.CLEAR_M)

    _, _, _, _, hip_env = _flat_profile(fig, hip_c, fig.hip, _below_arms(fig))
    hip_ring = O._ring(hip_c, n, u, v, np.maximum(hip_r * fit, hip_env * 1.12), 1.0, O.CLEAR_M)
    up = [hip_ring,
          _torso_ring(fig, fig.waist, fit, O.CLEAR_M),
          _torso_ring(fig, fig.chest - 0.05 * h, fit, O.CLEAR_M),
          _torso_ring(fig, fig.chest + 0.005 * h, fit * 0.97, O.CLEAR_M),
          _torso_ring(fig, fig.chest + 0.6 * (fig.neck - fig.chest), 1.0, O.CLEAR_M + 0.002)]
    mid = [low(f) for f in (1.0 - border, 0.66, 0.33)] + [hip_ring]
    band = [low(1.0), low(1.0 - 0.74 * border), low(1.0 - border)]
    centre = O._flat(fig, fig.chest)[0]
    parts = []
    for rings, role in ((band, band_role), (mid, "clothlow"), (up, "cloth")):
        part = O._loft(rings, role)
        part.centre = centre
        parts.append(part)
    belt_z = fig.hip + 0.6 * (fig.waist - fig.hip)
    parts.append(O._band(fig, belt_z, 0.012 * h, fit, "leather", out=0.002))
    return parts, band[0]


SLEEVE_RINGS = {
    # (bone segment, share along it, ease on the measured arm): shoulder (inside the trunk, so no gap shows), mid upper
    # arm, elbow, forearm, cuff (NpcMeshes: ArmR 1.5 at the shoulder, 1.25 at the elbow, 1.15 at the cuff).
    "Short": (("u", -0.08, 1.25), ("u", 0.05, 1.22), ("u", 0.3, 1.18), ("u", 0.55, 1.16), ("u", 0.75, 1.15)),
    "Long": (("u", -0.08, 1.25), ("u", 0.05, 1.22), ("u", 0.35, 1.18), ("u", 0.7, 1.16), ("u", 1.0, 1.15),
             ("l", 0.3, 1.15), ("l", 0.6, 1.17), ("l", 0.88, 1.3)),
}


def _arm(fig, side):
    a, e, w = fig.head_of["upperarm_" + side], fig.head_of["lowerarm_" + side], fig.head_of["hand_" + side]
    return a, e, w


def _sleeve(fig, side, length, role, ease=0.0, cuff=1.0):
    """One sleeve as rings round the measured arm; `ease` loosens every ring (a sleeve worn over another), `cuff`
    widens the last ring (a robe's open cuff)."""
    a, e, w = _arm(fig, side)
    mask = _mask(fig, ("upperarm", "lowerarm"), side)
    spec = SLEEVE_RINGS[length]
    rings = []
    for k, (seg, t, scale) in enumerate(spec):
        p, d = (a + (e - a) * t, e - a) if seg == "u" else (e + (w - e) * t, w - e)
        if k == len(spec) - 1:
            scale *= cuff
        rings.append(_limb_ring(fig, p, d.normalized(), mask, scale + ease, O.CLEAR_M))
    return _tube_part(rings, role, a, w - a)


def _lapels(fig, fit):
    """Coat: lapels folded back from the collar to the second button (NpcMeshes Overgarment), on the cloth's ease."""
    h, hw = fig.h, _halfwidth(fig, fig.chest)
    parts = []
    for s in (1.0, -1.0):
        neck, nn = _on_cloth(fig, s * 0.45 * fig.hr, fig.chest + 0.005 * h, fit, 0.004)
        tip, nt = _on_cloth(fig, s * 0.55 * hw, fig.chest - 0.04 * h, fit, 0.006)
        low, nl = _on_cloth(fig, s * 0.01 * h, fig.chest - 0.14 * h, fit, 0.004)
        parts.append(O._panel(neck, tip, low, (nn + nt + nl).normalized(), 0.003, "cloth2"))
    return parts


def _open_front(fig, fit, hem_ring):
    """Coat: below the belt an open coat parts, a dark wedge where the trousers show (NpcMeshes Overgarment)."""
    h = fig.h
    # Under the belt (band out CLEAR_M + 0.002 + bulge, 3 mm thick), so its tip tucks beneath it.
    top, n = _on_cloth(fig, 0.0, fig.hip + 0.45 * (fig.waist - fig.hip), fit, 0.004)
    pts = []
    for s in (-1.0, 1.0):
        near = min(hem_ring, key=lambda p: (p.x - s * 0.06 * h) ** 2 + (p.y - min(q.y for q in hem_ring)) ** 2)
        pts.append(near + Vector((0.0, -0.004, 0.0)))
    return O._panel(top, pts[0], pts[1], Vector((0.0, -1.0, 0.0)), 0.003, "cloth2dark")


def _poncho(fig, fit):
    """Mantle: a poncho sloping from the collar over the shoulders and falling straight past the hips, lowest at the
    sides (NpcMeshes Overgarment). Rides the trunk only: in the T bind pose the arms leave through it; lowered, they
    pass under its sides."""
    h = fig.h
    mask = _mask(fig, ("upperarm",), "l")
    a, e, _ = _arm(fig, "l")
    _, _, arm_r = _support(fig, a + (e - a) * 0.3, (e - a).normalized(), mask, LIMB_BINS, 0.012)
    wide = _halfwidth(fig, fig.chest) * fit + float(arm_r.mean()) * 1.9
    # As deep as the trunk is anywhere from the hip to the chest (a belly, the seat), so the garment under it and its
    # belt stay inside.
    deep = 0.0
    for z in (fig.chest, fig.waist, fig.hip):
        band = _below_arms(fig) & (np.abs(fig.co[:, 2] - z) < 0.015)
        deep = max(deep, 0.5 * float(fig.co[band, 1].max() - fig.co[band, 1].min()))
    deep *= 1.35 * fit
    hem = fig.hip - 0.08 * h

    def ring(z, sx, sy, sag, rx=None, ry=None):
        c = Vector((0.0, fig.axis_y(min(max(z, fig.hip), fig.chest)), z))
        rx, ry = (rx or wide) * sx, (ry or deep) * sy
        pts = []
        for i in range(24):
            t = (i + 0.5) / 24 * 2 * math.pi - math.pi
            x, y = math.sin(t), -math.cos(t)
            pts.append(c + Vector((x * rx, y * ry, -sag * x * x)))
        return pts

    rings = [ring(hem, 1.16, 1.05, 0.1 * h), ring(hem + (fig.chest - hem) * 0.12, 1.14, 1.05, 0.09 * h),
             ring(hem + (fig.chest - hem) * 0.2, 1.12, 1.05, 0.08 * h), ring(hem + (fig.chest - hem) * 0.7, 1.04, 1.03, 0.025 * h),
             ring(fig.chest - 0.035 * h, 1.0, 1.0, 0.0), ring(fig.chest + 0.01 * h, 0.72, 0.85, 0.0),
             ring(fig.chest + 0.55 * (fig.neck - fig.chest), 0.95, 0.9, 0.0, fig.hr, fig.hr)]
    centre = O._flat(fig, fig.chest)[0]
    parts = []
    for sel, role in (((0, 1), "cloth2shade"), ((1, 2), "accent"), ((2, 3, 4, 5, 6), "cloth2")):
        part = O._loft([rings[i] for i in sel], role, thickness=0.004, near="torso")
        part.centre = centre
        parts.append(part)
    return parts


def _vest_fronts(fig, fit):
    """Vest: the two open fronts from the chest to just under the waist (NpcMeshes Overgarment slabs)."""
    h = fig.h
    z0, z1 = fig.chest, fig.hip + 0.3 * (fig.waist - fig.hip)
    parts = []
    for s in (1.0, -1.0):
        part = O.Part("clothdark")
        rows, cols = 6, 3
        for i in range(rows):
            z = z0 + (z1 - z0) * i / (rows - 1)
            hw = _halfwidth(fig, z)
            for k in range(cols):
                x = s * hw * (0.17 + 0.5 * k / (cols - 1))
                p, _ = _on_cloth(fig, x, z, fit, 0.003)
                part.verts.append(p)
        for i in range(rows - 1):
            for k in range(cols - 1):
                q = i * cols + k
                part.faces.append((q, q + 1, q + cols + 1, q + cols))
        part.thickness = 0.004
        part.outward = Vector((0.0, -1.0, 0.0))
        parts.append(part)
    return parts


def _wrap_sash(fig, fit):
    """Wrap: the cloth over the right shoulder to the left hip, the other shoulder bare (NpcMeshes Overgarment)."""
    h = fig.h
    a = fig.head_of["upperarm_r"] + Vector((0.02 * h, 0.0, 0.03 * h))
    b = Vector((fig.hip_x, fig.axis_y(fig.hip), fig.hip + 0.04 * h))
    d = (b - a).normalized()
    t = -a.x / (b.x - a.x)
    z = a.z + (b.z - a.z) * t
    c = Vector((0.0, fig.axis_y(z), z))
    n = d.cross(Vector((0.0, 1.0, 0.0))).normalized()
    return O._hoop(fig, c, n, 0.042 * h, fit, O.CLEAR_M + 0.006 * h, "accent")


def top(cut, sleeve):
    def build(fig, hem, ease, border=BORDER):
        # A robe's top stops just past the skirt's waist and its braid moves to the skirt's hem: hung to the ankle as
        # NpcMeshes does (hem 0.9 over a skirt of fall 0.93 and wider flare) the two would cross and show through.
        parts, hem_ring = _trunk(fig, hem, ease, border, "cloth" if cut == "Robe" else "braid")
        if sleeve != "Bare":
            role = "cloth2" if cut == "Vest" else "cloth"
            cuff = 1.9 / 1.15 if cut == "Robe" and sleeve == "Long" else 1.0
            parts += [_sleeve(fig, s, sleeve, role, cuff=cuff) for s in ("l", "r")]
        if cut == "Coat":
            parts += _lapels(fig, ease) + [_open_front(fig, ease, hem_ring)]
        elif cut == "Mantle":
            parts += _poncho(fig, ease)
        elif cut == "Vest":
            parts += _vest_fronts(fig, ease)
        elif cut == "Wrap":
            parts.append(_wrap_sash(fig, ease))
        return parts
    return build


# ---- lower garments -----------------------------------------------------------------------------------------------


def skirt(cut):
    role = {"Robe": "cloth", "Wrap": "accent"}.get(cut, "cloth2")

    def build(fig, fall, flare, border=None):
        """NpcMeshes Dress skirt: from just over the hip to legLen x (1 - fall), widening by the flare (x 0.3 across,
        x 0.5 front to back at the hem). The robe's skirt carries the braid its top would (`border`)."""
        h = fig.h
        hip_c, n = O._flat(fig, fig.hip)
        _, _, u, v, env = _flat_profile(fig, hip_c, fig.hip, _below_arms(fig))
        top_z = fig.hip + 0.03 * h
        rings = [_torso_ring(fig, top_z, 1.0, O.CLEAR_M)]
        bins = TRUNK_BINS
        stations = (0.2, 0.45, 0.72, 0.93, 1.0)
        if border is not None:
            # NpcMeshes hangs the robe's band from a hem 0.9 of the leg below the hip; this skirt falls `fall` of it.
            # The ring above the band moves up with it, so a wide band never folds over it.
            start = 1.0 - border * 0.9 / fall
            stations = (0.2, 0.45, min(0.72, start - 0.06), start, 1.0)
        for f in stations:
            z = fig.hip - fig.hip * fall * f
            here = _hanging(fig, hip_c, z)
            # The flare grows as f^1.5 rather than f: the procedural skirt starts inside the top's hem (x 0.95), and a
            # linear flare would push through a dress top's hem band.
            g = f ** 1.5
            sx, sy = 1.0 + 0.3 * flare * g, (1.1 + 0.5 * flare * g) / 1.1
            c = Vector((0.0, hip_c.y, z))
            pts = []
            for i in range(bins):
                a = (i + 0.5) / bins * 2 * math.pi - math.pi
                ca, sa = math.cos(a), math.sin(a)
                r = max(env[i] * math.hypot(ca * sy, sa * sx), here[i] * 1.08) + O.CLEAR_M
                r += 0.004 * h * f * (0.5 + 0.5 * math.sin(9.0 * a))
                pts.append(c + (u * ca + v * sa) * r)
            rings.append(pts)
        parts = []
        for sel, tone in ((rings[:5], role), (rings[4:], "braid" if cut == "Robe" else role)):
            part = O._loft(sel, tone)
            part.centre = hip_c
            parts.append(part)
        return parts
    return build


LEG_STATIONS = (("t", 0.15), ("t", 0.32), ("t", 0.66), ("t", 1.0), ("c", 0.3), ("c", 0.6), ("c", 0.9))


def legs(fit):
    def build(fig):
        """NpcMeshes Dress trousers: the seat round both hips, then each leg's rings at the procedural nodes (thigh 0.32,
        knee, calf 0.3, cuff 0.9 to the ankle) at the cut's ease, the cuff 1.1 wider."""
        h = fig.h
        hip_c, n = O._flat(fig, fig.hip)
        seat = []
        # The seat hugs the pelvis (ease 1, under every top's hip ring at ease >= 1.07) and only the legs below take the
        # cut's ease, so trousers never show through the top above its hem.
        for z, ease in ((fig.hip + 0.2 * (fig.waist - fig.hip), 1.0), (fig.hip, 1.0), (fig.hip - 0.04 * h, min(fit, 1.08))):
            _, _, u, v, env = _flat_profile(fig, hip_c, z, _below_arms(fig))
            seat.append(O._ring(Vector((0.0, hip_c.y, z)), n, u, v, env, ease, O.CLEAR_M))
        part = O._loft(seat, "cloth2")
        part.centre = hip_c
        parts = [part]
        for s in ("l", "r"):
            hip, knee, ankle = fig.head_of["thigh_" + s], fig.head_of["calf_" + s], fig.head_of["foot_" + s]
            mask = _mask(fig, ("thigh", "calf"), s)
            rings = []
            for seg, t in LEG_STATIONS:
                a, b = (hip, knee) if seg == "t" else (knee, ankle)
                scale = fit * (1.1 if (seg, t) == ("c", 0.9) else 1.0)
                rings.append(_limb_ring(fig, a + (b - a) * t, (b - a).normalized(), mask, scale, O.CLEAR_M))
            parts.append(_tube_part(rings, "cloth2", hip, ankle - hip))
        return parts
    return build


def _boot(fig, side, height, role):
    """One boot as rings: the shaft round the shin from the ankle up to lerp(ankle, knee, height x 1.6), the foot round
    its own axis from behind the heel to past the toes. Rings are convex envelopes (_support), so the toes merge into
    one toe cap and a claw never shows through."""
    knee, ankle = fig.head_of["calf_" + side], fig.head_of["foot_" + side]
    toe = fig.tail_of["ball_" + side]
    up = (knee - ankle).normalized()
    top = min(1.0, height * 1.6)
    shaft_mask = _mask(fig, ("calf", "foot"), side)
    # The shaft starts a little over the ankle so its rings cut the shin, not the instep.
    shaft = [_limb_ring(fig, ankle + (knee - ankle) * (0.04 + (top - 0.04) * t), up, shaft_mask, 1.06, BOOT_M)
             for t in (0.0, 0.5, 1.0)]
    foot_mask = _mask(fig, ("foot", "ball"), side)
    d = toe - ankle
    fwd = d.normalized()
    foot = []
    for t, scale in ((-0.32, 0.75), (-0.2, 1.0), (0.05, 1.0), (0.35, 1.0), (0.65, 1.0), (0.9, 1.0), (1.02, 0.85), (1.12, 0.4)):
        foot.append(_limb_ring(fig, ankle + d * t, fwd, foot_mask, scale, BOOT_M * scale))
    return [_tube_part(shaft, role, ankle, up), _tube_part(foot, role, ankle, fwd)]


def boots(era, height):
    def build(fig):
        """NpcMeshes Dress boots: the foot and the shin up to lerp(ankle, knee, height x 1.6); the future pair in the
        trousers' tone (future clothes do not glow)."""
        role = "cloth2shade" if era == "Future" else "leather"
        parts = []
        for s in ("l", "r"):
            parts += _boot(fig, s, height, role)
        return parts
    return build


# ---- small sleeve slots -------------------------------------------------------------------------------------------


def _puff(fig):
    """Mercantile: puffed shoulders (NpcMeshes Dress shoulder ball 2.2 arm radii instead of 1.6)."""
    parts = []
    for s in ("l", "r"):
        a, e, _ = _arm(fig, s)
        _, _, r = _support(fig, a + (e - a) * 0.3, (e - a).normalized(), _mask(fig, ("upperarm",), s), LIMB_BINS, 0.012)
        rr = float(r.mean()) * 2.2 / 1.5
        parts.append(O._sphere(a + Vector((0.0, 0.0, 0.25 * rr)), (rr, rr, rr * 0.85), "cloth", 14, 8))
    return parts


def _cuffs(fig):
    """Twilight: wide cuffs on long sleeves (NpcMeshes Dress cuff 2.6 arm radii), outside the sleeve from mid forearm."""
    parts = []
    for s in ("l", "r"):
        a, e, w = _arm(fig, s)
        mask = _mask(fig, ("lowerarm",), s)
        d = (w - e).normalized()
        _, _, elbow = _support(fig, e + (w - e) * 0.05, d, mask, LIMB_BINS, 0.012)
        rings = [_limb_ring(fig, e + (w - e) * 0.5, d, mask, 1.25, O.CLEAR_M + 0.002)]
        for t, k in ((0.7, 1.6), (0.9, 2.1)):
            p = e + (w - e) * t
            u, v, _ = _support(fig, p, d, mask, LIMB_BINS, 0.012)
            rings.append(O._ring(p, d, u, v, np.full(LIMB_BINS, float(elbow.mean()) * k), 1.0, O.CLEAR_M))
        parts.append(_tube_part(rings, "cloth", e, d))
    return parts


def _right_sleeve(fig):
    """Wasteland: the right arm always in a long sleeve, whatever the left wears (NpcMeshes Dress `cover`); worn over a
    short or bare top, a little looser than its sleeve."""
    return [_sleeve(fig, "r", "Long", "cloth", ease=0.04)]


def _slots():
    slots = {}
    border = tuple(TABLE["border"])
    for cut, spec in TABLE["top"].items():
        params = {p: tuple(spec[p]) for p in ("hem", "ease")}
        # The robe's top band is plain cloth; its skirt's hem carries the braid.
        if cut != "Robe":
            params["border"] = border
        for sleeve in spec["sleeves"]:
            slots["top_%s_%s" % (cut, sleeve)] = (top(cut, sleeve), params)
    for cut, spec in TABLE["skirt"].items():
        params = {p: tuple(spec[p]) for p in ("fall", "flare")}
        if cut == "Robe":
            params["border"] = border
        slots["skirt_" + cut] = (skirt(cut), params)
    for name, fit in TABLE["legs"].items():
        slots["legs_" + name] = (legs(fit), {})
    for era, height in TABLE["boots"].items():
        slots["boots_" + era] = (boots(era, height), {})
    slots["puff_Mercantile"] = (_puff, {})
    slots["cuff_Twilight"] = (_cuffs, {})
    slots["sleeve_Wasteland"] = (_right_sleeve, {})
    return slots


SLOTS = _slots()
