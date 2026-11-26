"""Device family, music / science / play set (殼體器: 殼體、面板／顯示、控制件、核心／光源、附件／天線): Spectacles, Scale,
Microscope, Lute, Drum, Keyboard, MusicBox, BoardGame (cosmos_chimera P1-19, ADR-0016).

Frame as forms_device: everything sits on z = 0 facing -Y, origin at the floor or hand contact. Microscope and
Keyboard are scene-only, so they are floor-standing pieces (on their own stand or legs). The rest are carried and
stay hand-sized (a lute stands on its tail end, spectacles stand on their rims with the temples folded back +Y).
Slot use per function:
- Spectacles: shell rims, panel lenses, controls bridge and hinges, core lens detail, attachment temples or strap.
- Scale: shell base and column, panel dial or marks, controls beam and pointer, core weights, attachment pans.
- Microscope: shell stand, panel stage, controls focus knobs, core body tube and lenses, attachment mirror or lamp.
- Lute: shell sound box, panel soundboard and bridge, controls neck and pegbox, core strings, attachment strap.
- Drum: shell drum body, panel heads, controls tension ropes or lugs, core sticks, attachment strap or stand.
- Keyboard: shell case or frame, panel keys, controls legs and pedals, core sounding parts, attachment desk trim.
- MusicBox: shell box, panel lid, controls crank or key, core comb and drum, attachment figure or ornament.
- BoardGame: shell board, panel grid, controls light pieces, core dark pieces, attachment box, dice or bag.
Glow: Music and Play groups do not light (everyday-objects.md 抽樣/發光); only Steampunk, Future, Wasteland and
Ancient forms carry their era glow as small accents. Science (Scale, Microscope) and Spectacles (3C) follow the
form era. Frame values (F) are drawn first, in a fixed order, so every slot variant meets the others.
"""
import math

from mathutils import Matrix

from forms_furniture import gear
from forms_tools import disk, rod
from kit_forms import DEVICE, F, J, coin, function
from kit_lib import M

T = Matrix.Translation
TAU = math.tau


def blk(p, x, y, z, w, d, h, mat="body", b=0, **kw):
    """Box with its bottom face at z."""
    p.box((w, d, h), T((x, y, z + h / 2)), mat=mat, bevel=b, **kw)


def strings(p, x0, x1, y, z0, z1, n, r=0.0008, mat="steel"):
    """n straight strings across x0..x1 from z0 to z1 at depth y."""
    for i in range(n):
        x = x0 + (x1 - x0) * i / max(1, n - 1)
        p.tube([(x, y, z0), (x, y, z1)], r, mat=mat, segs=3)


def rim(p, x, z, r, t, mat, segs=10, y=0.0):
    """Lens rim standing in the XZ plane."""
    p.ring(r, t, T((x, y, z)) @ M(rot=(90, 0, 0)), mat=mat, segs=segs, square=True)


def lens(p, x, z, r, mat="glass", segs=10, y=0.0):
    disk(p, (x, y, z), r, 0.002, "y", mat, segs=segs)


# ================================================================ Spectacles
@function("Spectacles", "Device", DEVICE, "carried")
def spectacles(p, slot):
    e = p.era
    r, gap = F(p, 0.022, 0.1), F(p, 0.016, 0.15)
    z = r * 1.1
    xs = (-(r + gap / 2), r + gap / 2)
    arm = F(p, 0.12, 0.08)
    if e == "Primal":  # bone snow goggles: one carved band with two slits
        W = (r + gap / 2) * 2 + r * 1.6
        if slot == "shell":
            p.plate([(-W / 2, z - r * 0.8), (W / 2, z - r * 0.8), (W / 2 * 0.95, z + r * 0.8), (-W / 2 * 0.95, z + r * 0.8)], 0.006, mat="bone", bevel=0)
        elif slot == "panel":
            for x in xs:
                p.box((r * 1.4, 0.008, r * J(p, 0.2, 0.3)), T((x, 0, z)), mat="rubber", bevel=0)
        elif slot == "controls":
            p.box((gap * 0.8, 0.008, r * 0.6), T((0, 0, z - r * 0.5)), mat="bone", bevel=0)
        elif slot == "core":
            for x in xs:
                p.box((r * 0.5, 0.004, r * 0.1), T((x, -0.004, z + r * 0.55)), mat="ceramic", bevel=0)
        else:
            for s in (-1, 1):
                p.tube([(s * W / 2, 0, z), (s * W / 2, arm * 0.5, z + 0.004), (s * W * 0.4, arm, z + J(p, 0.01, 0.5))], 0.0025, mat="hide", segs=3)
        return
    if e == "Agrarian":  # crystal reading stone in a wooden handle frame
        if slot == "shell":
            rim(p, 0, r * 2.2, r * 1.3, r * 0.18, "wood", segs=10)
        elif slot == "panel":
            p.ball(1.0, M(loc=(0, 0, r * 2.2), scale=(r * 1.2, r * 0.3, r * 1.2)), mat="glass", segs=(8, 4))
        elif slot == "controls":
            p.cyl(r * 0.25, r * 0.2, r * J(p, 1.0, 0.15), T((0, 0, 0)), mat="wood_dark", segs=6)
        elif slot == "core":
            p.ring(r * 0.25, 0.002, T((0, 0, r * 0.95)), mat="iron", segs=6)
        else:
            p.tube([(0, 0, 0.004), (0.012, 0.01, -0.01), (0.02, 0.0, -0.03)], 0.0015, mat="rope", segs=3)
        return
    if e == "Mercantile":  # monocle on a chain
        if slot == "shell":
            rim(p, 0, z, r * 1.05, r * 0.1, "gold", segs=12)
        elif slot == "panel":
            lens(p, 0, z, r)
        elif slot == "controls":
            p.ball(r * 0.15, T((r * 1.1, 0, z)), mat="gold", segs=(5, 3))
        elif slot == "core":
            rim(p, 0, z, r * J(p, 0.9, 0.05), r * 0.03, "brass", segs=10, y=-0.002)
        else:
            p.tube([(r * 1.1, 0, z), (r * 1.6, 0.01, z * 0.4), (r * 2.3, 0.02, 0.003), (r * J(p, 3.2, 0.1), 0.03, 0.003)], 0.0012, mat="gold", segs=3)
        return
    if e == "Future":  # AR visor: one curved lens band
        W = (r + gap / 2) * 2 + r * 1.2
        if slot == "shell":
            p.box((W, 0.006, r * 0.4), T((0, 0, z + r * 0.85)), mat="body", bevel=0.3, bevel_seg=1)
        elif slot == "panel":
            p.box((W * 0.95, 0.004, r * 1.5), T((0, -0.003, z)), mat="glass", bevel=0)
        elif slot == "controls":
            p.box((gap * 0.8, 0.008, r * 0.4), T((0, 0.002, z - r * 0.6)), mat="shell_dark", bevel=0)
        elif slot == "core":
            p.box((r * J(p, 0.6, 0.3), 0.002, r * 0.2), T((xs[1], -0.006, z + r * 0.3)), mat="glow", bevel=0)
        else:
            for s in (-1, 1):
                p.box((0.005, arm, r * 0.35), T((s * W / 2, arm / 2, z + r * 0.8)), mat="body", bevel=0)
        return
    if e == "Ancient":  # stone visor with rune lenses
        W = (r + gap / 2) * 2 + r * 1.4
        if slot == "shell":
            p.plate([(-W / 2, z - r), (W / 2, z - r), (W / 2, z + r * 0.9), (0, z + r * 1.3), (-W / 2, z + r * 0.9)], 0.008, mat="stone", bevel=0)
        elif slot == "panel":
            for x in xs:
                lens(p, x, z, r * 0.7, mat="glow", segs=6, y=-0.0045)
        elif slot == "controls":
            p.box((gap * 0.6, 0.01, r * 0.3), T((0, 0, z + r * 0.95)), mat="gold", bevel=0)
        elif slot == "core":
            rim(p, xs[0], z, r * J(p, 0.75, 0.05), r * 0.08, "stone_dark", segs=6, y=-0.005)
            rim(p, xs[1], z, r * 0.75, r * 0.08, "stone_dark", segs=6, y=-0.005)
        else:
            for s in (-1, 1):
                p.box((0.006, arm, r * 0.3), T((s * W / 2, arm / 2, z)), mat="stone_dark", bevel=0)
        return
    # Industrial round frames, Steampunk multi-lens goggles, Wasteland welding goggles
    rmat = {"Industrial": "steel", "Steampunk": "brass", "Wasteland": "rust"}[e]
    if slot == "shell":
        for x in xs:
            if e == "Industrial":
                rim(p, x, z, r, r * 0.07, rmat, segs=10)
            else:
                p.cyl(r * 1.05, r * 1.0, r * 0.7, T((x, 0, z)) @ M(rot=(90, 0, 0)), mat=rmat, segs=10)
    elif slot == "panel":
        for x in xs:
            lens(p, x, z, r * 0.92, mat="glass" if e != "Wasteland" else "rubber", y=-r * (0.7 if e != "Industrial" else 0))
    elif slot == "controls":
        p.tube([(xs[0] + r, 0, z + r * 0.2), (0, 0, z + r * J(p, 0.55, 0.2)), (xs[1] - r, 0, z + r * 0.2)], r * 0.07, mat=rmat, segs=4)
    elif slot == "core":
        if e == "Steampunk":  # extra flip-down lens
            p.cyl(r * 0.55, r * 0.55, r * 0.3, T((xs[1] + r * 0.6, -r * 1.0, z + r * 0.6)) @ M(rot=(90, 0, 0)), mat="copper", segs=8)
            lens(p, xs[1] + r * 0.6, z + r * 0.6, r * 0.45, mat="glow", y=-r * 1.32)
        elif e == "Wasteland":
            p.box((r * 1.0, 0.004, r * 0.6), T((xs[0], -r * 0.72, z - r * 0.4)), mat="cloth", bevel=0)
        else:
            for x in xs:
                p.ball(r * 0.08, T((x + math.copysign(r, x), 0, z + r * 0.3)), mat="steel", segs=(4, 3))
    else:
        if e == "Industrial":
            for s in (-1, 1):
                p.tube([(s * (xs[1] + r), 0, z + r * 0.3), (s * (xs[1] + r), arm * 0.9, z + r * 0.2), (s * (xs[1] + r * 0.8), arm, z - r * 0.4)], 0.0012, mat="steel", segs=3)
        else:  # strap
            p.tube([(xs[0] - r, 0, z), (xs[0] - r * 1.5, arm * 0.7, z), (0, arm * J(p, 1.2, 0.1), z), (xs[1] + r * 1.5, arm * 0.7, z), (xs[1] + r, 0, z)],
                   r * 0.12, mat="leather" if e == "Steampunk" else "cloth", segs=3)


# ================================================================ Scale
@function("Scale", "Device", DEVICE, "carried")
def scale(p, slot):
    e = p.era
    H, Wb = F(p, 0.32, 0.08), F(p, 0.34, 0.08)
    if e in ("Primal", "Agrarian", "Mercantile", "Wasteland", "Ancient"):  # beam balances in each era's craft
        post = {"Primal": "wood", "Agrarian": "wood", "Mercantile": "brass", "Wasteland": "rust", "Ancient": "stone"}[e]
        armw = Wb * (0.5 if e == "Agrarian" else 1.0)
        off = 0.0 if e != "Agrarian" else Wb * 0.15  # steelyard: off-centre pivot
        if slot == "shell":
            if e == "Primal":
                p.ball(1.0, M(loc=(0, 0, 0.02), scale=(0.07, 0.06, 0.035)), mat="stone", segs=(6, 4), noise=0.05)
                p.tube([(0, 0, 0.02), (0.005, 0, H * 0.5), (0, 0, H)], 0.007, mat="wood", segs=5)
            else:
                p.lathe([(0, 0), (0.06, 0), (0.06, 0.02), (0.015, 0.03), (0.012, H), (0, H)], mat=post, segs=8 if e != "Ancient" else 6)
        elif slot == "panel":
            p.plate([(-0.012, H + 0.01), (0.012, H + 0.01), (0, H + J(p, 0.06, 0.2))], 0.004, T((0, -0.006, 0)), mat=post if e != "Ancient" else "glow", bevel=0)
        elif slot == "controls":
            rod(p, (-armw / 2 + off, 0, H), (armw / 2 + off, 0, H), 0.005, mat="wood_dark" if e in ("Primal", "Agrarian") else post, segs=5)
        elif slot == "core":
            if e == "Agrarian":
                p.lathe([(0, 0), (0.015, 0.005), (0.018, 0.025), (0.006, 0.035)], T((armw / 2 + off - 0.02, 0, H - 0.08)), mat="iron", segs=7)
                p.tube([(armw / 2 + off - 0.02, 0, H), (armw / 2 + off - 0.02, 0, H - 0.045)], 0.001, mat="rope", segs=3)
            elif e == "Primal":
                p.ball(J(p, 0.025, 0.2), T((armw / 2, 0, H - 0.1)), mat="stone_dark", segs=(6, 4), noise=0.05)
                p.tube([(armw / 2, 0, H), (armw / 2, 0, H - 0.08)], 0.001, mat="rope", segs=3)
            else:
                for i in range(2 + (1 if coin(p) else 0)):
                    p.cyl(0.012 - i * 0.002, 0.012 - i * 0.002, 0.012, T((0.08 + i * 0.03, -0.05, 0)), mat="brass" if e == "Mercantile" else post, segs=7)
        else:  # pans on cords
            sides = (-1,) if e == "Agrarian" else (-1, 1)
            for s in sides:
                x = s * armw / 2 + off
                zp = H * J(p, 0.45, 0.1)
                pmat = {"Primal": "hide", "Agrarian": "wood", "Mercantile": "brass", "Wasteland": "steel", "Ancient": "stone_dark"}[e]
                p.lathe([(0, zp), (0.05, zp + 0.005), (0.055, zp + 0.015)], T((x, 0, 0)), mat=pmat, segs=8)
                for k in range(3):
                    a = k * TAU / 3
                    p.tube([(x, 0, H), (x + math.cos(a) * 0.05, math.sin(a) * 0.05, zp + 0.015)], 0.0008, mat="rope" if e in ("Primal", "Agrarian") else "steel", segs=3)
                if e == "Ancient":
                    p.ring(0.052, 0.002, T((x, 0, zp + 0.016)), mat="glow", segs=6)
        return
    if e == "Industrial":  # platform scale with a dial column
        if slot == "shell":
            blk(p, 0, 0, 0, Wb * 0.8, Wb * 0.6, 0.04, mat="paint")
            blk(p, 0, Wb * 0.25, 0.04, 0.04, 0.04, H * 0.7, mat="paint")
        elif slot == "panel":
            disk(p, (0, Wb * 0.25 - 0.02, H * 0.75), J(p, 0.06, 0.1), 0.01, "y", "steel", segs=12)
            disk(p, (0, Wb * 0.25 - 0.026, H * 0.75), 0.05, 0.002, "y", "shell", segs=12)
        elif slot == "controls":
            p.box((0.004, 0.002, 0.04), M(loc=(0.008, Wb * 0.25 - 0.028, H * 0.76), rot=(0, J(p, 30, 0.6), 0)), mat="paint", bevel=0)
        elif slot == "core":
            blk(p, 0, -0.02, 0.04, Wb * 0.7, Wb * 0.45, 0.012, mat="steel")
        else:
            p.cyl(0.03, 0.03, 0.03, T((J(p, 0.05, 0.5), -0.03, 0.052)), mat="iron", segs=8)
        return
    if e == "Steampunk":  # brass spring scale: dial housing on a stand, pan on top
        if slot == "shell":
            p.lathe([(0, 0), (0.07, 0), (0.07, 0.015), (0.02, 0.03), (0.02, H * 0.4)], mat="brass", segs=10)
        elif slot == "panel":
            p.cyl(0.07, 0.07, 0.03, T((0, 0.015, H * 0.55)) @ M(rot=(90, 0, 0)), mat="brass", segs=12)
            disk(p, (0, -0.016, H * 0.55), 0.06, 0.002, "y", "glow", segs=12)
        elif slot == "controls":
            p.box((0.004, 0.002, 0.05), M(loc=(0, -0.019, H * 0.56), rot=(0, J(p, -40, 0.6), 0)), mat="steel", bevel=0)
        elif slot == "core":  # exposed spring
            p.tube([(0.015 * math.cos(a), 0.015 * math.sin(a), H * 0.65 + a * 0.004) for a in [i * 0.7 for i in range(14)]], 0.002, mat="copper", segs=3)
        else:
            p.lathe([(0, H * 0.7), (0.08, H * 0.7 + 0.005), (0.085, H * 0.7 + J(p, 0.02, 0.2))], mat="copper", segs=10)
        return
    # Future: floating pan over a base disc
    if slot == "shell":
        p.lathe([(0, 0), (0.09, 0), (0.095, 0.02), (0.07, 0.035), (0, 0.035)], mat="body", segs=12)
    elif slot == "panel":
        p.box((0.06, 0.003, 0.02), M(loc=(0, -0.08, 0.02), rot=(-30, 0, 0)), mat="glow", bevel=0)
    elif slot == "controls":
        p.ring(0.07, 0.003, T((0, 0, 0.036)), mat="glow", segs=12)
    elif slot == "core":
        p.ball(0.012, T((0, 0, H * 0.4)), mat="glow", segs=(6, 4))
    else:
        p.lathe([(0, H * 0.55), (0.09, H * 0.55 + 0.004), (0.095, H * 0.55 + J(p, 0.015, 0.3))], mat="shell", segs=12)


# ================================================================ Microscope (scene: on its own stand)
@function("Microscope", "Device", DEVICE, "scene")
def microscope(p, slot):
    e = p.era
    Z = F(p, 0.75, 0.06)  # stand top
    h = F(p, 0.3, 0.1)
    if slot == "shell":  # stand: stump, small table or pedestal
        if e == "Primal":
            p.cyl(0.2, 0.23, Z, mat="bark", segs=8, noise=0.04)
        elif e in ("Agrarian", "Mercantile"):
            blk(p, 0, 0, Z - 0.04, 0.5, 0.4, 0.04, mat="wood" if e == "Agrarian" else "wood_dark")
            for sx in (-1, 1):
                for sy in (-1, 1):
                    blk(p, sx * 0.21, sy * 0.16, 0, 0.04, 0.04, Z - 0.04, mat="wood" if e == "Agrarian" else "wood_dark")
        elif e in ("Industrial", "Steampunk", "Wasteland"):
            mat = {"Industrial": "steel", "Steampunk": "wood_dark", "Wasteland": "rust"}[e]
            blk(p, 0, 0, Z - 0.03, 0.5, 0.4, 0.03, mat=mat)
            for sx in (-1, 1):
                p.box((0.03, 0.35, Z - 0.03), T((sx * 0.22, 0, (Z - 0.03) / 2)), mat="iron" if e != "Steampunk" else "brass", bevel=0)
        elif e == "Future":  # scanning pod pedestal
            p.lathe([(0, 0), (0.3, 0), (0.28, 0.06), (0.15, 0.1), (0.13, Z - 0.05), (0.25, Z)], mat="body", segs=12)
        else:
            p.cyl(0.25, 0.22, Z, mat="stone", segs=6, bevel=0.05)
        return
    if e == "Primal":  # water-drop lens: a dew drop in a bent leaf over a shell
        if slot == "panel":
            p.lathe([(0, Z), (0.06, Z + 0.004), (0.07, Z + 0.015)], mat="bone", segs=8)
        elif slot == "controls":
            p.tube([(0.05, 0, Z), (0.06, 0, Z + 0.1), (0.0, 0, Z + J(p, 0.15, 0.15))], 0.004, mat="wood", segs=4)
        elif slot == "core":
            p.ball(0.012, T((0, 0, Z + 0.15)), mat="glass", segs=(6, 4))
            p.box((0.05, 0.03, 0.003), M(loc=(0.01, 0, Z + 0.14), rot=(0, 10, 0)), mat="cloth", bevel=0)
        else:
            p.ball(1.0, M(loc=(-0.12, 0, Z + 0.02), scale=(0.04, 0.03, 0.02)), mat="stone_dark", segs=(6, 4))
        return
    if e == "Agrarian":  # magnifying stone on a wooden post
        if slot == "panel":
            blk(p, 0, -0.05, Z, 0.16, 0.12, 0.02, mat="wood_dark")
        elif slot == "controls":
            blk(p, 0, 0.04, Z, 0.03, 0.03, h, mat="wood")
            p.box((0.02, 0.12, 0.02), T((0, -0.01, Z + h * J(p, 0.75, 0.1))), mat="wood", bevel=0)
        elif slot == "core":
            p.ball(1.0, M(loc=(0, -0.06, Z + h * 0.75), scale=(0.035, 0.035, 0.012)), mat="glass", segs=(8, 4))
        else:
            p.box((0.06, 0.04, 0.004), T((0, -0.05, Z + 0.022)), mat="cloth", bevel=0)
        return
    # Mercantile single-lens, Industrial compound, Steampunk multi-tube brass, Wasteland junk, Ancient stone, Future pod
    body = {"Mercantile": "brass", "Industrial": "paint", "Steampunk": "brass", "Wasteland": "steel", "Ancient": "stone", "Future": "shell_dark"}[e]
    if e == "Future":
        if slot == "panel":
            p.lathe([(0, Z), (0.18, Z), (0.2, Z + 0.02), (0, Z + 0.02)], mat="glass", segs=12)
        elif slot == "controls":
            p.ring(0.22, 0.012, T((0, 0, Z + 0.25)), mat="shell_dark", segs=12)
            for i in range(3):
                a = i * TAU / 3
                rod(p, (math.cos(a) * 0.22, math.sin(a) * 0.22, Z), (math.cos(a) * 0.22, math.sin(a) * 0.22, Z + 0.25), 0.01, mat="body")
        elif slot == "core":
            p.ring(0.21, 0.004, T((0, 0, Z + J(p, 0.12, 0.3))), mat="glow", segs=12)
        else:
            p.box((0.16, 0.004, 0.1), M(loc=(0, -0.27, Z + 0.3), rot=(-15, 0, 0)), mat="glow", bevel=0)
        return
    if slot == "panel":  # stage
        blk(p, 0, -0.02, Z + 0.06, 0.12, 0.1, 0.008, mat=body if e != "Ancient" else "stone_dark")
        blk(p, 0, 0.05, Z, 0.12, 0.1, 0.03, mat=body)
    elif slot == "controls":  # arm with focus knobs
        p.box((0.03, 0.03, h), T((0, 0.05, Z + 0.03 + h / 2)), mat=body, bevel=0)
        for s in (-1, 1):
            disk(p, (s * 0.03, 0.05, Z + h * 0.6), J(p, 0.018, 0.15), 0.012, "x", "steel" if e != "Ancient" else "gold", segs=8)
    elif slot == "core":  # tube(s) and objective
        n = 3 if e == "Steampunk" else 1
        for i in range(n):
            x = (i - (n - 1) / 2) * 0.03
            p.cyl(0.016, 0.014, h * 0.7, T((x, 0, Z + 0.09)) @ M(rot=(-12, 0, 0)), mat=body if e != "Industrial" else "steel", segs=8)
            p.cyl(0.02, 0.02, 0.015, T((x, 0.0, Z + 0.07)), mat="steel" if e != "Ancient" else "glow", segs=8)
        if e == "Wasteland":
            p.box((0.02, 0.004, 0.06), T((0.02, -0.02, Z + 0.15)), mat="cloth", bevel=0)
    else:  # mirror or lamp under the stage, slides and samples
        if e in ("Mercantile", "Industrial"):
            disk(p, (0, -0.02, Z + 0.035), J(p, 0.025, 0.1), 0.004, "y", "glass", segs=8)
        elif e == "Steampunk":
            p.ball(0.018, T((0, -0.02, Z + 0.035)), mat="glow", segs=(6, 4))
        elif e == "Wasteland":
            p.cyl(0.015, 0.012, 0.05, T((0.09, -0.04, Z)), mat="paint", segs=6)
        else:
            p.box((0.06, 0.004, 0.02), T((0, -0.07, Z + 0.035)), mat="glow", bevel=0)
        p.box((0.06, 0.02, 0.002), T((0.1, -0.08, Z + 0.001)), mat="glass", bevel=0)


# ================================================================ Lute (carried: stands on its tail)
LUTE = {"Primal": ("wood", "bark"), "Agrarian": ("ceramic", "wood"), "Mercantile": ("wood_dark", "wood"),
        "Industrial": ("paint", "wood_dark"), "Steampunk": ("brass", "wood_dark"), "Future": ("shell", "shell_dark"),
        "Wasteland": ("rust", "wood"), "Ancient": ("stone", "stone_dark")}


@function("Lute", "Device", DEVICE, "carried")
def lute(p, slot):
    e = p.era
    Rb, Hb, Ln = F(p, 0.14, 0.08), F(p, 0.3, 0.08), F(p, 0.45, 0.08)
    body, neck = LUTE[e]
    zt = Hb + Ln  # head of the neck
    if e == "Primal":  # musical bow: bent stick, one string, gourd resonator
        if slot == "shell":
            p.ball(1.0, M(loc=(0, 0.02, 0.09), scale=(0.08, 0.07, 0.09)), mat="bark", segs=(8, 5))
        elif slot == "panel":
            disk(p, (0, -0.05, 0.09), 0.04, 0.004, "y", "bark", segs=8)
        elif slot == "controls":
            pts = [(0, 0, 0.0)] + [(J(p, 0.12, 0.1) * math.sin(math.pi * t), 0, zt * 1.2 * t) for t in (0.25, 0.5, 0.75)] + [(0, 0, zt * 1.2)]
            p.tube(pts, 0.008, mat="wood", segs=5)
        elif slot == "core":
            p.tube([(0, -0.003, 0.0), (0, -0.003, zt * 1.2)], 0.0012, mat="hide", segs=3)
        else:
            p.band(0.012, zt * 0.55, h=0.025)
        return
    if slot == "shell":
        if e in ("Agrarian", "Mercantile", "Steampunk", "Ancient"):  # round back: half gourd / bowl / brass resonator
            p.ball(1.0, M(loc=(0, 0.015, Hb * 0.5), scale=(Rb, Rb * 0.5, Hb * 0.5)), mat=body, segs=(10, 6))
        elif e == "Future":  # open frame: two ribs
            for s in (-1, 1):
                p.tube([(0, 0, 0.0), (s * Rb, 0, Hb * 0.3), (s * Rb * 0.8, 0, Hb * 0.75), (0, 0, Hb)], 0.012, mat="body", segs=5)
        else:  # guitar figure-eight: two lobes
            p.cyl(Rb, Rb, 0.07, T((0, 0.035, Hb * 0.32)) @ M(rot=(90, 0, 0)), mat=body, segs=12)
            p.cyl(Rb * 0.78, Rb * 0.78, 0.07, T((0, 0.035, Hb * 0.78)) @ M(rot=(90, 0, 0)), mat=body, segs=12)
    elif slot == "panel":  # soundboard face, rosette, bridge
        if e == "Future":
            p.box((Rb * 1.4, 0.004, Hb * 0.8), T((0, 0, Hb * 0.5)), mat="glass", bevel=0)
        elif e in ("Industrial", "Wasteland"):
            disk(p, (0, -0.001, Hb * 0.55), Rb * J(p, 0.3, 0.1), 0.003, "y", "rubber", segs=10)
            p.box((Rb * 0.6, 0.01, 0.012), T((0, -0.004, Hb * 0.22)), mat=neck, bevel=0)
        else:
            disk(p, (0, -0.002, Hb * 0.5), Rb * 0.95, 0.004, "y", "wood" if e != "Ancient" else "stone_dark", segs=12)
            disk(p, (0, -0.005, Hb * 0.62), Rb * J(p, 0.25, 0.1), 0.002, "y", "rubber" if e != "Steampunk" else "glow", segs=8)
            p.box((Rb * 0.5, 0.01, 0.01), T((0, -0.008, Hb * 0.25)), mat="wood_dark" if e != "Ancient" else "gold", bevel=0)
    elif slot == "controls":  # neck and pegbox
        p.box((0.045, 0.025, Ln), T((0, -0.005, Hb + Ln / 2 - 0.02)), mat=neck, bevel=0)
        if e in ("Mercantile",):  # bent-back pegbox
            p.box((0.04, 0.02, 0.12), M(loc=(0, 0.04, zt + 0.03), rot=(60, 0, 0)), mat=neck, bevel=0)
        else:
            p.box((0.055, 0.02, J(p, 0.12, 0.15)), T((0, -0.005, zt + 0.04)), mat=neck if e != "Steampunk" else "brass", bevel=0)
        for i in range(3):
            for s in (-1, 1):
                rod(p, (s * 0.02, -0.005, zt + 0.01 + i * 0.03), (s * 0.045, -0.005, zt + 0.01 + i * 0.03), 0.004, mat="wood_dark" if e != "Future" else "shell_dark", segs=4)
    elif slot == "core":
        n = {"Agrarian": 3, "Mercantile": 6, "Industrial": 6, "Steampunk": 5, "Future": 5, "Wasteland": 4, "Ancient": 4}[e]
        mat = "glow" if e in ("Future", "Ancient") else "steel" if e not in ("Agrarian",) else "rope"
        strings(p, -0.014, 0.014, -0.022, Hb * 0.25, zt, n, r=0.0009 if e not in ("Future", "Ancient") else 0.0014, mat=mat)
    else:  # strap or ornament
        if e in ("Industrial", "Wasteland"):
            p.tube([(0, 0.07, 0.01), (Rb * 1.2, 0.08, Hb * 0.6), (Rb * 0.5, 0.06, zt * J(p, 0.85, 0.08)), (0, 0.0, zt * 0.8)], 0.008,
                   mat="leather" if e == "Industrial" else "cloth", segs=3)
        elif e == "Steampunk":
            gear(p, J(p, 0.035, 0.15), T((Rb * 0.6, -0.04, Hb * 0.8)), teeth=8, th=0.006)
        else:
            p.tube([(0, 0, zt + 0.08), (0.03, -0.01, zt + 0.02), (0.04, -0.015, zt - J(p, 0.1, 0.2))], 0.003,
                   mat="cloth" if e != "Ancient" else "gold", segs=3)


# ================================================================ Drum (carried)
@function("Drum", "Device", DEVICE, "carried")
def drum(p, slot):
    e = p.era
    R, H = F(p, 0.16, 0.1), F(p, 0.22, 0.1)
    if e == "Primal":  # slit log drum
        if slot == "shell":
            p.cyl(R, R, H * 2, T((-H, 0, R)) @ M(rot=(0, 90, 0)), mat="wood", segs=8, noise=0.03)
        elif slot == "panel":
            p.box((H * 1.5, R * 0.2, 0.02), T((0, 0, R * 1.98)), mat="rubber", bevel=0)
        elif slot == "controls":
            for s in (-1, 1):
                p.ball(1.0, M(loc=(s * H, 0, R), scale=(0.02, R * 0.95, R * 0.95)), mat="bark", segs=(6, 4))
        elif slot == "core":
            for s in (-1, 1):
                rod(p, (s * H * 0.3, -R * 1.2, 0.01), (s * H * 0.5, -R * 1.2 - 0.05, 0.03), 0.01, mat="wood", segs=4)
                p.ball(0.02, T((s * H * 0.5, -R * 1.2 - 0.05, 0.03)), mat="hide", segs=(5, 3))
        else:
            for s in (-1, 1):
                p.ball(1.0, M(loc=(s * H * 0.7, 0, 0.02), scale=(0.04, R * J(p, 0.8, 0.1), 0.025)), mat="stone", segs=(5, 3))
        return
    if e == "Future":  # touch pad
        if slot == "shell":
            p.box((R * 2.2, R * 1.6, 0.04), T((0, 0, 0.02)), mat="body", bevel=0.4, bevel_seg=2)
        elif slot == "panel":
            for i in range(4):
                p.cyl(R * 0.35, R * 0.35, 0.004, T(((i % 2 - 0.5) * R * 0.9, ((i // 2) - 0.5) * R * 0.7, 0.04)), mat="shell_dark", segs=10)
        elif slot == "controls":
            p.box((R * 1.6, 0.004, 0.006), T((0, -R * 0.8, 0.02)), mat="glow", bevel=0)
        elif slot == "core":
            for s in (-1, 1):
                rod(p, (s * R * 0.4, -R * 1.0, 0.01), (s * R * 0.6, -R * 1.2, J(p, 0.03, 0.3)), 0.006, mat="shell_dark", segs=6)
        else:
            p.box((R * 0.4, 0.04, 0.12), M(loc=(0, R * 0.6, 0.06), rot=(-20, 0, 0)), mat="shell_dark", bevel=0)
        return
    shellmat = {"Agrarian": "wood", "Mercantile": "paint", "Industrial": "paint", "Steampunk": "brass", "Wasteland": "rust", "Ancient": "stone"}[e]
    head = {"Agrarian": "hide", "Mercantile": "hide", "Industrial": "shell", "Steampunk": "hide", "Wasteland": "rubber", "Ancient": "stone_dark"}[e]
    if e == "Industrial":  # compact kit: bass drum on its side, snare, cymbal
        if slot == "shell":
            p.cyl(R, R, H * 0.8, T((0, H * 0.4, R)) @ M(rot=(90, 0, 0)), mat=shellmat, segs=12)
            p.cyl(R * 0.6, R * 0.6, H * 0.4, T((R * 1.4, 0, R * 0.9)), mat=shellmat, segs=10)
        elif slot == "panel":
            disk(p, (0, -H * 0.4, R), R * 0.98, 0.004, "y", head, segs=12)
            p.cyl(R * 0.61, R * 0.61, 0.004, T((R * 1.4, 0, R * 0.9 + H * 0.4)), mat=head, segs=10)
        elif slot == "controls":
            for s in (-1, 1):
                rod(p, (R * 1.4 + s * R * 0.4, s * R * 0.3, 0), (R * 1.4 + s * R * 0.2, s * R * 0.15, R * 0.9), 0.006, mat="steel", segs=4)
        elif slot == "core":
            rod(p, (-R * 1.2, -R * 0.3, 0), (-R * 1.2, -R * 0.3, R * 2.2), 0.006, mat="steel", segs=4)
            p.lathe([(0, 0), (R * J(p, 0.6, 0.1), -0.01), (R * 0.65, -0.015)], T((-R * 1.2, -R * 0.3, R * 2.2)), mat="brass", segs=12)
        else:
            for s in (-1, 1):
                rod(p, (R * 1.4 + s * 0.05, -R * 0.8, R * 0.9 + H * 0.45), (R * 1.4 + s * 0.12, -R * 1.2, R * 0.95 + H * 0.45), 0.005, mat="wood", segs=4)
        return
    # hand drum / snare / steam drum / scrap drum / stone drum: upright cylinder
    if slot == "shell":
        if e == "Agrarian":  # waisted hand drum
            p.lathe([(R * 0.5, 0), (R * 0.45, H * 0.4), (R * 0.95, H * 0.85), (R, H)], mat=shellmat, segs=12)
        elif e == "Steampunk":
            p.cyl(R, R, H, mat=shellmat, segs=12)
            p.cyl(R * 0.3, R * 0.3, H * 0.6, T((R * 1.1, 0, 0)), mat="copper", segs=8)
        else:
            p.lathe([(R, 0), (R * 1.0, H * 0.5), (R, H)], mat=shellmat, segs=12 if e != "Ancient" else 6)
    elif slot == "panel":
        p.cyl(R * 1.02, R * 1.02, 0.006, T((0, 0, H)), mat=head, segs=12 if e != "Ancient" else 6)
        if e in ("Mercantile", "Steampunk"):
            p.ring(R * 1.03, 0.006, T((0, 0, H - 0.005)), mat="brass" if e == "Steampunk" else "wood_dark", segs=12)
    elif slot == "controls":
        if e in ("Agrarian", "Mercantile"):  # zigzag tension ropes
            n = 6
            pts = []
            for i in range(n * 2 + 1):
                a = i * TAU / (n * 2)
                zz = H * 0.95 if i % 2 == 0 else (H * 0.45 if e == "Agrarian" else H * 0.08)
                rr = (R * 0.97 if e != "Agrarian" or i % 2 == 0 else R * 0.47) * 1.03
                pts.append((math.cos(a) * rr, math.sin(a) * rr, zz))
            p.tube(pts, 0.002, mat="rope", segs=3)
        elif e == "Steampunk":
            for i in range(6):
                a = i * TAU / 6
                rod(p, (math.cos(a) * R * 1.03, math.sin(a) * R * 1.03, H * 0.1), (math.cos(a) * R * 1.03, math.sin(a) * R * 1.03, H * 0.95), 0.004, mat="copper", segs=4)
            disk(p, (0, -R * 1.02, H * 0.5), R * 0.15, 0.006, "y", "glow", segs=8)
        elif e == "Wasteland":
            p.band(R, H * J(p, 0.5, 0.3), h=0.04)
        else:
            for i in range(3):
                p.ring(R * 1.02, 0.005, T((0, 0, H * (0.25 + i * 0.25))), mat="glow", segs=6)
    elif slot == "core":
        if e == "Agrarian":
            p.ball(R * 0.12, T((R * 0.6, -R * 0.6, H + 0.02)), mat="hide", segs=(5, 3))
        else:
            for s in (-1, 1):
                rod(p, (s * R * 0.3, -R * 0.3, H + 0.01), (s * R * 0.9, -R * 1.2, H + J(p, 0.04, 0.3)), 0.005, mat="wood" if e != "Ancient" else "stone_dark", segs=4)
    else:
        if e in ("Mercantile", "Wasteland"):
            p.tube([(-R, 0, H * 0.8), (-R * 1.3, 0.02, H * 1.6), (0, 0.05, H * J(p, 2.0, 0.08)), (R * 1.3, 0.02, H * 1.6), (R, 0, H * 0.8)], 0.008,
                   mat="leather" if e == "Mercantile" else "cloth", segs=3)
        elif e == "Steampunk":
            p.tube([(R * 1.1, 0, H * 0.6), (R * 1.1, 0, H * 1.2), (R * 0.5, 0, H * J(p, 1.3, 0.1))], 0.006, mat="copper", segs=4)
        else:
            p.ring(R * 0.5, 0.006, T((0, 0, 0.004)), mat="cloth" if e == "Agrarian" else "stone_dark", segs=8, square=False)


# ================================================================ Keyboard (scene: floor-standing)
@function("Keyboard", "Device", DEVICE, "scene")
def keyboard(p, slot):
    e = p.era
    W, Zk = F(p, 1.2, 0.08), F(p, 0.72, 0.05)
    D = 0.45
    if e in ("Primal", "Agrarian"):  # lithophone stones / bell rack on a frame
        Ht = 0.9 if e == "Primal" else 1.6
        if slot == "shell":
            for s in (-1, 1):
                p.box((0.08, 0.08, Ht), T((s * W / 2, 0, Ht / 2)), mat="wood", bevel=0, noise=0.02 if e == "Primal" else 0)
            p.box((W + 0.2, 0.08, 0.08), T((0, 0, Ht)), mat="wood", bevel=0)
            if e == "Agrarian":
                p.box((W + 0.2, 0.08, 0.06), T((0, 0, Ht * 0.55)), mat="wood", bevel=0)
        elif slot == "panel":
            for s in (-1, 1):
                p.box((0.3, 0.3, 0.06), T((s * W / 2, 0, 0.03)), mat="stone" if e == "Primal" else "wood_dark", bevel=0)
        elif slot == "controls":
            rod(p, (W * 0.3, -0.3, 0.02), (W * 0.35, -0.45, J(p, 0.06, 0.3)), 0.012, mat="wood", segs=4)
            p.ball(0.03, T((W * 0.35, -0.45, 0.06)), mat="hide" if e == "Primal" else "wood_dark", segs=(5, 3))
        elif slot == "core":
            n = 6 if e == "Primal" else 7
            for i in range(n):
                x = -W * 0.4 + W * 0.8 * i / (n - 1)
                k = 1 - i * 0.06
                if e == "Primal":
                    p.box((0.08, 0.04, 0.3 * k), T((x, 0, Ht - 0.2 * k)), mat="stone_dark", bevel=0, noise=0.04)
                    p.tube([(x, 0, Ht), (x, 0, Ht - 0.05)], 0.003, mat="rope", segs=3)
                else:
                    for row, zz in enumerate((Ht - 0.05, Ht * 0.55 - 0.05)):
                        p.lathe([(0.02, 0), (0.06 * k, -0.08 * k), (0.08 * k, -0.18 * k), (0.07 * k, -0.2 * k)], T((x, 0, zz)), mat="copper", segs=8)
        else:
            if e == "Agrarian":
                for s in (-1, 1):
                    p.plate([(-0.08, 0), (0.08, 0), (0.12, 0.15), (0, 0.22), (-0.12, 0.15)], 0.03, T((s * (W / 2 + 0.05), 0, Ht + 0.04)), mat="paint", bevel=0)
            else:
                p.ball(1.0, M(loc=(-W * 0.3, -0.3, 0.03), scale=(0.08, 0.06, 0.03)), mat="stone", segs=(6, 4))
        return
    case = {"Mercantile": "wood_dark", "Industrial": "rubber", "Steampunk": "wood_dark", "Future": "body", "Wasteland": "rust", "Ancient": "stone"}[e]
    if slot == "shell":
        if e == "Mercantile":  # harpsichord wing
            p.plate([(-W / 2, 0), (W / 2, 0), (W / 2, 0.1), (0, D * 2.2), (-W / 2, D * 2.4)], 0.2, T((0, 0, Zk + 0.1)) @ M(rot=(90, 0, 0)) @ T((0, 0, 0)), mat=case, bevel=0)
        elif e == "Industrial":  # upright piano
            blk(p, 0, D * 0.2, 0, W, D * 0.6, 1.3, mat=case)
            blk(p, 0, -D * 0.15, Zk - 0.05, W, D * 0.4, 0.05, mat=case)
        elif e == "Steampunk":  # organ console
            blk(p, 0, D * 0.2, 0, W, D * 0.6, Zk + 0.35, mat=case)
            blk(p, 0, -D * 0.1, Zk - 0.05, W, D * 0.3, 0.05, mat=case)
        elif e == "Future":
            p.box((W, D * 0.6, 0.06), T((0, 0, Zk)), mat=case, bevel=0.3, bevel_seg=2)
        elif e == "Wasteland":
            blk(p, 0, 0, Zk - 0.15, W, D * 0.6, 0.15, mat="wood")
        else:
            blk(p, 0, 0, Zk - 0.12, W, D * 0.7, 0.12, mat=case, b=0.15)
    elif slot == "panel":  # keys
        zt = Zk + (0.02 if e != "Mercantile" else 0.12)
        yk = -D * 0.25 if e != "Future" else -0.02
        white = {"Mercantile": "bone", "Industrial": "shell", "Steampunk": "bone", "Future": "glass", "Wasteland": "shell", "Ancient": "stone_dark"}[e]
        blk(p, 0, yk, zt - 0.02, W * 0.9, 0.15, 0.02, mat=white)
        n = 9
        for i in range(n):
            if i % 7 in (2, 6):
                continue
            x = -W * 0.42 + W * 0.84 * i / (n - 1)
            blk(p, x, yk + 0.03, zt, W * 0.04, 0.09, 0.012, mat="rubber" if e not in ("Future", "Ancient") else "glow")
    elif slot == "controls":  # legs and pedals
        if e in ("Mercantile", "Wasteland", "Ancient"):
            for sx in (-1, 1):
                for sy in ((-1, 1) if e != "Mercantile" else (-1,)):
                    blk(p, sx * W * 0.42, sy * D * 0.2, 0, 0.06, 0.06, Zk - (0.12 if e == "Ancient" else 0.15 if e == "Wasteland" else 0.0) - 0.0, mat="wood" if e == "Wasteland" else case)
            if e == "Mercantile":
                blk(p, 0, D * 1.6, 0, 0.06, 0.06, Zk, mat=case)
        elif e == "Future":
            p.lathe([(0, 0), (0.25, 0), (0.2, 0.03), (0.05, 0.05), (0.04, Zk - 0.03), (0.1, Zk - 0.03)], mat="shell_dark", segs=10)
        else:
            for s in (-1, 0, 1):
                blk(p, s * 0.06, -D * 0.15, 0.02, 0.03, 0.12, 0.015, mat="brass")
        if e in ("Industrial", "Steampunk"):
            for s in (-1, 1):
                blk(p, s * W * 0.45, -D * 0.2, 0, 0.05, 0.05, Zk - 0.05, mat=case)
    elif slot == "core":
        if e == "Steampunk":  # pipes
            for i in range(7):
                x = -W * 0.4 + W * 0.8 * i / 6
                hh = (0.5 + 0.35 * math.sin(i / 6 * math.pi)) * J(p, 1.0, 0.08)
                p.cyl(0.03, 0.03, hh, T((x, D * 0.35, Zk + 0.35)), mat="brass", segs=8)
                p.ball(0.012, T((x, D * 0.35 - 0.03, Zk + 0.4)), mat="glow", segs=(4, 3))
        elif e == "Mercantile":  # lid propped open
            p.plate([(-W / 2, 0), (W / 2, 0), (0, D * 2.2), (-W / 2, D * 2.4)], 0.015, T((0, 0, Zk + 0.21)) @ M(rot=(90 - J(p, 30, 0.2), 0, 0)), mat=case, bevel=0)
        elif e == "Industrial":
            blk(p, 0, D * 0.15, 1.3, W * 1.02, D * 0.65, 0.03, mat=case)
            p.box((W * 0.7, 0.01, 0.4), T((0, -D * 0.1, 1.0)), mat="wood_dark", bevel=0)
        elif e == "Future":  # light keyboard projection
            p.box((W * 0.9, 0.004, 0.2), M(loc=(0, D * 0.25, Zk + 0.15), rot=(-10, 0, 0)), mat="glow", bevel=0)
        elif e == "Wasteland":  # toy keyboard on crates with a car speaker
            p.cyl(0.12, 0.1, 0.08, T((W * 0.35, D * 0.2, Zk)) @ M(rot=(-80, 0, 0)), mat="rubber", segs=10)
        else:
            for i in range(5):
                p.box((0.05, 0.05, 0.2), T((-W * 0.4 + i * W * 0.2, D * 0.25, Zk + 0.1)), mat="stone_dark", bevel=0)
    else:  # music desk / candle / ornament
        if e in ("Mercantile", "Industrial", "Steampunk"):
            p.box((W * 0.5, 0.015, 0.2), M(loc=(0, D * (0.0 if e != "Industrial" else -0.12), Zk + (0.25 if e != "Industrial" else 0.9)), rot=(-15, 0, 0)), mat=case, bevel=0)
        elif e == "Wasteland":
            p.box((W * 0.3, 0.004, J(p, 0.1, 0.2)), T((-W * 0.2, -D * 0.31, Zk - 0.08)), mat="paint", bevel=0)
        else:
            p.box((W * 0.8, 0.004, 0.006), T((0, -D * 0.36 if e == "Ancient" else -D * 0.31, Zk - J(p, 0.05, 0.3))), mat="glow", bevel=0)


# ================================================================ MusicBox (carried)
@function("MusicBox", "Device", DEVICE, "carried")
def music_box(p, slot):
    e = p.era
    W, D, H = F(p, 0.16, 0.1), F(p, 0.11, 0.1), F(p, 0.08, 0.1)
    if e == "Primal":  # wind chime on a stick tripod
        Ht = 0.35
        if slot == "shell":
            for i in range(3):
                a = i * TAU / 3
                p.tube([(math.cos(a) * 0.1, math.sin(a) * 0.1, 0), (0, 0, Ht)], 0.006, mat="wood", segs=4)
        elif slot == "panel":
            p.ring(0.06, 0.005, T((0, 0, Ht - 0.04)), mat="bark", segs=8, square=False)
        elif slot == "controls":
            p.tube([(0, 0, Ht), (0, 0, Ht - 0.04)], 0.002, mat="rope", segs=3)
        elif slot == "core":
            for i in range(5):
                a = i * TAU / 5
                L = J(p, 0.12, 0.25)
                p.tube([(math.cos(a) * 0.06, math.sin(a) * 0.06, Ht - 0.04), (math.cos(a) * 0.06, math.sin(a) * 0.06, Ht - 0.08)], 0.001, mat="rope", segs=3)
                p.cyl(0.008, 0.006, L, T((math.cos(a) * 0.06, math.sin(a) * 0.06, Ht - 0.08 - L)), mat="bone", segs=5)
        else:
            p.box((0.03, 0.002, 0.05), T((0, 0, Ht - 0.22)), mat="feather", bevel=0)
        return
    shellmat = {"Agrarian": "wood", "Mercantile": "wood_dark", "Industrial": "wood_dark", "Steampunk": "brass", "Future": "shell",
                "Wasteland": "rust", "Ancient": "stone"}[e]
    if slot == "shell":
        if e == "Agrarian":  # hurdy box with a wheel hump
            blk(p, 0, 0, 0, W * 1.4, D, H, mat=shellmat)
        elif e == "Future":
            p.lathe([(0, 0), (W * 0.6, 0), (W * 0.62, H * 0.3), (W * 0.5, H * 0.45), (0, H * 0.45)], mat=shellmat, segs=12)
        else:
            blk(p, 0, 0, 0, W, D, H, mat=shellmat, b=0.06 if e in ("Mercantile", "Steampunk") else 0.0)
    elif slot == "panel":  # lid (open on some)
        if e == "Agrarian":
            p.cyl(H * 0.5, H * 0.5, D * 0.6, T((W * 0.3, D * 0.3, H)) @ M(rot=(90, 0, 0)), mat="wood_dark", segs=8)
        elif e == "Future":
            p.box((W * 0.9, 0.004, H * 1.5), M(loc=(0, 0, H * 1.4), rot=(J(p, 0, 1) * 10, 0, 0)), mat="glow", bevel=0)
        elif e == "Industrial":  # roll window
            p.box((W * 0.7, 0.004, H * 0.5), T((0, -D / 2 - 0.002, H * 0.5)), mat="glass", bevel=0)
            blk(p, 0, 0, H, W * 1.02, D * 1.02, 0.015, mat=shellmat)
        else:
            ang = J(p, 65, 0.2)
            p.box((W * 1.02, D, 0.012), T((0, D / 2, H)) @ M(rot=(ang, 0, 0)) @ T((0, -D / 2, 0.006)), mat=shellmat if e != "Ancient" else "stone_dark", bevel=0)
    elif slot == "controls":  # crank / winding key
        if e in ("Agrarian", "Industrial", "Wasteland"):
            p.tube([(W * (0.7 if e == "Agrarian" else 0.5), 0, H * 0.5), (W * 0.8, 0, H * 0.5), (W * 0.8, -0.03, H * 0.3)], 0.003, mat="iron" if e != "Industrial" else "brass", segs=4)
            p.cyl(0.006, 0.006, 0.02, T((W * 0.8 + 0.0, -0.03, H * 0.3)) @ M(rot=(0, 90, 0)), mat="wood", segs=5)
        elif e == "Future":
            p.ring(W * 0.55, 0.003, T((0, 0, H * 0.3)), mat="glow", segs=12)
        else:
            rod(p, (W / 2, 0, H * 0.5), (W / 2 + 0.015, 0, H * 0.5), 0.003, mat="brass" if e != "Ancient" else "gold", segs=4)
            p.box((0.004, 0.025, 0.018), T((W / 2 + 0.018, 0, H * 0.5)), mat="brass" if e != "Ancient" else "gold", bevel=0)
    elif slot == "core":  # comb and pinned drum seen inside
        if e == "Future":
            p.ball(H * 0.2, T((0, 0, H * 0.6)), mat="glow", segs=(6, 4))
        else:
            p.cyl(H * 0.15, H * 0.15, W * 0.5, T((-W * 0.25, D * 0.1, H * 0.75)) @ M(rot=(0, 90, 0)), mat="brass" if e != "Ancient" else "glow", segs=8)
            p.box((W * 0.45, D * 0.3, 0.004), T((0, -D * 0.1, H * 0.7)), mat="steel" if e != "Ancient" else "gold", bevel=0)
    else:  # figure or ornament
        if e in ("Mercantile", "Steampunk"):  # tiny dancer on the lid top / gear
            p.lathe([(0, 0), (0.012, 0.004), (0.004, 0.02), (0.006, 0.03), (0, 0.04)], T((0, -D * 0.1, H + 0.004)), mat="shell" if e == "Mercantile" else "brass", segs=6)
            if e == "Steampunk":
                gear(p, J(p, 0.02, 0.2), T((-W * 0.3, -D / 2 - 0.004, H * 0.5)), teeth=8, th=0.004, mat="copper")
                p.ball(0.006, T((W * 0.3, -D / 2 - 0.004, H * 0.6)), mat="glow", segs=(4, 3))
        elif e == "Wasteland":
            p.box((W * 0.4, 0.004, H * 0.4), M(loc=(-W * 0.15, -D / 2 - 0.002, H * 0.5), rot=(0, J(p, 8, 1), 0)), mat="paint", bevel=0)
        elif e == "Ancient":
            p.box((W * 0.8, 0.004, 0.006), T((0, -D / 2 - 0.002, H * J(p, 0.4, 0.2))), mat="glow", bevel=0)
        elif e == "Industrial":
            p.cyl(0.02, 0.02, 0.004, T((0, 0, H + 0.015)), mat="brass", segs=8)
        else:
            p.box((W * 0.3, 0.004, H * 0.3), T((-W * 0.4, -D / 2 - 0.002, H * J(p, 0.5, 0.2))), mat="paint", bevel=0)


# ================================================================ BoardGame (carried)
@function("BoardGame", "Device", DEVICE, "carried")
def board_game(p, slot):
    e = p.era
    S = F(p, 0.32, 0.08)
    n = 4
    z = {"Primal": 0.03, "Agrarian": 0.025, "Mercantile": 0.035, "Industrial": 0.012, "Steampunk": 0.08, "Future": 0.03,
         "Wasteland": 0.015, "Ancient": 0.04}[e]
    bmat = {"Primal": "stone", "Agrarian": "wood", "Mercantile": "wood_dark", "Industrial": "paint", "Steampunk": "brass",
            "Future": "shell_dark", "Wasteland": "steel", "Ancient": "stone"}[e]
    light = {"Primal": "bone", "Agrarian": "wood", "Mercantile": "bone", "Industrial": "shell", "Steampunk": "brass",
             "Future": "glow", "Wasteland": "paint", "Ancient": "gold"}[e]
    dark = {"Primal": "stone_dark", "Agrarian": "rubber", "Mercantile": "wood_dark", "Industrial": "rubber", "Steampunk": "iron",
            "Future": "shell", "Wasteland": "rust", "Ancient": "stone_dark"}[e]

    def cell(i, j):
        return (-S * 0.375 + S * 0.25 * i, -S * 0.375 + S * 0.25 * j)

    def piece(x, y, mat, tall):
        if e in ("Primal", "Wasteland"):
            p.ball(S * 0.05, M(loc=(x, y, z + S * 0.03), scale=(1, 1, 0.7)), mat=mat, segs=(6, 4))
        elif e == "Future":
            p.cyl(S * 0.06, S * 0.0, S * 0.1 * tall, T((x, y, z + 0.004)), mat=mat, segs=6)
        else:
            p.lathe([(0, 0), (S * 0.05, 0), (S * 0.04, S * 0.02), (S * 0.02, S * 0.06 * tall), (S * 0.03, S * 0.09 * tall), (0, S * 0.1 * tall)],
                    T((x, y, z)), mat=mat, segs=6 if e != "Ancient" else 4)

    if slot == "shell":
        if e == "Primal":
            p.ball(1.0, M(loc=(0, 0, z * 0.5), scale=(S * 0.6, S * 0.55, z * 0.6)), mat=bmat, segs=(8, 4), noise=0.03)
        elif e == "Industrial":  # folding board half open
            p.box((S, S * 0.5, z), T((0, -S * 0.25, z / 2)), mat=bmat, bevel=0)
            p.box((S, S * 0.5, z), T((0, 0, 0)) @ M(rot=(J(p, 25, 0.3), 0, 0)) @ T((0, S * 0.25, z / 2)), mat=bmat, bevel=0)
        elif e == "Steampunk":
            blk(p, 0, 0, 0, S * 1.05, S * 1.05, z, mat="wood_dark")
            blk(p, 0, 0, z - 0.01, S, S, 0.01, mat=bmat)
        elif e == "Future":
            p.lathe([(0, 0), (S * 0.62, 0), (S * 0.6, z), (0, z)], mat=bmat, segs=12)
        else:
            blk(p, 0, 0, 0, S, S, z, mat=bmat, b=0.1 if e in ("Mercantile", "Ancient") else 0.0)
    elif slot == "panel":  # alternate squares
        gmat = {"Primal": "rubber", "Future": "glow", "Ancient": "glow"}.get(e, dark if e != "Steampunk" else "copper")
        for i in range(n):
            for j in range(n):
                if (i + j) % 2 == 0:
                    x, y = cell(i, j)
                    if e in ("Primal", "Future", "Ancient"):
                        p.box((S * 0.22, S * 0.02, 0.002), T((x, y, z + 0.001)), mat=gmat, bevel=0)
                    else:
                        p.box((S * 0.25, S * 0.25, 0.002), T((x, y, z + 0.001)), mat=gmat, bevel=0)
    elif slot == "controls":
        for k in range(3):
            x, y = cell(k, 0)
            piece(x, y, light, J(p, 1.0, 0.2) if k == 1 else 0.8)
    elif slot == "core":
        for k in range(3):
            x, y = cell(k + 1, 3)
            piece(x, y, dark if e != "Future" else "shell", J(p, 1.0, 0.2) if k == 1 else 0.8)
    else:
        if e == "Steampunk":  # automaton arm on the side
            p.cyl(S * 0.06, S * 0.06, S * 0.3, T((S * 0.6, 0, 0)), mat="brass", segs=8)
            rod(p, (S * 0.6, 0, S * 0.3), (S * 0.35, 0, S * 0.35 + J(p, 0.03, 0.3)), 0.006, mat="copper", segs=5)
            gear(p, S * 0.07, T((S * 0.6, -S * 0.07, S * 0.2)), teeth=6, th=0.005)
            p.ball(0.008, T((S * 0.6, -S * 0.07, S * 0.3)), mat="glow", segs=(4, 3))
        elif e in ("Mercantile", "Agrarian"):  # drawer / piece box
            blk(p, S * 0.7, 0, 0, S * 0.25, S * 0.4, S * 0.08, mat=bmat)
        elif e == "Future":
            p.box((S * 0.5, 0.004, S * 0.2), M(loc=(0, S * 0.65, S * 0.15), rot=(-10, 0, 0)), mat="glow", bevel=0)
        else:  # dice or a pebble bag
            for k in range(2):
                p.box((S * 0.05, S * 0.05, S * 0.05), M(loc=(S * 0.65 + k * S * 0.08, -S * 0.2, S * 0.025), rot=(0, 0, J(p, 20, 1))), mat=light if e != "Ancient" else "stone_dark", bevel=0)
