"""Vessel set 3: SewingKit, AlchemySet, Quiver, Teaset, Tableware (cosmos_chimera P1-19, ADR-0016).

Slots are kit_forms.VESSEL (body, lid, handle, band). Frame as forms_vessel: Z up, front -Y, origin at the floor
contact (an NPC carries a vessel on the shoulder; a floor spot shrinks it into a 0.42 m footprint).
Sets of several pieces (tea set, tableware, alchemy glassware) stand together on one footprint: the body slot is
the main piece, lid its cover, handle the grips, spouts, stands or utensils, band the companion pieces and trims.
Each form draws its F() frame values first, in a fixed order, so every slot of one (function, era) shares them.
Containers and kitchenware do not glow; Steampunk, Future, Wasteland and Ancient keep their era glow as small
accents (a gauge, a seam, a rune), as the earlier vessels do.
"""
import math

from mathutils import Matrix

from forms_tools import disk, rod
from forms_vessel import bail, closed, shell
from kit_forms import VESSEL, F, J, coin, function
from kit_lib import M

T = Matrix.Translation
TAU = math.tau


def blk(p, x, y, z, w, d, h, mat="body", b=0, **kw):
    """Box with its bottom face at z."""
    p.box((w, d, h), T((x, y, z + h / 2)), mat=mat, bevel=b, **kw)


def bowl(p, r, h, loc, mat="ceramic", segs=10, foot=0.0):
    x, y, z = loc
    outer = [(r * 0.45, 0), (r * 0.8, h * 0.35), (r, h)] if not foot else [(r * 0.4, 0), (r * 0.42, foot), (r * 0.8, h * 0.45), (r, h)]
    shell(p, outer, max(0.003, r * 0.08), m=T((x, y, z)), mat=mat, segs=segs)


def plate(p, r, loc, mat="ceramic", segs=12, h=0.012):
    x, y, z = loc
    p.lathe([(0, 0), (r * 0.6, 0), (r, h), (r * 0.92, h), (r * 0.55, h * 0.35), (0, h * 0.35)], T((x, y, z)), mat=mat, segs=segs)


def cup(p, r, h, loc, mat="ceramic", segs=8, handle=False, hmat=None):
    x, y, z = loc
    shell(p, [(r * 0.7, 0), (r * 0.9, h * 0.4), (r, h)], max(0.002, r * 0.12), m=T((x, y, z)), mat=mat, segs=segs)
    if handle:
        p.tube([(x + r * 0.9, y, z + h * 0.75), (x + r * 1.45, y, z + h * 0.6), (x + r * 0.9, y, z + h * 0.25)], h * 0.07, mat=hmat or mat, segs=4)


def needle(p, a, b, mat="steel"):
    rod(p, a, b, 0.0012, 0.0004, mat=mat, segs=3)


def spool(p, x, y, z, r, h, thread="cloth", end="wood", axis="z"):
    m = T((x, y, z)) if axis == "z" else T((x, y, z)) @ M(rot=(0, 90, 0))
    p.cyl(r * 0.8, r * 0.8, h, m, mat=thread, segs=7)
    for zz in (0.0, h):
        p.cyl(r, r, 0.003, m @ T((0, 0, zz - 0.0015)), mat=end, segs=7)


def arrow(p, x, y, z0, L, rot=(0, 0, 0), fletch="feather", shaft="wood", tip=None):
    m = T((x, y, z0)) @ M(rot=rot)
    p.cyl(0.0035, 0.0035, L, m, mat=shaft, segs=4)
    for i in range(3):
        p.box((0.0012, 0.012, 0.05), m @ M(loc=(0, 0, L - 0.04), rot=(0, 0, i * 120)) @ T((0, 0.007, 0)), mat=fletch, bevel=0)
    if tip:
        p.cyl(0.006, 0.0005, 0.03, m @ T((0, 0, -0.03)) @ M(rot=(180, 0, 0)) @ T((0, 0, -0.03)), mat=tip, segs=4)


# ================================================================ SewingKit
@function("SewingKit", "Vessel", VESSEL, "carried")
def sewing_kit(p, slot):
    e = p.era
    W, D, H = F(p, 0.2, 0.1), F(p, 0.13, 0.1), F(p, 0.08, 0.12)
    if e == "Primal":  # hide pouch with bone needles
        prof = [(W * 0.35, 0), (W * 0.5, H * 0.5), (W * 0.42, H), (W * 0.15, H * 1.25)]
        if slot == "body":
            closed(p, prof, m=M(scale=(1, D / W, 1)), mat="hide", segs=8, noise=0.05)
        elif slot == "lid":  # drawstring neck
            p.ring(W * 0.17, 0.006, T((0, 0, H * 1.18)) @ M(scale=(1, D / W, 1)), mat="rope", segs=6, square=False)
        elif slot == "handle":
            p.tube([(-W * 0.15, 0, H * 1.2), (-W * 0.35, 0.01, H * 1.6), (W * 0.2, 0, H * J(p, 1.7, 0.1)), (W * 0.15, 0, H * 1.2)], 0.004, mat="rope", segs=3)
        else:
            for i in range(3):
                needle(p, (W * (0.05 + i * 0.05), -D * 0.2, H * 1.1), (W * (0.1 + i * 0.06), -D * 0.25, H * J(p, 1.7, 0.1)), mat="bone")
    elif e == "Agrarian":  # round lidded basket with spools
        prof = [(W * 0.42, 0), (W * 0.5, H * 0.8), (W * 0.5, H)]
        if slot == "body":
            shell(p, prof, 0.006, mat="wood", segs=12)
            for z in (H * 0.3, H * 0.65):
                p.ring(W * 0.48, 0.003, T((0, 0, z)), mat="rope", segs=12, square=False)
        elif slot == "lid":
            p.lathe([(W * 0.52, H), (W * 0.52, H + 0.012), (W * 0.3, H + 0.02), (0, H + J(p, 0.024, 0.2))], mat="wood", segs=12)
        elif slot == "handle":
            p.ball(0.012, T((0, 0, H + 0.03)), mat="wood_dark", segs=(6, 4))
        else:
            spool(p, W * 0.6, -D * 0.2, 0, 0.018, 0.03)
            needle(p, (W * 0.2, -W * 0.3, H + 0.02), (W * 0.4, -W * 0.4, H + J(p, 0.04, 0.3)), mat="iron")
    elif e == "Mercantile":  # wooden sewing box with brass corners
        if slot == "body":
            blk(p, 0, 0, 0, W, D, H, mat="wood_dark", b=0.04)
        elif slot == "lid":
            blk(p, 0, 0, H, W * 1.02, D * 1.02, J(p, 0.025, 0.2), mat="wood_dark", b=0.06)
            p.box((W * 0.5, 0.002, 0.012), T((0, -D * 0.51, H + 0.012)), mat="brass", bevel=0)
        elif slot == "handle":
            bail(p, W * 0.18, H + 0.025, J(p, 0.03, 0.2), 0.003, mat="brass")
        else:
            for sx in (-1, 1):
                for sy in (-1, 1):
                    p.box((0.012, 0.012, H * 0.95), T((sx * W * 0.5, sy * D * 0.5, H * 0.5)), mat="brass", bevel=0)
            spool(p, W * 0.7, 0, 0, 0.015, 0.03, thread="paint")
    elif e == "Industrial":  # steel tool case with cantilever trays
        if slot == "body":
            blk(p, 0, 0, 0, W, D, H, mat="paint")
        elif slot == "lid":
            for s in (-1, 1):
                p.box((W * 0.5, D * 0.95, 0.008), M(loc=(s * W * 0.25, 0, H + 0.02), rot=(0, s * -J(p, 20, 0.3), 0)), mat="paint", bevel=0)
        elif slot == "handle":
            bail(p, W * 0.2, H + 0.02, 0.035, 0.004, mat="steel")
        else:
            p.box((W * 1.0, 0.004, 0.01), T((0, -D * 0.5, H * 0.75)), mat="steel", bevel=0)
            spool(p, -W * 0.15, 0, H, 0.012, 0.025, thread="cloth", end="steel")
            p.box((0.05, 0.005, 0.008), M(loc=(W * 0.15, 0, H + 0.01), rot=(0, 0, 30)), mat="steel", bevel=0)
    elif e == "Steampunk":  # brass needle case: cylinder on its side with a gauge
        r = H * 0.6
        if slot == "body":
            p.cyl(r, r, W, T((0, 0, r)) @ M(rot=(0, 90, 0)) @ T((0, 0, -W / 2)), mat="brass", segs=10)
            for s in (-1, 1):
                p.box((0.02, D * 0.8, 0.01), T((s * W * 0.35, 0, 0.005)), mat="copper", bevel=0)
        elif slot == "lid":
            for s in (-1, 1):
                disk(p, (s * W / 2, 0, r), r * 1.06, 0.012, "x", "copper", segs=10)
        elif slot == "handle":
            p.tube([(-W * 0.3, 0, r * 2), (0, 0, r * 2 + J(p, 0.03, 0.2)), (W * 0.3, 0, r * 2)], 0.004, mat="leather", segs=3)
        else:
            disk(p, (0, -r, r), r * 0.4, 0.006, "y", "steel", segs=8)
            disk(p, (0, -r - 0.004, r), r * 0.3, 0.002, "y", "glow", segs=8)
    elif e == "Future":  # auto-suturer: rounded shell with nozzle and spool window
        if slot == "body":
            p.box((W, D, H), T((0, 0, H / 2)), mat="body", bevel=0.4, bevel_seg=2)
        elif slot == "lid":
            p.box((W * 0.5, 0.004, H * 0.4), T((-W * 0.15, -D / 2, H * 0.55)), mat="glass", bevel=0)
        elif slot == "handle":
            rod(p, (W * 0.5, -D * 0.2, H * 0.5), (W * 0.5 + J(p, 0.05, 0.2), -D * 0.4, H * 0.5), 0.008, 0.003, mat="shell_dark", segs=6)
        else:
            p.box((W * 0.9, 0.004, 0.006), T((0, -D / 2 - 0.001, H * 0.2)), mat="glow", bevel=0)
            spool(p, -W * 0.15, -D * 0.3, H * 0.4, 0.012, 0.02, thread="paint", end="shell_dark", axis="x")
    elif e == "Wasteland":  # cookie-tin kit tied with wire
        if slot == "body":
            p.cyl(W * 0.5, W * 0.5, H, mat="rust", segs=12)
        elif slot == "lid":
            p.cyl(W * 0.52, W * 0.52, 0.02, T((0, 0, H - 0.005 + J(p, 0.01, 0.5))), mat="paint", segs=12)
        elif slot == "handle":
            p.tube([(-W * 0.5, 0, H * 0.5), (0, 0, H + 0.03), (W * 0.5, 0, H * 0.5)], 0.0025, mat="iron", segs=3)
        else:
            spool(p, W * 0.7, 0, 0, 0.014, 0.03, thread="cloth", end="steel")
            needle(p, (0, -W * 0.3, H + 0.02), (W * 0.1, -W * 0.3, H + J(p, 0.05, 0.2)))
    else:  # Ancient: stone case with a glowing needle groove
        if slot == "body":
            blk(p, 0, 0, 0, W, D, H, mat="stone", b=0.25)
        elif slot == "lid":
            blk(p, 0, 0, H, W * 0.96, D * 0.96, J(p, 0.02, 0.2), mat="stone_dark", b=0.3)
        elif slot == "handle":
            for s in (-1, 1):
                p.box((0.015, D * 0.5, 0.02), T((s * W * 0.52, 0, H * 0.6)), mat="stone_dark", bevel=0)
        else:
            p.box((W * 0.7, 0.004, 0.006), T((0, -D * 0.5, H * 0.5)), mat="glow", bevel=0)
            p.box((W * J(p, 0.3, 0.3), 0.004, 0.004), T((0, -D * 0.5, H * 0.3)), mat="glow", bevel=0)


# ================================================================ AlchemySet
def flask(p, x, y, z, r, h, mat="glass", segs=8):
    p.lathe([(0, 0), (r, 0.0), (r * 1.05, h * 0.3), (r * 0.6, h * 0.65), (r * 0.25, h * 0.75), (r * 0.25, h), (0, h)], T((x, y, z)), mat=mat, segs=segs)


def tube_rack(p, x, y, n, W, h, mat="wood"):
    blk(p, x, y, 0, W, 0.04, 0.01, mat=mat)
    blk(p, x, y, h * 0.6, W, 0.04, 0.008, mat=mat)
    for i in range(n):
        xx = x - W * 0.4 + W * 0.8 * i / max(1, n - 1)
        p.cyl(0.006, 0.006, h * 0.9, T((xx, y, 0.01)), mat="glass", segs=6)


@function("AlchemySet", "Vessel", VESSEL, "carried")
def alchemy_set(p, slot):
    e = p.era
    R, H = F(p, 0.1, 0.1), F(p, 0.16, 0.1)
    if e == "Primal":  # clay bowl and stone pestle
        if slot == "body":
            bowl(p, R, H * 0.45, (0, 0, 0), mat="ceramic", segs=10)
        elif slot == "lid":  # herbs heaped inside
            p.ball(1.0, M(loc=(0, 0, H * 0.3), scale=(R * 0.65, R * 0.6, H * 0.12)), mat="cloth", segs=(7, 4), noise=0.05)
        elif slot == "handle":
            p.lathe([(0, 0), (R * 0.22, 0.01), (R * 0.15, H * 0.5), (R * 0.12, H * J(p, 0.75, 0.1)), (0, H * 0.78)],
                    M(loc=(R * 0.3, 0, H * 0.18), rot=(0, 25, 0)), mat="stone", segs=6, noise=0.04)
        else:
            p.ball(1.0, M(loc=(R * 1.4, -R * 0.4, 0.02), scale=(R * 0.4, R * 0.35, 0.025)), mat="stone_dark", segs=(6, 4), noise=0.04)
    elif e == "Agrarian":  # elixir furnace: tripod cauldron with lid
        prof = [(R * 0.5, H * 0.25), (R, H * 0.5), (R * 0.85, H * 0.85)]
        if slot == "body":
            shell(p, prof, 0.008, mat="iron", segs=10)
        elif slot == "lid":
            p.lathe([(R * 0.88, H * 0.85), (R * 0.6, H * 0.95), (R * 0.2, H * 1.0), (R * 0.15, H * J(p, 1.08, 0.05)), (0, H * 1.1)], mat="iron", segs=10)
        elif slot == "handle":  # three legs and ear handles
            for i in range(3):
                a = i * TAU / 3
                rod(p, (math.cos(a) * R * 0.6, math.sin(a) * R * 0.6, H * 0.3), (math.cos(a) * R * 0.8, math.sin(a) * R * 0.8, 0), 0.008, 0.006, mat="iron")
            for s in (-1, 1):
                p.ring(0.02, 0.004, M(loc=(s * R * 0.9, 0, H * 0.92), rot=(0, 90, 0)), mat="iron", segs=6)
        else:
            for i in range(2):
                p.lathe([(0, 0), (0.02, 0.01), (0.015, 0.04), (0.006, 0.05), (0.008, 0.06)], T((R * 1.4, (i - 0.5) * R * 0.8, 0)), mat="ceramic", segs=7)
    elif e == "Mercantile":  # glass alembic set on a wooden stand
        if slot == "body":
            flask(p, 0, 0, 0.04, R * 0.6, H)
        elif slot == "lid":  # alembic head with its long neck
            p.ball(R * 0.35, T((0, 0, H + 0.06)), mat="glass", segs=(8, 5))
            rod(p, (0, 0, H + 0.07), (R * J(p, 1.5, 0.1), 0, H * 0.6), 0.006, 0.004, mat="glass")
        elif slot == "handle":
            blk(p, 0, 0, 0, R * 1.3, R * 1.0, 0.04, mat="wood_dark", b=0.05)
            blk(p, R * 1.5, 0, 0, R * 0.5, R * 0.5, H * 0.3, mat="wood_dark")
        else:
            flask(p, R * 1.5, 0, H * 0.3, R * 0.25, H * 0.35)
            p.cyl(0.01, 0.01, 0.06, T((-R * 0.9, -R * 0.3, 0)), mat="glass", segs=6)
    elif e == "Industrial":  # test-tube rack and a beaker
        if slot == "body":
            tube_rack(p, 0, 0, 5, R * 2.2, H * 0.8, mat="steel")
        elif slot == "lid":
            for i in range(5):
                xx = -R * 0.88 + R * 1.76 * i / 4
                p.cyl(0.0055, 0.0055, H * J(p, 0.35, 0.3), T((xx, 0, 0.012)), mat="paint", segs=5)
        elif slot == "handle":
            p.lathe([(0, 0), (R * 0.4, 0), (R * 0.4, H * 0.45), (R * 0.45, H * 0.5)], T((R * 0.3, -R * 0.6, 0)), mat="glass", segs=8)
        else:  # bunsen burner
            p.cyl(0.03, 0.03, 0.008, T((-R * 0.7, -R * 0.6, 0)), mat="iron", segs=8)
            p.cyl(0.008, 0.008, H * J(p, 0.5, 0.15), T((-R * 0.7, -R * 0.6, 0)), mat="steel", segs=6)
    elif e == "Steampunk":  # brass reactor: sphere on legs with gauge and coil
        if slot == "body":
            p.ball(R * 0.7, T((0, 0, H * 0.6)), mat="brass", segs=(10, 6))
        elif slot == "lid":
            p.lathe([(R * 0.3, H * 0.6 + R * 0.6), (R * 0.2, H * 0.6 + R * 0.85), (R * 0.25, H * 0.6 + R * J(p, 0.95, 0.1))], mat="copper", segs=8)
        elif slot == "handle":
            for i in range(3):
                a = i * TAU / 3
                rod(p, (math.cos(a) * R * 0.4, math.sin(a) * R * 0.4, H * 0.4), (math.cos(a) * R * 0.75, math.sin(a) * R * 0.75, 0), 0.006, mat="copper")
        else:
            disk(p, (0, -R * 0.7, H * 0.6), R * 0.22, 0.008, "y", "steel", segs=8)
            disk(p, (0, -R * 0.72 - 0.005, H * 0.6), R * 0.16, 0.002, "y", "glow", segs=8)
            p.tube([(R * 0.6, 0, H * 0.7)] + [(R * 0.85 + 0.02 * math.cos(a), 0.02 * math.sin(a), H * 0.7 - a * 0.006) for a in (1, 2, 3, 4, 5, 6)], 0.003, mat="copper", segs=3)
    elif e == "Future":  # analysis cartridge box with sample vials
        if slot == "body":
            p.box((R * 2, R * 1.4, H * 0.5), T((0, 0, H * 0.25)), mat="body", bevel=0.3, bevel_seg=2)
        elif slot == "lid":
            p.box((R * 1.6, R * 1.2, 0.006), M(loc=(0, R * 0.2, H * 0.5 + J(p, 0.04, 0.3)), rot=(-20, 0, 0)), mat="glass", bevel=0)
        elif slot == "handle":
            p.box((R * 0.6, 0.004, H * 0.08), T((-R * 0.5, -R * 0.7, H * 0.3)), mat="glow", bevel=0)
        else:
            for i in range(4):
                p.cyl(0.008, 0.008, H * J(p, 0.25, 0.2), T((-R * 0.5 + i * R * 0.33, 0, H * 0.4)), mat="glass", segs=6)
    elif e == "Wasteland":  # jar still: mason jars, tubing, can burner
        if slot == "body":
            p.cyl(R * 0.5, R * 0.5, H * 0.7, mat="glass", segs=8)
        elif slot == "lid":
            p.cyl(R * 0.52, R * 0.52, 0.015, T((0, 0, H * 0.7)), mat="rust", segs=8)
        elif slot == "handle":
            p.tube([(0, 0, H * 0.72), (0, 0, H * 0.9), (R * 0.9, 0, H * J(p, 0.85, 0.1)), (R * 1.2, 0, H * 0.4)], 0.004, mat="rubber", segs=4)
        else:
            p.cyl(R * 0.35, R * 0.35, H * 0.45, T((R * 1.2, 0, 0)), mat="glass", segs=8)
            p.cyl(R * 0.3, R * 0.3, 0.03, T((-R * 1.1, 0, 0)), mat="paint", segs=7)
    else:  # Ancient: stone vessel with a floating rune lens
        if slot == "body":
            p.lathe([(0, 0), (R * 0.6, 0), (R * 0.9, H * 0.3), (R * 0.7, H * 0.55), (R * 0.75, H * 0.6), (0, H * 0.6)], mat="stone", segs=8)
        elif slot == "lid":
            p.ring(R * 0.5, 0.006, T((0, 0, H * J(p, 0.9, 0.08))), mat="glow", segs=8)
        elif slot == "handle":
            for s in (-1, 1):
                p.box((0.02, 0.03, H * 0.3), T((s * R * 0.85, 0, H * 0.4)), mat="stone_dark", bevel=0)
        else:
            p.box((R * 0.5, 0.004, H * 0.05), T((0, -R * 0.82, H * 0.3)), mat="glow", bevel=0)
            p.lathe([(0, 0), (0.025, 0.02), (0, 0.05)], T((R * 1.3, 0, 0)), mat="stone_dark", segs=5)


# ================================================================ Quiver
@function("Quiver", "Vessel", VESSEL, "carried")
def quiver(p, slot):
    e = p.era
    H, r = F(p, 0.55, 0.08), F(p, 0.055, 0.1)
    if e in ("Primal", "Agrarian", "Mercantile"):  # bark tube / leather / carved quiver with arrows
        if slot == "body":
            if e == "Primal":
                p.lathe([(0, 0), (r * 0.9, 0), (r, H * 0.5), (r * 1.1, H)], mat="bark", segs=8, noise=0.03)
            elif e == "Agrarian":
                p.lathe([(0, 0), (r * 0.8, 0), (r, H * 0.3), (r * 1.05, H)], mat="leather", segs=8)
            else:
                p.lathe([(0, 0), (r * 0.85, 0), (r, H * 0.2), (r * 1.05, H * 0.9), (r * 1.15, H)], mat="wood_dark", segs=10)
        elif slot == "lid":  # arrows sticking out
            n = 4 + (1 if coin(p) else 0)
            for i in range(n):
                a = i * TAU / n + 0.3
                arrow(p, math.cos(a) * r * 0.55, math.sin(a) * r * 0.55, H * 0.5, H * J(p, 0.75, 0.08),
                      rot=(math.sin(a) * 5, math.cos(a) * 5, 0), fletch="feather")
        elif slot == "handle":  # strap
            p.tube([(r, 0, H * 0.85), (r * 2.2, 0.02, H * 0.6), (r * 2.4, 0.02, H * 0.3), (r, 0, H * 0.12)], 0.006,
                   mat="hide" if e == "Primal" else "leather", segs=3)
        else:
            if e == "Primal":
                p.band(r * 1.02, H * 0.85, h=0.03)
                p.band(r * 0.95, H * 0.15, h=0.03)
            elif e == "Agrarian":
                p.ring(r * 1.06, 0.004, T((0, 0, H * 0.97)), mat="iron", segs=8)
                p.box((r * 0.9, 0.004, H * 0.3), T((0, -r * 1.02, H * 0.5)), mat="hide", bevel=0)
            else:  # carved and inlaid
                for z in (H * 0.2, H * 0.5, H * 0.8):
                    p.ring(r * 1.03, 0.005, T((0, 0, z)), mat="brass", segs=10)
                p.plate([(-r * 0.5, H * 0.3), (0, H * 0.25), (r * 0.5, H * 0.3), (r * 0.4, H * 0.65), (0, H * J(p, 0.72, 0.05)), (-r * 0.4, H * 0.65)],
                        0.004, T((0, -r * 1.02, 0)), mat="gold", bevel=0)
    elif e == "Industrial":  # ammunition bag
        W, D = r * 3.2, r * 1.6
        if slot == "body":
            p.box((W, D, H * 0.4), T((0, 0, H * 0.2)), mat="cloth", bevel=0.1, bevel_seg=1)
        elif slot == "lid":
            p.box((W * 1.02, D * 0.5, H * 0.18), M(loc=(0, -D * 0.3, H * 0.33), rot=(J(p, -8, 0.5), 0, 0)), mat="cloth", bevel=0)
        elif slot == "handle":
            p.tube([(-W * 0.45, 0, H * 0.38), (-W * 0.2, 0.02, H * 0.75), (W * 0.2, 0.02, H * 0.75), (W * 0.45, 0, H * 0.38)], 0.008, mat="leather", segs=3)
        else:
            for x in (-W * 0.25, W * 0.25):
                p.cyl(0.006, 0.006, 0.006, T((x, -D * 0.56, H * 0.3)) @ M(rot=(90, 0, 0)), mat="brass", segs=6)
            for i in range(4):
                p.cyl(0.006, 0.006, 0.04, T((-W * 0.3 + i * 0.02, D * 0.1, H * 0.4)), mat="brass", segs=5)
    elif e == "Steampunk":  # magazine belt box: brass drum with cartridges
        if slot == "body":
            p.cyl(r * 1.4, r * 1.4, H * 0.35, mat="brass", segs=12)
        elif slot == "lid":
            p.cyl(r * 1.45, r * 1.45, 0.02, T((0, 0, H * 0.35)), mat="copper", segs=12)
            disk(p, (0, 0, H * 0.37 + 0.006), r * 0.4, 0.01, "y", "brass", segs=6)
        elif slot == "handle":  # bandolier
            p.tube([(r * 1.4, 0, H * 0.2), (r * 2.5, 0.01, H * 0.6), (r * 1.5, 0.02, H * J(p, 1.0, 0.1)), (-r * 1.4, 0, H * 0.25)], 0.01, mat="leather", segs=3)
        else:
            for i in range(5):
                a = -0.6 + i * 0.3
                p.cyl(0.006, 0.006, 0.05, T((math.cos(a) * r * 1.4, -math.sin(a) * r * 1.4 * -1, H * 0.12)), mat="brass", segs=5)
            disk(p, (0, -r * 1.4, H * 0.2), r * 0.35, 0.006, "y", "glow", segs=6)
    elif e == "Future":  # energy cell belt: cells in a shell rack
        W = r * 3.6
        if slot == "body":
            p.box((W, r * 1.2, H * 0.3), T((0, 0, H * 0.15)), mat="shell_dark", bevel=0.3, bevel_seg=2)
        elif slot == "lid":
            for i in range(4):
                p.cyl(r * 0.32, r * 0.32, H * J(p, 0.2, 0.2), T((-W * 0.36 + i * W * 0.24, 0, H * 0.3)), mat="body", segs=8)
        elif slot == "handle":
            p.box((W * 1.4, r * 0.3, 0.03), T((0, r * 0.75, H * 0.12)), mat="rubber", bevel=0)
        else:
            for i in range(4):
                p.box((r * 0.3, 0.004, H * 0.1), T((-W * 0.36 + i * W * 0.24, -r * 0.61, H * 0.15)), mat="glow", bevel=0)
    elif e == "Wasteland":  # pipe quiver of rebar bolts
        if slot == "body":
            p.cyl(r, r, H * 0.75, mat="rust", segs=8)
        elif slot == "lid":
            for i in range(4):
                a = i * TAU / 4
                arrow(p, math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, H * 0.45, H * J(p, 0.6, 0.1), fletch="paint", shaft="steel")
        elif slot == "handle":
            p.tube([(r, 0, H * 0.7), (r * 2.2, 0.02, H * 0.4), (r, 0, H * 0.1)], 0.008, mat="cloth", segs=3)
        else:
            p.band(r, H * 0.6, h=0.04)
            p.box((r * 1.2, 0.004, H * 0.15), T((0, -r * 1.01, H * 0.25)), mat="paint", bevel=0)
    else:  # Ancient: stone sheath of light bolts
        if slot == "body":
            p.lathe([(0, 0), (r * 0.8, 0), (r * 1.1, H * 0.15), (r * 1.0, H * 0.7), (r * 1.2, H * 0.75)], mat="stone", segs=6)
        elif slot == "lid":
            for i in range(3):
                a = i * TAU / 3
                p.cyl(0.004, 0.004, H * J(p, 0.45, 0.1), T((math.cos(a) * r * 0.45, math.sin(a) * r * 0.45, H * 0.6)), mat="glow", segs=4)
        elif slot == "handle":
            p.tube([(r, 0, H * 0.7), (r * 2.0, 0.02, H * 0.4), (r, 0, H * 0.1)], 0.007, mat="stone_dark", segs=4)
        else:
            for z in (H * 0.25, H * 0.5):
                p.ring(r * 1.05, 0.004, T((0, 0, z)), mat="glow", segs=6)


# ================================================================ Teaset
@function("Teaset", "Vessel", VESSEL, "scene")
def teaset(p, slot):
    e = p.era
    R, H = F(p, 0.08, 0.1), F(p, 0.14, 0.1)
    tray = F(p, 0.38, 0.06)
    if e == "Primal":  # coconut-shell bowls on a leaf mat
        if slot == "body":
            bowl(p, R * 1.2, H * 0.5, (0, 0, 0), mat="bark", segs=10)
        elif slot == "lid":  # half shell lying as a lid
            p.lathe([(0, H * 0.5 + 0.03), (R * 0.9, H * 0.5 + 0.01), (R * 1.1, H * 0.5)], M(rot=(J(p, 10, 0.5), 0, 0)), mat="bark", segs=8)
        elif slot == "handle":
            p.tube([(R * 1.1, 0, H * 0.45), (R * 1.6, -0.01, H * 0.6), (R * 2.0, -0.02, H * J(p, 0.5, 0.2))], 0.006, mat="wood", segs=4)
        else:
            p.plate([(-tray / 2, -tray * 0.3), (0, -tray * 0.45), (tray / 2, -tray * 0.25), (tray * 0.4, tray * 0.35), (-tray * 0.45, tray * 0.3)],
                    0.004, T((0, 0, 0.002)) @ M(rot=(90, 0, 0)), mat="cloth", bevel=0)
            bowl(p, R * 0.6, H * 0.3, (tray * 0.28, -tray * 0.2, 0.004), mat="bark", segs=8)
    elif e in ("Agrarian", "Mercantile", "Industrial"):  # clay pot / porcelain / enamel
        mat = {"Agrarian": "ceramic", "Mercantile": "glaze", "Industrial": "paint"}[e]
        prof = [(R * 0.6, 0), (R, H * 0.35), (R * 0.95, H * 0.6), (R * 0.5, H * 0.75)] if e != "Industrial" else \
               [(R * 0.9, 0), (R, H * 0.1), (R * 0.85, H * 0.6), (R * 0.45, H * 0.75)]
        if slot == "body":
            closed(p, prof, mat=mat, segs=10)
        elif slot == "lid":
            p.lathe([(R * 0.52, H * 0.75), (R * 0.4, H * 0.82), (R * 0.12, H * 0.84), (R * 0.1, H * 0.84 + J(p, 0.02, 0.3)), (0, H * 0.88)],
                    mat=mat, segs=10)
        elif slot == "handle":
            rod(p, (-R * 0.9, 0, H * 0.35), (-R * 1.6, 0, H * J(p, 0.6, 0.1)), R * 0.18, R * 0.06, mat=mat, segs=6)
            if e == "Industrial":
                bail(p, R * 0.5, H * 0.72, H * 0.35, 0.004, mat="steel")
            else:
                p.tube([(R * 0.9, 0, H * 0.55), (R * 1.35, 0, H * 0.5), (R * 1.3, 0, H * 0.2), (R * 0.95, 0, H * 0.15)], 0.007, mat=mat, segs=4)
        else:  # cups (and a tray from Mercantile on)
            if e != "Agrarian":
                p.lathe([(0, 0), (tray * 0.5, 0), (tray * 0.52, 0.012), (tray * 0.48, 0.012), (0, 0.006)], T((0, 0, 0)), mat="wood_dark" if e == "Mercantile" else "steel", segs=12)
            z = 0.012 if e != "Agrarian" else 0
            for i, (x, y) in enumerate(((tray * 0.3, -tray * 0.15), (-tray * 0.3, -tray * 0.15), (0, -tray * 0.32))):
                if i < 2 or coin(p):
                    cup(p, R * 0.4, R * 0.55, (x, y, z), mat=mat, handle=e != "Agrarian")
    elif e == "Steampunk":  # samovar
        if slot == "body":
            p.lathe([(R * 0.6, 0), (R * 0.7, H * 0.1), (R * 0.4, H * 0.2), (R * 1.0, H * 0.3), (R * 1.1, H * 0.7), (R * 0.7, H * 0.9)], mat="brass", segs=12)
        elif slot == "lid":
            p.lathe([(R * 0.72, H * 0.9), (R * 0.5, H * 0.98), (R * 0.2, H * 1.04), (R * 0.25, H * 1.04 + J(p, 0.05, 0.2)), (0, H * 1.15)], mat="copper", segs=10)
            p.cyl(R * 0.4, R * 0.4, 0.004, T((0, 0, H * 1.15)), mat="glow", segs=8)
        elif slot == "handle":
            rod(p, (0, -R * 1.05, H * 0.4), (0, -R * 1.5, H * 0.38), 0.008, 0.006, mat="brass", segs=6)
            p.box((0.02, 0.01, 0.02), T((0, -R * 1.5, H * 0.42)), mat="wood_dark", bevel=0)
            for s in (-1, 1):
                p.tube([(s * R * 1.08, 0, H * 0.68), (s * R * 1.4, 0, H * 0.66), (s * R * 1.38, 0, H * 0.5), (s * R * 1.1, 0, H * 0.48)], 0.006, mat="wood_dark", segs=4)
        else:
            p.lathe([(0, 0), (tray * 0.5, 0), (tray * 0.52, 0.015), (0, 0.008)], mat="copper", segs=12)
            for x in (-tray * 0.32, tray * 0.32):
                p.cyl(R * 0.32, R * 0.3, R * 0.7, T((x, -tray * 0.15, 0.012)), mat="glass", segs=8)
                p.ring(R * 0.33, 0.004, T((x, -tray * 0.15, 0.03)), mat="brass", segs=8)
    elif e == "Future":  # auto-brewer: capsule tower with a cup bay
        if slot == "body":
            p.box((R * 2.2, R * 1.8, H * 1.2), T((0, R * 0.2, H * 0.6)), mat="body", bevel=0.35, bevel_seg=2)
        elif slot == "lid":
            p.cyl(R * 0.7, R * 0.7, H * J(p, 0.25, 0.2), T((0, R * 0.3, H * 1.2)), mat="glass", segs=10)
        elif slot == "handle":
            p.box((R * 1.4, R * 0.5, 0.02), T((0, -R * 0.8, H * 0.75)), mat="shell_dark", bevel=0)
            p.box((R * 0.8, 0.004, 0.008), T((0, -R * 0.72, H * 1.0)), mat="glow", bevel=0)
        else:
            p.box((R * 1.6, R * 0.8, 0.012), T((0, -R * 0.6, 0.006)), mat="shell_dark", bevel=0)
            cup(p, R * 0.35, R * 0.6, (0, -R * 0.65, 0.012), mat="shell", handle=coin(p))
    elif e == "Wasteland":  # dented kettle on a can stove, mismatched mugs
        if slot == "body":
            p.cyl(R * 0.8, R * 0.8, H * 0.25, mat="rust", segs=8)
            closed(p, [(R * 0.8, H * 0.25), (R, H * 0.4), (R * 0.9, H * 0.65), (R * 0.4, H * 0.75)], mat="steel", segs=10)
        elif slot == "lid":
            p.cyl(R * 0.42, R * 0.3, 0.02 + J(p, 0.01, 0.5), T((0, 0, H * 0.75)), mat="iron", segs=8)
        elif slot == "handle":
            bail(p, R * 0.6, H * 0.7, H * 0.3, 0.004, mat="iron")
            rod(p, (R * 0.9, 0, H * 0.5), (R * 1.6, 0, H * 0.7), R * 0.15, R * 0.07, mat="steel", segs=5)
        else:
            cup(p, R * 0.4, R * 0.75, (-tray * 0.35, -tray * 0.1, 0), mat="paint", handle=True)
            cup(p, R * 0.35, R * 0.65, (tray * 0.35, -tray * 0.15, 0), mat="steel", handle=coin(p))
    else:  # Ancient: stone ewer and bowls, rune band
        if slot == "body":
            closed(p, [(R * 0.5, 0), (R * 0.9, H * 0.3), (R * 0.8, H * 0.6), (R * 0.4, H * 0.8)], mat="stone", segs=8)
        elif slot == "lid":
            p.lathe([(R * 0.42, H * 0.8), (R * 0.5, H * 0.85), (0, H * J(p, 0.95, 0.05))], mat="stone_dark", segs=8)
        elif slot == "handle":
            rod(p, (-R * 0.7, 0, H * 0.55), (-R * 1.4, 0, H * 0.75), R * 0.14, R * 0.06, mat="stone", segs=5)
        else:
            p.ring(R * 0.88, 0.004, T((0, 0, H * 0.4)), mat="glow", segs=8)
            for x in (-tray * 0.32, tray * 0.32):
                bowl(p, R * 0.45, R * 0.4, (x, -tray * 0.15, 0), mat="stone", segs=8)


# ================================================================ Tableware
@function("Tableware", "Vessel", VESSEL, "scene")
def tableware(p, slot):
    e = p.era
    R = F(p, 0.12, 0.1)
    W = F(p, 0.42, 0.06)
    if e == "Primal":  # leaf plates with food and a gourd ladle
        if slot == "body":
            for x, s in ((-W * 0.2, 1.0), (W * 0.22, 0.8)):
                p.plate([(-R * s, 0), (-R * 0.5 * s, R * 0.45 * s), (R * s, 0), (-R * 0.5 * s, -R * 0.45 * s)], 0.004,
                        T((x, 0, 0.002)) @ M(rot=(90, 0, J(p, 20, 0.8))), mat="cloth", bevel=0)
        elif slot == "lid":  # food heaps
            for x in (-W * 0.2, W * 0.22):
                p.ball(1.0, M(loc=(x, 0, 0.015), scale=(R * 0.4, R * 0.3, J(p, 0.025, 0.3))), mat="ceramic", segs=(6, 4), noise=0.05)
        elif slot == "handle":
            rod(p, (0, -R * 0.6, 0.01), (J(p, 0.12, 0.2), -R * 0.9, 0.02), 0.006, mat="wood", segs=4)
            p.ball(0.025, M(loc=(0, -R * 0.6, 0.015), scale=(1, 1, 0.5)), mat="bark", segs=(6, 4))
        else:
            p.ball(1.0, M(loc=(0, R * 0.9, 0.03), scale=(0.04, 0.04, 0.035)), mat="bark", segs=(6, 4))
    elif e == "Agrarian":  # wooden bowls and chopsticks
        if slot == "body":
            bowl(p, R * 0.7, R * 0.55, (-W * 0.18, 0, 0), mat="wood", foot=0.01)
            bowl(p, R * 0.6, R * 0.45, (W * 0.2, R * 0.2, 0), mat="wood", foot=0.008)
        elif slot == "lid":  # inverted bowl as a lid
            p.lathe([(R * 0.72, R * 0.55), (R * 0.55, R * 0.75), (R * 0.2, R * 0.8), (0, R * 0.8 + J(p, 0.01, 0.5))], T((-W * 0.18, 0, 0)), mat="wood_dark", segs=10)
        elif slot == "handle":
            for dy in (-0.006, 0.006):
                rod(p, (W * 0.05 - 0.1, -R * 0.75 + dy, 0.004), (W * 0.05 + J(p, 0.12, 0.1), -R * 0.8 + dy, 0.006), 0.003, 0.0018, mat="wood_dark", segs=4)
        else:
            p.box((W, R * 1.5, 0.012), T((0, -R * 0.1, -0.0)), mat="wood", bevel=0)
    elif e in ("Mercantile", "Industrial"):  # porcelain plates / enamel dishes with cutlery
        mat = "glaze" if e == "Mercantile" else "shell"
        if slot == "body":
            plate(p, R, (0, 0, 0), mat=mat)
            plate(p, R * 0.75, (0, 0, 0.012), mat=mat)
        elif slot == "lid":
            bowl(p, R * 0.45, R * 0.35, (0, 0, 0.018), mat=mat, segs=10)
            if e == "Industrial":
                p.ring(R * 0.46, 0.003, T((0, 0, 0.018 + R * 0.35)), mat="paint", segs=10)
        elif slot == "handle":
            for s in (-1, 1):
                x = s * (R + 0.03)
                p.box((0.012, J(p, 0.17, 0.08), 0.004), T((x, 0, 0.004)), mat="steel" if e == "Industrial" else "gold", bevel=0)
            p.box((0.025, 0.02, 0.004), T((R + 0.03, -0.09, 0.004)), mat="steel" if e == "Industrial" else "gold", bevel=0)
        else:
            if e == "Mercantile":
                p.ring(R * 0.97, 0.003, T((0, 0, 0.012)), mat="gold", segs=12)
                p.box((W * 1.1, W * 0.6, 0.004), T((0, 0, -0.002)), mat="cloth", bevel=0)
            else:
                cup(p, 0.03, 0.06, (R + 0.07, R * 0.4, 0), mat="paint", handle=True)
    elif e == "Steampunk":  # brass cloche on a platter
        if slot == "body":
            plate(p, R * 1.15, (0, 0, 0), mat="brass", h=0.02)
        elif slot == "lid":
            p.lathe([(R * 0.95, 0.015), (R * 0.9, R * 0.35), (R * 0.6, R * 0.65), (R * 0.2, R * 0.75), (0, R * 0.76)], mat="brass", segs=12)
            p.ring(R * 0.94, 0.004, T((0, 0, 0.02)), mat="copper", segs=12)
        elif slot == "handle":
            p.lathe([(0.008, R * 0.75), (0.015, R * 0.78), (0.012, R * 0.78 + J(p, 0.03, 0.3)), (0, R * 0.82 + 0.02)], mat="copper", segs=8)
        else:
            disk(p, (0, -R * 0.88, R * 0.3), R * 0.14, 0.006, "y", "steel", segs=8)
            disk(p, (0, -R * 0.89 - 0.004, R * 0.3), R * 0.1, 0.002, "y", "glow", segs=8)
    elif e == "Future":  # heated plate pods with lit rims
        if slot == "body":
            for x in (-W * 0.22, W * 0.22):
                p.lathe([(0, 0), (R * 0.75, 0), (R * 0.8, 0.02), (R * 0.7, 0.025), (0, 0.015)], T((x, 0, 0)), mat="body", segs=12)
        elif slot == "lid":
            p.lathe([(R * 0.7, 0.025), (R * 0.65, R * 0.3), (0, R * J(p, 0.42, 0.1))], T((-W * 0.22, 0, 0)), mat="glass", segs=10)
        elif slot == "handle":
            p.box((0.012, J(p, 0.14, 0.1), 0.006), T((0, -R * 0.2, 0.004)), mat="shell_dark", bevel=0)
        else:
            for x in (-W * 0.22, W * 0.22):
                p.ring(R * 0.78, 0.003, T((x, 0, 0.02)), mat="glow", segs=12)
    elif e == "Wasteland":  # hubcap plate, cans, bent fork
        if slot == "body":
            plate(p, R * 1.05, (0, 0, 0), mat="steel", h=0.018)
        elif slot == "lid":
            p.cyl(0.035, 0.035, J(p, 0.08, 0.2), T((R * 1.3, R * 0.3, 0)), mat="paint", segs=8)
        elif slot == "handle":
            p.tube([(-R * 0.3, -R * 0.2, 0.02), (R * 0.4, -R * 0.4, 0.02), (R * 0.6, -R * 0.35, 0.04)], 0.003, mat="iron", segs=3)
        else:
            p.cyl(R * 0.4, R * 0.4, 0.02, T((0, 0, 0.018)), mat="rust", segs=8)
    else:  # Ancient: stone platter and bowls, a glowing seam
        if slot == "body":
            p.lathe([(0, 0), (R * 1.1, 0), (R * 1.15, 0.03), (R, 0.035), (0, 0.025)], mat="stone", segs=8)
        elif slot == "lid":
            bowl(p, R * 0.4, R * 0.35, (R * 0.4, 0, 0.03), mat="stone_dark", segs=8)
        elif slot == "handle":
            rod(p, (-R * 0.6, -R * 0.2, 0.04), (-R * 0.1, -R * 0.4, J(p, 0.05, 0.2)), 0.006, mat="stone_dark", segs=4)
        else:
            p.ring(R * 1.05, 0.004, T((0, 0, 0.03)), mat="glow", segs=8)
