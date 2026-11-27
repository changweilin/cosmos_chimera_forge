"""Vehicle family forms (載具: 車體、行走件、動力／牽引、貨架、頂／帆): Cart, Sled, Boat, Minecart, SteamCar, Airship,
Wheelbarrow, Palanquin (cosmos_chimera P1-19, ADR-0016; settlement-structures.md#交通工具 P3-17).

Slots: body (車體: bed, hull, tub, chair), running (行走件: wheels, runners, keel, rails shoes, hover pads),
power (動力／牽引: shafts and yoke for a draft beast, poles for bearers, sails' mast, boiler, motor, burner),
rack (貨架: load, cargo, bales, seats), top (頂／帆: canopy, cover, sail, envelope, roof).
Frame: Z up, travel along +X (the tow end or bow at +X), the side faces -Y; origin at the ground contact under
the middle of the vehicle. A boat's origin is its waterline (the hull dips below z = 0); an airship's is the
ground under its gondola (P3-17 lifts it). Draft animals and bearers are not part of the kit: P3-17 draws the
beast (FieldMeshes.DraftBeast) and the kit only provides shafts, yokes or carrying poles. Sizes follow the P3-17
field vehicles (about 2–3.5 m long; an airship about 3.5–5 m tall). Budget 'machine' (4000).
Glow: form-era glow only (Steampunk, Future, Wasteland, Ancient), as for machines.
Every form draws its frame values first (L, W, H by F), in a fixed order.
"""
import math

from mathutils import Matrix, Vector

from forms_furniture import wheel
from forms_lamp import flame, lit
from forms_machine import boiler, flue, gauge, patch, sack, wire
from forms_tools import rod
from kit_forms import F, J, coin, function
from kit_lib import M

VEH = ("body", "running", "power", "rack", "top")
T = Matrix.Translation
TAU = math.tau


def wheels(p, xs, ys, r, rim="iron", hub="wood", spokes=6, t=None, axle="wood"):
    for x in xs:
        for y in ys:
            wheel(p, r, (x, y, r), rim=rim, hub=hub, spokes=spokes, t=t)
        rod(p, (x, ys[0], r), (x, ys[-1], r), r * 0.08, mat=axle, segs=6)


def tyres(p, xs, ys, r, w, mat="rubber", hub="steel"):
    for x in xs:
        for y in ys:
            p.ring(r * 0.8, r * 0.22, T((x, y, r)) @ M(rot=(90, 0, 0)), mat=mat, segs=12, square=False)
            p.cyl(r * 0.55, r * 0.55, w * 0.6, T((x, y - w * 0.3, r)) @ M(rot=(-90, 0, 0)), mat=hub, segs=8)


def shafts(p, x0, L, W, z, mat="wood", yoke=True):
    """Pair of draft shafts from the front of the bed out along +X, curving down, with a cross bar."""
    for s in (-1, 1):
        p.tube([(x0, s * W * 0.35, z), (x0 + L * 0.5, s * W * 0.33, z + 0.05), (x0 + L, s * W * 0.3, z - 0.15)], 0.03, mat=mat, segs=5)
    if yoke:
        rod(p, (x0 + L * 0.9, -W * 0.32, z - 0.1), (x0 + L * 0.9, W * 0.32, z - 0.1), 0.025, mat=mat, segs=5)


def bales(p, x0, x1, y, z, n, r=0.22, mat="cloth"):
    for i in range(n):
        x = x0 + (x1 - x0) * (i + 0.5) / n
        p.ball(1.0, M(loc=(x, y + p.rng.uniform(-0.05, 0.05), z + r * 0.8), scale=(r, r * 0.9, r * 0.8)), mat=mat if i % 2 == 0 else "hide", segs=(8, 5), noise=0.03)


def dispatch(table):
    def form(p, slot):
        fn, l, w, h = table[p.era]
        fn(p, slot, l * F(p, 1, 0.07), w * F(p, 1, 0.06), h * F(p, 1, 0.06))
    return form


# ================================================================ Cart
def _cart_primal(p, s, L, W, H):  # travois-like drag sled: two poles, cross bars, hide load
    if s == "body":
        for i in range(4):
            x = -L * 0.35 + i * L * 0.18
            rod(p, (x, -W * 0.4, 0.12 + i * 0.07), (x, W * 0.4, 0.12 + i * 0.07), 0.025, mat="wood", segs=5)
    elif s == "running":
        for y in (-W * 0.35, W * 0.35):
            p.tube([(-L * 0.5, y, 0.03), (0, y, 0.25), (L * 0.5, y * 0.4, 0.9)], 0.04, mat="wood", segs=6)
    elif s == "power":
        p.band(0.05, 0, h=0.08, m=T((L * 0.45, 0, 0.85)) @ M(rot=(0, 70, 0)))
    elif s == "rack":
        bales(p, -L * 0.35, L * 0.05, 0, 0.18, 2, r=0.22, mat="hide")
    else:
        p.tube([(-L * 0.35, -W * 0.3, 0.3), (-L * 0.1, 0, 0.55), (L * 0.05, W * 0.3, 0.35)], 0.012, mat="rope", segs=3)


def _cart_wagon(p, s, L, W, H, era):
    plank = {"Agrarian": "wood", "Mercantile": "wood_dark", "Industrial": "paint"}[era]
    r = {"Agrarian": 0.38, "Mercantile": 0.42, "Industrial": 0.35}[era]
    zb = r + 0.12
    if s == "body":
        p.box((L, W, 0.06), T((0, 0, zb)), mat=plank, bevel=0)
        for y in (-W / 2, W / 2):
            p.box((L, 0.04, 0.28), T((0, y, zb + 0.16)), mat=plank, bevel=0)
        p.box((0.04, W, 0.28), T((-L / 2, 0, zb + 0.16)), mat=plank, bevel=0)
    elif s == "running":
        if era == "Industrial":
            wheels(p, (-L * 0.3, L * 0.3), (-W / 2 - 0.05, W / 2 + 0.05), r, rim="iron", hub="iron", spokes=8, t=0.04, axle="iron")
        else:
            wheels(p, (-L * 0.28, L * 0.3) if era == "Mercantile" else (0.0,), (-W / 2 - 0.05, W / 2 + 0.05), r, rim="iron" if era != "Agrarian" else "wood", hub="wood", spokes=6)
    elif s == "power":
        shafts(p, L / 2, J(p, 1.4, 0.08), W, zb)
    elif s == "rack":
        if era == "Industrial":
            for i in range(3):
                p.box((0.5, 0.5, 0.4), M(loc=(-L * 0.3 + i * L * 0.3, 0, zb + 0.23), rot=(0, 0, p.rng.uniform(-6, 6))), mat="wood", bevel=0)
        else:
            bales(p, -L * 0.35, L * 0.35, 0, zb, 3, r=0.25)
    else:
        if era == "Mercantile":  # covered wagon hoops and canvas
            for i in range(4):
                x = -L * 0.4 + i * L * 0.27
                p.tube([(x, -W / 2, zb + 0.3)] + [(x, -W / 2 * math.cos(a), zb + 0.3 + W * 0.55 * math.sin(a)) for a in (0.6, 1.2, 1.9, 2.5)] + [(x, W / 2, zb + 0.3)], 0.015, mat="wood", segs=4)
            p.cyl(W * 0.53, W * 0.53, L * 0.85, T((-L * 0.42, 0, zb + 0.3)) @ M(rot=(0, 90, 0), scale=(1, 1, 1)), mat="cloth", segs=10, cap=False)
        elif era == "Industrial":
            p.box((L * 0.8, W * 0.9, 0.02), M(loc=(0, 0, zb + 0.46), rot=(J(p, 4, 1), 0, 0)), mat="cloth", bevel=0)
        else:
            p.tube([(-L * 0.4, -W * 0.45, zb + 0.3), (0, 0, zb + 0.6), (L * 0.35, W * 0.45, zb + 0.3)], 0.012, mat="rope", segs=3)


def _cart_agr(p, s, L, W, H):
    _cart_wagon(p, s, L, W, H, "Agrarian")


def _cart_mer(p, s, L, W, H):
    _cart_wagon(p, s, L, W, H, "Mercantile")


def _cart_ind(p, s, L, W, H):
    _cart_wagon(p, s, L, W, H, "Industrial")


def _cart_steam(p, s, L, W, H):  # steam traction tractor-trailer
    r = 0.4
    if s == "body":
        p.box((L, W, 0.12), T((0, 0, r + 0.1)), mat="iron", bevel=0.05)
    elif s == "running":
        wheels(p, (-L * 0.3, L * 0.3), (-W / 2 - 0.06, W / 2 + 0.06), r, rim="iron", hub="brass", spokes=8, t=0.06, axle="iron")
    elif s == "power":
        boiler(p, L * 0.3, 0, r + 0.16, J(p, 0.32, 0.08), 0.7)
    elif s == "rack":
        for i in range(2):
            p.box((0.45, W * 0.8, 0.45), T((-L * 0.25 + i * 0.5, 0, r + 0.4)), mat="wood", bevel=0)
    else:
        flue(p, L * 0.3, 0, r + 1.2, r + 1.7, 0.07, mat="iron")
        p.ball(0.05, T((L * 0.3, -0.33, r + 0.6)), mat="glow", segs=(6, 4))


def _cart_future(p, s, L, W, H):  # hover pallet
    z = 0.4
    if s == "body":
        p.box((L, W, 0.15), T((0, 0, z)), mat="body", bevel=0.25, bevel_seg=2)
    elif s == "running":
        for x in (-L * 0.3, L * 0.3):
            for y in (-W * 0.3, W * 0.3):
                p.cyl(0.18, 0.2, 0.08, T((x, y, z - 0.16)), mat="shell_dark", segs=10)
                p.cyl(0.14, 0.14, 0.01, T((x, y, z - 0.17)), mat="glow", segs=10)
    elif s == "power":
        p.box((0.25, W * 0.6, 0.3), T((L * 0.45, 0, z + 0.2)), mat="shell_dark", bevel=0.2)
        p.box((0.01, W * 0.4, 0.05), T((L * 0.58, 0, z + 0.25)), mat="glow", bevel=0)
    elif s == "rack":
        for i in range(2):
            p.box((0.55, W * 0.7, 0.4), T((-L * 0.25 + i * 0.6, 0, z + 0.28)), mat="paint", bevel=0.1)
    else:
        p.box((L * 0.9, 0.01, 0.03), T((0, -W / 2 - 0.005, z)), mat="glow", bevel=0)


def _cart_waste(p, s, L, W, H):  # car-chassis cart on mismatched tyres
    if s == "body":
        p.box((L, W, 0.25), T((0, 0, 0.55)), mat="rust", bevel=0)
        patch(p, 0.4, 0.15, T((0.3, -W / 2 - 0.003, 0.55)), mat="paint")
    elif s == "running":
        tyres(p, (-L * 0.32, L * 0.32), (-W / 2 - 0.08, W / 2 + 0.08), 0.32, 0.18)
    elif s == "power":
        shafts(p, L / 2, J(p, 1.3, 0.08), W, 0.6, mat="steel")
    elif s == "rack":
        p.cyl(0.25, 0.25, 0.55, T((-L * 0.25, 0, 0.68)), mat="paint", segs=10)
        p.box((0.5, 0.4, 0.35), T((L * 0.15, 0, 0.85)), mat="wood", bevel=0)
    else:
        p.box((L * 0.6, W * 0.9, 0.02), M(loc=(-0.1, 0, 1.25), rot=(J(p, 5, 1), 0, 0)), mat="cloth", bevel=0)
        for x in (-L * 0.4, L * 0.2):
            rod(p, (x, -W * 0.4, 0.68), (x, -W * 0.4, 1.25), 0.02, mat="steel", segs=4)


def _cart_ancient(p, s, L, W, H):  # floating stone barge sled
    z = 0.35
    if s == "body":
        p.box((L, W, 0.3), T((0, 0, z + 0.15)), mat="stone", bevel=0.15)
    elif s == "running":
        for x in (-L * 0.3, L * 0.3):
            p.box((0.3, W * 0.8, 0.1), T((x, 0, z - 0.1)), mat="stone_dark", bevel=0.2)
    elif s == "power":
        p.box((L * 0.8, 0.02, 0.04), T((0, -W / 2 - 0.01, z + 0.15)), mat="glow", bevel=0)
        p.ball(0.08, T((L / 2 + 0.1, 0, z + 0.3)), mat="glow", segs=(6, 4))
    elif s == "rack":
        p.box((0.6, W * 0.6, 0.4), M(loc=(0, 0, z + 0.5), rot=(0, 0, 10)), mat="stone_dark", bevel=0.15)
    else:
        for x in (-L * 0.45, L * 0.45):
            p.box((0.1, 0.1, 0.5), T((x, 0, z + 0.55)), mat="stone", bevel=0.1)


CART = {"Primal": (_cart_primal, 2.4, 0.9, 1.0), "Agrarian": (_cart_agr, 1.8, 1.1, 1.0), "Mercantile": (_cart_mer, 2.6, 1.3, 1.4),
        "Industrial": (_cart_ind, 2.6, 1.3, 1.2), "Steampunk": (_cart_steam, 2.8, 1.3, 1.8), "Future": (_cart_future, 2.4, 1.2, 1.0),
        "Wasteland": (_cart_waste, 2.6, 1.3, 1.3), "Ancient": (_cart_ancient, 2.4, 1.2, 1.0)}
function("Cart", "Vehicle", VEH, "machine")(dispatch(CART))


# ================================================================ Sled
def runners(p, L, W, mat="wood", up=0.25, r=0.03, gap=0.42):
    for y in (-W * gap, W * gap):
        p.tube([(-L * 0.5, y, 0.03), (L * 0.35, y, 0.03), (L * 0.48, y, 0.1), (L * 0.52, y, up)], r, mat=mat, segs=5)


def _sled_basic(p, s, L, W, H, era):
    deck = {"Primal": "hide", "Agrarian": "wood", "Mercantile": "wood_dark", "Industrial": "steel", "Wasteland": "rust"}[era]
    run = {"Primal": "bone", "Agrarian": "wood", "Mercantile": "iron", "Industrial": "steel", "Wasteland": "steel"}[era]
    z = 0.22
    if s == "body":
        p.box((L * 0.85, W * 0.9, 0.04), T((-L * 0.05, 0, z)), mat=deck, bevel=0, noise=0.03 if era == "Primal" else 0)
        if era in ("Mercantile", "Industrial"):
            for y in (-W * 0.45, W * 0.45):
                p.box((L * 0.85, 0.03, 0.2), T((-L * 0.05, y, z + 0.12)), mat=deck, bevel=0)
    elif s == "running":
        runners(p, L, W, mat=run)
        for x in (-L * 0.3, 0, L * 0.25):
            for y in (-W * 0.42, W * 0.42):
                rod(p, (x, y, 0.04), (x, y, z), 0.02, mat=run if era != "Primal" else "wood", segs=4)
    elif s == "power":
        if era == "Industrial":
            shafts(p, L * 0.45, J(p, 1.3, 0.08), W, z + 0.1, mat="steel")
        else:
            p.tube([(L * 0.5, -W * 0.3, 0.2), (L * 0.5 + J(p, 0.9, 0.1), 0, 0.5), (L * 0.5, W * 0.3, 0.2)], 0.012, mat="rope" if era != "Wasteland" else "iron", segs=3)
    elif s == "rack":
        bales(p, -L * 0.35, L * 0.2, 0, z + 0.02, 2, r=0.22, mat="hide" if era == "Primal" else "cloth")
    else:
        if era == "Mercantile":  # covered sled hood
            p.cyl(W * 0.48, W * 0.48, L * 0.5, T((-L * 0.45, 0, z + 0.2)) @ M(rot=(0, 90, 0)), mat="cloth", segs=10, cap=False)
        elif era == "Industrial":
            rod(p, (-L * 0.45, -W * 0.4, z), (-L * 0.5, -W * 0.4, z + J(p, 0.7, 0.1)), 0.02, mat="steel", segs=4)
            rod(p, (-L * 0.45, W * 0.4, z), (-L * 0.5, W * 0.4, z + 0.7), 0.02, mat="steel", segs=4)
            rod(p, (-L * 0.5, -W * 0.4, z + 0.7), (-L * 0.5, W * 0.4, z + 0.7), 0.02, mat="rubber", segs=4)
        else:
            p.tube([(-L * 0.4, -W * 0.4, z + 0.3), (-L * 0.1, 0, z + J(p, 0.5, 0.15)), (L * 0.2, W * 0.4, z + 0.3)], 0.012, mat="rope", segs=3)


def _sled_steam(p, s, L, W, H):  # tracked steam sled
    if s == "body":
        p.box((L * 0.8, W, 0.2), T((0, 0, 0.45)), mat="brass", bevel=0.05)
    elif s == "running":
        for y in (-W * 0.42, W * 0.42):
            p.box((L * 0.85, 0.22, 0.25), T((0, y, 0.18)), mat="iron", bevel=0.4)
            for k in range(4):
                p.cyl(0.08, 0.08, 0.24, T((-L * 0.3 + k * L * 0.2, y - 0.12, 0.15)) @ M(rot=(-90, 0, 0)), mat="steel", segs=8)
    elif s == "power":
        boiler(p, L * 0.2, 0, 0.55, J(p, 0.28, 0.08), 0.55)
    elif s == "rack":
        p.box((0.6, W * 0.7, 0.35), T((-L * 0.25, 0, 0.72)), mat="wood", bevel=0)
    else:
        flue(p, L * 0.2, 0, 1.4, 1.8, 0.06, mat="iron")
        gauge(p, L * 0.2, -0.29, 0.85, 0.05)


def _sled_future(p, s, L, W, H):  # hovercraft sled with a rear fan
    if s == "body":
        p.box((L, W, 0.25), T((0, 0, 0.4)), mat="body", bevel=0.35, bevel_seg=2)
    elif s == "running":
        p.box((L * 1.02, W * 1.02, 0.12), T((0, 0, 0.12)), mat="rubber", bevel=0.4)
        p.box((L * 0.9, 0.01, 0.02), T((0, -W * 0.51, 0.06)), mat="glow", bevel=0)
    elif s == "power":
        p.ring(0.35, 0.05, T((-L * 0.45, 0, 0.9)) @ M(rot=(0, 90, 0)), mat="shell_dark", segs=12)
        p.ball(0.08, T((-L * 0.45, 0, 0.9)), mat="glow", segs=(6, 4))
    elif s == "rack":
        p.box((0.6, W * 0.6, 0.3), T((L * 0.1, 0, 0.67)), mat="paint", bevel=0.1)
    else:
        p.box((0.5, W * 0.8, 0.02), M(loc=(L * 0.35, 0, 0.75), rot=(0, -20, 0)), mat="glass", bevel=0)


def _sled_ancient(p, s, L, W, H):
    if s == "body":
        p.box((L * 0.9, W, 0.18), T((0, 0, 0.35)), mat="stone", bevel=0.2)
    elif s == "running":
        runners(p, L, W, mat="stone_dark", r=0.05)
    elif s == "power":
        for y in (-W * 0.42, W * 0.42):
            p.box((L * 0.7, 0.02, 0.03), T((0, y, 0.06)), mat="glow", bevel=0)
    elif s == "rack":
        p.box((0.5, W * 0.6, 0.3), M(loc=(0, 0, 0.6), rot=(0, 0, 8)), mat="stone_dark", bevel=0.15)
    else:
        p.ball(0.07, T((L * 0.45, 0, 0.6 + J(p, 0.1, 0.5))), mat="glow", segs=(6, 4))


SLED = {"Primal": (lambda p, s, L, W, H: _sled_basic(p, s, L, W, H, "Primal"), 2.0, 0.8, 0.8),
        "Agrarian": (lambda p, s, L, W, H: _sled_basic(p, s, L, W, H, "Agrarian"), 2.2, 0.9, 0.8),
        "Mercantile": (lambda p, s, L, W, H: _sled_basic(p, s, L, W, H, "Mercantile"), 2.4, 1.1, 1.2),
        "Industrial": (lambda p, s, L, W, H: _sled_basic(p, s, L, W, H, "Industrial"), 2.4, 1.0, 1.0),
        "Steampunk": (_sled_steam, 2.6, 1.2, 1.8), "Future": (_sled_future, 2.4, 1.2, 1.0),
        "Wasteland": (lambda p, s, L, W, H: _sled_basic(p, s, L, W, H, "Wasteland"), 2.2, 1.0, 0.9),
        "Ancient": (_sled_ancient, 2.2, 1.0, 0.9)}
function("Sled", "Vehicle", VEH, "machine")(dispatch(SLED))


# ================================================================ Boat (origin at the waterline)
def hull(p, L, W, D, mat="wood", z=0.0, sheer=0.25, segs=10, flat=False):
    """Hull as a lathe along X: pointed bow (+X) and stern, belly D below the waterline, sheer above it."""
    prof = [(0, -L / 2), (W * 0.3, -L * 0.42), (W * 0.5, -L * 0.2), (W * 0.5, L * 0.15), (W * 0.35 if not flat else W * 0.45, L * 0.38), (0, L / 2)]
    p.lathe(prof, T((0, 0, z + sheer * 0.3)) @ M(rot=(0, 90, 0)) @ M(scale=((D + sheer) / W, 1, 1)), mat=mat, segs=segs)


def _boat_primal(p, s, L, W, H):  # dugout canoe
    if s == "body":
        hull(p, L, W, 0.2, mat="wood", sheer=0.15)
    elif s == "running":
        p.box((L * 0.7, W * 0.6, 0.02), T((0, 0, 0.12)), mat="wood_dark", bevel=0)
    elif s == "power":  # paddle
        rod(p, (-L * 0.1, -W * 0.3, 0.2), (L * 0.1, W * 0.2, J(p, 0.6, 0.15)), 0.02, mat="wood", segs=5)
        p.box((0.25, 0.02, 0.12), T((-L * 0.1 - 0.12, -W * 0.3 - 0.02, 0.15)), mat="wood", bevel=0)
    elif s == "rack":
        p.ball(1.0, M(loc=(-L * 0.2, 0, 0.18), scale=(0.2, 0.15, 0.1)), mat="hide", segs=(6, 4))
    else:
        p.tube([(L * 0.45, 0, 0.2), (L * 0.55, 0, 0.35)], 0.02, mat="bone", segs=4)


def _boat_raft(p, s, L, W, H):  # log raft with a pole and a lean-to
    if s == "body":
        n = 6
        for i in range(n):
            y = -W / 2 + W * (i + 0.5) / n
            rod(p, (-L / 2, y, 0.05), (L / 2 + p.rng.uniform(-0.1, 0.1), y, 0.05), W / n * 0.5, mat="wood", segs=7)
    elif s == "running":
        for x in (-L * 0.35, L * 0.35):
            rod(p, (x, -W / 2, 0.15), (x, W / 2, 0.15), 0.04, mat="wood_dark", segs=5)
    elif s == "power":
        rod(p, (-L * 0.4, -W * 0.3, 0.1), (-L * 0.45, -W * 0.35, J(p, 2.2, 0.1)), 0.025, mat="wood", segs=5)
    elif s == "rack":
        bales(p, 0, L * 0.35, 0, 0.15, 2, r=0.2)
    else:
        for y in (-W * 0.3, W * 0.3):
            rod(p, (-L * 0.1, y, 0.15), (-L * 0.1, 0, 0.9), 0.02, mat="wood", segs=4)
        p.box((0.6, W * 0.65, 0.02), M(loc=(-L * 0.1, 0, 0.55)), mat="cloth", bevel=0)


def _boat_sail(p, s, L, W, H):  # small sailing boat
    if s == "body":
        hull(p, L, W, 0.35, mat="wood_dark", sheer=0.3)
    elif s == "running":
        p.box((L * 0.5, 0.04, 0.35), T((0, 0, -0.45)), mat="wood_dark", bevel=0)
        p.box((0.04, 0.2, 0.35), T((-L * 0.48, 0, -0.1)), mat="wood", bevel=0)
    elif s == "power":
        rod(p, (L * 0.1, 0, 0.1), (L * 0.1, 0, H), 0.04, mat="wood", segs=6)
        rod(p, (L * 0.1, 0, 0.6), (-L * 0.35, 0, 0.55), 0.025, mat="wood", segs=5)
    elif s == "rack":
        p.box((L * 0.6, W * 0.8, 0.03), T((-L * 0.05, 0, 0.25)), mat="wood", bevel=0)
        sack(p, -L * 0.3, 0.15, 0.15, 0.3) if coin(p) else p.box((0.3, 0.3, 0.25), T((-L * 0.3, 0.1, 0.38)), mat="wood", bevel=0)
    else:
        p.plate([(L * 0.08, 0.65), (L * 0.08, H - 0.1), (-L * J(p, 0.32, 0.08), 0.62)], 0.01, mat="cloth", bevel=0)
        p.plate([(L * 0.12, 0.6), (L * 0.12, H - 0.2), (L * 0.42, 0.35)], 0.01, mat="paint", bevel=0)


def _boat_launch(p, s, L, W, H):  # motor launch with a cabin
    if s == "body":
        hull(p, L, W, 0.35, mat="paint", sheer=0.35, flat=True)
    elif s == "running":
        rod(p, (-L * 0.45, 0, -0.1), (-L * 0.52, 0, -0.35), 0.02, mat="steel", segs=5)
        for i in range(3):
            p.box((0.1, 0.015, 0.06), T((-L * 0.52, 0, -0.35)) @ M(rot=(i * 120, 0, 0)) @ T((0, 0, 0.04)), mat="brass", bevel=0)
    elif s == "power":
        p.box((0.4, W * 0.5, 0.3), T((-L * 0.25, 0, 0.45)), mat="iron", bevel=0)
        flue(p, -L * 0.25, 0, 0.6, 1.0, 0.04, mat="steel")
    elif s == "rack":
        p.box((L * 0.6, W * 0.85, 0.03), T((0, 0, 0.3)), mat="wood", bevel=0)
    else:
        p.box((0.7, W * 0.75, 0.45), T((L * 0.12, 0, 0.55)), mat="shell", bevel=0.05)
        p.box((0.02, W * 0.6, 0.18), T((L * 0.12 + 0.35, 0, 0.65)), mat="glass", bevel=0)
        p.box((0.8, W * 0.85, 0.04), T((L * 0.12, 0, 0.8 + J(p, 0.02, 0.5))), mat="paint", bevel=0)


def _boat_paddle(p, s, L, W, H):  # paddle steamer
    if s == "body":
        hull(p, L, W, 0.35, mat="wood_dark", sheer=0.35, flat=True)
    elif s == "running":
        for y in (-W / 2 - 0.1, W / 2 + 0.1):
            m = T((-L * 0.05, y, 0.2)) @ M(rot=(90, 0, 0))
            p.ring(0.45, 0.04, m, mat="iron", segs=12)
            for i in range(4):
                p.box((0.9, 0.18, 0.03), T((-L * 0.05, y, 0.2)) @ M(rot=(0, i * 45, 0)), mat="wood", bevel=0)
    elif s == "power":
        boiler(p, -L * 0.05, 0, 0.3, J(p, 0.28, 0.08), 0.5)
    elif s == "rack":
        p.box((L * 0.7, W * 0.85, 0.03), T((0, 0, 0.3)), mat="wood", bevel=0)
        for y in (-W * 0.45, W * 0.45):
            p.box((L * 0.75, 0.02, 0.02), T((0, y, 0.55)), mat="brass", bevel=0)
    else:
        flue(p, -L * 0.05, 0, 1.1, 1.8, 0.08, mat="iron")
        p.ball(0.06, T((L * 0.35, 0, 0.5)), mat="glow", segs=(6, 4))


def _boat_hydrofoil(p, s, L, W, H):  # hydrofoil skiff
    if s == "body":
        hull(p, L, W, 0.25, mat="body", sheer=0.35, segs=12)
    elif s == "running":
        for x in (-L * 0.35, L * 0.3):
            for y in (-W * 0.35, W * 0.35):
                rod(p, (x, y, 0.0), (x, y * 1.3, -0.45), 0.025, mat="shell_dark", segs=6)
            p.box((0.25, W * 1.0, 0.02), T((x, 0, -0.45)), mat="shell_dark", bevel=0)
    elif s == "power":
        p.ring(0.18, 0.04, T((-L * 0.5, 0, 0.35)) @ M(rot=(0, 90, 0)), mat="shell_dark", segs=10)
        p.ball(0.06, T((-L * 0.5, 0, 0.35)), mat="glow", segs=(6, 4))
    elif s == "rack":
        p.box((L * 0.4, W * 0.6, 0.15), T((-L * 0.05, 0, 0.35)), mat="shell", bevel=0.2)
    else:
        p.box((0.5, W * 0.7, 0.02), M(loc=(L * 0.15, 0, 0.55), rot=(0, -25, 0)), mat="glass", bevel=0)
        p.box((L * 0.9, 0.01, 0.02), T((0, -W / 2, 0.25)), mat="glow", bevel=0)


def _boat_waste(p, s, L, W, H):  # oil-drum pontoon raft with an outboard
    if s == "body":
        for y in (-W * 0.35, W * 0.35):
            for x in (-L * 0.25, L * 0.25):
                p.cyl(0.25, 0.25, L * 0.45, T((x - L * 0.225, y, 0.0)) @ M(rot=(0, 90, 0)), mat="paint" if x > 0 else "rust", segs=10)
    elif s == "running":
        p.box((L * 0.9, W * 1.0, 0.04), T((0, 0, 0.28)), mat="wood", bevel=0, noise=0.01)
    elif s == "power":
        p.box((0.25, 0.2, 0.3), T((-L * 0.5, 0, 0.45)), mat="iron", bevel=0)
        rod(p, (-L * 0.5, 0, 0.3), (-L * 0.55, 0, -0.3), 0.025, mat="steel", segs=5)
    elif s == "rack":
        p.cyl(0.2, 0.2, 0.45, T((L * 0.2, 0, 0.3)), mat="rust", segs=8)
    else:
        rod(p, (0, 0, 0.3), (0, 0, J(p, 1.6, 0.1)), 0.03, mat="steel", segs=5)
        p.plate([(0.02, 0.6), (0.02, 1.5), (-0.6, 0.65)], 0.01, mat="cloth", bevel=0)
        wire(p, 0, 0, 0.6, 0.04)


def _boat_ancient(p, s, L, W, H):  # stone reed-shaped barque with a rune prow
    if s == "body":
        hull(p, L, W, 0.25, mat="stone", sheer=0.3, segs=8)
    elif s == "running":
        p.tube([(L * 0.45, 0, 0.2), (L * 0.55, 0, 0.5), (L * 0.5, 0, 0.75)], 0.06, mat="stone", segs=6)
        p.tube([(-L * 0.45, 0, 0.2), (-L * 0.55, 0, 0.55)], 0.06, mat="stone", segs=6)
    elif s == "power":
        p.ball(0.1, T((L * 0.5, 0, 0.8)), mat="glow", segs=(6, 4))
    elif s == "rack":
        p.box((0.6, W * 0.5, 0.4), T((0, 0, 0.45)), mat="stone_dark", bevel=0.15)
    else:
        p.box((L * 0.8, 0.02, 0.03), T((0, -W * 0.5, 0.25)), mat="glow", bevel=0)
        p.box((0.06, 0.06, J(p, 0.6, 0.15)), T((-L * 0.25, 0, 0.6)), mat="stone", bevel=0.1)


BOAT = {"Primal": (_boat_primal, 3.0, 0.6, 0.6), "Agrarian": (_boat_raft, 2.6, 1.4, 1.0), "Mercantile": (_boat_sail, 3.4, 1.2, 2.6),
        "Industrial": (_boat_launch, 3.4, 1.3, 1.2), "Steampunk": (_boat_paddle, 3.6, 1.3, 2.0), "Future": (_boat_hydrofoil, 3.4, 1.2, 1.0),
        "Wasteland": (_boat_waste, 2.6, 1.6, 1.6), "Ancient": (_boat_ancient, 3.2, 1.0, 1.0)}
function("Boat", "Vehicle", VEH, "machine")(dispatch(BOAT))


# ================================================================ Minecart
def _mc_basic(p, s, L, W, H, era):
    tub = {"Primal": "rope", "Agrarian": "wood", "Mercantile": "wood_dark", "Industrial": "steel", "Steampunk": "brass", "Wasteland": "rust"}[era]
    r = 0.15
    z = r + 0.05
    if s == "body":
        if era == "Primal":  # drag basket on skids
            p.lathe([(0, 0), (W * 0.45, 0.05), (W * 0.5, 0.4), (W * 0.52, 0.45)], T((0, 0, 0.08)) @ M(scale=(L / W, 1, 1)), mat="rope", segs=10)
        else:
            p.box((L * 0.85, W * 0.85, 0.06), T((0, 0, z + 0.03)), mat=tub, bevel=0)
            for y in (-W * 0.47, W * 0.47):
                p.box((L * 0.95, 0.04, 0.45), M(loc=(0, y, z + 0.27), rot=(math.copysign(8, y), 0, 0)), mat=tub, bevel=0)
            for x in (-L * 0.47, L * 0.47):
                p.box((0.04, W * 0.95, 0.45), T((x, 0, z + 0.27)), mat=tub, bevel=0)
    elif s == "running":
        if era == "Primal":
            for y in (-W * 0.3, W * 0.3):
                p.tube([(-L * 0.5, y, 0.03), (L * 0.4, y, 0.03), (L * 0.55, y, 0.15)], 0.03, mat="wood", segs=5)
        else:
            rim = "wood" if era == "Agrarian" else "iron"
            for x in (-L * 0.3, L * 0.3):
                for y in (-W * 0.42, W * 0.42):
                    p.cyl(r, r, 0.05, T((x, y, r)) @ M(rot=(90, 0, 0)) @ T((0, 0, -0.025)), mat=rim, segs=10)
                rod(p, (x, -W * 0.42, r), (x, W * 0.42, r), 0.02, mat="iron", segs=5)
    elif s == "power":
        if era == "Steampunk":
            p.cyl(0.15, 0.15, 0.4, T((L * 0.55, 0, z)), mat="copper", segs=10)
            p.ball(0.15, T((L * 0.55, 0, z + 0.4)), mat="copper", segs=(8, 4))
            p.ball(0.04, T((L * 0.55, -0.15, z + 0.2)), mat="glow", segs=(5, 3))
        else:
            p.tube([(L * 0.48, 0, z + 0.2), (L * 0.6, 0, z + 0.15), (L * 0.68, 0, z + J(p, 0.1, 0.5))], 0.012, mat="iron" if era not in ("Primal", "Agrarian") else "rope", segs=4)
    elif s == "rack":  # ore heap
        p.ball(1.0, M(loc=(0, 0, z + 0.4), scale=(L * 0.42, W * 0.4, J(p, 0.18, 0.2))), mat="stone_dark", segs=(8, 5), noise=0.06)
    else:
        if era in ("Industrial", "Steampunk"):
            for x in (-L * 0.25, 0, L * 0.25):
                p.box((0.03, W, 0.03), T((x, 0, z + 0.48)), mat="iron", bevel=0)
        elif era == "Wasteland":
            patch(p, 0.3, 0.15, T((0, -W * 0.5, z + 0.25)), mat="paint")
        else:
            p.box((0.05, 0.02, 0.2), T((L * 0.3, -W * 0.5, z + 0.25)), mat="iron" if era != "Primal" else "bone", bevel=0)


def _mc_future(p, s, L, W, H):  # maglev pod
    z = 0.3
    if s == "body":
        p.box((L, W, 0.45), T((0, 0, z + 0.22)), mat="body", bevel=0.35, bevel_seg=2)
    elif s == "running":
        for y in (-W * 0.35, W * 0.35):
            p.box((L * 0.9, 0.12, 0.08), T((0, y, z - 0.05)), mat="shell_dark", bevel=0.2)
            p.box((L * 0.85, 0.08, 0.01), T((0, y, z - 0.1)), mat="glow", bevel=0)
    elif s == "power":
        p.box((0.02, W * 0.6, 0.08), T((L * 0.5, 0, z + 0.25)), mat="glow", bevel=0)
    elif s == "rack":
        p.box((L * 0.8, W * 0.8, 0.02), M(loc=(0, 0, z + 0.48), rot=(J(p, 0, 1) * 3, 0, 0)), mat="glass", bevel=0)
    else:
        p.ball(1.0, M(loc=(0, 0, z + 0.45), scale=(L * 0.35, W * 0.35, 0.12)), mat="stone_dark", segs=(8, 4))


def _mc_ancient(p, s, L, W, H):
    z = 0.25
    if s == "body":
        p.box((L, W, 0.45), T((0, 0, z + 0.22)), mat="stone", bevel=0.15)
    elif s == "running":
        for y in (-W * 0.35, W * 0.35):
            p.box((L * 0.8, 0.12, 0.12), T((0, y, z - 0.08)), mat="stone_dark", bevel=0.2)
    elif s == "power":
        p.box((L * 0.7, 0.02, 0.03), T((0, -W * 0.5, z + 0.2)), mat="glow", bevel=0)
    elif s == "rack":
        p.ball(1.0, M(loc=(0, 0, z + 0.45), scale=(L * 0.35, W * 0.35, J(p, 0.15, 0.2))), mat="glow", segs=(6, 4))
    else:
        for x in (-L * 0.45, L * 0.45):
            p.box((0.08, W * 0.8, 0.1), T((x, 0, z + 0.5)), mat="stone_dark", bevel=0.1)


MINECART = {"Primal": (lambda p, s, L, W, H: _mc_basic(p, s, L, W, H, "Primal"), 1.2, 0.8, 0.6),
            "Agrarian": (lambda p, s, L, W, H: _mc_basic(p, s, L, W, H, "Agrarian"), 1.2, 0.8, 0.8),
            "Mercantile": (lambda p, s, L, W, H: _mc_basic(p, s, L, W, H, "Mercantile"), 1.3, 0.85, 0.8),
            "Industrial": (lambda p, s, L, W, H: _mc_basic(p, s, L, W, H, "Industrial"), 1.4, 0.9, 0.8),
            "Steampunk": (lambda p, s, L, W, H: _mc_basic(p, s, L, W, H, "Steampunk"), 1.4, 0.9, 0.9),
            "Future": (_mc_future, 1.5, 0.9, 0.8),
            "Wasteland": (lambda p, s, L, W, H: _mc_basic(p, s, L, W, H, "Wasteland"), 1.3, 0.85, 0.8),
            "Ancient": (_mc_ancient, 1.4, 0.9, 0.8)}
function("Minecart", "Vehicle", VEH, "machine")(dispatch(MINECART))


# ================================================================ SteamCar (era's self-moving car)
def _sc_primal(p, s, L, W, H):  # log rollers under a platform pushed along
    if s == "body":
        p.box((L, W, 0.06), T((0, 0, 0.33)), mat="wood", bevel=0, noise=0.02)
    elif s == "running":
        for x in (-L * 0.35, 0, L * 0.35):
            rod(p, (x, -W * 0.6, 0.15), (x, W * 0.6, 0.15), 0.15, mat="bark", segs=8)
    elif s == "power":
        for y in (-W * 0.35, W * 0.35):
            p.tube([(-L * 0.5, y, 0.35), (-L * 0.5 - J(p, 0.7, 0.1), y, 0.9)], 0.03, mat="wood", segs=5)
    elif s == "rack":
        p.box((0.8, 0.6, 0.6), M(loc=(0, 0, 0.66), rot=(0, 0, 8)), mat="stone", bevel=0.1, noise=0.04)
    else:
        p.tube([(-0.4, -W * 0.4, 0.36), (0, 0, 1.0), (0.4, W * 0.4, 0.36)], 0.015, mat="rope", segs=3)


def _sc_sail(p, s, L, W, H, era):  # wind cart (Agrarian) / land yacht (Mercantile)
    r = 0.3 if era == "Agrarian" else 0.35
    z = r + 0.1
    if s == "body":
        p.box((L, W * 0.7, 0.08), T((0, 0, z)), mat="wood" if era == "Agrarian" else "wood_dark", bevel=0)
    elif s == "running":
        if era == "Agrarian":
            wheels(p, (0.0,), (-W / 2, W / 2), r, rim="wood", hub="wood", spokes=6)
        else:
            wheels(p, (-L * 0.3,), (-W / 2, W / 2), r, rim="iron", hub="wood", spokes=8)
            wheel(p, r * 0.8, (L * 0.45, 0, r * 0.8), rim="iron", hub="wood", spokes=6)
    elif s == "power":
        rod(p, (0, 0, z), (0, 0, H), 0.04, mat="wood", segs=6)
        rod(p, (0, 0, z + 0.4), (-L * 0.45, 0, z + 0.4), 0.025, mat="wood", segs=5)
    elif s == "rack":
        bales(p, -L * 0.3, L * 0.3, 0, z, 2, r=0.2)
    else:
        if era == "Agrarian":  # square mat sail
            p.box((0.04, W * 0.9, H * 0.55), T((0.05, 0, z + 0.45 + H * 0.27)), mat="rope", bevel=0)
        else:
            p.plate([(-0.02, z + 0.45), (-0.02, H - 0.05), (-L * J(p, 0.42, 0.08), z + 0.42)], 0.01, mat="cloth", bevel=0)


def _sc_auto(p, s, L, W, H):  # early motor car
    r = 0.32
    if s == "body":
        p.box((L * 0.85, W * 0.9, 0.35), T((0, 0, r + 0.3)), mat="paint", bevel=0.08)
        p.box((L * 0.35, W * 0.8, 0.3), T((L * 0.3, 0, r + 0.6)), mat="paint", bevel=0.1)
    elif s == "running":
        tyres(p, (-L * 0.32, L * 0.32), (-W / 2, W / 2), r, 0.16, hub="steel")
    elif s == "power":
        p.box((0.05, W * 0.5, 0.25), T((L * 0.47, 0, r + 0.6)), mat="steel", bevel=0)
        for y in (-W * 0.3, W * 0.3):
            p.cyl(0.08, 0.08, 0.06, T((L * 0.45, y, r + 0.55)) @ M(rot=(0, 90, 0)), mat="glass", segs=8)
    elif s == "rack":
        p.box((0.3, W * 0.8, 0.35), T((-L * 0.15, 0, r + 0.65)), mat="leather", bevel=0.1)
    else:
        p.box((L * 0.45, W * 0.9, 0.03), T((-L * 0.1, 0, H)), mat="cloth", bevel=0)
        for x in (-L * 0.3, L * 0.1):
            rod(p, (x, -W * 0.44, r + 0.5), (x, -W * 0.44, H), 0.015, mat="steel", segs=4)
        p.box((0.02, W * 0.8, 0.3), M(loc=(L * 0.13, 0, r + 0.95), rot=(0, -15, 0)), mat="glass", bevel=0)


def _sc_steam(p, s, L, W, H):  # steam carriage
    r = 0.42
    if s == "body":
        p.box((L * 0.8, W * 0.85, 0.15), T((0, 0, r + 0.15)), mat="wood_dark", bevel=0.05)
    elif s == "running":
        wheels(p, (-L * 0.3, L * 0.3), (-W / 2, W / 2), r, rim="iron", hub="brass", spokes=8, t=0.05, axle="iron")
    elif s == "power":
        p.cyl(0.32, 0.32, 0.7, T((L * 0.3, 0, r + 0.25)) @ M(rot=(0, 90, 0)) @ T((0, 0, -0.35)), mat="brass", segs=12)
        p.ball(0.05, T((L * 0.3 + 0.36, 0, r + 0.25)), mat="glow", segs=(6, 4))
    elif s == "rack":
        p.box((0.35, W * 0.8, 0.4), T((-L * 0.2, 0, r + 0.42)), mat="leather", bevel=0.1)
        p.box((0.1, W * 0.8, 0.5), T((-L * 0.35, 0, r + 0.5)), mat="leather", bevel=0.1)
    else:
        flue(p, L * 0.45, 0, r + 0.55, H, J(p, 0.07, 0.15), mat="iron")
        gauge(p, L * 0.15, -W * 0.43, r + 0.35, 0.05)


def _sc_hover(p, s, L, W, H):  # hover car
    z = 0.45
    if s == "body":
        p.ball(1.0, M(loc=(0, 0, z + 0.2), scale=(L * 0.5, W * 0.5, 0.25)), mat="body", segs=(14, 6))
    elif s == "running":
        for x in (-L * 0.3, L * 0.3):
            for y in (-W * 0.35, W * 0.35):
                p.cyl(0.15, 0.17, 0.06, T((x, y, z - 0.12)), mat="shell_dark", segs=10)
                p.cyl(0.12, 0.12, 0.01, T((x, y, z - 0.13)), mat="glow", segs=10)
    elif s == "power":
        p.box((0.05, W * 0.6, 0.06), T((-L * 0.5, 0, z + 0.2)), mat="glow", bevel=0)
    elif s == "rack":
        p.box((0.5, W * 0.6, 0.15), T((-L * 0.05, 0, z + 0.4)), mat="shell_dark", bevel=0.3)
    else:
        p.ball(1.0, M(loc=(L * 0.05, 0, z + 0.45), scale=(L * 0.25, W * 0.35, J(p, 0.25, 0.1))), mat="glass", segs=(12, 5))


def _sc_waste(p, s, L, W, H):  # stripped buggy with a roll cage
    r = 0.35
    if s == "body":
        p.box((L * 0.9, W * 0.7, 0.15), T((0, 0, r + 0.15)), mat="rust", bevel=0)
    elif s == "running":
        tyres(p, (-L * 0.33, L * 0.33), (-W / 2, W / 2), r, 0.2, hub="rust")
    elif s == "power":
        p.box((0.45, W * 0.5, 0.35), T((-L * 0.3, 0, r + 0.4)), mat="iron", bevel=0)
        flue(p, -L * 0.45, W * 0.2, r + 0.4, r + 1.0, 0.04, mat="rust")
    elif s == "rack":
        p.box((0.35, 0.4, 0.4), T((L * 0.05, 0, r + 0.42)), mat="leather", bevel=0.1)
        p.cyl(0.15, 0.15, 0.4, T((L * 0.35, W * 0.2, r + 0.23)), mat="paint", segs=8)
    else:
        for x in (-L * 0.1, L * 0.25):
            p.tube([(x, -W * 0.35, r + 0.22), (x, -W * 0.3, H), (x, W * 0.3, H), (x, W * 0.35, r + 0.22)], 0.025, mat="steel", segs=5)
        rod(p, (-L * 0.1, 0, H), (L * 0.25, 0, H + J(p, 0.0, 1) * 0.05), 0.025, mat="steel", segs=5)


def _sc_ancient(p, s, L, W, H):  # floating stone chariot
    z = 0.4
    if s == "body":
        p.box((L * 0.8, W * 0.8, 0.3), T((0, 0, z + 0.15)), mat="stone", bevel=0.2)
    elif s == "running":
        for x in (-L * 0.3, L * 0.3):
            p.ring(0.3, 0.06, T((x, -W * 0.45, z)) @ M(rot=(90, 0, 0)), mat="stone_dark", segs=8)
            p.ring(0.3, 0.06, T((x, W * 0.45, z)) @ M(rot=(90, 0, 0)), mat="stone_dark", segs=8)
    elif s == "power":
        for x in (-L * 0.3, L * 0.3):
            for y in (-W * 0.45, W * 0.45):
                p.ball(0.08, T((x, y, z)), mat="glow", segs=(6, 4))
    elif s == "rack":
        p.box((0.2, W * 0.7, 0.6), T((-L * 0.3, 0, z + 0.6)), mat="stone", bevel=0.15)
    else:
        p.box((L * 0.7, 0.02, 0.03), T((0, -W * 0.41, z + 0.2)), mat="glow", bevel=0)
        p.lathe([(0, 0), (0.08, 0.05), (0, J(p, 0.3, 0.15))], T((L * 0.42, 0, z + 0.3)), mat="gold", segs=4)


STEAMCAR = {"Primal": (_sc_primal, 2.2, 1.2, 1.0), "Agrarian": (lambda p, s, L, W, H: _sc_sail(p, s, L, W, H, "Agrarian"), 2.0, 1.2, 2.4),
            "Mercantile": (lambda p, s, L, W, H: _sc_sail(p, s, L, W, H, "Mercantile"), 2.6, 1.4, 3.0),
            "Industrial": (_sc_auto, 2.8, 1.4, 1.6), "Steampunk": (_sc_steam, 2.8, 1.4, 2.2), "Future": (_sc_hover, 2.8, 1.4, 1.4),
            "Wasteland": (_sc_waste, 2.6, 1.4, 1.6), "Ancient": (_sc_ancient, 2.4, 1.3, 1.3)}
function("SteamCar", "Vehicle", VEH, "machine")(dispatch(STEAMCAR))


# ================================================================ Airship (origin under the gondola)
def envelope(p, R, Lx, z, mat="cloth", segs=12, round_=False):
    if round_:
        p.lathe([(0, z), (R * 0.4, z + R * 0.1), (R * 0.9, z + R * 0.7), (R, z + R * 1.2), (R * 0.8, z + R * 1.8), (0, z + R * 2.05)], mat=mat, segs=segs)
    else:
        p.lathe([(0, -Lx / 2), (R * 0.6, -Lx * 0.4), (R, -Lx * 0.1), (R * 0.95, Lx * 0.2), (R * 0.5, Lx * 0.42), (0, Lx / 2)],
                T((0, 0, z)) @ M(rot=(0, 90, 0)), mat=mat, segs=segs)


def lines(p, pts_a, pts_b, mat="rope", r=0.008):
    for a, b in zip(pts_a, pts_b):
        p.tube([a, b], r, mat=mat, segs=3)


def _as_kite(p, s, L, W, H):  # kite raft: hide kite over a reed raft
    if s == "body":
        for i in range(5):
            y = -W / 2 + W * (i + 0.5) / 5
            rod(p, (-L / 2, y, 0.05), (L / 2, y, 0.05), 0.05, mat="wood", segs=6)
    elif s == "running":
        rod(p, (-L * 0.4, -W / 2, 0.12), (-L * 0.4, W / 2, 0.12), 0.03, mat="wood", segs=5)
        rod(p, (L * 0.4, -W / 2, 0.12), (L * 0.4, W / 2, 0.12), 0.03, mat="wood", segs=5)
    elif s == "power":
        lines(p, [(0, 0, 0.1)], [(L * 0.3, 0, H * 0.75)])
    elif s == "rack":
        bales(p, -L * 0.3, L * 0.1, 0, 0.1, 2, r=0.18, mat="hide")
    else:
        m = T((L * 0.3, 0, H * 0.8)) @ M(rot=(0, -20, 0))
        p.plate([(-0.8, 0), (0, J(p, 0.9, 0.1)), (0.8, 0), (0, -0.6)], 0.02, m, mat="hide", bevel=0)
        rod(p, tuple(m @ Vector((-0.8, 0, 0))), tuple(m @ Vector((0.8, 0, 0))), 0.02, mat="wood", segs=4)


def _as_lantern(p, s, L, W, H):  # big sky lantern with a hanging basket
    R = H * 0.25
    zb = 1.2
    if s == "body":
        p.lathe([(0, 0), (W * 0.45, 0.02), (W * 0.5, 0.45)], mat="wood", segs=10)
    elif s == "running":
        p.ring(R * 0.5, 0.03, T((0, 0, zb)), mat="wood", segs=10)
    elif s == "power":
        p.lathe([(0, zb - 0.1), (0.15, zb - 0.05), (0.18, zb + 0.05)], mat="iron", segs=8)
        flame(p, 0, 0, zb + 0.05, 0.12, mat=lit(p), segs=6)
    elif s == "rack":
        lines(p, [(W * 0.45 * math.cos(a), W * 0.45 * math.sin(a), 0.45) for a in (0, 2.1, 4.2)],
              [(R * 0.5 * math.cos(a), R * 0.5 * math.sin(a), zb) for a in (0, 2.1, 4.2)])
    else:
        p.lathe([(R * 0.5, zb), (R * 0.9, zb + R * 0.8), (R, zb + R * 2), (R * 0.85, zb + R * 3), (0, zb + R * J(p, 3.3, 0.06))], mat="paint", segs=10)


def _as_balloon(p, s, L, W, H, era):
    R = H * 0.24
    zb = 1.3
    basket = {"Mercantile": "wood", "Wasteland": "rust"}[era]
    if s == "body":
        p.lathe([(0, 0), (W * 0.4, 0.02), (W * 0.42, 0.9)], mat=basket, segs=8 if era == "Wasteland" else 10)
    elif s == "running":
        p.ring(W * 0.43, 0.025, T((0, 0, 0.9)), mat="leather" if era == "Mercantile" else "steel", segs=10)
    elif s == "power":
        p.cyl(0.12, 0.15, 0.25, T((0, 0, zb - 0.05)), mat="iron" if era == "Mercantile" else "rust", segs=8)
        flame(p, 0, 0, zb + 0.2, 0.1, mat=lit(p), segs=6)
    elif s == "rack":
        lines(p, [(W * 0.4 * math.cos(a), W * 0.4 * math.sin(a), 0.9) for a in (0.4, 2.0, 3.6, 5.2)],
              [(R * 0.4 * math.cos(a), R * 0.4 * math.sin(a), zb + R * 0.1) for a in (0.4, 2.0, 3.6, 5.2)])
        sack(p, W * 0.45, 0, 0.1, 0.25)
    else:
        envelope(p, R, 0, zb, mat="cloth" if era == "Mercantile" else "paint", segs=12, round_=True)
        if era == "Wasteland":
            patch(p, 0.5, 0.4, T((0, -R * 1.0, zb + R * J(p, 1.2, 0.1))), mat="cloth")
        else:
            for k in (0.7, 1.4):
                p.ring(R * (0.88 if k < 1 else 0.96), 0.015, T((0, 0, zb + R * k)), mat="paint", segs=12)


def _as_biplane(p, s, L, W, H):  # parked biplane
    z = 0.55
    if s == "body":
        p.lathe([(0, -L / 2), (0.18, -L * 0.3), (0.32, 0), (0.3, L * 0.3), (0.2, L * 0.48), (0, L / 2)], T((0, 0, z)) @ M(rot=(0, 90, 0)), mat="paint", segs=8)
    elif s == "running":
        for y in (-0.4, 0.4):
            p.ring(0.2, 0.06, T((L * 0.2, y, 0.2)) @ M(rot=(90, 0, 0)), mat="rubber", segs=10, square=False)
            rod(p, (L * 0.2, y, 0.2), (L * 0.15, y * 0.5, z - 0.2), 0.02, mat="steel", segs=4)
        rod(p, (-L * 0.45, 0, 0.05), (-L * 0.42, 0, z - 0.1), 0.02, mat="steel", segs=4)
    elif s == "power":
        p.cyl(0.25, 0.25, 0.2, T((L * 0.5, 0, z)) @ M(rot=(0, 90, 0)), mat="steel", segs=10)
        p.box((0.04, 0.12, J(p, 1.6, 0.08)), T((L * 0.5 + 0.22, 0, z)), mat="wood", bevel=0)
    elif s == "rack":  # wings and struts
        for zz in (z + 0.1, z + 0.8):
            p.box((0.7, W, 0.05), T((L * 0.15, 0, zz)), mat="cloth", bevel=0)
        for y in (-W * 0.35, W * 0.35):
            rod(p, (L * 0.15, y, z + 0.1), (L * 0.15, y, z + 0.8), 0.015, mat="wood", segs=4)
    else:  # tail
        p.box((0.5, 1.2, 0.04), T((-L * 0.45, 0, z + 0.1)), mat="cloth", bevel=0)
        p.plate([(-L * 0.5, z), (-L * 0.3, z), (-L * 0.48, z + 0.55)], 0.03, mat="paint", bevel=0)


def _as_zeppelin(p, s, L, W, H):  # small dirigible with a brass gondola
    zb = H * 0.55
    R = H * 0.25
    if s == "body":
        p.box((L * 0.35, W * 0.4, 0.45), T((0, 0, 0.3)), mat="brass", bevel=0.1)
        p.box((L * 0.3, 0.01, 0.15), T((0, -W * 0.2, 0.4)), mat="glass", bevel=0)
    elif s == "running":
        for x in (-L * 0.1, L * 0.1):
            lines(p, [(x, -W * 0.2, 0.52), (x, W * 0.2, 0.52)], [(x * 2, -R * 0.4, zb - R * 0.9), (x * 2, R * 0.4, zb - R * 0.9)], mat="steel")
    elif s == "power":
        for y in (-W * 0.3, W * 0.3):
            p.cyl(0.08, 0.08, 0.3, T((-L * 0.2, y, 0.35)) @ M(rot=(0, 90, 0)), mat="copper", segs=8)
            p.box((0.02, 0.06, J(p, 0.45, 0.1)), T((-L * 0.2 - 0.16, y, 0.35)), mat="wood", bevel=0)
        p.ball(0.04, T((L * 0.17, -W * 0.2, 0.3)), mat="glow", segs=(5, 3))
    elif s == "rack":
        for zz in (-0.25, 0.25):
            p.plate([(-L * 0.5, 0), (-L * 0.35, 0), (-L * 0.5, 0.55)], 0.03, T((0, 0, zb + zz * 0 + 0.0)) @ M(rot=(0 if zz < 0 else 180, 0, 0)), mat="paint", bevel=0)
    else:
        envelope(p, R, L, zb, mat="cloth", segs=12)
        p.ring(R * 1.0, 0.02, T((L * 0.1, 0, zb)) @ M(rot=(0, 90, 0)), mat="brass", segs=12)


def _as_future(p, s, L, W, H):  # floating skiff with gravity rings
    z = 0.8
    if s == "body":
        p.ball(1.0, M(loc=(0, 0, z), scale=(L * 0.5, W * 0.45, 0.3)), mat="body", segs=(14, 6))
    elif s == "running":
        for x in (-L * 0.3, L * 0.3):
            p.ring(0.35, 0.05, T((x, 0, z - 0.32)), mat="shell_dark", segs=12)
    elif s == "power":
        for x in (-L * 0.3, L * 0.3):
            p.ring(0.33, 0.015, T((x, 0, z - 0.36)), mat="glow", segs=12)
    elif s == "rack":
        p.box((L * 0.3, W * 0.5, 0.2), T((-L * 0.1, 0, z + 0.3)), mat="shell_dark", bevel=0.3)
    else:
        p.ball(1.0, M(loc=(L * 0.15, 0, z + 0.25), scale=(L * 0.2, W * 0.3, J(p, 0.25, 0.1))), mat="glass", segs=(10, 5))


def _as_ancient(p, s, L, W, H):  # floating stone barge held up by a rune crystal
    z = 0.9
    if s == "body":
        p.box((L * 0.8, W * 0.7, 0.35), T((0, 0, z)), mat="stone", bevel=0.2)
    elif s == "running":
        p.lathe([(0.2, z - 0.15), (0.0, z - J(p, 0.8, 0.1))], mat="stone_dark", segs=6)
    elif s == "power":
        p.lathe([(0, z + 0.2), (0.25, z + 0.7), (0, z + 1.3)], mat="glow", segs=6)
    elif s == "rack":
        for x in (-L * 0.35, L * 0.35):
            p.box((0.15, 0.15, 0.6), T((x, 0, z + 0.45)), mat="stone", bevel=0.1)
    else:
        for y in (-W * 0.36, W * 0.36):
            p.box((L * 0.7, 0.02, 0.03), T((0, y, z)), mat="glow", bevel=0)


AIRSHIP = {"Primal": (_as_kite, 2.0, 1.2, 3.0), "Agrarian": (_as_lantern, 1.2, 1.0, 4.0),
           "Mercantile": (lambda p, s, L, W, H: _as_balloon(p, s, L, W, H, "Mercantile"), 1.4, 1.2, 4.6),
           "Industrial": (_as_biplane, 3.4, 4.0, 1.6), "Steampunk": (_as_zeppelin, 4.0, 1.4, 3.2), "Future": (_as_future, 3.0, 1.6, 1.4),
           "Wasteland": (lambda p, s, L, W, H: _as_balloon(p, s, L, W, H, "Wasteland"), 1.4, 1.2, 4.4),
           "Ancient": (_as_ancient, 2.6, 1.4, 2.2)}
function("Airship", "Vehicle", VEH, "machine")(dispatch(AIRSHIP))


# ================================================================ Wheelbarrow
def _wb_litter(p, s, L, W, H):  # stretcher: two poles and a hide sling
    if s == "body":
        p.box((L * 0.55, W * 0.7, 0.02), T((0, 0, 0.5)), mat="hide", bevel=0, noise=0.03)
    elif s == "running":
        for x in (-L * 0.2, L * 0.2):
            rod(p, (x, -W * 0.4, 0.0), (x, -W * 0.4, 0.5), 0.02, mat="wood", segs=4)
            rod(p, (x, W * 0.4, 0.0), (x, W * 0.4, 0.5), 0.02, mat="wood", segs=4)
    elif s == "power":
        for y in (-W * 0.4, W * 0.4):
            rod(p, (-L / 2, y, 0.52), (L / 2, y, 0.52), 0.025, mat="wood", segs=5)
    elif s == "rack":
        p.ball(1.0, M(loc=(0, 0, 0.62), scale=(0.3, 0.2, J(p, 0.12, 0.2))), mat="cloth", segs=(6, 4))
    else:
        p.band(0.03, 0, h=0.04, m=T((L * 0.3, W * 0.4, 0.52)) @ M(rot=(0, 90, 0)))


def _wb_barrow(p, s, L, W, H, era):
    tray = {"Agrarian": "wood", "Mercantile": "wood_dark", "Industrial": "paint", "Steampunk": "brass", "Wasteland": "rust"}[era]
    r = 0.2
    two = era in ("Mercantile", "Steampunk")
    if s == "body":
        if era in ("Industrial", "Wasteland"):
            p.lathe([(0, 0), (W * 0.4, 0.02), (W * 0.55, 0.35)], T((L * 0.1, 0, 0.3)) @ M(scale=(1.3, 1, 1)), mat=tray, segs=8)
        else:
            p.box((L * 0.45, W * 0.8, 0.04), T((L * 0.1, 0, 0.35)), mat=tray, bevel=0)
            for y in (-W * 0.4, W * 0.4):
                p.box((L * 0.45, 0.03, 0.22), T((L * 0.1, y, 0.47)), mat=tray, bevel=0)
            p.box((0.03, W * 0.8, 0.25), T((L * 0.32, 0, 0.47)), mat=tray, bevel=0)
    elif s == "running":
        if two:
            wheels(p, (L * 0.15,), (-W * 0.5, W * 0.5), r * 1.3, rim="iron", hub="wood" if era == "Mercantile" else "brass", spokes=6)
        elif era == "Industrial":
            p.ring(r * 0.8, r * 0.25, T((L * 0.42, 0, r)) @ M(rot=(90, 0, 0)), mat="rubber", segs=12, square=False)
        else:
            wheel(p, r, (L * 0.42, 0, r), rim="iron" if era != "Agrarian" else "wood", hub="wood", spokes=6)
    elif s == "power":  # handles and legs
        for y in (-W * 0.3, W * 0.3):
            rod(p, (L * 0.42, y * 0.8, r), (-L / 2, y, J(p, 0.55, 0.05)), 0.02, mat="wood" if era not in ("Industrial", "Wasteland") else "steel", segs=5)
            if not two:
                rod(p, (-L * 0.15, y, 0.4), (-L * 0.15, y, 0.0), 0.018, mat="wood" if era != "Industrial" else "steel", segs=4)
    elif s == "rack":
        if era == "Steampunk":
            p.cyl(0.12, 0.12, 0.25, T((-L * 0.25, 0, 0.35)), mat="copper", segs=8)
            p.ball(0.03, T((-L * 0.25, -0.12, 0.45)), mat="glow", segs=(5, 3))
        else:
            p.ball(1.0, M(loc=(L * 0.1, 0, 0.55), scale=(L * 0.2, W * 0.3, J(p, 0.12, 0.2))), mat="stone_dark" if era != "Agrarian" else "cloth", segs=(7, 4), noise=0.05)
    else:
        if era == "Wasteland":
            wire(p, L * 0.1, 0, 0.45, 0.2)
        else:
            p.box((0.15, 0.02, 0.15), T((L * 0.1, -W * 0.42, 0.48)), mat="iron" if era != "Industrial" else "steel", bevel=0)


def _wb_future(p, s, L, W, H):  # follow-bot: tray on a rolling sphere with a sensor head
    if s == "body":
        p.box((L * 0.6, W * 0.7, 0.2), T((0, 0, 0.55)), mat="body", bevel=0.3, bevel_seg=2)
    elif s == "running":
        p.ball(0.22, T((0, 0, 0.22)), mat="shell_dark", segs=(10, 6))
    elif s == "power":
        p.ring(0.23, 0.01, T((0, 0, 0.22)), mat="glow", segs=10)
    elif s == "rack":
        p.box((0.35, 0.3, 0.25), T((-0.05, 0, 0.78)), mat="paint", bevel=0.1)
    else:
        p.ball(0.08, T((L * 0.3, 0, 0.7 + J(p, 0.03, 0.5))), mat="shell", segs=(8, 5))
        p.box((0.02, 0.1, 0.03), T((L * 0.3 + 0.08, 0, 0.72)), mat="glow", bevel=0)


def _wb_ancient(p, s, L, W, H):
    if s == "body":
        p.box((L * 0.6, W * 0.7, 0.2), T((0, 0, 0.5)), mat="stone", bevel=0.2)
    elif s == "running":
        p.ring(0.2, 0.05, T((L * 0.3, 0, 0.25)) @ M(rot=(90, 0, 0)), mat="stone_dark", segs=8)
    elif s == "power":
        p.ball(0.06, T((L * 0.3, 0, 0.25)), mat="glow", segs=(5, 3))
    elif s == "rack":
        p.box((0.3, 0.3, 0.2), M(loc=(0, 0, 0.7), rot=(0, 0, J(p, 15, 0.5))), mat="stone_dark", bevel=0.15)
    else:
        for y in (-W * 0.3, W * 0.3):
            rod(p, (-L * 0.25, y, 0.5), (-L * 0.5, y, 0.6), 0.025, mat="stone", segs=5)


WB = {"Primal": (_wb_litter, 2.0, 0.6, 0.6), "Agrarian": (lambda p, s, L, W, H: _wb_barrow(p, s, L, W, H, "Agrarian"), 1.4, 0.6, 0.7),
      "Mercantile": (lambda p, s, L, W, H: _wb_barrow(p, s, L, W, H, "Mercantile"), 1.4, 0.7, 0.7),
      "Industrial": (lambda p, s, L, W, H: _wb_barrow(p, s, L, W, H, "Industrial"), 1.4, 0.6, 0.7),
      "Steampunk": (lambda p, s, L, W, H: _wb_barrow(p, s, L, W, H, "Steampunk"), 1.4, 0.7, 0.7),
      "Future": (_wb_future, 1.0, 0.6, 0.9),
      "Wasteland": (lambda p, s, L, W, H: _wb_barrow(p, s, L, W, H, "Wasteland"), 1.4, 0.6, 0.7),
      "Ancient": (_wb_ancient, 1.2, 0.6, 0.7)}
function("Wheelbarrow", "Vehicle", VEH, "machine")(dispatch(WB))


# ================================================================ Palanquin
def _pq_chair(p, s, L, W, H, era):  # carrying chair (Primal) / bamboo sedan (Agrarian) / carved sedan (Mercantile)
    mat = {"Primal": "wood", "Agrarian": "wood", "Mercantile": "wood_dark"}[era]
    z = 0.55
    if s == "body":
        if era == "Mercantile":
            p.box((0.8, W * 0.8, 1.1), T((0, 0, z + 0.55)), mat=mat, bevel=0.05)
            p.box((0.02, W * 0.4, 0.4), T((0.41, 0, z + 0.7)), mat="paint", bevel=0)
        else:
            p.box((0.6, W * 0.7, 0.05), T((0, 0, z)), mat=mat, bevel=0)
            p.box((0.05, W * 0.7, 0.6), T((-0.28, 0, z + 0.3)), mat=mat, bevel=0)
    elif s == "running":  # rests / legs
        for x in (-0.3, 0.3):
            for y in (-W * 0.3, W * 0.3):
                rod(p, (x, y, 0), (x, y, z), 0.025, mat=mat, segs=4)
    elif s == "power":  # carrying poles
        for y in (-W * 0.45, W * 0.45):
            rod(p, (-L / 2, y, z + 0.3), (L / 2, y, z + 0.3), 0.035, mat=mat, segs=6)
    elif s == "rack":
        if era == "Mercantile":
            p.box((0.6, W * 0.6, 0.08), T((0, 0, z + 0.3)), mat="cloth", bevel=0)
        else:
            p.box((0.5, W * 0.6, 0.06), T((0, 0, z + 0.06)), mat="cloth" if era == "Agrarian" else "hide", bevel=0)
    else:
        if era == "Mercantile":
            p.lathe([(W * 0.5, 0), (W * 0.4, 0.15), (0.05, 0.35), (0, J(p, 0.42, 0.1))], T((0, 0, z + 1.1)) @ M(scale=(0.8 / W, 1, 1)), mat="paint", segs=4)
        elif era == "Agrarian":  # canopy on four sticks
            for x in (-0.3, 0.3):
                for y in (-W * 0.35, W * 0.35):
                    rod(p, (x, y, z), (x, y, z + 1.0), 0.015, mat="wood", segs=4)
            p.box((0.75, W * 0.85, 0.03), M(loc=(0, 0, z + 1.0), rot=(0, J(p, 3, 1), 0)), mat="cloth", bevel=0)
        else:
            for i in range(3):
                p.box((0.02, 0.003, 0.25), M(loc=(-0.28, -W * 0.2 + i * W * 0.2, z + 0.7), rot=(0, (i - 1) * 15, 0)), mat="feather", bevel=0)


def _pq_rickshaw(p, s, L, W, H):  # rickshaw (Industrial)
    r = 0.55
    if s == "body":
        p.box((0.7, W * 0.8, 0.12), T((-0.2, 0, r + 0.1)), mat="paint", bevel=0.05)
        p.box((0.15, W * 0.8, 0.55), M(loc=(-0.5, 0, r + 0.4), rot=(0, -10, 0)), mat="leather", bevel=0.1)
    elif s == "running":
        wheels(p, (-0.2,), (-W / 2 - 0.05, W / 2 + 0.05), r, rim="steel", hub="steel", spokes=10, t=0.025, axle="steel")
    elif s == "power":
        for y in (-W * 0.35, W * 0.35):
            rod(p, (0.1, y, r + 0.12), (L / 2, y * 0.8, r - 0.1), 0.02, mat="wood", segs=5)
        rod(p, (L / 2, -W * 0.28, r - 0.1), (L / 2, W * 0.28, r - 0.1), 0.02, mat="wood", segs=5)
    elif s == "rack":
        p.box((0.5, W * 0.7, 0.1), T((-0.2, 0, r + 0.22)), mat="leather", bevel=0.1)
    else:  # folding hood
        for k in range(3):
            a = math.radians(20 + k * 25)
            p.tube([(-0.5 + 0.0, -W * 0.42, r + 0.4), (-0.5 + math.sin(a) * 0.5, -W * 0.42, r + 0.4 + math.cos(a) * 0.6),
                    (-0.5 + math.sin(a) * 0.5, W * 0.42, r + 0.4 + math.cos(a) * 0.6), (-0.5, W * 0.42, r + 0.4)], 0.012, mat="steel", segs=3)
        p.box((0.5, W * 0.85, 0.03), M(loc=(-0.3, 0, r + 1.0 + J(p, 0.02, 0.5)), rot=(0, 25, 0)), mat="cloth", bevel=0)


def _pq_steam(p, s, L, W, H):  # steam seat car: an armchair on a small steam chassis
    r = 0.3
    if s == "body":
        p.box((L * 0.7, W * 0.85, 0.12), T((0, 0, r + 0.1)), mat="iron", bevel=0.05)
    elif s == "running":
        wheels(p, (-L * 0.25, L * 0.25), (-W / 2, W / 2), r, rim="iron", hub="brass", spokes=8, axle="iron")
    elif s == "power":
        boiler(p, L * 0.25, 0, r + 0.16, J(p, 0.2, 0.08), 0.45)
    elif s == "rack":  # armchair
        p.box((0.5, W * 0.6, 0.15), T((-L * 0.15, 0, r + 0.35)), mat="leather", bevel=0.15)
        p.box((0.12, W * 0.6, 0.6), T((-L * 0.15 - 0.22, 0, r + 0.65)), mat="leather", bevel=0.15)
    else:
        flue(p, L * 0.25, 0, r + 0.85, r + 1.4, 0.05, mat="iron")
        p.lathe([(0, 0), (0.45, 0.1), (0.5, 0.12)], T((-L * 0.15, 0, r + 1.3)), mat="cloth", segs=8)
        rod(p, (-L * 0.15 - 0.25, 0, r + 0.65), (-L * 0.15, 0, r + 1.3), 0.015, mat="brass", segs=4)


def _pq_future(p, s, L, W, H):  # floating pod seat
    z = 0.6
    if s == "body":
        p.ball(1.0, M(loc=(0, 0, z + 0.3), scale=(L * 0.4, W * 0.45, 0.45)), mat="body", segs=(12, 6))
    elif s == "running":
        p.cyl(0.35, 0.4, 0.08, T((0, 0, z - 0.25)), mat="shell_dark", segs=12)
    elif s == "power":
        p.cyl(0.3, 0.3, 0.01, T((0, 0, z - 0.26)), mat="glow", segs=12)
    elif s == "rack":
        p.box((0.5, W * 0.6, 0.1), T((0, 0, z + 0.25)), mat="paint", bevel=0.2)
    else:
        p.ball(1.0, M(loc=(0.05, 0, z + 0.65), scale=(L * 0.35, W * 0.4, J(p, 0.3, 0.1))), mat="glass", segs=(12, 5))


def _pq_waste(p, s, L, W, H):  # car seat lashed between two pipes
    z = 0.55
    if s == "body":
        p.box((0.55, W * 0.6, 0.15), T((0, 0, z)), mat="leather", bevel=0.15)
        p.box((0.15, W * 0.6, 0.6), M(loc=(-0.25, 0, z + 0.35), rot=(0, -10, 0)), mat="leather", bevel=0.15)
    elif s == "running":
        for x in (-0.2, 0.2):
            for y in (-W * 0.3, W * 0.3):
                rod(p, (x, y, 0), (x, y, z - 0.07), 0.02, mat="rust", segs=4)
    elif s == "power":
        for y in (-W * 0.45, W * 0.45):
            rod(p, (-L / 2, y, z + 0.1), (L / 2, y, z + 0.1), 0.03, mat="steel", segs=6)
    elif s == "rack":
        wire(p, 0.25, W * 0.45, z + 0.1, 0.04, axis="x")
        wire(p, -0.25, -W * 0.45, z + 0.1, 0.04, axis="x")
    else:
        p.box((0.6, W * 0.8, 0.02), M(loc=(0, 0, z + 1.0), rot=(J(p, 4, 1), 0, 0)), mat="cloth", bevel=0)
        rod(p, (-0.3, 0, z + 0.1), (-0.3, 0, z + 1.0), 0.02, mat="rust", segs=4)


def _pq_ancient(p, s, L, W, H):  # stone throne floating on a rune disc
    z = 0.5
    if s == "body":
        p.box((0.7, W * 0.7, 0.3), T((0, 0, z + 0.15)), mat="stone", bevel=0.15)
        p.box((0.2, W * 0.7, 0.9), T((-0.3, 0, z + 0.6)), mat="stone", bevel=0.15)
    elif s == "running":
        p.cyl(0.5, 0.45, 0.12, T((0, 0, z - 0.2)), mat="stone_dark", segs=8)
    elif s == "power":
        p.ring(0.47, 0.015, T((0, 0, z - 0.21)), mat="glow", segs=8)
    elif s == "rack":
        for y in (-W * 0.33, W * 0.33):
            p.box((0.5, 0.1, 0.2), T((0, y, z + 0.4)), mat="stone_dark", bevel=0.15)
    else:
        p.lathe([(0, 0), (0.1, 0.05), (0, J(p, 0.3, 0.15))], T((-0.3, 0, z + 1.05)), mat="gold", segs=4)
        p.box((0.02, W * 0.4, 0.03), T((-0.19, 0, z + 0.8)), mat="glow", bevel=0)


PALANQUIN = {"Primal": (lambda p, s, L, W, H: _pq_chair(p, s, L, W, H, "Primal"), 2.6, 0.9, 1.4),
             "Agrarian": (lambda p, s, L, W, H: _pq_chair(p, s, L, W, H, "Agrarian"), 3.0, 0.9, 1.8),
             "Mercantile": (lambda p, s, L, W, H: _pq_chair(p, s, L, W, H, "Mercantile"), 3.2, 1.0, 2.2),
             "Industrial": (_pq_rickshaw, 2.4, 1.0, 1.8), "Steampunk": (_pq_steam, 2.0, 1.1, 1.8), "Future": (_pq_future, 1.6, 1.1, 1.6),
             "Wasteland": (_pq_waste, 2.6, 1.0, 1.6), "Ancient": (_pq_ancient, 1.4, 1.1, 1.8)}
function("Palanquin", "Vehicle", VEH, "machine")(dispatch(PALANQUIN))
