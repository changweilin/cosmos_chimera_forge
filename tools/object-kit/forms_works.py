"""Machine family, works and field set (機械: 底座、主機構、傳動、動力源、外露管線／飾): Press, WindPump, Crane,
PrintingPress, Generator, SewingMachine, Drill (cosmos_chimera P1-19, ADR-0016).

Same slots and frame as forms_machine: floor contact at z = 0, front faces -Y, metres. base (底座: frame, plinth,
tower legs), mechanism (主機構: the working part — vat, wheel, jib, platen, stator, needle head, bit), drive (傳動:
screws, beams, gears, cables, belts), power (動力源: the era's energy — muscle, water, wind, motor, boiler, coil
core, rune core), trim (外露管線／飾: pipes, gauges, buckets, sacks, paper stacks, ropes).
WindPump and Crane are the roadside field machines of P3-17 (settlement-structures.md#交通工具); they stand about
3–5 m tall, like the field-specimen meshes they replace. The rest are workshop pieces about 1–2 m.
Glow follows the game rule for machines: form-era glow only (Steampunk, Future, Wasteland, Ancient); a generator's
bonfire uses the lamp flame colour like the forge does.
Every form draws its frame factors first (W, D, H by F), in a fixed order, so beams, belts and pipes meet.
"""
import math

from mathutils import Matrix

from forms_furniture import flagstone, gear, rock, runes, wheel
from forms_machine import (beam, belt, boiler, brick, coilcore, fire, flue, gauge, logs, motor, patch, sheet,
                           shell_box, wire, xcyl, xwheel)
from forms_tools import disk, rod
from kit_forms import F, J, function
from kit_lib import M

MACH = ("base", "mechanism", "drive", "power", "trim")
T = Matrix.Translation
TAU = math.tau


def legs4(p, W, D, z, s, mat="wood"):
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box((s, s, z), T((sx * (W / 2 - s / 2), sy * (D / 2 - s / 2), z / 2)), mat=mat, bevel=0)


def papers(p, x, y, z, w, d, n=3, mat="bone"):
    for i in range(n):
        p.box((w, d, 0.004), M(loc=(x, y, z + i * 0.005), rot=(0, 0, p.rng.uniform(-6, 6))), mat=mat, bevel=0)


def dispatch(table):
    def form(p, slot):
        fn, w, d, h = table[p.era]
        fn(p, slot, w * F(p, 1, 0.08), d * F(p, 1, 0.08), h * F(p, 1, 0.06))
    return form


# ================================================================ Press
def _press_primal(p, s, W, D, H):  # treading trough: hollow log vat with a spout
    if s == "base":
        flagstone(p, W * 1.1, D * 1.2, 0.03, 0, n=8, rough=0.2)
    elif s == "mechanism":
        p.box((W, D, H), T((0, 0, 0.03 + H / 2)), mat="wood", bevel=0.05, noise=0.02)
        p.box((W * 0.9, D * 0.8, 0.02), T((0, 0, 0.03 + H - 0.01)), mat="paint", bevel=0)
    elif s == "drive":
        p.box((0.08, 0.2, 0.04), M(loc=(W / 2 + 0.06, 0, 0.1), rot=(0, 15, 0)), mat="wood", bevel=0)
    elif s == "power":  # treading pole to hold on to
        for sx in (-1, 1):
            p.tube([(sx * W * 0.45, D * 0.5, 0), (sx * W * 0.45, D * 0.5, H + 0.9)], 0.03, mat="wood", segs=5)
        p.tube([(-W * 0.5, D * 0.5, H + J(p, 0.85, 0.05)), (W * 0.5, D * 0.5, H + 0.85)], 0.025, mat="wood", segs=5)
    else:
        p.lathe([(0, 0), (0.12, 0), (0.16, 0.18), (0.14, 0.2)], T((W / 2 + 0.2, 0, 0)), mat="ceramic", segs=8)
        p.ball(1.0, M(loc=(-W * 0.6, -D * 0.4, 0.1), scale=(0.2, 0.15, 0.1)), mat="paint", segs=(6, 4), noise=0.05)


def _press_lever(p, s, W, D, H, mat="wood"):  # lever press: post, long beam, weight stone
    if s == "base":
        p.box((W, D, 0.12), T((0, 0, 0.06)), mat="stone", bevel=0.05)
        p.box((0.15, 0.15, H), T((-W / 2 + 0.1, 0, H / 2)), mat=mat, bevel=0)
    elif s == "mechanism":
        p.cyl(D * 0.35, D * 0.35, 0.35, T((0, 0, 0.12)), mat=mat, segs=10)
        for z in (0.18, 0.4):
            p.ring(D * 0.36, 0.01, T((0, 0, z)), mat="iron", segs=10)
    elif s == "drive":
        beam(p, (-W / 2 + 0.1, 0, H * 0.75), (W / 2 + 0.6, 0, J(p, 0.55, 0.15)), 0.1, mat=mat, bevel=0)
    elif s == "power":
        rock(p, 0.2, 0.18, 0.2, (W / 2 + 0.55, 0, 0.2))
        p.tube([(W / 2 + 0.55, 0, 0.35), (W / 2 + 0.55, 0, 0.55)], 0.01, mat="rope", segs=4)
    else:
        p.cyl(0.12, 0.14, 0.2, T((D * 0.5, -D * 0.5, 0)), mat="wood", segs=8)


def _press_screw(p, s, W, D, H):  # screw press: twin uprights, wooden screw, cross bar
    if s == "base":
        p.box((W, D, 0.15), T((0, 0, 0.075)), mat="wood_dark", bevel=0.04)
        for sx in (-1, 1):
            p.box((0.14, 0.14, H), T((sx * W * 0.4, 0, H / 2)), mat="wood_dark", bevel=0)
        p.box((W, 0.16, 0.16), T((0, 0, H)), mat="wood_dark", bevel=0)
    elif s == "mechanism":
        p.cyl(D * 0.35, D * 0.35, 0.3, T((0, 0, 0.15)), mat="wood", segs=10)
        p.cyl(D * 0.33, D * 0.33, 0.06, T((0, 0, 0.5)), mat="wood_dark", segs=10)
    elif s == "drive":
        p.cyl(0.05, 0.05, H - 0.56, T((0, 0, 0.56)), mat="wood", segs=8)
        p.tube([(0.055 * math.cos(a), 0.055 * math.sin(a), 0.6 + a * 0.02) for a in [i * 0.8 for i in range(int((H - 0.7) / 0.016))]], 0.008, mat="wood_dark", segs=3)
    elif s == "power":
        rod(p, (-0.45, 0, H * J(p, 0.62, 0.08)), (0.45, 0, H * 0.62), 0.025, mat="wood", segs=6)
    else:
        p.cyl(0.14, 0.12, 0.25, T((W * 0.6, -D * 0.4, 0)), mat="brass", segs=8)


def _press_industrial(p, s, W, D, H):  # cast-iron frame press with a handwheel
    if s == "base":
        p.box((W, D, 0.12), T((0, 0, 0.06)), mat="iron", bevel=0)
        for sx in (-1, 1):
            p.box((0.1, D * 0.6, H), T((sx * W * 0.4, 0, H / 2)), mat="paint", bevel=0)
        p.box((W, D * 0.6, 0.14), T((0, 0, H)), mat="paint", bevel=0)
    elif s == "mechanism":
        p.cyl(D * 0.38, D * 0.38, 0.35, T((0, 0, 0.12)), mat="steel", segs=12)
        for i in range(8):
            a = i * TAU / 8
            p.box((0.015, 0.015, 0.3), T((math.cos(a) * D * 0.39, math.sin(a) * D * 0.39, 0.3)), mat="iron", bevel=0)
    elif s == "drive":
        p.cyl(0.04, 0.04, H - 0.5, T((0, 0, 0.5)), mat="steel", segs=8)
        p.cyl(D * 0.34, D * 0.34, 0.05, T((0, 0, 0.5)), mat="steel", segs=10)
    elif s == "power":
        p.ring(J(p, 0.3, 0.1), 0.02, T((0, 0, H + 0.12)), mat="iron", segs=12)
        for i in range(2):
            p.box((0.6, 0.02, 0.02), T((0, 0, H + 0.12)) @ M(rot=(0, 0, i * 90)), mat="iron", bevel=0)
    else:
        p.box((0.15, 0.3, 0.04), M(loc=(0, -D * 0.5 - 0.1, 0.12), rot=(-20, 0, 0)), mat="steel", bevel=0)
        p.cyl(0.13, 0.13, 0.3, T((0, -D * 0.5 - 0.3, 0)), mat="steel", segs=8)


def _press_steampunk(p, s, W, D, H):  # hydraulic press: brass ram, boiler at the side
    if s == "base":
        p.box((W, D, 0.15), T((0, 0, 0.075)), mat="iron", bevel=0.05)
        for sx in (-1, 1):
            p.cyl(0.06, 0.06, H, T((sx * W * 0.38, 0, 0)), mat="brass", segs=8)
        p.box((W, D * 0.5, 0.16), T((0, 0, H)), mat="iron", bevel=0.05)
    elif s == "mechanism":
        p.cyl(D * 0.35, D * 0.35, 0.3, T((0, 0, 0.15)), mat="copper", segs=12)
        p.band(D * 0.35, 0.3, h=0.05)
    elif s == "drive":
        p.cyl(0.11, 0.11, H - 0.55, T((0, 0, 0.55)), mat="steel", segs=10)
        p.cyl(D * 0.33, D * 0.33, 0.06, T((0, 0, 0.5)), mat="brass", segs=12)
    elif s == "power":
        boiler(p, W / 2 + 0.3, 0, 0, J(p, 0.2, 0.08), H * 0.6)
    else:
        p.tube([(W / 2 + 0.3, 0, H * 0.6 + 0.3), (W / 2 + 0.3, 0, H + 0.1), (0, 0, H + 0.1)], 0.02, mat="copper", segs=6)
        gauge(p, W * 0.38, -0.07, H * 0.7, 0.06)


def _press_future(p, s, W, D, H):  # centrifugal extractor: drum pod on a plinth
    if s == "base":
        shell_box(p, W, D, 0.15, (0, 0, 0), mat="shell_dark", bevel=0.2)
    elif s == "mechanism":
        p.lathe([(0, 0.15), (D * 0.45, 0.15), (D * 0.5, H * 0.5), (D * 0.4, H * 0.9), (0, H * 0.95)], mat="body", segs=14)
    elif s == "drive":
        p.ring(D * 0.5, 0.012, T((0, 0, H * J(p, 0.5, 0.1))), mat="glow", segs=14)
        p.box((D * 0.4, 0.01, H * 0.3), T((0, -D * 0.48, H * 0.5)), mat="glass", bevel=0)
    elif s == "power":
        coilcore(p, W / 2 + 0.15, 0, 0.15, 0.1, H * 0.6)
    else:
        p.cyl(0.08, 0.08, 0.35, T((-W / 2 - 0.15, -D * 0.2, 0)), mat="glass", segs=10)
        p.tube([(-D * 0.4, 0, 0.3), (-W / 2 - 0.15, -D * 0.2, 0.35)], 0.015, mat="shell_dark", segs=6)


def _press_wasteland(p, s, W, D, H):  # car-jack press on a drum
    if s == "base":
        for sx in (-1, 1):
            p.box((0.08, 0.08, H), T((sx * W * 0.4, 0, H / 2)), mat="rust", bevel=0)
        p.box((W, 0.12, 0.1), T((0, 0, H)), mat="rust", bevel=0)
    elif s == "mechanism":
        p.cyl(D * 0.4, D * 0.4, 0.5, mat="paint", segs=10)
        patch(p, 0.2, 0.15, T((0, -D * 0.41, 0.3)), mat="steel")
    elif s == "drive":
        p.box((0.2, 0.15, 0.12), T((0, 0, 0.56)), mat="steel", bevel=0)
        p.cyl(0.03, 0.03, H - 0.65, T((0, 0, 0.62)), mat="steel", segs=6)
    elif s == "power":
        p.tube([(0.1, 0, 0.6), (0.5, -0.1, J(p, 0.75, 0.15))], 0.015, mat="steel", segs=5)
        p.cyl(0.02, 0.02, 0.12, T((0.5, -0.1, 0.75)) @ M(rot=(0, 90, 0)), mat="cloth", segs=6)
    else:
        wire(p, -W * 0.4, 0, H * 0.7, 0.05)
        p.cyl(0.12, 0.12, 0.3, T((W * 0.6, -D * 0.3, 0)), mat="rust", segs=8)


def _press_ancient(p, s, W, D, H):
    if s == "base":
        p.box((W, D, 0.2), T((0, 0, 0.1)), mat="stone", bevel=0.1)
        for sx in (-1, 1):
            p.box((0.18, 0.25, H), T((sx * W * 0.4, 0, H / 2)), mat="stone", bevel=0.1)
    elif s == "mechanism":
        p.cyl(D * 0.35, D * 0.33, 0.3, T((0, 0, 0.2)), mat="stone_dark", segs=8)
    elif s == "drive":
        p.box((W * 0.7, 0.2, 0.18), T((0, 0, H * J(p, 0.7, 0.08))), mat="stone", bevel=0.15)
    elif s == "power":
        p.ball(0.08, T((0, 0, H * 0.85)), mat="glow", segs=(8, 5))
    else:
        for sx in (-1, 1):
            runes(p, sx * W * 0.4, -0.13, 0.3, H * 0.9, n=3, w=0.04)


PRESS = {"Primal": (_press_primal, 1.2, 0.7, 0.35), "Agrarian": (_press_lever, 1.3, 0.6, 1.6),
         "Mercantile": (_press_screw, 1.0, 0.7, 1.7), "Industrial": (_press_industrial, 0.9, 0.7, 1.4),
         "Steampunk": (_press_steampunk, 0.9, 0.7, 1.5), "Future": (_press_future, 0.9, 0.8, 1.3),
         "Wasteland": (_press_wasteland, 0.9, 0.6, 1.3), "Ancient": (_press_ancient, 1.1, 0.7, 1.6)}
function("Press", "Machine", MACH, "machine")(dispatch(PRESS))


# ================================================================ WindPump (field machine, 3–5 m)
def _wp_primal(p, s, W, D, H):  # shadoof: pivoting pole on a post, bucket and counterweight
    if s == "base":
        flagstone(p, W * 0.8, D * 0.8, 0.05, 0, n=7, rough=0.2)
        p.tube([(0, 0, 0), (0.03, 0, H * 0.5), (0, 0, H * 0.6)], 0.08, mat="wood", segs=6)
        for s2 in (-1, 1):
            p.tube([(0, 0, H * 0.55), (s2 * 0.12, 0, H * 0.66)], 0.04, mat="wood", segs=5)
    elif s == "mechanism":  # well ring
        p.ring(0.5, 0.12, T((W * 0.45, 0, 0.12)), mat="stone", segs=10, square=False)
    elif s == "drive":
        tilt = J(p, 18, 0.3)
        a = math.radians(tilt)
        L = W * 0.9
        p.tube([(-L * 0.4 * math.cos(a), 0, H * 0.62 + L * 0.4 * math.sin(a)), (L * 0.6 * math.cos(a), 0, H * 0.62 - L * 0.6 * math.sin(a))], 0.04, mat="wood", segs=6)
    elif s == "power":
        rock(p, 0.22, 0.2, 0.18, (-W * 0.36 * 0.95, 0, H * 0.62 + W * 0.36 * 0.3 - 0.15))
    else:
        x = W * 0.54 * 0.95
        p.tube([(x, 0, H * 0.62 - W * 0.54 * 0.3), (x, 0, 0.5)], 0.008, mat="rope", segs=3)
        p.lathe([(0, 0), (0.1, 0.01), (0.14, 0.2), (0.12, 0.22)], T((x, 0, 0.3)), mat="hide", segs=8)


def _wp_agrarian(p, s, W, D, H):  # undershot water wheel with a trough
    R = H * 0.45
    if s == "base":
        for sy in (-1, 1):
            p.box((0.15, 0.15, R + 0.2), T((0, sy * 0.45, (R + 0.2) / 2)), mat="wood", bevel=0)
        p.box((W, 1.2, 0.1), T((0, 0, 0.05)), mat="stone", bevel=0)
    elif s == "mechanism":
        wheel(p, R, (0, 0, R + 0.2), rim="wood", hub="wood", spokes=8, t=0.06)
    elif s == "drive":
        p.cyl(0.06, 0.06, 1.1, T((0, -0.55, R + 0.2)) @ M(rot=(-90, 0, 0)), mat="wood_dark", segs=8)
    elif s == "power":  # paddles
        for i in range(8):
            a = i * TAU / 8 + 0.2
            p.box((R * 0.25, 0.3, 0.03), T((math.cos(a) * R * 0.9, 0, R + 0.2 + math.sin(a) * R * 0.9)) @ M(rot=(0, -math.degrees(a), 0)), mat="wood", bevel=0)
    else:
        p.box((W * 0.5, 0.3, 0.1), T((W * 0.5, 0, R * 2 + 0.25)), mat="wood", bevel=0)
        for i in range(4):
            p.cyl(0.07, 0.08, 0.15, T((math.cos(i * 1.57) * R, 0.1, R + 0.2 + math.sin(i * 1.57) * R)), mat="wood", segs=6)


def _wp_mercantile(p, s, W, D, H):  # post windmill: tapered tower, four cloth sails
    zh = H * 0.8
    if s == "base":
        p.lathe([(W * 0.4, 0), (W * 0.32, zh * 0.8), (W * 0.25, zh)], mat="stone", segs=8)
    elif s == "mechanism":  # cap
        p.lathe([(W * 0.3, zh), (W * 0.32, zh + 0.1), (W * 0.15, zh + 0.6), (0, zh + 0.7)], mat="wood_dark", segs=8)
    elif s == "drive":
        p.cyl(0.08, 0.06, 0.5, T((0, -W * 0.3, zh + 0.3)) @ M(rot=(90, 0, 0)), mat="wood", segs=8)
    elif s == "power":  # sails
        Ls = J(p, H * 0.4, 0.06)
        for i in range(4):
            a = i * 90 + 45
            m = T((0, -W * 0.3 - 0.5, zh + 0.3)) @ M(rot=(0, a, 0))
            p.box((0.06, 0.06, Ls), m @ T((0, 0, Ls / 2)), mat="wood", bevel=0)
            p.box((Ls * 0.25, 0.02, Ls * 0.8), m @ T((Ls * 0.14, 0.03, Ls * 0.55)), mat="cloth", bevel=0)
    else:
        p.box((0.8, 0.4, 0.05), T((0, -W * 0.45, 0.6)), mat="wood", bevel=0)
        p.box((0.4, 0.02, 0.8), T((0, -W * 0.39, 0.4)), mat="wood_dark", bevel=0)


def _wp_industrial(p, s, W, D, H):  # steel lattice windpump with a multi-blade rotor and tail vane
    zh = H * 0.85
    if s == "base":
        for sx in (-1, 1):
            for sy in (-1, 1):
                rod(p, (sx * W * 0.4, sy * W * 0.4, 0), (sx * 0.1, sy * 0.1, zh), 0.03, mat="steel", segs=4)
        for k in (0.3, 0.6):
            r = W * 0.4 * (1 - k) + 0.1 * k
            for i in range(4):
                a = i * TAU / 4 + TAU / 8
                b = a + TAU / 4
                rod(p, (math.cos(a) * r * 1.41, math.sin(a) * r * 1.41, zh * k), (math.cos(b) * r * 1.41, math.sin(b) * r * 1.41, zh * k), 0.015, mat="steel", segs=4)
    elif s == "mechanism":  # rotor
        c = (0, -0.3, zh + 0.1)
        R = J(p, H * 0.18, 0.08)
        p.ring(R, 0.02, T(c) @ M(rot=(90, 0, 0)), mat="steel", segs=14)
        for i in range(12):
            a = i * 30
            p.box((0.1, 0.01, R), T(c) @ M(rot=(0, a, 0)) @ T((0, 0, R / 2)) @ M(rot=(0, 0, 25)), mat="paint", bevel=0)
    elif s == "drive":
        p.box((0.2, 0.7, 0.2), T((0, 0.05, zh + 0.1)), mat="iron", bevel=0)
        p.cyl(0.02, 0.02, zh, mat="steel", segs=6)
    elif s == "power":  # tail vane
        p.box((0.04, 1.2, 0.04), T((0, 0.9, zh + 0.1)), mat="steel", bevel=0)
        p.box((0.02, 0.6, 0.5), T((0, 1.5, zh + 0.15)), mat="paint", bevel=0)
    else:
        p.cyl(0.6, 0.6, 0.5, T((W * 0.9, 0, 0)), mat="iron", segs=12)
        p.tube([(0, 0, 0.3), (W * 0.9, 0, 0.6)], 0.03, mat="steel", segs=6)


def _wp_steampunk(p, s, W, D, H):  # steam pumping engine: beam engine on a brick house
    if s == "base":
        brick(p, W, D, H * 0.35, (0, 0, 0), mat="ceramic", n=3)
    elif s == "mechanism":  # walking beam
        z = H * 0.35 + J(p, 0.9, 0.08)
        p.box((0.15, 0.15, 0.9), T((0, 0, H * 0.35 + 0.45)), mat="iron", bevel=0)
        p.box((W * 1.2, 0.12, 0.15), M(loc=(0, 0, z), rot=(0, 8, 0)), mat="brass", bevel=0)
    elif s == "drive":
        p.cyl(0.08, 0.08, H * 0.35 + 0.7, T((W * 0.55, -D * 0.55, 0)), mat="steel", segs=8)
        p.cyl(0.3, 0.3, 0.6, T((W * 0.55, -D * 0.55, 0)), mat="iron", segs=10)
    elif s == "power":
        boiler(p, -W * 0.3, 0, H * 0.35, J(p, 0.35, 0.08), H * 0.3)
    else:
        flue(p, -W * 0.3, D * 0.3, H * 0.35, H, 0.1, mat="iron")
        p.ball(0.06, T((-W * 0.3, D * 0.3, H + 0.1)), mat="glow", segs=(6, 4))
        p.tube([(W * 0.55, -D * 0.55, 0.4), (W * 0.9, -D * 0.55, 0.3), (W * 0.95, -D * 0.2, 0.25)], 0.04, mat="copper", segs=6)


def _wp_future(p, s, W, D, H):  # turbine water-collecting tower: tapered shell, ducted turbine
    if s == "base":
        p.lathe([(0, 0), (W * 0.45, 0), (W * 0.42, 0.2), (W * 0.2, H * 0.4), (W * 0.15, H * 0.75)], mat="body", segs=14)
    elif s == "mechanism":
        c = (0, -0.1, H * 0.85)
        R = J(p, H * 0.15, 0.08)
        p.ring(R, 0.06, T(c) @ M(rot=(90, 0, 0)), mat="shell_dark", segs=14, square=False)
        for i in range(3):
            p.box((0.06, 0.02, R * 0.95), T(c) @ M(rot=(0, i * 120, 0)) @ T((0, 0, R * 0.47)), mat="body", bevel=0)
    elif s == "drive":
        p.ball(0.15, T((0, -0.1, H * 0.85)), mat="body", segs=(10, 6))
        p.cyl(0.1, 0.1, H * 0.1, T((0, 0, H * 0.75)), mat="shell_dark", segs=10)
    elif s == "power":
        for i in range(3):
            p.ring(W * 0.2 - i * 0.02, 0.01, T((0, 0, H * (0.45 + i * 0.1))), mat="glow", segs=12)
    else:
        p.cyl(W * 0.35, W * 0.35, 0.6, T((W * 0.7, 0, 0)), mat="glass", segs=12)
        p.ring(W * 0.36, 0.015, T((W * 0.7, 0, 0.6)), mat="shell_dark", segs=12)


def _wp_wasteland(p, s, W, D, H):  # scrap windpump: pipe mast, oil-drum rotor, tyre counterweights
    if s == "base":
        for i in range(3):
            a = i * TAU / 3
            rod(p, (math.cos(a) * W * 0.4, math.sin(a) * W * 0.4, 0), (0, 0, H * 0.8), 0.05, mat="rust", segs=6)
    elif s == "mechanism":  # split-drum rotor (savonius)
        for sgn in (-1, 1):
            p.cyl(0.3, 0.3, J(p, 0.9, 0.1), T((sgn * 0.15, sgn * 0.08, H * 0.8)), mat="paint", segs=8)
    elif s == "drive":
        p.cyl(0.03, 0.03, H * 0.8 + 1.0, mat="steel", segs=6)
    elif s == "power":
        p.ring(0.35, 0.12, T((0, 0, 0.12)), mat="rubber", segs=10, square=False)
    else:
        p.cyl(0.35, 0.35, 0.8, T((W * 0.7, 0, 0)), mat="rust", segs=10)
        p.tube([(0, 0, 0.5), (W * 0.7, 0, 0.75)], 0.03, mat="rubber", segs=5)
        wire(p, 0, 0, H * 0.5, 0.06)


def _wp_ancient(p, s, W, D, H):  # rune spire drawing water up through a glowing channel
    if s == "base":
        p.lathe([(W * 0.45, 0), (W * 0.4, 0.4), (W * 0.2, 0.6), (W * 0.15, H * 0.9), (0, H)], mat="stone", segs=6)
    elif s == "mechanism":
        p.ring(W * 0.3, 0.08, T((0, 0, H * J(p, 0.7, 0.08))), mat="stone_dark", segs=6)
    elif s == "drive":
        p.box((0.06, 0.02, H * 0.6), T((0, -W * 0.17, H * 0.45)), mat="glow", bevel=0)
    elif s == "power":
        p.ball(0.18, T((0, 0, H + 0.2)), mat="glow", segs=(8, 5))
    else:
        p.cyl(0.5, 0.5, 0.3, T((W * 0.8, 0, 0)), mat="stone", segs=6)
        p.ring(0.48, 0.02, T((W * 0.8, 0, 0.3)), mat="glow", segs=6)


WINDPUMP = {"Primal": (_wp_primal, 3.2, 1.0, 2.6), "Agrarian": (_wp_agrarian, 2.6, 1.2, 3.6),
            "Mercantile": (_wp_mercantile, 2.2, 2.2, 5.0), "Industrial": (_wp_industrial, 2.0, 2.0, 5.0),
            "Steampunk": (_wp_steampunk, 2.0, 1.6, 4.0), "Future": (_wp_future, 2.0, 2.0, 5.0),
            "Wasteland": (_wp_wasteland, 2.0, 2.0, 4.2), "Ancient": (_wp_ancient, 1.8, 1.8, 4.5)}
function("WindPump", "Machine", MACH, "machine")(dispatch(WINDPUMP))


# ================================================================ Crane (field machine)
def _cr_primal(p, s, W, D, H):  # tripod of poles with a rope and a net load
    top = (0, 0, H)
    if s == "base":
        for i in range(3):
            a = i * TAU / 3 + 0.3
            p.tube([(math.cos(a) * W * 0.5, math.sin(a) * W * 0.5, 0), top], 0.05, mat="wood", segs=6)
    elif s == "mechanism":
        p.band(0.08, H - 0.1, h=0.15)
    elif s == "drive":
        p.tube([top, (0, 0, H * 0.4)], 0.012, mat="rope", segs=3)
        p.tube([top, (W * 0.5, -0.1, 0.3)], 0.012, mat="rope", segs=3)
    elif s == "power":
        p.ball(1.0, M(loc=(0, 0, H * 0.4 - 0.25), scale=(0.3, 0.3, J(p, 0.28, 0.1))), mat="rope", segs=(8, 5), noise=0.05)
    else:
        rock(p, 0.15, 0.12, 0.12, (W * 0.5, -0.1, 0.12))


def _cr_lever(p, s, W, D, H):  # lever crane: post with a pivoting boom and a stone counterweight box
    if s == "base":
        p.box((0.25, 0.25, H * 0.7), T((0, 0, H * 0.35)), mat="wood", bevel=0)
        for i in range(4):
            a = i * TAU / 4
            beam(p, (math.cos(a) * 0.7, math.sin(a) * 0.7, 0), (math.cos(a) * 0.1, math.sin(a) * 0.1, H * 0.3), 0.08, mat="wood", bevel=0)
    elif s == "mechanism":
        beam(p, (-W * 0.35, 0, H * 0.6), (W * 0.65, 0, H * J(p, 0.95, 0.05)), 0.12, mat="wood", bevel=0)
    elif s == "drive":
        p.tube([(W * 0.65, 0, H * 0.95), (W * 0.65, 0, H * 0.35)], 0.012, mat="rope", segs=3)
    elif s == "power":
        p.box((0.4, 0.4, 0.35), T((-W * 0.35, 0, H * 0.6 - 0.2)), mat="wood_dark", bevel=0)
    else:
        p.box((0.5, 0.4, 0.35), T((W * 0.65, 0, H * 0.35 - 0.2)), mat="wood", bevel=0)


def _cr_treadwheel(p, s, W, D, H):  # treadwheel crane: big wheel, A-frame, jib
    R = H * 0.3
    if s == "base":
        for sy in (-1, 1):
            beam(p, (-W * 0.3, sy * 0.5, 0), (0, sy * 0.3, H * 0.8), 0.15, mat="wood_dark", bevel=0)
            beam(p, (W * 0.3, sy * 0.5, 0), (0, sy * 0.3, H * 0.8), 0.15, mat="wood_dark", bevel=0)
        p.box((W * 0.8, 1.2, 0.15), T((0, 0, 0.075)), mat="wood_dark", bevel=0)
    elif s == "mechanism":
        beam(p, (0, 0, H * 0.8), (W * 0.7, 0, H * J(p, 1.0, 0.05)), 0.15, mat="wood", bevel=0)
    elif s == "drive":
        p.tube([(W * 0.7, 0, H), (W * 0.7, 0, H * 0.3), (W * 0.7 - 0.02, 0, H * 0.25)], 0.015, mat="rope", segs=3)
        p.tube([(0, 0, H * 0.8), (-W * 0.25, 0.6, R + 0.2)], 0.015, mat="rope", segs=3)
    elif s == "power":
        m = T((-W * 0.25, 0.8, R + 0.15)) @ M(rot=(90, 0, 0))
        p.ring(R, 0.06, m, mat="wood", segs=14)
        p.ring(R, 0.06, m @ T((0, 0, 0.6)), mat="wood", segs=14)
        for i in range(6):
            a = i * TAU / 6
            p.box((0.06, 0.6, 0.06), T((-W * 0.25 + math.cos(a) * R, 0.5, R + 0.15 + math.sin(a) * R)), mat="wood", bevel=0)
    else:
        p.box((0.6, 0.5, 0.4), T((W * 0.7, 0, H * 0.25 - 0.2)), mat="wood", bevel=0)
        p.box((0.5, 0.45, 0.04), T((W * 0.7, 0, H * 0.25)), mat="iron", bevel=0)


def _cr_industrial(p, s, W, D, H):  # steel jib crane on a mast with a winch house
    if s == "base":
        p.box((1.0, 1.0, 0.2), T((0, 0, 0.1)), mat="stone", bevel=0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                p.box((0.06, 0.06, H), T((sx * 0.2, sy * 0.2, H / 2)), mat="paint", bevel=0)
        for k in range(1, 5):
            p.box((0.46, 0.46, 0.03), T((0, 0, H * k / 5)), mat="paint", bevel=0)
    elif s == "mechanism":
        L = W * J(p, 0.9, 0.05)
        beam(p, (-0.5, 0, H), (L, 0, H + 0.1), 0.18, mat="paint", bevel=0)
        for i in range(5):
            x = -0.3 + i * (L + 0.3) / 5
            p.box((0.03, 0.2, 0.2), M(loc=(x, 0, H + 0.05), rot=(0, 45, 0)), mat="paint", bevel=0)
    elif s == "drive":
        p.tube([(W * 0.85, 0, H), (W * 0.85, 0, H * 0.3)], 0.01, mat="steel", segs=3)
        p.tube([(0, 0, H + 0.5), (W * 0.85, 0, H + 0.1)], 0.008, mat="steel", segs=3)
        p.cyl(0.03, 0.03, 0.5, T((0, 0, H)), mat="steel", segs=6)
    elif s == "power":
        p.box((0.5, 0.4, 0.4), T((-0.55, 0, H + 0.2)), mat="iron", bevel=0)
        p.box((0.4, 0.4, 0.3), T((0.0, -0.5, 0.35)), mat="paint", bevel=0)
    else:
        p.lathe([(0, 0), (0.06, 0.02), (0.05, 0.08), (0.02, 0.1)], T((W * 0.85, 0, H * 0.3 - 0.1)), mat="steel", segs=8)
        p.tube([(W * 0.85, 0, H * 0.3 - 0.1), (W * 0.85 + 0.04, 0, H * 0.3 - 0.18), (W * 0.85, 0, H * 0.3 - 0.22)], 0.012, mat="iron", segs=4)


def _cr_steampunk(p, s, W, D, H):  # steam derrick: boom on a slewing boiler car
    if s == "base":
        p.box((1.4, 1.0, 0.3), T((0, 0, 0.35)), mat="iron", bevel=0.05)
        for sx in (-1, 1):
            for sy in (-1, 1):
                xwheel(p, 0.2, (sx * 0.5, sy * 0.52, 0.2), rim="iron", hub="iron", spokes=4, t=0.04)
    elif s == "mechanism":
        L = W * J(p, 1.0, 0.05)
        a = math.radians(40)
        for sy in (-1, 1):
            rod(p, (0.3, sy * 0.15, 0.6), (0.3 + L * math.cos(a), 0, 0.6 + L * math.sin(a)), 0.05, mat="brass", segs=6)
    elif s == "drive":
        a = math.radians(40)
        L = W
        tip = (0.3 + L * math.cos(a), 0, 0.6 + L * math.sin(a))
        p.tube([(-0.3, 0, 1.4), tip], 0.012, mat="steel", segs=3)
        p.tube([tip, (tip[0], 0, 0.6)], 0.012, mat="steel", segs=3)
        xcyl(p, 0.15, 0.4, (-0.3, 0, 0.9), mat="copper", segs=10)
    elif s == "power":
        boiler(p, -0.4, 0, 0.5, J(p, 0.28, 0.08), H * 0.25)
    else:
        flue(p, -0.4, 0, 0.5 + H * 0.25 + 0.3, 0.5 + H * 0.4, 0.07, mat="iron")
        gauge(p, 0.2, -0.51, 0.45, 0.06)


def _cr_future(p, s, W, D, H):  # anti-gravity lift platform: pylons with a floating deck
    if s == "base":
        for sx in (-1, 1):
            p.lathe([(0, 0), (0.35, 0), (0.3, 0.2), (0.15, 0.35), (0.12, H)], T((sx * W * 0.4, 0, 0)), mat="body", segs=10)
    elif s == "mechanism":
        z = H * J(p, 0.45, 0.15)
        p.box((W * 0.7, 1.2, 0.12), T((0, 0, z)), mat="shell_dark", bevel=0.2)
    elif s == "drive":
        for sx in (-1, 1):
            for k in (0.3, 0.6, 0.9):
                p.ring(0.17, 0.02, T((sx * W * 0.4, 0, H * k)), mat="glow", segs=10)
    elif s == "power":
        for sx in (-1, 1):
            p.ball(0.18, T((sx * W * 0.4, 0, H + 0.1)), mat="glow", segs=(8, 5))
    else:
        p.box((0.5, 0.5, 0.5), T((0.2, 0, H * 0.45 + 0.31)), mat="paint", bevel=0.1)


def _cr_wasteland(p, s, W, D, H):  # scrap boom on a truck chassis, chain hook, engine block
    if s == "base":
        p.box((1.8, 0.9, 0.3), T((0, 0, 0.45)), mat="rust", bevel=0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                p.ring(0.25, 0.1, T((sx * 0.6, sy * 0.5, 0.3)) @ M(rot=(90, 0, 0)), mat="rubber", segs=10, square=False)
    elif s == "mechanism":
        rod(p, (-0.5, 0, 0.6), (W * 0.7, 0, H * J(p, 1.0, 0.05)), 0.07, mat="steel", segs=6)
    elif s == "drive":
        p.tube([(W * 0.7, 0, H), (W * 0.7, 0, H * 0.4)], 0.015, mat="iron", segs=3)
        p.tube([(W * 0.7, 0, H * 0.4), (W * 0.7 + 0.08, 0, H * 0.33), (W * 0.7, 0, H * 0.28)], 0.02, mat="iron", segs=4)
    elif s == "power":
        p.box((0.5, 0.5, 0.4), T((-0.6, 0, 0.8)), mat="iron", bevel=0)
        flue(p, -0.6, 0.15, 1.0, 1.5, 0.05, mat="rust")
    else:
        patch(p, 0.3, 0.2, T((0.3, -0.455, 0.45)), mat="paint")
        wire(p, 0.5, 0, 0.75, 0.08)


def _cr_ancient(p, s, W, D, H):  # stone gantry with a rune lift stone
    if s == "base":
        for sx in (-1, 1):
            p.box((0.4, 0.5, H), T((sx * W * 0.4, 0, H / 2)), mat="stone", bevel=0.1)
    elif s == "mechanism":
        p.box((W + 0.4, 0.5, 0.4), T((0, 0, H + 0.2)), mat="stone", bevel=0.1)
    elif s == "drive":
        p.box((0.06, 0.04, H * 0.4), T((0, -0.2, H * 0.78)), mat="glow", bevel=0)
    elif s == "power":
        p.box((0.6, 0.6, 0.5), M(loc=(0, 0, H * J(p, 0.35, 0.15)), rot=(0, 0, 20)), mat="stone_dark", bevel=0.15)
    else:
        for sx in (-1, 1):
            runes(p, sx * W * 0.4, -0.26, 0.4, H * 0.8, n=3, w=0.08)


CRANE = {"Primal": (_cr_primal, 2.0, 2.0, 2.8), "Agrarian": (_cr_lever, 3.0, 1.0, 3.2),
         "Mercantile": (_cr_treadwheel, 3.2, 1.6, 4.2), "Industrial": (_cr_industrial, 3.2, 1.2, 4.2),
         "Steampunk": (_cr_steampunk, 3.0, 1.2, 3.6), "Future": (_cr_future, 3.0, 1.4, 3.6),
         "Wasteland": (_cr_wasteland, 3.0, 1.2, 3.4), "Ancient": (_cr_ancient, 3.0, 1.2, 3.6)}
function("Crane", "Machine", MACH, "machine")(dispatch(CRANE))


# ================================================================ PrintingPress
def _pp_primal(p, s, W, D, H):  # rubbing stone: carved slab, hide sheet, ochre pad
    if s == "base":
        flagstone(p, W, D, 0.12, 0, n=8, rough=0.15)
    elif s == "mechanism":
        p.box((W * 0.6, D * 0.6, 0.004), M(loc=(0, 0, 0.123), rot=(0, 0, J(p, 6, 1))), mat="hide", bevel=0)
    elif s == "drive":
        for i in range(4):
            p.box((W * 0.4, 0.01, 0.004), T((0, -D * 0.2 + i * D * 0.13, 0.126)), mat="ceramic", bevel=0)
    elif s == "power":
        p.ball(1.0, M(loc=(W * 0.45, -D * 0.4, 0.06), scale=(0.07, 0.07, 0.05)), mat="ceramic", segs=(6, 4), noise=0.05)
    else:
        p.ball(1.0, M(loc=(-W * 0.6, 0, 0.04), scale=(0.1, 0.08, 0.04)), mat="stone_dark", segs=(6, 4))


def _pp_agrarian(p, s, W, D, H):  # woodblock table
    if s == "base":
        p.box((W, D, 0.05), T((0, 0, H - 0.025)), mat="wood", bevel=0)
        legs4(p, W, D, H - 0.05, 0.06, mat="wood")
    elif s == "mechanism":
        p.box((W * 0.35, D * 0.5, 0.04), T((-W * 0.15, 0, H + 0.02)), mat="wood_dark", bevel=0)
    elif s == "drive":
        papers(p, W * 0.25, 0, H, W * 0.3, D * 0.4, n=p.rng.randint(2, 4))
    elif s == "power":
        p.lathe([(0, 0), (0.06, 0.01), (0.05, 0.04), (0.015, 0.05), (0.015, 0.14)], T((-W * 0.4, D * 0.3, H)), mat="hide", segs=8)
    else:
        p.cyl(0.06, 0.05, 0.08, T((W * 0.4, D * 0.3, H)), mat="ceramic", segs=8)


def _pp_mercantile(p, s, W, D, H):  # wooden hand press: two cheeks, platen, bar, carriage bed
    if s == "base":
        p.box((W, D * 1.6, 0.1), T((0, 0, 0.75)), mat="wood_dark", bevel=0)
        legs4(p, W, D * 1.6, 0.7, 0.08, mat="wood_dark")
        for sx in (-1, 1):
            p.box((0.14, 0.2, H), T((sx * W * 0.4, 0, H / 2)), mat="wood_dark", bevel=0)
        p.box((W, 0.22, 0.16), T((0, 0, H)), mat="wood_dark", bevel=0)
    elif s == "mechanism":
        p.box((W * 0.6, D * 0.6, 0.06), T((0, 0, 1.05)), mat="wood", bevel=0)
    elif s == "drive":
        p.cyl(0.05, 0.05, H - 1.1, T((0, 0, 1.1)), mat="iron", segs=8)
    elif s == "power":
        rod(p, (0, 0, H * 0.75), (W * 0.6, -0.3, H * J(p, 0.72, 0.05)), 0.02, mat="iron", segs=6)
        p.ball(0.03, T((W * 0.6, -0.3, H * 0.72)), mat="wood", segs=(6, 4))
    else:
        papers(p, 0, -D * 0.55, 0.8, W * 0.5, D * 0.4, n=3)
        p.box((W * 0.5, D * 0.5, 0.04), T((0, D * 0.55, 0.82)), mat="iron", bevel=0)


def _pp_industrial(p, s, W, D, H):  # cylinder press: frame, big drum, flywheel, motor
    zc = H * 0.6
    if s == "base":
        for sx in (-1, 1):
            p.box((0.1, D, zc + 0.2), T((sx * W * 0.45, 0, (zc + 0.2) / 2)), mat="iron", bevel=0)
        p.box((W, D, 0.08), T((0, 0, 0.04)), mat="iron", bevel=0)
    elif s == "mechanism":
        xcyl(p, J(p, 0.25, 0.08), W * 0.85, (0, 0, zc), mat="steel", segs=12)
        p.box((W * 0.85, D * 0.8, 0.05), T((0, 0, zc - 0.3)), mat="steel", bevel=0)
    elif s == "drive":
        xwheel(p, 0.35, (W / 2 + 0.06, 0, zc), rim="iron", hub="iron", spokes=6, t=0.03)
    elif s == "power":
        mc = motor(p, W / 2 + 0.3, D * 0.6, 0, 0.13, 0.32)
        belt(p, (W / 2 + 0.06, 0, zc), 0.1, (W / 2 + 0.06, mc[1], mc[2]), 0.07)
    else:
        papers(p, 0, -D * 0.55, zc - 0.25, W * 0.6, 0.3, n=4)
        p.box((W * 0.7, 0.3, 0.03), M(loc=(0, -D * 0.55, zc - 0.28), rot=(-10, 0, 0)), mat="paint", bevel=0)


def _pp_steampunk(p, s, W, D, H):  # rotary press: two brass drums, paper web, boiler
    if s == "base":
        p.box((W, D, 0.15), T((0, 0, 0.075)), mat="iron", bevel=0.05)
        for sx in (-1, 1):
            p.box((0.08, D * 0.9, H), T((sx * W * 0.45, 0, H / 2)), mat="brass", bevel=0)
    elif s == "mechanism":
        for z in (H * 0.4, H * 0.75):
            xcyl(p, 0.18, W * 0.85, (0, 0, z), mat="copper", segs=12)
    elif s == "drive":
        sheet(p, (-D * 0.5, H * 0.3), (0, H * 0.4 + 0.18), W * 0.75, 0.004, mat="bone")
        sheet(p, (0, H * 0.75 - 0.18), (D * 0.5, H * J(p, 0.95, 0.05)), W * 0.75, 0.004, mat="bone")
        gear(p, 0.15, T((W / 2 + 0.03, 0, H * 0.4)) @ M(rot=(0, 0, 90)), teeth=10, th=0.02)
    elif s == "power":
        boiler(p, -W / 2 - 0.3, 0, 0, J(p, 0.22, 0.08), H * 0.6)
    else:
        p.tube([(-W / 2 - 0.3, 0, H * 0.6 + 0.3), (-W / 2 - 0.3, 0, H + 0.1), (0, 0, H + 0.1)], 0.02, mat="copper", segs=6)
        gauge(p, -W * 0.45, -D * 0.46, H * 0.6, 0.05)


def _pp_future(p, s, W, D, H):  # hologram printer: slab with a projection field
    if s == "base":
        shell_box(p, W, D, H * 0.5, (0, 0, 0), mat="body", bevel=0.2)
    elif s == "mechanism":
        p.box((W * 0.8, D * 0.7, 0.02), T((0, 0, H * 0.5 + 0.01)), mat="glass", bevel=0)
    elif s == "drive":
        p.box((W * 0.6, D * 0.5, H * J(p, 0.35, 0.15)), T((0, 0, H * 0.5 + 0.2)), mat="glow", bevel=0)
    elif s == "power":
        for sx in (-1, 1):
            p.box((0.06, D * 0.7, 0.4), T((sx * W * 0.42, 0, H * 0.5 + 0.2)), mat="shell_dark", bevel=0.2)
    else:
        p.box((W * 0.6, 0.01, 0.02), T((0, -D * 0.5, H * 0.35)), mat="glow", bevel=0)
        papers(p, W * 0.25, -D * 0.25, H * 0.5 + 0.02, 0.2, 0.28, n=2, mat="shell")


def _pp_wasteland(p, s, W, D, H):  # mimeograph on a crate
    if s == "base":
        p.box((W, D, H * 0.6), T((0, 0, H * 0.3)), mat="wood", bevel=0, noise=0.01)
    elif s == "mechanism":
        xcyl(p, 0.14, W * 0.7, (0, 0, H * 0.6 + 0.16), mat="rust", segs=10)
    elif s == "drive":
        p.tube([(W * 0.35, 0, H * 0.6 + 0.16), (W * 0.45, 0, H * 0.6 + 0.16), (W * 0.45, -0.15, H * 0.6 + J(p, 0.05, 0.3))], 0.012, mat="steel", segs=4)
    elif s == "power":
        p.cyl(0.1, 0.1, 0.25, T((-W * 0.6, 0, 0)), mat="paint", segs=8)
    else:
        papers(p, 0, -D * 0.4, H * 0.6, W * 0.4, 0.2, n=3)
        wire(p, -W * 0.3, 0, H * 0.6 + 0.16, 0.15, axis="x")


def _pp_ancient(p, s, W, D, H):  # rune stamp slab
    if s == "base":
        p.box((W, D, H * 0.55), T((0, 0, H * 0.275)), mat="stone", bevel=0.1)
    elif s == "mechanism":
        p.box((W * 0.5, D * 0.5, 0.2), T((0, 0, H * 0.55 + J(p, 0.25, 0.2))), mat="stone_dark", bevel=0.15)
    elif s == "drive":
        p.box((W * 0.4, D * 0.4, 0.004), T((0, 0, H * 0.55 + 0.002)), mat="glow", bevel=0)
    elif s == "power":
        for sx in (-1, 1):
            p.box((0.1, 0.1, 0.5), T((sx * W * 0.35, 0, H * 0.55 + 0.25)), mat="stone", bevel=0.1)
    else:
        runes(p, 0, -D * 0.51, 0.1, H * 0.5, n=3, w=0.06)


PRINT = {"Primal": (_pp_primal, 0.8, 0.6, 0.12), "Agrarian": (_pp_agrarian, 1.0, 0.6, 0.75),
         "Mercantile": (_pp_mercantile, 0.9, 0.7, 1.9), "Industrial": (_pp_industrial, 1.1, 0.9, 1.3),
         "Steampunk": (_pp_steampunk, 1.0, 0.9, 1.5), "Future": (_pp_future, 1.0, 0.7, 1.1),
         "Wasteland": (_pp_wasteland, 0.9, 0.6, 1.0), "Ancient": (_pp_ancient, 1.0, 0.7, 1.0)}
function("PrintingPress", "Machine", MACH, "machine")(dispatch(PRINT))


# ================================================================ Generator
def _gen_primal(p, s, W, D, H):  # bonfire heap: stone ring, logs, fire
    if s == "base":
        for i in range(8):
            a = i * TAU / 8
            rock(p, 0.1, 0.08, 0.07, (math.cos(a) * W * 0.4, math.sin(a) * W * 0.4, 0.05), segs=(5, 4))
    elif s == "mechanism":
        logs(p, 0, 0, 0.0, W * 0.6, 0.05, n=3)
    elif s == "drive":  # leaning sticks
        for i in range(5):
            a = i * TAU / 5
            p.tube([(math.cos(a) * W * 0.3, math.sin(a) * W * 0.3, 0), (0, 0, J(p, 0.5, 0.15))], 0.025, mat="wood", segs=4)
    elif s == "power":
        fire(p, 0, 0, 0.08, 0.12, n=3)
    else:
        logs(p, W * 0.7, 0, 0, 0.5, 0.05, n=2)


def _gen_agrarian(p, s, W, D, H):  # animal treadmill sweep: central post, gear ring, long sweep
    R = W * 0.45
    if s == "base":
        p.cyl(R * 0.3, R * 0.3, 0.15, mat="stone", segs=10)
        p.cyl(0.08, 0.08, H, T((0, 0, 0.15)), mat="wood", segs=8)
    elif s == "mechanism":
        p.ring(R * 0.28, 0.05, T((0, 0, H * 0.5)), mat="wood_dark", segs=12)
        for i in range(12):
            a = i * TAU / 12
            p.box((0.05, 0.05, 0.08), T((math.cos(a) * R * 0.3, math.sin(a) * R * 0.3, H * 0.5 + 0.06)), mat="wood", bevel=0)
    elif s == "drive":
        beam(p, (0, 0, H * 0.8), (R, 0, H * J(p, 0.7, 0.08)), 0.1, mat="wood", bevel=0)
    elif s == "power":  # horizontal shaft out to a work post
        xcyl(p, 0.05, R * 0.8, (-R * 0.5, 0, 0.35), mat="wood", segs=8)
        p.box((0.2, 0.2, 0.5), T((-R * 0.9, 0, 0.25)), mat="wood", bevel=0)
    else:
        p.ring(R, 0.04, T((0, 0, 0.02)), mat="stone_dark", segs=14)


def _gen_mercantile(p, s, W, D, H):  # water wheel with a mill house wall
    R = H * 0.42
    if s == "base":
        p.box((0.3, D, R + 0.4), T((-0.5, 0, (R + 0.4) / 2)), mat="stone", bevel=0)
        p.box((0.2, 0.2, R + 0.2), T((0.6, 0, (R + 0.2) / 2)), mat="wood", bevel=0)
    elif s == "mechanism":
        m = T((0.05, 0, R + 0.2)) @ M(rot=(0, 90, 0))
        p.ring(R, 0.05, m, mat="wood", segs=14)
        for i in range(4):
            p.box((0.05, R * 1.9, 0.05), T((0.05, 0, R + 0.2)) @ M(rot=(i * 45, 0, 0)), mat="wood", bevel=0)
    elif s == "drive":
        xcyl(p, 0.06, 1.2, (0.0, 0, R + 0.2), mat="wood_dark", segs=8)
    elif s == "power":
        for i in range(10):
            a = i * TAU / 10
            p.box((0.3, 0.03, R * 0.25), T((0.05, math.cos(a) * R * 0.95, R + 0.2 + math.sin(a) * R * 0.95)) @ M(rot=(math.degrees(a), 0, 0)), mat="wood", bevel=0)
    else:
        p.box((0.3, 0.3, 0.1), T((0.05, 0, R * 2 + J(p, 0.35, 0.1))), mat="wood", bevel=0)
        p.box((0.25, 1.2, 0.08), M(loc=(0.05, -0.7, R * 2 + 0.3), rot=(5, 0, 0)), mat="wood", bevel=0)


def _gen_industrial(p, s, W, D, H):  # dynamo: field housing, commutator, belt to a motor/engine, panel
    zc = H * 0.45
    if s == "base":
        p.box((W, D, 0.1), T((0, 0, 0.05)), mat="iron", bevel=0)
        for sx in (-1, 1):
            p.box((0.1, D * 0.6, zc), T((sx * W * 0.3, 0, zc / 2)), mat="iron", bevel=0)
    elif s == "mechanism":
        xcyl(p, J(p, 0.3, 0.06), W * 0.5, (0, 0, zc), mat="paint", segs=12)
        for k in (-0.2, 0, 0.2):
            p.ring(0.31, 0.015, T((k * W, 0, zc)) @ M(rot=(0, 90, 0)), mat="copper", segs=12)
    elif s == "drive":
        xcyl(p, 0.03, W * 0.8, (0, 0, zc), mat="steel", segs=6)
        xcyl(p, 0.12, 0.08, (W * 0.42, 0, zc), mat="steel", segs=10)
    elif s == "power":
        p.box((0.3, 0.15, 0.5), T((-W * 0.55, -D * 0.3, 0.35)), mat="paint", bevel=0)
        gauge(p, -W * 0.55, -D * 0.3 - 0.075, 0.45, 0.06)
    else:
        p.tube([(-W * 0.25, 0, zc + 0.3), (-W * 0.4, 0, zc + 0.5), (-W * 0.55, -D * 0.3, 0.6)], 0.012, mat="rubber", segs=4)
        p.ball(0.05, T((-W * 0.55, -D * 0.3, 0.7)), mat="glass", segs=(6, 4))


def _gen_steampunk(p, s, W, D, H):  # steam generator: boiler, piston, flywheel, brass dynamo
    if s == "base":
        p.box((W, D, 0.15), T((0, 0, 0.075)), mat="iron", bevel=0.05)
    elif s == "mechanism":
        xcyl(p, 0.22, 0.5, (W * 0.25, 0, 0.45), mat="brass", segs=12)
        p.band(0.22, 0, h=0.05, m=T((W * 0.25, 0, 0.45)) @ M(rot=(0, 90, 0)))
    elif s == "drive":
        xwheel(p, J(p, 0.35, 0.08), (0, 0, 0.5), rim="iron", hub="iron", spokes=6, t=0.04)
        xcyl(p, 0.03, W * 0.6, (0.1, 0, 0.5), mat="steel", segs=6)
    elif s == "power":
        boiler(p, -W * 0.35, 0, 0.15, J(p, 0.25, 0.08), H * 0.5)
    else:
        flue(p, -W * 0.35, 0, 0.15 + H * 0.5 + 0.35, H, 0.06, mat="iron")
        p.tube([(-W * 0.2, 0, 0.6), (0, 0, 0.9), (W * 0.25, 0, 0.7)], 0.02, mat="copper", segs=6)
        p.ball(0.05, T((W * 0.25, -0.24, 0.45)), mat="glow", segs=(6, 4))


def _gen_future(p, s, W, D, H):  # fusion cell: ringed core in a shell cradle
    if s == "base":
        shell_box(p, W, D, 0.2, (0, 0, 0), mat="shell_dark", bevel=0.2)
    elif s == "mechanism":
        coilcore(p, 0, 0, 0.2, 0.22, H * 0.7, n=4)
    elif s == "drive":
        p.ring(0.4, 0.04, T((0, 0, 0.2 + H * J(p, 0.35, 0.15))) @ M(rot=(70, 0, 0)), mat="body", segs=14)
    elif s == "power":
        p.ball(0.12, T((0, 0, 0.2 + H * 0.35)), mat="glow", segs=(8, 5))
    else:
        for sx in (-1, 1):
            p.tube([(sx * W * 0.45, -D * 0.3, 0.2), (sx * W * 0.45, -D * 0.3, 0.6), (sx * 0.24, 0, 0.7)], 0.03, mat="shell_dark", segs=6)


def _gen_wasteland(p, s, W, D, H):  # car alternator on a bike frame with a battery stack
    if s == "base":
        p.box((W, D * 0.6, 0.06), T((0, 0, 0.03)), mat="rust", bevel=0)
        rod(p, (-W * 0.3, 0, 0.06), (0, 0, 0.8), 0.025, mat="paint", segs=6)
        rod(p, (W * 0.3, 0, 0.06), (0, 0, 0.8), 0.025, mat="paint", segs=6)
    elif s == "mechanism":
        xwheel(p, J(p, 0.3, 0.06), (0, 0, 0.45), rim="rubber", hub="steel", spokes=6, t=0.03)
    elif s == "drive":
        p.cyl(0.08, 0.08, 0.15, T((W * 0.35, 0, 0.3)) @ M(rot=(0, 90, 0)), mat="steel", segs=8)
        p.tube([(0, 0, 0.75), (W * 0.35, 0, 0.38)], 0.006, mat="rubber", segs=3)
    elif s == "power":
        for i in range(3):
            p.box((0.2, 0.15, 0.18), T((-W * 0.6, 0, 0.09 + i * 0.18)), mat="paint" if i % 2 else "rubber", bevel=0)
    else:
        p.tube([(-W * 0.6, 0, 0.5), (-W * 0.3, -0.2, 0.8), (W * 0.35, 0, 0.35)], 0.008, mat="rubber", segs=3)
        p.ball(0.04, T((-W * 0.6, 0, 0.6)), mat="glow", segs=(6, 4))


def _gen_ancient(p, s, W, D, H):  # rune obelisk battery
    if s == "base":
        p.box((W, D, 0.25), T((0, 0, 0.125)), mat="stone", bevel=0.1)
    elif s == "mechanism":
        p.lathe([(W * 0.25, 0.25), (W * 0.2, H * 0.8), (0, H)], mat="stone", segs=4)
    elif s == "drive":
        for k in (0.4, 0.6, 0.8):
            p.ring(W * 0.24 * (1 - k * 0.5), 0.02, T((0, 0, H * k)) @ M(rot=(0, 0, 45)), mat="glow", segs=4)
    elif s == "power":
        p.ball(0.08, T((0, 0, H + J(p, 0.15, 0.3))), mat="glow", segs=(8, 5))
    else:
        for sx in (-1, 1):
            p.box((0.2, 0.2, 0.4), T((sx * W * 0.4, 0, 0.45)), mat="stone_dark", bevel=0.15)


GEN = {"Primal": (_gen_primal, 1.0, 1.0, 0.5), "Agrarian": (_gen_agrarian, 3.0, 3.0, 1.6),
       "Mercantile": (_gen_mercantile, 1.4, 1.4, 2.8), "Industrial": (_gen_industrial, 1.2, 0.8, 1.2),
       "Steampunk": (_gen_steampunk, 1.4, 0.8, 1.8), "Future": (_gen_future, 1.0, 0.9, 1.4),
       "Wasteland": (_gen_wasteland, 1.0, 0.7, 1.0), "Ancient": (_gen_ancient, 0.8, 0.8, 1.8)}
function("Generator", "Machine", MACH, "machine")(dispatch(GEN))


# ================================================================ SewingMachine
def _sm_primal(p, s, W, D, H):  # lacing frame: two stakes with a hide stretched by thongs
    if s == "base":
        for sx in (-1, 1):
            p.tube([(sx * W / 2, 0, 0), (sx * W / 2, 0, H)], 0.03, mat="wood", segs=5)
        p.tube([(-W / 2, 0, H * 0.95), (W / 2, 0, H * 0.95)], 0.025, mat="wood", segs=5)
    elif s == "mechanism":
        p.box((W * 0.7, 0.01, H * 0.6), T((0, 0, H * 0.5)), mat="hide", bevel=0, noise=0.02)
    elif s == "drive":
        for i in range(4):
            z = H * (0.25 + i * 0.17)
            for sx in (-1, 1):
                p.tube([(sx * W * 0.35, 0, z), (sx * W / 2, 0, z + 0.03)], 0.004, mat="rope", segs=3)
    elif s == "power":
        rod(p, (W * 0.1, -0.05, H * 0.4), (W * 0.2, -0.08, H * J(p, 0.5, 0.15)), 0.004, mat="bone", segs=3)
    else:
        p.ball(1.0, M(loc=(W * 0.4, -0.2, 0.04), scale=(0.08, 0.06, 0.04)), mat="rope", segs=(6, 4))


def _sm_table(p, s, W, D, H, mat="wood", top=None, head=None):  # sewing table / treadle machine / electric / clockwork
    e = p.era
    if s == "base":
        p.box((W, D, 0.04), T((0, 0, H - 0.02)), mat=top or mat, bevel=0)
        if e == "Mercantile":  # cast treadle frame
            for sx in (-1, 1):
                p.plate([(-D / 2, 0), (D / 2, 0), (D * 0.3, H - 0.04), (-D * 0.3, H - 0.04)], 0.03, T((sx * W * 0.42, 0, 0)) @ M(rot=(0, 0, 90)), mat="iron", bevel=0)
        else:
            legs4(p, W, D, H - 0.04, 0.05, mat="steel" if e == "Industrial" else mat)
    elif s == "mechanism":  # machine head (agrarian: a hand needle frame)
        if e == "Agrarian":
            p.box((0.04, 0.04, 0.3), T((W * 0.2, 0, H + 0.15)), mat="wood", bevel=0)
            p.ring(0.12, 0.012, T((W * 0.2 - 0.12, 0, H + 0.28)) @ M(rot=(0, 90, 0)), mat="wood", segs=10, square=False)
            p.box((W * 0.4, D * 0.6, 0.004), T((-W * 0.1, 0, H + 0.002)), mat="cloth", bevel=0)
            return
        hm = head or "paint"
        p.box((0.12, 0.14, 0.22), T((W * 0.2, 0, H + 0.11)), mat=hm, bevel=0.15)
        p.box((W * 0.45, 0.12, 0.09), T((0, 0, H + 0.2)), mat=hm, bevel=0.15)
        p.box((0.08, 0.1, 0.14), T((-W * 0.2, 0, H + 0.12)), mat=hm, bevel=0.15)
    elif s == "drive":
        if e == "Agrarian":
            p.box((W * 0.3, D * 0.4, 0.004), M(loc=(W * 0.15, -D * 0.1, H + 0.006), rot=(0, 0, J(p, 10, 0.8))), mat="paint", bevel=0)
        else:
            rod(p, (-W * 0.2, -0.02, H + 0.05), (-W * 0.2, -0.02, H + J(p, 0.01, 0.5)), 0.004, mat="steel", segs=4)
            disk(p, (W * 0.2 + 0.07, 0, H + 0.17), 0.08, 0.02, "x", "steel" if e != "Steampunk" else "brass", segs=12)
    elif s == "power":
        if e == "Mercantile":  # treadle and drive wheel with belt
            p.box((W * 0.4, D * 0.5, 0.03), M(loc=(0, 0, 0.12), rot=(J(p, 8, 0.5), 0, 0)), mat="iron", bevel=0)
            xwheel(p, 0.22, (W * 0.35, 0, 0.4), rim="iron", hub="iron", spokes=6, t=0.025)
            p.tube([(W * 0.35, 0, 0.62), (W * 0.27, 0, H + 0.17)], 0.004, mat="leather", segs=3)
        elif e == "Industrial":  # electric motor under the table
            p.cyl(0.07, 0.07, 0.18, T((W * 0.3, D * 0.2, H - 0.18)) @ M(rot=(0, 90, 0)), mat="paint", segs=10)
            p.tube([(W * 0.3, D * 0.2, H - 0.11), (W * 0.3, D * 0.4, 0.2), (W * 0.6, D * 0.4, 0.0)], 0.006, mat="rubber", segs=3)
        elif e == "Steampunk":  # clockwork drum with a winding key
            p.cyl(0.12, 0.12, 0.2, T((W * 0.3, 0, H - 0.2)), mat="brass", segs=10)
            p.box((0.02, 0.12, 0.08), T((W * 0.3, -0.18, H - 0.1)), mat="copper", bevel=0)
            p.ball(0.03, T((W * 0.3, -0.125, H - 0.1)), mat="glow", segs=(5, 3))
        else:
            p.cyl(0.03, 0.03, 0.08, T((-W * 0.3, D * 0.3, H)), mat="wood", segs=6)
    else:
        p.box((W * 0.3, D * 0.4, 0.004), T((-W * 0.1, -D * 0.1, H + 0.004)), mat="cloth", bevel=0)
        p.cyl(0.02, 0.02, 0.04, T((W * 0.35, -D * 0.3, H)), mat="cloth", segs=6)


def _sm_agrarian(p, s, W, D, H):
    _sm_table(p, s, W, D, H, mat="wood")


def _sm_mercantile(p, s, W, D, H):
    _sm_table(p, s, W, D, H, mat="wood_dark", head="rubber")


def _sm_industrial(p, s, W, D, H):
    _sm_table(p, s, W, D, H, mat="wood", head="paint")


def _sm_steampunk(p, s, W, D, H):
    _sm_table(p, s, W, D, H, mat="wood_dark", head="brass")


def _sm_future(p, s, W, D, H):  # stitching robot arm on a cradle
    if s == "base":
        shell_box(p, W, D, H, (0, 0, 0), mat="body", bevel=0.15)
    elif s == "mechanism":
        rod(p, (W * 0.3, 0, H), (W * 0.2, 0, H + 0.4), 0.05, mat="shell_dark", segs=8)
        rod(p, (W * 0.2, 0, H + 0.4), (-W * 0.1, -0.05, H + J(p, 0.25, 0.15)), 0.035, mat="shell_dark", segs=8)
    elif s == "drive":
        p.ball(0.06, T((W * 0.2, 0, H + 0.4)), mat="body", segs=(8, 5))
        p.ball(0.06, T((W * 0.3, 0, H)), mat="body", segs=(8, 5))
    elif s == "power":
        p.lathe([(0.03, 0), (0.01, -0.06), (0, -0.07)], T((-W * 0.1, -0.05, H + 0.25)), mat="glow", segs=6)
        p.box((W * 0.8, 0.01, 0.02), T((0, -D / 2, H * 0.5)), mat="glow", bevel=0)
    else:
        p.box((W * 0.4, D * 0.5, 0.004), T((-W * 0.15, 0, H + 0.002)), mat="cloth", bevel=0)


def _sm_wasteland(p, s, W, D, H):  # hand-crank machine head bolted to a door on crates
    if s == "base":
        for sx in (-1, 1):
            p.box((0.3, D * 0.8, H - 0.04), T((sx * W * 0.35, 0, (H - 0.04) / 2)), mat="wood", bevel=0)
        p.box((W, D, 0.04), T((0, 0, H - 0.02)), mat="paint", bevel=0)
    elif s == "mechanism":
        p.box((W * 0.45, 0.12, 0.09), T((0, 0, H + 0.2)), mat="rust", bevel=0)
        p.box((0.12, 0.14, 0.22), T((W * 0.2, 0, H + 0.11)), mat="rust", bevel=0)
    elif s == "drive":
        p.tube([(W * 0.2 + 0.07, 0, H + 0.17), (W * 0.2 + 0.1, -0.08, H + 0.1), (W * 0.2 + 0.14, -0.08, H + J(p, 0.12, 0.2))], 0.006, mat="steel", segs=4)
    elif s == "power":
        wire(p, -W * 0.2, 0, H + 0.12, 0.05)
    else:
        patch(p, 0.2, 0.1, T((0, -D / 2 - 0.003, H * 0.7)), mat="steel")


def _sm_ancient(p, s, W, D, H):  # stone loom-table with a floating rune needle
    if s == "base":
        p.box((W, D, H), T((0, 0, H / 2)), mat="stone", bevel=0.1)
    elif s == "mechanism":
        p.box((W * 0.15, D * 0.2, 0.25), T((W * 0.3, 0, H + 0.125)), mat="stone_dark", bevel=0.15)
    elif s == "drive":
        p.lathe([(0, 0), (0.01, 0.02), (0, J(p, 0.12, 0.2))], T((0, 0, H + 0.1)), mat="glow", segs=4)
    elif s == "power":
        p.ring(0.06, 0.008, T((0, 0, H + 0.08)), mat="glow", segs=6)
    else:
        runes(p, 0, -D / 2 - 0.006, 0.15, H * 0.85, n=3, w=0.05)


SEW = {"Primal": (_sm_primal, 0.9, 0.3, 1.0), "Agrarian": (_sm_agrarian, 0.9, 0.5, 0.72),
       "Mercantile": (_sm_mercantile, 0.9, 0.45, 0.76), "Industrial": (_sm_industrial, 1.0, 0.5, 0.76),
       "Steampunk": (_sm_steampunk, 0.9, 0.5, 0.78), "Future": (_sm_future, 0.9, 0.6, 0.75),
       "Wasteland": (_sm_wasteland, 1.0, 0.5, 0.75), "Ancient": (_sm_ancient, 0.9, 0.5, 0.75)}
function("SewingMachine", "Machine", MACH, "machine")(dispatch(SEW))


# ================================================================ Drill
def _dr_primal(p, s, W, D, H):  # bow drill on a hearth board
    if s == "base":
        p.box((W, D, 0.04), T((0, 0, 0.02)), mat="wood", bevel=0, noise=0.02)
    elif s == "mechanism":
        p.cyl(0.012, 0.012, H, T((0, 0, 0.04)), mat="wood", segs=5)
    elif s == "drive":  # bow
        p.tube([(-W * 0.45, -0.1, H * 0.5), (0, -0.15, H * J(p, 0.55, 0.1)), (W * 0.45, -0.1, H * 0.5)], 0.012, mat="wood", segs=4)
        p.tube([(-W * 0.45, -0.1, H * 0.5), (0, 0, H * 0.5), (W * 0.45, -0.1, H * 0.5)], 0.002, mat="hide", segs=3)
    elif s == "power":  # handhold stone
        rock(p, 0.05, 0.05, 0.03, (0, 0, H + 0.06), segs=(6, 4))
    else:
        p.ball(1.0, M(loc=(W * 0.3, 0, 0.05), scale=(0.04, 0.03, 0.01)), mat="rope", segs=(5, 3))


def _dr_agrarian(p, s, W, D, H):  # brace drill on a bench block
    if s == "base":
        p.box((W, D, 0.25), T((0, 0, 0.125)), mat="wood", bevel=0)
    elif s == "mechanism":
        p.cyl(0.006, 0.006, 0.12, T((0, 0, 0.25)), mat="iron", segs=5)
    elif s == "drive":
        p.tube([(0, 0, 0.37), (0, 0, 0.42), (0.1, 0, 0.47), (0.1, 0, J(p, 0.6, 0.06)), (0, 0, 0.65), (0, 0, 0.7)], 0.01, mat="iron", segs=5)
    elif s == "power":
        p.lathe([(0, 0), (0.04, 0.01), (0.045, 0.04), (0, 0.05)], T((0, 0, 0.7)), mat="wood_dark", segs=8)
        p.cyl(0.016, 0.016, 0.06, T((0.1, 0, 0.5)), mat="wood_dark", segs=6)
    else:
        p.box((0.15, 0.1, 0.06), T((-W * 0.3, 0, 0.28)), mat="wood_dark", bevel=0)


def _dr_mercantile(p, s, W, D, H):  # capstan drill: tripod frame, screw stem, turning bars
    if s == "base":
        for i in range(3):
            a = i * TAU / 3
            p.tube([(math.cos(a) * W * 0.5, math.sin(a) * W * 0.5, 0), (0, 0, H)], 0.05, mat="wood_dark", segs=6)
    elif s == "mechanism":
        p.cyl(0.04, 0.04, H * 0.9, mat="iron", segs=8)
        p.cyl(0.002, 0.05, 0.12, T((0, 0, -0.08)), mat="iron", segs=6)
    elif s == "drive":
        z = H * J(p, 0.35, 0.15)
        for i in range(2):
            p.box((W * 0.9, 0.05, 0.05), T((0, 0, z)) @ M(rot=(0, 0, i * 90)), mat="wood", bevel=0)
    elif s == "power":
        p.box((0.2, 0.2, 0.15), T((0, 0, H)), mat="iron", bevel=0)
    else:
        p.ring(0.3, 0.05, T((0, 0, 0.03)), mat="stone", segs=10, square=False)


def _dr_industrial(p, s, W, D, H):  # oil derrick: lattice tower, crown block, drill string
    if s == "base":
        for sx in (-1, 1):
            for sy in (-1, 1):
                rod(p, (sx * W / 2, sy * W / 2, 0), (sx * 0.1, sy * 0.1, H), 0.04, mat="steel", segs=4)
        for k in (0.25, 0.5, 0.75):
            r = W / 2 * (1 - k) + 0.1 * k
            p.box((r * 2, r * 2, 0.03), T((0, 0, H * k)), mat="steel", bevel=0)
    elif s == "mechanism":
        p.cyl(0.05, 0.05, H * 0.9, mat="iron", segs=8)
    elif s == "drive":
        p.box((0.35, 0.35, 0.2), T((0, 0, H + 0.1)), mat="paint", bevel=0)
        p.tube([(0, 0, H), (0, 0, H * J(p, 0.6, 0.15))], 0.012, mat="steel", segs=3)
    elif s == "power":
        p.box((0.6, 0.5, 0.5), T((W * 0.8, 0, 0.25)), mat="paint", bevel=0)
        flue(p, W * 0.8, 0.15, 0.5, 1.1, 0.05, mat="iron")
    else:
        p.box((W, W, 0.15), T((0, 0, 0.075)), mat="wood", bevel=0)


def _dr_steampunk(p, s, W, D, H):  # steam drilling rig: boiler cart, brass mast, piston
    if s == "base":
        p.box((W, D, 0.25), T((0, 0, 0.3)), mat="iron", bevel=0.05)
        for sx in (-1, 1):
            for sy in (-1, 1):
                xwheel(p, 0.18, (sx * W * 0.35, sy * (D / 2 + 0.03), 0.18), rim="iron", hub="iron", spokes=4, t=0.04)
    elif s == "mechanism":
        p.box((0.15, 0.15, H), T((-W * 0.3, 0, H / 2 + 0.3)), mat="brass", bevel=0)
        p.cyl(0.04, 0.03, H * 0.7, T((-W * 0.3 - 0.15, 0, -0.1)), mat="steel", segs=8)
    elif s == "drive":
        p.cyl(0.1, 0.1, 0.3, T((-W * 0.3 - 0.15, 0, H * J(p, 0.6, 0.1))), mat="copper", segs=10)
        gear(p, 0.15, T((-W * 0.3, -0.09, H * 0.45)), teeth=10, th=0.02)
    elif s == "power":
        boiler(p, W * 0.2, 0, 0.42, J(p, 0.25, 0.08), H * 0.4)
    else:
        p.tube([(W * 0.2, 0, 0.42 + H * 0.4 + 0.2), (W * 0.2, 0, H + 0.4), (-W * 0.3 - 0.15, 0, H + 0.4), (-W * 0.3 - 0.15, 0, H * 0.75)], 0.02, mat="copper", segs=6)
        gauge(p, W * 0.2, -0.26, 0.42 + H * 0.25, 0.05)


def _dr_future(p, s, W, D, H):  # laser drill: tripod pod with a beam emitter
    if s == "base":
        for i in range(3):
            a = i * TAU / 3
            rod(p, (math.cos(a) * W * 0.5, math.sin(a) * W * 0.5, 0), (math.cos(a) * 0.15, math.sin(a) * 0.15, H * 0.7), 0.05, mat="shell_dark", segs=8)
    elif s == "mechanism":
        p.ball(1.0, M(loc=(0, 0, H * 0.75), scale=(0.3, 0.3, 0.22)), mat="body", segs=(12, 6))
    elif s == "drive":
        p.cyl(0.08, 0.05, 0.25, T((0, 0, H * 0.75 - 0.4)), mat="shell_dark", segs=10)
    elif s == "power":
        p.cyl(0.015, 0.015, H * 0.75 - 0.4, mat="glow", segs=6)
        p.ring(0.1, 0.015, T((0, 0, 0.02)), mat="glow", segs=10)
    else:
        p.ring(0.31, 0.012, T((0, 0, H * J(p, 0.75, 0.04))), mat="glow", segs=12)


def _dr_wasteland(p, s, W, D, H):  # jackhammer rig on a scrap frame with an engine
    if s == "base":
        for sx in (-1, 1):
            p.box((0.06, 0.06, H), T((sx * W * 0.35, 0, H / 2)), mat="rust", bevel=0)
        p.box((W * 0.8, 0.1, 0.08), T((0, 0, H)), mat="rust", bevel=0)
    elif s == "mechanism":
        p.cyl(0.08, 0.08, 0.5, T((0, 0, H * J(p, 0.35, 0.15))), mat="steel", segs=8)
        p.cyl(0.02, 0.005, 0.3, T((0, 0, H * 0.35 - 0.3)), mat="steel", segs=5)
    elif s == "drive":
        p.tube([(0, 0, H), (0, 0, H * 0.35 + 0.5)], 0.008, mat="iron", segs=3)
    elif s == "power":
        p.box((0.4, 0.35, 0.35), T((W * 0.7, 0, 0.175)), mat="paint", bevel=0)
        p.tube([(W * 0.6, 0, 0.3), (0.1, 0, H * 0.5)], 0.02, mat="rubber", segs=5)
    else:
        wire(p, W * 0.35, 0, H * 0.6, 0.04)
        p.ring(0.3, 0.08, T((0, 0, 0.08)), mat="rubber", segs=10, square=False)


def _dr_ancient(p, s, W, D, H):  # stone spike bore held in a rune arch
    if s == "base":
        for sx in (-1, 1):
            p.box((0.25, 0.3, H), T((sx * W * 0.4, 0, H / 2)), mat="stone", bevel=0.1)
        p.box((W + 0.25, 0.3, 0.25), T((0, 0, H)), mat="stone", bevel=0.1)
    elif s == "mechanism":
        p.lathe([(0, 0.1), (0.12, H * 0.4), (0.15, H * 0.6), (0, H * 0.62)], mat="stone_dark", segs=6)
    elif s == "drive":
        p.ring(0.17, 0.02, T((0, 0, H * J(p, 0.5, 0.15))), mat="glow", segs=6)
    elif s == "power":
        p.ball(0.08, T((0, 0, H - 0.12)), mat="glow", segs=(6, 4))
    else:
        for sx in (-1, 1):
            runes(p, sx * W * 0.4, -0.16, 0.2, H * 0.85, n=3, w=0.06)


DRILL = {"Primal": (_dr_primal, 0.5, 0.15, 0.4), "Agrarian": (_dr_agrarian, 0.5, 0.3, 0.75),
         "Mercantile": (_dr_mercantile, 1.4, 1.4, 1.8), "Industrial": (_dr_industrial, 1.4, 1.4, 4.0),
         "Steampunk": (_dr_steampunk, 1.4, 0.8, 1.8), "Future": (_dr_future, 1.2, 1.2, 1.6),
         "Wasteland": (_dr_wasteland, 1.0, 0.6, 1.8), "Ancient": (_dr_ancient, 1.2, 0.6, 2.0)}
function("Drill", "Machine", MACH, "machine")(dispatch(DRILL))
