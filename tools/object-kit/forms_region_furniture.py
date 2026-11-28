"""Four-planet forms of the furniture (cosmos_chimera everyday-objects.md#四星球形體, Q-A38 batch 2, furniture).

Table, Chair, Shelf, Stall, Workbench, Signboard and Altar for Ocean, Gale, Radiant and Metropolis in all 8 eras.
Slots, frame order and the per-era surface heights are those of forms_furniture.py (top / legs / frame / trim; floor at
z = 0, front -Y), so props set on a table top or a stall counter sit where they sat on the shared forms.

Region vocabulary (planet-world.md#四星球時代造型, the stilt-house / beam-end / roof-pavilion / fin traditions):
- Ocean: bamboo posts with nodes, rattan lashing, slatted tops, saddle roofs whose ridge ends sweep up into horns,
  the spirit house on a post.
- Gale: chunky carved wood, beam-end pegs bristling from rails, painted zigzag bands, posts capped with cones,
  the one-piece carved stool and the mud-pillar altar.
- Radiant: turned legs, scalloped arches, lotus petals, onion-dome pavilions (chhatri), jali backs, the dome shrine.
- Metropolis: by era (meteoric iron and hull plate, iron and glass, art-deco setbacks, chrome and shell with light
  strips, container steel).
Craft materials come from the region's roles (kit_lib.REGION_STYLE); era tokens (gear, light strip, rune slots,
scrap patch) mark the four eras that have their own.
"""
import math

from mathutils import Matrix

from forms_furniture import FURN, corners, flagstone, pot, rock, runes, slab
from forms_region_pilot import HAND, MACHINE, dome, horn, lash, pegs, petals, steps, zig
from kit_forms import F, J, coin, regional
from kit_lib import M, REGIONS

T = Matrix.Translation


def _tier(e):
    return "hand" if e in HAND else "machine" if e in MACHINE else "high"


# ---------------------------------------------------------------- shared regional parts


def leg(p, x, y, z0, z1, s):
    """A region's leg or post from z0 to z1, half-width s."""
    g, e = p.region, p.era
    h = z1 - z0
    if g == "Ocean":
        p.cyl(s, s, h, T((x, y, z0)), mat="body", segs=6, bevel=0)
        p.cyl(s * 1.15, s * 1.15, s * 0.7, T((x, y, z0 + h * 0.55)), mat="body", segs=6, bevel=0)
        if e == "Future":  # float foot
            p.ball(s * 1.6, M(loc=(x, y, z0 + s), scale=(1, 1, 0.7)), mat="fit", segs=(6, 4))
    elif g == "Gale":
        p.cyl(s * 1.25, s * 0.9, h, T((x, y, z0)), mat="body", segs=5, bevel=0)
    elif g == "Radiant":
        p.lathe([(s * 1.1, 0), (s * 0.8, h * 0.15), (s * 1.3, h * 0.3), (s * 0.75, h * 0.5), (s * 1.2, h * 0.75), (s * 0.85, h * 0.9), (s, h)],
                T((x, y, z0)), mat="body", segs=6)
    else:
        if e == "Primal":
            p.box((s * 2.2, s * 1.8, h), M(loc=(x, y, z0 + h / 2), rot=(0, 0, J(p, 8, 1))), mat="body", noise=0.04)
        elif e == "Industrial":
            p.box((s * 1.4, s * 1.4, h), T((x, y, z0 + h / 2)), mat="body", bevel=0)
            steps(p, s * 3.2, s * 3.2, z0, 2, s * 0.8, M(loc=(x, y, 0)), mat="fit", shrink=0.75)
        elif e == "Future":
            p.box((s * 1.2, s * 3.0, h), T((x, y, z0 + h / 2)), mat="body", bevel=0.3)
        else:
            p.box((s * 2, s * 2, h), T((x, y, z0 + h / 2)), mat="body", bevel=0)


def surface(p, W, D, t, u, mat="body"):
    """A region's flat top whose underside is at u."""
    g, e = p.region, p.era
    if g == "Ocean" and e not in ("Future", "Ancient"):  # slats along X
        n = 5
        for i in range(n):
            p.cyl(D / n * 0.5, D / n * 0.5, W, M(loc=(-W / 2, -D / 2 + D / n * (i + 0.5), u + t / 2), rot=(0, 90, 0)), mat=mat, segs=6, bevel=0)
    elif g == "Gale":
        slab(p, W, D, t * 1.3, u - t * 0.3, mat=mat)
    elif g == "Radiant":
        slab(p, W, D, t, u, mat=mat)
        slab(p, W * 1.04, D * 1.04, t * 0.3, u + t * 0.7, mat="fit", bevel=0)
    else:
        slab(p, W, D, t, u, mat=mat, bevel=0.3 if e == "Future" else None)


def rails(p, W, D, z, h=0.08):
    """A region's apron under a top: four rails with its own joinery."""
    g, e = p.region, p.era
    for y in (-D / 2, D / 2):
        slab(p, W, 0.025, h, z - h, y=y, mat="body", bevel=0)
    for x in (-W / 2, W / 2):
        slab(p, 0.025, D, h, z - h, x=x, mat="body", bevel=0)
    if g == "Ocean":  # rail ends sweep up into horns
        for s in (-1, 1):
            horn(p, s * W / 2, -D / 2, z - h * 0.5, h * 1.2, s, mat="accent")
    elif g == "Gale":  # beam ends poke through the front rail
        for i in range(5):
            x = -W / 2 + W * (i + 0.5) / 5
            p.box((0.03, 0.08, 0.03), T((x, -D / 2 - 0.03, z - h * 0.4)), mat="body", bevel=0)
    elif g == "Radiant":  # scalloped front apron
        pts = [(-W / 2, 0), (W / 2, 0)]
        n = 4
        for i in range(n * 2 + 1):
            xx = W / 2 - W * i / (n * 2)
            pts.append((xx, -h * (1.6 if i % 2 else 1.0)))
        p.plate(pts, 0.012, T((0, -D / 2 - 0.014, z)), mat="fit", bevel=0)
    elif e == "Industrial":
        steps(p, W * 0.4, 0.02, z - h * 1.6, 2, h * 0.3, M(loc=(0, -D / 2 - 0.015, 0)), mat="fit", shrink=0.7)


def token(p, x, y, z, s=0.1):
    """The era's own mark on a -Y face (gear, light strip, rune slots, scrap patch)."""
    e = p.era
    if e == "Steampunk":
        p.cyl(s * 0.5, s * 0.5, 0.012, T((x, y - 0.006, z)) @ M(rot=(90, 0, 0)), mat="brass", segs=8, bevel=0)
        for i in range(8):
            a = i * math.tau / 8
            p.box((s * 0.14, 0.012, s * 0.14), M(loc=(x + math.cos(a) * s * 0.55, y - 0.012, z + math.sin(a) * s * 0.55), rot=(0, -math.degrees(a), 0)),
                  mat="brass", bevel=0)
    elif e == "Future":
        p.box((s * 3, 0.01, s * 0.12), T((x, y - 0.005, z)), mat="glow", bevel=0)
    elif e == "Ancient":
        runes(p, x, y - 0.006, z - s, z + s, n=3, w=s * 0.3)
    elif e == "Wasteland":
        p.box((s * 1.4, 0.008, s * 0.9), M(loc=(x, y - 0.004, z), rot=(0, J(p, 8, 1), 0)), mat="metal", bevel=0)


def goods(p, W, D, z, n=3):
    """Small wares set on a top at z: the region's vessels."""
    g, e = p.region, p.era
    for i in range(n):
        x = -W * 0.35 + W * 0.7 * i / max(1, n - 1) + p.rng.uniform(-0.04, 0.04)
        y = p.rng.uniform(-D * 0.2, D * 0.15)
        s = J(p, 0.06, 0.25)
        if g == "Ocean":  # coconut-shell bowls and a bamboo cup
            if i % 2:
                p.cyl(s * 0.4, s * 0.4, s * 1.6, T((x, y, z)), mat="body", segs=6, bevel=0)
            else:
                p.lathe([(0, 0), (s * 0.9, s * 0.15), (s, s * 0.6)], T((x, y, z)), mat="bark" if e in HAND else "accent", segs=7)
        elif g == "Gale":  # gourds
            p.ball(s * 0.7, T((x, y, z + s * 0.6)), mat="gourd" if e in HAND else "accent", segs=(6, 4))
            p.ball(s * 0.4, T((x, y, z + s * 1.4)), mat="gourd" if e in HAND else "accent", segs=(5, 3))
        elif g == "Radiant":  # brass pots and a lamp
            if i == 1:
                p.lathe([(0, 0), (s * 0.6, s * 0.1), (s * 0.3, s * 0.3), (s * 0.5, s * 0.45), (0.0, s * 0.5)], T((x, y, z)), mat="fit", segs=7)
            else:
                pot(p, s * 0.7, s * 1.3, (x, y, z), mat="fit" if e not in ("Primal",) else "clay", segs=7)
        else:
            if _tier(e) == "high":
                p.box((s * 1.2, s * 0.8, s * 0.6), T((x, y, z + s * 0.3)), mat="body", bevel=0.3, bevel_seg=1)
            elif _tier(e) == "machine":
                p.cyl(s * 0.5, s * 0.5, s * 1.2, T((x, y, z)), mat="metal", segs=7, bevel=0)
            else:
                p.box((s * 1.2, s * 0.9, s * 0.8), T((x, y, z + s * 0.4)), mat="body", bevel=0)


def saddle_roof(p, W, D, z, rise, mat="body"):
    """Ocean: two roof planes over W x D with the ridge along X, ridge ends sweeping up into horns."""
    for s in (-1, 1):
        ang = math.degrees(math.atan2(rise, D / 2))
        L = math.hypot(rise, D / 2)
        p.box((W * 1.05, L * 1.1, 0.03), M(loc=(0, s * D / 4, z + rise / 2), rot=(-s * ang, 0, 0)), mat=mat, bevel=0)
    for s in (-1, 1):
        horn(p, s * W * 0.52, 0, z + rise, rise * 0.7, s, mat="accent")


# ---------------------------------------------------------------- Table


def table(p, slot):
    e, g = p.era, p.region
    fh, fw, fd = F(p, 1, 0.04), F(p, 1, 0.1), F(p, 1, 0.08)
    h0, w0, d0, t = {"Primal": (0.55, 1.0, 0.7, 0.1), "Agrarian": (0.74, 1.15, 0.7, 0.045),
                     "Mercantile": (0.76, 1.1, 0.66, 0.045), "Industrial": (0.75, 1.2, 0.7, 0.035),
                     "Steampunk": (0.76, 0.95, 0.95, 0.05), "Future": (0.74, 1.2, 0.68, 0.05),
                     "Wasteland": (0.74, 1.2, 0.72, 0.045), "Ancient": (0.72, 1.2, 0.72, 0.12)}[e]
    H, W, D = h0 * fh, w0 * fw, d0 * fd
    u = H - t
    ix, iy = W / 2 - 0.07, D / 2 - 0.07
    if slot == "top":
        if g == "Gale" and e == "Primal":  # low round carved top
            p.cyl(W * 0.42, W * 0.4, t, T((0, 0, u)), mat="body", segs=10, bevel=0)
        else:
            surface(p, W, D, t, u)
    elif slot == "legs":
        if g == "Gale" and e in HAND:  # one carved pedestal
            p.lathe([(W * 0.3, 0), (W * 0.12, u * 0.2), (W * J(p, 0.08, 0.2), u * 0.6), (W * 0.2, u)], mat="body", segs=8)
        else:
            s = J(p, 0.03, 0.12)
            for x, y in corners(ix, iy):
                leg(p, x, y, 0, u, s)
    elif slot == "frame":
        if g == "Gale" and e in HAND:
            zig(p, W * 0.32, u - 0.02, 0.05, 8)
        else:
            rails(p, ix * 2 + 0.05, iy * 2 + 0.05, u)
            if g == "Ocean":
                lash(p, 0.035, 0, 0.04, M(loc=(ix, -iy, u - 0.04)), segs=6)
    else:
        goods(p, W, D, H, n=p.rng.randint(2, 3))
        token(p, 0, -D / 2 - 0.02, u - 0.04)
        if g == "Radiant" and coin(p):
            petals(p, 0.04, H, 5, 0.03, M(loc=(W * 0.3, D * 0.2, 0)), mat="accent")


# ---------------------------------------------------------------- Chair


def chair(p, slot):
    e, g = p.era, p.region
    fs, fw, fb = F(p, 1, 0.04), F(p, 1, 0.08), F(p, 1, 0.06)
    S = 0.45 * fs
    W, D = 0.45 * fw, 0.43 * fw
    B = 0.92 * fb
    t = 0.04
    if g == "Gale" and e in HAND + ("Ancient",):
        # One-piece carved stool: curved seat on a pillared base.
        if slot == "top":
            pts = [(-W * 0.55, 0.03), (-W * 0.3, -0.01), (0, -0.025), (W * 0.3, -0.01), (W * 0.55, 0.03), (W * 0.55, 0.06), (0, 0.02), (-W * 0.55, 0.06)]
            p.plate(pts, D * 0.7, T((0, 0, S - 0.02)), mat="body", bevel=0)
        elif slot == "legs":
            slab(p, W * 0.9, D * 0.6, 0.06, 0, mat="body")
            p.cyl(W * 0.14, W * 0.12, S - 0.1, T((0, 0, 0.06)), mat="body", segs=7, bevel=0)
            for s in (-1, 1):
                p.cyl(0.025, 0.025, S - 0.1, T((s * W * 0.3, 0, 0.06)), mat="body", segs=5, bevel=0)
        elif slot == "frame":
            zig(p, W * 0.15, S * 0.45, 0.05, 6)
            pegs(p, W * 0.12, S * 0.25, 4, 0.04, mat="fit")
        else:
            p.ball(0.03, T((0, -D * 0.32, 0.08)), mat="accent", segs=(5, 3))
            token(p, 0, -D * 0.3, S * 0.5, 0.05)
        return
    ix, iy = W / 2 - 0.04, D / 2 - 0.04
    if slot == "top":
        if g == "Ocean":  # woven rattan seat disc
            p.cyl(W * 0.55, W * 0.5, t, T((0, 0, S - t)), mat="fit" if e in HAND else "body", segs=10, bevel=0)
            p.ring(W * 0.53, 0.012, T((0, 0, S - t * 0.3)), mat="fit", segs=10)
        else:
            surface(p, W, D, t, S - t)
    elif slot == "legs":
        if g == "Ocean" and e in HAND:  # rattan drum base
            p.lathe([(W * 0.4, 0), (W * 0.3, (S - t) * 0.5), (W * 0.45, S - t)], mat="fit", segs=8)
            lash(p, W * 0.3, (S - t) * 0.5, 0.04, segs=8)
        else:
            s = J(p, 0.02, 0.12)
            for x, y in corners(ix, iy):
                leg(p, x, y, 0, S - t, s)
    elif slot == "frame":  # the back
        bh = B - S
        if g == "Ocean":  # peacock fan back
            r = J(p, 0.38, 0.1) * W / 0.45
            p.ring(r, 0.015, M(loc=(0, iy, S + r * 0.9), rot=(80, 0, 0), scale=(1, 1.2, 1)), mat="fit", segs=12)
            for i in range(5):
                a = math.radians(30 + i * 30)
                p.tube([(0, iy, S), (math.cos(a) * r, iy + 0.02, S + r * 0.9 + math.sin(a) * r * 0.9)], 0.006, mat="fit", segs=4)
        elif g == "Gale":  # low back with pegged crest
            slab(p, W, 0.04, bh * 0.6, S, y=iy, mat="body", bevel=0)
            for i in range(4):
                p.box((0.025, 0.07, 0.025), T((-W * 0.38 + W * 0.76 * i / 3, iy, S + bh * 0.6)), mat="body", bevel=0)
        elif g == "Radiant":  # jali back under a little dome
            pts = [(-W / 2, 0), (W / 2, 0), (W / 2, bh * 0.7), (W * 0.25, bh * 0.85), (0, bh * 0.95), (-W * 0.25, bh * 0.85), (-W / 2, bh * 0.7)]
            p.plate(pts, 0.025, T((0, iy, S)), mat="body", bevel=0)
            for i in range(3):
                p.box((0.03, 0.03, bh * 0.45), T((-W * 0.25 + W * 0.25 * i, iy - 0.014, S + bh * 0.4)), mat="fit", bevel=0)
            dome(p, 0.045, S + bh * 0.92, M(loc=(0, iy, 0)), mat="fit", segs=8)
        else:
            if e == "Industrial":  # stepped deco back
                for i in range(3):
                    slab(p, W * (1 - i * 0.2), 0.03, bh * 0.28, S + bh * 0.3 * i, y=iy, mat="body", bevel=0)
            elif e == "Future":  # shell back with a light seam
                p.box((W, 0.05, bh), M(loc=(0, iy, S + bh / 2), rot=(-8, 0, 0)), mat="body", bevel=0.35)
                p.box((W * 0.8, 0.052, 0.01), M(loc=(0, iy, S + bh * 0.8), rot=(-8, 0, 0)), mat="glow", bevel=0)
            else:  # ladder back
                for x in (-ix, ix):
                    leg(p, x, iy, S, B, 0.018)
                for k in (0.4, 0.7, 0.95):
                    slab(p, ix * 2, 0.02, 0.05, S + bh * k - 0.05, y=iy, mat="body", bevel=0)
    else:
        if e in HAND:
            p.box((W * 0.8, D * 0.7, 0.03), T((0, 0, S + 0.015)), mat="cloth" if g != "Gale" else "hide", bevel=0.4)
        else:
            p.box((W * 0.8, D * 0.7, 0.04), T((0, 0, S + 0.02)), mat="grip", bevel=0.4)
        token(p, 0, -D / 2, S - 0.06, 0.05)


# ---------------------------------------------------------------- Shelf


def shelf(p, slot):
    e, g = p.era, p.region
    fh, fw, fd = F(p, 1, 0.06), F(p, 1, 0.1), F(p, 1, 0.08)
    h0, w0, d0 = {"Primal": (1.1, 0.9, 0.42), "Agrarian": (1.5, 0.9, 0.35), "Mercantile": (1.7, 0.9, 0.4),
                  "Industrial": (1.6, 0.95, 0.4), "Steampunk": (1.5, 0.7, 0.7), "Future": (1.6, 0.95, 0.32),
                  "Wasteland": (1.45, 1.0, 0.4), "Ancient": (1.5, 0.9, 0.42)}[e]
    H, W, D = h0 * fh, w0 * fw, d0 * fd
    n = 3 if H < 1.3 else 4
    levels = [0.12 + (H - 0.2) * i / n for i in range(n)]
    t = 0.03
    if slot == "top":
        for z in levels:
            surface(p, W, D, t, z)
        if g == "Radiant":  # arched top board
            pts = [(-W / 2, 0), (W / 2, 0), (W / 2, 0.08), (W * 0.2, 0.14), (0, 0.22), (-W * 0.2, 0.14), (-W / 2, 0.08)]
            p.plate(pts, D, T((0, 0, H - 0.08)), mat="body", bevel=0)
        else:
            surface(p, W * 1.05, D * 1.05, t, H - t)
    elif slot == "legs":
        for x, y in corners(W / 2 - 0.02, D / 2 - 0.02):
            leg(p, x, y, 0, H - t, 0.02)
    elif slot == "frame":
        if g == "Ocean":  # woven back and a horned crest
            slab(p, W, 0.012, H - 0.15, 0.12, y=D / 2 - 0.01, mat="fit", bevel=0)
            for s in (-1, 1):
                horn(p, s * W / 2, -D / 2, H, 0.12, s, mat="accent")
        elif g == "Gale":  # carved sides with pegs and a zig cornice
            for x in (-W / 2, W / 2):
                slab(p, 0.025, D, H - 0.1, 0.05, x=x, mat="body", bevel=0)
            for i in range(4):
                p.box((0.03, 0.03, 0.08), T((-W / 2 + W * (i + 0.5) / 4, -D / 2 - 0.02, H + 0.04)), mat="body", bevel=0)
            for x in (-W / 2, W / 2):
                p.cyl(0.035, 0.0, 0.14, T((x, -D / 2, H)), mat="body", segs=5, bevel=0)
        elif g == "Radiant":  # arched niches on the back panel
            slab(p, W, 0.015, H - 0.1, 0.05, y=D / 2 - 0.01, mat="body", bevel=0)
            for x in (-W / 2, W / 2):
                dome(p, 0.04, H + 0.02, M(loc=(x, -D / 2 + 0.03, 0)), mat="fit", segs=7)
        else:
            if e == "Future":
                slab(p, W, 0.02, H - 0.1, 0.05, y=D / 2 - 0.01, mat="fit", bevel=0)
                for z in levels:
                    p.box((W * 0.95, 0.01, 0.008), T((0, -D / 2 - 0.004, z + t)), mat="glow", bevel=0)
            elif e == "Industrial":
                steps(p, W * 0.6, D * 0.6, H, 3, 0.05, mat="fit", shrink=0.7)
            else:
                for i in range(2):
                    p.tube([(-W / 2, D / 2 - 0.01, 0.12 + i * 0.4), (W / 2, D / 2 - 0.01, 0.12 + (H - 0.3) - i * 0.4)], 0.008, mat="metal", segs=4)
    else:
        for z in levels[:-1]:
            goods(p, W * 0.9, D * 0.6, z + t, n=2)
        token(p, 0, -D / 2 - 0.02, H - 0.08)


# ---------------------------------------------------------------- Stall


def stall(p, slot):
    e, g = p.era, p.region
    fh, fw, fd, fr = F(p, 1, 0.04), F(p, 1, 0.08), F(p, 1, 0.08), F(p, 1, 0.04)
    W, D = 1.6 * fw, 0.75 * fd
    C = (0.65 if e == "Primal" else 0.88) * fh
    R = 2.35 * fr
    t = 0.05
    if slot == "top":  # counter
        surface(p, W, D, t, C - t)
    elif slot == "legs":  # counter body
        if g == "Ocean":
            for x, y in corners(W / 2 - 0.05, D / 2 - 0.05):
                leg(p, x, y, 0, C - t, 0.03)
            slab(p, W * 0.95, 0.012, (C - t) * 0.6, 0.15, y=-D / 2 + 0.05, mat="fit", bevel=0)
        elif g == "Gale":  # mud-block counter with pegs
            slab(p, W, D * 0.8, C - t, 0, mat="clay" if e in HAND else "body", bevel=0)
            for i in range(5):
                p.box((0.035, 0.09, 0.035), T((-W * 0.4 + W * 0.2 * i, -D * 0.4 - 0.03, C - 0.12)), mat="body", bevel=0)
        elif g == "Radiant":
            slab(p, W, D * 0.8, C - t, 0, mat="body", bevel=0)
            pts = [(-W / 2, 0), (W / 2, 0)]
            for i in range(9):
                pts.append((W / 2 - W * i / 8, -(0.18 if i % 2 else 0.1)))
            p.plate(pts, 0.012, T((0, -D * 0.4 - 0.008, C - t)), mat="fit", bevel=0)
        else:
            for x, y in corners(W / 2 - 0.05, D / 2 - 0.05):
                leg(p, x, y, 0, C - t, 0.025)
            slab(p, W * 0.95, 0.015, C * 0.5, C * 0.2, y=-D / 2 + 0.05, mat="body" if e != "Industrial" else "fit", bevel=0)
    elif slot == "frame":  # posts and roof
        for x, y in corners(W / 2, D / 2):
            leg(p, x, y, C, R, 0.022) if g != "Gale" else p.cyl(0.03, 0.025, R - C, T((x, y, C)), mat="body", segs=5, bevel=0)
        if g == "Ocean":
            saddle_roof(p, W, D * 1.2, R, 0.35, mat="fit" if e in HAND else "body")
        elif g == "Gale":  # flat roof, beam ends, cone pinnacles
            slab(p, W * 1.05, D * 1.1, 0.06, R, mat="clay" if e in HAND else "body", bevel=0)
            for i in range(6):
                p.box((0.03, 0.12, 0.03), T((-W / 2 + W * (i + 0.5) / 6, -D * 0.55 - 0.04, R + 0.02)), mat="body", bevel=0)
            for x, y in corners(W * 0.5, D * 0.52):
                p.cyl(0.05, 0.0, 0.25, T((x, y, R + 0.06)), mat="clay" if e in HAND else "body", segs=5, bevel=0)
        elif g == "Radiant":  # chhatri: scalloped eave under a dome
            slab(p, W * 1.08, D * 1.15, 0.04, R, mat="body", bevel=0)
            dome(p, min(W, D) * 0.42, R + 0.04, mat="fit", segs=10)
        else:
            if e == "Future":
                p.box((W * 1.1, D * 1.2, 0.04), M(loc=(0, 0, R), rot=(6, 0, 0)), mat="glass", bevel=0)
                p.box((W * 1.1, 0.01, 0.02), T((0, -D * 0.6, R - 0.05)), mat="glow", bevel=0)
            elif e == "Industrial":
                p.box((W * 1.1, D * 1.25, 0.03), M(loc=(0, -0.05, R), rot=(10, 0, 0)), mat="paint", bevel=0)
                steps(p, W * 0.5, 0.06, R + 0.05, 3, 0.07, mat="fit", shrink=0.7)
            else:
                p.box((W * 1.1, D * 1.25, 0.03), M(loc=(0, -0.05, R), rot=(10, 0, 0)), mat="cloth" if e != "Primal" else "hide", bevel=0)
    else:
        goods(p, W, D * 0.8, C, n=p.rng.randint(3, 4))
        token(p, 0, -D / 2 - 0.02, C - 0.15, 0.12)
        if g == "Ocean":
            lash(p, 0.03, R * 0.7, 0.04, M(loc=(-W / 2, -D / 2, 0)), segs=6)


# ---------------------------------------------------------------- Workbench


def workbench(p, slot):
    e, g = p.era, p.region
    fh, fw, fd = F(p, 1, 0.04), F(p, 1, 0.1), F(p, 1, 0.08)
    h0, w0, d0, t = {"Primal": (0.62, 1.3, 0.55, 0.16), "Agrarian": (0.84, 1.5, 0.6, 0.08),
                     "Mercantile": (0.86, 1.5, 0.62, 0.07), "Industrial": (0.88, 1.5, 0.7, 0.04),
                     "Steampunk": (0.88, 1.4, 0.7, 0.06), "Future": (0.9, 1.4, 0.7, 0.06),
                     "Wasteland": (0.85, 1.5, 0.65, 0.05), "Ancient": (0.86, 1.4, 0.65, 0.12)}[e]
    H, W, D = h0 * fh, w0 * fw, d0 * fd
    u = H - t
    ix, iy = W / 2 - 0.08, D / 2 - 0.08
    if slot == "top":
        surface(p, W, D, t, u)
    elif slot == "legs":
        s = J(p, 0.04, 0.12)
        for x, y in corners(ix, iy):
            leg(p, x, y, 0, u, s)
        slab(p, ix * 2, iy * 2, 0.025, u * 0.25, mat="body", bevel=0)  # lower shelf
    elif slot == "frame":
        rails(p, ix * 2 + 0.08, iy * 2 + 0.08, u, h=0.1)
        # The vise: region's clamp at the front-left corner.
        vx = -W / 2 + 0.12
        if g == "Ocean":
            p.cyl(0.03, 0.03, 0.14, M(loc=(vx, -D / 2 - 0.02, u - 0.07), rot=(90, 0, 0)), mat="body", segs=6, bevel=0)
            lash(p, 0.03, 0, 0.03, M(loc=(vx, -D / 2 - 0.08, u - 0.07), rot=(90, 0, 0)), segs=6)
        elif g == "Gale":
            p.box((0.08, 0.06, 0.12), T((vx, -D / 2 - 0.03, u - 0.04)), mat="body", bevel=0)
            pegs(p, 0.03, 0, 2, 0.05, M(loc=(vx, -D / 2 - 0.03, u - 0.04)), mat="fit")
        elif g == "Radiant":
            p.box((0.1, 0.05, 0.1), T((vx, -D / 2 - 0.025, u - 0.03)), mat="fit", bevel=0)
            p.lathe([(0.01, 0), (0.02, 0.06), (0, 0.08)], T((vx, -D / 2 - 0.05, u - 0.03)) @ M(rot=(90, 0, 0)), mat="fit", segs=6)
        else:
            p.box((0.12, 0.08, 0.1), T((vx, -D / 2 - 0.04, u + 0.02)), mat="metal", bevel=0)
            p.cyl(0.008, 0.008, 0.16, M(loc=(vx - 0.08, -D / 2 - 0.09, u + 0.02), rot=(0, 90, 0)), mat="metal", segs=5, bevel=0)
    else:
        # Tools laid out: two short hafts and a block, plus the region's wares.
        for i in range(2):
            x = W * (0.05 + 0.15 * i)
            p.cyl(0.012, 0.012, 0.22, M(loc=(x, -D * 0.2, H + 0.012), rot=(0, 90, J(p, 20, 1))), mat="body", segs=5, bevel=0)
            p.box((0.05, 0.03, 0.03), T((x + 0.22, -D * 0.2, H + 0.015)), mat="metal", bevel=0)
        goods(p, W * 0.4, D * 0.4, H, n=2)
        token(p, W * 0.25, -D / 2 - 0.02, u - 0.05)


# ---------------------------------------------------------------- Signboard


def signboard(p, slot):
    e, g = p.era, p.region
    fh, fw, fs = F(p, 1, 0.05), F(p, 1, 0.1), F(p, 1, 0.08)
    Hp = 2.2 * fh
    Sw, Sh = 0.7 * fw, 0.42 * fs
    zb = Hp - 0.2  # crossbar / bracket
    if slot == "top":  # the sign face
        if g == "Ocean":  # board hung on two cords
            slab(p, Sw, 0.03, Sh, zb - 0.1 - Sh, y=-0.25, mat="body" if e != "Future" else "glass")
        elif g == "Gale":  # painted board with a zig border, on the post itself
            slab(p, Sw, 0.04, Sh, zb - Sh - 0.15, y=-0.06, mat="body")
            for i in range(6):
                x = -Sw / 2 + Sw * (i + 0.5) / 6
                p.box((Sw / 6 * 0.8, 0.01, 0.04), M(loc=(x, -0.085, zb - 0.18), rot=(0, 30 if i % 2 else -30, 0)), mat="accent" if i % 2 else "fit", bevel=0)
        elif g == "Radiant":  # arch-topped board
            pts = [(-Sw / 2, 0), (Sw / 2, 0), (Sw / 2, Sh * 0.7), (Sw * 0.3, Sh * 0.9), (0, Sh * 1.1), (-Sw * 0.3, Sh * 0.9), (-Sw / 2, Sh * 0.7)]
            p.plate(pts, 0.035, T((0, -0.06, zb - Sh - 0.2)), mat="body", bevel=0)
            p.plate([(x * 0.85, z * 0.85) for x, z in pts], 0.01, T((0, -0.08, zb - Sh - 0.2 + Sh * 0.06)), mat="fit", bevel=0)
        else:
            if e == "Industrial":  # stepped deco blade sign
                for i in range(3):
                    slab(p, 0.06, Sw * (1 - i * 0.2), Sh * 0.9, zb - Sh * 1.6 + i * Sh * 0.9, y=-Sw * 0.5, mat="paint" if i % 2 else "body", bevel=0)
            elif e == "Future":
                p.box((Sw, 0.02, Sh), T((0, -0.3, zb - Sh / 2 - 0.1)), mat="glass", bevel=0)
                p.box((Sw * 0.8, 0.022, Sh * 0.15), T((0, -0.3, zb - Sh / 2 - 0.1)), mat="glow", bevel=0)
            else:
                slab(p, Sw, 0.03, Sh, zb - 0.1 - Sh, y=-0.3, mat="body")
    elif slot == "legs":  # post
        if g == "Ocean":
            leg(p, 0, 0, 0, Hp, 0.04)
        elif g == "Gale":
            p.cyl(0.06, 0.045, Hp, mat="body", segs=6, bevel=0)
            slab(p, 0.3, 0.3, 0.15, 0, mat="clay" if e in HAND else "body", bevel=0)
        elif g == "Radiant":
            p.lathe([(0.12, 0), (0.1, 0.12), (0.05, 0.2), (0.04, Hp * 0.5), (0.055, Hp * 0.55), (0.04, Hp * 0.6), (0.04, Hp)], mat="body", segs=7)
        else:
            leg(p, 0, 0, 0, Hp, J(p, 0.035, 0.15))
    elif slot == "frame":  # crossbar / bracket and crest
        if g == "Ocean":
            p.box((0.05, 0.6, 0.05), T((0, -0.2, zb)), mat="body", bevel=0)
            for x in (-Sw * 0.4, Sw * 0.4):
                p.tube([(x, -0.25, zb), (x, -0.25, zb - 0.1)], 0.004, mat="fit", segs=3)
            horn(p, 0, -0.5, zb, 0.12, 1, mat="accent")
            lash(p, 0.04, zb, 0.06, segs=6)
        elif g == "Gale":
            pegs(p, 0.05, zb - 0.05, 4, 0.08, mat="body")
            p.cyl(0.06, 0.0, 0.3, T((0, 0, Hp)), mat="body", segs=6, bevel=0)
        elif g == "Radiant":
            dome(p, 0.09, Hp, mat="fit", segs=8)
            petals(p, 0.07, Hp - 0.02, 5, 0.04, mat="accent", tilt=45)
        else:
            if e == "Industrial":
                steps(p, 0.14, 0.14, Hp, 3, 0.06, mat="fit", shrink=0.7)
            elif e == "Future":
                p.box((0.06, 0.5, 0.04), T((0, -0.2, zb + 0.05)), mat="fit", bevel=0.3)
            else:
                p.box((0.04, 0.55, 0.04), T((0, -0.2, zb)), mat="metal", bevel=0)
                p.tube([(0, -0.05, zb - 0.25), (0, -0.3, zb - 0.02)], 0.01, mat="metal", segs=4)
    else:
        token(p, 0, -0.32 if g in ("Ocean", "Metropolis") else -0.1, zb - Sh * 0.6, 0.08)
        if g == "Ocean":
            p.ball(0.05, M(loc=(Sw * 0.3, -0.27, zb - Sh - 0.15), scale=(1, 0.5, 1.2)), mat="bone", segs=(5, 3))
        elif g == "Radiant":
            p.tube([(-Sw * 0.5, -0.1, zb - 0.18), (0, -0.14, zb - 0.28), (Sw * 0.5, -0.1, zb - 0.18)], 0.015, mat="accent", segs=4)
        elif g == "Gale":
            for s in (-1, 1):
                p.ball(0.04, T((s * Sw * 0.4, -0.08, zb - Sh - 0.2)), mat="gourd" if e in HAND else "accent", segs=(5, 3))
        elif e in ("Industrial", "Future"):
            p.box((Sw * 1.02, 0.01, 0.015), T((0, -0.33, zb - 0.09)), mat="glow", bevel=0)
        else:  # bolted corner plates on the board
            for x in (-Sw * 0.45, Sw * 0.45):
                p.box((0.05, 0.01, 0.05), T((x, -0.32, zb - 0.15)), mat="metal", bevel=0)


# ---------------------------------------------------------------- Altar


def altar(p, slot):
    e, g = p.era, p.region
    fh, fw, fd, fb = F(p, 1, 0.04), F(p, 1, 0.08), F(p, 1, 0.08), F(p, 1, 0.08)
    h0, w0, d0, t = {"Primal": (0.85, 1.4, 0.85, 0.16), "Agrarian": (0.82, 1.2, 0.6, 0.05),
                     "Mercantile": (0.95, 1.2, 0.65, 0.1), "Industrial": (0.92, 1.2, 0.6, 0.05),
                     "Steampunk": (0.92, 1.1, 0.65, 0.06), "Future": (0.95, 0.9, 0.9, 0.08),
                     "Wasteland": (0.9, 1.1, 0.6, 0.04), "Ancient": (0.95, 1.3, 0.75, 0.14)}[e]
    H, W, D = h0 * fh, w0 * fw, d0 * fd
    u = H - t
    Bk = 1.55 * fb
    if g == "Ocean":
        # Spirit house on a post: a little stilt house with a horned saddle roof.
        hw, hd, hh = W * 0.6, D * 0.6, (Bk - H) * 0.55
        if slot == "top":
            surface(p, W * 0.8, D * 0.8, t, u)
        elif slot == "legs":
            leg(p, 0, 0, 0, u, 0.06)
            if e in HAND:
                for x, y in corners(W * 0.3, D * 0.3):
                    p.tube([(x * 1.4, y * 1.4, 0), (x * 0.3, y * 0.3, u * 0.6)], 0.015, mat="body", segs=4)
        elif slot == "frame":
            slab(p, hw, hd, hh, H, mat="body" if e != "Future" else "glass", bevel=0)
            saddle_roof(p, hw * 1.1, hd * 1.3, H + hh, hh * 0.6, mat="fit" if e in HAND else "accent")
        else:
            for x in (-W * 0.3, W * 0.3):
                p.ball(0.035, T((x, -D * 0.3, H + 0.035)), mat="accent", segs=(5, 3))
            p.cyl(0.004, 0.004, 0.12, T((0, -D * 0.32, H)), mat="glow" if e in ("Future", "Ancient", "Steampunk") else "wood", segs=3, bevel=0)
            token(p, 0, -hd / 2, H + hh * 0.5, 0.05)
    elif g == "Gale":
        # Mud-pillar altar: a tapering block bristling with pegs, cone pinnacles on top.
        if slot == "top":
            slab(p, W, D, t, u, mat="clay" if e in HAND else "body", bevel=0)
        elif slot == "legs":
            p.box((W * 0.8, D * 0.75, u), M(loc=(0, 0, u / 2), scale=(1, 1, 1)), mat="clay" if e in HAND else "body", bevel=0)
            for i in range(4):
                p.box((0.035, 0.1, 0.035), T((-W * 0.3 + W * 0.2 * i, -D * 0.375 - 0.04, u * 0.7)), mat="body", bevel=0)
        elif slot == "frame":
            slab(p, W * 0.7, D * 0.25, Bk - H, H, y=D * 0.3, mat="clay" if e in HAND else "body", bevel=0)
            for x in (-W * 0.3, 0, W * 0.3):
                p.cyl(0.06, 0.0, 0.25, T((x, D * 0.3, Bk)), mat="clay" if e in HAND else "body", segs=5, bevel=0)
        else:
            for x in (-W * 0.25, W * 0.25):
                p.ball(0.06, T((x, -D * 0.2, H + 0.06)), mat="gourd" if e in HAND else "accent", segs=(6, 4))
            token(p, 0, -D * 0.375 - 0.02, u * 0.4)
    elif g == "Radiant":
        # Dome shrine on a lotus plinth.
        if slot == "top":
            surface(p, W, D, t, u)
        elif slot == "legs":
            slab(p, W * 0.9, D * 0.9, u * 0.5, 0, mat="body", bevel=0)
            slab(p, W * 0.75, D * 0.75, u * 0.5, u * 0.5, mat="fit" if e not in HAND else "body", bevel=0)
            petals(p, W * 0.38, u * 0.9, 8, 0.06, mat="accent", tilt=30)
        elif slot == "frame":
            sw = W * 0.45
            for x, y in corners(sw / 2, D * 0.18):
                leg(p, x, y + D * 0.15, H, Bk - 0.1, 0.02)
            slab(p, sw * 1.2, D * 0.5, 0.04, Bk - 0.1, y=D * 0.15, mat="body", bevel=0)
            dome(p, sw * 0.5, Bk - 0.06, M(loc=(0, D * 0.15, 0)), mat="fit", segs=10)
        else:
            p.lathe([(0, 0), (0.05, 0.01), (0.025, 0.04), (0.04, 0.06), (0, 0.065)], T((0, -D * 0.25, H)), mat="fit", segs=7)
            p.ball(0.012, T((0, -D * 0.25, H + 0.08)), mat="glow" if e not in HAND else "accent", segs=(4, 3))
            for x in (-W * 0.3, W * 0.3):
                pot(p, 0.04, 0.08, (x, -D * 0.2, H), mat="fit", segs=7)
            token(p, 0, -D * 0.45 - 0.02, u * 0.3)
    else:
        if slot == "top":
            surface(p, W, D, t, u)
        elif slot == "legs":
            if e == "Industrial":
                steps(p, W, D, 0, 3, u / 3, mat="body", shrink=0.9)
            elif e == "Primal":  # stacked hull plates on meteoric iron
                for i in range(3):
                    p.box((W * (0.9 - i * 0.1), D * 0.85, u / 3), M(loc=(0, 0, u / 6 + i * u / 3), rot=(0, 0, J(p, 4, 1))), mat="body", noise=0.03)
            else:
                slab(p, W * 0.85, D * 0.8, u, 0, mat="body", bevel=0.2 if e == "Future" else None)
        elif slot == "frame":
            bh = Bk - H
            if e == "Industrial":  # deco setback stele
                for i in range(4):
                    slab(p, W * (0.7 - i * 0.14), 0.12, bh / 4, H + bh / 4 * i, y=D * 0.35, mat="body" if i % 2 == 0 else "fit", bevel=0)
            elif e == "Future":  # holo pillar
                p.box((0.16, 0.16, bh), T((0, D * 0.3, H + bh / 2)), mat="body", bevel=0.3)
                p.box((0.04, 0.17, bh * 0.8), T((0, D * 0.3, H + bh / 2)), mat="glow", bevel=0)
            else:
                pts = [(-W * 0.4, 0), (W * 0.4, 0), (W * 0.35, bh * 0.8), (0, bh), (-W * 0.35, bh * 0.8)]
                p.plate(pts, 0.1, T((0, D * 0.35, H)), mat="body", bevel=0)
        else:
            goods(p, W * 0.6, D * 0.4, H, n=2)
            token(p, 0, -D * 0.4 - 0.02, u * 0.5)


for _g in REGIONS:
    regional("Table", _g)(table)
    regional("Chair", _g)(chair)
    regional("Shelf", _g)(shelf)
    regional("Stall", _g)(stall)
    regional("Workbench", _g)(workbench)
    regional("Signboard", _g)(signboard)
    regional("Altar", _g)(altar)
