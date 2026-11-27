"""Hafted set 3: FishingRod, Spindle, Brush, WalkingStaff, Flute, Horn (cosmos_chimera P1-19, ADR-0016).

Same frame as kit_forms' Hoe and forms_tools: the grip end sits at the origin, the haft runs up +Z to z = L and the
working end (tip, whorl, bristles, knob, mouth hole, bell) is the head. Flutes and horns are their own haft: the
haft slot is the sounding tube, the butt the foot or mouthpiece at the hand.
Long pieces (fishing rod, walking staff) stand on their butt through the hand; short ones are held about 12 % up.
Haft length and radius are frame values (F, drawn first and in this order); head-only proportions use J.
Glow only where the era has its own (Steampunk, Future, Wasteland, Ancient): tools and music do not light up.
"""
import math

from mathutils import Matrix, Vector

from forms_tools import _butt, _haft, disk, rod, stone_collar
from kit_forms import F, HAFTED, J, function, joint
from kit_lib import M

T = Matrix.Translation
TAU = math.tau


def line(p, pts, r=0.0012, mat="rope"):
    p.tube(pts, r, mat=mat, segs=3)


def holes(p, z0, z1, n, r, rad, mat="rubber"):
    """Finger holes as dark studs on the -Y face of a tube of radius rad."""
    for i in range(n):
        z = z0 + (z1 - z0) * i / max(1, n - 1)
        disk(p, (0, -rad + 0.0005, z), r, 0.003, "y", mat, segs=6)


def taper(p, L, r0, r1, mat="body", segs=7, z0=0.0):
    p.cyl(r0, r1, L - z0, T((0, 0, z0)), mat=mat, segs=segs)


def rings(p, zs, r, mat="fit", t=0.006, segs=7):
    for z in zs:
        p.cyl(r, r, t, T((0, 0, z - t / 2)), mat=mat, segs=segs)


def hafted(L0, r0, haft_fn, head, joint_fn=None, butt_fn=None, sl=0.08):
    """Hafted form with era-table haft length and a radius from the frame stream."""
    def form(p, slot):
        L = F(p, L0[p.era] if isinstance(L0, dict) else L0, sl)
        r = F(p, r0, 0.08)
        if slot == "haft":
            haft_fn(p, L, r)
        elif slot == "joint":
            (joint_fn or (lambda q, L_, r_: joint(q, L_, r_)))(p, L, r)
        elif slot == "butt":
            (butt_fn or (lambda q, L_, r_: _butt(q, r_)))(p, L, r)
        else:
            head(p, L, r)
    return form


# ================================================================ FishingRod
def _rod_haft(p, L, r):
    e = p.era
    if e == "Primal":  # harpoon shaft: straight sapling
        _haft(p, L, r * 1.2)
    elif e == "Agrarian":  # bamboo pole with nodes
        taper(p, L, r * 1.2, r * 0.45, mat="wood")
        rings(p, [L * k for k in (0.2, 0.42, 0.62, 0.8)], r * 1.05, mat="wood_dark", t=0.008)
    elif e == "Mercantile":  # tapered cane with a cork-like grip
        taper(p, L, r, r * 0.3, mat="wood_dark")
        p.cyl(r * 1.35, r * 1.25, L * 0.16, T((0, 0, 0.02)), mat="hide", segs=8)
    elif e == "Industrial":  # carbon blank, rubber grip
        taper(p, L, r * 0.8, r * 0.22, mat="rubber")
        p.cyl(r * 1.3, r * 1.15, L * J(p, 0.2, 0.15), mat="grip", segs=8)
    elif e == "Steampunk":
        taper(p, L, r, r * 0.35, mat="wood_dark")
        rings(p, [L * k for k in (0.25, 0.5, 0.72)], r * 0.9, mat="brass")
        p.cyl(r * 1.3, r * 1.3, L * 0.15, T((0, 0, 0.02)), mat="leather", segs=8)
    elif e == "Future":  # telescoping shell sections
        for i, k in enumerate((1.0, 0.75, 0.55, 0.38)):
            z = L * i * 0.25
            p.cyl(r * k, r * k * 0.92, L * 0.27, T((0, 0, z)), mat="body" if i % 2 == 0 else "shell_dark", segs=8)
        p.box((r * 0.4, r * 0.3, L * 0.18), T((0, -r * 0.9, L * 0.12)), mat="glow", bevel=0)
    elif e == "Wasteland":  # car-antenna sections on a pipe grip
        p.cyl(r * 1.1, r * 1.1, L * 0.3, mat="rust", segs=7)
        taper(p, L, r * 0.6, r * 0.2, mat="steel", z0=L * 0.28)
        p.cyl(r * 1.2, r * 1.2, L * 0.06, T((0, 0, L * J(p, 0.12, 0.3))), mat="cloth", segs=7)
    else:
        taper(p, L, r * 1.1, r * 0.4, mat="stone", segs=6)
        for k in (0.3, 0.55, 0.78):
            p.box((r * 0.3, r * 0.15, L * 0.06), T((0, -r * (1.05 - k * 0.6), L * k)), mat="glow", bevel=0)


def _rod_head(p, L, r):
    e = p.era
    drop = J(p, 0.55, 0.2)
    lean = J(p, 0.08, 0.3)
    tip = (0, 0, L)
    hang = (0, -lean - 0.06, L - drop)
    if e == "Primal":  # barbed bone harpoon point lashed on, no line
        p.lathe([(r * 1.2, L - 0.02), (r * 1.1, L + 0.02), (r * 0.6, L + 0.12), (0, L + J(p, 0.2, 0.15))], mat="bone", segs=6)
        for s in (1, -1):
            for k in (0.06, 0.11):
                p.tube([(0, 0, L + k), (s * 0.012, -0.004, L + k - 0.03)], 0.0035, mat="bone", segs=3)
        p.band(r * 1.3, L - 0.01, h=0.03)
        return
    line(p, [tip, (0, -lean * 0.6, L - drop * 0.4), hang])
    if e == "Agrarian":
        p.ball(0.012, T((0, -lean * 0.6, L - drop * 0.5)), mat="feather", segs=(6, 4))
        rod(p, hang, (0, hang[1], hang[2] - 0.03), 0.002, mat="iron", segs=3)
    elif e == "Mercantile":
        p.lathe([(0, 0), (0.012, 0.012), (0.008, 0.03), (0, 0.045)], T((0, -lean * 0.6, L - drop * 0.55)), mat="paint", segs=6)
        rod(p, hang, (0, hang[1] - 0.01, hang[2] - 0.025), 0.002, mat="iron", segs=3)
    elif e == "Industrial":  # spoon lure and tip guide
        p.box((0.012, 0.004, 0.035), T((0, hang[1], hang[2] - 0.02)), mat="steel", bevel=0)
        p.ring(r * 0.6, 0.0015, T((0, -r * 0.6, L - 0.03)) @ M(rot=(90, 0, 0)), mat="steel", segs=6)
    elif e == "Steampunk":  # brass bobber with a little lamp
        p.ball(0.016, T((0, -lean * 0.6, L - drop * 0.5)), mat="brass", segs=(6, 4))
        p.ball(0.006, T((0, -lean * 0.6, L - drop * 0.5 + 0.018)), mat="glow", segs=(5, 3))
        rod(p, hang, (0, hang[1], hang[2] - 0.03), 0.0025, mat="copper", segs=3)
    elif e == "Future":  # sonar pod at the tip
        p.ball(r * 1.4, T((0, -r * 0.4, L + 0.01)), mat="body", segs=(8, 5))
        p.ring(r * 1.3, r * 0.2, T((0, -r * 0.4, L + 0.01)) @ M(rot=(70, 0, 0)), mat="glow", segs=8)
        p.ball(0.01, T(hang), mat="glow", segs=(6, 4))
    elif e == "Wasteland":  # bottle-cap float, bent-nail hook
        p.cyl(0.014, 0.014, 0.008, T((0, -lean * 0.6, L - drop * 0.5)), mat="paint", segs=7)
        p.tube([hang, (0, hang[1], hang[2] - 0.03), (0, hang[1] - 0.01, hang[2] - 0.02)], 0.0025, mat="rust", segs=3)
    else:
        p.lathe([(r * 0.6, L - 0.02), (r * 1.2, L), (0, L + 0.04)], mat="stone", segs=6)
        p.ball(0.012, T(hang), mat="glow", segs=(6, 4))


def _rod_joint(p, L, r):
    e = p.era
    z = L * J(p, 0.2, 0.1) if e not in ("Primal",) else L * 0.85
    if e == "Primal":
        p.band(r * 1.3, z, h=0.05)
        p.tube([(r * 1.2, 0, z), (0.03, -0.02, z - 0.08), (0.02, -0.03, z - 0.18)], 0.0025, mat="hide", segs=3)
    elif e == "Agrarian":  # hand winder: two pegs with wound line
        for zz in (z, z + 0.08):
            rod(p, (0, 0, zz), (0, -0.04, zz), 0.005, mat="wood", segs=5)
        p.cyl(0.006, 0.006, 0.08, T((0, -0.03, z)), mat="rope", segs=5)
    elif e == "Mercantile":  # wooden reel
        disk(p, (r * 2.4, -0.01, z), J(p, 0.03, 0.1), 0.02, "x", "wood", segs=10)
        p.tube([(r, 0, z), (r * 2.4, -0.01, z)], 0.004, mat="brass", segs=4)
        disk(p, (r * 2.4 + 0.012, -0.03, z + 0.01), 0.004, 0.012, "x", "wood_dark", segs=5)
    elif e == "Industrial":  # spinning reel and guides
        p.box((0.012, 0.02, 0.03), T((0, -r * 1.5, z)), mat="steel", bevel=0)
        p.cyl(0.022, 0.02, 0.035, T((0, -0.05, z - 0.017)) @ M(rot=(0, 0, 0)), mat="paint", segs=8)
        rod(p, (0, -0.03, z + 0.005), (0.035, -0.04, z + 0.005), 0.003, mat="steel", segs=4)
        for k in (0.45, 0.7):
            p.ring(r * 0.8, 0.0015, T((0, -r * 0.9, L * k)) @ M(rot=(90, 0, 0)), mat="steel", segs=6)
    elif e == "Steampunk":  # clockwork reel: brass drum and gear
        disk(p, (r * 2.4, -0.012, z), 0.032, 0.025, "x", "brass", segs=10)
        disk(p, (r * 2.4 + 0.016, -0.012, z), 0.022, 0.006, "x", "copper", segs=8)
        p.tube([(r, 0, z), (r * 2.4, -0.012, z)], 0.004, mat="copper", segs=4)
        p.ball(0.005, T((r * 2.4 + 0.022, -0.012, z)), mat="glow", segs=(5, 3))
    elif e == "Future":
        p.box((r * 2.6, r * 2.2, 0.07), T((0, -r * 0.8, z)), mat="body", bevel=0.2, bevel_seg=1)
        p.box((r * 1.6, 0.003, 0.035), T((0, -r * 1.92, z)), mat="glow", bevel=0)
    elif e == "Wasteland":  # tin-can reel with a crank
        p.cyl(0.03, 0.03, 0.04, T((r * 2.6, -0.01, z - 0.02)) @ M(rot=(0, 90, 0)), mat="rust", segs=8)
        p.tube([(r * 2.6 + 0.02, -0.01, z), (r * 2.6 + 0.03, -0.04, z - 0.02)], 0.003, mat="steel", segs=3)
        p.band(r * 1.2, z, h=0.03)
    else:
        p.ring(r * 2.2, r * 0.5, T((0, 0, z)), mat="stone", segs=8)
        p.ring(r * 2.25, r * 0.15, T((0, 0, z)), mat="glow", segs=8)


function("FishingRod", "Hafted", HAFTED, "carried")(hafted(
    {"Primal": 1.5, "Agrarian": 1.9, "Mercantile": 1.75, "Industrial": 1.7, "Steampunk": 1.6, "Future": 1.5,
     "Wasteland": 1.6, "Ancient": 1.55}, 0.014, _rod_haft, _rod_head, _rod_joint))


# ================================================================ Spindle
# The haft is the spindle shaft; the head is the whorl (or the wheel), the joint the wound yarn, the butt the tip.
def _sp_haft(p, L, r):
    e = p.era
    if e in ("Primal", "Agrarian"):
        p.lathe([(r * 0.5, 0), (r, L * 0.3), (r * 0.9, L * 0.7), (r * 0.4, L)], mat="wood", segs=6, noise=0.02 if e == "Primal" else 0)
    elif e == "Mercantile":  # hand wheel on a staff: the haft is the staff
        _haft(p, L, r * 1.6)
    elif e == "Industrial":
        p.lathe([(r * 0.6, 0), (r * 0.5, L * 0.5), (r * J(p, 0.35, 0.2), L)], mat="steel", segs=6)
    elif e == "Steampunk":
        p.cyl(r * 0.7, r * 0.5, L, mat="brass", segs=6)
        p.cyl(r * 1.5, r * 1.5, L * 0.25, T((0, 0, 0.0)), mat="leather", segs=8)
    elif e == "Future":  # pen body
        p.lathe([(r * 0.5, 0), (r * 1.3, L * 0.12), (r * 1.3, L * 0.85), (r * 0.9, L)], mat="body", segs=8)
    elif e == "Wasteland":  # rebar with a taped grip
        p.cyl(r * 0.7, r * 0.7, L, mat="rust", segs=6)
        p.cyl(r * 1.0, r * 1.0, L * 0.2, T((0, 0, L * 0.05)), mat="cloth", segs=6)
    else:
        p.cyl(r * 0.8, r * 0.5, L, mat="stone", segs=6)
        p.box((r * 0.25, r * 0.2, L * 0.4), T((0, -r * 0.62, L * 0.45)), mat="glow", bevel=0)


def _sp_head(p, L, r):
    e = p.era
    z = L * 0.18
    if e == "Primal":  # stone whorl
        p.cyl(J(p, 0.035, 0.15), J(p, 0.03, 0.15), 0.014, T((0, 0, z)), mat="stone", segs=8, noise=0.04)
    elif e == "Agrarian":
        p.lathe([(r, z), (J(p, 0.03, 0.15), z + 0.006), (J(p, 0.024, 0.15), z + 0.022), (r, z + 0.03)], mat="wood_dark", segs=10)
    elif e == "Mercantile":  # little spinning wheel at the top of the staff
        R = J(p, 0.12, 0.1)
        c = (0, 0, L + R + 0.02)
        p.ring(R, 0.008, T(c) @ M(rot=(0, 90, 0)), mat="wood", segs=12, square=False)
        for i in range(3):
            p.box((0.006, R * 1.9, 0.006), T(c) @ M(rot=(i * 60, 0, 0)), mat="wood", bevel=0)
        p.box((0.02, 0.03, R + 0.03), T((0, 0, L + (R + 0.03) / 2)), mat="wood_dark", bevel=0)
    elif e == "Industrial":  # bobbin flanges
        for zz in (L * 0.35, L * 0.85):
            p.cyl(J(p, 0.026, 0.1), 0.026, 0.006, T((0, 0, zz)), mat="paint", segs=10)
    elif e == "Steampunk":  # tiny boiler and gear by the bobbin
        p.cyl(0.02, 0.02, 0.05, T((0.03, 0, L * 0.3)), mat="copper", segs=8)
        p.ball(0.02, T((0.03, 0, L * 0.3 + 0.05)), mat="copper", segs=(8, 4))
        disk(p, (0, -0.012, L * 0.62), J(p, 0.03, 0.1), 0.006, "y", "brass", segs=8)
        p.ball(0.005, T((0.03, -0.02, L * 0.32)), mat="glow", segs=(5, 3))
    elif e == "Future":  # glowing nozzle
        p.lathe([(r * 0.9, L), (r * 0.5, L + 0.02), (r * 0.15, L + 0.035)], mat="shell_dark", segs=8)
        p.ball(r * 0.35, T((0, 0, L + 0.038)), mat="glow", segs=(6, 4))
    elif e == "Wasteland":  # stack of washers and a nut
        for i in range(p.rng.randint(2, 3)):
            p.cyl(J(p, 0.028, 0.2), 0.028, 0.004, T((0, 0, z + i * 0.005)), mat="steel", segs=8)
        p.cyl(0.012, 0.012, 0.01, T((0, 0, z + 0.016)), mat="iron", segs=6)
    else:
        p.ring(J(p, 0.03, 0.1), 0.008, T((0, 0, z)), mat="stone", segs=8)
        p.ring(0.03, 0.003, T((0, 0, z + 0.006)), mat="glow", segs=8)


def _sp_joint(p, L, r):
    e = p.era
    if e == "Mercantile":  # yarn on a short spindle at the side of the wheel and a crank
        R = 0.12
        p.cyl(0.012, 0.018, 0.06, T((0, -0.04, L + 0.02)) @ M(rot=(-90, 0, 0)), mat="cloth", segs=6)
        p.tube([(0.015, 0, L + R + 0.02), (0.04, -0.03, L + R - 0.02)], 0.004, mat="wood_dark", segs=4)
        line(p, [(0, -0.1, L + 0.02), (0, -0.02, L + R * 2)], mat="cloth")
        return
    if e == "Future":  # fibre spool clipped on the side
        disk(p, (r * 1.5, 0, L * 0.6), J(p, 0.018, 0.1), 0.012, "x", "paint", segs=8)
        return
    z0, z1 = L * 0.32, L * J(p, 0.75, 0.08)
    rr = J(p, 0.018, 0.2)
    p.lathe([(r, z0), (rr, z0 + (z1 - z0) * 0.25), (rr * 1.05, z0 + (z1 - z0) * 0.6), (r, z1)],
            mat="cloth" if e not in ("Primal",) else "rope", segs=8)
    if e in ("Primal", "Agrarian"):
        line(p, [(0, 0, z1), (rr * 0.6, -0.01, L * 0.95), (0, -0.01, L + 0.05)], mat="rope")


def _sp_butt(p, L, r):
    e = p.era
    if e == "Mercantile":
        _butt(p, r * 1.6)
    elif e in ("Industrial", "Wasteland"):
        h = J(p, 0.02, 0.3)
        p.cyl(0.0005, r * 0.6, h, T((0, 0, -h)), mat="steel", segs=5)
    elif e == "Steampunk":
        p.lathe([(0, -0.02), (r * 1.6, -0.01), (r * 1.5, 0)], mat="brass", segs=6)
    elif e == "Future":
        p.ball(r * 0.6, T((0, 0, 0)), mat="shell_dark", segs=(6, 4))
    elif e == "Ancient":
        p.lathe([(0, -0.015), (r * 0.9, -0.005), (r * 0.8, 0)], mat="stone", segs=6)
    else:  # notched top: hook groove
        p.tube([(0, 0, L - 0.005), (0.004, -0.006, L + 0.012), (0, -0.01, L + 0.008)], 0.0022, mat="rope", segs=3)


function("Spindle", "Hafted", HAFTED, "carried")(hafted(
    {"Primal": 0.28, "Agrarian": 0.3, "Mercantile": 0.55, "Industrial": 0.24, "Steampunk": 0.26, "Future": 0.16,
     "Wasteland": 0.27, "Ancient": 0.28}, 0.006, _sp_haft, _sp_head, _sp_joint, _sp_butt))


# ================================================================ Brush
def _br_haft(p, L, r):
    e = p.era
    if e == "Primal":  # the ochre stick is a lump of pigment bound to a twig
        _haft(p, L, r)
    elif e == "Agrarian":
        p.cyl(r, r * 0.95, L, mat="wood", segs=7)
    elif e == "Mercantile":
        p.lathe([(r * 0.5, 0), (r * 1.1, L * 0.55), (r * 0.9, L)], mat="paint", segs=7)
    elif e == "Industrial":  # airbrush body
        p.lathe([(r * 0.6, 0), (r * 1.5, L * 0.3), (r * 1.6, L * 0.8), (r * 1.1, L)], mat="steel", segs=8)
    elif e == "Steampunk":
        p.lathe([(r * 1.4, 0), (r * 1.35, L * 0.5), (r * J(p, 1.3, 0.1), L)], mat="brass", segs=8)
    elif e == "Future":
        p.lathe([(r * 0.4, 0), (r * 1.3, L * 0.15), (r * 1.2, L * 0.9), (r * 0.8, L)], mat="body", segs=8)
        p.box((r * 0.4, r * 0.3, L * 0.4), T((0, -r * 1.2, L * 0.5)), mat="glow", bevel=0)
    elif e == "Wasteland":  # stick with a taped spray can
        _haft(p, L, r)
    else:
        p.cyl(r * 1.2, r * 0.9, L, mat="stone", segs=6)
        p.box((r * 0.3, r * 0.2, L * 0.5), T((0, -r * 1.05, L * 0.45)), mat="glow", bevel=0)


def _br_head(p, L, r):
    e = p.era
    h = J(p, 0.045, 0.2)
    if e == "Primal":
        p.ball(1.0, M(loc=(0, 0, L + h * 0.4), scale=(r * 2.2, r * 1.8, h * 0.8)), mat="ceramic", segs=(6, 4), noise=0.05)
    elif e == "Agrarian":  # tuft with an inked tip
        p.lathe([(r * 1.1, L), (r * 1.5, L + h * 0.3), (r * 0.6, L + h * 0.8), (0, L + h)], mat="hide", segs=7)
        p.lathe([(r * 0.62, L + h * 0.78), (0, L + h * 1.02)], mat="rubber", segs=6)
    elif e == "Mercantile":  # brass ferrule and flat bristles with paint
        p.cyl(r * 1.0, r * 1.3, h * 0.6, T((0, 0, L)), mat="brass", segs=7)
        p.box((r * 2.8, r * 1.0, h * 0.7), T((0, 0, L + h * 0.95)), mat="hide", bevel=0)
        p.box((r * 2.6, r * 0.9, h * 0.18), T((0, 0, L + h * 1.38)), mat="paint", bevel=0)
    elif e == "Industrial":  # nozzle and paint cup
        p.cyl(r * 1.0, r * 0.2, h * 0.7, T((0, 0, L)), mat="steel", segs=7)
        p.cyl(r * 1.8, r * 1.6, h * 0.6, T((0, r * 2.2, L * 0.7)), mat="glass", segs=8)
    elif e == "Steampunk":  # rubber bulb and brass horn nozzle
        p.lathe([(r * 1.3, L), (r * 0.6, L + h * 0.5), (r * 1.4, L + h)], mat="copper", segs=8)
        p.ball(r * 2.4, T((0, r * 2.6, L * 0.35)), mat="rubber", segs=(7, 5))
        p.ball(r * 0.6, T((0, -r * 1.2, L * 0.7)), mat="glow", segs=(5, 3))
    elif e == "Future":
        p.lathe([(r * 0.8, L), (r * 0.3, L + h * 0.6), (0, L + h * 0.7)], mat="shell_dark", segs=8)
        p.ball(r * 0.6, T((0, 0, L + h * 0.75)), mat="glow", segs=(6, 4))
    elif e == "Wasteland":
        p.cyl(r * 3.2, r * 3.2, h * 1.6, T((0, -r * 3.6, L - h)), mat="paint", segs=8)
        p.cyl(r * 1.0, r * 1.0, h * 0.3, T((0, -r * 3.6, L + h * 0.6)), mat="steel", segs=6)
    else:
        p.lathe([(r * 0.9, L), (r * 0.4, L + h * 0.7), (0, L + h)], mat="stone_dark", segs=6)
        p.ball(r * 0.5, T((0, 0, L + h * 0.95)), mat="glow", segs=(5, 3))


def _br_joint(p, L, r):
    e = p.era
    if e == "Primal":  # sinew wrap binding the pigment
        p.band(r * 1.4, L - 0.006, h=0.02)
    elif e == "Agrarian":  # hanging loop at the top end of the stick (bottom here)
        p.ring(r * 1.6, 0.0015, T((0, 0, 0.004)) @ M(rot=(90, 0, 0)), mat="rope", segs=6)
        p.cyl(r * 1.08, r * 1.08, 0.008, T((0, 0, L - 0.012)), mat="bone", segs=7)
    elif e == "Mercantile":
        p.cyl(r * 1.02, r * 1.02, 0.006, T((0, 0, L * J(p, 0.6, 0.1))), mat="gold", segs=7)
    elif e == "Industrial":  # trigger and hose
        p.box((r * 0.8, r * 1.2, r * 2.2), T((0, -r * 1.6, L * 0.75)), mat="steel", bevel=0)
        p.tube([(0, 0, 0.002), (0, 0.01, -0.03), (0.02, 0.02, -0.08)], r * 0.45, mat="rubber", segs=4)
    elif e == "Steampunk":
        p.ring(r * 1.45, r * 0.3, T((0, 0, L * 0.5)), mat="copper", segs=8)
        p.tube([(0, r * 1.4, L * 0.5), (0, r * 2.2, L * 0.4)], r * 0.35, mat="copper", segs=4)
    elif e == "Future":
        p.ring(r * 1.25, r * J(p, 0.15, 0.3), T((0, 0, L * J(p, 0.15, 0.3))), mat="shell_dark", segs=8)
    elif e == "Wasteland":
        p.band(r * 3.0, L - 0.01, h=0.02)
    else:
        p.ring(r * 1.25, r * J(p, 0.25, 0.3), T((0, 0, L * J(p, 0.2, 0.3))), mat="stone_dark", segs=6)


function("Brush", "Hafted", HAFTED, "carried")(hafted(
    {"Primal": 0.16, "Agrarian": 0.2, "Mercantile": 0.24, "Industrial": 0.14, "Steampunk": 0.14, "Future": 0.15,
     "Wasteland": 0.16, "Ancient": 0.17}, 0.0055, _br_haft, _br_head, _br_joint))


# ================================================================ WalkingStaff
def _st_head(p, L, r):
    e = p.era
    if e == "Primal":  # forked branch top
        for s in (1, -1):
            p.tube([(0, 0, L - 0.02), (s * 0.03, -0.005, L + 0.07), (s * J(p, 0.045, 0.2), 0, L + J(p, 0.14, 0.2))], r * 0.6, mat="body", segs=5)
    elif e == "Agrarian":  # carved knob
        p.lathe([(r, L), (r * 1.6, L + 0.03), (r * J(p, 1.9, 0.12), L + 0.06), (r * 1.2, L + 0.1), (0, L + 0.11)], mat="wood_dark", segs=8)
        p.ring(r * 1.55, 0.002, T((0, 0, L + 0.03)), mat="wood", segs=8)
    elif e == "Mercantile":  # silver pommel
        p.lathe([(r, L), (r * 1.2, L + 0.02), (r * J(p, 1.9, 0.12), L + 0.05), (r * 1.4, L + 0.08), (0, L + 0.09)], mat="steel", segs=10)
    elif e == "Industrial":  # crook handle
        R = J(p, 0.05, 0.12)
        pts = [(0, 0, L)] + [(0, -R + R * math.cos(a), L + R * math.sin(a) * 1.1) for a in (0.6, 1.4, 2.2, 3.0)]
        p.tube(pts, r * 0.95, mat="wood_dark", segs=7)
    elif e == "Steampunk":  # brass knob with a gear and gauge
        p.lathe([(r, L), (r * 1.8, L + 0.03), (r * 2.0, L + 0.07), (r * 1.2, L + 0.1), (0, L + 0.11)], mat="brass", segs=10)
        disk(p, (0, -r * 2.0, L + 0.05), r * 1.0, 0.004, "y", "glow", segs=8)
    elif e == "Future":  # hover ring around the top
        p.ball(r * 1.3, T((0, 0, L + 0.01)), mat="body", segs=(8, 5))
        p.ring(J(p, 0.05, 0.15), 0.006, T((0, 0, L + 0.06)) @ M(rot=(12, 0, 0)), mat="glow", segs=10)
    elif e == "Wasteland":  # rebar crook with a rag tied on
        p.tube([(0, 0, L - 0.01), (0, 0, L + 0.08), (0, -0.05, L + 0.1), (0, -0.06, L + 0.06)], r * 0.6, mat="rust", segs=5)
        p.box((0.05, 0.006, 0.08), M(loc=(0.02, -0.01, L - 0.05), rot=(0, 15, 0)), mat="cloth", bevel=0)
    else:  # stone crown holding a glowing crystal
        stone_collar(p, L, r, 0.05)
        p.lathe([(0, L + 0.02), (r * 1.3, L + 0.06), (0, L + J(p, 0.14, 0.15))], mat="glow", segs=6)


def _st_haft(p, L, r):
    if p.era == "Industrial":  # steel core under a dark wood skin
        p.lathe([(r * 0.8, 0), (r * 0.75, L * 0.5), (r * J(p, 0.7, 0.08), L)], mat="wood_dark", segs=8)
        return
    _haft(p, L, r)


function("WalkingStaff", "Hafted", HAFTED, "carried")(hafted(
    {"Primal": 1.55, "Agrarian": 1.4, "Mercantile": 0.88, "Industrial": 0.82, "Steampunk": 0.95, "Future": 1.3,
     "Wasteland": 1.4, "Ancient": 1.45}, 0.017, _st_haft, _st_head))


# ================================================================ Flute
def _fl_haft(p, L, r):
    e = p.era
    if e == "Primal":  # bone tube
        p.lathe([(r * 1.3, 0), (r, L * 0.2), (r * 0.9, L * 0.6), (r * 1.05, L * 0.9), (r * 1.35, L)], mat="bone", segs=7, noise=0.02)
        holes(p, L * 0.35, L * 0.7, 3, r * 0.3, r * 0.92)
    elif e == "Agrarian":
        p.cyl(r, r * 0.96, L, mat="wood", segs=8)
        holes(p, L * 0.3, L * 0.7, 6, r * 0.28, r)
    elif e == "Mercantile":
        p.lathe([(r * 1.15, 0), (r, L * 0.08), (r * 0.92, L * 0.6), (r * 1.05, L * 0.95), (r * 1.2, L)], mat="wood_dark", segs=8)
        holes(p, L * 0.25, L * 0.65, 6, r * 0.28, r * 0.95)
    elif e == "Industrial":
        p.lathe([(r * 0.9, 0), (r * 0.9, L * J(p, 0.5, 0.3)), (r * 0.9, L)], mat="steel", segs=10)
    elif e == "Steampunk":  # three brass pipes bound side by side
        for i, k in enumerate((1.0, 0.85, 0.7)):
            p.cyl(r * 0.7, r * 0.7, L * k, T(((i - 1) * r * 1.5, 0, 0)), mat="brass", segs=7)
    elif e == "Future":
        p.lathe([(r * 0.8, 0), (r * 1.1, L * 0.1), (r * 1.1, L * 0.9), (r * 0.8, L)], mat="body", segs=8)
        for i in range(5):
            disk(p, (0, -r * 1.1, L * (0.3 + i * 0.1)), r * 0.3, 0.003, "y", "glow", segs=6)
    elif e == "Wasteland":  # cut pipe with drilled holes
        p.cyl(r, r, L, mat="rust", segs=7)
        holes(p, L * 0.3, L * 0.7, 5, r * 0.3, r)
    else:
        p.cyl(r * 1.15, r * 1.05, L, mat="stone", segs=6)
        for i in range(5):
            disk(p, (0, -r * 1.05, L * (0.3 + i * 0.09)), r * 0.3, 0.003, "y", "glow", segs=6)


def _fl_head(p, L, r):
    e = p.era
    if e == "Primal":
        p.ring(r * 1.3, r * 0.35, T((0, 0, L - 0.003)), mat="hide", segs=7)
        disk(p, (0, -r, L * 0.88), r * 0.4, 0.003, "y", "rubber", segs=6)
    elif e == "Agrarian":
        p.cyl(r * 1.08, r * 1.08, 0.01, T((0, 0, L * 0.86)), mat="wood_dark", segs=8)
        disk(p, (0, -r, L * 0.92), r * 0.4, 0.003, "y", "rubber", segs=6)
    elif e == "Mercantile":
        p.lathe([(r * 1.1, L), (r * 1.35, L + 0.02), (r * 1.2, L + 0.04), (0, L + 0.045)], mat="bone", segs=8)
    elif e == "Industrial":  # lip plate and crown
        p.box((r * 1.8, r * 0.5, r * 2.6), T((0, -r * 1.0, L * 0.88)), mat="steel", bevel=0)
        p.lathe([(r * 0.9, L), (r * 1.1, L + 0.01), (0, L + 0.015)], mat="steel", segs=8)
    elif e == "Steampunk":  # mouthpiece manifold
        p.box((r * 4.4, r * 1.6, r * 1.8), T((0, 0, L + r * 0.4)), mat="copper", bevel=0)
        p.cyl(r * 0.5, r * 0.4, r * 2.0, T((0, -r * 0.8, L + r)) @ M(rot=(-90, 0, 0)), mat="brass", segs=6)
    elif e == "Future":
        p.ring(r * 1.15, r * 0.25, T((0, 0, L - 0.005)), mat="glow", segs=8)
        p.ball(r * 1.0, T((0, 0, L)), mat="shell_dark", segs=(8, 4))
    elif e == "Wasteland":  # hose mouthpiece
        p.tube([(0, 0, L), (0, -0.01, L + 0.03), (0, -0.03, L + 0.05)], r * 0.6, mat="rubber", segs=5)
    else:
        p.lathe([(r * 1.1, L), (r * 1.6, L + 0.02), (r * 0.8, L + 0.05), (0, L + 0.055)], mat="stone", segs=6)


def _fl_joint(p, L, r):
    e = p.era
    if e in ("Primal", "Agrarian"):
        rings(p, [L * 0.15, L * J(p, 0.82, 0.04)], r * 1.06, mat="rope" if e == "Primal" else "cloth")
    elif e == "Mercantile":
        rings(p, [L * 0.08, L * 0.5, L * 0.95], r * 1.12, mat="bone", t=0.012)
    elif e == "Industrial":  # key mechanism
        p.box((r * 0.3, r * 0.3, L * 0.55), T((r * 0.9, -r * 0.4, L * 0.45)), mat="steel", bevel=0)
        for i in range(6):
            disk(p, (0, -r * 0.92, L * (0.2 + i * 0.09)), r * 0.45, 0.004, "y", "steel", segs=6)
    elif e == "Steampunk":  # valves
        for i in range(3):
            p.cyl(r * 0.45, r * 0.45, r * 1.4, T(((i - 1) * r * 1.5, -r * 0.7, L * 0.55)) @ M(rot=(90, 0, 0)), mat="copper", segs=6)
        p.box((r * 4.4, r * 0.6, r * 0.8), T((0, 0, L * 0.3)), mat="brass", bevel=0)
    elif e == "Future":
        rings(p, [L * 0.12, L * 0.92], r * 1.15, mat="shell_dark", t=0.01)
    elif e == "Wasteland":
        rings(p, [L * J(p, 0.5, 0.3)], r * 1.1, mat="cloth", t=0.03)
    else:
        rings(p, [L * 0.12, L * 0.9], r * 1.2, mat="gold", t=0.008, segs=6)


def _fl_butt(p, L, r):
    e = p.era
    if e == "Steampunk":
        p.box((r * 4.4, r * J(p, 1.2, 0.2), r * 0.8), T((0, 0, r * 0.4)), mat="brass", bevel=0)
    elif e in ("Mercantile", "Industrial"):
        p.lathe([(r * 1.1, -0.008), (r * 1.25, 0), (r * 1.0, 0.012)], mat="bone" if e == "Mercantile" else "steel", segs=8)
    elif e == "Future":
        p.ball(r * 1.0, M(scale=(1, 1, 0.6)), mat="shell_dark", segs=(8, 4))
    elif e == "Ancient":
        p.lathe([(0, -0.02), (r * 1.4, -0.01), (r * 1.1, 0)], mat="stone_dark", segs=6)
    else:  # carry cord
        line(p, [(0, 0, 0.005), (0.02, -0.004, -0.03), (0.005, -0.01, -0.06)], r=0.0015, mat="rope" if e != "Wasteland" else "rubber")


function("Flute", "Hafted", HAFTED, "carried")(hafted(
    {"Primal": 0.2, "Agrarian": 0.45, "Mercantile": 0.6, "Industrial": 0.62, "Steampunk": 0.38, "Future": 0.4,
     "Wasteland": 0.42, "Ancient": 0.5}, 0.011, _fl_haft, _fl_head, _fl_joint, _fl_butt))


# ================================================================ Horn
# The grip end (origin) is the mouthpiece; the tube rises +Z and swings to -Y, the bell is the head.
def _horn_path(p, L, curl):
    """Points of the horn's centre line from the mouthpiece (origin) to the bell seat."""
    pts = []
    for i in range(6):
        t = i / 5
        a = t * curl
        pts.append(Vector((0, -math.sin(a) * L * 0.35, t * L * (1 - 0.25 * curl / math.pi))))
    return pts


def _cone_chain(p, pts, r0, r1, mat, segs=7):
    n = len(pts) - 1
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        rod(p, tuple(a), tuple(b), r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n, mat=mat, segs=segs)


HORN = {"Primal": (1.6, "bone"), "Agrarian": (0.0, "ceramic"), "Mercantile": (0.15, "copper"), "Industrial": (0.0, "brass"),
        "Steampunk": (0.3, "brass"), "Future": (0.0, "body"), "Wasteland": (0.2, "rust"), "Ancient": (1.2, "stone")}


def _hn_haft(p, L, r):
    e = p.era
    curl, mat = HORN[e]
    if e == "Agrarian":  # conch: spiral whorls stacked on the axis
        for i in range(4):
            k = 1 - i * 0.22
            p.ball(1.0, M(loc=(0, 0, L * (0.25 + i * 0.18)), rot=(0, 0, i * 40), scale=(r * 4.5 * k, r * 3.8 * k, L * 0.14)), mat="ceramic", segs=(8, 5))
        return
    if e == "Industrial":  # bugle: one loop of tube
        pts = [(0, 0, 0), (0, 0, L * 0.5), (0, -0.05, L * 0.72), (0, -0.1, L * 0.5), (0, -0.1, L * 0.15), (0, -0.05, L * 0.05),
               (0, 0, L * 0.25), (0, 0, L * 0.9)]
        p.tube(pts, r * 0.55, mat="brass", segs=6)
        return
    if e == "Future":  # emitter grip
        p.lathe([(r * 0.8, 0), (r * 1.4, L * 0.1), (r * 1.3, L * 0.85), (r * 0.9, L)], mat="body", segs=8)
        p.box((r * 0.4, r * 0.3, L * 0.5), T((0, -r * 1.3, L * 0.45)), mat="glow", bevel=0)
        return
    _cone_chain(p, _horn_path(p, L, curl), r * 0.5, r * 1.4, mat)


def _hn_head(p, L, r):
    e = p.era
    curl, mat = HORN[e]
    if e == "Agrarian":  # conch spire tip and lip
        p.lathe([(r * 2.0, L * 0.8), (r * 1.0, L * 0.95), (0, L * J(p, 1.05, 0.05))], mat="ceramic", segs=7)
        p.plate([(0, L * 0.2), (r * 3.2, L * 0.3), (r * 3.5, L * 0.6), (0, L * 0.7)], 0.006, T((0, -r * 3.8, 0)), mat="bone", bevel=0)
        return
    if e == "Future":  # emitter dish
        R = J(p, 0.06, 0.15)
        p.lathe([(r, L), (R, L + 0.03), (R * 1.05, L + 0.04), (R * 0.85, L + 0.035), (0, L + 0.02)], mat="shell_dark", segs=10)
        p.ring(R * 0.6, 0.004, T((0, 0, L + 0.03)), mat="glow", segs=10)
        return
    pts = _horn_path(p, L, curl) if e != "Industrial" else [Vector((0, 0, L * 0.85)), Vector((0, 0, L * 0.9))]
    top = pts[-1]
    d = (pts[-1] - pts[-2]).normalized()
    R = J(p, {"Primal": 0.025, "Mercantile": 0.055, "Industrial": 0.045, "Steampunk": 0.06, "Wasteland": 0.07,
              "Ancient": 0.035}[e], 0.15)
    m = T(top) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    if e == "Primal":
        p.lathe([(r * 1.4, 0), (R, 0.04), (R * 0.9, 0.05)], m, mat="bone", segs=7)
    elif e == "Wasteland":  # funnel bell
        p.lathe([(r * 1.4, 0), (R, J(p, 0.09, 0.2)), (R * 1.02, 0.095)], m, mat="paint", segs=8)
    elif e == "Ancient":
        p.lathe([(r * 1.4, 0), (R, 0.05), (R * 0.8, 0.06)], m, mat="stone", segs=6)
        p.ring(R * 0.85, 0.004, m @ T((0, 0, 0.055)), mat="glow", segs=6)
    else:
        p.lathe([(r * 1.4, 0), (R * 0.4, 0.04), (R * 0.8, 0.08), (R, 0.1), (R * 0.95, 0.102)], m, mat=mat, segs=10)


def _hn_joint(p, L, r):
    e = p.era
    if e in ("Primal", "Ancient", "Mercantile", "Steampunk", "Wasteland"):
        pts = _horn_path(p, L, HORN[e][0])
        a, b = pts[1], pts[4]
        mat = {"Primal": "hide", "Ancient": "gold", "Mercantile": "brass", "Steampunk": "copper", "Wasteland": "cloth"}[e]
        line(p, [tuple(a), tuple((a + b) / 2 + Vector((0.03, 0.02, 0))), tuple(b)], r=0.003, mat=mat if e != "Primal" else "hide")
        for q in (a, b):
            p.ball(r * 0.9, T(tuple(q)), mat=mat, segs=(6, 3))
        if e == "Steampunk":  # steam whistle valve
            p.cyl(r * 0.7, r * 0.7, r * 2, T(tuple(pts[2] + Vector((r * 0.6, 0, 0)))) @ M(rot=(0, 90, 0)), mat="copper", segs=6)
            p.ball(r * 0.4, T(tuple(pts[2] + Vector((r * 2.6, 0, 0)))), mat="glow", segs=(5, 3))
    elif e == "Agrarian":  # cord through a drilled hole
        line(p, [(0, 0, L * 0.3), (r * 4, 0.01, L * 0.5), (0, 0, L * 0.7)], r=0.002, mat="rope")
    elif e == "Industrial":  # tasselled cord
        line(p, [(0, 0, L * 0.5), (0.03, 0.01, L * 0.35), (0, -0.1, L * 0.3)], r=0.002, mat="paint")
        p.lathe([(0, 0), (0.008, 0.004), (0.01, 0.03), (0, 0.035)], T((0, -0.1, L * 0.27)), mat="paint", segs=6)
    else:  # Future: trigger stud
        p.box((r * 0.8, r * 1.2, r * J(p, 1.6, 0.3)), T((0, -r * 1.6, L * 0.3)), mat="shell_dark", bevel=0)


def _hn_butt(p, L, r):
    e = p.era
    if e in ("Agrarian", "Primal"):
        p.lathe([(0, -0.004), (r * 0.7, 0), (r * 0.6, 0.01)], mat="bone", segs=6)
    elif e == "Future":
        p.ball(r * 0.9, M(scale=(1, 1, 0.6)), mat="shell_dark", segs=(6, 4))
    else:  # cup mouthpiece
        p.lathe([(r * 0.5, 0.01), (r * 0.5, -0.01), (r * 1.0, -0.02), (r * 0.9, -0.022)], mat="steel" if e == "Wasteland" else "brass" if e != "Ancient" else "stone_dark", segs=7)


function("Horn", "Hafted", HAFTED, "carried")(hafted(
    {"Primal": 0.3, "Agrarian": 0.24, "Mercantile": 0.7, "Industrial": 0.32, "Steampunk": 0.36, "Future": 0.18,
     "Wasteland": 0.38, "Ancient": 0.4}, 0.012, _hn_haft, _hn_head, _hn_joint, _hn_butt))
