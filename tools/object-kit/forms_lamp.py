"""Lamp family forms (燈具: 燈體、光源、罩、掛鉤／底座): Torch, Lantern, Candlestand, Streetlamp, Headlamp, Censer.

Slots: body (燈體), light (光源), shade (罩), mount (掛鉤／底座). Lamps always glow (everyday-objects.md 發光), so the
light slot uses a glow material in every era, including the ones whose craft STYLE has none: flames and embers
are glow_amber, early electric bulbs glow_dim. Enclosed lamps make their lit glass, paper or crystal the light slot
itself, because the game draws glass opaque and a flame behind it would read as an unlit lamp.
Frames: the torch stands on +Z with the grip at the origin (hafted convention); every other lamp sits on z = 0
facing -Y (device / vessel convention), which is also the floor contact when the game stands it in a scene.
"""
import math

from mathutils import Matrix

from kit_forms import F, J, coin, function
from kit_lib import M

LAMP = ("body", "light", "shade", "mount")
T = Matrix.Translation


def lit(p, electric=False):
    """Glow material of the light source: the era's own glow, else a flame (amber) or an early bulb (dim)."""
    g = p.style["glow"]
    if g:
        return g
    return "glow_dim" if electric else "glow_amber"


def flame(p, x, y, z, s, lean=0.0, mat=None, segs=8):
    """Teardrop flame standing on (x, y, z), s = base radius scale; height ~2 s."""
    k = J(p, 1.0, 0.15)
    prof = [(0, 0), (s * 0.5 * k, s * 0.3), (s * 0.58 * k, s * 0.7), (s * 0.32, s * 1.3), (0, s * 2.1 * J(p, 1, 0.15))]
    p.lathe(prof, M(loc=(x, y, z), rot=(lean, 0, 0)), mat=mat or lit(p), segs=segs)


def candle(p, x, y, z, cr, ch, mat="bone"):
    """Wax candle of radius cr, height ch on (x, y, z), with wick and flame."""
    p.cyl(cr, cr * 0.95, ch, T((x, y, z)), mat=mat, segs=8, bevel=0)
    flame(p, x, y, z + ch + 0.003, cr * 0.85, segs=6)


def bail(p, w, z0, rise, r=0.0028, mat="iron", y=0.0, n=7):
    """Arched carrying handle in the XZ plane from (-w, z0) over to (w, z0)."""
    pts = []
    for i in range(n):
        a = math.pi * i / (n - 1)
        pts.append((-w * math.cos(a), y, z0 + rise * math.sin(a)))
    p.tube(pts, r, mat=mat, segs=4)


def chain(p, a, b, r=0.003, mat="brass"):
    p.tube([a, b], r, mat=mat, segs=4)


def petals(p, n, z0, z1, r0, r1, w, t, mat="body", phase=0.0):
    """n plates leaning out from radius r0 at z0 to r1 at z1 (crowns, leaf screens, apertures)."""
    lean = math.degrees(math.atan2(r1 - r0, z1 - z0))
    for i in range(n):
        a = phase + i * math.tau / n
        out = [(-w * 0.35, 0), (-w * 0.5, (z1 - z0) * 0.6), (0, z1 - z0), (w * 0.5, (z1 - z0) * 0.6), (w * 0.35, 0)]
        p.plate(out, t, M(loc=(math.cos(a) * r0, math.sin(a) * r0, z0), rot=(0, 0, math.degrees(a) + 90)) @ M(rot=(-lean, 0, 0)),
                mat=mat, bevel=0)


# ---------------------------------------------------------------- Torch (grip at the origin, flame up +Z)
@function("Torch", "Lamp", LAMP, "carried")
def torch(p, slot):
    e = p.era
    L = F(p, {"Primal": 0.58, "Agrarian": 0.6, "Mercantile": 0.58, "Industrial": 0.5, "Steampunk": 0.46,
              "Future": 0.42, "Wasteland": 0.55, "Ancient": 0.56}[e], 0.08)
    r = F(p, 0.016, 0.1)
    if e == "Primal":  # forked branch with a twig bundle
        if slot == "body":
            w = [0] + [J(p, 0.012, 0.6) * (1 if i % 2 else -1) for i in range(1, 4)] + [0]
            p.tube([(w[i], w[(i + 2) % 5] * 0.5, L * 0.72 * i / 4) for i in range(5)], r * 1.1, mat="wood", segs=6)
            if coin(p):
                p.tube([(0, 0, L * 0.35), (r * 2.5, -r * 0.5, L * 0.42)], r * 0.4, mat="wood", segs=4)
        elif slot == "shade":
            n = p.rng.randint(5, 7)
            for i in range(n):
                a = i * math.tau / n + p.rng.uniform(-0.2, 0.2)
                top = J(p, 1.0, 0.04)
                p.tube([(math.cos(a) * r * 0.9, math.sin(a) * r * 0.9, L * 0.6),
                        (math.cos(a) * r * 2.3, math.sin(a) * r * 2.3, L * top)], r * 0.45, mat="bark", segs=4)
            p.band(r * 1.5, L * 0.66, h=0.035)
        elif slot == "light":
            flame(p, 0, 0, L * 0.86, J(p, 0.065, 0.12))
            flame(p, J(p, 0.015), 0.005, L * 0.84, 0.03, lean=J(p, 14, 0.4))
        else:
            p.band(r * 1.15, L * J(p, 0.2, 0.2), h=0.06)
            if coin(p):
                p.tube([(r, 0, L * 0.18), (r * 2.5, -0.01, L * 0.08), (r * 2.2, 0, -0.03)], 0.002, mat="hide", segs=4)
    elif e == "Agrarian":  # oil-cloth torch: stick, rag wrap, iron collar and ferrule
        if slot == "body":
            p.cyl(r, r * 0.88, L * 0.95, mat="wood", segs=8, bevel=0)
        elif slot == "shade":
            p.lathe([(r * 1.0, L * 0.68), (r * 2.2, L * 0.73), (r * J(p, 2.6, 0.12), L * 0.85), (r * 2.1, L * 0.95),
                     (r * 0.9, L)], mat="cloth", segs=10, noise=0.03)
            p.ring(r * J(p, 2.5, 0.05), 0.003, T((0, 0, L * J(p, 0.8, 0.04))), mat="rope", segs=10, square=False)
        elif slot == "light":
            flame(p, 0, 0, L * 0.97, J(p, 0.06, 0.15))
        else:
            p.cyl(r * 1.15, r * 1.1, 0.045, T((0, 0, -0.01)), mat="iron", segs=8, bevel=0)
            p.ring(r * 1.02, 0.004, T((0, 0, L * 0.665)), mat="iron", segs=8)
            if coin(p):
                p.ring(0.012, 0.0025, M(loc=(0, 0, -0.022), rot=(90, 0, 0)), mat="leather", segs=6, square=False)
    elif e == "Mercantile":  # pine-resin torch: turned handle, bound split splints
        if slot == "body":
            p.lathe([(r * 1.2, 0), (r * 1.0, L * 0.05), (r * 0.9, L * 0.35), (r * 1.08, L * 0.55), (r * 0.95, L * 0.66)],
                    mat="wood_dark", segs=8)
            p.cyl(r * 1.08, r * 1.0, L * J(p, 0.22, 0.2), T((0, 0, L * 0.06)), mat="grip", segs=8, bevel=0)
        elif slot == "shade":
            n = 6
            for i in range(n):
                a = i * math.tau / n
                p.box((0.009, 0.009, L * 0.36), M(loc=(math.cos(a) * r * 1.35, math.sin(a) * r * 1.35, L * 0.82),
                                                  rot=(0, J(p, 5, 0.5), math.degrees(a))), mat="wood", bevel=0)
            p.lathe([(r * 2.2, L * 0.96), (r * J(p, 2.0, 0.1), L * 1.0), (0, L * 1.02)], mat="bark", segs=8)
            for z in (0.7, 0.88):
                p.ring(r * 2.05, 0.004, T((0, 0, L * z)), mat="iron", segs=8)
        elif slot == "light":
            flame(p, 0, 0, L * 1.0, J(p, 0.055, 0.15))
        else:
            p.lathe([(0, -0.03), (r * 1.25, -0.025), (r * 1.4, -0.01), (r * 1.2, 0.0)], mat="brass", segs=8)
            p.ring(r * 1.25, 0.004, T((0, 0, L * 0.65)), mat="brass", segs=8)
    elif e == "Industrial":  # windproof torch: steel tube, fuel cup, slatted wind guard
        if slot == "body":
            p.cyl(r * 0.85, r * 0.85, L * 0.82, mat="steel", segs=8, bevel=0)
            p.cyl(r * 1.1, r * 1.1, L * J(p, 0.38, 0.15), T((0, 0, 0.02)), mat="rubber", segs=8, bevel=0)
        elif slot == "shade":
            p.cyl(r * 2.2, r * 2.5, L * 0.1, T((0, 0, L * 0.8)), mat="paint", segs=10, bevel=0)
            n = p.rng.choice((5, 6, 8))
            for i in range(n):
                a = i * math.tau / n
                p.box((0.008, 0.002, L * 0.14), M(loc=(math.cos(a) * r * 2.4, math.sin(a) * r * 2.4, L * 0.97),
                                                  rot=(0, 0, math.degrees(a) + 90)), mat="steel", bevel=0)
            p.ring(r * 2.4, 0.003, T((0, 0, L * 1.04)), mat="steel", segs=10)
        elif slot == "light":
            flame(p, 0, 0, L * 0.9, J(p, 0.042, 0.12))
        else:
            p.ring(0.014, 0.003, M(loc=(0, 0, -0.012), rot=(90, 0, 0)), mat="steel", segs=8, square=False)
            p.cyl(r * 0.95, r * 0.95, 0.01, T((0, 0, -0.002)), mat="paint", segs=8, bevel=0)
            if coin(p):
                p.box((0.01, 0.004, 0.05), T((0, r * 1.2, L * 0.3)), mat="steel", bevel=0)
    elif e == "Steampunk":  # gas torch: brass canister, copper riser, flared reflector, valve wheel
        if slot == "body":
            p.cyl(r * 1.9, r * 1.9, L * 0.5, mat="brass", segs=10, bevel=0)
            p.lathe([(r * 1.9, L * 0.5), (r * 0.6, L * 0.55), (r * 0.55, L * 0.86)], mat="copper", segs=8)
            p.band(r * 1.9, L * J(p, 0.25, 0.2), h=0.025)
        elif slot == "shade":
            p.lathe([(r * 0.6, L * 0.84), (r * 1.5, L * 0.88), (r * J(p, 3.0, 0.12), L * 0.98), (r * 3.2, L * 1.0)],
                    mat="brass", segs=10)
            p.ring(r * 3.1, 0.003, T((0, 0, L * 1.0)), mat="copper", segs=10)
        elif slot == "light":
            flame(p, 0, 0, L * 0.88, J(p, 0.03, 0.12))
            p.ball(r * 0.6, T((0, 0, L * 0.9)), mat=lit(p), segs=(6, 4))
        else:
            p.ring(0.016, 0.003, M(loc=(r * 1.9 + 0.006, 0, L * 0.44), rot=(0, 90, 0)), mat="copper", segs=8)
            p.box((0.002, 0.03, 0.003), T((r * 1.9 + 0.006, 0, L * 0.44)), mat="copper", bevel=0)
            p.cyl(0.012, 0.012, 0.006, M(loc=(0, -r * 1.9, L * J(p, 0.3, 0.15)), rot=(90, 0, 0)), mat="brass", segs=10, bevel=0)
            p.lathe([(r * 1.9, 0), (r * 1.5, -0.012), (0, -0.016)], mat="copper", segs=10)
    elif e == "Future":  # light stick: shell grip, emitter collar, glowing rod
        if slot == "body":
            p.cyl(r * 1.4, r * 1.2, L * 0.38, M(scale=(J(p, 1.15, 0.1), 1, 1)), mat="body", segs=10, bevel=0)
            p.box((r * 0.9, r * 0.5, L * 0.22), T((0, -r * 1.2, L * 0.18)), mat="grip", bevel=0)
        elif slot == "light":
            p.cyl(r * 0.75, r * J(p, 0.75, 0.15), L * 0.6, T((0, 0, L * 0.38)), mat=lit(p), segs=8, bevel=0)
            p.ball(r * 0.8, T((0, 0, L * 0.98)), mat=lit(p), segs=(8, 4))
        elif slot == "shade":
            p.lathe([(r * 1.2, L * 0.36), (r * J(p, 1.9, 0.12), L * 0.42), (r * 1.0, L * 0.46)], mat="shell_dark", segs=10)
            if coin(p):
                p.ring(r * 1.1, 0.002, T((0, 0, L * J(p, 0.7, 0.1))), mat="shell_dark", segs=8)
        else:
            p.ball(r * 1.3, M(loc=(0, 0, 0.0), scale=(1, 1, 0.7)), mat="shell_dark", segs=(8, 4))
            p.ring(0.012, 0.002, M(loc=(0, 0, -0.016), rot=(90, 0, 0)), mat="grip", segs=8, square=False)
    elif e == "Wasteland":  # pipe handle, tin can stuffed with rag
        if slot == "body":
            p.cyl(r * 1.05, r * 1.05, L * 0.5, mat="body", segs=7, bevel=0)
            p.cyl(r * 0.9, r * 0.9, L * 0.3, M(loc=(0, 0, L * 0.49), rot=(J(p, 3, 0.8), 0, 0)), mat="steel", segs=7, bevel=0)
            p.cyl(r * 1.25, r * 1.25, L * J(p, 0.25, 0.25), T((0, 0, L * 0.06)), mat="grip", segs=7, bevel=0, noise=0.05)
        elif slot == "shade":
            p.cyl(r * 2.5, r * J(p, 2.6, 0.08), L * 0.2, T((0, 0, L * 0.78)), mat="steel", segs=9, bevel=0)
            p.box((r * 2.6, 0.002, L * 0.1), T((0, -r * 2.5, L * 0.88)), mat="paint", bevel=0)
            p.band(r * 2.55, L * 0.84, h=0.03)
        elif slot == "light":
            for i in range(3):
                a = i * math.tau / 3 + J(p, 0.5, 0.5)
                p.ball(r * 1.0, T((math.cos(a) * r * 1.2, math.sin(a) * r * 1.2, L * 0.98)), mat="cloth", segs=(5, 3))
            flame(p, 0, 0, L * 0.97, J(p, 0.04, 0.15))
        else:
            pts = [(r * 1.15 * math.cos(i * 1.4), r * 1.15 * math.sin(i * 1.4), L * (0.44 + i * 0.012)) for i in range(9)]
            p.tube(pts, 0.0018, mat="iron", segs=4)
            if coin(p):
                p.cyl(0.005, 0.005, r * 3, M(loc=(-r * 1.5, 0, L * 0.5), rot=(0, 90, 0)), mat="iron", segs=6, bevel=0)
    else:  # Ancient: rune rod, stone petal crown, floating rune flame
        if slot == "body":
            p.cyl(r * 1.35, r * 1.1, L * 0.8, mat="body", segs=6, bevel=0.05)
            for i in range(3):
                p.box((r * 0.35, r * 0.15, L * 0.06), T((0, -r * 1.2, L * (0.3 + i * 0.13))), mat="glow", bevel=0)
        elif slot == "shade":
            petals(p, 4, L * 0.78, L * 0.98, r * 1.4, r * J(p, 3.2, 0.12), r * 2.4, 0.008, mat="body", phase=math.pi / 4)
        elif slot == "light":
            p.ball(J(p, 0.022, 0.12), T((0, 0, L * 0.95)), mat=lit(p), segs=(8, 6))
            p.cyl(0.015, 0.0, J(p, 0.06, 0.15), T((0, 0, L * 0.97)), mat=lit(p), segs=4, bevel=0)
        else:
            p.ring(r * 1.45, 0.006, T((0, 0, L * 0.78)), mat="gold", segs=6)
            p.ball(r * J(p, 1.6, 0.1), M(loc=(0, 0, -0.005), rot=(0, 0, 45)), mat="stone_dark", segs=(4, 2))


# ---------------------------------------------------------------- Lantern (stands on z = 0, bail on top)
@function("Lantern", "Lamp", LAMP, "carried")
def lantern(p, slot):
    e = p.era
    h = F(p, {"Primal": 0.1, "Agrarian": 0.3, "Mercantile": 0.26, "Industrial": 0.28, "Steampunk": 0.28,
              "Future": 0.22, "Wasteland": 0.22, "Ancient": 0.26}[e], 0.1)
    r = F(p, {"Primal": 0.07, "Agrarian": 0.1, "Future": 0.07}.get(e, 0.075), 0.1)
    if e == "Primal":  # tallow lamp: hollowed stone dish, bark wind screen, rope sling
        if slot == "body":
            p.lathe([(0, 0), (r * 0.9, 0.004), (r * 1.25, h * 0.45), (r * 1.2, h * 0.8), (r * 0.9, h * 0.75),
                     (r * 0.6, h * 0.6), (0, h * 0.58)], mat="stone", segs=10, noise=0.05)
        elif slot == "light":
            p.cyl(r * 0.85, r * 0.85, 0.006, T((0, 0, h * 0.58)), mat="bone", segs=8, bevel=0)
            flame(p, J(p, 0.01, 0.8), 0, h * 0.62, J(p, 0.022, 0.15))
        elif slot == "shade":
            for i in range(3):
                a = math.radians(60 + i * 30)
                p.plate([(-0.03, 0), (-0.028, J(p, 0.09, 0.15)), (0.028, J(p, 0.1, 0.15)), (0.03, 0)], 0.004,
                        M(loc=(math.cos(a) * r * 1.05, math.sin(a) * r * 1.05, h * 0.55), rot=(0, 0, math.degrees(a) + 90)),
                        mat="bark", bevel=0)
        else:
            for s in (-1, 1):
                p.tube([(s * r * 1.2, 0, h * 0.5), (s * r * 0.9, 0, h * 1.6), (0, 0, h * 2.6)], 0.004, mat="rope", segs=4)
            p.ball(0.01, T((0, 0, h * 2.6)), mat="rope", segs=(5, 3))
    elif e == "Agrarian":  # paper lantern: glowing paper drum, bamboo ribs, wooden rims
        prof = [(r * 0.72, 0.02), (r * 1.05, h * 0.3), (r * 1.08, h * 0.6), (r * 0.72, h - 0.015)]
        if slot == "body":
            p.cyl(r * 0.76, r * 0.76, 0.02, mat="wood", segs=10, bevel=0)
            p.cyl(r * 0.76, r * 0.74, 0.016, T((0, 0, h - 0.016)), mat="wood", segs=10, bevel=0)
        elif slot == "light":
            p.lathe(prof, mat=lit(p), segs=12)
        elif slot == "shade":
            for z, rr in ((h * 0.3, 1.06), (h * 0.6, 1.09)):
                p.ring(r * rr, 0.003, T((0, 0, z)), mat="wood", segs=12, square=False)
            p.lathe([(r * 0.74, h), (r * J(p, 0.5, 0.15), h + 0.02), (0, h + 0.024)], mat="wood_dark", segs=10)
        else:
            bail(p, r * 0.45, h + 0.02, J(p, 0.09, 0.15), mat="wood")
            p.ring(0.01, 0.002, M(loc=(0, 0, h + 0.02 + 0.09), rot=(90, 0, 0)), mat="iron", segs=6, square=False)
    elif e == "Mercantile":  # framed oil lantern: square base, four posts, lit panes, pyramid roof
        a = r * 0.9
        if slot == "body":
            p.box((a * 2.1, a * 2.1, h * 0.12), T((0, 0, h * 0.06)), mat="wood_dark", bevel=0.05)
            for x in (-1, 1):
                for y in (-1, 1):
                    p.box((0.008, 0.008, h * 0.7), T((x * a, y * a, h * 0.47)), mat="brass", bevel=0)
        elif slot == "light":
            p.box((a * J(p, 1.8, 0.06), a * J(p, 1.8, 0.06), h * 0.66), T((0, 0, h * 0.45)), mat=lit(p), bevel=0)
        elif slot == "shade":
            p.lathe([(a * 1.55, h * 0.8), (a * J(p, 0.5, 0.2), h * 0.95), (a * 0.4, h * 1.0)], M(rot=(0, 0, 45)),
                    mat="brass", segs=4)
            p.cyl(a * 0.35, a * 0.28, h * J(p, 0.08, 0.3), T((0, 0, h)), mat="brass", segs=8, bevel=0)
        else:
            p.ring(J(p, 0.028, 0.2), 0.004, M(loc=(0, 0, h * 1.08 + 0.028), rot=(90, 0, 0)), mat="brass", segs=10, square=False)
    elif e == "Industrial":  # kerosene hurricane lantern: tank, lit globe, wire guards, vented cap, bail
        if slot == "body":
            p.lathe([(0, 0), (r * 1.15, 0), (r * 1.25, h * 0.1), (r * 1.05, h * 0.24), (r * 0.6, h * 0.26)],
                    mat="paint", segs=12)
            for s in (-1, 1):
                p.tube([(s * r * 1.1, 0, h * 0.18), (s * r * 1.15, 0, h * 0.5), (s * r * 0.8, 0, h * 0.8)], 0.0035,
                       mat="steel", segs=4)
            p.cyl(0.008, 0.008, 0.02, M(loc=(0, -r * 1.05, h * 0.18), rot=(90, 0, 0)), mat="steel", segs=6, bevel=0)
        elif slot == "light":
            p.lathe([(r * 0.55, h * 0.26), (r * 0.85, h * 0.4), (r * J(p, 0.9, 0.08), h * 0.55), (r * 0.5, h * 0.76)],
                    mat=lit(p), segs=12)
        elif slot == "shade":
            p.lathe([(r * 0.85, h * 0.76), (r * 0.75, h * 0.86), (r * 0.3, h * 0.9), (r * 0.3, h * 0.97),
                     (r * 0.4, h * 0.98), (0, h * 1.0)], mat="steel", segs=10)
            if coin(p):
                for s in (-1, 1):
                    p.tube([(s * r * 0.4, -r * 0.7, h * 0.3), (s * r * 0.5, -r * 1.0, h * 0.5), (s * r * 0.4, -r * 0.7, h * 0.72)],
                           0.0025, mat="steel", segs=4)
        else:
            bail(p, r * 0.8, h * 0.8, J(p, h * 0.55, 0.15), mat="steel")
    elif e == "Steampunk":  # brass gas lantern: riveted reservoir, lit mantle globe, copper cage, chimney cap
        if slot == "body":
            p.cyl(r * 1.1, r * 1.2, h * 0.22, mat="brass", segs=10, bevel=0)
            p.band(r * 1.12, h * 0.11, h=0.025)
            for i in range(3):
                a = i * math.tau / 3 + math.pi / 2
                p.cyl(0.004, 0.004, h * 0.58, T((math.cos(a) * r * 0.95, math.sin(a) * r * 0.95, h * 0.2)), mat="copper", segs=6, bevel=0)
        elif slot == "light":
            p.lathe([(r * 0.35, h * 0.22), (r * 0.8, h * 0.38), (r * J(p, 0.85, 0.1), h * 0.55), (r * 0.4, h * 0.78)],
                    mat=lit(p), segs=10)
        elif slot == "shade":
            p.ring(r * 0.96, 0.004, T((0, 0, h * J(p, 0.5, 0.15))), mat="copper", segs=10)
            p.lathe([(r * 1.1, h * 0.78), (r * 0.9, h * 0.9), (r * 0.3, h * 0.95), (r * 0.25, h * 1.05),
                     (r * 0.35, h * 1.07), (0, h * 1.08)], mat="brass", segs=10)
        else:
            p.ring(0.016, 0.004, M(loc=(r * 1.25, 0, h * 0.12), rot=(0, 90, 0)), mat="copper", segs=8)
            p.box((0.002, 0.028, 0.003), T((r * 1.25, 0, h * 0.12)), mat="copper", bevel=0)
            p.tube([(0, 0, h * 1.07), (0, 0, h * 1.15), (0.02, 0, h * 1.22), (0, 0, h * 1.3), (-0.012, 0, h * 1.25)],
                   0.004, mat="brass", segs=5)
    elif e == "Future":  # floating light orb over an emitter puck
        if slot == "body":
            p.lathe([(0, 0), (r * 0.8, 0), (r * 0.9, 0.012), (r * J(p, 0.8, 0.08), 0.026), (r * 0.5, 0.032), (0, 0.032)], mat="body", segs=12)
        elif slot == "light":
            p.ball(r * J(p, 0.72, 0.1), T((0, 0, h * 0.62)), mat=lit(p), segs=(10, 6))
        elif slot == "shade":
            for i, tilt in enumerate((J(p, 20, 0.3), -J(p, 35, 0.3))):
                p.ring(r * (1.0 + 0.12 * i), 0.004, M(loc=(0, 0, h * 0.62), rot=(tilt, 0, 30 * i)), mat="shell_dark", segs=10)
        else:
            p.tube([(0, r * 0.7, 0.03), (0, r * 1.05, h * 0.35), (0, r * 0.9, h * 1.05), (0, 0, h * 1.18)], 0.004,
                   mat="shell_dark", segs=4)
            p.ball(0.008, T((0, 0, h * 1.18)), mat="shell_dark", segs=(6, 4))
    elif e == "Wasteland":  # jar lantern: cut tin base, glowing jar, hubcap roof, wire bail
        if slot == "body":
            p.cyl(r * 1.05, r * 1.0, h * 0.18, mat="body", segs=9, bevel=0)
            for i in range(3):
                a = i * math.tau / 3 + 0.3
                p.tube([(math.cos(a) * r, math.sin(a) * r, h * 0.15), (math.cos(a) * r * 0.95, math.sin(a) * r * 0.95, h * 0.82)],
                       0.0025, mat="iron", segs=4)
        elif slot == "light":
            p.lathe([(r * 0.8, h * 0.18), (r * 0.85, h * 0.6), (r * 0.6, h * 0.72), (r * 0.55, h * 0.8)], mat=lit(p), segs=10)
        elif slot == "shade":
            p.lathe([(r * J(p, 1.35, 0.1), h * 0.8), (r * 0.9, h * 0.88), (r * 0.25, h * 0.92), (0, h * 0.93)],
                    M(rot=(J(p, 4, 0.8), 0, 0)), mat="steel", segs=9)
            p.box((r * 0.5, r * 0.5, 0.006), M(loc=(r * 0.3, 0, h * 0.9), rot=(0, 12, 25)), mat="paint", bevel=0)
        else:
            rise = J(p, h * 0.75, 0.15)
            bail(p, r * 0.9, h * 0.6, rise, mat="iron", r=0.0022)
            p.cyl(0.008, 0.008, 0.04, M(loc=(-0.02, 0, h * 0.6 + rise * 0.99), rot=(0, 90, 0)), mat="cloth", segs=6, bevel=0)
    else:  # Ancient: stone plinth, four pillars, rune crystal core, domed cap, stone ring
        a = r * 0.85
        if slot == "body":
            p.box((a * 2.4, a * 2.4, h * 0.16), T((0, 0, h * 0.08)), mat="body", bevel=0.1, bevel_seg=1)
            for x in (-1, 1):
                for y in (-1, 1):
                    p.box((a * 0.5, a * 0.5, h * 0.62), T((x * a, y * a, h * 0.47)), mat="body", bevel=0)
            p.box((a * 1.2, 0.006, h * 0.04), T((0, -a * 1.2, h * 0.08)), mat="glow", bevel=0)
        elif slot == "light":
            p.ball(a * J(p, 0.6, 0.12), M(loc=(0, 0, h * 0.48), scale=(1, 1, 1.5)), mat=lit(p), segs=(4, 2))
        elif slot == "shade":
            p.lathe([(a * 1.45, h * 0.78), (a * 1.5, h * 0.86), (a * J(p, 1.0, 0.12), h * 0.98), (0, h * 1.02)],
                    mat="stone", segs=8)
            p.ring(a * 1.47, 0.004, T((0, 0, h * 0.82)), mat="glow", segs=8)
        else:
            p.ring(J(p, 0.03, 0.15), 0.008, M(loc=(0, 0, h * 1.02 + 0.03), rot=(90, 0, 0)), mat="stone_dark", segs=8)


# ---------------------------------------------------------------- Candlestand (scene, floor contact)
@function("Candlestand", "Lamp", LAMP, "scene")
def candlestand(p, slot):
    e = p.era
    h = F(p, {"Primal": 0.16, "Agrarian": 0.12, "Mercantile": 0.36, "Industrial": 0.5, "Steampunk": 0.42,
              "Future": 0.34, "Wasteland": 0.38, "Ancient": 0.42}[e], 0.1)
    w = F(p, {"Mercantile": 0.13, "Industrial": 0.16, "Wasteland": 0.12}.get(e, 0.1), 0.1)
    if e == "Primal":  # stone cup on a rough pillar on a slab
        if slot == "mount":
            p.ball(w * 1.3, M(loc=(0, 0, 0.012), scale=(1, 0.8, 0.12)), mat="stone_dark", segs=(10, 4), noise=0.06)
        elif slot == "body":
            p.lathe([(w * 0.55, 0.02), (w * 0.45, h * 0.5), (w * 0.4, h * 0.8)], mat="stone", segs=8, noise=0.06)
        elif slot == "shade":
            p.lathe([(w * 0.4, h * 0.8), (w * 0.7, h * 0.88), (w * J(p, 0.75, 0.1), h), (w * 0.55, h * 0.98),
                     (0, h * 0.93)], mat="stone", segs=10, noise=0.04)
        else:
            p.cyl(w * 0.5, w * 0.45, 0.012, T((0, 0, h * 0.93)), mat="bone", segs=8, bevel=0)
            flame(p, 0, 0, h * 0.95, J(p, 0.018, 0.15))
    elif e == "Agrarian":  # ceramic chamberstick: saucer, short stem, socket, finger loop
        if slot == "mount":
            p.lathe([(0, 0), (w * 0.95, 0.0), (w * 1.0, 0.015), (w * 0.85, 0.012), (0, 0.008)], mat="ceramic", segs=12)
        elif slot == "body":
            p.lathe([(w * 0.25, 0.01), (w * 0.18, h * 0.5), (w * 0.22, h * 0.8)], mat="ceramic", segs=10)
            p.ring(0.018, 0.004, M(loc=(w * 0.8, 0, 0.03), rot=(90, 0, 0)), mat="ceramic", segs=8, square=False)
        elif slot == "shade":
            p.lathe([(w * 0.22, h * 0.8), (w * J(p, 0.32, 0.12), h * 0.9), (w * 0.3, h), (w * 0.22, h * 0.98)],
                    mat="glaze", segs=10)
        else:
            candle(p, 0, 0, h * 0.98, 0.011, J(p, 0.16, 0.25))
    elif e == "Mercantile":  # brass three-light candelabrum
        arms = [(-w, 0.0), (0, 0.0), (w, 0.0)]
        if slot == "mount":
            p.lathe([(0, 0), (w * 0.75, 0), (w * 0.7, 0.02), (w * 0.35, 0.05), (w * 0.18, 0.07)], mat="brass", segs=12)
        elif slot == "body":
            p.lathe([(w * 0.18, 0.07), (w * 0.1, h * 0.3), (w * J(p, 0.2, 0.15), h * 0.45), (w * 0.09, h * 0.6),
                     (w * 0.12, h * 0.98)], mat="brass", segs=8)
            for s in (-1, 1):
                p.tube([(0, 0, h * 0.62), (s * w * 0.6, 0, h * J(p, 0.6, 0.06)), (s * w, 0, h * 0.8), (s * w, 0, h * 0.94)],
                       0.006, mat="brass", segs=6)
        elif slot == "shade":
            for x, y in arms:
                p.lathe([(0.008, h * 0.94), (J(p, 0.028, 0.15), h * 0.97), (0.03, h * 0.98), (0.012, h), (0.013, h * 1.06)],
                        T((x, y, 0)), mat="brass", segs=10)
        else:
            for i, (x, y) in enumerate(arms):
                candle(p, x, y, h * 1.06, 0.01, J(p, 0.16 if i == 1 else 0.13, 0.25))
    elif e == "Industrial":  # wrought-iron branch candlestand: tripod, stem, scrolled branches, spike cups
        arms = [(0, 0, h)] + [(math.cos(i * math.tau / 4 + 0.4) * w, math.sin(i * math.tau / 4 + 0.4) * w,
                               h * (0.72 if i % 2 else 0.84)) for i in range(4)]
        if slot == "mount":
            for i in range(3):
                a = i * math.tau / 3
                p.tube([(0, 0, h * 0.12), (math.cos(a) * w * 0.6, math.sin(a) * w * 0.6, 0.03),
                        (math.cos(a) * w * 0.75, math.sin(a) * w * 0.75, 0.0), (math.cos(a) * w * 0.82, math.sin(a) * w * 0.82, 0.02)],
                       0.006, mat="iron", segs=5)
        elif slot == "body":
            p.cyl(0.008, 0.007, h, T((0, 0, h * 0.1)), mat="iron", segs=6, bevel=0)
            for x, y, z in arms[1:]:
                p.tube([(0, 0, z - h * 0.22), (x * 0.5, y * 0.5, z - h * 0.18), (x * 1.08, y * 1.08, z - h * 0.1),
                        (x, y, z - h * 0.04)], 0.0045, mat="iron", segs=5)
        elif slot == "shade":
            for x, y, z in arms:
                p.cyl(0.012, J(p, 0.024, 0.15), 0.012, T((x, y, z - h * 0.04)), mat="iron", segs=8, bevel=0)
                p.cyl(0.002, 0.0, 0.012, T((x, y, z - h * 0.03)), mat="steel", segs=4, bevel=0)
        else:
            for x, y, z in arms:
                candle(p, x, y, z - h * 0.028, 0.009, J(p, 0.1, 0.3))
    elif e == "Steampunk":  # gas sconce on a standing backplate: brass pipe arm, valve, lit tulip
        if slot == "mount":
            p.cyl(w * 0.9, w, 0.025, mat="wood_dark", segs=12, bevel=0)
            p.plate([(-w * 0.45, 0), (-w * 0.45, h * 0.6), (0, h * J(p, 0.75, 0.06)), (w * 0.45, h * 0.6), (w * 0.45, 0)], 0.012,
                    T((0, w * 0.5, 0.02)), mat="brass")
        elif slot == "body":
            p.tube([(0, w * 0.44, h * 0.35), (0, w * 0.1, h * 0.38), (0, -w * 0.2, h * 0.5), (0, -w * 0.3, h * 0.68)],
                   0.007, mat="copper", segs=6)
            p.ring(0.014, 0.003, M(loc=(0.012, w * 0.15, h * 0.38), rot=(0, 90, 0)), mat="brass", segs=8)
        elif slot == "shade":
            p.lathe([(0.012, h * 0.66), (0.03, h * 0.7), (J(p, 0.034, 0.12), h * 0.73)], T((0, -w * 0.3, 0)), mat="brass", segs=10)
            p.ball(0.012, T((0, -w * 0.3 - 0.0, h * 0.62)), mat="brass", segs=(6, 4))
        else:
            p.lathe([(0.03, h * 0.72), (J(p, 0.05, 0.12), h * 0.82), (0.045, h * 0.92), (0.03, h * 0.96)], T((0, -w * 0.3, 0)),
                    mat=lit(p), segs=12)
    elif e == "Future":  # light-pillar stand: shell plinth, glowing column, hovering rings
        if slot == "mount":
            p.cyl(w * 0.9, w * 0.8, 0.03, mat="body", segs=14, bevel=0.15)
        elif slot == "body":
            p.cyl(w * 0.35, w * 0.25, h * 0.35, T((0, 0, 0.03)), mat="body", segs=10, bevel=0.1)
        elif slot == "light":
            p.cyl(w * 0.14, w * J(p, 0.1, 0.25), h * 0.62, T((0, 0, h * 0.38)), mat=lit(p), segs=8, bevel=0)
        else:
            for i in range(2):
                p.ring(w * (0.35 - 0.08 * i), 0.004, M(loc=(0, 0, h * (0.62 + 0.22 * i) * J(p, 1, 0.05)), rot=(J(p, 8, 1), 0, 0)),
                       mat="shell_dark", segs=12)
    elif e == "Wasteland":  # bent rebar on a brake disc, candles in tin cans
        arms = [(0, 0, h), (-w, 0, h * 0.78), (w * 0.9, 0.02, h * 0.68)]
        if slot == "mount":
            p.cyl(w * 0.9, w * 0.9, 0.02, mat="iron", segs=12, bevel=0)
            p.cyl(w * 0.35, w * 0.35, 0.035, mat="body", segs=8, bevel=0)
        elif slot == "body":
            p.tube([(0, 0, 0.03), (0.005, 0, h * 0.5), (0, 0, h - 0.04)], 0.006, mat="body", segs=5)
            for x, y, z in arms[1:]:
                p.tube([(0, 0, z - h * 0.25), (x * 0.6, y, z - h * 0.2), (x, y, z - h * 0.1), (x, y, z - 0.04)], 0.005,
                       mat="body", segs=5)
            p.band(0.009, h * 0.45, h=0.03)
        elif slot == "shade":
            for x, y, z in arms:
                p.cyl(0.024, J(p, 0.024, 0.1), 0.045, T((x, y, z - 0.045)), mat="steel", segs=8, bevel=0)
        else:
            for x, y, z in arms:
                candle(p, x, y, z - 0.03, 0.012, J(p, 0.05, 0.4))
    else:  # Ancient: stepped plinth, rune obelisk, lotus bowl, floating rune flame
        if slot == "mount":
            p.box((w * 1.6, w * 1.6, 0.03), T((0, 0, 0.015)), mat="stone_dark")
            p.box((w * 1.1, w * 1.1, 0.03), T((0, 0, 0.045)), mat="stone_dark")
        elif slot == "body":
            p.lathe([(w * 0.45, 0.06), (w * 0.3, h * 0.82)], M(rot=(0, 0, 45)), mat="body", segs=4)
            for i in range(3):
                p.box((w * 0.12, 0.006, h * 0.08), T((0, -w * (0.42 - 0.04 * i) * 0.71, h * (0.25 + i * 0.18))), mat="glow", bevel=0)
        elif slot == "shade":
            petals(p, 5, h * 0.8, h * 0.95, w * 0.22, w * J(p, 0.6, 0.12), w * 0.4, 0.008, mat="stone")
        else:
            p.ball(J(p, 0.02, 0.15), T((0, 0, h * 0.96)), mat=lit(p), segs=(8, 6))
            p.cyl(0.016, 0.0, J(p, 0.07, 0.15), T((0, 0, h * 0.98)), mat=lit(p), segs=4, bevel=0)


# ---------------------------------------------------------------- Streetlamp (scene, floor contact, 2.5-4 m)
@function("Streetlamp", "Lamp", LAMP, "scene")
def streetlamp(p, slot):
    e = p.era
    H = F(p, {"Primal": 2.4, "Agrarian": 2.2, "Mercantile": 3.0, "Industrial": 4.0, "Steampunk": 3.5,
              "Future": 3.8, "Wasteland": 3.3, "Ancient": 3.2}[e], 0.08)
    r = F(p, {"Primal": 0.14, "Agrarian": 0.16, "Mercantile": 0.07, "Industrial": 0.075, "Steampunk": 0.09,
              "Future": 0.07, "Wasteland": 0.07, "Ancient": 0.16}[e], 0.1)
    if e == "Primal":  # brazier column: log post on a cairn, stone fire bowl on top
        if slot == "mount":
            for i in range(6):
                a = i * math.tau / 6 + J(p, 0.3, 0.5)
                p.ball(r * J(p, 1.1, 0.2), M(loc=(math.cos(a) * r * 1.6, math.sin(a) * r * 1.6, r * 0.5), scale=(1, 1, 0.7)),
                       mat="stone", segs=(6, 4), noise=0.08)
        elif slot == "body":
            p.lathe([(r * 1.1, 0), (r, H * 0.3), (r * J(p, 0.92, 0.06), H * 0.7), (r * 0.9, H * 0.9)], mat="bark", segs=8, noise=0.04)
            p.band(r * 0.95, H * 0.85, h=0.12)
        elif slot == "shade":
            p.lathe([(r * 0.9, H * 0.9), (r * 2.2, H * 0.94), (r * J(p, 2.6, 0.1), H * 1.0), (r * 2.2, H * 0.99),
                     (0, H * 0.96)], mat="stone", segs=10, noise=0.05)
        else:
            for i in range(3):
                a = i * math.tau / 3 + 0.5
                flame(p, math.cos(a) * r * 0.9, math.sin(a) * r * 0.9, H * 0.96, J(p, 0.12, 0.2), lean=J(p, 10, 1))
            flame(p, 0, 0, H * 0.96, 0.18)
    elif e == "Agrarian":  # stone lantern: pedestal, column, lit firebox, broad roof, finial
        if slot == "mount":
            p.cyl(r * 2.4, r * 2.2, H * 0.06, mat="stone_dark", segs=6, bevel=0)
            p.cyl(r * 1.6, r * 1.3, H * 0.05, T((0, 0, H * 0.06)), mat="stone", segs=6, bevel=0)
        elif slot == "body":
            p.cyl(r, r * 0.9, H * 0.45, T((0, 0, H * 0.11)), mat="stone", segs=8, bevel=0)
            p.cyl(r * 1.9, r * 1.6, H * 0.06, T((0, 0, H * 0.56)), mat="stone", segs=6, bevel=0)
        elif slot == "light":
            p.cyl(r * 1.25, r * 1.25, H * 0.17, T((0, 0, H * 0.62)), mat=lit(p), segs=6, bevel=0)
        else:
            for i in range(6):
                a = i * math.tau / 6 + math.pi / 6
                p.box((r * 0.35, r * 0.35, H * 0.17), T((math.cos(a) * r * 1.38, math.sin(a) * r * 1.38, H * 0.705)), mat="stone", bevel=0)
            p.lathe([(r * J(p, 2.6, 0.1), H * 0.79), (r * 2.4, H * 0.82), (r * 0.9, H * 0.9), (r * 0.5, H * 0.92)],
                    M(rot=(0, 0, 30)), mat="stone_dark", segs=6)
            p.ball(r * 0.45, M(loc=(0, 0, H * 0.95), scale=(1, 1, 1.4)), mat="stone", segs=(6, 4))
    elif e == "Mercantile":  # oil lamp post: iron post, ladder bar, glazed lantern box on top
        a = r * 2.4
        if slot == "mount":
            p.lathe([(r * 2.6, 0), (r * 2.4, 0.12), (r * 1.6, 0.2), (r * 1.4, 0.35)], mat="stone", segs=8)
        elif slot == "body":
            p.lathe([(r * 1.4, 0.35), (r * 1.0, 0.5), (r * 0.8, H * 0.6), (r * 0.7, H * 0.86), (r * 1.6, H * 0.88)],
                    mat="iron", segs=8)
            p.cyl(0.018, 0.018, r * J(p, 8, 0.15), M(loc=(-r * 4, 0, H * 0.8), rot=(0, 90, 0)), mat="iron", segs=6, bevel=0)
        elif slot == "light":
            p.lathe([(a * 0.75, H * 0.88), (a * 1.05, H * 0.97), (a * 1.05, H * 0.99)], M(rot=(0, 0, 45)), mat=lit(p), segs=4)
            p.box((a * 1.4, a * 1.4, H * 0.06), T((0, 0, H * 0.96)), mat=lit(p), bevel=0)
        else:
            for x in (-1, 1):
                for y in (-1, 1):
                    p.box((0.02, 0.02, H * 0.12), T((x * a * 0.72, y * a * 0.72, H * 0.94)), mat="iron", bevel=0)
            p.lathe([(a * 1.3, H * 0.995), (a * J(p, 0.3, 0.2), H * 1.05), (0, H * 1.07)], M(rot=(0, 0, 45)), mat="iron", segs=4)
            p.ball(0.03, T((0, 0, H * 1.08)), mat="brass", segs=(6, 4))
    elif e == "Industrial":  # electric pole: tapered steel pole, crook arm, enamel dish, bulb
        reach = r * 12
        if slot == "mount":
            p.lathe([(r * 2.2, 0), (r * 2.0, 0.25), (r * 1.5, 0.45), (r * 1.1, 0.5)], mat="paint", segs=8)
            p.box((r * 1.2, 0.01, 0.18), T((0, -r * 1.9, 0.2)), mat="steel", bevel=0)
        elif slot == "body":
            p.cyl(r * 1.1, r * 0.75, H * 0.95, T((0, 0, 0.5)), mat="steel", segs=8, bevel=0)
            pts = [(0, 0, H * 0.9)] + [(-reach * (1 - math.cos(t)) * 0.5, 0, H * 0.9 + reach * 0.35 * math.sin(t))
                                       for t in (0.6, 1.2, 1.8, 2.4, math.pi)]
            p.tube(pts + [(-reach, 0, H * 0.9 - 0.12)], 0.03, mat="steel", segs=6)
        elif slot == "shade":
            p.lathe([(0.04, H * 0.9 - 0.12), (0.1, H * 0.9 - 0.16), (J(p, 0.26, 0.12), H * 0.9 - 0.28), (0.27, H * 0.9 - 0.3)],
                    T((-reach, 0, 0)), mat="paint", segs=12)
        else:
            p.ball(J(p, 0.07, 0.15), M(loc=(-reach, 0, H * 0.9 - 0.26), scale=(1, 1, 1.25)), mat=lit(p, electric=True), segs=(8, 6))
    elif e == "Steampunk":  # gas street lamp: fluted column, valve base, lit mantle, crowned lantern
        if slot == "mount":
            p.lathe([(r * 3, 0), (r * 2.8, 0.15), (r * 2.0, 0.3), (r * 2.1, 0.5), (r * 1.5, 0.7)], mat="iron", segs=8)
            p.ring(0.08, 0.012, M(loc=(0, -r * 2.4, 0.35), rot=(90, 0, 0)), mat="brass", segs=10)
        elif slot == "body":
            p.lathe([(r * 1.5, 0.7), (r * 1.0, 0.9), (r * J(p, 0.85, 0.08), H * 0.5), (r * 0.7, H * 0.78), (r * 1.4, H * 0.8)],
                    mat="iron", segs=8)
            p.band(r * 0.9, H * 0.42, h=0.08)
            p.tube([(r * 0.95, 0, 0.75), (r * 1.0, 0, H * 0.6), (r * 0.8, 0, H * 0.78)], 0.012, mat="copper", segs=5)
            p.cyl(0.25, 0.25, 0.03, M(loc=(-0.25, 0, H * 0.72), rot=(0, 90, 0)), mat="iron", segs=6, bevel=0)
        elif slot == "light":
            p.lathe([(r * 1.0, H * 0.81), (r * J(p, 2.0, 0.1), H * 0.87), (r * 2.0, H * 0.92), (r * 1.4, H * 0.95)],
                    mat=lit(p), segs=12)
        else:
            for i in range(6):
                a = i * math.tau / 6
                p.tube([(math.cos(a) * r * 1.4, math.sin(a) * r * 1.4, H * 0.8), (math.cos(a) * r * 2.2, math.sin(a) * r * 2.2, H * 0.89),
                        (math.cos(a) * r * 1.6, math.sin(a) * r * 1.6, H * 0.96)], 0.012, mat="brass", segs=4)
            p.lathe([(r * 2.4, H * 0.955), (r * 2.2, H * 0.975), (r * 0.6, H * 1.02), (r * 0.4, H * 1.04), (0, H * 1.07)],
                    mat="brass", segs=10)
            p.ring(r * 0.5, 0.01, M(loc=(0, 0, H * 1.08), rot=(90, 0, 0)), mat="brass", segs=8)
    elif e == "Future":  # hovering light pillar: base pad, split column, floating light bar and halos
        if slot == "mount":
            p.cyl(r * 4, r * 3.6, 0.06, mat="shell_dark", segs=6, bevel=0.1)
            p.ring(r * 3.0, 0.012, T((0, 0, 0.06)), mat="glow", segs=12)
        elif slot == "body":
            p.cyl(r * 1.4, r * 0.9, H * 0.55, T((0, 0, 0.06)), mat="body", segs=8, bevel=0.1)
            p.cyl(r * 0.8, r * 0.7, H * 0.18, T((0, 0, H * 0.62)), mat="body", segs=8, bevel=0.1)
        elif slot == "light":
            p.cyl(r * 0.45, r * J(p, 0.45, 0.2), H * 0.2, T((0, 0, H * 0.82)), mat=lit(p), segs=8, bevel=0)
            p.ball(r * 0.9, T((0, 0, H * 1.04)), mat=lit(p), segs=(10, 6))
        else:
            for i in range(p.rng.randint(2, 3)):
                p.ring(r * (2.0 - 0.4 * i), 0.012, M(loc=(0, 0, H * (0.86 + 0.06 * i)), rot=(J(p, 6, 1), 0, 0)), mat="shell_dark", segs=14)
    elif e == "Wasteland":  # oil-drum base, spliced pipe pole, hubcap hood with salvaged headlight
        reach = 0.5
        if slot == "mount":
            p.cyl(0.3, 0.3, 0.85, mat="body", segs=12, bevel=0)
            for z in (0.28, 0.56):
                p.ring(0.305, 0.012, T((0, 0, z)), mat="body", segs=12, square=False)
            p.box((0.3, 0.01, 0.25), M(loc=(0.05, -0.3, 0.5), rot=(0, 6, 0)), mat="paint", bevel=0)
        elif slot == "body":
            p.cyl(r, r, H * 0.5, T((0, 0, 0.7)), mat="steel", segs=7, bevel=0)
            p.cyl(r * 0.85, r * 0.85, H * 0.45, M(loc=(0, 0, 0.7 + H * 0.49), rot=(J(p, 2, 0.8), 0, 0)), mat="rust", segs=7, bevel=0)
            p.band(r * 1.05, 0.7 + H * 0.5, h=0.12)
            p.tube([(0, 0, H * 0.92), (-reach * 0.6, 0, H * 0.97), (-reach, 0, H * 0.94)], r * 0.5, mat="steel", segs=6)
            p.tube([(r, 0, H * 0.9), (r * 1.6, -0.05, H * 0.6), (r * 1.4, -0.08, H * 0.3)], 0.008, mat="rubber", segs=4)
        elif slot == "shade":
            p.lathe([(J(p, 0.24, 0.12), H * 0.88), (0.2, H * 0.92), (0.06, H * 0.95), (0, H * 0.955)],
                    M(loc=(-reach, 0, 0), rot=(J(p, 5, 1), 0, 0)), mat="steel", segs=10)
            p.cyl(0.09, 0.1, 0.08, M(loc=(-reach, 0, H * 0.86)), mat="paint", segs=8, bevel=0)
        else:
            p.cyl(0.08, 0.08, 0.03, M(loc=(-reach, 0, H * 0.84)), mat=lit(p, electric=True), segs=10, bevel=0)
            p.ball(0.05, M(loc=(-reach, 0, H * 0.84), scale=(1, 1, 0.5)), mat=lit(p, electric=True), segs=(8, 4))
    else:  # Ancient monolith: stepped plinth, tapered pillar with rune slots, crown cradling a rune orb
        if slot == "mount":
            for i, s in enumerate((2.6, 2.0)):
                p.box((r * s * 2, r * s * 2, 0.16), T((0, 0, 0.08 + i * 0.16)), mat="stone_dark", bevel=0.1)
        elif slot == "body":
            p.lathe([(r * 1.3, 0.32), (r * 1.0, H * 0.82)], M(rot=(0, 0, 45)), mat="body", segs=4)
            for i in range(4):
                p.box((r * 0.18, 0.02, H * 0.08), T((0, -r * (1.25 - 0.3 * (0.32 + 0.12 * i)) * 0.71, H * (0.3 + 0.12 * i))),
                      mat="glow", bevel=0)
        elif slot == "shade":
            petals(p, 4, H * 0.8, H * 0.96, r * 0.7, r * J(p, 1.8, 0.1), r * 1.3, 0.05, mat="stone", phase=math.pi / 4)
            p.ring(r * 0.95, 0.02, T((0, 0, H * 0.82)), mat="gold", segs=8)
        else:
            p.ball(r * J(p, 0.9, 0.12), T((0, 0, H * 0.93)), mat=lit(p), segs=(10, 6))
            p.ring(r * 1.3, 0.012, M(loc=(0, 0, H * 0.93), rot=(J(p, 25, 0.4), 0, 0)), mat=lit(p), segs=12)


# ---------------------------------------------------------------- Headlamp (carried; origin under the head loop)
@function("Headlamp", "Lamp", LAMP, "carried")
def headlamp(p, slot):
    e = p.era
    R = F(p, 0.095, 0.06)  # head radius: the band, cap or helmet sits on it
    z = F(p, {"Agrarian": 0.12, "Mercantile": 0.05, "Industrial": 0.06, "Wasteland": 0.06}.get(e, 0.03), 0.1)  # lamp height
    front = (0, -R, z)
    if e == "Primal":  # forehead fire bowl on a hide band
        if slot == "body":
            p.ring(R, J(p, 0.012, 0.25), M(loc=(0, 0, 0.015), scale=(1, J(p, 1.15, 0.05), 1)), mat="hide", segs=12)
        elif slot == "shade":
            p.lathe([(0, z), (0.02, z + 0.004), (J(p, 0.034, 0.12), z + 0.026), (0.03, z + 0.028), (0, z + 0.02)],
                    T((0, -R * 1.15 - 0.022, 0)), mat="ceramic", segs=8, noise=0.05)
            p.box((0.03, 0.01, 0.025), T((0, -R * 1.15 - 0.004, z + 0.005)), mat="bone", bevel=0)
        elif slot == "light":
            flame(p, 0, -R * 1.15 - 0.022, z + 0.022, J(p, 0.016, 0.15))
        else:
            p.ball(0.012, T((0, R * 1.15 + 0.006, 0.015)), mat="hide", segs=(5, 3))
            for s in (-1, 1):
                p.tube([(s * 0.006, R * 1.15 + 0.01, 0.015), (s * J(p, 0.018, 0.3), R * 1.15 + 0.02, -0.05)], 0.003, mat="hide", segs=4)
            if coin(p):
                p.tube([(0.03, R * 1.1, 0.02), (0.05, R * 1.2, 0.09)], 0.004, mat="feather", segs=4)
    elif e == "Agrarian":  # head-top oil lamp: padded ring on the head, spouted clay lamp on top
        if slot == "body":
            p.ring(R * 0.8, 0.018, T((0, 0, 0.018)), mat="cloth", segs=12, square=False)
            for i in range(4):
                a = i * math.tau / 4 + math.pi / 4
                p.tube([(math.cos(a) * R * 0.8, math.sin(a) * R * 0.8, 0.03), (math.cos(a) * R * 0.3, math.sin(a) * R * 0.3, z - 0.01)],
                       0.004, mat="wood", segs=4)
        elif slot == "shade":
            p.lathe([(0, z - 0.012), (0.04, z - 0.01), (J(p, 0.048, 0.1), z + 0.01), (0.03, z + 0.024), (0.012, z + 0.03)],
                    mat="ceramic", segs=10)
            p.tube([(0, -0.03, z + 0.008), (0, -0.065, z + 0.016)], 0.008, mat="ceramic", segs=5)
        elif slot == "light":
            flame(p, 0, -0.066, z + 0.022, J(p, 0.013, 0.15))
        else:
            for s in (-1, 1):
                p.tube([(s * R * 0.78, 0, 0.004), (s * R * J(p, 0.85, 0.1), 0, -0.025), (s * R * 0.6, -R * 0.2, -0.04)], 0.0025, mat="leather", segs=4)
    elif e == "Mercantile":  # miner's oil lamp hooked on a leather cap
        if slot == "body":
            p.lathe([(R * 1.02, 0), (R * 1.05, 0.04), (R * 0.85, 0.09), (R * 0.4, 0.12), (0, 0.125)], mat="leather", segs=12)
            p.ring(R * 1.04, 0.006, T((0, 0, 0.005)), mat="leather", segs=12)
        elif slot == "shade":
            p.lathe([(0, 0), (0.018, 0.003), (J(p, 0.022, 0.12), 0.022), (0.012, 0.034), (0.006, 0.04)],
                    T((0, -R * 1.05 - 0.028, z - 0.02)), mat="brass", segs=10)
            p.tube([(0, -R * 1.05 - 0.035, z - 0.002), (0, -R * 1.05 - 0.06, z + 0.012)], 0.005, mat="brass", segs=5)
        elif slot == "light":
            flame(p, 0, -R * 1.05 - 0.062, z + 0.015, J(p, 0.01, 0.15))
        else:
            p.tube([(0, -R * 1.05, z - 0.03), (0, -R * 1.05 - 0.012, z + 0.005), (0, -R * 1.05 - 0.02, z - 0.004)], 0.0025, mat="iron", segs=4)
            p.box((0.016, 0.004, 0.03), T((0, -R * 1.04, z - 0.035)), mat="iron", bevel=0)
    elif e == "Industrial":  # carbide lamp on a hard hat
        if slot == "body":
            p.lathe([(R * 1.5, 0.0), (R * 1.5, 0.006), (R * 1.0, 0.012), (R * 1.0, 0.05), (R * 0.8, 0.11), (R * 0.4, 0.14), (0, 0.145)],
                    mat="paint", segs=12)
        elif slot == "shade":
            p.cyl(0.018, 0.018, 0.05, M(loc=(0, -R * 1.02 - 0.02, z - 0.04)), mat="brass", segs=8, bevel=0)
            p.lathe([(0.008, 0), (0.02, 0.004), (J(p, 0.04, 0.12), 0.016)], M(loc=(0, -R * 1.02 - 0.03, z + 0.02), rot=(90, 0, 0)),
                    mat="steel", segs=12)
        elif slot == "light":
            flame(p, 0, -R * 1.02 - 0.042, z + 0.012, J(p, 0.008, 0.15), lean=-90)
        else:
            p.box((0.03, 0.006, 0.04), T((0, -R * 1.0, z - 0.02)), mat="steel", bevel=0)
            p.cyl(0.006, 0.006, 0.012, M(loc=(0.018, -R * 1.02 - 0.02, z - 0.01), rot=(0, 90, 0)), mat="brass", segs=6, bevel=0)
            if coin(p):
                p.tube([(0, R * 1.0, 0.03), (0, R * 1.3, -0.02), (0.02, R * 1.2, -0.12)], 0.004, mat="rubber", segs=4)
    elif e == "Steampunk":  # brass headlamp barrel on a riveted leather strap, rear canister
        if slot == "body":
            p.ring(R, 0.014, M(loc=(0, 0, 0.015), scale=(1, 1.15, 1)), mat="leather", segs=12)
            p.tube([(-R, 0, 0.02), (-R * 0.5, 0, 0.11), (R * 0.5, 0, 0.11), (R, 0, 0.02)], 0.008, mat="leather", segs=4)
        elif slot == "shade":
            p.cyl(0.026, J(p, 0.03, 0.1), 0.05, M(loc=(0, -R * 1.15 + 0.01, z), rot=(90, 0, 0)), mat="brass", segs=10, bevel=0)
            p.ring(0.03, 0.004, M(loc=(0, -R * 1.15 - 0.04, z), rot=(90, 0, 0)), mat="copper", segs=10)
        elif slot == "light":
            p.cyl(0.024, 0.024, 0.006, M(loc=(0, -R * 1.15 - 0.038, z), rot=(90, 0, 0)), mat=lit(p), segs=10, bevel=0)
            p.ball(0.012, M(loc=(0, -R * 1.15 - 0.042, z), scale=(1, 0.6, 1)), mat=lit(p), segs=(6, 4))
        else:
            p.cyl(0.02, 0.02, J(p, 0.06, 0.15), M(loc=(0.03, R * 1.15 + 0.02, 0.0), rot=(0, 90, 0)), mat="brass", segs=8, bevel=0)
            p.tube([(0.0, R * 1.15 + 0.02, 0.02), (R * 0.9, R * 0.6, 0.03), (R * 0.9, -R * 0.6, 0.03), (0.02, -R * 1.15 + 0.01, z)],
                   0.003, mat="copper", segs=4)
    elif e == "Future":  # head-ring light: thin circlet, emitter strip, visor fin, rear node
        if slot == "body":
            p.ring(R, J(p, 0.006, 0.3), M(loc=(0, 0, z), scale=(1, 1.15, J(p, 1.0, 0.3))), mat="body", segs=16)
        elif slot == "light":
            for i in range(p.rng.choice((3, 5))):
                a = math.radians(-90 + (i - 1) * 12)
                p.box((0.018, 0.006, 0.006), M(loc=(math.cos(a) * R * 1.01, math.sin(a) * R * 1.16, z), rot=(0, 0, math.degrees(a) + 90)),
                      mat=lit(p), bevel=0)
        elif slot == "shade":
            p.plate([(-0.05, 0), (-0.04, 0.02), (0.04, 0.02), (0.05, 0)], 0.004, M(loc=(0, -R * 1.15 - 0.006, z - 0.01), rot=(J(p, -20, 0.4), 0, 0)),
                    mat="shell_dark", bevel=0)
        else:
            p.box((0.03, 0.02, 0.02), T((0, R * 1.15, z)), mat="shell_dark", bevel=0.2)
    elif e == "Wasteland":  # dented hard hat with a flashlight taped on
        if slot == "body":
            p.lathe([(R * 1.15, 0.0), (R * 1.1, 0.01), (R * 1.0, 0.05), (R * 0.8, 0.11), (R * 0.3, 0.135), (0, 0.14)],
                    M(rot=(J(p, 4, 0.5), 0, 0)), mat="paint", segs=10, noise=0.03)
        elif slot == "shade":
            p.cyl(0.018, 0.022, J(p, 0.1, 0.15), M(loc=(0.02, -R * 1.0 - 0.018, z), rot=(0, 90, 0)), mat="steel", segs=8, bevel=0)
        elif slot == "light":
            p.cyl(0.02, 0.02, 0.006, M(loc=(0.018, -R * 1.0 - 0.018, z), rot=(0, -90, 0)), mat=lit(p), segs=8, bevel=0)
        else:
            for x in (0.04, 0.08):
                p.ring(0.024, 0.004, M(loc=(x, -R * 1.0 - 0.018, z), rot=(0, 90, 0)), mat="cloth", segs=8)
            p.tube([(0.1, -R, z), (0.12, -R * 0.5, 0.05), (0.1, 0, 0.12)], 0.002, mat="iron", segs=4)
    else:  # Ancient: stone circlet, brow rune gem in a petal setting, gold rear clasp
        if slot == "body":
            p.ring(R, J(p, 0.012, 0.25), M(loc=(0, 0, z), scale=(1, 1.15, J(p, 1.2, 0.3))), mat="body", segs=10)
        elif slot == "light":
            p.ball(J(p, 0.014, 0.15), M(loc=(0, -R * 1.15 - 0.012, z + 0.01), scale=(1, 0.7, 1.4)), mat=lit(p), segs=(4, 2))
            for s in (-1, 1):
                p.box((0.012, 0.004, 0.004), M(loc=(s * 0.04, -R * 1.12, z), rot=(0, 0, s * 20)), mat=lit(p), bevel=0)
        elif slot == "shade":
            petals(p, 3, z - 0.01, z + J(p, 0.04, 0.15), 0.0, 0.012, 0.022, 0.006, mat="stone", phase=0)
        else:
            p.box((0.03, 0.012, 0.022), T((0, R * 1.15, z)), mat="gold", bevel=0.1)


# ---------------------------------------------------------------- Censer (carried; stands on z = 0)
@function("Censer", "Lamp", LAMP, "carried")
def censer(p, slot):
    e = p.era
    h = F(p, {"Primal": 0.08, "Mercantile": 0.12, "Steampunk": 0.16, "Future": 0.14}.get(e, 0.12), 0.1)
    r = F(p, {"Primal": 0.08, "Agrarian": 0.075, "Industrial": 0.07, "Wasteland": 0.05}.get(e, 0.06), 0.1)
    if e == "Primal":  # smoke stone: hollowed rock on pebbles, smouldering herb bundle and embers
        if slot == "body":
            p.lathe([(0, 0.015), (r * 0.9, 0.02), (r * 1.1, h * 0.5), (r * 1.0, h), (r * 0.7, h * 0.95), (0, h * 0.7)],
                    mat="stone", segs=10, noise=0.06)
        elif slot == "light":
            for i in range(p.rng.randint(3, 5)):
                a = p.rng.uniform(0, math.tau)
                p.ball(r * J(p, 0.18, 0.3), T((math.cos(a) * r * 0.35, math.sin(a) * r * 0.35, h * 0.78)), mat=lit(p), segs=(5, 3))
        elif slot == "shade":
            for i in range(3):
                a = J(p, 0.6, 0.5) + i * 0.5
                p.tube([(-math.cos(a) * r * 0.8, -math.sin(a) * r * 0.8, h * 0.82), (math.cos(a) * r * 0.8, math.sin(a) * r * 0.8, h * 0.88)],
                       0.006, mat="cloth", segs=4)
        else:
            for i in range(3):
                a = i * math.tau / 3 + 0.3
                p.ball(r * J(p, 0.25, 0.2), M(loc=(math.cos(a) * r * 0.6, math.sin(a) * r * 0.6, 0.012), scale=(1, 1, 0.6)),
                       mat="stone_dark", segs=(5, 3))
    elif e == "Agrarian":  # clay incense burner: tripod pot, lid, incense sticks with glowing tips
        if slot == "body":
            p.lathe([(0, 0.02), (r * 0.7, 0.02), (r * 1.05, h * 0.45), (r * 0.9, h * 0.85), (r * 0.95, h)], mat="ceramic", segs=12)
            for s in (-1, 1):
                p.ring(0.014, 0.004, M(loc=(s * r, 0, h * 0.8), rot=(0, 90, 0)), mat="ceramic", segs=6)
        elif slot == "shade":
            p.lathe([(r * 0.98, h), (r * 0.8, h + 0.02), (r * 0.2, h + 0.03), (0.01, h + 0.04), (0, h + 0.05)], mat="glaze", segs=12)
        elif slot == "light":
            for i in range(p.rng.randint(1, 3)):
                x = (i - 1) * 0.012
                L = J(p, 0.12, 0.25)
                p.cyl(0.0018, 0.0018, L, M(loc=(x, 0.01, h), rot=(J(p, 6, 1), 0, 0)), mat="wood", segs=4, bevel=0)
                p.ball(0.0035, T((x, 0.01, h + L)), mat=lit(p), segs=(4, 3))
            p.ring(r * 0.4, 0.003, T((0, 0, h + 0.03)), mat=lit(p), segs=8)
        else:
            for i in range(3):
                a = i * math.tau / 3 + math.pi / 2
                p.cyl(0.012, 0.008, 0.03, M(loc=(math.cos(a) * r * 0.65, math.sin(a) * r * 0.65, 0.0)), mat="ceramic", segs=6, bevel=0)
    elif e == "Mercantile":  # brass hanging thurible: footed bowl, pierced dome, glowing seam, three chains
        top = h * 1.0 + 0.36
        if slot == "body":
            p.lathe([(r * 0.5, 0), (r * 0.5, 0.012), (r * 0.25, 0.02), (r * 0.9, h * 0.25), (r * 1.1, h * 0.45)], mat="brass", segs=12)
        elif slot == "light":
            p.ring(r * J(p, 1.08, 0.04), J(p, 0.006, 0.3), T((0, 0, h * 0.47)), mat=lit(p), segs=12)
        elif slot == "shade":
            p.lathe([(r * 1.1, h * 0.48), (r * J(p, 1.0, 0.08), h * 0.7), (r * 0.5, h * 0.95), (r * 0.15, h), (0, h * 1.05)],
                    mat="brass", segs=12)
            for i in range(4):
                a = i * math.tau / 4
                p.box((0.004, 0.004, h * 0.18), M(loc=(math.cos(a) * r * 0.95, math.sin(a) * r * 0.95, h * 0.68), rot=(0, 0, math.degrees(a))),
                      mat=lit(p), bevel=0)
        else:
            for i in range(3):
                a = i * math.tau / 3 + math.pi / 2
                chain(p, (math.cos(a) * r * 1.1, math.sin(a) * r * 1.1, h * 0.47), (0, 0, top))
            p.cyl(0.012, 0.012, 0.012, T((0, 0, top - 0.006)), mat="brass", segs=8, bevel=0)
            p.ring(J(p, 0.018, 0.15), 0.003, M(loc=(0, 0, top + 0.024), rot=(90, 0, 0)), mat="brass", segs=8, square=False)
    elif e == "Industrial":  # cast-iron burner: drum pot on legs, glowing grate window, lid with chimney
        if slot == "body":
            p.cyl(r, r * 1.05, h, T((0, 0, 0.03)), mat="iron", segs=12, bevel=0)
            for s in (-1, 1):
                p.tube([(s * r, 0, h * 0.8), (s * r * 1.35, 0, h * 0.85), (s * r * 1.35, 0, h * 0.55), (s * r, 0, h * 0.5)], 0.004,
                       mat="iron", segs=4)
        elif slot == "light":
            p.box((r * 0.9, 0.006, h * 0.45), T((0, -r * 1.02, 0.03 + h * 0.45)), mat=lit(p), bevel=0)
            for i in range(3):
                p.box((r * 0.9, 0.006, 0.004), T((0, -r * 1.04, 0.03 + h * (0.3 + i * 0.15))), mat="iron", bevel=0)
        elif slot == "shade":
            p.lathe([(r * 1.08, h + 0.03), (r * 0.9, h + 0.05), (r * 0.25, h + 0.06), (r * 0.2, h + 0.06 + J(p, 0.06, 0.2)),
                     (r * 0.3, h + 0.07 + J(p, 0.06, 0.2))], mat="iron", segs=10)
        else:
            for i in range(3):
                a = i * math.tau / 3 + math.pi / 2
                p.cyl(0.006, J(p, 0.01, 0.25), 0.035, M(loc=(math.cos(a) * r * 0.85, math.sin(a) * r * 0.85, 0.0)), mat="steel", segs=6, bevel=0)
    elif e == "Steampunk":  # steam-mist burner: brass boiler globe, portholes, vented dome, tripod
        if slot == "body":
            p.lathe([(0, 0.03), (r * 0.8, 0.035), (r * 1.15, h * 0.4), (r * 1.1, h * 0.7), (r * 0.8, h * 0.82)], mat="brass", segs=12)
            p.band(r * 1.15, h * 0.42, h=0.02)
        elif slot == "light":
            for i in range(3):
                a = -math.pi / 2 + (i - 1) * 0.9
                p.cyl(0.016, 0.016, 0.006, M(loc=(math.cos(a) * r * 1.12, math.sin(a) * r * 1.12, h * 0.6), rot=(90, 0, math.degrees(a) + 90)),
                      mat=lit(p), segs=8, bevel=0)
            p.ball(0.01, T((0, 0, h * 1.0 + J(p, 0.05, 0.2))), mat=lit(p), segs=(6, 4))
        elif slot == "shade":
            p.lathe([(r * 0.8, h * 0.82), (r * 0.5, h * 0.92), (r * 0.15, h)], mat="copper", segs=10)
            for s in (-1, 1):
                p.tube([(s * r * 0.4, 0, h * 0.88), (s * r * 0.6, 0, h * 1.02), (s * r * J(p, 0.5, 0.2), 0, h * 1.1)], 0.006, mat="copper", segs=5)
            p.ring(0.014, 0.003, M(loc=(r * 0.5, -r * 0.5, h * 0.9), rot=(90, 0, 45)), mat="brass", segs=8)
        else:
            for i in range(3):
                a = i * math.tau / 3 + math.pi / 2
                p.tube([(math.cos(a) * r * 0.75, math.sin(a) * r * 0.75, 0.04), (math.cos(a) * r * 1.0, math.sin(a) * r * 1.0, 0.0)], 0.005,
                       mat="iron", segs=4)
            bail(p, r * 1.15, h * 0.5, J(p, h * 0.9, 0.12), mat="brass", r=0.003)
    elif e == "Future":  # light-mist emitter: hover ring, shell pod, aperture petals, glowing plume
        if slot == "mount":
            p.ring(r * J(p, 0.9, 0.1), J(p, 0.006, 0.3), T((0, 0, 0.006)), mat="shell_dark", segs=14)
        elif slot == "body":
            p.lathe([(0, 0.025), (r * 0.6, 0.03), (r * 1.0, h * 0.35), (r * 0.9, h * 0.6), (r * 0.6, h * 0.7)], mat="body", segs=14)
        elif slot == "shade":
            petals(p, 3, h * 0.65, h * 0.8, r * 0.6, r * J(p, 0.85, 0.1), r * 0.8, 0.005, mat="shell_dark", phase=math.pi / 6)
        else:
            k = J(p, 1.0, 0.15)
            p.lathe([(r * 0.35, h * 0.68), (r * 0.5 * k, h * 0.95), (r * 0.3, h * 1.25), (r * 0.45 * k, h * 1.5), (0, h * 1.7)],
                    mat=lit(p), segs=10)
    elif e == "Wasteland":  # punched tin can on a wire bail, crimped lid, glowing embers through holes
        if slot == "body":
            p.cyl(r, r * 0.98, h, mat="steel", segs=9, bevel=0)
            p.box((r * 1.2, 0.002, h * 0.4), T((0, -r * 0.99, h * 0.5)), mat="paint", bevel=0)
        elif slot == "light":
            for i in range(p.rng.randint(4, 6)):
                a = -math.pi / 2 + p.rng.uniform(-1.2, 1.2)
                p.box((0.008, 0.004, 0.008), M(loc=(math.cos(a) * r * 1.0, math.sin(a) * r * 1.0, h * p.rng.uniform(0.15, 0.4)),
                                               rot=(0, 0, math.degrees(a) + 90)), mat=lit(p), bevel=0)
            p.cyl(r * 0.85, r * 0.85, 0.01, T((0, 0, h * 0.7)), mat=lit(p), segs=8, bevel=0)
        elif slot == "shade":
            p.lathe([(r * J(p, 1.05, 0.04), h * 0.95), (r * 0.6, h * 1.08), (r * 0.15, h * 1.12)], M(rot=(J(p, 6, 0.8), 0, 0)), mat="iron", segs=9)
        else:
            bail(p, r * 1.0, h * 0.85, J(p, 0.22, 0.15), mat="iron", r=0.002)
            p.band(r * 1.0, h * 0.85, h=0.015)
    else:  # Ancient: square stepped base, stone bowl on a stem, rune slots, floating mist orb
        if slot == "mount":
            p.box((r * 2.4, r * 2.4, 0.02), T((0, 0, 0.01)), mat="stone_dark", bevel=0.1)
        elif slot == "body":
            p.lathe([(r * 0.4, 0.02), (r * 0.3, h * 0.35), (r * 0.6, h * 0.5), (r * 1.15, h * 0.8), (r * 1.1, h * 0.9)], mat="body", segs=8)
            for i in range(4):
                a = i * math.tau / 4 + math.pi / 8
                p.box((0.012, 0.006, 0.01), M(loc=(math.cos(a) * r * 1.0, math.sin(a) * r * 1.0, h * 0.72), rot=(0, 0, math.degrees(a) + 90)),
                      mat="glow", bevel=0)
        elif slot == "shade":
            p.ring(r * 1.0, 0.008, M(loc=(0, 0, h * 1.1), rot=(J(p, 10, 0.5), 0, 0)), mat="stone", segs=8)
        else:
            p.ball(r * J(p, 0.45, 0.12), T((0, 0, h * 1.12)), mat=lit(p), segs=(8, 6))
