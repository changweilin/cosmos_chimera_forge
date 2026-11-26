"""Vessel-family forms (cosmos_chimera everyday-objects-catalog.md): Bucket, Basket, Pot, Strongbox, MedKit, Mortar,
Creel, Bell. Slots are kit_forms.VESSEL (body, lid, handle, band); every era builds its own functional equivalent.

Frame: Z up, front -Y, origin at the floor contact (the bottom also rides the shoulder when an NPC carries it).
Open vessels use the lid slot for their mouth (rim, hoop, funnel); bells use it for the crown.
Each form draws its F() frame values first, in a fixed order, so every slot of one (function, era) shares them.
"""
import math

from mathutils import Matrix, Vector

from kit_forms import VESSEL, F, J, coin, function
from kit_lib import M


def T(x, y, z):
    return Matrix.Translation((x, y, z))


def rad_at(outer, z):
    """Outer radius of a lathe profile [(r, z), ...] at height z (linear between points)."""
    for (r0, z0), (r1, z1) in zip(outer, outer[1:]):
        if z0 <= z <= z1 and z1 > z0:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return outer[-1][0] if z > outer[-1][1] else outer[0][0]


def shell(p, outer, wall, mat="body", segs=12, floor=None, m=None, **kw):
    """Open vessel: outer profile bottom to rim, a flat rim of width `wall`, then the inner wall back down."""
    z0 = outer[0][1]
    fl = floor if floor is not None else z0 + wall
    inner = [(max(r - wall, 0.003), z) for r, z in reversed(outer) if z > fl + 1e-4]
    prof = [(0, z0)] + list(outer) + inner + [(inner[-1][0] if inner else 0.003, fl), (0, fl)]
    p.lathe(prof, m, mat=mat, segs=segs, **kw)


def closed(p, outer, mat="body", segs=12, m=None, **kw):
    """Closed solid of revolution from the bottom centre to the top centre."""
    prof = [(0, outer[0][1])] + list(outer) + [(0, outer[-1][1])]
    p.lathe(prof, m, mat=mat, segs=segs, **kw)


def bail(p, half, z0, rise, rad, mat="fit", segs=4, n=7, m=None, y=0.0):
    """Arched handle in the XZ plane from (-half, z0) over to (+half, z0)."""
    mm = m or Matrix()
    pts = []
    for i in range(n):
        t = math.pi * i / (n - 1)
        pts.append(tuple(mm @ Vector((-half * math.cos(t), y, z0 + rise * math.sin(t)))))
    p.tube(pts, rad, mat=mat, segs=segs)


def bell_shape(p, r, h, wall, mat="body", segs=12, waist=0.62, m=None, **kw):
    """Hollow bell standing on its mouth at z = 0, crown at z = h."""
    outer = [(r, 0), (r * 0.97, h * 0.07), (r * 0.76, h * 0.3), (r * waist, h * 0.62), (r * waist * 0.95, h * 0.9),
             (r * waist * 0.7, h)]
    inner = [(0, h - wall * 1.5), (r * waist * 0.95 - wall, h * 0.86), (r * waist - wall, h * 0.6),
             (r * 0.76 - wall, h * 0.3), (r - wall, 0)]
    p.lathe(inner + outer + [(0, h)], m, mat=mat, segs=segs, **kw)
    return outer


def lugs(p, x, z, rr, t, mat, segs=8):
    """Pair of ring handles on the +-X sides, each standing in the YZ plane."""
    for s in (-1, 1):
        p.ring(rr, t, M(loc=(s * x, 0, z), rot=(0, 90, 0)), mat=mat, segs=segs)


def weave(p, outer, zs, mat, t=0.006, segs=10, scale=(1, 1, 1)):
    """Horizontal weave courses on a lathe body."""
    for z in zs:
        p.ring(rad_at(outer, z) * 1.01, t, M(loc=(0, 0, z), scale=scale), mat=mat, segs=segs, square=False)


def ribs(p, outer, n, mat, rad=0.004, z0=None, z1=None, scale=(1, 1), phase=0.0):
    """Vertical rods following a lathe profile (wire cages, wicker stakes)."""
    a0 = outer[0][1] if z0 is None else z0
    a1 = outer[-1][1] if z1 is None else z1
    for i in range(n):
        a = i * math.tau / n + phase
        pts = []
        for k in range(3):
            z = a0 + (a1 - a0) * k / 2
            rr = rad_at(outer, z) * 1.005
            pts.append((math.cos(a) * rr * scale[0], math.sin(a) * rr * scale[1], z))
        p.tube(pts, rad, mat=mat, segs=4)


# ---------------------------------------------------------------- Bucket
@function("Bucket", "Vessel", VESSEL, "carried")
def bucket(p, slot):
    e = p.era
    h, r = F(p, 0.30, 0.1), F(p, 0.15, 0.1)
    rb = r * F(p, 0.8, 0.06)
    if e == "Primal":  # hide water bag sewn to a bent-wood hoop
        outer = [(rb * 0.55, 0), (r * 1.08, h * 0.35), (r * 0.98, h * 0.75), (r * 0.88, h)]
        if slot == "body":
            shell(p, outer, 0.01, mat="hide", segs=10, noise=0.02)
        elif slot == "lid":
            p.ring(r * 0.88, J(p, 0.013, 0.2), T(0, 0, h), mat="wood", segs=10, square=False)
            for i in range(p.rng.randint(3, 5)):
                a = i * math.tau / 5 + 0.3
                p.box((0.006, 0.02, 0.03), M(loc=(math.cos(a) * r * 0.88, math.sin(a) * r * 0.88, h - 0.01), rot=(0, 0, math.degrees(a))), mat="rope", bevel=0)
        elif slot == "handle":
            bail(p, r * 0.88, h, J(p, h * 0.55, 0.15), 0.008, mat="rope")
        else:
            p.band(rad_at(outer, h * 0.55), h * 0.55, h=J(p, 0.05, 0.2))
    elif e == "Agrarian":  # coopered wooden pail with two tall ear staves
        outer = [(rb, 0), (r, h)]
        if slot == "body":
            shell(p, outer, 0.014, mat="wood", segs=10, floor=0.03)
        elif slot == "lid":
            ew = J(p, 0.05, 0.15)
            for s in (-1, 1):
                p.box((ew, 0.024, h * 0.32), T(s * r * 0.97, 0, h + h * 0.1), mat="wood", bevel=0.05)
            p.ring(r * 0.99, 0.006, T(0, 0, h - 0.004), mat="wood", segs=10)
        elif slot == "handle":
            if coin(p):
                p.cyl(0.013, 0.013, r * 2.3, M(loc=(-r * 1.15, 0, h * 1.2), rot=(0, 90, 0)), mat="wood", segs=6)
            else:
                bail(p, r * 0.97, h * 1.18, J(p, h * 0.3, 0.2), 0.006, mat="rope", n=5)
        else:
            for z in (J(p, 0.15, 0.2), J(p, 0.8, 0.06)):
                p.band(rad_at(outer, h * z), h * z, h=0.04)
    elif e == "Mercantile":  # spun copper bucket, iron bail on brass ears
        outer = [(rb * 0.95, 0), (rb, 0.02), (r * 0.95, h * 0.6), (r, h)]
        if slot == "body":
            shell(p, outer, 0.008, mat="copper", segs=12)
        elif slot == "lid":
            p.ring(r * 1.0, J(p, 0.008, 0.2), T(0, 0, h), mat="copper", segs=12, square=False)
        elif slot == "handle":
            ez = h * J(p, 0.88, 0.03)
            for s in (-1, 1):
                p.box((0.012, 0.035, 0.04), T(s * rad_at(outer, ez), 0, ez), mat="brass", bevel=0)
            bail(p, rad_at(outer, ez) + 0.006, ez, J(p, r * 1.0, 0.15), 0.005, mat="iron")
        else:
            bz = h * J(p, 0.3, 0.2)
            p.ring(rad_at(outer, bz) * 1.02, 0.008, T(0, 0, bz), mat="brass", segs=12)
    elif e == "Industrial":  # pressed tin pail, wire bail with wooden grip
        outer = [(rb, 0), (r, h)]
        if slot == "body":
            shell(p, outer, 0.006, mat="steel", segs=12, floor=0.012)
        elif slot == "lid":
            p.ring(r * 1.01, J(p, 0.007, 0.2), T(0, 0, h - 0.003), mat="steel", segs=12, square=False)
        elif slot == "handle":
            rise = J(p, r * 0.95, 0.12)
            bail(p, r * 1.0, h * 0.92, rise, 0.003, mat="steel", segs=4)
            p.cyl(0.012, 0.012, 0.09, M(loc=(-0.045, 0, h * 0.92 + rise), rot=(0, 90, 0)), mat="wood", segs=6)
        else:
            for z in (0.3, J(p, 0.66, 0.08)):
                p.ring(rad_at(outer, h * z) * 1.005, 0.005, T(0, 0, h * z), mat="steel", segs=12, square=False)
    elif e == "Steampunk":  # brass kettle-bucket: domed lid, spout, gauge
        outer = [(rb, 0), (r * 1.05, h * 0.4), (r, h * 0.8), (r * 0.78, h * 0.92)]
        if slot == "body":
            shell(p, outer, 0.01, mat="brass", segs=10)
            p.tube([(0, -r * 0.95, h * 0.4), (0, -r * 1.3, h * 0.65), (0, -r * J(p, 1.45, 0.06), h * 0.92)], 0.013, mat="brass", segs=6)
        elif slot == "lid":
            z0 = h * 0.92
            p.lathe([(r * 0.8, z0), (r * 0.62, z0 + h * J(p, 0.09, 0.2)), (0.02, z0 + h * 0.12), (0.028, z0 + h * 0.16), (0, z0 + h * 0.17)], mat="copper", segs=12)
        elif slot == "handle":
            ez = h * 0.85
            bail(p, rad_at(outer, ez) + 0.008, ez, J(p, r * 1.1, 0.12), 0.007, mat="copper", segs=5)
            for s in (-1, 1):
                p.ball(0.014, T(s * (rad_at(outer, ez) + 0.008), 0, ez), mat="brass", segs=(5, 3))
        else:
            p.band(rad_at(outer, h * 0.2), h * 0.2, h=0.05)
            gz = h * J(p, 0.6, 0.1)
            gx = rad_at(outer, gz)
            p.cyl(0.03, 0.03, 0.012, M(loc=(gx, 0, gz), rot=(0, 90, 0)), mat="brass", segs=8)
            p.cyl(0.024, 0.024, 0.002, M(loc=(gx + 0.012, 0, gz), rot=(0, 90, 0)), mat="glow", segs=8, bevel=0)
    elif e == "Future":  # insulated canister with screw cap
        outer = [(r * 0.92, 0), (r, 0.03), (r, h * 0.88)]
        if slot == "body":
            shell(p, outer, 0.02, mat="body", segs=16)
        elif slot == "lid":
            z0 = h * 0.88
            p.lathe([(r, z0), (r * 0.97, z0 + h * 0.08), (r * J(p, 0.7, 0.1), z0 + h * 0.13), (0, z0 + h * 0.14)], mat="shell_dark", segs=16)
        elif slot == "handle":
            hz = h * 0.7
            for s in (-1, 1):
                p.cyl(0.022, 0.022, 0.014, M(loc=(s * r, 0, hz), rot=(0, 90 * s, 0)), mat="shell_dark", segs=10)
            bail(p, r + 0.01, hz, J(p, h * 0.55, 0.12), 0.009, mat="grip", segs=4, n=6)
        else:
            p.band(r, h * J(p, 0.22, 0.15), h=0.05)
            p.box((0.04, 0.004, 0.014), T(0, -r - 0.001, h * 0.5), mat="glow", bevel=0)
    elif e == "Wasteland":  # cut-down drum, rebar bail, patched
        outer = [(r * 0.95, 0), (r * 0.95, h * 0.5), (r * 0.95, h)]
        if slot == "body":
            shell(p, outer, 0.006, mat="rust", segs=9, noise=0.012)
            p.box((r * 0.7, 0.012, h * J(p, 0.3, 0.25)), M(loc=(r * 0.15, -r * 0.95, h * 0.5), rot=(0, J(p, 8, 0.6), 0)), mat="iron", bevel=0)
        elif slot == "lid":
            p.ring(r * 0.96, J(p, 0.01, 0.2), T(0, 0, h - 0.004), mat="iron", segs=9)
            if coin(p):
                p.tube([(r * 0.6, -r * 0.7, h), (r * 0.9, -r * 0.9, h + 0.03), (r * 1.1, -r * 1.0, h - 0.04)], 0.01, mat="rubber", segs=4)
        elif slot == "handle":
            w = [J(p, 0.012, 0.8) for _ in range(5)]
            rise = J(p, r * 1.0, 0.15)
            pts = [(-r * 0.97, 0, h * 0.9), (-r * 0.7, w[0], h * 0.9 + rise * 0.7), (0, w[1], h * 0.9 + rise), (r * 0.7, w[2], h * 0.9 + rise * 0.7), (r * 0.97, 0, h * 0.9)]
            p.tube(pts, 0.005, mat="iron", segs=4)
            p.cyl(0.015, 0.015, 0.08, M(loc=(-0.04, w[1], h * 0.9 + rise), rot=(0, 90, 0)), mat="cloth", segs=5, noise=0.05)
        else:
            p.band(r * 0.95, h * J(p, 0.5, 0.2), h=0.06)
    else:  # Ancient: seamless stone pail, lug rings, rune ring
        outer = [(r * 0.72, 0), (r * 0.95, h * 0.15), (r * 1.05, h * 0.55), (r * 0.95, h)]
        if slot == "body":
            shell(p, outer, 0.028, mat="stone", segs=10)
        elif slot == "lid":
            p.ring(r * 0.94, J(p, 0.018, 0.15), T(0, 0, h), mat="stone_dark", segs=10, square=False)
        elif slot == "handle":
            lz = h * J(p, 0.82, 0.04)
            lugs(p, rad_at(outer, lz) + 0.02, lz, J(p, 0.035, 0.15), 0.011, "stone_dark")
        else:
            p.band(rad_at(outer, h * 0.5), h * J(p, 0.5, 0.12), h=0.07)


# ---------------------------------------------------------------- Basket
@function("Basket", "Vessel", VESSEL, "carried")
def basket(p, slot):
    e = p.era
    h, r = F(p, 0.24, 0.12), F(p, 0.19, 0.1)
    sy = F(p, 0.72, 0.08)
    rb = r * F(p, 0.78, 0.06)
    oval = M(scale=(1, sy, 1))
    outer = [(rb, 0), (rb * 1.04, 0.02), (r, h)]
    if e == "Primal":  # folded bark basket, vine strap
        outer = [(rb * 0.9, 0), (r * 1.02, h * 0.55), (r, h)]
        if slot == "body":
            shell(p, outer, 0.008, mat="bark", segs=6, m=M(scale=(1, sy * 0.85, 1)), noise=0.035)
        elif slot == "lid":
            p.ring(r * 1.0, J(p, 0.012, 0.2), M(loc=(0, 0, h), scale=(1, sy * 0.85, 1)), mat="wood", segs=8, square=False)
        elif slot == "handle":
            bail(p, r * 0.98, h * 0.9, h * J(p, 0.75, 0.15), 0.007, mat="rope", segs=4, m=M(rot=(J(p, 12, 0.5), 0, 0)))
        else:
            for z in (0.25, J(p, 0.7, 0.1)):
                p.ring(rad_at(outer, h * z) * 1.02, 0.007, M(loc=(0, 0, h * z), scale=(1, sy * 0.85, 1)), mat="rope", segs=8, square=False)
    elif e == "Agrarian":  # round woven bamboo basket, tall hoop handle
        if slot == "body":
            shell(p, outer, 0.008, mat="wood", segs=12, m=oval)
        elif slot == "lid":
            p.ring(r * 1.0, J(p, 0.011, 0.2), M(loc=(0, 0, h), scale=(1, sy, 1)), mat="wood", segs=12, square=False)
        elif slot == "handle":
            bail(p, r * 0.98, h * 0.92, J(p, h * 1.25, 0.12), 0.009, mat="wood", segs=4)
        else:
            weave(p, outer, [h * z for z in (0.2, J(p, 0.45, 0.1), 0.7)], "rope", t=0.005, segs=12, scale=(1, sy, 1))
    elif e == "Mercantile":  # oval rattan hand-basket with two hinged lid flaps
        if slot == "body":
            shell(p, outer, 0.008, mat="bark", segs=12, m=oval)
            p.ring(rb * 1.02, 0.008, M(loc=(0, 0, 0.012), scale=(1, sy, 1)), mat="wood", segs=12, square=False)
        elif slot == "lid":
            tilt = J(p, 6, 0.8)
            for s in (-1, 1):
                p.plate([(-r * 0.0, 0), (r * 0.6, 0), (r * 0.92, -0.01), (r * 0.6, -0.012), (0, -0.012)],
                        r * sy * 1.5, M(loc=(0, 0, h + 0.012), rot=(0, s * tilt, 0 if s > 0 else 180)), mat="bark", bevel=0)
        elif slot == "handle":
            rise = J(p, h * 0.9, 0.12)
            bail(p, r * 0.97, h, rise, 0.01, mat="wood", segs=5)
            p.cyl(0.016, 0.016, 0.1, M(loc=(-0.05, 0, h + rise), rot=(0, 90, 0)), mat="grip", segs=6)
        else:
            weave(p, outer, [h * 0.35, h * J(p, 0.7, 0.08)], "grip", t=0.006, segs=10, scale=(1, sy, 1))
    elif e == "Industrial":  # wire basket: pressed base, upright wires, wire courses
        if slot == "body":
            p.cyl(rb, rb, 0.008, M(scale=(1, sy, 1)), mat="steel", segs=10)
            ribs(p, outer, 10, "steel", rad=0.0025, scale=(1, sy))
        elif slot == "lid":
            p.ring(r * 1.0, J(p, 0.006, 0.2), M(loc=(0, 0, h), scale=(1, sy, 1)), mat="steel", segs=12, square=False)
        elif slot == "handle":
            rise = J(p, h * 0.8, 0.15)
            bail(p, r * 0.98, h, rise, 0.0035, mat="steel", segs=4)
            p.cyl(0.011, 0.011, 0.1, M(loc=(-0.05, 0, h + rise), rot=(0, 90, 0)), mat="grip", segs=6)
        else:
            weave(p, outer, [h * 0.33, h * J(p, 0.66, 0.1)], "steel", t=0.0025, segs=10, scale=(1, sy, 1))
    elif e == "Steampunk":  # brass-framed mesh basket, riveted strap handle
        if slot == "body":
            shell(p, outer, 0.006, mat="iron", segs=10, m=oval)
            ribs(p, outer, 6, "brass", rad=0.006, scale=(1, sy), phase=math.pi / 6)
        elif slot == "lid":
            p.ring(r * 1.01, J(p, 0.01, 0.2), M(loc=(0, 0, h), scale=(1, sy, 1)), mat="brass", segs=10)
            if coin(p):
                p.plate([(0, 0), (r * 0.9, 0), (r * 0.9, 0.01), (0, 0.01)], r * sy * 1.6, M(loc=(-r * 0.45, 0, h + 0.005)), mat="iron", bevel=0)
        elif slot == "handle":
            rise = J(p, h * 0.85, 0.12)
            bail(p, r * 1.0, h, rise, 0.008, mat="brass", segs=4)
            for s in (-1, 1):
                p.cyl(0.02, 0.02, 0.01, M(loc=(s * r * 1.0, 0, h), rot=(0, 90 * s, 0)), mat="copper", segs=8)
        else:
            p.band(rad_at(outer, h * 0.5), h * J(p, 0.5, 0.15), m=oval, h=0.04)
    elif e == "Future":  # hover basket: shallow shell bowl over a field pad
        z0 = 0.05
        bowl = [(rb * 0.8, z0), (r * 0.9, z0 + h * 0.35), (r, h)]
        if slot == "body":
            shell(p, bowl, 0.012, mat="body", segs=14, m=oval)
        elif slot == "lid":
            p.ring(r * 1.0, J(p, 0.01, 0.2), M(loc=(0, 0, h), scale=(1, sy, 1)), mat="shell_dark", segs=14)
        elif slot == "handle":
            rise = J(p, h * 0.75, 0.12)
            bail(p, r * 0.95, h, rise, 0.01, mat="shell_dark", segs=4, n=6)
        else:
            p.cyl(rb * 0.5, rb * 0.55, 0.03, M(scale=(1, sy, 1)), mat="shell_dark", segs=12)
            p.cyl(rb * 0.62, rb * 0.7, z0 - 0.03, M(loc=(0, 0, 0.03), scale=(1, sy, 1)), mat="glow", segs=12, cap=False)
    elif e == "Wasteland":  # wire basket patched with sheet and tied with hose
        if slot == "body":
            p.cyl(rb, rb, 0.01, M(scale=(1, sy, 1)), mat="rust", segs=9)
            ribs(p, outer, 9, "rust", rad=0.003, scale=(1, sy))
            p.box((r * 0.8, 0.008, h * J(p, 0.5, 0.2)), M(loc=(-r * 0.2, -rad_at(outer, h * 0.5) * sy - 0.004, h * 0.45), rot=(0, J(p, 5, 1), 0)), mat="paint", bevel=0)
        elif slot == "lid":
            p.ring(r * 1.01, J(p, 0.012, 0.2), M(loc=(0, 0, h), scale=(1, sy, 1)), mat="rubber", segs=9, square=False)
        elif slot == "handle":
            rise = J(p, h * 0.85, 0.15)
            pts = [(-r, 0, h), (-r * 0.6, J(p, 0.01, 1), h + rise * 0.8), (r * 0.3, 0, h + rise), (r, 0, h)]
            p.tube(pts, 0.005, mat="iron", segs=4)
            p.cyl(0.016, 0.016, 0.07, M(loc=(-0.06, 0, h + rise * 0.95), rot=(0, 90, 0)), mat="cloth", segs=5, noise=0.05)
        else:
            p.band(rad_at(outer, h * 0.5), h * J(p, 0.55, 0.15), m=oval, h=0.05)
    else:  # Ancient: stone lattice basket, rune courses
        if slot == "body":
            shell(p, outer, 0.016, mat="stone", segs=10, m=oval)
            ribs(p, outer, 8, "stone_dark", rad=0.008, scale=(1, sy), phase=math.pi / 8)
        elif slot == "lid":
            p.ring(r * 1.0, J(p, 0.014, 0.15), M(loc=(0, 0, h), scale=(1, sy, 1)), mat="stone_dark", segs=10, square=False)
        elif slot == "handle":
            bail(p, r * 0.95, h, J(p, h * 0.85, 0.1), 0.014, mat="stone", segs=6, n=6)
        else:
            p.band(rad_at(outer, h * 0.5), h * J(p, 0.5, 0.12), m=oval, h=0.06)


# ---------------------------------------------------------------- Pot
@function("Pot", "Vessel", VESSEL, "scene")
def pot(p, slot):
    e = p.era
    h, r = F(p, 0.2, 0.12), F(p, 0.17, 0.1)
    if e == "Primal":  # stone boiling pit: hollow stone basin, hot stones, wooden tongs, stone ring
        R = r * 1.35
        outer = [(R * 0.8, 0), (R, h * 0.3), (R * 0.95, h * 0.6)]
        if slot == "body":
            shell(p, outer, 0.04, mat="stone", segs=9, floor=h * 0.2, noise=0.05)
        elif slot == "lid":
            for i in range(p.rng.randint(3, 5)):
                a = p.rng.uniform(0, math.tau)
                d = p.rng.uniform(0, R * 0.45)
                p.ball(J(p, 0.04, 0.3), M(loc=(math.cos(a) * d, math.sin(a) * d, h * 0.28), scale=(1, 0.9, 0.7)), mat="stone_dark", segs=(6, 4), noise=0.06)
        elif slot == "handle":
            lean = J(p, 0.0, 1) + 0.02
            for s in (-0.02, 0.02):
                p.tube([(R * 0.3, s, h * 0.3), (R * 0.95, s * 2, h * 0.65), (R * 1.5 + lean, s * 3, h * 0.2)], 0.008, mat="wood", segs=4)
        else:
            n = p.rng.randint(7, 9)
            for i in range(n):
                a = i * math.tau / n + p.rng.uniform(-0.1, 0.1)
                p.ball(J(p, 0.055, 0.25), M(loc=(math.cos(a) * R * 1.05, math.sin(a) * R * 1.05, 0.03), scale=(1.2, 1, 0.75)), mat="stone", segs=(6, 4), noise=0.07)
    elif e == "Agrarian":  # round-bottomed clay cauldron with a brim, wooden lid
        outer = [(r * 0.45, 0.004), (r * 1.0, h * 0.45), (r * 0.85, h * 0.85), (r * 0.76, h)]
        if slot == "body":
            shell(p, outer, 0.012, mat="ceramic", segs=12)
        elif slot == "lid":
            p.cyl(r * 0.85, r * 0.85, J(p, 0.02, 0.2), T(0, 0, h), mat="wood", segs=12)
            p.cyl(0.03, 0.022, 0.025, T(0, 0, h + 0.015), mat="wood", segs=8)
        elif slot == "handle":
            lz = h * J(p, 0.82, 0.04)
            for s in (-1, 1):
                p.box((0.04, 0.05, 0.03), T(s * (rad_at(outer, lz) + 0.012), 0, lz), mat="ceramic", bevel=0.3)
        else:
            bz = h * J(p, 0.5, 0.08)
            p.ring(rad_at(outer, bz) + 0.025, 0.028, M(loc=(0, 0, bz), scale=(1, 1, 0.3)), mat="ceramic", segs=12)
    elif e == "Mercantile":  # straight copper pot, domed lid, riveted loop handles
        outer = [(r * 0.95, 0), (r, 0.015), (r, h)]
        if slot == "body":
            shell(p, outer, 0.006, mat="copper", segs=14)
        elif slot == "lid":
            p.lathe([(r * 1.02, h), (r * 0.9, h + h * J(p, 0.1, 0.25)), (0.02, h + h * 0.16), (0.03, h + h * 0.24), (0, h + h * 0.26)], mat="copper", segs=14)
        elif slot == "handle":
            lz = h * 0.78
            for s in (-1, 1):
                p.tube([(s * r, -0.035, lz), (s * (r + J(p, 0.04, 0.2)), -0.03, lz + 0.03), (s * (r + 0.045), 0.03, lz + 0.03), (s * r, 0.035, lz)], 0.006, mat="brass", segs=5)
        else:
            p.band(r, h * J(p, 0.85, 0.04), h=0.04)
    elif e == "Industrial":  # cast-iron dutch oven on stub legs, wire bail
        outer = [(r * 0.9, 0.03), (r, 0.05), (r, h)]
        if slot == "body":
            shell(p, outer, 0.01, mat="iron", segs=12)
            for i in range(3):
                a = i * math.tau / 3 + math.pi / 2
                p.cyl(0.016, 0.012, 0.035, T(math.cos(a) * r * 0.65, math.sin(a) * r * 0.65, 0), mat="iron", segs=6)
        elif slot == "lid":
            p.cyl(r * 1.02, r * 1.0, 0.018, T(0, 0, h), mat="iron", segs=12)
            p.ring(r * 0.93, 0.008, T(0, 0, h + 0.02), mat="iron", segs=12)
            p.ring(J(p, 0.03, 0.15), 0.006, M(loc=(0, 0, h + 0.05), rot=(90, 0, 0)), mat="iron", segs=8, square=False)
        elif slot == "handle":
            lz = h * 0.85
            for s in (-1, 1):
                p.box((0.02, 0.04, 0.035), T(s * (r + 0.008), 0, lz), mat="iron", bevel=0.2)
            bail(p, r + 0.016, lz, J(p, r * 1.1, 0.15), 0.004, mat="steel", segs=4)
        else:
            p.ring(r * 1.01, 0.008, T(0, 0, h * J(p, 0.62, 0.1)), mat="iron", segs=12)
    elif e == "Steampunk":  # pressure cooker: clamped lid, valve weight, gauge, long handle
        outer = [(r * 0.95, 0), (r, 0.015), (r, h)]
        if slot == "body":
            shell(p, outer, 0.008, mat="steel", segs=14)
        elif slot == "lid":
            p.lathe([(r * 1.03, h - 0.005), (r * 1.03, h + 0.015), (r * 0.8, h + h * 0.14), (0.025, h + h * 0.2), (0, h + h * 0.2)], mat="brass", segs=14)
            p.cyl(0.012, 0.012, 0.05, T(0, 0, h + h * 0.2), mat="brass", segs=6)
            p.cyl(0.024, 0.02, J(p, 0.03, 0.25), T(0, 0, h + h * 0.2 + 0.045), mat="iron", segs=8)
            gz = h + h * 0.12
            p.cyl(0.022, 0.022, 0.01, M(loc=(r * 0.45, -r * 0.45, gz), rot=(55, 0, 45)), mat="brass", segs=10)
            p.cyl(0.018, 0.018, 0.002, M(loc=(r * 0.45, -r * 0.45, gz), rot=(55, 0, 45)) @ T(0, 0, 0.01), mat="glow", segs=10, bevel=0)
        elif slot == "handle":
            L = J(p, 0.17, 0.12)
            p.box((L, 0.03, 0.028), T(r + L / 2, 0, h - 0.01), mat="wood_dark", bevel=0.2)
            p.box((0.05, 0.035, 0.025), T(-r - 0.025, 0, h - 0.01), mat="wood_dark", bevel=0.2)
        else:
            p.band(r * 1.02, h - 0.005, h=J(p, 0.04, 0.2))
    elif e == "Future":  # induction pot: rounded shell, glass dome lid, field base ring
        outer = [(r * 0.85, 0.012), (r * 0.98, 0.03), (r, h * 0.3), (r, h)]
        if slot == "body":
            shell(p, outer, 0.01, mat="body", segs=16)
        elif slot == "lid":
            p.lathe([(r * 1.0, h), (r * 0.85, h + h * J(p, 0.18, 0.2)), (r * 0.3, h + h * 0.28), (0, h + h * 0.3)], mat="glass", segs=16)
            p.cyl(0.03, 0.025, 0.02, T(0, 0, h + h * 0.29), mat="shell_dark", segs=10)
        elif slot == "handle":
            for s in (-1, 1):
                p.box((J(p, 0.06, 0.15), 0.07, 0.016), T(s * (r + 0.025), 0, h * 0.88), mat="shell_dark")
        else:
            p.cyl(r * 0.85, r * 0.85, 0.012, mat="shell_dark", segs=16)
            p.ring(r * J(p, 0.7, 0.08), 0.004, T(0, 0, 0.013), mat="glow", segs=16)
            p.box((0.03, 0.004, 0.01), T(0, -r - 0.001, h * 0.2), mat="glow", bevel=0)
    elif e == "Wasteland":  # pot cut from a gas bottle, hubcap lid, rebar handles
        outer = [(r * 0.5, 0), (r * 0.9, 0.03), (r, h * 0.2), (r, h)]
        if slot == "body":
            shell(p, outer, 0.006, mat="rust", segs=10, noise=0.01)
            p.box((r * 0.6, 0.01, h * J(p, 0.35, 0.2)), M(loc=(-r * 0.2, -r, h * 0.55), rot=(0, J(p, 6, 1), 0)), mat="paint", bevel=0)
        elif slot == "lid":
            p.lathe([(r * 1.04, h), (r * 0.9, h + 0.02), (r * 0.3, h + h * J(p, 0.12, 0.25)), (0, h + h * 0.13)], mat="steel", segs=10)
            p.cyl(0.012, 0.012, 0.03, T(0, 0, h + h * 0.12), mat="iron", segs=6)
        elif slot == "handle":
            for s in (-1, 1):
                p.tube([(s * r, -0.04, h * 0.8), (s * (r + J(p, 0.04, 0.3)), 0, h * 0.85), (s * r, 0.04, h * 0.8)], 0.006, mat="iron", segs=4)
        else:
            p.band(r, h * J(p, 0.5, 0.2), h=0.06)
    else:  # Ancient: thick stone cauldron, gem-knobbed lid, rune ring
        outer = [(r * 0.7, 0), (r * 1.02, h * 0.3), (r, h * 0.8), (r * 0.9, h)]
        if slot == "body":
            shell(p, outer, 0.025, mat="stone", segs=12)
        elif slot == "lid":
            p.lathe([(r * 0.92, h), (r * 0.75, h + h * J(p, 0.15, 0.2)), (0.03, h + h * 0.22), (0, h + h * 0.22)], mat="stone_dark", segs=12)
            p.ball(0.022, T(0, 0, h + h * 0.22 + 0.012), mat="glow", segs=(6, 4))
        elif slot == "handle":
            lz = h * J(p, 0.75, 0.05)
            lugs(p, rad_at(outer, lz) + 0.022, lz, 0.04, 0.012, "stone_dark")
        else:
            p.band(rad_at(outer, h * 0.45), h * J(p, 0.45, 0.12), h=0.07)


# ---------------------------------------------------------------- Strongbox
@function("Strongbox", "Vessel", VESSEL, "carried")
def strongbox(p, slot):
    e = p.era
    w, d = F(p, 0.3, 0.1), F(p, 0.2, 0.1)
    hb, hl = F(p, 0.13, 0.12), F(p, 0.045, 0.15)
    top = hb + hl
    if e == "Primal":  # shell-hung hide purse
        r, hh = d * 0.6, hb * 1.1
        outer = [(r * 0.6, 0), (r, hh * 0.4), (r * 0.85, hh * 0.85), (r * 0.4, hh)]
        if slot == "body":
            closed(p, outer, mat="hide", segs=10, noise=0.03)
        elif slot == "lid":
            p.lathe([(r * 0.4, hh), (r * 0.25, hh + 0.02), (r * J(p, 0.55, 0.2), hh + hl), (0, hh + hl * 0.9)], mat="hide", segs=8, noise=0.04)
            p.ring(r * 0.27, 0.008, T(0, 0, hh + 0.02), mat="rope", segs=8, square=False)
        elif slot == "handle":
            bail(p, r * 0.25, hh + 0.02, J(p, hh * 0.6, 0.2), 0.004, mat="rope", n=6, m=M(rot=(0, 0, 30)))
        else:
            n = p.rng.randint(5, 7)
            zz = hh * 0.55
            for i in range(n):
                a = -math.pi / 2 + (i - (n - 1) / 2) * 0.32
                rr = rad_at(outer, zz) * 1.04
                p.ball(J(p, 0.016, 0.2), M(loc=(math.cos(a) * rr, math.sin(a) * rr, zz - abs(i - (n - 1) / 2) * 0.008), rot=(0, 0, math.degrees(a)), scale=(0.4, 1, 1)), mat="bone", segs=(5, 3))
            p.ring(rad_at(outer, zz) * 1.02, 0.003, T(0, 0, zz + 0.012), mat="rope", segs=10, square=False)
    elif e == "Agrarian":  # wooden cash box with coin slot and iron hasp
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="wood")
            p.box((w * 0.9, 0.006, J(p, 0.012, 0.3)), T(0, -d / 2, hb * 0.25), mat="wood_dark", bevel=0)
        elif slot == "lid":
            p.box((w * 1.03, d * 1.03, hl), T(0, 0, hb + hl / 2), mat="wood")
            p.box((J(p, 0.05, 0.2), 0.008, 0.004), T(0, 0, top + 0.001), mat="iron", bevel=0)
        elif slot == "handle":
            hz = top * J(p, 0.7, 0.08)
            for s in (-1, 1):
                p.ring(0.022, 0.004, M(loc=(s * (w / 2 + 0.006), 0, hz), rot=(0, 90, 0)), mat="iron", segs=8, square=False)
        else:
            for s in (-1, 1):
                p.box((0.012, d * 1.04, top * 0.98), T(s * w * J(p, 0.33, 0.1), 0, top / 2), mat="iron", bevel=0)
            p.box((0.03, 0.01, hl * 1.6), T(0, -d / 2 - 0.008, hb), mat="iron", bevel=0)
            p.ring(0.012, 0.003, M(loc=(0, -d / 2 - 0.014, hb - hl * 0.8), rot=(90, 0, 0)), mat="iron", segs=8, square=False)
    elif e == "Mercantile":  # iron-clad strongbox with brass lock plate and drop handles
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="wood_dark")
        elif slot == "lid":
            p.lathe([(d * 0.52, 0), (d * 0.52, w * 1.02)], M(loc=(-w * 0.51, 0, hb), rot=(0, 90, 0), scale=(J(p, hl / (d * 0.52), 0.1), 1, 1)), mat="wood_dark", segs=8)
        elif slot == "handle":
            hz = hb * J(p, 0.7, 0.08)
            for s in (-1, 1):
                p.box((0.01, 0.03, 0.02), T(s * (w / 2 + 0.005), 0, hz + 0.01), mat="iron", bevel=0)
                p.tube([(s * (w / 2 + 0.01), -0.035, hz), (s * (w / 2 + 0.018), 0, hz - 0.03), (s * (w / 2 + 0.01), 0.035, hz)], 0.004, mat="iron", segs=4)
        else:
            for x in (-w * 0.5, w * 0.5):
                p.box((0.025, d * 1.03, hb * 1.01), T(x * J(p, 0.94, 0.02), 0, hb / 2), mat="iron", bevel=0)
            p.plate([(-0.03, 0), (0.03, 0), (0.03, -0.04), (0, -0.055), (-0.03, -0.04)], 0.006, T(0, -d / 2 - 0.003, hb + 0.012), mat="brass")
            p.box((0.006, 0.004, 0.014), T(0, -d / 2 - 0.007, hb - 0.022), mat="rubber", bevel=0)
    elif e == "Industrial":  # small safe: steel cube on feet, door, dial, wheel handle
        if slot == "body":
            p.box((w, d, top - 0.02), T(0, 0, 0.02 + (top - 0.02) / 2), mat="steel")
            for x in (-w * 0.4, w * 0.4):
                for y in (-d * 0.35, d * 0.35):
                    p.cyl(0.012, 0.014, 0.02, T(x, y, 0), mat="rubber", segs=6)
        elif slot == "lid":
            p.box((w * 0.84, 0.012, (top - 0.02) * J(p, 0.82, 0.05)), T(-w * 0.02, -d / 2 - 0.005, 0.02 + (top - 0.02) / 2), mat="paint", bevel=0.1)
        elif slot == "handle":
            hz = 0.02 + (top - 0.02) * 0.45
            p.cyl(0.007, 0.007, 0.02, M(loc=(w * 0.18, -d / 2 - 0.01, hz), rot=(90, 0, 0)), mat="steel", segs=6)
            for i in range(3):
                a = i * 120 + J(p, 15, 1)
                p.box((0.004, 0.006, 0.05), M(loc=(w * 0.18, -d / 2 - 0.03, hz), rot=(0, a, 0)) @ T(0, 0, 0.022), mat="steel", bevel=0)
        else:
            dz = 0.02 + (top - 0.02) * 0.62
            p.cyl(0.026, 0.026, 0.012, M(loc=(-w * 0.12, -d / 2 - 0.01, dz), rot=(90, 0, 0)), mat="steel", segs=12)
            p.cyl(0.018, 0.018, 0.004, M(loc=(-w * 0.12, -d / 2 - 0.022, dz), rot=(90, 0, 0)), mat="bone", segs=12, bevel=0)
            for z in (0.3, 0.75):
                p.cyl(0.007, 0.007, J(p, 0.03, 0.2), T(w * 0.4, -d / 2 - 0.008, 0.02 + (top - 0.02) * z - 0.015), mat="steel", segs=6)
    elif e == "Steampunk":  # brass combination box: tumbler wheels and an amber tell-tale
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="brass")
            p.box((w * 1.02, d * 1.02, 0.015), T(0, 0, J(p, 0.012, 0.3)), mat="wood_dark", bevel=0.05)
        elif slot == "lid":
            p.lathe([(d * 0.5, 0), (d * 0.5, w)], M(loc=(-w * 0.5, 0, hb), rot=(0, 90, 0), scale=(J(p, hl / (d * 0.5), 0.1), 1, 1)), mat="copper", segs=10)
        elif slot == "handle":
            ht = top + J(p, 0.04, 0.2)
            p.tube([(-w * 0.2, 0, top - 0.005), (-w * 0.2, 0, ht), (w * 0.2, 0, ht), (w * 0.2, 0, top - 0.005)], 0.007, mat="brass", segs=5)
        else:
            for i in range(3):
                p.cyl(0.018, 0.018, 0.016, M(loc=(-0.04 + i * 0.04, -d / 2 - 0.004, hb * 0.55), rot=(0, 90, 0)), mat="bone", segs=8)
            p.box((0.14, 0.008, 0.05), T(0, -d / 2 - 0.002, hb * 0.55), mat="copper", bevel=0.1)
            p.ball(0.008, T(w * 0.35, -d / 2 - 0.004, hb * J(p, 0.55, 0.15)), mat="glow", segs=(5, 3))
    elif e == "Future":  # bio-lock case: rounded shell, palm scanner, light seam
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="body")
        elif slot == "lid":
            p.box((w, d, hl), T(0, 0, hb + hl / 2), mat="shell_dark")
        elif slot == "handle":
            p.box((J(p, w * 0.4, 0.12), 0.02, 0.016), T(0, d * 0.3, top + 0.006), mat="shell_dark")
        else:
            p.box((0.07, 0.004, 0.05), T(0, -d / 2 - 0.001, hb * 0.5), mat="glow", bevel=0)
            p.box((w * 1.004, d * 1.004, 0.004), T(0, 0, hb * J(p, 1.0, 0.03)), mat="glow", bevel=0)
    elif e == "Wasteland":  # ammo can lockbox: clamp lever, chain, padlock
        if slot == "body":
            p.box((w * 0.85, d * 0.7, hb), T(0, 0, hb / 2), mat="paint")
            p.box((w * 0.3, 0.008, hb * J(p, 0.4, 0.3)), M(loc=(w * 0.2, -d * 0.35 - 0.003, hb * 0.5), rot=(0, 5, 0)), mat="rust", bevel=0)
        elif slot == "lid":
            p.box((w * 0.88, d * 0.74, hl), T(0, 0, hb + hl / 2), mat="paint")
            p.box((0.03, 0.04, 0.012), M(loc=(-w * 0.44, 0, hb + hl * 0.5), rot=(0, J(p, 20, 0.5), 0)), mat="iron", bevel=0)
        elif slot == "handle":
            p.tube([(-w * 0.15, 0, top), (-w * 0.12, 0, top + J(p, 0.03, 0.3)), (w * 0.12, 0, top + 0.03), (w * 0.15, 0, top)], 0.006, mat="iron", segs=4)
        else:
            p.box((0.03, 0.012, 0.035), T(w * 0.1, -d * 0.37 - 0.01, hb - 0.03), mat="steel")
            p.ring(0.011, 0.003, M(loc=(w * 0.1, -d * 0.37 - 0.01, hb - 0.004), rot=(90, 0, 0)), mat="steel", segs=8, square=False)
            for i in range(p.rng.randint(3, 5)):
                p.ring(0.012, 0.003, M(loc=(w * 0.1 + 0.02 + i * 0.018, -d * 0.37 - 0.012, hb - 0.012 - i * 0.012), rot=(90 * (i % 2), 0, 30)), mat="iron", segs=6)
    else:  # Ancient: stone casket with rune seal
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="stone")
        elif slot == "lid":
            p.box((w * 1.04, d * 1.04, hl), T(0, 0, hb + hl / 2), mat="stone_dark")
        elif slot == "handle":
            p.ring(J(p, 0.03, 0.15), 0.009, M(loc=(0, 0, top + 0.022), rot=(90, 0, 0)), mat="gold", segs=8)
        else:
            p.box((0.05, 0.006, 0.05), M(loc=(0, -d / 2 - 0.002, hb * 0.55), rot=(0, 45, 0)), mat="gold", bevel=0)
            p.box((0.026, 0.006, 0.026), M(loc=(0, -d / 2 - 0.005, hb * 0.55), rot=(0, 45, 0)), mat="glow", bevel=0)
            for s in (-1, 1):
                p.box((w * J(p, 0.25, 0.15), 0.004, 0.008), T(s * w * 0.3, -d / 2 - 0.001, hb * 0.55), mat="glow", bevel=0)


# ---------------------------------------------------------------- MedKit
@function("MedKit", "Vessel", VESSEL, "carried")
def medkit(p, slot):
    e = p.era
    w, d = F(p, 0.28, 0.1), F(p, 0.14, 0.1)
    hb, hl = F(p, 0.17, 0.1), F(p, 0.05, 0.15)
    top = hb + hl
    if e == "Primal":  # herb pouch with leaves sprouting from the neck
        r = d * 0.75
        outer = [(r * 0.55, 0), (r, hb * 0.4), (r * 0.8, hb * 0.85), (r * 0.45, hb)]
        if slot == "body":
            closed(p, outer, mat="hide", segs=9, noise=0.03)
        elif slot == "lid":
            for i in range(p.rng.randint(3, 5)):
                a = p.rng.uniform(0, math.tau)
                tip = (math.cos(a) * r * 0.6, math.sin(a) * r * 0.6, hb + J(p, 0.09, 0.3))
                p.plate([(-0.012, 0), (0.012, 0), (0.004, 0.08), (-0.004, 0.08)], 0.004, M(loc=(math.cos(a) * r * 0.2, math.sin(a) * r * 0.2, hb - 0.02), rot=(math.degrees(math.atan2(tip[1], 0.08)) * 0.4, -math.degrees(math.atan2(tip[0], 0.08)) * 0.4, math.degrees(a) + 90)), mat="cloth", bevel=0)
        elif slot == "handle":
            bail(p, r * 0.5, hb * 0.9, J(p, 0.09, 0.25), 0.004, mat="rope", segs=4, m=M(rot=(J(p, 15, 0.5), 0, 20)))
        else:
            p.ring(r * 0.5, 0.007, T(0, 0, hb * 0.9), mat="rope", segs=8, square=False)
            p.cyl(0.006, 0.006, J(p, 0.05, 0.2), M(loc=(-0.025, -r * 0.5, hb * 0.88), rot=(0, 90, 0)), mat="bone", segs=5)
    elif e == "Agrarian":  # small woven herb basket with conical lid and a gourd
        r = d * 0.85
        outer = [(r * 0.85, 0), (r, hb)]
        if slot == "body":
            shell(p, outer, 0.008, mat="bark", segs=10)
        elif slot == "lid":
            p.lathe([(r * 1.06, hb - 0.01), (r * 1.06, hb + 0.01), (r * 0.3, hb + hl * J(p, 1.0, 0.15)), (0, hb + hl * 1.05)], mat="bark", segs=10)
        elif slot == "handle":
            bail(p, r * 0.98, hb * 0.8, J(p, hb * 0.9, 0.15), 0.006, mat="rope", segs=4, m=M(rot=(0, 0, 90)))
        else:
            weave(p, outer, [hb * 0.3, hb * J(p, 0.65, 0.1)], "rope", t=0.005, segs=10)
            p.ball(0.03, M(loc=(r * 1.15, 0, hb * 0.35), scale=(1, 1, 1.2)), mat="ceramic", segs=(6, 4))
            p.ball(0.02, T(r * 1.15, 0, hb * 0.35 + 0.045), mat="ceramic", segs=(5, 3))
    elif e == "Mercantile":  # apothecary chest: drawers, brass pulls, top handle
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="wood_dark")
        elif slot == "lid":
            p.box((w * 1.04, d * 1.06, hl), T(0, 0, hb + hl / 2), mat="wood")
        elif slot == "handle":
            ht = top + J(p, 0.035, 0.2)
            p.tube([(-w * 0.18, 0, top), (-w * 0.16, 0, ht), (w * 0.16, 0, ht), (w * 0.18, 0, top)], 0.006, mat="brass", segs=5)
        else:
            rows = 2
            for i in range(rows):
                for s in (-1, 1):
                    z = hb * (0.28 + i * 0.46)
                    p.box((w * 0.44, 0.008, hb * 0.4), T(s * w * 0.24, -d / 2 - 0.003, z), mat="wood", bevel=0)
                    p.ball(J(p, 0.008, 0.2), T(s * w * 0.24, -d / 2 - 0.01, z), mat="brass", segs=(5, 3))
    elif e == "Industrial":  # steel first-aid case with green cross panel and latches
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="steel")
        elif slot == "lid":
            p.box((w * 1.01, d * 1.01, hl), T(0, 0, hb + hl / 2), mat="steel")
            p.box((w * 1.012, d * 1.012, J(p, 0.006, 0.3)), T(0, 0, hb), mat="rubber", bevel=0)
        elif slot == "handle":
            p.tube([(-w * 0.15, 0, top), (-w * 0.13, 0, top + J(p, 0.03, 0.2)), (w * 0.13, 0, top + 0.03), (w * 0.15, 0, top)], 0.008, mat="rubber", segs=5)
        else:
            p.box((0.08, 0.004, 0.08), T(0, -d / 2 - 0.001, hb * 0.55), mat="paint", bevel=0)
            p.box((0.05, 0.004, 0.014), T(0, -d / 2 - 0.003, hb * 0.55), mat="shell", bevel=0)
            p.box((0.014, 0.004, 0.05), T(0, -d / 2 - 0.003, hb * 0.55), mat="shell", bevel=0)
            for s in (-1, 1):
                p.box((0.02, 0.008, J(p, 0.03, 0.2)), T(s * w * 0.36, -d / 2 - 0.004, hb), mat="steel", bevel=0)
    elif e == "Steampunk":  # brass medical case with a rack of glowing vials
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="brass")
        elif slot == "lid":
            p.box((w * 1.02, d * 1.02, hl), T(0, 0, hb + hl / 2), mat="wood_dark")
            p.box((w * 0.5, d * 0.6, 0.004), T(0, 0, top + 0.001), mat="glass", bevel=0)
        elif slot == "handle":
            ht = top + J(p, 0.035, 0.2)
            p.tube([(-w * 0.16, 0, top), (-w * 0.16, 0, ht), (w * 0.16, 0, ht), (w * 0.16, 0, top)], 0.006, mat="copper", segs=5)
        else:
            for i in range(3):
                x = -w * 0.25 + i * w * 0.25
                p.cyl(0.014, 0.014, hb * 0.6, T(x, -d / 2 - 0.012, hb * 0.18), mat="glass", segs=6)
                p.cyl(0.011, 0.011, hb * J(p, 0.35, 0.3), T(x, -d / 2 - 0.012, hb * 0.19), mat="glow", segs=6)
            p.box((w * 0.85, 0.01, 0.012), T(0, -d / 2 - 0.006, hb * 0.5), mat="copper", bevel=0)
    elif e == "Future":  # auto-diagnoser: sloped shell, screen, docked scanner wand
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="body")
        elif slot == "lid":
            p.plate([(-w / 2, 0), (w / 2, 0), (w / 2, hl), (-w / 2, hl * 0.35)], d, T(0, 0, hb), mat="shell_dark")
            p.screen(w * 0.5, hl * 0.4, M(loc=(w * 0.05, -d / 2 - 0.002, hb + hl * 0.35)))
        elif slot == "handle":
            hz = hb * J(p, 0.55, 0.12)
            p.cyl(0.016, 0.014, hb * 0.85, T(w / 2 + 0.016, -d * 0.15, hb * 0.1), mat="shell_dark", segs=8)
            p.ring(0.022, 0.004, T(w / 2 + 0.016, -d * 0.15, hb * 0.95), mat="glow", segs=8)
            p.box((0.01, 0.03, 0.04), T(w / 2 + 0.004, -d * 0.15, hz), mat="shell_dark", bevel=0)
        else:
            p.box((w * 1.004, d * 1.004, 0.005), T(0, 0, hb * J(p, 0.25, 0.2)), mat="glow", bevel=0)
            for i in range(3):
                p.box((0.008, 0.004, 0.008), T(-w * 0.38 + i * 0.016, -d / 2 - 0.001, hb * 0.6), mat="glow", bevel=0)
    elif e == "Wasteland":  # toolbox turned med-box: taped cross, strapped syringes
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="rust")
            p.box((w * 0.35, 0.008, hb * J(p, 0.4, 0.3)), M(loc=(-w * 0.2, -d / 2 - 0.003, hb * 0.45), rot=(0, -6, 0)), mat="iron", bevel=0)
        elif slot == "lid":
            p.box((w * 1.02, d * 1.04, hl), T(0, 0, hb + hl / 2), mat="paint")
            p.box((w * 0.3, 0.004, 0.012), M(loc=(w * 0.1, -d * 0.52 - 0.002, hb + hl * 0.5), rot=(0, J(p, 4, 1), 0)), mat="cloth", bevel=0)
        elif slot == "handle":
            p.tube([(-w * 0.2, 0, top), (-w * 0.18, J(p, 0.01, 1), top + 0.04), (w * 0.18, 0, top + 0.04), (w * 0.2, 0, top)], 0.005, mat="iron", segs=4)
        else:
            p.box((0.07, 0.004, 0.02), M(loc=(w * 0.15, -d / 2 - 0.002, hb * 0.55), rot=(0, 8, 0)), mat="cloth", bevel=0)
            p.box((0.02, 0.004, 0.07), M(loc=(w * 0.15, -d / 2 - 0.003, hb * 0.55), rot=(0, 8, 0)), mat="cloth", bevel=0)
            for i in range(p.rng.randint(1, 3)):
                p.cyl(0.008, 0.008, 0.08, M(loc=(w / 2 + 0.01, -d * 0.2 + i * 0.022, hb * 0.2), rot=(0, 0, 0)), mat="glass", segs=5)
            p.box((0.012, d * 1.06, 0.02), T(w / 2 + 0.004, 0, hb * 0.5), mat="cloth", bevel=0)
    else:  # Ancient: stone reliquary with glowing vial slots
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="stone")
        elif slot == "lid":
            p.box((w * 1.03, d * 1.05, hl), T(0, 0, hb + hl / 2), mat="stone_dark")
        elif slot == "handle":
            p.ring(J(p, 0.03, 0.15), 0.009, M(loc=(0, 0, top + 0.022), rot=(90, 0, 0)), mat="stone_dark", segs=8)
        else:
            for i in range(3):
                p.box((0.014, 0.006, hb * J(p, 0.55, 0.12)), T(-w * 0.22 + i * w * 0.22, -d / 2 - 0.002, hb * 0.5), mat="glow", bevel=0)
            p.box((w * 0.8, 0.006, 0.01), T(0, -d / 2 - 0.002, hb * 0.12), mat="gold", bevel=0)


# ---------------------------------------------------------------- Mortar
@function("Mortar", "Vessel", VESSEL, "carried")
def mortar(p, slot):
    e = p.era
    h, r = F(p, 0.11, 0.12), F(p, 0.1, 0.1)
    if e == "Primal":  # hollowed stone, crushed seeds, pebble pestle, wedge stones
        R = r * 1.3
        outer = [(R * 0.8, 0.012), (R, h * 0.4), (R * 0.9, h * 0.7)]
        if slot == "body":
            shell(p, outer, 0.035, mat="stone", segs=9, floor=h * 0.35, noise=0.06)
        elif slot == "lid":
            p.ball(R * 0.5, M(loc=(0, 0, h * 0.38), scale=(1, 0.9, J(p, 0.18, 0.3))), mat="hide", segs=(7, 3), noise=0.08)
        elif slot == "handle":
            p.ball(J(p, 0.03, 0.15), M(loc=(R * 0.3, 0, h * 0.62), rot=(0, 60, 20), scale=(1, 1, 2.4)), mat="stone_dark", segs=(6, 4), noise=0.05)
        else:
            for i in range(3):
                a = i * math.tau / 3 + J(p, 0.3, 0.5)
                p.ball(0.022, M(loc=(math.cos(a) * R * 0.85, math.sin(a) * R * 0.85, 0.012), scale=(1.3, 1, 0.6)), mat="stone_dark", segs=(5, 3), noise=0.08)
    elif e == "Agrarian":  # stone mortar with foot and wooden pestle
        outer = [(r * 0.75, 0), (r * 0.8, h * 0.15), (r * 0.95, h * 0.35), (r, h)]
        if slot == "body":
            shell(p, outer, 0.025, mat="stone", segs=10, floor=h * 0.45)
        elif slot == "lid":
            p.ring(r * 0.99, J(p, 0.01, 0.2), T(0, 0, h), mat="stone_dark", segs=10, square=False)
        elif slot == "handle":
            L = J(p, 0.24, 0.1)
            p.lathe([(0, 0), (0.022, 0.01), (0.022, 0.05), (0.014, 0.08), (0.017, L - 0.025), (0.012, L - 0.004), (0, L)], M(loc=(0, 0, h * 0.5), rot=(J(p, 20, 0.3), 0, 25)), mat="wood", segs=7)
        else:
            p.ring(rad_at(outer, h * 0.15) * 1.02, 0.008, T(0, 0, h * J(p, 0.15, 0.2)), mat="stone_dark", segs=10)
    elif e == "Mercantile":  # flared bronze mortar with lug ears and pestle
        outer = [(r * 0.85, 0), (r * 0.85, 0.012), (r * 0.7, h * 0.2), (r * 0.82, h * 0.65), (r, h)]
        if slot == "body":
            shell(p, outer, 0.012, mat="brass", segs=12, floor=h * 0.4)
        elif slot == "lid":
            p.ring(r * 1.0, J(p, 0.008, 0.2), T(0, 0, h), mat="brass", segs=12, square=False)
        elif slot == "handle":
            L = J(p, 0.2, 0.1)
            p.lathe([(0, 0), (0.018, 0.005), (0.02, 0.03), (0.01, 0.06), (0.01, L - 0.03), (0.016, L - 0.015), (0, L)], M(loc=(0, 0, h * 0.45), rot=(J(p, 18, 0.3), 0, -30)), mat="brass", segs=8)
        else:
            bz = h * J(p, 0.62, 0.06)
            p.ring(rad_at(outer, bz) * 1.02, 0.005, T(0, 0, bz), mat="brass", segs=12, square=False)
            for s in (-1, 1):
                p.box((0.018, 0.02, 0.025), T(s * (rad_at(outer, h * 0.5) + 0.006), 0, h * 0.5), mat="brass", bevel=0)
    elif e == "Industrial":  # hand-crank grinding mill: iron body, hopper, crank, clamp foot
        if slot == "body":
            p.lathe([(0, 0.03), (r * 0.6, 0.03), (r * 0.55, h * 0.7), (r * 0.62, h), (0, h)], mat="iron", segs=10)
            p.tube([(0, -r * 0.5, h * 0.45), (0, -r * 0.85, h * 0.35), (0, -r * 0.95, h * 0.15)], 0.016, mat="iron", segs=6)
        elif slot == "lid":
            p.lathe([(r * 0.3, h), (r * J(p, 0.9, 0.1), h + h * 0.6), (r * 0.85, h + h * 0.62), (r * 0.26, h + 0.006)], mat="steel", segs=10)
        elif slot == "handle":
            L = J(p, 0.12, 0.12)
            hz = h + h * 0.75
            p.cyl(0.006, 0.006, h * 0.8, T(0, 0, h), mat="steel", segs=6)
            p.box((L, 0.012, 0.01), T(L / 2, 0, hz), mat="iron", bevel=0)
            p.cyl(0.012, 0.012, 0.05, T(L, 0, hz), mat="wood", segs=6)
        else:
            p.box((r * 1.6, r * 1.1, 0.03), T(0, 0, 0.015), mat="iron", bevel=0.1)
            p.cyl(0.006, 0.006, J(p, 0.05, 0.2), T(r * 0.6, r * 0.35, 0.03), mat="steel", segs=6)
            p.cyl(0.006, 0.006, 0.05, T(-r * 0.6, r * 0.35, 0.03), mat="steel", segs=6)
    elif e == "Steampunk":  # geared grinder: brass drum, copper hopper, exposed gear and crank
        if slot == "body":
            p.cyl(r * 0.75, r * 0.75, h, mat="brass", segs=12)
            p.tube([(0, -r * 0.6, h * 0.35), (0, -r * 1.0, h * 0.2), (0, -r * 1.05, h * 0.05)], 0.014, mat="brass", segs=6)
        elif slot == "lid":
            p.lathe([(r * 0.3, h), (r * J(p, 0.95, 0.1), h + h * 0.55), (r * 0.9, h + h * 0.58), (r * 0.26, h + 0.006)], mat="copper", segs=12)
        elif slot == "handle":
            gr = J(p, 0.05, 0.15)
            gm = M(loc=(r * 0.75 + 0.01, 0, h * 0.55), rot=(0, 90, 0))
            p.ring(gr, 0.007, gm, mat="brass", segs=12)
            for i in range(8):
                a = i * math.tau / 8
                p.box((0.012, 0.012, 0.01), gm @ T(math.cos(a) * (gr + 0.008), math.sin(a) * (gr + 0.008), 0), mat="brass", bevel=0)
            p.tube([(r * 0.75 + 0.02, 0, h * 0.55), (r * 0.75 + 0.04, 0, h * 0.55), (r * 0.75 + 0.04, 0, h * 0.55 + 0.07)], 0.005, mat="iron", segs=4)
            p.cyl(0.01, 0.01, 0.04, M(loc=(r * 0.75 + 0.04, 0, h * 0.55 + 0.07), rot=(0, 90, 0)), mat="wood_dark", segs=6)
        else:
            p.band(r * 0.75, h * J(p, 0.25, 0.2), h=0.03)
            p.ball(0.009, T(-r * 0.4, -r * 0.62, h * 0.8), mat="glow", segs=(5, 3))
    elif e == "Future":  # ultrasonic pulverizer: shell base, glass chamber, emitter ring
        bh = h * 0.45
        if slot == "body":
            p.lathe([(0, 0), (r * 0.9, 0), (r, bh * 0.4), (r * 0.85, bh), (0, bh)], mat="body", segs=14)
        elif slot == "lid":
            p.cyl(r * 0.6, r * 0.6, h * 1.0, T(0, 0, bh), mat="glass", segs=12)
            p.cyl(r * 0.64, r * 0.6, h * J(p, 0.15, 0.2), T(0, 0, bh + h), mat="shell_dark", segs=12)
        elif slot == "handle":
            p.box((0.02, 0.03, h * 0.9), T(0, r * 0.75, bh + h * 0.45), mat="shell_dark")
            p.box((0.02, J(p, 0.04, 0.2), 0.02), T(0, r * 0.62, bh + h * 0.88), mat="shell_dark", bevel=0)
        else:
            p.ring(r * 0.66, 0.006, T(0, 0, bh + 0.006), mat="glow", segs=14)
            p.box((0.03, 0.004, 0.01), T(0, -r * 0.95, bh * J(p, 0.45, 0.2)), mat="glow", bevel=0)
    elif e == "Wasteland":  # pipe-section mortar welded to a plate, bolt pestle
        if slot == "body":
            p.box((r * 2.0, r * 1.8, 0.012), M(rot=(0, 0, J(p, 8, 1))) @ T(0, 0, 0.006), mat="iron", bevel=0)
            shell(p, [(r * 0.8, 0.012), (r * 0.8, h)], 0.01, mat="rust", segs=9, floor=h * 0.3)
        elif slot == "lid":
            p.ring(r * 0.81, J(p, 0.008, 0.25), T(0, 0, h), mat="steel", segs=9)
        elif slot == "handle":
            L = J(p, 0.2, 0.12)
            m = M(loc=(0, 0, h * 0.35), rot=(J(p, 15, 0.4), 0, 40))
            p.cyl(0.012, 0.012, L, m, mat="steel", segs=6)
            p.cyl(0.022, 0.022, 0.016, m @ T(0, 0, L - 0.016), mat="steel", segs=6)
        else:
            p.band(r * 0.8, h * J(p, 0.5, 0.2), h=0.04)
    else:  # Ancient: rounded stone bowl, rune ring, glow-tipped pestle
        outer = [(r * 0.6, 0), (r * 0.95, h * 0.35), (r, h)]
        if slot == "body":
            shell(p, outer, 0.022, mat="stone", segs=10, floor=h * 0.4)
        elif slot == "lid":
            p.ring(r * 0.99, J(p, 0.012, 0.15), T(0, 0, h), mat="stone_dark", segs=10, square=False)
        elif slot == "handle":
            L = J(p, 0.18, 0.1)
            m = M(loc=(0, 0, h * 0.45), rot=(J(p, 18, 0.3), 0, 35))
            p.lathe([(0, 0), (0.018, 0.008), (0.014, L * 0.6), (0.016, L - 0.01), (0, L)], m, mat="stone", segs=6)
            p.ball(0.012, m @ T(0, 0, 0.004), mat="glow", segs=(5, 3))
        else:
            p.band(rad_at(outer, h * 0.5), h * J(p, 0.5, 0.15), h=0.04)


# ---------------------------------------------------------------- Creel
@function("Creel", "Vessel", VESSEL, "carried")
def creel(p, slot):
    e = p.era
    h, r = F(p, 0.28, 0.1), F(p, 0.13, 0.1)
    neck = r * F(p, 0.5, 0.1)
    if e == "Primal":  # grass-woven fish basket with a narrow neck
        outer = [(r * 0.7, 0), (r * 1.05, h * 0.35), (r * 0.9, h * 0.7), (neck, h * 0.9), (neck * 1.1, h)]
        if slot == "body":
            shell(p, outer, 0.008, mat="rope", segs=9, noise=0.03)
        elif slot == "lid":
            p.ring(neck * 1.15, J(p, 0.012, 0.2), T(0, 0, h), mat="rope", segs=8, square=False)
        elif slot == "handle":
            bail(p, neck * 1.05, h * 0.92, h * J(p, 0.4, 0.15), 0.005, mat="rope", segs=4, m=M(rot=(J(p, 10, 0.5), 0, 0)))
        else:
            weave(p, outer, [h * 0.2, h * J(p, 0.45, 0.1), h * 0.65], "bark", t=0.006, segs=9)
    elif e == "Agrarian":  # bamboo fish basket: bulb, narrow neck, flared mouth, waist cord
        outer = [(r * 0.8, 0), (r, h * 0.3), (r * 0.95, h * 0.6), (neck, h * 0.85), (neck * 1.4, h)]
        if slot == "body":
            shell(p, outer, 0.007, mat="wood", segs=10)
        elif slot == "lid":
            p.ring(neck * 1.4, J(p, 0.01, 0.2), T(0, 0, h), mat="wood", segs=10, square=False)
        elif slot == "handle":
            p.ring(neck * 1.05, 0.005, T(0, 0, h * 0.85), mat="rope", segs=8, square=False)
            p.tube([(neck, 0, h * 0.85), (r * 1.1, 0, h * J(p, 1.05, 0.08)), (r * 1.5, 0.02, h * 0.95)], 0.005, mat="rope", segs=4)
        else:
            weave(p, outer, [h * 0.15, h * J(p, 0.4, 0.1), h * 0.65], "bark", t=0.005, segs=8)
    elif e == "Mercantile":  # wicker creel: rounded box, lid with fish hole, leather strap
        w, d = r * 2.2, r * 1.3
        hb = h * 0.85
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="bark", bevel=0.25)
        elif slot == "lid":
            p.box((w * 1.02, d * 1.04, h - hb), T(0, 0, hb + (h - hb) / 2), mat="bark", bevel=0.2)
            p.ring(J(p, 0.03, 0.15), 0.008, M(loc=(w * 0.15, 0, h), scale=(1.4, 1, 1)), mat="grip", segs=8)
        elif slot == "handle":
            bail(p, w / 2 + 0.004, hb * 0.8, h - hb * 0.8 + J(p, 0.16, 0.2), 0.007, mat="grip", segs=4, n=9)
            for s in (-1, 1):
                p.box((0.008, 0.03, 0.03), T(s * (w / 2 + 0.002), 0, hb * 0.8), mat="brass", bevel=0)
        else:
            for x in (-w * 0.25, w * 0.25):
                p.box((0.025, d * 1.03, hb * J(p, 0.9, 0.05)), T(x, 0, hb * 0.45), mat="grip", bevel=0)
    elif e == "Industrial":  # wire mesh keep-cage with funnel mouth
        outer = [(r, 0), (r, h)]
        if slot == "body":
            p.cyl(r, r, 0.01, mat="steel", segs=10)
            ribs(p, outer, 10, "steel", rad=0.0025)
        elif slot == "lid":
            p.lathe([(r * 1.01, h), (r * 1.01, h + 0.008), (neck * J(p, 0.8, 0.15), h - h * 0.2), (neck * 0.75, h - h * 0.22)], mat="steel", segs=10)
        elif slot == "handle":
            bail(p, r * 1.01, h, J(p, r * 1.0, 0.15), 0.003, mat="steel", segs=4)
        else:
            weave(p, outer, [h * 0.25, h * J(p, 0.5, 0.1), h * 0.75], "steel", t=0.003, segs=10)
    elif e == "Steampunk":  # brass water-tank creel: porthole, hatch, pump
        outer = [(r * 0.95, 0), (r, 0.02), (r, h * 0.85), (r * 0.8, h * 0.95)]
        if slot == "body":
            closed(p, outer, mat="brass", segs=12)
        elif slot == "lid":
            p.cyl(r * 0.8, r * 0.75, J(p, 0.02, 0.2), T(0, 0, h * 0.95), mat="copper", segs=12)
            p.cyl(r * 0.45, r * 0.45, 0.004, T(0, 0, h * 0.95 + 0.02), mat="glass", segs=12, bevel=0)
        elif slot == "handle":
            p.cyl(0.012, 0.012, h * 0.35, T(r * 0.55, r * 0.3, h * 0.95), mat="iron", segs=6)
            p.box((0.07, 0.012, 0.012), T(r * 0.55 + 0.03, r * 0.3, h * 0.95 + h * J(p, 0.35, 0.15)), mat="wood_dark", bevel=0)
        else:
            p.band(r, h * 0.2, h=0.04)
            p.ring(0.035, 0.008, M(loc=(0, -r - 0.004, h * 0.55), rot=(90, 0, 0)), mat="copper", segs=10)
            p.cyl(0.032, 0.032, 0.004, M(loc=(0, -r + 0.004, h * 0.55), rot=(90, 0, 0)), mat="glow", segs=10, bevel=0)
            p.ball(0.006, T(r * 0.6, -r * 0.8, h * J(p, 0.75, 0.1)), mat="copper", segs=(4, 3))
    elif e == "Future":  # chill box: shell body, dark lid, strap, temperature light
        w, d = r * 2.3, r * 1.6
        hb = h * 0.75
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="body")
        elif slot == "lid":
            p.box((w * 1.02, d * 1.02, h - hb), T(0, 0, hb + (h - hb) / 2), mat="shell_dark")
        elif slot == "handle":
            ht = h + J(p, 0.06, 0.2)
            p.tube([(-w / 2 - 0.005, 0, hb * 0.7), (-w / 2 - 0.01, 0, ht), (w / 2 + 0.01, 0, ht), (w / 2 + 0.005, 0, hb * 0.7)], 0.008, mat="grip", segs=4)
        else:
            p.box((0.05, 0.004, 0.02), T(w * 0.25, -d / 2 - 0.001, hb * J(p, 0.75, 0.1)), mat="glow", bevel=0)
            p.box((w * 1.004, d * 1.004, 0.004), T(0, 0, hb * 0.15), mat="glow", bevel=0)
    elif e == "Wasteland":  # jerrycan cut open on top, seat-belt strap, wire lashings
        w, d = r * 2.0, r * 1.2
        hb = h * 0.9
        if slot == "body":
            p.box((w, d, hb), T(0, 0, hb / 2), mat="paint")
            p.box((w * 0.4, 0.008, hb * J(p, 0.3, 0.3)), M(loc=(-w * 0.2, -d / 2 - 0.003, hb * 0.4), rot=(0, 7, 0)), mat="rust", bevel=0)
        elif slot == "lid":
            p.box((w * 0.98, d * 0.98, 0.01), M(loc=(0, d * 0.49, hb + 0.005), rot=(J(p, 10, 0.5), 0, 0)) @ T(0, -d * 0.49, 0), mat="iron", bevel=0)
        elif slot == "handle":
            p.tube([(-w / 2, 0, hb * 0.85), (-w * 0.45, 0, h + J(p, 0.15, 0.2)), (w * 0.45, 0, h + 0.15), (w / 2, 0, hb * 0.85)], 0.008, mat="cloth", segs=4)
        else:
            p.band(w * 0.55, hb * J(p, 0.5, 0.2), m=M(scale=(1, d / w, 1)), h=0.05)
    else:  # Ancient: stone fish vessel with water-rune and stopper
        outer = [(r * 0.7, 0), (r * 1.02, h * 0.35), (r * 0.9, h * 0.75), (neck, h * 0.92), (neck * 1.05, h)]
        if slot == "body":
            shell(p, outer, 0.02, mat="stone", segs=10)
        elif slot == "lid":
            p.lathe([(neck * 0.85, h - 0.03), (neck * 1.05, h), (neck * 0.9, h + J(p, 0.03, 0.2)), (0, h + 0.035)], mat="stone_dark", segs=8)
        elif slot == "handle":
            lz = h * J(p, 0.62, 0.05)
            lugs(p, rad_at(outer, lz) + 0.018, lz, 0.03, 0.01, "stone_dark")
        else:
            p.band(rad_at(outer, h * 0.4), h * J(p, 0.4, 0.12), h=0.06)


# ---------------------------------------------------------------- Bell
@function("Bell", "Vessel", VESSEL, "carried")
def bell(p, slot):
    e = p.era
    h, r = F(p, 0.18, 0.12), F(p, 0.08, 0.1)
    if e == "Primal":  # wooden slit clapper-block on the ground, beater stick
        L = h * 1.6
        R = r * 1.1
        if slot == "body":
            p.cyl(R, R, L, M(loc=(-L / 2, 0, R), rot=(0, 90, 0)), mat="wood", segs=8, noise=0.02)
            p.box((L * 0.7, 0.012, 0.012), T(0, -R * 0.2, R * 2 - 0.004), mat="bark", bevel=0)
        elif slot == "lid":
            for s in (-1, 1):
                p.cyl(R * 1.04, R * 1.02, J(p, 0.02, 0.2), M(loc=(s * L / 2, 0, R), rot=(0, -90 * s, 0)), mat="bark", segs=8)
        elif slot == "handle":
            p.tube([(-L * 0.3, -R * 1.2, 0.012), (L * J(p, 0.3, 0.2), -R * 1.5, 0.014)], 0.01, mat="wood", segs=5)
            p.ball(0.018, T(L * 0.3, -R * 1.5, 0.018), mat="hide", segs=(5, 3))
        else:
            for s in (-1, 1):
                p.band(R, 0, m=M(loc=(s * L * J(p, 0.35, 0.1), 0, R), rot=(0, 90, 0)), h=0.025)
    elif e == "Agrarian":  # almond-section bronze bell with boss studs and loop handle
        sm = M(scale=(1, 0.75, 1))
        if slot == "body":
            outer = bell_shape(p, r, h, 0.006, mat="copper", segs=10, waist=0.72, m=sm)
            p.ball(0.012, T(0, 0, h * 0.25), mat="iron", segs=(5, 3))
        elif slot == "lid":
            p.cyl(r * 0.5, r * 0.4, J(p, 0.015, 0.2), M(loc=(0, 0, h), scale=(1, 0.75, 1)), mat="copper", segs=10)
        elif slot == "handle":
            p.cyl(0.01, 0.009, J(p, 0.05, 0.2), T(0, 0, h + 0.01), mat="iron", segs=6)
            p.ring(0.02, 0.005, M(loc=(0, 0, h + 0.075), rot=(90, 0, 0)), mat="iron", segs=8, square=False)
        else:
            for row in (0.45, J(p, 0.62, 0.06)):
                for i in range(6):
                    a = i * math.tau / 6
                    rr = r * (0.76 + (0.72 - 0.76) * (row - 0.3) / 0.32) * 1.0
                    p.ball(0.006, T(math.cos(a) * rr, math.sin(a) * rr * 0.75, h * row), mat="copper", segs=(4, 3))
    elif e == "Mercantile":  # flared hand bell with a turned wooden handle
        if slot == "body":
            bell_shape(p, r, h, 0.006, mat="brass", segs=12, waist=0.6)
            p.ball(0.012, T(0, 0, h * 0.2), mat="iron", segs=(5, 3))
        elif slot == "lid":
            p.cyl(r * 0.42, r * 0.25, J(p, 0.02, 0.2), T(0, 0, h), mat="brass", segs=10)
        elif slot == "handle":
            L = J(p, 0.12, 0.12)
            z0 = h + 0.015
            p.lathe([(0.012, z0), (0.016, z0 + L * 0.2), (0.011, z0 + L * 0.5), (0.018, z0 + L * 0.85), (0, z0 + L)], mat="wood_dark", segs=8)
        else:
            for z in (0.12, J(p, 0.55, 0.08)):
                p.ring(r * (0.97 if z < 0.2 else 0.62) * 1.02, 0.004, T(0, 0, h * z), mat="brass", segs=12, square=False)
    elif e == "Industrial":  # cast-iron bell hung in a steel frame with a pull cord
        H = h * 1.0
        zb = 0.07
        span = r * 1.5
        if slot == "body":
            bell_shape(p, r, H, 0.008, mat="iron", segs=12, waist=0.64, m=T(0, 0, zb))
            p.ball(0.014, T(0, 0, zb + 0.01), mat="iron", segs=(5, 3))
        elif slot == "lid":
            p.box((0.03, 0.04, J(p, 0.035, 0.2)), T(0, 0, zb + H + 0.012), mat="steel", bevel=0.1)
        elif slot == "handle":
            beam = zb + H + 0.035
            for s in (-1, 1):
                p.box((0.02, 0.05, beam), T(s * span, 0, beam / 2), mat="steel", bevel=0.05)
                p.box((0.06, r * J(p, 1.6, 0.1), 0.012), T(s * span, 0, 0.006), mat="steel", bevel=0)
            p.box((span * 2 + 0.02, 0.03, 0.02), T(0, 0, beam), mat="steel", bevel=0.05)
        else:
            p.ring(r * 0.99, 0.006, T(0, 0, zb + H * 0.1), mat="iron", segs=12)
            p.tube([(0, 0, zb + 0.01), (0.01, -0.01, zb - 0.02), (J(p, 0.02, 1), -0.02, 0.01)], 0.003, mat="rope", segs=4)
    elif e == "Steampunk":  # clockwork bell: dome gong on a pedestal, spring hammer, key
        zb = 0.06
        if slot == "body":
            p.box((r * 2.6, r * 2.0, 0.03), T(0, 0, 0.015), mat="wood_dark", bevel=0.1)
            p.cyl(0.01, 0.01, zb + h * 0.55, T(0, 0, 0.03), mat="brass", segs=6)
            p.lathe([(r, zb), (r * 0.98, zb + 0.01), (r * 0.8, zb + h * 0.3), (r * 0.4, zb + h * 0.5), (0, zb + h * 0.55),
                     (0, zb + h * 0.5), (r * 0.37, zb + h * 0.45), (r * 0.94, zb + 0.005)], mat="brass", segs=12)
        elif slot == "lid":
            p.cyl(0.018, 0.012, J(p, 0.02, 0.2), T(0, 0, zb + h * 0.55), mat="copper", segs=8)
            p.ball(0.01, T(0, 0, zb + h * 0.55 + 0.03), mat="glow", segs=(5, 3))
        elif slot == "handle":
            p.cyl(0.004, 0.004, h * 0.4, T(r * 1.05, 0, 0.03), mat="iron", segs=4)
            p.ball(0.014, T(r * 1.05 - 0.01, 0, 0.03 + h * J(p, 0.35, 0.1)), mat="brass", segs=(5, 3))
            p.tube([(-r * 0.8, r * 0.9, 0.035), (-r * 0.8, r * 1.0, 0.07), (-r * 0.8, r * 1.1, 0.05)], 0.004, mat="brass", segs=4)
        else:
            gm = M(loc=(-r * 0.7, -r * 1.0 - 0.003, 0.015), rot=(90, 0, 0))
            p.cyl(J(p, 0.025, 0.2), 0.025, 0.006, gm, mat="copper", segs=10)
            p.ring(r * 0.99, 0.004, T(0, 0, zb + 0.006), mat="copper", segs=12)
    elif e == "Future":  # resonance bell: hovering ring over an emitter pedestal
        if slot == "body":
            p.lathe([(0, 0), (r * 0.9, 0), (r * 0.8, h * 0.12), (r * 0.35, h * 0.2), (0, h * 0.2)], mat="body", segs=14)
            p.ring(r * 0.75, 0.012, M(loc=(0, 0, h * 0.62), rot=(90, 0, 0), scale=(1, 1.35, 1)), mat="body", segs=14)
        elif slot == "lid":
            p.ball(J(p, 0.016, 0.2), T(0, 0, h * 0.62), mat="glow", segs=(6, 4))
        elif slot == "handle":
            p.cyl(0.012, 0.012, h * 0.2, T(0, r * 0.6, h * 0.1), mat="shell_dark", segs=8)
            p.box((0.02, 0.012, J(p, 0.03, 0.2)), T(0, r * 0.6, h * 0.32), mat="shell_dark", bevel=0)
        else:
            p.ring(r * 0.45, 0.004, T(0, 0, h * 0.21), mat="glow", segs=12)
            p.ring(r * 0.7, 0.003, M(loc=(0, 0, h * 0.62), rot=(90, J(p, 30, 0.3), 0), scale=(1, 1.35, 1)), mat="glow", segs=14)
    elif e == "Wasteland":  # bell cut from a gas bottle, hung on a pipe gallows with a bolt clapper
        zb = 0.06
        H = h * 0.9
        if slot == "body":
            p.lathe([(r - 0.006, zb), (r, zb), (r, zb + H * 0.6), (r * 0.6, zb + H * 0.92), (0, zb + H), (0, zb + H - 0.008),
                     (r * 0.6 - 0.006, zb + H * 0.9), (r - 0.006, zb + H * 0.58)], mat="rust", segs=9, noise=0.01)
        elif slot == "lid":
            p.ring(0.012, 0.003, M(loc=(0, 0, zb + H + 0.012), rot=(90, 0, 0)), mat="iron", segs=6)
            p.ring(0.012, 0.003, M(loc=(0, 0, zb + H + 0.032), rot=(90, 0, 90)), mat="iron", segs=6)
            p.cyl(0.006, 0.006, J(p, 0.08, 0.2), T(0, 0, zb - 0.04), mat="steel", segs=6)
        elif slot == "handle":
            top = zb + H + 0.045
            x = r * J(p, 1.5, 0.1)
            p.tube([(x, 0, 0), (x, 0, top), (0, 0, top)], 0.008, mat="iron", segs=5)
            p.box((0.08, 0.08, 0.012), T(x, 0, 0.006), mat="rust", bevel=0)
        else:
            p.band(r, zb + H * J(p, 0.3, 0.2), h=0.04)
    else:  # Ancient: thick stone bell, rune ring, glowing crown gem, stone loop
        if slot == "body":
            bell_shape(p, r, h, 0.012, mat="stone", segs=10, waist=0.66)
        elif slot == "lid":
            p.cyl(r * 0.46, r * 0.3, J(p, 0.018, 0.2), T(0, 0, h), mat="stone_dark", segs=8)
            p.ball(0.01, T(0, -r * 0.3, h + 0.01), mat="glow", segs=(5, 3))
        elif slot == "handle":
            p.ring(J(p, 0.024, 0.15), 0.008, M(loc=(0, 0, h + 0.04), rot=(90, 0, 0)), mat="stone_dark", segs=8)
        else:
            p.band(r * 0.78, h * J(p, 0.32, 0.12), h=0.05)
