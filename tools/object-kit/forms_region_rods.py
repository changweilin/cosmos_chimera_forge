"""Four-planet forms of the rods (cosmos_chimera everyday-objects.md#四星球形體, Q-A38 batch 2, hafted part 2).

FishingRod, Spindle, Brush, WalkingStaff, Flute and Horn for Ocean, Gale, Radiant and Metropolis in all 8 eras.
Same frame, slot meaning and haft-length tables as forms_rods.py (flutes and horns are their own haft; the butt is the
foot or mouthpiece), so the game's hand anchors fit both.

The mechanism keeps its era by tier (forms_region_pilot: hand-made / machine / high-tech): a hand-era spindle is a drop
spindle, a machine-era one a bobbin, a high-tech one a fibre pen; a machine-era flute has keys. The region decides the
shape: Ocean bamboo culms, rattan lashing, conch and upswept horn curls; Gale gourds, carved knobs, beam-end pegs and
painted zigzags; Radiant turned brass, lotus petals and onion domes; Metropolis by era (meteoric iron, art-deco
setbacks, sleek shell with light strips).
"""
import math

from mathutils import Matrix, Vector

from forms_region_pilot import HAND, MACHINE, dome, era_mark, gear, horn, lash, pegs, petals, r_butt, steps, zig
from forms_rods import disk, hafted, holes, line, rod
from kit_forms import J, coin, regional
from kit_lib import M, REGIONS

T = Matrix.Translation
HIGH = ("Future", "Ancient")


def _tier(e):
    return "hand" if e in HAND else "machine" if e in MACHINE else "high"


def _mark(p, r, z):
    """The era's own token for eras whose regional shape does not carry one."""
    if p.region != "Metropolis" and p.era in ("Steampunk", "Future", "Ancient", "Wasteland"):
        era_mark(p, r, z)


def _shaft(p, L, r, r_top=None, segs=7):
    """A region's straight pole from the grip (z = 0) to L."""
    g, e = p.region, p.era
    rt = r if r_top is None else r_top
    if g == "Ocean":
        p.cyl(r, rt, L, mat="body", segs=segs, bevel=0)
        n = 2 if L < 0.5 else 3
        for i in range(n):
            z = L * (0.2 + i * 0.6 / max(1, n - 1)) if n > 1 else L * 0.5
            k = r + (rt - r) * z / L
            p.cyl(k * 1.12, k * 1.12, k * 0.6, T((0, 0, z)), mat="body", segs=segs, bevel=0)
        if e == "Future":
            p.cyl(r * 0.35, rt * 0.35, L * 0.85, T((0, 0, L * 0.05)), mat="glow", segs=5, bevel=0)
    elif g == "Gale":
        p.cyl(r * 1.05, rt, L, mat="body", segs=segs, bevel=0)
        if e == "Wasteland":
            p.cyl(r * 1.4, r * 1.4, L * 0.12, T((0, 0, L * 0.04)), mat="rubber", segs=segs, bevel=0)
        else:
            zig(p, r * 1.05, L * 0.12, r * 2.4, 6)
    elif g == "Radiant":
        prof = [(r, 0)]
        for z in (0.12, 0.3):
            prof += [(r, L * z - r * 1.5), (r * 1.45, L * z), (r, L * z + r * 1.5)]
        prof.append((rt, L))
        p.lathe(prof, mat="body", segs=segs)
    else:
        if e == "Primal":
            p.cyl(r * 1.1, rt * 0.9, L, mat="body", segs=5, bevel=0, noise=0.06)
        elif e == "Industrial":
            p.cyl(r * 0.85, rt * 0.85, L, mat="body", segs=8, bevel=0)
            steps(p, r * 2.2, r * 2.2, L * 0.02, 2, r * 1.2, mat="chrome", shrink=0.85)
        elif e == "Future":
            p.box((r * 1.5, r * 1.1, L), T((0, 0, L / 2)), mat="body", bevel=0.3)
            p.box((r * 0.25, r * 0.2, L * 0.7), T((0, -r * 0.58, L * 0.45)), mat="glow", bevel=0)
        else:
            p.cyl(r, rt, L, mat="body", segs=segs, bevel=0)
            p.cyl(r * 1.15, r * 1.12, L * J(p, 0.12, 0.2), T((0, 0, L * 0.03)), mat="grip", segs=segs, bevel=0)


def _bind(p, r, z, h):
    """A region's band around a round part."""
    g = p.region
    if g == "Ocean":
        lash(p, r, z, h, segs=6)
    elif g == "Gale":
        p.cyl(r * 1.12, r * 1.12, h, T((0, 0, z - h / 2)), mat="fit", segs=6, bevel=0)
    elif g == "Radiant":
        p.ring(r * 1.05, h * 0.2, T((0, 0, z)), mat="fit", segs=8, square=False)
    else:
        p.band(r * 1.05, z, h=h)


# ================================================================ FishingRod


def _rod_haft(p, L, r):
    _shaft(p, L, r * 1.2, r * 0.45)


def _rod_head(p, L, r):
    g, e = p.region, p.era
    drop, lean = J(p, 0.55, 0.2), J(p, 0.08, 0.3)
    hang = (0, -lean - 0.06, L - drop)
    fz = L - drop * 0.5
    fy = -lean * 0.6
    if e == "Primal":
        # Spearing, not angling: each region's fish spear on the pole top.
        if g == "Ocean":  # three-pronged bamboo spear, prongs curling out
            for s in (-1, 0, 1):
                p.tube([(0, 0, L - 0.02), (s * 0.02, 0, L + 0.08), (s * 0.035, -0.005, L + 0.18)], 0.004, mat="bone", segs=4)
            lash(p, r * 1.3, L, 0.03, segs=6)
        elif g == "Gale":  # barbed point on a tang through a knob
            p.ball(r * 1.8, T((0, 0, L)), mat="body", segs=(6, 4))
            p.cyl(r * 0.7, 0.0, J(p, 0.18, 0.15), T((0, 0, L)), mat="bone", segs=5, bevel=0)
            pegs(p, r * 1.6, L, 3, r * 1.5)
        elif g == "Radiant":  # clay-weighted net cast from the pole: a hanging net bag
            line(p, [(0, 0, L), (0, -0.05, L - 0.15), hang])
            p.lathe([(0, 0), (0.05, 0.04), (0.045, 0.09), (0, 0.1)], T((hang[0], hang[1], hang[2] - 0.1)), mat="rope", segs=6)
        else:  # meteoric iron harpoon
            p.cyl(r * 1.1, 0.0, J(p, 0.22, 0.15), T((0, 0, L - 0.02)), mat="iron", segs=5, bevel=0, noise=0.1)
            for s in (-1, 1):
                rod(p, (0, 0, L + 0.08), (s * 0.015, -0.004, L + 0.05), 0.004, 0.001, mat="iron", segs=3)
        return
    line(p, [(0, 0, L), (0, fy, L - drop * 0.4), hang])
    if g == "Ocean":  # bamboo float, hook curled like a horn
        p.cyl(0.006, 0.006, 0.05, T((0, fy, fz - 0.02)), mat="body" if e != "Future" else "glow", segs=5, bevel=0)
        p.tube([hang, (0, hang[1], hang[2] - 0.025), (0, hang[1] - 0.012, hang[2] - 0.03), (0, hang[1] - 0.015, hang[2] - 0.015)],
               0.002, mat="metal" if e not in HIGH else "glow", segs=3)
    elif g == "Gale":  # gourd float (two lobes)
        p.ball(0.013, T((0, fy, fz)), mat="gourd" if e in HAND else "accent", segs=(6, 4))
        p.ball(0.008, T((0, fy, fz + 0.016)), mat="gourd" if e in HAND else "accent", segs=(5, 3))
        rod(p, hang, (0, hang[1], hang[2] - 0.03), 0.002, mat="iron", segs=3)
    elif g == "Radiant":  # lotus float
        petals(p, 0.006, fz, 4, 0.007, M(loc=(0, fy, 0)), mat="accent", tilt=40)
        rod(p, hang, (0, hang[1], hang[2] - 0.03), 0.002, mat="fit", segs=3)
    else:
        if e == "Industrial":  # spoon lure and a tip guide
            p.box((0.012, 0.004, 0.035), T((0, hang[1], hang[2] - 0.02)), mat="chrome", bevel=0)
            p.ring(r * 0.6, 0.0015, T((0, -r * 0.6, L - 0.03)) @ M(rot=(90, 0, 0)), mat="chrome", segs=6)
        elif e == "Future":
            p.box((0.02, 0.012, 0.03), T((0, fy, fz)), mat="body", bevel=0.3)
            p.ball(0.008, T(hang), mat="glow", segs=(5, 3))
        else:  # two-tone bobber
            p.lathe([(0, 0), (0.012, 0.012), (0.008, 0.03), (0, 0.045)], T((0, fy, fz - 0.02)), mat="paint", segs=6)
            rod(p, hang, (0, hang[1] - 0.01, hang[2] - 0.025), 0.002, mat="iron", segs=3)
            if e == "Steampunk":
                p.ball(0.005, T((0, fy, fz + 0.03)), mat="glow", segs=(5, 3))


def _rod_joint(p, L, r):
    g, e = p.region, p.era
    t = _tier(e)
    z = L * J(p, 0.2, 0.1)
    if e == "Primal":
        _bind(p, r * 1.2, L * 0.85, 0.04)
        return
    if g == "Ocean":  # rattan-wrapped bamboo spool on a stub
        disk(p, (r * 2.4, -0.01, z), J(p, 0.024, 0.1), 0.03, "x", "body" if t != "high" else "shell", segs=7)
        lash(p, 0.024, 0, 0.02, M(loc=(r * 2.4, -0.01, z), rot=(0, 90, 0)), segs=6)
        p.tube([(r, 0, z), (r * 2.4, -0.01, z)], 0.004, mat="fit", segs=4)
    elif g == "Gale":  # line wound on pegs through the pole
        for zz in (z, z + 0.08):
            pegs(p, r, zz, 2, 0.03, mat="fit")
        p.cyl(0.006, 0.006, 0.08, T((0, -0.025, z)), mat="rope", segs=5, bevel=0)
    elif g == "Radiant":  # brass drum reel, lotus hub
        disk(p, (r * 2.4, -0.012, z), J(p, 0.03, 0.1), 0.022, "x", "fit", segs=8)
        petals(p, 0.008, 0, 4, 0.006, M(loc=(r * 2.4 + 0.012, -0.012, z), rot=(0, 90, 0)), mat="accent", tilt=70)
        p.tube([(r, 0, z), (r * 2.4, -0.012, z)], 0.004, mat="fit", segs=4)
    else:
        if t == "hand":
            for zz in (z, z + 0.08):
                rod(p, (0, 0, zz), (0, -0.04, zz), 0.005, mat="body", segs=5)
        elif t == "machine":  # stepped reel housing
            steps(p, 0.04, 0.03, z - 0.02, 3, 0.012, M(loc=(0, -0.035, 0)), mat="chrome" if e == "Industrial" else "metal", shrink=0.8)
            if e == "Steampunk":
                gear(p, 0.014, M(loc=(0.022, -0.035, z), rot=(0, 90, 0)))
        else:
            p.box((r * 2.6, r * 2.2, 0.07), T((0, -r * 0.8, z)), mat="body", bevel=0.2, bevel_seg=1)
            p.box((r * 1.6, 0.003, 0.035), T((0, -r * 1.92, z)), mat="glow", bevel=0)
    _mark(p, r * 0.9, L * 0.45)


# ================================================================ Spindle


def _sp_haft(p, L, r):
    g, e = p.region, p.era
    t = _tier(e)
    if t == "hand":
        p.lathe([(r * 0.5, 0), (r, L * 0.3), (r * 0.9, L * 0.7), (r * 0.4, L)], mat="body", segs=6)
    elif t == "machine":
        p.cyl(r * 0.7, r * 0.55, L, mat="metal" if g != "Ocean" else "body", segs=6, bevel=0)
    else:  # fibre pen body in the region's shell
        if g == "Metropolis":
            p.box((r * 2.2, r * 1.8, L), T((0, 0, L / 2)), mat="body", bevel=0.3)
        else:
            p.lathe([(r * 0.5, 0), (r * 1.4, L * 0.15), (r * 1.4, L * 0.85), (r * 0.9, L)], mat="body", segs=8)


def _sp_head(p, L, r):
    g, e = p.region, p.era
    t = _tier(e)
    z = L * 0.18
    R = J(p, 0.032, 0.15)
    if t == "hand":  # the whorl
        if g == "Ocean":  # half coconut shell
            p.lathe([(r, z), (R, z + 0.004), (R * 0.7, z + 0.02), (r, z + 0.026)], mat="bark" if e == "Primal" else "accent", segs=8)
        elif g == "Gale":  # clay disc with pegs on its rim
            p.cyl(R, R, 0.01, T((0, 0, z)), mat="clay", segs=7, bevel=0)
            pegs(p, R, z + 0.005, 4, 0.008, mat="accent")
        elif g == "Radiant":  # brass takli disc, petalled rim
            p.cyl(R, R * 0.9, 0.004, T((0, 0, z)), mat="fit", segs=8, bevel=0)
            petals(p, R * 0.8, z, 5, 0.006, mat="accent", tilt=80)
        else:
            p.cyl(R, R * 0.8, 0.012, T((0, 0, z)), mat="iron", segs=6, bevel=0, noise=0.05 if e == "Primal" else 0)
    elif t == "machine":  # bobbin flanges
        for zz in (L * 0.35, L * 0.85):
            if g == "Ocean":
                lash(p, R * 0.8, zz, 0.01, segs=6)
            elif g == "Gale":
                p.cyl(R, R, 0.006, T((0, 0, zz)), mat="body", segs=6, bevel=0)
                pegs(p, R, zz + 0.003, 3, 0.006)
            elif g == "Radiant":
                p.cyl(R * 0.95, R, 0.006, T((0, 0, zz)), mat="fit", segs=8, bevel=0)
            else:
                steps(p, R * 1.6, R * 1.6, zz, 2, 0.004, mat="chrome", shrink=0.75)
        if e == "Steampunk":
            gear(p, 0.014, M(loc=(0, -0.012, L * 0.6), rot=(90, 0, 0)))
    else:  # nozzle
        if g == "Radiant":
            dome(p, r * 1.3, L, finial=False, segs=8, mat="fit")
        elif g == "Gale":
            p.lathe([(r * 1.3, L), (r * 0.6, L + 0.02), (r * 0.2, L + 0.03)], mat="clay", segs=7)
        elif g == "Ocean":
            p.ball(r * 1.6, M(loc=(0, 0, L + 0.006), scale=(1, 1, 1.4)), mat="glass", segs=(6, 4))
        else:
            p.box((r * 1.4, r * 1.2, 0.02), T((0, 0, L + 0.01)), mat="chrome", bevel=0)
        p.ball(r * 0.4, T((0, 0, L + 0.03)), mat="glow", segs=(5, 3))


def _sp_joint(p, L, r):
    e = p.era
    if _tier(e) == "high":  # fibre spool clipped on the side
        disk(p, (r * 1.8, 0, L * 0.6), J(p, 0.018, 0.1), 0.012, "x", "cloth", segs=8)
        return
    z0, z1 = L * 0.32, L * J(p, 0.75, 0.08)
    rr = J(p, 0.018, 0.2)
    p.lathe([(r, z0), (rr, z0 + (z1 - z0) * 0.25), (rr * 1.05, z0 + (z1 - z0) * 0.6), (r, z1)], mat="cloth" if e != "Primal" else "rope", segs=8)
    if e in ("Primal", "Agrarian"):
        line(p, [(0, 0, z1), (rr * 0.6, -0.01, L * 0.95), (0, -0.01, L + 0.05)], mat="rope")


def _sp_butt(p, L, r):
    g, e = p.region, p.era
    if g == "Ocean" and e in HAND:  # little horn hook at the top
        horn(p, 0, 0, L - 0.005, 0.012, 1, mat="body")
    elif g == "Radiant":
        p.lathe([(0, -0.02), (r * 1.6, -0.008), (r * 1.4, 0)], mat="fit", segs=6)
    elif _tier(e) == "high":
        p.ball(r * 0.7, T((0, 0, 0)), mat="shell_dark" if g != "Gale" else "clay", segs=(6, 4))
    else:
        h = J(p, 0.02, 0.3)
        p.cyl(0.0005, r * 0.6, h, T((0, 0, -h)), mat="metal", segs=5, bevel=0)


# ================================================================ Brush


def _br_haft(p, L, r):
    g, e = p.region, p.era
    if g == "Ocean":
        p.cyl(r, r * 0.95, L, mat="body", segs=7, bevel=0)
        p.cyl(r * 1.15, r * 1.15, r * 0.8, T((0, 0, L * 0.5)), mat="body", segs=7, bevel=0)
    elif g == "Gale":  # reed pen / chewing stick, knob at the top end
        p.cyl(r * 0.9, r * 1.05, L, mat="body", segs=6, bevel=0)
        p.ball(r * 1.6, T((0, 0, 0)), mat="body", segs=(6, 4))
    elif g == "Radiant":  # turned kalam
        p.lathe([(r * 0.7, 0), (r * 1.3, L * 0.15), (r, L * 0.3), (r * 1.2, L * 0.55), (r * 0.9, L)], mat="body", segs=7)
    else:
        if e == "Industrial":  # fountain pen body
            p.lathe([(r * 1.2, 0), (r * 1.4, L * 0.5), (r * 1.2, L)], mat="body", segs=8)
        elif e == "Future":
            p.box((r * 2.0, r * 1.6, L), T((0, 0, L / 2)), mat="body", bevel=0.3)
            p.box((r * 0.4, r * 0.3, L * 0.5), T((0, -r * 0.8, L * 0.5)), mat="glow", bevel=0)
        else:
            p.cyl(r * (1.1 if e == "Primal" else 1.0), r * 0.9, L, mat="body", segs=6 if e == "Primal" else 7, bevel=0, noise=0.05 if e == "Primal" else 0)


def _br_head(p, L, r):
    g, e = p.region, p.era
    h = J(p, 0.045, 0.2)
    t = _tier(e)
    if g == "Gale" and t != "high":  # cut reed nib
        p.cyl(r * 0.9, r * 0.2, h, T((0, 0, L)), mat="body" if t == "hand" else "metal", segs=5, bevel=0)
    elif g == "Radiant" and t != "high":  # brass ferrule, pointed tuft, petal collar
        p.cyl(r * 1.0, r * 1.25, h * 0.4, T((0, 0, L)), mat="fit", segs=7, bevel=0)
        p.lathe([(r * 1.2, L + h * 0.4), (r * 1.3, L + h * 0.6), (0, L + h * 1.2)], mat="hide", segs=7)
        petals(p, r * 1.2, L, 4, r * 0.6, mat="accent", tilt=40)
    elif g == "Ocean" and t != "high":  # frayed bamboo-fibre tip
        p.lathe([(r * 1.1, L), (r * 1.6, L + h * 0.4), (r * 0.8, L + h), (0, L + h * 1.05)], mat="rattan" if t == "hand" else "hide", segs=7)
        lash(p, r * 1.15, L, 0.01, segs=6)
    elif g == "Metropolis" and t != "high":
        if e == "Primal":
            p.cyl(r * 0.9, 0.0, h, T((0, 0, L)), mat="iron", segs=5, bevel=0, noise=0.08)
        elif e == "Industrial":  # nib
            p.plate([(-r, 0), (r, 0), (0, h * 0.9)], 0.0015, T((0, 0, L)), mat="gold", bevel=0)
            p.cyl(r * 1.2, r * 0.9, h * 0.3, T((0, 0, L - h * 0.1)), mat="chrome", segs=8, bevel=0)
        else:  # flat brush
            p.cyl(r * 1.0, r * 1.3, h * 0.6, T((0, 0, L)), mat="fit", segs=7, bevel=0)
            p.box((r * 2.8, r * 1.0, h * 0.7), T((0, 0, L + h * 0.95)), mat="hide", bevel=0)
    else:  # high-tech stylus tip in the region's shell
        mat = {"Ocean": "glass", "Gale": "clay", "Radiant": "fit", "Metropolis": "chrome"}[g]
        p.lathe([(r * 0.9, L), (r * 0.35, L + h * 0.6), (0, L + h * 0.7)], mat=mat, segs=7)
        p.ball(r * 0.5, T((0, 0, L + h * 0.72)), mat="glow", segs=(5, 3))


def _br_joint(p, L, r):
    g, e = p.region, p.era
    if g == "Ocean":  # horn-curl hanging end
        horn(p, 0, 0, -0.004, 0.02, -1, mat="fit")
    elif g == "Gale":
        zig(p, r * 1.05, L * 0.6, r * 2.5, 6)
    elif g == "Radiant":
        p.ring(r * 1.05, r * 0.25, T((0, 0, L * 0.55)), mat="accent", segs=7, square=False)
    else:
        if e == "Industrial":  # pocket clip
            p.box((r * 0.4, r * 0.4, L * 0.35), T((0, r * 1.3, L * 0.25)), mat="chrome", bevel=0)
        else:
            p.band(r * 1.05, L * J(p, 0.6, 0.1), h=0.008)
    _mark(p, r * 1.1, L * 0.3)


# ================================================================ WalkingStaff


def _st_haft(p, L, r):
    _shaft(p, L, r, r * 0.92)


def _st_head(p, L, r):
    g, e = p.region, p.era
    if g == "Ocean":  # two horns curling up and apart, the gable crown of a stilt house
        for s in (-1, 1):
            horn(p, 0, 0, L - 0.01, J(p, 0.06, 0.15), s, mat="body" if e in HAND else "accent")
        lash(p, r * 1.3, L - 0.02, 0.04, segs=6)
        if e == "Future":
            p.ball(r * 1.0, T((0, 0, L + 0.04)), mat="glow", segs=(5, 3))
    elif g == "Gale":  # knobkerrie head with beam-end pegs
        R = r * J(p, 3.0, 0.12)
        p.ball(R, M(loc=(0, 0, L + R * 0.8), scale=(1, 1, 1.15)), mat="body" if e not in MACHINE else "metal", segs=(7, 5))
        pegs(p, R * 0.9, L + R * 0.8, 4 if coin(p) else 5, R * 0.6, mat="fit")
    elif g == "Radiant":  # onion-dome finial over a lotus
        petals(p, r * 1.6, L, 5, r * 1.1, mat="accent", tilt=45)
        dome(p, r * J(p, 2.6, 0.12), L + r, mat="fit", segs=8)
    else:
        if e == "Primal":
            p.ball(r * 2.2, M(loc=(0, 0, L + r), scale=(1, 0.9, 1.4)), mat="iron", segs=(6, 4), noise=0.12)
        elif e == "Industrial":  # art-deco stepped pommel
            steps(p, r * 3.2, r * 3.2, L, 3, r * 0.9, mat="chrome", shrink=0.75)
        elif e == "Future":
            p.ball(r * 1.3, T((0, 0, L + 0.01)), mat="body", segs=(8, 5))
            p.ring(J(p, 0.05, 0.15), 0.006, T((0, 0, L + 0.06)) @ M(rot=(12, 0, 0)), mat="glow", segs=10)
        elif e == "Mercantile":  # silver-capped gentleman's cane
            p.lathe([(r, L), (r * 1.3, L + 0.02), (r * J(p, 1.9, 0.12), L + 0.05), (r * 1.4, L + 0.08), (0, L + 0.09)], mat="chrome", segs=8)
        else:  # crook
            R = J(p, 0.05, 0.12)
            p.tube([(0, 0, L)] + [(0, -R + R * math.cos(a), L + R * math.sin(a) * 1.1) for a in (0.7, 1.6, 2.5, 3.1)], r * 0.95,
                   mat="body", segs=6)
            if e == "Steampunk":
                gear(p, r * 1.2, M(loc=(r * 1.1, 0, L * 0.98), rot=(0, 90, 0)))
    _mark(p, r * 1.1, L * 0.9)


# ================================================================ Flute


def _fl_haft(p, L, r):
    g, e = p.region, p.era
    t = _tier(e)
    if g == "Ocean":  # bamboo suling: culm with a node near each end
        p.cyl(r, r * 0.96, L, mat="body", segs=7, bevel=0)
        for z in (0.06, 0.94):
            p.cyl(r * 1.1, r * 1.1, r * 0.6, T((0, 0, L * z)), mat="body", segs=7, bevel=0)
    elif g == "Gale":  # end-blown flute flaring into a gourd foot
        p.cyl(r * 0.9, r, L * 0.8, T((0, 0, L * 0.2)), mat="body", segs=7, bevel=0)
        p.ball(r * 2.0, M(loc=(0, 0, L * 0.12), scale=(1, 1, 1.3)), mat="gourd" if t == "hand" else "accent", segs=(7, 4))
    elif g == "Radiant":  # bansuri, slim
        p.cyl(r * 0.9, r * 0.88, L, mat="body", segs=8, bevel=0)
    else:
        if e == "Primal":
            p.cyl(r * 1.05, r * 0.95, L, mat="iron", segs=6, bevel=0, noise=0.04)
        elif e == "Future":
            p.box((r * 1.8, r * 1.8, L), T((0, 0, L / 2)), mat="body", bevel=0.3)
        else:
            p.lathe([(r * 1.2, 0), (r, L * 0.1), (r * 0.95, L * 0.9), (r * 1.15, L)], mat="body", segs=8)
    rad = r * (0.9 if g == "Radiant" else 1.0 if g != "Metropolis" or e != "Future" else 0.9)
    if t == "high":
        for i in range(5):
            disk(p, (0, -rad, L * (0.3 + i * 0.09)), r * 0.3, 0.003, "y", "glow", segs=5)
    else:
        holes(p, L * 0.3, L * 0.7, 6 if t == "machine" or g == "Radiant" else 5, r * 0.28, rad)


def _fl_head(p, L, r):
    g, e = p.region, p.era
    if g == "Ocean":  # rattan ring over the blowing end
        lash(p, r * 1.15, L * 0.9, 0.02, segs=6)
    elif g == "Gale":  # notched rim with a peg
        p.cyl(r * 1.15, r * 1.25, 0.012, T((0, 0, L - 0.012)), mat="fit", segs=6, bevel=0)
        pegs(p, r * 1.2, L - 0.006, 2, r * 1.2)
    elif g == "Radiant":  # silk-thread bands and a lotus cap
        p.ring(r * 0.95, 0.003, T((0, 0, L * 0.88)), mat="accent", segs=8, square=False)
        petals(p, r * 0.8, L, 4, r * 0.5, mat="fit", tilt=30)
    else:
        if e == "Industrial":  # lip plate and stepped crown
            p.box((r * 1.8, r * 0.5, r * 2.6), T((0, -r * 1.0, L * 0.88)), mat="chrome", bevel=0)
            steps(p, r * 2.2, r * 2.2, L, 2, r * 0.6, mat="chrome", shrink=0.7)
        elif e == "Future":
            p.ring(r * 1.25, r * 0.25, T((0, 0, L - 0.005)), mat="glow", segs=8)
        else:
            p.lathe([(r * 1.1, L), (r * 1.35, L + 0.02), (0, L + 0.03)], mat="fit", segs=7)
    disk(p, (0, -r, L * 0.9), r * 0.4, 0.003, "y", "rubber", segs=5)


def _fl_joint(p, L, r):
    g, e = p.region, p.era
    t = _tier(e)
    if t == "machine":  # keys along the bore
        p.box((r * 0.3, r * 0.3, L * 0.5), T((r * 0.95, -r * 0.4, L * 0.47)), mat="metal", bevel=0)
        for i in range(4):
            disk(p, (r * 0.6, -r * 0.8, L * (0.3 + i * 0.12)), r * 0.4, 0.004, "y", "metal", segs=5)
        if e == "Steampunk":
            gear(p, r * 0.9, M(loc=(r * 1.2, 0, L * 0.2), rot=(0, 90, 0)))
        return
    if g == "Ocean":
        lash(p, r * 1.05, L * 0.2, 0.015, segs=6)
    elif g == "Gale":
        zig(p, r * 1.02, L * 0.55, r * 2.2, 6)
    elif g == "Radiant":
        for z in (0.15, 0.22):
            p.ring(r * 0.95, 0.003, T((0, 0, L * z)), mat="accent", segs=8, square=False)
    else:
        p.band(r * 1.05, L * 0.5, h=0.012)
    _mark(p, r * 1.05, L * 0.8)


def _fl_butt(p, L, r):
    g, e = p.region, p.era
    if g == "Radiant":
        p.lathe([(0, -0.015), (r * 1.2, -0.005), (r * 0.95, 0)], mat="fit", segs=7)
    elif g == "Ocean" and e in HAND:  # carry cord ending in a shell
        line(p, [(0, 0, 0.005), (0.02, -0.004, -0.03), (0.005, -0.01, -0.06)], r=0.0015)
        p.ball(0.008, M(loc=(0.005, -0.01, -0.065), scale=(1, 0.5, 1.2)), mat="bone", segs=(5, 3))
    elif g == "Metropolis" and _tier(e) != "hand":
        p.lathe([(r * 1.1, -0.008), (r * 1.25, 0), (r * 1.0, 0.012)], mat="metal" if e != "Future" else "shell_dark", segs=8)
    else:
        line(p, [(0, 0, 0.005), (0.02, -0.004, -0.03), (0.005, -0.01, -0.06)], r=0.0015, mat="rope" if e != "Wasteland" else "rubber")


# ================================================================ Horn
# Hand eras blow a natural horn or shell, machine eras a metal horn, high-tech eras an emitter; the region shapes each.


def _horn_path(L, curl, sway=0.35):
    pts = []
    for i in range(6):
        t = i / 5
        a = t * curl
        pts.append(Vector((0, -math.sin(a) * L * sway, t * L * (1 - 0.25 * curl / math.pi))))
    return pts


def _cone_chain(p, pts, r0, r1, mat, segs=6):
    n = len(pts) - 1
    for i in range(n):
        rod(p, tuple(pts[i]), tuple(pts[i + 1]), r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n, mat=mat, segs=segs)


CURL = {"Ocean": 0.6, "Gale": 2.2, "Radiant": 1.4, "Metropolis": 0.3}


def _hn_pts(p, L):
    return _horn_path(L, CURL[p.region], 0.35 if p.region != "Radiant" else 0.5)


def _hn_haft(p, L, r):
    g, e = p.region, p.era
    t = _tier(e)
    if t == "high":
        if g == "Metropolis":
            p.box((r * 2.2, r * 1.8, L), T((0, 0, L / 2)), mat="body", bevel=0.3)
        else:
            p.lathe([(r * 0.8, 0), (r * 1.4, L * 0.1), (r * 1.3, L * 0.85), (r * 0.9, L)], mat="body", segs=8)
        p.box((r * 0.4, r * 0.3, L * 0.5), T((0, -r * 1.3, L * 0.45)), mat="glow", bevel=0)
        return
    if g == "Ocean" and t == "hand":  # triton conch: stacked whorls
        for i in range(3):
            k = 1 - i * 0.25
            p.ball(1.0, M(loc=(0, 0, L * (0.25 + i * 0.22)), rot=(0, 0, i * 40), scale=(r * 4.2 * k, r * 3.6 * k, L * 0.16)),
                   mat="bone" if e != "Primal" else "accent", segs=(7, 4))
        return
    mat = ("bone" if g != "Radiant" else "fit") if t == "hand" else "metal"
    _cone_chain(p, _hn_pts(p, L), r * 0.5, r * 1.4, mat)


def _hn_head(p, L, r):
    g, e = p.region, p.era
    t = _tier(e)
    if t == "high":
        R = J(p, 0.05, 0.15)
        if g == "Radiant":
            p.lathe([(r, L), (R, L + 0.03), (R * 0.8, L + 0.035), (0, L + 0.02)], mat="fit", segs=8)
            petals(p, R * 0.9, L + 0.02, 5, R * 0.3, mat="accent", tilt=60)
        elif g == "Metropolis":
            steps(p, R * 1.8, R * 1.8, L, 3, 0.01, mat="chrome", shrink=0.8)
        else:
            p.lathe([(r, L), (R, L + 0.03), (R * 1.05, L + 0.04), (0, L + 0.025)], mat="shell" if g == "Ocean" else "clay", segs=8)
        p.ring(R * 0.55, 0.004, T((0, 0, L + 0.03)), mat="glow", segs=8)
        return
    if g == "Ocean" and t == "hand":  # conch spire and lip
        p.lathe([(r * 1.8, L * 0.8), (r * 0.9, L * 0.95), (0, L * J(p, 1.05, 0.05))], mat="bone", segs=6)
        p.plate([(0, L * 0.2), (r * 3.0, L * 0.3), (r * 3.3, L * 0.6), (0, L * 0.7)], 0.006, T((0, -r * 3.4, 0)), mat="accent", bevel=0)
        return
    pts = _hn_pts(p, L)
    top, d = pts[-1], (pts[-1] - pts[-2]).normalized()
    m = T(top) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    R = J(p, 0.03 if t == "hand" else 0.055, 0.15)
    if g == "Ocean":  # bell whose rim sweeps up into horn tips
        p.lathe([(r * 1.4, 0), (R * 0.5, 0.04), (R, 0.08)], m, mat="metal", segs=8)
        for s in (-1, 1):
            p.tube([tuple(m @ Vector((s * R, 0, 0.08))), tuple(m @ Vector((s * R * 1.4, 0, 0.1))), tuple(m @ Vector((s * R * 1.3, 0, 0.13)))],
                   0.004, mat="accent", segs=4)
    elif g == "Gale":
        p.lathe([(r * 1.4, 0), (R, 0.04), (R * 0.95, 0.05)], m, mat="bone" if t == "hand" else "metal", segs=7)
        if t == "machine":
            pegs(p, R, 0.03, 4, R * 0.5, m)
    elif g == "Radiant":  # dragon-mouth bell: wide flare with a lotus ring
        p.lathe([(r * 1.4, 0), (R * 0.6, 0.04), (R * 1.1, 0.08), (R * 1.15, 0.085)], m, mat="fit", segs=8)
        petals(p, R * 0.6, 0.03, 5, R * 0.25, m, mat="accent", tilt=50)
    else:
        if e == "Primal":
            p.lathe([(r * 1.4, 0), (R, 0.04), (R * 0.9, 0.05)], m, mat="iron", segs=6, noise=0.08)
        elif e == "Industrial":
            steps(p, R * 1.8, R * 1.8, 0.0, 3, 0.02, m, mat="chrome", shrink=1.25)
        else:
            p.lathe([(r * 1.4, 0), (R * 0.4, 0.04), (R * 0.8, 0.08), (R, 0.1)], m, mat="metal", segs=8)


def _hn_joint(p, L, r):
    g, e = p.region, p.era
    if _tier(e) == "high":
        p.box((r * 0.8, r * 1.2, r * J(p, 1.6, 0.3)), T((0, -r * 1.6, L * 0.3)), mat="shell_dark", bevel=0)
        return
    if g == "Ocean" and _tier(e) == "hand":
        line(p, [(0, 0, L * 0.3), (r * 4, 0.01, L * 0.5), (0, 0, L * 0.7)], r=0.002, mat="fit")
        return
    pts = _hn_pts(p, L)
    a, b = pts[1], pts[4]
    line(p, [tuple(a), tuple((a + b) / 2 + Vector((0.03, 0.02, 0))), tuple(b)], r=0.003, mat="fit")
    if g == "Gale":
        zig(p, r * 1.0, 0, r * 2, 6, T(tuple(pts[2])))
    elif g == "Radiant":
        p.ring(r * 1.0, r * 0.25, T(tuple(pts[2])), mat="accent", segs=7, square=False)
    elif e == "Steampunk":
        p.cyl(r * 0.7, r * 0.7, r * 2, T(tuple(pts[2] + Vector((r * 0.6, 0, 0)))) @ M(rot=(0, 90, 0)), mat="metal", segs=6)
        p.ball(r * 0.4, T(tuple(pts[2] + Vector((r * 2.6, 0, 0)))), mat="glow", segs=(5, 3))
    else:
        for q in (a, b):
            p.ball(r * 0.9, T(tuple(q)), mat="fit", segs=(5, 3))
    if g != "Metropolis" and e in ("Steampunk", "Wasteland", "Ancient"):
        era_mark(p, r * 0.9, 0, T(tuple(pts[3])))


def _hn_butt(p, L, r):
    e = p.era
    if _tier(e) == "high":
        p.ball(r * 0.9, M(scale=(1, 1, 0.6)), mat="shell_dark", segs=(6, 4))
    elif _tier(e) == "hand":
        p.lathe([(0, -0.004), (r * 0.7, 0), (r * 0.6, 0.01)], mat="bone" if p.region != "Radiant" else "fit", segs=6)
    else:  # cup mouthpiece
        p.lathe([(r * 0.5, 0.01), (r * 0.5, -0.01), (r * 1.0, -0.02), (r * 0.9, -0.022)], mat="metal", segs=7)


def _rod_butt(p, L, r):
    r_butt(p, r)


ROD_L = {"Primal": 1.5, "Agrarian": 1.9, "Mercantile": 1.75, "Industrial": 1.7, "Steampunk": 1.6, "Future": 1.5, "Wasteland": 1.6, "Ancient": 1.55}
SPINDLE_L = {"Primal": 0.28, "Agrarian": 0.3, "Mercantile": 0.3, "Industrial": 0.24, "Steampunk": 0.26, "Future": 0.16, "Wasteland": 0.27, "Ancient": 0.28}
BRUSH_L = {"Primal": 0.16, "Agrarian": 0.2, "Mercantile": 0.24, "Industrial": 0.14, "Steampunk": 0.14, "Future": 0.15, "Wasteland": 0.16, "Ancient": 0.17}
STAFF_L = {"Primal": 1.55, "Agrarian": 1.4, "Mercantile": 0.88, "Industrial": 0.82, "Steampunk": 0.95, "Future": 1.3, "Wasteland": 1.4, "Ancient": 1.45}
FLUTE_L = {"Primal": 0.2, "Agrarian": 0.45, "Mercantile": 0.6, "Industrial": 0.62, "Steampunk": 0.38, "Future": 0.4, "Wasteland": 0.42, "Ancient": 0.5}
HORN_L = {"Primal": 0.3, "Agrarian": 0.24, "Mercantile": 0.7, "Industrial": 0.32, "Steampunk": 0.36, "Future": 0.18, "Wasteland": 0.38, "Ancient": 0.4}

for _g in REGIONS:
    regional("FishingRod", _g)(hafted(ROD_L, 0.014, _rod_haft, _rod_head, _rod_joint, _rod_butt))
    regional("Spindle", _g)(hafted(SPINDLE_L, 0.006, _sp_haft, _sp_head, _sp_joint, _sp_butt))
    regional("Brush", _g)(hafted(BRUSH_L, 0.0055, _br_haft, _br_head, _br_joint, lambda p, L, r: r_butt(p, r * 0.7)))
    regional("WalkingStaff", _g)(hafted(STAFF_L, 0.017, _st_haft, _st_head, lambda p, L, r: _bind(p, r * 1.1, L * 0.62, 0.05), _rod_butt))
    regional("Flute", _g)(hafted(FLUTE_L, 0.011, _fl_haft, _fl_head, _fl_joint, _fl_butt))
    regional("Horn", _g)(hafted(HORN_L, 0.012, _hn_haft, _hn_head, _hn_joint, _hn_butt))
