"""Four-planet forms of the workshop machines (cosmos_chimera everyday-objects.md#四星球形體, Q-A38 batch 3, machines).

Loom, Forge, Anvil, Millstone, Kiln, Stove and Still for Ocean, Gale, Radiant and Metropolis in all 8 eras. Slots and
footprints are forms_machine.py's (base / mechanism / drive / power / trim; floor contact at z = 0, front -Y; the
per-era W x D x H tables are reused so a regional machine takes the same spot as the shared one). Fire and coals
glow in every era, as in the shared machines.

Each region keeps one working tradition and swaps the power by tier: hand-made eras run on hands, feet and fire;
machine eras on a motor (Industrial), a boiler (Steampunk) or scrap (Wasteland); high-tech eras on a coil core
(Future) or a rune pillar (Ancient). The region's crown sits on every engine housing.
Ocean: ikat backstrap loom between horn-tipped beams, twin bamboo piston bellows, a stump-set block anvil, the long
rice-pounding trough with pestles, a kiln under a horned saddle shelter, a long clay tungku with a wok, an arak still
with a bamboo condenser through a trough.
Gale: the narrow-strip loom with its drag stone, pot bellows, a stone anvil with a hammerstone, a grinding platform
with several hollows, a peg-studded clay updraft kiln, a round clay stove with a three-legged pot, a gourd still.
Radiant: the pit loom, a hand-cranked fan blower under a dome hood, an anvil on a lotus plinth, the chakki quern with
its peg handle, a brick bhatti with a domed chimney, a U-shaped chulha with a tawa, a degh-bhapka still.
Metropolis by era (frame loom, hooded hearth, London anvil on a stand, cased stones, bottle kiln, range, alembic).
"""
import math

from mathutils import Matrix

from forms_furniture import flagstone, rock, runes
from forms_lamp import flame, lit
from forms_machine import (ANVIL, FORGE, KILN, LOOM, MILL, STILL, STOVE, _cookpot, _horned, _wok, beam, boiler, brick,
                           bucket, coilcore, fire, flue, hammer, logs, motor, sack, shell_box, threads, tongs,
                           xcyl, xwheel, ycyl)
from forms_region_pilot import HAND, MACHINE, dome, horn, lash, pegs, petals, steps, zig
from kit_forms import F, J, regional
from kit_lib import M, REGIONS

T = Matrix.Translation
TAU = math.tau


def tier(e):
    return "hand" if e in HAND else "machine" if e in MACHINE else "high"


def pick(p, hand, machine="body", high="body"):
    return {"hand": hand, "machine": machine, "high": high}[tier(p.era)]


def frame(p, table):
    _, w, d, h = table[p.era]
    return w * F(p, 1, 0.08), d * F(p, 1, 0.08), h * F(p, 1, 0.05)


def crown(p, x, y, z, r):
    """The region's crown on top of a housing."""
    g = p.region
    if g == "Ocean":
        for s in (-1, 1):
            horn(p, x + s * r, y, z, r * 0.8, s, mat="accent")
    elif g == "Gale":
        p.cyl(r * 0.9, 0.0, r * 1.2, T((x, y, z)), mat="fit", segs=6)
        pegs(p, r * 0.5, z + r * 0.2, 4, r * 0.6, T((x, y, 0)), mat="body")
    elif g == "Radiant":
        dome(p, r * 0.8, z, T((x, y, 0)), mat="fit", segs=8)
    else:
        if p.era == "Industrial":
            steps(p, r * 2, r * 2, z, 3, r * 0.2, T((x, y, 0)), mat="fit", shrink=0.7)
        else:
            p.cyl(r, r * 0.8, r * 0.25, T((x, y, z)), mat="fit", segs=8)


def engine(p, x, y, z, s):
    """Power unit of the machine and high-tech eras, crowned by the region. Returns its top z."""
    e = p.era
    if e == "Industrial":
        motor(p, x, y, z, s * 0.25, s * 0.7, mat="paint")
        top = z + s * 0.55
    elif e == "Steampunk":
        boiler(p, x, y, z, s * 0.28, s * 0.9)
        top = z + s * 1.1
    elif e == "Wasteland":
        shell_box(p, s * 0.5, s * 0.4, s * 0.35, (x, y, z), mat="rust", bevel=0)
        p.cyl(s * 0.08, s * 0.08, s * 0.2, T((x + s * 0.15, y - s * 0.1, z + s * 0.35)), mat="rubber", segs=6)
        top = z + s * 0.35
    elif e == "Future":
        coilcore(p, x, y, z, s * 0.18, s * 0.8)
        top = z + s * 0.9
    else:  # Ancient rune pillar
        p.box((s * 0.35, s * 0.35, s * 0.9), T((x, y, z + s * 0.45)), mat="stone", bevel=0.05)
        runes(p, x, y - s * 0.18, z + s * 0.1, z + s * 0.8, n=3, w=s * 0.08)
        top = z + s * 0.9
    crown(p, x, y, top, s * 0.15)
    return top


def heat(p, x, y, z, s):
    """The fire of a hearth by era: wood fire, gas ring, steam-era coals, scrap fire, glowing plate."""
    e = p.era
    if tier(e) == "hand" or e in ("Steampunk", "Wasteland"):
        fire(p, x, y, z, s, n=3 if e != "Wasteland" else 2)
    elif e == "Industrial":
        p.ring(s * 1.2, s * 0.12, T((x, y, z)), mat="metal", segs=10)
        for i in range(5):
            a = i * TAU / 5
            flame(p, x + math.cos(a) * s * 1.2, y + math.sin(a) * s * 1.2, z + s * 0.1, s * 0.25, mat=lit(p), segs=4)
    else:
        p.cyl(s * 1.4, s * 1.4, 0.01, T((x, y, z)), mat="glow", segs=10)


# ================================================================ Loom


def loom(p, slot):
    e, g = p.era, p.region
    W, D, H = frame(p, LOOM)
    yarn = pick(p, "cloth", "cloth", "glass" if e == "Future" else "cloth")
    if g == "Ocean":  # backstrap ikat loom: warp from a horned beam on posts down to the weaver's breast bar
        zb, zf = H * 0.7, 0.45
        if slot == "base":
            for s in (-1, 1):
                p.cyl(0.035, 0.03, H * 0.85, T((s * W * 0.45, D * 0.4, 0)), mat=pick(p, "bamboo", "metal", "fit"), segs=6)
            flagstone(p, W * 0.7, D * 0.4, 0.02, 0, y=-D * 0.3, mat="rattan" if tier(e) == "hand" else "fit", rough=0.05)
        elif slot == "mechanism":
            threads(p, (D * 0.4, zb), (-D * 0.15, zf), W * 0.7, W * 0.5, 12, mat="cloth")
            p.box((W * 0.5, 0.004, 0.25), M(loc=(0, -D * 0.05, zf + 0.12), rot=(-35, 0, 0)), mat=yarn, bevel=0)
            for i in range(3):  # ikat bands
                p.box((W * 0.5, 0.006, 0.02), M(loc=(0, -D * 0.06, zf + 0.04 + i * 0.07), rot=(-35, 0, 0)), mat=("accent", "fit", "accent")[i], bevel=0)
        elif slot == "drive":
            xcyl(p, 0.03, W, (0, D * 0.4, zb), mat=pick(p, "teak" if e != "Primal" else "bamboo", "metal", "fit"), segs=6)
            for s in (-1, 1):
                horn(p, s * W * 0.5, D * 0.4, zb, 0.12, s, mat="accent")
            xcyl(p, 0.02, W * 0.6, (0, -D * 0.15, zf), mat="wood_dark", segs=6)
            xcyl(p, 0.012, W * 0.55, (0, D * 0.15, zf + (zb - zf) * 0.55), mat="wood", segs=5)
        elif slot == "power":
            if tier(e) == "hand":  # the backstrap
                p.tube([(-W * 0.3, -D * 0.15, zf), (0, -D * 0.45, zf - 0.05), (W * 0.3, -D * 0.15, zf)], 0.02, mat="grip", segs=4)
            else:
                engine(p, W * 0.6, D * 0.2, 0, 0.6)
        else:
            lash(p, 0.035, H * 0.6, 0.04, T((-W * 0.45, D * 0.4, 0)), segs=6)
            sack(p, -W * 0.55, -D * 0.3, 0.1, 0.18, mat="cloth")
    elif g == "Gale":  # narrow-strip loom: tall frame with a hanging heddle pulley, long warp to a drag stone
        Hh = max(H, 1.4)
        if slot == "base":
            for x in (-0.35, 0.35):
                for y in (D * 0.3, D * 0.6):
                    beam(p, (x, y, 0), (x * 0.8, y, Hh), 0.05, mat=pick(p, "wood", "metal", "fit"))
            beam(p, (-0.38, D * 0.45, Hh), (0.38, D * 0.45, Hh), 0.05, mat=pick(p, "wood", "metal", "fit"))
        elif slot == "mechanism":  # narrow warp running far forward, finished strips rolled at the weaver
            threads(p, (D * 0.45, 0.6), (-D * 1.6, 0.05), 0.12, 0.12, 6, mat="cloth")
            p.cyl(0.07, 0.07, 0.14, T((-0.07, D * 0.6, 0.55)) @ M(rot=(0, 90, 0)), mat=yarn, segs=8)
            zig(p, 0.071, 0, 0.1, 6, T((0, D * 0.6, 0.55)) @ M(rot=(0, 90, 0)))
        elif slot == "drive":  # heddle pulley hanging from the top bar, treadles
            p.tube([(0, D * 0.45, Hh), (0, D * 0.45, Hh - 0.4)], 0.004, mat="grip", segs=3)
            p.cyl(0.04, 0.04, 0.03, T((-0.015, D * 0.45, Hh - 0.45)) @ M(rot=(0, 90, 0)), mat="wood_dark", segs=8)
            for x in (-0.06, 0.06):
                p.box((0.1, 0.01, 0.12), T((x, D * 0.45, Hh - 0.6)), mat="wood", bevel=0)
                p.box((0.04, 0.3, 0.02), T((x, D * 0.55, 0.03)), mat="wood", bevel=0)
        elif slot == "power":
            if tier(e) == "hand":  # the drag stone holding the warp end
                rock(p, 0.12, 0.1, 0.08, (0, -D * 1.6, 0.06), mat="stone")
                p.box((0.35, 0.3, 0.25), T((0, D * 0.95, 0.125)), mat="wood", bevel=0.05)  # bench
            else:
                engine(p, 0.6, D * 0.45, 0, 0.6)
        else:
            pegs(p, 0.05, Hh - 0.1, 4, 0.12, T((0.38, D * 0.45, 0)), mat="body")
            p.cyl(0.08, 0.0, 0.15, T((0, D * 0.45, Hh + 0.025)), mat="accent", segs=6)
    elif g == "Radiant":  # pit loom: weaver sits on the pit rim, overhead beater beam, lotus posts
        zw = 0.35
        if slot == "base":
            p.box((W * 0.5, 0.5, 0.06), T((0, -D * 0.2, 0.03)), mat="stone", bevel=0)  # pit rim
            p.box((W * 0.45, 0.42, 0.04), T((0, -D * 0.2, 0.065)), mat="stone_dark", bevel=0)
            for s in (-1, 1):
                p.lathe([(0.06, 0), (0.05, 0.1), (0.04, H), (0.06, H + 0.04)], T((s * W * 0.45, D * 0.1, 0)), mat=pick(p, "wood", "metal", "fit"), segs=8)
                petals(p, 0.05, 0.0, 6, 0.03, T((s * W * 0.45, D * 0.1, 0)), mat="accent", tilt=60)
        elif slot == "mechanism":
            threads(p, (D * 0.6, zw), (-D * 0.1, zw), W * 0.6, W * 0.6, 12, mat="cloth")
            p.box((W * 0.6, 0.25, 0.004), T((0, -D * 0.25, zw)), mat=yarn, bevel=0)
            p.box((W * 0.6, 0.04, 0.005), T((0, -D * 0.2, zw + 0.002)), mat="accent", bevel=0)
        elif slot == "drive":  # beater hanging from the overhead beam
            xcyl(p, 0.03, W * 0.95, (0, D * 0.1, H), mat=pick(p, "wood", "metal", "fit"), segs=6)
            for s in (-1, 1):
                p.tube([(s * W * 0.3, D * 0.1, H), (s * W * 0.3, D * 0.05, zw + 0.08)], 0.008, mat="wood", segs=4)
            xcyl(p, 0.025, W * 0.65, (0, D * 0.05, zw + 0.06), mat="wood_dark", segs=6)
            xcyl(p, 0.03, W * 0.65, (0, -D * 0.38, zw), mat="wood_dark", segs=6)
        elif slot == "power":
            if tier(e) == "hand":  # treadles down in the pit
                for x in (-0.06, 0.06):
                    p.box((0.05, 0.35, 0.02), T((x, -D * 0.1, 0.09)), mat="wood", bevel=0)
            else:
                engine(p, W * 0.6, D * 0.3, 0, 0.6)
        else:
            for s in (-1, 1):
                dome(p, 0.07, H + 0.03, T((s * W * 0.45, D * 0.1, 0)), mat="fit", segs=7)
    else:  # frame loom by era
        if slot == "base":
            for x in (-W * 0.45, W * 0.45):
                for y in (-D * 0.4, D * 0.4):
                    p.box((0.06, 0.06, H), T((x, y, H / 2)), mat=pick(p, "wood_dark" if e != "Primal" else "iron", "metal", "body"), bevel=0)
            for y in (-D * 0.4, D * 0.4):
                p.box((W * 0.95, 0.06, 0.06), T((0, y, H)), mat=pick(p, "wood_dark" if e != "Primal" else "iron", "metal", "body"), bevel=0)
        elif slot == "mechanism":
            threads(p, (D * 0.4, H * 0.6), (-D * 0.4, H * 0.55), W * 0.75, W * 0.75, 12, mat="cloth")
            p.box((W * 0.75, D * 0.3, 0.005), T((0, -D * 0.3, H * 0.55)), mat=yarn, bevel=0)
        elif slot == "drive":
            p.box((W * 0.8, 0.05, H * 0.3), T((0, 0, H * 0.75)), mat=pick(p, "wood", "metal", "fit"), bevel=0)
            for y in (-D * 0.4, D * 0.4):
                xcyl(p, 0.04, W * 0.9, (0, y, H * 0.58), mat="wood" if tier(e) == "hand" else "metal", segs=8)
        elif slot == "power":
            if tier(e) == "hand":
                for x in (-0.1, 0.1):
                    p.box((0.06, D * 0.7, 0.02), M(loc=(x, 0, 0.08), rot=(6, 0, 0)), mat="wood", bevel=0)
                p.box((W * 0.6, 0.3, 0.45), T((0, -D * 0.8, 0.225)), mat="wood_dark", bevel=0.05)
            else:
                engine(p, W * 0.65, 0, 0, 0.6)
        else:
            if e == "Industrial":
                steps(p, W * 0.5, 0.08, H, 3, 0.04, mat="fit", shrink=0.75)
            elif tier(e) == "high":
                p.box((W * 0.95, D * 0.85, 0.04), T((0, 0, H + 0.03)), mat="fit", bevel=0.3)
            else:
                for i in range(3):
                    p.cyl(0.03, 0.03, 0.1, T((-W * 0.3 + i * 0.1, D * 0.4, H + 0.03)), mat="accent", segs=6)


# ================================================================ Forge


def forge(p, slot):
    e, g = p.era, p.region
    W, D, H = frame(p, FORGE)
    Hh = max(H, 0.35)
    if g == "Ocean":  # low clay hearth and twin upright piston bellows
        if slot == "base":
            p.box((W, D * 0.7, 0.18), T((0, -D * 0.1, 0.09)), mat=pick(p, "clay", "metal", "body"), bevel=0.1)
        elif slot == "mechanism":
            p.lathe([(0, 0.15), (0.16, 0.16), (0.2, 0.2)], T((-W * 0.1, -D * 0.1, 0)), mat="stone_dark", segs=10)
            p.tube([(W * 0.05, D * 0.2, 0.12), (-W * 0.1, -D * 0.05, 0.16)], 0.025, mat="clay" if tier(e) == "hand" else "metal", segs=6)
        elif slot == "drive":
            if tier(e) == "hand":  # two bamboo cylinders with plunger rods and feather pistons
                for s in (-1, 1):
                    x = W * 0.12 + s * 0.09
                    p.cyl(0.07, 0.07, 0.75, T((x, D * 0.3, 0)), mat="bamboo", segs=8)
                    p.cyl(0.006, 0.006, 0.35, T((x, D * 0.3, 0.7 + (0.05 if s < 0 else 0.15))), mat="wood", segs=4)
                    p.cyl(0.03, 0.03, 0.02, T((x, D * 0.3, 1.05 + (0.05 if s < 0 else 0.15))), mat="wood_dark", segs=6)
                lash(p, 0.16, 0.5, 0.04, M(loc=(W * 0.12, D * 0.3, 0), scale=(1.3, 0.5, 1)), segs=6)
            else:
                ycyl(p, 0.1, 0.12, (W * 0.12, D * 0.3, 0.25), mat="metal", segs=10)
        elif slot == "power":
            heat(p, -W * 0.1, -D * 0.1, 0.2, 0.05)
            if tier(e) != "hand":
                engine(p, W * 0.4, D * 0.35, 0, 0.6)
        else:
            tongs(p, -W * 0.45, -D * 0.4, 0.18, 0.4, rot=20)
            ycyl(p, 0.05, 0.6, (W * 0.45, -D * 0.35, 0.05), mat="bamboo", segs=6)
            for s in (-1, 1):
                horn(p, s * W * 0.5, -D * 0.1, 0.18, 0.08, s, mat="accent")
    elif g == "Gale":  # ground hearth with a clay tuyere fed by two pot bellows
        if slot == "base":
            flagstone(p, W * 1.2, D * 1.1, 0.03, 0, mat="stone_dark", rough=0.2)
        elif slot == "mechanism":
            p.lathe([(0.25, 0.0), (0.24, 0.12), (0.16, 0.14), (0.0, 0.08)], T((0, -D * 0.15, 0)), mat=pick(p, "clay", "metal", "body"), segs=10)
            p.tube([(0, D * 0.15, 0.12), (0, -D * 0.05, 0.12)], 0.035, mat="clay" if tier(e) == "hand" else "metal", segs=6)
        elif slot == "drive":
            if tier(e) == "hand":  # pot bellows: clay bowls covered with hide, stick handles
                for s in (-1, 1):
                    x = s * 0.15
                    p.lathe([(0, 0), (0.12, 0.02), (0.14, 0.1), (0.13, 0.13)], T((x, D * 0.4, 0)), mat="clay", segs=8)
                    p.ball(0.13, M(loc=(x, D * 0.4, 0.13), scale=(1, 1, 0.25)), mat="hide", segs=(8, 3))
                    p.cyl(0.008, 0.008, 0.45, T((x, D * 0.4, 0.15)), mat="wood", segs=4)
                    p.tube([(x, D * 0.3, 0.06), (0, D * 0.15, 0.12)], 0.015, mat="clay", segs=4)
                zig(p, 0.14, 0.07, 0.04, 6, T((-0.15, D * 0.4, 0)))
            else:
                ycyl(p, 0.1, 0.12, (0, D * 0.4, 0.15), mat="metal", segs=10)
        elif slot == "power":
            heat(p, 0, -D * 0.15, 0.12, 0.05)
            if tier(e) != "hand":
                engine(p, W * 0.5, D * 0.3, 0, 0.6)
        else:
            rock(p, 0.07, 0.06, 0.05, (-W * 0.45, -D * 0.4, 0.05))
            pegs(p, 0.25, 0.08, 4, 0.08, T((0, -D * 0.15, 0)), mat="body")
    elif g == "Radiant":  # brick hearth, hand-cranked fan blower, domed hood
        if slot == "base":
            brick(p, W, D * 0.7, Hh * 0.75, (0, 0, 0), mat=pick(p, "clay", "metal", "body"), n=2)
        elif slot == "mechanism":
            p.lathe([(0, Hh * 0.72), (0.18, Hh * 0.73), (0.22, Hh * 0.78)], T((-W * 0.1, 0, 0)), mat="stone_dark", segs=10)
        elif slot == "drive":
            c = (W * 0.55, 0, Hh * 0.45)
            if tier(e) == "hand":
                xwheel(p, 0.25, c, rim="fit", hub="wood", spokes=6)
                p.tube([(W * 0.6, -0.2, Hh * 0.45), (W * 0.65, -0.2, Hh * 0.45)], 0.015, mat="wood", segs=4)
            else:
                ycyl(p, 0.15, 0.12, (W * 0.55, 0, Hh * 0.45), mat="metal", segs=10)
            p.tube([(W * 0.5, 0, Hh * 0.45), (W * 0.1, 0, Hh * 0.6)], 0.03, mat="metal", segs=6)
        elif slot == "power":
            heat(p, -W * 0.1, 0, Hh * 0.75, 0.05)
            if tier(e) != "hand":
                engine(p, W * 0.55, D * 0.4, 0, 0.55)
        else:  # dome hood on four posts with a lotus collar
            for sx in (-1, 1):
                for sy in (-1, 1):
                    p.cyl(0.02, 0.02, 0.55, T((-W * 0.1 + sx * 0.25, sy * 0.2, Hh * 0.75)), mat="fit", segs=4)
            dome(p, 0.32, Hh * 0.75 + 0.55, T((-W * 0.1, 0, 0)), mat="fit", segs=8)
            petals(p, 0.3, Hh * 0.75 + 0.53, 6, 0.06, T((-W * 0.1, 0, 0)), mat="accent", tilt=70)
            tongs(p, W * 0.2, -D * 0.25, Hh * 0.75, 0.4, rot=-15)
    else:  # hooded hearth on legs
        if slot == "base":
            for sx in (-1, 1):
                for sy in (-1, 1):
                    p.box((0.05, 0.05, Hh * 0.75), T((sx * W * 0.4, sy * D * 0.3, Hh * 0.375)), mat=pick(p, "iron", "metal", "body"), bevel=0)
        elif slot == "mechanism":
            p.box((W * 0.9, D * 0.7, 0.1), T((0, 0, Hh * 0.75 + 0.05)), mat=pick(p, "iron", "metal", "body"), bevel=0.05)
        elif slot == "drive":
            if tier(e) == "hand":  # great bellows
                p.lathe([(0, 0), (0.25, 0.05), (0.2, 0.5), (0.03, 0.75)], T((W * 0.45, 0, Hh * 0.8)) @ M(rot=(0, 90, 0), scale=(1, 0.4, 1)), mat="leather", segs=8)
            else:
                xcyl(p, 0.12, 0.1, (W * 0.55, 0, Hh * 0.55), mat="metal", segs=10)
        elif slot == "power":
            heat(p, 0, 0, Hh * 0.75 + 0.1, 0.05)
            if tier(e) != "hand":
                engine(p, W * 0.6, D * 0.45, 0, 0.55)
        else:
            p.lathe([(0.4, Hh + 0.5), (0.12, Hh + 0.85)], mat="metal" if tier(e) != "high" else "body", segs=8)
            flue(p, 0, 0, Hh + 0.85, Hh + 1.5, 0.08, mat="metal")
            if e == "Industrial":
                steps(p, 0.3, 0.3, Hh + 1.5, 3, 0.05, mat="fit", shrink=0.7)


# ================================================================ Anvil


def anvil(p, slot):
    e, g = p.era, p.region
    W, D, H = frame(p, ANVIL)
    if g == "Ocean":  # low block anvil set in a log stump: the smith squats
        Ha = min(H, 0.45)
        if slot == "base":
            p.cyl(W * 0.35, W * 0.38, Ha - 0.12, mat=pick(p, "teak" if e != "Primal" else "wood", "metal", "body"), segs=10)
        elif slot == "mechanism":
            p.box((W * 0.3, D * 0.25, 0.14), T((0, 0, Ha - 0.05)), mat=pick(p, "iron" if e != "Primal" else "stone", "metal", "body"), bevel=0.05)
        elif slot == "drive":
            hammer(p, W * 0.05, -D * 0.05, Ha + 0.02, rot=30)
        elif slot == "power":
            p.box((0.18, 0.02, 0.02), T((-W * 0.05, D * 0.05, Ha + 0.03)), mat=lit(p), bevel=0)
            if tier(e) != "hand":
                engine(p, W * 0.8, D * 0.3, 0, 0.55)
        else:
            lash(p, W * 0.36, (Ha - 0.12) * 0.5, 0.05, segs=8)
            for s in (-1, 1):
                horn(p, s * W * 0.36, 0, Ha - 0.12, 0.08, s, mat="accent")
    elif g == "Gale":  # boulder anvil with a hammerstone, on a clay ring
        if slot == "base":
            p.cyl(W * 0.5, W * 0.55, 0.1, mat=pick(p, "clay", "metal", "body"), segs=10)
            zig(p, W * 0.52, 0.05, 0.06, 10)
        elif slot == "mechanism":
            rock(p, W * 0.35, D * 0.3, H * 0.45, (0, 0, H * 0.5), mat=pick(p, "stone", "metal", "body"))
            p.box((W * 0.4, D * 0.35, 0.03), T((0, 0, H * 0.93)), mat=pick(p, "iron" if e != "Primal" else "stone_dark", "metal", "fit"), bevel=0)
        elif slot == "drive":
            if tier(e) == "hand":
                rock(p, 0.07, 0.055, 0.05, (W * 0.2, -D * 0.1, H * 0.96 + 0.05), mat="stone_dark")
            else:
                hammer(p, W * 0.1, -D * 0.1, H * 0.95, rot=20)
        elif slot == "power":
            p.ball(0.04, M(loc=(-W * 0.1, 0, H * 0.95 + 0.02), scale=(1.8, 1, 0.6)), mat=lit(p), segs=(6, 4))
            if tier(e) != "hand":
                engine(p, W * 0.8, D * 0.3, 0, 0.55)
        else:
            pegs(p, W * 0.5, 0.1, 4, 0.1, mat="body")
    elif g == "Radiant":  # horned anvil on a lotus-carved stone plinth
        zp = H - 0.24
        if slot == "base":
            p.lathe([(W * 0.4, 0), (W * 0.38, 0.06), (W * 0.25, zp * 0.5), (W * 0.3, zp)], mat=pick(p, "sandstone", "metal", "body"), segs=8)
            petals(p, W * 0.35, 0.02, 8, 0.05, mat="accent", tilt=55)
        elif slot == "mechanism":
            _horned(p, H, W * 0.8, D * 0.3, mat=pick(p, "iron", "metal", "fit"), horn=True)
        elif slot == "drive":
            hammer(p, 0, -D * 0.05, H, rot=-20)
        elif slot == "power":
            p.box((0.2, 0.022, 0.022), T((-W * 0.08, D * 0.05, H + 0.011)), mat=lit(p), bevel=0)
            if tier(e) != "hand":
                engine(p, W * 0.85, D * 0.3, 0, 0.55)
        else:
            dome(p, 0.1, 0.0, T((-W * 0.75, D * 0.3, 0)), mat="fit", segs=8)  # quench pot
            tongs(p, W * 0.5, -D * 0.3, 0.0, 0.45, rot=50)
    else:  # London anvil on a stand; press head over it in the high eras
        if slot == "base":
            if tier(e) == "hand":
                p.cyl(W * 0.38, W * 0.4, H - 0.24, mat="wood", segs=10)
            else:
                for sx in (-1, 1):
                    for sy in (-1, 1):
                        p.box((0.05, 0.05, H - 0.24), M(loc=(sx * W * 0.25, sy * D * 0.2, (H - 0.24) / 2), rot=(sy * 6, -sx * 6, 0)), mat="metal", bevel=0)
        elif slot == "mechanism":
            _horned(p, H, W * 0.85, D * 0.3, mat=pick(p, "iron", "metal", "body"))
        elif slot == "drive":
            if tier(e) == "high":  # C-arm press head
                p.box((0.1, D * 0.2, 0.7), T((-W * 0.45, D * 0.25, H + 0.35)), mat="body", bevel=0.2)
                p.box((W * 0.5, D * 0.2, 0.08), T((-W * 0.2, D * 0.25, H + 0.66)), mat="body", bevel=0.2)
                p.box((0.12, 0.12, 0.1), T((0, 0, H + 0.55)), mat="fit", bevel=0.2)
            else:
                hammer(p, 0, -D * 0.05, H, rot=25)
        elif slot == "power":
            p.box((0.2, 0.022, 0.022), T((-W * 0.08, D * 0.05, H + 0.011)), mat=lit(p), bevel=0)
            if tier(e) != "hand":
                engine(p, W * 0.85, D * 0.3, 0, 0.55)
        else:
            bucket(p, -W * 0.85, D * 0.2, 0.15, 0.32, mat="wood" if tier(e) == "hand" else "metal")
            if e == "Industrial":
                steps(p, W * 0.5, D * 0.5, 0, 2, 0.04, mat="fit", shrink=0.8)


# ================================================================ Millstone


def millstone(p, slot):
    e, g = p.era, p.region
    W, D, H = frame(p, MILL)
    if g == "Ocean":  # long rice-pounding trough with pestles
        L = max(W, 0.9)
        if slot == "base":
            for s in (-1, 1):
                p.box((0.1, D * 0.5, 0.08), T((s * L * 0.35, 0, 0.04)), mat="stone", bevel=0.05)
        elif slot == "mechanism":
            p.box((L, 0.3, 0.22), T((0, 0, 0.19)), mat=pick(p, "teak" if e != "Primal" else "wood", "metal", "body"), bevel=0.1)
            for x in (-L * 0.25, L * 0.15):
                p.cyl(0.08, 0.06, 0.006, T((x, 0, 0.301)), mat="bone", segs=8)
        elif slot == "drive":
            if tier(e) == "hand":
                for i, x in enumerate((-L * 0.25, L * 0.15)):
                    p.lathe([(0.03, 0), (0.025, 0.2), (0.02, 0.8), (0.03, 1.1), (0, 1.12)], M(loc=(x, 0, 0.31 + i * 0.25), rot=(J(p, 6, 0.6), 0, 0)), mat="wood", segs=6)
            else:  # huller drum on the trough
                xcyl(p, 0.14, L * 0.5, (0, 0, 0.45), mat="metal", segs=10)
        elif slot == "power":
            if tier(e) != "hand":
                engine(p, L * 0.65, D * 0.3, 0, 0.6)
            else:
                p.cyl(0.1, 0.1, 0.18, T((L * 0.55, -0.2, 0)), mat="rattan", segs=8)
        else:
            for s in (-1, 1):
                horn(p, s * L * 0.5, 0, 0.27, 0.1, s, mat="accent")
            sack(p, -L * 0.6, D * 0.25, 0.12, 0.25, mat="rope")
    elif g == "Gale":  # grinding platform with several hollows and handstones
        if slot == "base":
            p.box((W * 1.1, D * 0.9, 0.25), T((0, 0, 0.125)), mat=pick(p, "clay", "metal", "body"), bevel=0.15)
        elif slot == "mechanism":
            for x in (-W * 0.3, 0, W * 0.3):
                p.lathe([(0.12, 0.251), (0.08, 0.235), (0, 0.23)], T((x, 0, 0)), mat="stone", segs=8)
        elif slot == "drive":
            if tier(e) == "hand":
                for x in (-W * 0.3, W * 0.3):
                    rock(p, 0.09, 0.05, 0.035, (x, -0.02, 0.27), mat="stone_dark")
            else:
                p.box((0.3, 0.3, 0.3), T((W * 0.3, 0, 0.4)), mat="metal", bevel=0.05)
                p.lathe([(0.05, 0.55), (0.18, 0.75)], T((W * 0.3, 0, 0)), mat="metal", segs=8)
        elif slot == "power":
            if tier(e) != "hand":
                engine(p, W * 0.75, D * 0.2, 0, 0.6)
            else:
                p.lathe([(0, 0), (0.12, 0.02), (0.15, 0.12), (0.1, 0.2)], T((-W * 0.7, -D * 0.2, 0)), mat="gourd", segs=8)
        else:
            zig(p, W * 0.56, 0.12, 0.08, 12, M(scale=(1, D / W, 1)))
    elif g == "Radiant":  # chakki: two stones with a peg handle on a cloth
        r = min(W, D) * 0.38
        if slot == "base":
            p.cyl(r * 1.5, r * 1.5, 0.01, mat="cloth", segs=10)
            petals(p, r * 1.4, 0.0, 8, 0.05, mat="accent", tilt=80)
        elif slot == "mechanism":
            p.cyl(r, r, 0.08, T((0, 0, 0.01)), mat="stone", segs=12, bevel=0.04)
            p.cyl(r * 0.97, r * 0.97, 0.08, T((0, 0, 0.096)), mat="stone", segs=12, bevel=0.04)
            p.cyl(r * 0.15, r * 0.1, 0.01, T((0, 0, 0.176)), mat="stone_dark", segs=8)
        elif slot == "drive":
            if tier(e) == "hand":
                p.cyl(0.015, 0.012, 0.22, T((r * 0.7, 0, 0.17)), mat="wood", segs=5)
            else:  # atta chakki: cased stones and a belt wheel
                p.cyl(r * 1.1, r * 1.1, 0.3, T((0, 0, 0.01)), mat="metal", segs=10)
                p.lathe([(0.06, 0.31), (0.2, 0.5)], mat="metal", segs=8)
                xwheel(p, 0.2, (r * 1.2, 0, 0.3), rim="metal", hub="metal", spokes=4)
        elif slot == "power":
            if tier(e) != "hand":
                engine(p, W * 0.7, D * 0.3, 0, 0.6)
            else:
                p.lathe([(0, 0), (0.1, 0.02), (0.13, 0.12), (0.07, 0.18), (0.09, 0.2)], T((-r * 1.3, -r * 0.5, 0)), mat="copper", segs=8)
        else:
            if tier(e) == "hand":
                dome(p, 0.06, 0.18, mat="fit", segs=6, finial=False)
            else:
                crown(p, 0, 0, 0.5, 0.1)
    else:  # cased stones by era
        r = min(W, D) * 0.4
        if slot == "base":
            p.box((W, D, 0.35), T((0, 0, 0.175)), mat=pick(p, "wood_dark" if e != "Primal" else "stone", "metal", "body"), bevel=0.05)
        elif slot == "mechanism":
            p.cyl(r, r, 0.2, T((0, 0, 0.35)), mat=pick(p, "wood", "metal", "body"), segs=12)
        elif slot == "drive":
            p.lathe([(0.06, 0.6), (r * 0.8, 0.9)], mat=pick(p, "wood", "metal", "fit"), segs=8)
            if tier(e) == "machine":
                xwheel(p, 0.25, (W * 0.55, 0, 0.45), rim="metal", hub="metal", spokes=6)
        elif slot == "power":
            if tier(e) != "hand":
                engine(p, W * 0.75, D * 0.3, 0, 0.6)
            else:
                p.tube([(r * 0.8, 0, 0.5), (r * 0.8, 0, 0.75)], 0.015, mat="wood", segs=4)
        else:
            if e == "Industrial":
                steps(p, W * 0.6, D * 0.6, 0.35, 2, 0.03, mat="fit", shrink=0.85)
            sack(p, -W * 0.6, -D * 0.3, 0.12, 0.28)


# ================================================================ Kiln


def kiln(p, slot):
    e, g = p.era, p.region
    W, D, H = frame(p, KILN)
    Hk = max(H, 1.0)
    r = min(W, D) * 0.45
    if g == "Ocean":  # beehive kiln under a horned saddle shelter
        if slot == "base":
            p.box((W * 1.1, D * 1.1, 0.12), T((0, 0, 0.06)), mat="stone", bevel=0)
        elif slot == "mechanism":
            p.lathe([(r, 0.12), (r * 1.02, Hk * 0.4), (r * 0.6, Hk * 0.7), (0.1, Hk * 0.78)], mat=pick(p, "clay", "metal", "body"), segs=10)
        elif slot == "drive":  # fire mouth
            p.box((0.3, 0.06, 0.25), T((0, -r * 0.95, 0.25)), mat="stone_dark", bevel=0)
        elif slot == "power":
            heat(p, 0, -r * 0.8, 0.14, 0.06)
            if tier(e) != "hand":
                engine(p, W * 0.7, D * 0.3, 0, 0.6)
        else:
            for sx in (-1, 1):
                for sy in (-1, 1):
                    p.cyl(0.04, 0.035, Hk, T((sx * W * 0.5, sy * D * 0.5, 0)), mat=pick(p, "bamboo", "metal", "fit"), segs=6)
            for s in (-1, 1):
                p.box((W * 1.3, D * 0.62, 0.03), M(loc=(0, s * D * 0.25, Hk + 0.12), rot=(s * 28, 0, 0)), mat=pick(p, "rattan", "fit"), bevel=0)
                horn(p, s * W * 0.65, 0, Hk + 0.2, 0.2, s, mat="accent")
    elif g == "Gale":  # tall clay updraft kiln bristling with pegs
        if slot == "base":
            p.cyl(r * 1.2, r * 1.25, 0.15, mat="clay", segs=10)
        elif slot == "mechanism":
            p.lathe([(r, 0.15), (r * 0.9, Hk * 0.6), (r * 0.35, Hk), (0.12, Hk * 1.05)], mat=pick(p, "clay", "metal", "body"), segs=10)
            zig(p, r * 0.85, Hk * 0.55, 0.12, 10)
        elif slot == "drive":
            p.plate([(-0.15, 0), (-0.15, 0.2), (0, 0.32), (0.15, 0.2), (0.15, 0)], 0.06, T((0, -r * 0.98, 0.15)), mat="stone_dark", bevel=0)
        elif slot == "power":
            heat(p, 0, -r * 0.8, 0.16, 0.06)
            if tier(e) != "hand":
                engine(p, W * 0.75, D * 0.2, 0, 0.6)
        else:
            for z in (0.35, 0.6, 0.85):
                pegs(p, r * (1.0 - z * 0.5), Hk * z, 6, 0.18, mat="body")
    elif g == "Radiant":  # brick bhatti with a domed chimney
        if slot == "base":
            p.box((W, D, 0.1), T((0, 0, 0.05)), mat="stone", bevel=0)
        elif slot == "mechanism":
            brick(p, W * 0.8, D * 0.8, Hk * 0.6, (0, 0, 0.1), mat=pick(p, "clay", "metal", "body"), n=3)
        elif slot == "drive":
            p.box((0.3, 0.06, 0.3), T((0, -D * 0.41, 0.3)), mat="stone_dark", bevel=0)
            p.lathe([(0.08, 0.25), (0.14, 0.3), (0.08, 0.4)], T((0, -D * 0.44, 0)) @ M(rot=(90, 0, 0)), mat="fit", segs=6)
        elif slot == "power":
            heat(p, 0, -D * 0.35, 0.12, 0.06)
            if tier(e) != "hand":
                engine(p, W * 0.7, 0, 0, 0.6)
        else:
            flue(p, W * 0.25, D * 0.25, Hk * 0.7, Hk * 1.4, 0.1, mat=pick(p, "clay", "metal", "body"), cap=False)
            dome(p, 0.15, Hk * 1.4, T((W * 0.25, D * 0.25, 0)), mat="fit", segs=8)
            petals(p, 0.14, Hk * 1.38, 6, 0.04, T((W * 0.25, D * 0.25, 0)), mat="accent", tilt=70)
    else:  # bottle kiln / box kiln / cabinet
        if slot == "base":
            p.cyl(r * 1.15, r * 1.2, 0.12, mat="stone", segs=10)
        elif slot == "mechanism":
            if tier(e) == "high":
                p.box((W * 0.8, D * 0.8, Hk * 0.8), T((0, 0, 0.12 + Hk * 0.4)), mat="body", bevel=0.3)
                p.box((W * 0.3, 0.02, Hk * 0.25), T((0, -D * 0.41, Hk * 0.45)), mat="glow", bevel=0)
            elif tier(e) == "machine":
                p.box((W * 0.9, D * 0.8, Hk * 0.7), T((0, 0, 0.12 + Hk * 0.35)), mat="metal", bevel=0.05)
            else:  # bottle kiln
                p.lathe([(r, 0.12), (r * 1.05, Hk * 0.5), (r * 0.4, Hk * 1.1), (r * 0.35, Hk * 1.4)], mat=pick(p, "clay"), segs=10)
        elif slot == "drive":
            p.box((0.35, 0.06, 0.4), T((0, -r * 1.02 if tier(e) == "hand" else -D * 0.42, 0.35)), mat="metal" if tier(e) != "hand" else "iron", bevel=0)
        elif slot == "power":
            heat(p, 0, -r * 0.8, 0.14, 0.06)
            if tier(e) != "hand":
                engine(p, W * 0.75, 0, 0, 0.6)
        else:
            if tier(e) == "hand":
                p.ring(r * 1.07, 0.02, T((0, 0, Hk * 0.4)), mat="iron", segs=10)
            else:
                flue(p, W * 0.3, D * 0.2, Hk * 0.82, Hk * 1.5, 0.08, mat="metal")
                if e == "Industrial":
                    steps(p, 0.3, 0.3, Hk * 1.5, 3, 0.05, mat="fit", shrink=0.7)


# ================================================================ Stove


def stove(p, slot):
    e, g = p.era, p.region
    W, D, H = frame(p, STOVE)
    Hs = max(H, 0.4)
    if g == "Ocean":  # long clay tungku with two holes and a wok
        if slot == "base":
            p.box((W + 0.1, D + 0.1, 0.06), T((0, 0, 0.03)), mat="stone", bevel=0)
        elif slot == "mechanism":
            p.box((W, D * 0.8, Hs - 0.06), T((0, 0, 0.06 + (Hs - 0.06) / 2)), mat=pick(p, "clay", "metal", "body"), bevel=0.1)
            for x in (-W * 0.25, W * 0.25):
                p.ring(0.17, 0.02, T((x, 0, Hs)), mat=pick(p, "clay", "metal", "fit"), segs=10)
        elif slot == "drive":
            _wok(p, -W * 0.25, 0, Hs + 0.01, J(p, 0.2, 0.06), mat="iron" if tier(e) != "high" else "fit")
            _cookpot(p, W * 0.25, 0, Hs, 0.13, mat="ceramic" if tier(e) == "hand" else "metal")
        elif slot == "power":
            heat(p, -W * 0.25, -D * 0.35, 0.07, 0.05)
            if tier(e) != "hand":
                engine(p, W * 0.75, D * 0.2, 0, 0.5)
        else:
            for s in (-1, 1):
                horn(p, s * W * 0.5, 0, Hs - 0.02, 0.1, s, mat="accent")
            logs(p, -W * 0.5 - 0.2, -D * 0.4, 0, 0.4, 0.03, n=2)
    elif g == "Gale":  # round clay stove with a three-legged pot
        r = min(W, D) * 0.4
        if slot == "base":
            flagstone(p, W, D, 0.03, 0, mat="stone_dark", rough=0.2)
        elif slot == "mechanism":
            p.lathe([(r, 0.03), (r * 0.95, Hs * 0.7), (r * 0.7, Hs * 0.75)], mat=pick(p, "clay", "metal", "body"), segs=10)
            zig(p, r * 0.97, Hs * 0.35, 0.08, 8)
        elif slot == "drive":  # potjie
            for i in range(3):
                a = i * TAU / 3 + math.pi / 2
                p.tube([(math.cos(a) * 0.1, math.sin(a) * 0.1, Hs * 0.75 + 0.04), (math.cos(a) * 0.12, math.sin(a) * 0.12, Hs * 0.75)], 0.008, mat="iron", segs=4)
            p.lathe([(0.08, Hs * 0.75 + 0.04), (0.17, Hs * 0.75 + 0.14), (0.14, Hs * 0.75 + 0.26), (0.13, Hs * 0.75 + 0.28)], mat="iron", segs=10)
        elif slot == "power":
            heat(p, 0, -r * 0.7, 0.05, 0.05)
            p.box((0.2, 0.05, 0.15), T((0, -r * 0.97, 0.1)), mat="stone_dark", bevel=0)
            if tier(e) != "hand":
                engine(p, W * 0.75, D * 0.2, 0, 0.5)
        else:
            pegs(p, r * 0.95, Hs * 0.55, 4, 0.08, mat="body")
    elif g == "Radiant":  # U-shaped chulha with a tawa
        if slot == "base":
            p.box((W, D, 0.05), T((0, 0, 0.025)), mat="stone", bevel=0)
        elif slot == "mechanism":
            for s in (-1, 1):
                p.box((0.12, D * 0.7, Hs * 0.6), T((s * 0.2, 0, 0.05 + Hs * 0.3)), mat=pick(p, "clay", "metal", "body"), bevel=0.2)
            p.box((0.52, 0.1, Hs * 0.6), T((0, D * 0.3, 0.05 + Hs * 0.3)), mat=pick(p, "clay", "metal", "body"), bevel=0.2)
        elif slot == "drive":  # tawa griddle
            p.lathe([(0, Hs * 0.65 + 0.01), (0.24, Hs * 0.65), (0.26, Hs * 0.65 + 0.015)], mat="iron" if tier(e) != "high" else "fit", segs=12)
            p.tube([(0.26, 0, Hs * 0.65 + 0.01), (0.4, -0.05, Hs * 0.65 + 0.02)], 0.006, mat="iron", segs=4)
        elif slot == "power":
            heat(p, 0, -D * 0.1, 0.06, 0.05)
            if tier(e) != "hand":
                engine(p, W * 0.6, D * 0.2, 0, 0.5)
        else:
            _cookpot(p, -W * 0.38, -D * 0.2, 0.05, 0.1, mat="copper" if tier(e) == "hand" else "metal")
            petals(p, 0.1, 0.05, 5, 0.03, T((-W * 0.38, -D * 0.2, 0)), mat="accent", tilt=70)
    else:  # range by era
        if slot == "base":
            for sx in (-1, 1):
                for sy in (-1, 1):
                    p.box((0.05, 0.05, 0.12), T((sx * W * 0.42, sy * D * 0.35, 0.06)), mat="metal" if tier(e) != "hand" else "iron", bevel=0)
        elif slot == "mechanism":
            p.box((W * 0.9, D * 0.8, Hs - 0.12), T((0, 0, 0.12 + (Hs - 0.12) / 2)), mat=pick(p, "iron" if e != "Primal" else "stone", "metal", "body"), bevel=0.05)
            p.box((W * 0.35, 0.02, Hs * 0.35), T((W * 0.2, -D * 0.41, Hs * 0.45)), mat="metal", bevel=0)
        elif slot == "drive":
            for x in (-W * 0.25, W * 0.2):
                _cookpot(p, x, 0, Hs, 0.12, mat="iron" if tier(e) == "hand" else "metal")
        elif slot == "power":
            heat(p, -W * 0.2, -D * 0.38, 0.2, 0.05)
            if tier(e) != "hand":
                engine(p, W * 0.7, D * 0.2, 0, 0.5)
        else:
            if tier(e) != "high":
                flue(p, -W * 0.35, D * 0.3, Hs, Hs + 1.0, 0.06, mat="metal" if tier(e) != "hand" else "iron")
            else:  # extractor hood on a back mast
                p.box((0.06, 0.06, 0.9), T((0, D * 0.38, Hs + 0.45)), mat="fit", bevel=0)
                p.box((W * 0.8, D * 0.6, 0.06), T((0, 0, Hs + 0.85)), mat="body", bevel=0.3)
            if e == "Industrial":
                steps(p, W * 0.9, 0.1, Hs, 3, 0.04, M(loc=(0, D * 0.4, 0)), mat="fit", shrink=0.85)


# ================================================================ Still


def still(p, slot):
    e, g = p.era, p.region
    W, D, H = frame(p, STILL)
    Hs = max(H * 0.6, 0.5)
    pmat = {"Ocean": pick(p, "clay", "metal", "body"), "Gale": pick(p, "clay", "metal", "body"),
            "Radiant": pick(p, "copper", "metal", "fit"), "Metropolis": pick(p, "copper" if e != "Primal" else "clay", "metal", "body")}[g]
    r = min(W, D) * 0.3
    x0 = -W * 0.3
    if slot == "base":  # firebox
        if g == "Gale":
            for i in range(3):
                a = i * TAU / 3
                rock(p, 0.09, 0.08, 0.12, (x0 + math.cos(a) * r * 0.9, math.sin(a) * r * 0.9, 0.1), mat="stone")
        else:
            brick(p, r * 2.4, r * 2.4, Hs * 0.4, (x0, 0, 0), mat=pick(p, "clay" if g != "Metropolis" else "stone", "metal", "body"), n=1)
    elif slot == "mechanism":  # the pot
        z = Hs * 0.4 if g != "Gale" else 0.2
        if g == "Radiant":  # degh: round copper pot with a dome lid
            p.lathe([(r * 0.5, z), (r * 1.05, z + r * 0.5), (r * 0.8, z + r * 1.1), (r * 0.6, z + r * 1.2)], T((x0, 0, 0)), mat=pmat, segs=10)
            dome(p, r * 0.6, z + r * 1.2, T((x0, 0, 0)), mat="fit", segs=8)
        else:
            p.lathe([(r * 0.6, z), (r * 1.05, z + r * 0.5), (r * 0.85, z + r * 1.1), (r * 0.4, z + r * 1.35)], T((x0, 0, 0)), mat=pmat, segs=10)
            if g == "Gale":
                zig(p, r * 1.0, z + r * 0.5, 0.06, 8, T((x0, 0, 0)))
    elif slot == "drive":  # the condenser line
        z = (Hs * 0.4 if g != "Gale" else 0.2) + r * 1.3
        xe = W * 0.35
        if g == "Ocean":  # long bamboo pipe through a water trough
            p.tube([(x0, 0, z), (xe, 0, 0.35)], 0.025, mat=pick(p, "bamboo", "metal", "fit"), segs=6)
            p.box((0.5, 0.2, 0.18), T(((x0 + xe) / 2 + 0.1, 0, 0.42)), mat=pick(p, "teak", "metal", "body"), bevel=0.05)
            p.box((0.48, 0.18, 0.004), T(((x0 + xe) / 2 + 0.1, 0, 0.5)), mat="glass", bevel=0)
            lash(p, 0.026, 0, 0.03, M(loc=(xe * 0.6, 0, 0.42), rot=(0, 70, 0)), segs=6)
        elif g == "Gale":  # reed pipe through a calabash cooler
            p.tube([(x0, 0, z), (W * 0.1, 0, 0.35), (xe, 0, 0.2)], 0.015, mat=pick(p, "bark", "metal", "fit"), segs=5)
            p.ball(0.16, M(loc=(W * 0.1, 0, 0.3), scale=(1, 1, 0.9)), mat=pick(p, "gourd", "metal", "body"), segs=(8, 5))
        elif g == "Radiant":  # bamboo tube into a clay bhapka sitting in a water bowl
            p.tube([(x0, 0, z), (xe, 0, 0.3)], 0.018, mat=pick(p, "bamboo", "metal", "fit"), segs=5)
            p.lathe([(0, 0), (0.25, 0.02), (0.27, 0.15)], T((xe, 0, 0)), mat="clay", segs=10)
            p.cyl(0.24, 0.24, 0.004, T((xe, 0, 0.13)), mat="glass", segs=10)
        else:  # swan neck to a worm tub
            p.tube([(x0, 0, z), (x0 + 0.2, 0, z + 0.2), (xe, 0, 0.6)], 0.02, mat=pick(p, "copper" if e != "Primal" else "bark", "metal", "fit"), segs=5)
            p.cyl(0.2, 0.2, 0.55, T((xe, 0, 0)), mat=pick(p, "wood", "metal", "body"), segs=10)
            for k in (0.15, 0.45):
                p.ring(0.205, 0.008, T((xe, 0, k)), mat="metal", segs=10)
    elif slot == "power":
        z = Hs * 0.4 if g != "Gale" else 0.2
        heat(p, x0, 0, 0.02 if g == "Gale" else z - 0.15, 0.05)
        if tier(e) != "hand":
            engine(p, x0 - r * 1.6, D * 0.2, 0, 0.55)
    else:  # receiver vessel and the region's mark
        xe = W * 0.35 + 0.25
        if g == "Ocean":
            p.lathe([(0, 0), (0.1, 0.02), (0.12, 0.15), (0.05, 0.25), (0.06, 0.28)], T((xe, -0.1, 0)), mat=pick(p, "clay", "glass", "glass"), segs=8)
            for s in (-1, 1):
                horn(p, x0 + s * r * 1.2, 0, Hs * 0.4, 0.08, s, mat="accent")
        elif g == "Gale":
            p.lathe([(0, 0), (0.1, 0.02), (0.12, 0.12), (0.06, 0.2), (0.08, 0.3), (0.03, 0.36)], T((W * 0.35 + 0.05, 0, 0)), mat=pick(p, "gourd", "glass", "glass"), segs=8)
        elif g == "Radiant":
            petals(p, r * 1.1, Hs * 0.4, 6, 0.04, T((x0, 0, 0)), mat="accent", tilt=70)
        else:
            p.lathe([(0, 0), (0.08, 0.01), (0.1, 0.15), (0.03, 0.25)], T((xe, -0.15, 0)), mat="glass", segs=8)
            if e == "Industrial":
                steps(p, 0.4, 0.4, 0, 2, 0.03, T((W * 0.35, 0, 0)), mat="fit", shrink=0.8)


for _g in REGIONS:
    regional("Loom", _g)(loom)
    regional("Forge", _g)(forge)
    regional("Anvil", _g)(anvil)
    regional("Millstone", _g)(millstone)
    regional("Kiln", _g)(kiln)
    regional("Stove", _g)(stove)
    regional("Still", _g)(still)
