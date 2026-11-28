"""Four-planet forms of the 3C shells (cosmos_chimera everyday-objects.md#四星球形體, Q-A38 batch 3, 3C).

Terminal, Camera, AudioPlayer, Calculator, Navigator, Spyglass, Radio and Display for Ocean, Gale, Radiant and
Metropolis in all 8 eras. Slots and frames are forms_device.py's (shell / panel / controls / core / attachment;
everything stands on z = 0 facing -Y; Terminal, Radio and Display are floor-standing scene pieces, the rest are
palm-sized carried kits that stand on their own base; the spyglass stands on its objective end, eyepiece up).
Glow follows the 3C rule: only Steampunk, Future, Wasteland and Ancient draw glow, other eras show glass or paint.

Each region keeps one housing and swaps the mechanism by tier (form-era rule: the mechanism reads as its era):
hand-made eras count, look and sound by hand; machine eras by gears, valves and lenses; high-tech eras by slates,
orbs and light. Housings: Ocean teak and bamboo under a horned saddle top, lashed; Gale gourd-round bodies with
zigzag bands and beam-end pegs; Radiant turned brass with onion domes and lotus petals; Metropolis by era (iron and
glass, art-deco setbacks, brass and gears, finned shells, scrap).
Hand-made centrepieces: Ocean sempoa abacus, stick chart, bamboo slit drum, wayang screen; Gale mancala counting
board, talking drum, painted hide screen; Radiant bead abacus, astrolabe, temple bell frame, kavad shrine box.
"""
import math

from mathutils import Matrix

from forms_device import blk, crt, knob, legs, slats, wires
from forms_region_pilot import HAND, MACHINE, dome, era_mark, gear, horn, lash, pegs, petals, steps, zig
from forms_tools import rod
from kit_forms import F, J, regional
from kit_lib import M, REGIONS

T = Matrix.Translation


def tier(e):
    return "hand" if e in HAND else "machine" if e in MACHINE else "high"


def pick(p, hand, machine="body", high="body"):
    return {"hand": hand, "machine": machine, "high": high}[tier(p.era)]


def lamp(p, alt="glass"):
    """3C glow rule: glow only in Steampunk, Future, Wasteland and Ancient."""
    return "glow" if p.era in ("Steampunk", "Future", "Wasteland", "Ancient") else alt


def housing(p, w, d, h, z=0.0):
    """The region's device housing standing on z: Ocean box with a horned saddle top, Gale rounded gourd body,
    Radiant turned brass drum with a dome, Metropolis box by era. Returns the top z."""
    g, e = p.region, p.era
    if g == "Ocean":
        blk(p, 0, 0, z, w, d, h, mat="body")
        roof = [(-w * 0.55, 0), (-w * 0.6, h * 0.12), (0, h * 0.3), (w * 0.6, h * 0.12), (w * 0.55, 0)]
        p.plate(roof, d * 1.05, T((0, 0, z + h)), mat="fit" if tier(e) != "hand" else "teak", bevel=0)
        return z + h + h * 0.3
    if g == "Gale":
        p.ball(1.0, M(loc=(0, 0, z + h * 0.5), scale=(w * 0.55, d * 0.6, h * 0.55)), mat="body", segs=(10, 6))
        return z + h
    if g == "Radiant":
        r = min(w, d) * 0.55
        p.lathe([(r * 0.8, z), (r, z + h * 0.1), (r, z + h * 0.85), (r * 0.9, z + h)], M(scale=(w / (2 * r), 1, 1)), mat="body", segs=10)
        dome(p, r * 0.6, z + h, M(scale=(w / (2 * r), 1, 1)), mat="fit", segs=8)
        return z + h + r * 0.7
    if e == "Industrial":
        blk(p, 0, 0, z, w, d, h * 0.85, mat="body")
        steps(p, w * 0.9, d * 0.9, z + h * 0.85, 2, h * 0.075, mat="fit", shrink=0.8)
    else:
        blk(p, 0, 0, z, w, d, h, mat="body", bevel=0.3 if tier(e) == "high" else None)
    return z + h


def badge(p, x, y, z, s):
    """The region's emblem on a -Y face."""
    g = p.region
    if g == "Ocean":
        lash(p, s * 0.5, 0, s * 0.4, M(loc=(x, y, z), rot=(90, 0, 0)), segs=6)
    elif g == "Gale":
        for i in range(4):
            p.box((s * 0.25, 0.003, s * 0.25), M(loc=(x + (i - 1.5) * s * 0.25, y, z), rot=(0, 30 if i % 2 else -30, 0)), mat=("accent", "fit")[i % 2], bevel=0)
    elif g == "Radiant":
        petals(p, s * 0.35, 0, 5, s * 0.2, M(loc=(x, y, z), rot=(90, 0, 0)), mat="accent", tilt=0)
    else:
        if p.era in ("Industrial", "Future"):
            steps(p, s, 0.004, z - s * 0.3, 3, s * 0.2, M(loc=(x, y, 0)), mat="fit", shrink=0.7)
        else:
            p.cyl(s * 0.35, s * 0.35, 0.004, M(loc=(x, y, z), rot=(90, 0, 0)), mat="fit", segs=8, bevel=0)


def mark(p, r, z, m=None):
    if p.era in ("Industrial", "Steampunk", "Wasteland", "Ancient") or (p.era == "Future" and p.region != "Metropolis"):
        era_mark(p, r, z, m)


def beads(p, W, H, z0, rows, n, mat, frame_mat):
    """Abacus: frame, rods and beads standing in the XZ plane."""
    p.box((W, 0.02, 0.02), T((0, 0, z0)), mat=frame_mat, bevel=0)
    p.box((W, 0.02, 0.02), T((0, 0, z0 + H)), mat=frame_mat, bevel=0)
    for s in (-1, 1):
        p.box((0.02, 0.025, H), T((s * W / 2, 0, z0 + H / 2)), mat=frame_mat, bevel=0)
    for i in range(rows):
        x = -W * 0.4 + W * 0.8 * i / max(1, rows - 1)
        p.cyl(0.0025, 0.0025, H, T((x, 0, z0)), mat="metal", segs=3, bevel=0)
        for k in range(n):
            p.ball(0.011, M(loc=(x, 0, z0 + 0.03 + k * 0.022 + (0.02 if k >= n - 1 else 0)), scale=(1, 1, 0.7)), mat=mat, segs=(4, 3))


# ================================================================ Terminal (scene)


def terminal(p, slot):
    e, g = p.era, p.region
    W, D, H = F(p, 0.85, 0.08), F(p, 0.5, 0.08), F(p, {"hand": 0.38, "machine": 0.75, "high": 0.9}[tier(e)], 0.06)
    if slot == "shell":  # table or cabinet
        if g == "Ocean":
            blk(p, 0, 0, H - 0.05, W, D, 0.05, mat="body")
            legs(p, W * 0.42, D * 0.4, 0, H - 0.05, 0.025, mat="body")
            for s in (-1, 1):
                horn(p, s * W * 0.5, 0, H - 0.02, 0.08, s, mat="accent")
        elif g == "Gale":  # carved stool-table on a central post
            p.cyl(W * 0.45, W * 0.45, 0.05, T((0, 0, H - 0.05)), mat="body", segs=10)
            p.cyl(0.08, 0.12, H - 0.05, mat="body", segs=8)
            pegs(p, 0.1, H * 0.4, 4, 0.08, mat="fit")
        elif g == "Radiant":  # low slanted desk on a cushion
            p.box((W * 1.1, D * 1.1, 0.08), T((0, 0, 0.04)), mat="cloth", bevel=0.4)
            p.box((W * 0.7, D * 0.6, 0.04), tilted(p, W, D, H) @ T((0, 0, 0)), mat="body", bevel=0)
            blk(p, 0, 0, 0.08, W * 0.65, D * 0.5, H - 0.1, mat="body")
        else:
            if tier(e) == "machine":
                blk(p, 0, D * 0.1, 0, W, D * 0.8, H, mat="body")
            elif tier(e) == "high":
                p.lathe([(0.25, 0), (0.12, 0.1), (0.08, H - 0.05), (0.15, H)], mat="body", segs=10)
            else:
                blk(p, 0, 0, H - 0.04, W, D, 0.04, mat="body")
                legs(p, W * 0.43, D * 0.42, 0, H - 0.04, 0.02, mat="body")
    elif slot == "panel":
        if tier(e) == "hand":
            if g == "Gale":  # mancala counting board
                blk(p, 0, 0, H, W * 0.7, D * 0.35, 0.04, mat="wood")
                for row in (-1, 1):
                    for i in range(6):
                        p.cyl(0.03, 0.022, 0.005, T((-W * 0.3 + i * W * 0.12, row * D * 0.08, H + 0.036)), mat="wood_dark", segs=6, bevel=0)
            elif g == "Metropolis":
                blk(p, 0, 0, H, W * 0.6, 0.03, 0.006, mat="fit")  # slide rule
                blk(p, -W * 0.2, D * 0.1, H, W * 0.3, D * 0.4, 0.03, mat="bone")
            else:  # abacus standing on the table
                beads(p, W * 0.55, 0.18, H + (0.0 if g == "Ocean" else 0.02), 9, 4, "accent" if g == "Ocean" else "fit", pick(p, "teak" if g == "Ocean" else "wood_dark"))
        elif tier(e) == "machine":
            c = crt(p, 0, D * 0.15, H, W * 0.5, D * 0.45, 0.35, mat="body")
            p.screen(W * 0.32, 0.22, T((c[0], c[1] - 0.003, c[2])))
        else:
            p.box((W * 0.7, 0.01, 0.4), M(loc=(0, 0, H + 0.35), rot=(-12, 0, 0)), mat="glass", bevel=0)
            p.box((W * 0.6, 0.004, 0.3), M(loc=(0, -0.008, H + 0.35), rot=(-12, 0, 0)), mat=lamp(p), bevel=0)
    elif slot == "controls":
        if tier(e) == "hand":
            for i in range(4):
                p.ball(0.015, M(loc=(W * 0.3 + i * 0.03, -D * 0.3, H + 0.01), scale=(1, 1, 0.6)), mat="stone" if g != "Radiant" else "fit", segs=(5, 3))
        else:
            p.box((W * 0.5, D * 0.25, 0.03), M(loc=(0, -D * 0.25, H + 0.015), rot=(8, 0, 0)), mat="fit", bevel=0)
            for i in range(5):
                p.box((W * 0.07, D * 0.06, 0.008), T((-W * 0.2 + i * W * 0.1, -D * 0.25, H + 0.032)), mat="bone", bevel=0)
    elif slot == "core":
        if tier(e) == "hand":
            blk(p, W * 0.32, D * 0.2, H, W * 0.18, D * 0.25, 0.04, mat="bone")  # ledger
        elif tier(e) == "machine":
            for i in range(2):
                p.cyl(0.07, 0.07, 0.03, M(loc=(-W * 0.38 + i * 0.16, D * 0.3, H + 0.2), rot=(90, 0, 0)), mat="metal", segs=10, bevel=0)
            p.cyl(0.02, 0.02, 0.006, M(loc=(W * 0.3, -D * 0.05, H + 0.12), rot=(90, 0, 0)), mat=lamp(p, "paint"), segs=6, bevel=0)
        else:
            p.ball(0.04, T((0, 0, H + 0.62)), mat=lamp(p), segs=(6, 4))
    else:  # region crown over the station
        if g == "Ocean":
            for s in (-1, 1):
                p.cyl(0.02, 0.02, 1.0, T((s * W * 0.48, D * 0.45, 0)), mat=pick(p, "bamboo", "metal", "fit"), segs=5)
            p.plate([(-W * 0.6, 0), (-W * 0.65, 0.06), (0, 0.2), (W * 0.65, 0.06), (W * 0.6, 0)], 0.3, T((0, D * 0.35, 1.0)), mat=pick(p, "rattan", "fit"), bevel=0)
        elif g == "Gale":
            zig(p, W * 0.46, H - 0.03, 0.05, 12)
        elif g == "Radiant":
            dome(p, 0.12, H + (0.25 if tier(e) == "hand" else 0.4), T((W * 0.35, D * 0.2, 0)), mat="fit", segs=8)
        else:
            if e == "Industrial":
                steps(p, W * 0.6, D * 0.5, H + 0.35, 2, 0.04, T((0, D * 0.15, 0)), mat="fit", shrink=0.8)
            else:  # ink stand or stylus dock
                blk(p, -W * 0.35, D * 0.3, H if tier(e) != "high" else H - 0.02, 0.08, 0.05, 0.03, mat="fit")
                p.cyl(0.004, 0.003, 0.12, M(loc=(-W * 0.35, D * 0.3, H + 0.03), rot=(15, 0, 0)), mat="metal", segs=4, bevel=0)
        mark(p, 0.06, H * 0.5, M(loc=(W * 0.3, -D * 0.4, 0)))


def tilted(p, w, d, h):
    return M(loc=(0, 0, h), rot=(math.degrees(math.atan2(d * 0.25, d)), 0, 0))


# ================================================================ Camera (carried)


def camera(p, slot):
    e = p.era
    w, d, h = F(p, 0.15, 0.08), F(p, 0.12, 0.08), F(p, 0.12, 0.08)
    if tier(e) == "high" and p.region != "Radiant":
        h = h * 0.8
    if slot == "shell":
        housing(p, w, d, h)
    elif slot == "panel":  # the eye
        if tier(e) == "hand":  # pinhole plate with a slide shutter
            p.box((w * 0.5, 0.008, h * 0.5), T((0, -d * 0.52, h * 0.5)), mat="wood_dark", bevel=0)
            knob(p, 0, -d * 0.53, h * 0.5, 0.006, 0.004, mat="rubber", segs=6)
        elif tier(e) == "machine":
            for i, r in enumerate((0.035, 0.03, 0.025)):
                p.cyl(r, r, 0.015, M(loc=(0, -d / 2 - i * 0.015, h * 0.5), rot=(90, 0, 0)), mat="metal", segs=10, bevel=0)
            knob(p, 0, -d / 2 - 0.045, h * 0.5, 0.022, 0.004, mat="glass")
        else:
            p.ball(0.03, M(loc=(0, -d / 2, h * 0.5), scale=(1, 0.6, 1)), mat="glass", segs=(8, 5))
            p.ring(0.031, 0.003, M(loc=(0, -d / 2 - 0.005, h * 0.5), rot=(90, 0, 0)), mat=lamp(p), segs=10)
    elif slot == "controls":
        for i in range(2 if tier(e) != "high" else 3):
            p.cyl(0.008, 0.008, 0.012, T((w * 0.3 - i * 0.025, 0, h)), mat="metal" if tier(e) != "hand" else "wood", segs=6, bevel=0)
    elif slot == "core":  # viewfinder
        if tier(e) == "hand":
            p.box((w * 0.6, 0.03, h * 0.4), T((0, d / 2 + 0.015, h * 0.6)), mat="cloth", bevel=0)
        else:
            p.box((w * 0.35, d * 0.3, 0.02), T((-w * 0.2, 0, h + 0.012)), mat="metal" if tier(e) == "machine" else "fit", bevel=0)
            p.box((w * 0.25, 0.004, 0.012), T((-w * 0.2, -d * 0.15 - 0.002, h + 0.012)), mat=lamp(p), bevel=0)
    else:
        badge(p, w * 0.3, -d / 2 - 0.004, h * 0.25, 0.03)
        p.tube([(-w / 2, 0, h * 0.8), (-w * 0.7, 0, h * 1.2), (w * 0.7, 0, h * 1.2), (w / 2, 0, h * 0.8)], 0.004, mat="grip", segs=4)


# ================================================================ AudioPlayer (carried)


def audio_player(p, slot):
    e, g = p.era, p.region
    w, d, h = F(p, 0.2, 0.08), F(p, 0.13, 0.08), F(p, 0.1, 0.08)
    if slot == "shell":
        if g == "Ocean" and tier(e) == "hand":  # bamboo slit resonator on two feet
            p.cyl(h * 0.5, h * 0.5, w, M(loc=(-w / 2, 0, h * 0.55), rot=(0, 90, 0)), mat="bamboo", segs=8, bevel=0)
            for s in (-1, 1):
                p.box((0.02, d * 0.6, h * 0.1), T((s * w * 0.35, 0, h * 0.05)), mat="teak", bevel=0)
        else:
            housing(p, w, d, h)
    elif slot == "panel":  # where the sound comes out
        if tier(e) == "hand":
            if g == "Ocean":
                p.box((w * 0.7, 0.01, 0.012), T((0, -h * 0.48, h * 0.55)), mat="wood_dark", bevel=0)
            else:
                knob(p, 0, -d / 2 - 0.002, h * 0.5, h * 0.3, 0.004, mat="hide" if g == "Gale" else "cloth")
        elif tier(e) == "machine":  # horn
            p.lathe([(0.01, 0), (0.015, 0.06), (0.06, 0.14)], M(loc=(w * 0.2, 0, h + 0.02), rot=(-60, 0, 0)), mat="fit", segs=8)
        else:
            slats(p, -w * 0.3, w * 0.3, -d / 2 - 0.003, h * 0.25, h * 0.75, 6, 0.006, "fit")
    elif slot == "controls":
        if tier(e) == "hand":  # crank or beater
            p.tube([(w / 2, 0, h * 0.5), (w / 2 + 0.03, 0, h * 0.5), (w / 2 + 0.03, 0, h * 0.75)], 0.004, mat="wood", segs=4)
        else:
            for x in (-w * 0.35, w * 0.35):
                knob(p, x, -d / 2 - 0.002, h * 0.3, 0.012, 0.008, mat="bone")
    elif slot == "core":
        if tier(e) == "machine":  # record platter
            p.cyl(w * 0.35, w * 0.35, 0.006, T((-w * 0.1, 0, h + 0.002)), mat="rubber", segs=10, bevel=0)
            p.cyl(0.01, 0.01, 0.008, T((-w * 0.1, 0, h + 0.008)), mat=lamp(p, "paint"), segs=6, bevel=0)
        elif tier(e) == "high":
            p.ring(min(w, d) * 0.3, 0.004, T((0, 0, h + 0.004)), mat=lamp(p), segs=6)
        else:
            p.ball(0.01, T((w * 0.3, -d * 0.2, h)), mat="accent", segs=(4, 3))
    else:
        badge(p, -w * 0.3, -d / 2 - 0.004, h * 0.6, 0.03)
        if tier(e) == "machine":
            mark(p, h * 0.3, h * 0.5, M(loc=(w * 0.3, 0, 0)))


# ================================================================ Calculator (carried, stands on its long edge)


def calculator(p, slot):
    e, g = p.era, p.region
    W, H = F(p, 0.22, 0.08), F(p, 0.13, 0.08)
    if tier(e) == "hand":
        if g == "Gale":  # counting board with pebbles in two rows of pits
            if slot == "shell":
                blk(p, 0, 0, 0, W, 0.08, 0.03, mat="body")
            elif slot == "panel":
                for row in (-1, 1):
                    for i in range(5):
                        p.cyl(0.012, 0.009, 0.004, T((-W * 0.36 + i * W * 0.18, row * 0.02, 0.028)), mat="wood_dark", segs=6, bevel=0)
            elif slot == "controls":
                for i in range(6):
                    p.ball(0.006, M(loc=(-W * 0.36 + (i % 5) * W * 0.18, (i % 2 - 0.5) * 0.04, 0.033), scale=(1, 1, 0.7)), mat="stone", segs=(4, 3))
            elif slot == "core":
                p.box((W, 0.004, 0.012), T((0, -0.042, 0.015)), mat="accent", bevel=0)
            else:
                pegs(p, W * 0.5, 0.015, 2, 0.03, mat="fit")
            return
        frame = pick(p, "teak" if g == "Ocean" else "wood_dark")
        bead = {"Ocean": "accent", "Radiant": "fit", "Metropolis": "wood"}[g]
        if slot == "shell":
            blk(p, 0, 0, 0, W, 0.04, 0.02, mat=frame)  # foot rail
        elif slot == "panel":
            beads(p, W, H, 0.02, 5, 3, bead, frame)
        elif slot == "controls":
            p.box((W, 0.022, 0.008), T((0, 0, 0.02 + H * 0.7)), mat=frame, bevel=0)  # reckoning bar
        elif slot == "core":
            if g == "Radiant":
                petals(p, 0.015, 0.02 + H, 5, 0.008, mat="accent", tilt=80)
            else:
                p.ball(0.006, T((0, -0.015, 0.02 + H * 0.85)), mat="bone", segs=(4, 3))
        else:
            if g == "Ocean":
                for s in (-1, 1):
                    horn(p, s * W / 2, 0, 0.02 + H, 0.03, s, mat="accent")
            else:
                p.cyl(0.006, 0.006, 0.004, M(loc=(0, -0.013, 0.01), rot=(90, 0, 0)), mat="fit", segs=6, bevel=0)
        return
    w, d, h = W * 0.6, W * 0.45, F(p, 0.05, 0.1) if tier(e) == "machine" else 0.02
    if slot == "shell":
        if tier(e) == "high":
            blk(p, 0, 0, 0, w, d, h, mat="body", bevel=0.4)
        else:
            housing(p, w, d, h)
    elif slot == "panel":  # readout
        z = h + (0.002 if g in ("Metropolis",) or tier(e) == "high" else h * 0.3)
        p.box((w * 0.7, d * 0.2, 0.004), T((0, d * 0.25, z)), mat=lamp(p, "glass"), bevel=0)
    elif slot == "controls":
        z = h + (0.002 if g in ("Metropolis",) or tier(e) == "high" else h * 0.3)
        for i in range(3):
            for k in range(3):
                p.box((w * 0.16, d * 0.1, 0.006), T((-w * 0.22 + i * w * 0.22, -d * 0.25 + k * d * 0.14, z)), mat="bone" if tier(e) == "machine" else "fit", bevel=0)
    elif slot == "core":
        if tier(e) == "machine":  # side crank
            p.tube([(w / 2, 0, h * 0.5), (w / 2 + 0.02, 0, h * 0.5), (w / 2 + 0.02, -0.02, h * 0.9)], 0.003, mat="metal", segs=4)
        else:
            p.cyl(0.004, 0.003, d * 0.8, M(loc=(w / 2 + 0.006, -d * 0.4, h * 0.5), rot=(-90, 0, 0)), mat="fit", segs=4, bevel=0)
    else:
        badge(p, -w * 0.3, -d / 2 - 0.003, h * 0.5, min(0.025, h))


# ================================================================ Navigator (carried)


def navigator(p, slot):
    e, g = p.era, p.region
    R = F(p, 0.08, 0.08)
    if tier(e) == "hand" and g == "Ocean":  # small stick chart with shell markers
        if slot == "shell":
            for s in (-1, 1):
                p.cyl(0.003, 0.003, R * 3, M(loc=(-R * 1.5, s * R * 0.9, 0.004), rot=(0, 90, 0)), mat="bamboo", segs=4, bevel=0)
                p.cyl(0.003, 0.003, R * 2, M(loc=(s * R * 1.4, -R, 0.004), rot=(-90, 0, 0)), mat="bamboo", segs=4, bevel=0)
        elif slot == "panel":
            for k in range(3):
                p.tube([(-R * 1.4, (k - 1) * R * 0.6, 0.007), (0, (k - 1) * R * 0.6 + J(p, 0.02, 0.5), 0.007), (R * 1.4, (k - 1) * R * 0.6, 0.007)], 0.002, mat="bamboo", segs=3)
        elif slot == "controls":
            for i in range(4):
                p.ball(0.008, M(loc=(p.rng.uniform(-R, R), p.rng.uniform(-R * 0.7, R * 0.7), 0.009), scale=(1.3, 1, 0.5)), mat="bone", segs=(5, 3))
        elif slot == "core":
            for sx in (-1, 1):
                for sy in (-1, 1):
                    p.ball(0.005, T((sx * R * 1.4, sy * R * 0.9, 0.005)), mat="grip", segs=(4, 3))
        else:
            horn(p, -R * 1.5, R * 0.9, 0.004, 0.03, -1, mat="accent")
        return
    h = R * 0.35
    if slot == "shell":  # dish or case
        if g == "Gale":  # carved stone star-compass disc on three pegs
            p.cyl(R, R * 0.95, h, T((0, 0, 0.02)), mat=pick(p, "stone", "body"), segs=10, bevel=0)
            for i in range(3):
                a = i * math.tau / 3
                p.cyl(0.006, 0.006, 0.02, T((math.cos(a) * R * 0.7, math.sin(a) * R * 0.7, 0)), mat="fit", segs=4, bevel=0)
        elif g == "Radiant":  # astrolabe mater with a raised limb and throne
            p.cyl(R, R, 0.01, M(loc=(0, 0, R + 0.01), rot=(90, 0, 0)), mat=pick(p, "brass", "body"), segs=12, bevel=0)
            p.ring(R, 0.006, M(loc=(0, 0, R + 0.01), rot=(90, 0, 0)), mat="fit", segs=12)
            p.box((0.05, 0.02, 0.02), T((0, 0, 0.01)), mat="fit", bevel=0)
        else:
            p.cyl(R, R * 0.95, h, mat=pick(p, "teak" if g == "Ocean" else "wood_dark", "body"), segs=12, bevel=0)
    elif slot == "panel":  # dial face
        if g == "Radiant":
            p.cyl(R * 0.8, R * 0.8, 0.003, M(loc=(0, -0.007, R + 0.01), rot=(90, 0, 0)), mat="accent", segs=12, bevel=0)
        else:
            z = h + (0.02 if g == "Gale" else 0)
            p.cyl(R * 0.85, R * 0.85, 0.003, T((0, 0, z)), mat="glass" if tier(e) != "hand" else "bone", segs=12, bevel=0)
            for i in range(4):
                a = i * math.pi / 2
                p.box((0.004, R * 0.18, 0.003), M(loc=(math.cos(a) * R * 0.7, math.sin(a) * R * 0.7, z + 0.002), rot=(0, 0, math.degrees(a) + 90)), mat="accent", bevel=0)
    elif slot == "controls":  # needle, rete or pointer
        if g == "Radiant":
            p.box((R * 1.7, 0.004, 0.008), M(loc=(0, -0.012, R + 0.01), rot=(0, J(p, 30, 0.8), 0)), mat="fit", bevel=0)
        else:
            z = h + (0.02 if g == "Gale" else 0) + 0.004
            p.box((R * 1.4, 0.006, 0.004), M(loc=(0, 0, z), rot=(0, 0, J(p, 30, 0.8))), mat=lamp(p, "paint"), bevel=0)
    elif slot == "core":
        if tier(e) == "high":
            p.ball(0.012, T((0, 0, h + R * 0.6)), mat=lamp(p), segs=(5, 3))
        elif tier(e) == "machine":
            p.cyl(R * 0.88, R * 0.86, 0.006, T((0, 0, h + 0.004)), mat="metal", segs=12, bevel=0)
        else:
            p.ball(0.008, T((0, 0, h + (0.02 if g == "Gale" else 0) + 0.006)) if g != "Radiant" else T((0, -0.015, R + 0.01)), mat="fit", segs=(4, 3))
    else:
        if g == "Radiant":
            petals(p, 0.015, R * 2 + 0.01, 5, 0.008, mat="accent", tilt=40)
        elif g == "Gale":
            zig(p, R * 0.97, 0.02 + h * 0.5, h * 0.6, 8)
        elif g == "Ocean":
            for s in (-1, 1):
                horn(p, s * R, 0, h, 0.025, s, mat="accent")
        else:
            p.ring(0.012, 0.003, M(loc=(R + 0.012, 0, h * 0.5), rot=(90, 0, 0)), mat="metal", segs=6)


# ================================================================ Spyglass (carried, stands on its objective)


def spyglass(p, slot):
    e, g = p.era, p.region
    L, r = F(p, 0.24, 0.08), F(p, 0.022, 0.08)
    if slot == "shell":
        if g == "Ocean":
            p.cyl(r, r * 0.9, L * 0.65, mat=pick(p, "bamboo", "body"), segs=8, bevel=0)
        elif g == "Gale":
            p.cyl(r * 1.05, r * 0.95, L * 0.65, mat=pick(p, "leather", "body"), segs=8, bevel=0)
        elif g == "Radiant":
            p.lathe([(r * 1.1, 0), (r, L * 0.1), (r * 0.95, L * 0.6), (r, L * 0.65)], mat=pick(p, "brass", "fit", "body"), segs=8)
        else:
            if e == "Industrial":
                steps(p, r * 2.2, r * 2.2, 0, 3, L * 0.2, mat="body", shrink=0.9)
            else:
                p.cyl(r, r * 0.92, L * 0.65, mat=pick(p, "leather" if e != "Primal" else "bone", "body"), segs=8, bevel=0.3 if tier(e) == "high" else 0)
    elif slot == "panel":  # draw tubes
        for i in range(2 if tier(e) != "hand" else 1):
            p.cyl(r * (0.85 - i * 0.12), r * (0.85 - i * 0.12), L * 0.2, T((0, 0, L * (0.65 + i * 0.18))), mat=pick(p, "bamboo" if g == "Ocean" else "wood", "metal", "fit"), segs=8, bevel=0)
    elif slot == "controls":  # eyepiece
        z = L * (0.85 if tier(e) == "hand" else 1.03)
        p.cyl(r * 0.7, r * 0.75, 0.015, T((0, 0, z)), mat="grip" if tier(e) != "high" else "rubber", segs=8, bevel=0)
    elif slot == "core":  # objective lens at the foot
        p.cyl(r * 0.95, r * 0.95, 0.003, T((0, 0, -0.001)), mat=lamp(p), segs=8, bevel=0)
        if tier(e) == "machine":
            if e == "Steampunk":
                gear(p, r * 0.6, M(loc=(r * 1.1, 0, L * 0.5), rot=(0, 90, 0)), mat="brass")
            else:
                p.ring(r * 1.05, 0.004, T((0, 0, L * 0.5)), mat="metal", segs=8)
    else:
        if g == "Ocean":
            lash(p, r, L * 0.3, 0.03, segs=6)
        elif g == "Gale":
            zig(p, r * 1.05, L * 0.35, 0.03, 6)
        elif g == "Radiant":
            petals(p, r * 1.05, L * 0.6, 4, 0.008, mat="accent", tilt=80)
        else:
            p.ring(r * 1.05, 0.003, T((0, 0, L * 0.4)), mat="fit", segs=8)
        mark(p, r, L * 0.15)


# ================================================================ Radio (scene)


def radio(p, slot):
    e, g = p.era, p.region
    H = F(p, {"hand": 1.5, "machine": 1.0, "high": 1.8}[tier(e)], 0.06)
    W = F(p, 0.6, 0.08)
    if tier(e) == "hand":
        if slot == "shell":  # frame or post
            if g == "Metropolis":  # speaking-tube post
                p.lathe([(0.15, 0), (0.08, 0.1), (0.05, H * 0.7), (0.07, H * 0.72)], mat="wood_dark", segs=8)
            else:
                for s in (-1, 1):
                    p.cyl(0.04, 0.035, H, T((s * W / 2, 0, 0)), mat=pick(p, "bamboo" if g == "Ocean" else "wood"), segs=6)
                p.box((W + 0.1, 0.06, 0.06), T((0, 0, H)), mat=pick(p, "teak" if g == "Ocean" else "wood_dark"), bevel=0)
        elif slot == "panel":  # the sounding thing
            if g == "Ocean":  # big bamboo slit drum
                p.cyl(0.1, 0.1, H * 0.55, T((0, 0, H * 0.3)), mat="bamboo", segs=8, bevel=0)
                p.box((0.04, 0.03, H * 0.35), T((0, -0.095, H * 0.55)), mat="wood_dark", bevel=0)
            elif g == "Gale":  # talking drum hung from the bar
                p.lathe([(0.1, 0), (0.06, 0.15), (0.06, 0.25), (0.1, 0.4)], M(loc=(0, 0, H * 0.45)), mat="wood", segs=8)
                for z in (H * 0.45, H * 0.45 + 0.4):
                    p.cyl(0.1, 0.1, 0.005, T((0, 0, z)), mat="hide", segs=8, bevel=0)
            elif g == "Radiant":  # temple bell
                p.lathe([(0.15, H * 0.55), (0.14, H * 0.6), (0.1, H * 0.72), (0.08, H * 0.8), (0.04, H * 0.84)], mat="brass", segs=10)
            else:
                p.lathe([(0.01, H * 0.72), (0.03, H * 0.8), (0.1, H * 0.88)], M(loc=(0, -0.05, 0)), mat="brass", segs=8)
        elif slot == "controls":  # beater, rope or plug
            if g == "Radiant":
                p.tube([(0, 0, H * 0.84), (0, 0, H)], 0.006, mat="rope", segs=3)
                p.tube([(0.05, -0.05, H * 0.58), (0.05, -0.05, H * 0.3)], 0.006, mat="rope", segs=3)
            else:
                p.tube([(W * 0.3, -0.15, 0.4), (W * 0.2, -0.15, 0.75)], 0.01, mat="wood", segs=4)
                p.ball(0.025, T((W * 0.2, -0.15, 0.77)), mat="hide" if g != "Metropolis" else "brass", segs=(5, 3))
        elif slot == "core":
            if g in ("Ocean", "Gale"):
                p.tube([(0, 0, H), (0, 0, H * 0.85 if g == "Ocean" else H * 0.45 + 0.4)], 0.005, mat="rope", segs=3)
            else:
                p.box((0.2, 0.2, 0.05), T((0, 0, 0.025)), mat="stone", bevel=0)
        else:
            if g == "Ocean":
                for s in (-1, 1):
                    horn(p, s * (W / 2 + 0.05), 0, H + 0.03, 0.1, s, mat="accent")
            elif g == "Gale":
                pegs(p, 0.04, H * 0.6, 4, 0.08, T((-W / 2, 0, 0)), mat="body")
                p.cyl(0.08, 0.0, 0.15, T((0, 0, H + 0.03)), mat="accent", segs=6, bevel=0)
            elif g == "Radiant":
                dome(p, 0.12, H + 0.03, mat="fit", segs=8)
            else:
                p.box((0.08, 0.006, 0.05), T((0, -0.06, H * 0.5)), mat="brass", bevel=0)
        return
    if slot == "shell":
        if tier(e) == "high":
            p.cyl(0.12, 0.09, H, mat="body", segs=8, bevel=0)
        else:
            housing(p, W, W * 0.5, H * 0.55, z=H * 0.4)
            legs(p, W * 0.4, W * 0.18, 0, H * 0.4, 0.02, mat="body")
    elif slot == "panel":
        if tier(e) == "high":
            for k in (0.3, 0.55, 0.8):
                p.ring(0.115, 0.01, T((0, 0, H * k)), mat=lamp(p), segs=10)
        else:
            p.box((W * 0.6, 0.01, H * 0.25), T((0, -W * 0.26, H * 0.7)), mat="cloth", bevel=0)
            slats(p, -W * 0.28, W * 0.28, -W * 0.27, H * 0.58, H * 0.82, 6, 0.008, "fit")
    elif slot == "controls":
        if tier(e) == "high":
            p.box((0.08, 0.01, 0.15), T((0, -0.11, H * 0.45)), mat="fit", bevel=0)
        else:
            for x in (-W * 0.25, W * 0.25):
                knob(p, x, -W * 0.26, H * 0.48, 0.025, 0.015, mat="bone")
            p.cyl(0.04, 0.04, 0.006, M(loc=(0, -W * 0.27, H * 0.48), rot=(90, 0, 0)), mat=lamp(p, "paint"), segs=8, bevel=0)
    elif slot == "core":  # aerial
        top = H if tier(e) == "high" else H * 0.95
        rod(p, (W * 0.3 if tier(e) != "high" else 0, 0, top), (W * 0.35 if tier(e) != "high" else 0, 0, top + J(p, 0.5, 0.2)), 0.005, 0.003, mat="metal", segs=4)
    else:
        if tier(e) == "high":
            crown_top = H
            if g == "Ocean":
                for s in (-1, 1):
                    horn(p, s * 0.1, 0, crown_top, 0.08, s, mat="accent")
            elif g == "Gale":
                pegs(p, 0.1, H * 0.2, 4, 0.1, mat="fit")
            elif g == "Radiant":
                petals(p, 0.12, 0.0, 6, 0.05, mat="accent", tilt=60)
            else:
                for i in range(4):
                    a = i * math.pi / 2
                    p.box((0.12, 0.01, 0.25), M(loc=(math.cos(a) * 0.12, math.sin(a) * 0.12, 0.125), rot=(0, 0, math.degrees(a))), mat="fit", bevel=0)
        else:
            badge(p, W * 0.3, -W * 0.26, H * 0.88, 0.05)
            if e == "Wasteland":
                wires(p, [(-W * 0.4, 0, H * 0.9), (-W * 0.6, -0.1, H * 0.5), (-W * 0.5, -0.15, 0.02)])


# ================================================================ Display (scene)


def display(p, slot):
    e, g = p.era, p.region
    W, H = F(p, 1.1, 0.08), F(p, 1.4, 0.06)
    if tier(e) == "hand":
        if g == "Radiant":  # kavad: a painted shrine box with folding doors
            w, d, h = 0.5, 0.3, 0.7
            if slot == "shell":
                blk(p, 0, 0, 0, 0.8, 0.5, 0.45, mat="wood_dark")  # stand
                blk(p, 0, 0, 0.45, w, d, h, mat="body")
            elif slot == "panel":
                p.box((w * 0.8, 0.005, h * 0.8), T((0, -d / 2 - 0.003, 0.45 + h * 0.5)), mat="paint", bevel=0)
            elif slot == "controls":  # open doors
                for s in (-1, 1):
                    p.box((w * 0.5, 0.015, h * 0.9), M(loc=(s * (w / 2 + w * 0.2), -d / 2 - w * 0.17, 0.45 + h * 0.5), rot=(0, 0, s * 40)), mat="paint", bevel=0)
            elif slot == "core":
                petals(p, 0.08, 0, 6, 0.03, M(loc=(0, -d / 2 - 0.008, 0.45 + h * 0.5), rot=(90, 0, 0)), mat="accent", tilt=0)
            else:
                dome(p, 0.2, 0.45 + h, mat="fit", segs=8)
            return
        if slot == "shell":  # two poles and crossbars
            for s in (-1, 1):
                p.cyl(0.03, 0.03, H, T((s * W / 2, 0, 0)), mat=pick(p, "bamboo" if g == "Ocean" else "wood"), segs=6)
            for z in (H * 0.3, H):
                p.cyl(0.02, 0.02, W, M(loc=(-W / 2, 0, z), rot=(0, 90, 0)), mat=pick(p, "bamboo" if g == "Ocean" else "wood"), segs=5, bevel=0)
        elif slot == "panel":  # screen
            p.box((W * 0.95, 0.006, H * 0.68), T((0, 0, H * 0.65)), mat="cloth" if g != "Gale" else "hide", bevel=0)
            if g == "Gale":
                for i in range(8):
                    p.box((W * 0.1, 0.008, 0.05), M(loc=(-W * 0.42 + i * W * 0.12, -0.003, H * 0.38), rot=(0, 30 if i % 2 else -30, 0)), mat=("accent", "fit")[i % 2], bevel=0)
        elif slot == "controls":  # puppets on sticks or painted figures
            for i in range(2):
                x = (i - 0.5) * W * 0.4
                if g == "Ocean":
                    p.plate([(-0.08, 0), (0.08, 0), (0.05, 0.3), (0, 0.38), (-0.05, 0.3)], 0.006, T((x, -0.01, H * 0.5)), mat="hide", bevel=0)
                    p.cyl(0.004, 0.004, H * 0.5, T((x, -0.01, 0)), mat="bamboo", segs=3, bevel=0)
                else:
                    p.plate([(-0.07, 0), (0.07, 0), (0.04, 0.25), (0, 0.32), (-0.04, 0.25)], 0.004, T((x, -0.005, H * 0.55)), mat="paint", bevel=0)
        elif slot == "core":  # the light behind the screen
            p.lathe([(0, 0), (0.12, 0.04), (0.14, 0.1)], T((0, 0.4, 0.3)), mat="clay" if g != "Metropolis" else "iron", segs=8)
            p.cyl(0.03, 0.03, 0.3, T((0, 0.4, 0)), mat="wood", segs=4, bevel=0)
        else:
            if g == "Ocean":
                for s in (-1, 1):
                    horn(p, s * W / 2, 0, H, 0.12, s, mat="accent")
            elif g == "Gale":
                for s in (-1, 1):
                    p.cyl(0.05, 0.0, 0.12, T((s * W / 2, 0, H)), mat="accent", segs=5, bevel=0)
            else:
                p.box((W * 1.1, 0.08, 0.04), T((0, 0, H + 0.02)), mat="wood_dark", bevel=0)
        return
    w, h = W * 0.6, 0.5
    z0 = 0.55
    if slot == "shell":
        if tier(e) == "high":
            p.box((w * 1.2, 0.04, h * 1.1), T((0, 0, z0 + h * 0.55)), mat="body", bevel=0.2)
            p.cyl(0.06, 0.08, z0, mat="body", segs=8, bevel=0)
        else:
            housing(p, w, w * 0.6, h, z=z0)
            legs(p, w * 0.42, w * 0.2, 0, z0, 0.02, mat="body")
    elif slot == "panel":
        if tier(e) == "high":
            p.screen(w * 1.1, h, T((0, -0.022, z0 + h * 0.55)))
        else:
            round_ = g in ("Gale", "Radiant")
            p.screen(w * (0.5 if round_ else 0.7), h * 0.6, T((0 if round_ else -w * 0.08, -w * (0.37 if round_ else 0.31), z0 + h * 0.52)))
    elif slot == "controls":
        if tier(e) == "machine":
            for z in (0.35, 0.6):
                knob(p, w * 0.38, -w * 0.3, z0 + h * z, 0.025, 0.015, mat="bone")
        else:
            p.box((w * 0.3, 0.06, 0.02), T((0, -0.15, z0 - 0.05)), mat="fit", bevel=0)
    elif slot == "core":
        if tier(e) == "machine":
            for s in (-1, 1):
                rod(p, (s * 0.03, 0, z0 + h), (s * 0.2, 0.05, z0 + h + 0.3), 0.004, 0.002, mat="metal", segs=4)
        else:
            p.box((w * 1.1, 0.01, 0.01), T((0, -0.025, z0 + 0.01)), mat=lamp(p), bevel=0)
    else:
        if g == "Ocean":
            for s in (-1, 1):
                horn(p, s * w * 0.6, 0, z0 + h + 0.02, 0.08, s, mat="accent")
        elif g == "Gale":
            pegs(p, 0.06, z0 * 0.5, 4, 0.08, mat="fit")
        elif g == "Radiant":
            if tier(e) == "high":
                petals(p, w * 0.3, z0 + h * 1.1 + 0.02, 6, 0.04, mat="accent", tilt=70)
            else:
                p.box((w * 0.9, 0.006, 0.04), T((0, -w * 0.31, z0 + 0.05)), mat="accent", bevel=0)
        else:
            if e == "Industrial":
                steps(p, w, w * 0.6, 0, 2, 0.03, mat="fit", shrink=0.85)
            else:
                p.cyl(0.2, 0.22, 0.02, mat="fit", segs=10, bevel=0)
        mark(p, 0.05, z0 + h * 0.2, M(loc=(w * 0.35, -w * 0.3, 0)))


for _g in REGIONS:
    regional("Terminal", _g)(terminal)
    regional("Camera", _g)(camera)
    regional("AudioPlayer", _g)(audio_player)
    regional("Calculator", _g)(calculator)
    regional("Navigator", _g)(navigator)
    regional("Spyglass", _g)(spyglass)
    regional("Radio", _g)(radio)
    regional("Display", _g)(display)
