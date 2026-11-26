"""Hafted hand tools: Sickle, Shovel, Pitchfork, Saw, Hatchet, Chisel, Wrench, Broom (cosmos_chimera P1-19, ADR-0016).

Same frame as kit_forms' Hoe/Hammer/Pickaxe: the grip end sits at the origin, the haft runs up +Z to z = L, the head
seats on its top and works toward -Y. Long tools (shovel, pitchfork, broom) stand on that end through the hand or lean
on a wall head-up; short ones (sickle, saw, chisel, wrench, hatchet) are held about 12 % up from it.
Haft length and radius are frame values (F, drawn first and in this order), so every head, joint and butt variant
meets every haft variant; head-only proportions use J.
"""
import math

from mathutils import Matrix, Vector

from kit_forms import F, HAFTED, J, butt, coin, function, haft, joint
from kit_lib import M

# Plate outlines given as (y, z) land in the YZ plane (thickness along X): blades seen side-on, like the pick.
SIDE = M(rot=(0, 0, 90))


def rod(p, a, b, r1, r2=None, mat="metal", segs=6, **kw):
    """Cone/cylinder from point a to point b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    m = Matrix.Translation(a) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    return p.cyl(r1, r1 if r2 is None else r2, d.length, m, mat=mat, segs=segs, **kw)


def side(p, pts, t, mat="metal", x=0.0, **kw):
    kw.setdefault("bevel", 0)
    return p.plate(pts, t, Matrix.Translation((x, 0, 0)) @ SIDE, mat=mat, **kw)


def front(p, pts, t, mat="metal", m=None, **kw):
    """(x, z) outline in the XZ plane facing -Y, thickness along Y."""
    kw.setdefault("bevel", 0)
    return p.plate(pts, t, m or Matrix(), mat=mat, **kw)


def disk(p, c, R, t, axis, mat, segs=10, **kw):
    """Cylinder of thickness t centred on c, its axis along 'x' or 'y'."""
    rot = (0, 90, 0) if axis == "x" else (90, 0, 0)
    return p.cyl(R, R, t, Matrix.Translation(c) @ M(rot=rot) @ Matrix.Translation((0, 0, -t / 2)), mat=mat, segs=segs, **kw)


def reshape(faces, fn):
    for v in {v for f in faces for v in f.verts}:
        fn(v.co)


def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


def collar(p, L, r, h, mat="metal", k=1.3, segs=8, up=0.3):
    """Socket/ferrule around the haft top: h tall, up*h of it above z = L."""
    return p.cyl(r * k, r * k * 0.93, h, Matrix.Translation((0, 0, L - h * (1 - up))), mat=mat, segs=segs)


def stone_collar(p, L, r, h=0.05):
    """Ancient: the head grows out of the haft through a seamless flared stone sleeve."""
    p.lathe([(r * 1.08, L - h), (r * 1.4, L - h * 0.4), (r * 1.55, L), (r * 1.2, L + h * 0.3)], mat="stone", segs=6)


def _haft(p, L, r):
    # kit_forms' Primal stick wobbles by a fixed few cm, a zigzag on a hand-length grip: short ones bend gently.
    if p.era == "Primal" and L < 0.4:
        w = [J(p, 0.004, 0.6) * (1 if i % 2 else -1) for i in range(4)]
        p.tube([(w[0], 0, 0), (w[1], w[2], L * 0.35), (w[3], 0, L * 0.7), (0, 0, L)], r, mat="body", segs=6)
        return
    # kit_forms' Wasteland haft tilts per variant, which walks a long haft's top off the head; scrap pipe stays straight.
    if p.era != "Wasteland":
        haft(p, L, r)
        return
    p.cyl(r * 0.85, r * 0.85, L, mat="body", segs=7)
    for _ in range(p.rng.randint(1, 3)):
        z = p.rng.uniform(0.04, 0.6) * L
        p.cyl(r * 1.02, r * 1.02, L * J(p, 0.08, 0.3), Matrix.Translation((0, 0, z)), mat="grip", segs=7)
    if coin(p):
        p.box((r * 1.2, r * 0.3, L * 0.12), Matrix.Translation((0, -r * 0.85, L * p.rng.uniform(0.3, 0.7))), mat="paint", bevel=0)


def _butt(p, r):
    # kit_forms' Industrial cap is a plain cylinder that morph cannot vary (it has no mid-height ring).
    if p.era != "Industrial":
        butt(p, r)
        return
    h = r * J(p, 1.4, 0.3)
    p.cyl(r * J(p, 1.12, 0.06), r * 1.05, h, Matrix.Translation((0, 0, -h * 0.65)), mat="rubber", segs=8)


def tool(L0, r0, head, sl=0.08):
    """Hafted form with a frame-drawn haft length (per-era table or one value) and radius."""
    def form(p, slot):
        L = F(p, L0[p.era] if isinstance(L0, dict) else L0, sl)
        r = F(p, r0, 0.08)
        if slot == "haft":
            _haft(p, L, r)
        elif slot == "joint":
            joint(p, L, r)
        elif slot == "butt":
            _butt(p, r)
        else:
            head(p, L, r)
    return form


# ---------------------------------------------------------------- sickle
def _crescent(base, R, w0, a0, a1, n=9, tip=0.12, teeth=0.0, jag=None):
    """Sickle blade outline (y, z): an arc that leaves the root at angle a0 (deg), bows up and forward (-Y) and
    hooks back down at a1; the inner (cutting) edge faces the centre. teeth > 0 serrates it; jag(i) nicks it."""
    a0r = math.radians(a0)
    c = (base[0] - R * math.cos(a0r), base[1] - R * math.sin(a0r))
    outer, inner = [], []
    for i in range(n):
        t = i / (n - 1)
        a = math.radians(a0 + (a1 - a0) * t)
        w = w0 * (1 - t) + w0 * tip * t
        ri = R - w - (teeth if (teeth and i % 2 and 0 < i < n - 1) else 0) - (jag(i) if jag else 0)
        outer.append((c[0] + R * math.cos(a), c[1] + R * math.sin(a)))
        inner.append((c[0] + ri * math.cos(a), c[1] + ri * math.sin(a)))
    return outer + inner[::-1], c


def gear(p, c, R, t, teeth, mat, axis="x"):
    disk(p, c, R, t, axis, mat, segs=teeth)
    for i in range(teeth):
        a = i * math.tau / teeth
        if axis == "x":
            loc = (c[0], c[1] + math.cos(a) * R, c[2] + math.sin(a) * R)
            p.box((t, R * 0.32, R * 0.32), M(loc=loc, rot=(math.degrees(a), 0, 0)), mat=mat, bevel=0)
        else:
            loc = (c[0] + math.cos(a) * R, c[1], c[2] + math.sin(a) * R)
            p.box((R * 0.32, t, R * 0.32), M(loc=loc, rot=(0, -math.degrees(a), 0)), mat=mat, bevel=0)


def _sickle_head(p, L, r):
    e = p.era
    R = J(p, 0.15, 0.1)
    w0 = J(p, 0.034, 0.15)
    a1 = J(p, 205, 0.04)
    base = (w0 * 0.45, L + 0.012)
    if e == "Primal":
        # Curved wooden holder with flint chips set in a row along its inner edge.
        _, c = _crescent(base, R, w0, 15, a1)
        Rm = R - 0.012
        pts = [(0, c[0] + Rm * math.cos(math.radians(a)), c[1] + Rm * math.sin(math.radians(a))) for a in (15, 60, 105, 150, a1)]
        pts[0] = (0, 0, L - 0.01)
        p.tube(pts, J(p, 0.012, 0.15), mat="body", segs=5)
        for i in range(p.rng.randint(4, 5)):
            a = math.radians(55 + i * 30 + p.rng.uniform(-6, 6))
            d = math.radians(9)
            ri = Rm - J(p, 0.03, 0.3)
            tri = [(c[0] + (Rm - 0.006) * math.cos(a - d), c[1] + (Rm - 0.006) * math.sin(a - d)),
                   (c[0] + ri * math.cos(a), c[1] + ri * math.sin(a)),
                   (c[0] + (Rm - 0.006) * math.cos(a + d), c[1] + (Rm - 0.006) * math.sin(a + d))]
            side(p, tri, 0.006, mat="stone_dark")
        p.band(r * 1.5, L - 0.01, h=0.035)
        return
    if e == "Future":
        p.box((0.03, 0.05, 0.05), Matrix.Translation((0, -0.004, L + 0.005)), mat="body", bevel_seg=1)
        p.box((0.034, 0.012, 0.03), Matrix.Translation((0, -0.03, L + 0.012)), mat="shell_dark", bevel=0)
        pts, _ = _crescent((0.0, L + 0.025), J(p, 0.14, 0.1), 0.012, 20, a1, n=8, tip=0.3)
        side(p, pts, 0.003, mat="glow")
        return
    if e == "Ancient":
        stone_collar(p, L, r)
        pts, _ = _crescent(base, R, w0 * 1.15, 15, a1 - 10, n=6, tip=0.25)
        side(p, pts, 0.012, mat="stone", bevel=0.15)
        glow, _ = _crescent((base[0] - w0 * 0.6, base[1] - w0 * 0.15), R - w0 * 0.6, w0 * 0.2, 18, a1 - 20, n=4, tip=0.5)
        side(p, glow, 0.0135, mat="glow")
        return
    if e == "Wasteland":
        # Cut from a scrap saw blade: nicked edge, wired and bolted onto the pipe.
        nick = [p.rng.uniform(0, 0.007) for _ in range(11)]
        pts, _ = _crescent(base, R, w0 * 1.1, 15, a1 - 15, n=11, tip=0.3, jag=lambda i: nick[i])
        side(p, pts, 0.004, mat="metal")
        p.band(r * 1.3, L - 0.01, h=0.04)
        rod(p, (-r * 1.6, 0, L - 0.005), (r * 1.6, 0, L - 0.005), 0.004, mat="steel", segs=6)
        if coin(p):
            side(p, [(0.015, L + 0.04), (-0.02, L + 0.07), (-0.01, L + 0.1), (0.02, L + 0.08)], 0.005, mat="paint")
        return
    teeth = 0.0
    n = 9
    mat = "iron"
    if e == "Mercantile":
        teeth, n = 0.005, 15
    elif e == "Industrial":
        R, w0, a1, mat = J(p, 0.16, 0.08), J(p, 0.028, 0.1), J(p, 180, 0.04), "steel"
    elif e == "Steampunk":
        R, a1 = J(p, 0.11, 0.1), J(p, 228, 0.03)
    pts, _ = _crescent((w0 * 0.45, L + 0.012), R, w0, 15, a1, n=n, teeth=teeth)
    side(p, pts, 0.004, mat=mat)
    if e == "Agrarian":
        collar(p, L, r, J(p, 0.05, 0.2), mat="iron")
    elif e == "Mercantile":
        collar(p, L, r, 0.045, mat="brass")
        p.ring(r * 1.32, 0.004, Matrix.Translation((0, 0, L - 0.03)), mat="brass", segs=10, square=False)
    elif e == "Industrial":
        collar(p, L, r, J(p, 0.06, 0.2), mat="paint", k=1.25)
        for z in (L - 0.012, L - 0.035):
            rod(p, (-r * 1.35, 0, z), (r * 1.35, 0, z), 0.003, mat="steel", segs=6)
    else:  # Steampunk: harvest hook driven through a brass gear at the root
        collar(p, L, r, 0.04, mat="copper")
        gear(p, (0, 0, L + 0.012), J(p, 0.026, 0.12), 0.01, 8, "brass")
        p.ball(0.006, Matrix.Translation((0.007, 0, L + 0.012)), mat="glow", segs=(6, 4))


# ---------------------------------------------------------------- shovel
def _shovel_outline(kind, W, H, z0):
    w = W / 2
    if kind == "square":
        return [(-w, z0), (w, z0), (w * 1.03, z0 + H), (-w * 1.03, z0 + H)]
    if kind == "round":
        pts = [(-w, z0), (w, z0), (w, z0 + H * 0.55)]
        for i in range(1, 6):
            a = i * math.pi / 6
            pts.append((w * math.cos(a), z0 + H * 0.55 + H * 0.45 * math.sin(a)))
        return pts + [(-w, z0 + H * 0.55)]
    return [(-w, z0), (w, z0), (w * 0.96, z0 + H * 0.58), (w * 0.4, z0 + H * 0.9), (0, z0 + H),
            (-w * 0.4, z0 + H * 0.9), (-w * 0.96, z0 + H * 0.58)]


def _shovel_head(p, L, r):
    e = p.era
    W = J(p, 0.22, 0.1)
    H = J(p, 0.28, 0.1)
    z0 = L + 0.045
    if e == "Primal":
        # Shoulder blade lashed onto the stick end: narrow joint end down, its spine ridge facing out.
        z = L - 0.06
        out = [(-0.022, z), (-0.085 * W / 0.22, z + 0.16), (-0.1 * W / 0.22, z + H * 0.9), (0.0, z + H), (0.11 * W / 0.22, z + H * 0.8),
               (0.07, z + 0.1), (0.022, z)]
        front(p, out, 0.012, mat="bone", m=Matrix.Translation((0, -r * 1.3, 0)))
        side(p, [(-r * 1.3, z + 0.03), (-r * 1.3 - 0.022, z + 0.1), (-r * 1.3 - 0.01, z + H * 0.85), (-r * 1.3, z + H * 0.85)], 0.008, mat="bone", x=0.012)
        p.band(r * 1.8, L - 0.02, h=0.04)
        return
    if e == "Agrarian":
        # Wooden blade shod with an iron edge.
        front(p, _shovel_outline("square", W * 0.9, H * 0.9, z0 - 0.02), 0.018, mat="body", bevel=0.05)
        zt = z0 - 0.02 + H * 0.9
        front(p, [(-W * 0.47, zt - 0.03), (W * 0.47, zt - 0.03), (W * 0.47, zt + 0.006), (-W * 0.47, zt + 0.006)], 0.022, mat="iron")
        p.box((0.014, 0.004, 0.17), Matrix.Translation((0, -0.0115, L - 0.03)), mat="iron", bevel=0)
        collar(p, L, r, 0.07, mat="body", k=1.25, up=0.4)
        return
    if e == "Future":
        # Folding nano spade: hinge across the neck, two shell leaves meeting at a glowing seam.
        disk(p, (0, 0, z0), 0.012, W * 0.5, "x", "shell_dark", segs=8)
        collar(p, L, r, 0.06, mat="body", k=1.2, up=0.6)
        lo = [(-W / 2, z0), (W / 2, z0), (W / 2, z0 + H * 0.48), (-W / 2, z0 + H * 0.48)]
        front(p, lo, 0.006, mat="body", m=Matrix.Translation((0, -0.01, 0)), bevel=0.1, bevel_seg=1)
        front(p, [(-W * 0.48, z0 + H * 0.5), (W * 0.48, z0 + H * 0.5), (W * 0.46, z0 + H * 0.62), (W * 0.19, z0 + H * 0.9),
                  (0, z0 + H), (-W * 0.19, z0 + H * 0.9), (-W * 0.46, z0 + H * 0.62)], 0.006, mat="body",
              m=Matrix.Translation((0, -0.01, 0.006)), bevel=0.1, bevel_seg=1)
        p.box((W * 0.92, 0.008, 0.004), Matrix.Translation((0, -0.01, z0 + H * 0.49 + 0.003)), mat="glow", bevel=0)
        if coin(p):
            p.box((0.006, 0.008, H * 0.35), Matrix.Translation((0, -0.0105, z0 + H * 0.25)), mat="glow", bevel=0)
        return
    if e == "Wasteland":
        # Blade cut from a painted drum lid / sign plate, bolted onto a squashed pipe end.
        k = [p.rng.uniform(-0.02, 0.02) for _ in range(5)]
        out = [(-W / 2 + k[0], z0), (W / 2 + k[1], z0), (W / 2 + k[2], z0 + H * 0.8), (W * 0.2, z0 + H + k[3]),
               (-W / 2 + k[4], z0 + H * 0.85)]
        front(p, out, 0.004, mat="paint", m=Matrix.Translation((0, -0.012, 0)))
        front(p, [(-W * 0.3, z0 + H * 0.3), (W * 0.1, z0 + H * 0.25), (W * 0.15, z0 + H * 0.55), (-W * 0.25, z0 + H * 0.6)],
              0.005, mat="rust", m=Matrix.Translation((0, -0.0125, 0)))
        p.cyl(r * 1.2, r * 1.2, 0.12, M(loc=(0, -0.004, L - 0.06), scale=(1.25, 0.65, 1)), mat="rust", segs=7)
        for x in (-0.012, 0.012):
            rod(p, (x, -0.02, z0 + 0.02), (x, 0.012, z0 + 0.02), 0.005, mat="steel", segs=6)
        p.band(r * 1.35, L - 0.03, h=0.04)
        return
    if e == "Ancient":
        stone_collar(p, L, r, 0.07)
        out = [(-W * 0.22, z0 - 0.03), (W * 0.22, z0 - 0.03), (W * 0.52, z0 + H * 0.35), (W * 0.4, z0 + H * 0.78), (0, z0 + H),
               (-W * 0.4, z0 + H * 0.78), (-W * 0.52, z0 + H * 0.35)]
        front(p, out, 0.018, mat="stone", m=Matrix.Translation((0, -0.004, 0)), bevel=0.2, bevel_seg=1)
        for i in range(3):
            z = z0 + H * (0.25 + i * 0.2)
            p.box((W * (0.42 - i * 0.1), 0.004, 0.009), Matrix.Translation((0, -0.0135, z)), mat="glow", bevel=0)
        return
    kind = {"Mercantile": "round", "Industrial": "point", "Steampunk": "square"}[e]
    mat = {"Mercantile": "iron", "Industrial": "steel", "Steampunk": "iron"}[e]
    front(p, _shovel_outline(kind, W, H, z0), 0.005, mat=mat, m=Matrix.Translation((0, -0.008, 0)))
    # Frog: the raised spine where the socket runs into the blade.
    front(p, [(-W * 0.22, z0 - 0.005), (W * 0.22, z0 - 0.005), (0, z0 + H * J(p, 0.45, 0.2))], 0.006, mat=mat,
          m=Matrix.Translation((0, -0.004, 0)))
    if e == "Mercantile":
        collar(p, L, r, 0.1, mat="iron", k=1.25, up=0.5)
        for y in (-1, 1):
            p.box((0.012, 0.004, 0.16), Matrix.Translation((0, y * r * 1.15, L - 0.1)), mat="iron", bevel=0)
            p.ball(0.004, Matrix.Translation((0, y * r * 1.3, L - 0.13)), mat="brass", segs=(5, 3))
    elif e == "Industrial":
        collar(p, L, r, J(p, 0.13, 0.15), mat="paint", k=1.2, up=0.4)
        for x in (-1, 1):
            p.box((W * 0.4, 0.026, 0.005), Matrix.Translation((x * W * 0.28, 0.006, z0 + 0.002)), mat="steel", bevel=0)
        rod(p, (-r * 1.3, 0, L - 0.04), (r * 1.3, 0, L - 0.04), 0.003, mat="steel")
    else:  # Steampunk: hydraulic shovel, twin pistons drive the blade
        collar(p, L, r, 0.08, mat="brass", k=1.3, up=0.6)
        for x in (-0.032, 0.032):
            p.cyl(0.011, 0.011, 0.17, Matrix.Translation((x, 0.018, L - 0.2)), mat="brass", segs=8)
            rod(p, (x, 0.018, L - 0.03), (x * 0.8, 0.0, z0 + 0.06), 0.005, mat="steel", segs=6)
            p.cyl(0.0125, 0.0125, 0.006, Matrix.Translation((x, 0.018, L - 0.045)), mat="copper", segs=8)
        disk(p, (0, -0.022, L - 0.12), 0.017, 0.012, "y", "brass", segs=10)
        disk(p, (0, -0.029, L - 0.12), 0.012, 0.003, "y", "glow", segs=10)


# ---------------------------------------------------------------- pitchfork
def _tine(p, x, zb, ln, r, mat, curve=0.05, segs=5, y0=0.0, dx=0.0):
    a = (x, y0, zb)
    m = (x + dx * 0.5, y0 - curve * 0.25, zb + ln * 0.55)
    b = (x + dx, y0 - curve, zb + ln * 0.85)
    p.tube([a, m, b], r, mat=mat, segs=segs)
    rod(p, b, (x + dx * 1.1, y0 - curve * 1.3, zb + ln), r, r * 0.25, mat=mat, segs=segs)


def _fork_head(p, L, r):
    e = p.era
    ln = J(p, 0.3, 0.1)
    sp = J(p, 0.065, 0.12)
    if e == "Primal":
        # Forked branch: the stick splits into two (sometimes three) prongs.
        for s in (-1, 1):
            a = (0, 0, L - 0.04)
            p.tube([a, (s * sp * 0.7, -0.005, L + 0.1), (s * sp * J(p, 1.1, 0.15), -0.02, L + ln * 0.85)], 0.011, mat="body", segs=5)
            rod(p, (s * sp * 1.1, -0.02, L + ln * 0.85), (s * sp * 1.15, -0.035, L + ln * 1.05), 0.011, 0.003, mat="body", segs=5)
        if coin(p):
            rod(p, (0, 0, L - 0.01), (0.004, -0.02, L + ln * 0.5), 0.008, 0.003, mat="body", segs=5)
        return
    if e == "Agrarian":
        p.box((sp * 2.5, 0.028, 0.032), Matrix.Translation((0, 0, L + 0.03)), mat="body")
        for x in (-sp, 0, sp):
            _tine(p, x, L + 0.04, ln, 0.009, "body", curve=J(p, 0.05, 0.3), segs=5)
        rod(p, (-sp, 0, L + 0.09), (sp, 0, L + 0.09), 0.004, mat="rope", segs=4)
        collar(p, L, r, 0.06, mat="iron", k=1.2)
        return
    if e == "Mercantile":
        collar(p, L, r, 0.1, mat="iron", k=1.25, up=0.45)
        p.ring(r * 1.3, 0.005, Matrix.Translation((0, 0, L - 0.05)), mat="brass", segs=10, square=False)
        zb = L + 0.04
        _tine(p, 0, zb, ln + 0.02, 0.007, "iron", curve=0.04)
        for s in (-1, 1):
            pts = [(0, 0, zb - 0.01), (s * sp * 0.8, 0, zb + 0.025), (s * sp, -0.006, zb + 0.08)]
            p.tube(pts, 0.007, mat="iron", segs=5)
            _tine(p, s * sp, zb + 0.08, ln - 0.06, 0.007, "iron", curve=0.035)
        return
    if e == "Industrial":
        collar(p, L, r, J(p, 0.12, 0.15), mat="steel", k=1.2, up=0.5)
        rod(p, (-r * 1.3, 0, L - 0.02), (r * 1.3, 0, L - 0.02), 0.003, mat="steel")
        w = sp * 1.15
        p.box((w * 3.3, 0.012, 0.02), Matrix.Translation((0, 0, L + 0.05)), mat="steel", bevel=0)
        for x in (-1.5, -0.5, 0.5, 1.5):
            _tine(p, x * w, L + 0.055, ln, 0.0055, "steel", curve=J(p, 0.07, 0.2), segs=5)
        return
    if e == "Steampunk":
        # Telescoping fork: stacked brass sleeves slide out of the haft.
        z = L - 0.05
        for i, (k, h) in enumerate(((1.35, 0.11), (1.15, 0.08), (0.95, 0.06))):
            p.cyl(r * k, r * k, h, Matrix.Translation((0, 0, z)), mat="brass", segs=6)
            p.cyl(r * k * 1.06, r * k * 1.06, 0.006, Matrix.Translation((0, 0, z + h - 0.007)), mat="glow" if i == 1 else "copper", segs=6)
            z += h
        p.lathe([(r * 0.9, z - 0.005), (sp * 1.1, z + 0.02), (sp * 1.1, z + 0.035), (0, z + 0.04)], mat="brass", segs=6)
        for x in (-sp, 0, sp):
            _tine(p, x, z + 0.03, ln * 0.9, 0.0065, "iron", curve=0.04)
        return
    if e == "Future":
        # Electromagnetic grab fork: shell prongs ringed by glowing coils.
        p.box((sp * 2.6, 0.04, 0.05), Matrix.Translation((0, 0, L + 0.025)), mat="body", bevel_seg=1)
        for x in (-sp, 0, sp):
            zb = L + 0.05
            _tine(p, x, zb, ln * (1.0 if x else 0.85), 0.0085, "body", curve=0.03 if x else 0.0, segs=5, dx=x * 0.2)
            p.cyl(0.012, 0.012, 0.008, Matrix.Translation((x, 0, zb + 0.02)), mat="glow", segs=6)
        return
    if e == "Wasteland":
        # Rebar tines welded to a flat bar, none quite the same length.
        tilt = p.rng.uniform(-5, 5)
        p.box((sp * 2.8, 0.01, 0.022), M(loc=(0, 0, L + 0.045), rot=(0, tilt, 0)), mat="iron", bevel=0)
        n = p.rng.choice((3, 4))
        for i in range(n):
            x = (i - (n - 1) / 2) * sp * 2.4 / (n - 1)
            _tine(p, x, L + 0.05, ln * p.rng.uniform(0.75, 1.1), 0.0065, "rust" if i != 1 else "steel",
                  curve=p.rng.uniform(0.0, 0.08), dx=p.rng.uniform(-0.02, 0.02), segs=5)
        p.cyl(r * 1.2, r * 1.2, 0.07, Matrix.Translation((0, 0, L - 0.025)), mat="rust", segs=7)
        p.cyl(r * 1.3, r * 1.3, 0.02, M(loc=(0, 0, L - 0.02), rot=(p.rng.uniform(-8, 8), 0, 0)), mat="iron", segs=7)
        return
    # Ancient: stone trident with a rune-lit hub.
    stone_collar(p, L, r, 0.06)
    p.lathe([(r * 1.2, L), (sp * 1.3, L + 0.04), (sp * 1.2, L + 0.07), (sp * 0.5, L + 0.085)], mat="stone", segs=6)
    for x in (-sp, 0, sp):
        rod(p, (x * 1.05, 0, L + 0.05), (x * 1.15, -0.02, L + 0.06 + ln * (1.1 if x == 0 else 0.9)), 0.013, 0.003, mat="stone", segs=6)
    p.box((sp * 1.4, 0.006, 0.008), Matrix.Translation((0, -sp * 1.15, L + 0.05)), mat="glow", bevel=0)
    p.ring(r * 1.45, 0.003, Matrix.Translation((0, 0, L - 0.01)), mat="glow", segs=6)


# ---------------------------------------------------------------- saw
def _saw_outline(yb0, yb1, yf0, yf1, z0, z1, n, tooth, jag=None):
    """Blade along Z (y, z): straight back edge at +Y, toothed front edge at -Y."""
    pts = [(yb0, z0), (yb1, z1)]
    for i in range(2 * n + 1):
        t = i / (2 * n)
        z = z1 - (z1 - z0) * t
        yf = yf1 + (yf0 - yf1) * t
        d = tooth if i % 2 else 0
        if jag:
            d += jag(i)
        pts.append((yf - d, z))
    return pts


def _saw_head(p, L, r):
    e = p.era
    Lb = J(p, 0.38, 0.1)
    z0 = L - 0.01
    if e == "Primal":
        # Obsidian flake blade split into the stick, knapped edge.
        lb = J(p, 0.17, 0.15)
        nick = [p.rng.uniform(0, 0.005) for _ in range(13)]
        side(p, _saw_outline(0.012, 0.004, -0.02, -0.012, L - 0.04, L + lb, 6, 0.005, jag=lambda i: nick[i]), 0.008, mat="stone_dark")
        p.band(r * 1.5, L - 0.015, h=0.035)
        return
    if e == "Agrarian":
        # Frame saw: wooden arms and stretcher, twisted-cord tension, thin blade along the front.
        z1 = L + Lb
        for z in (L + 0.012, z1):
            p.box((0.022, 0.2, 0.026), Matrix.Translation((0, 0.07, z)), mat="body", bevel_seg=1)
        p.box((0.016, 0.016, Lb), Matrix.Translation((0, 0.075, L + 0.012 + Lb / 2 - 0.006)), mat="body", bevel_seg=1)
        for x in (-0.004, 0.004):
            rod(p, (x, 0.155, L + 0.012), (x, 0.155, z1), 0.0035, mat="rope", segs=4)
        p.box((0.006, 0.05, 0.008), M(loc=(0, 0.13, L + Lb * J(p, 0.5, 0.2)), rot=(J(p, 15, 0.8), 0, 0)), mat="body", bevel=0)
        side(p, _saw_outline(0.0, 0.0, -0.02, -0.02, L + 0.0, z1 + 0.005, 13, 0.004), 0.0015, mat="iron")
        return
    if e == "Mercantile":
        side(p, _saw_outline(J(p, 0.06, 0.15), 0.02, -0.034, -0.028, z0, L + Lb, 15, 0.0045), 0.0015, mat="steel")
        for y, z in ((0.03, L + 0.01), (0.0, L + 0.025), (0.035, L + 0.04)):
            rod(p, (-0.004, y, z), (0.004, y, z), 0.005, mat="brass", segs=6)
        collar(p, L, r, 0.03, mat="brass", k=1.2)
        return
    if e == "Industrial":
        # Hacksaw: painted steel bow behind a thin blade, wing nut at the toe.
        z1 = L + Lb * 0.85
        p.tube([(0, 0.0, L - 0.005), (0, 0.07, L + 0.012), (0, J(p, 0.08, 0.1), z1 - 0.01), (0, 0.0, z1 + 0.01)], 0.0055, mat="paint", segs=6)
        side(p, _saw_outline(0.0, 0.0, -0.012, -0.012, L, z1, 12, 0.003), 0.0012, mat="steel")
        p.box((0.004, 0.022, 0.01), Matrix.Translation((0, 0.0, z1 + 0.012)), mat="steel", bevel=0)
        rod(p, (0, 0, z1 + 0.005), (0, 0, z1 + 0.017), 0.004, mat="steel")
        collar(p, L, r, 0.025, mat="paint", k=1.15)
        return
    if e == "Steampunk":
        # Clockwork chainsaw: brass spring housing, winding key, guide bar wrapped in a toothed chain.
        p.box((0.05, 0.08, 0.1), Matrix.Translation((0, 0.012, L + 0.045)), mat="brass", bevel_seg=1)
        rod(p, (0.025, 0.02, L + 0.06), (0.05, 0.02, L + 0.06), 0.004, mat="steel")
        p.box((0.005, 0.03, 0.018), Matrix.Translation((0.052, 0.02, L + 0.06)), mat="brass", bevel=0)
        zb = L + 0.08
        z1 = zb + Lb * 0.75
        bar = [(0.018, zb), (0.018, z1)] + [(0.018 * math.cos(a), z1 + 0.018 * math.sin(a)) for a in (0.8, 1.57, 2.35)] + [(-0.018, z1), (-0.018, zb)]
        side(p, bar, 0.007, mat="iron")
        side(p, _saw_outline(0.022, 0.022, -0.022, -0.022, zb + 0.005, z1 + 0.012, 9, 0.006), 0.004, mat="steel")
        disk(p, (0, -0.029, L + 0.05), 0.013, 0.004, "y", "glow", segs=10)
        p.tube([(0.02, 0.05, L + 0.02), (0.03, 0.06, L - 0.03), (0.0, r * 1.1, L - 0.06)], 0.004, mat="copper", segs=5)
        return
    if e == "Future":
        # Hot-wire cutter: shell C-bow, glowing wire strung between its tips.
        z1 = L + Lb * 0.75
        bow = [(-0.012, L - 0.01), (0.075, L + 0.015), (0.085, z1 - 0.02), (-0.012, z1 + 0.012), (-0.012, z1 - 0.012),
               (0.06, z1 - 0.03), (0.055, L + 0.035), (-0.012, L + 0.02)]
        side(p, bow, 0.014, mat="body", bevel=0.12)
        for z in (L + 0.015, z1):
            p.box((0.016, 0.012, 0.014), Matrix.Translation((0, -0.018, z)), mat="shell_dark", bevel=0)
        rod(p, (0, -0.02, L + 0.02), (0, -0.02, z1), 0.0022, mat="glow", segs=5)
        p.box((0.0145, 0.004, (z1 - L) * 0.6), Matrix.Translation((0, 0.08, (L + z1) / 2)), mat="glow", bevel=0)
        return
    if e == "Wasteland":
        # Scrap bow saw: bent rebar bow, crude blade wired on at both ends.
        z1 = L + Lb
        bend = J(p, 0.1, 0.2)
        p.tube([(0, 0, L), (0, bend * 0.8, L + Lb * 0.15), (0, bend, L + Lb * 0.5), (0, bend * 0.8, L + Lb * 0.85), (0, 0, z1)], 0.006, mat="rust", segs=5)
        side(p, _saw_outline(0.0, 0.0, -0.016, -0.016, L, z1, 8, 0.006), 0.0015, mat="steel")
        for z in (L + 0.005, z1 - 0.005):
            p.ring(0.008, 0.002, M(loc=(0, -0.004, z), rot=(0, 90, 0)), mat="iron", segs=8)
        if coin(p):
            p.box((0.012, 0.01, 0.04), Matrix.Translation((0, bend, L + Lb * 0.5)), mat="cloth", bevel=0)
        return
    # Ancient: stone blade, scalloped edge, rune line along the spine.
    stone_collar(p, L, r, 0.04)
    z1 = L + Lb * 0.8
    side(p, _saw_outline(0.035, 0.02, -0.02, -0.016, L - 0.01, z1, 5, 0.008), 0.01, mat="stone", bevel=0.1)
    p.box((0.0115, 0.005, (z1 - L) * 0.75), Matrix.Translation((0, 0.015, L + (z1 - L) * 0.45)), mat="glow", bevel=0)


# ---------------------------------------------------------------- hatchet
def _axe_outline(back, edge, top, bot, beard, zc, double=False):
    """Axe head (y, z) around the eye at (0, zc): poll at +back, edge at -edge, beard drops the lower heel."""
    if double:
        return [(edge * 0.25, zc + 0.022), (edge, zc + top), (edge * 1.04, zc), (edge, zc - top),
                (edge * 0.25, zc - 0.022), (-edge * 0.25, zc - 0.022), (-edge, zc - top), (-edge * 1.04, zc),
                (-edge, zc + top), (-edge * 0.25, zc + 0.022)]
    return [(back, zc + 0.024), (-edge * 0.3, zc + 0.024), (-edge, zc + top), (-edge * 1.03, zc + top * 0.2),
            (-edge, zc - bot), (-edge * 0.82, zc - bot - beard * 0.3), (-edge * 0.35, zc - 0.026), (back, zc - 0.024)]


def taper_axe(faces, f_edge=0.22, start=0.02, span=0.12, double=False):
    def fn(co):
        d = abs(co.y) if double else -co.y
        co.x *= lerp(1.0, f_edge, (d - start) / span)
    reshape(faces, fn)


def _hatchet_head(p, L, r):
    e = p.era
    zc = L - 0.035
    edge = J(p, 0.15, 0.1)
    top = J(p, 0.05, 0.15)
    bot = J(p, 0.05, 0.2)
    if e == "Primal":
        p.ball(0.03, M(loc=(0, -0.035, zc), scale=(0.9, J(p, 2.6, 0.12), 1.5)), mat="stone", segs=(8, 6), noise=0.08)
        p.band(r * 1.6, zc - 0.03, h=0.03)
        p.ring(r * 1.8, 0.004, M(loc=(0, 0, zc), rot=(35, 0, 0)), mat="rope", segs=8)
        return
    if e == "Future":
        p.box((0.032, 0.07, 0.06), Matrix.Translation((0, 0.005, zc)), mat="body", bevel_seg=1)
        blade = [(-0.03, zc + 0.022), (-edge, zc + top), (-edge * 1.05, zc), (-edge, zc - bot), (-0.03, zc - 0.022)]
        side(p, blade, 0.004, mat="glow")
        side(p, [(-0.03, zc + 0.026), (-0.05, zc + 0.03), (-0.05, zc - 0.03), (-0.03, zc - 0.026)], 0.012, mat="shell_dark")
        p.box((0.034, 0.006, 0.03), Matrix.Translation((0, 0.04, zc)), mat="glow", bevel=0)
        return
    if e == "Wasteland":
        k = [p.rng.uniform(-0.012, 0.012) for _ in range(6)]
        out = [(0.03 + k[0], zc + 0.03), (-edge * 0.5, zc + 0.035 + k[1]), (-edge + k[2], zc + top), (-edge - 0.01, zc + k[3]),
               (-edge + k[4], zc - bot), (-0.02, zc - 0.03 + k[5])]
        side(p, out, 0.012, mat="metal")
        for z in (zc + 0.012, zc - 0.012):
            rod(p, (-0.01, 0.012, z), (0.01, 0.012, z), 0.004, mat="steel")
        p.band(r * 1.35, zc - 0.035, h=0.03)
        if coin(p):
            side(p, [(-0.06, zc - 0.01), (-0.1, zc - 0.02), (-0.1, zc + 0.02), (-0.06, zc + 0.025)], 0.0135, mat="paint")
        return
    if e == "Ancient":
        stone_collar(p, zc - 0.03, r, 0.04)
        out = [(0.04, zc + 0.02), (0.0, zc + 0.034), (-edge, zc + top + 0.01), (-edge * 1.06, zc), (-edge, zc - bot - 0.01),
               (0.0, zc - 0.034), (0.04, zc - 0.02)]
        f = side(p, out, 0.036, mat="stone", bevel=0.2)
        taper_axe(f, 0.35)
        p.box((0.018, 0.006, top + bot), Matrix.Translation((0, -edge * 0.72, zc)), mat="glow", bevel=0)
        p.ball(0.006, Matrix.Translation((0, 0.038, zc)), mat="glow", segs=(6, 4))
        return
    double = e == "Mercantile"
    beard = {"Agrarian": 0.05, "Mercantile": 0.0, "Industrial": 0.01, "Steampunk": 0.02}[e]
    mat = {"Agrarian": "iron", "Mercantile": "iron", "Industrial": "paint", "Steampunk": "iron"}[e]
    out = _axe_outline(0.03, edge if e != "Industrial" else edge * 0.62, top, bot, beard, zc, double)
    taper_axe(side(p, out, 0.032, mat=mat), double=double)
    if e == "Industrial":
        steel = [(-edge * 0.6, zc + top * 0.75), (-edge, zc + top), (-edge * 1.03, zc), (-edge, zc - bot), (-edge * 0.6, zc - bot * 0.75)]
        taper_axe(side(p, steel, 0.032, mat="steel"))
    elif e == "Mercantile":
        p.box((0.02, 0.008, 0.006), Matrix.Translation((0, 0, L + 0.001)), mat="brass", bevel=0)
    elif e == "Agrarian":
        p.ring(r * 1.25, 0.004, Matrix.Translation((0, 0, zc - 0.03)), mat="iron", segs=8)
    else:  # Steampunk: steam-driven axe, piston on the poll and a boiler canister behind the haft
        disk(p, (0, 0.06, zc), 0.019, 0.06, "y", "brass", segs=10)
        rod(p, (0, 0.09, zc), (0, 0.11, zc), 0.007, mat="steel")
        p.cyl(0.022, 0.022, 0.1, Matrix.Translation((0, 0.032, zc - 0.17)), mat="brass", segs=10)
        p.tube([(0, 0.032, zc - 0.07), (0, 0.06, zc - 0.05), (0, 0.065, zc - 0.02)], 0.004, mat="copper", segs=5)
        p.box((0.004, 0.008, 0.04), Matrix.Translation((0.022, 0.032, zc - 0.12)), mat="glow", bevel=0)


# ---------------------------------------------------------------- chisel
def _flat_bit(p, z0, z1, w0, w1, t, mat, bevel_len=0.02, y=0.0):
    f = front(p, [(-w0 / 2, z0), (w0 / 2, z0), (w1 / 2, z1), (-w1 / 2, z1)], t, mat=mat, m=Matrix.Translation((0, y, 0)))

    def grind(co):
        k = (co.z - (z1 - bevel_len)) / bevel_len
        if k > 0:
            co.y = y + (co.y - y) * lerp(1.0, 0.15, k) - t * 0.4 * k
    reshape(f, grind)


def _chisel_head(p, L, r):
    e = p.era
    Lb = J(p, 0.13, 0.12)
    w = J(p, 0.018, 0.2)
    z1 = L + Lb
    if e == "Primal":
        p.cyl(0.011, 0.005, Lb + 0.03, M(loc=(0, 0, L - 0.03), scale=(1.3, 0.6, 1)), mat="bone", segs=6)
        p.band(r * 1.5, L - 0.01, h=0.03)
        return
    if e == "Agrarian":
        collar(p, L, r, 0.03, mat="iron", k=1.15)
        _flat_bit(p, L - 0.01, z1, 0.01, w, 0.007, "iron")
        return
    if e == "Mercantile":
        # One of a carving set: the variant decides the tip (skew, V, gouge, knife).
        collar(p, L, r, 0.03, mat="brass", k=1.15)
        zs = L + Lb * 0.5
        rod(p, (0, 0, L - 0.01), (0, 0, zs), 0.0042, mat="steel", segs=6)
        kind = p.rng.randrange(4)
        tw = J(p, 0.012, 0.2)
        if kind == 0:
            front(p, [(-0.004, zs - 0.005), (0.004, zs - 0.005), (tw / 2, z1 - 0.012), (-tw / 2, z1)], 0.003, mat="steel")
        elif kind == 1:
            for s in (-1, 1):
                front(p, [(-0.004, zs - 0.005), (0.004, zs - 0.005), (0.004, z1), (-0.004, z1 - 0.008)], 0.0025, mat="steel",
                      m=M(loc=(s * 0.003, 0, 0), rot=(0, 0, s * 35)))
        elif kind == 2:
            for a in (-50, 0, 50):
                front(p, [(-0.0035, zs - 0.005), (0.0035, zs - 0.005), (0.004, z1), (-0.004, z1)], 0.0025, mat="steel",
                      m=M(loc=(math.sin(math.radians(a)) * 0.006, -math.cos(math.radians(a)) * 0.006 + 0.006, 0), rot=(0, 0, a)))
        else:
            front(p, [(-0.004, zs - 0.005), (0.004, zs - 0.005), (0.005, z1 - 0.02), (0.0, z1), (-0.003, z1 - 0.025)], 0.003, mat="steel")
        return
    if e == "Industrial":
        p.cyl(r * 1.2, r * 1.2, 0.012, Matrix.Translation((0, 0, L - 0.006)), mat="steel", segs=6)
        rod(p, (0, 0, L), (0, 0, L + 0.025), 0.005, 0.004, mat="steel")
        _flat_bit(p, L + 0.02, z1, w * 1.2, w * 1.35, 0.006, "steel", bevel_len=0.025)
        return
    if e == "Steampunk":
        # Vibrating chisel: coil housing, amber pulse slit, narrow bit.
        p.cyl(r * 1.25, r * 1.1, 0.06, Matrix.Translation((0, 0, L - 0.01)), mat="brass", segs=8)
        for z in (L + 0.005, L + 0.025):
            p.ring(r * 1.27, 0.003, Matrix.Translation((0, 0, z)), mat="copper", segs=8)
        p.box((0.004, 0.004, 0.02), Matrix.Translation((0, -r * 1.2, L + 0.04)), mat="glow", bevel=0)
        _flat_bit(p, L + 0.045, z1, 0.008, w * 0.8, 0.005, "steel")
        return
    if e == "Future":
        # Laser engraving pen: tapered shell, glowing tip.
        zt = L + Lb * 0.5
        p.cyl(r * 1.0, r * 0.45, zt - L, Matrix.Translation((0, 0, L)), mat="body", segs=8)
        p.ring(r * 0.85, 0.0025, Matrix.Translation((0, 0, L + (zt - L) * 0.35)), mat="glow", segs=8)
        p.cyl(r * 0.45, r * 0.3, 0.01, Matrix.Translation((0, 0, zt)), mat="shell_dark", segs=8)
        p.cyl(0.0035, 0.0, 0.014, Matrix.Translation((0, 0, zt + 0.01)), mat="glow", segs=6)
        return
    if e == "Wasteland":
        # Ground-down rebar or bolt, a hex nut for a ferrule.
        p.cyl(r * 1.25, r * 1.25, 0.012, Matrix.Translation((0, 0, L - 0.008)), mat="iron", segs=6)
        f = p.cyl(0.0065, 0.0065, Lb + 0.01, Matrix.Translation((0, 0, L - 0.01)), mat="metal", segs=6)
        reshape(f, lambda co: setattr(co, "y", co.y * lerp(1.0, 0.25, (co.z - (z1 - 0.03)) / 0.03)))
        return
    stone_collar(p, L, r, 0.03)
    p.cyl(0.01, 0.0045, Lb, Matrix.Translation((0, 0, L)), mat="stone", segs=6)
    p.cyl(0.0045, 0.0, 0.012, Matrix.Translation((0, 0, z1)), mat="glow", segs=6)
    p.ring(0.0085, 0.002, Matrix.Translation((0, 0, L + Lb * 0.3)), mat="glow", segs=6)


# ---------------------------------------------------------------- wrench
def _open_jaw(Ro, wj, depth, n=9):
    """Open-end jaw (x, z) around (0, 0): a disc with a slot cut down from the top."""
    d = math.asin(min(0.95, wj / 2 / Ro))
    pts = []
    for i in range(n):
        a = math.pi / 2 + d + (2 * math.pi - 2 * d) * i / (n - 1)
        pts.append((Ro * math.cos(a), Ro * math.sin(a)))
    return pts + [(wj / 2, -depth), (-wj / 2, -depth)]


def _wrench_head(p, L, r):
    e = p.era
    Ro = J(p, 0.022, 0.12)
    zc = L + Ro * 0.85
    tilt = J(p, 15, 0.5)

    def neck(t, mat, **kw):
        front(p, [(-r * 0.9, L - 0.02), (r * 0.9, L - 0.02), (Ro * 0.55, zc - Ro * 0.6), (-Ro * 0.55, zc - Ro * 0.6)], t, mat=mat, **kw)

    if e == "Primal":
        # Lever stick with a lashed wooden wedge.
        f = side(p, [(0.02, L - 0.03), (-0.02, L - 0.03), (-0.028, L + 0.03), (-0.004, J(p, 0.075, 0.12) + L), (0.024, L + 0.03)], 0.03, mat="body")
        reshape(f, lambda co: setattr(co, "x", co.x * lerp(1.0, 0.3, (co.z - L) / 0.09)))
        p.band(r * 1.9, L - 0.01, h=0.03)
        return
    if e == "Mercantile":
        # Bronze box-end: a hex ring, scrolled neck.
        neck(0.008, "brass")
        p.ring(Ro * 0.72, Ro * 0.22, M(loc=(0, 0, zc), rot=(90, 0, 0)), mat="brass", segs=6)
        p.ball(0.005, Matrix.Translation((0, 0, zc + Ro * 0.95)), mat="brass", segs=(6, 4))
        return
    if e == "Industrial":
        # Adjustable wrench: fixed jaw, sliding jaw, knurled worm.
        t = 0.009
        neck(t, "steel")
        body = [(-0.022, -0.018), (0.02, -0.018), (0.025, 0.0), (0.012, 0.006), (-0.01, 0.006), (-0.012, 0.03), (-0.024, 0.03)]
        front(p, [(x * Ro / 0.022, z * Ro / 0.022) for x, z in body], t, mat="steel", m=M(loc=(0, 0, zc), rot=(0, tilt, 0)))
        open_w = J(p, 0.006, 0.4) * Ro / 0.022
        m = M(loc=(0, 0, zc), rot=(0, tilt, 0))
        p.box((0.011 * Ro / 0.022, t, 0.022 * Ro / 0.022), m @ Matrix.Translation(((0.003 + open_w) * Ro / 0.022 + 0.0055, 0, 0.016 * Ro / 0.022)), mat="steel", bevel=0)
        p.cyl(0.0055, 0.0055, 0.016, m @ M(loc=(-0.004, -t * 0.55, -0.007), rot=(0, 90, 0)), mat="iron", segs=8)
        return
    if e == "Steampunk":
        # Gear wrench: toothed ratchet ring, amber pawl switch.
        neck(0.008, "brass")
        gear(p, (0, 0, zc), Ro * 0.8, 0.009, 10, "brass", axis="y")
        disk(p, (0, -0.0055, zc), Ro * 0.38, 0.003, "y", "glow", segs=8)
        p.box((0.006, 0.004, 0.01), Matrix.Translation((0, -0.006, zc - Ro * 0.95)), mat="copper", bevel=0)
        return
    if e == "Future":
        # Smart torque wrench: shell disc head, square drive, lit torque ring and read-out.
        neck(0.012, "body")
        disk(p, (0, 0, zc), Ro * 0.95, 0.016, "y", "body", segs=12)
        p.ring(Ro * 0.62, 0.0025, M(loc=(0, -0.0085, zc), rot=(90, 0, 0)), mat="glow", segs=12)
        p.box((0.009, 0.012, 0.009), Matrix.Translation((0, -0.013, zc)), mat="shell_dark", bevel=0)
        p.box((r * 1.1, 0.004, 0.022), Matrix.Translation((0, -0.0065, L - 0.005)), mat="glow", bevel=0)
        return
    if e == "Wasteland":
        # Scavenged pipe wrench: hook jaw on a knurled nut, wired to the pipe.
        t = 0.01
        hook = [(-0.006, -0.03), (0.006, -0.03), (0.006, 0.015), (0.024, 0.02), (0.022, 0.03), (-0.008, 0.026)]
        front(p, [(x * Ro / 0.022, z * Ro / 0.022) for x, z in hook], t, mat="metal", m=Matrix.Translation((0, 0, zc)))
        p.cyl(0.009, 0.009, 0.012, Matrix.Translation((0, 0, zc - Ro * 0.7)), mat="iron", segs=6)
        p.box((0.022, t, 0.007), Matrix.Translation((0.009, 0, zc - Ro * 0.85)), mat="steel", bevel=0)
        p.band(r * 1.35, L - 0.01, h=0.03)
        return
    t = 0.008 if e == "Agrarian" else 0.014
    mat = "iron" if e == "Agrarian" else "stone"
    neck(t, mat)
    kw = dict(bevel=0.2) if e == "Ancient" else {}
    front(p, _open_jaw(Ro, Ro * J(p, 0.9, 0.12), Ro * 0.2), t, mat=mat, m=M(loc=(0, 0, zc), rot=(0, tilt, 0)), **kw)
    if e == "Ancient":
        stone_collar(p, L, r, 0.03)
        m = M(loc=(0, 0, zc), rot=(0, tilt, 0))
        p.box((Ro * 0.8, t + 0.002, 0.003), m @ Matrix.Translation((0, 0, -Ro * 0.22)), mat="glow", bevel=0)
        p.ball(0.003, m @ Matrix.Translation((0, -t / 2, -Ro * 0.6)), mat="glow", segs=(6, 4))


# ---------------------------------------------------------------- broom
def _broom_head(p, L, r):
    e = p.era
    H = J(p, 0.36, 0.12)
    if e == "Primal":
        # Bundle of twigs bound to the stick end.
        n = p.rng.randint(6, 8)
        for i in range(n):
            x = (i / (n - 1) - 0.5) * J(p, 0.24, 0.15)
            y = p.rng.uniform(-0.03, 0.03)
            p.tube([(x * 0.1, y * 0.2, L - 0.06), (x * 0.45, y * 0.5, L + 0.1), (x, y, L + H * p.rng.uniform(0.85, 1.05))], p.rng.uniform(0.004, 0.006), mat="body", segs=4)
        p.band(r * 2.2, L, h=0.05)
        return
    if e == "Agrarian":
        # Flat straw broom with two stitch rows.
        sq = J(p, 0.35, 0.15)
        wd = J(p, 0.13, 0.12)
        prof = [(r * 1.15, L - 0.08), (0.032, L + 0.03), (0.055, L + 0.14), (wd, L + H * 0.92), (wd * 0.96, L + H), (0.0, L + H)]
        p.lathe(prof, M(scale=(1, sq, 1)), mat="rope", segs=10)
        for z, rr in ((L + 0.09, 0.045), (L + 0.16, 0.06)):
            p.box((rr * 2.06, rr * 2 * sq + 0.006, 0.008), Matrix.Translation((0, 0, z)), mat="leather", bevel=0)
        return
    if e == "Mercantile":
        # Horsehair push broom: dark wooden block, bristle bed, iron braces.
        W = J(p, 0.36, 0.1)
        p.box((W, 0.06, 0.045), Matrix.Translation((0, 0, L + 0.04)), mat="body", bevel_seg=1)
        p.box((W * 0.96, 0.052, J(p, 0.08, 0.2)), Matrix.Translation((0, 0, L + 0.1)), mat="leather", bevel=0)
        p.box((0.05, 0.004, 0.022), Matrix.Translation((0, -0.031, L + 0.04)), mat="brass", bevel=0)
        for s in (-1, 1):
            rod(p, (0, 0, L - 0.12), (s * W * 0.3, 0, L + 0.02), 0.004, mat="iron", segs=5)
        collar(p, L, r, 0.04, mat="brass", k=1.2)
        return
    if e == "Industrial":
        # String mop in a steel clamp.
        p.box((0.06, 0.035, 0.04), Matrix.Translation((0, 0, L + 0.01)), mat="steel", bevel=0)
        n = 10
        for i in range(n):
            a = i * math.tau / n + p.rng.uniform(-0.2, 0.2)
            s = J(p, 0.12, 0.25)
            c, sn = math.cos(a), math.sin(a)
            p.tube([(c * 0.015, sn * 0.01, L + 0.03), (c * s * 0.6, sn * s * 0.5, L + H * 0.5), (c * s, sn * s * 0.8, L + H * p.rng.uniform(0.55, 0.8))], 0.008, mat="cloth", segs=4)
        return
    if e == "Steampunk":
        # Clockwork carpet sweeper: brass housing, twin brush rollers, winding key.
        W = J(p, 0.28, 0.1)
        zh = L + 0.1
        p.box((W, 0.1, 0.07), Matrix.Translation((0, 0, zh)), mat="brass", bevel_seg=1)
        for y in (-0.028, 0.028):
            disk(p, (0, y, zh + 0.036), 0.02, W * 0.92, "x", "leather", segs=8)
        p.tube([(-W * 0.35, 0, zh - 0.035), (-W * 0.2, 0, L + 0.02), (0, 0, L - 0.01), (W * 0.2, 0, L + 0.02), (W * 0.35, 0, zh - 0.035)], 0.006, mat="copper", segs=5)
        rod(p, (W / 2, 0, zh), (W / 2 + 0.025, 0, zh), 0.004, mat="steel")
        p.box((0.005, 0.03, 0.02), Matrix.Translation((W / 2 + 0.027, 0, zh)), mat="brass", bevel=0)
        p.box((0.05, 0.004, 0.018), Matrix.Translation((0, -0.051, zh)), mat="glow", bevel=0)
        return
    if e == "Future":
        # Vacuum stick: flat shell nozzle with a lit intake, dust canister on the haft.
        W = J(p, 0.26, 0.1)
        rod(p, (0, 0, L - 0.02), (0, 0, L + 0.11), r * 1.1, mat="body", segs=8)
        p.box((W, 0.06, 0.035), Matrix.Translation((0, 0, L + 0.125)), mat="body", bevel_seg=1)
        p.box((W * 0.85, 0.004, 0.006), Matrix.Translation((0, -0.031, L + 0.13)), mat="glow", bevel=0)
        cz = L - J(p, 0.32, 0.15)
        p.cyl(0.028, 0.028, 0.15, Matrix.Translation((0, -0.034, cz)), mat="glass", segs=8)
        for z in (cz - 0.012, cz + 0.15):
            p.cyl(0.03, 0.03, 0.012, Matrix.Translation((0, -0.034, z)), mat="shell_dark", segs=8)
        p.ring(0.0285, 0.003, Matrix.Translation((0, -0.034, cz + 0.11)), mat="glow", segs=8)
        return
    if e == "Wasteland":
        # Tin-can socket stuffed with plastic strips and wire.
        p.cyl(0.032, 0.03, 0.1, Matrix.Translation((0, 0, L - 0.03)), mat="rust", segs=8)
        n = p.rng.randint(7, 9)
        for i in range(n):
            a = i * math.tau / n
            c, sn = math.cos(a), math.sin(a)
            tip = (c * J(p, 0.11, 0.3), sn * J(p, 0.05, 0.3), L + H * p.rng.uniform(0.6, 0.95))
            rod(p, (c * 0.018, sn * 0.018, L + 0.06), tip, 0.006, 0.004, mat=p.rng.choice(("paint", "cloth", "rubber")), segs=4)
        p.band(0.032, L + 0.03, h=0.03)
        return
    # Ancient: stone fan head, comb of rune channels.
    stone_collar(p, L, r, 0.05)
    out = [(-0.03, L - 0.02), (0.03, L - 0.02), (0.13, L + H * 0.82), (0.08, L + H * 0.95), (0, L + H),
           (-0.08, L + H * 0.95), (-0.13, L + H * 0.82)]
    front(p, out, 0.03, mat="stone", bevel=0.2, bevel_seg=1)
    for k in (-2, -1, 0, 1, 2):
        a = k * 11
        p.box((0.005, 0.004, H * 0.55), M(loc=(math.sin(math.radians(a)) * H * 0.5, -0.0155, L + 0.02 + H * 0.45 * math.cos(math.radians(a))), rot=(0, a, 0)),
              mat="glow", bevel=0)


# Haft lengths (m, grip end to head seat). Short tools are a grip only: the blade or jaw is the head.
function("Sickle", "Hafted", HAFTED, "carried")(tool(0.27, 0.016, _sickle_head))
function("Shovel", "Hafted", HAFTED, "carried")(tool(1.05, 0.018, _shovel_head))
function("Pitchfork", "Hafted", HAFTED, "carried")(tool(1.2, 0.017, _fork_head))
function("Saw", "Hafted", HAFTED, "carried")(tool(0.13, 0.016, _saw_head))
function("Hatchet", "Hafted", HAFTED, "carried")(tool(0.58, 0.016, _hatchet_head))
function("Chisel", "Hafted", HAFTED, "carried")(tool(0.11, 0.014, _chisel_head))
function("Wrench", "Hafted", HAFTED, "carried")(tool(0.17, 0.011, _wrench_head))
function("Broom", "Hafted", HAFTED, "carried")(tool(1.15, 0.015, _broom_head))
