"""Four-planet forms of the lamps (cosmos_chimera everyday-objects.md#四星球形體, Q-A38 batch 2, lamps).

Torch, Lantern, Candlestand, Streetlamp, Headlamp and Censer for Ocean, Gale, Radiant and Metropolis in all 8 eras.
Slots, frames and per-era sizes are those of forms_lamp.py (body / light / shade / mount; the torch is hafted with the
grip at the origin, the rest sit on z = 0 facing -Y), and the light slot always glows (forms_lamp.lit): a flame in
the hand-made eras, a flame or an early bulb in the machine eras, the era's own glow in the high-tech ones.

Region vocabulary: Ocean bamboo culms, rattan cages and lashing, coconut shells, horned caps; Gale gourds and clay,
carved posts, pegs, painted zigzags, cone tops; Radiant turned brass, lotus petals, onion domes, tiered diya dishes;
Metropolis by era (meteoric iron, cast iron and glass, art-deco setbacks, chrome and shell with light strips, scrap).
"""
import math

from mathutils import Matrix

from forms_lamp import bail, flame, lit
from forms_lamp import petals as leaf_crown
from forms_region_pilot import HAND, MACHINE, dome, era_mark, gear, horn, lash, pegs, petals, steps, zig
from forms_region_rods import _shaft
from kit_forms import F, J, regional
from kit_lib import M, REGIONS

T = Matrix.Translation


def _tier(e):
    return "hand" if e in HAND else "machine" if e in MACHINE else "high"


def _electric(p):
    """Metropolis machine eras and every Industrial lamp run on a bulb, not a flame."""
    return p.era == "Industrial" or (p.region == "Metropolis" and p.era in MACHINE)


def bulb(p, x, y, z, r, electric=None):
    """The light source: a flame, a bulb or the era's glow."""
    if _tier(p.era) == "high":
        p.ball(r, T((x, y, z + r)), mat=lit(p), segs=(6, 4))
    elif _electric(p) if electric is None else electric:
        p.ball(r, M(loc=(x, y, z + r), scale=(1, 1, 1.25)), mat=lit(p, True), segs=(6, 4))
    else:
        flame(p, x, y, z, r * 0.9, segs=6)


def mark(p, r, z, m=None):
    if p.region != "Metropolis" and p.era in ("Steampunk", "Future", "Ancient", "Wasteland"):
        era_mark(p, r, z, m)


# ================================================================ Torch (hafted: grip at origin, flame up +Z)


def torch(p, slot):
    e, g = p.era, p.region
    L = F(p, {"Primal": 0.58, "Agrarian": 0.6, "Mercantile": 0.58, "Industrial": 0.5, "Steampunk": 0.46,
              "Future": 0.42, "Wasteland": 0.55, "Ancient": 0.56}[e], 0.08)
    r = F(p, 0.016, 0.1)
    top = L * 0.72
    if slot == "body":
        _shaft(p, top, r * 1.1, r, segs=7)
    elif slot == "shade":  # the head that holds the fire or the bulb
        if g == "Ocean":  # open bamboo cup stuffed with coconut husk
            p.cyl(r * 1.7, r * 1.9, L - top, T((0, 0, top)), mat="body", segs=7, bevel=0)
            lash(p, r * 1.75, top + (L - top) * 0.3, 0.03, segs=7)
            p.cyl(r * 1.6, r * 1.4, 0.02, T((0, 0, L - 0.01)), mat="bark" if _tier(e) != "high" else "fit", segs=7, bevel=0)
        elif g == "Gale":  # clay fire cup with a zig band
            p.lathe([(r, top), (r * 2.4, top + (L - top) * 0.6), (r * J(p, 2.8, 0.1), L), (r * 2.4, L + 0.004)], mat="clay" if e in HAND else "fit", segs=8)
            zig(p, r * 2.4, top + (L - top) * 0.55, 0.02, 6)
        elif g == "Radiant":  # mashaal: brass cup with a lotus rim, cloth wad
            p.lathe([(r, top), (r * 1.6, top + 0.03), (r * 1.3, top + 0.06), (r * 2.4, L)], mat="fit", segs=8)
            petals(p, r * 2.3, L - 0.01, 6, r * 0.8, mat="accent", tilt=55)
        else:
            if e == "Primal":
                p.ball(r * 2.2, M(loc=(0, 0, top + 0.04), scale=(1, 1, 1.6)), mat="iron", segs=(6, 4), noise=0.1)
            elif e == "Industrial":  # deco flashlight head
                steps(p, r * 2.0, r * 2.0, top, 3, (L - top) / 3, mat="chrome", shrink=1.18)
            elif e == "Future":
                p.box((r * 3, r * 2.4, L - top), T((0, 0, (L + top) / 2)), mat="body", bevel=0.3)
            elif e == "Steampunk":
                p.cyl(r * 1.6, r * 2.4, L - top, T((0, 0, top)), mat="brass", segs=8, bevel=0)
                gear(p, r * 1.2, M(loc=(r * 2.2, 0, top + (L - top) * 0.5), rot=(0, 90, 0)))
            else:
                p.cyl(r * 1.6, r * 2.0, L - top, T((0, 0, top)), mat="metal", segs=8, bevel=0)
    elif slot == "light":
        if g == "Metropolis" and e in ("Industrial", "Future"):
            p.cyl(r * 2.1, r * 2.1, 0.008, T((0, 0, L)), mat=lit(p, True), segs=8, bevel=0)
        else:
            bulb(p, 0, 0, L, J(p, 0.05, 0.15), electric=False if g != "Metropolis" else None)
    else:
        if g == "Ocean":
            horn(p, 0, 0, 0.0, 0.03, 1, mat="accent")
        elif g == "Gale":
            pegs(p, r * 1.2, top * 0.35, 4, r * 1.4)
        elif g == "Radiant":
            p.lathe([(0, -0.02), (r * 1.4, -0.01), (r * 1.2, 0.01)], mat="fit", segs=7)
        else:
            p.band(r * 1.15, top * 0.3, h=0.05)
        mark(p, r * 1.2, top * 0.6)


# ================================================================ Lantern (sits on z = 0, hangs by its mount)


def lantern(p, slot):
    e, g = p.era, p.region
    h = F(p, {"Primal": 0.18, "Agrarian": 0.3, "Mercantile": 0.26, "Industrial": 0.28, "Steampunk": 0.28,
              "Future": 0.22, "Wasteland": 0.22, "Ancient": 0.26}[e], 0.1)
    r = F(p, {"Agrarian": 0.1, "Future": 0.07}.get(e, 0.075), 0.1)
    zl, zt = h * 0.12, h * 0.82  # glowing drum between base and cap
    if slot == "body":  # base and cap
        if g == "Radiant":
            p.lathe([(r * 0.6, 0), (r * 1.1, 0.01), (r * 1.05, zl)], mat="fit", segs=8)
        elif g == "Gale":
            p.cyl(r * 1.1, r, zl, mat="clay" if e in HAND else "body", segs=8, bevel=0)
        else:
            p.cyl(r * 1.05, r * 1.05, zl, mat="body" if g == "Ocean" or e not in ("Future",) else "fit", segs=8, bevel=0)
        p.cyl(r * 1.0, r * 0.9, h * 0.05, T((0, 0, zt)), mat="body", segs=8, bevel=0)
    elif slot == "light":  # the lit drum (paper, glass, crystal)
        if g == "Ocean":
            p.lathe([(r * 0.85, zl), (r * 1.0, (zl + zt) / 2), (r * 0.85, zt)], mat=lit(p, _electric(p)), segs=8)
        elif g == "Radiant":
            p.cyl(r * 0.85, r * 0.85, zt - zl, T((0, 0, zl)), mat=lit(p, _electric(p)), segs=6, bevel=0)
        else:
            p.cyl(r * 0.8, r * 0.85, zt - zl, T((0, 0, zl)), mat=lit(p, _electric(p)), segs=8, bevel=0)
    elif slot == "shade":  # cage and roof
        if g == "Ocean":  # bamboo ribs and a horned cap
            for i in range(6):
                a = i * math.tau / 6
                p.cyl(0.004, 0.004, zt - zl, T((math.cos(a) * r * 0.98, math.sin(a) * r * 0.98, zl)), mat="fit", segs=3, bevel=0)
            for s in (-1, 1):
                horn(p, s * r * 0.9, 0, zt + h * 0.04, h * 0.12, s, mat="accent")
        elif g == "Gale":  # cone roof with pegs
            p.cyl(r * 1.15, 0.0, h * 0.3, T((0, 0, zt + h * 0.04)), mat="clay" if e in HAND else "fit", segs=7, bevel=0)
            pegs(p, r * 0.8, zt + h * 0.1, 5, r * 0.4, mat="body")
        elif g == "Radiant":  # dome on a petal collar
            petals(p, r * 0.9, zt + h * 0.02, 6, r * 0.25, mat="accent", tilt=70)
            dome(p, r * 0.85, zt + h * 0.05, mat="fit", segs=8)
        else:
            if e == "Industrial":
                steps(p, r * 2.0, r * 2.0, zt + h * 0.04, 3, h * 0.05, mat="chrome", shrink=0.75)
            elif e == "Future":
                p.cyl(r * 1.0, r * 1.0, h * 0.06, T((0, 0, zt + h * 0.04)), mat="fit", segs=8, bevel=0)
            else:  # cast-iron frame posts and a pyramid cap
                for i in range(4):
                    a = i * math.tau / 4 + math.pi / 4
                    p.cyl(0.005, 0.005, zt - zl, T((math.cos(a) * r * 0.95, math.sin(a) * r * 0.95, zl)), mat="metal", segs=4, bevel=0)
                p.cyl(r * 1.15, 0.01, h * 0.18, T((0, 0, zt + h * 0.04)), mat="metal", segs=4, bevel=0)
    else:  # how it is carried
        zc = zt + h * 0.22
        if g == "Ocean":
            bail(p, r * 0.7, zc - h * 0.12, h * 0.4, r=0.004, mat="fit")
        elif g == "Gale":
            p.ring(r * 0.35, 0.006, M(loc=(0, 0, zc + h * 0.15), rot=(90, 0, 0)), mat="grip", segs=8, square=False)
        elif g == "Radiant":
            p.tube([(0, 0, zc), (0, 0, zc + h * 0.4)], 0.003, mat="fit", segs=4)
            p.ring(0.012, 0.003, M(loc=(0, 0, zc + h * 0.45), rot=(90, 0, 0)), mat="fit", segs=6)
        else:
            bail(p, r * 0.8, zc - h * 0.12, h * 0.35, r=0.004, mat="metal")
        mark(p, r * 1.05, zl * 0.5)


# ================================================================ Candlestand (scene)


def candlestand(p, slot):
    e, g = p.era, p.region
    h = F(p, {"Primal": 0.16, "Agrarian": 0.12, "Mercantile": 0.36, "Industrial": 0.5, "Steampunk": 0.42,
              "Future": 0.34, "Wasteland": 0.38, "Ancient": 0.42}[e], 0.1)
    w = F(p, {"Mercantile": 0.13, "Industrial": 0.16, "Wasteland": 0.12}.get(e, 0.1), 0.1)
    if slot == "mount":  # base
        if g == "Radiant":  # lotus base
            p.lathe([(w * 1.1, 0), (w * 1.0, 0.02), (w * 0.4, 0.04)], mat="fit", segs=10)
            petals(p, w * 0.8, 0.0, 8, w * 0.25, mat="accent", tilt=60)
        elif g == "Gale":
            p.cyl(w * 1.0, w * 0.9, 0.04, mat="body", segs=7, bevel=0)
            zig(p, w * 0.95, 0.02, 0.03, 8)
        elif g == "Ocean":
            p.lathe([(0, 0), (w * 0.95, 0.005), (w, 0.03), (w * 0.4, 0.035)], mat="bark" if e in HAND else "body", segs=10)
        else:
            if e == "Industrial":
                steps(p, w * 2, w * 2, 0, 3, 0.02, mat="body", shrink=0.75)
            elif e == "Primal":
                p.ball(w * 1.2, M(loc=(0, 0, 0.02), scale=(1, 0.9, 0.25)), mat="iron", segs=(7, 4), noise=0.08)
            else:
                p.cyl(w, w * 0.9, 0.03, mat="metal" if e != "Future" else "body", segs=8, bevel=0)
    elif slot == "body":  # stem
        if g == "Ocean":
            _shaft(p, h * 0.85, w * 0.22, w * 0.2, segs=6)
        elif g == "Gale":
            p.cyl(w * 0.3, w * 0.2, h * 0.85, mat="body", segs=6, bevel=0)
            pegs(p, w * 0.25, h * 0.5, 4, w * 0.35)
        elif g == "Radiant":  # samai column with knops
            p.lathe([(w * 0.25, 0.04), (w * 0.4, h * 0.2), (w * 0.2, h * 0.35), (w * 0.35, h * 0.55), (w * 0.2, h * 0.7), (w * 0.3, h * 0.85)],
                    mat="fit", segs=8)
        else:
            if e == "Future":
                p.box((w * 0.3, w * 0.3, h * 0.85), T((0, 0, h * 0.425)), mat="body", bevel=0.3)
            else:
                p.cyl(w * 0.15, w * 0.15, h * 0.85, mat="metal" if e != "Primal" else "iron", segs=6, bevel=0)
    elif slot == "shade":  # the dish or cup that holds the light
        z = h * 0.85
        if g == "Radiant":  # tiered diya dish
            p.lathe([(w * 0.2, z), (w * 0.9, z + 0.02), (w * 0.95, z + 0.035)], mat="fit", segs=10)
            p.lathe([(w * 0.2, h * 0.45), (w * 0.6, h * 0.47), (w * 0.62, h * 0.49)], mat="fit", segs=8)
        elif g == "Ocean":  # coconut-shell saucer under a leaf crown
            p.lathe([(w * 0.2, z), (w * 0.7, z + 0.01), (w * 0.8, z + 0.04)], mat="bark" if e in HAND else "accent", segs=8)
            leaf_crown(p, 4, z + 0.02, z + 0.08, w * 0.5, w * 0.8, w * 0.4, 0.003, mat="fit")
        elif g == "Gale":
            p.lathe([(w * 0.25, z), (w * 0.6, z + 0.03), (w * 0.55, z + 0.05)], mat="clay" if e in HAND else "fit", segs=8)
        else:
            if e == "Industrial":
                p.cyl(w * 0.4, w * 0.25, 0.04, T((0, 0, z)), mat="chrome", segs=8, bevel=0)
            else:
                p.lathe([(w * 0.15, z), (w * 0.5, z + 0.01), (w * 0.3, z + 0.03)], mat="metal" if e != "Future" else "fit", segs=8)
    else:  # light
        z = h * 0.85
        if g == "Radiant":  # five wicks on the top dish, three on the lower
            for i in range(5):
                a = i * math.tau / 5
                flame(p, math.cos(a) * w * 0.7, math.sin(a) * w * 0.7, z + 0.035, 0.012, mat=lit(p), segs=5)
            for i in range(3):
                a = i * math.tau / 3 + 0.5
                flame(p, math.cos(a) * w * 0.5, math.sin(a) * w * 0.5, h * 0.49, 0.01, mat=lit(p), segs=5)
        elif g == "Metropolis" and _tier(e) != "hand":
            p.cyl(w * 0.12, w * 0.12, 0.06, T((0, 0, z + 0.03)), mat="bone" if e != "Future" else "fit", segs=6, bevel=0)
            bulb(p, 0, 0, z + 0.09, 0.015)
        else:
            p.cyl(w * 0.16, w * 0.15, J(p, 0.08, 0.25), T((0, 0, z + 0.02)), mat="bone", segs=6, bevel=0)
            flame(p, 0, 0, z + 0.02 + 0.085, 0.014, mat=lit(p), segs=6)


# ================================================================ Streetlamp (scene)


def streetlamp(p, slot):
    e, g = p.era, p.region
    H = F(p, {"Primal": 2.4, "Agrarian": 2.2, "Mercantile": 3.0, "Industrial": 4.0, "Steampunk": 3.5,
              "Future": 3.8, "Wasteland": 3.3, "Ancient": 3.2}[e], 0.08)
    r = F(p, {"Primal": 0.12, "Agrarian": 0.12, "Ancient": 0.14}.get(e, 0.08), 0.1)
    if slot == "mount":
        if g == "Ocean":  # stone footing, or a float in the future
            if e == "Future":
                p.ball(r * 3, M(loc=(0, 0, r), scale=(1, 1, 0.5)), mat="fit", segs=(8, 4))
            else:
                p.cyl(r * 2.5, r * 2.2, 0.15, mat="stone", segs=7, bevel=0, noise=0.03)
        elif g == "Gale":  # mud plinth
            p.box((r * 5, r * 5, 0.35), T((0, 0, 0.175)), mat="clay" if e in HAND else "body", bevel=0)
            zig(p, r * 2.6, 0.25, 0.08, 8)
        elif g == "Radiant":  # lotus plinth
            p.lathe([(r * 3, 0), (r * 3, 0.12), (r * 1.5, 0.25)], mat="body", segs=10)
            petals(p, r * 2, 0.18, 8, r * 0.8, mat="accent", tilt=50)
        else:
            if e == "Industrial":
                steps(p, r * 5, r * 5, 0, 3, 0.12, mat="body", shrink=0.75)
            elif e == "Primal":
                for i in range(5):
                    a = i * math.tau / 5
                    p.ball(r * J(p, 1.1, 0.2), M(loc=(math.cos(a) * r * 1.6, math.sin(a) * r * 1.6, r * 0.5), scale=(1, 1, 0.7)), mat="iron", segs=(5, 4), noise=0.08)
            else:
                p.cyl(r * 2.2, r * 1.6, 0.3, mat="metal" if e != "Future" else "body", segs=8, bevel=0)
    elif slot == "body":  # pole or pillar
        if g == "Ocean":
            _shaft(p, H * 0.95, r * 0.9, r * 0.75, segs=7)
        elif g == "Gale":
            p.cyl(r * 1.8, r * 1.1, H * 0.85, T((0, 0, 0.35)), mat="clay" if e in HAND else "body", segs=7, bevel=0)
            for z in (0.4, 0.65):
                pegs(p, r * 1.4, H * z, 4, r * 1.2, mat="body")
        elif g == "Radiant":  # deepastambha: turned pillar with dish tiers
            p.lathe([(r * 1.4, 0.25), (r, H * 0.3), (r * 0.8, H * 0.9)], mat="body", segs=8)
            for k in (0.35, 0.55, 0.75):
                p.lathe([(r * 0.8, H * k), (r * 2.4, H * k + 0.04), (r * 2.5, H * k + 0.07)], mat="fit", segs=8)
        else:
            if e == "Future":
                p.box((r * 1.2, r * 1.8, H), T((0, 0, H / 2)), mat="body", bevel=0.3)
                p.box((r * 0.2, r * 1.85, H * 0.8), T((0, 0, H * 0.5)), mat="glow", bevel=0)
            elif e == "Industrial":
                p.cyl(r * 0.8, r * 0.55, H, mat="body", segs=8, bevel=0)
            else:
                p.cyl(r, r * 0.7, H * 0.95, mat="metal" if e not in ("Primal",) else "iron", segs=8 if e != "Primal" else 5, bevel=0,
                      noise=0.04 if e == "Primal" else 0)
    elif slot == "shade":  # arm, cage and roof
        if g == "Ocean":  # horn-curl bracket with a lantern and a small saddle cap
            p.tube([(0, 0, H * 0.92), (0, -0.25, H * 0.98), (0, -0.4, H * 0.94)], r * 0.35, mat="body", segs=5)
            horn(p, 0, 0, H * 0.95, 0.15, -1, mat="accent")
            for s in (-1, 1):
                p.box((0.22, 0.12, 0.012), M(loc=(0, -0.4 + s * 0.05, H * 0.9), rot=(s * 30, 0, 0)), mat="fit", bevel=0)
        elif g == "Gale":  # fire bowl under a cone
            p.lathe([(r * 1.1, H * 0.85 + 0.35), (r * 3, H * 0.95), (r * 3.2, H)], mat="clay" if e in HAND else "fit", segs=8)
            p.cyl(r * 0.5, 0.0, 0.4, T((0, 0, H + 0.25)), mat="body", segs=5, bevel=0)
            for s in (-1, 1):
                p.cyl(0.02, 0.02, 0.27, T((s * r * 2.5, 0, H)), mat="body", segs=4, bevel=0)
        elif g == "Radiant":  # chhatri top
            for i in range(4):
                a = i * math.tau / 4 + math.pi / 4
                p.cyl(0.02, 0.02, 0.35, T((math.cos(a) * r * 2, math.sin(a) * r * 2, H * 0.9)), mat="fit", segs=4, bevel=0)
            dome(p, r * 2.6, H * 0.9 + 0.35, mat="fit", segs=8)
        else:
            if e == "Industrial":  # deco globe on a stepped collar
                steps(p, r * 3, r * 3, H, 3, 0.06, mat="chrome", shrink=0.75)
            elif e == "Future":  # cantilever light bar
                p.box((0.06, 0.9, 0.05), T((0, -0.4, H)), mat="body", bevel=0.3)
            else:  # gas lamp: arm, glass box, pyramid cap
                p.tube([(0, 0, H * 0.93), (0, -0.3, H * 0.98)], 0.02, mat="metal", segs=5)
                p.cyl(0.16, 0.02, 0.15, T((0, -0.3, H * 0.98 + 0.25)), mat="metal", segs=4, bevel=0)
                if e == "Steampunk":
                    gear(p, 0.08, M(loc=(0.05, 0, H * 0.8), rot=(0, 90, 0)))
    else:  # light
        if g == "Ocean":
            p.lathe([(0.06, H * 0.8), (0.09, H * 0.85), (0.06, H * 0.9)], T((0, -0.4, 0)), mat=lit(p, _electric(p)), segs=8)
        elif g == "Gale":
            bulb(p, 0, 0, H, 0.12, electric=False)
        elif g == "Radiant":
            for k in (0.55, 0.75):
                for i in range(4):
                    a = i * math.tau / 4
                    flame(p, math.cos(a) * r * 2.2, math.sin(a) * r * 2.2, H * k + 0.06, 0.02, mat=lit(p), segs=5)
            bulb(p, 0, 0, H * 0.9, 0.07, electric=False)
        else:
            if e == "Industrial":
                p.ball(0.14, T((0, 0, H + 0.32)), mat=lit(p, True), segs=(8, 6))
            elif e == "Future":
                p.box((0.04, 0.8, 0.012), T((0, -0.4, H - 0.03)), mat=lit(p), bevel=0)
            elif e == "Primal":
                flame(p, 0, 0, H * 0.95, 0.14, mat=lit(p), segs=6)
            else:
                p.box((0.14, 0.14, 0.22), T((0, -0.3, H * 0.98 + 0.12)), mat=lit(p, _electric(p)), bevel=0)
        if g != "Metropolis":
            mark(p, r * 1.2, H * 0.3)


# ================================================================ Headlamp (worn: R is the head radius)


def headlamp(p, slot):
    e, g = p.era, p.region
    R = F(p, 0.095, 0.06)
    z = F(p, {"Agrarian": 0.06, "Mercantile": 0.05, "Industrial": 0.06, "Wasteland": 0.06}.get(e, 0.04), 0.1)
    fy = -R * 1.1
    if slot == "body":  # band, cap or wrap on the head
        if g == "Radiant":  # turban wrap
            for i in range(2):
                p.ring(R * (1.02 - i * 0.05), 0.016, M(loc=(0, 0, 0.015 + i * 0.025), rot=(J(p, 6, 0.8) * (1 if i else -1), 0, 0)), mat="cloth", segs=10, square=False)
        elif g == "Metropolis" and e in ("Industrial", "Steampunk", "Wasteland"):  # hard hat
            p.lathe([(R * 1.2, 0.0), (R * 1.05, 0.02), (R * 0.95, 0.08), (R * 0.5, 0.13), (0, 0.14)], mat="paint" if e == "Industrial" else "metal", segs=10)
        else:
            p.ring(R, J(p, 0.01, 0.25), T((0, 0, 0.015)), mat="grip" if g != "Ocean" else "fit", segs=10)
            if g == "Gale":
                zig(p, R * 1.02, 0.015, 0.02, 8)
    elif slot == "shade":  # lamp housing on the forehead
        if g == "Ocean":  # short bamboo tube lamp
            p.cyl(0.02, 0.022, 0.05, M(loc=(0, fy + 0.02, z), rot=(90, 0, 0)), mat="body", segs=6, bevel=0)
            lash(p, 0.021, 0, 0.012, M(loc=(0, fy, z), rot=(90, 0, 0)), segs=6)
        elif g == "Gale":  # small gourd lamp
            p.ball(0.026, M(loc=(0, fy - 0.01, z), scale=(1, 1.2, 1)), mat="gourd" if e in HAND else "fit", segs=(6, 4))
        elif g == "Radiant":  # brass lotus cup
            p.lathe([(0, 0), (0.025, 0.006), (0.03, 0.025)], M(loc=(0, fy - 0.02, z - 0.01)), mat="fit", segs=8)
            petals(p, 0.022, 0.02, 5, 0.008, M(loc=(0, fy - 0.02, z - 0.01)), mat="accent", tilt=50)
        else:
            if e == "Future":
                p.box((R * 1.4, 0.02, 0.025), T((0, -R * 1.02, z)), mat="body", bevel=0.3)
            elif e == "Industrial":
                steps(p, 0.05, 0.03, z - 0.02, 3, 0.012, M(loc=(0, fy - 0.015, 0)), mat="chrome", shrink=0.8)
            else:
                p.cyl(0.024, 0.03, 0.04, M(loc=(0, fy + 0.015, z), rot=(90, 0, 0)), mat="metal", segs=8, bevel=0)
    elif slot == "light":
        if g == "Metropolis" and e == "Future":
            p.box((R * 1.2, 0.022, 0.008), T((0, -R * 1.03, z)), mat=lit(p), bevel=0)
        elif g in ("Ocean", "Metropolis") and (_electric(p) or _tier(e) == "high"):
            p.cyl(0.018, 0.018, 0.005, M(loc=(0, fy - 0.03, z), rot=(90, 0, 0)), mat=lit(p, True), segs=8, bevel=0)
        else:
            flame(p, 0, fy - 0.02, z + 0.012, 0.012, mat=lit(p, _electric(p)), segs=6)
    else:  # back of the head: knot, battery or counterweight
        if g == "Ocean":
            p.ball(0.012, T((0, R * 1.02, 0.015)), mat="fit", segs=(5, 3))
            p.tube([(0, R * 1.05, 0.015), (0.01, R * 1.1, -0.04)], 0.003, mat="fit", segs=3)
        elif g == "Gale":
            for s in (-1, 1):
                p.ball(0.01, T((s * R * 0.7, -R * 0.7, 0.015)), mat="accent", segs=(4, 3))
            p.tube([(0.03, R * 1.0, 0.02), (0.05, R * 1.1, 0.09)], 0.004, mat="feather", segs=4)
        elif g == "Radiant":
            p.ball(0.014, T((0, -R * 1.02, 0.05)), mat="accent", segs=(5, 3))
        else:
            if _tier(e) == "hand":
                p.ball(0.012, T((0, R * 1.02, 0.015)), mat="iron", segs=(5, 3))
            else:
                p.box((0.06, 0.025, 0.04), T((0, R * 1.05, 0.03)), mat="metal" if e != "Future" else "body", bevel=0)
        mark(p, R, 0.015)


# ================================================================ Censer (carried, sits on z = 0)


def censer(p, slot):
    e, g = p.era, p.region
    h = F(p, {"Primal": 0.08, "Mercantile": 0.12, "Steampunk": 0.16, "Future": 0.14}.get(e, 0.12), 0.1)
    r = F(p, {"Primal": 0.08, "Agrarian": 0.075, "Industrial": 0.07, "Wasteland": 0.05}.get(e, 0.06), 0.1)
    zb = h * 0.25  # bowl bottom (above the feet)
    if slot == "body":  # bowl
        if g == "Ocean":  # coconut-shell bowl
            p.lathe([(0, zb), (r * 0.8, zb + 0.005), (r, zb + h * 0.35), (r * 0.9, zb + h * 0.55)], mat="bark" if e in HAND else "body", segs=8)
        elif g == "Gale":  # clay pot with a side handle
            p.lathe([(0, zb), (r * 0.9, zb + 0.01), (r * 1.05, zb + h * 0.35), (r * 0.7, zb + h * 0.55)], mat="clay" if e in HAND else "body", segs=8)
            p.tube([(r * 0.9, 0, zb + h * 0.3), (r * 1.6, 0, zb + h * 0.35), (r * 2.4, 0, zb + h * 0.5)], 0.008, mat="clay" if e in HAND else "body", segs=5)
        elif g == "Radiant":  # dhoop dani: brass bowl with a long handle
            p.lathe([(0, zb), (r * 0.9, zb + 0.005), (r, zb + h * 0.4), (r * 1.05, zb + h * 0.45)], mat="fit", segs=8)
            p.tube([(r, 0, zb + h * 0.3), (r * 2.6, 0, zb + h * 0.4)], 0.007, mat="fit", segs=5)
        else:
            if e == "Industrial":
                steps(p, r * 2, r * 2, zb, 3, h * 0.15, mat="body", shrink=0.85)
            elif e == "Future":
                p.lathe([(0, zb), (r, zb + 0.01), (r, zb + h * 0.45)], mat="body", segs=8)
            else:
                p.lathe([(0, zb), (r * 0.9, zb + 0.005), (r, zb + h * 0.45)], mat="metal" if e != "Primal" else "iron", segs=8, noise=0.05 if e == "Primal" else 0)
    elif slot == "light":  # embers or incense tips
        n = 3 if e in HAND else 2
        for i in range(n):
            a = i * math.tau / n + J(p, 0.3, 0.5)
            p.ball(r * J(p, 0.2, 0.3), T((math.cos(a) * r * 0.35, math.sin(a) * r * 0.35, zb + h * 0.5)), mat=lit(p), segs=(5, 3))
    elif slot == "shade":  # lid
        zl = zb + h * 0.55
        if g == "Ocean":  # shell lid with a horn knob
            p.lathe([(r * 0.92, zl), (r * 0.6, zl + h * 0.25), (0, zl + h * 0.3)], mat="bark" if e in HAND else "accent", segs=8)
            horn(p, 0, 0, zl + h * 0.28, h * 0.25, 1, mat="accent")
        elif g == "Gale":  # pierced cone with pegs
            p.cyl(r * 0.75, 0.0, h * 0.6, T((0, 0, zl)), mat="clay" if e in HAND else "fit", segs=6, bevel=0)
            pegs(p, r * 0.45, zl + h * 0.2, 4, r * 0.3)
        elif g == "Radiant":
            dome(p, r * 0.9, zl, mat="fit", segs=8)
        else:
            if e == "Industrial":
                steps(p, r * 1.4, r * 1.4, zl, 2, h * 0.12, mat="chrome", shrink=0.7)
            elif e == "Future":
                p.ring(r * 0.95, 0.006, T((0, 0, zl)), mat="glow", segs=8)
            else:
                p.lathe([(r, zl), (r * 0.5, zl + h * 0.3), (r * 0.1, zl + h * 0.45)], mat="metal" if e != "Primal" else "iron", segs=8)
    else:  # feet or chains
        if g == "Ocean":  # three bamboo legs lashed
            for i in range(3):
                a = i * math.tau / 3
                p.tube([(math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, zb + 0.01), (math.cos(a) * r * 0.9, math.sin(a) * r * 0.9, 0)], 0.006, mat="body", segs=4)
        elif g == "Gale":
            p.cyl(r * 0.6, r * 0.8, zb, mat="clay" if e in HAND else "body", segs=7, bevel=0)
        elif g == "Radiant":
            petals(p, r * 0.6, 0.0, 6, r * 0.25, mat="accent", tilt=60)
            p.cyl(r * 0.5, r * 0.7, zb, mat="fit", segs=8, bevel=0)
        else:
            if e in ("Mercantile", "Steampunk", "Ancient"):  # thurible chains
                for i in range(3):
                    a = i * math.tau / 3
                    p.tube([(math.cos(a) * r, math.sin(a) * r, zb + h * 0.45), (0, 0, zb + h * 2.2)], 0.002, mat="metal", segs=3)
                p.cyl(r * 0.5, r * 0.6, zb, mat="metal", segs=6, bevel=0)
            else:
                p.cyl(r * 0.5, r * 0.7, zb, mat="body" if e == "Future" else "metal", segs=7, bevel=0)
        mark(p, r * 1.02, zb + h * 0.2)


for _g in REGIONS:
    regional("Torch", _g)(torch)
    regional("Lantern", _g)(lantern)
    regional("Candlestand", _g)(candlestand)
    regional("Streetlamp", _g)(streetlamp)
    regional("Headlamp", _g)(headlamp)
    regional("Censer", _g)(censer)
