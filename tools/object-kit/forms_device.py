"""Device family, 3C set (殼體器: 殼體、面板／顯示、控制件、核心／光源、附件／天線): Terminal, Camera, AudioPlayer,
Calculator, Navigator, Spyglass, Radio, Display (cosmos_chimera P1-19, ADR-0016).

Same slots and frame as kit_forms' Communicator / GameConsole / Timepiece: everything sits on z = 0 facing -Y.
Terminal, Radio and Display are scene-only, so they are floor-standing pieces (a counting table, a cabinet, a TV on
its own stand) with the origin at floor contact. Camera, AudioPlayer, Calculator, Navigator and Spyglass are
carried: NpcMeshes.Carry holds a non-hafted kit with its bottom in the hand or hangs it on the hip, so they stay
palm-sized, stand on their own base and keep under ~500 triangles assembled. Spyglasses stand on the objective end
(eyepiece up): a tube lying along Y would be stretched lengthwise by morph, which scales X and Y by height.
Glow follows the game rule for the 3C group (everyday-objects.md 抽樣/發光): only Steampunk, Future, Wasteland and
Ancient draw glow parts; the other eras show the same element as paint, bone or glass.
Frame values (F) are drawn first in each era branch, in a fixed order, so every slot variant meets the others.
"""
import math

from mathutils import Matrix

from kit_forms import DEVICE, F, J, coin, function
from kit_lib import M
from forms_furniture import gear, runes
from forms_tools import disk, rod
from forms_vessel import bail, bell_shape, closed, shell

T = Matrix.Translation


# ---------------------------------------------------------------- helpers
def blk(p, x, y, z, w, d, h, mat="body", **kw):
    """Box with its bottom face at z."""
    return p.box((w, d, h), T((x, y, z + h / 2)), mat=mat, **kw)


def knob(p, x, y, z, r, t, mat="accent", segs=8, **kw):
    """Round knob, dial or lens on a -Y face at y, standing t proud of it."""
    return disk(p, (x, y - t / 2, z), r, t, "y", mat, segs=segs, **kw)


def legs(p, hx, hy, z0, z1, r, mat="body", segs=6, splay=0.0, y0=0.0):
    """Four round legs from z1 down to the floor at z0, feet pushed out by splay."""
    for sx in (-1, 1):
        for sy in (-1, 1):
            rod(p, (sx * (hx + splay), y0 + sy * (hy + splay), z0), (sx * hx, y0 + sy * hy, z1), r, r * 0.85, mat=mat, segs=segs)


def slats(p, x0, x1, y, z0, z1, n, t, mat):
    """Vertical grille bars across a -Y face."""
    for i in range(n):
        x = x0 + (x1 - x0) * (i + 0.5) / n
        p.box((t, t, z1 - z0), T((x, y, (z0 + z1) / 2)), mat=mat, bevel=0)


def wires(p, pts, r=0.003, mat="rubber"):
    p.tube(pts, r, mat=mat, segs=4)


def patch(p, x, y, z, w, h, mat="paint", rot=0.0):
    """Riveted scrap patch on a -Y face (Wasteland)."""
    p.box((w, 0.004, h), M(loc=(x, y - 0.002, z), rot=(0, rot, 0)), mat=mat, bevel=0)


def crt(p, x, y, z, w, d, h, mat="body"):
    """Television / monitor cabinet with its bottom at z and a front bezel; returns the screen centre (x, yf, zc)."""
    blk(p, x, y, z, w, d, h, mat=mat)
    p.box((w * 0.62, d * 0.5, h * 0.7), T((x, y + d * 0.6, z + h * 0.5)), mat=mat, bevel=0)
    return (x - w * 0.08, y - d / 2, z + h * 0.52)


def tilted(p, w, d, h):
    """Placement of a slanted reading/desk top: front edge low, back edge high, centred at height h."""
    return M(loc=(0, 0, h), rot=(math.degrees(math.atan2(d * 0.25, d)), 0, 0))


# ================================================================ Terminal (scene: floor-standing)
@function("Terminal", "Device", DEVICE, "scene")
def terminal(p, slot):
    e = p.era
    if e == "Primal":  # counting-stone array: grooved slab, pebble tallies, notched tally stone, knotted cords
        R, hs = F(p, 0.52), F(p, 0.62)
        top = 0.1
        if slot == "shell":
            p.cyl(R, R * 0.9, top, mat="stone", segs=9, noise=0.05)
            if coin(p):
                p.ball(1.0, M(loc=(R * 0.8, -R * 0.45, 0.05), scale=(0.1, 0.08, 0.06)), mat="stone", segs=(6, 4), noise=0.05)
        elif slot == "panel":
            for i in range(5):
                x = (i - 2) * R * 0.3
                p.box((0.03, R * J(p, 1.15, 0.08), 0.014), T((x, -R * 0.1, top)), mat="stone_dark", bevel=0)
            p.box((R * 1.4, 0.03, 0.014), T((0, -R * J(p, 0.15, 0.3), top)), mat="stone_dark", bevel=0)
        elif slot == "controls":
            for i in range(4):
                x = (i - 1.5) * R * 0.3
                for k in range(p.rng.randint(1, 4)):
                    for y in (-R * 0.45 + k * 0.07, R * 0.15 + k * 0.07):
                        if p.rng.random() < 0.7:
                            p.ball(0.028, M(loc=(x, y, top + 0.016), scale=(1, 0.9, 0.6)), mat=p.rng.choice(("bone", "stone_dark")),
                                   segs=(5, 3))
        elif slot == "core":
            y = R * 0.72
            p.cyl(0.1, 0.06, hs, M(loc=(0, y, 0), rot=(J(p, 4, 0.5), 0, 0)), mat="stone", segs=5, noise=0.05)
            for i in range(p.rng.randint(4, 7)):
                p.box((0.06, 0.02, 0.012), T((0, y - 0.085 + i * 0.002, hs * (0.25 + i * 0.09))), mat="stone_dark", bevel=0)
        else:
            y = R * 0.72
            for s in (-1, 1):
                x1 = s * J(p, R * 0.55, 0.2)
                pts = [(s * 0.05, y - 0.02, hs * 0.9), (x1 * 0.6, y - R * 0.2, hs * 0.4), (x1, y - R * 0.4, top + 0.01)]
                p.tube(pts, 0.008, mat="rope", segs=4)
                for t in (0.35, 0.6, 0.85):
                    p.ball(0.018, T((x1 * t, y - R * 0.4 * t, hs * 0.9 - (hs * 0.9 - top) * t)), mat="rope", segs=(5, 3))
    elif e == "Agrarian":  # counting-rod board on a low floor table, rod tube, ledger and ink stone
        W, D, H = F(p, 0.78), F(p, 0.5), F(p, 0.34)
        if slot == "shell":
            blk(p, 0, 0, H - 0.035, W, D, 0.035, mat="wood")
            for sx in (-1, 1):
                blk(p, sx * W * 0.4, 0, 0, 0.05, D * 0.85, 0.04, mat="wood")
                blk(p, sx * W * 0.4, 0, 0.04, 0.045, J(p, 0.05, 0.2), H - 0.075, mat="wood", bevel=0)
        elif slot == "panel":
            bw, bd = W * 0.62, D * 0.7
            blk(p, -W * 0.08, 0, H, bw, bd, 0.012, mat="wood_dark")
            for i in range(1, 5):
                p.box((0.005, bd, 0.004), T((-W * 0.08 - bw / 2 + bw * i / 5, 0, H + 0.013)), mat="bone", bevel=0)
            p.box((bw, 0.005, 0.004), T((-W * 0.08, -bd * J(p, 0.12, 0.3), H + 0.013)), mat="bone", bevel=0)
        elif slot == "controls":
            bw, bd = W * 0.62, D * 0.7
            for c in range(5):
                cx = -W * 0.08 - bw / 2 + bw * (c + 0.5) / 5
                n = p.rng.randint(1, 5)
                for k in range(n):
                    if p.rng.random() < 0.5 or k == 0:
                        p.box((0.006, 0.09, 0.006), M(loc=(cx - 0.03 + k * 0.014, -bd * 0.28, H + 0.016)), mat="bone", bevel=0)
                    else:
                        p.box((0.09, 0.006, 0.006), T((cx, bd * 0.12 + k * 0.014, H + 0.016)), mat="bone", bevel=0)
        elif slot == "core":
            x, y = W * 0.36, D * 0.22
            p.cyl(0.04, 0.042, J(p, 0.16, 0.15), T((x, y, H)), mat="bark", segs=8)
            p.ring(0.042, 0.004, T((x, y, H + 0.05)), mat="rope", segs=8)
            for i in range(p.rng.randint(4, 7)):
                a = i * 2.4
                rod(p, (x + math.cos(a) * 0.02, y + math.sin(a) * 0.02, H + 0.02), (x + math.cos(a) * 0.035, y + math.sin(a) * 0.035, H + 0.21),
                    0.003, mat="bone", segs=3)
        else:
            x = W * 0.33
            blk(p, x, -D * 0.18, H, 0.13, 0.17, J(p, 0.025, 0.3), mat="hide")
            blk(p, x, -D * 0.18 + 0.005, H + 0.026, 0.12, 0.15, 0.002, mat="bone", bevel=0)
            blk(p, -W * 0.08, -D * 0.43, H, 0.09, 0.06, 0.018, mat="stone_dark")
    elif e == "Mercantile":  # slide-rule desk: slanted writing desk, wall-long brass slide rule, ledger, drawers
        W, D, H = F(p, 0.86), F(p, 0.52), F(p, 0.92)
        top = tilted(p, W, D, H)
        if slot == "shell":
            p.box((W, D, 0.03), top @ T((0, 0, 0)), mat="body")
            for sx in (-1, 1):
                for sy in (-1, 1):
                    p.lathe([(0.03, 0), (0.024, 0.08), (0.032, H * 0.35), (0.022, H * 0.7), (0.028, H - 0.05)],
                            T((sx * (W / 2 - 0.04), sy * (D / 2 - 0.04), 0)), mat="body", segs=6)
            blk(p, 0, D * 0.05, H * 0.55, W - 0.06, D * 0.85, H * 0.36, mat="body", bevel=0)
        elif slot == "panel":
            # A rule as long as the desk, on a back riser at eye level: a hand-sized one would vanish at scene scale.
            rl = W * 0.95
            ry = D / 2 + 0.03
            zr = H + D * 0.15
            blk(p, 0, ry + 0.01, H - 0.02, rl, 0.04, zr - H + 0.32, mat="body")
            blk(p, 0, ry - 0.016, zr + 0.04, rl, 0.012, 0.07, mat="wood")
            blk(p, J(p, 0.05, 1.0), ry - 0.022, zr + 0.11, rl, 0.012, 0.06, mat="brass")
            blk(p, 0, ry - 0.016, zr + 0.17, rl, 0.012, 0.07, mat="wood")
            for i in range(13):
                x = -rl * 0.46 + rl * 0.92 * math.log(1 + i) / math.log(13)
                for z in (zr + 0.08, zr + 0.21):
                    p.box((0.004, 0.004, 0.03), T((x, ry - 0.024, z)), mat="iron", bevel=0)
        elif slot == "controls":
            rl, ry, zr = W * 0.95, D / 2 + 0.03, H + D * 0.15
            x = J(p, 0.1, 2.0)
            p.box((0.06, 0.004, 0.24), T((x, ry - 0.032, zr + 0.14)), mat="glass", bevel=0)
            for dz in (-0.115, 0.115):
                p.box((0.07, 0.014, 0.012), T((x, ry - 0.032, zr + 0.14 + dz)), mat="brass", bevel=0)
            p.cyl(0.022, 0.026, 0.04, top @ T((W * 0.38, D * 0.32, 0.015)), mat="glass", segs=8)
            rod(p, (W * 0.38, D * 0.3, H + 0.1), (W * 0.42 + J(p, 0.02, 0.5), D * 0.42, H + 0.26), 0.003, 0.001, mat="feather", segs=4)
        elif slot == "core":
            for sx in (-1, 1):
                zc = H * 0.73
                p.box((W * 0.42, 0.012, H * 0.28), T((sx * W * 0.23, -D * 0.38, zc)), mat="wood_dark")
                p.ball(J(p, 0.016, 0.2), T((sx * W * 0.23, -D * 0.4 - 0.008, zc)), mat="brass", segs=(6, 4))
        else:
            a = J(p, 10, 0.4)
            for s in (-1, 1):
                p.box((0.17, 0.24, 0.012), top @ M(loc=(s * 0.088 - W * 0.12, -D * 0.06, 0.022), rot=(0, s * a, 0)), mat="bone", bevel=0)
            p.box((0.36, 0.25, 0.008), top @ T((-W * 0.12, -D * 0.06, 0.017)), mat="leather", bevel=0)
    elif e == "Industrial":  # punch-card computer: steel cabinet, lamp panel, keypunch desk, tape reels, card hopper
        W, D, H = F(p, 0.92), F(p, 0.62), F(p, 1.55)
        dc = D * 0.55
        yc = D / 2 - dc / 2
        yf = D / 2 - dc
        zd = 0.74
        if slot == "shell":
            blk(p, 0, yc, 0.06, W, dc, H - 0.06, mat="steel")
            blk(p, 0, yc, 0, W * 0.96, dc * 0.9, 0.06, mat="rubber", bevel=0)
            blk(p, 0, yc, H, W * 1.02, dc * 1.04, J(p, 0.03, 0.3), mat="paint")
        elif slot == "panel":
            blk(p, 0, yf - 0.005, zd + 0.12, W * 0.86, 0.012, H * 0.3, mat="paint", bevel=0)
            for r in range(3):
                for c in range(8):
                    if p.rng.random() < 0.8:
                        knob(p, -W * 0.36 + c * W * 0.1, yf - 0.011, zd + 0.18 + r * 0.07, 0.013, 0.01,
                             mat=p.rng.choice(("accent", "bone", "glass")), segs=6)
            for sx in (-1, 1):
                knob(p, sx * W * 0.3, yf - 0.011, zd + 0.12 + H * 0.3 - 0.04, 0.03, 0.008, mat="bone", segs=10)
        elif slot == "controls":
            dd = yf + D / 2
            blk(p, 0, -D / 2 + dd / 2, zd, W * 0.7, dd, 0.04, mat="paint")
            for sx in (-1, 1):
                blk(p, sx * W * 0.32, -D / 2 + 0.04, 0, 0.04, 0.04, zd, mat="steel", bevel=0)
            for k in range(3):
                for i in range(p.rng.randint(6, 8)):
                    p.box((0.028, 0.028, 0.012), T((-0.14 + i * 0.04, -D / 2 + 0.06 + k * 0.035, zd + 0.046 + k * 0.006)), mat="bone", bevel=0)
        elif slot == "core":
            zr = H * 0.82
            for sx in (-1, 1):
                knob(p, sx * W * 0.22, yf, zr, J(p, 0.12, 0.1), 0.02, mat="rubber", segs=12)
                knob(p, sx * W * 0.22, yf - 0.02, zr, 0.03, 0.012, mat="steel", segs=8)
            p.box((W * 0.44, 0.006, 0.012), T((0, yf - 0.012, zr - 0.1)), mat="paint", bevel=0)
        else:
            x = W / 2 + 0.11
            blk(p, x, yc - 0.05, 0, 0.2, 0.24, J(p, 0.72, 0.1), mat="steel")
            blk(p, x, yc - 0.06, J(p, 0.72, 0.1), 0.16, 0.08, 0.06, mat="bone", bevel=0)
            wires(p, [(W / 2 - 0.1, D / 2, 0.3), (W / 2 + 0.05, D / 2 + 0.12, 0.02), (W / 2 + 0.25, D / 2 + 0.1, 0.01)], r=0.012)
    elif e == "Steampunk":  # difference engine: plinth, brass frame, columns of figure wheels, crank, gauge glow
        W, D, H = F(p, 0.96), F(p, 0.46), F(p, 1.25)
        zb = 0.32
        cols = 4
        if slot == "shell":
            blk(p, 0, 0, 0, W, D, zb, mat="wood_dark", bevel_seg=1)
            blk(p, 0, 0, H - 0.03, W * 0.98, D * 0.8, 0.03, mat="brass", bevel_seg=1)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    p.cyl(0.018, 0.018, H - zb, T((sx * W * 0.46, sy * D * 0.34, zb)), mat="brass", segs=6)
            p.box((W * 1.01, D * 1.01, J(p, 0.03, 0.3)), T((0, 0, zb - 0.04)), mat="brass", bevel=0)
        elif slot == "panel":
            for c in range(cols):
                x = -W * 0.33 + c * W * 0.22
                n = 4
                for k in range(n):
                    z = zb + 0.08 + k * (H - zb - 0.14) / n
                    p.cyl(0.07, 0.07, 0.09, T((x, 0, z)), mat="brass", segs=8)
                    p.box((0.024, 0.004, 0.044), M(loc=(x, -0.066, z + 0.045), rot=(0, 0, p.rng.uniform(-1, 1) * 30)), mat="bone", bevel=0)
                p.cyl(0.012, 0.012, H - zb, T((x, 0, zb)), mat="iron", segs=4)
        elif slot == "controls":
            x = W / 2 + 0.03
            z = zb + (H - zb) * J(p, 0.45, 0.2)
            disk(p, (x, 0, z), J(p, 0.12, 0.15), 0.02, "x", "brass", segs=12)
            rod(p, (x, 0, z), (x + 0.06, 0, z), 0.012, mat="iron", segs=6)
            rod(p, (x + 0.02, 0, z + 0.1), (x + 0.11, 0, z + 0.1), 0.012, mat="wood_dark", segs=6)
        elif slot == "core":
            knob(p, -W * 0.25, -D / 2, zb * 0.55, J(p, 0.06, 0.1), 0.015, mat="brass", segs=12)
            knob(p, -W * 0.25, -D / 2 - 0.015, zb * 0.55, 0.05, 0.004, mat="glow", segs=12)
            p.cyl(0.02, 0.02, 0.18, M(loc=(W * 0.15, -D / 2 - 0.02, zb * 0.5), rot=(0, 90, 0)), mat="glow", segs=8)
            for x in (W * 0.15, W * 0.33):
                p.cyl(0.026, 0.026, 0.014, M(loc=(x - 0.007, -D / 2 - 0.02, zb * 0.5), rot=(0, 90, 0)), mat="copper", segs=8)
        else:
            gear(p, J(p, 0.1, 0.15), M(loc=(-W / 2 - 0.01, 0, zb + 0.2), rot=(0, 0, 90)), teeth=8, th=0.015)
            gear(p, 0.06, M(loc=(-W / 2 - 0.01, 0.12, zb + 0.34), rot=(0, 0, 90)), teeth=6, th=0.015)
            p.tube([(W * 0.4, D / 2, zb), (W * 0.4, D / 2 + 0.06, zb + 0.2), (W * 0.4, D / 2 + 0.06, H + J(p, 0.2, 0.3))], 0.022, mat="copper", segs=6)
    elif e == "Future":  # holo terminal: tapered pedestal, slanted desk, floating screen, glow keypad, emitter
        W, H = F(p, 0.74), F(p, 1.0)
        D = W * 0.6
        top = tilted(p, W, D, H)
        zs = H + 0.42
        if slot == "shell":
            p.lathe([(0.24, 0), (0.25, 0.04), (0.12, 0.1), (0.09, H * 0.6), (0.14, H - 0.04)], mat="body", segs=10)
            p.box((W, D, 0.05), top, mat="body", bevel_seg=1)
        elif slot == "panel":
            p.box((W * 0.95, 0.008, J(p, 0.44, 0.1)), M(loc=(0, D * 0.32, zs), rot=(-8, 0, 0)), mat="glow", bevel=0)
            for sx in (-1, 1):
                p.box((0.012, 0.012, 0.46), M(loc=(sx * W * 0.49, D * 0.32, zs), rot=(-8, 0, 0)), mat="shell_dark", bevel=0)
        elif slot == "controls":
            p.box((W * 0.6, D * 0.45, 0.004), top @ T((0, -D * 0.12, 0.026)), mat="glow", bevel=0)
            for i in range(p.rng.randint(2, 4)):
                p.box((0.06, 0.04, 0.004), top @ T((W * 0.38, -D * 0.3 + i * 0.06, 0.027)), mat="shell_dark", bevel=0)
        elif slot == "core":
            p.cyl(0.05, J(p, 0.03, 0.2), 0.08, top @ T((0, D * 0.3, 0.02)), mat="shell_dark", segs=10)
            p.cyl(0.025, 0.06, 0.012, top @ T((0, D * 0.3, 0.1)), mat="glow", segs=10)
        else:
            for sx in (-1, 1):
                p.plate([(0, 0), (sx * J(p, 0.12, 0.2), 0.02), (sx * 0.04, H * 0.55), (0, H * 0.6)], 0.012,
                        T((sx * 0.09, 0, 0.05)), mat="shell_dark", bevel=0)
            p.ring(0.26, 0.006, T((0, 0, 0.01)), mat="glow", segs=12)
    elif e == "Wasteland":  # scrap terminal: crate stand, salvaged monitor, plank keyboard, car battery, wire nest
        W, H = F(p, 0.74), F(p, 0.72)
        mw, md, mh = 0.46, 0.4, 0.38
        if slot == "shell":
            blk(p, 0, 0.04, 0, W, 0.5, H, mat="wood", noise=0.02)
            for z in (H * 0.33, H * 0.66):
                p.box((W + 0.01, 0.51, 0.03), T((0, 0.04, z)), mat="wood_dark", bevel=0)
            crt(p, J(p, -0.03, 1.0), 0.05, H, mw, md, mh, mat="rust")
            patch(p, mw * 0.3, 0.05 - md / 2, H + mh * 0.2, 0.1, 0.08, rot=J(p, 12, 0.5))
        elif slot == "panel":
            p.screen(mw * 0.66, mh * 0.6, T((-mw * 0.08, 0.05 - md / 2 - 0.003, H + mh * 0.52)))
            p.box((0.12, 0.006, 0.03), M(loc=(-mw * 0.25, 0.05 - md / 2 - 0.006, H + mh * 0.75), rot=(0, J(p, 25, 0.4), 0)), mat="cloth", bevel=0)
        elif slot == "controls":
            p.box((0.5, 0.2, 0.025), M(loc=(0, -0.3, H + 0.01), rot=(J(p, 4, 1), 0, 0)), mat="wood", bevel=0)
            for k in range(3):
                for i in range(8):
                    if p.rng.random() < 0.85:
                        p.box((0.032, 0.03, 0.014), T((-0.15 + i * 0.043, -0.35 + k * 0.04, H + 0.028)),
                              mat=p.rng.choice(("rubber", "paint", "bone")), bevel=0)
        elif slot == "core":
            blk(p, W / 2 + 0.14, -0.05, 0, 0.22, 0.16, 0.18, mat="paint")
            p.ball(0.018, T((W / 2 + 0.08, -0.13, 0.15)), mat="glow", segs=(6, 4))
            for x in (W / 2 + 0.08, W / 2 + 0.2):
                p.cyl(0.016, 0.016, 0.03, T((x, -0.05, 0.18)), mat="iron", segs=6)
        else:
            wires(p, [(W / 2 + 0.2, -0.05, 0.21), (W / 2 + 0.1, 0.1, 0.4), (mw * 0.2, 0.25, H + 0.1), (0, 0.25, H + 0.2)], r=0.008)
            wires(p, [(-mw * 0.2, 0.2, H + mh), (-mw * 0.25, 0.22, H + mh + J(p, 0.3, 0.3)), (-mw * 0.1, 0.24, H + mh + 0.45)], r=0.004, mat="iron")
            p.band(0.06, H + mh + 0.05, m=T((-mw * 0.22, 0.21, 0)), h=0.04)
    else:  # Ancient: seamless stone console, rune face, relief keys on the slant, floating glow core
        W, H = F(p, 0.72), F(p, 1.05)
        D = 0.45
        top = tilted(p, W, D, H)
        if slot == "shell":
            blk(p, 0, 0, 0, W * 1.15, D * 1.15, 0.12, mat="stone_dark")
            blk(p, 0, 0, 0.12, W, D, H - 0.14, mat="body")
            p.box((W * 1.05, D * 1.05, 0.08), top, mat="body", bevel_seg=1)
        elif slot == "panel":
            blk(p, 0, -D / 2 - 0.004, H * 0.25, W * 0.7, 0.012, H * 0.5, mat="stone_dark", bevel=0)
            for x in (-W * 0.22, 0, W * 0.22):
                runes(p, x, -D / 2 - 0.012, H * 0.3, H * 0.7, n=p.rng.randint(2, 4), w=0.04)
        elif slot == "controls":
            for i in range(3):
                for k in range(2):
                    p.cyl(0.035, 0.03, 0.015, top @ T((-W * 0.25 + i * W * 0.25, -D * 0.25 + k * 0.12, 0.035)), mat="gold",
                          segs=6)
            p.box((W * J(p, 0.6, 0.15), 0.01, 0.006), top @ T((0, D * 0.25, 0.042)), mat="glow", bevel=0)
        elif slot == "core":
            z = H + J(p, 0.32, 0.15)
            p.ball(0.07, M(loc=(0, D * 0.15, z), rot=(0, 0, 45), scale=(1, 1, 1.5)), mat="glow", segs=(4, 2))
            p.ring(0.11, 0.008, M(loc=(0, D * 0.15, z), rot=(70, 0, 0)), mat="gold", segs=10)
        else:
            for sx in (-1, 1):
                p.plate([(0, 0), (sx * J(p, 0.14, 0.2), 0), (sx * 0.06, H * 0.8), (0, H * 0.85)], 0.08,
                        M(loc=(sx * W / 2, 0, 0.12), rot=(0, 0, 0)), mat="stone_dark", bevel=0.1)
                runes(p, sx * (W / 2 + 0.04), -0.045, 0.2, H * 0.6, n=2, w=0.02)


# ================================================================ Camera (carried)
@function("Camera", "Device", DEVICE, "carried")
def camera(p, slot):
    e = p.era
    if e == "Primal":  # charcoal sketch board: lashed stick frame, stretched hide, charcoal, lashings and thong
        W, H = F(p, 0.28), F(p, 0.22)
        if slot == "shell":
            for z in (0.01, H):
                p.tube([(-W / 2 - 0.02, 0, z), (0, 0, z + J(p, 0.006, 0.8)), (W / 2 + 0.02, 0, z)], 0.008, mat="wood", segs=4)
            for x in (-W / 2, W / 2):
                p.tube([(x, 0.0, -0.0), (x, 0.0, H + 0.03)], 0.008, mat="wood", segs=4)
        elif slot == "panel":
            p.box((W * 0.92, 0.004, H * 0.88), T((0, 0.006, H * 0.5 + 0.005)), mat="hide", bevel=0, noise=0.02)
        elif slot == "controls":
            for i in range(p.rng.randint(1, 3)):
                rod(p, (-W * 0.3 + i * 0.03, -0.012, 0.02), (-W * 0.3 + i * 0.03 + J(p, 0.05, 0.3), -0.014, 0.024), 0.004, mat="stone_dark", segs=4)
        elif slot == "core":
            for i in range(p.rng.randint(3, 5)):
                x = p.rng.uniform(-W * 0.3, W * 0.3)
                z = p.rng.uniform(H * 0.3, H * 0.8)
                p.box((p.rng.uniform(0.03, 0.08), 0.002, 0.005), M(loc=(x, 0.003, z), rot=(0, p.rng.uniform(-60, 60), 0)), mat="stone_dark", bevel=0)
        else:
            for x in (-W / 2, W / 2):
                for z in (0.01, H):
                    p.ball(0.013, T((x, 0, z)), mat="rope", segs=(5, 3))
            p.tube([(-W / 2, 0.005, H), (0, 0.015, H + J(p, 0.08, 0.3)), (W / 2, 0.005, H)], 0.003, mat="hide", segs=3)
    elif e == "Agrarian":  # pinhole dark box: wooden box, cloth viewing hood, pinhole and slide shutter, rope strap
        W, D, H = F(p, 0.18), F(p, 0.24), F(p, 0.15)
        if slot == "shell":
            blk(p, 0, 0, 0, W, D, H, mat="wood")
        elif slot == "panel":
            p.box((W * 0.7, 0.004, H * 0.7), T((0, D / 2 + 0.002, H / 2)), mat="bone", bevel=0)
            p.lathe([(0.075, 0), (0.09, 0.04), (J(p, 0.1, 0.12), 0.07)], M(loc=(0, D / 2, H / 2), rot=(-90, 0, 0)) @ M(rot=(0, 0, 45)),
                    mat="cloth", segs=4)
        elif slot == "controls":
            p.box((0.05, 0.008, 0.04), T((J(p, 0.03, 0.6), -D / 2 - 0.006, H * 0.5)), mat="wood_dark", bevel=0)
            p.box((0.07, 0.004, 0.006), T((0, -D / 2 - 0.003, H * 0.5 + 0.024)), mat="iron", bevel=0)
            p.box((0.07, 0.004, 0.006), T((0, -D / 2 - 0.003, H * 0.5 - 0.024)), mat="iron", bevel=0)
        elif slot == "core":
            knob(p, 0, -D / 2, H * 0.5, J(p, 0.015, 0.2), 0.004, mat="iron", segs=8)
            knob(p, 0, -D / 2 - 0.004, H * 0.5, 0.004, 0.002, mat="stone_dark", segs=6)
        else:
            bail(p, W / 2 + 0.005, H * 0.6, J(p, 0.1, 0.25), 0.004, mat="rope", n=6)
            for sx in (-1, 1):
                p.box((0.006, 0.03, 0.02), T((sx * (W / 2 + 0.003), 0, H * 0.6)), mat="iron", bevel=0)
    elif e == "Mercantile":  # wooden box camera: brass lens barrel, ground-glass back, top handle, focus knob
        W, D, H = F(p, 0.17), F(p, 0.2), F(p, 0.18)
        if slot == "shell":
            blk(p, 0, 0, 0, W, D, H, mat="body")
            for sx in (-1, 1):
                for sz in (0, 1):
                    p.box((0.016, D * 1.01, 0.016), T((sx * W / 2, 0, sz * H)), mat="brass", bevel=0)
        elif slot == "panel":
            p.box((W * 0.8, 0.006, H * 0.75), T((0, D / 2 + 0.003, H / 2)), mat="brass", bevel=0)
            p.box((W * 0.65, 0.006, H * 0.6), T((0, D / 2 + 0.005, H / 2)), mat="glass", bevel=0)
        elif slot == "controls":
            bail(p, J(p, 0.04, 0.2), H, 0.03, 0.005, mat="leather", n=5)
            disk(p, (W / 2 + 0.006, p.rng.uniform(-0.02, 0.02), H * 0.4), 0.018, 0.012, "x", "brass", segs=8)
        elif slot == "core":
            L = J(p, 0.05, 0.25)
            p.cyl(0.036, 0.03, L, M(loc=(0, -D / 2, H * 0.5), rot=(90, 0, 0)), mat="brass", segs=10)
            knob(p, 0, -D / 2 - L, H * 0.5, 0.026, 0.003, mat="glass", segs=10)
        else:
            p.tube([(0, -D / 2 - 0.02, H * 0.5 - 0.035), (J(p, 0.03, 0.4), -D / 2 - 0.03, H * 0.2), (0.04, -D / 2 - 0.02, 0.02)], 0.002, mat="brass", segs=3)
            for sx in (-1, 1):
                p.cyl(0.012, 0.014, 0.012, T((sx * W * 0.35, 0, -0.012)), mat="brass", segs=6)
    elif e == "Industrial":  # folding bellows camera: body, drop bed, stepped bellows, lens board, flash dish
        W, H, D, L = F(p, 0.15), F(p, 0.1), F(p, 0.045), F(p, 0.09)
        y0 = D / 2
        if slot == "shell":
            blk(p, 0, y0, 0, W, D, H, mat="paint")
            p.box((W * 0.6, L + 0.02, 0.006), T((0, -L / 2, 0.003)), mat="steel", bevel=0)
        elif slot == "panel":
            n = 4
            for i in range(n):
                t = i / n
                s = 1 - 0.35 * t
                p.box((W * 0.7 * s, L / n * 0.98, H * 0.8 * s), T((0, -L * (i + 0.5) / n, 0.01 + H * 0.4 * s)), mat="leather", bevel=0)
        elif slot == "controls":
            p.cyl(0.006, 0.006, 0.008, T((W * 0.32, y0, H)), mat="steel", segs=6)
            p.cyl(0.012, 0.012, 0.008, T((-W * 0.3, y0, H)), mat="steel", segs=8)
            blk(p, 0, y0, H, J(p, 0.04, 0.2), 0.024, 0.018, mat="rubber", bevel=0)
        elif slot == "core":
            zl = 0.01 + H * 0.4 * 0.74
            blk(p, 0, -L - 0.004, 0.006, W * 0.5, 0.008, H * 0.6, mat="steel", bevel=0)
            knob(p, 0, -L - 0.008, zl, J(p, 0.018, 0.15), 0.02, mat="rubber", segs=10)
            knob(p, 0, -L - 0.028, zl, 0.014, 0.002, mat="glass", segs=10)
        else:
            x = -W / 2 - 0.02
            rod(p, (-W / 2, y0, H * 0.7), (x, y0, H + 0.04), 0.003, mat="steel", segs=4)
            p.lathe([(0.004, 0), (J(p, 0.035, 0.15), 0.012), (0.038, 0.016)], M(loc=(x, y0 - 0.003, H + 0.04), rot=(90, 0, 0)), mat="steel", segs=8)
            disk(p, (x, y0 - 0.006, H + 0.04), 0.008, 0.008, "y", "glass", segs=6)
    elif e == "Steampunk":  # brass camera: wood-panelled brass box, lens turret, gauge glow, dials, viewfinder tube
        W, D, H = F(p, 0.16), F(p, 0.13), F(p, 0.13)
        if slot == "shell":
            blk(p, 0, 0, 0, W, D, H, mat="brass", bevel_seg=1)
            for sx in (-1, 1):
                p.box((0.004, D * 0.8, H * 0.8), T((sx * W / 2, 0, H / 2)), mat="wood_dark", bevel=0)
        elif slot == "panel":
            knob(p, J(p, -W * 0.2, 0.3), D / 2 + 0.008, H * 0.6, 0.025, 0.008, mat="brass", segs=10)
            knob(p, -W * 0.2, D / 2 + 0.008 - 0.008, H * 0.6, 0.019, 0.002, mat="glow", segs=10)
            p.box((W * 0.25, 0.004, H * 0.35), T((W * 0.2, D / 2 + 0.002, H * 0.45)), mat="glass", bevel=0)
        elif slot == "controls":
            for x in (-W * 0.25, W * 0.25):
                p.cyl(J(p, 0.018, 0.2), 0.016, 0.01, T((x, 0, H)), mat="copper", segs=8)
            rod(p, (W / 2, -D * 0.2, H * 0.8), (W / 2 + 0.025, -D * 0.2, H + 0.02), 0.004, mat="brass", segs=4)
        elif slot == "core":
            L = J(p, 0.06, 0.2)
            p.lathe([(0.03, 0), (0.034, L * 0.6), (0.042, L * 0.65), (0.042, L)], M(loc=(0, -D / 2, H * 0.48), rot=(90, 0, 0)), mat="brass", segs=10)
            knob(p, 0, -D / 2 - L, H * 0.48, 0.036, 0.002, mat="glass", segs=10)
            for sx in (-1, 1):
                p.cyl(0.012, 0.012, 0.02, M(loc=(sx * W * 0.32, -D / 2, H * 0.75), rot=(90, 0, 0)), mat="brass", segs=6)
        else:
            p.cyl(0.012, 0.014, D * J(p, 1.1, 0.15), M(loc=(W * 0.25, D / 2, H + 0.018), rot=(90, 0, 0)), mat="brass", segs=8)
            p.ball(0.008, T((-W * 0.35, -D * 0.2, H + 0.01)), mat="glow", segs=(6, 4))
    elif e == "Future":  # floating camera orb over its palm dock: lens eye, stabiliser fins, thruster glow
        R, zc = F(p, 0.055), F(p, 0.11)
        if slot == "shell":
            p.ball(R, M(loc=(0, 0, zc), scale=(1, J(p, 1.05, 0.05), 0.92)), mat="body", segs=(10, 6))
        elif slot == "panel":
            knob(p, 0, -R * 0.78, zc, R * 0.6, 0.02, mat="shell_dark", segs=10)
            knob(p, 0, -R * 0.78 - 0.02, zc, R * J(p, 0.32, 0.15), 0.004, mat="glow", segs=10)
        elif slot == "controls":
            for sx in (-1, 1):
                p.plate([(0, -0.015), (sx * J(p, 0.04, 0.2), -0.005), (sx * 0.035, 0.012), (0, 0.015)], 0.004,
                        T((sx * R * 0.92, 0.0, zc)), mat="shell_dark", bevel=0)
        elif slot == "core":
            p.cyl(R * 0.45, R * 0.25, 0.012, T((0, 0, zc - R * 0.92 - 0.006)), mat="shell_dark", segs=8)
            p.cyl(R * 0.22, R * J(p, 0.12, 0.3), 0.02, T((0, 0, zc - R - 0.03)), mat="glow", segs=8)
        else:
            p.cyl(0.05, 0.045, 0.01, mat="shell_dark", segs=10)
            p.box((J(p, 0.05, 0.2), 0.004, 0.003), T((0, -0.03, 0.011)), mat="glow", bevel=0)
    elif e == "Wasteland":  # scrap camera: dented body, tin-can lens wired on, taped screen, battery strapped on
        W, D, H = F(p, 0.15), F(p, 0.07), F(p, 0.1)
        if slot == "shell":
            p.box((W, D, H), M(loc=(0, 0, H / 2), rot=(0, J(p, 3, 1), 0)), mat="body")
            patch(p, -W * 0.25, -D / 2, H * 0.6, 0.05, 0.04, rot=J(p, 15, 0.5))
        elif slot == "panel":
            p.screen(W * 0.5, H * 0.5, T((W * 0.1, D / 2 + 0.003, H * 0.55)))
            p.box((W * 0.55, 0.004, 0.012), M(loc=(W * 0.1, D / 2 + 0.006, H * J(p, 0.7, 0.15)), rot=(0, 8, 0)), mat="cloth", bevel=0)
        elif slot == "controls":
            p.cyl(0.008, 0.008, 0.01, T((W * 0.3, 0, H)), mat="iron", segs=6)
            p.cyl(0.011, 0.011, 0.008, T((-W * J(p, 0.2, 0.4), 0, H)), mat="paint", segs=6)
        elif slot == "core":
            L = J(p, 0.05, 0.25)
            p.cyl(0.03, 0.03, L, M(loc=(W * 0.1, -D / 2, H * 0.5), rot=(90, 0, 0)), mat="steel", segs=9)
            knob(p, W * 0.1, -D / 2 - L, H * 0.5, 0.024, 0.003, mat="glass", segs=8)
            p.band(0.03, L * 0.5, m=M(loc=(W * 0.1, -D / 2, H * 0.5), rot=(90, 0, 0)), h=0.02)
        else:
            p.cyl(0.016, 0.016, W * J(p, 0.8, 0.15), M(loc=(-W * 0.4, D / 2 + 0.017, H * 0.25), rot=(0, 90, 0)), mat="paint", segs=7)
            wires(p, [(-W / 2, 0, H * 0.7), (-W / 2 - 0.03, 0, H + 0.03), (W / 2 + 0.03, 0, H + 0.03), (W / 2, 0, H * 0.7)], r=0.0025, mat="iron")
    else:  # Ancient: stone eye: rounded stone lens block, crystal eye, rune slit back, relief stud controls
        W, D, H = F(p, 0.14), F(p, 0.1), F(p, 0.12)
        if slot == "shell":
            p.box((W, D, H), T((0, 0, H / 2)), mat="body", bevel_seg=1)
        elif slot == "panel":
            for i in range(3):
                p.box((W * 0.5 if i % 2 == 0 else W * 0.3, 0.006, 0.008), T((0, D / 2 + 0.002, H * (0.3 + i * 0.2))), mat="glow", bevel=0)
            if coin(p):
                p.box((0.008, 0.006, H * 0.5), T((-W * 0.35, D / 2 + 0.002, H * 0.5)), mat="glow", bevel=0)
        elif slot == "controls":
            for x in (-W * 0.25, W * 0.25):
                p.cyl(0.014, J(p, 0.01, 0.2), 0.008, T((x, 0, H)), mat="gold", segs=6)
        elif slot == "core":
            knob(p, 0, -D / 2, H * 0.5, J(p, 0.04, 0.1), 0.012, mat="stone_dark", segs=8)
            p.ball(0.026, M(loc=(0, -D / 2 - 0.014, H * 0.5), scale=(1, 0.6, 1)), mat="glow", segs=(8, 4))
        else:
            p.ring(J(p, 0.03, 0.15), 0.008, M(loc=(0, 0, H + 0.025), rot=(90, 0, 0)), mat="stone_dark", segs=8)


# ================================================================ AudioPlayer (carried)
@function("AudioPlayer", "Device", DEVICE, "carried")
def audio_player(p, slot):
    e = p.era
    if e == "Primal":  # resonance gourd: two-bulb gourd, hide-covered mouth, string bow, seed rattle, carry cord
        H, R = F(p, 0.26), F(p, 0.085)
        prof = [(R * 0.5, 0), (R, H * 0.18), (R * 0.95, H * 0.4), (R * 0.5, H * 0.58), (R * 0.62, H * 0.76), (R * 0.42, H * 0.95),
                (R * 0.3, H)]
        if slot == "shell":
            closed(p, prof, mat="bark", segs=8)
        elif slot == "panel":
            knob(p, 0, -R * 0.95, H * 0.24, R * J(p, 0.35, 0.2), 0.006, mat="stone_dark", segs=8)
            p.cyl(R * 0.32, R * 0.3, 0.008, T((0, 0, H)), mat="hide", segs=8)
        elif slot == "controls":
            x = R * 1.05
            p.tube([(x, 0, H * 0.08), (x + J(p, 0.04, 0.3), 0, H * 0.5), (x, 0, H * 0.95)], 0.006, mat="wood", segs=4)
            rod(p, (x, 0, H * 0.1), (x, 0, H * 0.93), 0.0015, mat="hide", segs=3)
        elif slot == "core":
            for i in range(p.rng.randint(3, 5)):
                p.ball(0.01, T((-R * 0.6 + i * 0.012, -R * 0.55, H * 0.58 - i * 0.03)), mat="bone", segs=(5, 3))
        else:
            p.ring(R * 0.52, 0.005, T((0, 0, H * J(p, 0.58, 0.04))), mat="rope", segs=8, square=False)
            p.tube([(-R * 0.5, 0, H * 0.58), (-R * 0.8, 0.02, H * 1.1), (0, 0.02, H * 1.25)], 0.004, mat="rope", segs=3)
    elif e == "Agrarian":  # hand-crank music box: lid propped open, pinned drum and comb, side crank, feet
        W, D, H = F(p, 0.17), F(p, 0.12), F(p, 0.08)
        if slot == "shell":
            blk(p, 0, 0, 0.008, W, D, H - 0.008, mat="wood")
        elif slot == "panel":
            a = J(p, 105, 0.1)
            p.box((W, D, 0.01), M(loc=(0, D / 2, H), rot=(-a, 0, 0)) @ T((0, -D / 2, 0.005)), mat="wood")
            p.box((W * 0.7, 0.002, D * 0.6), M(loc=(0, D / 2, H), rot=(-a, 0, 0)) @ T((0, -D / 2, -0.001)) @ M(rot=(90, 0, 0)), mat="bone", bevel=0)
        elif slot == "controls":
            x = W / 2
            rod(p, (x, 0, H * 0.55), (x + 0.012, 0, H * 0.55), 0.003, mat="iron", segs=4)
            rod(p, (x + 0.012, 0, H * 0.55), (x + 0.012, 0, H * 0.55 + J(p, 0.035, 0.2)), 0.003, mat="iron", segs=4)
            rod(p, (x + 0.012, 0, H * 0.55 + J(p, 0.035, 0.2)), (x + 0.025, 0, H * 0.55 + 0.035), 0.005, mat="wood_dark", segs=5)
        elif slot == "core":
            disk(p, (0, 0.01, H + 0.004), 0.014, W * 0.6, "x", "brass", segs=8)
            p.box((W * 0.55, 0.02, 0.003), T((0, -0.018, H + J(p, 0.002, 0.5))), mat="iron", bevel=0)
        else:
            for sx in (-1, 1):
                for sy in (-1, 1):
                    p.cyl(0.008, J(p, 0.01, 0.2), 0.008, T((sx * W * 0.4, sy * D * 0.35, 0)), mat="wood_dark", segs=5)
    elif e == "Mercantile":  # cylinder phonograph: base box, brass bed, wax cylinder, crank, brass horn
        W, D, H = F(p, 0.2), F(p, 0.13), F(p, 0.08)
        zc = H + 0.035
        if slot == "shell":
            blk(p, 0, 0, 0, W, D, H, mat="body")
            p.box((W * 1.04, D * 1.04, 0.01), T((0, 0, 0.005)), mat="body", bevel=0)
        elif slot == "panel":
            blk(p, 0, 0, H, W * 0.85, D * 0.6, 0.006, mat="brass", bevel=0)
            for x in (-W * 0.36, W * 0.36):
                blk(p, x, 0, H, 0.012, 0.02, J(p, 0.04, 0.1), mat="brass", bevel=0)
        elif slot == "controls":
            x = W / 2
            rod(p, (x, 0, H * 0.5), (x + 0.015, 0, H * 0.5), 0.003, mat="brass", segs=4)
            rod(p, (x + 0.015, 0, H * 0.5), (x + 0.015, -J(p, 0.04, 0.2), H * 0.5), 0.003, mat="brass", segs=4)
            rod(p, (x + 0.015, -0.04, H * 0.5), (x + 0.03, -0.04, H * 0.5), 0.005, mat="wood_dark", segs=5)
        elif slot == "core":
            disk(p, (0, 0, zc), J(p, 0.027, 0.1), W * 0.62, "x", "bone", segs=10)
        else:
            x0 = -W * 0.1
            rod(p, (x0, 0.0, zc + 0.03), (x0, 0.0, zc + 0.06), 0.006, mat="brass", segs=6)
            L = J(p, 0.18, 0.15)
            p.lathe([(0.008, 0), (0.012, L * 0.4), (0.025, L * 0.75), (0.05, L * 0.95), (0.055, L)],
                    M(loc=(x0, 0.0, zc + 0.06), rot=(-90 - 25, 0, 0)), mat="brass", segs=10)
    elif e == "Industrial":  # portable gramophone: case with lid up, platter and record, tone arm, crank, handle
        W, D, H = F(p, 0.28), F(p, 0.26), F(p, 0.1)
        if slot == "shell":
            blk(p, 0, 0, 0, W, D, H, mat="leather")
            p.box((W, 0.02, D), M(loc=(0, D / 2, H), rot=(J(p, 8, 0.5), 0, 0)) @ T((0, 0.01, D / 2)), mat="leather")
        elif slot == "panel":
            p.cyl(D * 0.4, D * 0.4, 0.008, T((-W * 0.08, 0, H)), mat="cloth", segs=12)
            p.cyl(D * J(p, 0.37, 0.05), D * 0.37, 0.004, T((-W * 0.08, 0, H + 0.008)), mat="rubber", segs=12)
        elif slot == "controls":
            x = W * 0.38
            p.cyl(0.015, 0.015, 0.02, T((x, D * 0.3, H)), mat="steel", segs=8)
            a = math.radians(J(p, 120, 0.12))
            p.tube([(x, D * 0.3, H + 0.02), (x + math.cos(a) * 0.08, D * 0.3 + math.sin(a) * -0.08, H + 0.024),
                    (x + math.cos(a) * 0.17, D * 0.3 - math.sin(a) * 0.17, H + 0.02)], 0.005, mat="steel", segs=5)
            rod(p, (W / 2, -D * 0.2, H * 0.5), (W / 2 + 0.04, -D * 0.2, H * 0.5), 0.004, mat="steel", segs=4)
            rod(p, (W / 2 + 0.04, -D * 0.2, H * 0.5), (W / 2 + 0.04, -D * 0.2 - 0.04, H * 0.3), 0.006, mat="rubber", segs=5)
        elif slot == "core":
            p.cyl(0.004, 0.004, 0.025, T((-W * 0.08, 0, H)), mat="steel", segs=5, bevel=0)
            p.cyl(D * J(p, 0.12, 0.15), D * 0.12, 0.003, T((-W * 0.08, 0, H + 0.011)), mat="accent", segs=10)
        else:
            k = J(p, 0.03, 0.25)
            p.tube([(-0.05, -D / 2, H * 0.5), (-0.04, -D / 2 - k, H * 0.5), (0.04, -D / 2 - k, H * 0.5), (0.05, -D / 2, H * 0.5)], 0.006, mat="rubber", segs=4)
            for x in (-W * 0.35, W * 0.35):
                p.box((0.02, 0.006, J(p, 0.03, 0.2)), T((x, -D / 2 - 0.003, H * 0.7)), mat="steel", bevel=0)
    elif e == "Steampunk":  # brass gramophone: flower horn, wood base with brass band, platter, glow tube, gears
        W, H, S = F(p, 0.22), F(p, 0.11), F(p, 0.17)
        if slot == "shell":
            blk(p, 0, 0, 0, W, W, H, mat="wood_dark", bevel_seg=1)
            p.box((W * 1.02, W * 1.02, J(p, 0.012, 0.3)), T((0, 0, H * 0.82)), mat="brass", bevel=0)
        elif slot == "panel":
            p.cyl(W * 0.42, W * 0.42, 0.01, T((0, 0, H)), mat="brass", segs=12)
            p.cyl(W * J(p, 0.38, 0.05), W * 0.38, 0.004, T((0, 0, H + 0.01)), mat="rubber", segs=12)
        elif slot == "controls":
            disk(p, (W / 2 + 0.004, -W * 0.15, H * 0.5), J(p, 0.03, 0.2), 0.008, "x", "copper", segs=8)
            p.tube([(W * 0.4, W * 0.4, H), (W * 0.42, W * 0.4, H + 0.05), (W * 0.1, W * 0.25, H + 0.06)], 0.004, mat="brass", segs=4)
        elif slot == "core":
            p.cyl(0.012, 0.012, W * 0.4, M(loc=(-W * 0.2, -W / 2 - 0.012, H * 0.5), rot=(0, 90, 0)), mat="glow", segs=8)
            for x in (-W * 0.2, W * 0.2):
                p.cyl(0.016, 0.016, J(p, 0.012, 0.3), M(loc=(x, -W / 2 - 0.012, H * 0.5), rot=(0, 90, 0)), mat="brass", segs=8)
        else:
            p.tube([(W * 0.4, W * 0.4, H), (W * 0.4, W * 0.4, H + 0.08), (W * 0.32, W * 0.3, H + 0.14)], 0.008, mat="brass", segs=6)
            prof = [(0.01, 0), (0.016, S * 0.35), (0.04, S * 0.7), (S * J(p, 0.55, 0.1), S)]
            p.lathe(prof, M(loc=(W * 0.32, W * 0.3, H + 0.14), rot=(-55, 0, 25)), mat="brass", segs=8)
    elif e == "Future":  # ear-hook player in its dock: pill dock, glow ring, touch strip, glow core, two ear hooks
        R = F(p, 0.045)
        zc = R + 0.008
        if slot == "shell":
            p.cyl(R, R, 0.03, M(loc=(0, 0.015, zc), rot=(90, 0, 0)), mat="body", segs=12)
            p.box((R * 1.6, 0.03, 0.012), T((0, 0, 0.006)), mat="shell_dark", bevel_seg=1)
        elif slot == "panel":
            p.ring(R * 0.75, 0.003, M(loc=(0, -0.016, zc), rot=(90, 0, 0)), mat="glow", segs=12)
            if coin(p):
                p.box((R * 0.5, 0.002, 0.003), T((0, -0.017, zc - R * J(p, 0.4, 0.2))), mat="glow", bevel=0)
        elif slot == "controls":
            p.box((0.004, J(p, 0.018, 0.2), R * 1.1), T((R + 0.001, 0, zc)), mat="shell_dark", bevel=0)
        elif slot == "core":
            knob(p, 0, -0.015, zc, R * J(p, 0.35, 0.15), 0.004, mat="glow", segs=10)
        else:
            for sx in (-1, 1):
                x = sx * R * 0.55
                k = J(p, 1.0, 0.12)
                p.tube([(x, 0.0, zc + R * 0.8), (x, 0.0, zc + R + 0.03 * k), (x + sx * 0.012, 0.0, zc + R + 0.05 * k),
                        (x + sx * 0.03, 0.0, zc + R + 0.04 * k), (x + sx * 0.035, 0.0, zc + R + 0.015)], 0.0035, mat="shell_dark", segs=4)
                p.ball(0.008, T((x, -0.004, zc + R + 0.03 * k)), mat="shell_dark", segs=(6, 4))
    elif e == "Wasteland":  # scrap boombox: rusty case, two speaker cones, tape window, VU glow, rebar handle
        W, H, D = F(p, 0.28), F(p, 0.14), F(p, 0.08)
        if slot == "shell":
            p.box((W, D, H), M(loc=(0, 0, H / 2), rot=(0, J(p, 2, 1), 0)), mat="body")
            patch(p, W * 0.38, -D / 2, H * 0.3, 0.05, 0.06, rot=J(p, 20, 0.5))
        elif slot == "panel":
            for x in (-W * 0.3, W * 0.3):
                r = J(p, 0.045, 0.12)
                knob(p, x, -D / 2, H * 0.5, r, 0.006, mat="iron", segs=10)
                knob(p, x, -D / 2 - 0.006, H * 0.5, r * 0.75, 0.004, mat="rubber", segs=8)
        elif slot == "controls":
            p.box((W * 0.24, 0.004, H * 0.3), T((0, -D / 2 - 0.002, H * 0.38)), mat="glass", bevel=0)
            for i in range(p.rng.randint(3, 5)):
                p.box((0.014, 0.014, 0.008), T((-W * 0.1 + i * 0.018, -D * 0.1, H + 0.003)), mat=p.rng.choice(("rubber", "paint", "iron")), bevel=0)
        elif slot == "core":
            p.box((W * 0.22, 0.004, J(p, 0.016, 0.2)), T((0, -D / 2 - 0.003, H * 0.78)), mat="glow", bevel=0)
        else:
            bail(p, W * 0.3, H, J(p, 0.05, 0.2), 0.005, mat="iron", n=5)
            wires(p, [(W * 0.4, 0, H), (W * 0.45, 0.01, H + 0.08), (W * 0.55, 0.02, H + 0.14)], r=0.002, mat="iron")
    else:  # Ancient: singing stone bowl on a ring stand, rune course, gold studs, floating glow core
        R, H = F(p, 0.09), F(p, 0.08)
        z0 = 0.025
        if slot == "shell":
            shell(p, [(R * 0.5, z0), (R * 0.9, z0 + H * 0.35), (R, z0 + H)], 0.012, mat="body", segs=10)
        elif slot == "panel":
            for i in range(6):
                a = i * math.tau / 6 + math.pi / 6
                p.box((0.016, 0.006, J(p, 0.014, 0.25)), M(loc=(math.cos(a) * R * 0.93, math.sin(a) * R * 0.93, z0 + H * 0.6),
                                                          rot=(0, 0, math.degrees(a) + 90)), mat="glow", bevel=0)
        elif slot == "controls":
            for i in range(3):
                a = i * math.tau / 3 - math.pi / 2
                p.ball(J(p, 0.009, 0.2), T((math.cos(a) * R, math.sin(a) * R, z0 + H)), mat="gold", segs=(6, 4))
        elif slot == "core":
            p.ball(R * 0.35, M(loc=(0, 0, z0 + H * J(p, 1.0, 0.1)), rot=(0, 0, 45)), mat="glow", segs=(4, 2))
        else:
            p.cyl(R * 0.62, R * J(p, 0.5, 0.1), z0, mat="stone_dark", segs=8)


# ================================================================ Calculator (carried)
@function("Calculator", "Device", DEVICE, "carried")
def calculator(p, slot):
    e = p.era
    if e == "Primal":  # tally sticks: notched stick bundle, notches, loose count sticks, binding, toggle cord
        L = F(p, 0.22)
        n = 4
        if slot == "shell":
            for i in range(n):
                p.box((L * (1 - 0.08 * (i % 2)), 0.014, 0.014), M(loc=(0, -0.022 + i * 0.015, 0.007 + (i % 2) * 0.004), rot=(0, 0, p.rng.uniform(-1, 1) * 3)),
                      mat="wood", bevel=0.15)
        elif slot == "panel":
            for i in range(n):
                k = p.rng.randint(2, 5)
                for j in range(k):
                    p.box((0.003, 0.016, 0.004), T((-L * 0.4 + j * 0.022, -0.022 + i * 0.015, 0.014 + (i % 2) * 0.004)), mat="stone_dark", bevel=0)
        elif slot == "controls":
            for i in range(p.rng.randint(2, 4)):
                rod(p, (L * 0.15 + i * 0.012, 0.04, 0.004), (L * 0.2 + i * 0.012, 0.04 + J(p, 0.07, 0.2), 0.006), 0.004, mat="bark", segs=4)
        elif slot == "core":
            p.ring(0.026, 0.004, M(loc=(p.rng.uniform(-0.02, 0.02) + 0.02, 0, 0.01), rot=(0, 90, 0), scale=(1, 1.3, 1)), mat="rope", segs=8)
        else:
            p.tube([(-L / 2, 0, 0.01), (-L / 2 - 0.04, 0.0, 0.01), (-L / 2 - J(p, 0.08, 0.2), 0.02, 0.005)], 0.0025, mat="hide", segs=3)
            p.box((0.008, 0.03, 0.008), T((-L / 2 - J(p, 0.08, 0.2), 0.02, 0.005)), mat="bone", bevel=0)
    elif e == "Agrarian":  # abacus standing on its long rail: frame, beam, rods, beads (one above, four below), feet
        # Upright, rods vertical: lying flat its beads are edge-on at every NPC and sheet view angle.
        W, H = F(p, 0.24), F(p, 0.13)
        n = 7
        z0 = 0.008
        zb = z0 + H * 0.7
        t = 0.018
        if slot == "shell":
            for z in (z0, z0 + H):
                p.box((W, t, 0.012), T((0, 0, z)), mat="wood_dark", bevel=0)
            for x in (-W / 2, W / 2):
                p.box((0.012, t, H + 0.012), T((x, 0, z0 + H / 2)), mat="wood_dark", bevel=0)
        elif slot == "panel":
            p.box((W, t * 0.8, J(p, 0.008, 0.2)), T((0, 0, zb)), mat="wood_dark", bevel=0)
        elif slot == "controls":
            for i in range(n):
                x = -W / 2 + W * (i + 0.5) / n
                zs = [zb + 0.012 if p.rng.random() < 0.5 else z0 + H - 0.012]
                k = p.rng.randint(0, 4)
                zs += [z0 + 0.012 + j * 0.013 for j in range(4 - k)] + [zb - 0.012 - j * 0.013 for j in range(k)]
                for z in zs:
                    p.lathe([(0, z - 0.006), (0.0095, z), (0, z + 0.006)], M(loc=(x, 0, 0), rot=(0, 0, 45)), mat="wood", segs=4)
        elif slot == "core":
            for i in range(n):
                x = -W / 2 + W * (i + 0.5) / n
                p.cyl(0.0016, 0.0016, H, T((x, 0, z0)), mat="bark", segs=3, cap=False)
        else:
            for x in (-W / 2, W / 2):
                p.box((0.016, t * J(p, 2.2, 0.15), 0.01), T((x, 0, 0.005)), mat="brass", bevel=0)
    elif e == "Mercantile":  # slide rule: stock, engraved scales, slider, glass cursor, leather half-sleeve
        L, W = F(p, 0.3), F(p, 0.04)
        t = 0.008
        if slot == "shell":
            for y in (-W * 0.35, W * 0.35):
                p.box((L, W * 0.3, t), T((0, y, t / 2)), mat="wood", bevel=0)
            p.box((L, W, 0.003), T((0, 0, 0.0015)), mat="wood", bevel=0)
        elif slot == "panel":
            for y in (-W * 0.35, W * 0.35):
                for i in range(p.rng.randint(8, 12)):
                    x = -L * 0.45 + L * 0.9 * (math.log(1 + i) / math.log(13))
                    p.box((0.0015, W * 0.12, 0.001), T((x, y - W * 0.08 * (1 if y < 0 else -1), t + 0.0005)), mat="stone_dark", bevel=0)
        elif slot == "controls":
            p.box((L, W * 0.38, t * 0.9), T((J(p, 0.02, 1.5), 0, t * 0.45 + 0.0015)), mat="bone", bevel=0)
        elif slot == "core":
            x = J(p, 0.03, 2.0)
            p.box((0.022, W * 1.1, 0.002), T((x, 0, t + 0.002)), mat="glass", bevel=0)
            for y in (-W * 0.55, W * 0.55):
                p.box((0.026, 0.004, t + 0.004), T((x, y, (t + 0.004) / 2)), mat="brass", bevel=0)
        else:
            ls = L * J(p, 0.3, 0.15)
            p.box((ls, W * 1.15, t * 1.6), T((L / 2 - ls / 2 + 0.004, 0, t * 0.8)), mat="leather", bevel=0)
    elif e == "Industrial":  # arithmometer: steel box, digit windows, slide levers, side crank, carry handle
        W, D, H = F(p, 0.22), F(p, 0.11), F(p, 0.07)
        n = 5
        if slot == "shell":
            blk(p, 0, 0, 0, W, D, H, mat="paint")
            p.box((W * 1.04, D * 1.04, 0.008), T((0, 0, 0.004)), mat="steel", bevel=0)
        elif slot == "panel":
            p.box((W * 0.8, D * 0.22, 0.004), T((0, D * 0.3, H + 0.002)), mat="steel", bevel=0)
            for i in range(n + 2):
                p.box((0.012, D * 0.14, 0.002), T((-W * 0.33 + i * W * 0.11, D * 0.3, H + 0.005)), mat="bone", bevel=0)
        elif slot == "controls":
            for i in range(n):
                x = -W * 0.3 + i * W * 0.12
                p.box((0.004, D * 0.5, 0.002), T((x, -D * 0.12, H + 0.001)), mat="rubber", bevel=0)
                y = -D * 0.12 + p.rng.uniform(-D * 0.2, D * 0.2)
                p.cyl(0.005, 0.004, 0.012, T((x, y, H)), mat="bone", segs=5)
        elif slot == "core":
            x = W / 2
            rod(p, (x, 0, H * 0.6), (x + 0.012, 0, H * 0.6), 0.004, mat="steel", segs=5)
            rod(p, (x + 0.012, 0, H * 0.6), (x + 0.012, -J(p, 0.04, 0.2), H * 0.6 + 0.02), 0.003, mat="steel", segs=4)
            p.cyl(0.006, 0.006, 0.02, M(loc=(x + 0.012, -0.04, H * 0.6 + 0.02), rot=(0, 90, 0)), mat="rubber", segs=6)
        else:
            bail(p, J(p, 0.04, 0.2), H, 0.02, 0.004, mat="steel", n=5, y=-D * 0.05)
    elif e == "Steampunk":  # gear calculator: brass box on wood plinth, figure wheels with glow window, keys, gear
        W, D, H = F(p, 0.18), F(p, 0.12), F(p, 0.06)
        if slot == "shell":
            blk(p, 0, 0, 0, W * 1.06, D * 1.06, 0.012, mat="wood_dark", bevel=0)
            blk(p, 0, 0, 0.012, W, D, H - 0.012, mat="brass", bevel_seg=1)
        elif slot == "panel":
            disk(p, (0, D * 0.25, H + 0.008), 0.014, W * 0.75, "x", "brass", segs=8)
            p.box((W * 0.6, 0.004, J(p, 0.01, 0.2)), T((0, D * 0.25 - 0.014, H + 0.008)), mat="glow", bevel=0)
        elif slot == "controls":
            for i in range(4):
                for k in range(2):
                    p.cyl(0.008, 0.008, J(p, 0.006, 0.3), T((-W * 0.3 + i * W * 0.2, -D * 0.3 + k * 0.025, H)), mat="bone", segs=6)
        elif slot == "core":
            gear(p, J(p, 0.026, 0.15), M(loc=(-W / 2 - 0.004, 0, H * 0.5), rot=(0, 0, 90)), teeth=6, th=0.006, mat="copper")
        else:
            x = W / 2
            rod(p, (x, 0, H * 0.5), (x + 0.03, 0, H * 0.5 + J(p, 0.04, 0.2)), 0.004, mat="brass", segs=4)
            p.ball(0.008, T((x + 0.03, 0, H * 0.5 + J(p, 0.04, 0.2))), mat="wood_dark", segs=(6, 4))
    elif e == "Future":  # projection calculator: thin slate, projected glow keypad, edge keys, emitter, stylus
        W, D = F(p, 0.08), F(p, 0.13)
        t = 0.008
        tilt = M(loc=(0, 0, 0.05), rot=(-35, 0, 0))
        if slot == "shell":
            p.box((W, D, t), T((0, 0, t / 2)), mat="body", bevel_seg=1)
        elif slot == "panel":
            for i in range(3):
                for k in range(4):
                    p.box((0.016, 0.002, 0.012), tilt @ T((-0.02 + i * 0.02, -D * 0.3, -0.02 + k * 0.016)), mat="glow", bevel=0)
            p.box((0.056, 0.002, J(p, 0.012, 0.2)), tilt @ T((0, -D * 0.3, 0.05)), mat="glow", bevel=0)
        elif slot == "controls":
            for i in range(p.rng.randint(2, 3)):
                p.box((0.003, 0.012, 0.004), T((W / 2 + 0.0015, D * 0.1 - i * 0.016, t / 2)), mat="shell_dark", bevel=0)
        elif slot == "core":
            p.box((W * 0.5, J(p, 0.006, 0.2), 0.003), T((0, -D * 0.42, t + 0.0015)), mat="glow", bevel=0)
        else:
            rod(p, (-W / 2 - 0.004, D * 0.4, t * 0.5), (-W / 2 - 0.004, D * 0.4 - J(p, 0.1, 0.15), t * 0.5), 0.0035, 0.002, mat="shell_dark", segs=5)
    elif e == "Wasteland":  # scrap adding box: dented case, nut-and-cap keys, dim glow readout, taped solar cell, wire
        W, D, H = F(p, 0.12), F(p, 0.16), F(p, 0.035)
        if slot == "shell":
            p.box((W, D, H), M(loc=(0, 0, H / 2), rot=(J(p, 2, 1), 0, 0)), mat="body")
        elif slot == "panel":
            p.box((W * 0.7, D * 0.18, 0.004), T((0, D * 0.3, H + 0.002)), mat="glow", bevel=0)
            p.box((W * 0.78, 0.01, 0.006), M(loc=(0, D * 0.2, H + 0.003), rot=(0, 0, J(p, 4, 1))), mat="cloth", bevel=0)
        elif slot == "controls":
            for i in range(3):
                for k in range(4):
                    if p.rng.random() < 0.9:
                        p.cyl(0.008, 0.008, 0.006, T((-W * 0.3 + i * W * 0.3, -D * 0.35 + k * 0.025, H)), mat=p.rng.choice(("iron", "paint", "rubber")),
                              segs=6)
        elif slot == "core":
            p.box((W * 0.5, J(p, 0.04, 0.2), 0.003), M(loc=(0, -D / 2 - 0.02, H * 0.6), rot=(20, 0, 0)), mat="glass", bevel=0)
            p.box((0.01, 0.01, H * 0.6), T((0, -D / 2 + 0.002, H * 0.5)), mat="iron", bevel=0)
        else:
            wires(p, [(W / 2, D * 0.2, H * 0.5), (W / 2 + 0.03, D * 0.3, 0.01), (W / 2 + J(p, 0.04, 0.3), D / 2 + 0.04, 0.005)], r=0.002, mat="paint")
            p.band(0.02, 0, m=M(loc=(0, D * 0.05, H * 0.5), rot=(0, 90, 0), scale=(0.7, 1.6, 1)), h=0.02)
    else:  # Ancient: stone reckoning tablet: slab, rune readout, relief key studs, glow seam, finger ring
        W, D, H = F(p, 0.12), F(p, 0.16), F(p, 0.03)
        if slot == "shell":
            p.box((W, D, H), T((0, 0, H / 2)), mat="body", bevel_seg=1)
        elif slot == "panel":
            p.box((W * 0.7, D * 0.2, 0.004), T((0, D * 0.28, H)), mat="stone_dark", bevel=0)
            for i in range(p.rng.randint(2, 4)):
                p.box((0.006, D * 0.12, 0.003), T((-W * 0.25 + i * 0.02, D * 0.28, H + 0.003)), mat="glow", bevel=0)
        elif slot == "controls":
            for i in range(3):
                for k in range(3):
                    p.cyl(0.011, J(p, 0.008, 0.2), 0.006, T((-W * 0.3 + i * W * 0.3, -D * 0.32 + k * 0.03, H)), mat="gold", segs=6)
        elif slot == "core":
            p.box((W * 0.85, 0.004, 0.004), T((0, D * J(p, 0.1, 0.4), H + 0.001)), mat="glow", bevel=0)
        else:
            p.ring(J(p, 0.016, 0.15), 0.005, M(loc=(0, D / 2 + 0.012, H * 0.5)), mat="stone_dark", segs=8)


# ================================================================ Navigator (carried)
@function("Navigator", "Device", DEVICE, "carried")
def navigator(p, slot):
    e = p.era
    if e == "Primal":  # star-position cord chart: lashed stick frame, curved swell sticks, shell markers, knots
        W, D = F(p, 0.3), F(p, 0.24)
        z = 0.008
        if slot == "shell":
            for y in (-D / 2, D / 2):
                rod(p, (-W / 2, y, z), (W / 2, y + J(p, 0.01, 1), z), 0.006, mat="wood", segs=4)
            for x in (-W / 2, W / 2):
                rod(p, (x, -D / 2, z + 0.008), (x, D / 2, z + 0.008), 0.006, mat="wood", segs=4)
        elif slot == "panel":
            for k in range(3):
                b = J(p, 0.05, 0.4)
                pts = [(-W / 2, -D * 0.3 + k * D * 0.3, z + 0.012), (0, -D * 0.3 + k * D * 0.3 + b, z + 0.012), (W / 2, -D * 0.3 + k * D * 0.3, z + 0.012)]
                p.tube(pts, 0.003, mat="bark", segs=3)
        elif slot == "controls":
            for i in range(p.rng.randint(3, 6)):
                p.ball(0.012, M(loc=(p.rng.uniform(-W * 0.4, W * 0.4), p.rng.uniform(-D * 0.4, D * 0.4), z + 0.02), scale=(1, 0.8, 0.6)), mat="bone", segs=(5, 3))
        elif slot == "core":
            for sx in (-1, 1):
                rod(p, (sx * W / 2, -D / 2, z + 0.014), (-sx * W / 2, D / 2, z + 0.014), 0.0025, mat="rope", segs=3)
            p.ball(J(p, 0.014, 0.2), T((0, 0, z + 0.016)), mat="rope", segs=(5, 3))
        else:
            for x in (-W / 2, W / 2):
                for y in (-D / 2, D / 2):
                    p.ball(0.011, T((x, y, z + 0.006)), mat="rope", segs=(5, 3))
            p.tube([(-W / 2, D / 2, z), (-W / 2 - 0.03, D / 2 + J(p, 0.04, 0.3), 0.004), (-W / 2 - 0.06, D / 2 + 0.02, 0.003)], 0.002, mat="rope", segs=3)
    elif e == "Agrarian":  # south-pointing fish: glazed bowl, water, rim marks, floating iron fish, bowl ring
        R, H = F(p, 0.1), F(p, 0.05)
        z0 = 0.012
        if slot == "shell":
            shell(p, [(R * 0.55, z0), (R * 0.9, z0 + H * 0.4), (R, z0 + H)], 0.008, mat="ceramic", segs=12)
        elif slot == "panel":
            p.cyl(R * 0.9, R * 0.9, 0.003, T((0, 0, z0 + H * J(p, 0.72, 0.08))), mat="glass", segs=12, bevel=0)
        elif slot == "controls":
            n = p.rng.choice((4, 8))
            for i in range(n):
                a = i * math.tau / n
                p.box((0.01, 0.004, 0.006), M(loc=(math.cos(a) * R * 0.98, math.sin(a) * R * 0.98, z0 + H + 0.001), rot=(0, 0, math.degrees(a))), mat="glaze", bevel=0)
        elif slot == "core":
            a = p.rng.uniform(-1, 1) * 25 - 90
            p.plate([(-0.045, 0), (-0.02, -0.012), (0.03, -0.007), (0.045, 0), (0.03, 0.007), (-0.02, 0.012)], 0.004,
                    M(loc=(0, 0, z0 + H * 0.72 + 0.004), rot=(0, 0, a)) @ M(rot=(90, 0, 0)), mat="iron", bevel=0)
            p.plate([(0, 0), (-0.015, 0.012), (-0.015, -0.012)], 0.003,
                    M(loc=(0, 0, z0 + H * 0.72 + 0.004), rot=(0, 0, a)) @ T((-0.045, 0, 0)) @ M(rot=(90, 0, 0)), mat="iron", bevel=0)
        else:
            p.cyl(R * 0.6, R * J(p, 0.55, 0.1), z0, mat="wood", segs=10)
    elif e == "Mercantile":  # astrolabe: brass mater with raised limb, engraved plate, rete, alidade, throne ring
        R = F(p, 0.08)
        c = (0, 0, R + 0.003)
        if slot == "shell":
            disk(p, c, R, 0.008, "y", "brass", segs=14)
            p.ring(R * 0.97, 0.004, M(loc=c, rot=(90, 0, 0)) @ T((0, 0, 0.005)), mat="brass", segs=12)
        elif slot == "panel":
            disk(p, (0, -0.004, c[2]), R * 0.88, 0.002, "y", "bone", segs=14)
            for i in range(6):
                a = i * math.tau / 6
                p.box((0.002, 0.002, R * J(p, 0.08, 0.3)), M(loc=(math.cos(a) * R * 0.92, -0.007, c[2] + math.sin(a) * R * 0.92), rot=(0, -math.degrees(a) + 90, 0)),
                      mat="iron", bevel=0)
        elif slot == "controls":
            a = J(p, 30, 1.0)
            p.box((R * 1.9, 0.003, 0.008), M(loc=(0, -0.012, c[2]), rot=(0, a, 0)), mat="brass", bevel=0)
            p.cyl(0.005, 0.005, 0.016, M(loc=(0, -0.004, c[2]), rot=(90, 0, 0)), mat="brass", segs=6)
        elif slot == "core":
            p.ring(R * 0.5, 0.003, M(loc=(0, -0.008, c[2] + R * 0.18), rot=(90, 0, 0)), mat="brass", segs=8)
            for i in range(p.rng.randint(4, 6)):
                a = p.rng.uniform(0, math.tau)
                p.plate([(0, 0), (0.006, 0.02), (-0.006, 0.02)], 0.002,
                        M(loc=(0, -0.009, c[2]), rot=(0, -math.degrees(a), 0)) @ T((0, 0, R * 0.55)), mat="brass", bevel=0)
        else:
            p.plate([(-0.016, 0), (-0.012, 0.016), (0, 0.022), (0.012, 0.016), (0.016, 0)], 0.008, T((0, 0, 2 * R)), mat="brass", bevel=0)
            p.ring(J(p, 0.012, 0.15), 0.003, M(loc=(0, 0, 2 * R + 0.034), rot=(90, 0, 0)), mat="brass", segs=8)
    elif e == "Industrial":  # pocket compass: steel case, dial card, needle, lid standing open with sight wire, bail
        R = F(p, 0.045)
        h = 0.018
        if slot == "shell":
            p.cyl(R, R * J(p, 0.97, 0.025), h, mat="steel", segs=12)
        elif slot == "panel":
            p.cyl(R * 0.88, R * 0.88, 0.002, T((0, 0, h - 0.004)), mat="bone", segs=12, bevel=0)
            for i in range(4):
                a = i * math.pi / 2
                p.box((0.004, 0.002, 0.003), M(loc=(math.cos(a) * R * 0.75, math.sin(a) * R * 0.75, h - 0.001), rot=(0, 0, math.degrees(a))), mat="rubber", bevel=0)
            p.cyl(R * 0.9, R * 0.9, 0.002, T((0, 0, h)), mat="glass", segs=12, bevel=0)
        elif slot == "controls":
            a = p.rng.uniform(-1, 1) * 40
            p.plate([(-R * 0.7, 0), (0, 0.006), (R * 0.7, 0), (0, -0.006)], 0.002, M(loc=(0, 0, h - 0.001), rot=(0, 0, a)) @ M(rot=(90, 0, 0)), mat="paint", bevel=0)
        elif slot == "core":
            a = J(p, 95, 0.12)
            lid = M(loc=(0, R, h), rot=(-a, 0, 0)) @ T((0, -R, 0))
            p.cyl(R, R, 0.006, lid, mat="steel", segs=12)
            p.box((0.002, R * 1.6, 0.002), lid @ T((0, 0, 0.007)), mat="iron", bevel=0)
        else:
            p.ring(J(p, 0.012, 0.15), 0.0025, M(loc=(0, -R - 0.01, h * 0.5), rot=(0, 0, 0)), mat="steel", segs=8)
            p.box((0.008, 0.008, 0.006), T((0, -R, h * 0.5)), mat="steel", bevel=0)
    elif e == "Steampunk":  # sextant: brass sector frame, graduated arc, swinging index arm, mirrors and glow, scope
        R = F(p, 0.18)
        apex = (0, 0, R + 0.01)
        th = 0.008
        if slot == "shell":
            for a in (-30, 30):
                rr = math.radians(a)
                rod(p, apex, (math.sin(rr) * R, 0, R + 0.01 - math.cos(rr) * R), 0.007, mat="brass", segs=5)
            pts = [(math.sin(math.radians(a)) * R, 0, R + 0.01 - math.cos(math.radians(a)) * R) for a in range(-32, 33, 8)]
            p.tube(pts, 0.008, mat="brass", segs=5)
            rod(p, (0, 0, R * 0.5), (0, 0.035, R * 0.45), 0.004, mat="brass", segs=4)
            p.cyl(0.012, 0.012, R * 0.3, M(loc=(0, 0.035, R * 0.3)), mat="wood_dark", segs=6)
        elif slot == "panel":
            pts = [(math.sin(math.radians(a)) * R * 0.96, -th, R + 0.01 - math.cos(math.radians(a)) * R * 0.96) for a in range(-30, 31, 10)]
            p.tube(pts, J(p, 0.005, 0.2), mat="bone", segs=4)
        elif slot == "controls":
            a = math.radians(p.rng.uniform(-1, 1) * 20)
            end = (math.sin(a) * R * 1.02, -th * 2, R + 0.01 - math.cos(a) * R * 1.02)
            rod(p, (0, -th * 2, apex[2]), end, 0.005, mat="brass", segs=4)
            p.box((0.03, 0.004, 0.012), M(loc=end, rot=(0, -math.degrees(a), 0)), mat="brass", bevel=0)
        elif slot == "core":
            p.box((0.03, 0.004, 0.04), M(loc=(0, -th * 3, apex[2] + 0.012), rot=(0, 0, 30)), mat="glass", bevel=0)
            p.box((0.024, 0.004, 0.03), M(loc=(-R * 0.25, -th, R * 0.55), rot=(0, 0, -15)), mat="glass", bevel=0)
            p.ball(J(p, 0.008, 0.2), T((R * 0.25, -th * 2, R * 0.2)), mat="glow", segs=(6, 4))
        else:
            z = R * 0.62
            p.cyl(0.012, 0.014, R * J(p, 0.7, 0.12), M(loc=(-R * 0.3, -th * 2.5, z), rot=(0, 90, 0)), mat="brass", segs=8)
            p.ring(0.013, 0.003, M(loc=(-R * 0.25, -th * 2.5, z), rot=(0, 90, 0)), mat="copper", segs=8)
    elif e == "Future":  # nav crystal slate: thin slab, glow chart lines, edge keys, floating arrow, back grip
        W, H = F(p, 0.1), F(p, 0.15)
        t = 0.012
        if slot == "shell":
            p.box((W, t, H), T((0, 0, H / 2)), mat="body", bevel_seg=1)
        elif slot == "panel":
            p.screen(W * 0.85, H * J(p, 0.78, 0.08), T((0, -t / 2 - 0.002, H * 0.5)))
        elif slot == "controls":
            for i in range(p.rng.randint(2, 3)):
                p.box((0.004, 0.006, 0.014), T((W / 2 + 0.002, 0, H * 0.6 - i * 0.02)), mat="shell_dark", bevel=0)
        elif slot == "core":
            z = H + J(p, 0.03, 0.3)
            p.plate([(-0.02, 0), (0, 0.03), (0.02, 0), (0.007, 0.006), (-0.007, 0.006)], 0.003, M(loc=(0, -0.01, z), rot=(0, p.rng.uniform(-1, 1) * 30, 0)), mat="glow", bevel=0)
        else:
            p.box((W * 0.5, J(p, 0.012, 0.2), H * 0.25), T((0, t / 2 + 0.006, H * 0.4)), mat="grip", bevel_seg=1)
    elif e == "Wasteland":  # scrap compass in a can lid: tin case, map scrap, dim glow needle, wire bail, bolt
        R = F(p, 0.06)
        h = 0.02
        if slot == "shell":
            p.cyl(R, R * J(p, 0.97, 0.03), h, M(rot=(J(p, 2, 1), 0, 0)), mat="body", segs=10)
        elif slot == "panel":
            p.cyl(R * 0.85, R * 0.85, 0.002, T((0, 0, h - 0.003)), mat="bone", segs=10, bevel=0)
            p.box((R * 0.6, R * 0.4, 0.002), M(loc=(R * 0.1, R * 0.15, h), rot=(0, 0, J(p, 20, 0.6))), mat="cloth", bevel=0)
        elif slot == "controls":
            a = p.rng.uniform(-1, 1) * 50
            p.box((R * 1.4, 0.004, 0.003), M(loc=(0, 0, h + 0.001), rot=(0, 0, a)), mat="glow", bevel=0)
        elif slot == "core":
            p.cyl(0.005, 0.005, 0.01, T((0, 0, h)), mat="iron", segs=6)
            p.box((0.012, 0.012, 0.004), T((J(p, R * 0.6, 0.2), -R * 0.5, h)), mat="iron", bevel=0)
        else:
            bail(p, R, h * 0.5, J(p, 0.05, 0.2), 0.002, mat="iron", n=5)
            p.band(R, h * 0.5, h=0.012)
    else:  # Ancient: stone compass disc: thick disc, rune ring, gold cardinal studs, floating crystal pointer, foot
        R = F(p, 0.07)
        h = 0.03
        z0 = 0.012
        if slot == "shell":
            p.cyl(R, R * J(p, 0.9, 0.05), h, T((0, 0, z0)), mat="body", segs=10)
        elif slot == "panel":
            for i in range(8):
                a = i * math.tau / 8
                p.box((0.012, J(p, 0.005, 0.3), 0.004), M(loc=(math.cos(a) * R * 0.72, math.sin(a) * R * 0.72, z0 + h), rot=(0, 0, math.degrees(a) + 90)), mat="glow", bevel=0)
        elif slot == "controls":
            for i in range(4):
                a = i * math.pi / 2 + math.pi / 4
                p.cyl(0.008, J(p, 0.006, 0.2), 0.008, T((math.cos(a) * R * 0.86, math.sin(a) * R * 0.86, z0 + h * 0.9)), mat="gold", segs=6)
        elif slot == "core":
            a = p.rng.uniform(-1, 1) * 40
            p.ball(0.015, M(loc=(0, 0, z0 + h + 0.03), rot=(0, 90, a), scale=(2.4, 1, 1)), mat="glow", segs=(4, 2))
        else:
            p.cyl(R * 0.7, R * J(p, 0.75, 0.08), z0, mat="stone_dark", segs=8)


# ================================================================ Spyglass (carried; stands on its objective end)
@function("Spyglass", "Device", DEVICE, "carried")
def spyglass(p, slot):
    e = p.era
    if e == "Primal":  # bone peep tube: hollow long bone, carved eye rim, rope grip wraps, aperture, carry thong
        L, r = F(p, 0.16), F(p, 0.016)
        if slot == "shell":
            p.lathe([(r * 1.35, 0), (r * 1.0, L * 0.15), (r * 0.85, L * 0.5), (r * 1.0, L * 0.85), (r * 1.4, L)], mat="bone", segs=7, noise=0.03)
        elif slot == "panel":
            p.ring(r * 1.35, J(p, 0.004, 0.2), T((0, 0, L)), mat="stone_dark", segs=7, square=False)
        elif slot == "controls":
            for z in (L * 0.32, L * J(p, 0.62, 0.08)):
                p.ring(r * 0.92, 0.003, T((0, 0, z)), mat="rope", segs=7)
        elif slot == "core":
            p.cyl(r * 1.2, r * 1.2, 0.003, T((0, 0, J(p, 0.002, 0.5))), mat="stone_dark", segs=7)
        else:
            p.tube([(r, 0, L * 0.4), (r * 2.5, -0.01, L * J(p, 0.2, 0.3)), (r * 2, 0, 0.005)], 0.0022, mat="hide", segs=3)
    elif e == "Agrarian":  # bamboo tube scope: outer cane, inner draw cane, node rings, crystal lens, cap on cord
        L, r = F(p, 0.24), F(p, 0.02)
        Lo = L * 0.62
        if slot == "shell":
            p.cyl(r, r * 0.96, Lo, mat="wood", segs=8)
        elif slot == "panel":
            p.cyl(r * 0.8, r * 0.78, L - Lo + 0.01, T((0, 0, Lo - 0.01)), mat="wood", segs=8)
        elif slot == "controls":
            for z in (Lo * J(p, 0.45, 0.15), Lo, L):
                p.ring(r * (1.01 if z <= Lo else 0.8), 0.003, T((0, 0, z - 0.004)), mat="bark", segs=8)
        elif slot == "core":
            p.cyl(r * 0.9, r * 0.9, 0.004, T((0, 0, -0.002 + J(p, 0.002, 0.5))), mat="glass", segs=8)
        else:
            p.cyl(r * 1.08, r * 1.08, J(p, 0.02, 0.2), T((-r * 2.4, 0, 0)), mat="wood_dark", segs=8)
            p.tube([(-r * 2.4, 0, 0.012), (-r * 1.4, 0, 0.03), (-r * 1.0, 0, 0.04)], 0.0018, mat="rope", segs=3)
    elif e == "Mercantile":  # draw-tube telescope: leather-wrapped barrel, brass draws, focus rings, lens, cap chain
        L, r = F(p, 0.26), F(p, 0.022)
        Lb = L * 0.5
        if slot == "shell":
            p.cyl(r * 1.1, r * J(p, 1.0, 0.06), Lb, mat="leather", segs=10)
        elif slot == "panel":
            p.cyl(r * 0.85, r * 0.85, L * 0.3, T((0, 0, Lb - 0.005)), mat="brass", segs=10)
            p.cyl(r * 0.68, r * 0.66, L * 0.22, T((0, 0, Lb + L * 0.3 - 0.01)), mat="brass", segs=10)
        elif slot == "controls":
            for z, rr in ((0.0, r * 1.18), (Lb - 0.006, r * 1.02), (Lb + L * 0.3 - 0.012, r * 0.88)):
                p.cyl(rr, rr, J(p, 0.012, 0.25), T((0, 0, z)), mat="brass", segs=10)
        elif slot == "core":
            p.cyl(r * 1.0, r * 1.0, 0.003, T((0, 0, J(p, 0.003, 0.5))), mat="glass", segs=10)
            p.cyl(r * 0.5, r * 0.45, 0.014, T((0, 0, L - 0.01)), mat="brass", segs=8)
        else:
            p.cyl(r * 1.22, r * 1.22, 0.012, T((-r * 3.2, 0, 0)), mat="brass", segs=10)
            p.tube([(-r * 2.1, 0, 0.008), (-r * 1.6, -0.005, J(p, 0.03, 0.3)), (-r * 1.15, 0, 0.02)], 0.0016, mat="brass", segs=3)
    elif e == "Industrial":  # binoculars: twin prism housings, eyecups, focus wheel on the bridge, lenses, strap
        L, r, s = F(p, 0.14), F(p, 0.022), F(p, 0.034)
        if slot == "shell":
            for sx in (-1, 1):
                p.cyl(r, r, L * 0.5, T((sx * s, 0, 0)), mat="paint", segs=8)
                blk(p, sx * s * 1.05, 0.004, L * 0.45, r * 2.1, r * 2.3, L * 0.4, mat="paint")
        elif slot == "panel":
            for sx in (-1, 1):
                p.cyl(r * 0.6, r * 0.7, J(p, 0.03, 0.2), T((sx * s * 0.95, 0, L * 0.85)), mat="rubber", segs=8)
        elif slot == "controls":
            disk(p, (0, 0, L * J(p, 0.72, 0.06)), 0.011, 0.018, "x", "rubber", segs=8)
            for z in (L * 0.55, L * 0.8):
                p.box((s * 1.4, 0.012, 0.01), T((0, 0, z)), mat="steel", bevel=0)
        elif slot == "core":
            for sx in (-1, 1):
                p.cyl(r * 1.06, r * 1.06, J(p, 0.012, 0.3), T((sx * s, 0, 0)), mat="rubber", segs=8)
                p.cyl(r * 0.9, r * 0.9, 0.002, T((sx * s, 0, -0.001)), mat="glass", segs=8)
        else:
            for sx in (-1, 1):
                p.box((0.006, 0.012, 0.012), T((sx * (s + r * 1.05 + 0.003), 0, L * 0.75)), mat="steel", bevel=0)
            p.tube([(-s - r * 1.1, 0, L * 0.75), (-s - r * 1.6, 0.0, L * J(p, 0.35, 0.3)), (-s * 0.5, 0.01, 0.01)], 0.003, mat="leather", segs=3)
    elif e == "Steampunk":  # multi-lens telescope: brass tube, swing-in auxiliary lenses on arms, gear focus, glow reticle
        L, r = F(p, 0.24), F(p, 0.024)
        if slot == "shell":
            p.lathe([(r * 1.25, 0), (r * 1.1, L * 0.1), (r, L * 0.6), (r * 0.7, L * 0.75), (r * 0.65, L)], mat="brass", segs=10)
        elif slot == "panel":
            p.cyl(r * 0.8, r * 0.95, 0.02, T((0, 0, L)), mat="leather", segs=8)
            p.ring(r * 1.01, 0.004, T((0, 0, L * J(p, 0.35, 0.2))), mat="copper", segs=10)
        elif slot == "controls":
            gear(p, J(p, 0.016, 0.15), M(loc=(r * 1.05, 0, L * 0.62), rot=(0, 0, 90)), teeth=6, th=0.006, mat="copper")
        elif slot == "core":
            p.cyl(r * 1.1, r * 1.1, 0.003, T((0, 0, J(p, 0.003, 0.5))), mat="glass", segs=10)
            p.cyl(r * 0.5, r * 0.5, 0.003, T((0, 0, L + 0.018)), mat="glow", segs=8)
        else:
            for i, sx in enumerate((-1, 1)):
                z = L * (0.25 + i * 0.25)
                a = J(p, 25, 0.5)
                end = (sx * (r + 0.03), -0.012, z + math.sin(math.radians(a)) * 0.02)
                rod(p, (sx * r, 0, z), end, 0.002, mat="brass", segs=3)
                disk(p, end, 0.012, 0.004, "y", "glass", segs=8)
    elif e == "Future":  # zoom eyepiece monocular: oval shell, telescoping zoom barrel, glow objective, rail, eyecup
        L, r = F(p, 0.12), F(p, 0.022)
        if slot == "shell":
            p.cyl(r * 1.25, r * J(p, 1.1, 0.08), L * 0.55, M(scale=(1, J(p, 0.85, 0.08), 1)), mat="body", segs=10)
        elif slot == "panel":
            p.cyl(r * 0.85, r * 0.85, L * J(p, 0.3, 0.2) + 0.002, T((0, 0, L * 0.55 - 0.002)), mat="shell_dark", segs=10)
            p.cyl(r * 0.95, r * 0.8, 0.018, T((0, 0, L * 0.85)), mat="grip", segs=10)
        elif slot == "controls":
            p.box((0.006, 0.01, L * J(p, 0.3, 0.2)), T((r * 1.2, 0, L * 0.28)), mat="shell_dark", bevel=0)
        elif slot == "core":
            p.cyl(r * 0.85, r * 0.85, 0.003, T((0, 0, -0.001 + J(p, 0.001, 0.5))), mat="glow", segs=10)
        else:
            p.ring(r * 1.17, J(p, 0.003, 0.2), M(loc=(0, 0, L * 0.4), scale=(1, 0.85, 1)), mat="glow", segs=10)
    elif e == "Wasteland":  # pipe scope: mismatched pipe sections, taped joint, bottle-glass lens, wire, dim glow
        L, r = F(p, 0.2), F(p, 0.02)
        if slot == "shell":
            p.cyl(r * 1.2, r * 1.2, L * 0.55, M(rot=(J(p, 2, 1), 0, 0)), mat="body", segs=7)
        elif slot == "panel":
            p.cyl(r * 0.85, r * 0.85, L * 0.48, T((0, 0, L * 0.52)), mat="steel", segs=7)
            p.cyl(r * 1.0, r * 1.0, 0.012, T((0, 0, L - 0.012)), mat="rubber", segs=7)
        elif slot == "controls":
            p.cyl(r * 1.3, r * 1.3, L * J(p, 0.12, 0.3), T((0, 0, L * 0.47)), mat="cloth", segs=7, noise=0.04)
        elif slot == "core":
            p.cyl(r * 1.05, r * 1.05, 0.003, T((0, 0, J(p, 0.002, 0.5))), mat="glass", segs=7)
            p.ball(0.006, T((r * 1.2, 0, L * 0.3)), mat="glow", segs=(5, 3))
        else:
            pts = [(r * 1.22 * math.cos(i * 1.5), r * 1.22 * math.sin(i * 1.5), L * (0.15 + i * 0.008 * J(p, 1, 0.3))) for i in range(8)]
            p.tube(pts, 0.0018, mat="iron", segs=3)
    else:  # Ancient: octagonal stone tube, crystal objective glow, rune bands, gold eye ring, stone foot ring
        L, r = F(p, 0.2), F(p, 0.024)
        if slot == "shell":
            p.lathe([(r * 1.3, 0), (r * 1.15, L * 0.2), (r, L * 0.8), (r * 1.1, L)], mat="body", segs=8)
        elif slot == "panel":
            for z in (L * 0.35, L * J(p, 0.62, 0.08)):
                for i in range(4):
                    a = i * math.pi / 2 + math.pi / 8
                    p.box((0.01, 0.004, 0.008), M(loc=(math.cos(a) * r * 1.1, math.sin(a) * r * 1.1, z), rot=(0, 0, math.degrees(a) + 90)), mat="glow", bevel=0)
        elif slot == "controls":
            p.cyl(r * 1.15, r * J(p, 1.0, 0.1), 0.01, T((0, 0, L - 0.002)), mat="gold", segs=8)
        elif slot == "core":
            p.ball(r * 1.1, M(loc=(0, 0, 0.004), scale=(1, 1, J(p, 0.3, 0.2))), mat="glow", segs=(8, 3))
        else:
            p.cyl(r * 1.5, r * 1.4, J(p, 0.012, 0.2), T((0, 0, L * 0.12)), mat="stone_dark", segs=8)


# ================================================================ Radio (scene: floor-standing)
@function("Radio", "Device", DEVICE, "scene")
def radio(p, slot):
    e = p.era
    if e == "Primal":  # speaking stone: standing hollow stone, voice hole, beater stones, base cairn, charm cord
        H, R = F(p, 0.95), F(p, 0.24)
        zh = H * 0.62
        if slot == "shell":
            p.lathe([(R, 0), (R * 1.05, H * 0.2), (R * 0.9, H * 0.6), (R * 0.65, H * 0.9), (R * 0.3, H), (0, H)], mat="stone", segs=7, noise=0.04)
        elif slot == "panel":
            p.ring(R * 0.32, J(p, 0.03, 0.2), M(loc=(0, -R * 0.82, zh), rot=(90, 0, 0)), mat="stone_dark", segs=8, square=False)
            knob(p, 0, -R * 0.8, zh, R * 0.3, 0.02, mat="stone_dark", segs=8)
        elif slot == "controls":
            x = R * 1.1
            p.ball(1.0, M(loc=(x, -R * 0.4, 0.06), scale=(0.07, 0.06, 0.06)), mat="stone", segs=(6, 4), noise=0.05)
            rod(p, (x, -R * 0.4, 0.1), (x + 0.04, -R * 0.4 - J(p, 0.05, 0.4), 0.42), 0.018, mat="wood", segs=5)
        elif slot == "core":
            for i in range(p.rng.randint(4, 7)):
                a = p.rng.uniform(0, math.tau)
                p.ball(1.0, M(loc=(math.cos(a) * R * 1.1, math.sin(a) * R * 1.1, 0.04), scale=(0.07, 0.06, 0.05)), mat="stone_dark", segs=(5, 3), noise=0.05)
        else:
            z = H * J(p, 0.82, 0.06)
            p.ring(R * 0.72, 0.012, T((0, 0, z)), mat="rope", segs=8, square=False)
            for i in range(3):
                x = (i - 1) * 0.08
                p.tube([(x, -R * 0.7, z), (x * 1.2, -R * 0.75, z - 0.12)], 0.004, mat="rope", segs=3)
                p.ball(0.02, M(loc=(x * 1.2, -R * 0.75, z - 0.14), scale=(0.6, 0.6, 1.3)), mat=("bone", "feather", "bone")[i], segs=(5, 3))
    elif e == "Agrarian":  # bronze bell tower: four posts, gable roof, pull rope, bronze bell, stone base
        H, W = F(p, 1.75), F(p, 0.62)
        zb = H - 0.12
        if slot == "shell":
            for sx in (-1, 1):
                for sy in (-1, 1):
                    rod(p, (sx * W / 2, sy * W / 2, 0.12), (sx * W * 0.38, sy * W * 0.38, H), 0.035, mat="wood", segs=6)
            for z in (0.55, zb):
                for sx in (-1, 1):
                    p.box((0.05, W * 0.95, 0.05), T((sx * W * (0.5 - 0.12 * (z - 0.12) / (H - 0.12)), 0, z)), mat="wood", bevel=0)
            p.box((W * 0.85, 0.06, 0.06), T((0, 0, zb)), mat="wood", bevel=0)
        elif slot == "panel":
            a = J(p, 28, 0.2)
            for sy in (-1, 1):
                p.box((W * 1.2, W * 0.55, 0.035), M(loc=(0, sy * W * 0.22, H + 0.1), rot=(-sy * a, 0, 0)), mat="bark")
            p.box((W * 1.25, 0.05, 0.05), T((0, 0, H + 0.1 + W * 0.25 * math.sin(math.radians(a)))), mat="wood", bevel=0)
        elif slot == "controls":
            p.tube([(0, -0.05, zb - 0.38), (J(p, 0.04, 1), -W * 0.3, zb - 0.6), (0.05, -W * 0.4, 0.95)], 0.008, mat="rope", segs=4)
            p.ball(0.025, T((0.05, -W * 0.4, 0.93)), mat="wood", segs=(5, 3))
        elif slot == "core":
            hb = J(p, 0.32, 0.12)
            bell_shape(p, hb * 0.6, hb, 0.02, mat="copper", segs=10, m=T((0, 0, zb - 0.04 - hb)))
            p.ball(0.03, T((0, 0, zb - 0.04 - hb - 0.02)), mat="iron", segs=(5, 3))
        else:
            p.box((W * 1.25, W * 1.25, 0.12), T((0, 0, 0.06)), mat="stone", noise=0.02)
            for i in range(p.rng.randint(2, 4)):
                p.box((W * 0.3, 0.035, 0.012), T((0, -W * 0.5 - 0.03, 0.15 + i * J(p, 0.25, 0.05))), mat="wood", bevel=0)
    elif e == "Mercantile":  # speaking-tube post: turned pedestal, brass mouth horn, whistle plug, pipe, plaque
        H = F(p, 1.3)
        zt = H
        if slot == "shell":
            p.lathe([(0.2, 0), (0.18, 0.05), (0.06, 0.12), (0.05, H * 0.5), (0.065, H * 0.55), (0.045, H - 0.04), (0.07, H - 0.02), (0.06, H)],
                    mat="body", segs=8)
        elif slot == "panel":
            L = J(p, 0.2, 0.15)
            p.lathe([(0.025, 0), (0.03, L * 0.5), (0.06, L * 0.85), (0.085, L)], M(loc=(0, 0, zt), rot=(90 - J(p, 20, 0.3), 0, 0)), mat="brass", segs=10)
        elif slot == "controls":
            p.cyl(0.02, 0.026, 0.05, T((0.12, -0.06, zt - 0.1)), mat="brass", segs=8)
            p.tube([(0.12, -0.06, zt - 0.1), (0.1, -0.08, zt - J(p, 0.18, 0.2)), (0.06, -0.06, zt - 0.08)], 0.0025, mat="brass", segs=3)
        elif slot == "core":
            p.cyl(0.026, 0.026, H - 0.12, T((0.0, 0.06, 0.12)), mat="brass", segs=8)
            for z in (0.4, H * J(p, 0.7, 0.1)):
                p.ring(0.03, 0.006, T((0.0, 0.06, z)), mat="brass", segs=8)
            rod(p, (0, 0.06, 0.12), (0, 0.06, 0.0), 0.026, mat="brass", segs=8)
        else:
            p.box((0.12, 0.008, J(p, 0.08, 0.2)), T((0, -0.055, H * 0.7)), mat="brass", bevel=0)
            p.box((0.1, 0.004, 0.012), T((0, -0.06, H * 0.7)), mat="iron", bevel=0)
    elif e == "Industrial":  # tube radio console: cabinet on legs, fretwork grille, dial and knobs, valves on top, aerial
        W, D, H = F(p, 0.62), F(p, 0.34), F(p, 1.02)
        zl = 0.2
        if slot == "shell":
            blk(p, 0, 0, zl, W, D, H - zl, mat="wood_dark")
            legs(p, W * 0.42, D * 0.38, 0, zl, 0.022, mat="wood_dark", splay=J(p, 0.02, 0.5))
            p.box((W * 1.03, D * 1.03, 0.03), T((0, 0, H)), mat="wood_dark", bevel=0)
        elif slot == "panel":
            z0, z1 = zl + 0.06, zl + (H - zl) * 0.58
            blk(p, 0, -D / 2 - 0.002, z0, W * 0.75, 0.004, z1 - z0, mat="cloth", bevel=0)
            slats(p, -W * 0.37, W * 0.37, -D / 2 - 0.008, z0, z1, p.rng.choice((5, 7, 9)), 0.014, "wood")
        elif slot == "controls":
            zc = zl + (H - zl) * 0.78
            p.box((W * 0.5, 0.008, 0.09), T((0, -D / 2 - 0.004, zc)), mat="bone", bevel=0)
            p.box((0.004, 0.012, 0.08), T((p.rng.uniform(-0.02, 0.02) + W * 0.1 * (p.rng.random() - 0.5), -D / 2 - 0.008, zc)), mat="paint", bevel=0)
            for x in (-W * 0.3, -W * 0.1, W * 0.1, W * 0.3):
                knob(p, x, -D / 2, zl + (H - zl) * 0.66, 0.022, 0.02, mat="bone", segs=8)
        elif slot == "core":
            for i in range(p.rng.randint(3, 5)):
                x = -W * 0.3 + i * 0.09
                h = J(p, 0.1, 0.2)
                p.cyl(0.022, 0.022, h, T((x, D * 0.15, H + 0.03)), mat="glass", segs=8)
                p.cyl(0.024, 0.024, 0.02, T((x, D * 0.15, H + 0.03)), mat="rubber", segs=8)
        else:
            for sx in (-1, 1):
                rod(p, (sx * 0.02, -D * 0.2, H + 0.03), (sx * J(p, 0.28, 0.2), -D * 0.25, H + 0.45), 0.004, mat="steel", segs=4)
            p.cyl(0.03, 0.035, 0.03, T((0, -D * 0.2, H + 0.03)), mat="rubber", segs=8)
    elif e == "Steampunk":  # brass transceiver: wood cabinet, brass horn speaker, glowing valve rack, gauges, coil aerial
        W, D, H = F(p, 0.72), F(p, 0.42), F(p, 1.15)
        if slot == "shell":
            blk(p, 0, 0, 0, W, D, H, mat="wood_dark")
            for z in (0.08, H - 0.08):
                p.band(W * 0.5, z, m=M(scale=(1, D / W, 1)), h=0.05)
        elif slot == "panel":
            for x in (-W * 0.25, W * 0.25):
                knob(p, x, -D / 2, H * 0.78, J(p, 0.07, 0.12), 0.02, mat="brass", segs=12)
                knob(p, x, -D / 2 - 0.02, H * 0.78, 0.055, 0.004, mat="bone", segs=12)
        elif slot == "controls":
            for i in range(3):
                knob(p, (i - 1) * W * 0.2, -D / 2, H * 0.62, 0.03, 0.025, mat="copper", segs=8)
            rod(p, (W * 0.4, -D / 2, H * 0.55), (W * 0.42, -D / 2 - 0.08, H * 0.55 + J(p, 0.08, 0.3)), 0.008, mat="brass", segs=5)
        elif slot == "core":
            # Valves stand proud of the face on a brass shelf: the game draws glass opaque, so a cabinet window would hide them.
            blk(p, 0, -D / 2 - 0.035, H * 0.16, W * 0.8, 0.07, 0.025, mat="brass", bevel=0)
            blk(p, 0, -D / 2 - 0.004, H * 0.16, W * 0.8, 0.008, H * 0.3, mat="iron", bevel=0)
            for i in range(p.rng.randint(4, 6)):
                x = -W * 0.32 + i * W * 0.13
                p.cyl(0.024, 0.02, J(p, 0.18, 0.2), T((x, -D / 2 - 0.035, H * 0.16 + 0.025)), mat="glow", segs=8)
        else:
            L = J(p, 0.34, 0.15)
            p.lathe([(0.04, 0), (0.05, L * 0.4), (0.1, L * 0.8), (0.17, L)], M(loc=(W * 0.3, 0, H), rot=(-60, 0, 0)), mat="brass", segs=10)
            pts = [(-W * 0.25 + 0.05 * math.cos(i * 1.2), 0.05 * math.sin(i * 1.2), H + 0.04 + i * 0.03) for i in range(14)]
            p.tube(pts, 0.006, mat="copper", segs=4)
            rod(p, (-W * 0.25, 0, H), (-W * 0.25, 0, H + 0.5), 0.008, mat="brass", segs=5)
    elif e == "Future":  # omnidirectional broadcast pillar: slim pillar, glow rings, touch panel, emitter, base fins
        H, r = F(p, 1.9), F(p, 0.11)
        if slot == "shell":
            p.lathe([(r * 1.4, 0), (r * 1.3, 0.08), (r, 0.2), (r * 0.8, H * 0.7), (r * 0.6, H - 0.05), (r * 0.5, H)], mat="body", segs=10)
        elif slot == "panel":
            for i in range(3):
                z = H * (0.4 + i * 0.16)
                rr = r * (0.8 + (1 - 0.8) * (1 - (z - 0.2) / (H * 0.5))) + 0.02
                p.ring(rr * J(p, 1.0, 0.1) + 0.03, 0.006, T((0, 0, z)), mat="glow", segs=12)
        elif slot == "controls":
            p.box((0.1, 0.01, J(p, 0.16, 0.2)), M(loc=(0, -r * 0.95, 1.1), rot=(8, 0, 0)), mat="shell_dark", bevel=0)
            p.box((0.07, 0.004, 0.1), M(loc=(0, -r * 0.95 - 0.006, 1.1), rot=(8, 0, 0)), mat="glow", bevel=0)
        elif slot == "core":
            p.ball(J(p, 0.09, 0.15), M(loc=(0, 0, H + 0.12), scale=(1, 1, 1.3)), mat="glow", segs=(8, 6))
            p.cyl(r * 0.3, r * 0.6, 0.04, T((0, 0, H)), mat="shell_dark", segs=10)
        else:
            for i in range(3):
                a = i * 120 + 90
                p.plate([(0, 0), (J(p, 0.26, 0.15), 0), (0, 0.5)], 0.02, M(loc=(0, 0, 0), rot=(0, 0, a)) @ T((r * 0.9, 0, 0)), mat="shell_dark", bevel=0)
    elif e == "Wasteland":  # scrap radio mast: oil drum, salvaged set on it, pipe mast, guy wires, dim glow dial
        R, H = F(p, 0.28), F(p, 0.82)
        mw, md, mh = 0.5, 0.3, 0.3
        if slot == "shell":
            p.cyl(R, R, H, mat="body", segs=10)
            for z in (H * 0.33, H * 0.66):
                p.ring(R * 1.01, 0.012, T((0, 0, z)), mat="body", segs=10)
            patch(p, R * 0.2, -R * 0.98, H * 0.45, 0.14, 0.12, rot=J(p, 10, 0.6))
        elif slot == "panel":
            p.box((mw, md, mh), M(loc=(0, 0, H + mh / 2), rot=(0, 0, J(p, 5, 0.8))), mat="paint")
            slats(p, -mw * 0.42, -mw * 0.05, -md / 2 - 0.005, H + 0.05, H + mh - 0.05, 5, 0.012, "iron")
        elif slot == "controls":
            for x in (mw * 0.12, mw * 0.3):
                knob(p, x, -md / 2, H + mh * 0.3, J(p, 0.025, 0.2), 0.02, mat=p.rng.choice(("rubber", "iron", "paint")), segs=7)
        elif slot == "core":
            knob(p, mw * 0.22, -md / 2, H + mh * 0.68, 0.05, 0.006, mat="glow", segs=10)
            p.box((0.004, 0.008, 0.07), M(loc=(mw * 0.22, -md / 2 - 0.008, H + mh * 0.68), rot=(0, J(p, 30, 1), 0)), mat="rubber", bevel=0)
        else:
            top = H + mh + J(p, 1.0, 0.15)
            rod(p, (mw * 0.35, md * 0.3, H + mh), (mw * 0.35, md * 0.3, top), 0.015, mat="steel", segs=6)
            for i in range(3):
                a = i * math.tau / 3 + 0.5
                wires(p, [(mw * 0.35, md * 0.3, top - 0.1), (math.cos(a) * R * 1.6, math.sin(a) * R * 1.6, 0.01)], r=0.003, mat="iron")
            p.band(0.015, top - 0.25, m=T((mw * 0.35, md * 0.3, 0)), h=0.05)
    else:  # Ancient: rune obelisk transmitter: tapered stone, rune faces, gold rings, crystal crown, stepped base
        H, R = F(p, 1.7), F(p, 0.18)
        if slot == "shell":
            p.lathe([(R, 0.15), (R * 0.95, H * 0.3), (R * 0.7, H - 0.12), (R * 0.4, H)], M(rot=(0, 0, 45)), mat="body", segs=4)
        elif slot == "panel":
            runes(p, 0, -R * 0.62, 0.35, H * J(p, 0.6, 0.08), n=p.rng.randint(3, 5), w=0.05)
        elif slot == "controls":
            for z in (H * 0.35, H * J(p, 0.62, 0.08)):
                rr = R * (0.95 - 0.25 * (z - 0.15) / (H - 0.27)) * 0.72
                p.ring(rr * 1.42, 0.012, M(loc=(0, 0, z), rot=(0, 0, 45)), mat="gold", segs=4)
        elif slot == "core":
            p.ball(J(p, 0.1, 0.15), M(loc=(0, 0, H + 0.2), scale=(1, 1, 1.8)), mat="glow", segs=(4, 2))
            for i in range(3):
                a = i * math.tau / 3
                p.box((0.04, 0.02, 0.07), M(loc=(math.cos(a) * 0.2, math.sin(a) * 0.2, H + 0.2), rot=(0, 0, math.degrees(a))), mat="stone_dark", bevel=0)
        else:
            p.box((R * 3.2, R * 3.2, 0.08), T((0, 0, 0.04)), mat="stone_dark", bevel_seg=1)
            p.box((R * J(p, 2.4, 0.08), R * 2.4, 0.08), T((0, 0, 0.11)), mat="stone_dark", bevel_seg=1)


# ================================================================ Display (scene: floor-standing)
@function("Display", "Device", DEVICE, "scene")
def display(p, slot):
    e = p.era
    if e == "Primal":  # shadow-puppet screen: two poles and crossbars, hide screen, puppets on sticks, fire bowl, stakes
        W, H = F(p, 1.2), F(p, 1.45)
        z0 = 0.35
        if slot == "shell":
            for sx in (-1, 1):
                p.tube([(sx * W / 2, 0, 0), (sx * W / 2 + J(p, 0.02, 1), 0, H * 0.5), (sx * W / 2, 0, H + 0.08)], 0.028, mat="wood", segs=5)
            for z in (z0, H):
                p.tube([(-W / 2 - 0.05, 0, z), (0, 0, z + 0.01), (W / 2 + 0.05, 0, z)], 0.02, mat="wood", segs=5)
        elif slot == "panel":
            p.box((W * 0.92, 0.006, H - z0 - 0.04), T((0, 0.01, (H + z0) / 2)), mat="hide", bevel=0, noise=0.01)
        elif slot == "controls":
            for i in range(2):
                x = (i - 0.5) * W * J(p, 0.4, 0.2)
                z = z0 + 0.3 + i * 0.08
                p.plate([(-0.08, 0), (-0.06, 0.18), (0, 0.26), (0.05, 0.2), (0.09, 0.05), (0.03, -0.02)], 0.006, T((x, -0.03, z)), mat="leather", bevel=0)
                rod(p, (x, -0.04, z), (x + 0.03, -0.25, z - 0.35), 0.006, mat="bark", segs=4)
        elif slot == "core":
            shell(p, [(0.12, 0.0), (0.2, 0.06), (0.24, 0.14)], 0.02, mat="stone", segs=8, m=T((0, 0.45, 0)), noise=0.03)
            for i in range(p.rng.randint(3, 5)):
                a = i * 2.1
                p.box((0.16, 0.035, 0.035), M(loc=(math.cos(a) * 0.03, 0.45 + math.sin(a) * 0.03, 0.14), rot=(0, J(p, 20, 0.5), math.degrees(a))), mat="bark", bevel=0)
        else:
            for sx in (-1, 1):
                p.tube([(sx * W / 2, 0, H * 0.8), (sx * (W / 2 + 0.3), -J(p, 0.3, 0.2), 0.0)], 0.006, mat="rope", segs=3)
                p.cyl(0.025, 0.012, 0.12, T((sx * (W / 2 + 0.3), -J(p, 0.3, 0.2), -0.04)), mat="wood", segs=5)
    elif e == "Agrarian":  # revolving lantern on a stand: pole with crossed feet, paper drum, silhouettes, vane, tassels
        H, R = F(p, 1.5), F(p, 0.2)
        zl = H - 0.55
        if slot == "shell":
            p.cyl(0.025, 0.022, H, mat="wood", segs=6)
            for a in (0, 90):
                p.box((0.6, 0.06, 0.05), M(loc=(0, 0, 0.025), rot=(0, 0, a)), mat="wood", bevel=0)
            p.box((R * 2.4, 0.04, 0.04), T((0, 0, H)), mat="wood", bevel=0)
            for sx in (-1, 1):
                p.box((0.03, 0.03, 0.12), T((sx * R * 1.15, 0, H - 0.04)), mat="wood", bevel=0)
        elif slot == "panel":
            hh = 0.4
            p.lathe([(R * 0.9, zl), (R, zl + hh * 0.15), (R * J(p, 1.04, 0.05), zl + hh * 0.5), (R, zl + hh * 0.85), (R * 0.9, zl + hh)], mat="bone", segs=10)
            for z in (zl, zl + hh):
                p.ring(R * 0.9, 0.008, T((0, 0, z)), mat="bark", segs=10)
        elif slot == "controls":
            for i in range(p.rng.randint(2, 4)):
                a = i * math.tau / 4 + J(p, 0.3, 1)
                p.plate([(-0.05, 0), (-0.04, 0.12), (0, 0.18), (0.04, 0.1), (0.06, 0)], 0.004,
                        M(loc=(math.cos(a) * R * 1.03, math.sin(a) * R * 1.03, zl + 0.1), rot=(0, 0, math.degrees(a) + 90)), mat="wood_dark", bevel=0)
        elif slot == "core":
            n = p.rng.choice((6, 8))
            for i in range(n):
                a = i * 360 / n
                p.box((R * 0.8, 0.003, 0.04), M(loc=(0, 0, zl + 0.44), rot=(0, 0, a)) @ T((R * 0.4, 0, 0)) @ M(rot=(25, 0, 0)), mat="bark", bevel=0)
        else:
            for i in range(4):
                a = i * math.tau / 4 + math.pi / 4
                x, y = math.cos(a) * R * 0.92, math.sin(a) * R * 0.92
                rod(p, (x, y, zl), (x, y, zl - J(p, 0.12, 0.25)), 0.004, mat="rope", segs=3)
                p.cyl(0.012, 0.018, 0.06, T((x, y, zl - J(p, 0.12, 0.25) - 0.06)), mat="accent", segs=5)
    elif e == "Mercantile":  # magic lantern on its stand: tripod, japanned lantern box, slide carrier, lens tube, chimney
        H = F(p, 1.05)
        W, D, B = 0.24, 0.28, 0.26
        if slot == "shell":
            for i in range(3):
                a = i * math.tau / 3 + math.pi / 2
                rod(p, (math.cos(a) * 0.32, math.sin(a) * 0.32, 0), (math.cos(a) * 0.05, math.sin(a) * 0.05, H - 0.04), 0.018, mat="wood_dark", segs=5)
            p.box((0.32, 0.36, 0.04), T((0, 0, H - 0.02)), mat="wood_dark")
        elif slot == "panel":
            blk(p, 0, 0, H, W, D, B, mat="iron")
            for sx in (-1, 1):
                p.box((0.004, D * 0.7, B * 0.6), T((sx * W / 2, 0, H + B * 0.5)), mat="brass", bevel=0)
        elif slot == "controls":
            x = J(p, 0.04, 1.0)
            p.box((0.34, 0.012, 0.08), T((x, -D / 2 - 0.012, H + B * 0.5)), mat="wood", bevel=0)
            for i in range(3):
                p.box((0.06, 0.014, 0.06), T((x - 0.1 + i * 0.1, -D / 2 - 0.012, H + B * 0.5)), mat="glass", bevel=0)
        elif slot == "core":
            L = J(p, 0.18, 0.15)
            p.cyl(0.05, 0.045, L, M(loc=(0, -D / 2 - 0.02, H + B * 0.5), rot=(90, 0, 0)), mat="brass", segs=10)
            knob(p, 0, -D / 2 - 0.02 - L, H + B * 0.5, 0.04, 0.004, mat="glass", segs=10)
        else:
            ch = J(p, 0.16, 0.2)
            p.cyl(0.035, 0.03, ch, T((0, D * 0.15, H + B)), mat="iron", segs=8)
            p.lathe([(0.03, 0), (0.06, 0.02), (0.065, 0.035), (0, 0.05)], T((0, D * 0.15, H + B + ch)), mat="iron", segs=8)
    elif e == "Industrial":  # CRT television on its own stand: cabinet, bulging screen, knobs, splayed legs, rabbit ears
        W, D, Hs = F(p, 0.62), F(p, 0.48), F(p, 0.5)
        Ht = W * 0.78
        sx_, sw, sh = -W * 0.12, W * 0.62, Ht * 0.68
        if slot == "shell":
            blk(p, 0, 0, Hs, W, D, Ht, mat="wood_dark")
            p.box((W * 0.66, D * 0.4, Ht * 0.7), T((0, D * 0.6, Hs + Ht * 0.48)), mat="paint", bevel=0)
        elif slot == "panel":
            p.box((sw + 0.04, 0.012, sh + 0.04), T((sx_, -D / 2 - 0.004, Hs + Ht * 0.52)), mat="paint", bevel=0)
            p.ball(1.0, M(loc=(sx_, -D / 2 - 0.004, Hs + Ht * 0.52), scale=(sw * 0.5, J(p, 0.03, 0.2), sh * 0.5)), mat="glass", segs=(10, 6))
        elif slot == "controls":
            xk = W * 0.36
            for i in range(p.rng.randint(2, 3)):
                knob(p, xk, -D / 2, Hs + Ht * (0.78 - i * 0.2), 0.03 if i == 0 else 0.022, 0.025, mat="bone", segs=10)
            slats(p, xk - 0.05, xk + 0.05, -D / 2 - 0.003, Hs + 0.04, Hs + Ht * 0.22, 4, 0.008, "steel")
        elif slot == "core":
            blk(p, 0, 0, Hs - 0.03, W * 0.9, D * 0.85, 0.03, mat="wood")
            legs(p, W * 0.38, D * 0.32, 0, Hs - 0.03, 0.018, mat="wood", splay=J(p, 0.05, 0.4))
            if coin(p):
                blk(p, 0, 0, Hs * 0.35, W * 0.8, D * 0.7, 0.02, mat="wood", bevel=0)
        else:
            z = Hs + Ht
            p.ball(0.05, M(loc=(0, D * 0.1, z), scale=(1, 1, 0.5)), mat="rubber", segs=(8, 4))
            a = J(p, 30, 0.3)
            for sx in (-1, 1):
                end = (sx * math.sin(math.radians(a)) * 0.45, D * 0.1, z + math.cos(math.radians(a)) * 0.45)
                rod(p, (0, D * 0.1, z + 0.01), end, 0.004, mat="steel", segs=4)
                p.ball(0.008, T(end), mat="steel", segs=(4, 3))
    elif e == "Steampunk":  # split-flap board on brass legs: framed board, rows of flaps, gear housing with glow, crank
        W, H = F(p, 0.95), F(p, 1.55)
        Hb = 0.7
        zb = H - Hb
        rows, cols = 4, 7
        if slot == "shell":
            blk(p, 0, 0, zb, W, 0.12, Hb, mat="wood_dark")
            for sx in (-1, 1):
                p.lathe([(0.06, 0), (0.05, 0.04), (0.025, 0.1), (0.022, zb)], T((sx * W * 0.4, 0, 0)), mat="brass", segs=8)
            p.band(W * 0.5, zb + Hb * J(p, 0.5, 0.0), m=M(scale=(1, 0.12 / W, 1)), h=0.03)
        elif slot == "panel":
            blk(p, 0, -0.064, zb + 0.06, W * 0.88, 0.01, Hb * 0.78, mat="rubber", bevel=0)
            for c in range(cols + 1):
                p.box((J(p, 0.012, 0.3), 0.016, Hb * 0.78), T((-W * 0.44 + c * W * 0.88 / cols, -0.07, zb + 0.06 + Hb * 0.39)), mat="brass", bevel=0)
        elif slot == "controls":
            fw, fh = W * 0.88 / cols * 0.8, Hb * 0.78 / rows * 0.7
            for rr in range(rows):
                for c in range(cols):
                    z = zb + 0.06 + Hb * 0.78 * (rr + 0.5) / rows
                    x = -W * 0.44 + W * 0.88 * (c + 0.5) / cols
                    a = p.rng.choice((0, 0, 0, 25, -30))
                    p.box((fw, 0.006, fh), M(loc=(x, -0.075, z), rot=(a, 0, 0)), mat=p.rng.choice(("bone", "bone", "paint")), bevel=0)
        elif slot == "core":
            p.box((W * 0.5, 0.1, 0.12), T((0, 0, H + 0.06)), mat="brass")
            for x in (-W * 0.15, W * 0.15):
                knob(p, x, -0.05, H + 0.06, J(p, 0.03, 0.15), 0.006, mat="glow", segs=8)
        else:
            gear(p, J(p, 0.1, 0.15), M(loc=(W / 2 + 0.01, 0, zb + Hb * 0.6), rot=(0, 0, 90)), teeth=10, th=0.015)
            rod(p, (W / 2 + 0.02, 0, zb + Hb * 0.6), (W / 2 + 0.06, 0, zb + Hb * 0.6), 0.01, mat="iron", segs=5)
            rod(p, (W / 2 + 0.06, 0, zb + Hb * 0.6), (W / 2 + 0.06, -0.08, zb + Hb * 0.6 - 0.06), 0.012, mat="wood_dark", segs=5)
    elif e == "Future":  # holo screen: low plinth, twin emitter posts, floating glow panel, base touch strip, halo
        W, H = F(p, 1.1), F(p, 1.4)
        zs = H * 0.62
        if slot == "shell":
            p.box((W * 0.7, 0.3, 0.08), T((0, 0, 0.04)), mat="body", bevel_seg=1)
            for sx in (-1, 1):
                p.lathe([(0.05, 0.08), (0.04, 0.3), (0.03, H * 0.95), (0.02, H)], T((sx * W * 0.52, 0, 0)), mat="body", segs=8)
                p.box((W * 0.2, 0.2, 0.06), T((sx * W * 0.45, 0, 0.03)), mat="body", bevel_seg=1)
        elif slot == "panel":
            p.box((W * 0.98, 0.006, J(p, 0.62, 0.08)), M(loc=(0, 0, zs + 0.12), rot=(J(p, -4, 0.5), 0, 0)), mat="glow", bevel=0)
        elif slot == "controls":
            p.box((W * 0.4, 0.004, 0.03), M(loc=(0, -0.152, 0.06)), mat="glow", bevel=0)
            for i in range(p.rng.randint(2, 4)):
                p.box((0.04, 0.006, 0.02), T((W * 0.25 + i * 0.05, -0.152, 0.05)), mat="shell_dark", bevel=0)
        elif slot == "core":
            for sx in (-1, 1):
                for z in (zs - 0.2, zs + J(p, 0.44, 0.1)):
                    p.cyl(0.04, 0.04, 0.02, M(loc=(sx * W * 0.52, 0, z), rot=(0, 90, 0)) @ T((0, 0, -0.01)), mat="glow", segs=8)
        else:
            p.ring(W * 0.38, 0.006, M(loc=(0, 0, H + 0.04), scale=(1, 0.25, 1)), mat="glow", segs=12)
            for sx in (-1, 1):
                p.box((0.012, 0.012, J(p, 0.14, 0.2)), T((sx * W * 0.52, 0, H + 0.05)), mat="shell_dark", bevel=0)
    elif e == "Wasteland":  # stacked scrap TVs on a crate: two salvaged sets, one dim-lit screen, wire aerial, patches
        W = F(p, 0.56)
        Hc = 0.42
        a_w, a_h, b_w, b_h = W * 0.9, W * 0.7, W * 0.7, W * 0.55
        if slot == "shell":
            blk(p, 0, 0.02, 0, W, 0.48, Hc, mat="wood", noise=0.02)
            crt(p, 0, 0.05, Hc, a_w, 0.42, a_h, mat="rust")
            crt(p, J(p, 0.06, 1), 0.08, Hc + a_h, b_w, 0.34, b_h, mat="paint")
        elif slot == "panel":
            p.screen(a_w * 0.62, a_h * 0.6, T((-a_w * 0.08, 0.05 - 0.21 - 0.003, Hc + a_h * 0.52)))
            p.box((b_w * 0.6, 0.006, b_h * 0.55), T((J(p, 0.06, 1) - b_w * 0.08, 0.08 - 0.17 - 0.003, Hc + a_h + b_h * 0.52)), mat="glass", bevel=0)
        elif slot == "controls":
            for i in range(p.rng.randint(2, 3)):
                knob(p, a_w * 0.38, 0.05 - 0.21, Hc + a_h * (0.75 - i * 0.2), 0.022, 0.02, mat=p.rng.choice(("rubber", "iron", "paint")), segs=7)
        elif slot == "core":
            patch(p, -a_w * 0.3, 0.05 - 0.21, Hc + a_h * 0.2, 0.12, 0.08, mat="iron", rot=J(p, 15, 0.6))
            p.box((b_w * 0.7, 0.008, 0.04), M(loc=(J(p, 0.06, 1), 0.08 - 0.17 - 0.006, Hc + a_h + b_h * 0.3), rot=(0, J(p, 10, 0.6), 0)), mat="cloth", bevel=0)
        else:
            z = Hc + a_h + b_h
            pts = [(0, 0.1, z), (0.05, 0.12, z + 0.15), (-0.15, 0.1, z + J(p, 0.35, 0.2)), (0.2, 0.12, z + 0.45)]
            wires(p, pts, r=0.004, mat="iron")
            wires(p, [(W / 2, 0.2, Hc + 0.1), (W / 2 + 0.1, 0.3, 0.02), (W / 2 + 0.3, 0.2, 0.01)], r=0.008)
    else:  # Ancient: rune stele screen: stone stele on stepped base, glowing rune field, gold frame, floating shards
        W, H = F(p, 0.9), F(p, 1.5)
        T0 = 0.18
        if slot == "shell":
            blk(p, 0, 0, T0, W, 0.2, H - T0, mat="body")
            p.box((W * 1.1, 0.24, 0.12), T((0, 0, H + 0.04)), mat="body", bevel_seg=1)
        elif slot == "panel":
            blk(p, 0, -0.104, T0 + 0.2, W * 0.75, 0.01, H * 0.62, mat="stone_dark", bevel=0)
            for x in (-W * 0.24, -W * 0.08, W * 0.08, W * 0.24):
                runes(p, x, -0.112, T0 + 0.25, T0 + 0.2 + H * 0.6, n=p.rng.randint(3, 5), w=0.05)
        elif slot == "controls":
            for sx in (-1, 1):
                p.box((0.03, 0.03, H * 0.66), T((sx * W * 0.39, -0.105, T0 + 0.2 + H * 0.31)), mat="gold", bevel=0)
            p.box((W * 0.81, 0.03, J(p, 0.03, 0.2)), T((0, -0.105, T0 + 0.2 + H * 0.64)), mat="gold", bevel=0)
        elif slot == "core":
            for sx in (-1, 1):
                z = H * J(p, 0.75, 0.1)
                p.ball(0.06, M(loc=(sx * (W / 2 + 0.14), -0.05, z), rot=(0, 0, 45), scale=(0.8, 0.8, 1.8)), mat="glow", segs=(4, 2))
        else:
            p.box((W * 1.3, 0.5, 0.09), T((0, -0.04, 0.045)), mat="stone_dark", bevel_seg=1)
            p.box((W * J(p, 1.15, 0.05), 0.36, 0.09), T((0, -0.02, 0.135)), mat="stone_dark", bevel_seg=1)
