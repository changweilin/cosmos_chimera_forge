"""Four-planet forms of the pilot functions (cosmos_chimera everyday-objects.md#四星球形體, Q-A38 batch 1).

Hoe, Hammer, Pickaxe, Communicator, GameConsole, Timepiece, Barrel, Jar, Crate, each for Ocean (東南亞), Gale (非洲),
Radiant (南亞) and Metropolis (世界都市＋星際宙域) in all 8 eras. Vocabulary: planet-world.md#四星球時代造型.
Same slots, frames and budgets as the shared forms in kit_forms.py, so the game assembles them the same way.

Devices keep the spec's form-era rule (the mechanism reads as its era) by grouping eras into three tiers:
hand-made (Primal, Agrarian, Mercantile), machine (Industrial, Steampunk, Wasteland) and high-tech (Future, Ancient).
Each region has its own mechanism per tier; eras inside a tier differ by craft and their own details.
"""
import math

from mathutils import Matrix

from kit_forms import F, J, coin, regional
from kit_lib import M, REGIONS

T = Matrix.Translation
HAND = ("Primal", "Agrarian", "Mercantile")
MACHINE = ("Industrial", "Steampunk", "Wasteland")


# ---------------------------------------------------------------- regional signatures


def lash(p, r, z, h=0.03, m=None, segs=8):
    """Ocean: crossed rattan lashing, two wraps tilted against each other."""
    base = (m or Matrix()) @ T((0, 0, z))
    for a in (-9, 9):
        p.ring(r * 1.04, h * 0.22, base @ M(rot=(a, 0, 0)), mat="fit", segs=segs)


def horn(p, x, y, z, s, side=1, mat="accent"):
    """Ocean: an upswept horn tip (the saddle-roof gable end) curling outward along x."""
    p.tube([(x, y, z), (x + side * s * 0.5, y, z + s * 0.25), (x + side * s * 0.8, y, z + s * 0.75),
            (x + side * s * 0.7, y, z + s * 1.1)], s * 0.1, mat=mat, segs=5)


def pegs(p, r, z, n, L, m=None, mat="fit"):
    """Gale: beam ends bristling out of a round part."""
    base = (m or Matrix()) @ T((0, 0, z))
    for i in range(n):
        a = i * math.tau / n
        p.cyl(L * 0.18, L * 0.15, L, base @ M(loc=(math.cos(a) * r * 0.9, math.sin(a) * r * 0.9, 0), rot=(0, 90, math.degrees(a))),
              mat=mat, segs=4, bevel=0)


def zig(p, r, z, h, n, m=None, mats=("accent", "fit")):
    """Gale: painted geometric band, alternating tilted tiles read as a zigzag at game distance."""
    base = (m or Matrix()) @ T((0, 0, z))
    w = math.tau * r / n
    for i in range(n):
        a = i * math.tau / n
        p.box((w * 0.9, h * 0.08, h), base @ M(loc=(math.cos(a) * r, math.sin(a) * r, 0), rot=(0, 30 if i % 2 else -30, math.degrees(a) + 90)),
              mat=mats[i % 2], bevel=0)


def dome(p, r, z, m=None, mat="fit", finial=True, segs=10):
    """Radiant: onion dome with a kalasha finial."""
    base = (m or Matrix()) @ T((0, 0, z))
    p.lathe([(r, 0), (r * 1.08, r * 0.35), (r * 0.7, r * 0.8), (r * 0.15, r * 1.1), (0, r * 1.2)], base, mat=mat, segs=segs)
    if finial:
        p.cyl(r * 0.08, 0.0, r * 0.5, base @ T((0, 0, r * 1.15)), mat="accent", segs=5, bevel=0)
        p.ball(r * 0.12, base @ T((0, 0, r * 1.3)), mat="accent", segs=(5, 3))


def petals(p, r, z, n, s, m=None, mat="accent", tilt=40):
    """Radiant: lotus petals around a round part."""
    base = (m or Matrix()) @ T((0, 0, z))
    for i in range(n):
        a = i * math.tau / n
        p.ball(s, base @ M(loc=(math.cos(a) * r, math.sin(a) * r, s * 0.4), rot=(0, -tilt, math.degrees(a)), scale=(0.45, 0.8, 1.4)),
               mat=mat, segs=(5, 3))


def fins(p, r, z0, z1, n, m=None, mat="fit", depth=None):
    """Metropolis: vertical fins between tall glazing."""
    base = m or Matrix()
    d = depth or r * 0.18
    for i in range(n):
        a = i * math.tau / n
        p.box((d, r * 0.06, z1 - z0), base @ M(loc=(math.cos(a) * (r + d * 0.4), math.sin(a) * (r + d * 0.4), (z0 + z1) / 2), rot=(0, 0, math.degrees(a))),
              mat=mat, bevel=0)


def steps(p, w, d, z, n, dz, m=None, mat="fit", shrink=0.78):
    """Metropolis: art-deco setbacks, n tiers shrinking upward."""
    base = m or Matrix()
    for i in range(n):
        f = shrink ** i
        p.box((w * f, d * f, dz), base @ T((0, 0, z + dz * (i + 0.5))), mat=mat, bevel=0)


def gear(p, r, m, mat="brass", teeth=6):
    """Steampunk token: a toothed wheel lying in the matrix's XY plane."""
    p.cyl(r, r, r * 0.25, m, mat=mat, segs=teeth, bevel=0)
    for i in range(teeth):
        a = (i + 0.5) * math.tau / teeth
        p.box((r * 0.25, r * 0.22, r * 0.22), m @ M(loc=(math.cos(a) * r * 1.05, math.sin(a) * r * 1.05, r * 0.12), rot=(0, 0, math.degrees(a))),
              mat=mat, bevel=0)


def era_mark(p, r, z, m=None):
    """The era's own small token on a round part (rivets, a gear, a glow seam, a patch, rune slits)."""
    e = p.era
    base = (m or Matrix()) @ T((0, 0, z))
    if e == "Industrial":
        for i in range(4):
            a = i * math.tau / 4 + 0.3
            p.ball(r * 0.09, base @ T((math.cos(a) * r, math.sin(a) * r, 0)), mat="metal", segs=(4, 3))
    elif e == "Steampunk":
        gear(p, r * 0.32, base @ M(loc=(0, -r * 1.02, 0), rot=(90, 0, 0)), mat="brass")
    elif e == "Future":
        p.ring(r * 1.01, r * 0.05, base, mat="glow", segs=10)
    elif e == "Wasteland":
        p.box((r * 0.8, r * 0.06, r * 0.6), base @ M(loc=(r * 0.2, -r * 0.98, 0), rot=(0, J(p, 9, 0.6), 0)), mat="metal", bevel=0)
        p.tube([(-r, -r * 0.4, 0), (-r * 1.1, -r * 0.8, r * 0.3), (-r * 0.6, -r * 1.05, r * 0.5)], r * 0.04, mat="rubber", segs=4)
    elif e == "Ancient":
        for i in range(3):
            a = i * math.tau / 3 + 0.6
            p.box((r * 0.2, r * 0.05, r * 0.5), base @ M(loc=(math.cos(a) * r * 1.0, math.sin(a) * r * 1.0, 0), rot=(0, 0, math.degrees(a) + 90)),
                  mat="glow", bevel=0)


def signature(p, r, z, h=0.04, m=None):
    """The region's binding on a round part."""
    g = p.region
    if g == "Ocean":
        lash(p, r, z, h, m)
    elif g == "Gale":
        zig(p, r * 1.02, z, h, 8, m)
    elif g == "Radiant":
        base = (m or Matrix()) @ T((0, 0, z))
        p.ring(r * 1.03, h * 0.18, base, mat="fit", segs=10)
        p.ring(r * 1.03, h * 0.12, base @ T((0, 0, h * 0.5)), mat="accent", segs=10, square=False)
    else:
        base = (m or Matrix()) @ T((0, 0, z))
        p.ring(r * 1.02, h * 0.3, base, mat="fit", segs=8)
        if p.era not in HAND:
            p.ring(r * 1.04, h * 0.08, base @ T((0, 0, h * 0.4)), mat="metal", segs=8)


# ---------------------------------------------------------------- hafted (head, haft, joint, butt)


def r_haft(p, L, r):
    g, e = p.region, p.era
    if g == "Ocean":
        # Bamboo: straight culm with raised nodes; later eras keep the jointed silhouette in their own material.
        p.cyl(r, r * 0.94, L, mat="body", segs=7 if e == "Primal" else 8, bevel=0)
        n = 3 if e != "Future" else 2
        for i in range(n):
            z = L * (0.18 + i * (0.7 / n)) * J(p, 1, 0.06)
            p.cyl(r * 1.1, r * 1.1, r * 0.55, T((0, 0, z)), mat="body", segs=7, bevel=0)
        if e == "Future":
            p.cyl(r * 0.4, r * 0.4, L * 0.8, T((0, 0, L * 0.08)), mat="glow", segs=6, bevel=0)
        elif e == "Wasteland":
            p.tube([(r * math.cos(t * 2.4), r * math.sin(t * 2.4), L * (0.1 + t * 0.06)) for t in range(5)], r * 0.18, mat="fit", segs=3)
        elif e == "Mercantile":
            p.cyl(r * 1.08, r * 1.08, L * J(p, 0.12, 0.2), T((0, 0, L * 0.86)), mat="gold", segs=8, bevel=0)
    elif g == "Gale":
        # Carved stick swelling into the knob that the blade's tang passes through.
        top = L * 0.86
        p.cyl(r * 0.95, r * 1.1, top, mat="body", segs=7, bevel=0)
        p.ball(r * J(p, 2.2, 0.12), M(loc=(0, 0, L * 0.94), scale=(1, 1, 1.25)), mat="body", segs=(7, 5))
        if e == "Future":
            for i in range(4):
                p.ring(r * 1.08, r * 0.2, T((0, 0, L * (0.1 + i * 0.07))), mat="fit", segs=7)
        elif e == "Wasteland":
            p.cyl(r * 1.4, r * 1.4, L * 0.16, T((0, 0, L * 0.04)), mat="rubber", segs=7, bevel=0)
        else:
            zig(p, r * 1.02, L * J(p, 0.22, 0.2), r * 3, 6)
    elif g == "Radiant":
        # Lathe-turned: bead-and-reel collars along the shaft.
        prof = [(r, 0)]
        for i in range(3):
            z = L * (0.25 + i * 0.22)
            prof += [(r, z - r * 2), (r * J(p, 1.45, 0.1), z), (r, z + r * 2)]
        prof.append((r * 0.95, L))
        p.lathe(prof, mat="body", segs=8)
        if e == "Wasteland":
            p.box((r * 2.6, r * 2.6, L * 0.14), M(loc=(0, 0, L * J(p, 0.5, 0.3)), rot=(0, 0, 20)), mat="tarp", bevel=0)
        elif e == "Future":
            p.box((r * 0.3, r * 0.2, L * 0.6), T((0, -r * 0.95, L * 0.45)), mat="gold", bevel=0)
    else:
        if e == "Primal":
            p.cyl(r * 1.1, r * 0.9, L, mat="body", segs=5, bevel=0, noise=0.08)
        elif e == "Industrial":
            p.cyl(r * 0.8, r * 0.8, L, mat="body", segs=8, bevel=0)
            for i in range(3):
                p.cyl(r * (1.25 - i * 0.1), r * (1.25 - i * 0.1), L * 0.05, T((0, 0, L * (0.05 + i * 0.06))), mat="fit", segs=8, bevel=0)
        elif e == "Future":
            p.box((r * 1.6, r * 1.1, L), T((0, 0, L / 2)), mat="body", bevel=0.3)
            p.box((r * 0.25, r * 0.2, L * 0.8), T((0, -r * 0.6, L * 0.5)), mat="glow", bevel=0)
        elif e == "Wasteland":
            p.cyl(r * 0.9, r * 0.9, L, M(rot=(J(p, 2, 1), 0, 0)), mat="body", segs=6, bevel=0)
            p.tube([(r, 0, L * 0.2), (r * 1.6, -r, L * 0.4), (r, 0, L * 0.6)], r * 0.2, mat="rubber", segs=4)
        else:
            p.cyl(r, r * 0.92, L, mat="body", segs=8, bevel=0)
            p.cyl(r * 1.12, r * 1.12, L * J(p, 0.26, 0.15), mat="grip", segs=8, bevel=0)


def r_joint(p, L, r):
    g = p.region
    z = L * J(p, 0.9, 0.03)
    if g == "Ocean":
        lash(p, r * 1.2, z, r * 3, segs=6)
    elif g == "Gale":
        p.cyl(r * 1.5, r * 1.5, r * 2.5, T((0, 0, z - r * 3)), mat="fit", segs=7, bevel=0)
        pegs(p, r * 1.5, z - r * 1.8, 3 if coin(p) else 4, r * 1.6)
    elif g == "Radiant":
        p.ring(r * 1.25, r * 0.35, T((0, 0, z)), mat="fit", segs=8)
        p.ball(r * 0.6, T((0, -r * 1.35, z)), mat="accent", segs=(5, 3))
    else:
        p.band(r * J(p, 1.25, 0.1), z, h=r * J(p, 2.2, 0.2))


def r_butt(p, r):
    g, e = p.region, p.era
    if g == "Ocean":
        if e == "Future":
            p.ball(r * 1.4, M(loc=(0, 0, -r * 0.6), scale=(1, 1, 1.3)), mat="glow", segs=(6, 4))
        elif e == "Wasteland":
            p.ball(r * J(p, 2.2, 0.15), T((0, 0, -r * 1.6)), mat="paint", segs=(6, 4))
        else:
            p.tube([(0, 0, 0), (0, -r * 0.6, -r * 2), (0, -r * 2.2, -r * 2.8), (0, -r * 3, -r * 1.8)], r * 0.55, mat="accent", segs=5)
    elif g == "Gale":
        if e == "Future":
            p.plate([(-r * 3, 0), (0, r * 0.4), (r * 3, 0), (0, -r * 2.5)], r * 0.25, M(loc=(0, 0, -r * 1.2)), mat="glow")
        elif e == "Wasteland":
            p.ring(r * 1.5, r * 0.6, T((0, 0, -r * 0.5)), mat="rubber", segs=8)
        else:
            p.ball(r * J(p, 1.5, 0.15), T((0, 0, -r * 0.6)), mat="body", segs=(6, 4))
            for i in range(3):
                p.ball(r * 0.4, T((math.cos(i * 2.1) * r * 1.4, math.sin(i * 2.1) * r * 1.4, -r * 1.2)), mat="accent", segs=(4, 3))
    elif g == "Radiant":
        p.lathe([(0, -r * 3.4), (r * 0.3, -r * 2.6), (r * J(p, 1.5, 0.12), -r * 1.6), (r * 1.1, -r * 0.5), (r, 0)], mat="fit", segs=8)
    else:
        if e == "Primal":
            p.ball(r * 1.8, M(loc=(0, 0, -r), scale=(1, 0.9, 1.2)), mat="metal", segs=(6, 4), noise=0.1)
        elif e == "Industrial":
            steps(p, r * 2.4, r * 2.4, -r * 2.4, 3, r * 0.8, mat="metal", shrink=1.12)
        elif e == "Future":
            p.box((r * 1.8, r * 1.3, r * 1.4), T((0, 0, -r * 0.7)), mat="metal", bevel=0)
            p.box((r * 1.2, r * 0.2, r * 0.3), T((0, -r * 0.7, -r * 0.7)), mat="glow", bevel=0)
        elif e == "Wasteland":
            p.cyl(r * 1.2, r * 1.2, r * 1.5, T((0, 0, -r * 1.4)), mat="metal", segs=6, bevel=0)
            for a in (0, 120, 240):
                p.cyl(r * 0.25, r * 0.25, r * 0.6, M(loc=(math.cos(math.radians(a)) * r * 1.2, math.sin(math.radians(a)) * r * 1.2, -r * 0.8), rot=(0, 90, a)), mat="iron", segs=6, bevel=0)
        else:
            p.cyl(r * 1.15, r, r * 1.3, T((0, 0, -r * 0.8)), mat="metal", segs=8, bevel=0)


def r_hafted(L, r, head):
    def form(p, slot):
        if slot == "haft":
            r_haft(p, L, r)
        elif slot == "joint":
            r_joint(p, L, r)
        elif slot == "butt":
            r_butt(p, r)
        else:
            head(p, L, r)
    return form


def _blade_mat(p):
    e = p.era
    if p.region == "Ocean" and e == "Primal":
        return "bone"
    if e == "Primal":
        return "stone" if p.region != "Metropolis" else "iron"
    if e == "Ancient":
        return "stone"
    if e == "Wasteland":
        return "paint" if p.region in ("Ocean", "Radiant") else "rust"
    return {"Future": "shell" if p.region != "Metropolis" else "chrome", "Steampunk": "iron"}.get(e, p.role("metal") if p.role("metal") not in ("clay", "stone") else "iron")


def _hoe_head(p, L, r):
    g, e = p.region, p.era
    top = L + 0.01
    w, h = J(p, 0.18, 0.12), J(p, 0.15, 0.12)
    mat = _blade_mat(p)
    if g == "Ocean":
        # Crescent blade on a bent crook, tips upswept like the gable horns.
        p.tube([(0, 0, top - 0.03), (0, -0.05, top + 0.03), (0, -0.12, top + 0.02)], r * 0.9, mat="body", segs=6)
        out = [(-w / 2, 0), (-w * 0.62, 0.05), (-w * 0.3, -h * 0.55), (0, -h), (w * 0.3, -h * 0.55), (w * 0.62, 0.05), (w / 2, 0), (0, -h * 0.35)]
        p.plate(out, 0.012, M(loc=(0, -0.14, top), rot=(J(p, 16, 0.3), 0, 0)), mat=mat)
        lash(p, r * 1.3, top - 0.02, 0.03, segs=6)
    elif g == "Gale":
        # Heart-shaped blade whose tang runs through the haft knob.
        p.cyl(0.006, 0.006, 0.09, M(loc=(0, 0.04, L * 0.94), rot=(90, 0, 0)), mat="iron", segs=5, bevel=0)
        out = [(0, 0.02), (-w * 0.45, -h * 0.25), (-w * 0.35, -h * 0.75), (0, -h * 1.1), (w * 0.35, -h * 0.75), (w * 0.45, -h * 0.25)]
        p.plate(out, 0.012, M(loc=(0, -0.05, L * 0.93), rot=(J(p, 70, 0.1), 0, 0)), mat=mat)
    elif g == "Radiant":
        # Mamoty: a broad square blade at right angles under a brass socket.
        p.cyl(r * 1.6, r * 1.6, 0.06, M(loc=(0, 0, top - 0.04)), mat="fit", segs=8, bevel=0)
        p.tube([(0, 0, top), (0, -0.06, top + 0.02), (0, -0.1, top - 0.02)], r * 0.9, mat="fit", segs=6)
        p.plate([(-w * 0.6, 0), (-w * 0.62, -h * 1.1), (w * 0.62, -h * 1.1), (w * 0.6, 0)], 0.01, M(loc=(0, -0.12, top - 0.01), rot=(8, 0, 0)), mat=mat)
    else:
        p.tube([(0, 0, top - 0.02), (0, -0.07, top + 0.02), (0, -0.13, top)], r * 0.8, mat="metal" if e != "Primal" else "iron", segs=6)
        if e == "Primal":
            p.ball(0.06, M(loc=(0, -0.14, top - 0.05), scale=(1.3, 0.5, 1)), mat=mat, segs=(6, 4), noise=0.12)
        elif e == "Industrial":
            for i in range(3):
                p.plate([(-w * (0.5 - i * 0.12), -h * i * 0.3), (-w * (0.5 - i * 0.12), -h * (i + 1) * 0.3), (w * (0.5 - i * 0.12), -h * (i + 1) * 0.3), (w * (0.5 - i * 0.12), -h * i * 0.3)],
                        0.012, M(loc=(0, -0.14, top), rot=(14, 0, 0)), mat=mat)
        elif e == "Future":
            for x in (-w * 0.35, w * 0.35):
                p.box((0.02, 0.012, h), M(loc=(x, -0.14, top - h / 2), rot=(14, 0, 0)), mat="chrome", bevel=0)
                p.box((0.006, 0.014, h * 0.8), M(loc=(x, -0.142, top - h / 2), rot=(14, 0, 0)), mat="glow", bevel=0)
        else:
            p.plate([(-w / 2, 0), (-w * 0.45, -h), (w * 0.45, -h), (w / 2, 0)], 0.012, M(loc=(0, -0.14, top), rot=(14, 0, 0)), mat=mat)
            if e == "Steampunk":
                gear(p, 0.025, M(loc=(0, -0.07, top + 0.03), rot=(0, 90, 0)))
            elif e == "Wasteland":
                p.box((w * 0.5, 0.004, h * 0.4), M(loc=(0, -0.15, top - h * 0.4), rot=(14, 0, 0)), mat="paint", bevel=0)
    if e in ("Future", "Ancient"):
        era_mark(p, r * 1.2, L * 0.97)


def _hammer_head(p, L, r):
    g, e = p.region, p.era
    s = J(p, 1.0, 0.1)
    top = L + 0.03 * s
    mat = _blade_mat(p)
    if g == "Ocean":
        if e == "Primal":
            p.ball(0.05 * s, M(loc=(0, 0, top), scale=(1, 1.4, 1)), mat="bark", segs=(8, 5), noise=0.1)
        else:
            p.cyl(0.04 * s, 0.04 * s, 0.13 * s, M(loc=(0, 0.065 * s, top), rot=(90, 0, 0)), mat="body" if e in HAND else mat, segs=8, bevel=0)
            for y in (-0.04, 0.04):
                lash(p, 0.04 * s, 0, 0.02, M(loc=(0, y * s, top), rot=(90, 0, 0)), segs=6)
            horn(p, 0, 0, top + 0.04 * s, 0.03 * s, 1, mat="accent")
    elif g == "Gale":
        p.ball(0.045 * s, T((0, 0, top)), mat="body" if e in ("Primal", "Agrarian", "Future") else mat, segs=(8, 6))
        pegs(p, 0.04 * s, top, 4 if coin(p) else 5, 0.025 * s, mat="fit")
        if e in MACHINE:
            p.cyl(0.03 * s, 0.03 * s, 0.05, M(loc=(0, -0.03, top), rot=(90, 0, 0)), mat=mat, segs=8, bevel=0)
    elif g == "Radiant":
        p.lathe([(0.02 * s, -0.07), (0.035 * s, -0.06), (0.028 * s, -0.02), (0.02 * s, 0), (0.028 * s, 0.02), (0.035 * s, 0.06), (0.02 * s, 0.07)],
                M(loc=(0, 0, top), rot=(90, 0, 0)), mat=mat, segs=8)
        petals(p, 0.02, 0, 5, 0.012, M(loc=(0, 0, top), rot=(90, 0, 0)), mat="fit", tilt=60)
    else:
        if e == "Primal":
            p.ball(0.05 * s, M(loc=(0, -0.01, top), scale=(0.9, 1.3, 0.8)), mat="iron", segs=(6, 4), noise=0.12)
        elif e == "Industrial":
            p.cyl(0.028 * s, 0.028 * s, 0.11 * s, M(loc=(0, 0.04, top), rot=(90, 22.5, 0)), mat=mat, segs=8, bevel=0)
            p.plate([(-0.01, 0), (-0.012, 0.06), (0.012, 0.06), (0.01, 0)], 0.01, M(loc=(0, 0.04, top - 0.01), rot=(-90, 0, 0)) @ M(rot=(0, 0, 0)), mat="chrome")
        elif e == "Future":
            p.box((0.05, 0.12, 0.045), T((0, 0, top)), mat="body", bevel=0.3)
            p.box((0.048, 0.006, 0.04), T((0, -0.062, top)), mat="glow", bevel=0)
        else:
            p.box((0.04 * s, 0.07, 0.04 * s), T((0, -0.02, top)), mat=mat)
            p.tube([(0, 0.015, top + 0.01), (0, 0.06, top + 0.02), (0, 0.09, top - 0.02)], 0.009, mat=mat, segs=5)
            if e == "Steampunk":
                gear(p, 0.02, M(loc=(0.022, -0.02, top), rot=(0, 90, 0)))
    if e in ("Ancient", "Wasteland") and g != "Metropolis":
        era_mark(p, 0.035, top, M(rot=(90, 0, 0)))


def _pick_head(p, L, r):
    g, e = p.region, p.era
    top = L + 0.02
    span = J(p, 0.24, 0.12)
    mat = _blade_mat(p)
    if g == "Ocean":
        # One long point sweeping up like a horn, a short adze behind.
        p.tube([(0, 0, top), (0, -span * 0.5, top + 0.02), (0, -span * 0.95, top + 0.07), (0, -span * 1.1, top + 0.15)], 0.016, mat=mat, segs=6)
        p.plate([(-0.03, 0), (-0.035, 0.07), (0.035, 0.07), (0.03, 0)], 0.01, M(loc=(0, 0.02, top), rot=(-80, 0, 0)), mat=mat)
        lash(p, r * 1.4, top - 0.01, 0.035, segs=6)
    elif g == "Gale":
        p.tube([(0, 0, top), (0, -span * 0.55, top - 0.02), (0, -span, top - 0.06)], 0.018, mat=mat, segs=6)
        p.plate([(-0.05, 0), (-0.06, 0.09), (0.06, 0.09), (0.05, 0)], 0.012, M(loc=(0, 0.02, top), rot=(-70, 0, 0)), mat=mat)
        pegs(p, r * 1.3, top, 2, r * 2.2)
    elif g == "Radiant":
        for y in (-1, 1):
            p.tube([(0, 0, top), (0, y * span * 0.55, top + 0.04), (0, y * span, top - 0.01)], 0.015, mat=mat, segs=6)
        petals(p, r * 1.2, top - 0.02, 6, 0.016, mat="fit", tilt=30)
    else:
        if e == "Primal":
            p.ball(0.03, M(loc=(0, -span * 0.4, top), scale=(0.6, 2.6, 0.7)), mat="iron", segs=(6, 4), noise=0.12)
        else:
            for y in (-1, 1):
                p.cyl(0.016, 0.003, span, M(loc=(0, 0, top), rot=(90 * -y, 0, 0)), mat=mat, segs=6, bevel=0)
            if e == "Industrial":
                steps(p, 0.05, 0.05, top - 0.03, 2, 0.03, mat="chrome", shrink=0.8)
            elif e == "Future":
                p.box((0.04, 0.05, 0.05), T((0, 0, top)), mat="body", bevel=0.3)
                for y in (-span, span):
                    p.ball(0.008, T((0, y, top)), mat="glow", segs=(5, 3))
            else:
                p.box((0.035, 0.05, 0.04), T((0, 0, top)), mat="metal" if e != "Mercantile" else "brass")
    if e in ("Ancient", "Steampunk") and g != "Metropolis":
        era_mark(p, r * 1.4, top - 0.06)


for _g in REGIONS:
    regional("Hoe", _g)(r_hafted(1.2, 0.017, _hoe_head))
    regional("Hammer", _g)(r_hafted(0.32, 0.013, _hammer_head))
    regional("Pickaxe", _g)(r_hafted(0.85, 0.017, _pick_head))


# ---------------------------------------------------------------- devices (shell, panel, controls, core, attachment)


def _ocean_communicator(p, slot):
    e = p.era
    if e in ("Primal", "Agrarian"):  # kentongan: a hanging slit drum of one bamboo culm
        h, r = F(p, 0.42), F(p, 0.07)
        if slot == "shell":
            p.cyl(r, r, h, mat="body", segs=8, bevel=0)
            for z in (0.15, 0.85):
                p.ring(r * 1.06, r * 0.18, T((0, 0, h * z)), mat="body", segs=8)
        elif slot == "panel":
            p.box((r * 0.35, r * 0.4, h * J(p, 0.5, 0.15)), T((0, -r * 0.85, h * 0.5)), mat="wood_dark", bevel=0)
        elif slot == "controls":
            p.tube([(r * 1.6, -r, h * 0.2), (r * 1.5, -r * 1.6, h * J(p, 0.65, 0.15))], 0.008, mat="wood", segs=5)
            p.ball(0.018, T((r * 1.5, -r * 1.6, h * 0.65)), mat="hide", segs=(5, 3))
        elif slot == "core":
            if e == "Agrarian":
                p.box((r * 2.4, r * 0.2, 0.02), T((0, 0, h + 0.07)), mat="teak")
            p.tube([(0, -r * 0.3, h), (0, 0, h + 0.07), (0, r * 0.3, h)], 0.005, mat="rattan", segs=4)
        else:
            horn(p, r * 0.6, 0, h, 0.05 * J(p, 1, 0.2), 1)
            horn(p, -r * 0.6, 0, h, 0.05 * J(p, 1, 0.2), -1)
    elif e == "Mercantile":  # bossed gong hung in a lacquer frame
        R = F(p, 0.14)
        if slot == "shell":
            for x in (-1, 1):
                p.box((0.025, 0.03, R * 3.2), T((x * R * 1.25, 0, R * 1.6)), mat="body")
            p.box((R * 2.9, 0.035, 0.03), T((0, 0, R * 3.2)), mat="body")
        elif slot == "panel":
            p.lathe([(R, 0), (R * 0.95, 0.025), (R * 0.4, 0.03), (R * 0.25, 0.05), (0, 0.06)], M(loc=(0, 0, R * 1.6), rot=(90, 0, 0)), mat="brass", segs=14)
        elif slot == "controls":
            p.tube([(R * 1.6, -0.04, 0.02), (R * 1.4, -0.06, R * J(p, 1.2, 0.2))], 0.008, mat="wood", segs=5)
            p.ball(0.025, T((R * 1.4, -0.06, R * 1.2)), mat="cloth", segs=(6, 4))
        elif slot == "core":
            for x in (-1, 1):
                p.tube([(x * R * 0.6, 0, R * 3.2), (x * R * 0.5, 0, R * 2.6)], 0.004, mat="rope", segs=4)
        else:
            for x in (-1, 1):
                horn(p, x * R * 1.4, 0, R * 3.2, 0.06, x, mat="gold")
    elif e in MACHINE:  # ship's set behind a porthole
        w, h = F(p, 0.2), F(p, 0.18)
        if slot == "shell":
            if e == "Wasteland":
                p.ball(w * 0.55, M(loc=(0, 0, w * 0.55), scale=(1, 0.85, 1)), mat="body", segs=(10, 6))
            else:
                p.box((w, w * 0.6, h), T((0, 0, h / 2)), mat="body")
        elif slot == "panel":
            z = w * 0.55 if e == "Wasteland" else h * 0.55
            y = -w * 0.48 if e == "Wasteland" else -w * 0.31
            p.ring(w * 0.22, 0.012, M(loc=(0, y, z), rot=(90, 0, 0)), mat="brass" if e == "Steampunk" else "fit", segs=10)
            p.cyl(w * 0.2, w * 0.2, 0.005, M(loc=(0, y, z), rot=(90, 0, 0)), mat="glow" if e != "Industrial" else "glass", segs=10, bevel=0)
        elif slot == "controls":
            for x in (-w * 0.35, w * 0.35):
                p.cyl(0.014, 0.014, 0.016, M(loc=(x, -w * 0.32, h * 0.2), rot=(90, 0, 0)), mat="rubber", segs=6, bevel=0)
            if e == "Industrial":
                for x in (-w * 0.5, w * 0.5):
                    p.box((0.008, w * 0.5, h * 0.8), T((x, 0, h * 0.5)), mat="rattan", bevel=0)
        elif slot == "core":
            if e == "Wasteland":
                p.tube([(-w * 0.5, 0, w * 0.4), (-w * 0.7, -w * 0.2, w * 0.2), (-w * 0.5, -w * 0.45, w * 0.1)], 0.005, mat="rope", segs=4)
                p.tube([(w * 0.5, 0, w * 0.4), (w * 0.7, -w * 0.2, w * 0.2), (w * 0.5, -w * 0.45, w * 0.1)], 0.005, mat="rope", segs=4)
            else:
                era_mark(p, w * 0.3, h * 0.5)
        else:
            top = w * 1.05 if e == "Wasteland" else h
            p.cyl(0.004, 0.003, J(p, 0.22, 0.2), T((w * 0.3, 0, top)), mat="metal", segs=4, bevel=0)
            horn(p, w * 0.3, 0, top + 0.18, 0.04, 1, mat="metal")
    else:  # Future / Ancient clamshell
        w = F(p, 0.1)
        if slot == "shell":
            p.ball(w, M(loc=(0, 0, w * 0.18), scale=(1, 0.8, 0.22)), mat="body", segs=(12, 6))
        elif slot == "panel":
            hinge = M(loc=(0, w * 0.75, w * 0.3), rot=(J(p, -62, 0.1), 0, 0))
            p.ball(w, hinge @ M(loc=(0, -w * 0.78, 0), scale=(1, 0.8, 0.12)), mat="fit" if e == "Future" else "stone_dark", segs=(12, 5))
            p.screen(w * 1.1, w * 0.8, hinge @ M(loc=(0, -w * 0.78, -w * 0.12), rot=(90, 0, 0)))
        elif slot == "controls":
            for i in range(3):
                p.ball(0.008, T(((i - 1) * w * 0.35, -w * 0.4, w * 0.38)), mat="bone", segs=(5, 3))
        elif slot == "core":
            p.ball(J(p, 0.014, 0.2), T((0, -w * 0.05, w * 0.4)), mat="glow", segs=(6, 4))
        else:
            horn(p, w * 0.7, w * 0.6, w * 0.35, 0.045, 1, mat="fit" if e == "Future" else "glow")


def _gale_communicator(p, slot):
    e = p.era
    if e in HAND:  # talking drum: hourglass, laced heads, a curved beater
        h, r = F(p, 0.36), F(p, 0.09)
        if slot == "shell":
            p.lathe([(r, 0), (r * 0.55, h * 0.5), (r, h)], mat="body" if e != "Primal" else "wood", segs=10)
        elif slot == "panel":
            for z in (0, h):
                p.cyl(r * 1.06, r * 1.06, 0.01, T((0, 0, z - 0.005)), mat="hide", segs=10, bevel=0)
        elif slot == "controls":
            n = 10 if e != "Primal" else 7
            for i in range(n):
                a = i * math.tau / n
                p.tube([(math.cos(a) * r, math.sin(a) * r, 0.005), (math.cos(a) * r * 0.56, math.sin(a) * r * 0.56, h * 0.5),
                        (math.cos(a) * r, math.sin(a) * r, h - 0.005)], 0.0025, mat="fit", segs=3)
        elif slot == "core":
            p.tube([(r * 1.5, -r, h * 0.7), (r * 1.7, -r * 1.6, h * 0.95), (r * 1.4, -r * 2.2, h * 1.05)], 0.006, mat="wood", segs=5)
        else:
            p.tube([(r * 0.9, 0, h * 0.9), (0, -r * 2.2, h * 1.4), (-r * 0.9, 0, h * 0.9)], 0.006, mat="leather", segs=4)
            if e == "Mercantile":
                for i in range(6):
                    a = i * math.tau / 6
                    p.ball(0.006, T((math.cos(a) * r * 1.02, math.sin(a) * r * 1.02, h * 0.92)), mat="brass", segs=(4, 3))
            else:
                zig(p, r * 0.92, h * 0.12, 0.03, 8)
    elif e in MACHINE:  # transistor radio, Steampunk with a horn and wind cups
        w, h = F(p, 0.26), F(p, 0.15)
        if slot == "shell":
            p.box((w, 0.09, h), T((0, 0, h / 2)), mat="body")
            if e == "Wasteland":
                for x in (-w / 2, w / 2):
                    p.cyl(0.03, 0.03, 0.1, M(loc=(x, 0.05, h * 0.5), rot=(90, 0, 0)), mat="rubber", segs=8, bevel=0)
        elif slot == "panel":
            for i in range(6):
                p.box((w * 0.07, 0.006, h * 0.6), T((-w * 0.38 + i * w * 0.09, -0.047, h * 0.5)), mat="fit", bevel=0)
        elif slot == "controls":
            for x in (w * 0.25, w * 0.38):
                p.cyl(0.018, 0.018, 0.014, M(loc=(x, -0.047, h * 0.55), rot=(90, 0, 0)), mat="accent", segs=8, bevel=0)
        elif slot == "core":
            p.box((w * 0.3, 0.004, 0.02), T((w * 0.3, -0.048, h * 0.82)), mat="glow" if e != "Industrial" else "glass", bevel=0)
        else:
            if e == "Steampunk":
                p.lathe([(0.01, 0), (0.015, 0.08), (0.05, 0.13)], M(loc=(-w * 0.35, 0, h)), mat="brass", segs=10)
                for i in range(3):
                    a = i * math.tau / 3
                    p.tube([(w * 0.3, 0, h + 0.08), (w * 0.3 + math.cos(a) * 0.05, math.sin(a) * 0.05, h + 0.08)], 0.003, mat="brass", segs=4)
                    p.ball(0.012, T((w * 0.3 + math.cos(a) * 0.05, math.sin(a) * 0.05, h + 0.08)), mat="copper", segs=(5, 3))
                p.cyl(0.003, 0.003, 0.08, T((w * 0.3, 0, h)), mat="brass", segs=4, bevel=0)
            else:
                p.cyl(0.003, 0.002, J(p, 0.28, 0.2), M(loc=(w * 0.4, 0, h), rot=(0, -15, 0)), mat="metal", segs=4, bevel=0)
                p.tube([(-w * 0.45, 0, h * 0.8), (0, 0, h * 1.6), (w * 0.45, 0, h * 0.8)], 0.006, mat="leather", segs=4)
    else:  # printed-earth dome with beam-end keys and a solar wing
        r = F(p, 0.09)
        if slot == "shell":
            prof = [(0, 0), (r, 0)]
            for i in range(4):
                prof += [(r * (1 - i * 0.16), r * (0.15 + i * 0.3)), (r * (0.94 - i * 0.16), r * (0.3 + i * 0.3))]
            prof.append((0, r * 1.35))
            p.lathe(prof, mat="body", segs=10)
        elif slot == "panel":
            p.screen(r * 0.8, r * 0.45, T((0, -r * 0.84, r * 0.45)))
        elif slot == "controls":
            pegs(p, r * 0.95, r * 0.2, 5, r * 0.35, mat="fit")
        elif slot == "core":
            p.ball(r * 0.2, T((0, 0, r * 1.4)), mat="glow", segs=(6, 4))
            if e == "Ancient":
                for a in (0, 120, 240):
                    p.cyl(r * 0.06, 0.0, r * 0.5, T((math.cos(math.radians(a)) * r * 0.7, math.sin(math.radians(a)) * r * 0.7, r * 0.8)), mat="stone", segs=4, bevel=0)
        else:
            mat = "glow" if e == "Future" else "stone_dark"
            for x in (-1, 1):
                p.plate([(0, 0), (x * r * 1.5, r * 0.3), (x * r * 1.4, -r * 0.2)], 0.006, M(loc=(x * r * 0.5, 0, r * 0.9)), mat=mat)


def _radiant_communicator(p, slot):
    e = p.era
    if e in HAND:  # temple bell on a kalasha handle
        h, r = F(p, 0.16), F(p, 0.08)
        if slot == "shell":
            p.lathe([(r, 0), (r * 0.95, h * 0.15), (r * 0.62, h * 0.6), (r * 0.5, h * 0.9), (0, h)], mat="body" if e == "Primal" else "fit", segs=12)
        elif slot == "panel":
            p.ring(r * 1.0, 0.007, T((0, 0, 0.005)), mat="accent" if e == "Mercantile" else "fit", segs=12, square=False)
        elif slot == "controls":
            p.cyl(0.003, 0.003, h * 0.7, T((0, 0, h * 0.15)), mat="metal" if e != "Primal" else "rope", segs=4, bevel=0)
            p.ball(J(p, 0.016, 0.2), T((0, 0, h * 0.15)), mat="metal" if e != "Primal" else "clay", segs=(5, 3))
        elif slot == "core":
            p.cyl(0.012, 0.012, 0.06, T((0, 0, h)), mat="fit", segs=6, bevel=0)
            dome(p, 0.02, h + 0.06, mat="fit", segs=8)
        else:
            if e == "Mercantile":
                petals(p, r * 0.6, h * 0.55, 6, 0.018, mat="enamel")
            else:
                p.tube([(0, 0, h + 0.1), (0, 0, h + 0.18)], 0.004, mat="rope", segs=4)
                p.ring(0.02, 0.004, M(loc=(0, 0, h + 0.2), rot=(90, 0, 0)), mat="rope", segs=6, square=False)
    elif e in MACHINE:  # railway signal box with a round lamp
        w, h = F(p, 0.12), F(p, 0.26)
        if slot == "shell":
            p.box((w, w, h), T((0, 0, h / 2)), mat="body")
            if e == "Steampunk":
                p.box((w * 1.3, w * 1.3, 0.03), T((0, 0, 0.015)), mat="marble")
        elif slot == "panel":
            p.ring(w * 0.3, 0.008, M(loc=(0, -w * 0.51, h * 0.65), rot=(90, 0, 0)), mat="fit", segs=10)
            p.cyl(w * 0.28, w * 0.28, 0.004, M(loc=(0, -w * 0.5, h * 0.65), rot=(90, 0, 0)), mat="glass", segs=10, bevel=0)
        elif slot == "controls":
            p.box((0.012, 0.012, h * 0.4), M(loc=(w * 0.55, 0, h * 0.4), rot=(0, J(p, 18, 0.4), 0)), mat="metal")
            p.ball(0.012, T((w * 0.62, 0, h * 0.6)), mat="paint" if e != "Steampunk" else "brass", segs=(5, 3))
        elif slot == "core":
            p.ball(w * 0.18, T((0, -w * 0.4, h * 0.65)), mat="glow" if e != "Industrial" else "glass", segs=(6, 4))
        else:
            if e == "Wasteland":
                p.box((w * 1.2, w * 0.6, 0.004), M(loc=(0, 0, h + 0.02), rot=(J(p, 8, 0.5), 6, 0)), mat="tarp", bevel=0)
            else:
                dome(p, w * 0.45, h, mat="fit" if e == "Steampunk" else "body", segs=8)
    else:  # lotus: petals open around a floating light
        r = F(p, 0.09)
        if slot == "shell":
            p.cyl(r, r * 0.85, r * 0.3, mat="body", segs=12)
        elif slot == "panel":
            petals(p, r * 0.6, r * 0.3, 8, r * 0.28, mat="fit" if e == "Future" else "marble", tilt=35)
        elif slot == "controls":
            for i in range(4):
                a = i * math.tau / 4 + 0.4
                p.ball(0.008, T((math.cos(a) * r * 0.95, math.sin(a) * r * 0.95, r * 0.2)), mat="accent", segs=(5, 3))
        elif slot == "core":
            p.ball(r * J(p, 0.3, 0.15), T((0, 0, r * 0.95)), mat="glow", segs=(8, 5))
        else:
            p.ring(r * 0.55, 0.004, M(loc=(0, 0, r * 0.95), rot=(70, 0, 0)), mat="glow" if e == "Future" else "gold", segs=12)


def _metropolis_communicator(p, slot):
    e = p.era
    if e == "Primal":  # struck meteor-iron plate
        w, h = F(p, 0.2), F(p, 0.3)
        if slot == "shell":
            p.box((w, 0.03, h), M(loc=(0, 0, h * 0.55), rot=(0, J(p, 6, 0.6), 0)), mat="iron", noise=0.08)
        elif slot == "panel":
            p.ball(w * 0.15, M(loc=(0, -0.02, h * 0.6), scale=(1, 0.3, 1)), mat="stone_dark", segs=(6, 4))
        elif slot == "controls":
            p.tube([(w * 0.8, -0.05, 0.02), (w * 0.7, -0.08, h * 0.5)], 0.01, mat="stone_dark", segs=5)
        elif slot == "core":
            p.tube([(-w * 0.4, 0, h * 1.05), (0, 0, h * 1.2), (w * 0.4, 0, h * 1.05)], 0.005, mat="hide", segs=4)
        else:
            p.box((w * 1.3, 0.12, 0.03), T((0, 0, 0.015)), mat="stone_dark")
    elif e in ("Agrarian", "Mercantile"):  # handbell / brass ear trumpet
        if e == "Agrarian":
            h, r = F(p, 0.14), F(p, 0.06)
            if slot == "shell":
                p.lathe([(r, 0), (r * 0.7, h * 0.5), (r * 0.5, h), (0, h * 1.05)], mat="iron", segs=10)
            elif slot == "panel":
                p.ring(r, 0.006, T((0, 0, 0.004)), mat="iron", segs=10, square=False)
            elif slot == "controls":
                p.ball(0.014, T((0, 0, h * 0.2)), mat="iron", segs=(5, 3))
            elif slot == "core":
                p.cyl(0.012, 0.014, J(p, 0.1, 0.2), T((0, 0, h)), mat="wood", segs=6, bevel=0)
            else:
                p.ball(0.018, T((0, 0, h + 0.1)), mat="wood", segs=(5, 3))
        else:
            L = F(p, 0.28)
            if slot == "shell":
                p.lathe([(0.012, 0), (0.016, L * 0.5), (0.04, L * 0.85), (0.075, L)], M(loc=(0, -L * 0.5, 0.1), rot=(90, 0, 0)), mat="brass", segs=12)
            elif slot == "panel":
                p.cyl(0.02, 0.02, L * 0.4, M(loc=(0, -L * 0.05, 0.1), rot=(-90, 0, 0)), mat="leather", segs=8, bevel=0)
            elif slot == "controls":
                p.ring(0.022, 0.004, M(loc=(0, L * 0.1, 0.1), rot=(90, 0, 0)), mat="brass", segs=8)
            elif slot == "core":
                p.ball(0.014, T((0, L * 0.5 + 0.01, 0.1)), mat="gold", segs=(5, 3))
            else:
                p.box((0.1, 0.16, 0.02), T((0, 0, 0.01)), mat="leather")
    elif e in MACHINE:  # tombstone radio with deco setbacks and vertical grille fins
        w, h = F(p, 0.22), F(p, 0.26)
        if slot == "shell":
            if e == "Wasteland":
                p.box((w, 0.12, h * 0.8), M(loc=(0, 0, h * 0.4), rot=(0, J(p, 4, 0.6), 0)), mat="body")
            else:
                p.box((w, 0.12, h * 0.7), T((0, 0, h * 0.35)), mat="body" if e != "Industrial" else "wood_dark")
                steps(p, w, 0.12, h * 0.7, 3, h * 0.1, mat="body" if e != "Industrial" else "wood_dark")
        elif slot == "panel":
            for i in range(5):
                p.box((w * 0.05, 0.008, h * 0.5), T((-w * 0.3 + i * w * 0.15, -0.062, h * 0.45)), mat="fit" if e != "Wasteland" else "shell_dark", bevel=0)
        elif slot == "controls":
            for x in (-w * 0.3, 0, w * 0.3):
                p.cyl(0.014, 0.014, 0.012, M(loc=(x, -0.062, h * 0.12), rot=(90, 0, 0)), mat="accent", segs=8, bevel=0)
        elif slot == "core":
            if e == "Steampunk":
                gear(p, w * 0.18, M(loc=(0, -0.066, h * 0.8), rot=(90, 0, 0)))
            p.cyl(w * 0.12, w * 0.12, 0.004, M(loc=(0, -0.064, h * 0.8), rot=(90, 0, 0)), mat="glow" if e != "Industrial" else "glass", segs=10, bevel=0)
        else:
            if e == "Wasteland":
                for i in range(3):
                    x = (i - 1) * w * 0.3
                    p.tube([(x, 0.06, h * 0.7), (x + 0.03, 0.12, h * 0.4), (x - 0.02, 0.1, 0.01)], 0.004, mat=("rubber", "paint", "copper")[i], segs=4)
                p.box((w * 0.5, 0.004, h * 0.3), M(loc=(0, 0.065, h * 0.5), rot=(0, 10, 0)), mat="glow", bevel=0)
            else:
                p.cyl(0.003, 0.002, 0.22, M(loc=(w * 0.4, 0, h * 0.9), rot=(0, -20, 0)), mat="chrome" if e == "Industrial" else "brass", segs=4, bevel=0)
    else:  # glass slab between fins under a light cone
        w, h = F(p, 0.08), F(p, 0.16)
        if slot == "shell":
            p.box((w, 0.012, h), T((0, 0, h / 2)), mat="body")
        elif slot == "panel":
            p.screen(w * 0.8, h * 0.85, T((0, -0.007, h * 0.5)))
        elif slot == "controls":
            for x in (-w / 2, w / 2):
                p.box((0.006, 0.02, h * 1.05), T((x, 0, h * 0.5)), mat="fit", bevel=0)
        elif slot == "core":
            p.cyl(0.006, w * J(p, 0.5, 0.2), w * 0.6, T((0, 0, h)), mat="glow", segs=8, bevel=0)
        else:
            p.box((w * 1.4, 0.05, 0.012), T((0, 0, 0.006)), mat="fit", bevel=0)


def _ocean_console(p, slot):
    e = p.era
    if e in HAND:  # congkak: a boat-shaped board with two rows of pits and end stores
        L = F(p, 0.5)
        if slot == "shell":
            p.box((L, 0.13, 0.05), T((0, 0, 0.025)), mat="body", bevel=0.2)
        elif slot == "panel":
            pit = J(p, 0.016, 0.18)
            for i in range(5):
                for y in (-0.03, 0.03):
                    p.cyl(pit, pit * 0.75, 0.005, T((-L * 0.28 + i * L * 0.14, y, 0.05)), mat="wood_dark", segs=6, bevel=0)
        elif slot == "controls":
            for i in range(6):
                p.ball(0.007, M(loc=(p.rng.uniform(-L * 0.3, L * 0.3), p.rng.uniform(-0.04, 0.04), 0.057), scale=(1.3, 1, 0.6)), mat="bone", segs=(5, 3))
        elif slot == "core":
            for x in (-L * 0.42, L * 0.42):
                p.cyl(0.03, 0.024, 0.006, T((x, 0, 0.05)), mat="wood_dark", segs=6, bevel=0)
        else:
            for x in (-1, 1):
                horn(p, x * L * 0.5, 0, 0.04, 0.06, x, mat="body" if e != "Mercantile" else "gold")
    elif e in MACHINE:  # tin fishing game: a tub of hinged fish turned by a crank
        r = F(p, 0.14)
        if slot == "shell":
            p.cyl(r, r * 0.95, 0.07, mat="body", segs=12)
        elif slot == "panel":
            p.cyl(r * 0.85, r * 0.85, 0.004, T((0, 0, 0.065)), mat="glass" if e != "Steampunk" else "glow", segs=12, bevel=0)
        elif slot == "controls":
            for i in range(5):
                a = i * math.tau / 5
                p.ball(0.014, M(loc=(math.cos(a) * r * 0.55, math.sin(a) * r * 0.55, 0.075), scale=(1.6, 0.8, 0.7), rot=(0, 0, math.degrees(a))), mat="paint", segs=(6, 3))
        elif slot == "core":
            p.tube([(r, 0, 0.04), (r * 1.25, 0, 0.04), (r * 1.25, 0, 0.09)], 0.005, mat="metal", segs=4)
        else:
            if e == "Wasteland":
                p.tube([(r * math.cos(t * 0.8), r * math.sin(t * 0.8), 0.07) for t in range(9)], 0.004, mat="rope", segs=4)
            else:
                lash(p, r, 0.035, 0.03)
    else:  # clamshell handheld
        w = F(p, 0.09)
        if slot == "shell":
            p.ball(w, M(loc=(0, 0, 0.012), scale=(1.3, 0.75, 0.15)), mat="body", segs=(12, 5))
        elif slot == "panel":
            p.screen(w * 1.1, w * 0.7, M(loc=(0, -0.004, w * 0.4), rot=(J(p, -12, 0.3), 0, 0)) @ M(rot=(90, 0, 0)))
            p.ball(w, M(loc=(0, w * 0.5, w * 0.4), rot=(80, 0, 0), scale=(1.3, 0.75, 0.12)), mat="fit" if e == "Future" else "stone_dark", segs=(12, 4))
        elif slot == "controls":
            for x in (-w * 0.7, w * 0.7):
                p.ball(0.01, T((x, -w * 0.2, 0.025)), mat="bone", segs=(5, 3))
        elif slot == "core":
            p.ball(0.01, T((0, -w * 0.4, 0.024)), mat="glow", segs=(5, 3))
        else:
            horn(p, w * 1.2, 0, 0.01, 0.03, 1, mat="fit" if e == "Future" else "glow")


def _gale_console(p, slot):
    e = p.era
    if e in HAND:  # bao board on a carved pedestal
        L = F(p, 0.42)
        if slot == "shell":
            p.box((L, 0.16, 0.035), T((0, 0, 0.12)), mat="body")
            p.cyl(0.035, 0.05, 0.11, T((0, 0, 0.0)), mat="body", segs=6, bevel=0)
        elif slot == "panel":
            for i in range(6):
                for y in (-0.04, 0.04):
                    p.cyl(0.015, 0.011, 0.005, T((-L * 0.36 + i * L * 0.144, y, 0.137)), mat="wood_dark", segs=6, bevel=0)
        elif slot == "controls":
            for i in range(7):
                p.ball(0.006, T((p.rng.uniform(-L * 0.4, L * 0.4), p.rng.uniform(-0.05, 0.05), 0.142)), mat="accent" if e != "Primal" else "bone", segs=(4, 3))
        elif slot == "core":
            zig(p, 0.05, 0.05, 0.04, 6)
        else:
            pegs(p, L * 0.5, 0.12, 2, 0.05, mat="body")
    elif e in MACHINE:  # spinning-top arena dish
        r = F(p, 0.16)
        if slot == "shell":
            p.lathe([(r * 0.4, 0), (r, 0.03), (r * 1.02, 0.05), (r * 0.95, 0.052), (0, 0.02)], mat="body", segs=12)
        elif slot == "panel":
            if e == "Wasteland":
                p.ring(r * 1.05, 0.025, T((0, 0, 0.035)), mat="rubber", segs=12)
            else:
                zig(p, r * 1.0, 0.03, 0.025, 10)
        elif slot == "controls":
            for x in (-r * 0.3, r * 0.25):
                p.lathe([(0, 0), (0.02, 0.012), (0.024, 0.02), (0.004, 0.03), (0.003, 0.045)], T((x, p.rng.uniform(-0.03, 0.03), 0.02)), mat="paint", segs=8)
        elif slot == "core":
            p.ball(0.012, T((0, 0, 0.022)), mat="glow" if e != "Industrial" else "metal", segs=(5, 3))
        else:
            p.tube([(r * 1.05, 0, 0.03), (r * 1.3, -0.02, 0.04), (r * 1.5, -0.04, 0.02)], 0.003, mat="fit", segs=4)
    else:  # printed-earth handheld with beam-end keys
        w = F(p, 0.16)
        if slot == "shell":
            for i in range(4):
                p.box((w * (1 - i * 0.03), 0.05, 0.016), T((0, 0, 0.008 + i * 0.016)), mat="body", bevel=0.4)
        elif slot == "panel":
            p.screen(w * 0.45, 0.05, M(loc=(0, -0.026, 0.035)))
        elif slot == "controls":
            for x in (-w * 0.38, w * 0.38):
                p.cyl(0.006, 0.005, 0.02, M(loc=(x, -0.025, 0.035), rot=(90, 0, 0)), mat="fit", segs=4, bevel=0)
        elif slot == "core":
            p.ball(0.008, T((0, 0, 0.066)), mat="glow", segs=(5, 3))
        else:
            for x in (-1, 1):
                p.plate([(0, 0), (x * 0.05, 0.03), (x * 0.06, -0.01)], 0.004, M(loc=(x * w * 0.5, 0, 0.04)), mat="glow" if e == "Future" else "stone_dark")


def _radiant_console(p, slot):
    e = p.era
    if e in HAND:  # chaupar: a cross-shaped cloth board, cowrie dice, cone pawns
        s = F(p, 0.5)
        if slot == "shell":
            for rot in (0, 90):
                p.box((s, s * 0.3, 0.006), M(loc=(0, 0, 0.003), rot=(0, 0, rot)), mat="cloth" if e != "Mercantile" else "body", bevel=0)
        elif slot == "panel":
            p.box((s * 0.3, s * 0.3, 0.008), T((0, 0, 0.005)), mat="accent", bevel=0)
            for i in range(4):
                a = i * 90
                p.box((s * 0.04, s * 0.04, 0.008), M(rot=(0, 0, a)) @ T((s * 0.38, 0, 0.006)), mat="accent", bevel=0)
        elif slot == "controls":
            for i in range(4):
                p.ball(0.01, M(loc=(p.rng.uniform(-0.1, 0.1), -s * 0.3 + p.rng.uniform(-0.03, 0.03), 0.012), scale=(1.3, 0.9, 0.6)), mat="bone", segs=(5, 3))
        elif slot == "core":
            for i in range(4):
                a = i * math.tau / 4 + 0.785
                p.cyl(0.012, 0.0, 0.035, T((math.cos(a) * s * 0.1, math.sin(a) * s * 0.1, 0.008)), mat="paint", segs=6, bevel=0)
        else:
            if e == "Mercantile":
                p.box((s * 0.3, s * 0.15, 0.06), T((s * 0.4, s * 0.4, 0.03)), mat="wood_dark")
                dome(p, 0.03, 0.06, M(loc=(s * 0.4, s * 0.4, 0)), mat="brass", segs=8)
            else:
                p.cyl(0.02, 0.02, s * 0.28, M(loc=(-s * 0.14, s * 0.4, 0.02), rot=(0, 90, 0)), mat="cloth", segs=8, bevel=0)
    elif e in MACHINE:  # carrom board
        s = F(p, 0.6)
        if slot == "shell":
            p.box((s, s, 0.012), T((0, 0, 0.006)), mat="wood" if e != "Wasteland" else "body", bevel=0)
            for rot in (0, 90, 180, 270):
                p.box((s * 1.06, 0.03, 0.025), M(rot=(0, 0, rot)) @ T((0, s / 2 + 0.01, 0.0125)), mat="fit" if e != "Industrial" else "wood_dark", bevel=0)
        elif slot == "panel":
            p.ring(s * J(p, 0.12, 0.2), 0.004, T((0, 0, 0.013)), mat="paint", segs=12)
            for x in (-1, 1):
                for y in (-1, 1):
                    p.cyl(0.025, 0.025, 0.003, T((x * s * 0.44, y * s * 0.44, 0.012)), mat="rubber", segs=8, bevel=0)
        elif slot == "controls":
            spread, turn = J(p, 0.035, 0.3), p.rng.uniform(0, 1)
            for i in range(6):
                a = i * math.tau / 6 + turn
                p.cyl(0.015, 0.015, 0.008, T((math.cos(a) * spread, math.sin(a) * spread, 0.013)), mat="wood_dark" if i % 2 else "bone", segs=8, bevel=0)
        elif slot == "core":
            p.cyl(0.016, 0.016, 0.008, T((0, 0, 0.013)), mat="paint", segs=8, bevel=0)
            if e == "Steampunk":
                p.ball(0.01, T((0, -s * 0.3, 0.02)), mat="glow", segs=(5, 3))
        else:
            p.cyl(0.02, 0.02, 0.008, T((0, -s * 0.36, 0.013)), mat="marble" if e == "Steampunk" else "accent", segs=8, bevel=0)
    else:  # lotus board: a holo grid floating over petals
        r = F(p, 0.13)
        if slot == "shell":
            p.cyl(r, r * 0.9, 0.03, mat="body", segs=12)
        elif slot == "panel":
            petals(p, r * 0.9, 0.02, 8, r * 0.2, mat="fit" if e == "Future" else "marble", tilt=70)
        elif slot == "controls":
            for i in range(4):
                p.cyl(0.008, 0.0, 0.025, T(((i % 2 - 0.5) * r * 0.5, (i // 2 - 0.5) * r * 0.5, 0.03)), mat="accent", segs=5, bevel=0)
        elif slot == "core":
            p.box((r * 1.1, r * 1.1, 0.002), T((0, 0, J(p, 0.09, 0.2))), mat="glow", bevel=0)
        else:
            p.ring(r * 1.02, 0.005, T((0, 0, 0.03)), mat="gold", segs=12)


def _metropolis_console(p, slot):
    e = p.era
    if e in HAND:  # stone pebbles / iron checkers / leather-and-brass chess box
        s = F(p, 0.32)
        if slot == "shell":
            mat = {"Primal": "iron", "Agrarian": "wood", "Mercantile": "leather"}[e]
            p.box((s, s, 0.04), T((0, 0, 0.02)), mat=mat, noise=0.06 if e == "Primal" else None)
        elif slot == "panel":
            for i in range(4):
                for j in range(4):
                    if (i + j) % 2:
                        p.box((s * 0.2, s * 0.2, 0.003), T((-s * 0.3 + i * s * 0.2, -s * 0.3 + j * s * 0.2, 0.041)), mat="stone_dark" if e == "Primal" else "iron", bevel=0)
        elif slot == "controls":
            for i in range(5):
                p.cyl(0.014, 0.014, 0.008, T((p.rng.uniform(-s * 0.4, s * 0.4), p.rng.uniform(-s * 0.4, s * 0.4), 0.045)), mat="stone" if e == "Primal" else "wood_dark", segs=8, bevel=0)
        elif slot == "core":
            p.lathe([(0.012, 0), (0.008, 0.02), (0.012, 0.04), (0, 0.05)], T((s * 0.3, s * 0.3, 0.04)), mat="gold" if e == "Mercantile" else "iron", segs=6)
        else:
            if e == "Mercantile":
                for x in (-s * 0.3, s * 0.3):
                    p.box((0.03, 0.01, 0.02), T((x, -s / 2 - 0.004, 0.025)), mat="brass")
            else:
                p.box((s * 0.3, 0.06, 0.03), T((0, s / 2 + 0.03, 0.015)), mat="stone_dark" if e == "Primal" else "iron")
    elif e in MACHINE:  # deco slot machine
        w, h = F(p, 0.24), F(p, 0.4)
        if slot == "shell":
            p.box((w, w * 0.8, h * 0.7), T((0, 0, h * 0.35)), mat="body")
            steps(p, w, w * 0.8, h * 0.7, 3 if e != "Wasteland" else 2, h * 0.07, mat="body")
        elif slot == "panel":
            for i in range(3):
                p.cyl(w * 0.12, w * 0.12, w * 0.18, M(loc=((i - 1) * w * 0.26, -w * 0.3, h * 0.48), rot=(0, 90, 0)), mat="shell" if e != "Wasteland" else "paint", segs=8, bevel=0)
        elif slot == "controls":
            p.cyl(0.008, 0.008, h * 0.3, T((w * 0.55, 0, h * 0.45)), mat="metal", segs=6, bevel=0)
            p.ball(0.022, T((w * 0.55, 0, h * 0.77)), mat="paint", segs=(6, 4))
        elif slot == "core":
            if e == "Steampunk":
                gear(p, w * 0.2, M(loc=(0, -w * 0.41, h * 0.2), rot=(90, 0, 0)))
            else:
                p.box((w * 0.7, 0.006, h * 0.04), T((0, -w * 0.41, h * 0.66)), mat="glow" if e == "Wasteland" else "glass", bevel=0)
        else:
            fins(p, w * 0.45, h * 0.1, h * 0.62, 2, M(rot=(0, 0, 0)), mat="fit" if e != "Wasteland" else "rust")
    else:  # chrome-finned handheld with a holo cone
        w = F(p, 0.17)
        if slot == "shell":
            p.box((w, 0.05, 0.022), T((0, 0, 0.011)), mat="body", bevel=0.4)
        elif slot == "panel":
            p.screen(w * 0.45, 0.04, T((0, -0.026, 0.016)) @ M(rot=(0, 0, 0)))
        elif slot == "controls":
            for x in (-w * 0.4, w * 0.4):
                p.box((0.012, 0.052, 0.026), T((x, 0, 0.013)), mat="fit", bevel=0)
        elif slot == "core":
            p.cyl(0.004, 0.03, 0.05, T((0, 0, 0.022)), mat="glow", segs=8, bevel=0)
        else:
            fins(p, w * 0.3, 0.0, 0.024, 2, mat="fit", depth=0.01)


def _ocean_timepiece(p, slot):
    e = p.era
    if e in HAND:  # water clock: a pierced coconut bowl sinking in a tub
        r, h = F(p, 0.16), F(p, 0.16)
        if slot == "shell":
            p.cyl(r, r * 0.92, h, mat="body", segs=12)
        elif slot == "panel":
            p.ball(r * 0.6, M(loc=(0, 0, h * J(p, 0.85, 0.06)), scale=(1, 1, 0.5)), mat="bark", segs=(10, 4))
        elif slot == "controls":
            for i in range(4 + coin(p)):
                p.cyl(0.003, 0.003, 0.08, M(loc=(r * 1.05, (i - 2) * 0.012, h * 0.5), rot=(J(p, 6, 0.6), 0, 0)), mat="bamboo", segs=4, bevel=0)
        elif slot == "core":
            if e == "Mercantile":
                p.ring(r * 1.02, 0.008, T((0, 0, h * 0.85)), mat="gold", segs=12)
            else:
                lash(p, r, h * 0.5, 0.04)
        else:
            for x in (-1, 1):
                horn(p, x * r, 0, h * 0.7, 0.05, x, mat="body")
    elif e in MACHINE:  # ship's chronometer in a box with a porthole bezel
        s = F(p, 0.14)
        if slot == "shell":
            p.box((s, s, s * 0.7), T((0, 0, s * 0.35)), mat="teak" if e == "Industrial" else "body")
        elif slot == "panel":
            p.cyl(s * 0.34, s * 0.34, 0.004, T((0, 0, s * 0.7)), mat="shell" if e != "Wasteland" else "glass", segs=12, bevel=0)
            for i in range(4):
                a = i * math.tau / 4
                p.box((0.004, 0.012, 0.002), M(loc=(math.cos(a) * s * 0.28, math.sin(a) * s * 0.28, s * 0.704), rot=(0, 0, math.degrees(a))), mat="iron", bevel=0)
        elif slot == "controls":
            p.ring(s * 0.36, 0.008, T((0, 0, s * 0.7)), mat="brass" if e != "Industrial" else "fit", segs=10)
            for i in range(6 if e == "Steampunk" else 0):
                a = i * math.tau / 6
                p.ball(0.004, T((math.cos(a) * s * 0.36, math.sin(a) * s * 0.36, s * 0.71)), mat="copper", segs=(4, 3))
        elif slot == "core":
            p.box((0.003, s * 0.25, 0.002), M(loc=(0, 0, s * 0.706), rot=(0, 0, J(p, 40, 0.8))), mat="iron", bevel=0)
            if e != "Industrial":
                p.ball(0.008, T((s * 0.4, -s * 0.4, s * 0.72)), mat="glow", segs=(5, 3))
        else:
            if e == "Wasteland":
                p.ball(s * 0.25, T((s * 0.6, 0, s * 0.25)), mat="paint", segs=(8, 5))
                p.tube([(s * 0.5, 0, s * 0.3), (s * 0.3, 0, s * 0.65)], 0.004, mat="rope", segs=4)
            else:
                for x in (-s / 2, s / 2):
                    p.box((0.01, s * 0.3, 0.015), T((x * 1.04, 0, s * 0.6)), mat="brass", bevel=0)
    else:  # clamshell clock, a glow ring for hours
        w = F(p, 0.08)
        if slot == "shell":
            p.ball(w, M(loc=(0, 0, w * 0.3), scale=(1, 1, 0.35)), mat="body", segs=(12, 5))
        elif slot == "panel":
            p.ball(w * 0.95, M(loc=(0, w * 0.6, w * 0.7), rot=(-60, 0, 0), scale=(1, 1, 0.2)), mat="fit" if e == "Future" else "stone_dark", segs=(12, 4))
        elif slot == "controls":
            p.ring(w * 0.7, 0.004, T((0, 0, w * 0.62)), mat="glow", segs=12)
        elif slot == "core":
            p.box((0.003, w * 0.5, 0.002), M(loc=(0, 0, w * 0.64), rot=(0, 0, J(p, 120, 0.5))), mat="glow", bevel=0)
        else:
            horn(p, w, 0, w * 0.3, 0.035, 1, mat="fit" if e == "Future" else "glow")


def _gale_timepiece(p, slot):
    e = p.era
    if e in HAND:  # shadow clock: a gnomon over painted hour pegs on a clay disc
        r = F(p, 0.16)
        if slot == "shell":
            p.cyl(r, r * 1.05, 0.03, mat="clay" if e == "Primal" else "body", segs=12)
        elif slot == "panel":
            if e == "Mercantile":
                p.cyl(r * 0.85, r * 0.85, 0.004, T((0, 0, 0.03)), mat="brass", segs=12, bevel=0)
            else:
                zig(p, r * 0.8, 0.033, 0.012, 10)
        elif slot == "controls":
            n = 7
            for i in range(n):
                a = math.pi * i / (n - 1)
                p.cyl(0.004, 0.004, 0.02, T((math.cos(a) * r * 0.75, -math.sin(a) * r * 0.75, 0.03)), mat="fit", segs=4, bevel=0)
        elif slot == "core":
            p.plate([(0, 0), (0, r * J(p, 0.7, 0.15)), (r * 0.7, 0)], 0.006, M(loc=(-r * 0.35, 0, 0.03)), mat="metal" if e == "Mercantile" else "wood")
        else:
            p.ball(0.04, M(loc=(r * 1.2, 0, 0.05), scale=(1, 1, 1.3)), mat="gourd", segs=(8, 5))
            p.ball(0.025, T((r * 1.2, 0, 0.11)), mat="gourd", segs=(6, 4))
    elif e in MACHINE:  # painted table clock; Steampunk an anemometer clock; Wasteland a dash clock in a tyre
        r = F(p, 0.09)
        if slot == "shell":
            if e == "Wasteland":
                p.ring(r * 1.25, r * 0.35, M(loc=(0, 0, r * 1.4), rot=(90, 0, 0)), mat="rubber", segs=12)
            p.cyl(r, r, 0.05, M(loc=(0, 0.025, r * 1.4), rot=(90, 0, 0)), mat="body", segs=12)
        elif slot == "panel":
            p.cyl(r * 0.85, r * 0.85, 0.003, M(loc=(0, -0.026, r * 1.4), rot=(90, 0, 0)), mat="shell", segs=12, bevel=0)
            zig(p, r * 1.0, 0, 0.012, 10, M(loc=(0, 0, r * 1.4), rot=(90, 0, 0)))
        elif slot == "controls":
            for x in (-r * 0.6, r * 0.6):
                p.cyl(0.008, 0.012, r * 0.55, T((x, 0, 0)), mat="metal", segs=5, bevel=0)
        elif slot == "core":
            p.box((0.004, 0.003, r * 0.7), M(loc=(0, -0.03, r * 1.4), rot=(0, J(p, 50, 0.6), 0)), mat="iron", bevel=0)
            if e != "Industrial":
                p.ball(0.008, T((0, -0.03, r * 1.4)), mat="glow", segs=(5, 3))
        else:
            if e == "Steampunk":
                p.cyl(0.003, 0.003, 0.08, T((0, 0, r * 2.4)), mat="brass", segs=4, bevel=0)
                for i in range(3):
                    a = i * math.tau / 3
                    p.ball(0.014, T((math.cos(a) * 0.05, math.sin(a) * 0.05, r * 2.4 + 0.08)), mat="copper", segs=(5, 3))
            else:
                for x in (-r * 0.5, r * 0.5):
                    p.ball(r * 0.28, T((x, 0, r * 2.4)), mat="metal", segs=(6, 4))
    else:  # ribbed earth dome with a solar wing; the hour is a glow band
        r = F(p, 0.08)
        if slot == "shell":
            prof = [(0, 0), (r, 0)]
            for i in range(3):
                prof += [(r * (1 - i * 0.2), r * (0.2 + i * 0.35)), (r * (0.92 - i * 0.2), r * (0.38 + i * 0.35))]
            prof.append((0, r * 1.2))
            p.lathe(prof, mat="body", segs=10)
        elif slot == "panel":
            p.ring(r * 0.86, 0.006, T((0, 0, r * 0.45)), mat="glow", segs=10)
        elif slot == "controls":
            pegs(p, r * 0.98, r * 0.15, 4, r * 0.3)
        elif slot == "core":
            p.ball(r * 0.15, T((0, 0, r * 1.25)), mat="glow", segs=(5, 3))
        else:
            p.plate([(0, 0), (r * 1.6, r * 0.4), (r * 1.5, -r * 0.1)], 0.005, M(loc=(r * 0.4, 0, r * 0.9)), mat="glow" if e == "Future" else "stone_dark")


def _radiant_timepiece(p, slot):
    e = p.era
    if e in HAND:  # ghati: a pierced copper bowl sinking in a wide vessel
        r, h = F(p, 0.15), F(p, 0.13)
        if slot == "shell":
            p.lathe([(r * 0.5, 0), (r, h * 0.5), (r * 0.9, h), (r * 0.95, h * 1.05)], mat="body" if e == "Primal" else "fit", segs=12)
        elif slot == "panel":
            p.lathe([(0, h * 0.6), (r * 0.5, h * 0.7), (r * 0.6, h * 0.95)], mat="metal" if e != "Primal" else "clay", segs=10)
        elif slot == "controls":
            for i in range(6):
                a = i * math.tau / 6
                p.box((0.004, 0.003, 0.02), M(loc=(math.cos(a) * r * 0.92, math.sin(a) * r * 0.92, h * 0.9), rot=(0, 0, math.degrees(a))), mat="paint", bevel=0)
        elif slot == "core":
            p.lathe([(r * 0.5, -0.04), (r * 0.6, 0), (r * 0.5, 0.005)], mat="wood" if e != "Mercantile" else "brass", segs=10)
        else:
            if e == "Mercantile":
                petals(p, r * 0.8, h * 0.35, 8, 0.02, mat="enamel", tilt=10)
            else:
                p.ring(r * 0.95, 0.008, T((0, 0, h * 0.5)), mat="fit" if e != "Primal" else "rope", segs=12, square=False)
    elif e in MACHINE:  # clock tower in miniature: sandstone block, round face, a dome
        w, h = F(p, 0.1), F(p, 0.3)
        if slot == "shell":
            p.box((w, w, h), T((0, 0, h / 2)), mat="sandstone" if e == "Industrial" else "body" if e == "Wasteland" else "marble")
        elif slot == "panel":
            p.cyl(w * 0.36, w * 0.36, 0.004, M(loc=(0, -w * 0.51, h * 0.75), rot=(90, 0, 0)), mat="shell", segs=12, bevel=0)
            p.ring(w * 0.38, 0.006, M(loc=(0, -w * 0.51, h * 0.75), rot=(90, 0, 0)), mat="fit", segs=12)
        elif slot == "controls":
            p.box((0.003, 0.004, w * 0.3), M(loc=(0, -w * 0.53, h * 0.75), rot=(0, J(p, 30, 0.8), 0)), mat="iron", bevel=0)
        elif slot == "core":
            if e == "Industrial":
                for z in (0.25, 0.45):
                    p.box((w * 1.04, w * 1.04, 0.008), T((0, 0, h * z)), mat="iron", bevel=0)
            else:
                p.ball(w * 0.08, T((0, -w * 0.55, h * 0.75)), mat="glow", segs=(5, 3))
        else:
            if e == "Wasteland":
                p.box((w * 1.4, w * 1.4, 0.004), M(loc=(0, 0, h + 0.01), rot=(5, -7, 0)), mat="tarp", bevel=0)
            else:
                dome(p, w * 0.5, h, mat="fit" if e == "Steampunk" else "sandstone", segs=8)
    else:  # lotus sundial: petals as hour marks, a light gnomon
        r = F(p, 0.1)
        if slot == "shell":
            p.cyl(r, r * 0.9, 0.035, mat="body", segs=12)
        elif slot == "panel":
            petals(p, r * 0.82, 0.03, 12, r * 0.14, mat="fit" if e == "Future" else "marble", tilt=75)
        elif slot == "controls":
            p.cyl(0.004, 0.0, r * 0.8, M(loc=(0, 0, 0.035), rot=(J(p, 25, 0.3), 0, 0)), mat="glow", segs=5, bevel=0)
        elif slot == "core":
            p.ball(0.012, T((0, 0, 0.04)), mat="accent", segs=(5, 3))
        else:
            p.ring(r * 1.02, 0.005, T((0, 0, 0.035)), mat="gold", segs=12)


def _metropolis_timepiece(p, slot):
    e = p.era
    if e == "Mercantile":  # pocket watch on a chain
        r = F(p, 0.03)
        if slot == "shell":
            p.cyl(r, r, 0.012, M(loc=(0, 0, r), rot=(90, 0, 0)), mat="gold", segs=12)
        elif slot == "panel":
            p.cyl(r * 0.85, r * 0.85, 0.002, M(loc=(0, -0.007, r), rot=(90, 0, 0)), mat="shell", segs=12, bevel=0)
        elif slot == "controls":
            p.cyl(0.004, 0.004, 0.008, T((0, 0, r * 2)), mat="gold", segs=6, bevel=0)
            p.ring(0.008, 0.0015, M(loc=(0, 0, r * 2 + 0.012), rot=(90, 0, 0)), mat="gold", segs=8, square=False)
        elif slot == "core":
            p.box((0.0015, 0.002, r * 0.6), M(loc=(0, -0.0085, r), rot=(0, J(p, 40, 0.8), 0)), mat="iron", bevel=0)
        else:
            pts = [(0.012 * math.sin(i * 0.9), 0, r * 2 + 0.012 + i * 0.012) for i in range(7)]
            p.tube(pts, 0.0015, mat="gold", segs=4)
    elif e in ("Primal", "Agrarian"):  # standing gnomon stone / iron hourglass
        if e == "Primal":
            h = F(p, 0.3)
            if slot == "shell":
                p.cyl(0.06, 0.04, h, mat="iron", segs=5, noise=0.1)
            elif slot == "panel":
                p.cyl(0.18, 0.2, 0.02, mat="stone_dark", segs=10)
            elif slot == "controls":
                for i in range(6):
                    a = i * math.tau / 6
                    p.ball(0.015, T((math.cos(a) * 0.16, math.sin(a) * 0.16, 0.025)), mat="stone", segs=(4, 3))
            elif slot == "core":
                p.ball(0.02, T((0, 0, h)), mat="iron", segs=(5, 3), noise=0.1)
            else:
                p.tube([(0.04, 0, h * 0.6), (0.06, -0.02, h * 0.5)], 0.006, mat="hide", segs=4)
        else:
            h, r = F(p, 0.22), F(p, 0.06)
            if slot == "shell":
                for z in (0, h - 0.012):
                    p.box((r * 2.3, r * 2.3, 0.012), T((0, 0, z + 0.006)), mat="wood")
            elif slot == "panel":
                p.lathe([(0, 0.012), (r, h * 0.2), (r * 0.15, h * 0.5), (r, h * 0.8), (0, h - 0.012)], mat="glass", segs=10)
            elif slot == "controls":
                for x in (-1, 1):
                    for y in (-1, 1):
                        p.cyl(0.004, 0.004, h, T((x * r * 1.05, y * r * 1.05, 0)), mat="iron", segs=4, bevel=0)
            elif slot == "core":
                p.cyl(r * 0.6, r * 0.2, h * 0.15, T((0, 0, 0.012)), mat="stone", segs=8, bevel=0)
            else:
                p.ring(0.015, 0.003, M(loc=(0, 0, h + 0.015), rot=(90, 0, 0)), mat="iron", segs=8, square=False)
    elif e in MACHINE:  # deco mantel clock in setbacks
        w, h = F(p, 0.22), F(p, 0.16)
        if slot == "shell":
            steps(p, w, 0.07, 0, 3, h / 3, mat="body", shrink=0.72)
        elif slot == "panel":
            p.cyl(h * 0.32, h * 0.32, 0.004, M(loc=(0, -0.037, h * 0.45), rot=(90, 0, 0)), mat="shell", segs=12, bevel=0)
        elif slot == "controls":
            fins(p, h * 0.33, h * 0.2, h * 0.7, 2, M(loc=(0, -0.03, 0)), mat="fit", depth=0.01)
        elif slot == "core":
            if e == "Steampunk":
                gear(p, h * 0.2, M(loc=(0, -0.04, h * 0.45), rot=(90, 0, 0)))
            elif e == "Wasteland":
                p.box((h * 0.5, 0.004, h * 0.15), T((0, -0.04, h * 0.45)), mat="glow", bevel=0)
            else:
                p.box((0.003, 0.003, h * 0.25), M(loc=(0, -0.04, h * 0.45), rot=(0, J(p, 35, 0.6), 0)), mat="iron", bevel=0)
        else:
            p.box((w * 1.1, 0.08, 0.012), T((0, 0, -0.006)), mat="accent" if e != "Wasteland" else "rust", bevel=0)
    else:  # floating ring of light between two fins
        r = F(p, 0.07)
        if slot == "shell":
            p.box((r * 2.4, 0.06, 0.02), T((0, 0, 0.01)), mat="body", bevel=0.3)
        elif slot == "panel":
            p.ring(r, 0.006, M(loc=(0, 0, r * 1.4), rot=(90, 0, 0)), mat="glow", segs=14)
        elif slot == "controls":
            for x in (-r * 1.1, r * 1.1):
                p.box((0.01, 0.03, r * 2), T((x, 0, r * 1.0 + 0.01)), mat="fit", bevel=0)
        elif slot == "core":
            p.box((0.003, 0.003, r * 0.7), M(loc=(0, 0, r * 1.4), rot=(0, J(p, 60, 0.6), 0)), mat="glow", bevel=0)
        else:
            p.ball(0.008, T((0, -0.031, 0.02)), mat="glow", segs=(5, 3))


for _g, _fns in (("Ocean", (_ocean_communicator, _ocean_console, _ocean_timepiece)),
                 ("Gale", (_gale_communicator, _gale_console, _gale_timepiece)),
                 ("Radiant", (_radiant_communicator, _radiant_console, _radiant_timepiece)),
                 ("Metropolis", (_metropolis_communicator, _metropolis_console, _metropolis_timepiece))):
    regional("Communicator", _g)(_fns[0])
    regional("GameConsole", _g)(_fns[1])
    regional("Timepiece", _g)(_fns[2])


# ---------------------------------------------------------------- vessels (body, lid, handle, band)

# Barrel bodies per region and era: (profile as (r fraction, z fraction), material). The silhouette carries the
# region (Ocean tubs, Gale gourds and oil drums, Radiant pot-bellied water vessels, Metropolis straight drums).
BARREL = {
    "Ocean": {
        "Primal": ([(0.9, 0), (1.0, 0.5), (0.95, 1)], "bamboo"), "Agrarian": ([(0.92, 0), (1.04, 0.5), (0.92, 1)], "teak"),
        "Mercantile": ([(0.85, 0), (1.06, 0.3), (1.06, 0.7), (0.85, 1)], "lacquer"), "Industrial": ([(0.95, 0), (0.95, 1)], "steel"),
        "Steampunk": ([(0.8, 0), (1.0, 0.15), (1.0, 0.85), (0.8, 1)], "brass"), "Future": ([(0.9, 0), (1.0, 0.05), (1.0, 0.95), (0.9, 1)], "glass"),
        "Wasteland": ([(0.5, 0), (0.95, 0.25), (1.0, 0.5), (0.95, 0.75), (0.5, 1)], "paint"), "Ancient": ([(0.75, 0), (1.05, 0.4), (0.95, 0.85), (0.7, 1)], "stone"),
    },
    "Gale": {
        "Primal": ([(0.5, 0), (1.0, 0.25), (0.62, 0.55), (0.75, 0.75), (0.4, 1)], "gourd"), "Agrarian": ([(0.7, 0), (1.05, 0.4), (0.75, 0.9), (0.6, 1)], "clay"),
        "Mercantile": ([(0.7, 0), (1.1, 0.35), (1.0, 0.75), (0.45, 1)], "leather"), "Industrial": ([(0.95, 0), (0.95, 1)], "steel"),
        "Steampunk": ([(0.85, 0), (1.0, 0.2), (1.0, 0.8), (0.6, 1)], "brass"), "Future": ([(1.0, 0), (0.96, 0.33), (0.9, 0.66), (0.8, 1)], "clay"),
        "Wasteland": ([(0.95, 0), (0.92, 0.3), (0.97, 0.55), (0.93, 1)], "rust"), "Ancient": ([(0.8, 0), (1.0, 0.3), (0.85, 0.9), (0.6, 1)], "clay"),
    },
    "Radiant": {
        "Primal": ([(0.55, 0), (1.05, 0.45), (0.7, 0.85), (0.6, 1)], "clay"), "Agrarian": ([(0.5, 0), (1.08, 0.4), (0.6, 0.85), (0.65, 1)], "copper"),
        "Mercantile": ([(0.6, 0), (1.05, 0.35), (0.95, 0.8), (0.55, 1)], "brass"), "Industrial": ([(0.95, 0), (0.95, 1)], "iron"),
        "Steampunk": ([(0.6, 0), (0.9, 0.1), (1.0, 0.55), (0.75, 1)], "brass"), "Future": ([(0.6, 0), (1.0, 0.35), (0.95, 0.75), (0.7, 1)], "shell"),
        "Wasteland": ([(0.95, 0), (0.95, 1)], "tarp"), "Ancient": ([(0.6, 0), (1.05, 0.4), (0.7, 0.9), (0.75, 1)], "sandstone"),
    },
    "Metropolis": {
        "Primal": ([(0.9, 0), (1.0, 0.5), (0.85, 1)], "iron"), "Agrarian": ([(0.85, 0), (1.08, 0.5), (0.85, 1)], "wood"),
        "Mercantile": ([(0.88, 0), (1.04, 0.5), (0.88, 1)], "wood_dark"), "Industrial": ([(0.95, 0), (0.95, 1)], "chrome"),
        "Steampunk": ([(0.85, 0), (1.0, 0.1), (1.0, 0.9), (0.85, 1)], "brass"), "Future": ([(0.85, 0), (0.95, 0.08), (0.95, 0.92), (0.85, 1)], "shell_dark"),
        "Wasteland": ([(0.95, 0), (0.9, 0.4), (0.97, 0.6), (0.95, 1)], "rust"), "Ancient": ([(0.8, 0), (1.0, 0.2), (1.0, 0.8), (0.8, 1)], "stone_dark"),
    },
}

JAR = {
    "Ocean": {  # bamboo tube, martaban jar with lugs, lacquer, sheet-tin can, brass diving-helmet jar, clear capsule, buoy, stone
        "Primal": ([(0.55, 0), (0.55, 1)], "bamboo"), "Agrarian": ([(0.55, 0), (1.0, 0.4), (0.8, 0.82), (0.45, 0.9), (0.5, 1)], "glaze"),
        "Mercantile": ([(0.55, 0), (0.95, 0.3), (1.0, 0.6), (0.5, 0.85), (0.55, 1)], "lacquer"), "Industrial": ([(0.8, 0), (0.8, 0.9), (0.6, 1)], "steel"),
        "Steampunk": ([(0.7, 0), (1.0, 0.35), (0.9, 0.85), (0.55, 1)], "brass"), "Future": ([(0.75, 0), (0.85, 0.1), (0.85, 0.9), (0.75, 1)], "glass"),
        "Wasteland": ([(0.4, 0), (0.9, 0.3), (0.95, 0.55), (0.5, 0.95), (0.35, 1)], "paint"), "Ancient": ([(0.5, 0), (1.0, 0.45), (0.65, 0.88), (0.5, 1)], "stone"),
    },
    "Gale": {  # gourd, pot with a flared lip, brass-studded water skin, tin, brass, printed fog bottle, salvaged, clay relic
        "Primal": ([(0.5, 0), (1.0, 0.25), (0.45, 0.55), (0.65, 0.72), (0.2, 0.95), (0.22, 1)], "gourd"), "Agrarian": ([(0.5, 0), (1.0, 0.45), (0.7, 0.85), (0.85, 1)], "clay"),
        "Mercantile": ([(0.6, 0), (1.05, 0.4), (0.8, 0.8), (0.25, 0.95), (0.25, 1)], "leather"), "Industrial": ([(0.85, 0), (0.85, 0.9), (0.6, 1)], "steel"),
        "Steampunk": ([(0.8, 0), (0.95, 0.3), (0.85, 0.8), (0.4, 1)], "brass"), "Future": ([(0.9, 0), (0.85, 0.3), (0.75, 0.6), (0.5, 0.85), (0.35, 1)], "clay"),
        "Wasteland": ([(0.85, 0), (0.85, 0.85), (0.4, 0.95), (0.4, 1)], "rust"), "Ancient": ([(0.5, 0), (1.0, 0.4), (0.55, 0.85), (0.7, 1)], "clay"),
    },
    "Radiant": {  # oil lamp jar, lota, enamelled spice jar, tin, brass samovar jar, white shell, patched tin, sandstone
        "Primal": ([(0.4, 0), (1.0, 0.4), (0.5, 0.75), (0.6, 1)], "clay"), "Agrarian": ([(0.45, 0), (1.05, 0.45), (0.55, 0.78), (0.4, 0.88), (0.7, 1)], "copper"),
        "Mercantile": ([(0.5, 0), (1.0, 0.4), (0.85, 0.8), (0.55, 1)], "enamel"), "Industrial": ([(0.8, 0), (0.8, 1)], "iron"),
        "Steampunk": ([(0.6, 0), (0.95, 0.25), (0.95, 0.7), (0.5, 1)], "brass"), "Future": ([(0.5, 0), (1.0, 0.35), (0.9, 0.8), (0.55, 1)], "shell"),
        "Wasteland": ([(0.8, 0), (0.8, 0.9), (0.55, 1)], "tarp"), "Ancient": ([(0.45, 0), (1.05, 0.45), (0.5, 0.85), (0.65, 1)], "sandstone"),
    },
    "Metropolis": {  # meteor bowl, iron pot, glass apothecary jar, chrome deco canister, brass gauge jar, holo canister, scrap
        "Primal": ([(0.7, 0), (1.0, 0.5), (0.85, 1)], "iron"), "Agrarian": ([(0.7, 0), (0.95, 0.4), (0.85, 0.9), (0.9, 1)], "iron"),
        "Mercantile": ([(0.8, 0), (0.85, 0.8), (0.55, 0.9), (0.6, 1)], "glass"), "Industrial": ([(0.75, 0), (0.75, 0.6), (0.6, 0.8), (0.45, 1)], "chrome"),
        "Steampunk": ([(0.8, 0), (0.85, 0.8), (0.6, 1)], "brass"), "Future": ([(0.7, 0), (0.75, 0.1), (0.75, 0.9), (0.7, 1)], "shell_dark"),
        "Wasteland": ([(0.85, 0), (0.85, 0.9), (0.6, 1)], "rust"), "Ancient": ([(0.6, 0), (0.95, 0.5), (0.6, 1)], "stone_dark"),
    },
}


def _profile(table, p, r, h):
    prof, mat = table[p.region][p.era]
    return [(f * r, z * h) for f, z in prof], mat


def _region_lid(p, r, h, body_mat):
    g, e = p.region, p.era
    if g == "Ocean":
        # Woven cone like a sun hat; Future a clear dome; Wasteland a net stretched over.
        if e == "Wasteland":
            p.box((r * 1.8, r * 1.8, 0.004), M(loc=(0, 0, h + 0.01), rot=(0, 0, 45)), mat="rope", bevel=0)
        else:
            p.lathe([(r * 1.05, h), (r * 0.5, h + r * 0.35), (0, h + r * 0.5)], mat="rattan" if e in HAND else "fit" if e != "Future" else "glass", segs=12)
    elif g == "Gale":
        p.cyl(r * 0.9, r * 0.9, 0.02, T((0, 0, h)), mat="wood" if e in HAND else "metal", segs=10, bevel=0)
        p.cyl(0.015, 0.012, 0.05, T((0, 0, h + 0.02)), mat="wood" if e != "Future" else "glow", segs=5, bevel=0)
    elif g == "Radiant":
        dome(p, r * 0.75, h, mat="fit" if e not in ("Primal", "Wasteland") else body_mat, segs=10)
    else:
        if e == "Industrial":
            steps(p, r * 1.6, r * 1.6, h, 2, 0.02, mat="metal", shrink=0.7)
        elif e == "Future":
            p.cyl(r * 0.9, r * 0.7, 0.03, T((0, 0, h)), mat="fit", segs=12, bevel=0)
            p.ring(r * 0.75, 0.006, T((0, 0, h + 0.03)), mat="glow", segs=12)
        else:
            p.cyl(r * 0.9, r * 0.9, 0.02, T((0, 0, h - 0.005)), mat="fit" if e not in ("Primal",) else "stone_dark", segs=10, bevel=0)


def _region_handle(p, r, h):
    g, e = p.region, p.era
    if g == "Ocean":
        for x in (-1, 1):
            horn(p, x * r * 0.95, 0, h * 0.75, r * 0.4, x, mat="fit" if e != "Ancient" else "glow")
    elif g == "Gale":
        p.tube([(-r * 0.9, 0, h * 0.85), (0, -r * 0.5, h * 1.3), (r * 0.9, 0, h * 0.85)], 0.012, mat="leather", segs=5)
    elif g == "Radiant":
        for x in (-1, 1):
            p.ring(r * 0.18, r * 0.03, M(loc=(x * r * 1.02, 0, h * 0.6), rot=(0, 90, 0)), mat="fit", segs=8, square=False)
    else:
        if e in HAND:
            p.tube([(-r * 0.9, 0, h * 0.7), (-r * 1.1, 0, h * 0.62), (-r * 0.9, 0, h * 0.54)], 0.01, mat="metal", segs=4)
            p.tube([(r * 0.9, 0, h * 0.7), (r * 1.1, 0, h * 0.62), (r * 0.9, 0, h * 0.54)], 0.01, mat="metal", segs=4)
        else:
            for x in (-1, 1):
                p.box((0.02, r * 0.5, 0.025), T((x * r * 1.0, 0, h * 0.8)), mat="fit")


def _region_band(p, r, h):
    g, e = p.region, p.era
    if g == "Metropolis" and e in ("Industrial", "Future", "Ancient"):
        fins(p, r * 0.93, h * 0.1, h * 0.9, 6, mat="fit")
        if e == "Future":
            p.ring(r * 0.97, 0.008, T((0, 0, h * 0.5)), mat="glow", segs=12)
        return
    signature(p, r * 0.97, h * J(p, 0.5, 0.25), 0.05)
    if e in ("Industrial", "Steampunk", "Future", "Wasteland", "Ancient"):
        era_mark(p, r * 0.97, h * 0.3)


@regional("Barrel", "Ocean")
@regional("Barrel", "Gale")
@regional("Barrel", "Radiant")
@regional("Barrel", "Metropolis")
def barrel(p, slot):
    h, r = F(p, 0.9, 0.1), F(p, 0.3, 0.1)
    prof, mat = _profile(BARREL, p, r, h)
    if slot == "body":
        p.lathe(prof, mat=mat, segs=12)
        if p.region == "Ocean" and p.era == "Primal":
            for z in (0.33, 0.66):
                p.ring(r * 1.0, 0.012, T((0, 0, h * z)), mat="bamboo", segs=12)
        elif p.region == "Gale" and p.era == "Future":
            for i in range(4):
                p.ring(r * (0.98 - i * 0.05), 0.01, T((0, 0, h * (0.15 + i * 0.22))), mat="clay", segs=12)
    elif slot == "lid":
        _region_lid(p, prof[-1][0], h, mat)
    elif slot == "handle":
        _region_handle(p, r, h)
    else:
        _region_band(p, r, h)


@regional("Jar", "Ocean")
@regional("Jar", "Gale")
@regional("Jar", "Radiant")
@regional("Jar", "Metropolis")
def jar(p, slot):
    h, r = F(p, 0.42, 0.12), F(p, 0.15, 0.12)
    prof, mat = _profile(JAR, p, r, h)
    top = prof[-1][0]
    g, e = p.region, p.era
    if slot == "body":
        p.lathe(prof, mat=mat, segs=12)
        if g == "Ocean" and e == "Primal":
            p.ring(top * 1.06, 0.01, T((0, 0, h * 0.5)), mat="bamboo", segs=10)
    elif slot == "lid":
        if g == "Ocean" and e == "Primal":
            p.ball(top * 1.1, M(loc=(0, 0, h), scale=(1, 1, 0.5)), mat="rattan", segs=(8, 4))
        elif g == "Gale" and e in ("Primal", "Mercantile"):
            p.cyl(top * 0.9, top * 0.9, 0.04, T((0, 0, h)), mat="wood" if e == "Primal" else "brass", segs=8, bevel=0)
        elif g == "Radiant" and e == "Primal":
            p.tube([(top, 0, h), (top * 2.2, 0, h + 0.01)], 0.012, mat="clay", segs=5)  # the spout of an oil lamp
            p.ball(0.012, T((top * 2.2, 0, h + 0.025)), mat="glow_dim", segs=(5, 3))
        else:
            _region_lid(p, top, h, mat)
    elif slot == "handle":
        if g == "Ocean" and e == "Agrarian":
            for i in range(4):
                a = i * math.tau / 4
                p.ring(0.018, 0.005, M(loc=(math.cos(a) * r * 0.85, math.sin(a) * r * 0.85, h * 0.78), rot=(0, 90, math.degrees(a) + 90)), mat="glaze", segs=6)
        elif g == "Radiant" and e == "Agrarian":
            p.tube([(top * 0.9, 0, h * 0.7), (r * 1.25, 0, h * 0.45)], 0.01, mat="copper", segs=5)
        elif g == "Gale" and e == "Mercantile":
            p.tube([(-r * 0.8, 0, h * 0.75), (0, 0, h * 1.25), (r * 0.8, 0, h * 0.75)], 0.008, mat="leather", segs=4)
        else:
            _region_handle(p, r * 0.9, h)
    else:
        if g == "Gale" and e == "Mercantile":
            for i in range(8):
                a = i * math.tau / 8
                p.ball(0.008, T((math.cos(a) * r * 1.04, math.sin(a) * r * 1.04, h * 0.4)), mat="brass", segs=(4, 3))
        else:
            _region_band(p, r * 0.9, h)


@regional("Crate", "Ocean")
def ocean_crate(p, slot):
    """Woven rattan hamper under a saddle lid whose ends sweep up into horns."""
    e = p.era
    s = F(p, 0.6, 0.1)
    if slot == "body":
        mat = {"Primal": "rattan", "Agrarian": "rattan", "Mercantile": "lacquer", "Industrial": "steel", "Steampunk": "brass",
               "Future": "glass", "Wasteland": "paint", "Ancient": "stone"}[e]
        p.box((s, s * 0.75, s * 0.7), T((0, 0, s * 0.35)), mat=mat, bevel=0.06)
        if e in ("Primal", "Agrarian", "Wasteland"):
            for z in (0.2, 0.45):
                p.box((s * 1.01, s * 0.76, 0.012), T((0, 0, s * z)), mat="rattan" if e != "Wasteland" else "rope", bevel=0)
    elif slot == "lid":
        roof = [(-s * 0.55, 0), (-s * 0.62, s * 0.08), (0, s * 0.22), (s * 0.62, s * 0.08), (s * 0.55, 0)]
        p.plate(roof, s * 0.8, M(loc=(0, 0, s * 0.7)) @ M(rot=(0, 0, 0)), mat="teak" if e in HAND else "fit" if e != "Future" else "glass")
    elif slot == "handle":
        for x in (-1, 1):
            horn(p, x * s * 0.58, 0, s * 0.76, s * 0.2, x, mat="body" if e != "Ancient" else "glow")
    else:
        if e == "Future":
            p.box((s * 1.005, s * 0.755, 0.012), T((0, 0, s * 0.1)), mat="glow", bevel=0)
            for i in range(3):
                p.ball(s * 0.05, M(loc=((i - 1) * s * 0.25, 0, s * 0.35), scale=(1.4, 1, 0.6)), mat="glow", segs=(6, 4))
        elif e == "Wasteland":
            p.ball(s * 0.12, T((s * 0.5, -s * 0.38, s * 0.5)), mat="paint", segs=(8, 5))
        else:
            for x in (-1, 1):
                p.box((0.03, s * 0.78, 0.03), T((x * s * 0.48, 0, s * 0.68)), mat="fit")
            era_mark(p, s * 0.2, s * 0.35, M(loc=(0, -s * 0.18, 0)))


@regional("Crate", "Gale")
def gale_crate(p, slot):
    """Earth-walled bin: battered sides, beam ends through the corners, a painted frieze."""
    e = p.era
    s = F(p, 0.6, 0.1)
    if slot == "body":
        mat = {"Primal": "wood", "Agrarian": "clay", "Mercantile": "wood_dark", "Industrial": "steel", "Steampunk": "brass",
               "Future": "clay", "Wasteland": "rust", "Ancient": "clay"}[e]
        p.lathe([(s * 0.62, 0), (s * 0.5, s * 0.75)], M(rot=(0, 0, 45)), mat=mat, segs=4)
    elif slot == "lid":
        p.box((s * 0.75, s * 0.75, 0.03), T((0, 0, s * 0.765)), mat="wood" if e in HAND else "metal")
        for x in (-1, 1):
            p.cyl(0.012, 0.0, s * 0.12, T((x * s * 0.32, -s * 0.32, s * 0.78)), mat="body" if e != "Future" else "glow", segs=4, bevel=0)
    elif slot == "handle":
        for z in (0.25, 0.6):
            for a in (0, 90, 180, 270):
                p.cyl(0.015, 0.013, s * 0.12, M(rot=(0, 0, a)) @ M(loc=(s * 0.52 - (z - 0.25) * s * 0.2, 0, s * z), rot=(0, 90, 0)), mat="wood" if e not in ("Future", "Ancient") else "fit", segs=4, bevel=0)
    else:
        if e == "Wasteland":
            p.ring(s * 0.5, s * 0.08, T((0, 0, s * 0.07)), mat="rubber", segs=8)
        else:
            zig(p, s * 0.45, s * 0.5, s * 0.08, 8, M(rot=(0, 0, 0)))
            if e in ("Steampunk", "Future", "Ancient"):
                era_mark(p, s * 0.3, s * 0.4, M(loc=(0, -s * 0.15, 0)))


@regional("Crate", "Radiant")
def radiant_crate(p, slot):
    """Spice chest: domed lid, brass corners, lotus feet."""
    e = p.era
    s = F(p, 0.6, 0.1)
    if slot == "body":
        mat = {"Primal": "clay", "Agrarian": "wood", "Mercantile": "wood_dark", "Industrial": "iron", "Steampunk": "marble",
               "Future": "shell", "Wasteland": "tarp", "Ancient": "sandstone"}[e]
        p.box((s, s * 0.65, s * 0.5), T((0, 0, s * 0.33)), mat=mat)
    elif slot == "lid":
        p.lathe([(s * 0.5, 0), (s * 0.48, s * 0.12), (s * 0.3, s * 0.2), (0, s * 0.24)], M(loc=(0, 0, s * 0.58), scale=(1, 0.65, 1)), mat="fit" if e not in ("Primal", "Wasteland") else "body", segs=12)
    elif slot == "handle":
        for x in (-1, 1):
            for y in (-1, 1):
                p.lathe([(0, 0), (s * 0.06, s * 0.03), (s * 0.045, s * 0.08)], T((x * s * 0.42, y * s * 0.26, 0)), mat="fit", segs=6)
    else:
        if e == "Wasteland":
            for i in range(2):
                p.box((s * 0.4, 0.006, s * 0.3), M(loc=((i - 0.5) * s * 0.45, -s * 0.33, s * 0.35), rot=(0, (i * 2 - 1) * 8, 0)), mat=("tarp", "paint")[i], bevel=0)
        else:
            petals(p, s * 0.12, 0, 6, s * 0.04, M(loc=(0, -s * 0.33, s * 0.33), rot=(90, 0, 0)), mat="accent", tilt=0)
            for x in (-1, 1):
                p.box((s * 0.1, s * 0.67, s * 0.06), T((x * s * 0.46, 0, s * 0.55)), mat="fit", bevel=0)


@regional("Crate", "Metropolis")
def metropolis_crate(p, slot):
    """Travelling trunk: leather and brass clasps; deco setbacks; finned cargo case; scrap box."""
    e = p.era
    s = F(p, 0.6, 0.1)
    if slot == "body":
        mat = {"Primal": "iron", "Agrarian": "wood", "Mercantile": "leather", "Industrial": "chrome", "Steampunk": "brass",
               "Future": "shell_dark", "Wasteland": "rust", "Ancient": "stone_dark"}[e]
        p.box((s, s * 0.55, s * 0.55), T((0, 0, s * 0.275)), mat=mat, noise=0.05 if e == "Primal" else None)
    elif slot == "lid":
        if e == "Industrial":
            steps(p, s, s * 0.55, s * 0.55, 2, s * 0.06, mat="fit", shrink=0.8)
        elif e in ("Mercantile", "Agrarian", "Steampunk"):
            p.cyl(s * 0.28, s * 0.28, s, M(loc=(-s / 2, 0, s * 0.55), rot=(0, 90, 0), scale=(1, 1, 1)), mat="body", segs=8, bevel=0)
        else:
            p.box((s * 1.02, s * 0.57, s * 0.08), T((0, 0, s * 0.59)), mat="fit")
    elif slot == "handle":
        if e in HAND:
            p.tube([(-s * 0.12, 0, s * 0.62), (0, 0, s * 0.7), (s * 0.12, 0, s * 0.62)], 0.012, mat="leather" if e != "Primal" else "hide", segs=4)
        else:
            for x in (-1, 1):
                p.box((0.025, s * 0.2, 0.04), T((x * s * 0.51, 0, s * 0.4)), mat="metal")
    else:
        if e in ("Industrial", "Future", "Ancient"):
            for x in (-0.35, 0, 0.35):
                p.box((s * 0.04, s * 0.58, s * 0.5), T((x * s, 0, s * 0.27)), mat="fit", bevel=0)
            if e == "Future":
                p.box((s * 1.005, s * 0.555, 0.01), T((0, 0, s * 0.5)), mat="glow", bevel=0)
        elif e == "Wasteland":
            p.box((s * 0.4, 0.008, s * 0.25), M(loc=(-s * 0.2, -s * 0.28, s * 0.3), rot=(0, 6, 0)), mat="shell_dark", bevel=0)
            p.box((s * 0.3, 0.004, s * 0.06), T((-s * 0.2, -s * 0.286, s * 0.3)), mat="glow", bevel=0)
        else:
            for x in (-s * 0.3, s * 0.3):
                p.box((0.04, 0.012, 0.05), T((x, -s * 0.28, s * 0.5)), mat="brass" if e != "Primal" else "stone_dark")
            for x in (-1, 1):
                for z in (0.02, 0.53):
                    p.box((0.05, s * 0.57, 0.04), T((x * s * 0.48, 0, s * z)), mat="metal" if e != "Mercantile" else "brass", bevel=0)
