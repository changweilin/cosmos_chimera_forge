"""Four-planet forms of the soft goods (cosmos_chimera everyday-objects.md#四星球形體, Q-A38 batch 3, soft goods).

FishingNet, Sack, Backpack, Ball, Kite, PrayerBeads and Banner for Ocean, Gale, Radiant and Metropolis in all 8 eras.
Slots, frames and per-era sizes are forms_soft.py's (cloth / hem / trim; net, sack, ball and banner stand on the
floor, the backpack hangs from its haul loop down -Z and back +Y, the kite rises from its grip, the beads hang from
the top of the loop). None of these groups glow: only Ancient rune slots use glow.

Each region keeps one silhouette and swaps the mechanism by tier (hand-made, machine, high-tech).
Ocean: net heaps with bamboo floats, woven pandan sacks, rattan back baskets, sepak takraw balls, wau bulan moon
kites, shell beads, umbul-umbul streamers on a bowed bamboo pole with horn tips.
Gale: nets with gourd floats and stone sinkers, hide sacks with bead strings, fringed leather packs, twine balls,
painted diamond hide kites, bright bead loops with cowries, square cloths on pegged poles with cone finials.
Radiant: pleated cast nets with brass weights, jute bags with a red band and lotus stamp, knotted cloth bundles
with a hanging lota, stitched leather balls, patang kites, rudraksha malas with a tassel, triangular dhvaja flags
with dome finials.
Metropolis by era (cork floats and canvas, deco setbacks, brass and gears, shell pods and drones, scrap).
"""
import math

from mathutils import Matrix, Vector

from forms_region_pilot import HAND, MACHINE, dome, gear, horn, lash, pegs, petals, steps, zig
from forms_soft import (banner_fn, bead_loop, belt, blob, cord, dome_prof, drape, great, heap, kite_tail, loop,
                        net_over, pack_body, patch, rim_pts, sack_prof, sail_fn, sheet, shoulder_straps, strap)
from forms_vessel import rad_at, shell
from kit_forms import F, J, regional
from kit_lib import M, REGIONS


def T(x, y, z):
    return Matrix.Translation((x, y, z))


def tier(e):
    return "hand" if e in HAND else "machine" if e in MACHINE else "high"


def pick(p, hand, machine="body", high="body"):
    return {"hand": hand, "machine": machine, "high": high}[tier(p.era)]


def mark(p, x, y, z, s):
    """Small era token (never glowing except Ancient runes)."""
    e = p.era
    if e == "Industrial":
        for dx in (-1, 1):
            p.ball(s * 0.12, T(x + dx * s * 0.4, y, z), mat="metal", segs=(4, 3))
    elif e == "Steampunk":
        gear(p, s * 0.3, M(loc=(x, y, z), rot=(90, 0, 0)), mat="brass")
    elif e == "Wasteland":
        p.box((s * 0.8, 0.004, s * 0.5), M(loc=(x, y, z), rot=(0, J(p, 12, 0.5), 0)), mat="rubber", bevel=0)
    elif e == "Ancient":
        for i in range(3):
            p.box((s * 0.2, 0.004, s * (0.5 if i % 2 else 0.3)), T(x + (i - 1) * s * 0.3, y, z), mat="glow", bevel=0)
    elif e == "Future":
        p.box((s * 0.7, 0.004, s * 0.2), T(x, y, z), mat="glass", bevel=0)


# ================================================================ FishingNet (heaped on the floor)


def fishing_net(p, slot):
    e, g = p.era, p.region
    R = F(p, {"Mercantile": 0.2, "Industrial": 0.22, "Steampunk": 0.11, "Future": 0.2, "Ancient": 0.23}.get(e, 0.25), 0.1)
    H = F(p, {"Mercantile": 0.26, "Industrial": 0.13, "Steampunk": 0.2, "Future": 0.16}.get(e, 0.13), 0.1)
    ph = p.frame.uniform(0, math.tau)
    netmat = pick(p, "rope", "rope" if e != "Industrial" else "paint", "fit")
    if g == "Radiant":  # cast net piled as a pleated cone
        Hc = max(H, 0.2)
        prof = [(0, 0), (R, 0), (R * 0.92, Hc * 0.15), (R * 0.55, Hc * 0.5), (R * 0.22, Hc * 0.85), (0.02, Hc), (0, Hc)]
        wp = heap(Hc, 8, 0.08, ph, 0.0)
        if slot == "cloth":
            blob(p, prof, wp, mat=netmat, segs=10)
        elif slot == "hem":  # hand line coiled on the crown, brass weights round the skirt
            p.ring(0.04, 0.006, T(0, 0, Hc), mat="grip", segs=6, square=False)
            for k in range(8):
                a = ph + k * math.tau / 8
                p.ball(0.012, T(math.cos(a) * R * 1.0, math.sin(a) * R * 1.0, 0.01), mat="fit", segs=(4, 3))
        else:
            petals(p, R * 0.5, Hc * 0.45, 5, 0.02, mat="accent", tilt=60)
            mark(p, 0, -R * 0.6, Hc * 0.3, 0.04)
        return
    wp = heap(H, 5, 0.12, ph)
    if slot == "cloth":
        blob(p, dome_prof(R, H), wp, mat=netmat, segs=10)
        net_over(p, R, H, wp, "bark" if tier(e) == "hand" else "fit", n=5, ph=ph)
    elif slot == "hem":
        if g == "Ocean":  # bamboo scoop hoop and handle
            p.tube(loop(rim_pts(R * 1.02, 10, 0.016, ph, 0.03, p.rng)), 0.011, mat=pick(p, "bamboo", "metal", "fit"), segs=5)
            a = ph + math.pi
            p.tube([(math.cos(a) * R, math.sin(a) * R, 0.016), (math.cos(a) * R * J(p, 2.0, 0.1), math.sin(a) * R * 2.0, 0.02)], 0.013,
                   mat=pick(p, "bamboo", "metal", "fit"), segs=5)
            lash(p, 0.013, 0, 0.02, M(loc=(math.cos(a) * R * 1.1, math.sin(a) * R * 1.1, 0.016), rot=(0, 90, math.degrees(a))), segs=4)
        elif g == "Gale":  # headrope coiled on the crown with pegs through it
            top = wp(Vector((0, 0, H))).z
            p.ring(0.05, 0.008, T(0, 0, top + 0.006), mat="grip", segs=6, square=False)
            pegs(p, 0.05, top + 0.01, 3, 0.05, mat="body")
        else:
            if tier(e) == "high":  # emitter puck
                p.cyl(R * 0.3, R * 0.28, 0.03, T(0, 0, H), mat="body", segs=8, bevel=0.2)
            elif e == "Industrial":
                steps(p, R * 0.5, R * 0.5, H * 0.9, 2, 0.02, mat="fit", shrink=0.7)
            else:
                p.tube([(0.05, 0, H), (R * 0.6, -0.04, H * 0.7), (R * 1.05, -0.06, 0.01), (R * J(p, 1.4, 0.1), -0.02, 0.008)], 0.006, mat="grip", segs=4)
    else:  # floats and sinkers round the foot
        n = 5
        for k in range(n):
            a = ph + 0.4 + k * math.tau / n
            c = (math.cos(a) * R * 1.02, math.sin(a) * R * 1.02, 0.018)
            if g == "Ocean":
                p.cyl(0.016, 0.016, 0.06, M(loc=c, rot=(90, 0, math.degrees(a))) @ T(0, 0, -0.03), mat=pick(p, "bamboo", "paint", "glass"), segs=5, bevel=0)
            elif g == "Gale":
                if k % 2:
                    p.ball(0.022, M(loc=c, scale=(1, 1, 1.3)), mat=pick(p, "gourd", "paint", "fit"), segs=(5, 3))
                else:
                    p.ball(0.018, M(loc=c, scale=(1.2, 1, 0.6)), mat="stone_dark", segs=(5, 3))
            else:
                p.ball(0.02, M(loc=c, scale=(1.3, 1, 0.8)), mat=pick(p, "bark", "paint", "glass"), segs=(5, 3))
        if g == "Gale":
            zig(p, R * 0.75, H * 0.35, 0.03, 6)
        mark(p, 0, -R * 0.95, H * 0.3, 0.04)


# ================================================================ Sack (stands on the floor)


def sack(p, slot):
    e, g = p.era, p.region
    H = F(p, {"Primal": 0.42, "Mercantile": 0.5, "Industrial": 0.58, "Steampunk": 0.48, "Future": 0.34, "Ancient": 0.48}.get(e, 0.56), 0.08)
    R = F(p, {"Primal": 0.17, "Industrial": 0.17, "Steampunk": 0.17, "Future": 0.25}.get(e, 0.2), 0.08)
    lean = F(p, 0.07, 0.5) * (1 if p.frame.random() < 0.5 else -1)
    ph = p.frame.uniform(0, math.tau)
    zn = H * 0.8
    neck = (lean * H * 0.64, 0, zn)
    top = {"Ocean": "tuft", "Gale": "roll", "Radiant": "tuft", "Metropolis": "roll" if tier(e) == "machine" else "dome"}[g]
    prof = sack_prof(R, H, top)
    wp = drape(H, 5, 0.07, ph, lean if top == "tuft" else lean * 0.5, lump=0.05)
    if slot == "cloth":
        mat = {"Ocean": pick(p, "rattan", "body"), "Gale": pick(p, "hide" if e == "Primal" else "leather", "body"),
               "Radiant": pick(p, "rope", "body"), "Metropolis": pick(p, "rope" if e != "Mercantile" else "cloth", "body")}[g]
        if tier(e) == "high":
            mat = "body"
        blob(p, prof, wp, mat=mat, segs=10)
        if g == "Radiant":  # red band
            belt(p, prof, wp, H * 0.35, H * 0.45, "paint", segs=10)
        elif g == "Ocean" and tier(e) == "hand":
            for z in (0.2, 0.5):
                belt(p, prof, wp, H * z, H * z + 0.012, "accent", segs=10)
    elif slot == "hem":
        if top == "tuft":
            p.ring(R * 0.3, 0.008, T(*neck), mat="grip", segs=8, square=False)
            if g == "Ocean":
                for s in (-1, 1):
                    horn(p, neck[0] + s * R * 0.3, 0, zn + 0.01, R * 0.3, s, mat="fit")
            else:
                for s in (-1, 1):
                    p.tube([(neck[0] + s * 0.01, -R * 0.3, zn), (neck[0] + s * 0.04, -R * 0.42, zn - J(p, 0.1, 0.2))], 0.004, mat="grip", segs=3)
        elif top == "roll":
            z = H * 0.92
            p.cyl(R * 0.1, R * 0.1, R * 1.6, M(loc=(lean * H * 0.4 - R * 0.8, 0, z), rot=(0, 90, 0)), mat="grip", segs=6, bevel=0)
            if g == "Gale":
                for s in (-1, 1):
                    p.tube([(lean * H * 0.4 + s * R * 0.8, 0, z), (s * R * 1.1, -R * 0.5, H * 0.5)], 0.004, mat="grip", segs=3)
        else:  # dome top with a carry loop
            p.ring(R * 0.15, 0.008, M(loc=(0, 0, H + 0.02), rot=(90, 0, 0)), mat="grip", segs=6, square=False)
    else:
        if g == "Gale":  # bead strings down the front
            for s in (-1, 1):
                for k in range(4):
                    c = surf_pt(prof, wp, -math.pi / 2 + s * 0.35, H * (0.6 - k * 0.08))
                    p.ball(0.008, T(*c), mat=("accent", "fit")[k % 2], segs=(4, 3))
        elif g == "Radiant":
            c = surf_pt(prof, wp, -math.pi / 2, H * 0.4, 1.03)
            petals(p, 0.03, 0, 5, 0.015, M(loc=c, rot=(90, 0, 0)), mat="accent", tilt=0)
        elif g == "Ocean":
            c = surf_pt(prof, wp, -math.pi / 2 + 0.3, H * 0.3, 1.02)
            p.box((0.06, 0.004, 0.04), T(*c), mat="paint" if tier(e) != "hand" else "bone", bevel=0)
        else:
            if e == "Industrial":
                patch(p, prof, wp, -math.pi / 2, 0.6, H * 0.3, H * 0.5, "paint")
            else:
                patch(p, prof, wp, -math.pi / 2, 0.5, H * 0.3, H * 0.45, "fit" if tier(e) != "hand" else "bone")
        c = surf_pt(prof, wp, -math.pi / 2 - 0.6, H * 0.25, 1.03)
        mark(p, c[0], c[1], c[2], 0.04)


def surf_pt(prof, warp, a, z, lift=1.02):
    r = rad_at(prof, z) * lift
    return tuple(warp(Vector((math.cos(a) * r, math.sin(a) * r, z))))


# ================================================================ Backpack (hangs from its haul loop)


def backpack(p, slot):
    e, g = p.era, p.region
    H = F(p, {"Primal": 0.62, "Agrarian": 0.55, "Industrial": 0.56, "Future": 0.46}.get(e, 0.48), 0.08)
    W = F(p, {"Agrarian": 0.36, "Future": 0.3}.get(e, 0.34), 0.08)
    D = F(p, {"Primal": 0.18, "Agrarian": 0.28, "Future": 0.16}.get(e, 0.2), 0.08)
    yc = D / 2 + 0.015
    m = T(0, yc, -H)
    if g == "Ocean":  # rattan back basket, square-mouthed
        r = W / 2
        outer = [(r * 0.7, 0), (r * 0.85, H * 0.5), (r, H)]
        sc = M(loc=(0, yc + 0.02, -H), scale=(1, D / W, 1))
        if slot == "cloth":
            shell(p, outer, 0.008, mat=pick(p, "rattan", "body"), segs=8, m=sc)
            p.ring(r * 1.02, 0.01, sc @ T(0, 0, H), mat="fit", segs=8, square=False)
        elif slot == "hem":
            shoulder_straps(p, W, D, H, "grip", w=0.035, t=0.01)
        else:
            for s in (-1, 1):
                horn(p, s * r, yc + 0.02, -0.02, r * 0.35, s, mat="accent")
            lash(p, rad_at(outer, H * 0.5), 0, 0.03, sc @ T(0, 0, H * 0.5), segs=8)
            mark(p, 0, yc + D * 0.6, -H * 0.4, 0.05)
        return
    if g == "Radiant":  # knotted cloth bundle carried on the back, a lota hanging
        rr = min(W, D) * 0.55
        if slot == "cloth":
            blob(p, [(0, 0), (rr * 0.8, 0.01), (rr * 1.05, H * 0.4), (rr, H * 0.75), (rr * 0.3, H * 0.95), (0, H)],
                 drape(H, 4, 0.08, 0.3, 0.0, lump=0.06), M(loc=(0, yc, -H), scale=(W / (2 * rr), 1, 1)), mat=pick(p, "cloth", "body"), segs=10)
        elif slot == "hem":  # the knot ends over the shoulders
            p.ball(0.025, M(loc=(0, yc - 0.02, -0.04), scale=(1.5, 1, 0.8)), mat=pick(p, "cloth", "fit"), segs=(6, 3))
            for s in (-1, 1):
                strap(p, [(s * 0.04, yc - 0.02, -0.04), (s * W * 0.35, -0.04, -H * 0.3), (s * W * 0.3, 0.012, -H * 0.7)], 0.04, mat=pick(p, "cloth", "grip"))
        else:
            c = (W * 0.45, yc, -H * 0.9)
            p.lathe([(0, 0), (0.035, 0.01), (0.045, 0.04), (0.02, 0.07), (0.03, 0.08)], T(*c), mat="fit", segs=7)
            petals(p, 0.03, 0, 5, 0.014, M(loc=(0, yc + rr * 0.95, -H * 0.5), rot=(-90, 0, 0)), mat="accent", tilt=0)
            mark(p, -W * 0.25, yc + rr, -H * 0.4, 0.05)
        return
    prof, wfn = pack_body(W, D, H, 0.06, 0.55)
    if slot == "cloth":
        mat = {"Gale": pick(p, "hide" if e == "Primal" else "leather", "body"), "Metropolis": pick(p, "leather" if e != "Primal" else "hide", "body")}[g]
        if g == "Metropolis" and e == "Future":
            p.box((W * 0.8, D * 0.8, H * 0.9), T(0, yc, -H * 0.5), mat="body", bevel=0.4)
        else:
            blob(p, prof, wfn, m, mat=mat, segs=10)
    elif slot == "hem":
        shoulder_straps(p, W, D, H, "grip", w=0.045)
        p.ring(0.025, 0.005, M(loc=(0, yc, 0.01), rot=(90, 0, 0)), mat="grip", segs=6, square=False)
    else:
        if g == "Gale":  # flap with a zigzag border and a fringe
            sheet(p, lambda u, v: ((u - 0.5) * W * 0.9, yc + D * 0.52 + 0.004 * v, -H * 0.02 - v * H * 0.4), 2, 2, 0.005, "grip")
            for i in range(6):
                x = (i - 2.5) * W * 0.14
                p.box((W * 0.11, 0.004, 0.03), M(loc=(x, yc + D * 0.53, -H * 0.38), rot=(0, 30 if i % 2 else -30, 0)), mat=("accent", "fit")[i % 2], bevel=0)
                p.cyl(0.003, 0.003, 0.06, T(x, yc + D * 0.53, -H * 0.48), mat="grip", segs=3, bevel=0)
        else:
            if e == "Industrial":
                steps(p, W * 0.6, 0.03, -H * 0.75, 3, H * 0.08, M(loc=(0, yc + D * 0.55, 0)), mat="fit", shrink=0.85)
            elif tier(e) == "high":
                for s in (-1, 1):
                    p.box((0.015, D * 0.9, H * 0.7), T(s * W * 0.42, yc, -H * 0.5), mat="fit", bevel=0)
            else:  # pocket and a rolled blanket on top
                p.box((W * 0.5, 0.04, H * 0.3), T(0, yc + D * 0.55, -H * 0.6), mat="grip" if tier(e) == "hand" else "fit", bevel=0.2)
                p.cyl(0.05, 0.05, W * 0.9, M(loc=(-W * 0.45, yc, -0.02), rot=(0, 90, 0)), mat="cloth", segs=7, bevel=0)
        mark(p, W * 0.25, yc + D * 0.56, -H * 0.3, 0.05)


# ================================================================ Ball (rests on the floor)


def ball(p, slot):
    e, g = p.era, p.region
    R = F(p, {"Primal": 0.075, "Steampunk": 0.09, "Future": 0.09, "Ancient": 0.1}.get(e, 0.11), 0.08)
    lift = 0.04 if (g == "Metropolis" and e == "Future") else 0.0
    zc = R + lift
    spin = p.frame.uniform(0, 180)
    if g == "Ocean":  # sepak takraw: open woven strips
        if slot == "cloth":
            for tl, sp in ((90, 0), (90, 60), (90, 120), (0, 0)):
                great(p, R, zc, tl, spin + sp, 0.008, pick(p, "rattan", "body", "fit"), segs=10, lift=1.0)
        elif slot == "hem":
            p.ball(R * 0.85, T(0, 0, zc), mat=pick(p, "bark", "rubber", "glass"), segs=(8, 6))
        else:
            great(p, R, zc, 45, spin + 30, 0.004, "accent", segs=8, lift=1.01)
    elif g == "Gale":  # twine-wound ball
        if slot == "cloth":
            p.ball(R, M(loc=(0, 0, zc), scale=(1, 1, J(p, 0.95, 0.03))), mat=pick(p, "cloth", "rubber", "body"), segs=(10, 6))
        elif slot == "hem":
            for k in range(3):
                great(p, R, zc, 90, spin + k * 60, 0.003, "grip", segs=10)
        else:
            great(p, R, zc, 0, 0, 0.006, "accent", segs=10)
            zig(p, R * 1.01, zc + R * 0.4, 0.015, 6, mats=("accent", "fit"))
    elif g == "Radiant":  # stitched leather ball with a raised seam
        if slot == "cloth":
            p.ball(R, T(0, 0, zc), mat=pick(p, "leather", "paint", "body"), segs=(10, 7))
        elif slot == "hem":
            great(p, R, zc, 90, spin, 0.006, "bone" if tier(e) != "high" else "fit", segs=12)
        else:
            if tier(e) == "hand":
                petals(p, R * 0.3, 0, 5, 0.012, M(loc=(0, 0, zc + R * 0.98)), mat="accent", tilt=80)
            else:
                great(p, R, zc, 90, spin + 90, 0.003, "accent", segs=12)
    else:
        if slot == "cloth":
            if tier(e) == "high":
                p.ball(R, T(0, 0, zc), mat="body", segs=(10, 6))
            else:
                p.ball(R, T(0, 0, zc), mat=pick(p, "leather" if e != "Primal" else "hide", "rubber" if e != "Steampunk" else "leather"), segs=(10, 7))
        elif slot == "hem":
            if e == "Steampunk":
                for k in range(3):
                    great(p, R, zc, 90, spin + k * 60, 0.004, "brass", segs=10, lift=1.04)
            elif e == "Industrial":
                for tl in (0, 90):
                    great(p, R, zc, tl, spin, 0.02, "paint", segs=12, lift=1.005)
            elif tier(e) == "high":
                great(p, R, zc, 0, 0, 0.008, "fit", segs=12)
            else:
                for k in range(3):
                    great(p, R, zc, 90, spin + k * 60, 0.003, "grip", segs=10)
        else:
            if tier(e) == "high":
                dome(p, R * 0.25, zc + R * 0.9, mat="glass" if e == "Future" else "fit", finial=False, segs=6)
            else:
                p.ball(R * 0.1, T(0, 0, zc + R), mat="metal", segs=(5, 3))
    if slot == "trim":
        mark(p, 0, -R * 1.02, zc, R * 0.4)


# ================================================================ Kite (grip at the origin, sail up +Z)

KITE = {
    "Ocean": [(0, 0.85), (0.12, 0.55), (0.25, 0.12), (0.45, 0.18), (0.65, 1.0), (0.85, 0.75), (1, 0.08)],  # wau bulan
    "Gale": [(0, 0.02), (0.6, 0.5), (1, 0.02)],  # diamond
    "Radiant": [(0, 0.02), (0.5, 0.5), (1, 0.02)],  # patang
    "Metropolis": [(0, 0.42), (0.75, 0.42), (0.86, 0.38), (0.95, 0.24), (1, 0.05)],
}


def kite(p, slot):
    e, g = p.era, p.region
    H = F(p, {"Primal": 0.62, "Agrarian": 0.7, "Industrial": 0.72, "Future": 0.09}.get(e, 0.66), 0.08)
    Wk = F(p, {"Agrarian": 1.0, "Industrial": 0.42, "Future": 0.55}.get(e, 0.9) * 0.6, 0.08)
    L = F(p, 0.42, 0.15)
    bow = F(p, 0.035, 0.3)
    ph = p.frame.uniform(0, math.tau)
    if g == "Metropolis" and e == "Future":  # small drone
        H = 0.09
        if slot == "cloth":
            p.box((0.12, 0.12, 0.04), T(0, 0, H + 0.05), mat="body", bevel=0.4)
        elif slot == "hem":
            for k in range(4):
                a = math.pi / 4 + k * math.pi / 2
                p.tube([(0, 0, H + 0.05), (math.cos(a) * 0.14, math.sin(a) * 0.14, H + 0.06)], 0.006, mat="fit", segs=4)
                p.ring(0.05, 0.004, T(math.cos(a) * 0.14, math.sin(a) * 0.14, H + 0.07), mat="fit", segs=8)
            p.cyl(0.008, 0.008, H + 0.03, mat="grip", segs=5, bevel=0)
        else:
            p.box((0.06, 0.004, 0.012), T(0, -0.062, H + 0.05), mat="glass", bevel=0)
        return
    tb = KITE[g]
    H = max(H, 0.55)
    fn = sail_fn(tb, Wk, H, bow, ph)

    def spar(vc, k=0.9):
        hw = Wk * k * _tab(tb, vc)
        return [(x, bow * (1 - (x / max(hw / k, 1e-3)) ** 2) * math.sin(math.pi * vc) + 0.008, vc * H) for x in (-hw, -hw * 0.5, 0, hw * 0.5, hw)]

    def decal(u0, u1, v0, v1, mat):
        sheet(p, lambda u, v: Vector(sail_fn(tb, Wk, H, bow, ph, 0.006)(u0 + (u1 - u0) * u, v0 + (v1 - v0) * v)), 2, 2, 0.003, mat)
    cloth = {"Ocean": pick(p, "bone", "cloth", "glass"), "Gale": pick(p, "hide" if e == "Primal" else "cloth", "cloth", "body"),
             "Radiant": pick(p, "bone", "paint", "body"), "Metropolis": pick(p, "bone" if e != "Mercantile" else "cloth", "cloth", "body")}[g]
    stick = pick(p, "bamboo" if g in ("Ocean", "Radiant") else "wood", "metal", "fit")
    if slot == "cloth":
        sheet(p, fn, 4, 8 if g == "Ocean" else 6, 0.004, cloth)
        if g == "Ocean":
            decal(0.35, 0.65, 0.6, 0.75, "accent")
        elif g == "Gale":
            decal(0.3, 0.7, 0.45, 0.55, "accent")
        elif g == "Radiant":
            decal(0.38, 0.62, 0.42, 0.6, "accent")
        else:
            decal(0.3, 0.7, 0.4, 0.62, "paint")
    elif slot == "hem":
        p.tube([(0, bow * math.sin(math.pi * v) + 0.008, v * H) for v in (0, 0.25, 0.5, 0.75, 1.0)], 0.005, mat=stick, segs=4)
        if g == "Ocean":
            p.tube(spar(0.65), 0.005, mat=stick, segs=4)
            p.tube(spar(0.0, 0.85), 0.005, mat=stick, segs=4)
        elif g == "Radiant":  # curved bow spar
            hw = Wk * 0.5 * 0.9
            p.tube([(-hw, 0.01, H * 0.5), (0, 0.02, H * 0.62), (hw, 0.01, H * 0.5)], 0.004, mat=stick, segs=4)
        else:
            p.tube(spar(0.6 if g == "Gale" else 0.7), 0.005, mat=stick, segs=4)
        if e == "Industrial" and g == "Metropolis":
            steps(p, 0.05, 0.02, H * 0.05, 2, 0.01, mat="fit", shrink=0.7)
    else:
        if g == "Ocean":  # bow hummer on top and a short tail
            p.tube([(-Wk * 0.3, 0.02, H * 0.98), (0, 0.05, H * 1.05), (Wk * 0.3, 0.02, H * 0.98)], 0.003, mat=stick, segs=3)
            for s in (-1, 1):
                horn(p, s * Wk * 0.3, 0.02, H * 0.98, 0.05, s, mat="accent")
        elif g == "Gale":
            kite_tail(p, 0, L, 0.035, ph, "accent")
            for k in range(3):
                v = (k + 1) / 4
                p.ball(0.01, T(0.05 * math.sin(v * math.pi * 1.5 + ph), 0.01, -v * L), mat="fit", segs=(4, 3))
        elif g == "Radiant":  # small tail tassel at the foot
            p.cyl(0.03, 0.0, 0.08, M(loc=(0, 0.005, 0.0), rot=(180, 0, 0)), mat="accent", segs=4, bevel=0)
        else:
            for s in (-1, 1):
                kite_tail(p, s * Wk * 0.2, L * J(p, 1.0, 0.15), 0.03, ph + s, "paint", 0.03)
        mark(p, 0, -0.004, H * 0.3, 0.05)


def _tab(pairs, v):
    for (v0, a), (v1, b) in zip(pairs, pairs[1:]):
        if v0 <= v <= v1:
            return a + (b - a) * (v - v0) / max(v1 - v0, 1e-6)
    return pairs[-1][1] if v > pairs[-1][0] else pairs[0][1]


# ================================================================ PrayerBeads (held at the top of the loop)


def prayer_beads(p, slot):
    e, g = p.era, p.region
    Lh = F(p, {"Future": 0.16, "Steampunk": 0.2}.get(e, 0.22), 0.08)
    Wl = F(p, {"Future": 0.08}.get(e, 0.07), 0.08)
    rb = F(p, {"Primal": 0.011, "Mercantile": 0.01, "Steampunk": 0.011, "Wasteland": 0.011, "Ancient": 0.011}.get(e, 0.009), 0.1)
    Lk = F(p, 0.035, 0.15)
    n = 14
    zk = -Lh - rb
    if slot == "cloth":
        p.tube(cord(Wl, Lh), 0.0015, mat=pick(p, "rope", "metal", "fit"), segs=3)
        for i, c in enumerate(bead_loop(Wl, Lh, n)):
            if g == "Ocean":  # shell and coral
                mat = pick(p, "bone" if i % 2 else "paint", "metal" if i % 2 else "paint", "glass" if i % 2 else "fit")
                p.ball(rb * (1.0 if i % 2 else 0.8), M(loc=c, scale=(1, 1, 0.7)), mat=mat, segs=(5, 3))
            elif g == "Gale":  # bright alternating beads
                p.ball(rb, T(*c), mat=("accent", "fit", "paint")[i % 3] if tier(e) != "high" else ("fit", "body")[i % 2], segs=(5, 3))
            elif g == "Radiant":  # rudraksha
                p.ball(rb * 1.1, T(*c), mat=pick(p, "bark", "fit", "body"), segs=(5, 3), noise=0.02 if tier(e) == "hand" else 0)
            else:
                if e == "Steampunk":  # brass gear-blank beads
                    p.cyl(rb, rb, rb * 0.8, M(loc=c, rot=(0, 0, 0)) @ T(0, 0, -rb * 0.4), mat="brass", segs=6, bevel=0)
                else:
                    p.ball(rb, T(*c), mat=pick(p, "wood" if e != "Mercantile" else "glaze", "metal", "glass" if e == "Future" else "body"), segs=(5, 3))
    elif slot == "hem":  # guru bead and the knot below
        if g == "Radiant":
            p.ball(rb * 1.6, T(0, 0, zk - rb * 0.4), mat=pick(p, "bark", "fit", "body"), segs=(6, 4))
            petals(p, rb * 0.8, zk - rb * 1.6, 5, rb * 0.6, mat="accent", tilt=-30)
        elif g == "Ocean":
            horn(p, 0, 0, zk, rb * 2.5, 1, mat="accent")
        else:
            p.ball(rb * 1.4, T(0, 0, zk - rb * 0.4), mat="fit" if g != "Gale" else "accent", segs=(6, 4))
        p.tube([(0, 0, zk - rb), (0, 0, zk - Lk)], 0.002, mat=pick(p, "rope", "metal", "fit"), segs=3)
    else:  # pendant
        z = zk - Lk
        if g == "Ocean":  # cowrie-like shell
            p.ball(0.014, M(loc=(0, 0, z - 0.014), scale=(0.7, 0.45, 1)), mat=pick(p, "bone", "metal", "glass"), segs=(6, 4))
        elif g == "Gale":
            for s in (-1, 0, 1):
                p.ball(0.008, M(loc=(s * 0.012, 0, z - 0.01 - abs(s) * 0.006), scale=(0.7, 0.5, 1)), mat="bone", segs=(4, 3))
        elif g == "Radiant":  # tassel
            p.lathe([(0.004, 0), (0.006, -0.01), (J(p, 0.014, 0.2), -0.05), (0, -0.052)], T(0, 0, z), mat="paint", segs=6)
        else:
            if e == "Ancient":
                p.box((0.02, 0.006, 0.03), T(0, 0, z - 0.015), mat="stone", bevel=0)
                p.box((0.004, 0.007, 0.018), T(0, 0, z - 0.015), mat="glow", bevel=0)
            elif e == "Industrial":
                steps(p, 0.025, 0.004, z - 0.03, 3, 0.009, mat="fit", shrink=0.75)
            else:
                p.cyl(0.015, 0.015, 0.004, M(loc=(0, 0.002, z - 0.016), rot=(90, 0, 0)), mat=pick(p, "fit", "metal", "glass" if e == "Future" else "fit"), segs=8, bevel=0)


# ================================================================ Banner (floor contact at z = 0)


def banner(p, slot):
    e, g = p.era, p.region
    Hp = F(p, {"Primal": 2.1, "Future": 2.3, "Ancient": 2.1}.get(e, 2.25), 0.06)
    Wc = F(p, {"Primal": 0.26, "Agrarian": 0.36, "Industrial": 0.5, "Future": 0.52, "Ancient": 0.4}.get(e, 0.46), 0.08)
    Lc = F(p, {"Primal": 0.7, "Agrarian": 1.15, "Future": 0.9, "Ancient": 0.95}.get(e, 1.0), 0.08)
    rp = F(p, {"Industrial": 0.018, "Future": 0.02, "Ancient": 0.035}.get(e, 0.022), 0.08)
    ph = p.frame.uniform(0, math.tau)
    Hc = Hp * 0.9
    yc = -rp - 0.014
    top = Hc - 0.012
    pole = pick(p, "bamboo" if g == "Ocean" else "wood" if g != "Radiant" else "wood_dark", "metal", "fit")
    if slot == "cloth":
        if g == "Ocean":  # umbul-umbul: long narrow streamer hanging from the bowed tip
            fn = banner_fn(Wc * 0.5, Lc * 1.4, top, yc, 2, 0.015, ph, "point", 0.4)
            sheet(p, fn, 3, 8, 0.005, pick(p, "cloth", "cloth", "glass"))
            sheet(p, lambda u, v: Vector(fn(u, 0.3 + v * 0.08)) + Vector((0, -0.004, 0)), 2, 1, 0.003, "accent")
        elif g == "Gale":  # square cloth with a zigzag hem
            fn = banner_fn(Wc, Lc * 0.75, top, yc, 3, 0.02, ph, "flat")
            sheet(p, fn, 6, 5, 0.006, pick(p, "hide" if e == "Primal" else "cloth", "cloth", "body"))
            sheet(p, lambda u, v: Vector(fn(u, 0.85 + v * 0.12)) + Vector((0, -0.004, 0)), 6, 1, 0.003, "accent")
        elif g == "Radiant":  # dhvaja: triangular flag flying from the top of the pole
            def tri(u, v):
                x = u * Wc * 1.4
                z = Hp - 0.02 - (1 - u) * 0.0 - v * Lc * 0.55 * (1 - u)
                y = -0.03 * math.sin(u * math.pi * 2 + ph) * u
                return (x + rp, y, z)
            sheet(p, tri, 5, 3, 0.005, pick(p, "paint", "cloth", "body"))
        else:
            fn = banner_fn(Wc, Lc, top, yc, 3, 0.02 if tier(e) != "high" else 0.004, ph, "swallow" if tier(e) == "hand" else "flat")
            sheet(p, fn, 6, 5, 0.006, pick(p, "cloth", "cloth", "glass" if e == "Future" else "body"))
    elif slot == "hem":
        if g == "Ocean":  # bowed bamboo pole with a horn tip
            pts = [(0, 0, 0), (0, 0, Hp * 0.5), (0, -0.04, Hp * 0.85), (0, -0.12, Hp)]
            p.tube(pts, rp, mat=pole, segs=6)
            p.cyl(0.01, 0.01, Wc * 0.6, M(loc=(-Wc * 0.3, yc, Hc), rot=(0, 90, 0)), mat=pole, segs=5, bevel=0)
            horn(p, 0, -0.12, Hp, 0.12, 1, mat="accent")
            p.cyl(0.09, 0.08, 0.08, mat="stone", segs=6, bevel=0)
        elif g == "Gale":  # pole with beam-end pegs and a cone finial
            p.cyl(rp, rp * 0.9, Hp, mat=pole, segs=7, bevel=0)
            pegs(p, rp, Hp * 0.3, 4, 0.08, mat="body")
            p.cyl(0.01, 0.01, Wc * 1.2, M(loc=(-Wc * 0.6, yc, Hc), rot=(0, 90, 0)), mat=pole, segs=5, bevel=0)
            p.cyl(rp * 2.5, 0.0, 0.15, T(0, 0, Hp), mat="accent", segs=6, bevel=0)
        elif g == "Radiant":  # turned pole with a dome finial and a lotus foot
            p.lathe([(rp * 1.3, 0), (rp, 0.1), (rp, Hp * 0.5), (rp * 1.3, Hp * 0.52), (rp, Hp * 0.54), (rp * 0.9, Hp)], mat=pole, segs=7)
            dome(p, rp * 2.2, Hp, mat="fit", segs=7)
            petals(p, 0.08, 0.0, 6, 0.04, mat="accent", tilt=60)
        else:
            if e == "Industrial":
                steps(p, 0.3, 0.3, 0, 3, 0.04, mat="body", shrink=0.75)
                p.cyl(rp, rp, Hp, mat="metal", segs=7, bevel=0)
            elif tier(e) == "high":
                p.cyl(rp * 1.6, rp, Hp, mat="body", segs=7, bevel=0)
                p.box((Wc * 1.1, 0.03, 0.04), T(0, yc, Hc), mat="fit", bevel=0.2)
            else:
                p.cyl(rp, rp * 0.9, Hp, mat=pole, segs=7, bevel=0)
                p.cyl(0.11, 0.1, 0.04, mat="stone" if tier(e) == "hand" else "metal", segs=8, bevel=0)
            if tier(e) != "high":
                p.cyl(0.011, 0.011, Wc * 1.2, M(loc=(-Wc * 0.6, yc, Hc), rot=(0, 90, 0)), mat=pole, segs=5, bevel=0)
                p.ball(rp * 1.6, T(0, 0, Hp + rp), mat="fit", segs=(6, 4))
    else:  # emblem
        if g == "Ocean":
            for k in range(3):
                p.ball(0.015, T(0, -0.12 - 0.01 * k, Hp - 0.06 - k * 0.04), mat=("accent", "fit", "paint")[k], segs=(4, 3))
        elif g == "Gale":
            z = top - Lc * 0.75 * 0.4
            p.plate([(-0.08, 0), (0, 0.1), (0.08, 0), (0, -0.1)], 0.006, T(0, yc - 0.02, z), mat="fit", bevel=0)
        elif g == "Radiant":
            petals(p, 0.04, 0, 6, 0.02, M(loc=(Wc * 0.4 + rp, -0.012, Hp - Lc * 0.15), rot=(90, 0, 0)), mat="gold", tilt=0)
        else:
            z = top - Lc * 0.45
            if e == "Steampunk":
                gear(p, 0.08, M(loc=(0, yc - 0.02, z), rot=(90, 0, 0)), mat="brass")
            else:
                p.cyl(0.08, 0.08, 0.006, M(loc=(0, yc - 0.022, z), rot=(90, 0, 0)), mat="bone" if e != "Future" else "fit", segs=10, bevel=0)
        mark(p, 0, -rp - 0.004, Hp * 0.25, 0.06)


for _g in REGIONS:
    regional("FishingNet", _g)(fishing_net)
    regional("Sack", _g)(sack)
    regional("Backpack", _g)(backpack)
    regional("Ball", _g)(ball)
    regional("Kite", _g)(kite)
    regional("PrayerBeads", _g)(prayer_beads)
    regional("Banner", _g)(banner)
