"""Four-planet forms of the hand tools (cosmos_chimera everyday-objects.md#四星球形體, Q-A38 batch 2, hafted part 1).

Sickle, Shovel, Pitchfork, Saw, Hatchet, Chisel, Wrench and Broom for Ocean, Gale, Radiant and Metropolis in all 8
eras. Same slots, frame and budget as forms_tools.py; haft, joint and butt are the pilot's regional ones
(forms_region_pilot.r_haft/r_joint/r_butt), so a region's tools read as one family. Haft lengths match the shared
forms so the game's hand anchor and leaning poses fit both.

Silhouette per region (planet-world.md#四星球時代造型): Ocean upswept horn tips and rattan lashing; Gale leaf and
heart blades whose tang runs through the haft knob, beam-end pegs; Radiant turned brass sockets with lotus petals and
scalloped edges; Metropolis by era (meteoric iron lump, art-deco setbacks, sleek shell with light strips).
"""
import math

from mathutils import Matrix

from forms_region_pilot import HAND, MACHINE, _blade_mat, era_mark, gear, lash, pegs, petals, r_hafted, steps, zig
from forms_tools import _crescent, _flat_bit, _saw_outline, _tine, front, rod, side
from kit_forms import J, regional
from kit_lib import M, REGIONS

T = Matrix.Translation


def _tail(p, r, z):
    """The era's own token on the haft top, for the three regions whose silhouette does not already carry it."""
    # Gale's Future haft already carries its rings; a glow ring on top would only cost triangles.
    if p.region == "Gale" and p.era == "Future":
        return
    if p.region != "Metropolis" and p.era in ("Steampunk", "Future", "Ancient", "Wasteland"):
        era_mark(p, r * 1.2, z)


def _socket(p, L, r, h=0.05, lotus=3):
    """Region's ferrule where the head meets the haft; lotus = Radiant petal count (0 where the head has its own)."""
    g, e = p.region, p.era
    if g == "Ocean":
        lash(p, r * 1.25, L - h * 0.5, h * 0.8, segs=6)
    elif g == "Gale":
        p.cyl(r * 1.35, r * 1.2, h, T((0, 0, L - h * 0.7)), mat="fit", segs=7, bevel=0)
    elif g == "Radiant":
        p.lathe([(r * 1.05, L - h), (r * 1.5, L - h * 0.5), (r * 1.6, L)], mat="fit", segs=8)
        if lotus:
            petals(p, r * 1.5, L - h * 0.15, lotus, r * 0.7, mat="accent", tilt=50)
    else:
        if e == "Primal":
            p.ball(r * 1.8, M(loc=(0, 0, L - h * 0.4), scale=(1, 1, 1.4)), mat="iron", segs=(6, 4), noise=0.1)
        elif e == "Industrial":
            steps(p, r * 2.6, r * 2.6, L - h, 3, h * 0.3, mat="chrome", shrink=0.85)
        elif e == "Future":
            p.box((r * 2.4, r * 2.0, h), T((0, 0, L - h * 0.4)), mat="body", bevel=0.3)
            p.box((r * 2.42, r * 0.3, h * 0.2), T((0, -r * 0.9, L - h * 0.4)), mat="glow", bevel=0)
        elif e == "Steampunk":
            p.band(r * 1.3, L - h * 0.5, h=h)
            gear(p, r * 1.1, M(loc=(r * 1.4, 0, L - h * 0.5), rot=(0, 90, 0)))
        else:
            p.band(r * 1.3, L - h * 0.5, h=h)


# ---------------------------------------------------------------- sickle


def _sickle_head(p, L, r):
    g, e = p.region, p.era
    mat = _blade_mat(p)
    R = J(p, 0.15, 0.1)
    w0 = J(p, 0.032, 0.15)
    base = (w0 * 0.45, L + 0.012)
    if g == "Ocean":
        # Long sweeping crescent whose tip curls up like the saddle-roof horn.
        a1 = J(p, 215, 0.03)
        pts, c = _crescent(base, R * 1.1, w0, 15, a1, n=9, tip=0.2)
        side(p, pts, 0.005, mat=mat)
        a = math.radians(a1)
        ty, tz = c[0] + R * 1.1 * math.cos(a), c[1] + R * 1.1 * math.sin(a)
        p.tube([(0, ty, tz), (0, ty + 0.012, tz - 0.02), (0, ty + 0.03, tz - 0.018), (0, ty + 0.034, tz)], 0.004, mat=mat, segs=4)
    elif g == "Gale":
        # Narrow hooked leaf; its tang passes through the haft knob and peeks out behind.
        a1 = J(p, 200, 0.04)
        pts, _ = _crescent(base, R * 0.9, w0 * 1.2, 20, a1, n=6, tip=0.05)
        side(p, pts, 0.006, mat=mat)
        p.cyl(0.005, 0.005, 0.07, M(loc=(0, 0.035, L * 0.94), rot=(90, 0, 0)), mat="iron" if e not in ("Primal", "Ancient") else "bone", segs=5, bevel=0)
    elif g == "Radiant":
        # Deep crescent with a toothed inner edge on a turned socket.
        pts, _ = _crescent(base, R, w0, 15, J(p, 222, 0.03), n=11, teeth=0.005)
        side(p, pts, 0.004, mat=mat)
    else:
        if e == "Primal":
            pts, _ = _crescent(base, R * 0.9, w0 * 1.4, 15, 190, n=6, tip=0.4)
            side(p, pts, 0.012, mat="iron", noise=0.1)
        elif e == "Future":
            pts, _ = _crescent((0.0, L + 0.03), R, 0.01, 20, J(p, 200, 0.04), n=8, tip=0.4)
            side(p, pts, 0.003, mat="glow")
        else:
            pts, _ = _crescent(base, R * J(p, 1.05, 0.06), w0 * 0.85, 15, 185 if e == "Industrial" else J(p, 205, 0.04), n=9)
            side(p, pts, 0.004, mat=mat)
    _socket(p, L + 0.01, r, J(p, 0.045, 0.15))
    _tail(p, r, L * 0.75)


# ---------------------------------------------------------------- shovel


def _shovel_head(p, L, r):
    g, e = p.region, p.era
    mat = _blade_mat(p)
    W, H = J(p, 0.22, 0.1), J(p, 0.28, 0.1)
    z0 = L + 0.04
    w = W / 2
    if g == "Ocean":
        # Narrow tapering blade, both shoulders swept up into horns.
        out = [(-w * 0.8, z0), (w * 0.8, z0), (w * 0.6, z0 + H * 0.8), (0, z0 + H * 1.1), (-w * 0.6, z0 + H * 0.8)]
        front(p, out, 0.012, mat=mat)
        for s in (-1, 1):
            p.tube([(s * w * 0.75, 0, z0 + 0.005), (s * w * 1.05, 0, z0 - 0.02), (s * w * 1.25, 0, z0 + 0.01), (s * w * 1.2, 0, z0 + 0.05)], 0.008, mat=mat, segs=4)
    elif g == "Gale":
        # Heart-shaped spade.
        out = [(0, z0 - 0.01), (-w * 0.5, z0 - 0.02), (-w, z0 + H * 0.25), (-w * 0.75, z0 + H * 0.7), (0, z0 + H * 1.05),
               (w * 0.75, z0 + H * 0.7), (w, z0 + H * 0.25), (w * 0.5, z0 - 0.02)]
        front(p, out, 0.012, mat=mat)
        p.box((0.016, 0.006, 0.16), T((0, -0.01, L - 0.02)), mat="iron" if e not in ("Primal", "Ancient") else "bone", bevel=0)
    elif g == "Radiant":
        # Round blade with a scalloped shoulder.
        out = [(-w, z0 + 0.02)]
        for i in range(5):
            x = -w + (i + 0.5) * W / 5
            out += [(x, z0 + (0.0 if i % 2 else 0.018))]
        out.append((w, z0 + 0.02))
        for i in range(1, 6):
            a = i * math.pi / 6
            out.append((w * math.cos(a), z0 + H * 0.5 + H * 0.5 * math.sin(a)))
        front(p, out, 0.011, mat=mat)
    else:
        if e == "Primal":
            front(p, [(-w * 0.8, z0), (w * 0.8, z0), (w * 0.7, z0 + H * 0.8), (-w * 0.5, z0 + H)], 0.02, mat="iron", noise=0.08)
        elif e == "Industrial":
            front(p, [(-w, z0), (w, z0), (w, z0 + H), (-w, z0 + H)], 0.008, mat=mat)
            for z in (0.3, 0.6):
                p.box((W * 0.9, 0.012, 0.006), T((0, -0.007, z0 + H * z)), mat="paint", bevel=0)
        elif e == "Future":
            front(p, [(-w, z0), (w, z0), (w * 0.9, z0 + H), (-w * 0.9, z0 + H)], 0.01, mat="body", bevel=0.2)
            p.box((W * 0.85, 0.012, 0.008), T((0, -0.004, z0 + H * 0.98)), mat="glow", bevel=0)
        else:
            front(p, [(-w, z0), (w, z0), (w * 0.95, z0 + H * 0.6), (0, z0 + H), (-w * 0.95, z0 + H * 0.6)], 0.01, mat=mat)
    _socket(p, z0 + 0.005, r, J(p, 0.07, 0.15))
    _tail(p, r, L * 0.85)


# ---------------------------------------------------------------- pitchfork


def _fork_head(p, L, r):
    g, e = p.region, p.era
    mat = _blade_mat(p) if e not in HAND else ("body" if e == "Primal" else _blade_mat(p))
    ln, sp = J(p, 0.3, 0.1), J(p, 0.06, 0.12)
    zb = L + 0.04
    if g == "Ocean":
        # Split-bamboo tines, many and thin, tips curling up; a rattan cross-lash.
        n = 5
        for i in range(n):
            x = (i - 2) * sp * 0.55
            _tine(p, x, zb, ln, 0.006, "body" if e in HAND else mat, curve=J(p, 0.06, 0.3), segs=4)
        rod(p, (-sp * 1.2, 0, zb + 0.06), (sp * 1.2, 0, zb + 0.06), 0.005, mat="fit", segs=4)
    elif g == "Gale":
        # Three tines splaying wide from a pegged crossbar.
        p.box((sp * 2.6, 0.026, 0.03), T((0, 0, zb)), mat="body" if e in HAND else "fit", bevel=0)
        for x, dx in ((-sp, -0.04), (0, 0), (sp, 0.04)):
            _tine(p, x, zb + 0.01, ln, 0.008, mat, curve=0.04, segs=4, dx=dx)
        for s in (-1, 1):
            p.cyl(0.006, 0.005, 0.03, M(loc=(s * sp * 1.35, 0, zb), rot=(0, 90 * s, 0)), mat="fit", segs=4, bevel=0)
    elif g == "Radiant":
        # Trident-like: a long centre tine, outer ones curving out and back up.
        _tine(p, 0, zb, ln * 1.1, 0.008, mat, curve=0.02, segs=4)
        for s in (-1, 1):
            p.tube([(0, 0, zb), (s * sp * 1.2, -0.01, zb + 0.03), (s * sp * 1.5, -0.02, zb + ln * 0.5)], 0.007, mat=mat, segs=4)
            rod(p, (s * sp * 1.5, -0.02, zb + ln * 0.5), (s * sp * 1.3, -0.03, zb + ln * 0.85), 0.007, 0.002, mat=mat, segs=4)
    else:
        if e == "Primal":
            for s in (-1, 1):
                rod(p, (0, 0, zb - 0.02), (s * sp, -0.02, zb + ln), 0.01, 0.003, mat="iron", segs=5, noise=0.1)
        elif e == "Future":
            for s in (-1, 1):
                rod(p, (s * sp * 0.6, 0, zb), (s * sp * 0.6, -0.02, zb + ln), 0.005, 0.002, mat="glow", segs=4)
            p.box((sp * 1.8, 0.03, 0.04), T((0, 0, zb)), mat="body", bevel=0.3)
        else:
            p.box((sp * 3.2, 0.02, 0.022), T((0, 0, zb)), mat=mat, bevel=0)
            for i in range(4):
                _tine(p, (i - 1.5) * sp * 0.9, zb + 0.005, ln, 0.006, mat, curve=0.05 if e != "Industrial" else 0.02, segs=4)
    if g != "Gale":  # the pegged crossbar is Gale's socket
        _socket(p, zb - 0.01, r, J(p, 0.07, 0.15))
    _tail(p, r, L * 0.85)


# ---------------------------------------------------------------- saw


def _saw_head(p, L, r):
    g, e = p.region, p.era
    mat = _blade_mat(p)
    Lb = J(p, 0.36, 0.1)
    z0, z1 = L - 0.01, L + Lb
    if g == "Ocean":
        # Long narrow blade ending in an upswept horn.
        side(p, _saw_outline(0.012, 0.004, -0.024, -0.012, z0, z1, 12, 0.004), 0.002, mat=mat)
        p.tube([(0, 0.004, z1), (0, 0.012, z1 + 0.02), (0, 0.028, z1 + 0.026), (0, 0.034, z1 + 0.012)], 0.004, mat=mat, segs=4)
    elif g == "Gale":
        # Wide pull saw with a stepped back.
        back = [(0.02, z0), (0.02, z0 + Lb * 0.4), (0.03, z0 + Lb * 0.45), (0.03, z1)]
        pts = back + _saw_outline(0, 0, -0.03, -0.04, z0, z1, 11, 0.005)[2:]
        side(p, pts, 0.002, mat=mat)
    elif g == "Radiant":
        # Curved back with three scallops, turned bolster.
        back = [(0.014, z0)] + [(0.014 + (0.008 if i % 2 else 0.0), z0 + Lb * (i + 1) / 6) for i in range(6)]
        pts = back + _saw_outline(0, 0, -0.02, -0.006, z0, z1, 10, 0.004)[2:]
        side(p, pts, 0.002, mat=mat)
    else:
        if e == "Primal":
            nick = [p.rng.uniform(0, 0.006) for _ in range(11)]
            side(p, _saw_outline(0.014, 0.006, -0.02, -0.012, z0, L + Lb * 0.5, 5, 0.006, jag=lambda i: nick[i]), 0.01, mat="iron")
        elif e == "Future":
            p.box((0.008, 0.012, Lb), T((0, 0.012, z0 + Lb / 2)), mat="body", bevel=0)
            side(p, [(0.006, z0), (0.006, z1), (-0.018, z1 - 0.01), (-0.018, z0)], 0.002, mat="glow")
        else:
            side(p, _saw_outline(0.03, 0.016, -0.03, -0.012, z0, z1, 13, 0.004), 0.0015, mat=mat)
            if e == "Industrial":
                for i in range(3):
                    p.box((0.006, 0.012, 0.012), T((0, 0.024 - i * 0.004, z0 + 0.02 + i * 0.016)), mat="chrome", bevel=0)
    _socket(p, L, r, 0.035)
    _tail(p, r, L * 0.6)


# ---------------------------------------------------------------- hatchet


def _hatchet_head(p, L, r):
    g, e = p.region, p.era
    mat = _blade_mat(p)
    zc = L - 0.035
    edge, top, bot = J(p, 0.15, 0.1), J(p, 0.05, 0.15), J(p, 0.05, 0.2)
    if g == "Ocean":
        # Bearded blade; its upper corner sweeps up into a horn.
        out = [(0.025, zc + 0.022), (-edge * 0.6, zc + 0.02), (-edge, zc + top), (-edge * 1.02, zc - bot * 0.3), (-edge * 0.8, zc - bot * 1.3),
               (-0.03, zc - 0.03), (0.025, zc - 0.022)]
        side(p, out, 0.01, mat=mat)
        p.tube([(0, -edge, zc + top), (0, -edge - 0.01, zc + top + 0.02), (0, -edge + 0.004, zc + top + 0.04)], 0.005, mat=mat, segs=4)
    elif g == "Gale":
        # Triangular blade on a tang that runs through the haft and out behind.
        side(p, [(-0.01, zc + 0.015), (-edge, zc + top * 1.1), (-edge * 0.9, zc - bot * 1.1), (-0.01, zc - 0.015)], 0.008, mat=mat)
        p.cyl(0.006, 0.004, 0.06, M(loc=(0, -0.01, zc), rot=(-90, 0, 0)), mat="iron" if e not in ("Primal", "Ancient") else "bone", segs=5, bevel=0)
    elif g == "Radiant":
        # Broad crescent edge on a turned socket.
        out = [(0.02, zc + 0.02), (-edge * 0.5, zc + 0.02)]
        for i in range(5):
            a = math.radians(70 - i * 35)
            out.append((-edge * 0.55 - edge * 0.5 * math.cos(a), zc + (top + bot) * 0.6 * math.sin(a)))
        out += [(-edge * 0.5, zc - 0.02), (0.02, zc - 0.02)]
        side(p, out, 0.008, mat=mat)
    else:
        if e == "Primal":
            p.ball(0.03, M(loc=(0, -0.04, zc), scale=(0.9, J(p, 2.4, 0.12), 1.4)), mat="iron", segs=(6, 4), noise=0.1)
        elif e == "Future":
            p.box((0.03, 0.06, 0.055), T((0, -0.01, zc)), mat="body", bevel=0.3)
            side(p, [(-0.04, zc + 0.02), (-edge, zc + top), (-edge, zc - bot), (-0.04, zc - 0.02)], 0.004, mat="glow")
        else:
            side(p, [(0.03, zc + 0.022), (-edge * 0.5, zc + 0.022), (-edge, zc + top), (-edge, zc - bot), (-edge * 0.5, zc - 0.022), (0.03, zc - 0.022)],
                 0.012, mat=mat)
            if e == "Industrial":
                steps(p, 0.03, 0.04, zc + 0.022, 2, 0.008, M(loc=(0, 0.015, 0)), mat="chrome")
    _socket(p, L, r, 0.04)
    _tail(p, r, L * 0.7)


# ---------------------------------------------------------------- chisel


def _chisel_head(p, L, r):
    g, e = p.region, p.era
    mat = _blade_mat(p)
    Lb, w = J(p, 0.13, 0.12), J(p, 0.018, 0.2)
    z1 = L + Lb
    if g == "Ocean":
        # Bent gouge: the bit bows forward and its corners lift like horns.
        _flat_bit(p, L - 0.01, z1, 0.01, w, 0.006, mat)
        for s in (-1, 1):
            rod(p, (s * w / 2, 0, z1 - 0.004), (s * w * 0.7, 0, z1 + 0.008), 0.003, 0.001, mat=mat, segs=4)
    elif g == "Gale":
        # Tanged bit with a leaf-shaped blade.
        front(p, [(-0.004, L - 0.01), (0.004, L - 0.01), (w * 0.6, L + Lb * 0.7), (0, z1), (-w * 0.6, L + Lb * 0.7)], 0.005, mat=mat)
    elif g == "Radiant":
        rod(p, (0, 0, L - 0.01), (0, 0, L + Lb * 0.4), 0.005, mat="fit", segs=6)
        _flat_bit(p, L + Lb * 0.35, z1, 0.008, w, 0.005, mat)
    else:
        if e == "Primal":
            p.cyl(0.011, 0.004, Lb, T((0, 0, L - 0.01)), mat="iron", segs=5, noise=0.1)
        elif e == "Future":
            p.box((0.016, 0.01, Lb * 0.5), T((0, 0, L + Lb * 0.2)), mat="body", bevel=0.3)
            _flat_bit(p, L + Lb * 0.4, z1, 0.008, w, 0.003, "glow")
        else:
            _flat_bit(p, L - 0.01, z1, 0.01, w, 0.007, mat)
    _socket(p, L, r, 0.03)
    _tail(p, r, L * 0.6)


# ---------------------------------------------------------------- wrench


def _wrench_head(p, L, r):
    g, e = p.region, p.era
    mat = _blade_mat(p) if e != "Primal" else "body"
    Ro = J(p, 0.022, 0.12)
    zc = L + Ro * 0.9
    neck = [(-r * 0.9, L - 0.02), (r * 0.9, L - 0.02), (Ro * 0.55, zc - Ro * 0.6), (-Ro * 0.55, zc - Ro * 0.6)]
    if g == "Ocean":
        # Open jaw made of two horns curling apart.
        front(p, neck, 0.008, mat=mat)
        for s in (-1, 1):
            p.tube([(s * Ro * 0.4, 0, zc - Ro * 0.6), (s * Ro * 0.9, 0, zc), (s * Ro * 0.8, 0, zc + Ro * 0.8), (s * Ro * 0.4, 0, zc + Ro * 1.1)],
                   Ro * 0.22, mat=mat, segs=4)
    elif g == "Gale":
        # Box-end ring bristling with short pegs.
        front(p, neck, 0.008, mat=mat)
        p.ring(Ro * 0.7, Ro * 0.25, M(loc=(0, 0, zc), rot=(90, 0, 0)), mat=mat, segs=7)
        pegs(p, Ro * 0.85, 0, 4, Ro * 0.5, M(loc=(0, 0, zc), rot=(90, 0, 0)), mat=mat)
    elif g == "Radiant":
        # Ring spanner whose ring is a lotus.
        front(p, neck, 0.008, mat=mat)
        p.ring(Ro * 0.7, Ro * 0.2, M(loc=(0, 0, zc), rot=(90, 0, 0)), mat=mat, segs=8, square=False)
        petals(p, Ro * 0.95, 0, 4, Ro * 0.25, M(loc=(0, 0, zc), rot=(90, 0, 0)), mat="accent", tilt=80)
    else:
        if e == "Primal":
            p.tube([(0, 0, L - 0.02), (0, 0, zc), (-Ro, 0, zc + Ro), (-Ro * 1.6, 0, zc + Ro * 0.4)], Ro * 0.3, mat="iron", segs=5, noise=0.1)
        elif e == "Future":
            p.box((Ro * 2, 0.012, Ro * 2.4), T((0, 0, zc)), mat="body", bevel=0.3)
            p.box((Ro * 0.9, 0.014, Ro * 1.2), T((0, 0, zc + Ro * 0.5)), mat="glow", bevel=0)
        else:
            front(p, neck, 0.008, mat=mat)
            front(p, [(-Ro, zc - Ro * 0.6), (Ro, zc - Ro * 0.6), (Ro, zc + Ro), (Ro * 0.4, zc + Ro), (Ro * 0.4, zc), (-Ro * 0.4, zc), (-Ro * 0.4, zc + Ro), (-Ro, zc + Ro)],
                  0.009, mat=mat)
            if e == "Industrial":
                steps(p, Ro * 1.6, 0.012, L - 0.02, 2, 0.008, mat="chrome", shrink=0.8)
    _socket(p, L, r, 0.025, lotus=0)
    _tail(p, r, L * 0.6)


# ---------------------------------------------------------------- broom


def _broom_head(p, L, r):
    g, e = p.region, p.era
    H = J(p, 0.36, 0.12)
    if g == "Ocean":
        # Palm-rib broom: a fan of stiff thin ribs.
        n = p.rng.randint(8, 10)
        for i in range(n):
            t = i / (n - 1) - 0.5
            rod(p, (t * 0.03, 0, L - 0.04), (t * J(p, 0.3, 0.15), p.rng.uniform(-0.03, 0.03), L + H * p.rng.uniform(0.85, 1.05)), 0.004, 0.0015,
                mat="body" if e in HAND else ("cloth" if e == "Wasteland" else "fit"), segs=3)
    elif g == "Gale":
        # Short stiff grass bundle tied in a cone, painted band.
        p.lathe([(r * 1.2, L - 0.06), (0.04, L + 0.06), (J(p, 0.09, 0.15), L + H * 0.85), (0.0, L + H * 0.9)], mat="rope" if e in HAND else "cloth", segs=8)
        zig(p, 0.045, L + 0.06, 0.025, 6)
    elif g == "Radiant":
        # Soft grass broom: a long flat feathery fan bound with beads.
        sq = J(p, 0.3, 0.15)
        p.lathe([(r * 1.1, L - 0.06), (0.03, L + 0.08), (J(p, 0.12, 0.12), L + H * 0.8), (0.07, L + H * 1.05), (0.0, L + H * 1.1)],
                M(scale=(1, sq, 1)), mat="rope" if e not in ("Future", "Ancient") else p.role("grip"), segs=8)
        p.ring(r * 1.6, 0.005, T((0, 0, L + 0.03)), mat="accent", segs=8, square=False)
    else:
        if e == "Primal":
            for i in range(6):
                x = (i / 5 - 0.5) * 0.22
                p.tube([(x * 0.1, 0, L - 0.05), (x * 0.5, 0, L + 0.1), (x, p.rng.uniform(-0.03, 0.03), L + H * p.rng.uniform(0.85, 1.0))], 0.005, mat="body", segs=4)
        else:
            Wb = J(p, 0.32, 0.1)
            p.box((Wb, 0.05, 0.04), T((0, 0, L + 0.04)), mat="body" if e != "Future" else "shell_dark", bevel=0.2 if e == "Future" else 0)
            p.box((Wb * 0.96, 0.04, H * 0.3), T((0, 0, L + 0.06 + H * 0.15)), mat="rubber" if e in MACHINE else "hide", bevel=0)
            if e == "Industrial":
                steps(p, Wb * 0.4, 0.05, L + 0.06, 2, 0.012, mat="chrome")
            elif e == "Future":
                p.box((Wb, 0.052, 0.006), T((0, 0, L + 0.05)), mat="glow", bevel=0)
    _socket(p, L, r, J(p, 0.05, 0.2), lotus=0)
    _tail(p, r, L * 0.8)


for _g in REGIONS:
    regional("Sickle", _g)(r_hafted(0.27, 0.016, _sickle_head))
    regional("Shovel", _g)(r_hafted(1.05, 0.018, _shovel_head))
    regional("Pitchfork", _g)(r_hafted(1.2, 0.017, _fork_head))
    regional("Saw", _g)(r_hafted(0.13, 0.016, _saw_head))
    regional("Hatchet", _g)(r_hafted(0.58, 0.016, _hatchet_head))
    regional("Chisel", _g)(r_hafted(0.11, 0.014, _chisel_head))
    regional("Wrench", _g)(r_hafted(0.17, 0.011, _wrench_head))
    regional("Broom", _g)(r_hafted(1.15, 0.015, _broom_head))
