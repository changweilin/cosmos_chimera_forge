"""Furniture family forms (cosmos_chimera everyday-objects-catalog.md: 家具 + Altar).

Slots follow the family order 面/座、腳、背/框、飾: top (surface, seat, sign face), legs (legs, base, wheels, post),
frame (apron, back, uprights, canopy, bracket), trim (fittings, goods, offerings, glow). Every form draws its frame
factors first and in the same order for every slot, so legs end exactly at the underside of the top, canopies stand
on the counter and signs hang from their brackets. Floor contact at z = 0, front faces -Y, metres.
The top surface height is never jittered per variant: later props are set on it.
"""
import math

from mathutils import Matrix

from kit_forms import F, J, coin, function
from kit_lib import M

FURN = ("top", "legs", "frame", "trim")
T = Matrix.Translation


# ---------------------------------------------------------------- helpers
def slab(p, w, d, t, z, x=0.0, y=0.0, mat="body", **kw):
    """Box with its bottom face at z."""
    p.box((w, d, t), T((x, y, z + t / 2)), mat=mat, **kw)


def post(p, x, y, z0, z1, s, mat="body", **kw):
    """Square post of half-width s from z0 to z1."""
    p.box((s * 2, s * 2, z1 - z0), T((x, y, (z0 + z1) / 2)), mat=mat, **kw)


def pole(p, a, b, r, mat="body", segs=6):
    p.tube([a, b], r, mat=mat, segs=segs)


def flagstone(p, w, d, t, z, mat="stone", n=8, rough=0.1, x=0.0, y=0.0, rz=0.0, noise=None):
    """Irregular flat slab (outline in XY) with its bottom at z; the outline stays within w x d."""
    pts = []
    for i in range(n):
        a = i * math.tau / n + math.pi / n + p.rng.uniform(-0.12, 0.12)
        k = 1 - p.rng.uniform(0, rough)
        c, s = math.cos(a), math.sin(a)
        pts.append((w / 2 * k * math.copysign(abs(c) ** 0.55, c), -d / 2 * k * math.copysign(abs(s) ** 0.55, s)))
    p.plate(pts, t, T((x, y, z + t / 2)) @ M(rot=(0, 0, rz)) @ M(rot=(90, 0, 0)), mat=mat, noise=noise)


def rock(p, rx, ry, rz, loc, mat="stone", noise=0.035, segs=(7, 5)):
    p.ball(1.0, M(loc=loc, scale=(rx, ry, rz)), mat=mat, segs=segs, noise=noise)


def gear(p, r, m, teeth=8, th=0.012, mat="brass"):
    """Toothed disc facing local -Y (plate outline in XZ)."""
    pts = []
    for i in range(teeth * 2):
        a0 = i * math.pi / teeth
        rr = r if i % 2 == 0 else r * 0.8
        for da in (-0.32, 0.32):
            a = a0 + da * math.pi / teeth
            pts.append((math.cos(a) * rr, math.sin(a) * rr))
    p.plate(pts, th, m, mat=mat, bevel=0)
    p.cyl(r * 0.3, r * 0.3, th * 1.6, m @ M(loc=(0, th * 0.8, 0), rot=(90, 0, 0)), mat="copper", segs=8)


def wheel(p, r, loc, rim="iron", hub="body", spokes=6, t=None):
    """Spoked wheel turning about Y (rolls along X, the long side of a cart)."""
    m = T(loc) @ M(rot=(90, 0, 0))
    p.ring(r, t or r * 0.09, m, mat=rim, segs=12)
    p.cyl(r * 0.16, r * 0.16, r * 0.3, m @ T((0, 0, -r * 0.15)), mat=hub, segs=8)
    for i in range(spokes // 2):
        p.box((r * 1.9, r * 0.05, r * 0.05), M(loc=loc, rot=(0, i * 360 / spokes, 0)), mat=hub, bevel=0)


def pot(p, r, h, loc, mat="ceramic", segs=8):
    x, y, z = loc
    p.lathe([(0, 0), (r * 0.7, 0), (r, h * 0.45), (r * 0.55, h * 0.85), (r * 0.65, h)], T((x, y, z)), mat=mat, segs=segs)


def runes(p, x, y, z0, z1, n=3, w=0.03, axis="z"):
    """Vertical row of glowing rune slots on a -Y face at (x, y)."""
    step = (z1 - z0) / n
    for i in range(n):
        z = z0 + step * (i + 0.5)
        sz = (w, 0.012, step * 0.55) if i % 2 == 0 else (w * 0.5, 0.012, step * 0.7)
        p.box(sz, T((x, y, z)), mat="glow", bevel=0)


def corners(hx, hy):
    return [(sx * hx, sy * hy) for sx in (-1, 1) for sy in (-1, 1)]


# ---------------------------------------------------------------- Table
@function("Table", "Furniture", FURN, "scene")
def table(p, slot):
    e = p.era
    fh, fw, fd = F(p, 1, 0.04), F(p, 1, 0.1), F(p, 1, 0.08)
    h0, w0, d0, t = {"Primal": (0.55, 1.0, 0.7, 0.1), "Agrarian": (0.74, 1.15, 0.7, 0.045),
                     "Mercantile": (0.76, 1.1, 0.66, 0.045), "Industrial": (0.75, 1.2, 0.7, 0.035),
                     "Steampunk": (0.76, 0.95, 0.95, 0.05), "Future": (0.74, 1.2, 0.68, 0.05),
                     "Wasteland": (0.74, 1.2, 0.72, 0.045), "Ancient": (0.72, 1.2, 0.72, 0.12)}[e]
    H, W, D = h0 * fh, w0 * fw, d0 * fd
    u = H - t
    if e == "Primal":  # flat stone on boulders
        xs = (-W * 0.3, W * 0.3)
        if slot == "top":
            flagstone(p, W, D, t, u, rough=0.12, noise=0.02)
        elif slot == "legs":
            for x in xs:
                rock(p, J(p, 0.17), J(p, 0.22), (u + 0.02) / 2, (x + p.rng.uniform(-0.03, 0.03), 0, (u + 0.02) / 2))
            if coin(p):
                rock(p, 0.12, 0.12, (u + 0.02) / 2, (0, D * 0.22, (u + 0.02) / 2))
        elif slot == "frame":  # shim stones at the joints, pebbles at the feet
            for x in xs:
                p.box((J(p, 0.16), 0.07, 0.03), M(loc=(x + 0.08, -0.12, u - 0.012), rot=(0, J(p, 6, 0.5), p.rng.uniform(-30, 30))), mat="stone_dark")
                for i in range(2):
                    rock(p, 0.05, 0.04, 0.035, (x + p.rng.uniform(-0.2, 0.2), -0.2 + p.rng.uniform(-0.05, 0.05), 0.03), noise=0.05, segs=(5, 3))
        else:  # hide, a gourd and bones
            flagstone(p, J(p, W * 0.55), J(p, D * 0.6), 0.008, H, mat="hide", n=6, rough=0.25, x=p.rng.uniform(-0.15, 0.15), rz=p.rng.uniform(-20, 20), noise=0)
            pot(p, J(p, 0.06), J(p, 0.16), (W * 0.32, 0.1, H), mat="bark")
            for i in range(p.rng.randint(1, 2)):
                y = -0.1 + i * 0.08
                pole(p, (-W * 0.3, y, H + 0.015), (-W * 0.12, y + 0.06, H + 0.015), 0.012, mat="bone")
    elif e == "Agrarian":  # wooden table
        ix, iy = W / 2 - 0.07, D / 2 - 0.07
        if slot == "top":
            n = 4 if coin(p) else 3
            ov = J(p, 0.04, 0.5)
            for i in range(n):
                pd = D / n
                slab(p, W + ov * 2, pd - 0.008, t, u, y=-D / 2 + pd * (i + 0.5), mat="wood", noise=0.004)
        elif slot == "legs":
            s = J(p, 0.032, 0.12)
            for x, y in corners(ix, iy):
                post(p, x, y, 0, u, s, mat="wood")
        elif slot == "frame":
            for y in (-iy, iy):
                slab(p, ix * 2, 0.024, 0.1, u - 0.1, y=y, mat="wood", bevel=0)
            for x in (-ix, ix):
                slab(p, 0.024, iy * 2, 0.1, u - 0.1, x=x, mat="wood", bevel=0)
            z = J(p, 0.16, 0.2)
            if coin(p):
                for x in (-ix, ix):
                    slab(p, 0.03, iy * 2, 0.04, z, x=x, mat="wood", bevel=0)
                slab(p, ix * 2, 0.03, 0.04, z, mat="wood", bevel=0)
            else:
                for y in (-iy, iy):
                    slab(p, ix * 2, 0.03, 0.04, z, y=y, mat="wood", bevel=0)
        else:
            for x, y in corners(ix, iy):
                p.cyl(0.012, 0.012, 0.004, T((x, y, H)), mat="wood_dark", segs=6)
            if coin(p, 0.6):
                slab(p, J(p, 0.34), D + 0.16, 0.004, H, x=p.rng.uniform(-0.25, 0.25), mat="cloth", bevel=0)
                for y in (-D / 2 - 0.08, D / 2 + 0.08):
                    slab(p, 0.3, 0.004, 0.12, H - 0.12, x=0, y=y, mat="cloth", bevel=0)
            else:
                pot(p, J(p, 0.07), J(p, 0.12), (p.rng.uniform(-0.3, 0.3), 0.05, H), mat="ceramic")
    elif e == "Mercantile":  # carved-leg table
        ix, iy = W / 2 - 0.06, D / 2 - 0.06
        if slot == "top":
            ov = J(p, 0.03, 0.4)
            slab(p, W + ov * 2 + 0.02, D + ov * 2 + 0.02, t * 0.45, u, mat="wood_dark")
            slab(p, W + ov * 2, D + ov * 2, t * 0.55, u + t * 0.45, mat="wood_dark")
        elif slot == "legs":
            b = J(p, 1.0, 0.15)
            prof = [(0.022, 0), (0.032 * b, 0.03), (0.02, 0.08), (0.03 * b, 0.18), (0.042 * b, u * 0.42),
                    (0.024, u * 0.62), (0.03, u - 0.13), (0.03, u - 0.12)]
            for x, y in corners(ix, iy):
                p.lathe(prof, T((x, y, 0)), mat="wood_dark", segs=6)
                post(p, x, y, u - 0.12, u, 0.034, mat="wood_dark", bevel=0)
        elif slot == "frame":
            dip = J(p, 0.05, 0.3)
            for y in (-iy, iy):
                pts = [(-ix, 0), (ix, 0), (ix, -0.1)]
                for i in range(1, 6):
                    xx = ix - ix * 2 * i / 6
                    pts.append((xx, -0.1 - dip * math.sin(math.pi * i / 6)))
                pts.append((-ix, -0.1))
                p.plate(pts, 0.022, T((0, y, u)), mat="wood_dark")
            for x in (-ix, ix):
                slab(p, 0.022, iy * 2, 0.1, u - 0.1, x=x, mat="wood_dark", bevel=0)
        else:
            p.ball(0.014, T((0, -iy - 0.02, u - 0.05)), mat="brass", segs=(6, 4))
            p.box((0.05, 0.004, 0.03), T((0, -iy - 0.013, u - 0.05)), mat="brass", bevel=0)
            for x, y in corners(ix, iy):
                p.cyl(0.026, 0.024, 0.03, T((x, y, 0)), mat="brass", segs=6)
            if coin(p):
                slab(p, W * 0.9, J(p, 0.3), 0.004, H, mat="cloth", bevel=0)
    elif e == "Industrial":  # iron-legged table
        ix, iy = W / 2 - 0.04, D / 2 - 0.04
        if slot == "top":
            if coin(p, 0.6):
                slab(p, W, D, t, u, mat="wood")
            else:
                slab(p, W, D, t, u, mat="steel")
                slab(p, W - 0.1, D - 0.1, 0.003, H, mat="rubber", bevel=0)
            for y in (-D / 2, D / 2):
                slab(p, W + 0.006, 0.006, t + 0.006, u - 0.003, y=y, mat="steel", bevel=0)
        elif slot == "legs":
            a = J(p, 0.045, 0.15)
            for x, y in corners(ix, iy):
                sx, sy = math.copysign(1, x), math.copysign(1, y)
                p.box((a, 0.005, u), T((x - sx * a / 2, y, u / 2)), mat="steel", bevel=0)
                p.box((0.005, a, u), T((x, y - sy * a / 2, u / 2)), mat="steel", bevel=0)
        elif slot == "frame":
            for y in (-iy, iy):
                slab(p, ix * 2, 0.005, 0.04, u - 0.04, y=y, mat="steel", bevel=0)
            for x in (-ix, ix):
                slab(p, 0.005, iy * 2, 0.04, u - 0.04, x=x, mat="steel", bevel=0)
            if coin(p):
                for s in (-1, 1):
                    pole(p, (-ix, iy, 0.1), (ix, iy, u - 0.06), 0.008, mat="steel", segs=4) if s > 0 else \
                        pole(p, (ix, iy, 0.1), (-ix, iy, u - 0.06), 0.008, mat="steel", segs=4)
            else:
                slab(p, ix * 2, iy * 2, 0.02, J(p, 0.18, 0.2), mat="steel")
        else:
            for x, y in corners(ix, iy):
                p.cyl(0.024, 0.024, 0.02, T((x, y, 0)), mat="rubber", segs=6)
                p.cyl(0.007, 0.007, 0.008, M(loc=(x, y - math.copysign(0.004, y), u - 0.02), rot=(90, 0, 0)), mat="steel", segs=6)
            if coin(p):
                p.box((0.12, 0.003, 0.05), T((J(p, 0.2, 0.5), -D / 2 - 0.004, u - 0.02)), mat="paint", bevel=0)
    elif e == "Steampunk":  # round brass mechanism table
        R = W / 2
        dr = 0.2
        zc = u - 0.12
        if slot == "top":
            p.cyl(R, R, t, T((0, 0, u)), mat="wood_dark", segs=16)
            p.ring(R, 0.012, T((0, 0, u + t / 2)), mat="brass", segs=16)
        elif slot == "legs":
            p.cyl(0.05, J(p, 0.045, 0.1), zc - 0.14, T((0, 0, 0.14)), mat="brass", segs=8)
            p.lathe([(0.09, 0.1), (0.06, 0.16), (0.05, 0.18)], mat="brass", segs=8)
            n = 3 if coin(p) else 4
            for i in range(n):
                a = i * math.tau / n + math.pi / 2
                fx, fy = math.cos(a) * R * 0.72, math.sin(a) * R * 0.72
                p.tube([(0, 0, 0.16), (fx * 0.5, fy * 0.5, 0.1), (fx, fy, 0.035)], 0.018, mat="brass", segs=6)
                p.ball(0.032, T((fx, fy, 0.032)), mat="brass", segs=(6, 4))
        elif slot == "frame":
            p.cyl(dr, dr, 0.12, T((0, 0, zc)), mat="brass", segs=12)
            p.band(dr, 0.03, m=T((0, 0, zc)), h=0.04)
            gear(p, J(p, 0.27, 0.1), T((0, 0, u - 0.008)) @ M(rot=(90, 0, J(p, 10, 1))), teeth=10, th=0.012)
        else:
            p.cyl(0.04, 0.04, 0.01, M(loc=(0, -dr, zc + 0.06), rot=(90, 0, 0)), mat="brass", segs=10)
            p.cyl(0.032, 0.032, 0.002, M(loc=(0, -dr - 0.01, zc + 0.06), rot=(90, 0, 0)), mat="glow", segs=10)
            p.tube([(dr * 0.7, -dr * 0.7, zc + 0.03), (0.08, -0.06, zc - 0.15), (0.05, -0.02, 0.3)], 0.01, mat="copper", segs=5)
            if coin(p):
                p.tube([(dr, 0, zc + 0.06), (dr + 0.06, 0, zc + 0.06), (dr + 0.06, 0, zc - 0.02)], 0.007, mat="brass", segs=4)
                p.ball(0.015, T((dr + 0.06, 0, zc - 0.03)), mat="wood_dark", segs=(6, 4))
    elif e == "Future":  # floating tabletop over an emitter
        zs = u - 0.22
        if slot == "top":
            slab(p, W, D, t, u, mat="body")
        elif slot == "legs":
            rb = J(p, 0.28, 0.12)
            p.lathe([(0, 0), (rb, 0), (rb * 1.04, 0.02), (rb * 0.9, 0.05), (0.09, 0.07), (0.06, 0.2),
                     (J(p, 0.05, 0.2), zs - 0.02), (0.07, zs), (0, zs)], mat="body", segs=14)
        elif slot == "frame":
            p.cyl(0.022, 0.022, u - zs, T((0, 0, zs)), mat="glow", segs=8)
            for i, z in enumerate((0.35, 0.7)):
                rr = J(p, 0.07 + i * 0.05, 0.2)
                p.ring(rr, 0.006, T((0, 0, zs + (u - zs) * z)), mat="glow", segs=12)
            p.cyl(0.16, 0.1, 0.02, M(loc=(0, 0, u), rot=(180, 0, 0)), mat="shell_dark", segs=14)
        else:
            for y in (-D / 2, D / 2):
                p.box((W * 0.7, 0.006, 0.01), T((0, y + math.copysign(0.001, y), u + t / 2)), mat="glow", bevel=0)
            if coin(p, 0.6):
                p.box((J(p, 0.3), J(p, 0.22), 0.002), T((p.rng.uniform(-0.3, 0.3), 0, H + 0.001)), mat="glow", bevel=0)
    elif e == "Wasteland":  # door slab on a drum and scrap legs
        xd = -W / 2 + 0.22
        xr = W / 2 - 0.08
        if slot == "top":
            slab(p, W, D, t, u, mat="wood", noise=0.006)
            p.box((J(p, 0.35), J(p, 0.3), 0.004), M(loc=(p.rng.uniform(-0.2, 0.2), p.rng.uniform(-0.1, 0.1), H + 0.002), rot=(0, 0, p.rng.uniform(-15, 15))), mat="rust", bevel=0)
            p.cyl(0.02, 0.02, 0.006, M(loc=(W * 0.3, -D / 2 - 0.003, u + t / 2), rot=(90, 0, 0)), mat="iron", segs=6)
        elif slot == "legs":
            p.cyl(0.19, 0.19, u, T((xd, 0, 0)), mat="paint", segs=12)
            if coin(p):
                for y in (-D / 2 + 0.08, D / 2 - 0.08):
                    p.cyl(0.022, 0.022, u, M(loc=(xr, y, 0), rot=(J(p, 2, 1), 0, 0)), mat="iron", segs=6)
            else:
                n = 3
                for i in range(n):
                    p.box((0.2, 0.4, u / n - 0.004), M(loc=(xr - 0.08, 0, u / n * (i + 0.5)), rot=(0, 0, p.rng.uniform(-6, 6))), mat="stone_dark", bevel=0.05)
        elif slot == "frame":
            for z in (0.12, u - 0.08):
                p.ring(0.192, 0.01, T((xd, 0, z)), mat="iron", segs=12)
            z = J(p, 0.35, 0.2)
            p.tube([(xd + 0.19, 0, z), (xr - 0.08, 0, z + 0.05)], 0.016, mat="rust", segs=6)
            p.band(0.03, 0, m=T((xr - 0.12, 0, z + 0.04)) @ M(rot=(0, 90, 0)), h=0.04)
        else:
            flagstone(p, J(p, 0.4), J(p, 0.5), 0.006, H, mat="cloth", n=6, rough=0.3, x=p.rng.uniform(-0.3, 0.1), noise=0)
            p.cyl(0.035, 0.035, 0.1, T((W * 0.3, 0.15, H)), mat="steel", segs=8)
            if coin(p, 0.6):
                p.cyl(0.05, 0.045, 0.12, T((-W * 0.25, 0.12, H)), mat="glass", segs=8)
                p.ball(0.03, T((-W * 0.25, 0.12, H + 0.06)), mat="glow", segs=(6, 4))
    else:  # Ancient: monolith slab on two block supports
        lx = W / 2 - W * 0.13
        lw = W * 0.15
        if slot == "top":
            slab(p, W, D, t, u, mat="body")
        elif slot == "legs":
            for x in (-lx, lx):
                p.box((lw, D * J(p, 0.75, 0.06), u), T((x, 0, u / 2)), mat="body", bevel=0.12)
        elif slot == "frame":
            inner = (lx - lw / 2) * 2
            slab(p, inner + 0.02, D * 0.45, 0.1, 0.0, mat="stone_dark", bevel=0.1)
            slab(p, inner + 0.02, D * J(p, 0.3, 0.2), 0.07, u - 0.07, mat="stone_dark", bevel=0.1)
        else:
            for x in (-lx, lx):
                runes(p, x, -D * 0.375 - 0.004, u * 0.25, u * 0.85, n=p.rng.choice((2, 3)))
            p.box((W * 0.85, 0.01, 0.014), T((0, -D / 2 - 0.003, u + t * 0.5)), mat="glow", bevel=0)
            if coin(p):
                p.box((W * 0.9, 0.012, 0.012), T((0, -D / 2 - 0.004, u + t * 0.85)), mat="gold", bevel=0)


# ---------------------------------------------------------------- Chair
@function("Chair", "Furniture", FURN, "scene")
def chair(p, slot):
    e = p.era
    fs, fw, fb = F(p, 1, 0.04), F(p, 1, 0.08), F(p, 1, 0.06)
    S = 0.45 * fs
    W, D = 0.45 * fw, 0.43 * fw
    B = 0.92 * fb
    if e == "Primal":  # tree stump
        r = W * 0.55
        if slot == "top":
            p.cyl(r * 0.98, r * 0.98, 0.012, T((0, 0, S - 0.012)), mat="wood", segs=10)
            for k in (0.45, 0.75):
                p.ring(r * k, 0.003, T((0, 0, S)), mat="bark", segs=10)
        elif slot == "legs":
            w = J(p, 1.0, 0.1)
            p.lathe([(r * 1.25 * w, 0), (r * 1.1, 0.05), (r * 1.02, S * 0.4), (r, S - 0.012), (r * 0.98, S - 0.012)], mat="bark", segs=10, noise=0.03)
        elif slot == "frame":  # root flares
            n = p.rng.randint(3, 5)
            for i in range(n):
                a = i * math.tau / n + p.rng.uniform(-0.3, 0.3)
                c, s = math.cos(a), math.sin(a)
                L = J(p, 0.22, 0.3)
                p.tube([(c * r * 0.9, s * r * 0.9, 0.12), (c * (r + L * 0.5), s * (r + L * 0.5), 0.05), (c * (r + L), s * (r + L), 0.0)], 0.035, mat="bark", segs=5)
        else:  # pelt
            flagstone(p, J(p, r * 1.7), J(p, r * 1.5), 0.01, S, mat="hide", n=7, rough=0.25, rz=p.rng.uniform(-30, 30), noise=0)
            p.box((J(p, 0.16), 0.012, 0.16), M(loc=(p.rng.uniform(-0.05, 0.05), -r - 0.012, S - 0.07), rot=(0, 0, p.rng.uniform(-10, 10))), mat="hide", bevel=0)
    elif e == "Agrarian":  # wooden stool
        st = 0.04
        sp = J(p, 1.0, 0.1)
        if slot == "top":
            if coin(p):
                p.cyl(W * 0.55, W * 0.55, st, T((0, 0, S - st)), mat="wood", segs=10, bevel=0.04)
            else:
                slab(p, W * 1.05, D * 0.8, st, S - st, mat="wood")
        elif slot == "legs":
            n = 3 if coin(p, 0.4) else 4
            for i in range(n):
                a = i * math.tau / n + math.pi / 4
                c, s = math.cos(a), math.sin(a)
                p.tube([(c * W * 0.3, s * W * 0.25, S - st), (c * W * 0.46 * sp, s * W * 0.4 * sp, 0)], J(p, 0.02, 0.1), mat="wood", segs=6)
        elif slot == "frame":  # rungs
            z = J(p, 0.18, 0.15)
            k = 0.3 + (0.46 * sp - 0.3) * (1 - z / S)
            for a in (math.pi / 4, 3 * math.pi / 4):
                c, s = math.cos(a), math.sin(a)
                pole(p, (c * W * k, s * W * k * 0.87, z), (-c * W * k, -s * W * k * 0.87, z + 0.03), 0.012, mat="wood")
        else:
            if coin(p, 0.6):
                p.cyl(W * 0.42, W * 0.4, 0.03, T((0, 0, S)), mat="cloth", segs=10)
            else:
                for x in (-W * 0.25, W * 0.25):
                    for y in (-W * 0.2, W * 0.2):
                        p.cyl(0.01, 0.01, 0.004, T((x, y, S)), mat="wood_dark", segs=6)
    elif e == "Mercantile":  # back chair
        st = 0.035
        ix, iy = W / 2 - 0.03, D / 2 - 0.03
        if slot == "top":
            slab(p, W, D, st, S - st, mat="wood_dark")
            slab(p, W - 0.05, D - 0.06, J(p, 0.035, 0.2), S, mat="leather", bevel=0.25)
        elif slot == "legs":
            b = J(p, 1.0, 0.15)
            prof = [(0.016, 0), (0.022 * b, 0.03), (0.014, 0.07), (0.024 * b, (S - st) * 0.5), (0.016, (S - st) * 0.8), (0.02, S - st)]
            for x, y in corners(ix, iy):
                if y < 0:
                    p.lathe(prof, T((x, y, 0)), mat="wood_dark", segs=6)
                else:
                    post(p, x, y, 0, S - st, 0.018, mat="wood_dark", bevel=0)
            for x in (-ix, ix):
                slab(p, 0.016, iy * 2, 0.025, 0.12, x=x, mat="wood_dark", bevel=0)
        elif slot == "frame":
            top = B - S
            for x in (-ix, ix):
                p.tube([(x, iy, S - 0.01), (x * 0.98, iy + 0.03, S + top * 0.5), (x * 0.95, iy + 0.06, B)], 0.018, mat="wood_dark", segs=6)
            pts = [(-ix, 0), (ix, 0), (ix * 1.05, 0.06)]
            arch = J(p, 0.05, 0.4)
            for i in range(1, 5):
                pts.append((ix - ix * 2 * i / 5, 0.06 + arch * math.sin(math.pi * i / 5)))
            pts.append((-ix * 1.05, 0.06))
            p.plate(pts, 0.025, M(loc=(0, iy + 0.06, B - 0.06), rot=(-8, 0, 0)), mat="wood_dark")
            w = J(p, 0.1, 0.25)
            vase = [(-w * 0.4, 0), (w * 0.4, 0), (w * 0.6, top * 0.3), (w * 0.3, top * 0.55), (w * 0.5, top * 0.82),
                    (-w * 0.5, top * 0.82), (-w * 0.3, top * 0.55), (-w * 0.6, top * 0.3)]
            p.plate(vase, 0.015, M(loc=(0, iy + 0.03, S), rot=(-8, 0, 0)), mat="wood_dark")
        else:
            for x in (-W / 2 + 0.01, W / 2 - 0.01):
                for y in (-D * 0.3, 0, D * 0.3):
                    p.ball(0.006, T((x, y, S - st * 0.5)), mat="brass", segs=(4, 3))
            if coin(p):
                for x in (-ix, ix):
                    p.ball(0.022, T((x * 0.95, iy + 0.06, B + 0.012)), mat="brass", segs=(6, 4))
            else:
                p.box((0.06, 0.006, 0.03), T((0, iy + 0.05, B - 0.03)), mat="brass", bevel=0)
    elif e == "Industrial":  # folding chair
        st = 0.03
        hx = W / 2 - 0.02
        if slot == "top":
            slab(p, W - 0.03, D, st, S - st, mat="wood" if coin(p) else "paint")
        elif slot == "legs":
            sp = J(p, 1.0, 0.08)
            for x in (-hx, hx):
                pole(p, (x, -D * 0.5 * sp, 0), (x, D * 0.38, S - st), 0.011, mat="steel")
                pole(p, (x, D * 0.5 * sp, 0), (x, -D * 0.38, S - st), 0.011, mat="steel")
            pole(p, (-hx, -D * 0.5 * sp, 0.03), (hx, -D * 0.5 * sp, 0.03), 0.009, mat="steel")
        elif slot == "frame":
            for x in (-hx, hx):
                pole(p, (x, D * 0.38, S - st), (x, D * 0.5, B), 0.011, mat="steel")
            p.box((W - 0.03, 0.02, J(p, 0.14, 0.15)), M(loc=(0, D * 0.48, B - 0.1), rot=(-8, 0, 0)), mat="paint")
            pole(p, (-hx, D * 0.44, S + 0.05), (hx, D * 0.44, S + 0.05), 0.008, mat="steel")
        else:
            for x in (-hx, hx):
                p.cyl(0.018, 0.018, 0.014, M(loc=(x - math.copysign(0.007, x), 0, S * 0.5), rot=(0, 90, 0)), mat="steel", segs=6)
                for y in (-D * 0.5, D * 0.5):
                    p.ball(0.016, M(loc=(x, y * J(p, 1.0, 0.08), 0.008), scale=(1, 1, 0.6)), mat="rubber", segs=(6, 3))
    elif e == "Steampunk":  # swivel chair
        zc = S - 0.08
        if slot == "top":
            p.cyl(W * 0.5, W * 0.48, 0.03, T((0, 0, zc)), mat="brass", segs=12)
            p.lathe([(W * 0.48, zc + 0.03), (W * 0.5, zc + 0.05), (W * 0.46, S), (0, S + 0.005)], mat="leather", segs=12)
        elif slot == "legs":
            p.cyl(0.03, 0.03, zc - 0.1, T((0, 0, 0.1)), mat="brass", segs=8)
            n = p.rng.choice((4, 5))
            for i in range(n):
                a = i * math.tau / n
                c, s = math.cos(a), math.sin(a)
                p.tube([(0, 0, 0.12), (c * 0.16, s * 0.16, 0.07), (c * 0.28, s * 0.28, 0.04)], 0.014, mat="brass", segs=5)
                p.ball(0.025, T((c * 0.28, s * 0.28, 0.025)), mat="wood_dark", segs=(6, 4))
        elif slot == "frame":
            arm = J(p, 1.0, 0.12)
            p.tube([(0, W * 0.35, zc + 0.01), (0, W * 0.5, zc + 0.08), (0, W * 0.52, S + 0.12 * arm)], 0.016, mat="brass", segs=6)
            zb = S + 0.1 * arm
            for i in range(6):
                a0 = math.radians(-60 + 120 * i / 6)
                a1 = math.radians(-60 + 120 * (i + 1) / 6)
                am = (a0 + a1) / 2
                L = 2 * W * 0.5 * math.sin((a1 - a0) / 2)
                p.box((L + 0.01, 0.03, B - zb), M(loc=(math.sin(am) * W * 0.5, math.cos(am) * W * 0.5, (zb + B) / 2), rot=(0, 0, -math.degrees(am))), mat="leather", bevel=0)
            p.tube([(math.sin(math.radians(a)) * W * 0.52, math.cos(math.radians(a)) * W * 0.52, B) for a in range(-62, 63, 20)], 0.01, mat="brass", segs=5)
        else:
            for z in (0.16, 0.22, 0.28):
                p.ring(0.042, 0.006, T((0, 0, z)), mat="copper", segs=8)
            p.cyl(0.06, 0.06, 0.03, T((0, 0, zc - 0.03)), mat="brass", segs=8)
            p.ball(0.012, T((0, -0.06, zc - 0.015)), mat="glow", segs=(6, 4))
            if coin(p):
                p.tube([(W * 0.45, 0, zc + 0.02), (W * 0.55, -0.02, zc - 0.03), (W * 0.55, -0.02, zc - 0.07)], 0.006, mat="brass", segs=4)
    elif e == "Future":  # hover seat
        zh = S - 0.2
        if slot == "top":
            p.lathe([(0, S - 0.09), (W * 0.42, S - 0.08), (W * 0.52, S - 0.03), (W * 0.5, S), (0, S - 0.01)], mat="body", segs=14)
        elif slot == "legs":
            rb = J(p, 0.22, 0.12)
            p.lathe([(0, 0), (rb, 0), (rb * 1.03, 0.015), (rb * 0.85, 0.04), (0.05, 0.05), (0.035, zh - 0.02), (0.05, zh), (0, zh)], mat="body", segs=12)
        elif slot == "frame":
            back = []
            for i in range(6):
                a = math.radians(-70 + 140 * i / 5)
                back.append((math.sin(a) * W * 0.48, math.cos(a) * W * 0.42))
            h = B - S
            for (x0, y0), (x1, y1) in zip(back, back[1:]):
                mx, my = (x0 + x1) / 2, (y0 + y1) / 2
                L = math.hypot(x1 - x0, y1 - y0)
                ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
                p.box((L + 0.012, 0.04, h * J(p, 1.0, 0.06)), M(loc=(mx, my, S - 0.03 + h / 2), rot=(0, 0, ang)), mat="body", bevel=0.15, bevel_seg=1)
        else:
            p.cyl(0.02, 0.02, S - 0.09 - zh, T((0, 0, zh)), mat="glow", segs=6)
            p.ring(J(p, 0.12, 0.2), 0.006, T((0, 0, (S - 0.09 + zh) / 2)), mat="glow", segs=12)
            p.ring(W * 0.5, 0.005, T((0, 0, S - 0.03)), mat="glow", segs=14)
    elif e == "Wasteland":  # car seat on tyres or a crate
        zc = S - 0.1
        if slot == "top":
            p.box((W * 1.05, D, 0.1), M(loc=(0, -0.01, zc + 0.05), rot=(-4, 0, 0)), mat="cloth", bevel=0.3)
            p.box((J(p, 0.14), J(p, 0.14), 0.006), M(loc=(p.rng.uniform(-0.1, 0.1), -0.05, S + 0.002), rot=(0, 0, 20)), mat="leather", bevel=0)
        elif slot == "legs":
            if coin(p):
                n = 2
                th = zc / n
                for i in range(n):
                    p.ring(0.2, th * 0.5, M(loc=(p.rng.uniform(-0.01, 0.01), 0, th * (i + 0.5)), rot=(0, 0, p.rng.uniform(0, 30))), mat="rubber", segs=12, square=True)
                p.cyl(0.14, 0.14, 0.01, T((0, 0, zc - 0.01)), mat="wood", segs=10)
            else:
                p.box((W * 0.95, D * 0.9, zc), M(loc=(0, 0, zc / 2), rot=(0, 0, p.rng.uniform(-5, 5))), mat="paint", bevel=0.05)
        elif slot == "frame":
            p.box((W, 0.12, B - zc), M(loc=(0, D * 0.42, (B + zc) / 2), rot=(-J(p, 10, 0.4), 0, 0)), mat="cloth", bevel=0.3)
        else:
            p.box((W * 1.08, 0.13, 0.05), M(loc=(0, D * 0.42, S + 0.12)), mat="steel", bevel=0)
            p.band(0.03, 0, m=M(loc=(W * 0.4, -0.02, zc + 0.05), rot=(90, 0, 0)), h=0.04)
            if coin(p):
                pole(p, (-W * 0.5, D * 0.42, S + 0.12), (-W * 0.5 - 0.02, D * 0.3, 0.05), 0.004, mat="iron", segs=4)
    else:  # Ancient: stone seat block
        if slot == "top":
            slab(p, W * 1.1, D * 1.05, 0.09, S - 0.09, mat="body")
        elif slot == "legs":
            for x in (-W * 0.42, W * 0.42):
                p.box((W * 0.22, D * J(p, 0.9, 0.06), S - 0.09), T((x, 0, (S - 0.09) / 2)), mat="body", bevel=0.12)
        elif slot == "frame":
            pts = [(-W * 0.5, 0), (W * 0.5, 0), (W * 0.5, (B - S) * 0.8), (W * 0.25, B - S), (-W * 0.25, B - S), (-W * 0.5, (B - S) * 0.8)]
            p.plate(pts, J(p, 0.08, 0.15), M(loc=(0, D * 0.45, S), rot=(-6, 0, 0)), mat="body", bevel=0.25)
        else:
            runes(p, 0, D * 0.45 - 0.05, S + 0.08, B - 0.12, n=p.rng.choice((2, 3)), w=0.04)
            for x in (-W * 0.42, W * 0.42):
                p.box((0.03, 0.01, (S - 0.09) * 0.5), T((x, -D * 0.45 - 0.004, (S - 0.09) * 0.5)), mat="glow" if coin(p) else "gold", bevel=0)


# ---------------------------------------------------------------- Shelf
@function("Shelf", "Furniture", FURN, "scene")
def shelf(p, slot):
    e = p.era
    fh, fw, fd = F(p, 1, 0.06), F(p, 1, 0.1), F(p, 1, 0.08)
    h0, w0, d0 = {"Primal": (1.1, 0.9, 0.42), "Agrarian": (1.5, 0.9, 0.35), "Mercantile": (1.7, 0.9, 0.4),
                  "Industrial": (1.6, 0.95, 0.4), "Steampunk": (1.5, 0.7, 0.7), "Future": (1.6, 0.95, 0.32),
                  "Wasteland": (1.45, 1.0, 0.4), "Ancient": (1.5, 0.9, 0.42)}[e]
    H, W, D = h0 * fh, w0 * fw, d0 * fd
    if e == "Primal":  # stone niche: piled slabs with a recess
        zb = 0.22
        levels = (zb, zb + (H - zb) * 0.48)
        if slot == "top":
            for z in levels:
                flagstone(p, W * 0.82, D * 0.9, 0.05, z - 0.05, rough=0.08, x=0, y=-0.02)
            flagstone(p, W * 1.08, D * 1.1, 0.09, H - 0.09, rough=0.12)
        elif slot == "legs":
            for x in (-W * 0.28, W * 0.28):
                rock(p, J(p, 0.2), D * 0.48, zb / 2 + 0.01, (x, 0, zb / 2))
        elif slot == "frame":
            for x in (-W * 0.45, W * 0.45):
                p.box((J(p, 0.12, 0.15), D, H - zb - 0.09), M(loc=(x, 0, (H + zb - 0.09) / 2), rot=(0, p.rng.uniform(-3, 3), 0)), mat="stone", noise=0.03)
            p.box((W * 0.8, 0.08, H - zb - 0.09), T((0, D * 0.45, (H + zb - 0.09) / 2)), mat="stone_dark", noise=0.02)
        else:
            pot(p, J(p, 0.08), J(p, 0.16), (-W * 0.15, 0, levels[0]), mat="ceramic")
            pole(p, (W * 0.05, -0.05, levels[1] + 0.015), (W * 0.3, 0.02, levels[1] + 0.02), 0.014, mat="bone")
            if coin(p):
                p.ball(0.06, M(loc=(W * 0.2, 0.02, levels[0] + 0.05), scale=(1.2, 1, 0.8)), mat="hide", segs=(6, 4))
            else:
                for i in range(3):
                    p.ball(0.025, T((W * 0.12 + i * 0.06, -0.02, levels[0] + 0.025)), mat="stone_dark", segs=(5, 3))
    elif e == "Agrarian":  # wooden shelf
        n = 4
        hx, hy = W / 2 - 0.025, D / 2 - 0.025
        zs = [0.1 + (H - 0.14) * i / (n - 1) for i in range(n)]
        if slot == "top":
            for z in zs:
                slab(p, W - 0.02, D - 0.02, 0.025, z, mat="wood", noise=0.003)
        elif slot == "legs":
            for x, y in corners(hx, hy):
                post(p, x, y, 0, 0.1, 0.03, mat="wood_dark", bevel=0.15)
        elif slot == "frame":
            for x, y in corners(hx, hy):
                post(p, x, y, 0.1, H, 0.022, mat="wood")
            if coin(p):
                for x in (-hx, hx):
                    pole(p, (x, -hy, zs[0] + 0.02), (x, hy, zs[2]), 0.01, mat="wood", segs=4)
            else:
                pole(p, (-hx, hy, zs[0] + 0.02), (hx, hy, zs[-1] - 0.02), 0.01, mat="wood", segs=4)
        else:
            pot(p, J(p, 0.08), J(p, 0.18), (-W * 0.22, 0, zs[1] + 0.025), mat="ceramic")
            p.lathe([(0, 0), (0.14, 0.005), (0.15, 0.12), (0.155, 0.13)], T((W * 0.18, 0, zs[0] + 0.025)), mat="rope", segs=8)
            if coin(p):
                pot(p, J(p, 0.06), J(p, 0.12), (W * 0.2, -0.02, zs[2] + 0.025), mat="glaze")
            else:
                for i in range(3):
                    p.ball(0.035, T((-W * 0.1 + i * 0.07, 0, zs[2] + 0.06)), mat="cloth", segs=(6, 4))
    elif e == "Mercantile":  # carved cabinet: open shelves over a cupboard
        zb = 0.08
        zc = 0.75 * fh
        hx = W / 2 - 0.02
        if slot == "top":
            slab(p, W - 0.04, D - 0.04, 0.03, zc, mat="wood_dark", bevel=0)
            for i in (1, 2):
                slab(p, W - 0.04, D - 0.06, 0.022, zc + (H - 0.1 - zc) * i / 3, mat="wood_dark", bevel=0)
            for s in (-1, 1):
                p.box((W / 2 - 0.03, 0.02, zc - zb - 0.02), T((s * (W / 4 - 0.005), -D / 2 + 0.01, (zc + zb) / 2)), mat="wood_dark")
        elif slot == "legs":
            for x, y in corners(hx - 0.03, D / 2 - 0.05):
                p.ball(J(p, 0.045, 0.15), M(loc=(x, y, zb / 2 + 0.005), scale=(1, 1, zb / 2 / 0.045)), mat="wood_dark", segs=(8, 4))
        elif slot == "frame":
            for x in (-hx, hx):
                slab(p, 0.03, D, H - zb - 0.08, zb, x=x, mat="wood_dark")
            slab(p, W - 0.04, 0.015, H - zb - 0.08, zb, y=D / 2 - 0.008, mat="wood", bevel=0)
            slab(p, W - 0.04, D, 0.03, zb, mat="wood_dark", bevel=0)
            slab(p, W + 0.06, D + 0.04, 0.035, H - 0.08, mat="wood_dark")
            slab(p, W + 0.02, D + 0.02, 0.045, H - 0.045, mat="wood_dark")
        else:
            crest = J(p, 0.16, 0.3)
            pts = [(-W * 0.4, 0), (W * 0.4, 0), (W * 0.3, crest * 0.5), (W * 0.12, crest * 0.6), (0, crest), (-W * 0.12, crest * 0.6), (-W * 0.3, crest * 0.5)]
            p.plate(pts, 0.025, T((0, -D / 2 + 0.03, H)), mat="wood_dark")
            for s in (-1, 1):
                p.ball(0.014, T((s * 0.04, -D / 2 - 0.006, (zc + zb) / 2 + 0.05)), mat="brass", segs=(6, 4))
            if coin(p):
                p.ball(0.03, T((0, -D / 2 + 0.03, H + crest + 0.02)), mat="brass", segs=(6, 4))
            for x in (-W * 0.25, W * 0.2):
                pot(p, J(p, 0.05), J(p, 0.14), (x, 0, zc + 0.03), mat="glaze")
    elif e == "Industrial":  # steel rack
        n = 4
        hx, hy = W / 2 - 0.02, D / 2 - 0.02
        zs = [0.08 + (H - 0.1) * i / (n - 1) for i in range(n)]
        if slot == "top":
            for z in zs:
                slab(p, W - 0.01, D - 0.01, 0.018, z - 0.018, mat="steel", bevel=0)
                for y in (-D / 2, D / 2):
                    slab(p, W - 0.01, 0.004, 0.035, z - 0.035, y=y, mat="steel", bevel=0)
        elif slot == "legs":
            for x, y in corners(hx, hy):
                slab(p, 0.07, 0.07, 0.006, 0, x=x, y=y, mat="steel", bevel=0)
                p.cyl(0.008, 0.008, 0.02, T((x, y, 0.006)), mat="steel", segs=6)
        elif slot == "frame":
            a = J(p, 0.035, 0.15)
            for x, y in corners(hx, hy):
                sx, sy = math.copysign(1, x), math.copysign(1, y)
                p.box((a, 0.004, H - 0.026), T((x - sx * a / 2, y, (H + 0.026) / 2)), mat="paint", bevel=0)
                p.box((0.004, a, H - 0.026), T((x, y - sy * a / 2, (H + 0.026) / 2)), mat="paint", bevel=0)
            if coin(p):
                for x in (-hx, hx):
                    pole(p, (x, -hy, zs[0]), (x, hy, zs[2]), 0.004, mat="steel", segs=4)
        else:
            for i, z in enumerate(zs[:3]):
                if coin(p, 0.7):
                    slab(p, J(p, 0.3), J(p, 0.26), J(p, 0.2), z, x=p.rng.uniform(-0.2, 0.2), mat="cloth" if i % 2 else "paint", bevel=0.04)
            for x, y in corners(hx, hy):
                for z in zs:
                    p.cyl(0.006, 0.006, 0.006, M(loc=(x, y - math.copysign(0.002, y), z - 0.02), rot=(90, 0, 0)), mat="steel", segs=6)
    elif e == "Steampunk":  # gear-driven rotating carousel rack
        R = W / 2
        zb = 0.12
        zs = [zb + (H - 0.2 - zb) * i / 2 for i in range(3)]
        if slot == "top":
            for i, z in enumerate(zs):
                rr = R * (1 - i * 0.12)
                p.cyl(rr, rr, 0.025, T((0, 0, z)), mat="wood_dark", segs=12)
                p.ring(rr, 0.008, T((0, 0, z + 0.03)), mat="brass", segs=12)
        elif slot == "legs":
            p.lathe([(0, 0.0), (R * 0.75, 0.0), (R * 0.8, 0.04), (R * 0.55, 0.09), (0.05, zb)], mat="brass", segs=12)
            for i in range(4):
                a = i * math.tau / 4 + math.pi / 4
                p.ball(0.03, T((math.cos(a) * R * 0.75, math.sin(a) * R * 0.75, 0.02)), mat="brass", segs=(6, 3))
        elif slot == "frame":
            p.cyl(0.03, 0.03, H - zb, T((0, 0, zb)), mat="brass", segs=8)
            p.lathe([(0.03, H), (0.06, H + 0.03), (0.0, H + 0.1)], mat="brass", segs=8)
            for z in zs:
                p.band(0.03, z - 0.02, h=0.04)
        else:
            gear(p, J(p, 0.13, 0.15), M(loc=(R * 0.55, -R * 0.55, zb + 0.02), rot=(90, 0, 45)), teeth=8, th=0.014)
            p.tube([(R * 0.6, -R * 0.62, zb + 0.08), (R * 0.75, -R * 0.75, zb + 0.08), (R * 0.75, -R * 0.75, zb + 0.18)], 0.008, mat="brass", segs=4)
            p.ball(0.016, T((0, 0, H + 0.11)), mat="glow", segs=(6, 4))
            for z in zs:
                if coin(p, 0.7):
                    p.lathe([(0, 0), (0.05, 0), (0.05, 0.12), (0.02, 0.16), (0.02, 0.18)], T((p.rng.uniform(-0.15, 0.15), -R * 0.55, z + 0.025)), mat="glass", segs=8)
    elif e == "Future":  # modular wall rack
        zb = 0.06
        if slot == "top":
            n = 3 if coin(p) else 4
            for i in range(n):
                z = zb + 0.2 + (H - 0.4) * i / (n - 1)
                w = W * (0.9 if i % 2 == 0 else 0.6)
                x = 0 if i % 2 == 0 else J(p, 0.15, 0.6) * (1 if coin(p) else -1)
                slab(p, w, D * 0.95, 0.04, z, x=x, y=-D * 0.02, mat="body", bevel=0.3, bevel_seg=1)
        elif slot == "legs":
            slab(p, W * 0.96, D * 0.4, zb, 0, y=D * 0.28, mat="shell_dark", bevel=0.3)
        elif slot == "frame":
            slab(p, W, 0.04, H - zb, zb, y=D / 2 - 0.02, mat="body", bevel=0.2, bevel_seg=1)
            for x in (-W * 0.35, W * 0.35):
                p.box((0.02, 0.01, H - zb - 0.2), T((x, D / 2 - 0.042, (H + zb) / 2)), mat="shell_dark", bevel=0)
        else:
            for x in (-W * 0.35, W * 0.35):
                p.box((0.008, 0.004, H - zb - 0.25), T((x, D / 2 - 0.049, (H + zb) / 2)), mat="glow", bevel=0)
            for i in range(p.rng.randint(2, 3)):
                z = zb + 0.2 + (H - 0.4) * i / 2
                p.box((J(p, 0.12, 0.3), 0.004, 0.012), T((p.rng.uniform(-0.3, 0.3), -D * 0.5, z + 0.02)), mat="glow", bevel=0)
            if coin(p):
                p.box((0.14, 0.14, 0.14), T((J(p, 0.25), 0, zb + 0.2 + 0.04 + 0.07)), mat="shell_dark", bevel=0.2, bevel_seg=1)
    elif e == "Wasteland":  # cinder blocks, scrap boards, pipe uprights
        zb = 0.18
        zs = (zb, zb + (H - zb) * 0.45, H - 0.03)
        if slot == "top":
            for i, z in enumerate(zs):
                mat = ("wood", "rust", "wood")[i]
                p.box((W * J(p, 1.0, 0.06), D, 0.025), M(loc=(p.rng.uniform(-0.03, 0.03), 0, z + 0.0125), rot=(0, p.rng.uniform(-1.5, 1.5), p.rng.uniform(-3, 3))), mat=mat, noise=0.005)
        elif slot == "legs":
            for x in (-W * 0.35, W * 0.35):
                p.box((0.2, D * 0.9, zb), M(loc=(x, 0, zb / 2), rot=(0, 0, p.rng.uniform(-4, 4))), mat="stone_dark", bevel=0.05, noise=0.01)
        elif slot == "frame":
            for x in (-W * 0.45, W * 0.45):
                for y in (-D * 0.4, D * 0.4):
                    p.cyl(0.018, 0.018, H - zb, T((x, y, zb)), mat="iron" if coin(p) else "rust", segs=6)
            p.box((W * 0.6, 0.012, (H - zb) * 0.5), M(loc=(-W * 0.1, D * 0.45, zb + (H - zb) * 0.3), rot=(0, 4, 0)), mat="rust", bevel=0)
        else:
            for z in zs[:2]:
                for x in (-W * 0.45, W * 0.45):
                    p.ring(0.022, 0.004, T((x, -D * 0.4, z + 0.01)), mat="iron", segs=6)
            p.cyl(0.04, 0.04, 0.11, T((-W * 0.2, 0, zs[0] + 0.025)), mat="steel", segs=8)
            p.cyl(0.04, 0.04, 0.11, T((-W * 0.08, 0.03, zs[0] + 0.025)), mat="paint", segs=8)
            if coin(p, 0.6):
                p.ball(0.03, T((W * 0.15, 0, zs[2] - 0.06)), mat="glow", segs=(6, 4))
                pole(p, (W * 0.15, 0, zs[2] - 0.03), (W * 0.15, 0, zs[2]), 0.004, mat="iron", segs=4)
    else:  # Ancient: arched stone niche wall
        zb = 0.12
        if slot == "top":
            for i in range(3):
                z = zb + 0.15 + (H - zb - 0.5) * i / 2
                slab(p, W * 0.78, D * 0.85, 0.05, z, y=-D * 0.05, mat="body", bevel=0.25)
        elif slot == "legs":
            slab(p, W * 1.05, D * 1.05, zb, 0, mat="stone_dark", bevel=0.2)
        elif slot == "frame":
            for x in (-W * 0.45, W * 0.45):
                p.box((W * 0.1, D, H - zb - 0.2), T((x, 0, zb + (H - zb - 0.2) / 2)), mat="body", bevel=0.15)
            slab(p, W * 0.9, 0.06, H - zb - 0.2, zb, y=D / 2 - 0.03, mat="stone_dark", bevel=0.1)
            pts = [(-W * 0.5, 0), (W * 0.5, 0), (W * 0.5, 0.12), (W * 0.3, 0.2 + J(p, 0.05, 0.4)), (-W * 0.3, 0.2 + J(p, 0.05, 0.4)), (-W * 0.5, 0.12)]
            p.plate(pts, D, T((0, 0, H - 0.2)), mat="body", bevel=0.2)
        else:
            for x in (-W * 0.45, W * 0.45):
                runes(p, x, -D / 2 - 0.004, zb + 0.1, H - 0.3, n=p.rng.choice((3, 4)), w=0.03)
            p.box((W * 0.5, 0.012, 0.02), T((0, -D / 2 - 0.004, H - 0.12)), mat="glow", bevel=0)
            if coin(p):
                p.ball(0.06, M(loc=(0, -0.02, zb + 0.2 + 0.06)), mat="gold", segs=(8, 5))


# ---------------------------------------------------------------- Stall
@function("Stall", "Furniture", FURN, "scene")
def stall(p, slot):
    e = p.era
    fh, fw, fd, fr = F(p, 1, 0.04), F(p, 1, 0.08), F(p, 1, 0.08), F(p, 1, 0.04)
    W, D = 1.6 * fw, 0.75 * fd
    C = 0.88 * fh  # counter surface
    R = 2.35 * fr  # roofline (back eave)
    Rf = R - 0.25  # front eave
    if e == "Primal":  # hide stall: log counter, crooked poles, hide roof
        C = 0.65 * fh
        if slot == "top":
            flagstone(p, W, D * 0.8, 0.012, C, mat="hide", n=8, rough=0.15, noise=0)
            for y in (-D * 0.25, D * 0.15):
                p.cyl(0.07, 0.07, W * 0.95, M(loc=(-W * 0.475, y, C - 0.07), rot=(0, 90, 0)), mat="bark", segs=7, noise=0.02)
        elif slot == "legs":
            for x in (-W * 0.35, W * 0.35):
                rock(p, J(p, 0.16), D * 0.4, (C - 0.13) / 2, (x, -0.05, (C - 0.13) / 2))
        elif slot == "frame":
            lean = J(p, 0.04, 0.5)
            for x, y in corners(W / 2, D / 2):
                top = Rf if y < 0 else R
                p.tube([(x, y, 0), (x + lean, y, top * 0.5), (x - lean * 0.5, y, top + 0.05)], 0.03, mat="wood", segs=5)
            for y, z in ((-D / 2, Rf), (D / 2, R)):
                pole(p, (-W / 2 - 0.08, y, z), (W / 2 + 0.08, y, z), 0.022, mat="wood", segs=5)
            ang = math.degrees(math.atan2(R - Rf, D))
            L = math.hypot(D, R - Rf) + 0.25
            p.plate([(-W / 2 - 0.2, -L / 2), (W / 2 + 0.2, -L / 2), (W / 2 + 0.1, L / 2), (0, L / 2 + 0.06), (-W / 2 - 0.1, L / 2)], 0.012,
                        M(loc=(0, 0, (R + Rf) / 2 + 0.03), rot=(ang, 0, 0)) @ M(rot=(90, 0, 0)), mat="hide", noise=0.01)
        else:
            for i in range(p.rng.randint(2, 3)):
                x = -W * 0.3 + i * W * 0.3
                pole(p, (x, -D / 2, Rf), (x, -D / 2, Rf - 0.35), 0.004, mat="rope", segs=4)
                p.box((J(p, 0.18), 0.01, J(p, 0.3)), T((x, -D / 2, Rf - 0.5)), mat="hide", bevel=0)
            pot(p, J(p, 0.08), J(p, 0.18), (W * 0.25, 0, C + 0.012), mat="bark")
            for i in range(3):
                p.ball(0.04, M(loc=(-W * 0.2 + i * 0.09, -0.05, C + 0.04), scale=(1, 1, 0.8)), mat="cloth", segs=(6, 4))
    elif e == "Agrarian":  # bamboo shed stall
        if slot == "top":
            n = 7
            for i in range(n):
                y = -D / 2 + D * (i + 0.5) / n
                p.cyl(D / n * 0.5, D / n * 0.5, W, M(loc=(-W / 2, y, C - D / n * 0.5), rot=(0, 90, 0)), mat="wood", segs=6)
        elif slot == "legs":
            for x, y in corners(W / 2 - 0.05, D / 2 - 0.05):
                p.cyl(0.03, 0.03, C - D / 7, T((x, y, 0)), mat="wood", segs=6)
            for y in (-D / 2 + 0.05, D / 2 - 0.05):
                pole(p, (-W / 2 + 0.05, y, J(p, 0.25, 0.2)), (W / 2 - 0.05, y, 0.25), 0.015, mat="wood")
        elif slot == "frame":
            for x, y in corners(W / 2, D / 2):
                top = Rf if y < 0 else R
                p.cyl(0.035, 0.032, top, T((x, y, 0)), mat="wood", segs=6)
                for z in (top * 0.33, top * 0.66):
                    p.ring(0.037, 0.006, T((x, y, z)), mat="wood_dark", segs=6)
            ang = math.degrees(math.atan2(R - Rf, D))
            L = math.hypot(D, R - Rf) + 0.35
            p.box((W + 0.35, L, 0.05), M(loc=(0, -0.08, (R + Rf) / 2 + 0.04), rot=(ang, 0, 0)), mat="rope", noise=0.02)
        else:
            p.lathe([(0, 0), (0.15, 0.005), (0.18, 0.1), (0.19, 0.11)], T((-W * 0.25, 0, C)), mat="rope", segs=10)
            for i in range(3):
                p.ball(0.05, T((-W * 0.25 + p.rng.uniform(-0.06, 0.06), p.rng.uniform(-0.06, 0.06), C + 0.1)), mat="paint", segs=(6, 4))
            for i in range(p.rng.randint(2, 4)):
                x = -W * 0.4 + i * W * 0.25
                pole(p, (x, -D / 2 - 0.03, Rf), (x, -D / 2 - 0.03, Rf - 0.2), 0.004, mat="rope", segs=4)
                p.lathe([(0, 0), (0.05, 0.04), (0.04, 0.12), (0.015, 0.16), (0, 0.17)], M(loc=(x, -D / 2 - 0.03, Rf - 0.2), rot=(180, 0, 0)), mat="ceramic" if i % 2 else "bark", segs=8)
    elif e == "Mercantile":  # cloth awning stall
        if slot == "top":
            slab(p, W + 0.06, D + 0.06, 0.04, C - 0.04, mat="wood_dark")
        elif slot == "legs":
            slab(p, W, 0.025, C - 0.06, 0.02, y=-D / 2 + 0.02, mat="wood_dark")
            for x in (-W / 2 + 0.03, W / 2 - 0.03):
                slab(p, 0.025, D - 0.04, C - 0.06, 0.02, x=x, mat="wood_dark", bevel=0)
            slab(p, W, D, 0.02, 0, mat="wood_dark", bevel=0)
            for x in (-W * 0.25, W * 0.25):
                p.box((W * 0.4, 0.01, (C - 0.06) * 0.6), T((x, -D / 2 + 0.002, C * 0.5)), mat="wood", bevel=0)
        elif slot == "frame":
            for x, y in corners(W / 2 + 0.02, D / 2):
                top = R if y > 0 else Rf
                post(p, x, y, C, top, 0.025, mat="wood_dark", bevel=0)
            n = 8
            ext = J(p, 0.3, 0.2)
            yf = -D / 2 - ext
            zf = Rf - 0.12
            ang = math.degrees(math.atan2(R - zf, D / 2 - yf))
            L = math.hypot(D / 2 - yf, R - zf)
            for i in range(n):
                x = -W / 2 - 0.04 + (W + 0.08) * (i + 0.5) / n
                p.box(((W + 0.08) / n, L, 0.012), M(loc=(x, (D / 2 + yf) / 2, (R + zf) / 2 + 0.02), rot=(ang, 0, 0)), mat="cloth" if i % 2 else "paint", bevel=0)
            for i in range(n):
                x = -W / 2 - 0.04 + (W + 0.08) * (i + 0.5) / n
                p.plate([(-(W + 0.08) / n / 2, 0), ((W + 0.08) / n / 2, 0), (0, -0.12)], 0.006, T((x, yf + 0.004, zf + 0.015)), mat="cloth" if i % 2 else "paint", bevel=0)
            pole(p, (-W / 2, yf, zf + 0.01), (W / 2, yf, zf + 0.01), 0.01, mat="wood_dark", segs=4)
            for x in (-W / 2 - 0.02, W / 2 + 0.02):
                pole(p, (x, -D / 2, Rf - 0.15), (x, yf, zf), 0.01, mat="wood_dark", segs=4)
        else:
            p.cyl(0.08, 0.08, 0.01, T((W * 0.3, 0, C + 0.18)), mat="brass", segs=8)
            p.cyl(0.008, 0.008, 0.18, T((W * 0.3 + 0.12, 0, C)), mat="brass", segs=6)
            pole(p, (W * 0.3, 0, C + 0.19), (W * 0.3 + 0.12, 0, C + 0.18), 0.004, mat="brass", segs=4)
            for i in range(p.rng.randint(2, 3)):
                slab(p, J(p, 0.22), J(p, 0.18), J(p, 0.12), C, x=-W * 0.35 + i * 0.25, y=p.rng.uniform(-0.1, 0.1), mat="wood")
            if coin(p):
                p.lathe([(0, 0), (0.05, 0.02), (0.06, 0.1), (0.03, 0.18), (0.035, 0.2)], T((W * 0.05, 0.1, C)), mat="glaze", segs=8)
    elif e == "Industrial":  # tin cart
        zw = 0.26
        if slot == "top":
            slab(p, W, D, 0.03, C - 0.03, mat="steel")
            for y in (-D / 2, D / 2):
                slab(p, W, 0.005, 0.06, C - 0.03, y=y, mat="steel", bevel=0)
        elif slot == "legs":
            for y in (-D / 2 - 0.04, D / 2 + 0.04):
                wheel(p, zw, (W * 0.22, y, zw), rim="rubber", hub="steel", spokes=6)
            pole(p, (W * 0.22, -D / 2 - 0.04, zw), (W * 0.22, D / 2 + 0.04, zw), 0.015, mat="steel")
            slab(p, W, D, C - 0.03 - zw - 0.05, zw + 0.05, mat="paint")
            for y in (-D * 0.4, D * 0.4):
                p.box((0.04, 0.04, zw + 0.05), T((-W * 0.42, y, (zw + 0.05) / 2)), mat="steel", bevel=0)
        elif slot == "frame":
            for x, y in corners(W / 2 - 0.02, D / 2 - 0.02):
                top = R if y > 0 else Rf
                p.cyl(0.012, 0.012, top - C, T((x, y, C)), mat="steel", segs=6)
            ang = math.degrees(math.atan2(R - Rf, D))
            L = math.hypot(D, R - Rf) + 0.2
            n = 9
            for i in range(n):
                x = -W / 2 - 0.05 + (W + 0.1) * (i + 0.5) / n
                p.box(((W + 0.1) / n * 0.55, L, 0.012), M(loc=(x, -0.06, (R + Rf) / 2 + 0.01 + (0.012 if i % 2 else 0)), rot=(ang, 0, 0)), mat="steel", bevel=0)
            p.box((W + 0.1, L, 0.004), M(loc=(0, -0.06, (R + Rf) / 2 + 0.008), rot=(ang, 0, 0)), mat="steel", bevel=0)
        else:
            p.tube([(W / 2, -D / 2 + 0.05, C - 0.08), (W / 2 + 0.25, -D / 2 + 0.05, C + 0.05), (W / 2 + 0.25, D / 2 - 0.05, C + 0.05), (W / 2, D / 2 - 0.05, C - 0.08)], 0.014, mat="steel", segs=6)
            p.box((W * 0.5, 0.006, 0.18), T((-W * 0.15, -D / 2 - 0.004, (C + zw) / 2 + 0.05)), mat="accent", bevel=0)
            for i in range(p.rng.randint(2, 3)):
                p.cyl(0.05, 0.05, J(p, 0.14), T((-W * 0.35 + i * 0.14, 0, C)), mat="paint" if i % 2 else "steel", segs=8)
    elif e == "Steampunk":  # brass cart with boiler and canopy
        zw = 0.34
        if slot == "top":
            slab(p, W, D, 0.04, C - 0.04, mat="wood_dark")
            for y in (-D / 2 + 0.01, D / 2 - 0.01):
                pole(p, (-W / 2, y, C + 0.06), (W / 2, y, C + 0.06), 0.008, mat="brass", segs=5)
                for x in (-W / 2, 0, W / 2):
                    p.cyl(0.006, 0.006, 0.06, T((x, y, C)), mat="brass", segs=4)
        elif slot == "legs":
            for y in (-D / 2 - 0.05, D / 2 + 0.05):
                wheel(p, zw, (W * 0.2, y, zw), rim="brass", hub="wood_dark", spokes=8)
            pole(p, (W * 0.2, -D / 2 - 0.05, zw), (W * 0.2, D / 2 + 0.05, zw), 0.018, mat="iron")
            for y in (-D * 0.4, D * 0.4):
                p.cyl(0.02, 0.02, zw + 0.02, T((-W * 0.42, y, 0)), mat="brass", segs=6)
            slab(p, W, D, C - 0.04 - zw - 0.02, zw + 0.02, mat="wood_dark")
            p.band(W * 0.5, (C + zw) / 2, m=M(scale=(1, D / W, 1)), h=0.05)
        elif slot == "frame":
            for x, y in corners(W / 2 - 0.03, D / 2 - 0.03):
                top = R if y > 0 else Rf
                p.cyl(0.018, 0.018, top - C, T((x, y, C)), mat="brass", segs=6)
            prof = []
            for i in range(6):
                a = math.pi * i / 5
                prof.append((math.cos(a) * (D / 2 + 0.12), Rf - 0.02 + math.sin(a) * J(p, 0.28, 0.15)))
            p.plate([(y, z) for y, z in prof], W + 0.12, M(loc=(0, 0, 0), rot=(0, 0, 90)), mat="copper", bevel=0)
        else:
            p.cyl(0.13, 0.13, 0.4, T((W * 0.32, D * 0.1, C)), mat="brass", segs=10)
            p.cyl(0.03, 0.04, 0.5, T((W * 0.32, D * 0.1, C + 0.4)), mat="iron", segs=6)
            p.cyl(0.05, 0.05, 0.01, M(loc=(W * 0.32, D * 0.1 - 0.13, C + 0.22), rot=(90, 0, 0)), mat="glow", segs=10)
            p.tube([(W * 0.32 - 0.13, D * 0.1, C + 0.3), (W * 0.05, D * 0.1, C + 0.35), (W * 0.0, D * 0.1, C + 0.05)], 0.012, mat="copper", segs=5)
            if coin(p):
                p.ball(0.05, T((-W * 0.45, -D / 2 - 0.02, Rf - 0.1)), mat="glow", segs=(6, 4))
                pole(p, (-W * 0.45, -D / 2 - 0.02, Rf - 0.05), (-W * 0.45, -D / 2 - 0.02, Rf + 0.04), 0.004, mat="brass", segs=4)
    elif e == "Future":  # holo stall: hover counter, arched spine canopy
        zb = 0.12
        if slot == "top":
            slab(p, W, D, 0.06, C - 0.06, mat="body", bevel=0.3, bevel_seg=1)
        elif slot == "legs":
            p.box((W * 0.9, D * 0.8, C - 0.06 - zb - 0.06), T((0, 0.02, zb + 0.06 + (C - 0.06 - zb - 0.06) / 2)), mat="body", bevel=0.25)
            slab(p, W * 0.7, D * 0.6, zb, 0, mat="shell_dark", bevel=0.3)
        elif slot == "frame":
            ys = D / 2 - 0.06
            pts = [(ys - 0.04, C - 0.02), (ys + 0.04, C - 0.02), (ys + 0.06, R - 0.2), (ys - 0.1, R), (-D / 2 - 0.3, Rf + 0.05),
                   (-D / 2 - 0.3, Rf - 0.02), (ys - 0.12, R - 0.08), (ys - 0.04, R - 0.25)]
            for x in (-W / 2 + 0.05, W / 2 - 0.05):
                p.plate([(y, z) for y, z in pts], 0.05, M(loc=(x, 0, 0), rot=(0, 0, 90)), mat="body", bevel=0)
            ang = math.degrees(math.atan2(R - Rf, D / 2 + 0.3 + ys))
            L = math.hypot(ys + D / 2 + 0.3, R - Rf)
            p.box((W, L, 0.03), M(loc=(0, (ys - D / 2 - 0.3) / 2, (R + Rf) / 2 + 0.03), rot=(ang, 0, 0)), mat="shell_dark", bevel=0.3, bevel_seg=1)
        else:
            p.box((W * 0.85, 0.006, 0.02), T((0, -D / 2 - 0.002, C - 0.03)), mat="glow", bevel=0)
            for i in range(p.rng.randint(2, 3)):
                x = -W * 0.3 + i * W * 0.3
                p.box((J(p, 0.3, 0.2), 0.004, J(p, 0.22, 0.2)), M(loc=(x, 0, C + 0.35), rot=(-10, 0, 0)), mat="glow", bevel=0)
                p.cyl(0.025, 0.035, 0.015, T((x, 0, C)), mat="shell_dark", segs=8)
            p.box((W * 0.9, 0.006, 0.015), T((0, -D / 2 - 0.29, Rf + 0.01)), mat="glow", bevel=0)
    elif e == "Wasteland":  # scrap stall: drums, door counter, tarp
        if slot == "top":
            slab(p, W, D, 0.04, C - 0.04, mat="wood", noise=0.005)
            p.box((J(p, 0.5), D * 0.6, 0.004), M(loc=(p.rng.uniform(-0.3, 0.3), 0, C + 0.002), rot=(0, 0, p.rng.uniform(-8, 8))), mat="rust", bevel=0)
        elif slot == "legs":
            for x in (-W * 0.33, W * 0.33):
                p.cyl(0.22, 0.22, C - 0.04, M(loc=(x, 0, 0), rot=(0, 0, p.rng.uniform(0, 90))), mat="paint" if x < 0 else "rust", segs=12)
                for z in (0.15, C - 0.15):
                    p.ring(0.222, 0.01, T((x, 0, z)), mat="iron", segs=12)
        elif slot == "frame":
            for x, y in corners(W / 2, D / 2):
                top = R if y > 0 else Rf
                p.cyl(0.02, 0.02, top - C, M(loc=(x, y, C), rot=(p.rng.uniform(-2, 2), p.rng.uniform(-2, 2), 0)), mat="iron" if coin(p) else "rust", segs=6)
            ang = math.degrees(math.atan2(R - Rf, D))
            L = math.hypot(D, R - Rf) + 0.2
            p.box((W * 0.55, L, 0.012), M(loc=(-W * 0.24, -0.06, (R + Rf) / 2 + 0.02), rot=(ang, 0, 0)), mat="cloth", bevel=0, noise=0.01)
            p.box((W * 0.55, L, 0.01), M(loc=(W * 0.24, -0.06, (R + Rf) / 2 + 0.025), rot=(ang, 3, 0)), mat="rust", bevel=0)
            p.box((W * 0.2, L * 0.9, 0.012), M(loc=(0, -0.06, (R + Rf) / 2 + 0.03), rot=(ang, 0, 0)), mat="steel", bevel=0)
        else:
            for i in range(p.rng.randint(3, 4)):
                x = -W * 0.4 + i * W * 0.27
                pole(p, (x, -D / 2, Rf), (x, -D / 2, Rf - 0.25), 0.003, mat="iron", segs=4)
                p.cyl(0.035, 0.035, 0.08, T((x, -D / 2, Rf - 0.33)), mat="steel" if i % 2 else "paint", segs=6)
            for x in (-W * 0.25, W * 0.2):
                p.ball(0.025, T((x, -D / 2 + 0.05, Rf - 0.03)), mat="glow", segs=(6, 4))
            if coin(p):
                p.cyl(0.18, 0.18, 0.07, M(loc=(0, -D / 2 - 0.04, C * 0.6), rot=(90, 0, 0)), mat="rubber", segs=12)
    else:  # Ancient: stone counter under a lintel
        if slot == "top":
            slab(p, W, D, 0.1, C - 0.1, mat="body")
        elif slot == "legs":
            p.box((W * 0.92, D * 0.85, C - 0.1), T((0, 0.02, (C - 0.1) / 2)), mat="body", bevel=0.1)
        elif slot == "frame":
            for x in (-W / 2 + 0.08, W / 2 - 0.08):
                p.box((0.16, 0.2, R - C), T((x, D * 0.25, (R + C) / 2)), mat="body", bevel=0.15)
            p.box((W + 0.3, 0.45 + J(p, 0.05, 0.6), 0.16), T((0, D * 0.12, R + 0.08)), mat="stone_dark", bevel=0.2)
        else:
            p.box((W * 0.8, 0.012, 0.02), T((0, -D / 2 - 0.003, C - 0.05)), mat="glow", bevel=0)
            for x in (-W / 2 + 0.08, W / 2 - 0.08):
                runes(p, x, D * 0.25 - 0.105, C + 0.2, R - 0.2, n=p.rng.choice((3, 4)), w=0.04)
            if coin(p):
                p.ball(0.07, T((0, 0.1, C + 0.07)), mat="gold", segs=(8, 5))
            else:
                p.box((0.3, 0.01, 0.05), T((0, D * 0.12 - 0.24, R + 0.08)), mat="gold", bevel=0)


# ---------------------------------------------------------------- Workbench
@function("Workbench", "Furniture", FURN, "scene")
def workbench(p, slot):
    e = p.era
    fh, fw, fd = F(p, 1, 0.04), F(p, 1, 0.1), F(p, 1, 0.08)
    h0, w0, d0, t = {"Primal": (0.62, 1.3, 0.55, 0.16), "Agrarian": (0.84, 1.5, 0.6, 0.08),
                     "Mercantile": (0.86, 1.5, 0.62, 0.07), "Industrial": (0.88, 1.5, 0.7, 0.04),
                     "Steampunk": (0.88, 1.4, 0.7, 0.06), "Future": (0.9, 1.4, 0.7, 0.06),
                     "Wasteland": (0.85, 1.5, 0.65, 0.05), "Ancient": (0.86, 1.4, 0.65, 0.12)}[e]
    H, W, D = h0 * fh, w0 * fw, d0 * fd
    u = H - t
    if e == "Primal":  # split log on stumps
        if slot == "top":
            prof = [(-D / 2, 0), (D / 2, 0), (D * 0.45, -t * 0.6), (D * 0.25, -t), (-D * 0.25, -t), (-D * 0.45, -t * 0.6)]
            p.plate(prof, W, M(loc=(0, 0, H), rot=(0, 0, 90)), mat="bark", noise=0.02)
            slab(p, W * 0.98, D * 0.96, 0.005, H - 0.004, mat="wood", bevel=0)
        elif slot == "legs":
            for x in (-W * 0.33, W * 0.33):
                p.cyl(J(p, 0.15, 0.12), 0.14, u + 0.02, T((x, 0, 0)), mat="bark", segs=8, noise=0.03)
        elif slot == "frame":
            for x in (-W * 0.33, W * 0.33):
                p.box((0.08, D * 0.3, 0.05), M(loc=(x + 0.12, -D * 0.25, u + 0.01), rot=(0, 20, p.rng.uniform(-20, 20))), mat="wood")
            if coin(p):
                rock(p, 0.1, 0.1, 0.07, (W * 0.1, 0.1, 0.06))
        else:
            rock(p, J(p, 0.05), 0.045, 0.04, (-W * 0.25, 0.05, H + 0.035), noise=0.06, segs=(6, 4))
            for i in range(p.rng.randint(2, 3)):
                p.plate([(0, 0), (0.04, 0.005), (0.02, 0.05)], 0.012, M(loc=(W * 0.1 + i * 0.08, -0.1, H + 0.006), rot=(-90, 0, p.rng.uniform(0, 180))), mat="stone_dark", bevel=0)
            pole(p, (W * 0.25, 0.05, H + 0.015), (W * 0.42, 0.12, H + 0.02), 0.014, mat="bone")
    elif e == "Agrarian":  # carpenter's bench
        ix, iy = W / 2 - 0.12, D / 2 - 0.08
        if slot == "top":
            for i in range(2):
                pd = D / 2
                slab(p, W, pd - 0.006, t, u, y=-D / 2 + pd * (i + 0.5), mat="wood", noise=0.003)
            for k in range(3):
                p.box((0.025, 0.025, 0.004), T((-W / 2 + 0.2 + k * 0.08, -D / 2 + 0.06, H + 0.001)), mat="wood_dark", bevel=0)
        elif slot == "legs":
            s = J(p, 0.045, 0.1)
            for x, y in corners(ix, iy):
                post(p, x, y, 0, u, s, mat="wood")
            for x in (-ix, ix):
                slab(p, 0.07, iy * 2 + 0.12, 0.07, 0.0, x=x, mat="wood")
        elif slot == "frame":
            z = J(p, 0.2, 0.15)
            for y in (-iy, iy):
                slab(p, ix * 2, 0.04, 0.08, z, y=y, mat="wood", bevel=0)
            slab(p, ix * 2, iy * 2, 0.02, z + 0.08, mat="wood", bevel=0)
            for y in (-iy, iy):
                slab(p, ix * 2, 0.03, 0.08, u - 0.08, y=y, mat="wood", bevel=0)
        else:
            p.box((0.06, D * 0.3, 0.06), T((-W / 2 + 0.03, -D / 2 + D * 0.15, H + 0.03)), mat="wood_dark")
            p.box((J(p, 0.22), 0.06, 0.05), M(loc=(p.rng.uniform(-0.1, 0.3), 0.05, H + 0.025), rot=(0, 0, p.rng.uniform(-20, 20))), mat="wood_dark")
            if coin(p):
                p.cyl(0.04, 0.04, 0.12, M(loc=(W * 0.35, -0.05, H + 0.04), rot=(0, 90, 0)), mat="wood", segs=8)
                pole(p, (W * 0.35 + 0.06, -0.05, H + 0.04), (W * 0.35 + 0.28, -0.05, H + 0.04), 0.012, mat="wood")
    elif e == "Mercantile":  # bench with a wooden screw vise and drawers
        ix, iy = W / 2 - 0.08, D / 2 - 0.06
        if slot == "top":
            slab(p, W, D, t, u, mat="wood_dark")
        elif slot == "legs":
            for x, y in corners(ix, iy):
                post(p, x, y, 0, u, J(p, 0.04, 0.1), mat="wood_dark", bevel=0)
        elif slot == "frame":
            dw = J(p, 0.5, 0.15)
            slab(p, dw, D - 0.1, 0.2, u - 0.2, x=ix - dw / 2, mat="wood_dark")
            for k in range(2):
                p.box((dw - 0.04, 0.01, 0.08), T((ix - dw / 2, -D / 2 + 0.045, u - 0.055 - k * 0.095)), mat="wood", bevel=0)
            slab(p, ix * 2, iy * 2, 0.025, 0.15, mat="wood_dark", bevel=0)
        else:
            vx = -W / 2 + 0.18
            p.box((0.24, 0.05, 0.2), T((vx, -D / 2 - 0.03, H - 0.09)), mat="wood_dark")
            p.cyl(0.02, 0.02, 0.18, M(loc=(vx, -D / 2 - 0.05, H - 0.08), rot=(90, 0, 0)), mat="iron", segs=8)
            p.cyl(0.008, 0.008, J(p, 0.2, 0.2), M(loc=(vx - 0.1, -D / 2 - 0.2, H - 0.08), rot=(0, 90, 0)), mat="wood", segs=6)
            for k in range(2):
                p.ball(0.012, T((ix - 0.25, -D / 2 + 0.035, u - 0.055 - k * 0.095)), mat="brass", segs=(6, 4))
            if coin(p):
                slab(p, 0.3, 0.1, 0.08, H, x=W * 0.1, y=D * 0.3, mat="wood")
    elif e == "Industrial":  # steel bench, lower shelf, pegboard
        ix, iy = W / 2 - 0.03, D / 2 - 0.03
        if slot == "top":
            slab(p, W, D, t, u, mat="steel")
            slab(p, W, 0.006, t + 0.03, u - 0.03, y=-D / 2, mat="steel", bevel=0)
        elif slot == "legs":
            a = J(p, 0.05, 0.12)
            for x, y in corners(ix, iy):
                sx, sy = math.copysign(1, x), math.copysign(1, y)
                p.box((a, 0.006, u), T((x - sx * a / 2, y, u / 2)), mat="paint", bevel=0)
                p.box((0.006, a, u), T((x, y - sy * a / 2, u / 2)), mat="paint", bevel=0)
        elif slot == "frame":
            slab(p, W - 0.02, D - 0.02, 0.02, J(p, 0.16, 0.2), mat="steel", bevel=0)
            ph = J(p, 0.6, 0.15)
            slab(p, W - 0.04, 0.012, ph, H, y=D / 2 - 0.01, mat="steel", bevel=0)
            for x in (-ix, ix):
                slab(p, 0.03, 0.03, ph, H, x=x, y=D / 2 - 0.02, mat="paint", bevel=0)
        else:
            vx = W / 2 - 0.2
            slab(p, 0.12, 0.16, 0.06, H, x=vx, y=-D / 2 + 0.06, mat="paint", bevel=0.1)
            p.box((0.14, 0.03, 0.08), T((vx, -D / 2 - 0.005, H + 0.07)), mat="steel", bevel=0)
            p.cyl(0.006, 0.006, 0.18, M(loc=(vx - 0.09, -D / 2 - 0.03, H + 0.05), rot=(0, 90, 0)), mat="steel", segs=6)
            for i in range(p.rng.randint(2, 4)):
                x = -W * 0.4 + i * 0.18
                p.box((0.015, 0.02, J(p, 0.2)), T((x, D / 2 - 0.03, H + 0.25)), mat="steel" if i % 2 else "rubber", bevel=0)
    elif e == "Steampunk":  # gear bench with a magnifier lamp
        ix, iy = W / 2 - 0.08, D / 2 - 0.08
        if slot == "top":
            slab(p, W, D, t, u, mat="wood_dark")
            for y in (-D / 2, D / 2):
                slab(p, W + 0.01, 0.008, t + 0.01, u - 0.005, y=y, mat="brass", bevel=0)
        elif slot == "legs":
            for x, y in corners(ix, iy):
                p.cyl(0.03, 0.025, u, T((x, y, 0)), mat="brass", segs=8)
                p.ball(0.04, T((x, y, 0.03)), mat="brass", segs=(6, 4))
        elif slot == "frame":
            ph = J(p, 0.55, 0.1)
            slab(p, W - 0.1, 0.02, ph, H, y=D / 2 - 0.02, mat="wood_dark")
            for x, z, r in ((-W * 0.25, H + ph * 0.5, 0.16), (-W * 0.25 + 0.25, H + ph * 0.4, 0.11), (W * 0.15, H + ph * 0.6, 0.13)):
                gear(p, r, T((x, D / 2 - 0.04, z)), teeth=8, th=0.012)
            p.box((W * 0.7, 0.03, 0.04), T((0, 0, 0.2)), mat="brass", bevel=0)
        else:
            lx = W / 2 - 0.15
            p.tube([(lx, D / 2 - 0.08, H), (lx, D / 2 - 0.08, H + 0.35), (lx - 0.05, -0.05, H + 0.45), (lx - 0.1, -0.15, H + 0.35)], 0.01, mat="brass", segs=5)
            p.ring(0.06, 0.008, M(loc=(lx - 0.1, -0.15, H + 0.32), rot=(40, 0, 0)), mat="brass", segs=10)
            p.cyl(0.055, 0.055, 0.004, M(loc=(lx - 0.1, -0.15, H + 0.32), rot=(40, 0, 0)), mat="glass", segs=10)
            p.ball(0.02, T((lx - 0.08, -0.13, H + 0.4)), mat="glow", segs=(6, 4))
            if coin(p):
                gear(p, 0.06, M(loc=(-W * 0.1, -0.1, H + 0.006), rot=(90, 0, 0)), teeth=6, th=0.01)
    elif e == "Future":  # fabrication platform under a gantry
        if slot == "top":
            slab(p, W, D, t, u, mat="body", bevel=0.3, bevel_seg=1)
            slab(p, W * 0.6, D * 0.6, 0.004, H, mat="shell_dark", bevel=0)
        elif slot == "legs":
            p.box((W * 0.85, D * 0.75, u - 0.08), T((0, 0.03, 0.08 + (u - 0.08) / 2)), mat="body", bevel=0.2)
            slab(p, W * 0.7, D * 0.55, 0.08, 0, y=0.03, mat="shell_dark", bevel=0.3)
        elif slot == "frame":
            gh = J(p, 0.55, 0.1)
            for x in (-W * 0.36, W * 0.36):
                p.box((0.06, 0.08, gh), T((x, D * 0.32, H + gh / 2)), mat="body", bevel=0.25, bevel_seg=1)
            p.box((W * 0.78, 0.08, 0.06), T((0, D * 0.32, H + gh)), mat="body", bevel=0.25, bevel_seg=1)
            p.box((0.12, 0.3, 0.07), T((J(p, 0.1, 1), D * 0.32 - 0.15, H + gh - 0.02)), mat="shell_dark", bevel=0.2, bevel_seg=1)
            p.cyl(0.02, 0.0, 0.06, M(loc=(J(p, 0.1, 1), D * 0.32 - 0.25, H + gh - 0.06), rot=(180, 0, 0)), mat="glow", segs=8)
        else:
            for k in range(-2, 3):
                p.box((W * 0.6, 0.004, 0.002), T((0, k * D * 0.12, H + 0.005)), mat="glow", bevel=0)
            p.box((W * 0.8, 0.006, 0.015), T((0, -D / 2 - 0.002, u + t / 2)), mat="glow", bevel=0)
            if coin(p):
                p.box((0.1, 0.1, 0.06), M(loc=(p.rng.uniform(-0.2, 0.2), 0, H + 0.035), rot=(0, 0, 30)), mat="paint", bevel=0.2, bevel_seg=1)
    elif e == "Wasteland":  # old door on a drum and a sawhorse
        if slot == "top":
            slab(p, W, D, t, u, mat="wood", noise=0.005)
            p.box((J(p, 0.4), D * 0.5, 0.004), M(loc=(p.rng.uniform(-0.3, 0.3), 0, H + 0.002), rot=(0, 0, p.rng.uniform(-10, 10))), mat="steel", bevel=0)
        elif slot == "legs":
            p.cyl(0.2, 0.2, u, T((-W / 2 + 0.25, 0, 0)), mat="rust", segs=12)
            x = W / 2 - 0.15
            sp = J(p, 0.2, 0.15)
            for y in (-sp, sp):
                pole(p, (x - 0.12, y, 0), (x, y * 0.3, u - 0.06), 0.022, mat="wood", segs=4)
                pole(p, (x + 0.12, y, 0), (x, y * 0.3, u - 0.06), 0.022, mat="wood", segs=4)
            slab(p, 0.08, D * 0.8, 0.06, u - 0.06, x=x, mat="wood", bevel=0)
        elif slot == "frame":
            for z in (0.15, u - 0.12):
                p.ring(0.202, 0.01, T((-W / 2 + 0.25, 0, z)), mat="iron", segs=12)
            p.tube([(-W / 2 + 0.45, -D * 0.3, 0.3), (W / 2 - 0.2, -D * 0.2, J(p, 0.32, 0.15))], 0.012, mat="iron", segs=6)
            p.box((0.5, 0.012, 0.35), M(loc=(-0.1, D / 2 - 0.02, H + 0.17), rot=(0, p.rng.uniform(-5, 5), 0)), mat="rust", bevel=0)
        else:
            vx = W / 2 - 0.25
            p.box((0.1, 0.14, 0.08), T((vx, -D / 2 + 0.07, H + 0.04)), mat="iron", bevel=0.05)
            p.box((0.12, 0.03, 0.06), T((vx, -D / 2 - 0.01, H + 0.09)), mat="rust", bevel=0)
            p.band(0.03, 0, m=M(loc=(vx, -D / 2 + 0.07, H + 0.04), rot=(0, 90, 0)), h=0.05)
            if coin(p, 0.6):
                p.tube([(-0.2, D / 2 - 0.05, H), (-0.2, D / 2 - 0.05, H + 0.45), (-0.05, D * 0.1, H + 0.4)], 0.006, mat="iron", segs=4)
                p.ball(0.028, T((-0.05, D * 0.1, H + 0.37)), mat="glow", segs=(6, 4))
    else:  # Ancient: stone bench with a rune back panel
        if slot == "top":
            slab(p, W, D, t, u, mat="body")
        elif slot == "legs":
            for x in (-W * 0.36, W * 0.36):
                p.box((W * 0.18, D * J(p, 0.8, 0.06), u), T((x, 0, u / 2)), mat="body", bevel=0.12)
        elif slot == "frame":
            bh = J(p, 0.45, 0.12)
            pts = [(-W * 0.45, 0), (W * 0.45, 0), (W * 0.45, bh * 0.75), (W * 0.3, bh), (-W * 0.3, bh), (-W * 0.45, bh * 0.75)]
            p.plate(pts, 0.1, T((0, D / 2 - 0.05, H)), mat="body", bevel=0.2)
            slab(p, W * 0.5, D * 0.4, 0.1, 0, mat="stone_dark", bevel=0.15)
        else:
            for i in range(5):
                p.box((0.035 if i % 2 else 0.06, 0.012, 0.05), T((-W * 0.24 + i * W * 0.12, D / 2 - 0.105, H + 0.17)), mat="glow", bevel=0)
            for x in (-W * 0.36, W * 0.36):
                runes(p, x, -D * 0.4 - 0.004, u * 0.2, u * 0.85, n=2)
            if coin(p):
                p.ball(0.045, M(loc=(W * 0.2, -0.05, H + 0.03), scale=(1, 1, 0.6)), mat="gold", segs=(8, 4))


# ---------------------------------------------------------------- Signboard
@function("Signboard", "Furniture", FURN, "scene")
def signboard(p, slot):
    e = p.era
    fh, fw, fs = F(p, 1, 0.05), F(p, 1, 0.1), F(p, 1, 0.08)
    Hp = 2.2 * fh  # post / pole height
    Sw, Sh = 0.7 * fw, 0.42 * fs  # sign face
    if e == "Primal":  # totem banner
        Hp = 2.3 * fh
        zb = Hp - 0.25  # crossbar
        if slot == "top":
            pts = [(-Sw * 0.4, 0), (Sw * 0.4, 0), (Sw * 0.42, -Sh * 1.6), (Sw * 0.15, -Sh * J(p, 1.9, 0.08)), (0, -Sh * 1.7),
                   (-Sw * 0.15, -Sh * J(p, 1.9, 0.08)), (-Sw * 0.42, -Sh * 1.6)]
            p.plate(pts, 0.012, T((0, -0.06, zb - 0.02)), mat="hide", noise=0.01)
        elif slot == "legs":
            p.tube([(0, 0, 0), (J(p, 0.02, 1), 0.01, Hp * 0.5), (0, 0, Hp)], 0.045, mat="wood", segs=6)
            for i in range(5):
                a = i * math.tau / 5 + p.rng.uniform(-0.2, 0.2)
                rock(p, 0.12, 0.1, 0.09, (math.cos(a) * 0.15, math.sin(a) * 0.15, 0.06), noise=0.05, segs=(6, 4))
        elif slot == "frame":
            pole(p, (-Sw * 0.5, -0.06, zb), (Sw * 0.5, -0.06, zb), 0.02, mat="wood", segs=5)
            p.band(0.05, zb, h=0.06)
            p.lathe([(0.05, Hp - 0.02), (J(p, 0.09, 0.15), Hp + 0.06), (0.07, Hp + 0.16), (0.08, Hp + 0.22), (0, Hp + 0.26)], mat="wood_dark", segs=7)
            for s in (-1, 1):
                p.tube([(s * 0.06, 0, Hp + 0.18), (s * 0.18, 0, Hp + 0.3), (s * 0.22, 0, Hp + 0.45)], 0.014, mat="bone", segs=5)
        else:
            for x in (-Sw * 0.5, Sw * 0.5):
                pole(p, (x, -0.06, zb), (x, -0.06, zb - J(p, 0.25)), 0.003, mat="rope", segs=4)
                p.cyl(0.015, 0.0, J(p, 0.16, 0.15), M(loc=(x, -0.06, zb - 0.25), rot=(180, 0, 0)), mat="feather", segs=5)
            for i in range(3):
                p.ball(0.018, T((-0.08 + i * 0.08, -0.075, zb - Sh * 0.8)), mat="accent" if i % 2 else "bone", segs=(5, 3))
    elif e == "Agrarian":  # wooden sign on two posts
        zs = Hp * 0.55
        px = Sw * 0.5 + 0.04
        if slot == "top":
            for k in range(2):
                slab(p, Sw, 0.03, Sh / 2 - 0.006, zs + k * Sh / 2, mat="wood", noise=0.004)
        elif slot == "legs":
            for x in (-px, px):
                post(p, x, 0, 0, zs + Sh + 0.15, J(p, 0.035, 0.1), mat="wood")
        elif slot == "frame":
            ang = J(p, 28, 0.2)
            for s in (-1, 1):
                p.box((Sw / 2 + 0.16, 0.1, 0.02), M(loc=(s * (Sw / 4 + 0.05), 0, zs + Sh + 0.18), rot=(0, s * ang, 0)), mat="wood_dark")
            pole(p, (-px, 0.0, zs - 0.06), (px, 0.0, zs - 0.06), 0.02, mat="wood", segs=4)
        else:
            p.ball(0.07, M(loc=(0, -0.02, zs + Sh / 2), scale=(1, 0.2, 1)), mat="paint", segs=(8, 4))
            if coin(p):
                p.plate([(-0.04, 0), (0.04, 0), (0.0, 0.1)], 0.006, T((0, -0.035, zs + Sh / 2 - 0.05)), mat="wood_dark", bevel=0)
            else:
                for x in (-Sw * 0.35, Sw * 0.35):
                    p.ball(0.012, T((x, -0.018, zs + Sh / 2)), mat="iron", segs=(5, 3))
            p.ring(0.04, 0.005, M(loc=(px, -0.04, zs + Sh * 0.3), rot=(90, 0, 0)), mat="rope", segs=8, square=False)
    elif e == "Mercantile":  # hanging iron sign from a post bracket
        arm = Sw + 0.2
        za = Hp - 0.1
        if slot == "top":
            prof = [(-Sw / 2, 0), (Sw / 2, 0), (Sw / 2, -Sh * 0.8), (Sw * 0.3, -Sh), (-Sw * 0.3, -Sh), (-Sw / 2, -Sh * 0.8)]
            p.plate(prof, 0.025, T((-0.12 - arm / 2, 0, za - 0.12)), mat="wood_dark")
        elif slot == "legs":
            post(p, 0, 0, 0, Hp + 0.05, 0.05, mat="wood_dark")
            slab(p, 0.18, 0.18, 0.05, 0, mat="stone", bevel=0.2)
        elif slot == "frame":
            pole(p, (0, 0, za), (-arm - 0.1, 0, za), 0.012, mat="iron", segs=4)
            p.tube([(-0.05, 0, za - 0.35), (-0.2, 0, za - 0.2), (-0.32, 0, za - 0.02)], 0.01, mat="iron", segs=4)
            sc = J(p, 0.07, 0.25)
            pts = [(-0.2 - sc * math.cos(a * 0.6), 0, za - 0.12 + sc * math.sin(a * 0.6)) for a in range(0, 11)]
            p.tube(pts, 0.006, mat="iron", segs=4)
            p.ball(0.02, T((-arm - 0.1, 0, za)), mat="iron", segs=(6, 4))
        else:
            for x in (-0.12 - arm / 2 - Sw * 0.4, -0.12 - arm / 2 + Sw * 0.4):
                pole(p, (x, 0, za), (x, 0, za - 0.12), 0.005, mat="iron", segs=4)
            p.cyl(J(p, 0.11, 0.15), J(p, 0.11, 0.15), 0.01, M(loc=(-0.12 - arm / 2, -0.016, za - 0.12 - Sh * 0.5), rot=(90, 0, 0)), mat="brass", segs=12)
            if coin(p):
                p.ring(0.12, 0.006, M(loc=(-0.12 - arm / 2, -0.018, za - 0.12 - Sh * 0.5), rot=(90, 0, 0)), mat="brass", segs=12, square=False)
    elif e == "Industrial":  # neon sign box on a steel pole
        zs = Hp - Sh - 0.1
        if slot == "top":
            slab(p, Sw + 0.2, 0.12, Sh, zs, mat="paint", bevel=0.05)
        elif slot == "legs":
            p.cyl(0.04, 0.04, zs, T((0, 0, 0)), mat="steel", segs=8)
            p.cyl(0.15, 0.15, 0.03, mat="steel", segs=8)
        elif slot == "frame":
            slab(p, Sw + 0.24, 0.13, 0.03, zs - 0.03, mat="steel", bevel=0)
            slab(p, Sw + 0.24, 0.13, 0.03, zs + Sh, mat="steel", bevel=0)
            for x in (-(Sw + 0.24) / 2, (Sw + 0.24) / 2):
                slab(p, 0.02, 0.13, Sh, zs, x=x, mat="steel", bevel=0)
            if coin(p):
                pole(p, (0, 0, zs + Sh + 0.03), (0, 0, zs + Sh + J(p, 0.2, 0.3)), 0.006, mat="steel", segs=4)
        else:  # neon: the catalogue calls for lit tubes in this era
            yy = -0.065
            z0 = zs + Sh * 0.25
            pts = [(-Sw * 0.4 + i * Sw * 0.1, yy, z0 + (Sh * 0.5 if i % 2 else 0)) for i in range(9)]
            p.tube(pts, 0.008, mat="glow_amber", segs=4)
            p.tube([(-Sw * 0.45, yy, zs + Sh * 0.85), (Sw * J(p, 0.45, 0.1), yy, zs + Sh * 0.85)], 0.006, mat="glow_amber", segs=4)
    elif e == "Steampunk":  # gear-driven flip sign
        zs = Hp - Sh - 0.2
        if slot == "top":
            n = 5
            for i in range(n):
                p.box((Sw, 0.03, Sh / n * 0.95), M(loc=(0, 0, zs + Sh / n * (i + 0.5)), rot=(J(p, 8, 1) * (1 if i % 2 else -1), 0, 0)), mat="wood_dark" if i % 2 else "paint", bevel=0)
        elif slot == "legs":
            p.cyl(0.04, 0.035, zs, T((0, 0.06, 0)), mat="brass", segs=8)
            p.lathe([(0.18, 0), (0.17, 0.04), (0.08, 0.1), (0.045, 0.2)], T((0, 0.06, 0)), mat="brass", segs=8)
        elif slot == "frame":
            for x in (-Sw / 2 - 0.03, Sw / 2 + 0.03):
                slab(p, 0.03, 0.05, Sh + 0.1, zs - 0.05, x=x, mat="brass", bevel=0)
            slab(p, Sw + 0.09, 0.05, 0.03, zs + Sh + 0.05, mat="brass", bevel=0)
            gear(p, J(p, 0.12, 0.15), T((Sw / 2 + 0.03, -0.04, zs + Sh + 0.08)), teeth=8, th=0.012)
        else:
            gear(p, 0.07, T((Sw / 2 - 0.08, -0.04, zs + Sh + 0.16)), teeth=6, th=0.01)
            for x in (-Sw / 2 - 0.03, Sw / 2 + 0.03):
                p.ball(0.025, T((x, -0.03, zs + Sh + 0.12)), mat="glow", segs=(6, 4))
            if coin(p):
                p.tube([(-Sw / 2 - 0.03, -0.03, zs - 0.05), (-Sw / 2 - 0.1, -0.03, zs - 0.15), (-Sw / 2 - 0.1, -0.03, zs - 0.3)], 0.008, mat="copper", segs=4)
    elif e == "Future":  # holo sign over a slim pylon
        zs = Hp - Sh - 0.05
        if slot == "top":
            p.box((Sw * J(p, 0.97, 0.03), 0.006, Sh), T((0, 0, zs + Sh / 2)), mat="glow", bevel=0)
            for i in range(p.rng.randint(1, 3)):
                p.box((Sw * J(p, 0.6, 0.3), 0.002, 0.008), T((0, -0.004, zs + Sh * (0.25 + i * 0.25))), mat="shell", bevel=0)
        elif slot == "legs":
            p.lathe([(0, 0), (0.18, 0), (0.17, 0.03), (0.06, 0.06), (J(p, 0.045, 0.2), zs * 0.5), (0.04, zs - 0.08), (0.08, zs - 0.06), (0, zs - 0.04)], mat="body", segs=12)
        elif slot == "frame":
            pts = [(-Sw / 2 - 0.05, -0.08), (Sw / 2 + 0.05, -0.08), (Sw / 2 + 0.05, 0), (Sw / 2, 0), (Sw / 2, -0.04), (-Sw / 2, -0.04), (-Sw / 2, 0), (-Sw / 2 - 0.05, 0)]
            p.plate(pts, 0.05, T((0, 0, zs)), mat="shell_dark", bevel=0)
            p.box((Sw + 0.1, 0.05, 0.03), T((0, 0, zs + Sh + 0.02)), mat="shell_dark", bevel=0.3, bevel_seg=1)
        else:
            for i in range(p.rng.randint(2, 3)):
                p.box((J(p, 0.22, 0.3), 0.004, 0.035), T((-Sw * 0.2 + i * 0.12, -0.006, zs + Sh * (0.3 + i * 0.2))), mat="shell", bevel=0)
            p.ring(0.08, 0.005, M(loc=(Sw * 0.3, -0.006, zs + Sh * 0.6), rot=(90, 0, 0)), mat="shell", segs=10)
    elif e == "Wasteland":  # scrap sheet on a pipe in a tyre
        zs = Hp - Sh - 0.15
        if slot == "top":
            pts = [(-Sw / 2, 0), (Sw / 2, J(p, 0.03, 1)), (Sw / 2 - 0.03, Sh), (-Sw / 2 + 0.05, Sh - 0.02)]
            p.plate(pts, 0.008, M(loc=(0, -0.05, zs), rot=(0, p.rng.uniform(-4, 4), 0)), mat="rust", bevel=0)
            p.box((Sw * 0.5, 0.004, Sh * 0.3), M(loc=(0, -0.056, zs + Sh * 0.5), rot=(0, -6, 0)), mat="paint", bevel=0)
        elif slot == "legs":
            p.cyl(0.03, 0.03, Hp, T((0, 0, 0)), mat="iron", segs=6)
            p.ring(0.24, 0.1, T((0, 0, 0.1)), mat="rubber", segs=12, square=True)
            p.cyl(0.18, 0.18, 0.16, T((0, 0, 0.02)), mat="stone_dark", segs=8)
        elif slot == "frame":
            pole(p, (-Sw / 2 - 0.05, -0.03, zs + Sh + 0.05), (Sw / 2 + 0.05, -0.03, zs + Sh + 0.05), 0.012, mat="rust")
            p.band(0.03, zs + Sh + 0.05, h=0.05)
            for x in (-Sw * 0.4, Sw * 0.4):
                pole(p, (x, -0.04, zs + Sh + 0.05), (x, -0.05, zs + Sh - 0.03), 0.003, mat="iron", segs=4)
        else:
            p.cyl(0.11, 0.09, 0.02, M(loc=(J(p, 0.12, 0.5), -0.06, zs + Sh * 0.5), rot=(90, 0, 0)), mat="steel", segs=10)
            for x in (-Sw * 0.45, 0, Sw * 0.45):
                if coin(p, 0.7):
                    p.ball(0.025, T((x, -0.045, zs + Sh + 0.02)), mat="glow", segs=(6, 4))
    else:  # Ancient: stele with a rune tablet under a stone gate
        zs = Hp - Sh - 0.15
        if slot == "top":
            slab(p, Sw, 0.1, Sh, zs, mat="stone_dark", bevel=0.15)
        elif slot == "legs":
            p.box((0.22, 0.2, zs), T((0, 0, zs / 2)), mat="body", bevel=0.15)
            slab(p, 0.5, 0.4, 0.12, 0, mat="stone_dark", bevel=0.2)
        elif slot == "frame":
            for x in (-Sw / 2 - 0.05, Sw / 2 + 0.05):
                slab(p, 0.1, 0.14, Sh + 0.05, zs - 0.05, x=x, mat="body", bevel=0.2)
            pts = [(-Sw / 2 - 0.12, 0), (Sw / 2 + 0.12, 0), (Sw / 2 + 0.05, 0.12), (0, 0.16 + J(p, 0.04, 0.5)), (-Sw / 2 - 0.05, 0.12)]
            p.plate(pts, 0.16, T((0, 0, zs + Sh)), mat="body", bevel=0.2)
        else:
            for i in range(4):
                p.box((0.05 if i % 2 else 0.08, 0.012, 0.05), T((-Sw * 0.3 + i * Sw * 0.2, -0.055, zs + Sh * 0.5 + (0.06 if i % 2 else -0.04))), mat="glow", bevel=0)
            if coin(p):
                p.ball(0.04, T((0, -0.07, zs + Sh + 0.08)), mat="gold", segs=(6, 4))
            runes(p, 0, -0.105, zs * 0.3, zs * 0.85, n=2, w=0.04)


# ---------------------------------------------------------------- Altar
@function("Altar", "Furniture", FURN, "scene")
def altar(p, slot):
    e = p.era
    fh, fw, fd, fb = F(p, 1, 0.04), F(p, 1, 0.08), F(p, 1, 0.08), F(p, 1, 0.08)
    h0, w0, d0, t = {"Primal": (0.85, 1.4, 0.85, 0.16), "Agrarian": (0.82, 1.2, 0.6, 0.05),
                     "Mercantile": (0.95, 1.2, 0.65, 0.1), "Industrial": (0.92, 1.2, 0.6, 0.05),
                     "Steampunk": (0.92, 1.1, 0.65, 0.06), "Future": (0.95, 0.9, 0.9, 0.08),
                     "Wasteland": (0.9, 1.1, 0.6, 0.04), "Ancient": (0.95, 1.3, 0.75, 0.14)}[e]
    H, W, D = h0 * fh, w0 * fw, d0 * fd
    u = H - t
    Bk = 1.55 * fb  # back piece top (stays under a person's height)
    if e == "Primal":  # megalith table (dolmen)
        if slot == "top":
            flagstone(p, W, D, t, u, rough=0.15, noise=0.03)
        elif slot == "legs":
            for x in (-W * 0.3, W * 0.3):
                p.box((J(p, 0.22, 0.12), D * 0.7, u + 0.03), M(loc=(x, 0, (u + 0.03) / 2), rot=(0, p.rng.uniform(-3, 3), p.rng.uniform(-6, 6))), mat="stone", noise=0.04)
            if coin(p):
                p.box((W * 0.45, 0.2, u * 0.85), M(loc=(0, D * 0.3, u * 0.42), rot=(0, 0, p.rng.uniform(-4, 4))), mat="stone_dark", noise=0.04)
        elif slot == "frame":  # ring of standing pebbles
            n = 7
            for i in range(n):
                a = math.pi * (0.1 + 0.8 * i / (n - 1))
                rock(p, 0.08, 0.07, J(p, 0.12, 0.3), (math.cos(a) * W * 0.65, -math.sin(a) * D * 0.9, 0.08), noise=0.05, segs=(5, 4))
        else:
            p.ball(0.09, M(loc=(0, -0.05, H + 0.07), scale=(0.8, 1.1, 0.8)), mat="bone", segs=(7, 5))
            for s in (-1, 1):
                p.tube([(s * 0.05, -0.05, H + 0.12), (s * 0.18, -0.08, H + 0.25), (s * 0.24, -0.05, H + J(p, 0.42, 0.12))], 0.014, mat="bone", segs=5)
            if coin(p):
                for i in range(3):
                    p.ball(0.03, T((W * 0.25 + i * 0.07, 0.1, H + 0.02)), mat="accent", segs=(5, 3))
            else:
                p.cyl(0.08, 0.06, 0.04, T((-W * 0.25, 0.05, H)), mat="stone_dark", segs=8)
    elif e == "Agrarian":  # wooden offering table with cloth and a back tablet
        ix, iy = W / 2 - 0.06, D / 2 - 0.06
        if slot == "top":
            slab(p, W, D, t, u, mat="wood")
            slab(p, W + 0.02, D * 0.5, 0.004, H, mat="cloth", bevel=0)
            slab(p, W * 0.5, 0.006, J(p, 0.35, 0.2), H - 0.35, y=-D / 2 - 0.004, mat="cloth", bevel=0) if coin(p, 0.5) else \
                slab(p, W * 0.4, 0.006, J(p, 0.5, 0.2), H - 0.5, y=-D / 2 - 0.004, mat="paint", bevel=0)
        elif slot == "legs":
            for x, y in corners(ix, iy):
                post(p, x, y, 0, u, J(p, 0.03, 0.1), mat="wood")
            for x in (-ix, ix):
                slab(p, 0.03, iy * 2, 0.04, 0.14, x=x, mat="wood", bevel=0)
        elif slot == "frame":
            bw = J(p, 0.45, 0.15)
            slab(p, bw, 0.04, Bk - H, H, y=D / 2 - 0.05, mat="wood_dark")
            ang = 18
            for s in (-1, 1):
                p.box((bw / 2 + 0.1, 0.1, 0.02), M(loc=(s * (bw / 4 + 0.03), D / 2 - 0.05, Bk + 0.04), rot=(0, s * ang, 0)), mat="wood_dark")
        else:
            p.lathe([(0, 0), (0.08, 0.01), (0.1, 0.07), (0.11, 0.08)], T((0, -0.05, H)), mat="ceramic", segs=10)
            for k in range(3):
                pole(p, (-0.02 + k * 0.02, -0.05, H + 0.05), (-0.03 + k * 0.03, -0.05, H + 0.25), 0.003, mat="wood_dark", segs=4)
            for x in (-W * 0.32, W * 0.32):
                p.cyl(0.02, 0.02, J(p, 0.14), T((x, 0, H)), mat="bone", segs=6)
            for i in range(p.rng.randint(2, 4)):
                p.ball(0.035, T((W * 0.15 + i * 0.05, 0.05 + (i % 2) * 0.04, H + 0.035)), mat="paint", segs=(6, 4))
    elif e == "Mercantile":  # carved stone altar with steps and a stele
        if slot == "top":
            slab(p, W, D, t, u, mat="stone")
            slab(p, W * 0.96, D * 0.96, 0.04, u - 0.04, mat="stone", bevel=0.1)
        elif slot == "legs":
            slab(p, W + 0.3, D + 0.3, 0.1, 0, mat="stone_dark")
            p.box((W * 0.88, D * 0.85, u - 0.14), T((0, 0, 0.1 + (u - 0.14) / 2)), mat="stone")
        elif slot == "frame":
            sw = J(p, 0.5, 0.12)
            pts = [(-sw / 2, 0), (sw / 2, 0), (sw / 2, (Bk - H) * 0.8), (0, Bk - H), (-sw / 2, (Bk - H) * 0.8)]
            p.plate(pts, 0.1, T((0, D / 2 - 0.05, H)), mat="stone")
        else:
            for x in (-W * 0.35, W * 0.35):
                p.lathe([(0.05, 0), (0.02, 0.03), (0.015, 0.2), (0.035, 0.22), (0.01, 0.24)], T((x, 0, H)), mat="brass", segs=8)
                p.cyl(0.012, 0.012, J(p, 0.08), T((x, 0, H + 0.24)), mat="bone", segs=6)
            p.box((W * 0.6, 0.012, 0.08), T((0, -D * 0.425 - 0.006, u * 0.6)), mat="gold" if coin(p) else "brass", bevel=0)
            p.lathe([(0, 0), (0.06, 0.005), (0.09, 0.05), (0.1, 0.06)], T((0, -0.05, H)), mat="brass", segs=10)
    elif e == "Industrial":  # cast-iron altar with a grille back
        ix, iy = W / 2 - 0.08, D / 2 - 0.06
        if slot == "top":
            slab(p, W, D, t, u, mat="iron")
            slab(p, W + 0.04, D + 0.04, 0.015, u - 0.015, mat="iron", bevel=0)
        elif slot == "legs":
            prof = [(0.06, 0), (0.04, 0.04), (0.025, 0.1), (0.035 * J(p, 1, 0.15), u * 0.5), (0.025, u - 0.06), (0.04, u - 0.015)]
            for x, y in corners(ix, iy):
                p.lathe(prof, T((x, y, 0)), mat="iron", segs=6)
            for y in (-iy, iy):
                slab(p, ix * 2, 0.012, 0.08, u - 0.095, y=y, mat="iron", bevel=0)
        elif slot == "frame":
            gw = J(p, 0.7, 0.1)
            gh = Bk - H
            for i in range(7):
                x = -gw / 2 + gw * i / 6
                p.box((0.012, 0.012, gh * (0.85 + 0.15 * math.cos((i - 3) / 3 * 1.2))), T((x, D / 2 - 0.04, H + gh * 0.42)), mat="iron", bevel=0)
            for z in (H + 0.04, H + gh * 0.5):
                p.box((gw + 0.02, 0.016, 0.02), T((0, D / 2 - 0.04, z)), mat="iron", bevel=0)
            p.ring(0.12, 0.012, M(loc=(0, D / 2 - 0.04, H + gh * 0.72), rot=(90, 0, 0)), mat="iron", segs=12)
        else:
            p.box((W * 0.7, 0.12, 0.03), T((0, 0.05, H + 0.015)), mat="iron", bevel=0)
            for i in range(p.rng.randint(4, 6)):
                x = -W * 0.3 + i * W * 0.12
                p.cyl(0.012, 0.012, J(p, 0.1, 0.4), T((x, 0.05, H + 0.03)), mat="bone", segs=6)
            p.cyl(0.04, 0.04, 0.008, M(loc=(0, -D / 2 - 0.006, u * 0.7), rot=(90, 0, 0)), mat="steel", segs=10)
    elif e == "Steampunk":  # mechanism altar: gear mandala and orb
        if slot == "top":
            slab(p, W, D, t, u, mat="wood_dark")
            for y in (-D / 2, D / 2):
                slab(p, W + 0.01, 0.01, t + 0.01, u - 0.005, y=y, mat="brass", bevel=0)
        elif slot == "legs":
            p.box((W * 0.85, D * 0.8, u - 0.08), T((0, 0, 0.08 + (u - 0.08) / 2)), mat="brass")
            slab(p, W + 0.1, D + 0.1, 0.08, 0, mat="iron")
        elif slot == "frame":
            gz = H + (Bk - H) * 0.5
            gr = J(p, 0.3, 0.1)
            p.box((0.06, 0.06, Bk - H), T((0, D / 2 - 0.05, (H + Bk) / 2)), mat="brass", bevel=0)
            gear(p, gr, T((0, D / 2 - 0.09, gz)), teeth=12, th=0.016)
            gear(p, gr * 0.45, T((gr * 0.95, D / 2 - 0.08, gz - gr * 0.6)), teeth=8, th=0.012, mat="copper")
        else:
            gz = H + (Bk - H) * 0.5
            p.ball(0.06, T((0, D / 2 - 0.12, gz)), mat="glow", segs=(8, 6))
            p.cyl(0.12, 0.12, 0.01, M(loc=(0, -D * 0.4 - 0.006, u * 0.55), rot=(90, 0, 0)), mat="brass", segs=12)
            p.cyl(0.08, 0.08, 0.004, M(loc=(0, -D * 0.4 - 0.012, u * 0.55), rot=(90, 0, 0)), mat="glow", segs=12)
            if coin(p):
                for x in (-W * 0.35, W * 0.35):
                    p.cyl(0.03, 0.02, 0.18, T((x, 0, H)), mat="brass", segs=6)
                    p.ball(0.02, T((x, 0, H + 0.2)), mat="glow", segs=(6, 4))
    elif e == "Future":  # altar of light: plinth, glowing disc, halo arc
        if slot == "top":
            p.cyl(W / 2, W / 2, t, T((0, 0, u)), mat="body", segs=16)
            p.cyl(W * 0.38, W * 0.38, 0.004, T((0, 0, H)), mat="glow", segs=16)
        elif slot == "legs":
            r0 = J(p, 0.22, 0.12)
            p.lathe([(0, 0), (W * 0.45, 0), (W * 0.45, 0.05), (r0, 0.12), (r0 * 0.8, u * 0.6), (r0 * 1.1, u), (0, u)], mat="body", segs=14)
        elif slot == "frame":
            pts = []
            hr = J(p, 0.42, 0.1)
            for i in range(9):
                a = math.pi * i / 8
                pts.append((math.cos(a) * hr, D / 2 - 0.05, H + 0.25 + math.sin(a) * hr * 0.9))
            p.tube(pts, 0.018, mat="shell_dark", segs=6)
            p.tube([(x, y - 0.012, z) for x, y, z in pts[1:-1]], 0.008, mat="glow", segs=4)
            for x in (pts[0][0], pts[-1][0]):
                p.cyl(0.03, 0.03, 0.25, T((x, D / 2 - 0.05, H)), mat="body", segs=8)
        else:
            for i in range(p.rng.randint(3, 5)):
                a = i * 1.3
                p.ball(0.018, T((math.cos(a) * 0.15, math.sin(a) * 0.15, H + J(p, 0.25, 0.4))), mat="glow", segs=(6, 4))
            p.ring(W * 0.46, 0.006, T((0, 0, 0.05)), mat="glow", segs=16)
    elif e == "Wasteland":  # junk shrine: drum, sheet top, can candles
        if slot == "top":
            slab(p, W, D, t, u, mat="rust", noise=0.004)
            p.box((J(p, 0.5), D * 0.7, 0.004), M(loc=(p.rng.uniform(-0.2, 0.2), 0, H + 0.002), rot=(0, 0, 5)), mat="cloth", bevel=0)
        elif slot == "legs":
            for x in (-W * 0.28, W * 0.28):
                p.cyl(0.2, 0.2, u, M(loc=(x, 0, 0), rot=(0, 0, p.rng.uniform(0, 90))), mat="paint" if x < 0 else "rust", segs=12)
        elif slot == "frame":
            pts = [(-0.3, 0), (0.3, 0), (0.28, (Bk - H) * 0.7), (0, Bk - H), (-0.3, (Bk - H) * 0.75)]
            p.plate(pts, 0.01, M(loc=(0, D / 2 - 0.03, H), rot=(0, J(p, 3, 1), 0)), mat="steel", bevel=0)
            pole(p, (-0.35, D / 2 - 0.04, H + (Bk - H) * 0.6), (0.35, D / 2 - 0.04, H + (Bk - H) * 0.6), 0.01, mat="iron")
            for x in (-W * 0.28, W * 0.28):
                p.ring(0.202, 0.01, T((x, 0, u * 0.5)), mat="iron", segs=12)
        else:
            for i in range(p.rng.randint(3, 5)):
                x = -W * 0.35 + i * W * 0.17
                p.cyl(0.03, 0.03, 0.08, T((x, -0.05, H)), mat="steel", segs=6)
                p.ball(0.015, T((x, -0.05, H + 0.1)), mat="glow", segs=(5, 3))
            p.cyl(0.1, 0.08, 0.02, M(loc=(0, D / 2 - 0.045, H + (Bk - H) * 0.45), rot=(90, 0, 0)), mat="steel", segs=10)
    else:  # Ancient: monolithic altar with rune channels under a stone arch
        if slot == "top":
            slab(p, W, D, t, u, mat="body")
        elif slot == "legs":
            p.box((W * 0.85, D * 0.8, u), T((0, 0, u / 2)), mat="body", bevel=0.1)
            slab(p, W + 0.25, D + 0.25, 0.08, 0, mat="stone_dark", bevel=0.15)
        elif slot == "frame":
            aw = W * 0.5
            pts = [(-aw, 0), (-aw + 0.14, 0), (-aw + 0.14, (Bk - H) * 0.6), (0, (Bk - H) * 0.82), (aw - 0.14, (Bk - H) * 0.6), (aw - 0.14, 0),
                   (aw, 0), (aw, (Bk - H) * 0.7), (0, Bk - H + J(p, 0.04, 1)), (-aw, (Bk - H) * 0.7)]
            p.plate(pts, 0.14, T((0, D / 2 - 0.07, H)), mat="body", bevel=0.15)
        else:
            p.box((W * 0.7, 0.012, 0.025), T((0, -D * 0.4 - 0.006, u * 0.8)), mat="glow", bevel=0)
            p.box((0.04, 0.012, u * 0.55), T((0, -D * 0.4 - 0.006, u * 0.4)), mat="glow", bevel=0)
            p.ball(J(p, 0.07, 0.2), T((0, 0.05, H + 0.07)), mat="glow", segs=(8, 6))
            if coin(p):
                for x in (-W * 0.32, W * 0.32):
                    p.box((0.08, 0.08, 0.16), T((x, 0, H + 0.08)), mat="gold", bevel=0.3)
