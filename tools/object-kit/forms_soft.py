"""Soft family forms (軟件: 布體、收邊／繩、飾片): FishingNet, Sack, Backpack, Ball, Kite, PrayerBeads, Banner.

Slots: cloth (布體: the fabric, net, bag, ball shell or sail), hem (收邊／繩: edging, ties, straps, lines, and the pole
or frame the cloth hangs from), trim (飾片: tags, floats, tails, tassels, emblems). Soft goods are static meshes, so
sag, folds and slump are modelled with a few segments (sheet, blob), not a cloth sim. None of these groups glow
(tools, containers, toys, ritual): only Ancient rune slots use the glow material, and they still read unlit.

Frames (Z up, front -Y):
- FishingNet, Sack, Ball, Banner: origin at the floor contact (they double as scene / dungeon props).
- Backpack: origin at the top of the strap side (the haul loop). The bag hangs down -Z and back +Y: in the hand or on
  the hip (NpcMeshes.Carry) it hangs from its loop, and on a back anchor the straps face the wearer.
- Kite: origin at the grip at the foot of the spine; the sail rises +Z, the tail hangs below the hand.
- PrayerBeads: origin at the top of the loop where the hand holds it; loop, knot and pendant hang -Z.
morph() keeps each part's lowest and highest z and scales the rest about the part's own centre, so slots meet at a
part's top or bottom (neck ties, bottoms, crossbars) or share the cloth's z range and centre (ball seams).
Each form draws its F() frame values first, in a fixed order, whatever the era.
"""
import math

from mathutils import Matrix, Vector

from forms_vessel import rad_at
from kit_forms import F, J, coin, function
from kit_lib import M, _lathe_bm, _merge

SOFT = ("cloth", "hem", "trim")


def T(x, y, z):
    return Matrix.Translation((x, y, z))


def tab(pairs, v):
    """Piecewise-linear lookup in [(v, value), ...] (outlines of sails and banners)."""
    for (v0, a), (v1, b) in zip(pairs, pairs[1:]):
        if v0 <= v <= v1:
            return a + (b - a) * (v - v0) / max(v1 - v0, 1e-6)
    return pairs[-1][1] if v > pairs[-1][0] else pairs[0][1]


def sheet(p, fn, nu, nv, t=0.006, mat="cloth", **kw):
    """Cloth panel: fn(u, v) -> (x, y, z) over an nu x nv grid, thickened t along its normal and closed, so it reads
    from both sides (the game culls back faces)."""
    def build(bm):
        P = [[Vector(fn(i / nu, j / nv)) for j in range(nv + 1)] for i in range(nu + 1)]
        A, B = [], []
        for i in range(nu + 1):
            ra, rb = [], []
            for j in range(nv + 1):
                du = P[min(i + 1, nu)][j] - P[max(i - 1, 0)][j]
                dv = P[i][min(j + 1, nv)] - P[i][max(j - 1, 0)]
                n = du.cross(dv)
                n = n.normalized() if n.length > 1e-9 else Vector((0, 1, 0))
                ra.append(bm.verts.new(P[i][j] - n * t / 2))
                rb.append(bm.verts.new(P[i][j] + n * t / 2))
            A.append(ra)
            B.append(rb)
        quads = []
        for i in range(nu):
            for j in range(nv):
                quads.append((A[i][j], A[i + 1][j], A[i + 1][j + 1], A[i][j + 1]))
                quads.append((B[i][j + 1], B[i + 1][j + 1], B[i + 1][j], B[i][j]))
        for i in range(nu):
            for j in (0, nv):
                quads.append((A[i][j], B[i][j], B[i + 1][j], A[i + 1][j]))
        for j in range(nv):
            for i in (0, nu):
                quads.append((A[i][j], A[i][j + 1], B[i][j + 1], B[i][j]))
        for q in quads:
            try:
                bm.faces.new(q)
            except ValueError:
                pass
    kw.setdefault("bevel", 0)
    return p._add(build, mat, **kw)


def blob(p, profile, warp=None, m=None, mat="cloth", segs=10, **kw):
    """Lathe whose vertices pass through warp(Vector) -> Vector (folds, slump, lumps) before placement by m."""
    def build(bm):
        src = _lathe_bm(profile, segs)
        if warp:
            for v in src.verts:
                v.co = Vector(warp(v.co.copy()))
        _merge(bm, src, m or Matrix())
    kw.setdefault("bevel", 0)
    return p._add(build, mat, **kw)


def drape(H, n=5, amp=0.08, ph=0.0, lean=0.0, lump=0.0, spread=0.08, sq=(1.0, 1.0)):
    """Slump warp for a bag standing on z = 0: n vertical folds, a lean that grows with height, a spread foot."""
    def w(c):
        t = max(0.0, min(1.0, c.z / H))
        a = math.atan2(c.y, c.x)
        k = (1 + amp * math.sin(n * a + ph) * math.sin(math.pi * min(1.0, t * 1.3))
             + lump * math.sin(2 * a + ph * 1.7) * math.sin(math.pi * t) + spread * (1 - t) ** 3)
        return Vector((c.x * k * sq[0] + lean * H * t * t, c.y * k * sq[1], c.z))
    return w


def surf(prof, warp, a, z, lift=1.0):
    """Point on a warped lathe surface at angle a and height z (for parts that must lie on a bag)."""
    r = rad_at(prof, z) * lift
    return warp(Vector((math.cos(a) * r, math.sin(a) * r, z)))


def patch(p, prof, warp, a, da, z0, z1, mat, lift=1.02, m=None, t=0.004):
    """Panel lying on a warped lathe surface (labels, patches, quilting)."""
    mm = m or Matrix()
    sheet(p, lambda u, v: mm @ surf(prof, warp, a + (u - 0.5) * da, z0 + (z1 - z0) * v, lift), 2, 2, t, mat)


def belt(p, prof, warp, z0, z1, mat, lift=1.02, m=None, segs=10):
    """Closed band hugging a warped lathe surface between z0 and z1 (straps, stripes, seams)."""
    r0, r1 = rad_at(prof, z0), rad_at(prof, z1)
    ring = [(r0 * 0.96, z0), (r0 * lift, z0), (r1 * lift, z1), (r1 * 0.96, z1), (r0 * 0.96, z0)]
    blob(p, ring, warp, m, mat=mat, segs=segs)


def strap(p, pts, w, mat="leather", t=0.006):
    """Flat strap of width w (across X) through pts."""
    n = len(pts) - 1

    def fn(u, v):
        s = v * n
        i = min(int(s), n - 1)
        c = Vector(pts[i]).lerp(Vector(pts[i + 1]), s - i)
        return (c.x + (u - 0.5) * w, c.y, c.z)
    sheet(p, fn, 1, n, t, mat)


def loop(pts):
    return list(pts) + [pts[0]]


# ---------------------------------------------------------------- FishingNet (heaped on the floor, origin at z = 0)
def dome_prof(R, H):
    return [(0, 0)] + [(R * math.sin(math.radians(d)), H * math.cos(math.radians(d))) for d in (90, 64, 38, 16)] + [(0, H)]


def heap(H, n, amp, ph, zamp=0.12):
    """Lumpy net heap: radial bulges and a wavy crown; the floor ring stays flat."""
    def w(c):
        a = math.atan2(c.y, c.x)
        t = max(0.0, min(1.0, c.z / H))
        k = 1 + amp * math.sin(n * a + ph)
        return Vector((c.x * k, c.y * k, c.z * (1 + zamp * math.sin((n - 1) * a + ph * 1.3) * t)))
    return w


def net_over(p, R, H, warp, mat, n=6, lats=(0.55,), r=0.0035, ph=0.0):
    """Mesh cords lying on a heap: meridians from the crown to the floor plus latitude rings."""
    def at(a, s):
        th = s * math.pi / 2
        return tuple(warp(Vector((math.cos(a) * R * math.sin(th) * 1.03, math.sin(a) * R * math.sin(th) * 1.03,
                                  H * math.cos(th) * 1.03 + 0.002))))
    for i in range(n):
        a = ph + i * math.tau / n
        p.tube([at(a, s) for s in (0.12, 0.45, 0.75, 1.0)], r, mat=mat, segs=3)
    for s in lats:
        p.tube([at(ph + k * math.tau / 8, s) for k in range(9)], r, mat=mat, segs=3)


def rim_pts(R, n, z, ph=0.0, wob=0.0, rng=None):
    out = []
    for k in range(n):
        a = ph + k * math.tau / n
        rr = R * (1 + (rng.uniform(-wob, wob) if rng else 0))
        out.append((math.cos(a) * rr, math.sin(a) * rr, z))
    return out


@function("FishingNet", "Soft", SOFT, "carried")
def fishing_net(p, slot):
    e = p.era
    R = F(p, {"Mercantile": 0.2, "Industrial": 0.22, "Steampunk": 0.11, "Future": 0.2, "Ancient": 0.23}.get(e, 0.25), 0.1)
    H = F(p, {"Mercantile": 0.26, "Industrial": 0.13, "Steampunk": 0.2, "Future": 0.16}.get(e, 0.13), 0.1)
    W = F(p, 0.34, 0.1)
    ph = p.frame.uniform(0, math.tau)
    if e == "Primal":  # rattan scoop net laid down: vine hoop, bag of net heaped inside, sinker stones
        Rb = R * 0.88
        wp = heap(H, 3, 0.1, ph)
        if slot == "cloth":
            blob(p, dome_prof(Rb, H), wp, mat="rope", segs=8)
            net_over(p, Rb, H, wp, "bark", n=p.rng.choice((5, 6)), ph=ph)
        elif slot == "hem":
            p.tube(loop(rim_pts(R, 10, 0.016, ph, 0.04, p.rng)), J(p, 0.013, 0.2), mat="bark", segs=5)
            a = ph + math.pi
            x0, y0 = math.cos(a) * R, math.sin(a) * R
            p.tube([(x0, y0, 0.016), (x0 * 1.5, y0 * 1.5 + J(p, 0.03, 0.8), 0.02), (x0 * J(p, 2.0, 0.1), y0 * 2.0, 0.018)],
                   0.014, mat="wood", segs=5)
        else:
            for k in range(p.rng.randint(3, 5)):
                a = ph + 0.5 + k * math.tau / 5
                p.ball(J(p, 0.022, 0.25), M(loc=(math.cos(a) * R * 0.96, math.sin(a) * R * 0.96, 0.016), scale=(1.2, 1, 0.7)),
                       mat="stone_dark", segs=(5, 3))
    elif e == "Agrarian":  # hemp net in a lumpy heap: coiled headrope on the crown, wooden floats round the foot
        wp = heap(H, 5, 0.13, ph)
        if slot == "cloth":
            blob(p, dome_prof(R, H), wp, mat="rope", segs=10)
            net_over(p, R, H, wp, "bark", n=p.rng.choice((6, 7)), lats=(J(p, 0.55, 0.1),), ph=ph)
        elif slot == "hem":
            top = wp(Vector((0, 0, H))).z
            for i in range(2):
                p.ring(J(p, 0.05, 0.15) - i * 0.01, 0.007, T(0, 0, top + 0.006 + i * 0.012), mat="rope", segs=6, square=False)
            p.tube([(0.05, 0, top + 0.01), (R * 0.6, -0.04, H * 0.7), (R * 1.05, -0.06, 0.01), (R * J(p, 1.4, 0.1), -0.02, 0.008)],
                   0.007, mat="rope", segs=4)
        else:
            n = p.rng.randint(4, 6)
            for k in range(n):
                a = ph + k * math.tau / n
                p.cyl(0.018, 0.018, J(p, 0.06, 0.2), M(loc=(math.cos(a) * R * 1.02, math.sin(a) * R * 1.02, 0.018),
                                                       rot=(90, 0, math.degrees(a))) @ T(0, 0, -0.03), mat="wood", segs=6)
    elif e == "Mercantile":  # cast net piled as a pleated cone: lead line and weights at the skirt, swivel and hand line
        prof = [(0, 0), (R, 0), (R * 0.92, H * 0.15), (R * 0.55, H * 0.5), (R * 0.22, H * 0.85), (0.02, H), (0, H)]
        wp = heap(H, 9, 0.14, ph, 0.0)
        if slot == "cloth":
            blob(p, prof, wp, mat="rope", segs=12)
            for i in range(6):
                a = ph + i * math.tau / 6
                p.tube([tuple(surf(prof, wp, a, z, 1.04)) for z in (H * 0.9, H * 0.5, H * 0.15, 0.004)], 0.003, mat="wood_dark", segs=3)
        elif slot == "hem":
            p.tube(loop(rim_pts(R * 1.01, 12, 0.008, ph)), 0.006, mat="iron", segs=4)
            for k in range(p.rng.choice((8, 10))):
                a = ph + k * math.tau / 12
                p.ball(J(p, 0.012, 0.2), T(math.cos(a) * R * 1.03, math.sin(a) * R * 1.03, 0.01), mat="iron", segs=(4, 2))
        else:
            p.ring(0.014, 0.004, M(loc=(0, 0, H + 0.015), rot=(90, 0, 0)), mat="brass", segs=6, square=False)
            p.ring(J(p, 0.07, 0.1), 0.006, T(R * 1.35, -R * 0.4, 0.006), mat="rope", segs=8, square=False)
            p.tube([(0, 0, H + 0.03), (R * 0.4, -R * 0.2, H * 0.6), (R * 1.0, -R * 0.4, 0.02), (R * 1.28, -R * 0.4, 0.008)], 0.004,
                   mat="rope", segs=3)
    elif e == "Industrial":  # folded nylon gill net: layered stack, a fold spilling over the front, float line
        D = R * 1.2
        if slot == "cloth":
            n = 3
            for i in range(n):
                p.box((2 * R * J(p, 1.0, 0.05), D, H / n), M(loc=(p.rng.uniform(-0.015, 0.015), 0, H / n * (i + 0.5)),
                                                           rot=(0, 0, p.rng.uniform(-3, 3))), mat="cloth", bevel=0.4)

            def flap(u, v):
                return ((u - 0.5) * 2 * R * 0.9, -D / 2 - 0.004 - 0.05 * math.sin(math.pi * v * 0.9) - v * 0.04,
                        H * (1 - v) + 0.003 + 0.008 * math.sin(u * math.pi * 5 + ph))
            sheet(p, flap, 5, 3, 0.006, "cloth")
            for z in (H * 0.33, H * 0.66):
                p.tube([(-R * 1.01, -D / 2 - 0.002, z), (R * 1.01, -D / 2 - 0.002, z)], 0.003, mat="paint", segs=3)
        elif slot == "hem":
            p.tube([(-R, D * 0.3, H + 0.006), (-R * 0.3, D * 0.25, H + 0.008), (R * 0.4, D * 0.32, H + 0.006), (R, D * 0.28, H + 0.006)],
                   0.006, mat="rope", segs=4)
            p.tube([(-R * 0.9, -D / 2 - 0.1, 0.008), (0, -D / 2 - J(p, 0.11, 0.15), 0.008), (R * 0.9, -D / 2 - 0.1, 0.008)],
                   0.008, mat="iron", segs=4)
        else:
            n = p.rng.randint(3, 4)
            for k in range(n):
                x = (k + 0.5) / n * 2 * R - R
                p.ball(J(p, 0.03, 0.15), M(loc=(x, D * 0.28, H + 0.025), scale=(1.5, 0.8, 0.8)), mat="accent", segs=(6, 4))
    elif e == "Steampunk":  # mechanical net reel: net wound on a brass drum, tail spilling to the floor, crank and gear
        Rr = R
        if slot == "cloth":
            p.cyl(Rr * 0.9, Rr * 0.9, W * 0.84, M(loc=(-W * 0.42, 0, H), rot=(0, 90, 0)), mat="rope", segs=10)

            def tail(u, v):
                return ((u - 0.5) * W * 0.7, -Rr * 0.85 - 0.12 * v * v - 0.01 * math.sin(u * 9 + ph), max(0.004, H * (1 - v * 1.15)))
            sheet(p, tail, 4, 3, 0.006, "rope")
            for x in (-W * 0.2, W * J(p, 0.15, 0.4)):
                p.ring(Rr * 0.91, 0.004, M(loc=(x, 0, H), rot=(0, 90, 0)), mat="wood_dark", segs=10, square=False)
        elif slot == "hem":
            for s in (-1, 1):
                p.plate([(-Rr * 1.1, 0), (-0.02, H + Rr * 0.4), (0.02, H + Rr * 0.4), (Rr * 1.1, 0)], 0.012,
                        M(loc=(s * W / 2, 0, 0), rot=(0, 0, 90)), mat="brass", bevel=0)
            p.cyl(0.012, 0.012, W * 1.12, M(loc=(-W * 0.56, 0, H), rot=(0, 90, 0)), mat="iron", segs=6)
            for y in (-Rr, Rr):
                p.box((W * 1.05, 0.03, 0.02), T(0, y * J(p, 1.0, 0.05), 0.01), mat="wood_dark", bevel=0)
        else:
            x = W / 2 + 0.02
            p.cyl(J(p, 0.06, 0.15), 0.06, 0.012, M(loc=(x, 0, H), rot=(0, 90, 0)), mat="copper", segs=10)
            p.tube([(x + 0.012, 0, H), (x + 0.02, 0, H + 0.09), (x + 0.05, 0, H + 0.09)], 0.007, mat="brass", segs=4)
            if coin(p):
                p.cyl(0.025, 0.025, 0.01, M(loc=(x, 0.06, H - 0.07), rot=(0, 90, 0)), mat="brass", segs=8)
    elif e == "Future":  # force-field net caster: emitter puck, four splayed prongs, a lattice of field strands
        n = 4
        tips = [(math.cos(ph + k * math.tau / n) * R, math.sin(ph + k * math.tau / n) * R, H) for k in range(n)]
        if slot == "cloth":
            p.tube(loop(tips), 0.004, mat="glass", segs=3)
            for k in range(n):
                a, b = tips[k], tips[(k + 1) % n]
                mid = ((a[0] + b[0]) * 0.35, (a[1] + b[1]) * 0.35, H * 0.55)
                p.tube([a, mid, (0, 0, 0.05)], 0.003, mat="glass", segs=3)
                p.tube([a, ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5, H * J(p, 0.75, 0.1)), b], 0.003, mat="glass", segs=3)
        elif slot == "hem":
            for k in range(n):
                tx, ty, tz = tips[k]
                p.tube([(tx * 0.2, ty * 0.2, 0.03), (tx * 0.55, ty * 0.55, H * J(p, 0.45, 0.15)), (tx, ty, tz)], 0.008,
                       mat="shell_dark", segs=4)
                p.ball(0.012, T(tx, ty, tz), mat="shell_dark", segs=(5, 3))
        else:
            p.lathe([(0, 0), (R * 0.32, 0), (R * 0.36, 0.015), (R * J(p, 0.3, 0.1), 0.04), (R * 0.12, 0.05), (0, 0.052)],
                    mat="body", segs=10)
            p.ring(R * 0.34, 0.004, T(0, 0, 0.02), mat="shell_dark", segs=10)
    elif e == "Wasteland":  # scavenged heap: rope and wire mesh, tarp scrap, bottle floats and a tyre-chunk weight
        wp = heap(H, 4, 0.15, ph)
        if slot == "cloth":
            blob(p, dome_prof(R, H), wp, mat="rope", segs=9)
            net_over(p, R, H, wp, "iron", n=p.rng.choice((5, 6)), lats=(0.5,), ph=ph)
            top = wp(Vector((0, 0, H))).z
            p.box((R * J(p, 0.7, 0.2), R * 0.5, 0.008), M(loc=(R * 0.1, 0, top - 0.01), rot=(p.rng.uniform(-8, 8), 6, 20)),
                  mat="paint", bevel=0)
        elif slot == "hem":
            p.tube(loop(rim_pts(R * 1.02, 9, 0.01, ph, 0.05, p.rng)), 0.007, mat="iron", segs=4)
            a = ph + 1.0
            p.tube([(math.cos(a) * R, math.sin(a) * R, 0.01), (math.cos(a) * R * 1.3, math.sin(a) * R * 1.3, 0.03),
                    (math.cos(a + 0.2) * R * J(p, 1.5, 0.1), math.sin(a + 0.2) * R * 1.5, 0.008)], 0.004, mat="iron", segs=3)
        else:
            for k in range(p.rng.randint(2, 3)):
                a = ph + 2.2 + k * 1.3
                c = (math.cos(a) * R * 1.05, math.sin(a) * R * 1.05, 0.028)
                p.cyl(0.028, 0.028, J(p, 0.1, 0.15), M(loc=c, rot=(90, 0, math.degrees(a) + 90)) @ T(0, 0, -0.05), mat="paint", segs=6)
            p.ring(0.05, 0.022, M(loc=(math.cos(ph - 1) * R * 1.15, math.sin(ph - 1) * R * 1.15, 0.022), scale=(1, 0.5, 1)),
                   mat="rubber", segs=8)
    else:  # Ancient: stone-fibre net heaped in a ring-stone, rune-cut weight stones
        Rb = R * 0.86
        wp = heap(H, 6, 0.08, ph)
        if slot == "cloth":
            blob(p, dome_prof(Rb, H), wp, mat="stone_dark", segs=8)
            net_over(p, Rb, H, wp, "stone", n=6, lats=(J(p, 0.5, 0.2),), r=0.005, ph=ph)
        elif slot == "hem":
            p.ring(R, J(p, 0.03, 0.15), T(0, 0, 0.03), mat="stone", segs=10)
        else:
            for k in range(p.rng.choice((2, 3))):
                a = ph + 0.6 + k * math.tau / 3
                c = T(math.cos(a) * R * 1.2, math.sin(a) * R * 1.2, 0.025) @ M(rot=(0, 0, math.degrees(a)))
                p.box((0.06, 0.04, 0.05), c, mat="stone", bevel=0.2, bevel_seg=1)
                p.box((0.004, 0.026, 0.03), c @ T(0.031, 0, 0), mat="glow", bevel=0)


# ---------------------------------------------------------------- Sack (stands slumped on the floor, origin at z = 0)
def sack_prof(R, H, top):
    """Bag profile bottom to top: 'tuft' = tied neck with a gathered crown, 'roll' = folded flat top, 'dome' = round top."""
    if top == "tuft":
        return [(0, 0), (R * 0.85, 0), (R * 1.02, H * 0.08), (R * 1.06, H * 0.3), (R * 0.95, H * 0.55), (R * 0.6, H * 0.7),
                (R * 0.26, H * 0.8), (R * 0.3, H * 0.84), (R * 0.42, H * 0.92), (R * 0.22, H), (0, H * 0.97)]
    if top == "roll":
        return [(0, 0), (R * 0.88, 0), (R, H * 0.06), (R * 1.03, H * 0.45), (R * 0.97, H * 0.8), (R * 0.85, H * 0.9),
                (R * 0.9, H * 0.95), (R * 0.6, H), (0, H * 0.99)]
    return [(0, 0), (R * 0.9, 0), (R, H * 0.12), (R * 1.02, H * 0.5), (R * 0.95, H * 0.82), (R * 0.68, H * 0.96), (0, H)]


@function("Sack", "Soft", SOFT, "carried")
def sack(p, slot):
    e = p.era
    H = F(p, {"Primal": 0.42, "Mercantile": 0.5, "Industrial": 0.58, "Steampunk": 0.48, "Future": 0.34, "Ancient": 0.48}.get(e, 0.56), 0.08)
    R = F(p, {"Primal": 0.17, "Industrial": 0.17, "Steampunk": 0.17, "Future": 0.25}.get(e, 0.2), 0.08)
    lean = F(p, 0.07, 0.5) * (1 if p.frame.random() < 0.5 else -1)
    ph = p.frame.uniform(0, math.tau)
    zn = H * 0.8
    neck = (lean * H * 0.64, 0, zn)  # tie centre: drape shifts x by lean * H * t^2
    if e == "Primal":  # hide bag: lumpy, thong-tied neck, bone toggle
        prof = sack_prof(R, H, "tuft")
        wp = drape(H, 3, 0.06, ph, lean, lump=0.08)
        if slot == "cloth":
            blob(p, prof, wp, mat="hide", segs=9)
            if coin(p):
                patch(p, prof, wp, ph, 0.7, H * 0.15, H * 0.35, "leather")
        elif slot == "hem":
            p.ring(R * 0.3, 0.008, T(*neck), mat="leather", segs=8, square=False)
            for s in (-1, 1):
                p.tube([(neck[0] + s * 0.01, -R * 0.3, zn), (neck[0] + s * J(p, 0.04, 0.3), -R * 0.42, zn - J(p, 0.1, 0.2))], 0.004,
                       mat="leather", segs=3)
        else:
            p.cyl(0.008, 0.008, J(p, 0.06, 0.2), M(loc=(neck[0] - 0.03, -R * 0.34, zn), rot=(0, 90, 0)), mat="bone", segs=5)
            if coin(p):
                p.cyl(0.012, 0.0, J(p, 0.12, 0.2), M(loc=(neck[0] + 0.02, R * 0.25, zn + 0.01), rot=(-30, 20, 0)), mat="feather", segs=5)
    elif e == "Agrarian":  # burlap sack: folded slump, rope tie with a bow, ears of grain at the mouth
        prof = sack_prof(R, H, "tuft")
        wp = drape(H, 6, 0.07, ph, lean)
        if slot == "cloth":
            blob(p, prof, wp, mat="rope", segs=10)
            belt(p, prof, wp, H * 0.07, H * 0.1, "bark", lift=1.015, segs=10)
        elif slot == "hem":
            p.ring(R * 0.31, 0.008, T(*neck), mat="rope", segs=8, square=False)
            for s in (-1, 1):
                p.ring(J(p, 0.025, 0.2), 0.005, M(loc=(neck[0] + s * 0.03, -R * 0.34, zn), rot=(90, 0, s * 25)), mat="rope", segs=6,
                       square=False)
        else:
            top = (lean * H, 0, H * 0.97)
            for k in range(p.rng.randint(3, 5)):
                a = ph + k * 1.7
                tip = (top[0] + math.cos(a) * 0.06, math.sin(a) * 0.06, H + J(p, 0.12, 0.25))
                p.tube([top, tip], 0.0025, mat="hide", segs=3)
                p.ball(0.008, M(loc=tip, scale=(1, 1, 2.2)), mat="hide", segs=(4, 3))
    elif e == "Mercantile":  # printed cloth bag: trader's label on the belly, drawstring, paper tag
        prof = sack_prof(R, H, "tuft")
        wp = drape(H, 5, 0.05, ph, lean)
        if slot == "cloth":
            blob(p, prof, wp, mat="cloth", segs=12)
            patch(p, prof, wp, -math.pi / 2, J(p, 1.1, 0.15), H * 0.2, H * 0.48, "bone", lift=1.025)
            patch(p, prof, wp, -math.pi / 2, 0.5, H * 0.3, H * 0.38, "paint", lift=1.04)
        elif slot == "hem":
            p.ring(R * 0.29, 0.005, T(*neck), mat="rope", segs=8, square=False)
            p.tube([(neck[0], -R * 0.29, zn), (neck[0] + 0.02, -R * 0.4, zn - 0.08), (neck[0] + J(p, 0.04, 0.3), -R * 0.38, zn - 0.14)],
                   0.003, mat="rope", segs=3)
        else:
            p.ball(0.012, T(neck[0] + 0.04, -R * 0.39, zn - J(p, 0.14, 0.1)), mat="wood_dark", segs=(5, 3))
            if coin(p, 0.7):
                p.plate([(-0.025, 0), (-0.025, -0.05), (0.025, -0.05), (0.025, 0), (0, 0.012)], 0.002,
                        M(loc=(neck[0] - 0.05, -R * 0.33, zn - 0.02), rot=(0, J(p, 12, 0.5), -20)), mat="bone", bevel=0)
    elif e == "Industrial":  # canvas sack: rolled top with grommets and cord, stencilled stripes, snap hook
        prof = sack_prof(R, H, "roll")
        wp = drape(H, 5, 0.04, ph, lean * 0.6)
        if slot == "cloth":
            blob(p, prof, wp, mat="cloth", segs=10)
            for z in (H * 0.35, H * J(p, 0.5, 0.06)):
                belt(p, prof, wp, z, z + H * 0.05, "paint", segs=10)
        elif slot == "hem":
            zg = H * 0.93
            c = Vector((lean * 0.6 * H * 0.93 ** 2, 0, zg))
            p.ring(R * 0.88, 0.007, T(c.x, 0, zg), mat="steel", segs=10)
            for k in range(p.rng.choice((5, 6))):
                a = k * math.tau / 6
                p.box((0.016, 0.016, 0.01), M(loc=(c.x + math.cos(a) * R * 0.88, math.sin(a) * R * 0.88, zg + 0.008), rot=(0, 0, math.degrees(a))),
                      mat="steel", bevel=0)
        else:
            x = lean * 0.6 * H
            p.ring(J(p, 0.022, 0.15), 0.004, M(loc=(x, 0, H + 0.022), rot=(90, 0, 0)), mat="steel", segs=8)
            p.box((0.012, 0.006, 0.03), T(x, 0, H + 0.05), mat="steel", bevel=0)
    elif e == "Steampunk":  # belted leather duffel standing on end: two straps with brass buckles, collar clasp
        prof = sack_prof(R, H, "dome")
        wp = drape(H, 4, 0.03, ph, lean * 0.5, spread=0.04)
        if slot == "cloth":
            blob(p, prof, wp, mat="cloth", segs=10)
            for z in (H * 0.25, H * J(p, 0.6, 0.06)):
                belt(p, prof, wp, z, z + 0.035, "leather", segs=10)
                b = surf(prof, wp, -math.pi / 2, z + 0.017, 1.06)
                p.box((0.04, 0.008, 0.045), T(b.x, b.y, b.z), mat="brass", bevel=0)
        elif slot == "hem":
            c = (lean * 0.5 * H, 0, H)
            p.ring(R * J(p, 0.35, 0.12), 0.012, T(c[0], 0, H * 0.985), mat="brass", segs=10)
            p.tube([(c[0] - R * 0.3, 0, H * 0.99), (c[0], 0, H + J(p, 0.09, 0.2)), (c[0] + R * 0.3, 0, H * 0.99)], 0.01, mat="leather", segs=4)
        else:
            c = lean * 0.5 * H
            p.tube([(c + R * 0.2, 0, H + 0.03), (c + R * 0.22, -0.004, H - 0.02)], 0.002, mat="brass", segs=3)
            p.plate([(-0.022, 0), (-0.022, -0.03), (0.022, -0.03), (0.022, 0)], 0.003,
                    M(loc=(c + R * 0.22, -0.006, H - 0.02), rot=(-12, 0, J(p, 15, 0.6))), mat="brass", bevel=0)
            p.ball(0.006, T(c - 0.03, 0.02, H + 0.004), mat="copper", segs=(4, 3))
    elif e == "Future":  # vacuum storage bag: flattened quilted pillow, top carry loop, valve
        prof = sack_prof(R, H, "dome")
        wp = drape(H, 4, 0.02, math.pi / 4, lean * 0.3, spread=0.04, sq=(1.25, 0.7))
        m = M(rot=(0, 0, 22.5))
        if slot == "cloth":
            blob(p, prof, wp, m, mat="shell", segs=8)
            for z in (H * 0.33, H * J(p, 0.62, 0.08)):
                belt(p, prof, wp, z, z + 0.012, "shell_dark", lift=1.012, m=m, segs=8)
        elif slot == "hem":
            x = lean * 0.3 * H
            p.tube([(x - R * 0.45, 0, H * 0.98), (x - R * 0.3, 0, H + J(p, 0.07, 0.2)), (x + R * 0.3, 0, H + 0.07), (x + R * 0.45, 0, H * 0.98)],
                   0.009, mat="shell_dark", segs=4)
        else:
            x = lean * 0.3 * H
            p.cyl(0.03, 0.026, 0.012, T(x + R * 0.1, -R * 0.12, H * 0.985), mat="shell_dark", segs=10)
            p.cyl(0.014, 0.014, J(p, 0.014, 0.3), T(x + R * 0.1, -R * 0.12, H * 0.985 + 0.012), mat="rubber", segs=8)
    elif e == "Wasteland":  # patched feed sack: tarp patches, wire-twisted neck, bottle-cap charm
        prof = sack_prof(R, H, "tuft")
        wp = drape(H, 5, 0.08, ph, lean, lump=0.05)
        if slot == "cloth":
            blob(p, prof, wp, mat="cloth", segs=10)
            for k in range(p.rng.randint(2, 3)):
                patch(p, prof, wp, ph + k * 2.1, J(p, 0.7, 0.3), H * (0.12 + 0.18 * k), H * (0.3 + 0.16 * k),
                      ("paint", "rust", "leather")[k], lift=1.03)
        elif slot == "hem":
            for i in range(2):
                p.ring(R * 0.3, 0.003, M(loc=(neck[0], 0, zn + (i - 0.5) * 0.015), rot=(p.rng.uniform(-10, 10), 0, 0)), mat="iron", segs=8)
            p.tube([(neck[0] + R * 0.3, 0, zn), (neck[0] + R * 0.45, -0.01, zn + 0.02), (neck[0] + R * J(p, 0.5, 0.2), 0.01, zn + 0.05)],
                   0.003, mat="iron", segs=3)
        else:
            p.tube([(neck[0], -R * 0.3, zn), (neck[0] + 0.01, -R * 0.35, zn - 0.06)], 0.002, mat="iron", segs=3)
            p.cyl(J(p, 0.016, 0.2), 0.016, 0.006, M(loc=(neck[0] + 0.01, -R * 0.36, zn - 0.07), rot=(90, 0, 0)), mat="steel", segs=8)
    else:  # Ancient: sack carved whole from stone, gold neck band set with rune slots, hanging seal
        prof = sack_prof(R, H, "tuft")
        wp = drape(H, 6, 0.09, ph, lean * 0.5, spread=0.05)
        neck = (lean * 0.5 * H * 0.64, 0, zn)
        if slot == "cloth":
            blob(p, prof, wp, mat="stone", segs=12)
        elif slot == "hem":
            p.ring(R * 0.31, J(p, 0.018, 0.2), T(*neck), mat="gold", segs=8)
            for k in range(3):
                a = k * math.tau / 3 - math.pi / 2
                p.box((0.02, 0.004, 0.012), M(loc=(neck[0] + math.cos(a) * R * 0.37, math.sin(a) * R * 0.37, zn), rot=(0, 0, math.degrees(a) + 90)),
                      mat="glow", bevel=0)
        else:
            c = (neck[0], -R * 0.42, zn - J(p, 0.07, 0.2))
            p.tube([(neck[0], -R * 0.33, zn), c], 0.003, mat="gold", segs=3)
            p.cyl(0.03, 0.03, 0.012, M(loc=c, rot=(90, 0, 0)) @ T(0, -0.03, 0), mat="stone_dark", segs=8)
            p.box((0.014, 0.004, 0.02), T(c[0], c[1] - 0.007, c[2] - 0.03), mat="glow", bevel=0)


# ---------------------------------------------------------------- Backpack (origin at the haul loop on the strap side)
def pack_body(W, D, H, bulge=0.06, top=0.55):
    """Soft rounded pack: lathe profile (radius 1 across) and the warp squashing it to W x D; draw with m = T(0, yc, -H)."""
    prof = [(0, 0), (0.82, 0), (1.0, H * 0.1), (1.0 + bulge, H * 0.5), (0.97, H * 0.86), (top, H), (0, H * 1.02)]

    def w(c):
        return Vector((c.x * W / 2, c.y * D / 2, c.z))
    return prof, w


def shoulder_straps(p, W, D, H, mat, w=0.05, t=0.007, out=0.05):
    for s in (-1, 1):
        x = s * W * 0.28
        strap(p, [(x, 0.012, -0.03), (x * 1.08, -out * 0.7, -H * 0.2), (x * 1.15, -out, -H * 0.5), (x * 1.2, -out * 0.5, -H * 0.8),
                  (x * 1.25, 0.012, -H * 0.88)], w, mat, t)


@function("Backpack", "Soft", SOFT, "carried")
def backpack(p, slot):
    e = p.era
    H = F(p, {"Primal": 0.62, "Agrarian": 0.55, "Industrial": 0.56, "Future": 0.46}.get(e, 0.48), 0.08)
    W = F(p, {"Agrarian": 0.36, "Future": 0.3}.get(e, 0.34), 0.08)
    D = F(p, {"Primal": 0.18, "Agrarian": 0.28, "Future": 0.16}.get(e, 0.2), 0.08)
    ph = p.frame.uniform(0, math.tau)
    yc = D / 2 + 0.015
    m = T(0, yc, -H)
    if e == "Primal":  # pack frame: two poles and crossbars, a hide-wrapped bundle lashed on, a gourd hanging
        if slot == "cloth":
            rr = D * 0.5
            L = W * 1.05
            blob(p, [(0, 0), (rr * 0.7, 0.01), (rr, L * 0.2), (rr * 1.05, L * 0.5), (rr, L * 0.8), (rr * 0.7, L - 0.01), (0, L)],
                 heap(L, 3, 0.08, ph, 0.0), M(loc=(-L / 2, rr + 0.03, -H * 0.42), rot=(0, 90, 0)), mat="hide", segs=8)
            if coin(p):
                p.cyl(rr * 0.6, rr * 0.6, W * 0.8, M(loc=(-W * 0.4, rr * 0.7 + 0.03, -H * 0.42 + rr * 1.4), rot=(0, 90, 0)), mat="rope", segs=7)
        elif slot == "hem":
            for s in (-1, 1):
                p.tube([(s * W * 0.42, 0.03, 0.06), (s * W * J(p, 0.4, 0.05), 0.03, -H * 0.5), (s * W * 0.34, 0.03, -H * 1.02)],
                       0.014, mat="wood", segs=5)
            for z in (-0.02, -H * 0.62, -H * 0.95):
                p.tube([(-W * 0.44, 0.03, z), (W * 0.44, 0.03, z + p.rng.uniform(-0.02, 0.02))], 0.01, mat="wood", segs=4)
            for s in (-1, 1):
                p.tube([(s * W * 0.25, 0.02, -0.03), (s * W * 0.3, -0.06, -H * 0.4), (s * W * 0.33, 0.02, -H * 0.85)], 0.006,
                       mat="hide", segs=4)
        else:
            c = (W * 0.42, 0.07, -H * 1.0)
            p.lathe([(0, 0), (0.035, 0.01), (0.045, 0.05), (0.025, 0.08), (0.03, J(p, 0.11, 0.12)), (0.012, 0.13), (0, 0.14)],
                    M(loc=c, rot=(0, 0, 0)) @ T(0, 0, -0.08), mat="bark", segs=7)
    elif e == "Agrarian":  # bamboo back basket: tapered, wider at the mouth, rope straps, firewood poking out
        r = W / 2
        outer = [(r * 0.62, 0), (r * 0.72, H * 0.3), (r * 0.88, H * 0.7), (r, H)]
        sc = M(loc=(0, yc + 0.02, -H), scale=(1, D / W, 1))
        if slot == "cloth":
            from forms_vessel import shell
            shell(p, outer, 0.008, mat="wood", segs=10, m=sc)
            for z in (H * 0.25, H * J(p, 0.6, 0.1)):
                p.ring(rad_at(outer, z) * 1.02, 0.005, sc @ T(0, 0, z), mat="bark", segs=8, square=False)
            p.ring(r * 1.02, 0.01, sc @ T(0, 0, H), mat="wood_dark", segs=8, square=False)
        elif slot == "hem":
            shoulder_straps(p, W, D, H, "rope", w=0.035, t=0.01, out=J(p, 0.05, 0.2))
        else:
            for k in range(p.rng.randint(3, 5)):
                x = p.rng.uniform(-r * 0.5, r * 0.5)
                y = yc + 0.02 + p.rng.uniform(-D * 0.25, D * 0.25)
                p.tube([(x, y, -H * 0.3), (x + p.rng.uniform(-0.04, 0.04), y + p.rng.uniform(-0.02, 0.03), J(p, 0.18, 0.3))], 0.013,
                       mat="bark", segs=5)
    elif e == "Mercantile":  # leather knapsack: flap with buckled straps, rolled blanket on top
        prof, w = pack_body(W, D, H, 0.05, 0.6)
        if slot == "cloth":
            blob(p, prof, w, m, mat="leather", segs=8)
            p.box((W * 0.92, 0.01, H * J(p, 0.5, 0.15)), M(loc=(0, D + 0.022, -H * 0.24), rot=(-3, 0, 0)), mat="leather", bevel=0.2)
        elif slot == "hem":
            shoulder_straps(p, W, D, H, "leather", out=J(p, 0.05, 0.2))
            for s in (-1, 1):
                strap(p, [(s * W * 0.22, D * 0.6, 0.005), (s * W * 0.22, D + 0.03, -0.02), (s * W * 0.22, D + 0.032, -H * 0.42)], 0.03,
                      "leather")
                p.box((0.04, 0.008, 0.035), T(s * W * 0.22, D + 0.037, -H * 0.4), mat="brass", bevel=0)
        else:
            rr = J(p, 0.055, 0.15)
            p.cyl(rr, rr, W * 1.05, M(loc=(-W * 0.525, yc, rr + 0.005), rot=(0, 90, 0)), mat="cloth", segs=8)
            for s in (-1, 1):
                p.ring(rr * 1.05, 0.006, M(loc=(s * W * 0.3, yc, rr + 0.005), rot=(0, 90, 0)), mat="leather", segs=8)
    elif e == "Industrial":  # canvas rucksack: tall body, front pocket, webbing and buckles, sleeping mat under
        prof, w = pack_body(W, D, H, 0.04, 0.5)
        if slot == "cloth":
            blob(p, prof, w, m, mat="cloth", segs=8)
            pw, pd, phh = W * 0.6, D * 0.4, H * J(p, 0.35, 0.15)
            p.box((pw, pd, phh), T(0, D + 0.005, -H * 0.62), mat="cloth", bevel=0.35)
            p.box((W * 0.75, 0.01, 0.006), T(0, D + 0.008, -H * 0.12), mat="rubber", bevel=0)
        elif slot == "hem":
            shoulder_straps(p, W, D, H, "rubber", w=0.045, out=J(p, 0.055, 0.2))
            for s in (-1, 1):
                p.box((0.03, D * 0.9, 0.025), T(s * (W / 2 + 0.006), yc, -H * J(p, 0.35, 0.1)), mat="rubber", bevel=0)
                p.box((0.012, 0.03, 0.03), T(s * (W / 2 + 0.014), yc - D * 0.2, -H * 0.35), mat="steel", bevel=0)
        else:
            rr = J(p, 0.06, 0.15)
            p.cyl(rr, rr, W * 1.1, M(loc=(-W * 0.55, yc, -H - rr * 0.9), rot=(0, 90, 0)), mat="accent", segs=8)
            if coin(p):
                p.cyl(0.035, 0.035, 0.13, T(W / 2 + 0.03, yc, -H * 0.95), mat="steel", segs=8)
    elif e == "Steampunk":  # brass-framed pack: leather bag in a brass frame, a small boiler tank across the top
        prof, w = pack_body(W, D, H, 0.04, 0.6)
        if slot == "cloth":
            blob(p, prof, w, m, mat="leather", segs=8)
            p.box((W * 0.5, 0.01, H * 0.3), T(0, D + 0.02, -H * J(p, 0.55, 0.1)), mat="leather", bevel=0.2)
        elif slot == "hem":
            for s in (-1, 1):
                p.tube([(s * W * 0.52, 0.01, 0.02), (s * W * 0.55, yc, -H * 0.5), (s * W * 0.52, D * 0.9, -H - 0.01)], 0.008, mat="brass", segs=5)
            p.tube([(-W * 0.52, D * 0.9, -H - 0.01), (W * 0.52, D * 0.9, -H - 0.01)], 0.008, mat="brass", segs=5)
            shoulder_straps(p, W, D, H, "leather", w=0.04, out=J(p, 0.05, 0.2))
            for s in (-1, 1):
                p.ball(0.012, T(s * W * 0.55, yc, -H * 0.5), mat="copper", segs=(5, 3))
        else:
            rr = J(p, 0.05, 0.12)
            p.cyl(rr, rr, W * 0.85, M(loc=(-W * 0.425, yc + 0.01, rr + 0.004), rot=(0, 90, 0)), mat="brass", segs=8)
            for x in (-W * 0.3, W * J(p, 0.3, 0.2)):
                p.ring(rr * 1.03, 0.005, M(loc=(x, yc + 0.01, rr + 0.004), rot=(0, 90, 0)), mat="copper", segs=8)
            p.tube([(W * 0.425, yc + 0.01, rr), (W * 0.48, yc + 0.03, rr * 0.5), (W * 0.5, D, -H * 0.3)], 0.006, mat="copper", segs=4)
            p.cyl(0.022, 0.022, 0.01, M(loc=(-W * 0.1, yc + 0.01 - rr, rr + 0.004), rot=(90, 0, 0)), mat="glass", segs=8)
    elif e == "Future":  # exoskeleton pack: sleek pod on a segmented spine, arms over the shoulders and round the hips
        if slot == "cloth":
            p.ball(1.0, M(loc=(0, yc + 0.01, -H * 0.5), scale=(W / 2, D / 2, H / 2)), mat="shell", segs=(10, 6))
            p.box((W * 0.5, 0.01, H * J(p, 0.5, 0.15)), T(0, yc + D / 2 - 0.004, -H * 0.5), mat="shell_dark", bevel=0.3)
        elif slot == "hem":
            n = 4
            for i in range(n):
                p.box((0.06, 0.03, H / n * 0.8), T(0, 0.012, -H / n * (i + 0.5)), mat="shell_dark", bevel=0.25, bevel_seg=1)
            for s in (-1, 1):
                p.tube([(s * 0.03, 0.01, -0.01), (s * W * 0.3, -0.04, 0.04), (s * W * 0.36, -J(p, 0.16, 0.12), 0.0),
                        (s * W * 0.36, -0.2, -0.12)], 0.012, mat="shell_dark", segs=4)
                p.tube([(s * 0.03, 0.01, -H + 0.02), (s * W * 0.45, -0.05, -H - 0.01), (s * W * 0.45, -0.17, -H - 0.01)], 0.014,
                       mat="shell_dark", segs=4)
        else:
            p.box((W * 0.3, 0.05, J(p, 0.03, 0.2)), T(0, yc + 0.01, 0.012), mat="shell_dark", bevel=0.4, bevel_seg=1)
            if coin(p):
                p.cyl(0.004, 0.003, J(p, 0.12, 0.2), T(W * 0.2, yc + D * 0.2, 0.0), mat="shell_dark", segs=4)
    elif e == "Wasteland":  # scrap pack: patched bag on a pipe frame, wire lashing, tin can and tarp roll
        prof, w = pack_body(W, D, H, 0.07, 0.6)
        if slot == "cloth":
            blob(p, prof, w, m, mat="cloth", segs=8)
            for k in range(p.rng.randint(1, 2)):
                p.box((W * J(p, 0.35, 0.2), 0.008, H * 0.2), M(loc=(p.rng.uniform(-W * 0.2, W * 0.2), D + 0.022, -H * (0.3 + 0.3 * k)),
                                                             rot=(0, p.rng.uniform(-12, 12), 0)), mat=("paint", "rust")[k], bevel=0)
        elif slot == "hem":
            for s in (-1, 1):
                p.cyl(0.011, 0.011, H * 1.08, M(loc=(s * W * 0.48, 0.03, -H * 1.04), rot=(J(p, 3, 0.6), 0, 0)), mat="rust", segs=6)
            p.cyl(0.009, 0.009, W * 1.0, M(loc=(-W * 0.5, 0.03, -H * 0.15), rot=(0, 90, 0)), mat="iron", segs=6)
            for z in (-H * 0.3, -H * 0.7):
                p.ring(W * 0.52, 0.003, M(loc=(0, yc, z), scale=(1, D / W * 1.1, 1)), mat="iron", segs=10)
            shoulder_straps(p, W, D, H, "cloth", w=0.04, out=J(p, 0.05, 0.2))
        else:
            p.cyl(0.035, 0.035, J(p, 0.08, 0.2), T(-W * 0.35, D + 0.02, -H - 0.09), mat="steel", segs=8)
            p.tube([(-W * 0.35, D + 0.02, -H - 0.01), (-W * 0.35, D + 0.02, -H + 0.0)], 0.003, mat="iron", segs=3)
            rr = J(p, 0.05, 0.2)
            p.cyl(rr, rr, W * 0.9, M(loc=(-W * 0.45, yc, rr + 0.003), rot=(0, 90, p.rng.uniform(-6, 6))), mat="paint", segs=7)
    else:  # Ancient: stone carapace on a stone yoke, rune channel down the shell, gold capstone
        if slot == "cloth":
            p.ball(1.0, M(loc=(0, yc, -H * 0.5), scale=(W / 2, D / 2, H / 2)), mat="stone", segs=(8, 5))
            for i in range(3):
                p.box((0.012, 0.006, H * 0.18), T(0, yc + D / 2 + 0.0, -H * (0.3 + 0.2 * i)), mat="glow", bevel=0)
        elif slot == "hem":
            shoulder_straps(p, W, D, H, "stone_dark", w=0.06, t=0.015, out=J(p, 0.05, 0.2))
            p.box((W * 0.7, 0.04, 0.05), T(0, 0.02, -0.03), mat="stone_dark", bevel=0.3)
        else:
            p.cyl(J(p, 0.045, 0.15), 0.04, 0.025, T(0, yc, -0.005), mat="gold", segs=8)
            p.box((0.02, 0.02, 0.004), T(0, yc, 0.021), mat="glow", bevel=0)


# ---------------------------------------------------------------- Ball (rests on the floor, origin at z = 0)
def great(p, R, zc, tilt, spin, w, mat, segs=10, lift=1.015):
    """Band along a great circle of a ball (seams, hoops, tape): spans the ball's height when tilt is 90."""
    p.ring(R * lift, w, T(0, 0, zc) @ M(rot=(0, 0, spin)) @ M(rot=(tilt, 0, 0)), mat=mat, segs=segs)


@function("Ball", "Soft", SOFT, "carried")
def ball(p, slot):
    e = p.era
    R = F(p, {"Primal": 0.075, "Steampunk": 0.09, "Future": 0.09, "Ancient": 0.1}.get(e, 0.11), 0.08)
    lift = 0.04 if e == "Future" else 0.0
    zc = R + lift
    spin = p.frame.uniform(0, 180)
    if e == "Primal":  # woven rattan ball: strips crossing in three directions over a dark core
        if slot == "cloth":
            for k, (tl, sp) in enumerate(((90, 0), (90, 60), (90, 120), (0, 0))):
                great(p, R, zc, tl, spin + sp, 0.007, "wood", segs=10, lift=1.0)
            if coin(p):
                great(p, R, zc, 90, spin + 30, 0.005, "wood", segs=10)
        elif slot == "hem":
            p.ball(R * J(p, 0.86, 0.04), T(0, 0, zc), mat="bark", segs=(8, 6))
        else:
            p.tube([(0, 0, 2 * R - 0.005), (0.01, 0.0, 2 * R + J(p, 0.03, 0.3)), (0.025, 0.01, 2 * R + 0.03)], 0.004, mat="wood", segs=3)
    elif e == "Agrarian":  # stuffed leather ball: lumpy bladder, laced meridian seam, knot on top
        if slot == "cloth":
            p.ball(R, M(loc=(0, 0, zc), scale=(1, 1, J(p, 0.96, 0.03))), mat="leather", segs=(10, 7))
        elif slot == "hem":
            great(p, R, zc, 90, spin, 0.004, "hide", segs=12)
            if coin(p):
                great(p, R, zc, 90, spin + 90, 0.003, "hide", segs=12, lift=1.01)
            for k in range(p.rng.randint(5, 6)):
                a = math.pi * (k + 1) / 7
                p.box((0.004, 0.018, 0.004), T(0, 0, zc) @ M(rot=(0, 0, spin)) @ M(loc=(0, math.cos(a) * R * 1.015, math.sin(a) * R * 1.015)) @
                      M(rot=(math.degrees(a), 0, 0)), mat="hide", bevel=0)
        else:
            p.ball(J(p, 0.012, 0.2), T(0, 0, 2 * R + 0.004), mat="hide", segs=(5, 3))
    elif e == "Mercantile":  # stitched panel ball: three crossing seams with stitch knots, maker's button on top
        if slot == "cloth":
            p.ball(R, T(0, 0, zc), mat="hide", segs=(12, 8))
        elif slot == "hem":
            for tl, sp in ((90, 0), (90, 90), (0, 0)):
                great(p, R, zc, tl, spin + sp, 0.0035, "leather", segs=10, lift=1.008)
        else:
            p.cyl(J(p, 0.014, 0.2), 0.012, 0.004, T(0, 0, 2 * R - 0.001), mat="brass", segs=8)
    elif e == "Industrial":  # rubber play ball: two crossing stripes, inflation valve
        if slot == "cloth":
            p.ball(R, T(0, 0, zc), mat="paint", segs=(12, 8))
        elif slot == "hem":
            w = J(p, 0.012, 0.2)
            great(p, R, zc, 90, spin, w, "shell", segs=10, lift=1.0)
            great(p, R, zc, 90, spin + 90, w, "shell", segs=10, lift=1.0)
        else:
            p.cyl(0.007, 0.005, J(p, 0.01, 0.3), T(0, 0, 2 * R - 0.002), mat="rubber", segs=6)
    elif e == "Steampunk":  # spring ball: leather core in a brass helix coil, brass pole caps
        if slot == "cloth":
            p.ball(R * 0.86, T(0, 0, zc), mat="leather", segs=(10, 7))
            for k in range(4):
                a = spin + k * 90
                p.ball(0.006, T(0, 0, zc) @ M(rot=(0, 0, a)) @ T(R * 0.86, 0, 0), mat="copper", segs=(4, 3))
        elif slot == "hem":
            turns = J(p, 3.0, 0.15)
            pts = []
            for i in range(25):
                t = i / 24
                th = math.pi * t
                a = math.radians(spin) + turns * math.tau * t
                pts.append((math.cos(a) * math.sin(th) * R, math.sin(a) * math.sin(th) * R, zc - math.cos(th) * R))
            p.tube(pts, 0.006, mat="brass", segs=4)
        else:
            p.cyl(R * 0.3, R * 0.2, J(p, 0.012, 0.3), T(0, 0, 2 * R - 0.012), mat="brass", segs=8)
            p.cyl(R * 0.2, R * 0.3, 0.012, T(0, 0, 0.0), mat="brass", segs=8)
    elif e == "Future":  # hover ball: segmented shell floating a hand above the floor, sensor dome on top
        if slot == "cloth":
            p.ball(R, T(0, 0, zc), mat="shell", segs=(12, 8))
        elif slot == "hem":
            great(p, R, zc, 90, spin, 0.006, "shell_dark", segs=10, lift=1.005)
            great(p, R, zc, 90, spin + J(p, 90, 0.25), 0.006, "shell_dark", segs=10, lift=1.005)
            p.ring(R * 0.35, 0.006, T(0, 0, zc - R * 0.94), mat="shell_dark", segs=8)
        else:
            p.lathe([(R * J(p, 0.3, 0.15), 2 * R + lift - 0.01), (R * 0.25, 2 * R + lift + 0.008), (0, 2 * R + lift + 0.012)], mat="glass", segs=8)
    elif e == "Wasteland":  # patched ball: squashed tyre-rubber ball, tape strips, wire twist on top
        if slot == "cloth":
            p.ball(R, M(loc=(0, 0, zc * 0.92), scale=(1.04, 1.04, 0.92)), mat="rubber", segs=(10, 7))
        elif slot == "hem":
            for k in range(p.rng.randint(2, 3)):
                great(p, R, zc * 0.92, 90, spin + k * 70, 0.01, "cloth", segs=12, lift=1.02)
        else:
            top = zc * 0.92 + R * 0.92
            p.tube([(0, 0, top - 0.004), (0.006, 0, top + 0.02), (-0.008, 0.004, top + J(p, 0.03, 0.3))], 0.002, mat="iron", segs=3)
            p.box((0.03, 0.03, 0.004), M(loc=(0, 0, top - 0.002), rot=(0, 0, J(p, 30, 0.8))), mat="paint", bevel=0)
    else:  # Ancient: stone sphere with carved great-circle grooves and a rune disc at the crown
        if slot == "cloth":
            p.ball(R, T(0, 0, zc), mat="stone", segs=(10, 7))
        elif slot == "hem":
            great(p, R, zc, 90, spin, 0.008, "stone_dark", segs=12, lift=1.0)
            great(p, R, zc, 90, spin + J(p, 90, 0.2), 0.008, "stone_dark", segs=12, lift=1.0)
        else:
            p.cyl(R * 0.28, R * 0.24, 0.008, T(0, 0, 2 * R - 0.004), mat="gold", segs=8)
            p.box((R * 0.25, 0.006, 0.004), M(loc=(0, 0, 2 * R + 0.005), rot=(0, 0, J(p, 45, 0.5))), mat="glow", bevel=0)


# ---------------------------------------------------------------- Kite (origin at the grip at the foot of the spine)
OUTLINE = {
    "Primal": [(0, 0.03), (0.15, 0.3), (0.45, 0.5), (0.7, 0.42), (0.9, 0.2), (1, 0.02)],
    "Agrarian": [(0, 0.42), (0.75, 0.42), (0.86, 0.38), (0.95, 0.24), (1, 0.05)],
    "Mercantile": [(0, 0.05), (0.15, 0.35), (0.3, 0.42), (0.42, 0.2), (0.5, 0.12), (0.62, 0.4), (0.78, 0.55), (0.9, 0.42), (1, 0.05)],
    "Steampunk": [(0, 0.03), (0.2, 0.25), (0.35, 0.18), (0.5, 0.42), (0.62, 0.34), (0.78, 0.55), (0.9, 0.48), (1, 0.04)],
    "Wasteland": [(0, 0.02), (0.68, 0.5), (1, 0.02)],
    "Ancient": [(0, 0.02), (0.65, 0.5), (1, 0.02)],
}


def sail_fn(table, Wk, H, bow, ph, lift=0.0):
    def fn(u, v):
        hw = max(tab(table, v) * Wk, 0.004)
        x = (2 * u - 1) * hw
        y = bow * (1 - (2 * u - 1) ** 2) * math.sin(math.pi * v) + 0.004 * math.sin(u * 7 + ph) - lift
        return (x, y, v * H)
    return fn


def kite_tail(p, x0, L, w, ph, mat, sway=0.05):
    sheet(p, lambda u, v: (x0 + sway * math.sin(v * math.pi * 1.5 + ph) + (u - 0.5) * w * (1 - 0.4 * v),
                           0.01 + 0.02 * math.sin(v * math.tau + ph), -v * L), 1, 6, 0.004, mat)


@function("Kite", "Soft", SOFT, "carried")
def kite(p, slot):
    e = p.era
    H = F(p, {"Primal": 0.62, "Agrarian": 0.7, "Industrial": 0.72, "Future": 0.09}.get(e, 0.66), 0.08)
    Wk = F(p, {"Agrarian": 1.0, "Industrial": 0.42, "Future": 0.55}.get(e, 0.9) * 0.6, 0.08)
    L = F(p, 0.42, 0.15)
    bow = F(p, 0.035, 0.3)
    ph = p.frame.uniform(0, math.tau)
    if e in OUTLINE:
        tb = OUTLINE[e]
        fn = sail_fn(tb, Wk, H, bow, ph)

        def spar(vc, k=0.88, dy=0.008):
            hw = tab(tb, vc) * Wk * k
            return [(x, bow * (1 - (x / max(hw / k, 1e-3)) ** 2) * math.sin(math.pi * vc) + dy, vc * H) for x in (-hw, -hw * 0.5, 0, hw * 0.5, hw)]

        def spine(dy=0.008):
            return [(0, bow * math.sin(math.pi * v) + dy, v * H) for v in (0, 0.25, 0.5, 0.75, 1.0)]

        def decal(u0, u1, v0, v1, mat, nu=2, nv=2):
            sheet(p, lambda u, v: Vector(sail_fn(tb, Wk, H, bow, ph, 0.006)(u0 + (u1 - u0) * u, v0 + (v1 - v0) * v)), nu, nv, 0.003, mat)
    if e == "Primal":  # big dried leaf on a twig spine and cross stick, knotted-grass tail
        if slot == "cloth":
            sheet(p, fn, 3, 6, 0.005, "bark")
        elif slot == "hem":
            p.tube(spine(), 0.007, mat="wood", segs=4)
            p.tube(spar(J(p, 0.5, 0.1), 0.82), 0.006, mat="wood", segs=4)
        else:
            kite_tail(p, 0, L, 0.03, ph, "rope")
            for k in range(p.rng.randint(2, 4)):
                v = (k + 1) / 5
                p.ball(0.012, T(0.05 * math.sin(v * math.pi * 1.5 + ph), 0.01, -v * L), mat="rope", segs=(4, 3))
    elif e == "Agrarian":  # paper kite: arched-top panel on a bamboo cross, painted roundel, twin paper tails
        if slot == "cloth":
            sheet(p, fn, 4, 6, 0.004, "bone")
            decal(0.3, 0.7, 0.4, 0.62, "paint")
        elif slot == "hem":
            p.tube(spine(), 0.005, mat="wood", segs=4)
            p.tube(spar(0.6), 0.005, mat="wood", segs=4)
            p.tube(spar(J(p, 0.88, 0.04), 0.85), 0.005, mat="wood", segs=4)
            if coin(p):
                p.tube(spar(0.2), 0.004, mat="wood", segs=4)
        else:
            for s in (-1, 1):
                kite_tail(p, s * tab(tb, 0) * Wk * 0.9, L * J(p, 1.0, 0.15), 0.035, ph + s, "paint", 0.03)
    elif e == "Mercantile":  # silk butterfly kite: two wing pairs, eye spots, bamboo spars, ribbon streamers
        if slot == "cloth":
            sheet(p, fn, 4, 8, 0.004, "cloth")
            for u0 in (0.08, 0.72):
                decal(u0, u0 + 0.2, 0.68, 0.84, "paint")
        elif slot == "hem":
            p.tube(spine(), 0.005, mat="wood_dark", segs=4)
            p.tube(spar(0.78, 0.9), 0.004, mat="wood_dark", segs=4)
            p.tube(spar(J(p, 0.28, 0.08), 0.86), 0.004, mat="wood_dark", segs=4)
        else:
            for s in (-1, 1):
                kite_tail(p, s * 0.02, L * J(p, 1.2, 0.15), 0.025, ph + s * 1.3, "paint", 0.06)
            p.tube([(0, bow * 0.1, H * 0.98), (-0.04, 0.0, H + 0.06)], 0.002, mat="wood_dark", segs=3)
            p.tube([(0, bow * 0.1, H * 0.98), (0.04, 0.0, H + 0.06)], 0.002, mat="wood_dark", segs=3)
    elif e == "Industrial":  # box kite: two square cloth cells on four dowel longerons, bridle and short tail
        s = Wk / 2
        rq = s * math.sqrt(2)
        if slot == "cloth":
            for z0, z1 in ((0.03 * H, 0.33 * H), (0.67 * H, 0.97 * H)):
                p.lathe([(rq * 0.98, z0), (rq, z0), (rq, z1), (rq * 0.98, z1), (rq * 0.98, z0)], M(rot=(0, 0, 45)), mat="cloth", segs=4)
        elif slot == "hem":
            for x in (-s, s):
                for y in (-s, s):
                    p.cyl(0.005, 0.005, H, T(x, y, 0), mat="wood", segs=4)
            for z in (0.18 * H, J(p, 0.82, 0.03) * H):
                p.tube([(-s, -s, z), (s, s, z)], 0.004, mat="wood", segs=3)
                p.tube([(s, -s, z), (-s, s, z)], 0.004, mat="wood", segs=3)
        else:
            p.tube([(-s, -s, 0.4 * H), (0, -s - J(p, 0.12, 0.2), 0.3 * H), (0, -s - 0.02, 0.0)], 0.002, mat="rope", segs=3)
            kite_tail(p, 0, L * 0.6, 0.03, ph, "paint", 0.03)
    elif e == "Steampunk":  # brass-boned bat-wing kite: scalloped leather membrane, radiating brass ribs, weighted tail
        if slot == "cloth":
            sheet(p, fn, 4, 8, 0.004, "leather")
        elif slot == "hem":
            p.tube(spine(), 0.006, mat="brass", segs=4)
            hub = (0, bow * 0.7 + 0.008, H * 0.42)
            for v in (0.22, 0.5, J(p, 0.79, 0.03)):
                hw = tab(tb, v) * Wk * 0.88
                for sgn in (-1, 1):
                    p.tube([hub, (sgn * hw, 0.008, v * H)], 0.004, mat="brass", segs=3)
            p.ball(0.014, T(*hub), mat="copper", segs=(5, 3))
        else:
            p.tube([(0, 0.008, 0), (0.01, 0.01, -L * 0.5), (0, 0.01, -L * J(p, 0.75, 0.1))], 0.003, mat="brass", segs=3)
            p.cyl(0.03, 0.03, 0.006, M(loc=(0, 0.01, -L * 0.75), rot=(90, 0, 0)), mat="brass", segs=8)
            p.plate([(-0.04, 0), (0, -0.06), (0.04, 0)], 0.004, T(0, 0.01, -L * 0.75 - 0.025), mat="copper", bevel=0)
    elif e == "Future":  # small quad drone held from below: body pod, four arms with rotor guards, skids
        span = Wk / 2
        zb = 0.045
        if slot == "cloth":
            p.ball(1.0, M(loc=(0, 0, zb), scale=(0.055, 0.075, 0.028)), mat="shell", segs=(8, 5))
            p.ball(0.022, M(loc=(0, -0.02, zb + 0.02), scale=(1, 1.3, 0.6)), mat="shell_dark", segs=(6, 4))
        elif slot == "hem":
            rr = J(p, 0.055, 0.12)
            for k in range(4):
                a = math.radians(45 + 90 * k)
                c = (math.cos(a) * span, math.sin(a) * span, zb + 0.008)
                p.box((span, 0.016, 0.012), M(loc=(c[0] / 2, c[1] / 2, zb), rot=(0, 0, math.degrees(a))), mat="shell_dark", bevel=0)
                p.ring(rr, 0.005, T(*c), mat="shell", segs=6)
                p.box((rr * 1.7, 0.012, 0.002), M(loc=(c[0], c[1], c[2] + 0.006), rot=(0, 0, k * 37)), mat="rubber", bevel=0)
        else:
            for s in (-1, 1):
                p.tube([(s * 0.035, -0.04, zb - 0.02), (s * 0.04, -0.04, 0.004), (s * 0.04, 0.04, 0.004), (s * 0.035, 0.04, zb - 0.02)],
                       0.003, mat="shell_dark", segs=4)
            p.ball(J(p, 0.012, 0.2), T(0, -0.06, zb - 0.015), mat="glass", segs=(6, 4))
    elif e == "Wasteland":  # bin-bag diamond on scrap rods, wire-lashed cross, rag-knot tail
        if slot == "cloth":
            sheet(p, fn, 4, 6, 0.004, "cloth")
            decal(J(p, 0.15, 0.3), 0.5, 0.3, 0.55, "paint")
        elif slot == "hem":
            p.tube(spine(), 0.005, mat="iron", segs=4)
            vc = 0.68
            p.tube(spar(vc, 0.9), 0.005, mat="rust", segs=4)
            for i in range(2):
                p.ring(0.012, 0.002, M(loc=(0, bow + 0.008, vc * H + (i - 0.5) * 0.008), rot=(0, J(p, 30, 0.5), 45 * i)), mat="iron", segs=6)
        else:
            kite_tail(p, 0, L, 0.02, ph, "rope", 0.04)
            for k in range(p.rng.randint(2, 4)):
                v = (k + 1) / 5
                p.box((0.04, 0.012, 0.02), M(loc=(0.04 * math.sin(v * math.pi * 1.5 + ph), 0.01, -v * L), rot=(0, p.rng.uniform(-30, 30), 0)),
                      mat=("paint", "cloth", "rust")[k % 3], bevel=0)
    else:  # Ancient: diamond of thin stone tiles on a gold cross, rune slot at the heart, tail of stone discs
        if slot == "cloth":
            sheet(p, fn, 2, 4, 0.01, "stone")
            decal(0.42, 0.58, 0.55, 0.72, "glow", 1, 1)
        elif slot == "hem":
            p.tube(spine(-0.002 + 0.012), 0.008, mat="gold", segs=4)
            p.tube(spar(0.65, J(p, 0.9, 0.03), 0.012), 0.007, mat="gold", segs=4)
        else:
            p.tube([(0, 0.01, 0), (0.02, 0.01, -L * 0.5), (0, 0.01, -L * J(p, 0.9, 0.08))], 0.002, mat="gold", segs=3)
            for k in range(3):
                p.cyl(0.018, 0.018, 0.008, M(loc=(0.013 * (k % 2), 0.006, -L * (0.3 + 0.25 * k)), rot=(90, 0, 0)), mat="stone", segs=6)


# ---------------------------------------------------------------- PrayerBeads (origin at the top of the loop, hangs -Z)
def bead_loop(Wl, Lh, n, gap=0.6):
    """Bead centres round a hanging teardrop loop, leaving a gap at the bottom for the knot."""
    out = []
    for i in range(n):
        th = math.pi + gap / 2 + (math.tau - gap) * i / (n - 1)
        x = Wl * math.sin(th) * (0.55 + 0.45 * (1 - math.cos(th)) / 2)
        out.append((x, 0.0, -Lh * (1 - math.cos(th)) / 2))
    return out


def cord(Wl, Lh, n=12):
    return [(Wl * math.sin(th) * (0.55 + 0.45 * (1 - math.cos(th)) / 2), 0.0, -Lh * (1 - math.cos(th)) / 2)
            for th in (math.pi + math.tau * i / n for i in range(n + 1))]


@function("PrayerBeads", "Soft", SOFT, "carried")
def prayer_beads(p, slot):
    e = p.era
    Lh = F(p, {"Future": 0.16, "Steampunk": 0.2}.get(e, 0.22), 0.08)
    Wl = F(p, {"Future": 0.08}.get(e, 0.07), 0.08)
    rb = F(p, {"Primal": 0.011, "Mercantile": 0.01, "Steampunk": 0.011, "Wasteland": 0.011, "Ancient": 0.011}.get(e, 0.009), 0.1)
    Lk = F(p, 0.035, 0.15)
    n = 14
    zk = -Lh - rb  # bottom of the loop: the knot hangs from here
    if e == "Primal":  # bone and tooth beads on a sinew cord, claw pendant
        if slot == "cloth":
            p.tube(cord(Wl, Lh), 0.0018, mat="hide", segs=3)
            for i, c in enumerate(bead_loop(Wl, Lh, n - 2)):
                if i % 3 == 1:
                    p.cyl(rb * 0.6, rb * 0.2, rb * J(p, 2.6, 0.2), M(loc=c, rot=(0, 90 if c[0] > 0 else -90, 0)), mat="bone", segs=5)
                else:
                    p.cyl(rb * 0.8, rb * 0.8, rb * J(p, 1.6, 0.2), M(loc=c, rot=(0, 0, 0)) @ T(0, 0, -rb * 0.8), mat="bone", segs=5)
        elif slot == "hem":
            p.ball(rb * 1.3, T(0, 0, zk), mat="hide", segs=(5, 3))
            for s in (-1, 1):
                p.tube([(0, 0, zk), (s * 0.008, 0, zk - Lk * J(p, 1.0, 0.2))], 0.0018, mat="hide", segs=3)
        else:
            z = zk - Lk
            p.plate([(-0.008, 0), (-0.005, -0.035), (0.004, J(p, -0.05, 0.15)), (0.008, 0)], 0.006, T(0, 0, z), mat="bone", bevel=0)
    elif e == "Agrarian":  # turned wooden beads, larger guru bead, cotton tassel
        if slot == "cloth":
            p.tube(cord(Wl, Lh), 0.0015, mat="rope", segs=3)
            for c in bead_loop(Wl, Lh, n):
                p.ball(rb * J(p, 1.0, 0.08), T(*c), mat="wood", segs=(5, 3))
        elif slot == "hem":
            p.ball(rb * J(p, 1.5, 0.12), T(0, 0, zk - rb * 0.4), mat="wood_dark", segs=(6, 4))
            p.tube([(0, 0, zk - rb), (0, 0, zk - Lk)], 0.0025, mat="rope", segs=3)
        else:
            z = zk - Lk
            p.lathe([(0.004, 0), (0.006, -0.01), (J(p, 0.014, 0.2), -0.05), (0, -0.052)], T(0, 0, z), mat="cloth", segs=6)
    elif e == "Mercantile":  # jade beads with gold spacers, silk cord, jade disc and tassel
        if slot == "cloth":
            p.tube(cord(Wl, Lh), 0.0015, mat="cloth", segs=3)
            for i, c in enumerate(bead_loop(Wl, Lh, n)):
                if i in (3, 10):
                    p.cyl(rb * 0.9, rb * 0.9, rb * 0.6, T(c[0], c[1], c[2] - rb * 0.3), mat="gold", segs=6)
                else:
                    p.ball(rb, T(*c), mat="glaze", segs=(5, 3))
        elif slot == "hem":
            p.ball(rb * 1.4, T(0, 0, zk - rb * 0.4), mat="gold", segs=(6, 4))
            p.tube([(0, 0, zk - rb), (0, 0, zk - Lk)], 0.002, mat="cloth", segs=3)
        else:
            z = zk - Lk
            R = J(p, 0.018, 0.15)
            p.cyl(R, R, 0.004, M(loc=(0, 0, z - R), rot=(90, 0, 0)) @ T(0, 0, -0.002), mat="glaze", segs=10)
            p.lathe([(0.003, -2 * R), (0.005, -2 * R - 0.01), (0.009, -2 * R - 0.04), (0, -2 * R - 0.042)], T(0, 0, z), mat="cloth", segs=5)
    elif e == "Industrial":  # steel beads on a ball chain, crimp ring, stamped medallion
        if slot == "cloth":
            p.tube(cord(Wl, Lh), 0.0012, mat="steel", segs=3)
            for i, c in enumerate(bead_loop(Wl, Lh, n)):
                if i % 4 == 0:
                    p.cyl(rb, rb, rb * 1.2, M(loc=c) @ T(0, 0, -rb * 0.6), mat="iron", segs=6)
                else:
                    p.ball(rb * J(p, 0.9, 0.05), T(*c), mat="steel", segs=(5, 3))
        elif slot == "hem":
            p.ring(rb * 1.1, 0.0025, M(loc=(0, 0, zk - rb * 0.6), rot=(90, 0, 0)), mat="steel", segs=8)
            p.tube([(0, 0, zk - rb * 1.6), (0, 0, zk - Lk * J(p, 1.0, 0.15))], 0.0015, mat="steel", segs=3)
        else:
            z = zk - Lk
            R = J(p, 0.016, 0.15)
            p.cyl(R, R, 0.003, M(loc=(0, 0, z - R), rot=(90, 0, 0)) @ T(0, 0, -0.0015), mat="steel", segs=10)
            p.box((R * 0.9, 0.004, 0.003), T(0, 0, z - R), mat="iron", bevel=0)
    elif e == "Steampunk":  # gear beads on a copper wire, crank-shaped guru bead, gear pendant
        if slot == "cloth":
            p.tube(cord(Wl, Lh), 0.0015, mat="copper", segs=3)
            for i, c in enumerate(bead_loop(Wl, Lh, n - 2)):
                if i % 2:
                    p.cyl(rb * 1.1, rb * 1.1, rb * 0.5, M(loc=c, rot=(0, 90, 0)) @ T(0, 0, -rb * 0.25), mat="brass", segs=8)
                else:
                    p.ball(rb * 0.7, T(*c), mat="copper", segs=(5, 3))
        elif slot == "hem":
            p.cyl(rb * 1.2, rb * 1.2, rb * 1.6, T(0, 0, zk - rb * 1.6), mat="brass", segs=6)
            p.tube([(0, 0, zk - rb * 1.6), (0, 0, zk - Lk)], 0.002, mat="copper", segs=3)
        else:
            z = zk - Lk
            R = J(p, 0.02, 0.15)
            teeth = []
            for k in range(16):
                a = k * math.tau / 16
                rr = R * (1.0 if k % 2 else 0.8)
                teeth.append((math.cos(a) * rr, math.sin(a) * rr - R))
            p.plate(teeth, 0.004, T(0, 0, z), mat="brass", bevel=0)
    elif e == "Future":  # light-bead ring: a rigid shell band with glassy bead nodes, clasp node, glass tear pendant
        def ring_pts(k):
            return [(math.sin(a) * Wl, 0.0, -Lh / 2 + math.cos(a) * Lh / 2) for a in (math.tau * i / k for i in range(k + 1))]
        if slot == "cloth":
            p.tube(ring_pts(14), 0.0035, mat="shell", segs=4)
            for c in ring_pts(12)[1:]:
                p.ball(rb * J(p, 0.95, 0.05), T(*c), mat="glass", segs=(5, 3))
        elif slot == "hem":
            p.box((rb * 2.4, rb * 1.6, rb * J(p, 2.2, 0.15)), T(0, 0, -Lh - rb * 0.8), mat="shell_dark", bevel=0.3)
        else:
            z = -Lh - rb * 0.8 - rb * 1.1
            p.lathe([(0, 0), (0.008, -0.01), (J(p, 0.009, 0.2), -0.02), (0, -0.035)], T(0, 0, z), mat="glass", segs=6)
            p.tube([(0, 0, z + 0.002), (0, 0, z - 0.004)], 0.002, mat="shell_dark", segs=3)
    elif e == "Wasteland":  # hex nuts and bottle caps on twisted wire, wire knot, shell-casing pendant
        if slot == "cloth":
            p.tube(cord(Wl, Lh), 0.0015, mat="iron", segs=3)
            for i, c in enumerate(bead_loop(Wl, Lh, n - 2)):
                if i % 3 == 2:
                    p.cyl(rb * 1.3, rb * 1.3, rb * 0.5, M(loc=c, rot=(90, 0, 0)) @ T(0, 0, -rb * 0.25), mat="paint", segs=8)
                else:
                    p.cyl(rb, rb, rb * 0.9, M(loc=c, rot=(0, 90, p.rng.uniform(0, 30))) @ T(0, 0, -rb * 0.45), mat="steel", segs=6)
        elif slot == "hem":
            p.tube([(-0.006, 0, zk), (0.006, 0, zk - 0.006), (-0.004, 0, zk - 0.012), (0.002, 0, zk - Lk * J(p, 1.0, 0.15))], 0.002,
                   mat="iron", segs=3)
        else:
            z = zk - Lk
            p.cyl(0.007, 0.007, J(p, 0.035, 0.15), M(loc=(0, 0, z), rot=(180, 0, 0)), mat="brass", segs=6)
            p.cyl(0.0075, 0.0075, 0.004, M(loc=(0, 0, z + 0.002), rot=(180, 0, 0)), mat="brass", segs=6)
    else:  # Ancient: faceted stone beads with gold spacers, rune-ringed guru stone, tablet pendant
        if slot == "cloth":
            p.tube(cord(Wl, Lh), 0.0016, mat="gold", segs=3)
            for i, c in enumerate(bead_loop(Wl, Lh, n)):
                if i % 4 == 3:
                    p.cyl(rb * 0.8, rb * 0.8, rb * 0.5, T(c[0], c[1], c[2] - rb * 0.25), mat="gold", segs=6)
                else:
                    p.ball(rb * J(p, 1.05, 0.05), M(loc=c, rot=(0, 0, 45)), mat="stone", segs=(4, 3))
        elif slot == "hem":
            p.ball(rb * 1.5, T(0, 0, zk - rb * 0.5), mat="stone_dark", segs=(6, 4))
            p.ring(rb * J(p, 1.5, 0.05), 0.0018, T(0, 0, zk - rb * 0.5), mat="glow", segs=8)
            p.tube([(0, 0, zk - rb * 1.8), (0, 0, zk - Lk)], 0.002, mat="gold", segs=3)
        else:
            z = zk - Lk
            h = J(p, 0.04, 0.15)
            p.box((0.026, 0.008, h), T(0, 0, z - h / 2), mat="stone", bevel=0.3, bevel_seg=1)
            p.box((0.006, 0.003, h * 0.6), T(0, -0.004, z - h / 2), mat="glow", bevel=0)


# ---------------------------------------------------------------- Banner (pole stands on the floor, origin at its foot)
BOTTOM = {
    "flat": lambda u: 1.0,
    "point": lambda u: 1.0 - 0.28 * abs(2 * u - 1),
    "swallow": lambda u: 1.0 - 0.25 * (1 - abs(2 * u - 1)),
    "tails": lambda u: 1.0 - 0.2 * abs(math.sin(u * math.pi * 3)),
    "torn": lambda u: 1.0 - 0.1 * abs(math.sin(u * 11.0)) - 0.06 * abs(math.sin(u * 23.0)),
}


def banner_fn(Wc, Lc, top, y0, folds, amp, ph, bottom="flat", taper=0.0, front=0.0):
    """Cloth hanging from a crossbar at z = top: vertical folds that deepen toward the hem, slight inward taper."""
    cut = BOTTOM[bottom]

    def fn(u, v):
        x = (u - 0.5) * Wc * (1 - taper * v)
        z = top - v * Lc * cut(u)
        y = y0 - amp * math.sin(u * math.pi * folds + ph) * (0.25 + 0.75 * v) - 0.015 * v * v - front
        return (x, y, z)
    return fn


@function("Banner", "Soft", SOFT, "carried")
def banner(p, slot):
    e = p.era
    Hp = F(p, {"Primal": 2.1, "Future": 2.3, "Ancient": 2.1}.get(e, 2.25), 0.06)
    Wc = F(p, {"Primal": 0.26, "Agrarian": 0.36, "Industrial": 0.5, "Future": 0.52, "Ancient": 0.4}.get(e, 0.46), 0.08)
    Lc = F(p, {"Primal": 0.7, "Agrarian": 1.15, "Future": 0.9, "Ancient": 0.95}.get(e, 1.0), 0.08)
    rp = F(p, {"Industrial": 0.018, "Future": 0.02, "Ancient": 0.035}.get(e, 0.022), 0.08)
    ph = p.frame.uniform(0, math.tau)
    Hc = Hp * 0.9
    yc = -rp - 0.014  # crossbar and cloth sit just in front of the pole
    top = Hc - 0.012
    if e == "Primal":  # feather pole: crooked staff, lashed cross-stick, hide streamer, hanging feathers, stone cairn
        if slot == "cloth":
            sheet(p, banner_fn(Wc, Lc, top, yc, 2, 0.02, ph, "torn", 0.25), 3, 6, 0.006, "hide")
        elif slot == "hem":
            w = [J(p, 0.02, 0.6) * (1 if i % 2 else -1) for i in range(5)]
            p.tube([(w[i] * (0 < i < 4), w[(i + 2) % 5] * 0.4 * (0 < i < 4), Hp * i / 4) for i in range(5)], rp, mat="wood", segs=6)
            p.tube([(-Wc * 0.75, yc, Hc + 0.02), (Wc * 0.75, yc, Hc - J(p, 0.03, 0.5))], 0.01, mat="wood", segs=5)
            p.ring(rp * 1.3, 0.006, T(0, 0, Hc), mat="rope", segs=6)
            for k in range(3):
                a = ph + k * 2.1
                p.ball(0.06, M(loc=(math.cos(a) * 0.07, math.sin(a) * 0.07, 0.03), scale=(1, 0.8, 0.6)), mat="stone", segs=(5, 3))
        else:
            for s in (-1, 1):
                x = s * Wc * 0.6
                z = Hc - 0.01
                p.tube([(x, yc, z), (x, yc, z - 0.12)], 0.002, mat="rope", segs=3)
                p.cyl(0.014, 0.0, J(p, 0.16, 0.2), M(loc=(x, yc, z - 0.12), rot=(180 + p.rng.uniform(-10, 10), 0, 0)), mat="feather", segs=5)
            for k in range(p.rng.randint(2, 3)):
                p.cyl(0.012, 0.0, J(p, 0.2, 0.2), M(loc=(0, 0, Hp - 0.02), rot=(p.rng.uniform(-25, 25), p.rng.uniform(-25, 25), 0)),
                      mat="feather", segs=5)
    elif e == "Agrarian":  # cloth 幡: tall narrow cloth with three tails, header band, T crossbar, knob finial, cords
        if slot == "cloth":
            fn = banner_fn(Wc, Lc, top, yc, 3, 0.018, ph, "tails")
            sheet(p, fn, 6, 6, 0.006, "cloth")
            sheet(p, lambda u, v: Vector(fn(u, v * 0.1)) + Vector((0, -0.005, 0)), 3, 1, 0.004, "paint")
        elif slot == "hem":
            p.cyl(rp, rp * 0.9, Hp, mat="wood", segs=8)
            p.cyl(0.011, 0.011, Wc * 1.3, M(loc=(-Wc * 0.65, yc, Hc), rot=(0, 90, 0)), mat="wood", segs=6)
            p.lathe([(rp * 0.9, Hp), (rp * 1.6, Hp + 0.03), (rp * J(p, 1.2, 0.15), Hp + 0.07), (0, Hp + 0.09)], mat="wood_dark", segs=8)
            for s in (-1, 1):
                p.tube([(s * Wc * 0.6, yc, Hc), (0, yc * 0.5, Hp - 0.02)], 0.003, mat="rope", segs=3)
            p.lathe([(0, 0), (0.09, 0), (0.08, 0.06), (rp * 1.2, 0.08), (0, 0.08)], mat="stone", segs=6)
        else:
            for s in (-1, 1):
                x = s * Wc * 0.65
                p.tube([(x, yc, Hc), (x + 0.01 * s, yc - 0.01, Hc - J(p, 0.35, 0.2))], 0.004, mat="paint", segs=3)
                p.ball(0.014, T(x + 0.01 * s, yc - 0.01, Hc - 0.02), mat="paint", segs=(5, 3))
    elif e == "Mercantile":  # heraldic banner: pointed hem with gold fringe, shield emblem, turned pole, spear finial, plinth
        if slot == "cloth":
            fn = banner_fn(Wc, Lc, top, yc, 3, 0.02, ph, "point")
            sheet(p, fn, 6, 6, 0.006, "cloth")
            sheet(p, lambda u, v: Vector(fn(u, 0.92 + v * 0.08)) + Vector((0, -0.004, 0)), 6, 1, 0.004, "gold")
        elif slot == "hem":
            p.lathe([(rp * 1.3, 0), (rp, 0.08), (rp, Hp * 0.5), (rp * 1.3, Hp * 0.52), (rp, Hp * 0.54), (rp * 0.9, Hp)], mat="wood_dark", segs=8)
            p.cyl(0.012, 0.012, Wc * 1.2, M(loc=(-Wc * 0.6, yc, Hc), rot=(0, 90, 0)), mat="wood_dark", segs=6)
            for s in (-1, 1):
                p.ball(0.02, T(s * Wc * 0.6, yc, Hc), mat="brass", segs=(5, 3))
            p.lathe([(rp, Hp), (rp * 1.4, Hp + 0.02), (rp * 0.4, Hp + 0.04), (rp * J(p, 1.5, 0.15), Hp + 0.08), (0, Hp + 0.17)], mat="brass", segs=6)
            p.box((0.22, 0.22, 0.08), T(0, 0, 0.04), mat="stone", bevel=0.15, bevel_seg=1)
        else:
            z = top - Lc * J(p, 0.35, 0.12)
            y = yc - 0.04
            p.plate([(-0.12, 0.1), (0.12, 0.1), (0.12, -0.02), (0, -0.14), (-0.12, -0.02)], 0.008, T(0, y, z), mat="paint")
            p.plate([(-0.035, 0.06), (0.035, 0.06), (0.05, -0.02), (0, -0.08), (-0.05, -0.02)], 0.006, T(0, y - 0.006, z), mat="gold", bevel=0)
    elif e == "Industrial":  # printed vinyl banner: steel pipe pole, ball finial, printed stripes, bottom weight bar, base disc
        if slot == "cloth":
            fn = banner_fn(Wc, Lc, top, yc, 4, 0.01, ph, "flat")
            sheet(p, fn, 6, 5, 0.005, "cloth")
            for v0 in (0.12, J(p, 0.75, 0.05)):
                sheet(p, lambda u, v: Vector(fn(u, v0 + v * 0.07)) + Vector((0, -0.004, 0)), 3, 1, 0.004, "paint")
            b = fn(0.5, 1.0)
            p.cyl(0.01, 0.01, Wc * 1.02, M(loc=(-Wc * 0.51, b[1], b[2] - 0.005), rot=(0, 90, 0)), mat="steel", segs=6)
        elif slot == "hem":
            p.cyl(rp, rp, Hp, mat="steel", segs=8)
            p.ball(rp * 1.8, T(0, 0, Hp + rp), mat="steel", segs=(8, 5))
            p.cyl(0.01, 0.01, Wc * 1.1, M(loc=(-Wc * 0.55, yc, Hc), rot=(0, 90, 0)), mat="steel", segs=6)
            p.cyl(J(p, 0.16, 0.1), 0.15, 0.03, mat="iron", segs=10)
            p.tube([(rp, 0, 0.05), (rp + 0.005, 0, Hp * 0.6), (rp, 0, Hp)], 0.002, mat="rope", segs=3)
        else:
            z = top - Lc * 0.45
            R = J(p, 0.1, 0.12)
            p.cyl(R, R, 0.006, M(loc=(0, yc - 0.022, z), rot=(90, 0, 0)), mat="bone", segs=12)
            p.plate([(0, R * 0.7), (R * 0.2, R * 0.2), (R * 0.65, 0.0), (R * 0.2, -R * 0.2), (0, -R * 0.7), (-R * 0.2, -R * 0.2),
                     (-R * 0.65, 0), (-R * 0.2, R * 0.2)], 0.006, T(0, yc - 0.028, z), mat="paint", bevel=0)
    elif e == "Steampunk":  # brass-boned standard: scalloped cloth stiffened by brass ribs, gear finial, tripod foot
        if slot == "cloth":
            fn = banner_fn(Wc, Lc, top, yc, 3, 0.022, ph, "tails")
            sheet(p, fn, 6, 6, 0.006, "leather")
            for u in (0.18, 0.5, 0.82):
                p.tube([Vector(fn(u, v)) + Vector((0, -0.006, 0)) for v in (0.0, 0.33, 0.66, 0.85)], 0.004, mat="brass", segs=3)
        elif slot == "hem":
            p.cyl(rp, rp, Hp, mat="brass", segs=8)
            p.band(rp, Hp * J(p, 0.5, 0.2), h=0.04)
            p.cyl(0.012, 0.012, Wc * 1.2, M(loc=(-Wc * 0.6, yc, Hc), rot=(0, 90, 0)), mat="copper", segs=6)
            for k in range(3):
                a = ph + k * math.tau / 3
                p.tube([(0, 0, 0.32), (math.cos(a) * J(p, 0.22, 0.1), math.sin(a) * 0.22, 0.0)], 0.009, mat="brass", segs=4)
        else:
            R = J(p, 0.05, 0.12)
            teeth = []
            for k in range(20):
                a = k * math.tau / 20
                rr = R * (1.0 if k % 2 else 0.82)
                teeth.append((math.cos(a) * rr, math.sin(a) * rr))
            p.plate(teeth, 0.01, T(0, 0, Hp + R), mat="brass", bevel=0)
            p.cyl(R * 0.35, R * 0.35, 0.016, M(loc=(0, 0.008, Hp + R), rot=(90, 0, 0)), mat="copper", segs=8)
    elif e == "Future":  # hologram standard: tapered shell mast, emitter arm, rigid glassy panel, bottom emitter bar
        if slot == "cloth":
            fn = banner_fn(Wc, Lc, top, yc - 0.01, 2, 0.008, ph, "flat")
            sheet(p, fn, 4, 4, 0.004, "glass")
            b = fn(0.5, 1.0)
            p.box((Wc * 1.02, 0.02, 0.02), T(0, b[1], b[2] - 0.01), mat="shell_dark", bevel=0.3)
        elif slot == "hem":
            p.lathe([(0.14, 0), (0.16, 0.02), (0.1, 0.05), (rp * 1.6, 0.1), (rp, Hp * 0.6), (rp * 0.8, Hp)], mat="shell", segs=8)
            p.box((Wc * 1.15, 0.05, 0.03), T(0, yc - 0.01, Hc + 0.015), mat="shell_dark", bevel=0.3, bevel_seg=1)
            p.ball(rp * J(p, 1.6, 0.15), T(0, 0, Hp), mat="shell", segs=(8, 5))
        else:
            z = top - Lc * J(p, 0.45, 0.1)
            y = yc - 0.03
            p.plate([(0, 0.09), (0.08, -0.05), (-0.08, -0.05)], 0.006, T(0, y, z), mat="shell_dark", bevel=0)
            p.ring(0.035, 0.005, M(loc=(0, y - 0.006, z - 0.005), rot=(90, 0, 0)), mat="shell", segs=10)
    elif e == "Wasteland":  # rag standard: bent pipe pole in a tyre, rebar crossbar wired on, torn patched tarp, hanging junk
        if slot == "cloth":
            fn = banner_fn(Wc, Lc, top, yc, 3, 0.025, ph, "torn")
            sheet(p, fn, 6, 6, 0.006, "cloth")
            for k in range(p.rng.randint(2, 3)):
                u0, v0 = p.rng.uniform(0.05, 0.6), p.rng.uniform(0.1, 0.6)
                sheet(p, lambda u, v, u0=u0, v0=v0: Vector(fn(u0 + u * 0.3, v0 + v * 0.22)) + Vector((0, -0.005, 0)), 1, 1, 0.004,
                      ("paint", "rust", "leather")[k])
        elif slot == "hem":
            p.tube([(0, 0, 0), (0.0, 0, Hp * 0.5), (J(p, 0.04, 0.4), 0.02, Hp * 0.85), (0.05, 0.03, Hp)], rp, mat="rust", segs=6)
            p.tube([(-Wc * 0.62, yc, Hc + 0.01), (Wc * 0.62, yc, Hc - 0.02)], 0.007, mat="iron", segs=4)
            for i in range(2):
                p.ring(rp * 1.3, 0.003, M(loc=(0, 0, Hc + (i - 0.5) * 0.02), rot=(p.rng.uniform(-15, 15), 0, 0)), mat="iron", segs=6)
            p.ring(0.17, 0.06, M(loc=(0, 0, 0.06), scale=(1, 1, 0.9)), mat="rubber", segs=10, square=False)
        else:
            for s in (-1, 1):
                x = s * Wc * 0.55
                drop = J(p, 0.16, 0.25)
                p.tube([(x, yc, Hc), (x, yc, Hc - drop)], 0.002, mat="iron", segs=3)
                p.cyl(0.025, 0.025, 0.06, T(x, yc, Hc - drop - 0.06), mat="steel", segs=7)
    else:  # Ancient: stone pillar, stone crossbeam, three hanging stone slabs with rune slots, gold sun disc
        if slot == "cloth":
            n = 3
            h = (Lc - 0.04 * (n - 1)) / n
            for i in range(n):
                z = top - i * (h + 0.04) - h / 2
                p.box((Wc * (1 - 0.08 * i), 0.03, h), M(loc=(0, yc - 0.02, z), rot=(0, 0, p.rng.uniform(-2, 2) * i)), mat="stone",
                      bevel=0.15, bevel_seg=1)
                p.box((0.012, 0.006, h * 0.6), T(0, yc - 0.037, z), mat="glow", bevel=0)
                if i:
                    for s in (-1, 1):
                        p.tube([(s * Wc * 0.3, yc - 0.02, z + h / 2 - 0.005), (s * Wc * 0.3, yc - 0.02, z + h / 2 + 0.045)], 0.005,
                               mat="gold", segs=4)
        elif slot == "hem":
            p.cyl(rp * 1.15, rp, Hp, mat="stone", segs=6)
            p.box((Wc * 1.25, 0.07, 0.07), T(0, yc - 0.02, Hc + 0.025), mat="stone", bevel=0)
            p.box((0.24, 0.24, 0.12), T(0, 0, 0.06), mat="stone_dark", bevel=0.2, bevel_seg=1)
            p.ball(rp * J(p, 1.6, 0.12), M(loc=(0, 0, Hp + rp * 0.8), rot=(0, 0, 22)), mat="gold", segs=(4, 2))
        else:
            R = J(p, 0.08, 0.12)
            z = top - (Lc - 0.08) / 3 / 2
            p.cyl(R, R, 0.01, M(loc=(0, yc - 0.04, z), rot=(90, 0, 0)), mat="gold", segs=10)
            p.ring(R * 0.6, 0.004, M(loc=(0, yc - 0.046, z), rot=(90, 0, 0)), mat="glow", segs=10)
