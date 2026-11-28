"""Four-planet forms of the documents (cosmos_chimera everyday-objects.md#四星球形體, Q-A38 batch 3, documents).

Book, Scroll, Ledger, Map, Letter, Newspaper and Notice for Ocean, Gale, Radiant and Metropolis in all 8 eras. Slots,
frames and sizes are forms_document.py's (cover / spine / clasp / edge; carried documents lie with their bottom at
z = 0, book spines face -Y along X, scrolls roll along X; Notice stands on the floor). Writing is never letters
(glyph strips). The Record group never glows: only Ancient rune slots use glow, Future screens are unlit glass.

Each region keeps one silhouette and swaps the mechanism by tier (hand-made, machine, high-tech); eras differ by
craft (kit_lib.REGION_STYLE roles) and a small era token.
Ocean: lontar palm-leaf books between boards on a cord, rattan-lashed rolls with horn knobs, bamboo tally slats,
stick charts with shell knots, letters in bamboo tubes, notice boards under horned saddle roofs.
Gale: leather satchel books on a shoulder strap, cone-capped scroll cases, bead tally boards, painted hide maps,
beaded pouches, mud-pillar notice posts with beam-end pegs and zigzag friezes.
Radiant: cloth-wrapped pothi bundles, brass dome finials, red bahi-khata ledgers tied lengthwise, round painted
cloth maps, red-thread envelopes with a lotus seal, notice boards under a chhatri dome.
Metropolis by era (leather codex with brass corners, deco setbacks, brass hasps and cogs, slates, tape and scrap).
"""
from mathutils import Matrix

from forms_document import cog, flat, hoop, page_block, rollx, runes_front, runes_top, sheets, slab, text_front, text_top, wrap
from forms_region_pilot import HAND, MACHINE, dome, gear, horn, lash, pegs, petals, steps, zig
from kit_forms import F, J, regional
from kit_lib import M, REGIONS

T = Matrix.Translation


def tier(e):
    return "hand" if e in HAND else "machine" if e in MACHINE else "high"


def pick(p, hand, machine="body", high="body"):
    return {"hand": hand, "machine": machine, "high": high}[tier(p.era)]


def ink(p):
    """Colour of the fake writing: the region's accent, carved dark wood in Primal."""
    return "wood_dark" if p.era == "Primal" else "accent"


def token(p, x, y, z, s):
    """Era token on a top face; never glowing except the Ancient runes (Record group)."""
    e = p.era
    if e == "Industrial":
        for dx in (-1, 1):
            p.ball(s * 0.12, T((x + dx * s * 0.4, y, z)), mat="metal", segs=(4, 3))
    elif e == "Steampunk":
        gear(p, s * 0.3, T((x, y, z)), mat="brass")
    elif e == "Wasteland":
        p.box((s * 0.8, s * 0.5, 0.002), M(loc=(x, y, z + 0.001), rot=(0, 0, J(p, 12, 0.5))), mat="rubber", bevel=0)
    elif e == "Ancient":
        runes_top(p, x, y, z, s, n=3)
    elif e == "Future":
        p.box((s * 0.7, s * 0.25, 0.002), T((x, y, z + 0.001)), mat="glass", bevel=0)


# ================================================================ Book (H along X, spine at -Y)


def book(p, slot):
    e, g = p.era, p.region
    H, W, Tk = F(p, 0.22, 0.1), F(p, 0.16, 0.1), F(p, 0.045, 0.2)
    if g == "Ocean":  # lontar: long narrow leaves between two boards, a cord through them
        L, D, bt = H * 1.4, W * 0.35, Tk * 0.2
        if slot == "cover":
            for z in (0, Tk - bt):
                slab(p, L, D, bt, z, mat=pick(p, "teak" if e != "Primal" else "bamboo", "body", "glass" if e == "Future" else "body"))
        elif slot == "spine":  # the cord through two holes
            for s in (-1, 1):
                p.cyl(0.004, 0.004, Tk + 0.004, T((s * L * 0.25, 0, -0.002)), mat="grip", segs=4, bevel=0)
            p.tube([(-L * 0.25, 0, Tk + 0.002), (0, -D * 0.2, Tk + 0.006), (L * 0.25, 0, Tk + 0.002)], 0.0025, mat="grip", segs=4)
        elif slot == "clasp":  # coin weight on the cord end
            x = L * J(p, 0.35, 0.15)
            p.tube([(L * 0.25, 0, Tk + 0.002), (x, -D * 0.9, 0.004)], 0.002, mat="grip", segs=3)
            p.cyl(0.012, 0.012, 0.003, T((x, -D * 0.9, 0)), mat="accent", segs=7, bevel=0)
            horn(p, -L / 2, 0, Tk, D * 0.5, -1, mat="accent")
        else:
            page_block(p, L * 0.98, D * 0.96, Tk - 2 * bt, bt)
            text_front(p, 0, -D / 2, Tk * 0.55, L * 0.6, 0.004, mat=ink(p))
            token(p, L * 0.3, 0, Tk, D * 0.6)
    elif g == "Gale":  # square book in a leather satchel on a shoulder strap
        if slot == "cover":
            slab(p, H * 0.9, W, Tk, 0, mat=pick(p, "leather" if e != "Primal" else "hide", "body"))
        elif slot == "spine":  # the satchel flap folded over the top
            slab(p, H * 0.92, W * 0.55, 0.004, Tk, y=W * 0.23, mat=pick(p, "leather" if e != "Primal" else "hide", "fit"))
        elif slot == "clasp":  # strap loop
            p.tube([(-H * 0.45, 0, Tk * 0.5), (-H * 0.55, 0, Tk + J(p, 0.1, 0.2)), (0, 0, Tk + 0.16), (H * 0.55, 0, Tk + 0.1), (H * 0.45, 0, Tk * 0.5)],
                   0.004, mat="grip", segs=4)
        else:
            for i in range(6):
                x = (i - 2.5) * H * 0.13
                p.box((H * 0.11, 0.003, Tk * 0.35), M(loc=(x, -W / 2 - 0.001, Tk * 0.5), rot=(0, 30 if i % 2 else -30, 0)), mat=("accent", "fit")[i % 2], bevel=0)
            token(p, -H * 0.25, -W * 0.15, Tk, W * 0.3)
    elif g == "Radiant":  # pothi: loose leaves between boards, wrapped in cloth, knotted on top
        if slot == "cover":
            slab(p, H * 1.15, W * 0.7, Tk, 0, mat=pick(p, "cloth", "body"), bevel=0.25)
        elif slot == "spine":  # the knot
            p.ball(0.014, M(loc=(0, 0, Tk + 0.008), scale=(1.4, 1, 0.7)), mat=pick(p, "cloth", "fit"), segs=(6, 3))
            for s in (-1, 1):
                p.tube([(0, 0, Tk + 0.008), (s * 0.03, -0.02, Tk + 0.002), (s * 0.05, -0.03, Tk)], 0.004, mat=pick(p, "cloth", "fit"), segs=3)
        elif slot == "clasp":  # string around the bundle
            wrap(p, 0, W * 0.7, Tk, J(p, 0.003, 0.2), "accent", axis="x")
        else:
            petals(p, 0.018, Tk, 5, 0.01, T((-H * 0.35, 0, 0)), mat="accent", tilt=80)
            text_front(p, H * 0.1, -W * 0.35, Tk * 0.5, H * 0.5, 0.006, mat=ink(p))
            token(p, H * 0.35, 0, Tk, W * 0.25)
    else:  # codex by era
        bt = 0.005
        if slot == "cover":
            if e == "Future":
                slab(p, H, W, Tk * 0.4, 0, mat="body", bevel=0.3)
                slab(p, H * 0.85, W * 0.8, 0.002, Tk * 0.4, mat="glass", bevel=0)
            else:
                for z in (0, Tk - bt):
                    slab(p, H + 0.01, W + 0.006, bt, z, y=0.003, mat=pick(p, "leather" if e != "Primal" else "iron", "body", "body"))
        elif slot == "spine":
            if e == "Future":
                rollx(p, Tk * 0.2, H, Tk * 0.2, y=-W / 2, mat="fit", segs=6)
            elif e == "Industrial":
                steps(p, H * 0.6, 0.01, Tk * 0.15, 3, Tk * 0.25, M(loc=(0, -W / 2 - 0.004, 0)), mat="fit", shrink=0.85)
            else:
                rollx(p, Tk / 2, H + 0.01, Tk / 2, y=-W / 2, mat=pick(p, "leather" if e != "Primal" else "iron", "body"), segs=8)
                for i in (-1, 0, 1):
                    hoop(p, Tk / 2 * 1.1, i * H * 0.28, 0.005, Tk / 2, y=-W / 2, mat="fit", segs=8)
        elif slot == "clasp":
            if tier(e) == "hand":  # brass corners
                for sx in (-1, 1):
                    xx = sx * (H / 2 + 0.005)
                    flat(p, [(xx, W / 2 + 0.006), (xx - sx * 0.03, W / 2 + 0.006), (xx, W / 2 - 0.024)], 0.002, Tk, mat="fit")
            elif e == "Steampunk":
                for s in (-1, 1):
                    p.box((0.018, 0.03, Tk + 0.006), T((s * H * 0.25, W / 2 + 0.004, Tk / 2)), mat="brass")
                cog(p, 0.022, T((0, 0, Tk + 0.002)) @ M(rot=(90, 0, 0)), mat="brass")
            elif e == "Wasteland":
                wrap(p, H * J(p, 0.1, 1), W, Tk, 0.003, "metal")
            else:
                p.box((0.012 if e == "Future" else 0.02, W * 0.4, Tk * (0.35 if e == "Future" else 0.8)), T((H / 2 + 0.006, 0, Tk * (0.2 if e == "Future" else 0.5))), mat="fit", bevel=0)
        else:
            if e != "Future":
                page_block(p, H - 0.004, W - 0.004, Tk - 2 * bt, bt, y=0.002)
            text_front(p, 0, -W / 2 - Tk / 2, Tk / 2, H * 0.35, 0.008, mat="gold" if tier(e) == "hand" else ink(p))
            token(p, 0, 0, Tk if e != "Future" else Tk * 0.4 + 0.002, W * 0.3)


# ================================================================ Scroll (rolls along X)


def scroll(p, slot):
    e, g = p.era, p.region
    L, r = F(p, 0.3, 0.1), F(p, 0.026, 0.15)
    if g == "Ocean":  # rolled pandan mat on a bamboo rod with horn knobs
        if slot == "cover":
            rollx(p, r, L * 0.9, r, mat=pick(p, "rattan", "body", "glass" if e == "Future" else "body"), segs=10)
        elif slot == "spine":
            rollx(p, r * 0.3, L * 1.12, r, mat=pick(p, "bamboo", "fit"), segs=6)
            for s in (-1, 1):
                horn(p, s * L * 0.56, 0, r, r * 1.2, s, mat="accent")
        elif slot == "clasp":
            for s in (-1, 1):
                p.ring(r * 1.04, 0.003, M(loc=(s * L * J(p, 0.25, 0.15), 0, r), rot=(0, 90 + 9 * s, 0)), mat="grip", segs=8)
        else:
            flat(p, [(-L * 0.4, r * 0.8), (L * 0.4, r * 0.8), (L * 0.4, r * 0.8 + J(p, 0.06, 0.3)), (-L * 0.4, r * 0.8 + 0.06)], 0.002, 0, mat=pick(p, "rattan", "body", "glass"))
            text_top(p, 0, r * 0.8 + 0.03, 0.002, L * 0.5, 0.006, mat=ink(p))
            token(p, L * 0.3, r * 0.8 + 0.03, 0.002, 0.03)
    elif g == "Gale":  # leather scroll case with cone caps
        if slot == "cover":
            rollx(p, r * 1.15, L * 0.85, r * 1.15, mat=pick(p, "leather" if e != "Primal" else "hide", "body"), segs=8)
        elif slot == "spine":
            for s in (-1, 1):
                p.cyl(r * 1.25, 0.0, r * 2.0, M(loc=(s * L * 0.425, 0, r * 1.15), rot=(0, 90 * s, 0)), mat=pick(p, "wood", "fit"), segs=7, bevel=0)
        elif slot == "clasp":  # strap
            p.tube([(-L * 0.35, 0, r * 2.2), (0, J(p, 0.02, 0.5), r * 2.3 + 0.12), (L * 0.35, 0, r * 2.2)], 0.004, mat="grip", segs=4)
        else:
            zig(p, r * 1.17, 0, 0.022, 6, M(loc=(0, 0, r * 1.15), rot=(0, 90, 0)))
            token(p, -L * 0.2, 0, r * 2.3, 0.025)
    elif g == "Radiant":  # cloth roll on a rod with brass dome finials and a knotted ribbon
        if slot == "cover":
            rollx(p, r, L * 0.8, r, mat=pick(p, "cloth", "body"), segs=9)
        elif slot == "spine":
            rollx(p, r * 0.3, L, r, mat="fit", segs=6)
            for s in (-1, 1):
                dome(p, r * 0.55, 0, M(loc=(s * L * 0.5, 0, r), rot=(0, 90 * s, 0)), mat="fit", finial=False, segs=7)
        elif slot == "clasp":
            hoop(p, r * 1.05, 0, 0.01, r, mat="accent", segs=9)
            for s in (-1, 1):
                p.tube([(0, -r, r * 0.6), (s * 0.02, -r * 1.4, 0.006), (s * 0.03, -r * 1.6, 0.002)], 0.0025, mat="accent", segs=3)
        else:
            petals(p, 0.012, 0, 5, 0.008, M(loc=(0, -r * 1.02, r), rot=(90, 0, 0)), mat="gold", tilt=0)
            token(p, L * 0.25, 0, r * 2, 0.025)
    else:
        if slot == "cover":
            if tier(e) == "machine":  # tube
                rollx(p, r * 1.3, L * 0.95, r * 1.3, mat="body", segs=8)
            else:
                rollx(p, r, L * 0.85, r, mat=pick(p, "bone", "body", "glass" if e == "Future" else "body"), segs=9)
        elif slot == "spine":
            if e == "Industrial":
                for s in (-1, 1):
                    for i in range(2):
                        rollx(p, r * (1.45 - i * 0.2), 0.02, r * 1.3, x=s * (L * 0.47 + i * 0.02), mat="fit", segs=8)
            elif tier(e) == "machine":
                for s in (-1, 1):
                    rollx(p, r * 1.4, 0.03, r * 1.3, x=s * L * 0.47, mat="fit", segs=8)
            else:
                rollx(p, r * 0.25, L * 1.05, r, mat=pick(p, "wood", "fit"), segs=6)
                for s in (-1, 1):
                    p.ball(r * 0.45, T((s * L * 0.53, 0, r)), mat="fit", segs=(6, 3))
        elif slot == "clasp":
            if tier(e) == "machine":
                p.tube([(-L * 0.4, 0, r * 2.6), (0, 0, r * 2.6 + 0.1), (L * 0.4, 0, r * 2.6)], 0.004, mat="grip", segs=4)
            else:
                hoop(p, r * 1.05, 0, 0.012, r, mat="accent" if e != "Future" else "fit", segs=9)
                p.cyl(0.012, 0.012, 0.004, M(loc=(0, -r * 1.05, r), rot=(90, 0, 0)), mat="paint" if tier(e) == "hand" else "fit", segs=7, bevel=0)
        else:
            if e == "Steampunk":
                cog(p, r * 1.5, M(loc=(L * 0.5, 0, r * 1.3), rot=(0, 0, 90)) @ M(rot=(90, 0, 0)), mat="brass")
            elif e == "Ancient":
                runes_front(p, 0, -r, r, L * 0.4, n=3, h=0.008)
            else:
                text_front(p, 0, -r * (1.3 if tier(e) == "machine" else 1.0), r, L * 0.4, 0.006, mat=ink(p))


# ================================================================ Ledger


def ledger(p, slot):
    e, g = p.era, p.region
    W, D, Tk = F(p, 0.26, 0.1), F(p, 0.18, 0.1), F(p, 0.03, 0.2)
    if g == "Ocean":  # bundle of tally slats, lashed
        n = 5
        sw = D / n
        if slot == "cover":
            for i in range(n):
                slab(p, W * J(p, 1.0, 0.03), sw * 0.9, Tk * 0.6, 0, y=(i - (n - 1) / 2) * sw, mat=pick(p, "bamboo", "body", "glass" if e == "Future" else "body"), bevel=0)
        elif slot == "spine":
            for s in (-1, 1):
                wrap(p, s * W * 0.3, D, Tk * 0.6, 0.003, "grip")
        elif slot == "clasp":  # tally beads on a cord
            for i in range(4):
                p.ball(0.008, T((W * 0.52 + i * 0.012, -D * 0.3, 0.008)), mat="accent", segs=(4, 3))
            horn(p, -W / 2, 0, Tk * 0.6, D * 0.3, -1, mat="accent")
        else:
            for i in range(n):
                for k in range(2):
                    p.box((0.003, sw * 0.5, 0.002), T((-W * 0.3 + k * W * 0.12 + i * 0.01, (i - (n - 1) / 2) * sw, Tk * 0.6 + 0.001)), mat=ink(p), bevel=0)
            token(p, W * 0.25, 0, Tk * 0.6, sw * 0.8)
    elif g == "Gale":  # bead tally board
        if slot == "cover":
            slab(p, W, D, Tk * 0.5, 0, mat=pick(p, "wood", "body"))
        elif slot == "spine":  # bead rods
            for i in range(4):
                y = (i - 1.5) * D * 0.2
                p.cyl(0.002, 0.002, W * 0.9, M(loc=(-W * 0.45, y, Tk * 0.5 + 0.008), rot=(0, 90, 0)), mat="metal" if tier(e) != "hand" else "wood_dark", segs=3, bevel=0)
        elif slot == "clasp":
            for i in range(4):
                y = (i - 1.5) * D * 0.2
                for k in range(p.rng.randint(2, 4)):
                    p.ball(0.008, T((-W * 0.3 + k * 0.018, y, Tk * 0.5 + 0.008)), mat=("accent", "fit")[(i + k) % 2], segs=(4, 3))
        else:
            for s in (-1, 1):
                p.box((W, 0.012, Tk * 0.4), T((0, s * D / 2, Tk * 0.7)), mat="fit", bevel=0)
            pegs(p, W * 0.48, Tk * 0.4, 2, 0.04, mat="body")
            token(p, W * 0.3, 0, Tk * 0.5, D * 0.2)
    elif g == "Radiant":  # bahi-khata: long red book folded lengthwise, tied with string
        if slot == "cover":
            slab(p, W * 1.2, D * 0.45, Tk, 0, mat=pick(p, "paint", "body"))
        elif slot == "spine":
            rollx(p, Tk * 0.5, W * 1.2, Tk * 0.5, y=-D * 0.225, mat=pick(p, "paint", "fit"), segs=7)
        elif slot == "clasp":
            p.tube([(W * 0.6, 0, Tk * 0.5), (W * 0.64, 0, Tk + 0.004), (W * 0.4, 0, Tk + 0.004), (W * 0.2, 0.02, Tk + 0.002)], 0.0025, mat="accent", segs=3)
        else:
            p.ball(0.012, M(loc=(0, 0, Tk), scale=(1, 1, 0.3)), mat="gold", segs=(6, 3))
            petals(p, 0.016, Tk - 0.004, 5, 0.008, mat="gold", tilt=85)
            token(p, -W * 0.35, 0, Tk, D * 0.15)
    else:
        if slot == "cover":
            if tier(e) == "high":
                slab(p, W * 0.8, D, Tk * 0.4, 0, mat="body", bevel=0.3)
                slab(p, W * 0.7, D * 0.85, 0.002, Tk * 0.4, mat="glass" if e == "Future" else "fit", bevel=0)
            elif tier(e) == "machine":  # card tray
                slab(p, W, D * 0.6, Tk * 1.6, 0, mat="body")
            else:
                slab(p, W, D, Tk, 0, mat=pick(p, "leather" if e != "Primal" else "iron"))
        elif slot == "spine":
            if e == "Industrial":
                steps(p, W * 0.9, D * 0.55, Tk * 1.6, 2, 0.006, mat="fit", shrink=0.9)
            elif tier(e) == "machine":
                for i in range(4):
                    slab(p, 0.003, D * 0.55, Tk * 1.2, Tk * 0.4, x=(i - 1.5) * W * 0.2, mat="bone", bevel=0)
            else:
                rollx(p, Tk / 2, W, Tk / 2, y=-D / 2, mat="fit" if tier(e) == "high" else pick(p, "leather"), segs=7)
        elif slot == "clasp":
            if tier(e) == "hand":
                wrap(p, W * 0.25, D, Tk, 0.003, "grip")
                p.ball(0.006, T((W * 0.25, D / 2, Tk * 0.5)), mat="fit", segs=(5, 3))
            else:
                p.box((W * 0.15, 0.01, 0.02), T((0, -D * 0.31 if tier(e) == "machine" else -D / 2, Tk * 0.8)), mat="metal", bevel=0)
        else:
            if tier(e) == "high":
                if e == "Ancient":
                    runes_top(p, 0, 0, Tk * 0.4 + 0.002, W * 0.5, n=4)
                else:
                    text_top(p, 0, 0, Tk * 0.4 + 0.002, W * 0.5, 0.005, rows=3, pitch=D * 0.2, mat="fit")
            else:
                text_front(p, 0, -D / 2 if tier(e) == "hand" else -D * 0.3, Tk * 0.5, W * 0.4, 0.008, mat=ink(p))
                token(p, W * 0.3, 0, Tk if tier(e) == "hand" else Tk * 1.6, D * 0.25)


# ================================================================ Map


def map_(p, slot):
    e, g = p.era, p.region
    W, D, Tk = F(p, 0.26, 0.1), F(p, 0.2, 0.1), F(p, 0.012, 0.2)
    if g == "Ocean":  # stick chart: a lattice of sticks with shell knots
        stick = pick(p, "bamboo", "metal", "fit")
        if slot == "cover":
            for s in (-1, 1):
                p.cyl(0.004, 0.004, W, M(loc=(-W / 2, s * D * 0.4, 0.004), rot=(0, 90, 0)), mat=stick, segs=4, bevel=0)
                p.cyl(0.004, 0.004, D, M(loc=(s * W * 0.45, -D / 2, 0.004), rot=(-90, 0, 0)), mat=stick, segs=4, bevel=0)
        elif slot == "spine":  # curved swell sticks
            for k in range(3):
                pts = [(-W * 0.45, (k - 1) * D * 0.25, 0.008), (0, (k - 1) * D * 0.25 + J(p, 0.03, 0.4), 0.008), (W * 0.45, (k - 1) * D * 0.25, 0.008)]
                p.tube(pts, 0.003, mat=stick, segs=3)
        elif slot == "clasp":  # lashed crossings
            for sx in (-1, 1):
                for sy in (-1, 1):
                    p.ball(0.007, T((sx * W * 0.45, sy * D * 0.4, 0.006)), mat="grip", segs=(4, 3))
        else:  # shells marking islands
            for i in range(p.rng.randint(3, 5)):
                p.ball(0.01, M(loc=(p.rng.uniform(-W * 0.35, W * 0.35), p.rng.uniform(-D * 0.3, D * 0.3), 0.01), scale=(1.3, 1, 0.5)),
                       mat="bone" if tier(e) != "high" else "glass", segs=(5, 3))
            token(p, W * 0.35, -D * 0.4, 0.008, 0.03)
    elif g == "Gale":  # painted hide spread on four corner pegs
        if slot == "cover":
            flat(p, [(-W / 2, -D * 0.45), (-W * 0.2, -D / 2), (W / 2, -D * 0.4), (W * 0.45, D / 2), (-W * 0.48, D * 0.45)], Tk * 0.5, 0,
                 mat=pick(p, "hide", "body"))
        elif slot == "spine":
            for (x, y) in ((-W / 2, -D * 0.45), (W / 2, -D * 0.4), (W * 0.45, D / 2), (-W * 0.48, D * 0.45)):
                p.cyl(0.006, 0.003, 0.03, T((x, y, 0)), mat=pick(p, "wood", "metal"), segs=4, bevel=0)
        elif slot == "clasp":  # route
            pts = [(-W * 0.35, -D * 0.3, Tk * 0.5 + 0.002), (-W * 0.1, D * 0.1, Tk * 0.5 + 0.002), (W * 0.15, -D * 0.05, Tk * 0.5 + 0.002), (W * 0.35, D * J(p, 0.3, 0.3), Tk * 0.5 + 0.002)]
            p.tube(pts, 0.002, mat="accent", segs=3)
        else:
            for i in range(6):
                p.box((W * 0.1, 0.012, 0.002), M(loc=(-W * 0.3 + i * W * 0.12, D * 0.38, Tk * 0.5 + 0.001), rot=(0, 0, 30 if i % 2 else -30)), mat=("accent", "fit")[i % 2], bevel=0)
            token(p, W * 0.3, -D * 0.3, Tk * 0.5, 0.03)
    elif g == "Radiant":  # round painted cloth map with a lotus border
        R = min(W, D) * 0.55
        if slot == "cover":
            p.cyl(R, R, Tk * 0.5, mat=pick(p, "cloth", "body", "glass" if e == "Future" else "body"), segs=12, bevel=0)
        elif slot == "spine":  # rings of the world
            for k in (0.4, 0.75):
                p.ring(R * k, 0.002, T((0, 0, Tk * 0.5 + 0.001)), mat="accent", segs=10)
        elif slot == "clasp":
            p.ball(0.012, M(loc=(0, 0, Tk * 0.5), scale=(1, 1, 0.4)), mat="gold", segs=(6, 3))
        else:
            petals(p, R * 0.95, Tk * 0.3, 6, 0.012, mat="accent", tilt=85)
            token(p, R * 0.5, 0, Tk * 0.5, 0.03)
    else:
        if slot == "cover":
            if tier(e) == "high":
                p.cyl(min(W, D) * 0.35, min(W, D) * 0.33, Tk * 2, mat="body", segs=10, bevel=0.2)
            elif tier(e) == "machine":
                slab(p, W, D, Tk * 1.2, 0, mat="body")
                sheets(p, W * 0.9, D * 0.85, Tk * 1.2, 1, mat="bone")
            else:
                for i in range(2):
                    slab(p, W * 0.5, D, Tk * 0.4, i * Tk * 0.4, x=(i - 0.5) * W * 0.02, mat="bone" if e != "Primal" else "hide", bevel=0)
        elif slot == "spine":
            if tier(e) == "high":
                p.cyl(min(W, D) * 0.3, min(W, D) * 0.2, Tk * 3, T((0, 0, Tk * 2)), mat="glass", segs=8, bevel=0)
            elif e == "Industrial":
                steps(p, W * 0.25, 0.03, Tk * 1.2, 2, 0.008, M(loc=(0, D * 0.45, 0)), mat="fit", shrink=0.8)
            else:
                p.box((W * 0.9 if tier(e) == "machine" else W * 0.02, 0.02, 0.012), T((0, D * 0.45, Tk * 1.5)), mat="fit", bevel=0)
        elif slot == "clasp":  # dividers or pencil
            p.tube([(-W * 0.1, -D * 0.1, Tk * 2), (0, 0, Tk * 2 + 0.03), (W * 0.1, -D * 0.12, Tk * 2)], 0.0025, mat="metal" if e != "Primal" else "bone", segs=3)
        else:
            if e == "Ancient":
                runes_top(p, 0, 0, Tk * 2, W * 0.3, n=3)
            elif e == "Steampunk":
                cog(p, 0.03, T((W * 0.3, 0, Tk * 1.5)) @ M(rot=(90, 0, 0)), mat="brass")
            else:
                for k in (0.3, 0.55):
                    p.ring(min(W, D) * k * 0.5, 0.002, T((-W * 0.1, 0, Tk * (2 if tier(e) == "high" else 1.3) + 0.001)), mat=ink(p), segs=8)


# ================================================================ Letter


def letter(p, slot):
    e, g = p.era, p.region
    W, D, Tk = F(p, 0.16, 0.1), F(p, 0.1, 0.1), F(p, 0.012, 0.2)
    if g == "Ocean":  # rolled leaf letter in a bamboo tube
        r = D * 0.22
        if slot == "cover":
            rollx(p, r, W, r, mat=pick(p, "bamboo", "body", "glass" if e == "Future" else "body"), segs=7)
        elif slot == "spine":
            for s in (-1, 1):
                rollx(p, r * 1.08, 0.006, r, x=s * W * 0.5, mat=pick(p, "bamboo", "fit"), segs=7)
        elif slot == "clasp":
            lash(p, r, 0, 0.02, M(loc=(0, 0, r), rot=(0, 90, 0)), segs=7)
        else:
            rollx(p, r * 0.6, 0.03, r, x=W * 0.5 + 0.015, mat="bone" if tier(e) != "high" else "fit", segs=6)
            horn(p, -W * 0.5, 0, r, r * 1.4, -1, mat="accent")
    elif g == "Gale":  # beaded leather pouch
        if slot == "cover":
            slab(p, W * 0.8, D, Tk * 1.6, 0, mat=pick(p, "leather" if e != "Primal" else "hide", "body"), bevel=0.3)
        elif slot == "spine":  # flap
            flat(p, [(-W * 0.4, -D * 0.1), (W * 0.4, -D * 0.1), (0, -D * 0.5)], 0.003, Tk * 1.6, mat=pick(p, "leather" if e != "Primal" else "hide", "fit"))
        elif slot == "clasp":
            p.ball(0.008, T((0, -D * 0.45, Tk * 1.6)), mat="accent", segs=(4, 3))
            p.tube([(-W * 0.4, D * 0.4, Tk), (-W * 0.6, D * 0.6, 0.004)], 0.002, mat="grip", segs=3)
        else:
            for i in range(5):
                p.ball(0.005, T(((i - 2) * W * 0.12, -D * 0.5, Tk * 0.8)), mat=("accent", "fit")[i % 2], segs=(4, 3))
            token(p, W * 0.2, D * 0.2, Tk * 1.6, 0.025)
    elif g == "Radiant":  # envelope with a red thread and a lotus seal
        if slot == "cover":
            slab(p, W, D, Tk * 0.6, 0, mat=pick(p, "bone", "body", "glass" if e == "Future" else "body"), bevel=0)
        elif slot == "spine":
            flat(p, [(-W / 2, D / 2), (W / 2, D / 2), (0, -D * 0.1)], 0.002, Tk * 0.6, mat=pick(p, "bone", "fit"))
        elif slot == "clasp":
            wrap(p, W * J(p, 0.15, 0.4), D, Tk * 0.6, 0.0018, "paint")
        else:
            petals(p, 0.01, Tk * 0.6, 5, 0.007, T((0, -D * 0.05, 0)), mat="accent", tilt=85)
            text_top(p, -W * 0.2, D * 0.25, Tk * 0.6, W * 0.4, 0.004, mat=ink(p))
    else:
        if slot == "cover":
            if tier(e) == "machine":  # parcel / capsule
                if e == "Steampunk":
                    rollx(p, D * 0.3, W, D * 0.3, mat="brass", segs=8)
                else:
                    slab(p, W, D, Tk * 3, 0, mat="body" if e != "Industrial" else "bark")
            elif tier(e) == "high":
                slab(p, W * 0.5, D * 0.6, Tk * 0.5, 0, mat="body", bevel=0.4)
            else:
                slab(p, W, D, Tk * 0.6, 0, mat="bone" if e != "Primal" else "hide", bevel=0)
        elif slot == "spine":
            if e == "Steampunk":
                for s in (-1, 1):
                    rollx(p, D * 0.32, 0.01, D * 0.3, x=s * W * 0.4, mat="cloth", segs=8)
            elif tier(e) == "machine":
                wrap(p, 0, D, Tk * 3, 0.002, "rope")
                wrap(p, 0, W, Tk * 3, 0.002, "rope", axis="y")
            elif tier(e) == "high":
                p.ring(0.008, 0.002, M(loc=(W * 0.27, 0, Tk * 0.25), rot=(90, 0, 0)), mat="fit", segs=6)
            else:
                flat(p, [(-W / 2, D / 2), (W / 2, D / 2), (0, 0)], 0.002, Tk * 0.6, mat="bone" if e != "Primal" else "hide")
        elif slot == "clasp":
            z = Tk * 3 if tier(e) == "machine" and e != "Steampunk" else D * 0.6 if e == "Steampunk" else Tk * 0.6
            if tier(e) == "hand":
                p.cyl(0.012, 0.012, 0.004, T((0, 0, z)), mat="paint", segs=7, bevel=0)
            elif tier(e) == "high":
                p.box((W * 0.3, D * 0.3, 0.002), T((0, 0, Tk * 0.5 + 0.001)), mat="glass" if e == "Future" else "fit", bevel=0)
            else:
                p.box((W * 0.3, D * 0.3, 0.002), T((W * 0.15, D * 0.1, z + 0.001)), mat="bone", bevel=0)
        else:
            if e == "Ancient":
                runes_top(p, 0, 0, Tk * 0.5, W * 0.3, n=2)
            elif e == "Industrial":
                steps(p, W * 0.15, D * 0.15, Tk * 3, 2, 0.002, mat="paint", shrink=0.7)
            else:
                token(p, -W * 0.25, 0, Tk * (3 if tier(e) == "machine" and e != "Steampunk" else 0.6), 0.025)
                if tier(e) == "hand":
                    text_top(p, W * 0.1, -D * 0.2, Tk * 0.6, W * 0.4, 0.004, rows=2, pitch=D * 0.15, mat=ink(p))
                if e == "Steampunk":
                    p.box((W * 0.3, 0.003, D * 0.15), T((0, -D * 0.3, D * 0.3)), mat="glass", bevel=0)


# ================================================================ Newspaper


def newspaper(p, slot):
    e, g = p.era, p.region
    W, D, Tk = F(p, 0.28, 0.1), F(p, 0.2, 0.1), F(p, 0.01, 0.2)
    sheet = pick(p, "bone" if e != "Primal" else "cloth", "bone", "glass" if e == "Future" else "body")
    if g == "Ocean":  # rolled sheet tied with rattan
        r = D * 0.12
        if slot == "cover":
            rollx(p, r, W * 0.9, r, mat=sheet, segs=8)
        elif slot == "spine":
            flat(p, [(-W * 0.45, r * 0.8), (W * 0.45, r * 0.8), (W * 0.45, r * 0.8 + D * 0.3), (-W * 0.45, r * 0.8 + D * 0.3)], 0.002, 0, mat=sheet)
        elif slot == "clasp":
            p.ring(r * 1.05, 0.003, M(loc=(W * J(p, 0.1, 1), 0, r), rot=(0, 90, 0)), mat="grip", segs=8)
            horn(p, W * 0.45, 0, r * 1.6, r, 1, mat="accent")
        else:
            text_top(p, 0, r * 0.8 + D * 0.15, 0.002, W * 0.6, 0.008, rows=2, pitch=D * 0.1, mat=ink(p))
    elif g == "Gale":  # folded sheet weighted by a bead string, zigzag masthead
        if slot == "cover":
            slab(p, W * 0.5, D, Tk, 0, mat=sheet, bevel=0)
        elif slot == "spine":
            p.cyl(Tk * 0.5, Tk * 0.5, D, M(loc=(-W * 0.25, -D / 2, Tk * 0.5), rot=(-90, 0, 0)), mat=sheet, segs=5, bevel=0)
        elif slot == "clasp":
            for i in range(6):
                p.ball(0.006, T((W * 0.27, (i - 2.5) * D * 0.12, 0.006)), mat=("accent", "fit")[i % 2], segs=(4, 3))
        else:
            for i in range(5):
                p.box((W * 0.08, 0.012, 0.002), M(loc=(-W * 0.18 + i * W * 0.09, -D * 0.38, Tk + 0.001), rot=(0, 0, 30 if i % 2 else -30)), mat=("accent", "fit")[i % 2], bevel=0)
            text_top(p, 0, D * 0.1, Tk, W * 0.35, 0.006, rows=3, pitch=D * 0.12, mat=ink(p))
    elif g == "Radiant":  # folded sheet with a lotus masthead, string tie
        if slot == "cover":
            slab(p, W * 0.5, D, Tk, 0, mat=sheet, bevel=0)
        elif slot == "spine":
            slab(p, W * 0.48, D * 0.98, Tk * 0.6, Tk, x=W * 0.005, mat=sheet, rz=J(p, 3, 1), bevel=0)
        elif slot == "clasp":
            wrap(p, 0, D, Tk * 1.6, 0.0018, "accent")
        else:
            petals(p, 0.012, Tk * 1.6, 5, 0.008, T((-W * 0.15, -D * 0.35, 0)), mat="accent", tilt=85)
            text_top(p, W * 0.05, D * 0.05, Tk * 1.6, W * 0.3, 0.006, rows=3, pitch=D * 0.12, mat=ink(p))
    else:
        if slot == "cover":
            if tier(e) == "high":
                slab(p, W * 0.5, D, Tk * 0.6, 0, mat="body" if e != "Future" else "glass", bevel=0.3)
            else:
                slab(p, W * 0.5, D, Tk, 0, mat=sheet, bevel=0)
        elif slot == "spine":
            if e == "Steampunk":
                rollx(p, 0.008, W * 0.6, Tk, mat="brass", segs=6)
            elif tier(e) == "high":
                rollx(p, Tk * 0.8, W * 0.52, Tk * 0.6, y=-D / 2, mat="fit", segs=6)
            else:
                slab(p, W * 0.48, D * 0.98, Tk * 0.5, Tk, mat=sheet, rz=J(p, 4, 1), bevel=0)
        elif slot == "clasp":
            if e == "Industrial":
                steps(p, W * 0.4, 0.02, Tk * 1.5, 2, 0.003, M(loc=(0, -D * 0.38, 0)), mat="paint", shrink=0.8)
            elif e == "Wasteland":
                p.box((0.02, 0.03, 0.012), T((W * 0.22, 0, Tk * 1.5)), mat="metal", bevel=0)
            else:
                wrap(p, W * J(p, 0.1, 1), D, Tk * 1.5, 0.0018, "rubber" if tier(e) == "machine" else "grip")
        else:
            if e == "Ancient":
                runes_top(p, 0, 0, Tk * 0.6, W * 0.3, n=3)
            else:
                text_top(p, 0, 0, Tk * (1.5 if tier(e) != "high" else 0.6), W * 0.35, 0.006, rows=3, pitch=D * 0.15, mat=ink(p) if e != "Future" else "fit")
                token(p, W * 0.15, D * 0.35, Tk * 1.5, 0.02)


# ================================================================ Notice (scene, floor contact at z = 0)


def notice(p, slot):
    e, g = p.era, p.region
    Hn, Bw, Bh = F(p, 1.9, 0.08), F(p, 0.9, 0.1), F(p, 0.7, 0.1)
    zb = Hn - Bh - 0.25
    if slot == "spine":  # post, pillar or column
        if g == "Ocean":  # two bamboo posts on stone footings
            for s in (-1, 1):
                p.cyl(0.05, 0.045, Hn, T((s * (Bw / 2 + 0.05), 0, 0)), mat=pick(p, "bamboo", "body"), segs=7, bevel=0)
                p.cyl(0.1, 0.09, 0.08, T((s * (Bw / 2 + 0.05), 0, 0)), mat="stone", segs=6, bevel=0)
        elif g == "Gale":  # one mud pillar
            p.cyl(0.22, 0.16, Hn - 0.1, mat=pick(p, "clay", "body"), segs=8, bevel=0)
        elif g == "Radiant":  # two turned pillars
            for s in (-1, 1):
                p.lathe([(0.08, 0), (0.08, 0.1), (0.05, 0.2), (0.045, Hn * 0.8), (0.06, Hn * 0.85), (0.05, Hn - 0.15)], T((s * (Bw / 2 + 0.06), 0, 0)), mat="body", segs=8)
        else:
            if e == "Industrial":
                steps(p, Bw * 0.5, 0.3, 0, 3, 0.08, mat="body", shrink=0.8)
                p.box((0.08, 0.08, Hn), T((0, 0.05, Hn / 2)), mat="metal", bevel=0)
            elif tier(e) == "high":
                p.box((0.12, 0.18, Hn), T((0, 0.05, Hn / 2)), mat="body", bevel=0.3)
            else:
                for s in (-1, 1):
                    p.box((0.06, 0.06, Hn - 0.1), T((s * (Bw / 2 + 0.03), 0, (Hn - 0.1) / 2)), mat=pick(p, "wood_dark" if e != "Primal" else "iron", "metal"))
    elif slot == "cover":  # the board and its papers
        y = -0.24 if g == "Gale" else -0.02
        if g == "Radiant" or g == "Ocean" or g == "Metropolis":
            slab(p, Bw, 0.03, Bh, zb, y=y + 0.01, mat=pick(p, "wood", "body", "glass" if e == "Future" else "body"))
        else:
            slab(p, Bw * 0.8, 0.03, Bh, zb, y=y, mat=pick(p, "wood", "body"))
        for i in range(p.rng.randint(2, 4)):
            w, h = J(p, 0.2, 0.25), J(p, 0.26, 0.25)
            x = p.rng.uniform(-Bw * 0.3, Bw * 0.3)
            z = p.rng.uniform(zb + h / 2 + 0.03, zb + Bh - h / 2 - 0.03)
            if e == "Ancient":
                runes_front(p, x, y - 0.006, z, w, n=3, h=0.03)
            else:
                p.box((w, 0.003, h), M(loc=(x, y - 0.006, z), rot=(0, p.rng.uniform(-8, 8), 0)), mat=("bone", "paint", "cloth")[i % 3] if e != "Future" else "glass", bevel=0)
    elif slot == "clasp":  # frame and pins
        y = -0.24 if g == "Gale" else -0.02
        if g == "Ocean":
            lash(p, 0.05, zb + Bh * 0.5, 0.06, T((-(Bw / 2 + 0.05), 0, 0)), segs=6)
            lash(p, 0.05, zb + Bh * 0.5, 0.06, T(((Bw / 2 + 0.05), 0, 0)), segs=6)
        elif g == "Gale":
            pegs(p, 0.2, zb - 0.1, 5, 0.18, mat="body")
        elif g == "Radiant":
            for z in (zb - 0.02, zb + Bh + 0.02):
                p.box((Bw + 0.06, 0.05, 0.04), T((0, y, z)), mat="fit")
        else:
            for z in (zb - 0.02, zb + Bh + 0.02):
                p.box((Bw + 0.06, 0.05, 0.035), T((0, y + 0.005, z)), mat="fit" if tier(e) != "hand" else "wood_dark")
        for i in range(3):
            p.ball(0.01, T((p.rng.uniform(-Bw * 0.35, Bw * 0.35), y - 0.02, p.rng.uniform(zb + 0.1, zb + Bh - 0.05))), mat="metal" if tier(e) != "hand" else "bone", segs=(4, 3))
    else:  # roof
        zr = Hn - 0.1
        if g == "Ocean":  # saddle roof with horned ends
            for s in (-1, 1):
                p.box((Bw + 0.4, 0.3, 0.02), M(loc=(0, s * 0.11, zr + 0.06), rot=(s * 28, 0, 0)), mat=pick(p, "rattan", "fit"), bevel=0)
            for s in (-1, 1):
                horn(p, s * (Bw / 2 + 0.2), 0, zr + 0.1, 0.18, s, mat="accent")
        elif g == "Gale":  # cone cap and zigzag frieze
            p.cyl(0.3, 0.0, 0.45, T((0, 0, Hn - 0.12)), mat=pick(p, "bark", "fit"), segs=7, bevel=0)
            zig(p, 0.2, Hn * 0.4, 0.12, 8)
        elif g == "Radiant":  # chhatri dome on a slab
            p.box((Bw + 0.3, 0.35, 0.05), T((0, 0, zr)), mat="body", bevel=0)
            dome(p, 0.22, zr + 0.025, mat="fit", segs=8)
            petals(p, 0.22, zr + 0.02, 6, 0.04, mat="accent", tilt=70)
        else:
            if e == "Industrial":
                steps(p, Bw + 0.1, 0.12, zr, 3, 0.04, mat="fit", shrink=0.8)
            elif tier(e) == "high":
                for z in (zb - 0.06, zb + Bh + 0.06):
                    p.box((Bw + 0.12, 0.1, 0.06), T((0, 0.0, z)), mat="fit", bevel=0.2)
            elif e == "Steampunk":
                p.box((Bw + 0.2, 0.2, 0.04), T((0, 0, zr)), mat="brass", bevel=0)
                for s in (-1, 1):
                    gear(p, 0.08, M(loc=(s * (Bw / 2 + 0.05), -0.04, zb + Bh * 0.5), rot=(90, 0, 0)), mat="brass")
            elif e == "Wasteland":
                p.box((Bw + 0.25, 0.3, 0.012), M(loc=(0, -0.08, zr), rot=(-J(p, 14, 0.3), J(p, 4, 1), 0)), mat="metal", bevel=0)
            else:
                p.box((Bw + 0.3, J(p, 0.3, 0.15), 0.03), M(loc=(0, -0.08, zr), rot=(-J(p, 18, 0.3), 0, 0)), mat=pick(p, "wood_dark" if e != "Primal" else "hide"))


for _g in REGIONS:
    regional("Book", _g)(book)
    regional("Scroll", _g)(scroll)
    regional("Ledger", _g)(ledger)
    regional("Map", _g)(map_)
    regional("Letter", _g)(letter)
    regional("Newspaper", _g)(newspaper)
    regional("Notice", _g)(notice)
