"""Figure family forms (塑像: 軀體、頭／面、飾): Automaton, Doll, Idol, Mask (cosmos_chimera P1-19, ADR-0016).

Slots: body (軀體: torso, limbs and base; a mask's face plate), head (頭／面: head and face; a mask's features),
trim (飾: clothing bits, ornaments, keys, antennae, plinth details, feathers and straps).
Frame: Z up, front -Y, origin at the floor contact; a mask stands on its chin edge with the face toward -Y.
Sizes: Automaton 0.9–1.6 m (a yard figure), Idol 1.1–1.8 m including its plinth, Doll and Mask hand-sized.
The figures are original, generic shapes (round heads, block bodies, simple features); they imitate no character.
Glow follows the group: Automaton is a machine (form era: Steampunk 0.5, Future and Ancient 1, Wasteland 0.3),
Idol and Mask are ritual and Doll is play (no glow; only small era accents, like the other unlit groups).
Each form draws its F() frame values first, in a fixed order, so the head always seats on the body's neck.
"""
import math

from mathutils import Matrix

from forms_furniture import gear
from forms_tools import disk, rod
from kit_forms import F, J, function
from kit_lib import M

FIG = ("body", "head", "trim")
T = Matrix.Translation
TAU = math.tau


def blk(p, x, y, z, w, d, h, mat="body", b=0, **kw):
    p.box((w, d, h), T((x, y, z + h / 2)), mat=mat, bevel=b, **kw)


def limb(p, a, b, r, mat="body", segs=6, r2=None):
    rod(p, a, b, r, r if r2 is None else r2, mat=mat, segs=segs)


def eyes(p, x, y, z, r, mat="rubber", segs=6):
    for s in (-1, 1):
        disk(p, (s * x, y, z), r, 0.004, "y", mat, segs=segs)


# ================================================================ Automaton
@function("Automaton", "Figure", FIG, "scene")
def automaton(p, slot):
    e = p.era
    H = F(p, {"Primal": 1.5, "Agrarian": 0.95, "Mercantile": 0.9, "Industrial": 1.25, "Steampunk": 1.35, "Future": 1.2,
              "Wasteland": 1.3, "Ancient": 1.6}[e], 0.06)
    zn = H * 0.82
    hr = H * 0.09
    if e == "Primal":  # straw figure on a pole cross
        if slot == "body":
            p.cyl(0.03, 0.025, H * 0.9, mat="wood", segs=6)
            p.box((H * 0.6, 0.04, 0.04), T((0, 0, zn - 0.05)), mat="wood", bevel=0)
            p.lathe([(0.05, zn * 0.45), (0.16, zn * 0.55), (0.14, zn - 0.05), (0.05, zn)], mat="rope", segs=8, noise=0.06)
        elif slot == "head":
            p.ball(hr * 1.1, T((0, 0, zn + hr)), mat="rope", segs=(8, 5), noise=0.06)
            eyes(p, hr * 0.4, -hr * 1.05, zn + hr * 1.1, hr * 0.12, mat="stone_dark")
        else:
            for s in (-1, 1):
                p.lathe([(0.03, 0), (0.06, -0.08), (0.02, -0.12)], T((s * H * 0.3, 0, zn - 0.05)) @ M(rot=(0, s * 90, 0)), mat="rope", segs=6, noise=0.08)
            p.box((0.3, 0.004, 0.12), M(loc=(0, -0.16, zn - 0.25), rot=(0, J(p, 6, 1), 0)), mat="hide", bevel=0)
        return
    if e == "Agrarian":  # marionette hanging from its crossbar on a post
        if slot == "body":
            p.cyl(0.02, 0.02, H * 1.15, T((0, 0.15, 0)), mat="wood", segs=6)
            p.box((0.04, 0.04, 0.03), T((0, 0.15, -0.0)), mat="wood", bevel=0)
            rod(p, (0, 0.15, H * 1.12), (0, 0.0, H * 1.12), 0.012, mat="wood", segs=5)
            p.lathe([(0.04, H * 0.42), (0.1, H * 0.5), (0.09, zn - 0.02), (0.03, zn)], mat="wood", segs=8)
            for s in (-1, 1):
                limb(p, (s * 0.04, 0, H * 0.42), (s * 0.06, -0.02, H * 0.12), 0.018, mat="wood")
                limb(p, (s * 0.1, 0, zn - 0.04), (s * 0.13, -0.03, zn - H * 0.3), 0.014, mat="wood")
        elif slot == "head":
            p.ball(hr, T((0, 0, zn + hr * 0.9)), mat="wood", segs=(8, 5))
            eyes(p, hr * 0.4, -hr * 0.95, zn + hr, hr * 0.12, mat="paint")
        else:
            for x in (-0.13, 0, 0.13):
                p.tube([(x * 0.7, 0, H * 1.11), (x, -0.02, zn - (0.3 if x else -0.12) * H * 0.5)], 0.0012, mat="rope", segs=3)
            p.box((0.2, 0.12, H * 0.2), T((0, 0, H * 0.5)), mat="cloth", bevel=0)
        return
    if e == "Mercantile":  # karakuri tea-serving figure on a low base
        if slot == "body":
            blk(p, 0, 0, 0, 0.3, 0.3, 0.06, mat="wood_dark")
            p.lathe([(0.14, 0.06), (0.15, H * 0.35), (0.11, zn - 0.04), (0.05, zn)], mat="cloth", segs=10)
            for s in (-1, 1):
                limb(p, (s * 0.1, 0, zn - 0.06), (s * 0.07, -0.16, zn - 0.18), 0.022, mat="cloth")
        elif slot == "head":
            p.ball(hr * 1.05, T((0, 0, zn + hr)), mat="shell", segs=(10, 6))
            p.ball(hr * 1.1, M(loc=(0, 0.02, zn + hr * 1.5), scale=(1, 1, 0.7)), mat="rubber", segs=(8, 4))
            eyes(p, hr * 0.38, -hr * 1.0, zn + hr * 1.05, hr * 0.1)
        else:  # tea tray held out
            p.box((0.14, 0.1, 0.01), T((0, -0.19, zn - 0.18)), mat="wood", bevel=0)
            p.cyl(0.025, 0.022, 0.04, T((0, -0.19, zn - 0.175)), mat="glaze", segs=8)
        return
    if e == "Industrial":  # tin robot: box body, cylinder limbs
        if slot == "body":
            for s in (-1, 1):
                limb(p, (s * 0.1, 0, 0), (s * 0.1, 0, H * 0.45), 0.05, mat="steel", segs=8)
                blk(p, s * 0.1, -0.02, 0, 0.12, 0.18, 0.05, mat="iron")
            blk(p, 0, 0, H * 0.45, 0.36, 0.24, zn - H * 0.45, mat="steel")
            for s in (-1, 1):
                limb(p, (s * 0.2, 0, zn - 0.04), (s * 0.24, -0.04, zn - H * 0.33), 0.04, mat="steel", segs=8)
        elif slot == "head":
            blk(p, 0, 0, zn + 0.02, 0.2, 0.18, J(p, 0.18, 0.1), mat="steel")
            eyes(p, 0.05, -0.091, zn + 0.12, 0.02, mat="glass")
            p.box((0.1, 0.004, 0.02), T((0, -0.091, zn + 0.06)), mat="iron", bevel=0)
        else:
            disk(p, (0, -0.121, H * 0.68), 0.04, 0.006, "y", "paint", segs=8)
            for i in range(3):
                p.box((0.03, 0.004, 0.015), T((-0.06 + i * 0.06, -0.122, H * 0.55)), mat="paint", bevel=0)
            rod(p, (0, 0, zn + 0.2), (0, 0, zn + 0.28), 0.005, mat="steel", segs=4)
            p.ball(0.015, T((0, 0, zn + 0.29)), mat="paint", segs=(5, 3))
        return
    if e == "Steampunk":  # brass clockwork figure: barrel chest, exposed gears, key in the back
        if slot == "body":
            for s in (-1, 1):
                limb(p, (s * 0.1, 0, 0), (s * 0.11, 0, H * 0.45), 0.035, mat="brass", segs=7)
            p.lathe([(0.1, H * 0.45), (0.2, H * 0.55), (0.21, H * 0.7), (0.15, zn - 0.02), (0.05, zn)], mat="brass", segs=10)
            for s in (-1, 1):
                limb(p, (s * 0.19, 0, zn - 0.06), (s * 0.24, -0.06, zn - H * 0.32), 0.03, mat="copper", segs=7)
        elif slot == "head":
            p.ball(hr, T((0, 0, zn + hr)), mat="brass", segs=(10, 6))
            eyes(p, hr * 0.4, -hr * 0.98, zn + hr * 1.05, hr * 0.18, mat="glow")
            p.cyl(hr * 0.6, hr * 0.7, hr * 0.5, T((0, 0, zn + hr * 1.85)), mat="copper", segs=8)
        else:
            gear(p, J(p, 0.08, 0.15), T((0.04, -0.21, H * 0.62)), teeth=10, th=0.01)
            p.box((0.012, 0.012, 0.08), T((0, 0.22, H * 0.65)) @ M(rot=(90, 0, 0)), mat="steel", bevel=0)
            p.box((0.1, 0.012, 0.05), T((0, 0.28, H * 0.65)), mat="brass", bevel=0)
        return
    if e == "Future":  # assist robot: capsule body on a hover base, ring arms
        if slot == "body":
            p.lathe([(0, 0.0), (0.22, 0.02), (0.24, 0.08), (0.12, 0.12)], mat="shell_dark", segs=12)
            p.lathe([(0.1, 0.18), (0.2, H * 0.4), (0.19, zn - 0.08), (0.08, zn)], mat="body", segs=12)
            for s in (-1, 1):
                limb(p, (s * 0.19, 0, zn - 0.12), (s * 0.27, -0.05, zn - H * 0.3), 0.03, mat="body", segs=8)
        elif slot == "head":
            p.ball(1.0, M(loc=(0, 0, zn + hr), scale=(hr * 1.3, hr * 1.1, hr)), mat="body", segs=(10, 6))
            p.box((hr * 1.8, 0.004, hr * 0.5), T((0, -hr * 1.1, zn + hr)), mat="shell_dark", bevel=0)
            eyes(p, hr * 0.4, -hr * 1.12, zn + hr, hr * 0.15, mat="glow")
        else:
            p.ring(0.23, 0.006, T((0, 0, 0.1)), mat="glow", segs=12)
            p.ring(J(p, 0.2, 0.08), 0.006, T((0, 0, H * 0.55)), mat="glow", segs=12)
        return
    if e == "Wasteland":  # junk bot: barrel torso, pipe limbs, mismatched eyes
        if slot == "body":
            for s in (-1, 1):
                limb(p, (s * 0.12, 0, 0), (s * 0.12, 0, H * 0.45), 0.04, mat="rust", segs=7)
            p.cyl(0.2, 0.2, zn - H * 0.45, T((0, 0, H * 0.45)), mat="paint", segs=10)
            limb(p, (0.2, 0, zn - 0.05), (0.3, -0.08, zn - H * 0.3), 0.035, mat="rust")
            limb(p, (-0.2, 0, zn - 0.05), (-0.25, -0.12, zn - 0.12), 0.03, mat="steel")
        elif slot == "head":
            blk(p, 0, 0, zn, 0.22, 0.16, J(p, 0.16, 0.15), mat="steel")
            disk(p, (-0.05, -0.081, zn + 0.09), 0.03, 0.01, "y", "glow", segs=8)
            disk(p, (0.05, -0.081, zn + 0.09), 0.02, 0.01, "y", "glass", segs=6)
        else:
            p.band(0.2, H * 0.62, h=0.05)
            rod(p, (0.08, 0, zn + 0.15), (0.12, 0.02, zn + 0.35), 0.004, mat="steel", segs=3)
            p.box((0.1, 0.004, 0.08), M(loc=(0.05, -0.202, H * 0.55), rot=(0, 10, 0)), mat="cloth", bevel=0)
        return
    # Ancient: stone guardian, rune joints
    if slot == "body":
        for s in (-1, 1):
            blk(p, s * 0.13, 0, 0, 0.16, 0.2, H * 0.45, mat="stone", b=0.15)
        blk(p, 0, 0, H * 0.45, 0.46, 0.28, zn - H * 0.45, mat="stone", b=0.12)
        for s in (-1, 1):
            blk(p, s * 0.3, -0.02, zn - H * 0.4, 0.13, 0.16, H * 0.38, mat="stone_dark", b=0.15)
    elif slot == "head":
        blk(p, 0, 0, zn + 0.01, 0.2, 0.2, J(p, 0.2, 0.1), mat="stone", b=0.2)
        p.box((0.14, 0.004, 0.025), T((0, -0.102, zn + 0.12)), mat="glow", bevel=0)
    else:
        for z in (H * 0.45, zn):
            p.box((0.48, 0.004, 0.012), T((0, -0.142, z)), mat="glow", bevel=0)
        p.box((0.06, 0.004, H * 0.15), T((0, -0.142, H * 0.62)), mat="glow", bevel=0)


# ================================================================ Doll (carried, ~0.25 m)
@function("Doll", "Figure", FIG, "carried")
def doll(p, slot):
    e = p.era
    H = F(p, 0.26, 0.1)
    zn = H * 0.68
    hr = H * 0.15
    if e == "Future":  # interactive robot pet: round body, ear fins
        if slot == "body":
            p.ball(1.0, M(loc=(0, 0, H * 0.3), scale=(H * 0.3, H * 0.35, H * 0.28)), mat="body", segs=(10, 6))
            for sx in (-1, 1):
                p.ball(H * 0.06, T((sx * H * 0.18, -H * 0.15, H * 0.05)), mat="shell_dark", segs=(6, 4))
        elif slot == "head":
            p.ball(H * 0.22, T((0, -H * 0.2, H * 0.62)), mat="body", segs=(10, 6))
            p.box((H * 0.3, 0.003, H * 0.12), T((0, -H * 0.41, H * 0.64)), mat="shell_dark", bevel=0)
            eyes(p, H * 0.06, -H * 0.415, H * 0.65, H * 0.03, mat="glow")
        else:
            for s in (-1, 1):
                p.plate([(0, 0), (H * 0.08, H * 0.18), (-H * 0.02, H * J(p, 0.16, 0.2))], 0.006, T((s * H * 0.12, -H * 0.2, H * 0.75)) @ M(rot=(0, -s * 20, 0)), mat="shell_dark", bevel=0)
        return
    if e == "Steampunk":  # clockwork walker: brass bell body, key
        if slot == "body":
            p.lathe([(H * 0.18, 0), (H * 0.15, H * 0.2), (H * 0.1, zn - 0.01), (H * 0.04, zn)], mat="brass", segs=10)
            for s in (-1, 1):
                limb(p, (s * H * 0.1, 0, zn - H * 0.05), (s * H * 0.16, -H * 0.06, zn - H * 0.3), H * 0.025, mat="copper")
        elif slot == "head":
            p.ball(hr, T((0, 0, zn + hr)), mat="shell", segs=(8, 5))
            eyes(p, hr * 0.38, -hr * 0.98, zn + hr * 1.05, hr * 0.13, mat="glow")
        else:
            p.box((0.004, H * 0.15, H * 0.02), T((0, H * 0.2, H * 0.45)), mat="steel", bevel=0)
            p.box((H * 0.12, 0.004, H * 0.06), T((0, H * 0.28, H * 0.45)), mat="brass", bevel=0)
            gear(p, H * J(p, 0.06, 0.15), T((0, -H * 0.15, H * 0.3)), teeth=6, th=0.004, mat="copper")
        return
    # cloth, straw, porcelain, tin soldier, patched, stone: seated or standing figure
    body = {"Primal": "rope", "Agrarian": "cloth", "Mercantile": "cloth", "Industrial": "paint", "Wasteland": "cloth", "Ancient": "stone"}[e]
    skin = {"Primal": "rope", "Agrarian": "hide", "Mercantile": "shell", "Industrial": "steel", "Wasteland": "hide", "Ancient": "stone"}[e]
    if slot == "body":
        if e == "Industrial":  # tin soldier on a round stand
            p.cyl(H * 0.18, H * 0.18, H * 0.04, mat="paint", segs=8)
            for s in (-1, 1):
                limb(p, (s * H * 0.05, 0, H * 0.04), (s * H * 0.05, 0, H * 0.35), H * 0.035, mat="rubber")
            blk(p, 0, 0, H * 0.35, H * 0.2, H * 0.12, zn - H * 0.35, mat="paint")
            for s in (-1, 1):
                limb(p, (s * H * 0.12, 0, zn - H * 0.03), (s * H * 0.13, 0, zn - H * 0.3), H * 0.03, mat="paint")
        elif e == "Ancient":
            p.lathe([(H * 0.18, 0), (H * 0.16, H * 0.1), (H * 0.1, zn - 0.01), (H * 0.04, zn)], mat="stone", segs=6)
        else:
            p.lathe([(H * 0.16, 0), (H * 0.18, H * 0.2), (H * 0.12, zn - 0.01), (H * 0.04, zn)], mat=body, segs=8, noise=0.05 if e == "Primal" else 0.0)
            for s in (-1, 1):
                limb(p, (s * H * 0.1, 0, zn - H * 0.05), (s * H * 0.17, -H * 0.04, zn - H * 0.28), H * 0.035, mat=body if e != "Mercantile" else "shell")
    elif slot == "head":
        if e == "Industrial":
            p.ball(hr * 0.8, T((0, 0, zn + hr * 0.8)), mat=skin, segs=(8, 5))
            p.cyl(hr * 0.7, hr * 0.8, hr * J(p, 1.4, 0.15), T((0, 0, zn + hr * 1.3)), mat="rubber", segs=8)
        else:
            p.ball(hr, T((0, 0, zn + hr)), mat=skin, segs=(8, 5), noise=0.05 if e == "Primal" else 0.0)
            if e != "Primal":
                eyes(p, hr * 0.38, -hr * 0.98, zn + hr * 1.05, hr * 0.12, mat="rubber" if e != "Ancient" else "stone_dark")
    else:
        if e == "Primal":  # straw knots and a twig
            p.band(H * 0.12, zn - H * 0.1, h=H * 0.06)
            rod(p, (H * 0.15, -0.01, H * 0.3), (H * 0.25, -0.02, H * J(p, 0.55, 0.15)), 0.003, mat="wood", segs=3)
        elif e == "Agrarian":  # head cloth
            p.ball(1.0, M(loc=(0, 0.004, zn + hr * 1.35), scale=(hr * 1.05, hr * 1.05, hr * J(p, 0.6, 0.15))), mat="paint", segs=(8, 4))
        elif e == "Mercantile":  # porcelain doll's hair and bow
            p.ball(1.0, M(loc=(0, hr * 0.15, zn + hr * 1.25), scale=(hr * 1.1, hr * 1.1, hr * 0.8)), mat="wood_dark", segs=(8, 5))
            p.box((hr * J(p, 0.9, 0.2), 0.01, hr * 0.3), T((0, -hr * 0.4, zn + hr * 1.9)), mat="paint", bevel=0)
        elif e == "Industrial":  # rifle on the shoulder
            rod(p, (H * 0.13, -0.01, zn - H * 0.25), (H * 0.13, -0.01, zn + H * J(p, 0.25, 0.1)), H * 0.012, mat="wood_dark", segs=4)
        elif e == "Wasteland":  # patches and a button eye
            p.box((H * 0.12, 0.004, H * 0.1), M(loc=(H * 0.05, -H * 0.18, H * 0.35), rot=(0, J(p, 15, 0.8), 0)), mat="paint", bevel=0)
            disk(p, (hr * 0.4, -hr * 0.98, zn + hr), hr * 0.25, 0.006, "y", "steel", segs=6)
        else:
            p.box((H * 0.12, 0.004, H * 0.2), T((0, -H * 0.17, H * J(p, 0.4, 0.15))), mat="glow", bevel=0)


# ================================================================ Idol (scene, with plinth)
@function("Idol", "Figure", FIG, "scene")
def idol(p, slot):
    e = p.era
    Hp, Hf = F(p, 0.35, 0.1), F(p, {"Primal": 1.1, "Agrarian": 0.8, "Mercantile": 1.0, "Industrial": 1.0, "Steampunk": 0.95,
                                     "Future": 1.0, "Wasteland": 1.3, "Ancient": 1.2}[e], 0.08)
    pmat = {"Primal": "stone", "Agrarian": "stone", "Mercantile": "stone", "Industrial": "iron", "Steampunk": "brass",
            "Future": "shell_dark", "Wasteland": "rust", "Ancient": "stone_dark"}[e]
    fmat = {"Primal": "wood", "Agrarian": "ceramic", "Mercantile": "stone", "Industrial": "iron", "Steampunk": "brass",
            "Future": "glow", "Wasteland": "steel", "Ancient": "stone"}[e]
    z0 = Hp
    zn = z0 + Hf * 0.75
    hr = Hf * 0.12
    if slot == "body":  # plinth and seated or standing body
        if e == "Future":
            p.lathe([(0, 0), (0.4, 0), (0.38, Hp * 0.6), (0.3, Hp), (0, Hp)], mat=pmat, segs=12)
            p.lathe([(0.12, z0 + 0.02), (0.22, z0 + Hf * 0.3), (0.16, zn - 0.04), (0.05, zn)], mat="glow", segs=10)
            return
        if e == "Primal":  # carved post figure, no plinth: a stone ring at its foot
            p.ring(0.3, 0.06, T((0, 0, 0.04)), mat="stone", segs=8, square=False)
            p.cyl(0.16, 0.14, zn, mat=fmat, segs=8, noise=0.02)
            return
        if e == "Wasteland":  # scrap totem: stacked drums and a tyre
            p.cyl(0.32, 0.32, 0.18, mat="rubber", segs=10)
            p.cyl(0.2, 0.2, Hp, T((0, 0, 0.18)), mat=pmat, segs=10)
            p.cyl(0.16, 0.16, Hf * 0.75 - 0.18, T((0, 0, z0 + 0.18 - 0.18)), mat="paint", segs=8)
            return
        blk(p, 0, 0, 0, 0.6, 0.5, Hp, mat=pmat, b=0.06)
        if e in ("Agrarian", "Ancient"):  # seated
            blk(p, 0, 0.02, z0, 0.42, 0.34, Hf * 0.22, mat=fmat, b=0.2)
            p.lathe([(0.14, z0 + Hf * 0.2), (0.17, z0 + Hf * 0.4), (0.13, zn - 0.03), (0.05, zn)], mat=fmat, segs=8)
        else:
            p.lathe([(0.17, z0), (0.16, z0 + Hf * 0.35), (0.18, z0 + Hf * 0.55), (0.12, zn - 0.03), (0.05, zn)], mat=fmat, segs=10)
            for s in (-1, 1):
                limb(p, (s * 0.15, 0, zn - 0.05), (s * 0.12, -0.12, z0 + Hf * 0.42), 0.04, mat=fmat)
    elif slot == "head":
        if e == "Primal":
            p.ball(1.0, M(loc=(0, 0, zn + hr * 0.6), scale=(0.17, 0.15, hr * 1.4)), mat=fmat, segs=(8, 5), noise=0.03)
            eyes(p, 0.05, -0.15, zn + hr * 0.8, 0.025, mat="bone")
            p.box((0.08, 0.01, 0.02), T((0, -0.15, zn + hr * 0.2)), mat="bone", bevel=0)
        elif e == "Industrial":  # helmeted bust
            p.ball(hr, T((0, 0, zn + hr)), mat=fmat, segs=(10, 6))
            p.lathe([(hr * 1.2, zn + hr * 1.1), (hr * 1.0, zn + hr * 1.6), (0, zn + hr * J(p, 2.0, 0.08))], mat=fmat, segs=10)
        elif e == "Future":  # hologram head
            p.ball(hr, T((0, 0, zn + hr)), mat="glow", segs=(8, 5))
            p.ring(hr * 1.6, 0.006, T((0, 0, zn + hr * J(p, 2.4, 0.1))), mat="glow", segs=10)
        elif e == "Wasteland":  # welded mask head
            blk(p, 0, 0, zn - 0.02, 0.3, 0.2, J(p, 0.28, 0.12), mat="steel")
            eyes(p, 0.07, -0.101, zn + 0.15, 0.035, mat="glow")
        elif e == "Steampunk":
            p.ball(hr, T((0, 0, zn + hr)), mat=fmat, segs=(10, 6))
            gear(p, hr * J(p, 1.6, 0.1), T((0, hr * 0.5, zn + hr * 1.1)), teeth=12, th=0.015, mat="copper")
            eyes(p, hr * 0.35, -hr * 0.98, zn + hr * 1.05, hr * 0.13, mat="glow")
        else:
            p.ball(hr, T((0, 0, zn + hr)), mat=fmat, segs=(8, 6) if e != "Ancient" else (6, 4))
            p.lathe([(hr * 0.6, zn + hr * 1.7), (hr * 0.3, zn + hr * 2.2), (0, zn + hr * J(p, 2.5, 0.1))], mat=fmat if e != "Ancient" else "gold", segs=8)
            if e == "Ancient":
                p.box((hr * 1.2, 0.004, hr * 0.15), T((0, -hr * 0.98, zn + hr * 1.05)), mat="glow", bevel=0)
    else:  # trim: halo, offerings, plinth inscription, banners
        if e == "Primal":
            for i in range(3):
                a = -0.6 + i * 0.6
                p.box((0.02, 0.004, 0.18), M(loc=(math.sin(a) * 0.16, -0.12, zn + hr * 1.9), rot=(0, math.degrees(a), 0)), mat="feather", bevel=0)
        elif e in ("Agrarian", "Mercantile"):
            p.ring(hr * 2.2, 0.01, T((0, 0.08, zn + hr * 1.1)) @ M(rot=(90, 0, 0)), mat="gold" if e == "Mercantile" else "paint", segs=12)
            p.cyl(0.04, 0.03, 0.05, T((J(p, 0.15, 0.3), -0.2, Hp)), mat="ceramic", segs=6)
        elif e == "Industrial":
            p.box((0.4, 0.006, 0.08), T((0, -0.253, Hp * 0.6)), mat="brass", bevel=0)
        elif e == "Steampunk":
            for s in (-1, 1):
                p.cyl(0.04, 0.04, Hp * 0.8, T((s * 0.33, -0.2, 0)), mat="copper", segs=8)
                p.ball(0.04, T((s * 0.33, -0.2, Hp * 0.8 + 0.03)), mat="glow", segs=(6, 4))
        elif e == "Future":
            p.ring(0.33, 0.006, T((0, 0, Hp * J(p, 0.5, 0.3))), mat="glow", segs=12)
        elif e == "Wasteland":
            p.box((0.3, 0.004, 0.25), M(loc=(0, -0.205, 0.35), rot=(0, J(p, 5, 1), 0)), mat="cloth", bevel=0)
            rod(p, (0.25, 0, 0.18), (0.3, 0, zn + 0.3), 0.01, mat="rust", segs=4)
        else:
            for z in (Hp * 0.3, Hp * 0.7):
                p.box((0.5, 0.004, 0.015), T((0, -0.252, z)), mat="glow", bevel=0)


# ================================================================ Mask (carried; stands on its chin, face -Y)
@function("Mask", "Figure", FIG, "carried")
def mask(p, slot):
    e = p.era
    W, H = F(p, 0.17, 0.08), F(p, 0.22, 0.08)
    mat = {"Primal": "bark", "Agrarian": "wood", "Mercantile": "paint", "Industrial": "steel", "Steampunk": "brass",
           "Future": "shell", "Wasteland": "rubber", "Ancient": "stone"}[e]
    zc = H * 0.5
    if slot == "body":  # curved face plate
        if e == "Future":  # light-screen visor: frame ring and a glowing plane
            p.ring(W * 0.5, 0.008, T((0, 0, zc)) @ M(rot=(90, 0, 0), scale=(1, H / W, 1)), mat="shell", segs=12)
            p.box((W * 0.9, 0.003, H * 0.85), T((0, 0, zc)), mat="glow", bevel=0)
            return
        p.ball(1.0, M(loc=(0, 0.03, zc), scale=(W * 0.5, W * 0.25, H * 0.5)), mat=mat, segs=(10, 6), noise=0.04 if e == "Primal" else 0.0)
    elif slot == "head":  # features
        if e == "Future":
            eyes(p, W * 0.18, -0.003, zc + H * 0.08, W * 0.07, mat="shell_dark")
            p.box((W * 0.3, 0.003, H * 0.04), T((0, -0.003, zc - H * 0.2)), mat="shell_dark", bevel=0)
        elif e == "Wasteland":  # gas mask: lenses and filter
            eyes(p, W * 0.2, -W * 0.22, zc + H * 0.1, W * 0.12, mat="glass")
            p.cyl(W * 0.14, W * 0.12, W * J(p, 0.22, 0.2), T((0, -W * 0.2, zc - H * 0.2)) @ M(rot=(90, 0, 0)), mat="steel", segs=8)
        elif e == "Steampunk":
            eyes(p, W * 0.2, -W * 0.24, zc + H * 0.1, W * 0.1, mat="glow")
            gear(p, W * J(p, 0.14, 0.15), T((W * 0.2, -W * 0.24, zc + H * 0.32)), teeth=8, th=0.005, mat="copper")
            p.box((W * 0.35, 0.006, H * 0.05), T((0, -W * 0.24, zc - H * 0.22)), mat="copper", bevel=0)
        elif e == "Ancient":
            p.box((W * 0.6, 0.004, H * 0.04), T((0, -W * 0.255, zc + H * 0.1)), mat="glow", bevel=0)
            p.box((W * 0.05, 0.004, H * J(p, 0.3, 0.15)), T((0, -W * 0.255, zc - H * 0.1)), mat="glow", bevel=0)
        else:
            dark = "rubber" if e != "Industrial" else "iron"
            eyes(p, W * 0.19, -W * 0.25, zc + H * 0.1, W * J(p, 0.08, 0.2), mat=dark)
            p.plate([(0, H * 0.05), (W * 0.05, -H * 0.08), (-W * 0.05, -H * 0.08)], W * 0.08, T((0, -W * 0.25, zc)), mat=mat, bevel=0)
            p.box((W * 0.3, 0.006, H * 0.03), T((0, -W * 0.24, zc - H * 0.25)), mat=dark, bevel=0)
    else:  # trim: feathers, horns, paint lines, rivets, straps
        if e == "Primal":
            for i in range(5):
                a = -0.8 + i * 0.4
                p.box((0.015, 0.003, H * J(p, 0.4, 0.2)), M(loc=(math.sin(a) * W * 0.45, 0.03, zc + math.cos(a) * H * 0.55), rot=(0, math.degrees(a), 0)), mat="feather", bevel=0)
        elif e == "Agrarian":  # horns
            for s in (-1, 1):
                p.tube([(s * W * 0.3, 0.02, zc + H * 0.35), (s * W * 0.45, 0.02, zc + H * 0.6), (s * W * J(p, 0.4, 0.15), 0.03, zc + H * 0.75)], 0.008, mat="bone", segs=5)
        elif e == "Mercantile":  # lacquer stripes and gold tassel
            for s in (-1, 1):
                p.box((W * 0.05, 0.004, H * 0.3), M(loc=(s * W * 0.25, -W * 0.2, zc - H * 0.05), rot=(0, s * 20, 0)), mat="gold", bevel=0)
            p.tube([(W * 0.45, 0.03, zc), (W * 0.5, 0.02, zc - H * J(p, 0.35, 0.15))], 0.004, mat="paint", segs=3)
        elif e == "Industrial":  # rivets
            for i in range(6):
                a = i * TAU / 6
                p.ball(0.005, T((math.cos(a) * W * 0.42, -W * 0.12, zc + math.sin(a) * H * 0.42)), mat="iron", segs=(4, 3))
        elif e == "Wasteland":
            p.tube([(-W * 0.48, 0.04, zc), (0, 0.1, zc + H * J(p, 0.1, 0.5)), (W * 0.48, 0.04, zc)], 0.006, mat="cloth", segs=3)
        elif e == "Future":
            p.box((W * 1.0, 0.03, 0.01), T((0, 0.02, zc + H * 0.42)), mat="shell_dark", bevel=0)
        elif e == "Steampunk":
            p.tube([(-W * 0.48, 0.04, zc), (0, 0.1, zc + H * J(p, 0.1, 0.5)), (W * 0.48, 0.04, zc)], 0.006, mat="leather", segs=3)
        else:
            p.lathe([(0, 0), (W * 0.06, 0.01), (0, H * J(p, 0.12, 0.2))], T((0, 0.0, zc + H * 0.5)), mat="gold", segs=4)
