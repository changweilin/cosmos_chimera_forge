"""Four-planet forms of the containers (cosmos_chimera everyday-objects.md#四星球形體, Q-A38 batch 2, vessels).

Bucket, Basket, Pot, Strongbox, MedKit, Mortar, Creel, Bell (forms_vessel.py) and SewingKit, AlchemySet, Quiver,
Teaset, Tableware (forms_ware.py) for Ocean, Gale, Radiant and Metropolis in all 8 eras. Slots, frames and sizes are
the shared forms' (body / lid / handle / band; Z up, front -Y, origin at the floor contact; sets stand on one
footprint: body the main piece, lid its cover, handle grips and utensils, band companions and trims).

Each region keeps one silhouette across the eras and swaps the mechanism by tier (hand-made, machine, high-tech);
eras inside a tier differ by craft (kit_lib.REGION_STYLE roles) and their own token (era_mark). Containers do not
glow except the era accents (Steampunk, Future, Wasteland, Ancient), as the shared vessels.

Region vocabulary: Ocean bamboo tubs, rattan weave and lashing, horn tips, wok and tudung cover, tumpeng tray;
Gale calabash and coiled baskets, clay, potjie on three legs, zigzag friezes, beam-end pegs, tagine cone, tall
teapot with glasses; Radiant brass lota and handi, lotus petals, onion domes, ghanta bell, thali with katoris;
Metropolis by era (iron coffer, wicker and leather, enamel tin, art-deco setbacks, chrome, finned shell, scrap).
"""
import math

from mathutils import Matrix, Vector

from forms_region_pilot import HAND, MACHINE, dome, era_mark, gear, horn, lash, pegs, petals, signature, steps, zig, fins
from forms_tools import rod
from forms_vessel import bail, bell_shape, closed, rad_at, ribs, shell, weave
from forms_ware import arrow, blk, bowl, cup, flask, plate, spool
from kit_forms import F, J, coin, regional
from kit_lib import M, REGIONS

T = Matrix.Translation


def tier(e):
    return "hand" if e in HAND else "machine" if e in MACHINE else "high"


def pick(p, hand, machine="body", high="body"):
    """Material by tier: a region's natural material in the hand-made eras, the era's roles afterwards."""
    return {"hand": hand, "machine": machine, "high": high}[tier(p.era)]


def mark(p, r, z, m=None):
    if p.era not in HAND:
        era_mark(p, r, z, m)


def rim(p, r, z, mat="fit", t=0.006, segs=10):
    p.ring(r, t, T((0, 0, z)), mat=mat, segs=segs, square=False)


def prof(table, p, r, h):
    """Region x tier lathe profile as (r fraction, z fraction)."""
    return [(f * r, z * h) for f, z in table[p.region][tier(p.era)]]


# ================================================================ Bucket (carried)

BUCKET = {
    "Ocean": {"hand": [(0.85, 0), (1.0, 1)], "machine": [(0.85, 0), (1.0, 1)], "high": [(0.9, 0), (1.0, 0.1), (1.0, 1)]},
    "Gale": {"hand": [(0.55, 0), (1.1, 0.4), (0.95, 0.8), (0.75, 1)], "machine": [(0.8, 0), (1.0, 0.5), (0.9, 1)],
             "high": [(0.7, 0), (1.05, 0.45), (0.85, 1)]},
    "Radiant": {"hand": [(0.55, 0), (1.08, 0.45), (0.8, 0.82), (0.95, 1)], "machine": [(0.6, 0), (1.05, 0.5), (0.85, 0.85), (0.95, 1)],
                "high": [(0.6, 0), (1.05, 0.45), (0.85, 0.85), (1.0, 1)]},
    "Metropolis": {"hand": [(0.8, 0), (1.0, 1)], "machine": [(0.8, 0), (1.0, 1)], "high": [(0.9, 0), (0.95, 0.05), (1.0, 1)]},
}


def bucket(p, slot):
    e, g = p.era, p.region
    h, r = F(p, 0.30, 0.1), F(p, 0.15, 0.1)
    outer = prof(BUCKET, p, r, h)
    top = outer[-1][0]
    if slot == "body":
        mat = {"Ocean": pick(p, "bamboo"), "Gale": pick(p, "gourd" if e == "Primal" else "clay" if e == "Agrarian" else "leather"),
               "Radiant": pick(p, "clay" if e == "Primal" else "copper" if e == "Agrarian" else "brass", "body", "fit"),
               "Metropolis": "body"}[g]
        shell(p, outer, 0.008, mat=mat, segs=10)
    elif slot == "lid":  # the mouth
        if g == "Radiant":
            p.ring(top * 1.02, 0.012, T((0, 0, h)), mat="fit", segs=10, square=False)
        elif g == "Gale" and tier(e) == "hand":
            rim(p, top * 1.03, h, mat="grip", t=0.01, segs=8)
        else:
            rim(p, top * 1.01, h, mat="fit", t=J(p, 0.007, 0.2))
        if g == "Metropolis" and e == "Future":
            p.ring(top * 1.0, 0.003, T((0, 0, h - 0.01)), mat="glow", segs=10)
    elif slot == "handle":
        if g == "Ocean":  # rattan bail on two horn ears
            bail(p, top * 0.98, h * 0.95, J(p, h * 0.6, 0.15), 0.006, mat="grip", segs=4)
            for s in (-1, 1):
                horn(p, s * top * 0.98, 0, h * 0.82, r * 0.35, s, mat="fit")
        elif g == "Gale":  # carrying cord through two pegs, a head-ring for the hand-made eras
            pegs(p, rad_at(outer, h * 0.85), h * 0.85, 2, r * 0.35)
            p.tube([(-top * 1.1, 0, h * 0.85), (0, 0, h * J(p, 1.5, 0.1)), (top * 1.1, 0, h * 0.85)], 0.005, mat="grip", segs=4)
        elif g == "Radiant":  # balti: two side loops
            for s in (-1, 1):
                p.ring(r * 0.16, 0.005, M(loc=(s * rad_at(outer, h * 0.85) * 1.05, 0, h * 0.85), rot=(0, 90, 0)), mat="fit", segs=6, square=False)
        else:
            rise = J(p, r * 0.95, 0.12)
            bail(p, top, h * 0.92, rise, 0.004, mat="metal" if tier(e) != "high" else "fit", segs=4)
            if tier(e) != "hand":
                p.cyl(0.012, 0.012, 0.09, M(loc=(-0.045, 0, h * 0.92 + rise), rot=(0, 90, 0)), mat="grip", segs=6)
    else:
        if g == "Metropolis" and e in ("Industrial", "Future"):
            fins(p, rad_at(outer, h * 0.5) * 0.95, h * 0.15, h * 0.85, 4, mat="fit")
        else:
            signature(p, rad_at(outer, h * 0.55), h * 0.5, 0.04)
        mark(p, rad_at(outer, h * 0.25), h * 0.25)


# ================================================================ Basket (carried)


def basket(p, slot):
    e, g = p.era, p.region
    h, r = F(p, 0.24, 0.12), F(p, 0.19, 0.1)
    sy = F(p, 0.72, 0.08)
    sc = M(scale=(1, sy, 1))
    weavemat = {"Ocean": pick(p, "rattan", "metal", "fit"), "Gale": pick(p, "bark" if e == "Primal" else "rope", "metal", "fit"),
                "Radiant": pick(p, "bamboo", "metal", "fit"), "Metropolis": pick(p, "bark", "metal", "fit")}[g]
    if g == "Ocean":  # low wide rattan basket, flared
        outer = [(r * 0.75, 0), (r * 0.95, h * 0.5), (r * 1.05, h * 0.8)]
    elif g == "Gale":  # tall coiled basket with a cone lid (agaseke)
        outer = [(r * 0.5, 0), (r * 0.72, h * 0.4), (r * 0.55, h * 1.0)]
    elif g == "Radiant":  # wide shallow tokri
        outer = [(r * 0.65, 0), (r * 1.05, h * 0.45), (r * 1.15, h * 0.6)]
    else:  # picnic basket / wire basket / shell tote, square-shouldered
        outer = [(r * 0.85, 0), (r * 0.95, h * 0.85)]
    top = outer[-1]
    if slot == "body":
        shell(p, outer, 0.008, mat=weavemat if tier(e) != "high" else "body", segs=10, m=sc)
    elif slot == "lid":
        if g == "Gale":
            p.cyl(top[0] * 1.02, 0.0, h * 0.6, M(loc=(0, 0, top[1])) @ sc, mat=weavemat if tier(e) != "high" else "fit", segs=8, bevel=0)
            p.ball(0.012, T((0, 0, top[1] + h * 0.6)), mat="accent", segs=(4, 3))
        elif g == "Metropolis" and tier(e) == "hand":
            for s in (-1, 1):
                p.box((top[0] * 0.95, top[0] * sy * 1.9, 0.01), M(loc=(s * top[0] * 0.48, 0, top[1] + 0.005)), mat="body", bevel=0)
        else:
            p.ring(top[0] * 1.01, 0.008, M(loc=(0, 0, top[1])) @ sc, mat="fit", segs=10, square=False)
    elif slot == "handle":
        if g == "Ocean":
            for s in (-1, 1):
                horn(p, s * top[0], 0, top[1] - 0.02, r * 0.3, s, mat="fit")
        elif g == "Gale":  # strap hung from the shoulder
            p.tube([(-r * 0.6, 0, h * 0.5), (0, J(p, 0.02, 0.5), h * 1.9), (r * 0.6, 0, h * 0.5)], 0.006, mat="grip", segs=4)
        elif g == "Radiant":
            for s in (-1, 1):
                p.ring(r * 0.12, 0.005, M(loc=(s * top[0] * 1.02, 0, top[1] * 0.85), rot=(0, 90, 0)), mat="fit", segs=8, square=False)
        else:
            bail(p, top[0] * 0.6, top[1], J(p, h * 0.7, 0.15), 0.006, mat="grip" if tier(e) == "hand" else "metal", segs=4, m=M(rot=(0, 0, 90)) if coin(p) else None)
    else:
        if tier(e) == "machine" and g != "Metropolis":
            ribs(p, outer, 8, "metal", rad=0.003, scale=(1, sy))
        elif g == "Gale":
            zig(p, rad_at(outer, h * 0.5), h * 0.45, 0.04, 8, sc)
        elif g == "Radiant":
            petals(p, rad_at(outer, h * 0.3), h * 0.25, 5, 0.018, sc, mat="accent", tilt=70)
        else:
            weave(p, outer, [h * 0.3, h * J(p, 0.6, 0.1)], "accent" if g == "Ocean" else "fit", t=0.005, segs=10, scale=(1, sy, 1))
        mark(p, rad_at(outer, h * 0.4), h * 0.4, sc)


# ================================================================ Pot (scene; cooking pot)


def pot(p, slot):
    e, g = p.era, p.region
    h, r = F(p, 0.2, 0.12), F(p, 0.17, 0.1)
    if g == "Ocean":  # wok under a woven tudung cover
        outer = [(r * 0.35, 0), (r * 0.8, h * 0.25), (r * 1.2, h * 0.5)]
    elif g == "Gale":  # potjie: round belly on three legs
        outer = [(r * 0.45, h * 0.18), (r * 1.0, h * 0.5), (r * 0.85, h * 0.85), (r * 0.8, h * 0.9)]
    elif g == "Radiant":  # handi: belly and a narrow flared neck
        outer = [(r * 0.5, 0), (r * 1.05, h * 0.4), (r * 0.65, h * 0.8), (r * 0.75, h * 0.9)]
    else:  # straight stock pot
        outer = [(r * 0.9, 0), (r * 0.95, h * 0.85)]
    top = outer[-1]
    if slot == "body":
        mat = {"Ocean": pick(p, "clay" if e == "Primal" else "iron", "metal"), "Gale": pick(p, "clay" if e == "Primal" else "iron", "metal"),
               "Radiant": pick(p, "clay" if e == "Primal" else "copper" if e == "Agrarian" else "brass", "metal", "fit"),
               "Metropolis": pick(p, "iron" if e != "Mercantile" else "copper", "metal")}[g]
        shell(p, outer, 0.008, mat=mat, segs=12)
    elif slot == "lid":
        if g == "Ocean":  # tudung saji: tall woven cone
            p.lathe([(top[0] * 1.0, top[1]), (top[0] * 0.7, top[1] + h * 0.35), (top[0] * 0.2, top[1] + h * 0.6), (0, top[1] + h * 0.62)],
                    mat=pick(p, "rattan", "fit", "glass"), segs=10)
            horn(p, 0, 0, top[1] + h * 0.6, h * 0.2, 1, mat="accent")
        elif g == "Gale":
            p.lathe([(top[0] * 1.02, top[1]), (top[0] * 0.6, top[1] + h * 0.15), (0.015, top[1] + h * 0.18)], mat="metal" if tier(e) != "hand" else "iron", segs=10)
            p.cyl(0.012, 0.01, 0.03, T((0, 0, top[1] + h * 0.18)), mat="accent", segs=5, bevel=0)
        elif g == "Radiant":
            dome(p, top[0] * 0.95, top[1], mat="fit", segs=10)
        else:
            if e == "Industrial":
                steps(p, top[0] * 1.8, top[0] * 1.8, top[1], 2, 0.015, mat="fit", shrink=0.6)
            else:
                p.lathe([(top[0] * 1.02, top[1]), (top[0] * 0.7, top[1] + h * 0.08), (0.02, top[1] + h * 0.1)], mat="fit" if e != "Primal" else "iron", segs=12)
                p.cyl(0.015, 0.015, 0.02, T((0, 0, top[1] + h * 0.1)), mat="grip", segs=6, bevel=0)
    elif slot == "handle":
        if g == "Ocean":
            for s in (-1, 1):
                p.ring(r * 0.12, 0.006, M(loc=(s * top[0] * 1.02, 0, top[1] - 0.005), rot=(0, 90, 0)), mat="fit", segs=8, square=False)
        elif g == "Gale":  # three legs and a bail
            for i in range(3):
                a = i * math.tau / 3 + math.pi / 2
                rod(p, (math.cos(a) * r * 0.55, math.sin(a) * r * 0.55, h * 0.25), (math.cos(a) * r * 0.75, math.sin(a) * r * 0.75, 0), 0.012, 0.009, mat="metal" if tier(e) != "hand" else "iron", segs=4)
            bail(p, top[0] * 0.95, top[1], J(p, r * 0.9, 0.12), 0.005, mat="iron" if tier(e) == "hand" else "metal")
        elif g == "Radiant":
            for s in (-1, 1):
                p.ring(r * 0.1, 0.006, M(loc=(s * rad_at(outer, h * 0.6) * 1.02, 0, h * 0.6), rot=(0, 90, 0)), mat="fit", segs=8, square=False)
        else:
            for s in (-1, 1):
                p.box((0.06, 0.03, 0.015), T((s * (top[0] + 0.028), 0, h * 0.75)), mat="grip" if tier(e) != "hand" else "metal", bevel=0.2)
    else:
        if g == "Ocean":  # the charcoal ring stand under the wok
            p.cyl(r * 0.5, r * 0.55, 0.03, mat=pick(p, "clay", "metal"), segs=8, bevel=0)
            if tier(e) == "high":
                p.ring(r * 0.52, 0.005, T((0, 0, 0.03)), mat="glow", segs=10)
        elif g == "Metropolis" and e in ("Future", "Industrial"):
            fins(p, top[0] * 0.98, h * 0.1, h * 0.7, 6, mat="fit")
            if e == "Future":
                p.ring(top[0], 0.004, T((0, 0, h * 0.05)), mat="glow", segs=12)
        else:
            signature(p, rad_at(outer, h * 0.5), h * 0.5, 0.04)
        mark(p, rad_at(outer, h * 0.4), h * 0.35)


# ================================================================ Strongbox (carried)


def strongbox(p, slot):
    e, g = p.era, p.region
    w, d = F(p, 0.3, 0.1), F(p, 0.2, 0.1)
    hb, hl = F(p, 0.13, 0.12), F(p, 0.045, 0.15)
    top = hb + hl
    if slot == "body":
        if g == "Gale":  # carved chest on four short peg legs
            blk(p, 0, 0, hb * 0.2, w, d, hb * 0.8, mat="body", b=0.05)
            for x in (-1, 1):
                for y in (-1, 1):
                    p.cyl(0.012, 0.014, hb * 0.2, T((x * w * 0.42, y * d * 0.4, 0)), mat="body", segs=4, bevel=0)
        elif g == "Radiant":  # dowry box with a stepped plinth
            blk(p, 0, 0, 0, w * 1.04, d * 1.04, hb * 0.12, mat="fit")
            blk(p, 0, 0, hb * 0.12, w, d, hb * 0.88, mat="body")
        else:
            blk(p, 0, 0, 0, w, d, hb, mat="body" if not (g == "Metropolis" and tier(e) == "hand") else "iron", b=None)
    elif slot == "lid":
        if g == "Ocean":  # saddle lid
            roof = [(-w * 0.52, 0), (-w * 0.56, hl * 0.6), (0, hl * 1.5), (w * 0.56, hl * 0.6), (w * 0.52, 0)]
            p.plate(roof, d * 1.04, T((0, 0, hb)), mat="fit" if tier(e) != "hand" else "body")
        elif g == "Radiant":  # domed lid
            p.lathe([(w * 0.5, 0), (w * 0.48, hl * 0.8), (w * 0.3, hl * 1.4), (0, hl * 1.6)], M(loc=(0, 0, hb), scale=(1, d / w, 1)), mat="fit" if e not in ("Primal", "Wasteland") else "body", segs=10)
        elif g == "Metropolis" and e == "Industrial":
            steps(p, w, d, hb, 2, hl * 0.5, mat="fit", shrink=0.85)
        else:
            blk(p, 0, 0, hb, w * 1.03, d * 1.03, hl, mat="body" if g != "Metropolis" or tier(e) == "high" else "fit")
    elif slot == "handle":  # lock and grips
        if g == "Ocean":
            for s in (-1, 1):
                horn(p, s * w * 0.55, 0, hb + hl * 0.6, hl * 1.4, s, mat="accent")
        elif g == "Gale":
            for s in (-1, 1):
                p.tube([(s * w * 0.5, -d * 0.2, hb * 0.75), (s * w * 0.58, 0, hb * 0.85), (s * w * 0.5, d * 0.2, hb * 0.75)], 0.006, mat="grip", segs=4)
        elif g == "Radiant":  # lotus lock plate
            petals(p, 0.02, 0, 5, 0.012, M(loc=(0, -d * 0.52, hb * 0.8), rot=(90, 0, 0)), mat="accent", tilt=0)
        else:
            if tier(e) == "high":  # keypad
                p.box((w * 0.25, 0.008, hb * 0.35), T((0, -d * 0.5, hb * 0.55)), mat="fit", bevel=0)
                p.box((w * 0.18, 0.004, 0.006), T((0, -d * 0.505, hb * 0.7)), mat="glow", bevel=0)
            else:  # dial or padlock hasp
                p.cyl(hb * 0.18, hb * 0.18, 0.012, M(loc=(0, -d * 0.5, hb * 0.55), rot=(90, 0, 0)), mat="metal", segs=8, bevel=0)
                p.tube([(-w * 0.1, 0, top + 0.002), (0, 0, top + J(p, 0.03, 0.2)), (w * 0.1, 0, top + 0.002)], 0.005, mat="metal", segs=4)
    else:
        if g == "Ocean":
            for x in (-1, 1):
                p.box((0.02, d * 1.05, hb * 0.9), T((x * w * 0.4, 0, hb * 0.5)), mat=pick(p, "rattan", "fit"), bevel=0)
        elif g == "Gale":
            for i in range(6):
                x = (i - 2.5) * w / 6
                p.box((w / 7, 0.006, hb * 0.25), M(loc=(x, -d * 0.505, hb * 0.55), rot=(0, 30 if i % 2 else -30, 0)), mat=("accent", "fit")[i % 2], bevel=0)
        elif g == "Radiant":
            for x in (-1, 1):
                for y in (-1, 1):
                    p.box((0.03, 0.03, hb * 0.9), T((x * w * 0.5, y * d * 0.5, hb * 0.55)), mat="fit", bevel=0)
        else:
            if e in ("Industrial", "Future", "Ancient"):
                for x in (-0.3, 0.3):
                    p.box((0.012, d * 1.02, hb * 0.9), T((x * w, 0, hb * 0.5)), mat="fit", bevel=0)
            else:
                for z in (hb * 0.2, hb * 0.8):
                    p.box((w * 1.02, d * 1.02, 0.012), T((0, 0, z)), mat="metal", bevel=0)
        mark(p, hb * 0.25, hb * 0.35, M(loc=(w * 0.3, -d * 0.3, 0)))


# ================================================================ MedKit (carried)


def medkit(p, slot):
    e, g = p.era, p.region
    w, d = F(p, 0.28, 0.1), F(p, 0.14, 0.1)
    hb, hl = F(p, 0.17, 0.1), F(p, 0.05, 0.15)
    if slot == "body":
        if g == "Ocean":  # bundle of bamboo tubes in a rattan case
            if tier(e) == "hand":
                for i in range(4):
                    x = (i - 1.5) * w / 4
                    p.cyl(w / 9, w / 9, hb, T((x, 0, 0)), mat="bamboo", segs=6, bevel=0)
            else:
                blk(p, 0, 0, 0, w, d, hb, mat="body", b=0.15)
        elif g == "Gale":  # calabash medicine bag
            closed(p, [(d * 0.5, 0), (d * 0.95, hb * 0.45), (d * 0.6, hb * 0.9), (d * 0.3, hb)], mat=pick(p, "gourd", "body", "body"), segs=9,
                   m=M(scale=(w / d / 1.4, 1, 1)))
        elif g == "Radiant":  # ayurvedic box with compartments
            blk(p, 0, 0, 0, w, d, hb, mat="body")
            for x in (-1, 0, 1):
                p.box((0.006, d * 1.01, hb * 0.8), T((x * w * 0.25, 0, hb * 0.5)), mat="fit", bevel=0)
        else:
            if tier(e) == "hand":  # doctor's bag
                p.lathe([(d * 0.5, 0), (d * 0.55, hb * 0.6), (d * 0.3, hb)], M(scale=(w / d / 1.0, 1, 1)), mat="grip" if e != "Primal" else "hide", segs=8)
            else:
                blk(p, 0, 0, 0, w, d, hb, mat="body" if e != "Industrial" else "paint")
    elif slot == "lid":
        if g == "Ocean":
            if tier(e) == "hand":
                for i in range(4):
                    p.cyl(w / 9 * 1.05, w / 9 * 0.9, hl * 0.5, T(((i - 1.5) * w / 4, 0, hb)), mat="rattan", segs=6, bevel=0)
            else:
                p.box((w * 1.02, d * 1.02, hl * 0.6), T((0, 0, hb + hl * 0.3)), mat="fit", bevel=0.2)
            horn(p, 0, 0, hb + hl * 0.5, hl, 1, mat="accent")
        elif g == "Gale":
            p.cyl(d * 0.32, d * 0.2, hl * 0.8, T((0, 0, hb)), mat="wood" if tier(e) == "hand" else "fit", segs=6, bevel=0)
        elif g == "Radiant":
            dome(p, d * 0.45, hb, M(scale=(w / d * 0.9, 1, 1)), mat="fit", segs=8)
        else:
            if tier(e) == "hand":
                p.cyl(d * 0.28, d * 0.28, w * 1.02, M(loc=(-w * 0.51, 0, hb), rot=(0, 90, 0)), mat="metal" if e != "Primal" else "bone", segs=6, bevel=0)
            elif e == "Industrial":
                steps(p, w, d, hb, 2, hl * 0.5, mat="fit", shrink=0.9)
            else:
                blk(p, 0, 0, hb, w * 1.02, d * 1.02, hl * 0.7, mat="fit")
    elif slot == "handle":
        if g == "Gale":
            p.tube([(-d * 0.35, 0, hb * 0.9), (0, 0, hb * 2.2), (d * 0.35, 0, hb * 0.9)], 0.005, mat="grip", segs=4)
        elif g == "Metropolis" and tier(e) == "hand":
            bail(p, w * 0.15, hb + d * 0.28, J(p, 0.05, 0.2), 0.008, mat="grip", segs=4)
        else:
            bail(p, w * 0.18, hb + hl * 0.6, J(p, 0.05, 0.2), 0.007, mat="grip", segs=4)
    else:  # the healer's sign on the front
        z = hb * 0.55
        if g == "Ocean":  # leaf
            p.plate([(-0.03, 0), (0, 0.02), (0.03, 0), (0, -0.02)], 0.005, T((0, -d * 0.53, z)), mat="accent", bevel=0)
        elif g == "Gale":
            for i in range(5):
                a = -math.pi / 2 + (i - 2) * 0.35
                p.ball(0.009, T((math.cos(a) * d * 0.62, math.sin(a) * d * 0.62, hb * 0.45)), mat="accent", segs=(4, 3))
        elif g == "Radiant":
            petals(p, 0.018, 0, 6, 0.01, M(loc=(0, -d * 0.52, z), rot=(90, 0, 0)), mat="accent", tilt=0)
        else:
            sign = "glow" if tier(e) == "high" else "paint" if e != "Primal" else "bone"
            p.box((0.05, 0.006, 0.015), T((0, -d * 0.51, z)), mat=sign, bevel=0)
            p.box((0.015, 0.006, 0.05), T((0, -d * 0.51, z)), mat=sign, bevel=0)
        mark(p, d * 0.3, hb * 0.2, M(loc=(w * 0.3, 0, 0)))


# ================================================================ Mortar (carried; handle is the pestle)


def mortar(p, slot):
    e, g = p.era, p.region
    h, r = F(p, 0.11, 0.12), F(p, 0.1, 0.1)
    if g == "Ocean":  # cobek: wide shallow stone dish, curved uleg
        outer = [(r * 0.9, 0), (r * 1.25, h * 0.4), (r * 1.3, h * 0.55)]
        fl = h * 0.25
    elif g == "Gale":  # hourglass wooden mortar
        outer = [(r * 0.85, 0), (r * 0.55, h * 0.4), (r * 0.8, h * 0.8), (r * 0.9, h)]
        fl = h * 0.5
    elif g == "Radiant":  # khal on a lotus foot
        outer = [(r * 0.6, 0), (r * 0.5, h * 0.2), (r * 0.95, h * 0.55), (r * 1.05, h)]
        fl = h * 0.45
    else:  # apothecary mortar with a spout lip
        outer = [(r * 0.7, 0), (r * 0.75, h * 0.15), (r * 0.95, h * 0.5), (r, h)]
        fl = h * 0.4
    top = outer[-1]
    if slot == "body":
        mat = {"Ocean": pick(p, "stone", "metal"), "Gale": pick(p, "wood" if e != "Mercantile" else "wood_dark", "body"),
               "Radiant": pick(p, "stone" if e == "Primal" else "brass", "fit", "body"), "Metropolis": pick(p, "stone" if e != "Mercantile" else "ceramic", "body")}[g]
        shell(p, outer, 0.02, mat=mat, segs=10, floor=fl, noise=0.04 if e == "Primal" else None)
    elif slot == "lid":  # rim and what is being ground
        rim(p, top[0] * 1.0, top[1], mat="fit" if g != "Ocean" else "body", t=0.006)
        p.ball(top[0] * 0.55, M(loc=(0, 0, fl + 0.004), scale=(1, 1, 0.15)), mat=("accent", "cloth", "paint", "bark")[REGIONS.index(g)] if tier(e) != "high" else "glow", segs=(6, 3))
    elif slot == "handle":
        L = J(p, {"Gale": 0.32}.get(g, 0.2), 0.1)
        base = M(loc=(0, 0, fl), rot=(J(p, 22, 0.3), 0, 25))
        if g == "Ocean":  # uleg: curved stone pestle
            p.tube([tuple(base @ Vector(v)) for v in ((0, 0, 0), (0.03, 0, L * 0.5), (0.02, 0, L))], 0.016, mat="stone" if tier(e) == "hand" else "metal", segs=5)
        elif g == "Gale":
            p.lathe([(0, 0), (0.018, 0.01), (0.012, L * 0.4), (0.012, L * 0.6), (0.018, L - 0.01), (0, L)], base, mat="wood" if tier(e) == "hand" else "fit", segs=6)
        elif g == "Radiant":
            p.lathe([(0, 0), (0.018, 0.01), (0.012, L * 0.5), (0.016, L - 0.01), (0, L)], base, mat="fit", segs=6)
            petals(p, 0.01, L - 0.005, 4, 0.008, base, mat="accent", tilt=40)
        else:
            p.lathe([(0, 0), (0.02, 0.01), (0.012, L * 0.4), (0.01, L * 0.8), (0.016, L - 0.01), (0, L)], base, mat="grip" if tier(e) != "hand" else "wood", segs=6)
    else:
        if g == "Radiant":
            petals(p, r * 0.45, 0, 5, r * 0.15, mat="accent", tilt=60)
        elif g == "Gale":
            zig(p, rad_at(outer, h * 0.8), h * 0.78, 0.025, 8)
        elif g == "Metropolis" and e == "Industrial":
            steps(p, r * 1.6, r * 1.6, 0, 2, 0.01, mat="fit", shrink=0.85)
        else:
            signature(p, rad_at(outer, h * 0.2), h * 0.15, 0.03)
        mark(p, rad_at(outer, h * 0.6), h * 0.6)


# ================================================================ Creel (carried; fish basket)


def creel(p, slot):
    e, g = p.era, p.region
    h, r = F(p, 0.28, 0.1), F(p, 0.13, 0.1)
    neck = r * F(p, 0.5, 0.1)
    boxy = g == "Metropolis" or (g == "Radiant" and tier(e) == "high")
    if g == "Ocean":  # bamboo bottle basket, flared mouth
        outer = [(r * 0.8, 0), (r * 1.05, h * 0.3), (r * 0.95, h * 0.6), (neck, h * 0.85), (neck * 1.5, h)]
    elif g == "Gale":  # calabash with a cut mouth
        outer = [(r * 0.55, 0), (r * 1.05, h * 0.35), (r * 0.75, h * 0.7), (neck * 0.9, h * 0.9), (neck, h)]
    else:  # wide-mouthed rope basket
        outer = [(r * 0.75, 0), (r * 1.0, h * 0.6), (r * 0.95, h * 0.85)]
    W, D, hb = r * 2.2, r * 1.3, h * 0.85
    if slot == "body":
        if boxy:
            blk(p, 0, 0, 0, W, D, hb, mat=pick(p, "bark" if e != "Primal" else "rope", "body"), b=0.2)
        else:
            mat = {"Ocean": pick(p, "bamboo", "metal"), "Gale": pick(p, "gourd", "body"), "Radiant": pick(p, "rope", "metal")}[g]
            shell(p, outer, 0.007, mat=mat, segs=10)
    elif slot == "lid":
        if boxy:
            p.box((W * 1.03, D * 1.03, 0.02), T((0, 0, hb + 0.01)), mat="fit" if tier(e) != "hand" else "bark", bevel=0.2)
            p.cyl(D * 0.2, D * 0.2, 0.004, T((W * 0.2, 0, hb + 0.02)), mat="glow" if tier(e) == "high" else "metal", segs=8, bevel=0)
        elif g == "Gale":
            p.cyl(neck * 0.95, neck * 0.95, 0.03, T((0, 0, h)), mat="wood" if tier(e) == "hand" else "fit", segs=6, bevel=0)
        else:
            rim(p, outer[-1][0] * 1.02, h, mat="fit", t=0.008)
    elif slot == "handle":
        if boxy:
            p.tube([(-W * 0.5, 0, hb * 0.9), (0, -D * 0.1, hb * 2.0), (W * 0.5, 0, hb * 0.9)], 0.008, mat="grip", segs=4)
        elif g == "Ocean":
            for s in (-1, 1):
                horn(p, s * neck * 1.4, 0, h * 0.93, r * 0.25, s, mat="fit")
            p.tube([(neck, 0, h * 0.85), (r * 1.1, 0, h * 1.1), (r * 1.5, 0.02, h * 0.95)], 0.005, mat="grip", segs=4)
        else:
            bail(p, neck * 1.05 if g == "Gale" else outer[-1][0], h * 0.9, h * J(p, 0.5, 0.15), 0.005, mat="grip", segs=4)
    else:
        if boxy:
            for x in (-0.3, 0.3):
                p.box((0.012, D * 1.02, hb * 0.9), T((x * W, 0, hb * 0.5)), mat="fit" if e not in ("Industrial",) else "paint", bevel=0)
        elif g == "Ocean":
            lash(p, rad_at(outer, h * 0.3), h * 0.3, 0.04, segs=8)
        elif g == "Gale":
            zig(p, rad_at(outer, h * 0.35), h * 0.35, 0.04, 8)
        else:
            petals(p, rad_at(outer, h * 0.2) * 1.02, h * 0.15, 5, 0.018, mat="accent", tilt=75)
        mark(p, r * 0.6, h * 0.45, M(loc=(0, -r * 0.4, 0)))


# ================================================================ Bell (carried; lid is the crown)


def bell(p, slot):
    e, g = p.era, p.region
    h, r = F(p, 0.18, 0.12), F(p, 0.08, 0.1)
    mat = pick(p, "brass" if e != "Primal" else "wood", "metal", "fit") if g != "Ocean" else pick(p, "bamboo" if e == "Primal" else "brass", "metal", "fit")
    if slot == "body":
        if g == "Gale":  # gankogui: two bells on one forked iron
            for s, k in ((-1, 1.0), (1, 0.75)):
                bell_shape(p, r * 0.7 * k, h * 0.6 * k, 0.005, mat=pick(p, "iron", "metal"), segs=8, waist=0.7,
                           m=M(loc=(s * r * 0.8, 0, h * 0.5), rot=(0, 180 + s * 20, 0)))
        elif g == "Ocean" and e == "Primal":  # bamboo tube chime
            p.cyl(r * 0.6, r * 0.6, h, mat="bamboo", segs=7, bevel=0)
            p.box((r * 0.2, 0.01, h * 0.6), T((0, -r * 0.58, h * 0.5)), mat="bark", bevel=0)
        else:
            waist = {"Ocean": 0.75, "Radiant": 0.6, "Metropolis": 0.62}[g]
            bell_shape(p, r * (1.15 if g == "Ocean" else 1.0), h * (0.75 if g == "Radiant" else 1.0), 0.006, mat=mat, segs=10, waist=waist)
    elif slot == "lid":  # crown
        if g == "Gale":
            p.tube([(-r * 0.8, 0, h * 0.5), (-r * 0.3, 0, h * 0.2), (0, 0, h * 0.05), (r * 0.3, 0, h * 0.2), (r * 0.8, 0, h * 0.5)], 0.006, mat=pick(p, "iron", "metal"), segs=4)
        elif g == "Ocean":  # pagoda-tier crown
            z = h if e != "Primal" else h
            for i in range(2):
                p.cyl(r * (0.45 - i * 0.15), r * (0.3 - i * 0.12), h * 0.08, T((0, 0, z + i * h * 0.08)), mat=mat, segs=8, bevel=0)
        elif g == "Radiant":
            dome(p, r * 0.42, h * 0.75, mat="fit", finial=False, segs=8)
        else:
            if e == "Industrial":
                steps(p, r * 0.8, r * 0.8, h, 2, h * 0.05, mat="fit", shrink=0.7)
            else:
                p.cyl(r * 0.45, r * 0.35, h * 0.06, T((0, 0, h)), mat=mat, segs=8, bevel=0)
    elif slot == "handle":
        if g == "Gale":  # the beater stick lying alongside
            p.lathe([(0, 0), (0.008, 0.01), (0.007, h * 1.4), (0, h * 1.45)], M(loc=(0, -r * 0.4, 0), rot=(0, 90, 0)), mat="wood", segs=5)
            p.cyl(0.01, 0.01, h * 0.5, T((0, 0, -0.0)), mat="grip", segs=5, bevel=0)
        elif g == "Ocean":  # rope hanger with horn tips
            p.ring(0.022, 0.004, M(loc=(0, 0, h * 1.25), rot=(90, 0, 0)), mat="grip", segs=8, square=False)
            for s in (-1, 1):
                horn(p, s * r * 0.4, 0, h * 1.12, r * 0.4, s, mat="accent")
        elif g == "Radiant":  # ghanta: tall handle with a lotus knop
            zb = h * 0.75
            p.lathe([(0.012, zb), (0.01, zb + h * 0.4), (0.016, zb + h * 0.45), (0.01, zb + h * 0.7)], mat="fit", segs=6)
            petals(p, 0.012, zb + h * 0.7, 5, 0.012, mat="accent", tilt=40)
        else:
            p.lathe([(0.014, h), (0.012, h + h * 0.35), (0.02, h + h * 0.6), (0, h + h * 0.65)], mat="grip" if tier(e) != "hand" else "wood", segs=6)
    else:  # clapper and trim
        if g == "Gale":
            zig(p, r * 0.5, h * 0.35, 0.02, 6, M(loc=(-r * 0.8, 0, 0)))
        else:
            hh = h * (0.75 if g == "Radiant" else 1.0)
            p.ball(r * 0.15, T((0, 0, hh * 0.08)), mat=pick(p, "iron", "metal", "glow"), segs=(5, 3))
            if g == "Radiant":
                p.ring(r * 0.98, 0.004, T((0, 0, hh * 0.12)), mat="accent", segs=10)
            elif g == "Metropolis" and e == "Future":
                p.ring(r * 0.98, 0.004, T((0, 0, hh * 0.12)), mat="glow", segs=10)
            else:
                rim(p, r * 1.05 if g != "Ocean" else r * 1.2, hh * 0.05, mat="fit", t=0.004)
        mark(p, r * 0.7, h * 0.45)


# ================================================================ SewingKit (carried)


def sewing_kit(p, slot):
    e, g = p.era, p.region
    W, D, H = F(p, 0.2, 0.1), F(p, 0.13, 0.1), F(p, 0.08, 0.12)
    round_ = g in ("Ocean", "Radiant")
    R = (W + D) / 4
    if slot == "body":
        if g == "Ocean":  # round rattan sewing basket
            shell(p, [(R * 0.9, 0), (R, H)], 0.006, mat=pick(p, "rattan", "body"), segs=10)
        elif g == "Radiant":  # brass paandan-like round box
            p.lathe([(R * 0.8, 0), (R * 1.0, H * 0.15), (R, H)], mat=pick(p, "brass", "fit", "body"), segs=10)
        elif g == "Gale":  # beaded leather pouch
            closed(p, [(D * 0.45, 0), (D * 0.6, H * 0.6), (D * 0.35, H * 1.3)], mat=pick(p, "leather" if e != "Primal" else "hide", "body"), segs=8,
                   m=M(scale=(W / D, 1, 1)))
        else:
            blk(p, 0, 0, 0, W, D, H, mat="body" if tier(e) != "hand" else "wood")
    elif slot == "lid":
        if g == "Ocean":
            p.lathe([(R * 1.05, H), (R * 0.6, H + H * 0.3), (0, H + H * 0.35)], mat=pick(p, "rattan", "fit", "glass"), segs=10)
            horn(p, 0, 0, H * 1.3, H * 0.4, 1, mat="accent")
        elif g == "Radiant":
            dome(p, R * 0.95, H, mat="fit", segs=10)
        elif g == "Gale":
            p.ring(D * 0.36, 0.006, M(loc=(0, 0, H * 1.2), scale=(W / D, 1, 1)), mat="grip", segs=8, square=False)
        else:
            if e == "Industrial":
                steps(p, W, D, H, 2, H * 0.12, mat="fit", shrink=0.85)
            else:
                blk(p, 0, 0, H, W * 1.03, D * 1.03, H * 0.2, mat="fit" if tier(e) != "hand" else "wood_dark")
    elif slot == "handle":  # spools and needles
        z = H + (H * 0.35 if g == "Ocean" else H * 0.6 if g == "Radiant" else H * 0.2)
        if g == "Gale":
            spool(p, W * 0.55, 0, 0, 0.012, 0.025, thread="accent", end="wood" if tier(e) == "hand" else "fit")
        else:
            spool(p, -W * 0.15 if not round_ else -R * 0.3, 0, z, 0.01, 0.022, thread="accent", end="wood" if tier(e) == "hand" else "fit")
        rod(p, (W * 0.1, -D * 0.1, z), (W * 0.2, -D * 0.1, z + 0.05), 0.0015, 0.0006, mat="metal" if tier(e) != "hand" else "bone", segs=3)
    else:
        if g == "Gale":
            for i in range(7):
                a = -math.pi / 2 + (i - 3) * 0.28
                p.ball(0.006, T((math.cos(a) * D * 0.6 * W / D * 0.75, math.sin(a) * D * 0.6, H * 0.6)), mat=("accent", "fit")[i % 2], segs=(4, 3))
        elif g == "Ocean":
            lash(p, R, H * 0.5, 0.03)
        elif g == "Radiant":
            petals(p, R * 0.95, H * 0.3, 6, 0.01, mat="accent", tilt=80)
        else:
            p.box((W * 0.3, 0.006, H * 0.3), T((0, -D * 0.505, H * 0.5)), mat="accent", bevel=0)
        mark(p, R * 0.5, H * 0.5, M(loc=(0, -R * 0.5, 0)))


# ================================================================ AlchemySet (carried)


def alchemy_set(p, slot):
    e, g = p.era, p.region
    R, H = F(p, 0.1, 0.1), F(p, 0.16, 0.1)
    if slot == "body":  # the main vessel over its fire
        if g == "Ocean":  # bamboo still: tube on a clay stove
            p.cyl(R * 0.7, R * 0.8, H * 0.25, mat=pick(p, "clay", "metal"), segs=8, bevel=0)
            p.cyl(R * 0.4, R * 0.4, H * 0.8, T((0, 0, H * 0.25)), mat=pick(p, "bamboo", "body", "glass"), segs=7, bevel=0)
        elif g == "Gale":  # gourd flask on a clay brazier
            p.cyl(R * 0.6, R * 0.75, H * 0.25, mat=pick(p, "clay", "metal"), segs=7, bevel=0)
            closed(p, [(R * 0.3, H * 0.25), (R * 0.7, H * 0.45), (R * 0.3, H * 0.7), (R * 0.45, H * 0.85), (R * 0.15, H)], mat=pick(p, "gourd", "glass", "body"), segs=8)
        elif g == "Radiant":  # copper kalash on a lotus stand
            petals(p, R * 0.5, 0, 6, R * 0.18, mat="accent", tilt=60)
            closed(p, [(R * 0.3, H * 0.15), (R * 0.75, H * 0.45), (R * 0.35, H * 0.8), (R * 0.45, H * 0.9)], mat=pick(p, "copper", "fit", "body"), segs=10)
        else:
            if tier(e) == "high":
                p.cyl(R * 0.7, R * 0.7, H * 0.2, mat="body", segs=10, bevel=0.2)
                closed(p, [(R * 0.4, H * 0.2), (R * 0.55, H * 0.5), (R * 0.2, H * 0.8)], mat="glass", segs=8)
            else:
                flask(p, 0, 0, H * 0.18, R * 0.55, H * 0.75, mat="glass", segs=8)
                for i in range(3):
                    a = i * math.tau / 3
                    rod(p, (math.cos(a) * R * 0.5, math.sin(a) * R * 0.5, 0), (math.cos(a) * R * 0.35, math.sin(a) * R * 0.35, H * 0.2), 0.004, mat="metal", segs=4)
    elif slot == "lid":  # head of the still
        if g == "Ocean":
            p.cyl(R * 0.45, R * 0.3, H * 0.12, T((0, 0, H * 1.05)), mat=pick(p, "rattan", "fit"), segs=7, bevel=0)
            rod(p, (0, 0, H * 1.1), (R * 1.3, 0, H * 0.7), 0.006, mat=pick(p, "bamboo", "metal", "fit"), segs=5)
        elif g == "Gale":
            p.cyl(R * 0.17, R * 0.12, H * 0.08, T((0, 0, H)), mat="wood" if tier(e) == "hand" else "fit", segs=5, bevel=0)
        elif g == "Radiant":
            dome(p, R * 0.45, H * 0.9, mat="fit", segs=8)
        else:
            rod(p, (0, 0, H * 0.93 if tier(e) != "high" else H * 0.8), (R * 1.4, 0, H * 0.55), 0.005, mat="glass" if tier(e) == "hand" else "metal", segs=5)
    elif slot == "handle":  # receiver beside the main vessel
        x = -R * 1.3
        if g == "Ocean":
            p.ball(R * 0.35, M(loc=(R * 1.3, 0, R * 0.3), scale=(1, 1, 0.9)), mat=pick(p, "bark", "glass"), segs=(6, 4))
        elif g == "Gale":
            for i in range(2):
                closed(p, [(R * 0.15, 0), (R * 0.3, H * 0.2), (R * 0.1, H * 0.4)], mat=pick(p, "gourd", "glass", "body"), segs=6, m=T((x, (i - 0.5) * R * 0.8, 0)))
        elif g == "Radiant":  # long ladle
            p.tube([(R * 0.3, -R * 0.4, H * 0.8), (R * 1.2, -R * 0.8, H * 0.3), (R * 1.4, -R * 0.9, 0.01)], 0.004, mat="fit", segs=4)
            bowl(p, R * 0.2, R * 0.12, (R * 1.4, -R * 0.9, 0), mat="fit", segs=6)
        else:
            p.cyl(R * 0.25, R * 0.25, H * 0.5, T((R * 1.4, 0, 0)), mat="glass", segs=7, bevel=0)
            if tier(e) == "machine":  # burner
                p.cyl(R * 0.12, R * 0.15, H * 0.15, T((0, 0, 0)), mat="metal", segs=6, bevel=0)
    else:
        if g == "Ocean":
            lash(p, R * 0.4, H * 0.6, 0.03, segs=7)
        elif g == "Gale":
            zig(p, R * 0.68, H * 0.12, 0.03, 6)
        elif g == "Radiant":
            p.ring(R * 0.7, 0.004, T((0, 0, H * 0.45)), mat="accent", segs=10)
        else:
            rack_n = 3
            for i in range(rack_n):
                p.cyl(0.008, 0.008, H * 0.4, T((-R * 1.2 + i * 0.022, R * 0.5, 0)), mat="glass", segs=5, bevel=0)
            blk(p, -R * 1.2 + 0.022, R * 0.5, H * 0.2, 0.08, 0.02, 0.008, mat="body" if tier(e) != "hand" else "wood")
        mark(p, R * 0.5, H * 0.35)


# ================================================================ Quiver (carried)


def quiver(p, slot):
    e, g = p.era, p.region
    H, r = F(p, 0.55, 0.08), F(p, 0.055, 0.1)
    if slot == "body":
        if g == "Ocean":  # bamboo tube
            p.cyl(r, r, H, mat=pick(p, "bamboo", "body"), segs=7, bevel=0)
            for z in (0.33, 0.66):
                p.ring(r * 1.04, 0.004, T((0, 0, H * z)), mat="body" if tier(e) != "hand" else "bamboo", segs=7)
        elif g == "Gale":  # bark tube widening to a leather mouth
            p.cyl(r * 0.85, r * 1.05, H, mat=pick(p, "bark", "body"), segs=7, bevel=0)
        elif g == "Radiant":  # cloth-covered with brass end caps
            p.lathe([(r * 0.7, 0), (r, H * 0.1), (r, H * 0.9), (r * 1.1, H)], mat=pick(p, "cloth", "body"), segs=8)
        else:
            if tier(e) == "hand":
                p.lathe([(r * 0.8, 0), (r * 1.05, H * 0.5), (r * 1.1, H)], M(scale=(1, 0.7, 1)), mat="grip" if e != "Primal" else "hide", segs=8)
            else:
                p.cyl(r, r, H, mat="body", segs=8, bevel=0)
    elif slot == "lid":  # what sticks out of the mouth
        hi = tier(e) == "high"
        n = 3 if g == "Ocean" else 4
        for i in range(n):
            a = i * math.tau / n + 0.4
            x, y = math.cos(a) * r * 0.45, math.sin(a) * r * 0.45
            if g == "Ocean" and not hi:  # blowgun darts with kapok puffs
                rod(p, (x, y, H * 0.8), (x * 1.2, y * 1.2, H + 0.12), 0.0025, mat="bamboo", segs=3)
                p.ball(0.008, T((x * 1.2, y * 1.2, H + 0.12)), mat="cloth", segs=(4, 3))
            elif hi:
                p.cyl(0.004, 0.004, 0.14, T((x, y, H * 0.85)), mat="glow", segs=4, bevel=0)
            else:
                arrow(p, x, y, H * 0.7, 0.42, rot=(J(p, 6, 0.8), J(p, 6, 0.8), 0), fletch="feather" if g != "Metropolis" or e != "Industrial" else "paint")
    elif slot == "handle":  # strap
        p.tube([(0, r, H * 0.85), (0, r * 2.4, H * 0.5), (0, r, H * 0.12)], 0.007, mat="grip", segs=4)
        if g == "Metropolis" and tier(e) == "machine":
            p.box((r * 1.2, 0.01, 0.03), T((0, r * 1.1, H * 0.5)), mat="metal", bevel=0)
    else:
        if g == "Ocean":
            lash(p, r, H * 0.92, 0.03, segs=7)
            horn(p, 0, -r * 0.9, H * 0.05, r * 0.6, 1, mat="accent")
        elif g == "Gale":
            p.cyl(r * 1.15, r * 0.9, H * 0.05, T((0, 0, H * 0.95)), mat="grip", segs=7, bevel=0)
            zig(p, r * 0.95, H * 0.5, 0.04, 6)
        elif g == "Radiant":
            for z in (0.0, H * 0.92):
                p.cyl(r * 1.08, r * 1.08, H * 0.08, T((0, 0, z)), mat="fit", segs=8, bevel=0)
            petals(p, r * 0.9, H * 0.45, 4, 0.014, mat="accent", tilt=80)
        else:
            if e in ("Industrial", "Future", "Ancient"):
                fins(p, r, H * 0.1, H * 0.6, 3, mat="fit")
            else:
                for z in (0.2, 0.8):
                    p.ring(r * 1.02, 0.004, T((0, 0, H * z)), mat="metal", segs=8)
        mark(p, r, H * 0.3)


# ================================================================ Teaset (scene)


def teaset(p, slot):
    e, g = p.era, p.region
    R, H = F(p, 0.08, 0.1), F(p, 0.14, 0.1)
    tray = F(p, 0.38, 0.06)
    if g == "Gale":  # tall teapot (berrad) with a long spout and tea glasses
        prof_ = [(R * 0.6, 0), (R * 0.9, H * 0.25), (R * 0.6, H * 0.55), (R * 0.45, H * 0.8), (R * 0.5, H)]
    elif g == "Radiant":  # chai kettle: squat belly, narrow neck
        prof_ = [(R * 0.7, 0), (R * 1.1, H * 0.3), (R * 0.8, H * 0.55), (R * 0.4, H * 0.65)]
    elif g == "Ocean":  # round clay teapot
        prof_ = [(R * 0.6, 0), (R * 1.0, H * 0.3), (R * 0.85, H * 0.55), (R * 0.45, H * 0.65)]
    else:
        prof_ = {"hand": [(R * 0.6, 0), (R * 0.95, H * 0.35), (R * 0.85, H * 0.65), (R * 0.45, H * 0.75)],
                 "machine": [(R * 0.9, 0), (R, H * 0.1), (R * 0.85, H * 0.6), (R * 0.45, H * 0.75)],
                 "high": [(R * 0.8, 0), (R * 0.85, H * 0.7), (R * 0.6, H * 0.8)]}[tier(e)]
    top = prof_[-1]
    pmat = {"Ocean": pick(p, "clay" if e != "Mercantile" else "glaze", "body"), "Gale": pick(p, "clay" if e == "Primal" else "brass", "metal", "fit"),
            "Radiant": pick(p, "clay" if e == "Primal" else "copper", "fit"), "Metropolis": pick(p, "ceramic" if e != "Mercantile" else "glaze", "body")}[g]
    if slot == "body":
        closed(p, prof_, mat=pmat, segs=10)
    elif slot == "lid":
        if g == "Gale":
            p.cyl(top[0] * 0.9, 0.0, H * 0.3, T((0, 0, top[1])), mat=pmat, segs=8, bevel=0)
            p.ball(0.008, T((0, 0, top[1] + H * 0.3)), mat="accent", segs=(4, 3))
        elif g == "Radiant":
            dome(p, top[0] * 1.0, top[1], mat="fit", segs=8)
        else:
            p.lathe([(top[0] * 1.05, top[1]), (top[0] * 0.8, top[1] + H * 0.06), (top[0] * 0.2, top[1] + H * 0.09), (0, top[1] + H * 0.12)], mat=pmat, segs=10)
            if g == "Ocean":
                horn(p, 0, 0, top[1] + H * 0.08, H * 0.12, 1, mat="accent")
            elif e == "Future":
                p.ring(top[0] * 0.9, 0.003, T((0, 0, top[1] + 0.004)), mat="glow", segs=10)
    elif slot == "handle":  # spout and grip
        if g == "Gale":
            rod(p, (R * 0.7, 0, H * 0.2), (R * 1.9, 0, H * 0.75), R * 0.12, R * 0.05, mat=pmat, segs=5)
            p.tube([(-R * 0.55, 0, H * 0.75), (-R * 1.1, 0, H * 0.7), (-R * 1.1, 0, H * 0.35), (-R * 0.8, 0, H * 0.25)], 0.006, mat=pmat, segs=4)
        elif g == "Ocean":  # rattan-wrapped bail over the top
            bail(p, top[0] * 1.6, H * 0.55, H * 0.45, 0.006, mat="grip", segs=4)
            rod(p, (R * 0.9, 0, H * 0.3), (R * 1.5, 0, H * 0.55), R * 0.14, R * 0.06, mat=pmat, segs=5)
        else:
            rod(p, (R * 0.95, 0, H * 0.3), (R * 1.6, 0, H * 0.6), R * 0.15, R * 0.06, mat=pmat, segs=5)
            p.tube([(-R * 0.9, 0, H * 0.55), (-R * 1.35, 0, H * 0.5), (-R * 1.3, 0, H * 0.2), (-R * 0.95, 0, H * 0.15)], 0.007, mat=pmat if g != "Radiant" else "grip", segs=4)
    else:  # tray and cups
        if g == "Ocean":  # bamboo mat
            for i in range(5):
                p.cyl(0.008, 0.008, tray, M(loc=(-tray / 2, (i - 2) * 0.03 - tray * 0.15, 0.004), rot=(0, 90, 0)), mat=pick(p, "bamboo", "fit"), segs=4, bevel=0)
            cups = [(tray * 0.3, -tray * 0.2), (-tray * 0.3, -tray * 0.2), (0, -tray * 0.35)]
            for x, y in cups:
                bowl(p, R * 0.35, R * 0.35, (x, y, 0.008), mat=pmat, segs=8)
        elif g == "Gale":  # round brass tray, tall glasses
            p.lathe([(0, 0), (tray * 0.5, 0), (tray * 0.52, 0.015), (0, 0.008)], mat="fit" if tier(e) != "hand" else "brass", segs=12)
            for x, y in ((tray * 0.3, -tray * 0.1), (-tray * 0.3, -tray * 0.1), (0, -tray * 0.3)):
                p.cyl(R * 0.25, R * 0.3, R * 0.9, T((x, y, 0.012)), mat="glass", segs=7, bevel=0)
                zig(p, R * 0.3, R * 0.6, 0.01, 4, T((x, y, 0.012)))
        elif g == "Radiant":  # kulhad clay cups on a wire carrier
            for x, y in ((tray * 0.25, -tray * 0.15), (-tray * 0.25, -tray * 0.15), (0, -tray * 0.32)):
                shell(p, [(R * 0.22, 0), (R * 0.32, R * 0.7)], 0.003, m=T((x, y, 0)), mat="clay" if tier(e) != "high" else "fit", segs=7)
            p.ring(tray * 0.3, 0.003, T((0, -tray * 0.2, R * 0.5)), mat="metal", segs=8, square=False)
            petals(p, R * 0.75, 0, 5, 0.015, mat="accent", tilt=70)
        else:
            p.lathe([(0, 0), (tray * 0.5, 0), (tray * 0.52, 0.012), (0, 0.006)], mat="fit" if tier(e) != "hand" else "wood_dark", segs=12)
            for x, y in ((tray * 0.3, -tray * 0.15), (-tray * 0.3, -tray * 0.15)):
                cup(p, R * 0.4, R * 0.55, (x, y, 0.012), mat=pmat, handle=True)
            if e == "Industrial":
                steps(p, tray * 0.2, tray * 0.2, 0.012, 2, 0.008, M(loc=(0, tray * 0.25, 0)), mat="fit", shrink=0.7)
        mark(p, R * 0.7, H * 0.25)


# ================================================================ Tableware (scene)


def tableware(p, slot):
    e, g = p.era, p.region
    R = F(p, 0.12, 0.1)
    W = F(p, 0.42, 0.06)
    dish = {"Ocean": pick(p, "cloth" if e == "Primal" else "glaze" if e == "Mercantile" else "wood", "body"),
            "Gale": pick(p, "clay", "body"), "Radiant": pick(p, "brass" if e != "Primal" else "cloth", "fit", "body"),
            "Metropolis": pick(p, "wood" if e == "Primal" else "glaze" if e == "Mercantile" else "ceramic", "body")}[g]
    if slot == "body":
        if g == "Ocean":  # round tray (tampah) with a leaf liner
            rr = R * J(p, 1.5, 0.08)
            p.lathe([(0, 0), (rr * 0.93, 0), (rr, 0.02), (rr * 0.95, 0.02), (0, 0.008)], mat=pick(p, "rattan", "fit"), segs=12)
        elif g == "Gale":  # tagine base: wide shallow dish
            p.lathe([(0, 0), (R * 1.0, 0.0), (R * 1.25, 0.03), (R * 1.2, 0.035), (0, 0.015)], mat=dish, segs=12)
        elif g == "Radiant":  # thali
            plate(p, R * 1.3, (0, 0, 0), mat=dish, segs=12, h=0.015)
        else:
            plate(p, R, (0, 0, 0), mat=dish)
            plate(p, R * 0.75, (0, 0, 0.012), mat=dish)
    elif slot == "lid":
        if g == "Ocean":  # tumpeng: cone of rice
            p.cyl(R * 0.55, 0.01, R * 1.1, T((0, 0, 0.01)), mat="bone" if tier(e) != "high" else "fit", segs=8, bevel=0)
        elif g == "Gale":  # tagine cone
            p.lathe([(R * 1.15, 0.03), (R * 0.5, R * 0.6), (R * 0.15, R * 1.2), (R * 0.2, R * 1.3), (0, R * 1.35)], mat=dish, segs=10)
        elif g == "Radiant":  # katoris on the thali
            for i in range(4):
                a = i * math.tau / 4 + 0.4
                bowl(p, R * 0.25, R * 0.18, (math.cos(a) * R * 0.85, math.sin(a) * R * 0.85, 0.008), mat=dish, segs=8)
        else:
            if tier(e) == "high" or e == "Steampunk":  # cloche
                p.lathe([(R * 0.75, 0.02), (R * 0.65, R * 0.4), (R * 0.2, R * 0.6), (0, R * 0.62)], mat="fit" if e == "Future" else "brass", segs=10)
            else:
                bowl(p, R * 0.45, R * 0.35, (0, 0, 0.018), mat=dish, segs=10)
    elif slot == "handle":  # utensils
        if g == "Ocean":
            for s in (-1, 1):
                horn(p, s * R * 1.45, 0, 0.015, R * 0.25, s, mat="accent")
        elif g == "Gale":
            p.ball(0.01, T((0, 0, R * 1.37)), mat="accent", segs=(4, 3))
            rod(p, (R * 1.2, -R * 0.9, 0.006), (R * 1.6, -R * 0.4, 0.008), 0.004, mat="wood" if tier(e) == "hand" else "metal", segs=4)
        elif g == "Radiant":
            rod(p, (R * 1.35, -R * 0.6, 0.006), (R * 1.5, R * 0.1, 0.008), 0.004, mat="fit", segs=4)
            p.ball(0.012, M(loc=(R * 1.35, -R * 0.6, 0.008), scale=(1, 1.4, 0.4)), mat="fit", segs=(5, 3))
        else:
            for s in (-1, 1):
                p.box((0.012, J(p, 0.17, 0.08), 0.004), T((s * (R + 0.03), 0, 0.004)), mat="metal" if tier(e) != "high" else "fit", bevel=0)
    else:  # companions and trims
        if g == "Ocean":
            for i in range(4):
                a = i * math.tau / 4 + 0.8
                p.ball(R * 0.15, M(loc=(math.cos(a) * R * 0.95, math.sin(a) * R * 0.95, 0.025), scale=(1, 1, 0.5)), mat=("accent", "paint", "cloth", "bark")[i], segs=(5, 3))
        elif g == "Gale":
            zig(p, R * 1.0, R * 0.55, 0.03, 8)
        elif g == "Radiant":
            p.ring(R * 1.28, 0.004, T((0, 0, 0.014)), mat="accent", segs=12)
            cup(p, R * 0.25, R * 0.45, (R * 1.6, R * 0.6, 0), mat=dish)
        else:
            if e == "Industrial":
                steps(p, W * 0.25, W * 0.15, 0, 2, 0.006, M(loc=(W * 0.4, 0, 0)), mat="fit", shrink=0.7)
            cup(p, 0.03, 0.06, (R + 0.07, R * 0.4, 0), mat=dish, handle=True)
        mark(p, R * 0.5, 0.03, M(loc=(-W * 0.4, 0, 0)))


for _g in REGIONS:
    regional("Bucket", _g)(bucket)
    regional("Basket", _g)(basket)
    regional("Pot", _g)(pot)
    regional("Strongbox", _g)(strongbox)
    regional("MedKit", _g)(medkit)
    regional("Mortar", _g)(mortar)
    regional("Creel", _g)(creel)
    regional("Bell", _g)(bell)
    regional("SewingKit", _g)(sewing_kit)
    regional("AlchemySet", _g)(alchemy_set)
    regional("Quiver", _g)(quiver)
    regional("Teaset", _g)(teaset)
    regional("Tableware", _g)(tableware)
