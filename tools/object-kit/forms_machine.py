"""Machine family forms (機械: 底座、主機構、傳動、動力源、外露管線／飾), workshop set: Loom, Forge, Anvil, Millstone,
Kiln, Stove, Still.

Slots: base (底座: plinth, frame, stump, pit rim), mechanism (主機構: the working part — warp, hearth, anvil body,
stones, chamber, cooktop, pot), drive (傳動: beams, bellows, hammers, gears, belts, doors, necks), power (動力源: the
era's energy — hearth fire, treadle, animal sweep, motor, steam boiler, coil core, rune core), trim (外露管線／飾:
flues, pipes, gauges, tools and wares).
Fire and hot coals use the glow material in every era, like the lamps' flames: amber where the era has no glow of
its own, so a Primal pit fire still reads as fire (the game sets brightness per group; the colour carries it).
Frame: floor contact at z = 0, front faces -Y, metres. Every form draws its frame factors first, in a fixed order,
so frames, beams, belts and pipes meet across slots. Budget 'machine' (4000) but each kit stays near or below 2500,
since a workshop shows several machines at once.
"""
import math

from mathutils import Matrix, Vector

from forms_furniture import flagstone, gear, pot, rock, runes
from forms_lamp import flame, lit
from kit_forms import F, J, coin, function
from kit_lib import M

MACH = ("base", "mechanism", "drive", "power", "trim")
T = Matrix.Translation
TAU = math.tau


# ---------------------------------------------------------------- helpers
def lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def xcyl(p, r, L, c, mat="body", segs=8, r2=None, **kw):
    """Cylinder along X centred on c."""
    p.cyl(r, r if r2 is None else r2, L, T(c) @ M(rot=(0, 90, 0)) @ T((0, 0, -L / 2)), mat=mat, segs=segs, **kw)


def ycyl(p, r, L, c, mat="body", segs=8, r2=None, **kw):
    """Cylinder along Y centred on c (r is the +Y end radius, r2 the -Y end)."""
    p.cyl(r, r if r2 is None else r2, L, T(c) @ M(rot=(90, 0, 0)) @ T((0, 0, -L / 2)), mat=mat, segs=segs, **kw)


def beam(p, a, b, s, mat="body", t=None, **kw):
    """Square bar of section s x (t or s) from point a to point b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    up = "Y" if abs(d.normalized().y) < 0.9 else "X"
    p.box((s, t or s, d.length), T((a + b) / 2) @ d.to_track_quat("Z", up).to_matrix().to_4x4(), mat=mat, **kw)


def sheet(p, a, b, w, t, mat="cloth", x=0.0, **kw):
    """Flat strip of width w (along X) and thickness t from a = (y, z) to b = (y, z)."""
    dy, dz = b[0] - a[0], b[1] - a[1]
    p.box((w, math.hypot(dy, dz), t), T((x, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2)) @ M(rot=(math.degrees(math.atan2(dz, dy)), 0, 0)),
          mat=mat, bevel=0, **kw)


def threads(p, a, b, wa, wb, n, r=0.004, mat="rope"):
    """n warp threads from a = (y, z) to b = (y, z), spread over width wa at a and wb at b."""
    for i in range(n):
        u = i / (n - 1) - 0.5
        p.tube([(u * wa, a[0], a[1]), (u * wb, b[0], b[1])], r, mat=mat, segs=3)


def side_plate(p, x, outline, t, mat="body", **kw):
    """Plate in the YZ plane at x (outline [(y, z), ...])."""
    p.plate(outline, t, T((x, 0, 0)) @ M(rot=(0, 0, 90)), mat=mat, **kw)


def coals(p, x, y, z, r, n=5):
    m = lit(p)
    for i in range(n):
        a = i * TAU / n + p.rng.uniform(-0.3, 0.3)
        d = r * p.rng.uniform(0.25, 0.75)
        p.ball(r * 0.3, M(loc=(x + math.cos(a) * d, y + math.sin(a) * d, z + r * 0.05), scale=(1, 1, 0.55)), mat=m, segs=(5, 3))


def fire(p, x, y, z, s, n=3, bed=True):
    """Fire on (x, y, z): one flame of base radius s and n - 1 smaller ones, on a coal bed."""
    m = lit(p)
    flame(p, x, y, z, s, mat=m, segs=6)
    for i in range(n - 1):
        a = i * TAU / max(1, n - 1) + p.rng.uniform(-0.5, 0.5)
        flame(p, x + math.cos(a) * s * 1.1, y + math.sin(a) * s * 1.1, z, s * J(p, 0.6, 0.2), lean=J(p, 12, 0.5), mat=m, segs=5)
    if bed:
        coals(p, x, y, z, s * 1.7, 4)


def logs(p, x, y, z, L, r, n=3, mat="wood"):
    for i in range(n):
        a = i * 180 / n + p.rng.uniform(-15, 15)
        p.cyl(r, r * 0.85, L, T((x, y, z + r)) @ M(rot=(0, 0, a)) @ M(rot=(0, 90, 0)) @ T((0, 0, -L / 2)), mat=mat, segs=6)


def gauge(p, x, y, z, r):
    """Dial on a -Y face at (x, y, z)."""
    p.cyl(r, r, r * 0.4, T((x, y, z)) @ M(rot=(90, 0, 0)), mat="brass", segs=8)
    p.cyl(r * 0.78, r * 0.78, 0.004, T((x, y - r * 0.4, z)) @ M(rot=(90, 0, 0)), mat=p.style["glow"] or "bone", segs=8)


def boiler(p, x, y, z, r, h, mat="brass"):
    """Upright boiler on (x, y, z): domed crown, copper hoops, safety valve, gauge and a lit fire door on -Y."""
    p.cyl(r, r, h, T((x, y, z)), mat=mat, segs=10)
    p.lathe([(r, h), (r * 0.85, h + r * 0.4), (r * 0.35, h + r * 0.62), (0, h + r * 0.66)], T((x, y, z)), mat=mat, segs=10)
    for k in (0.12, 0.8):
        p.ring(r * 1.02, r * 0.06, T((x, y, z + h * k)), mat="copper", segs=10)
    p.cyl(r * 0.1, r * 0.08, r * 0.45, T((x, y, z + h + r * 0.55)), mat="copper", segs=6)
    gauge(p, x, y - r, z + h * 0.62, r * 0.26)
    p.box((r * 0.7, 0.02, r * 0.45), T((x, y - r * 0.97, z + h * 0.3)), mat=lit(p), bevel=0)


def coilcore(p, x, y, z, r, h, n=3):
    """Future / Ancient power core: column wound with glowing rings, capped."""
    p.cyl(r, r, h, T((x, y, z)), mat="fit", segs=10)
    for i in range(n):
        p.ring(r * 1.05, h * 0.05, T((x, y, z + h * (i + 1) / (n + 1))), mat="glow", segs=10)
    p.lathe([(r * 1.1, h), (r * 0.8, h + r * 0.35), (0, h + r * 0.45)], T((x, y, z)), mat="body", segs=10)


def flue(p, x, y, z0, z1, r, mat="iron", cap=True, segs=8):
    p.cyl(r, r, z1 - z0, T((x, y, z0)), mat=mat, segs=segs)
    if cap:
        p.cyl(r * 1.7, r * 0.3, r * 0.8, T((x, y, z1 + r * 0.4)), mat=mat, segs=segs)


def motor(p, x, y, z, r, L, mat="paint"):
    """Electric motor along X standing on z; pulley on the -X end. Returns the pulley centre."""
    c = (x, y, z + r * 1.15)
    p.box((L * 0.8, r * 1.7, r * 0.3), T((x, y, z + r * 0.15)), mat="steel", bevel=0)
    xcyl(p, r, L, c, mat=mat, segs=10)
    for k in (-0.25, 0.0, 0.25):
        p.ring(r * 1.03, r * 0.05, T((x + k * L, c[1], c[2])) @ M(rot=(0, 90, 0)), mat="steel", segs=10)
    pc = (x - L / 2 - r * 0.25, c[1], c[2])
    xcyl(p, r * 0.55, r * 0.35, pc, mat="steel", segs=8)
    return pc


def belt(p, a, ra, b, rb, mat="rubber"):
    """Open belt between pulleys centred at a and b (same x)."""
    for s in (1, -1):
        p.tube([(a[0], a[1], a[2] + s * ra), (b[0], b[1], b[2] + s * rb)], 0.008, mat=mat, segs=4)


def xwheel(p, r, c, rim="iron", hub="body", spokes=6, t=None):
    """Spoked wheel turning about X (in the YZ plane)."""
    p.ring(r, t or r * 0.07, T(c) @ M(rot=(0, 90, 0)), mat=rim, segs=12)
    xcyl(p, r * 0.15, r * 0.25, c, mat=hub, segs=8)
    for i in range(spokes // 2):
        p.box((r * 0.04, r * 1.9, r * 0.04), T(c) @ M(rot=(i * 360 / spokes, 0, 0)), mat=hub, bevel=0)


def brick(p, w, d, h, loc, mat="ceramic", n=3, mortar="stone", **kw):
    """Brick or block mass (bottom at loc z) with n mortar courses."""
    x, y, z = loc
    p.box((w, d, h), T((x, y, z + h / 2)), mat=mat, **kw)
    for i in range(n):
        zz = z + h * (i + 1) / (n + 1)
        p.box((w + 0.012, d + 0.012, 0.012), T((x, y, zz)), mat=mortar, bevel=0)


def wire(p, x, y, z, r, turns=2.5, axis="z"):
    """Wasteland wire lashing around a round member."""
    pts = []
    for i in range(int(turns * 6) + 1):
        a = i * TAU / 6
        if axis == "z":
            pts.append((x + math.cos(a) * r, y + math.sin(a) * r, z + i * 0.004))
        else:
            pts.append((x + i * 0.004, y + math.cos(a) * r, z + math.sin(a) * r))
    p.tube(pts, 0.0025, mat="iron", segs=3)


def patch(p, w, h, m, mat="paint"):
    p.box((w, 0.006, h), m, mat=mat, bevel=0)
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.cyl(0.006, 0.006, 0.006, m @ T((sx * w * 0.4, -0.003, sz * h * 0.4)) @ M(rot=(90, 0, 0)), mat="steel", segs=4)


def bucket(p, x, y, r, h, mat="wood", hoop="iron"):
    p.cyl(r * 0.85, r, h, T((x, y, 0)), mat=mat, segs=10)
    for k in (0.2, 0.8):
        p.ring(r * (0.88 + 0.12 * k) * 1.01, 0.004, T((x, y, h * k)), mat=hoop, segs=10)
    p.cyl(r * 0.93, r * 0.93, 0.004, T((x, y, h * 0.85)), mat="glass", segs=10)


def tongs(p, x, y, z, L, rot=0.0, mat="iron"):
    """Smith's tongs lying on z, jaws toward +X."""
    m = T((x, y, z)) @ M(rot=(0, 0, rot))
    for s in (-1, 1):
        a, b, c = m @ Vector((-L / 2, s * 0.012, 0.006)), m @ Vector((L * 0.32, s * 0.004, 0.006)), m @ Vector((L / 2, s * 0.012, 0.008))
        p.tube([tuple(a), tuple(b), tuple(c)], 0.006, mat=mat, segs=4)


def hammer(p, x, y, z, L=0.32, rot=0.0, head="iron", handle="wood"):
    """Hand hammer lying on z, head toward +X."""
    m = T((x, y, z)) @ M(rot=(0, 0, rot))
    p.box((L, 0.02, 0.02), m @ T((0, 0, 0.014)), mat=handle, bevel=0)
    p.box((0.045, 0.1, 0.045), m @ T((L / 2, 0, 0.026)), mat=head, bevel=0)


def sack(p, x, y, r, h, mat="cloth"):
    p.lathe([(0, 0), (r * 0.95, 0.01), (r * 1.05, h * 0.45), (r * 0.85, h * 0.85), (r * 0.3, h), (0, h * 1.02)],
            T((x, y, 0)), mat=mat, segs=8, noise=0.03)
    p.ring(r * 0.33, 0.006, T((x, y, h * 0.94)), mat="rope", segs=6)


def shell_box(p, w, d, h, loc, mat="body", **kw):
    """Box with its bottom face at loc z."""
    x, y, z = loc
    p.box((w, d, h), T((x, y, z + h / 2)), mat=mat, **kw)


# ================================================================ Loom
def _loom_primal(p, s, W, D, H):  # backstrap loom: warp tied to a post, breast bar on forked stakes
    yb, yf = D / 2, -D / 2
    top, front = (yb - 0.05, H * 0.72), (yf + 0.02, 0.37)
    if s == "base":
        p.tube([(0, yb, 0), (J(p, 0.02, 1), yb + 0.01, H * 0.5), (0, yb, H)], 0.05, mat="wood", segs=7)
        if coin(p):
            p.tube([(0, yb, H * 0.85), (0.12, yb + 0.02, H * 1.05)], 0.02, mat="wood", segs=5)
        for sx in (-1, 1):
            x = sx * W * 0.55
            p.tube([(x, yf, 0), (x, yf, 0.34)], 0.022, mat="wood", segs=5)
            p.tube([(x, yf, 0.27), (x + sx * 0.05, yf - 0.02, 0.4)], 0.012, mat="wood", segs=4)
        for i in range(p.rng.randint(2, 3)):
            rock(p, J(p, 0.1), J(p, 0.08), 0.06, (p.rng.uniform(-0.15, 0.15), yb + p.rng.uniform(-0.08, 0.08), 0.03), segs=(6, 4))
    elif s == "mechanism":
        threads(p, top, front, W * 0.6, W * 0.8, p.rng.choice((7, 9)), r=0.004)
        sheet(p, front, lerp(front, top, J(p, 0.32, 0.25)), W * 0.8, 0.012)
    elif s == "drive":
        xcyl(p, 0.02, W * 0.75, (0, top[0], top[1]), mat="wood", segs=6)
        for sx in (-1, 1):
            p.tube([(sx * W * 0.37, top[0], top[1]), (0, yb - 0.04, top[1] + 0.06)], 0.006, mat="rope", segs=4)
        xcyl(p, 0.026, W * 1.2, (0, front[0], front[1]), mat="wood", segs=6)
        for t, r in ((0.55, 0.012), (0.74, 0.022)):
            q = lerp(front, top, t)
            xcyl(p, r, W * J(p, 0.85, 0.06), (0, q[0], q[1] + 0.02), mat="wood", segs=5)
    elif s == "power":  # backstrap belt looping toward the weaver's seat, hide mat
        for sx in (-1, 1):
            x = sx * W * 0.5
            p.tube([(x, front[0], front[1]), (x * 1.05, yf - 0.12, 0.24), (x * 0.85, yf - 0.3, 0.06)], 0.009, mat="hide", segs=4)
        sheet(p, (yf - 0.32, 0.05), (yf - 0.36, 0.035), W * 0.9, 0.02, mat="hide")
        flagstone(p, J(p, 0.5), J(p, 0.35), 0.01, 0, mat="hide", n=6, rough=0.25, y=yf - 0.5, noise=0)
    else:
        for i in range(p.rng.randint(2, 3)):
            p.ball(J(p, 0.05), T((W * 0.55 + i * 0.1, yb - 0.25 + p.rng.uniform(-0.05, 0.05), 0.045)), mat="cloth", segs=(6, 4))
        p.box((J(p, 0.4), 0.04, 0.008), M(loc=(-W * 0.6, -0.05, 0.004), rot=(0, 0, J(p, 70, 0.2))), mat="bone", bevel=0)


def _loom_agrarian(p, s, W, D, H):  # warp-weighted upright loom
    y0, y1 = -D * 0.2, D * 0.3

    def at(t, dy=0.0):
        return (y0 + (y1 - y0) * t + dy, H * t)
    xs = (-W / 2, W / 2)
    if s == "base":
        for x in xs:
            beam(p, (x, y0, 0), (x, y1, H), 0.08, mat="wood")
            beam(p, (x, y0 + (y1 - y0) * 0.5, H * 0.5), (x, D * 0.75, 0.02), 0.06, mat="wood")
            p.box((0.12, D * 1.2, 0.07), T((x, D * 0.25, 0.035)), mat="wood")
        if coin(p):
            beam(p, (xs[0], *at(0.12, 0.02)), (xs[1], *at(0.12, 0.02)), 0.05, mat="wood")
    elif s == "mechanism":
        a, b = at(0.9, -0.08), at(0.6, -0.08)
        sheet(p, a, b, W * 0.82, 0.014)
        bot = at(0.2, -0.08)
        threads(p, b, bot, W * 0.82, W * 0.82, 9, r=0.004, mat="rope")
    elif s == "drive":
        c = at(0.95, -0.02)
        xcyl(p, 0.065, W + 0.22, (0, c[0], c[1]), mat="wood", segs=8)
        for x in (-W / 2 - 0.12, W / 2 + 0.12):
            p.box((0.03, 0.22, 0.03), T((x, c[0], c[1])), mat="wood", bevel=0)
        h = at(0.5, -0.16)
        xcyl(p, 0.025, W * 1.02, (0, h[0], h[1]), mat="wood", segs=6)
        for x in xs:
            p.box((0.05, 0.14, 0.04), T((x, h[0] + 0.05, h[1] - 0.04)), mat="wood", bevel=0)
        sr = at(0.36, -0.06)
        xcyl(p, J(p, 0.03, 0.2), W * 0.95, (0, sr[0], sr[1]), mat="wood", segs=6)
    elif s == "power":  # loom weights: gravity keeps the warp taut, two sheds front and back
        bot = at(0.2, -0.08)
        for i in range(9):
            u = i / 8 - 0.5
            dy = 0.03 if i % 2 else -0.03
            z = bot[1] - J(p, 0.1, 0.25)
            p.cyl(J(p, 0.04, 0.12), 0.024, 0.09, T((u * W * 0.82, bot[0] + dy, z - 0.09)), mat="ceramic", segs=6)
            p.tube([(u * W * 0.82, bot[0], bot[1]), (u * W * 0.82, bot[0] + dy, z)], 0.003, mat="rope", segs=3)
    else:
        p.plate([(0, 0), (0.05, 0.02), (0.05, J(p, 0.6, 0.12)), (0, 0.66)], 0.02, M(loc=(W / 2 + 0.1, -0.15, 0), rot=(0, -12, 0)),
                mat="wood", bevel=0)
        pot(p, J(p, 0.14), J(p, 0.16), (-W / 2 - 0.15, -0.2, 0), mat="bark")
        for i in range(2):
            p.ball(0.045, T((-W / 2 - 0.15 + i * 0.05, -0.2, 0.17)), mat="cloth", segs=(6, 4))


def _loom_mercantile(p, s, W, D, H):  # treadle floor loom
    zw, hx, hy = 0.82, W / 2, D / 2
    if s == "base":
        for x in (-hx, hx):
            for y in (-hy, hy):
                p.box((0.07, 0.07, H), T((x, y, H / 2)), mat="body", bevel=0.04)
            p.box((0.06, D, 0.07), T((x, 0, 0.14)), mat="body", bevel=0)
            p.box((0.06, D, 0.08), T((x, 0, H - 0.04)), mat="body", bevel=0)
        for y in (-hy + 0.04, hy - 0.04):
            p.box((W, 0.09, 0.08), T((0, y, zw)), mat="body", bevel=0.05)
        p.box((W, 0.06, 0.06), T((0, hy, 0.14)), mat="body", bevel=0)
    elif s == "mechanism":
        cut = -hy * J(p, 0.25, 0.3)
        sheet(p, (hy - 0.06, zw + 0.045), (cut, zw + 0.045), W * 0.86, 0.004, mat="rope")
        sheet(p, (cut, zw + 0.045), (-hy + 0.06, zw + 0.045), W * 0.86, 0.012, mat="cloth")
        xcyl(p, 0.07, W * 0.86, (0, -hy + 0.12, 0.42), mat="cloth", segs=8)
        sheet(p, (-hy + 0.06, zw + 0.04), (-hy + 0.16, 0.48), W * 0.86, 0.01, mat="cloth")
        for i, y in enumerate((0.0, 0.1)):
            for z in (zw + 0.26, zw - 0.16):
                p.box((W * 0.9, 0.025, 0.03), T((0, y, z)), mat="wood", bevel=0)
            p.box((W * 0.86, 0.006, 0.4), T((0, y, zw + 0.05)), mat="rope", bevel=0)
        for x in (-hx * 0.95, hx * 0.95):
            p.box((0.04, 0.03, H - zw - 0.1), T((x, -hy * 0.45, (H + zw) / 2 - 0.02)), mat="wood", bevel=0)
        p.box((W * 0.96, 0.06, 0.07), T((0, -hy * 0.45, zw + 0.06)), mat="wood", bevel=0)
    elif s == "drive":
        p.box((W + 0.1, 0.08, 0.08), T((0, 0.05, H + 0.04)), mat="body", bevel=0)
        for x in (-W * 0.25, W * 0.25):
            xcyl(p, J(p, 0.045, 0.15), 0.06, (x, 0.05, H - 0.04), mat="wood", segs=8)
            for y in (0.0, 0.1):
                p.tube([(x, 0.05, H - 0.04), (x, y, zw + 0.27)], 0.004, mat="rope", segs=3)
        p.box((W * 0.9, 0.04, 0.04), T((0, 0.05, 0.36)), mat="wood", bevel=0)
    elif s == "power":  # treadles hinged at the back
        n = p.rng.choice((2, 3, 4))
        for i in range(n):
            x = (i / (n - 1) - 0.5) * W * 0.45
            beam(p, (x, hy - 0.08, 0.05), (x, -hy + 0.18, 0.17), 0.07, mat="wood", t=0.025, bevel=0)
            p.tube([(x, -hy * 0.1, 0.13), (x, 0.05, 0.35)], 0.004, mat="rope", segs=3)
        xcyl(p, 0.015, W * 0.9, (0, hy - 0.08, 0.05), mat="iron", segs=6)
    else:  # bench, shuttle, bobbins
        yb = -hy - J(p, 0.22, 0.1)
        p.box((W * 0.8, 0.26, 0.05), T((0, yb, 0.55)), mat="body", bevel=0.04)
        for x in (-W * 0.35, W * 0.35):
            p.box((0.05, 0.2, 0.53), T((x, yb, 0.265)), mat="body", bevel=0)
        p.ball(0.12, M(loc=(J(p, 0.1, 1), -hy + 0.3, zw + 0.07), scale=(1, 0.18, 0.12)), mat="wood_dark", segs=(8, 4))
        for i in range(p.rng.randint(2, 3)):
            p.cyl(0.03, 0.012, 0.14, T((-W * 0.25 + i * 0.09, yb, 0.575)), mat="cloth", segs=6)


def _loom_industrial(p, s, W, D, H):  # power loom: painted cast-iron frames, belt-driven
    hx, hy, zw = W / 2, D / 2, H * 0.72
    wb, cb = (hy * 0.55, H * 0.32), (-hy * 0.6, H * 0.38)
    pul = (-hx - 0.1, hy * 0.2, H * 0.48)
    if s == "base":
        out = [(-hy, 0), (-hy + 0.14, 0), (-hy * 0.2, H * 0.38), (hy * 0.2, H * 0.38), (hy - 0.14, 0), (hy, 0),
               (hy * 0.86, zw + 0.06), (-hy * 0.86, zw + 0.06)]
        for x in (-hx, hx):
            side_plate(p, x, out, 0.05, mat="paint", bevel=0.02)
        for y, z in ((-hy * 0.8, 0.06), (hy * 0.8, 0.06), (0, zw)):
            p.box((W, 0.06, 0.06), T((0, y, z)), mat="iron", bevel=0)
    elif s == "mechanism":
        xcyl(p, 0.1, W * 0.88, (0, *wb), mat="cloth", segs=10)
        sheet(p, (wb[0], wb[1] + 0.1), (hy * 0.8, zw + 0.03), W * 0.84, 0.004, mat="rope")
        sheet(p, (hy * 0.8, zw + 0.03), (-hy * 0.2, zw + 0.03), W * 0.84, 0.004, mat="rope")
        sheet(p, (-hy * 0.2, zw + 0.03), (-hy * 0.8, zw + 0.03), W * 0.84, 0.01, mat="cloth")
        xcyl(p, 0.08, W * 0.84, (0, *cb), mat="cloth", segs=10)
        for y in (hy * 0.15, hy * 0.3):
            p.box((W * 0.86, 0.02, 0.38), T((0, y, zw + 0.06)), mat="steel", bevel=0)
        p.box((W * 0.9, 0.08, 0.14), T((0, -hy * 0.05, zw + 0.02)), mat="wood_dark", bevel=0)
    elif s == "drive":
        xcyl(p, 0.03, W + 0.3, (0, -hy * 0.1, H * 0.48), mat="steel", segs=8)
        gear(p, J(p, 0.2, 0.1), T((hx + 0.07, -hy * 0.1, H * 0.48)) @ M(rot=(0, 0, 90)), teeth=10, th=0.03, mat="iron")
        gear(p, 0.1, T((hx + 0.07, hy * 0.25, H * 0.62)) @ M(rot=(0, 0, 90)), teeth=8, th=0.03, mat="iron")
        xcyl(p, 0.16, 0.08, (pul[0], pul[1], pul[2]), mat="steel", segs=10)
        xcyl(p, 0.16, 0.08, (pul[0] - 0.09, pul[1], pul[2]), mat="iron", segs=10)
        beam(p, (pul[0] + 0.05, pul[1], pul[2]), (-hx, -hy * 0.1, H * 0.48), 0.03, mat="steel", bevel=0)
    elif s == "power":
        mc = motor(p, pul[0] + 0.12, hy * 0.2 + 0.05, 0.0, J(p, 0.13, 0.1), 0.34)
        mc = (pul[0], mc[1], mc[2])
        belt(p, pul, 0.16, mc, 0.07)
        p.box((0.05, 0.05, 0.04), T((pul[0] + 0.25, hy * 0.2 - 0.18, 0.3)), mat="paint", bevel=0)
    else:
        p.plate([(-0.24, 0), (-0.2, 0.16), (0, 0.24), (0.2, 0.16), (0.24, 0)], 0.02, T((hx + 0.12, -hy * 0.1, H * 0.48)) @ M(rot=(0, 0, 90)),
                mat="paint", bevel=0)
        xcyl(p, 0.012, W * 0.9, (0, hy + 0.06, H * 0.9), mat="steel", segs=6)
        for i in range(p.rng.randint(3, 5)):
            x = (i / 4 - 0.5) * W * 0.8
            p.cyl(0.04, 0.015, 0.14, T((x, hy + 0.06, H * 0.9)), mat="cloth", segs=6)
        if coin(p):
            p.cyl(0.05, 0.05, 0.08, T((hx * 0.6, -hy - 0.1, 0)), mat="steel", segs=8)
            p.tube([(hx * 0.6, -hy - 0.1, 0.08), (hx * 0.6, -hy - 0.16, 0.16)], 0.006, mat="steel", segs=4)


def _loom_steampunk(p, s, W, D, H):  # steam jacquard loom: card head on tall posts, side boiler
    hx, hy, zw = W / 2, D / 2, 0.85
    hz = H - 0.25
    bx = hx + 0.32
    if s == "base":
        for x in (-hx, hx):
            for y in (-hy, hy):
                p.box((0.08, 0.08, H - 0.2), T((x, y, (H - 0.2) / 2)), mat="wood_dark", bevel=0.04)
                p.cyl(0.055, 0.05, 0.05, T((x, y, 0)), mat="brass", segs=8)
            p.box((0.07, D, 0.08), T((x, 0, 0.18)), mat="wood_dark", bevel=0)
        for y in (-hy, hy):
            p.box((W, 0.08, 0.08), T((0, y, zw)), mat="wood_dark", bevel=0.04)
        p.box((W + 0.1, D + 0.1, 0.06), T((0, 0, hz - 0.03)), mat="brass", bevel=0.04)
    elif s == "mechanism":
        sheet(p, (hy - 0.05, zw + 0.045), (-hy * 0.2, zw + 0.045), W * 0.86, 0.004, mat="rope")
        sheet(p, (-hy * 0.2, zw + 0.045), (-hy + 0.05, zw + 0.045), W * 0.86, 0.012, mat="cloth")
        p.box((W * 0.7, D * 0.55, 0.22), T((0, 0, hz + 0.11)), mat="brass", bevel=0.06)
        for i in range(8):
            x = (i / 7 - 0.5) * W * 0.6
            p.tube([(x, 0.0, hz), (x * 1.2, 0.0, zw + 0.06)], 0.003, mat="rope", segs=3)
        p.box((W * 0.9, 0.04, 0.05), T((0, 0.0, zw + 0.25)), mat="brass", bevel=0)
    elif s == "drive":
        gear(p, J(p, 0.18, 0.1), T((hx + 0.06, -hy * 0.3, 0.5)) @ M(rot=(0, 0, 90)), teeth=10, th=0.025)
        gear(p, 0.11, T((hx + 0.06, hy * 0.1, 0.68)) @ M(rot=(0, 0, 90)), teeth=8, th=0.025)
        p.tube([(hx + 0.08, -hy * 0.3, 0.5), (bx - 0.05, -hy * 0.15, 0.95)], 0.012, mat="steel", segs=5)
        beam(p, (hx + 0.1, 0.0, 0.68), (hx + 0.1, 0.0, hz + 0.1), 0.03, mat="brass", bevel=0)
    elif s == "power":
        boiler(p, bx, -hy * 0.15, 0.0, J(p, 0.2, 0.08), 0.75)
        ycyl(p, 0.05, 0.22, (bx - 0.05, -hy * 0.15, 0.95), mat="copper", segs=8)
    else:  # punched-card chain looping down the side, steam pipe, gauge
        n = 7
        for i in range(n):
            t = i / (n - 1)
            z = hz + 0.15 - math.sin(t * math.pi) * J(p, 0.5, 0.15)
            y = -hy * 0.25 + t * hy * 0.5
            p.box((0.24, 0.07, 0.006), M(loc=(-hx - 0.08, y, z), rot=(0, 75, 0)), mat="bone", bevel=0)
        p.tube([(bx, -hy * 0.15, 0.95 + 0.33), (bx, -hy * 0.15, hz + 0.15), (hx * 0.3, 0, hz + 0.15)], 0.018, mat="copper", segs=6)
        gauge(p, hx * 0.2, -D * 0.28, hz + 0.11, 0.05)


def _loom_future(p, s, W, D, H):  # auto-weave pod: shell housing, glowing weave plane, cloth out the front
    hx, hy = W / 2, D / 2
    zm = H * 0.45
    if s == "base":
        shell_box(p, W, D, 0.12, (0, 0, 0), mat="body")
        p.box((W * 0.9, 0.01, 0.02), T((0, -hy - 0.002, 0.06)), mat="glow", bevel=0)
    elif s == "mechanism":
        shell_box(p, W * 0.94, D * 0.8, H - 0.12, (0, hy * 0.1, 0.12), mat="body")
        p.box((W * 0.75, 0.04, 0.12), T((0, -hy * 0.7, zm)), mat="shell_dark", bevel=0)
        p.box((W * 0.7, 0.01, 0.06), T((0, -hy * 0.73, zm)), mat="glow", bevel=0)
    elif s == "drive":
        for z in (zm - 0.09, zm + 0.09):
            xcyl(p, 0.03, W * 0.8, (0, -hy * 0.76, z), mat="shell_dark", segs=8)
        for x in (-hx * 0.88, hx * 0.88):
            p.box((0.04, 0.12, 0.3), T((x, -hy * 0.72, zm)), mat="shell_dark", bevel=0.1)
    elif s == "power":
        coilcore(p, J(p, 0.2, 0.5) * (1 if coin(p) else -1), hy * 0.2, H, 0.13, 0.22)
    else:  # cloth flowing out over a tray onto a roll, spool cones on top
        sheet(p, (-hy * 0.75, zm), (-hy - 0.12, zm - 0.12), W * 0.62, 0.008, mat="cloth")
        xcyl(p, J(p, 0.07, 0.2), W * 0.64, (0, -hy - 0.16, zm - 0.18), mat="cloth", segs=8)
        for x in (-hx * 0.8, hx * 0.8):
            p.box((0.03, 0.2, 0.03), T((x, -hy - 0.08, zm - 0.18)), mat="shell_dark", bevel=0)
        for i in range(p.rng.randint(2, 4)):
            p.cyl(0.045, 0.02, 0.12, T((-hx * 0.7 + i * 0.13, hy * 0.6, H)), mat="cloth", segs=6)


def _loom_wasteland(p, s, W, D, H):  # pipe-frame loom on a pallet, bicycle-wheel treadle drive
    hx, hy, zw = W / 2, D / 2, 0.85
    wc = (hx + 0.1, hy * 0.1, 0.36)
    if s == "base":
        for i in range(4):
            p.box((W, 0.12, 0.03), T((0, -hy + D * (i + 0.5) / 4, 0.12)), mat="wood", bevel=0, noise=0.01)
        for y in (-hy * 0.7, hy * 0.7):
            p.box((W, 0.09, 0.09), T((0, y, 0.05)), mat="wood", bevel=0)
        for x in (-hx * 0.95, hx * 0.95):
            for y in (-hy * 0.8, hy * 0.8):
                p.cyl(0.025, 0.025, H - 0.13, T((x, y, 0.13)), mat="steel", segs=6)
                wire(p, x, y, zw - 0.02, 0.03)
            p.cyl(0.025, 0.025, D * 1.6, T((x, -hy * 0.8, H - 0.05)) @ M(rot=(-90, 0, 0)), mat="rust", segs=6)
    elif s == "mechanism":
        for y in (-hy * 0.8, hy * 0.8):
            xcyl(p, 0.035, W * 1.95 / 2 * 1.0, (0, y, zw), mat="rust", segs=6)
        sheet(p, (hy * 0.8, zw + 0.035), (-hy * 0.15, zw + 0.035), W * 0.8, 0.004, mat="rope")
        sheet(p, (-hy * 0.15, zw + 0.035), (-hy * 0.8, zw + 0.035), W * 0.8, 0.012, mat="cloth")
        patch(p, 0.2, 0.012, T((J(p, 0.1, 1), -hy * 0.5, zw + 0.045)) @ M(rot=(90, 0, 0)), mat="paint")
        p.box((W * 0.85, 0.03, 0.5), T((0, hy * 0.15, zw + 0.06)), mat="iron", bevel=0)
        p.box((W * 0.75, 0.01, 0.4), T((0, hy * 0.15, zw + 0.06)), mat="rope", bevel=0)
    elif s == "drive":  # chain from the wheel sprocket up to a shaft
        sc = (hx + 0.05, hy * 0.15, zw + 0.1)
        gear(p, 0.07, T(sc) @ M(rot=(0, 0, 90)), teeth=8, th=0.01, mat="steel")
        gear(p, 0.09, T((hx + 0.05, wc[1], wc[2])) @ M(rot=(0, 0, 90)), teeth=10, th=0.01, mat="steel")
        belt(p, (hx + 0.05, wc[1], wc[2]), 0.09, (hx + 0.05, sc[1], sc[2]), 0.07, mat="iron")
        p.tube([(hx * 0.95, hy * 0.15, zw + 0.1), (hx + 0.06, hy * 0.15, zw + 0.1)], 0.015, mat="steel", segs=6)
    elif s == "power":  # bicycle wheel flywheel with pedal cranks
        xwheel(p, J(p, 0.3, 0.08), wc, rim="rubber", hub="steel", spokes=8, t=0.02)
        for sx, a in ((1, 1), (-1, -1)):
            p.tube([(wc[0] + sx * 0.05, wc[1], wc[2]), (wc[0] + sx * 0.08, wc[1] + a * 0.12, wc[2] - a * 0.08)], 0.01, mat="steel", segs=4)
            p.box((0.08, 0.04, 0.02), T((wc[0] + sx * 0.12, wc[1] + a * 0.12, wc[2] - a * 0.08)), mat="rubber", bevel=0)
        p.cyl(0.025, 0.025, 0.36, T((wc[0] + 0.06, wc[1], 0)), mat="rust", segs=6)
    else:  # tarp over the top, hanging cans, cable
        sheet(p, (hy * 0.9, H + 0.02), (-hy * 0.5, H + J(p, 0.06, 0.5)), W * 1.05, 0.008, mat="cloth", noise=0.01)
        for i in range(p.rng.randint(1, 3)):
            x = -hx * 0.9 + i * 0.12
            p.tube([(x, -hy * 0.8, H - 0.05), (x, -hy * 0.8 - 0.01, H - 0.25)], 0.0025, mat="iron", segs=3)
            p.cyl(0.035, 0.035, 0.09, T((x, -hy * 0.8 - 0.01, H - 0.34)), mat="steel", segs=7)


def _loom_ancient(p, s, W, D, H):  # stone gate loom: warp of light between lintels
    hx, hy = W / 2, D / 2
    if s == "base":
        shell_box(p, W + 0.3, D, 0.15, (0, 0, 0), mat="body")
        for x in (-hx, hx):
            shell_box(p, 0.18, D * 0.6, H - 0.15, (x, 0, 0.15), mat="body")
    elif s == "mechanism":
        threads(p, (0, H - 0.2), (0, 0.42), W * 0.82, W * 0.82, 9, r=0.004, mat="glow")
        sheet(p, (-0.012, H - 0.24), (-0.012, H - 0.24 - J(p, 0.45, 0.2)), W * 0.84, 0.014, mat="cloth")
    elif s == "drive":
        shell_box(p, W + 0.12, D * 0.5, 0.16, (0, 0, H - 0.2), mat="fit")
        shell_box(p, W - 0.12, D * 0.35, 0.12, (0, 0, 0.3), mat="fit")
        for x in (-hx - 0.06, hx + 0.06):
            p.ring(0.06, 0.012, T((x, 0, H - 0.12)) @ M(rot=(0, 90, 0)), mat="gold", segs=8)
    elif s == "power":  # rune orb in a cradle at the foot
        p.lathe([(0.12, 0.15), (0.16, 0.2), (0.1, 0.25)], T((0, -hy * 0.75, 0)), mat="fit", segs=8)
        p.ball(J(p, 0.09, 0.15), T((0, -hy * 0.75, 0.3)), mat="glow", segs=(8, 6))
    else:
        for x in (-hx, hx):
            runes(p, x, -D * 0.3 - 0.006, 0.4, H - 0.3, n=p.rng.choice((3, 4)), w=0.04)
            p.box((0.2, D * 0.62, 0.03), T((x, 0, H * J(p, 0.55, 0.15))), mat="gold", bevel=0)


LOOM = {"Primal": (_loom_primal, 0.75, 1.0, 0.95), "Agrarian": (_loom_agrarian, 1.3, 0.55, 1.8),
        "Mercantile": (_loom_mercantile, 1.15, 1.15, 1.5), "Industrial": (_loom_industrial, 1.25, 0.95, 1.25),
        "Steampunk": (_loom_steampunk, 1.1, 0.9, 1.95), "Future": (_loom_future, 1.25, 0.85, 1.3),
        "Wasteland": (_loom_wasteland, 1.15, 1.0, 1.45), "Ancient": (_loom_ancient, 1.25, 0.55, 1.75)}


@function("Loom", "Machine", MACH, "machine")
def loom(p, slot):
    fn, w, d, h = LOOM[p.era]
    fn(p, slot, w * F(p, 1, 0.08), d * F(p, 1, 0.08), h * F(p, 1, 0.05))


# ================================================================ Forge
def _forge_primal(p, s, W, D, H):  # pit fire in a stone ring, clay tuyere, hide-bag bellows
    R = W / 2
    if s == "base":
        n = p.rng.randint(8, 10)
        for i in range(n):
            a = i * TAU / n + p.rng.uniform(-0.1, 0.1)
            rock(p, J(p, 0.13), J(p, 0.1), J(p, 0.09), (math.cos(a) * R, math.sin(a) * R, 0.06), segs=(6, 4))
    elif s == "mechanism":
        p.cyl(R * 0.85, R * 0.75, 0.05, mat="stone_dark", segs=10, noise=0.02)
        p.ring(R * 0.8, 0.03, T((0, 0, 0.04)), mat="stone_dark", segs=10, square=False)
    elif s == "drive":  # clay tuyere into the fire from the right
        p.cyl(0.05, 0.035, R * 0.9, T((R * 1.2, 0, 0.12)) @ M(rot=(0, -80, 0)), mat="ceramic", segs=6)
    elif s == "power":
        fire(p, 0, 0, 0.05, J(p, 0.09, 0.12))
        logs(p, 0, 0, 0.04, R * 1.0, 0.03, n=p.rng.choice((2, 3)))
    else:  # hide bag bellows at the tuyere mouth, hammerstone, a hot bloom
        p.ball(0.15, M(loc=(R * 1.45, 0, 0.12), scale=(J(p, 1.2, 0.1), 0.9, 0.7)), mat="hide", segs=(7, 5), noise=0.04)
        rock(p, 0.06, 0.05, 0.05, (-R * 0.4, -R * 1.25, 0.04), segs=(5, 4))
        p.ball(0.05, M(loc=(R * 0.2, -R * 0.15, 0.08), scale=(1.3, 1, 0.7)), mat=lit(p), segs=(6, 4))


def _forge_agrarian(p, s, W, D, H):  # stone hearth with a fireback, lever bellows
    if s == "base":
        p.box((W, D, H), T((0, 0, H / 2)), mat="stone", noise=0.02)
        for i in range(2):
            p.box((W + 0.02, D + 0.02, 0.02), T((0, 0, H * (i + 1) / 3)), mat="stone_dark", bevel=0)
    elif s == "mechanism":
        p.box((W, 0.2, J(p, 0.45, 0.15)), T((0, D / 2 - 0.1, H + 0.22)), mat="stone", noise=0.02)
        p.ring(0.22, 0.04, T((0, -0.05, H + 0.02)), mat="stone_dark", segs=10)
    elif s == "drive":  # wedge bellows on a trestle at the left, pipe into the hearth
        x = -W / 2 - 0.35
        for y in (-0.15, 0.15):
            p.box((0.05, 0.05, H * 0.75), T((x, y, H * 0.375)), mat="wood", bevel=0)
        b = J(p, 0.14, 0.15)
        p.plate([(0.3, 0), (0.0, b * 0.75), (-0.3, b), (-0.3, -b), (0.0, -b * 0.75)], 0.34, T((x, 0, H * 0.82 + b)), mat="leather", bevel=0)
        for z in (H * 0.82 + b * 2, H * 0.82):
            p.box((0.58, 0.36, 0.02), T((x - 0.02, 0, z)), mat="wood", bevel=0)
        p.cyl(0.03, 0.03, 0.3, T((x + 0.28, 0, H * 0.82)) @ M(rot=(0, 90, 0)), mat="iron", segs=6)
        p.tube([(x - 0.28, 0, H * 0.82 + 0.3), (x - 0.4, 0, H * 0.82 + 0.3 + J(p, 0.3, 0.2))], 0.015, mat="wood", segs=4)
    elif s == "power":
        fire(p, 0, -0.05, H + 0.02, J(p, 0.08, 0.12))
    else:  # tongs and quench trough
        tongs(p, W * 0.25, -D / 2 + 0.12, H, 0.45, rot=J(p, 20, 0.5))
        bucket(p, W / 2 + 0.25, -0.1, J(p, 0.17, 0.1), 0.35)


def _forge_mercantile(p, s, W, D, H):  # brick hearth, hood and chimney, great bellows
    hz = H + 0.6
    if s == "base":
        brick(p, W, D, H, (0, 0, 0), n=3)
    elif s == "mechanism":  # hearth rim and fire pan, brick hood on corbels
        p.box((W * 0.7, D * 0.6, 0.06), T((0, -0.05, H + 0.03)), mat="stone_dark", bevel=0)
        p.lathe([(W * 0.5, hz), (W * 0.52, hz + 0.05), (W * 0.2, hz + 0.45), (W * 0.18, hz + 0.5)],
                T((0, D * 0.15, 0)) @ M(scale=(1, D / W, 1)), mat="ceramic", segs=4)
        for x in (-W / 2 + 0.05, W / 2 - 0.05):
            p.box((0.1, 0.1, hz - H), T((x, D / 2 - 0.08, (H + hz) / 2)), mat="ceramic", bevel=0)
    elif s == "drive":  # double bellows on a frame at the back left, lever arm
        x = -W / 2 - 0.3
        p.box((0.08, 0.08, H * 0.7), T((x, D * 0.1, H * 0.35)), mat="wood", bevel=0)
        b = J(p, 0.55, 0.1)
        p.plate([(-b, 0.0), (-b * 0.8, 0.2), (b * 0.4, 0.08), (b * 0.5, 0.0), (b * 0.4, -0.08), (-b * 0.8, -0.2)], 0.42,
                T((x, D * 0.1, H * 0.95)) @ M(rot=(0, 0, 90)), mat="leather", bevel=0)
        for z in (H * 0.95 + 0.2, H * 0.95):
            p.plate([(-b * 1.05, 0), (b * 0.45, 0), (b * 0.45, 0.02), (-b * 1.05, 0.02)], 0.44, T((x, D * 0.1, z)) @ M(rot=(0, 0, 90)),
                    mat="wood", bevel=0)
        p.cyl(0.035, 0.03, 0.3, T((x, D * 0.1 - b * 0.45, H * 0.95)) @ M(rot=(0, 90, -60)), mat="iron", segs=6)
        p.tube([(x, D * 0.1 + b * 0.9, H * 0.95 + 0.2), (x, D * 0.1 + b * 1.1, H * 1.6)], 0.02, mat="wood", segs=4)
    elif s == "power":
        fire(p, 0, -0.05, H + 0.06, J(p, 0.1, 0.12))
    else:  # chimney stack, tongs on the rim, quench tub
        brick(p, W * 0.36, D * 0.36, J(p, 0.75, 0.15), (0, D * 0.15, hz + 0.5), n=2)
        tongs(p, W * 0.3, -D / 2 + 0.1, H + 0.005, 0.5, rot=J(p, -15, 0.5))
        bucket(p, W / 2 + 0.25, -D * 0.2, 0.18, 0.4)


def _forge_industrial(p, s, W, D, H):  # coke forge: steel pan on legs, hood and flue, crank blower
    if s == "base":
        for x in (-W / 2 + 0.04, W / 2 - 0.04):
            for y in (-D / 2 + 0.04, D / 2 - 0.04):
                p.box((0.05, 0.05, H - 0.1), T((x, y, (H - 0.1) / 2)), mat="iron", bevel=0)
        p.box((W, D, 0.03), T((0, 0, 0.25)), mat="iron", bevel=0)
    elif s == "mechanism":
        p.lathe([(W * 0.62, H - 0.12), (W * 0.7, H), (W * 0.62, H - 0.01), (W * 0.2, H - 0.08), (0, H - 0.09)],
                M(rot=(0, 0, 45), scale=(1, D / W, 1)), mat="steel", segs=4)
        p.cyl(0.12, 0.08, 0.12, T((0, 0, H - 0.2)), mat="iron", segs=8)
    elif s == "drive":  # snail blower under the pan, duct up to the firepot
        c = (W * 0.28, -D / 2 + 0.05, 0.55)
        p.cyl(J(p, 0.16, 0.1), 0.16, 0.12, T(c) @ M(rot=(90, 0, 0)) @ T((0, 0, -0.06)), mat="paint", segs=10)
        p.box((0.1, 0.12, 0.18), T((c[0] - 0.12, c[1], c[2] + 0.12)), mat="paint", bevel=0)
        p.tube([(c[0], c[1] + 0.06, c[2]), (0, 0, c[2]), (0, 0, H - 0.2)], 0.045, mat="steel", segs=6)
        p.tube([(c[0], c[1] - 0.07, c[2]), (c[0] + 0.1, c[1] - 0.08, c[2] + 0.08)], 0.012, mat="steel", segs=4)
    elif s == "power":
        fire(p, 0, 0, H - 0.06, J(p, 0.07, 0.12))
        coals(p, 0, 0, H - 0.07, W * 0.3, 6)
    else:  # sheet hood and flue
        hz = H + 0.55
        p.lathe([(W * 0.55, hz), (W * 0.15, hz + 0.4)], T((0, D * 0.15, 0)) @ M(rot=(0, 0, 45)), mat="steel", segs=4)
        flue(p, 0, D * 0.15, hz + 0.38, J(p, 2.35, 0.03), 0.1, mat="steel")
        for x in (-W / 2 + 0.06, W / 2 - 0.06):
            p.box((0.03, 0.03, hz - H), T((x, D / 2 - 0.05, (H + hz) / 2)), mat="iron", bevel=0)
        p.box((0.35, 0.1, 0.25), T((-W / 2 - 0.2, 0, 0.125)), mat="iron", bevel=0)


def _forge_steampunk(p, s, W, D, H):  # round riveted hearth, copper hood, steam blower fed by a boiler
    R = W / 2
    bx = R + 0.35
    if s == "base":
        p.cyl(R * 0.75, R * 0.85, H - 0.1, mat="iron", segs=12)
        p.band(R * 0.8, H * 0.4, h=0.08)
    elif s == "mechanism":
        p.lathe([(R * 0.75, H - 0.1), (R, H), (R * 0.95, H + 0.04), (R * 0.5, H - 0.02), (0, H - 0.04)], mat="brass", segs=12)
        p.lathe([(R * 0.9, H + 0.65), (R * 0.95, H + 0.7), (R * 0.3, H + 1.0), (R * 0.25, H + 1.05)], mat="copper", segs=12)
        for i in range(3):
            a = i * TAU / 3 + 0.5
            p.tube([(math.cos(a) * R * 0.92, math.sin(a) * R * 0.92, H + 0.02), (math.cos(a) * R * 0.88, math.sin(a) * R * 0.88, H + 0.67)],
                   0.012, mat="brass", segs=4)
    elif s == "drive":  # steam turbine blower and blast pipe
        c = (R + 0.12, -R * 0.4, H * 0.5)
        p.cyl(J(p, 0.13, 0.1), 0.13, 0.12, T(c) @ M(rot=(90, 0, 0)) @ T((0, 0, -0.06)), mat="brass", segs=10)
        p.ring(0.13, 0.015, T(c) @ M(rot=(90, 0, 0)), mat="copper", segs=10)
        p.tube([c, (R * 0.4, -R * 0.2, H * 0.5), (0, 0, H - 0.1)], 0.04, mat="copper", segs=6)
    elif s == "power":
        boiler(p, bx, R * 0.2, 0, J(p, 0.2, 0.08), 0.8)
        fire(p, 0, 0, H - 0.04, J(p, 0.08, 0.12))
    else:
        flue(p, 0, 0, H + 1.03, J(p, 2.3, 0.04), R * 0.24, mat="copper")
        p.tube([(bx, R * 0.2, 0.8 + 0.12), (bx, R * 0.2, 1.0), (R + 0.12, -R * 0.4, 1.0), (R + 0.12, -R * 0.4, H * 0.5 + 0.13)],
               0.018, mat="copper", segs=6)
        gauge(p, R + 0.12, -R * 0.4 - 0.1, H * 0.5 + 0.2, 0.045)


def _forge_future(p, s, W, D, H):  # induction furnace: cabinet, crucible in a glowing coil, tilt arms
    if s == "base":
        shell_box(p, W, D, H - 0.2, (0, 0, 0), mat="body")
        p.box((W * 0.5, 0.01, 0.12), T((0, -D / 2 - 0.002, H * 0.5)), mat="shell_dark", bevel=0)
        p.box((W * 0.3, 0.012, 0.03), T((0, -D / 2 - 0.004, H * 0.55)), mat="glow", bevel=0)
    elif s == "mechanism":
        p.lathe([(0, H - 0.2), (0.14, H - 0.18), (0.2, H + 0.1), (0.21, H + 0.2), (0.17, H + 0.2), (0.15, H - 0.1)],
                T((0, -D * 0.05, 0)), mat="shell_dark", segs=12)
    elif s == "drive":  # tilt cradle arms either side of the crucible
        for x in (-0.33, 0.33):
            p.box((0.06, 0.12, 0.3), T((x, -D * 0.05, H - 0.05)), mat="shell_dark", bevel=0.15)
        xcyl(p, 0.035, 0.6, (0, -D * 0.05, H + 0.05), mat="fit", segs=8)
    elif s == "power":
        for i in range(3):
            p.ring(0.235, 0.012, T((0, -D * 0.05, H - 0.12 + i * 0.1)), mat="glow", segs=12)
        p.cyl(0.15, 0.15, 0.01, T((0, -D * 0.05, H + 0.15)), mat="glow", segs=10)
    else:  # exhaust ring hood on a mast, cable conduit
        mx = W / 2 - 0.08
        p.box((0.06, 0.06, 1.1), T((mx, D / 2 - 0.08, H - 0.2 + 0.55)), mat="shell_dark", bevel=0.1)
        p.box((mx + 0.04, 0.05, 0.05), T((mx / 2, D / 2 - 0.08, H + 0.85)), mat="shell_dark", bevel=0)
        p.ring(J(p, 0.25, 0.1), 0.03, T((0, -D * 0.05, H + 0.75)), mat="body", segs=12)
        p.tube([(-W / 2 + 0.1, D / 2, 0.02), (-W / 2 + 0.1, D / 2 + 0.15, 0.02), (-W / 2 - 0.2, D / 2 + 0.15, 0.02)], 0.025, mat="rubber", segs=6)


def _forge_wasteland(p, s, W, D, H):  # oil drum forge on cinder blocks, scrap blower and battery
    r = 0.3
    zc = H - r
    if s == "base":
        for x in (-W * 0.3, W * 0.3):
            for k in range(2):
                p.box((0.2, 0.4, 0.2), T((x, 0, 0.1 + k * 0.2)), mat="stone_dark", bevel=0, noise=0.01)
    elif s == "mechanism":
        xcyl(p, r, W, (0, 0, zc), mat="rust", segs=10)
        for x in (-W * 0.42, 0, W * 0.42):
            p.ring(r * 1.02, 0.01, T((x, 0, zc)) @ M(rot=(0, 90, 0)), mat="iron", segs=10)
        p.box((W * 0.6, 0.03, r * 0.8), T((0, -r * 0.92, zc + 0.04)), mat="rubber", bevel=0)
    elif s == "drive":  # salvaged blower and duct into the drum end
        c = (W / 2 + 0.2, 0.1, zc - 0.12)
        p.box((0.2, 0.18, 0.2), T(c), mat="paint", bevel=0)
        p.cyl(0.07, 0.07, 0.04, T((c[0], c[1] - 0.09, c[2])) @ M(rot=(90, 0, 0)), mat="steel", segs=8)
        p.tube([(c[0] - 0.1, c[1], c[2] + 0.05), (W / 2 + 0.02, 0.05, zc)], 0.04, mat="steel", segs=6)
        wire(p, W / 2 + 0.06, 0.06, zc - 0.02, 0.045, axis="x")
    elif s == "power":
        fire(p, 0, -r * 0.6, zc - r * 0.35, J(p, 0.07, 0.12))
        p.box((W * 0.55, 0.02, r * 0.5), T((0, -r * 0.96, zc - 0.02)), mat=lit(p), bevel=0)
        p.box((0.25, 0.17, 0.2), T((W / 2 + 0.2, -0.25, 0.1)), mat="rubber", bevel=0)
        for x in (-0.06, 0.06):
            p.cyl(0.015, 0.015, 0.03, T((W / 2 + 0.2 + x, -0.25, 0.2)), mat="steel", segs=6)
        p.tube([(W / 2 + 0.26, -0.25, 0.23), (W / 2 + 0.3, -0.1, 0.3), (W / 2 + 0.25, 0.05, zc - 0.22)], 0.006, mat="paint", segs=3)
    else:  # can-stack flue and a patch
        x = -W * 0.3
        for i in range(4):
            p.cyl(0.07, 0.07, 0.2, T((x, 0, zc + r * 0.9 + i * 0.19)) @ M(rot=(J(p, 2, 1), 0, 0)), mat="steel", segs=7)
        patch(p, 0.18, 0.12, T((W * 0.3, -r * 0.97, zc + 0.12)) @ M(rot=(-15, 0, 0)))


def _forge_ancient(p, s, W, D, H):  # monolithic altar hearth with rune channels and an obelisk flue
    if s == "base":
        shell_box(p, W, D, H * 0.25, (0, 0, 0), mat="body")
        shell_box(p, W * 0.8, D * 0.8, H * 0.75, (0, 0, H * 0.25), mat="body")
    elif s == "mechanism":
        p.lathe([(W * 0.42, H - 0.02), (W * 0.44, H + 0.1), (W * 0.36, H + 0.12), (W * 0.25, H + 0.02), (0, H)], mat="fit", segs=8)
    elif s == "drive":  # glowing channels down the front
        for x in (-W * 0.25, 0, W * 0.25):
            p.box((0.03, 0.012, H * 0.6), T((x, -D * 0.4 - 0.004, H * 0.6)), mat="glow", bevel=0)
        p.box((W * 0.6, 0.012, 0.03), T((0, -D * 0.4 - 0.004, H * 0.3)), mat="glow", bevel=0)
    elif s == "power":
        fire(p, 0, 0, H + 0.04, J(p, 0.1, 0.12))
    else:
        shell_box(p, 0.22, 0.22, J(p, 1.0, 0.15), (0, D * 0.42, H), mat="body")
        p.ring(0.13, 0.02, T((0, D * 0.42, H + 0.5)), mat="gold", segs=4)
        runes(p, 0, D * 0.42 - 0.115, H + 0.15, H + 0.85, n=3, w=0.04)


FORGE = {"Primal": (_forge_primal, 1.0, 1.0, 0.1), "Agrarian": (_forge_agrarian, 0.95, 0.75, 0.7),
         "Mercantile": (_forge_mercantile, 1.0, 0.85, 0.75), "Industrial": (_forge_industrial, 0.9, 0.75, 0.82),
         "Steampunk": (_forge_steampunk, 0.85, 0.85, 0.8), "Future": (_forge_future, 0.9, 0.75, 0.85),
         "Wasteland": (_forge_wasteland, 0.95, 0.6, 1.0), "Ancient": (_forge_ancient, 1.0, 0.8, 0.8)}


@function("Forge", "Machine", MACH, "machine")
def forge(p, slot):
    fn, w, d, h = FORGE[p.era]
    fn(p, slot, w * F(p, 1, 0.08), d * F(p, 1, 0.08), h * F(p, 1, 0.05))


# ================================================================ Anvil
def _horned(p, H, L, w, mat="iron", horn=True):
    """Horned anvil body standing on z = H - body height; face at H. L = face length along X."""
    h = 0.24
    z0 = H - h
    p.box((L * 0.55, w * 1.5, 0.06), T((0, 0, z0 + 0.03)), mat=mat, bevel=0)
    p.box((L * 0.35, w * 0.8, h - 0.12), T((0, 0, z0 + 0.06 + (h - 0.12) / 2)), mat=mat, bevel=0)
    p.box((L * 0.62, w, 0.07), T((-L * 0.05, 0, H - 0.035)), mat=mat, bevel=0.06)
    if horn:
        p.cyl(w * 0.48, 0.008, L * 0.4, T((L * 0.26, 0, H - 0.04)) @ M(rot=(0, 90, 0)) @ M(scale=(1.3, 1, 1)), mat=mat, segs=8)
    p.box((L * 0.12, w * 0.85, 0.05), T((-L * 0.4, 0, H - 0.03)), mat=mat, bevel=0)


def _anvil_primal(p, s, W, D, H):
    if s == "base":
        flagstone(p, W * 1.3, D * 1.3, 0.03, 0, mat="stone_dark", rough=0.2)
    elif s == "mechanism":
        rock(p, W * 0.45, D * 0.4, H * 0.5, (0, 0, H * 0.5), noise=0.02)
        flagstone(p, W * 0.7, D * 0.6, 0.04, H * 0.92, rough=0.12)
    elif s == "drive":
        rock(p, J(p, 0.07), 0.055, 0.05, (W * 0.25, -D * 0.1, H * 0.96 + 0.05), segs=(6, 4))
    elif s == "power":
        p.ball(0.04, M(loc=(-W * 0.1, 0, H * 0.96 + 0.025), scale=(J(p, 1.8, 0.2), 1, 0.6)), mat=lit(p), segs=(6, 4))
        coals(p, -W * 0.7, -D * 0.2, 0.02, 0.15, 4)
    else:
        for i in range(2):
            p.tube([(-W * 0.6 + i * 0.05, -D * 0.6, 0.01), (-W * 0.2 + i * 0.07, -D * 0.75, 0.012)], 0.012, mat="bone", segs=4)
        p.tube([(W * 0.5, D * 0.5, 0.02), (W * 0.9, D * 0.3, 0.02)], 0.02, mat="wood", segs=5)


def _anvil_stump(p, H, r, z1):
    p.cyl(r, r * 1.05, z1, mat="wood", segs=10, noise=0.02)
    p.cyl(r * 0.9, r * 0.9, 0.01, T((0, 0, z1)), mat="wood_dark", segs=10)


def _anvil_agrarian(p, s, W, D, H):
    z1 = H - 0.2
    if s == "base":
        _anvil_stump(p, H, W * 0.42, z1)
        p.ring(W * 0.43, 0.012, T((0, 0, z1 - 0.08)), mat="iron", segs=10)
    elif s == "mechanism":
        p.box((W * 0.45, D * 0.3, 0.2), T((0, 0, z1 + 0.1)), mat="iron", bevel=0.05)
        p.box((W * 0.52, D * 0.34, 0.03), T((0, 0, H - 0.015)), mat="iron", bevel=0)
    elif s == "drive":
        hammer(p, J(p, 0.05, 1), -D * 0.05, H, rot=J(p, 25, 0.5))
    elif s == "power":
        p.box((J(p, 0.22, 0.2), 0.022, 0.022), T((-W * 0.08, D * 0.08, H + 0.011)), mat=lit(p), bevel=0)
    else:
        tongs(p, W * 0.5, D * 0.25, 0.0, 0.5, rot=J(p, 60, 0.3))
        bucket(p, -W * 0.95, D * 0.2, 0.16, 0.34)


def _anvil_mercantile(p, s, W, D, H):
    z1 = H - 0.24
    if s == "base":
        _anvil_stump(p, H, W * 0.38, z1)
        for z in (0.08, z1 - 0.06):
            p.ring(W * 0.39 * (1.05 if z < 0.1 else 1.0), 0.012, T((0, 0, z)), mat="iron", segs=10)
    elif s == "mechanism":
        _horned(p, H, W * 0.9, D * 0.24)
    elif s == "drive":
        hammer(p, -W * 0.15, -D * 0.05, H, L=J(p, 0.32, 0.1), rot=J(p, -20, 0.6))
        p.box((0.025, 0.025, 0.07), T((-W * 0.35, 0, H + 0.035)), mat="iron", bevel=0)
    elif s == "power":
        p.tube([(W * 0.05, D * 0.06, H + 0.012), (W * 0.3, D * 0.04, H + 0.02), (W * 0.42, D * 0.05, H - 0.02)], 0.011, mat=lit(p), segs=4)
    else:
        for i in range(p.rng.randint(1, 2)):
            p.tube([(W * 0.38 * (1 if i else -1), -W * 0.35, z1 - 0.02), (W * 0.42 * (1 if i else -1), -W * 0.38, 0.25)], 0.006, mat="iron", segs=4)
        bucket(p, W * 0.65, D * 0.25, 0.17, 0.36)


def _anvil_industrial(p, s, W, D, H):
    z1 = H - 0.24
    if s == "base":
        for a in range(3):
            ang = a * TAU / 3 + 0.5
            p.tube([(math.cos(ang) * W * 0.45, math.sin(ang) * W * 0.45, 0), (math.cos(ang) * W * 0.18, math.sin(ang) * W * 0.18, z1 - 0.02)],
                   0.025, mat="steel", segs=6)
        p.cyl(W * 0.25, W * 0.25, 0.03, T((0, 0, z1 - 0.03)), mat="steel", segs=10)
    elif s == "mechanism":
        _horned(p, H, W * 0.95, D * 0.22, mat="steel")
    elif s == "drive":
        hammer(p, -W * 0.12, -D * 0.06, H, L=0.34, rot=J(p, 10, 1), head="steel", handle="rubber")
        if coin(p):
            p.box((0.03, 0.03, 0.08), T((-W * 0.33, 0, H + 0.04)), mat="steel", bevel=0)
    elif s == "power":
        p.box((J(p, 0.25, 0.2), 0.03, 0.012), T((W * 0.12, D * 0.06, H + 0.006)), mat=lit(p), bevel=0)
    else:  # chain hold-down and a tool rack hoop
        p.tube([(-W * 0.05, D * 0.12, H - 0.06), (-W * 0.1, D * 0.15, z1 - 0.1), (-W * 0.05, D * 0.12, z1 - 0.2)], 0.008, mat="iron", segs=4)
        p.ring(0.08, 0.008, T((0, W * 0.25 + 0.01, z1 - 0.1)) @ M(rot=(90, 0, 0)), mat="steel", segs=8)
        for i in range(2):
            p.tube([(-0.04 + i * 0.06, W * 0.28, z1 - 0.04), (-0.04 + i * 0.06, W * 0.28, z1 - 0.45)], 0.007, mat="steel", segs=4)


def _anvil_steampunk(p, s, W, D, H):  # steam hammer: arch frame, cylinder and ram over the anvil die
    top = H + 1.05
    if s == "base":
        p.box((W * 1.3, D, 0.1), T((0, 0, 0.05)), mat="iron", bevel=0.04)
        p.cyl(W * 0.25, W * 0.3, H - 0.18, T((0, 0, 0.1)), mat="iron", segs=10)
    elif s == "mechanism":
        p.box((W * 0.4, D * 0.4, 0.1), T((0, 0, H - 0.05)), mat="steel", bevel=0.05)
    elif s == "drive":
        for x in (-W * 0.55, W * 0.55):
            beam(p, (x, 0, 0.1), (x * 0.45, 0, top), 0.09, mat="brass")
        p.box((W * 0.7, 0.14, 0.12), T((0, 0, top)), mat="brass", bevel=0.05)
        p.cyl(0.11, 0.11, 0.35, T((0, 0, top + 0.06)), mat="brass", segs=10)
        p.ring(0.115, 0.015, T((0, 0, top + 0.2)), mat="copper", segs=10)
        rz = H + J(p, 0.25, 0.3)
        p.cyl(0.03, 0.03, top - rz, T((0, 0, rz)), mat="steel", segs=6)
        p.box((W * 0.3, D * 0.3, 0.14), T((0, 0, rz)), mat="iron", bevel=0.05)
    elif s == "power":
        boiler(p, W * 0.95, D * 0.15, 0, J(p, 0.17, 0.08), 0.7)
        p.box((J(p, 0.2, 0.2), 0.04, 0.025), T((0, -0.02, H + 0.013)), mat=lit(p), bevel=0)
    else:
        p.tube([(W * 0.95, D * 0.15, 0.87), (W * 0.95, D * 0.15, top + 0.3), (0.12, 0, top + 0.3), (0.0, 0, top + 0.4)],
               0.02, mat="copper", segs=6)
        gauge(p, W * 0.3, -0.08, top, 0.045)
        p.tube([(W * 0.5, -0.05, top - 0.2), (W * 0.7, -0.15, top - 0.45)], 0.012, mat="brass", segs=4)
        p.ball(0.025, T((W * 0.7, -0.15, top - 0.45)), mat="wood_dark", segs=(6, 4))


def _anvil_future(p, s, W, D, H):  # forming platform: pad with a glowing grid, press head on a C-arm
    top = H + 0.7
    if s == "base":
        shell_box(p, W, D, H - 0.08, (0, 0, 0), mat="body")
    elif s == "mechanism":
        shell_box(p, W * 0.8, D * 0.8, 0.08, (0, 0, H - 0.08), mat="shell_dark")
        for i in range(3):
            p.box((W * 0.7, 0.008, 0.004), T((0, (i - 1) * D * 0.2, H + 0.002)), mat="glow", bevel=0)
            p.box((0.008, D * 0.7, 0.004), T(((i - 1) * W * 0.2, 0, H + 0.002)), mat="glow", bevel=0)
    elif s == "drive":
        p.box((W * 0.2, 0.16, top - H + 0.1), T((0, D / 2 - 0.08, (H + top) / 2)), mat="body", bevel=0.2)
        p.box((W * 0.2, D * 0.55, 0.14), T((0, D * 0.2, top)), mat="body", bevel=0.2)
        p.cyl(J(p, 0.16, 0.12), 0.16, 0.08, T((0, -D * 0.02, top - 0.2)), mat="shell_dark", segs=10)
        p.ring(0.16, 0.012, T((0, -D * 0.02, top - 0.2)), mat="glow", segs=10)
    elif s == "power":
        coilcore(p, -W / 2 - 0.12, D * 0.2, 0, 0.1, J(p, 0.55, 0.15))
    else:
        p.box((0.22, 0.01, 0.14), M(loc=(W * 0.35, -D / 2 - 0.05, H + 0.15), rot=(-20, 0, 0)), mat="glow", bevel=0)
        p.box((0.02, 0.02, 0.15), T((W * 0.35, -D / 2 - 0.02, H + 0.04)), mat="shell_dark", bevel=0)
        p.tube([(-W / 2 - 0.12, D * 0.2 + 0.1, 0.02), (-W / 2, D / 2 + 0.05, 0.02), (0, D / 2 + 0.05, 0.02)], 0.02, mat="rubber", segs=5)


def _anvil_wasteland(p, s, W, D, H):  # rail-section anvil on a tyre stack
    z1 = H - 0.15
    if s == "base":
        n = 3
        for i in range(n):
            p.ring(W * 0.32, z1 / n * 0.5, T((0, 0, z1 / n * (i + 0.5))), mat="rubber", segs=12, square=False)
        p.cyl(W * 0.3, W * 0.3, 0.03, T((0, 0, z1 - 0.03)), mat="wood", segs=8, noise=0.02)
    elif s == "mechanism":  # rail profile along X
        out = [(-0.07, 0), (0.07, 0), (0.07, 0.02), (0.015, 0.035), (0.015, 0.1), (0.035, 0.11), (0.035, 0.15), (-0.035, 0.15),
               (-0.035, 0.11), (-0.015, 0.1), (-0.015, 0.035), (-0.07, 0.02)]
        p.plate(out, W * 0.85, T((0, 0, z1)) @ M(rot=(0, 0, 90)), mat="rust", bevel=0)
    elif s == "drive":
        p.box((0.06, 0.1, 0.06), T((W * 0.15, -D * 0.25, H + 0.03)), mat="steel", bevel=0)
        p.cyl(0.015, 0.015, 0.4, T((W * 0.15 - 0.2, -D * 0.25, H + 0.03)) @ M(rot=(0, 90, 0)), mat="steel", segs=6)
        wire(p, W * 0.15 - 0.15, -D * 0.25, H + 0.03, 0.018, axis="x")
    elif s == "power":
        p.box((J(p, 0.18, 0.2), 0.03, 0.02), T((-W * 0.1, 0, H + 0.01)), mat=lit(p), bevel=0)
        p.cyl(0.09, 0.09, 0.35, T((W * 0.6, D * 0.3, 0)), mat="paint", segs=8)
        p.lathe([(0.09, 0.35), (0.05, 0.4), (0.02, 0.42)], T((W * 0.6, D * 0.3, 0)), mat="paint", segs=8)
    else:
        for i in range(2):
            p.tube([(W * 0.3, -0.05 + i * 0.05, H - 0.04), (W * 0.38, -0.05 + i * 0.06, z1 - 0.2), (W * 0.35, -0.04 + i * 0.05, 0.25)],
                   0.008, mat="iron", segs=4)
        patch(p, 0.16, 0.12, T((0, -W * 0.33, z1 * 0.5)))


def _anvil_ancient(p, s, W, D, H):
    z1 = H - 0.25
    if s == "base":
        shell_box(p, W * 0.7, D * 0.6, z1, (0, 0, 0), mat="body")
    elif s == "mechanism":
        _horned(p, H, W * 0.95, D * 0.26, mat="stone", horn=False)
        p.cyl(D * 0.12, 0.01, W * 0.38, T((W * 0.26, 0, H - 0.05)) @ M(rot=(0, 90, 0)), mat="gold", segs=6)
    elif s == "drive":
        p.box((0.07, 0.14, 0.07), M(loc=(-W * 0.05, -D * 0.08, H + 0.035), rot=(0, 0, J(p, 20, 0.6))), mat="fit", bevel=0.2)
        p.box((0.3, 0.025, 0.025), M(loc=(-W * 0.05 - 0.15, -D * 0.08, H + 0.02), rot=(0, 0, J(p, 20, 0.6))), mat="fit", bevel=0)
    elif s == "power":
        runes(p, 0, -D * 0.3 - 0.006, 0.08, z1 - 0.05, n=3, w=0.05)
        p.box((W * 0.3, 0.02, 0.012), T((-W * 0.05, -D * 0.13, H - 0.04)), mat="glow", bevel=0)
    else:
        for x in (-W * 0.36, W * 0.36):
            p.box((0.05, D * 0.62, 0.04), T((x, 0, z1 * J(p, 0.7, 0.1))), mat="gold", bevel=0)


ANVIL = {"Primal": (_anvil_primal, 0.7, 0.6, 0.35), "Agrarian": (_anvil_agrarian, 0.6, 0.6, 0.75),
         "Mercantile": (_anvil_mercantile, 0.75, 0.6, 0.8), "Industrial": (_anvil_industrial, 0.75, 0.6, 0.82),
         "Steampunk": (_anvil_steampunk, 0.8, 0.6, 0.6), "Future": (_anvil_future, 0.8, 0.7, 0.8),
         "Wasteland": (_anvil_wasteland, 0.75, 0.6, 0.72), "Ancient": (_anvil_ancient, 0.75, 0.6, 0.8)}


@function("Anvil", "Machine", MACH, "machine")
def anvil(p, slot):
    fn, w, d, h = ANVIL[p.era]
    fn(p, slot, w * F(p, 1, 0.08), d * F(p, 1, 0.08), h * F(p, 1, 0.05))


# ================================================================ Millstone
def _stones(p, r, z0, h, lower="stone", upper="stone", eye=True, grooves=True):
    """Bed stone and runner stone stacked on z0, each h tall."""
    p.cyl(r, r, h, T((0, 0, z0)), mat=lower, segs=12, bevel=0.04)
    p.cyl(r * 0.97, r * 0.97, h, T((0, 0, z0 + h + 0.006)), mat=upper, segs=12, bevel=0.04)
    if eye:
        p.cyl(r * 0.18, r * 0.12, 0.012, T((0, 0, z0 + 2 * h)), mat="stone_dark", segs=8)
    if grooves:
        p.ring(r * 0.99, 0.006, T((0, 0, z0 + h + 0.003)), mat="stone_dark", segs=12)


def _mill_primal(p, s, W, D, H):  # saddle quern
    if s == "base":
        flagstone(p, W * 1.2, D * 1.3, 0.008, 0, mat="hide", n=7, rough=0.25, noise=0)
        for x in (-W * 0.3, W * 0.3):
            rock(p, 0.08, 0.07, 0.05, (x, 0, 0.04), segs=(5, 4))
    elif s == "mechanism":
        p.lathe([(0, 0.05), (0.22, 0.06), (0.25, 0.1), (0.24, H), (0.2, H - 0.02), (0, H - 0.04)],
                M(scale=(W / 0.5, D / 0.5 * 0.7, 1)), mat="stone", segs=10, noise=0.03)
    elif s == "drive":
        p.ball(1.0, M(loc=(J(p, 0.04, 1), -D * 0.05, H + 0.02), scale=(J(p, 0.1, 0.1), 0.17, 0.05)), mat="stone_dark", segs=(8, 4))
    elif s == "power":  # kneeling pad at the front end
        flagstone(p, 0.4, 0.3, 0.03, 0.008, mat="hide", n=6, rough=0.2, y=-D * 0.6 - 0.2, noise=0.02)
    else:
        pot(p, J(p, 0.1), 0.12, (W * 0.55, D * 0.1, 0.008), mat="bark")
        p.cyl(0.08, 0.02, 0.03, T((-W * 0.45, -D * 0.1, 0.008)), mat="bone", segs=8)


def _mill_agrarian(p, s, W, D, H):  # rotary push mill on a stone pedestal, long push pole
    r = 0.3
    z0 = H - 0.2
    hx = r + 0.05
    if s == "base":
        p.cyl(r * 1.35, r * 1.25, z0 - 0.08, mat="stone", segs=10, noise=0.02)
        p.lathe([(r * 1.4, z0 - 0.08), (r * 1.45, z0), (r * 1.15, z0), (r * 1.1, z0 - 0.04)], mat="stone", segs=12)
        p.box((0.12, 0.2, 0.05), T((0, -r * 1.45, z0 - 0.06)), mat="stone", bevel=0)
    elif s == "mechanism":
        _stones(p, r, z0 - 0.04, 0.12)
    elif s == "drive":
        p.box((0.05, 0.05, 0.12), T((hx, 0, z0 + 0.14)), mat="wood", bevel=0)
        p.cyl(0.02, 0.02, 0.08, T((0, 0, z0 + 0.2)), mat="iron", segs=6)
    elif s == "power":  # L push pole from the runner handle, hung from a rope at its crossbar end
        L = J(p, 1.0, 0.1)
        p.tube([(hx, 0, z0 + 0.2), (hx + L * 0.3, -0.04, z0 + 0.32), (hx + L, -0.06, z0 + 0.35)], 0.022, mat="wood", segs=6)
        p.cyl(0.02, 0.02, 0.6, T((hx + L, -0.36, z0 + 0.35)) @ M(rot=(-90, 0, 0)), mat="wood", segs=6)
        p.tube([(hx + L * 0.75, -0.1, 0), (hx + L * 0.75, -0.07, z0 + 0.28)], 0.018, mat="wood", segs=5)
        for sx in (-1, 1):
            p.tube([(hx + L * 0.75, -0.07, z0 + 0.24), (hx + L * 0.75 + sx * 0.05, -0.06, z0 + 0.38)], 0.01, mat="wood", segs=4)
    else:
        sack(p, -r * 1.6, r * 0.4, 0.17, 0.42)
        p.lathe([(0, 0), (0.15, 0.01), (0.2, 0.08), (0.18, 0.08)], T((0, -r * 1.6 - 0.12, 0)), mat="wood", segs=10)


def _mill_mercantile(p, s, W, D, H):  # animal mill: big stones on a round bed, central post, sweep with a yoke
    r = W * 0.38
    z0 = H - 0.3
    if s == "base":
        p.cyl(W / 2, W / 2, z0 - 0.04, mat="stone", segs=14, noise=0.01)
        p.ring(W / 2 - 0.02, 0.03, T((0, 0, z0 - 0.02)), mat="stone", segs=14)
    elif s == "mechanism":
        _stones(p, r, z0 - 0.04, 0.15)
        p.lathe([(r * 0.3, z0 + 0.3), (r * 0.55, z0 + 0.55), (r * 0.5, z0 + 0.57)], mat="wood", segs=8)
        for a in range(3):
            ang = a * TAU / 3 + 0.3
            p.tube([(math.cos(ang) * r * 0.5, math.sin(ang) * r * 0.5, z0 + 0.56), (math.cos(ang) * r * 0.7, math.sin(ang) * r * 0.7, z0 + 0.26)],
                   0.012, mat="wood", segs=4)
    elif s == "drive":  # spindle and an iron collar clamp
        p.cyl(0.04, 0.04, 0.32, T((0, 0, z0 + 0.26)), mat="wood", segs=8)
        p.box((r * 1.2, 0.08, 0.08), T((0, 0, z0 + 0.3)), mat="wood", bevel=0)
        for x in (-r * 0.6, r * 0.6):
            p.box((0.06, 0.06, 0.06), T((x, 0, z0 + 0.26)), mat="iron", bevel=0)
    elif s == "power":  # sweep beam out to the animal's yoke
        L = J(p, 1.15, 0.06)
        beam(p, (r * 0.5, 0, z0 + 0.3), (L, -0.08, z0 + 0.42), 0.08, mat="wood")
        p.ring(0.18, 0.025, T((L, -0.08, z0 + 0.3)) @ M(rot=(0, 90, 0)), mat="wood", segs=10, square=False)
        p.tube([(L, -0.08, z0 + 0.42), (L + 0.02, -0.1, z0 + 0.12), (L - 0.05, -0.06, 0.02)], 0.008, mat="leather", segs=4)
    else:
        sack(p, -W * 0.55, -W * 0.2, 0.18, 0.45)
        p.box((0.12, 0.25, 0.04), M(loc=(-r * 0.8, -r * 1.05, z0 - 0.04), rot=(-25, 0, 0)), mat="wood", bevel=0)
        if coin(p):
            sack(p, -W * 0.6, W * 0.15, 0.16, 0.4)


def _mill_industrial(p, s, W, D, H):  # roller mill: cast casing with hopper, flywheel, motor and belt
    zc = H * 0.55
    pul = (W / 2 + 0.12, 0, zc)
    if s == "base":
        for x in (-W * 0.4, W * 0.4):
            p.box((0.1, D * 0.9, zc - 0.25), T((x, 0, (zc - 0.25) / 2)), mat="iron", bevel=0)
        p.box((W, D, 0.05), T((0, 0, zc - 0.25)), mat="iron", bevel=0)
    elif s == "mechanism":
        p.box((W * 0.85, D * 0.8, 0.5), T((0, 0, zc)), mat="paint", bevel=0.04)
        p.lathe([(0.08, zc + 0.25), (W * 0.3, H - 0.05), (W * 0.32, H)], M(rot=(0, 0, 45)), mat="steel", segs=4)
        p.box((W * 0.5, 0.01, 0.1), T((0, -D * 0.4 - 0.004, zc + 0.08)), mat="glass", bevel=0)
    elif s == "drive":
        xcyl(p, 0.025, W * 0.3, (W * 0.5, 0, zc), mat="steel", segs=6)
        xwheel(p, J(p, 0.26, 0.08), (W / 2 + 0.05, 0, zc), rim="iron", hub="iron", spokes=6, t=0.025)
        xcyl(p, 0.1, 0.07, pul, mat="steel", segs=10)
    elif s == "power":
        mc = motor(p, W / 2 + 0.3, D * 0.1 + 0.1, 0, 0.12, 0.32)
        belt(p, pul, 0.1, (pul[0], mc[1], mc[2]), 0.07)
    else:  # outlet chute and a sack under it
        p.box((0.16, 0.25, 0.06), M(loc=(0, -D * 0.5, zc - 0.3), rot=(-35, 0, 0)), mat="steel", bevel=0)
        sack(p, J(p, 0.0, 1) + 0.02, -D * 0.6 - 0.05, 0.17, 0.42)


def _mill_steampunk(p, s, W, D, H):  # steam mill: cased stones, bevel gears, upright engine with boiler
    r = W * 0.35
    z0 = H - 0.5
    bx = W / 2 + 0.25
    if s == "base":
        p.box((W, D, 0.12), T((0, 0, 0.06)), mat="iron", bevel=0.05)
        p.cyl(r * 1.05, r * 1.1, z0 - 0.12, T((0, 0, 0.12)), mat="iron", segs=12)
        p.band(r * 1.08, z0 * 0.5, h=0.06)
    elif s == "mechanism":
        p.cyl(r * 1.1, r * 1.1, 0.3, T((0, 0, z0)), mat="brass", segs=12)
        p.lathe([(r * 1.1, z0 + 0.3), (r * 0.3, z0 + 0.38), (r * 0.5, z0 + 0.55), (r * 0.55, z0 + 0.58)], mat="brass", segs=12)
        p.band(r * 1.1, z0 + 0.15, h=0.06)
    elif s == "drive":  # vertical shaft, bevel gear pair, horizontal shaft to the engine
        p.cyl(0.03, 0.03, 0.35, T((0, 0, z0 + 0.38)), mat="steel", segs=6)
        gear(p, J(p, 0.11, 0.1), T((0, 0, z0 + 0.42)) @ M(rot=(90, 0, 0)), teeth=10, th=0.02)
        gear(p, 0.08, T((0.13, 0, z0 + 0.53)) @ M(rot=(0, 0, 90)), teeth=8, th=0.02)
        xcyl(p, 0.025, bx - 0.13, ((bx + 0.13) / 2, 0, z0 + 0.53), mat="steel", segs=6)
    elif s == "power":
        boiler(p, bx, 0.0, 0, J(p, 0.2, 0.08), z0 + 0.25)
    else:
        p.tube([(bx, 0, z0 + 0.25 + 0.13), (bx, 0, H + 0.2), (0, 0, H + 0.2), (0, 0, H)], 0.015, mat="copper", segs=6)
        gauge(p, r * 0.6, -r * 1.1, z0 + 0.15, 0.05)
        sack(p, -W * 0.5, -D * 0.5, 0.16, 0.4)


def _mill_future(p, s, W, D, H):  # pulveriser: rounded housing, glowing slot, funnel, coil core
    zc = H * 0.5
    if s == "base":
        shell_box(p, W, D, 0.1, (0, 0, 0), mat="shell_dark")
    elif s == "mechanism":
        p.box((W * 0.8, D * 0.75, zc * 1.5), T((0, 0, 0.1 + zc * 0.75)), mat="body")
        p.lathe([(0.1, 0.1 + zc * 1.5), (W * 0.32, H - 0.05), (W * 0.34, H)], mat="body", segs=12)
    elif s == "drive":  # crushing drum ring visible through the front
        p.ring(J(p, 0.17, 0.1), 0.03, T((0, -D * 0.38, zc)) @ M(rot=(90, 0, 0)), mat="shell_dark", segs=12)
        p.box((W * 0.5, 0.01, 0.04), T((0, -D * 0.38 - 0.005, zc + 0.3)), mat="glow", bevel=0)
    elif s == "power":
        coilcore(p, W / 2 + 0.12, D * 0.15, 0.1, 0.1, J(p, 0.5, 0.15))
    else:
        p.cyl(0.11, 0.11, 0.25, T((0, -D / 2 - 0.15, 0.1)), mat="glass", segs=10)
        p.cyl(0.115, 0.115, 0.03, T((0, -D / 2 - 0.15, 0.35)), mat="shell_dark", segs=10)
        p.box((0.08, 0.15, 0.06), T((0, -D / 2 - 0.05, 0.4)), mat="shell_dark", bevel=0.2)


def _mill_wasteland(p, s, W, D, H):  # drum grinder on crates, car-wheel crank, scrap motor
    zc = H * 0.6
    if s == "base":
        for x in (-W * 0.25, W * 0.25):
            p.box((0.38, D * 0.7, zc - 0.25), T((x, 0, (zc - 0.25) / 2)), mat="wood", bevel=0, noise=0.01)
    elif s == "mechanism":
        xcyl(p, 0.25, W * 0.8, (0, 0, zc), mat="rust", segs=10)
        p.lathe([(0.06, zc + 0.2), (0.25, H - 0.05), (0.27, H)], M(rot=(0, 0, 45)), mat="paint", segs=4)
        patch(p, 0.2, 0.15, T((W * 0.15, -0.255, zc)), mat="steel")
    elif s == "drive":
        xcyl(p, 0.02, W * 0.4, (W * 0.5, 0, zc), mat="steel", segs=6)
        xwheel(p, J(p, 0.22, 0.08), (W / 2 + 0.08, 0, zc), rim="steel", hub="steel", spokes=4, t=0.03)
    elif s == "power":  # crank handle with a pipe grip, lashed
        p.tube([(W / 2 + 0.12, 0, zc), (W / 2 + 0.14, -0.2, zc - 0.1)], 0.015, mat="steel", segs=5)
        p.cyl(0.02, 0.02, 0.15, T((W / 2 + 0.14, -0.2, zc - 0.1)) @ M(rot=(0, 90, 0)), mat="cloth", segs=6)
        wire(p, W / 2 + 0.12, 0, zc, 0.03, axis="x")
    else:
        p.cyl(0.14, 0.14, 0.3, T((0, -D * 0.55, 0)), mat="paint", segs=8)
        p.box((0.1, 0.25, 0.04), M(loc=(0, -D * 0.38, zc - 0.28), rot=(-30, 0, 0)), mat="steel", bevel=0)
        wire(p, -W * 0.3, 0, zc, 0.26, axis="x")


def _mill_ancient(p, s, W, D, H):
    r = W * 0.38
    z0 = H - 0.3
    if s == "base":
        p.cyl(W / 2, W / 2 * 0.95, z0 - 0.04, mat="body", segs=8, bevel=0.1)
    elif s == "mechanism":
        _stones(p, r, z0 - 0.04, 0.15, lower="body", upper="fit", grooves=False)
    elif s == "drive":
        p.cyl(0.04, 0.03, 0.2, T((0, 0, z0 + 0.26)), mat="gold", segs=6)
        p.ring(r * 0.98, 0.01, T((0, 0, z0 + 0.11)), mat="gold", segs=8)
    elif s == "power":
        for i in range(4):
            a = i * TAU / 4 + 0.4
            p.box((0.06, 0.012, 0.03), T((math.cos(a) * r * 0.98, math.sin(a) * r * 0.98, z0 + 0.19)) @ M(rot=(0, 0, math.degrees(a) + 90)),
                  mat="glow", bevel=0)
        p.ball(J(p, 0.05, 0.15), T((0, 0, z0 + 0.32)), mat="glow", segs=(8, 5))
    else:
        for x in (-W * 0.55, W * 0.55):
            shell_box(p, 0.14, 0.14, J(p, 0.75, 0.15), (x, 0, 0), mat="body")
            runes(p, x, -0.075, 0.15, 0.6, n=2, w=0.04)


MILL = {"Primal": (_mill_primal, 0.55, 0.32, 0.16), "Agrarian": (_mill_agrarian, 0.7, 0.7, 0.75),
        "Mercantile": (_mill_mercantile, 1.2, 1.2, 0.8), "Industrial": (_mill_industrial, 0.75, 0.6, 1.25),
        "Steampunk": (_mill_steampunk, 0.85, 0.75, 1.1), "Future": (_mill_future, 0.75, 0.65, 1.15),
        "Wasteland": (_mill_wasteland, 0.8, 0.6, 1.05), "Ancient": (_mill_ancient, 1.0, 1.0, 0.75)}


@function("Millstone", "Machine", MACH, "machine")
def millstone(p, slot):
    fn, w, d, h = MILL[p.era]
    fn(p, slot, w * F(p, 1, 0.08), d * F(p, 1, 0.08), h * F(p, 1, 0.05))


# ================================================================ Kiln
def _wares(p, n, x0, dx, y, z, r=0.07, mat="ceramic"):
    for i in range(n):
        pot(p, J(p, r, 0.2), J(p, r * 2.2, 0.2), (x0 + i * dx, y, z), mat=mat)


def _kiln_primal(p, s, W, D, H):  # pit firing: pots under a tepee of sticks
    R = W / 2
    if s == "base":
        p.ring(R, 0.06, T((0, 0, 0.02)), mat="stone_dark", segs=12, square=False, noise=0.05)
        p.cyl(R * 0.95, R * 0.95, 0.02, mat="stone_dark", segs=12)
    elif s == "mechanism":
        _wares(p, 3, -R * 0.35, R * 0.35, 0, 0.02, r=0.08)
    elif s == "drive":  # stick tepee
        n = p.rng.randint(7, 9)
        for i in range(n):
            a = i * TAU / n + p.rng.uniform(-0.15, 0.15)
            p.tube([(math.cos(a) * R * 0.85, math.sin(a) * R * 0.85, 0.02), (math.cos(a) * 0.05, math.sin(a) * 0.05, H)], 0.018, mat="wood", segs=4)
    elif s == "power":
        fire(p, -R * 0.4, -R * 0.4, 0.02, J(p, 0.07, 0.15))
        fire(p, R * 0.4, R * 0.2, 0.02, J(p, 0.06, 0.15), n=2)
    else:
        for i in range(p.rng.randint(2, 3)):
            a = p.rng.uniform(0, TAU)
            p.box((0.1, 0.07, 0.01), M(loc=(math.cos(a) * R * 1.3, math.sin(a) * R * 1.3, 0.005), rot=(0, 0, p.rng.uniform(0, 180))), mat="ceramic", bevel=0)
        pot(p, 0.09, 0.2, (R * 1.3, -R * 0.4, 0), mat="ceramic")


def _kiln_agrarian(p, s, W, D, H):  # updraft clay dome on an earth platform
    R = W / 2
    if s == "base":
        p.cyl(R * 1.1, R * 1.15, 0.15, mat="stone", segs=12, noise=0.02)
    elif s == "mechanism":
        p.lathe([(R, 0.15), (R * 0.98, H * 0.45), (R * 0.75, H * 0.8), (R * 0.3, H), (R * 0.2, H)], mat="ceramic", segs=12, noise=0.015)
    elif s == "drive":  # stoking arch and door slab
        p.plate([(-0.17, 0), (-0.17, 0.2), (-0.09, 0.3), (0, 0.32), (0.09, 0.3), (0.17, 0.2), (0.17, 0)], 0.1,
                T((0, -R * 0.96, 0.15)), mat="stone_dark", bevel=0)
        p.box((0.3, 0.04, 0.28), M(loc=(0.28, -R * 1.02, 0.29), rot=(0, 0, J(p, 15, 0.6))), mat="stone", bevel=0)
    elif s == "power":
        fire(p, 0, -R * 1.0, 0.16, J(p, 0.06, 0.12))
    else:
        p.cyl(R * 0.2, R * 0.16, J(p, 0.25, 0.2), T((0, 0, H - 0.02)), mat="ceramic", segs=8)
        logs(p, -R * 1.25, -R * 0.3, 0, 0.5, 0.04, n=2)
        _wares(p, p.rng.randint(1, 2), R * 1.1, 0.16, -R * 0.4, 0)


def _kiln_mercantile(p, s, W, D, H):  # climbing kiln: chambers stepping up along X, firebox low, chimney high
    n = 3
    cw = W / (n + 0.6)

    def cz(i):
        return 0.1 + i * 0.18

    if s == "base":
        for i in range(n):
            brick(p, cw + 0.02, D, cz(i), (-W / 2 + cw * (i + 0.8), 0, 0), n=1)
        brick(p, cw * 0.6, D * 0.8, 0.1, (-W / 2 + cw * 0.3, 0, 0), n=0)
    elif s == "mechanism":  # barrel vaults
        for i in range(n):
            vr = D * 0.45
            p.plate([(math.cos(a / 8 * math.pi) * vr, math.sin(a / 8 * math.pi) * vr) for a in range(9)], D * 0.9,
                    T((-W / 2 + cw * (i + 0.8), 0, cz(i))), mat="ceramic", bevel=0)
            p.box((cw * 0.06, D * 0.92, D * 0.42), T((-W / 2 + cw * (i + 0.3), 0, cz(i) + D * 0.21)), mat="ceramic", bevel=0)
    elif s == "drive":  # stoking ports with doors
        for i in range(n):
            x = -W / 2 + cw * (i + 0.8)
            p.box((0.14, 0.03, 0.16), T((x + J(p, 0.0, 1) * 0.1, -D * 0.44, cz(i) + D * 0.2)), mat="iron", bevel=0)
    elif s == "power":
        x = -W / 2 + cw * 0.3
        p.box((cw * 0.5, 0.02, 0.18), T((x, -D * 0.4 - 0.005, 0.2)), mat=lit(p), bevel=0)
        fire(p, x, -D * 0.42, 0.1, J(p, 0.06, 0.12), n=2, bed=False)
    else:
        x = W / 2 - cw * 0.2
        brick(p, 0.26, 0.26, J(p, 2.2, 0.06) - cz(n - 1), (x, 0, cz(n - 1)), n=4)
        _wares(p, 2, -W / 2 + cw * 1.8, 0.18, -D * 0.68, 0)


def _kiln_industrial(p, s, W, D, H):  # tunnel kiln: long box on a pad, rails, kiln car emerging
    zr = 0.12
    if s == "base":
        p.box((W, D, 0.1), T((0, 0, 0.05)), mat="stone_dark", bevel=0)
        for y in (-0.14, 0.14):
            p.box((W + 0.5, 0.03, 0.03), T((-0.25, y - 0.08, 0.115)), mat="steel", bevel=0)
    elif s == "mechanism":
        p.box((W * 0.85, D * 0.9, H - 0.1), T((W * 0.07, 0, 0.1 + (H - 0.1) / 2)), mat="ceramic", bevel=0.02)
        p.plate([(-0.25, 0), (-0.25, 0.4), (-0.15, 0.5), (0.15, 0.5), (0.25, 0.4), (0.25, 0)], 0.05,
                T((-W * 0.36, -0.08, 0.1)) @ M(rot=(0, 0, 90)), mat="stone_dark", bevel=0)
        for i in range(3):
            p.box((0.04, D * 0.92, H - 0.05), T((W * (-0.2 + i * 0.25), 0, 0.1 + (H - 0.1) / 2)), mat="steel", bevel=0)
    elif s == "drive":  # kiln car with stacked ware, coming out the -X end
        x = -W / 2 - J(p, 0.12, 0.3)
        p.box((0.45, 0.4, 0.08), T((x, -0.08, zr + 0.06)), mat="steel", bevel=0)
        for y in (-0.22, 0.06):
            for dx in (-0.15, 0.15):
                xcyl(p, 0.04, 0.03, (x + dx, y, zr + 0.04), mat="iron", segs=8)
        p.box((0.36, 0.32, 0.25), T((x, -0.08, zr + 0.22)), mat="ceramic", bevel=0)
    elif s == "power":  # burner ports along the front with a gas manifold
        for i in range(3):
            x = W * (-0.1 + i * 0.22)
            p.box((0.08, 0.02, 0.08), T((x, -D * 0.45 - 0.006, H * 0.45)), mat=lit(p), bevel=0)
            p.cyl(0.02, 0.02, 0.07, T((x, -D * 0.45, H * 0.3)) @ M(rot=(90, 0, 0)), mat="steel", segs=6)
        xcyl(p, 0.025, W * 0.7, (W * 0.12, -D * 0.45 - 0.07, H * 0.3), mat="paint", segs=6)
    else:
        flue(p, W * 0.38, D * 0.2, H, J(p, 2.3, 0.04), 0.1, mat="steel")
        gauge(p, W * 0.4, -D * 0.45 - 0.01, H * 0.7, 0.05)


def _kiln_steampunk(p, s, W, D, H):  # riveted dome kiln with a porthole door, boiler-fired
    R = D / 2
    bx = R + 0.3
    if s == "base":
        p.cyl(R * 1.1, R * 1.15, 0.2, mat="iron", segs=12)
        for i in range(4):
            a = i * TAU / 4 + 0.78
            p.cyl(0.04, 0.05, 0.08, T((math.cos(a) * R, math.sin(a) * R, 0.0)), mat="brass", segs=6)
    elif s == "mechanism":
        p.lathe([(R, 0.2), (R, H * 0.55), (R * 0.85, H * 0.8), (R * 0.4, H * 0.95), (R * 0.3, H)], mat="copper", segs=12)
        p.band(R, H * 0.35, h=0.08)
    elif s == "drive":  # round porthole door with a wheel lock
        c = (0, -R * 0.98, H * 0.42)
        p.cyl(0.2, 0.2, 0.05, T(c) @ M(rot=(90, 0, 0)), mat="brass", segs=12)
        p.ring(J(p, 0.09, 0.12), 0.01, T((c[0], c[1] - 0.06, c[2])) @ M(rot=(90, 0, 0)), mat="iron", segs=8)
        p.cyl(0.07, 0.07, 0.01, T((c[0], c[1] - 0.05, c[2])) @ M(rot=(90, 0, 0)), mat=lit(p), segs=10)
    elif s == "power":
        boiler(p, bx, R * 0.2, 0, J(p, 0.18, 0.08), H * 0.6)
    else:
        flue(p, 0, 0, H, J(p, 2.2, 0.04), R * 0.25, mat="copper")
        p.tube([(bx, R * 0.2, H * 0.6 + 0.12), (bx, R * 0.2, H * 0.75), (R * 0.6, 0, H * 0.75)], 0.018, mat="copper", segs=6)
        gauge(p, -R * 0.55, -R * 0.84, H * 0.6, 0.05)


def _kiln_future(p, s, W, D, H):  # plasma sintering cabinet: rounded chamber, glowing window, torch rings
    if s == "base":
        shell_box(p, W, D, 0.12, (0, 0, 0), mat="shell_dark")
    elif s == "mechanism":
        shell_box(p, W * 0.9, D * 0.85, H - 0.12, (0, 0, 0.12), mat="body")
        p.box((W * 0.55, 0.012, H * 0.4), T((0, -D * 0.425 - 0.004, H * 0.5)), mat="glow", bevel=0)
    elif s == "drive":  # sliding door frame on rails
        for z in (H * 0.27, H * 0.73):
            p.box((W * 0.9, 0.04, 0.03), T((0, -D * 0.425 - 0.02, z)), mat="shell_dark", bevel=0)
        p.box((0.05, 0.05, H * 0.2), T((W * 0.33, -D * 0.425 - 0.04, H * 0.5)), mat="shell_dark", bevel=0.2)
    elif s == "power":
        for x in (-W * 0.22, W * 0.22):
            coilcore(p, x, 0, H, 0.08, J(p, 0.2, 0.2), n=2)
    else:
        p.tube([(W * 0.45, D * 0.3, H - 0.1), (W * 0.6, D * 0.3, H - 0.1), (W * 0.6, D * 0.3, 0.02), (W * 0.8, D * 0.3, 0.02)], 0.03, mat="rubber", segs=6)
        p.ring(J(p, 0.12, 0.15), 0.02, T((0, D * 0.25, H + 0.02)), mat="shell_dark", segs=10)


def _kiln_wasteland(p, s, W, D, H):  # old fridge kiln on cinder blocks, propane torch
    if s == "base":
        for x in (-W * 0.3, W * 0.3):
            p.box((0.2, D * 0.9, 0.2), T((x, 0, 0.1)), mat="stone_dark", bevel=0, noise=0.01)
    elif s == "mechanism":
        p.box((W * 0.9, D, H - 0.2), T((0, 0, 0.2 + (H - 0.2) / 2)), mat="paint", bevel=0.03)
        patch(p, 0.25, 0.2, T((W * 0.2, -D / 2 - 0.004, H * 0.35)), mat="rust")
    elif s == "drive":  # hinged door, wire latch
        p.box((W * 0.85, 0.04, (H - 0.25) * J(p, 0.95, 0.03)), M(loc=(-W * 0.02, -D / 2 - 0.03, 0.22 + (H - 0.25) / 2), rot=(0, 0, J(p, 6, 0.6))), mat="steel", bevel=0)
        p.box((0.04, 0.05, 0.25), T((W * 0.38, -D / 2 - 0.06, H * 0.6)), mat="rubber", bevel=0)
    elif s == "power":
        p.cyl(0.13, 0.13, 0.4, T((W * 0.75, 0, 0)), mat="paint", segs=8)
        p.lathe([(0.13, 0.4), (0.06, 0.47), (0.03, 0.5)], T((W * 0.75, 0, 0)), mat="paint", segs=8)
        p.tube([(W * 0.75, 0, 0.5), (W * 0.6, 0.05, 0.55), (W * 0.48, 0, 0.35)], 0.008, mat="rubber", segs=4)
        flame(p, W * 0.46, 0, 0.32, 0.03, lean=70, mat=lit(p), segs=5)
    else:
        for i in range(3):
            p.cyl(0.07, 0.07, 0.25, T((-W * 0.25, 0, H + i * 0.24)) @ M(rot=(J(p, 2, 1), 0, 0)), mat="steel", segs=7)
        wire(p, -W * 0.25, 0, H + 0.22, 0.075)


def _kiln_ancient(p, s, W, D, H):
    R = W / 2
    if s == "base":
        p.cyl(R * 1.1, R * 1.1, 0.15, mat="body", segs=8, bevel=0.1)
    elif s == "mechanism":
        p.lathe([(R * 0.95, 0.15), (R * 0.95, H * 0.4), (R * 0.7, H * 0.8), (R * 0.25, H)], M(rot=(0, 0, 22.5)), mat="body", segs=8)
        p.ring(R * 0.96, 0.02, T((0, 0, H * 0.38)), mat="gold", segs=8)
    elif s == "drive":
        p.box((0.36, 0.08, 0.45), T((J(p, 0.0, 1) * 0.15, -R * 0.92, 0.15 + 0.23)), mat="fit", bevel=0.15)
    elif s == "power":
        for i in range(6):
            a = i * TAU / 6 + 0.5
            if math.sin(a) > -0.6:
                p.box((0.04, 0.012, 0.12), T((math.cos(a) * R * 0.92, math.sin(a) * R * 0.92, H * 0.55)) @ M(rot=(0, 0, math.degrees(a) + 90)), mat="glow", bevel=0)
        fire(p, 0, 0, H, J(p, 0.05, 0.15), n=2, bed=False)
    else:
        for x in (-R * 1.05, R * 1.05):
            shell_box(p, 0.14, 0.14, J(p, 1.2, 0.12), (x, R * 0.4, 0), mat="body")
            runes(p, x, R * 0.4 - 0.075, 0.2, 1.0, n=3, w=0.04)


KILN = {"Primal": (_kiln_primal, 1.0, 1.0, 0.65), "Agrarian": (_kiln_agrarian, 1.1, 1.1, 1.4),
        "Mercantile": (_kiln_mercantile, 2.2, 1.0, 1.2), "Industrial": (_kiln_industrial, 1.8, 0.95, 1.1),
        "Steampunk": (_kiln_steampunk, 1.1, 1.1, 1.4), "Future": (_kiln_future, 1.0, 0.85, 1.4),
        "Wasteland": (_kiln_wasteland, 0.75, 0.7, 1.55), "Ancient": (_kiln_ancient, 1.1, 1.1, 1.4)}


@function("Kiln", "Machine", MACH, "machine")
def kiln(p, slot):
    fn, w, d, h = KILN[p.era]
    fn(p, slot, w * F(p, 1, 0.08), d * F(p, 1, 0.08), h * F(p, 1, 0.05))


# ================================================================ Stove
def _cookpot(p, x, y, z, r, mat="iron"):
    p.lathe([(0, 0), (r * 0.7, 0), (r, r * 0.5), (r * 0.95, r * 1.0), (r * 1.02, r * 1.05)], T((x, y, z)), mat=mat, segs=10)
    p.cyl(r * 0.95, r * 0.95, 0.004, T((x, y, z + r * 0.9)), mat="glass", segs=10)


def _wok(p, x, y, z, r, mat="iron"):
    p.lathe([(0, z - r * 0.4), (r * 0.6, z - r * 0.3), (r, z + 0.01)], T((x, y, 0)), mat=mat, segs=10)
    for sx in (-1, 1):
        p.ring(0.025, 0.005, T((x + sx * r * 1.02, y, z)) @ M(rot=(0, 90, 0)), mat=mat, segs=6)


def _stove_primal(p, s, W, D, H):  # three-stone hearth
    if s == "base":
        flagstone(p, W, D, 0.02, 0, mat="stone_dark", rough=0.25, noise=0.02)
    elif s == "mechanism":
        for i in range(3):
            a = i * TAU / 3 - math.pi / 2
            rock(p, J(p, 0.1), J(p, 0.09), H * 0.5, (math.cos(a) * 0.17, math.sin(a) * 0.17, H * 0.5), segs=(6, 4))
    elif s == "drive":
        _cookpot(p, 0, 0, H - 0.02, J(p, 0.15, 0.1), mat="ceramic")
    elif s == "power":
        fire(p, 0, 0, 0.02, J(p, 0.05, 0.12))
        logs(p, 0, 0, 0.02, 0.4, 0.025, n=2)
    else:
        logs(p, W * 0.55, D * 0.3, 0, 0.45, 0.035, n=p.rng.choice((2, 3)))
        p.tube([(0.05, -0.05, H + 0.12), (0.3, -0.25, H + 0.45)], 0.01, mat="wood", segs=4)


def _stove_agrarian(p, s, W, D, H):  # mud stove with a pot hole and fire mouth
    if s == "base":
        p.box((W + 0.1, D + 0.1, 0.06), T((0, 0, 0.03)), mat="stone", bevel=0)
    elif s == "mechanism":
        p.box((W, D, H - 0.06), T((0, 0, 0.06 + (H - 0.06) / 2)), mat="ceramic", noise=0.012)
        p.ring(0.2, 0.025, T((-W * 0.1, 0, H)), mat="ceramic", segs=10)
    elif s == "drive":
        _wok(p, -W * 0.1, 0, H + 0.01, J(p, 0.22, 0.06))
        p.plate([(-0.13, 0), (-0.13, 0.12), (0, 0.2), (0.13, 0.12), (0.13, 0)], 0.04, T((-W * 0.1, -D / 2 - 0.01, 0.06)), mat="stone_dark", bevel=0)
    elif s == "power":
        fire(p, -W * 0.1, -D / 2 + 0.05, 0.07, J(p, 0.05, 0.12), n=2)
    else:
        p.cyl(0.08, 0.07, J(p, 0.5, 0.2), T((W * 0.35, D * 0.3, H)), mat="ceramic", segs=8)
        logs(p, -W * 0.5 - 0.2, -D * 0.3, 0, 0.4, 0.03, n=2)


def _stove_mercantile(p, s, W, D, H):  # brick range with two wok holes, two fire mouths and a chimney
    xs = (-W * 0.22, W * 0.22)
    if s == "base":
        brick(p, W + 0.06, D + 0.06, 0.15, (0, 0, 0), n=0)
    elif s == "mechanism":
        brick(p, W, D, H - 0.15, (0, 0, 0.15), n=2)
        p.box((W + 0.04, D + 0.04, 0.04), T((0, 0, H - 0.02)), mat="stone", bevel=0)
    elif s == "drive":
        for x in xs:
            _wok(p, x, -D * 0.05, H + 0.01, J(p, 0.18, 0.08))
            p.box((0.16, 0.02, 0.14), T((x, -D / 2 - 0.006, 0.3)), mat="iron", bevel=0)
    elif s == "power":
        for x in xs:
            p.box((0.13, 0.015, 0.1), T((x, -D / 2 - 0.018, 0.29)), mat=lit(p), bevel=0)
            coals(p, x, -D / 2 - 0.08, 0.15, 0.07, 3)
    else:
        brick(p, 0.24, 0.24, J(p, 2.0, 0.06) - H, (W * 0.38, D * 0.35, H), n=4)
        for i in range(p.rng.randint(1, 3)):  # bamboo steamer stack on the left wok
            p.cyl(0.16, 0.16, 0.07, T((-W * 0.22, -D * 0.05, H + 0.03 + i * 0.075)), mat="wood", segs=10)
        p.tube([(W * 0.05, -D * 0.4, H + 0.01), (W * 0.2, -D * 0.25, H + 0.06)], 0.008, mat="iron", segs=4)


def _stove_industrial(p, s, W, D, H):  # cast-iron range on legs, oven door, hob lids, stovepipe
    zb = 0.2
    if s == "base":
        for x in (-W / 2 + 0.06, W / 2 - 0.06):
            for y in (-D / 2 + 0.06, D / 2 - 0.06):
                p.lathe([(0.04, 0), (0.025, 0.05), (0.03, zb)], T((x, y, 0)), mat="iron", segs=6)
    elif s == "mechanism":
        p.box((W, D, H - zb - 0.03), T((0, 0, zb + (H - zb - 0.03) / 2)), mat="iron", bevel=0.03)
        p.box((W + 0.04, D + 0.02, 0.03), T((0, 0, H - 0.015)), mat="steel", bevel=0)
        p.box((W + 0.06, 0.03, 0.02), T((0, -D / 2 - 0.04, H - 0.12)), mat="steel", bevel=0)
    elif s == "drive":  # oven door, firebox door, hob lids and knobs
        p.box((W * 0.45, 0.025, (H - zb) * 0.55), T((W * 0.2, -D / 2 - 0.01, zb + (H - zb) * 0.38)), mat="iron", bevel=0.05)
        p.box((0.16, 0.012, 0.012), T((W * 0.2, -D / 2 - 0.035, zb + (H - zb) * 0.62)), mat="steel", bevel=0)
        for x in (-W * 0.25, W * 0.2):
            p.cyl(J(p, 0.09, 0.1), 0.09, 0.008, T((x, 0, H)), mat="iron", segs=10)
        p.cyl(0.02, 0.02, 0.03, T((-W * 0.25, -D / 2 - 0.0, zb + (H - zb) * 0.75)) @ M(rot=(90, 0, 0)), mat="steel", segs=6)
    elif s == "power":
        p.box((W * J(p, 0.25, 0.1), 0.02, (H - zb) * 0.3), T((-W * 0.25, -D / 2 - 0.005, zb + (H - zb) * 0.35)), mat=lit(p), bevel=0)
        coals(p, -W * 0.25, -D * 0.3, zb + (H - zb) * 0.22, 0.08, 3)
    else:
        flue(p, W * 0.35, D * 0.3, H, J(p, 2.0, 0.08), 0.07, mat="iron", cap=False)
        _cookpot(p, -W * 0.25, 0, H + 0.008, 0.1, mat="steel")
        if coin(p):
            p.tube([(-W * 0.25 + 0.09, 0, H + 0.08), (-W * 0.25 + 0.18, 0, H + 0.12)], 0.008, mat="steel", segs=4)


def _stove_steampunk(p, s, W, D, H):  # brass range with a back boiler, valves and pipes
    zb = 0.15
    if s == "base":
        p.box((W + 0.06, D + 0.06, zb), T((0, 0, zb / 2)), mat="iron", bevel=0.05)
    elif s == "mechanism":
        p.box((W, D, H - zb), T((0, 0, zb + (H - zb) / 2)), mat="brass", bevel=0.04)
        p.box((W + 0.02, D + 0.02, 0.025), T((0, 0, H * 0.55)), mat="copper", bevel=0)
    elif s == "drive":
        for x in (-W * 0.25, W * 0.15):
            p.cyl(J(p, 0.1, 0.1), 0.1, 0.01, T((x, -D * 0.05, H)), mat="iron", segs=10)
        for i in range(3):
            x = -W * 0.3 + i * 0.15
            p.ring(0.03, 0.006, T((x, -D / 2 - 0.03, H * 0.8)) @ M(rot=(90, 0, 0)), mat="copper", segs=8)
            p.cyl(0.006, 0.006, 0.03, T((x, -D / 2, H * 0.8)) @ M(rot=(90, 0, 0)), mat="brass", segs=4)
    elif s == "power":
        boiler(p, W * 0.35, D * 0.55, 0, J(p, 0.15, 0.08), H + 0.2)
        p.box((W * 0.4, 0.02, (H - zb) * 0.3), T((-W * 0.1, -D / 2 - 0.005, zb + (H - zb) * 0.25)), mat=lit(p), bevel=0)
    else:
        flue(p, -W * 0.35, D * 0.35, H, J(p, 1.9, 0.08), 0.06, mat="copper")
        p.tube([(W * 0.35, D * 0.55, H + 0.32), (W * 0.35, D * 0.55, H + 0.45), (W * 0.15, D * 0.1, H + 0.45), (W * 0.15, -D * 0.05, H + 0.2)],
               0.015, mat="copper", segs=6)
        gauge(p, W * 0.3, -D / 2, H * 0.35, 0.05)


def _stove_future(p, s, W, D, H):  # induction counter
    if s == "base":
        shell_box(p, W * 0.94, D * 0.9, 0.1, (0, 0.02, 0), mat="shell_dark")
    elif s == "mechanism":
        shell_box(p, W, D, H - 0.1, (0, 0, 0.1), mat="body")
        p.box((W + 0.02, D + 0.02, 0.025), T((0, 0, H - 0.012)), mat="shell_dark", bevel=0.2)
    elif s == "drive":  # touch strip on the front edge
        p.box((W * 0.5, 0.01, 0.05), T((0, -D / 2 - 0.006, H - 0.06)), mat="shell_dark", bevel=0)
        for i in range(4):
            p.box((0.02, 0.012, 0.02), T((-W * 0.18 + i * W * 0.12, -D / 2 - 0.01, H - 0.06)), mat="glow", bevel=0)
    elif s == "power":
        for x, r in ((-W * 0.25, 0.12), (W * 0.22, 0.1)):
            p.ring(J(p, r, 0.1), 0.008, T((x, 0, H + 0.002)), mat="glow", segs=12)
            p.ring(r * 0.55, 0.006, T((x, 0, H + 0.002)), mat="glow", segs=10)
    else:
        _cookpot(p, -W * 0.25, 0, H + 0.004, J(p, 0.1, 0.1), mat="steel")
        p.box((0.25, 0.12, 0.02), T((W * 0.22, D * 0.15, H + 0.01)), mat="wood", bevel=0)


def _stove_wasteland(p, s, W, D, H):  # drum stove on rebar legs with a grill and can flue
    r = D / 2
    zc = H - r
    if s == "base":
        for x in (-W * 0.35, W * 0.35):
            for y in (-r * 0.6, r * 0.6):
                p.tube([(x, y * 1.3, 0), (x * 0.95, y, zc - r * 0.7)], 0.012, mat="rust", segs=4)
    elif s == "mechanism":
        xcyl(p, r, W, (0, 0, zc), mat="rust", segs=10)
        patch(p, 0.18, 0.12, T((W * 0.25, -r * 0.95, zc + 0.05)) @ M(rot=(-15, 0, 0)), mat="paint")
    elif s == "drive":
        p.box((W * 0.85, r * 1.3, 0.012), T((0, 0, H + 0.02)), mat="iron", bevel=0)
        for i in range(5):
            p.box((0.01, r * 1.3, 0.02), T((-W * 0.35 + i * W * 0.175, 0, H + 0.01)), mat="iron", bevel=0)
        p.box((0.22, 0.02, 0.16), M(loc=(-W * 0.25, -r - 0.05, zc - 0.04), rot=(0, 0, J(p, 25, 0.5))), mat="steel", bevel=0)
    elif s == "power":
        fire(p, -W * 0.25, -r * 0.5, zc - r * 0.5, J(p, 0.05, 0.12), n=2)
        p.box((0.2, 0.02, 0.14), T((-W * 0.25, -r * 0.96, zc - 0.04)), mat=lit(p), bevel=0)
    else:
        for i in range(3):
            p.cyl(0.06, 0.06, 0.22, T((W * 0.38, r * 0.3, H - 0.05 + i * 0.21)) @ M(rot=(J(p, 2, 1), 0, 0)), mat="steel", segs=7)
        wire(p, W * 0.38, r * 0.3, H + 0.15, 0.065)
        _cookpot(p, -W * 0.05, 0, H + 0.028, 0.09, mat="steel")


def _stove_ancient(p, s, W, D, H):
    if s == "base":
        shell_box(p, W, D, 0.12, (0, 0, 0), mat="fit")
    elif s == "mechanism":
        shell_box(p, W * 0.92, D * 0.88, H - 0.12, (0, 0, 0.12), mat="body")
    elif s == "drive":
        for x in (-W * 0.22, W * 0.22):
            p.ring(J(p, 0.12, 0.1), 0.015, T((x, 0, H + 0.004)), mat="gold", segs=8)
    elif s == "power":
        for x in (-W * 0.22, W * 0.22):
            p.cyl(0.08, 0.08, 0.006, T((x, 0, H)), mat="glow", segs=8)
        runes(p, 0, -D * 0.44 - 0.006, 0.2, H - 0.1, n=3, w=0.05)
    else:
        p.lathe([(0, 0), (0.1, 0.01), (0.13, 0.1), (0.1, 0.18), (0.11, 0.2)], T((-W * 0.22, 0, H + 0.01)), mat="fit", segs=8)
        shell_box(p, 0.14, 0.14, J(p, 0.5, 0.2), (W * 0.42, D * 0.35, H), mat="body")


STOVE = {"Primal": (_stove_primal, 0.8, 0.8, 0.22), "Agrarian": (_stove_agrarian, 0.9, 0.65, 0.65),
         "Mercantile": (_stove_mercantile, 1.3, 0.75, 0.8), "Industrial": (_stove_industrial, 1.0, 0.65, 0.85),
         "Steampunk": (_stove_steampunk, 1.0, 0.65, 0.85), "Future": (_stove_future, 1.2, 0.65, 0.9),
         "Wasteland": (_stove_wasteland, 0.9, 0.55, 0.75), "Ancient": (_stove_ancient, 1.1, 0.7, 0.85)}


@function("Stove", "Machine", MACH, "machine")
def stove(p, slot):
    fn, w, d, h = STOVE[p.era]
    fn(p, slot, w * F(p, 1, 0.08), d * F(p, 1, 0.08), h * F(p, 1, 0.05))


# ================================================================ Still
def _still_primal(p, s, W, D, H):  # clay pot over a fire, bowl of cold water on the lid, reed spout to a gourd
    zp = 0.18
    r = 0.2
    if s == "base":
        for i in range(3):
            a = i * TAU / 3 - math.pi / 2
            rock(p, 0.09, 0.08, zp * 0.55, (math.cos(a) * r * 0.9, math.sin(a) * r * 0.9, zp * 0.5), segs=(6, 4))
    elif s == "mechanism":
        p.lathe([(0, zp), (r * 0.8, zp + 0.02), (r, zp + 0.2), (r * 0.85, zp + 0.38), (r * 0.6, zp + 0.42)], mat="ceramic", segs=10)
    elif s == "drive":  # condensing lid bowl and a reed pipe
        p.lathe([(r * 0.6, zp + 0.42), (r * 0.95, zp + 0.5), (r * 1.0, zp + 0.56), (0, zp + 0.48)], mat="ceramic", segs=10)
        p.tube([(r * 0.6, 0, zp + 0.4), (r * 1.7, -0.05, zp + 0.25), (W * 0.5, -0.08, zp * 0.6)], 0.012, mat="wood", segs=5)
    elif s == "power":
        fire(p, 0, 0, 0.0, J(p, 0.06, 0.12))
    else:
        p.lathe([(0, 0), (0.07, 0.03), (0.08, 0.1), (0.035, 0.16), (0.02, 0.2)], T((W * 0.52, -0.08, 0)), mat="bark", segs=8)
        p.cyl(r * 0.85, r * 0.85, 0.004, T((0, 0, zp + 0.53)), mat="glass", segs=10)


def _still_agrarian(p, s, W, D, H):  # copper alembic on a stone firebox, swan neck to a worm tub
    r = 0.26
    zp = 0.4
    tx = W / 2 - 0.2
    if s == "base":
        p.cyl(r * 1.15, r * 1.2, zp, mat="stone", segs=10, noise=0.02)
        p.plate([(-0.11, 0), (-0.11, 0.12), (0, 0.18), (0.11, 0.12), (0.11, 0)], 0.04, T((0, -r * 1.12, 0)), mat="stone_dark", bevel=0)
    elif s == "mechanism":
        p.lathe([(r * 0.9, zp), (r, zp + 0.15), (r * 0.95, zp + 0.3), (r * 0.4, zp + 0.42), (r * 0.25, zp + 0.45)], mat="copper", segs=12)
    elif s == "drive":
        p.lathe([(r * 0.25, zp + 0.45), (r * 0.6, zp + 0.55), (r * 0.5, zp + 0.68), (r * 0.12, zp + 0.75)], mat="copper", segs=10)
        p.tube([(0, 0, zp + 0.74), (0.15, 0, zp + 0.82), (tx - 0.15, 0, zp + 0.55), (tx, 0, H * 0.55)], 0.018, mat="copper", segs=6)
    elif s == "power":
        fire(p, 0, -r * 1.05, 0.0, J(p, 0.05, 0.12), n=2)
    else:
        p.cyl(0.2, 0.22, H * 0.55, T((tx, 0, 0)), mat="wood", segs=10)
        for k in (0.2, 0.8):
            p.ring(0.215, 0.006, T((tx, 0, H * 0.55 * k)), mat="iron", segs=10)
        p.cyl(0.01, 0.01, 0.1, T((tx, -0.2, 0.1)) @ M(rot=(90, 0, 0)), mat="copper", segs=5)
        p.lathe([(0, 0), (0.07, 0.01), (0.08, 0.1), (0.03, 0.15)], T((tx, -0.32, 0)), mat="ceramic", segs=8)


def _still_mercantile(p, s, W, D, H):  # glass set on a bench: retort over a lamp, long neck into a receiver
    zt = H * 0.55
    rx, fx = -W * 0.25, W * 0.3
    if s == "base":
        p.box((W, D, 0.04), T((0, 0, zt - 0.02)), mat="body", bevel=0.05)
        for x in (-W / 2 + 0.05, W / 2 - 0.05):
            for y in (-D / 2 + 0.05, D / 2 - 0.05):
                p.box((0.05, 0.05, zt - 0.04), T((x, y, (zt - 0.04) / 2)), mat="body", bevel=0)
        p.box((W - 0.1, 0.03, 0.03), T((0, D / 2 - 0.05, 0.12)), mat="body", bevel=0)
    elif s == "mechanism":  # retort on a ring stand
        p.cyl(0.006, 0.006, 0.45, T((rx - 0.14, 0, zt)), mat="brass", segs=4)
        p.ring(0.08, 0.006, T((rx, 0, zt + 0.17)), mat="brass", segs=10)
        p.ball(J(p, 0.1, 0.1), T((rx, 0, zt + 0.26)), mat="glass", segs=(10, 6))
    elif s == "drive":
        p.tube([(rx, 0, zt + 0.34), (rx + 0.06, 0, zt + 0.42), (fx - 0.06, 0, zt + 0.22)], 0.012, mat="glass", segs=5)
        p.tube([(rx - 0.14, 0, zt + 0.42), (rx + 0.12, 0, zt + 0.42)], 0.005, mat="brass", segs=4)
    elif s == "power":
        p.lathe([(0, zt), (0.05, zt), (0.055, zt + 0.04), (0.015, zt + 0.07)], T((rx, 0, 0)), mat="brass", segs=8)
        flame(p, rx, 0, zt + 0.07, J(p, 0.018, 0.15), mat=lit(p), segs=6)
    else:
        p.lathe([(0, zt), (0.08, zt + 0.02), (0.09, zt + 0.1), (0.04, zt + 0.18), (0.02, zt + 0.22)], T((fx, 0, 0)), mat="glass", segs=10)
        for i in range(p.rng.randint(2, 3)):
            p.lathe([(0, zt), (0.035, zt), (0.035, zt + 0.12), (0.012, zt + 0.15), (0.012, zt + 0.18)],
                    T((-W * 0.4 + i * 0.09, D * 0.25, 0)), mat="glass", segs=6)


def _still_industrial(p, s, W, D, H):  # column still on a skid: pot, plated column, condenser
    px, cx = -W * 0.25, W * 0.25
    if s == "base":
        for y in (-D / 2 + 0.05, D / 2 - 0.05):
            p.box((W, 0.08, 0.1), T((0, y, 0.05)), mat="steel", bevel=0)
        for x in (-W / 2 + 0.05, W / 2 - 0.05):
            p.box((0.08, D, 0.06), T((x, 0, 0.13)), mat="steel", bevel=0)
    elif s == "mechanism":
        p.cyl(0.25, 0.25, 0.5, T((px, 0, 0.3)), mat="steel", segs=12)
        p.lathe([(0.25, 0.8), (0.18, 0.9), (0.1, 0.94)], T((px, 0, 0)), mat="steel", segs=12)
        p.cyl(0.11, 0.11, H - 0.94, T((px, 0, 0.94)), mat="copper", segs=10)
        for i in range(4):
            p.ring(0.115, 0.01, T((px, 0, 1.0 + i * (H - 1.1) / 4)), mat="steel", segs=10)
    elif s == "drive":
        p.tube([(px, 0, H), (px, 0, H + 0.12), (cx, 0, H + 0.12), (cx, 0, H * 0.7)], 0.03, mat="copper", segs=6)
        p.ring(0.05, 0.008, T((px + 0.1, -0.03, 0.55)) @ M(rot=(90, 0, 0)), mat="paint", segs=8)
    elif s == "power":  # gas burner under the pot
        for x in (-0.12, 0.12):
            p.box((0.04, 0.3, 0.12), T((px + x, 0, 0.22)), mat="iron", bevel=0)
        coals(p, px, 0, 0.17, 0.16, 5)
        p.tube([(px, -0.15, 0.19), (px, -D / 2 - 0.05, 0.19), (px - 0.3, -D / 2 - 0.05, 0.19)], 0.015, mat="paint", segs=5)
    else:
        p.cyl(0.13, 0.13, H * 0.45, T((cx, 0, H * 0.25)), mat="steel", segs=10)
        for sx in (-1, 1):
            p.box((0.04, 0.04, H * 0.25 - 0.16), T((cx + sx * 0.13, 0.08, 0.16 + (H * 0.25 - 0.16) / 2)), mat="steel", bevel=0)
        p.cyl(0.18, 0.18, 0.25, T((cx, -0.1, 0.0)), mat="steel", segs=10)
        p.tube([(cx, 0, H * 0.25), (cx, -0.1, 0.25)], 0.015, mat="copper", segs=5)
        gauge(p, px, -0.25, 0.6, 0.05)


def _still_steampunk(p, s, W, D, H):  # brass still: boiler pot, coiled tube in a sight glass, gauges
    px, cx = -W * 0.25, W * 0.28
    if s == "base":
        p.box((W, D, 0.12), T((0, 0, 0.06)), mat="iron", bevel=0.05)
    elif s == "mechanism":
        p.lathe([(0.24, 0.12), (0.28, 0.35), (0.26, 0.6), (0.15, 0.75), (0.08, 0.8)], T((px, 0, 0)), mat="brass", segs=12)
        p.band(0.27, 0.45, h=0.07)
    elif s == "drive":  # helmet dome and a coiled lyne
        p.lathe([(0.08, 0.8), (0.15, 0.9), (0.12, 1.0), (0.03, 1.05)], T((px, 0, 0)), mat="copper", segs=10)
        pts = [(px, 0, 1.03), (px + 0.2, 0, 1.15)]
        for i in range(9):
            a = i * TAU / 4.5
            pts.append((cx + math.cos(a) * 0.08, math.sin(a) * 0.08, H * 0.85 - i * 0.06))
        p.tube(pts, 0.012, mat="copper", segs=4)
    elif s == "power":  # firebox under the pot
        p.box((0.36, 0.3, 0.12), T((px, 0, 0.06 + 0.06)), mat="iron", bevel=0)
        p.box((0.2, 0.02, 0.08), T((px, -0.155, 0.12)), mat=lit(p), bevel=0)
    else:
        p.cyl(0.12, 0.12, H * 0.6, T((cx, 0, 0.12)), mat="glass", segs=10)
        for z in (0.12, H * 0.72):
            p.cyl(0.14, 0.14, 0.04, T((cx, 0, z)), mat="brass", segs=10)
        gauge(p, px, -0.27, 0.55, 0.05)
        gauge(p, cx, -0.14, H * 0.78, 0.04)


def _still_future(p, s, W, D, H):  # molecular separator: column with glowing stages, manifold, vials
    if s == "base":
        shell_box(p, W, D, 0.1, (0, 0, 0), mat="shell_dark")
    elif s == "mechanism":
        p.lathe([(0, 0.1), (0.2, 0.1), (0.22, 0.3), (0.16, H - 0.1), (0.12, H), (0, H + 0.02)], mat="body", segs=12)
    elif s == "drive":
        for i in range(3):
            p.ring(0.2 - i * 0.015, 0.015, T((0, 0, 0.5 + i * (H - 0.7) / 3)), mat="glow", segs=12)
        p.tube([(0.15, 0, H - 0.15), (W * 0.4, 0, H - 0.15), (W * 0.4, 0, 0.4)], 0.02, mat="shell_dark", segs=6)
    elif s == "power":
        coilcore(p, -W * 0.38, D * 0.1, 0.1, 0.08, J(p, 0.5, 0.2), n=2)
    else:
        shell_box(p, 0.25, 0.15, 0.3, (W * 0.4, 0, 0.1), mat="body")
        for i in range(3):
            p.cyl(0.018, 0.018, 0.1, T((W * 0.4 - 0.07 + i * 0.07, -0.02, 0.4)), mat="glass", segs=6)
        p.box((0.15, 0.01, 0.08), T((W * 0.4, -0.08, 0.25)), mat="glow", bevel=0)


def _still_wasteland(p, s, W, D, H):  # pressure-cooker still on a grill, radiator condenser, jerrycans
    px = -W * 0.25
    zg = 0.35
    if s == "base":
        for x in (-0.12, 0.12):
            p.box((0.15, 0.35, zg), T((px + x * 1.3, 0, zg / 2)), mat="stone_dark", bevel=0, noise=0.01)
        p.box((0.45, 0.35, 0.01), T((px, 0, zg + 0.005)), mat="iron", bevel=0)
    elif s == "mechanism":
        p.cyl(0.18, 0.18, 0.3, T((px, 0, zg + 0.01)), mat="steel", segs=10)
        p.cyl(0.185, 0.17, 0.04, T((px, 0, zg + 0.31)), mat="steel", segs=10)
        p.box((0.15, 0.03, 0.02), T((px + 0.25, 0, zg + 0.31)), mat="rubber", bevel=0)
    elif s == "drive":  # copper pipe to a car radiator
        p.tube([(px, 0, zg + 0.35), (px, 0, zg + 0.5), (W * 0.3, 0, zg + 0.5), (W * 0.3, 0, H * 0.75)], 0.012, mat="copper", segs=5)
        p.box((0.4, 0.06, 0.4), T((W * 0.3, 0, H * 0.75 - 0.2)), mat="steel", bevel=0)
        for i in range(5):
            p.box((0.38, 0.065, 0.008), T((W * 0.3, 0, H * 0.75 - 0.36 + i * 0.07)), mat="iron", bevel=0)
    elif s == "power":
        fire(p, px, 0, 0.0, J(p, 0.06, 0.12), n=2)
    else:
        for x in (W * 0.3 - 0.15, W * 0.3 + 0.15):
            p.box((0.03, 0.03, H * 0.75 - 0.4), T((x, 0, (H * 0.75 - 0.4) / 2)), mat="rust", bevel=0)
        p.box((0.16, 0.08, 0.22), T((W * 0.3, -D * 0.3, 0.11)), mat="paint", bevel=0)
        p.cyl(0.06, 0.06, 0.12, T((W * 0.3 + 0.18, -D * 0.25, 0)), mat="glass", segs=8)
        wire(p, px, 0, zg + 0.15, 0.19)


def _still_ancient(p, s, W, D, H):
    if s == "base":
        p.cyl(W * 0.45, W * 0.45, 0.15, mat="body", segs=8, bevel=0.1)
    elif s == "mechanism":
        p.lathe([(0.22, 0.15), (0.3, 0.4), (0.26, 0.65), (0.12, 0.8)], M(rot=(0, 0, 22.5)), mat="body", segs=8)
    elif s == "drive":
        pts = [(math.cos(i * 0.9) * 0.12, math.sin(i * 0.9) * 0.12, 0.8 + i * 0.05) for i in range(12)]
        p.tube(pts, 0.015, mat="gold", segs=4)
        p.tube([pts[-1], (W * 0.35, 0, H * 0.9), (W * 0.38, -0.05, 0.4)], 0.015, mat="gold", segs=4)
    elif s == "power":
        p.ball(J(p, 0.07, 0.15), T((0, 0, H * 0.82 + 0.4)), mat="glow", segs=(8, 5))
        runes(p, 0, -0.29, 0.25, 0.65, n=3, w=0.05)
    else:
        p.lathe([(0, 0), (0.12, 0.01), (0.15, 0.2), (0.12, 0.3)], T((W * 0.38, -0.05, 0)), mat="fit", segs=8)
        shell_box(p, 0.12, 0.12, J(p, 0.6, 0.2), (-W * 0.4, 0, 0), mat="body")


STILL = {"Primal": (_still_primal, 1.0, 0.6, 0.6), "Agrarian": (_still_agrarian, 1.3, 0.6, 1.3),
         "Mercantile": (_still_mercantile, 1.1, 0.55, 1.4), "Industrial": (_still_industrial, 1.2, 0.7, 2.2),
         "Steampunk": (_still_steampunk, 1.1, 0.65, 1.5), "Future": (_still_future, 0.9, 0.6, 1.6),
         "Wasteland": (_still_wasteland, 1.1, 0.6, 1.4), "Ancient": (_still_ancient, 1.0, 0.7, 1.2)}


@function("Still", "Machine", MACH, "machine")
def still(p, slot):
    fn, w, d, h = STILL[p.era]
    fn(p, slot, w * F(p, 1, 0.08), d * F(p, 1, 0.08), h * F(p, 1, 0.05))
