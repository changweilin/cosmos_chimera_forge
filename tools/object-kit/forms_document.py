"""Document family forms (cosmos_chimera everyday-objects-catalog.md 記錄與書本): Book, Scroll, Ledger, Map, Letter,
Newspaper, Notice. Slots follow the family order 封面／卷身、書脊／軸、扣件、頁緣／飾片: cover (boards, roll body,
tablet, sheet), spine (spine, axle, core, post), clasp (ties, straps, seals, hasps, pins), edge (page block, end
faces, marks and ornaments).

Frames: carried documents lie closed (books, tablets, folded sheets) or rolled (scrolls, along X) with their bottom
face at z = 0; that face rides the hand or the hip when an NPC carries one. Book spines face -Y and run along X so
the spine reads from the front. Notice is scene-only: a standing board, post or column with its floor contact at
z = 0. Writing is never letters: rows of strips with a per-variant rhythm, recoloured by the region's accent
(glaze), carved grooves, or Ancient rune slots. The Record group never glows (everyday-objects.md 發光), so only
Ancient rune slots use a glow material; screens and holograms are drawn as unlit glass.
Each form draws its F() frame values first, in a fixed order, so every slot of one (function, era) shares them.
"""
import math

from mathutils import Matrix

from kit_forms import F, J, coin, function
from kit_lib import M

DOC = ("cover", "spine", "clasp", "edge")
T = Matrix.Translation


# ---------------------------------------------------------------- helpers
def slab(p, w, d, t, z=0.0, x=0.0, y=0.0, mat="body", rz=0.0, **kw):
    """Box with its bottom face at z (one bevel segment: documents are small and many)."""
    kw.setdefault("bevel_seg", 1)
    p.box((w, d, t), T((x, y, z + t / 2)) @ M(rot=(0, 0, rz)), mat=mat, **kw)


def rollx(p, r, L, z, x=0.0, y=0.0, mat="body", segs=10, r2=None, cap=True, **kw):
    """Cylinder lying along X, centred on x, axis at height z."""
    p.cyl(r, r if r2 is None else r2, L, M(loc=(x - L / 2, y, z), rot=(0, 90, 0)), mat=mat, segs=segs, cap=cap, **kw)


def hoop(p, r, x, w, z, y=0.0, mat="rope", segs=10):
    """Open band of radius r and width w around a roll lying along X (cheaper than a torus)."""
    rollx(p, r, w, z, x=x, y=y, mat=mat, segs=segs, cap=False)


def flat(p, outline, t, z, mat="body", m=None, **kw):
    """Polygon outline in XY lying flat, bottom at z, thickness t."""
    kw.setdefault("bevel", 0)
    p.plate([(x, -y) for x, y in outline], t, (m or Matrix()) @ T((0, 0, z + t / 2)) @ M(rot=(90, 0, 0)), mat=mat, **kw)


def glyphs(p, L, h, m, mat="glaze", t=0.002):
    """Fake writing: a row of strips along local X in the local XZ plane, thin on Y, with a per-variant rhythm."""
    n = p.rng.randint(2, 5)
    ws = [p.rng.uniform(0.5, 1.6) for _ in range(n)]
    gap = 0.35
    s = sum(ws) + gap * (n - 1)
    x = -L / 2
    for w in ws:
        ww = L * w / s
        p.box((ww, t, h * p.rng.uniform(0.6, 1.0)), m @ T((x + ww / 2, 0, 0)), mat=mat, bevel=0)
        x += ww + L * gap / s


def text_top(p, x, y, z, L, h, rows=1, pitch=0.0, mat="glaze", rz=0.0):
    """Rows of fake writing lying on a top face at height z, rows stacked along Y."""
    for i in range(rows):
        yy = (i - (rows - 1) / 2) * pitch
        glyphs(p, L, h, T((x, y, z + 0.001)) @ M(rot=(0, 0, rz)) @ T((0, yy, 0)) @ M(rot=(90, 0, 0)), mat=mat)


def text_front(p, x, y, z, L, h, mat="glaze", rows=1, pitch=0.0):
    """Rows of fake writing standing on a -Y face at depth y."""
    for i in range(rows):
        glyphs(p, L, h, T((x, y - 0.001, z - i * pitch)), mat=mat)


def wrap(p, c, w, t, rad, mat, z0=0.0, mid=0.0, axis="x", segs=4):
    """Cord or strap loop around a lying block: crosses it at coordinate c along `axis`, spans width w (centred on
    mid) across, and thickness t up from z0."""
    hw = w / 2 + rad * 0.5
    lo, hi = z0 + rad, z0 + t + rad * 0.5
    ring = [(-hw, lo), (-hw, hi), (hw, hi), (hw, lo), (-hw, lo * 1.01)]
    if axis == "x":
        pts = [(c, mid + a, z) for a, z in ring]
    else:
        pts = [(mid + a, c, z) for a, z in ring]
    p.tube(pts, rad, mat=mat, segs=segs)


def cog(p, r, m, teeth=6, t=0.004, mat="brass"):
    """Light toothed disc in the local XZ plane (extruded along local Y)."""
    pts = []
    for i in range(teeth * 2):
        a = i * math.pi / teeth
        rr = r if i % 2 == 0 else r * 0.78
        pts.append((math.cos(a) * rr, math.sin(a) * rr))
    p.plate(pts, t, m, mat=mat, bevel=0)


def runes_top(p, x, y, z, L, n=3, w=0.008):
    """Row of rune slots lying on a top face (Ancient); they read by colour when the Record group does not glow."""
    for i in range(n):
        xx = x + (i - (n - 1) / 2) * L / n
        sz = (L / n * 0.55, w, 0.003) if i % 2 == 0 else (L / n * 0.3, w * 1.6, 0.003)
        p.box(sz, T((xx, y, z + 0.001)), mat="glow", bevel=0)


def runes_front(p, x, y, z, L, n=3, h=0.01):
    for i in range(n):
        xx = x + (i - (n - 1) / 2) * L / n
        sz = (L / n * 0.55, 0.003, h) if i % 2 == 0 else (L / n * 0.3, 0.003, h * 1.5)
        p.box(sz, T((xx, y - 0.001, z)), mat="glow", bevel=0)


def sheets(p, w, d, z, n, mat="bone", t=0.0015, spread=4.0, x=0.0, y=0.0):
    """Loose sheets stacked slightly askew from z."""
    for i in range(n):
        slab(p, w * J(p, 1, 0.04), d * J(p, 1, 0.04), t, z + i * t, x=x + J(p, 0.004, 1) * (1 if i % 2 else -1), y=y,
             mat=mat if i % 2 == 0 else "bone", rz=p.rng.uniform(-spread, spread), bevel=0)


def page_block(p, w, d, t, z, x=0.0, y=0.0):
    slab(p, w, d, t, z, x=x, y=y, mat="bone", bevel=0)


# ---------------------------------------------------------------- Book
@function("Book", "Document", DOC, "carried")
def book(p, slot):
    e = p.era
    H, W, Tk = F(p, 0.22, 0.1), F(p, 0.16, 0.1), F(p, 0.045, 0.2)
    # Height runs along X; the spine is the -Y edge, the fore-edge +Y.
    if e == "Primal":  # carved wooden boards laced together through the bound edge
        bt = Tk * 0.5
        if slot == "cover":
            slab(p, H, W, bt * 0.96, 0, mat="wood", noise=0.02)
            slab(p, H * J(p, 1.0, 0.04), W * J(p, 1.0, 0.04), bt * 0.96, bt, mat="wood", rz=p.rng.uniform(-3, 3), noise=0.02)
        elif slot == "spine":
            n = p.rng.randint(2, 4)
            for i in range(n):
                x = (i - (n - 1) / 2) * H / (n + 0.6)
                p.tube([(x, -W / 2 + 0.018, 2 * bt + 0.002), (x, -W / 2 - 0.005, bt), (x, -W / 2 + 0.018, 0.004)], 0.0045, mat="rope", segs=4)
        elif slot == "clasp":
            wrap(p, H * J(p, 0.2, 0.4) * (1 if coin(p) else -1), W, 2 * bt, J(p, 0.005, 0.2), "rope")
        else:
            text_top(p, 0, W * 0.05, 2 * bt, H * 0.7, 0.008, rows=p.rng.randint(2, 3), pitch=W * 0.22, mat="wood_dark")
            if coin(p):
                p.ball(0.012, M(loc=(H * 0.38, W * 0.3, 2 * bt), scale=(1, 1, 0.4)), mat="bone", segs=(6, 3))
    elif e == "Agrarian":  # bamboo slips rolled into a bundle
        r = Tk * 0.85
        L = H * 1.1
        if slot == "cover":
            rollx(p, r, L, r, mat="wood", segs=12)
            p.box((L * J(p, 1.04, 0.03), 0.012, 0.004), T((0, 0, 2 * r + 0.001)), mat="wood", bevel=0)
        elif slot == "spine":
            for s in (-1, 1):
                hoop(p, r * 1.04, s * L * J(p, 0.3, 0.12), 0.008, r, mat="rope", segs=12)
        elif slot == "clasp":
            x = L * 0.3
            ty = -r - J(p, 0.05, 0.3)
            p.tube([(x, -r * 0.6, r * 1.6), (x, -r * 1.02, r * 0.8), (x + 0.01, ty * 0.8, 0.004), (x + 0.03, ty, 0.003)], 0.0025, mat="rope", segs=4)
            slab(p, J(p, 0.05, 0.2), 0.018, 0.004, 0, x=x + 0.05, y=ty, mat="wood_dark", bevel=0, rz=J(p, 20, 0.8))
        else:
            for s in (-1, 1):
                p.cyl(r * J(p, 0.55, 0.15), r * 0.55, 0.002, M(loc=(s * L / 2, 0, r), rot=(0, 90 * s, 0)), mat="wood_dark", segs=8, bevel=0)
            text_front(p, -L * 0.05, -r, r, L * 0.5, 0.012)
    elif e == "Mercantile":  # leather binding, raised bands, strap to a brass stud
        bt = 0.006
        if slot == "cover":
            for z in (0, Tk - bt):
                slab(p, H + 0.012, W + 0.006, bt, z, y=0.003, mat="leather")
        elif slot == "spine":
            rollx(p, Tk / 2, H + 0.012, Tk / 2, y=-W / 2, mat="leather", segs=8)
            n = p.rng.randint(3, 5)
            for i in range(n):
                hoop(p, Tk / 2 * 1.12, (i - (n - 1) / 2) * H / (n + 0.5), 0.006, Tk / 2, y=-W / 2, mat="leather", segs=8)
            text_front(p, 0, -W / 2 - Tk / 2, Tk / 2, H * 0.35, 0.01, mat="gold")
        elif slot == "clasp":
            x = H * J(p, 0.0, 1) + H * 0.1 * (1 if coin(p) else -1)
            p.tube([(x, W / 2, 0.003), (x, W / 2 + 0.012, Tk / 2), (x, W / 2 + 0.006, Tk + 0.003), (x, W / 2 - J(p, 0.04, 0.2), Tk + 0.003)], 0.004, mat="leather", segs=4)
            p.ball(0.006, T((x, W / 2 - 0.035, Tk + 0.004)), mat="brass", segs=(6, 3))
        else:
            page_block(p, H - J(p, 0.006, 0.4), W - 0.004, Tk - 2 * bt, bt, x=0, y=0.002)
            if coin(p, 0.6):
                c = J(p, 0.03, 0.2)
                for sx in (-1, 1):
                    xx = sx * (H / 2 + 0.006)
                    flat(p, [(xx, W / 2 + 0.006), (xx - sx * c, W / 2 + 0.006), (xx, W / 2 + 0.006 - c)], 0.002, Tk, mat="brass")
    elif e == "Industrial":  # cloth hardcover, printed spine bands
        bt = 0.004
        if slot == "cover":
            for z in (0, Tk - bt):
                slab(p, H + 0.008, W + 0.004, bt, z, y=0.002, mat="paint", bevel=0)
        elif slot == "spine":
            p.box((H + 0.008, 0.004, Tk), T((0, -W / 2 - 0.002, Tk / 2)), mat="paint", bevel=0)
            for s in (-1, 1):
                p.box((J(p, 0.012, 0.4), 0.002, Tk * 0.9), T((s * H * 0.4, -W / 2 - 0.005, Tk / 2)), mat="glaze", bevel=0)
            text_front(p, -H * 0.05, -W / 2 - 0.004, Tk / 2, H * 0.45, Tk * 0.35, mat="bone")
        elif slot == "clasp":
            if coin(p):
                wrap(p, H * J(p, 0.25, 0.3), W, Tk, 0.003, "rubber")
            else:
                y = J(p, 0.0, 1) + W * 0.1
                p.tube([(H / 2 - 0.01, y, Tk * 0.5), (H / 2 + 0.006, y, Tk * 0.35), (H / 2 + J(p, 0.04, 0.3), y + 0.01, 0.002)], 0.003, mat="cloth", segs=4)
        else:
            page_block(p, H - 0.002, W - 0.002, Tk - 2 * bt, bt, y=0.001)
            if coin(p):
                p.box((H + 0.01, W * J(p, 0.25, 0.2), 0.002), T((0, W * 0.05, Tk + 0.001)), mat="glaze", bevel=0)
    elif e == "Steampunk":  # leather boards, brass ribbed spine, locking hasps, cog emblem
        bt = 0.007
        if slot == "cover":
            for z in (0, Tk - bt):
                slab(p, H + 0.014, W + 0.006, bt, z, y=0.003, mat="leather")
        elif slot == "spine":
            rollx(p, Tk / 2 * 1.03, H + 0.016, Tk / 2, y=-W / 2, mat="brass", segs=8)
            for i in range(p.rng.randint(2, 3)):
                hoop(p, Tk / 2 * 1.14, (i - 1) * H * J(p, 0.32, 0.1), 0.008, Tk / 2, y=-W / 2, mat="copper", segs=8)
            text_front(p, 0, -W / 2 - Tk / 2 * 1.04, Tk / 2, H * 0.3, 0.008, mat="glaze")
        elif slot == "clasp":
            n = 1 if coin(p) else 2
            for i in range(n):
                x = 0 if n == 1 else (i - 0.5) * H * J(p, 0.5, 0.1)
                y0 = W / 2 + 0.006
                p.box((0.022, 0.035, 0.003), T((x, y0 - 0.017, Tk + 0.0015)), mat="brass", bevel=0)
                p.box((0.022, 0.004, Tk + 0.003), T((x, y0 + 0.002, Tk / 2)), mat="brass", bevel=0)
                p.cyl(0.007, 0.007, 0.003, M(loc=(x, y0 + 0.004, Tk / 2), rot=(-90, 0, 0)), mat="copper", segs=8, bevel=0)
        else:
            page_block(p, H, W - 0.002, Tk - 2 * bt, bt, y=0.001)
            r = J(p, 0.035, 0.15)
            cog(p, r, T((0, W * 0.02, Tk + 0.002)) @ M(rot=(90, 0, 0)), teeth=p.rng.randint(6, 8), t=0.003, mat="brass")
            p.cyl(r * 0.35, r * 0.35, 0.004, T((0, W * 0.02, Tk)), mat="copper", segs=8, bevel=0)
    elif e == "Future":  # e-reader slate in a folio hinge
        tb = Tk * 0.28
        if slot == "cover":
            slab(p, H, W, tb, mat="body")
        elif slot == "spine":
            rollx(p, tb * 0.62, H * J(p, 1.0, 0.03), tb * 0.62, y=-W / 2, mat="shell_dark", segs=8)
        elif slot == "clasp":
            w = J(p, 0.03, 0.25)
            x = H * J(p, 0.2, 0.3)
            p.box((w, 0.03, 0.002), T((x, W / 2 - 0.012, tb + 0.001)), mat="shell_dark", bevel=0)
            p.box((w, 0.003, tb + 0.002), T((x, W / 2 + 0.0015, tb / 2)), mat="shell_dark", bevel=0)
        else:
            sw, sd = H * 0.8, W * 0.78
            p.box((sw, sd, 0.0015), T((-H * 0.04, 0.0, tb + 0.0007)), mat="glass", bevel=0)
            text_top(p, -H * 0.04, 0, tb + 0.0015, sw * 0.8, 0.004, rows=p.rng.randint(3, 5), pitch=sd * 0.18, mat="shell_dark")
            p.cyl(0.006, 0.006, 0.002, T((H * 0.45, 0, tb)), mat="shell_dark", segs=8, bevel=0)
    elif e == "Wasteland":  # salvaged boards, taped spine, wired shut, loose sheets
        bt = 0.004
        if slot == "cover":
            slab(p, H + 0.01, W + 0.006, 0.003, 0, mat="rust", bevel=0)
            slab(p, H * J(p, 1.02, 0.03), W * J(p, 1.0, 0.04), 0.005, Tk - 0.005, mat="hide", rz=p.rng.uniform(-4, 4), bevel=0)
            slab(p, H * 0.3, W * 0.3, 0.002, Tk, x=H * J(p, 0.2, 0.5), y=W * 0.15, mat="cloth", rz=J(p, 15, 0.5), bevel=0)
        elif slot == "spine":
            p.box((H + 0.012, 0.004, Tk + 0.004), T((0, -W / 2 - 0.004, Tk / 2)), mat="cloth", bevel=0)
            for z in (0.0, Tk):
                p.box((H + 0.012, J(p, 0.03, 0.3), 0.002), T((0, -W / 2 + 0.01, z + (0.001 if z else 0.001))), mat="cloth", bevel=0)
            text_front(p, 0, -W / 2 - 0.006, Tk / 2, H * 0.5, Tk * 0.4, mat="paint")
        elif slot == "clasp":
            if coin(p):
                x = H * J(p, 0.15, 0.6)
                wrap(p, x, W + 0.01, Tk + 0.002, 0.002, "iron")
                wrap(p, x + 0.008, W + 0.01, Tk + 0.002, 0.002, "iron")
            else:
                wrap(p, H * J(p, -0.2, 0.4), W + 0.01, Tk + 0.002, 0.004, "leather")
                p.box((0.018, 0.012, 0.004), T((H * -0.2, W / 2 - 0.02, Tk + 0.006)), mat="iron", bevel=0)
        else:
            page_block(p, H - 0.004, W - 0.004, Tk - bt - 0.006, 0.003, y=0.001)
            for i in range(p.rng.randint(1, 3)):
                slab(p, J(p, 0.1, 0.3), J(p, 0.12, 0.2), 0.0015, 0.008 + i * 0.012, x=J(p, 0.02, 1) - 0.02, y=W * 0.35,
                     mat="bone" if i % 2 else "paint", rz=p.rng.uniform(-25, 25), bevel=0)
    else:  # Ancient: stone codex, rune-slotted spine block, gold lock bar
        bt = Tk * 0.25
        if slot == "cover":
            for z in (0, Tk - bt):
                slab(p, H + 0.01, W + 0.006, bt, z, y=0.003, mat="stone")
        elif slot == "spine":
            slab(p, H + 0.014, 0.018, Tk, 0, y=-W / 2 - 0.004, mat="stone_dark")
            runes_front(p, 0, -W / 2 - 0.013, Tk / 2, H * J(p, 0.6, 0.15), n=p.rng.randint(3, 5), h=Tk * 0.3)
        elif slot == "clasp":
            n = 1 if coin(p) else 2
            for i in range(n):
                x = (i - (n - 1) / 2) * H * 0.45
                p.box((0.016, 0.03, 0.004), T((x, W / 2 - 0.008, Tk + 0.002)), mat="gold", bevel=0)
                p.box((0.016, 0.006, Tk + 0.004), T((x, W / 2 + 0.009, Tk / 2)), mat="gold", bevel=0)
            p.box((J(p, 0.012, 0.3), 0.003, 0.008), T((0, W / 2 + 0.0125, Tk / 2)), mat="glow", bevel=0)
        else:
            n = p.rng.randint(2, 3)
            lt = (Tk - 2 * bt) / n
            for i in range(n):
                slab(p, H - 0.004, W - 0.006, lt * 0.8, bt + i * lt + lt * 0.1, mat="stone_dark", bevel=0)
            runes_top(p, 0, W * 0.05, Tk, H * J(p, 0.5, 0.2), n=3, w=0.01)


# ---------------------------------------------------------------- Scroll
@function("Scroll", "Document", DOC, "carried")
def scroll(p, slot):
    e = p.era
    L, r = F(p, 0.3, 0.1), F(p, 0.026, 0.15)
    if e == "Primal":  # rolled bark sheet on a twig, vine tie, ochre marks on the loose flap
        fw = 0.05
        if slot == "cover":
            rollx(p, r, L * 0.9, r, mat="bark", segs=8, noise=0.04)
            slab(p, L * 0.86, fw, 0.004, 0, y=-r * 0.5 - fw / 2, mat="bark", noise=0.02, bevel=0)
        elif slot == "spine":
            rollx(p, r * 0.25, L * J(p, 1.15, 0.05), r, x=J(p, 0.01, 1), mat="wood", segs=5)
        elif slot == "clasp":
            for i in range(p.rng.randint(1, 2)):
                hoop(p, r * 1.05, L * J(p, 0.25, 0.3) * (1 - 2 * i), 0.006, r, mat="rope", segs=8)
        else:
            text_top(p, 0, -r * 0.5 - fw / 2, 0.004, L * J(p, 0.6, 0.15), 0.01, rows=2, pitch=0.018, mat="paint")
    elif e == "Agrarian":  # silk roll on a wooden rod with knobbed ends, cord and tassel
        if slot == "cover":
            rollx(p, r, L, r, mat="cloth", segs=10)
        elif slot == "spine":
            ext = J(p, 0.03, 0.2)
            rollx(p, r * 0.3, L + ext * 2, r, mat="wood_dark", segs=6)
            for s in (-1, 1):
                p.ball(r * J(p, 0.55, 0.15), T((s * (L / 2 + ext), 0, r)), mat="ceramic", segs=(6, 4))
        elif slot == "clasp":
            x = L * J(p, 0.1, 0.8)
            hoop(p, r * 1.05, x, 0.004, r, mat="rope", segs=10)
            p.tube([(x, -r, r), (x + 0.01, -r * 1.5, r * 0.4), (x + 0.02, -r * 2.4, 0.004)], 0.002, mat="rope", segs=4)
            p.cyl(0.006, 0.003, J(p, 0.03, 0.2), M(loc=(x + 0.02, -r * 2.4, 0.004), rot=(90, 0, 20)), mat="glaze", segs=5)
        else:
            for s in (-1, 1):
                hoop(p, r * 1.02, s * (L / 2 - 0.012), J(p, 0.02, 0.2), r, mat="glaze", segs=10)
            slab(p, J(p, 0.05, 0.2), 0.012, 0.002, 2 * r, x=-L * 0.25, mat="bone", bevel=0)
    elif e == "Mercantile":  # parchment roll, ribbon and wax seal, a lip unrolled on the table
        if slot == "cover":
            rollx(p, r, L, r, mat="hide", segs=10)
            slab(p, L * 0.98, J(p, 0.03, 0.3), 0.002, 0, y=-r - 0.01, mat="hide", bevel=0)
        elif slot == "spine":
            for s in (-1, 1):
                for k, rr in enumerate((0.7, 0.4)):
                    p.cyl(r * rr * J(p, 1, 0.1), r * rr, 0.002, M(loc=(s * L / 2, 0, r), rot=(0, 90 * s, 0)), mat="bone" if k else "leather", segs=8, bevel=0)
        elif slot == "clasp":
            x = L * J(p, 0.05, 1)
            hoop(p, r * 1.04, x, J(p, 0.01, 0.3), r, mat="paint", segs=10)
            p.cyl(0.011, 0.011, 0.004, M(loc=(x, -r * 0.7, r * 1.75), rot=(-45, 0, 0)), mat="paint", segs=8)
        else:
            p.tube([(-L / 2, -r - 0.02, 0.001), (0, -r - J(p, 0.024, 0.3), 0.001), (L / 2, -r - 0.02, 0.001)], 0.0015, mat="bone", segs=4)
            text_top(p, 0, -r - 0.012, 0.002, L * 0.6, 0.004, mat="glaze")
    elif e == "Industrial":  # blueprint tube with steel caps and a carry strap
        R = r * 1.5
        if slot == "cover":
            rollx(p, R, L, R, mat="paint", segs=12)
        elif slot == "spine":
            for s in (-1, 1):
                p.cyl(R * 1.08, R * 1.08, J(p, 0.03, 0.2), M(loc=(s * L / 2, 0, R), rot=(0, -90 * s, 0)), mat="steel", segs=12)
        elif slot == "clasp":
            xs = L * J(p, 0.32, 0.1)
            p.tube([(-xs, -R * 0.2, 2 * R), (-xs * 0.5, -R * 1.3, 0.003), (xs * 0.5, -R * 1.4, 0.003), (xs, -R * 0.2, 2 * R)], 0.003, mat="cloth", segs=4)
            for s in (-1, 1):
                p.box((0.012, 0.01, 0.006), T((s * xs, -R * 0.1, 2 * R + 0.002)), mat="steel", bevel=0)
        else:
            rollx(p, R * 0.8, J(p, 0.05, 0.3), R, x=L / 2 + 0.025, mat="glaze", segs=10)
            hoop(p, R * 1.01, -L * J(p, 0.1, 0.5), 0.04, R, mat="bone", segs=12)
    elif e == "Steampunk":  # brass scroll housing with a slot, end cogs and winding crank
        R = r * 1.4
        if slot == "cover":
            rollx(p, R, L, R, mat="brass", segs=10)
            p.box((L * 0.85, 0.004, 0.006), T((0, -R * 0.98, R * 0.55)), mat="rubber", bevel=0)
        elif slot == "spine":
            for s in (-1, 1):
                cog(p, R * J(p, 1.1, 0.06), T((s * (L / 2 + 0.003), 0, R)) @ M(rot=(0, 0, 90)), teeth=p.rng.randint(6, 8), t=0.005, mat="copper")
        elif slot == "clasp":
            x0 = L / 2 + 0.006
            arm = J(p, 0.03, 0.2)
            p.tube([(x0, 0, R), (x0 + 0.01, 0, R), (x0 + 0.01, 0, R + arm), (x0 + 0.03, 0, R + arm)], 0.003, mat="brass", segs=4)
            p.cyl(0.005, 0.005, 0.018, M(loc=(x0 + 0.03, 0, R + arm), rot=(0, 90, 0)), mat="wood_dark", segs=6, bevel=0)
        else:
            tl = J(p, 0.05, 0.25)
            slab(p, L * 0.8, tl, 0.0015, 0, y=-R * 0.8 - tl / 2, mat="bone", bevel=0)
            text_top(p, 0, -R * 0.8 - tl / 2, 0.0015, L * 0.6, 0.005, rows=2, pitch=tl * 0.35, mat="rubber")
            for s in (-1, 1):
                p.ball(0.003, T((s * L * 0.44, -R * 0.97, R * 1.1)), mat="copper", segs=(4, 3))
    elif e == "Future":  # slim holo-scroll rod with a film pulled out flat
        R = r * 0.7
        if slot == "cover":
            prof = [(0, 0), (R * 0.8, 0.004), (R, 0.015), (R, L - 0.015), (R * 0.8, L - 0.004), (0, L)]
            p.lathe(prof, M(loc=(-L / 2, 0, R), rot=(0, 90, 0)), mat="body", segs=10)
        elif slot == "spine":
            for s in (-1, 1):
                hoop(p, R * 1.08, s * (L / 2 - J(p, 0.03, 0.2)), 0.012, R, mat="shell_dark", segs=10)
        elif slot == "clasp":
            p.box((J(p, 0.03, 0.25), 0.008, 0.005), T((L * 0.1, -R * 0.4, 2 * R)), mat="shell_dark", bevel=0)
        else:
            fl = J(p, 0.09, 0.25)
            slab(p, L * 0.82, fl, 0.001, 0, y=-R - fl / 2, mat="glass", bevel=0)
            text_top(p, 0, -R - fl / 2, 0.001, L * 0.6, 0.004, rows=p.rng.randint(2, 4), pitch=fl * 0.2, mat="shell_dark")
    elif e == "Wasteland":  # plastic sheet rolled on a pipe, wire-twisted, taped
        if slot == "cover":
            rollx(p, r, L * 0.85, r, mat="paint", segs=8)
            rollx(p, r * 1.03, L * 0.3, r, x=L * 0.15, mat="cloth", segs=8, cap=False)
        elif slot == "spine":
            rollx(p, r * 0.35, L * J(p, 1.1, 0.06), r, x=J(p, 0.02, 1), mat="rust", segs=6)
        elif slot == "clasp":
            for i in range(p.rng.randint(1, 3)):
                p.ring(r * 1.04, 0.0018, M(loc=(L * (i * 0.25 - 0.3), 0, r), rot=(0, 90 + J(p, 8, 1), 0)), mat="iron", segs=8)
        else:
            slab(p, L * 0.5, J(p, 0.03, 0.3), 0.002, 0, x=-L * 0.1, y=-r - 0.012, mat="paint", rz=J(p, 4, 1), bevel=0)
            p.box((0.03, 0.002, 0.02), T((-L * 0.3, -r - 0.001, r)), mat="cloth", bevel=0)
    else:  # Ancient: stone scroll case, gold end discs, rune ring lock
        R = r * 1.3
        if slot == "cover":
            p.lathe([(0, 0), (R * 0.9, 0), (R, 0.01), (R, L - 0.01), (R * 0.9, L), (0, L)], M(loc=(-L / 2, 0, R), rot=(0, 90, 0)), mat="stone", segs=8)
        elif slot == "spine":
            for s in (-1, 1):
                p.cyl(R * J(p, 0.75, 0.15), R * 0.6, 0.008, M(loc=(s * L / 2, 0, R), rot=(0, 90 * s, 0)), mat="gold", segs=8, bevel=0)
        elif slot == "clasp":
            x = L * J(p, 0.15, 0.5)
            hoop(p, R * 1.06, x, 0.014, R, mat="stone_dark", segs=8)
            p.box((0.006, 0.003, R * 0.5), T((x, -R * 1.08, R)), mat="glow", bevel=0)
        else:
            runes_front(p, -L * 0.1, -R, R, L * J(p, 0.55, 0.15), n=p.rng.randint(3, 5), h=R * 0.3)


# ---------------------------------------------------------------- Ledger
@function("Ledger", "Document", DOC, "carried")
def ledger(p, slot):
    e = p.era
    W, D, Tk = F(p, 0.26, 0.1), F(p, 0.18, 0.1), F(p, 0.03, 0.2)
    if e == "Primal":  # knotted-cord tally: a top cord with hanging pendants laid flat
        rr = 0.006
        y0 = -D / 2
        xs = [(i - 3) * W / 7 for i in range(7)]
        if slot == "cover":
            p.tube([(-W / 2 - 0.02, y0, rr), (0, y0 - 0.004, rr), (W / 2 + 0.02, y0, rr)], rr, mat="rope", segs=5)
        elif slot == "spine":
            for i, x in enumerate(xs):
                L = D * J(p, 0.85, 0.15)
                w = J(p, 0.01, 1)
                p.tube([(x, y0, 0.003), (x + w, y0 + L * 0.5, 0.003), (x - w * 0.5, y0 + L, 0.003)], 0.003, mat="rope" if i % 2 else "cloth", segs=4)
        elif slot == "clasp":
            for x in xs:
                for k in range(p.rng.randint(1, 2)):
                    p.ball(0.006, T((x, y0 + D * p.rng.uniform(0.2, 0.75), 0.004)), mat="rope", segs=(4, 3))
        else:
            for s in (-1, 1):
                p.cyl(0.006, 0.006, J(p, 0.04, 0.2), M(loc=(s * (W / 2 + 0.02), y0, rr), rot=(0, 90 * s, 0)), mat="bone", segs=6)
    elif e == "Agrarian":  # clay tablet with a rounded binding edge, cord and clay bulla, wedge rows
        w, d, t = W * 0.6, D * 0.7, Tk * 0.8
        if slot == "cover":
            slab(p, w, d, t, mat="ceramic", bevel=0.4, noise=0.01)
        elif slot == "spine":
            rollx(p, t * 0.55, w * J(p, 0.96, 0.03), t * 0.55, y=-d / 2, mat="ceramic", segs=6)
        elif slot == "clasp":
            x = w * J(p, 0.35, 0.15)
            p.tube([(x, d / 2 - 0.01, t), (x + 0.01, d / 2 + 0.01, t * 0.6), (x + 0.03, d / 2 + 0.03, 0.006)], 0.002, mat="rope", segs=4)
            p.ball(J(p, 0.012, 0.2), M(loc=(x + 0.035, d / 2 + 0.035, 0.008), scale=(1, 1, 0.7)), mat="ceramic", segs=(6, 4))
        else:
            text_top(p, 0, 0.004, t, w * 0.8, 0.005, rows=p.rng.randint(3, 4), pitch=d * 0.18, mat="stone_dark")
    elif e == "Mercantile":  # long account book: leather wrap, stitched spine, wound thong, index tabs
        H, Wd = W * 1.15, D * 0.6
        bt = 0.005
        if slot == "cover":
            for z in (0, Tk - bt):
                slab(p, H + 0.01, Wd + 0.004, bt, z, y=0.002, mat="leather")
        elif slot == "spine":
            p.box((H + 0.01, 0.004, Tk), T((0, -Wd / 2 - 0.002, Tk / 2)), mat="leather", bevel=0)
            n = p.rng.randint(3, 5)
            for i in range(n):
                x = (i - (n - 1) / 2) * H / (n + 0.4)
                p.box((0.004, 0.003, Tk * 0.8), T((x, -Wd / 2 - 0.0045, Tk / 2)), mat="rope", bevel=0)
        elif slot == "clasp":
            x = H * J(p, 0.05, 1)
            wrap(p, x, Wd + 0.006, Tk, 0.003, "leather")
            wrap(p, x + 0.012, Wd + 0.006, Tk, 0.003, "leather")
            p.cyl(0.004, 0.004, J(p, 0.025, 0.2), M(loc=(x - 0.01, Wd / 2 + 0.006, Tk / 2), rot=(0, 90, 0)), mat="bone", segs=5)
        else:
            page_block(p, H - 0.004, Wd - 0.003, Tk - 2 * bt, bt, y=0.0015)
            for i in range(p.rng.randint(2, 4)):
                slab(p, 0.016, 0.01, 0.0015, bt + (i + 1) * (Tk - 2 * bt) / 5, x=-H * 0.3 + i * H * 0.17, y=Wd / 2 + 0.004, mat="paint", bevel=0)
    elif e == "Industrial":  # punched-card deck in a steel tray, rubber band
        cw, cd, ct = W * 0.72, D * 0.45, Tk * 1.1
        if slot == "cover":
            c = J(p, 0.012, 0.3)
            flat(p, [(-cw / 2 + c, -cd / 2), (cw / 2, -cd / 2), (cw / 2, cd / 2), (-cw / 2, cd / 2), (-cw / 2, -cd / 2 + c)], ct, 0.003, mat="bone")
        elif slot == "spine":
            slab(p, cw + 0.012, cd + 0.012, 0.003, 0, mat="steel", bevel=0)
            for s in (-1, 1):
                slab(p, 0.002, cd + 0.012, ct * J(p, 0.5, 0.2), 0.003, x=s * (cw / 2 + 0.005), mat="steel", bevel=0)
            slab(p, cw + 0.012, 0.002, ct * 0.4, 0.003, y=cd / 2 + 0.005, mat="steel", bevel=0)
        elif slot == "clasp":
            wrap(p, cw * J(p, 0.2, 0.4) * (1 if coin(p) else -1), cd, ct, 0.002, "rubber", z0=0.003)
        else:
            for i in range(p.rng.randint(3, 4)):
                y = -cd * 0.3 + i * cd * 0.2
                for k in range(p.rng.randint(3, 6)):
                    p.box((0.003, 0.006, 0.001), T((-cw * 0.4 + p.rng.uniform(0, cw * 0.8), y, ct + 0.0035)), mat="rubber", bevel=0)
    elif e == "Steampunk":  # brass counting-ledger machine: sloped case, counter drum, lever, paper tape
        w, d, hf, hb = W * 0.6, D * 0.6, Tk * 1.6, Tk * 2.6
        if slot == "cover":
            p.plate([(-d / 2, 0), (d / 2, 0), (d / 2, hb), (-d / 2, hf)], w, M(rot=(0, 0, 90)), mat="brass")
        elif slot == "spine":
            zc = (hf + hb) / 2 + 0.006
            rollx(p, 0.01, w * J(p, 0.7, 0.1), zc, mat="bone", segs=8)
            for i in range(p.rng.randint(3, 5)):
                hoop(p, 0.0105, -w * 0.3 + i * w * 0.15, 0.002, zc, mat="copper", segs=8)
        elif slot == "clasp":
            x = w / 2 + 0.004
            ang = J(p, 25, 0.5)
            p.cyl(0.006, 0.006, 0.006, M(loc=(x, 0, hf * 0.8), rot=(0, 90, 0)), mat="copper", segs=6)
            p.tube([(x + 0.006, 0, hf * 0.8), (x + 0.006, -math.sin(math.radians(ang)) * 0.04, hf * 0.8 + math.cos(math.radians(ang)) * 0.04)], 0.0025, mat="brass", segs=4)
            p.ball(0.006, T((x + 0.006, -math.sin(math.radians(ang)) * 0.04, hf * 0.8 + math.cos(math.radians(ang)) * 0.04)), mat="wood_dark", segs=(5, 3))
        else:
            tl = J(p, 0.06, 0.3)
            p.tube([(0, -d / 2 + 0.002, hf * 0.5), (0, -d / 2 - 0.012, hf * 0.3), (0, -d / 2 - 0.02, 0.002), (0, -d / 2 - tl, 0.001)], 0.0012, mat="bone", segs=4)
            slab(p, 0.03, tl * 0.8, 0.001, 0, y=-d / 2 - tl * 0.6, mat="bone", bevel=0)
            text_top(p, 0, -d / 2 - tl * 0.6, 0.001, 0.024, 0.003, rows=2, pitch=0.008, mat="rubber")
    elif e == "Future":  # data slate with side rail, stylus, screen bars
        w, d, t = W * 0.8, D * 0.85, Tk * 0.35
        if slot == "cover":
            slab(p, w, d, t, mat="body")
        elif slot == "spine":
            rollx(p, t * 0.5, w * J(p, 0.98, 0.02), t * 0.5, y=-d / 2 - t * 0.25, mat="shell_dark", segs=8)
        elif slot == "clasp":
            rollx(p, 0.0035, w * J(p, 0.6, 0.15), t + 0.0035, y=d / 2 - 0.008, x=w * 0.1, mat="shell_dark", segs=6)
        else:
            p.box((w * 0.82, d * 0.72, 0.0015), T((0, 0.004, t + 0.0007)), mat="glass", bevel=0)
            for i in range(p.rng.randint(2, 4)):
                hh = d * p.rng.uniform(0.15, 0.45)
                p.box((w * 0.08, hh, 0.001), T((-w * 0.3 + i * w * 0.14, -d * 0.3 + hh / 2, t + 0.0018)), mat="shell_dark", bevel=0)
    elif e == "Wasteland":  # scrap clipboard: plate board, mixed sheets, big clip, tally marks
        w, d = W * 0.85, D * 1.1
        if slot == "cover":
            flat(p, [(-w / 2, -d / 2), (w / 2, -d / 2 + J(p, 0.01, 1)), (w / 2 - 0.01, d / 2), (-w / 2 + 0.005, d / 2)], 0.004, 0, mat="rust")
        elif slot == "spine":
            sheets(p, w * 0.85, d * 0.82, 0.004, p.rng.randint(2, 3), mat="paint", spread=5, y=0.01)
        elif slot == "clasp":
            cw = J(p, 0.06, 0.2)
            slab(p, cw, 0.035, 0.006, 0.008, y=-d / 2 + 0.02, mat="iron", bevel=0)
            p.tube([(-cw * 0.4, -d / 2 + 0.03, 0.014), (0, -d / 2 + 0.05, 0.024), (cw * 0.4, -d / 2 + 0.03, 0.014)], 0.002, mat="iron", segs=4)
        else:
            for g in range(p.rng.randint(1, 3)):
                gx = -w * 0.25 + g * w * 0.22
                for i in range(4):
                    p.box((0.002, 0.03, 0.001), T((gx + i * 0.008, d * 0.1, 0.0125)), mat="rubber", bevel=0)
                p.box((0.04, 0.002, 0.001), M(loc=(gx + 0.012, d * 0.1, 0.0128), rot=(0, 0, -50)), mat="rubber", bevel=0)
    else:  # Ancient: stone tally slab with grooved tracks and gold counter beads
        w, d, t = W * 0.8, D * 0.8, Tk * 0.9
        rows = 3
        if slot == "cover":
            slab(p, w, d, t, mat="stone")
        elif slot == "spine":
            for i in range(rows):
                slab(p, w * J(p, 0.8, 0.06), 0.006, 0.003, t, y=-d * 0.25 + i * d * 0.25, mat="stone_dark", bevel=0)
        elif slot == "clasp":
            for i in range(rows):
                for k in range(p.rng.randint(1, 4)):
                    p.ball(0.008, M(loc=(-w * 0.35 + p.rng.uniform(0, w * 0.7), -d * 0.25 + i * d * 0.25, t + 0.006), scale=(1, 1, 0.75)), mat="gold", segs=(6, 4))
        else:
            runes_top(p, 0, d * 0.4, t, w * J(p, 0.6, 0.15), n=p.rng.randint(3, 5), w=0.008)
            runes_front(p, 0, -d / 2, t / 2, w * 0.4, n=3, h=t * 0.3)


# ---------------------------------------------------------------- Map
@function("Map", "Document", DOC, "carried")
def map_(p, slot):
    e = p.era
    W, D, Tk = F(p, 0.26, 0.1), F(p, 0.2, 0.1), F(p, 0.012, 0.2)
    if e == "Primal":  # folded hide chart, sinew tie, painted trails
        if slot == "cover":
            pts = [(-W / 2, -D / 2), (-W * 0.1, -D / 2 - 0.012), (W / 2, -D / 2 + 0.004), (W / 2 + 0.01, D * 0.1),
                   (W / 2 - 0.006, D / 2), (0, D / 2 + 0.01), (-W / 2 + 0.01, D / 2 - 0.004), (-W / 2 - 0.012, 0)]
            flat(p, pts, 0.004, 0, mat="hide", noise=0.01)
            flat(p, [(x * 0.96, y * 0.92 + 0.006) for x, y in pts], 0.004, 0.004, mat="hide", noise=0.01)
        elif slot == "spine":
            rollx(p, 0.006, W * J(p, 0.95, 0.04), 0.006, y=-D / 2 + 0.002, mat="hide", segs=6)
        elif slot == "clasp":
            wrap(p, W * J(p, 0.22, 0.3) * (1 if coin(p) else -1), D * 0.95, 0.008, 0.002, "rope")
        else:
            pts = [(-W * 0.35, -D * 0.2, 0.0095), (-W * 0.1, D * J(p, 0.1, 1), 0.0095), (W * 0.15, -D * 0.05, 0.0095), (W * 0.32, D * J(p, 0.25, 0.4), 0.0095)]
            p.tube(pts, 0.002, mat="paint", segs=4)
            for i in range(p.rng.randint(2, 4)):
                p.ball(0.005, M(loc=(p.rng.uniform(-W * 0.35, W * 0.35), p.rng.uniform(-D * 0.3, D * 0.3), 0.0085), scale=(1, 1, 0.3)), mat="paint", segs=(5, 3))
    elif e == "Agrarian":  # painted hand-scroll half unrolled: roll at -X, painted sheet laid out
        r = 0.022
        if slot == "cover":
            slab(p, W, D * 0.8, 0.0015, 0, x=W * 0.05, mat="bone", bevel=0)
        elif slot == "spine":
            p.cyl(r, r, D * 0.82, M(loc=(-W / 2 + 0.02, D * 0.41, r), rot=(90, 0, 0)), mat="bone", segs=10)
            ext = J(p, 0.02, 0.3)
            p.cyl(0.006, 0.006, D * 0.82 + 2 * ext, M(loc=(-W / 2 + 0.02, D * 0.41 + ext, r), rot=(90, 0, 0)), mat="wood_dark", segs=6)
            p.cyl(0.006, 0.006, D * 0.82 + 2 * ext, M(loc=(W / 2 + W * 0.05, D * 0.41 + ext, 0.006), rot=(90, 0, 0)), mat="wood_dark", segs=6)
        elif slot == "clasp":
            p.tube([(-W / 2 + 0.02, 0.0, 2 * r), (-W / 2 - 0.01, -0.01, r), (-W / 2 - J(p, 0.04, 0.3), -0.03, 0.003)], 0.002, mat="rope", segs=4)
            p.ball(0.007, T((-W / 2 - J(p, 0.04, 0.3), -0.03, 0.006)), mat="glaze", segs=(6, 4))
        else:
            for i in range(p.rng.randint(2, 4)):
                cx = -W * 0.2 + i * W * 0.15
                s = J(p, 0.05, 0.3)
                flat(p, [(cx - s, -D * 0.1), (cx + s, -D * 0.1), (cx + s * 0.1, -D * 0.1 + s * 1.3)], 0.001, 0.0015, mat="paint" if i % 2 else "glaze")
            p.tube([(-W * 0.3, D * 0.2, 0.002), (0, D * 0.12, 0.002), (W * 0.4, D * J(p, 0.25, 0.3), 0.002)], 0.003, mat="glaze", segs=4)
    elif e == "Mercantile":  # folded sea chart, brass dividers, compass rose
        if slot == "cover":
            for k in range(2):
                slab(p, W, D, 0.002, k * 0.002, mat="bone", bevel=0, rz=k * J(p, 1.5, 1))
        elif slot == "spine":
            for s in (-1, 1):
                rollx(p, 0.002, W * 0.99, 0.002, y=s * D / 2, mat="bone", segs=4)
            rollx(p, 0.0006, W * J(p, 0.98, 0.02), 0.0042, y=0, mat="bone", segs=4)
        elif slot == "clasp":
            a = J(p, 25, 0.3)
            base = (W * 0.2, -D * 0.25, 0.007)
            for s in (-1, 1):
                ang = math.radians(90 + s * a / 2 + J(p, 20, 0.8))
                p.tube([base, (base[0] + math.cos(ang) * 0.12, base[1] + math.sin(ang) * 0.12, 0.0045)], 0.002, mat="brass", segs=4)
            p.cyl(0.006, 0.006, 0.004, T((base[0], base[1], 0.005)), mat="brass", segs=8, bevel=0)
        else:
            rr = J(p, 0.04, 0.15)
            pts = []
            for i in range(16):
                a = i * math.pi / 8
                k = rr if i % 2 == 0 else rr * (0.25 if i % 4 else 0.55)
                pts.append((-W * 0.25 + math.cos(a) * k, D * 0.15 + math.sin(a) * k))
            flat(p, pts, 0.001, 0.004, mat="paint")
            for i in range(p.rng.randint(2, 3)):
                a = math.radians(p.rng.uniform(-40, 40))
                p.box((W * 0.5, 0.0015, 0.0008), M(loc=(-W * 0.05, D * 0.1, 0.0045), rot=(0, 0, math.degrees(a))) @ T((W * 0.2, 0, 0)), mat="glaze", bevel=0)
    elif e == "Industrial":  # survey sheet on a plan board, clamp bar, ruler and pencil, contour rings
        if slot == "cover":
            slab(p, W, D, 0.006, mat="wood", bevel=0)
            slab(p, W * 0.94, D * 0.9, 0.001, 0.006, y=0.004, mat="bone", bevel=0)
        elif slot == "spine":
            slab(p, W * J(p, 1.0, 0.02), 0.016, 0.006, 0.006, y=-D / 2 + 0.008, mat="steel", bevel=0)
            for s in (-1, 1):
                p.cyl(0.004, 0.004, 0.004, T((s * W * 0.4, -D / 2 + 0.008, 0.012)), mat="steel", segs=6, bevel=0)
        elif slot == "clasp":
            rz = J(p, 8, 1)
            slab(p, W * 0.7, 0.022, 0.002, 0.007, x=0, y=D * 0.3, mat="steel", rz=rz, bevel=0)
            p.cyl(0.0035, 0.0035, J(p, 0.14, 0.15), M(loc=(-W * 0.3, -D * 0.15, 0.0105), rot=(0, 90, J(p, 20, 0.8))), mat="paint", segs=6)
        else:
            cx, cy = W * J(p, 0.1, 1), -D * 0.02
            for i in range(3):
                rr = 0.02 + i * J(p, 0.018, 0.2)
                p.ring(rr, 0.0008, M(loc=(cx, cy, 0.0072), scale=(1.3, 0.85, 1)), mat="glaze", segs=10)
    elif e == "Steampunk":  # palm-sized mechanical globe: brass stand, meridian ring, latitude cogs
        R = W * 0.3
        zc = R + 0.035
        if slot == "cover":
            p.ball(R, T((0, 0, zc)), mat="glaze", segs=(10, 7))
        elif slot == "spine":
            p.ring(R * 1.12, 0.003, M(loc=(0, 0, zc), rot=(90, J(p, 23, 0.2), 0)), mat="brass", segs=12)
            p.cyl(0.003, 0.003, R * 2.5, M(loc=(0, 0, zc), rot=(0, J(p, 23, 0.2), 0)) @ T((0, 0, -R * 1.25)), mat="brass", segs=5, bevel=0)
        elif slot == "clasp":
            p.lathe([(0, 0), (R * J(p, 0.7, 0.15), 0), (R * 0.65, 0.008), (0.008, 0.02), (0.006, zc - R * 1.1), (0, zc - R * 1.1)], mat="brass", segs=10)
        else:
            cog(p, J(p, 0.018, 0.2), T((R * 0.45, -0.01, 0.024)), teeth=6, t=0.003, mat="copper")
            p.ring(R * 1.01, 0.002, M(loc=(0, 0, zc + R * J(p, 0.3, 0.4))), mat="copper", segs=10)
    elif e == "Future":  # holo-map puck: emitter ring, side keys, glass terrain
        R = W * 0.28
        h = Tk * 1.6
        if slot == "cover":
            p.lathe([(0, 0), (R * 0.9, 0), (R, h * 0.3), (R * 0.95, h), (0, h)], mat="body", segs=12)
        elif slot == "spine":
            p.ring(R * J(p, 0.72, 0.08), 0.003, T((0, 0, h)), mat="shell_dark", segs=12)
        elif slot == "clasp":
            for i in range(p.rng.randint(1, 3)):
                a = math.radians(-90 + (i - 1) * 25)
                p.box((0.012, 0.004, h * 0.3), M(loc=(math.cos(a) * R * 0.99, math.sin(a) * R * 0.99, h * 0.55), rot=(0, 0, math.degrees(a) + 90)), mat="shell_dark", bevel=0)
        else:
            p.cyl(R * 0.65, R * 0.65, 0.0015, T((0, 0, h)), mat="glass", segs=12, bevel=0)
            for i in range(p.rng.randint(2, 4)):
                a = p.rng.uniform(0, math.tau)
                d = p.rng.uniform(0, R * 0.4)
                p.cyl(J(p, 0.018, 0.3), 0.0, J(p, 0.02, 0.4), T((math.cos(a) * d, math.sin(a) * d, h + 0.0015)), mat="glass", segs=5)
    elif e == "Wasteland":  # accordion-folded road map, taped, scrawled route
        if slot == "cover":
            n = 3
            for k in range(n):
                slab(p, W / 2, D, 0.0015, k * 0.0016, x=(k % 2) * 0.004 - 0.002, mat="paint" if k % 2 else "bone", rz=J(p, 1.5, 1) * (k - 1), bevel=0)
        elif slot == "spine":
            for s in (-1, 1):
                p.box((0.003, D * J(p, 0.98, 0.02), 0.005), T((s * W / 4, 0, 0.0025)), mat="bone", bevel=0)
        elif slot == "clasp":
            for i in range(p.rng.randint(1, 2)):
                slab(p, 0.05, 0.016, 0.001, 0.0048, x=-W * 0.1 + i * 0.06, y=D * 0.4, mat="cloth", rz=J(p, 30, 0.8), bevel=0)
            wrap(p, W * 0.15, 0.02, 0.005, 0.0012, "iron", mid=-D * 0.45)
        else:
            pts = [(-W * 0.2, -D * 0.35, 0.0052), (-W * 0.05, -D * 0.05, 0.0052), (-W * 0.15, D * 0.15, 0.0052), (W * J(p, 0.1, 1), D * 0.3, 0.0052)]
            p.tube(pts, 0.0015, mat="rubber", segs=4)
            for s in (-1, 1):
                p.box((0.025, 0.003, 0.001), M(loc=(W * 0.1, D * 0.3, 0.0055), rot=(0, 0, 45 * s)), mat="paint", bevel=0)
    else:  # Ancient: stone star-disc with a gold boss and pointer, rune ring
        R = W * 0.36
        t = Tk * 1.5
        if slot == "cover":
            p.lathe([(0, 0), (R * 0.95, 0), (R, t * 0.4), (R * 0.95, t), (0, t)], mat="stone", segs=12)
        elif slot == "spine":
            p.cyl(J(p, 0.018, 0.2), 0.014, 0.008, T((0, 0, t)), mat="gold", segs=8, bevel=0)
            p.ring(R * 0.72, 0.003, T((0, 0, t)), mat="stone_dark", segs=12)
        elif slot == "clasp":
            a = J(p, 30, 1)
            flat(p, [(0, -0.006), (R * 0.85, 0), (0, 0.006), (-R * 0.2, 0)], 0.002, t + 0.008, mat="gold", m=M(rot=(0, 0, a)))
        else:
            n = p.rng.randint(4, 6)
            for i in range(n):
                a = i * math.tau / n + 0.3
                p.box((0.012, 0.006, 0.003), M(loc=(math.cos(a) * R * 0.84, math.sin(a) * R * 0.84, t + 0.001), rot=(0, 0, math.degrees(a) + 90)), mat="glow", bevel=0)


# ---------------------------------------------------------------- Letter
@function("Letter", "Document", DOC, "carried")
def letter(p, slot):
    e = p.era
    W, D, Tk = F(p, 0.16, 0.1), F(p, 0.1, 0.1), F(p, 0.012, 0.2)
    if e == "Primal":  # notched bone plaque on a cord loop
        w, d = W * 0.6, D * 0.55
        if slot == "cover":
            flat(p, [(-w / 2, -d * 0.3), (-w * 0.2, -d / 2), (w / 2, -d * J(p, 0.4, 0.2)), (w * J(p, 0.45, 0.1), d * 0.4), (0, d / 2), (-w / 2, d * 0.2)], Tk * 0.5, 0, mat="bone", noise=0.02)
        elif slot == "spine":
            p.tube([(-w * 0.35, 0, Tk * 0.25), (-w * 0.55, -0.015, 0.003), (-w * 0.5 - J(p, 0.04, 0.3), 0.005, 0.003), (-w * 0.35, 0.004, Tk * 0.25)], 0.0018, mat="rope", segs=4)
        elif slot == "clasp":
            p.ball(J(p, 0.006, 0.2), T((-w * 0.5 - J(p, 0.04, 0.3), 0.0, 0.004)), mat="wood", segs=(5, 3))
        else:
            for i in range(p.rng.randint(3, 6)):
                p.box((0.002, d * p.rng.uniform(0.3, 0.6), 0.001), T((-w * 0.25 + i * w * 0.12, 0, Tk * 0.5 + 0.0004)), mat="stone_dark", bevel=0)
    elif e == "Agrarian":  # bound wooden slips with a clay seal in a seal box
        w, d, t = W, D * 0.4, 0.006
        if slot == "cover":
            for k in range(2):
                slab(p, w, d, t, k * t, mat="wood", bevel=0)
        elif slot == "spine":
            for s in (-1, 1):
                wrap(p, s * w * J(p, 0.3, 0.1), d, 2 * t, 0.0018, "rope")
        elif slot == "clasp":
            slab(p, 0.03, d * 0.9, 0.006, 2 * t, mat="wood_dark", bevel=0)
            p.ball(J(p, 0.01, 0.2), M(loc=(0, 0, 2 * t + 0.006), scale=(1.2, 0.8, 0.45)), mat="ceramic", segs=(6, 4))
        else:
            text_top(p, w * 0.28, 0, 2 * t, w * 0.3, 0.004, rows=p.rng.randint(1, 2), pitch=d * 0.35, mat="rubber")
    elif e == "Mercantile":  # folded letter packet, wax seal on the flap, string tie
        t = 0.003
        if slot == "cover":
            slab(p, W, D, t, mat="bone", bevel=0)
            p.box((0.0015, D, 0.0006), T((W * J(p, 0.3, 0.2) * (1 if coin(p) else -1), 0, t + 0.0003)), mat="bone", bevel=0)
        elif slot == "spine":
            fd = D * J(p, 0.55, 0.12)
            flat(p, [(-W / 2, D / 2), (W / 2, D / 2), (0, D / 2 - fd)], 0.001, t, mat="bone")
        elif slot == "clasp":
            p.cyl(J(p, 0.011, 0.15), 0.01, 0.003, T((0, D / 2 - D * 0.45, t + 0.001)), mat="paint", segs=8)
            p.ball(0.006, M(loc=(0, D / 2 - D * 0.45, t + 0.004), scale=(1, 1, 0.4)), mat="paint", segs=(6, 3))
        else:
            if coin(p):
                wrap(p, W * J(p, -0.25, 0.3), D, t + 0.001, 0.0012, "rope")
            text_top(p, -W * 0.1, -D * 0.2, t, W * 0.4, 0.003, rows=2, pitch=0.008, mat="rubber")
    elif e == "Industrial":  # brown-paper parcel with string cross, bow, stamps and label
        w, d, t = W * 1.2, D * 1.2, Tk * 3
        if slot == "cover":
            slab(p, w, d, t, mat="hide", bevel=0.1)
        elif slot == "spine":
            wrap(p, J(p, 0.0, 1) + 0.003, d, t, 0.0015, "rope")
            wrap(p, 0.004, w, t, 0.0015, "rope", axis="y")
        elif slot == "clasp":
            for s in (-1, 1):
                p.ring(J(p, 0.01, 0.2), 0.0015, M(loc=(s * 0.01, 0.004, t + 0.0015), rot=(J(p, 70, 0.1), 0, s * 30)), mat="rope", segs=6)
        else:
            for i in range(p.rng.randint(1, 3)):
                slab(p, 0.018, 0.022, 0.0008, t, x=w * 0.38 - i * 0.022, y=d * 0.3, mat="paint" if i % 2 else "glaze", bevel=0)
            slab(p, w * 0.35, d * 0.3, 0.0008, t, x=-w * 0.2, y=-d * 0.2, mat="bone", bevel=0)
    elif e == "Steampunk":  # pneumatic-post capsule: brass body, felt rings, latched cap, address window
        R, L = Tk * 1.8, W * 1.1
        if slot == "cover":
            p.lathe([(0, 0), (R * 0.8, 0.002), (R, 0.012), (R, L - 0.03), (0, L - 0.03)], M(loc=(-L / 2, 0, R), rot=(0, 90, 0)), mat="brass", segs=10)
        elif slot == "spine":
            for s in (-1, 1):
                hoop(p, R * 1.06, s * L * J(p, 0.3, 0.1), 0.012, R, mat="leather", segs=10)
        elif slot == "clasp":
            p.lathe([(R * 1.04, 0), (R * 1.04, 0.025), (R * 0.6, 0.032), (0, 0.033)], M(loc=(L / 2 - 0.03, 0, R), rot=(0, 90, 0)), mat="copper", segs=10)
            p.box((J(p, 0.012, 0.3), 0.004, 0.006), T((L / 2 - 0.03, -R * 1.04, R)), mat="brass", bevel=0)
        else:
            p.box((L * 0.3, 0.003, R * 0.7), T((-L * 0.05, -R * 0.98, R)), mat="bone", bevel=0)
            for i in range(p.rng.randint(2, 4)):
                p.ball(0.0025, T((-L * 0.25 + i * L * 0.12, -R * 0.96, R * 1.55)), mat="copper", segs=(4, 3))
    elif e == "Future":  # message chip in a sleeve with a lanyard ring
        w, d, t = W * 0.4, D * 0.45, Tk * 0.5
        if slot == "cover":
            slab(p, w, d, t, mat="body")
        elif slot == "spine":
            slab(p, w * J(p, 0.35, 0.2), d * 0.7, t * 0.5, t * 0.25, x=w / 2 + w * 0.1, mat="shell_dark", bevel=0)
        elif slot == "clasp":
            p.ring(J(p, 0.009, 0.2), 0.0015, T((-w / 2 - 0.006, 0, t / 2)), mat="shell_dark", segs=8)
        else:
            for i in range(p.rng.randint(3, 5)):
                p.box((0.008, 0.002, 0.0008), T((w / 2 + w * 0.2, -d * 0.25 + i * 0.006, t * 0.75 + 0.0004)), mat="gold", bevel=0)
            p.box((w * 0.5, d * 0.15, 0.0008), T((-w * 0.08, -d * 0.2, t + 0.0004)), mat="shell_dark", bevel=0)
    elif e == "Wasteland":  # note rolled into a spent casing, wire twist, rag tag
        R, L = Tk * 1.0, W * 0.55
        if slot == "cover":
            rollx(p, R, L, R, mat="rust", segs=8)
        elif slot == "spine":
            rollx(p, R * 0.7, J(p, 0.04, 0.3), R, x=L / 2 + 0.015, mat="bone", segs=8)
        elif slot == "clasp":
            p.ring(R * 1.06, 0.0012, M(loc=(L * J(p, 0.1, 1), 0, R), rot=(0, 90 + J(p, 10, 1), 0)), mat="iron", segs=8)
        else:
            flat(p, [(0, 0), (0.02, -0.004), (J(p, 0.03, 0.3), 0.012), (0.004, 0.016)], 0.0015, 0, mat="cloth", m=T((-L / 2 - 0.02, -R, 0)))
    else:  # Ancient: sealed stone lozenge with seam ring and rune seal
        w, d, t = W * 0.55, D * 0.6, Tk * 1.5
        if slot == "cover":
            p.ball(1.0, M(loc=(0, 0, t / 2), scale=(w / 2, d / 2, t / 2)), mat="stone", segs=(10, 6))
        elif slot == "spine":
            p.ring(1.0, 0.04, M(loc=(0, 0, t / 2), scale=(w / 2 * 1.01, d / 2 * 1.01, J(p, 0.08, 0.3))), mat="stone_dark", segs=12)
        elif slot == "clasp":
            p.cyl(J(p, 0.01, 0.2), 0.008, 0.004, T((0, 0, t - 0.001)), mat="gold", segs=8, bevel=0)
        else:
            runes_top(p, 0, d * 0.22, t * 0.85, w * J(p, 0.5, 0.15), n=3, w=0.005)


# ---------------------------------------------------------------- Newspaper
@function("Newspaper", "Document", DOC, "carried")
def newspaper(p, slot):
    e = p.era
    W, D, Tk = F(p, 0.28, 0.1), F(p, 0.2, 0.1), F(p, 0.01, 0.2)
    if e == "Primal":  # painted message stone, carried in a cord sling
        w, d, t = W * 0.6, D * 0.65, Tk * 3.5
        if slot == "cover":
            p.ball(1.0, M(loc=(0, 0, t / 2), scale=(w / 2, d / 2, t / 2)), mat="stone", segs=(10, 6), noise=0.025)
        elif slot == "spine":
            wrap(p, w * J(p, 0.1, 1), d * 0.9, t * 0.9, 0.003, "rope")
        elif slot == "clasp":
            p.cyl(0.004, 0.0, J(p, 0.05, 0.2), M(loc=(w * 0.1, -d * 0.45, t * 0.85), rot=(-80, 0, J(p, 20, 1))), mat="feather", segs=5)
        else:
            for i in range(p.rng.randint(2, 4)):
                cx = -w * 0.25 + i * w * 0.17
                flat(p, [(cx - 0.012, -0.006), (cx + 0.012, -0.006), (cx, J(p, 0.018, 0.3))], 0.001, t, mat="paint" if i % 2 else "accent")
    elif e == "Agrarian":  # small wooden notice board on a hand stick
        w, d, t = W * 0.55, D * 0.6, Tk * 1.2
        if slot == "cover":
            slab(p, w, d, t, mat="wood")
        elif slot == "spine":
            L = J(p, 0.14, 0.15)
            p.box((L, 0.024, t * 0.9), T((w / 2 + L / 2 - 0.01, 0, t * 0.45)), mat="wood_dark", bevel=0)
        elif slot == "clasp":
            for x in (-w * 0.42, w * 0.42):
                p.cyl(0.004, 0.004, 0.002, T((x, J(p, 0.0, 1) + d * 0.35, t)), mat="iron", segs=6, bevel=0)
        else:
            text_top(p, 0, 0, t, w * 0.75, 0.006, rows=p.rng.randint(3, 4), pitch=d * 0.2, mat="rubber")
    elif e == "Mercantile":  # stitched news pamphlet with a woodcut panel
        w, d, t = W * 0.6, D * 0.75, Tk * 0.6
        if slot == "cover":
            sheets(p, w, d, 0, 3, mat="bone", t=t / 3, spread=1.5)
        elif slot == "spine":
            for i in range(p.rng.randint(2, 3)):
                p.box((0.003, 0.002, t + 0.002), T((-w / 2 + 0.002, -d * 0.3 + i * d * 0.3, t / 2)), mat="rope", bevel=0)
        elif slot == "clasp":
            if coin(p):
                wrap(p, w * J(p, 0.2, 0.4), d, t, 0.0012, "rope")
            else:
                p.box((0.004, 0.02, 0.0015), T((w * 0.48, J(p, 0.0, 1) + d * 0.1, t + 0.0007)), mat="paint", bevel=0)
        else:
            p.box((w * 0.4, d * 0.35, 0.0008), T((-w * 0.12, d * J(p, 0.12, 0.3), t + 0.0004)), mat="rubber", bevel=0)
            text_top(p, w * 0.22, d * 0.1, t, w * 0.3, 0.003, rows=3, pitch=d * 0.1, mat="rubber")
            text_top(p, 0, -d * 0.3, t, w * 0.8, 0.003, rows=2, pitch=d * 0.08, mat="rubber")
    elif e == "Industrial":  # folded broadsheet: two-ply fold, headline and columns, rubber band
        w, d, t = W * 0.75, D, Tk * 0.4
        if slot == "cover":
            slab(p, w, d, t, mat="bone", bevel=0)
            slab(p, w * 0.98, d * 0.98, t, t, y=0.002, mat="bone", bevel=0, rz=J(p, 1, 1))
        elif slot == "spine":
            rollx(p, t, w * J(p, 0.99, 0.01), t, y=-d / 2, mat="bone", segs=6)
        elif slot == "clasp":
            if coin(p):
                wrap(p, w * J(p, 0.2, 0.4), d, 2 * t, 0.0015, "rubber")
            else:
                wrap(p, J(p, 0.0, 1) + d * 0.15, w, 2 * t, 0.0012, "rope", axis="y")
        else:
            p.box((w * 0.85, d * 0.14, 0.0008), T((0, -d * 0.33, 2 * t + 0.0004)), mat="rubber", bevel=0)
            ncol = p.rng.randint(3, 4)
            for c in range(ncol):
                x = -w * 0.42 + (c + 0.5) * w * 0.84 / ncol
                p.box((w * 0.84 / ncol * 0.8, d * 0.55, 0.0006), T((x, d * 0.08, 2 * t + 0.0003)), mat="stone_dark", bevel=0)
    elif e == "Steampunk":  # press express clamped in a brass reading rod
        w, d, t = W * 0.75, D, Tk * 0.5
        if slot == "cover":
            sheets(p, w, d, 0, 2, mat="bone", t=t / 2, spread=1.0)
        elif slot == "spine":
            ext = J(p, 0.03, 0.25)
            rollx(p, 0.005, w + 2 * ext, t + 0.005, y=-d / 2 + 0.012, mat="brass", segs=6)
            rollx(p, 0.005, w + 0.01, 0.005, y=-d / 2 + 0.012, mat="brass", segs=6)
        elif slot == "clasp":
            ext = J(p, 0.03, 0.25)
            for s in (-1, 1):
                p.ball(0.008, T((s * (w / 2 + ext), -d / 2 + 0.012, t + 0.005)), mat="copper", segs=(6, 4))
            p.box((0.006, 0.006, t + 0.012), T((w / 2 + 0.006, -d / 2 + 0.012, (t + 0.01) / 2)), mat="brass", bevel=0)
        else:
            p.box((w * 0.8, d * 0.12, 0.0008), T((0, -d * 0.25, t + 0.0004)), mat="rubber", bevel=0)
            cog(p, J(p, 0.02, 0.2), T((w * 0.3, d * 0.2, t + 0.0005)) @ M(rot=(90, 0, 0)), teeth=6, t=0.001, mat="paint")
            text_top(p, -w * 0.12, d * 0.15, t, w * 0.5, 0.003, rows=3, pitch=d * 0.1, mat="rubber")
    elif e == "Future":  # flexible e-paper sheet folded over a roll bar
        w, d, t = W * 0.7, D * 0.9, Tk * 0.25
        if slot == "cover":
            slab(p, w, d, t, mat="body", bevel=0)
            slab(p, w, d * J(p, 0.95, 0.04), t, t + 0.003, y=0.0, mat="body", bevel=0)
        elif slot == "spine":
            rollx(p, 0.003 + t, w * J(p, 1.02, 0.02), 0.003 + t, y=-d / 2, mat="shell_dark", segs=8)
        elif slot == "clasp":
            p.box((J(p, 0.02, 0.3), 0.012, 0.0015), T((w * 0.3, d / 2 - 0.004, 2 * t + 0.0038)), mat="shell_dark", bevel=0)
        else:
            p.box((w * 0.9, d * 0.8, 0.0008), T((0, 0.004, 2 * t + 0.0034)), mat="glass", bevel=0)
            text_top(p, 0, d * 0.05, 2 * t + 0.0038, w * 0.75, 0.004, rows=p.rng.randint(3, 5), pitch=d * 0.12, mat="shell_dark")
    elif e == "Wasteland":  # stapled sheets on cardboard, tape spine, binder clip, stain
        w, d, t = W * 0.65, D * 0.85, Tk * 0.5
        if slot == "cover":
            slab(p, w, d, 0.004, mat="hide", bevel=0)
            sheets(p, w * 0.92, d * 0.9, 0.004, 2, mat="paint", t=0.0012, spread=4)
        elif slot == "spine":
            p.box((0.02, d * J(p, 1.0, 0.03), 0.0075), T((-w / 2 + 0.006, 0, 0.0037)), mat="cloth", bevel=0)
        elif slot == "clasp":
            cw = J(p, 0.03, 0.2)
            slab(p, cw, 0.012, 0.012, 0, y=-d / 2 + 0.004, x=w * 0.15, mat="rubber", bevel=0)
            p.tube([(w * 0.15 - cw * 0.4, -d / 2 + 0.004, 0.012), (w * 0.15, -d / 2 + 0.03, 0.016), (w * 0.15 + cw * 0.4, -d / 2 + 0.004, 0.012)], 0.0012, mat="steel", segs=4)
        else:
            p.box((w * 0.7, d * 0.12, 0.0008), M(loc=(0, -d * 0.25, 0.0068), rot=(0, 0, J(p, 3, 1))), mat="rubber", bevel=0)
            p.cyl(J(p, 0.02, 0.3), 0.02, 0.0006, T((w * 0.2, d * 0.2, 0.0066)), mat="rust", segs=8, bevel=0)
    else:  # Ancient: thin stone news leaf with a thick edge and gold boss
        w, d, t = W * 0.6, D * 0.75, Tk * 0.8
        if slot == "cover":
            slab(p, w, d, t, mat="stone")
        elif slot == "spine":
            slab(p, w + 0.008, 0.016, t * 1.6, 0, y=-d / 2, mat="stone_dark")
        elif slot == "clasp":
            p.cyl(J(p, 0.012, 0.2), 0.009, 0.004, T((w * 0.35, d * 0.3, t)), mat="gold", segs=8, bevel=0)
        else:
            for i in range(p.rng.randint(2, 3)):
                runes_top(p, -w * 0.05, d * 0.2 - i * d * 0.18, t, w * 0.7, n=p.rng.randint(3, 5), w=0.006)


# ---------------------------------------------------------------- Notice (scene: floor contact at z = 0)
@function("Notice", "Document", DOC, "scene")
def notice(p, slot):
    e = p.era
    Hn, Bw, Bh = F(p, 1.9, 0.08), F(p, 0.9, 0.1), F(p, 0.7, 0.1)
    if e == "Primal":  # totem pole with hide notices pinned by thorns, carved head and wings
        r = 0.1
        if slot == "spine":
            p.tube([(0, 0, 0), (J(p, 0.02, 1), 0.01, Hn * 0.5), (0, 0, Hn)], r, mat="wood", segs=7)
            for i in range(5):
                a = i * math.tau / 5 + p.rng.uniform(-0.2, 0.2)
                p.ball(1.0, M(loc=(math.cos(a) * 0.17, math.sin(a) * 0.17, 0.05), scale=(0.1, 0.08, 0.07)), mat="stone", segs=(6, 4), noise=0.05)
        elif slot == "cover":
            for k, z in enumerate((Hn * 0.45, Hn * 0.62)):
                w, h = Bw * J(p, 0.32, 0.15), Bh * J(p, 0.32, 0.15)
                pts = [(-w / 2, 0), (w / 2, J(p, 0.02, 1)), (w * 0.45, -h), (0, -h * 1.1), (-w * 0.5, -h * 0.95)]
                p.plate(pts, 0.01, M(loc=((k - 0.5) * 0.04, -r - 0.006, z), rot=(0, J(p, 6, 1) * (1 - 2 * k), 0)), mat="hide", noise=0.01)
        elif slot == "clasp":
            for z in (Hn * 0.45 - 0.02, Hn * 0.62 - 0.02):
                for x in (-0.05, 0.05):
                    p.cyl(0.008, 0.0, J(p, 0.07, 0.2), M(loc=(x, -r - 0.01, z), rot=(90, 0, 0)), mat="bone", segs=5)
            p.band(r, Hn * J(p, 0.3, 0.15), h=0.06)
        else:
            zt = Hn - 0.12
            p.box((0.26, 0.22, 0.22), T((0, 0, zt)), mat="wood_dark", noise=0.02)
            p.plate([(-0.04, 0), (0.04, 0), (0, -J(p, 0.12, 0.2))], 0.05, M(loc=(0, -0.13, zt - 0.02), rot=(-70, 0, 0)), mat="paint")
            for s in (-1, 1):
                p.plate([(0, 0), (s * J(p, 0.35, 0.15), 0.08), (s * 0.3, -0.05), (s * 0.1, -0.08)], 0.03, T((s * 0.12, 0, zt - 0.02)), mat="feather")
                p.box((0.04, 0.012, 0.03), T((s * 0.06, -0.115, zt + 0.03)), mat="bone", bevel=0)
    elif e == "Agrarian":  # plank notice on a post under a small gable roof
        zb = Hn - Bh - 0.2
        if slot == "spine":
            p.box((0.1, 0.1, Hn), T((0, 0.05, Hn / 2)), mat="wood")
            p.box((0.24, 0.24, 0.08), T((0, 0.05, 0.04)), mat="stone", noise=0.03)
        elif slot == "cover":
            n = 3
            for k in range(n):
                slab(p, Bw, 0.03, Bh / n - 0.006, zb + k * Bh / n, y=-0.015, mat="wood", noise=0.004)
            text_front(p, 0, -0.03, zb + Bh * 0.8, Bw * 0.7, 0.03, mat="rubber", rows=p.rng.randint(3, 4), pitch=Bh * 0.2)
        elif slot == "clasp":
            for s in (-1, 1):
                p.box((0.04, 0.04, Bh + 0.04), T((s * (Bw / 2 + 0.02), -0.01, zb + Bh / 2)), mat="wood_dark")
            for x in (-Bw * 0.3, Bw * 0.3):
                for z in (zb + 0.06, zb + Bh - 0.06):
                    p.cyl(0.008, 0.008, 0.01, M(loc=(x * J(p, 1, 0.05), -0.03, z), rot=(90, 0, 0)), mat="iron", segs=6, bevel=0)
        else:
            pitch = J(p, 28, 0.2)
            zr = zb + Bh + 0.05
            for s in (-1, 1):
                p.box((Bw / 2 + 0.16, 0.22, 0.025), M(loc=(s * (Bw / 4 + 0.05), -0.01, zr + 0.06), rot=(0, s * pitch, 0)), mat="wood_dark")
            p.box((0.06, 0.06, 0.12), T((0, -0.01, zr)), mat="wood", bevel=0)
    elif e == "Mercantile":  # framed bulletin board on two legs, pinned papers, shingle canopy
        zb = Hn - Bh - 0.25
        px = Bw / 2 + 0.03
        if slot == "spine":
            for x in (-px, px):
                p.box((0.06, 0.06, Hn - 0.1), T((x, 0, (Hn - 0.1) / 2)), mat="wood_dark")
                p.box((0.06, 0.4, 0.05), T((x, 0, 0.025)), mat="wood_dark")
        elif slot == "cover":
            slab(p, Bw, 0.03, Bh, zb, mat="wood")
            for i in range(p.rng.randint(3, 5)):
                w, h = J(p, 0.2, 0.25), J(p, 0.26, 0.25)
                x = p.rng.uniform(-Bw * 0.35, Bw * 0.35)
                z = p.rng.uniform(zb + h / 2 + 0.03, zb + Bh - h / 2 - 0.03)
                p.box((w, 0.003, h), M(loc=(x, -0.017, z), rot=(0, p.rng.uniform(-8, 8), 0)), mat="bone" if i % 2 else "paint", bevel=0)
        elif slot == "clasp":
            for z in (zb - 0.02, zb + Bh + 0.02):
                p.box((Bw + 0.08, 0.05, 0.04), T((0, -0.005, z)), mat="wood_dark")
            for i in range(p.rng.randint(4, 7)):
                p.ball(0.01, T((p.rng.uniform(-Bw * 0.4, Bw * 0.4), -0.022, p.rng.uniform(zb + 0.1, zb + Bh - 0.05))), mat="brass", segs=(5, 3))
        else:
            zr = Hn - 0.1
            p.box((Bw + 0.3, J(p, 0.3, 0.15), 0.03), M(loc=(0, -0.08, zr), rot=(-J(p, 18, 0.3), 0, 0)), mat="wood_dark")
            for x in (-px, px):
                p.ball(0.035, T((x, 0, zr + 0.06)), mat="brass", segs=(6, 4))
    elif e == "Industrial":  # round poster column: shaft and posters, plinth, steel bands, domed cap
        R = Bw * 0.33
        Hc = Hn * 1.15
        if slot == "cover":
            # Rings every ~0.2 m so the per-variant swell bends the shaft with its posters instead of under them.
            p.lathe([(0, 0.15)] + [(R, 0.15 + (Hc - 0.15) * k / 9) for k in range(10)] + [(0, Hc)], mat="stone", segs=14)
            n = p.rng.randint(4, 6)
            for i in range(n):
                a = i * math.tau / n + p.rng.uniform(-0.1, 0.1)
                h = J(p, 0.75, 0.2)
                z = p.rng.uniform(0.4, Hc - h - 0.3) + h / 2
                w = 2 * R * math.sin(math.pi / n) * 0.95
                for k in range(4):
                    zk = z - h / 2 + h * (k + 0.5) / 4
                    p.box((w, 0.006, h / 4), M(loc=(math.cos(a) * (R + 0.006), math.sin(a) * (R + 0.006), zk), rot=(0, 0, math.degrees(a) + 90)), mat=("paint", "bone", "glaze")[i % 3], bevel=0)
        elif slot == "spine":
            p.cyl(R * 1.15, R * J(p, 1.12, 0.03), 0.15, mat="stone_dark", segs=14)
        elif slot == "clasp":
            for z in (0.28, Hc - J(p, 0.18, 0.2)):
                p.cyl(R * 1.05, R * 1.05, 0.04, T((0, 0, z)), mat="steel", segs=14, cap=False)
        else:
            p.lathe([(R * 1.2, Hc), (R * 1.25, Hc + 0.05), (R * 1.05, Hc + 0.12), (R * J(p, 0.6, 0.15), Hc + 0.3), (0.03, Hc + 0.4), (0, Hc + J(p, 0.48, 0.15))], mat="steel", segs=14)
    elif e == "Steampunk":  # split-flap gear board between brass pillars
        zb = Hn - Bh - 0.2
        px = Bw / 2 + 0.05
        if slot == "spine":
            for x in (-px, px):
                p.cyl(0.035, 0.03, Hn - 0.05, T((x, 0, 0)), mat="brass", segs=8)
                p.lathe([(0.14, 0), (0.13, 0.04), (0.06, 0.1), (0.04, 0.18)], T((x, 0, 0)), mat="brass", segs=8)
        elif slot == "cover":
            p.box((Bw + 0.06, 0.06, Bh + 0.06), T((0, 0.02, zb + Bh / 2)), mat="wood_dark", bevel=0)
            rows, cols = 4, 6
            for i in range(rows):
                for k in range(cols):
                    fw, fh = Bw / cols * 0.88, Bh / rows * 0.86
                    tilt = J(p, 8, 1) if p.rng.random() < 0.3 else 0
                    p.box((fw, 0.012, fh), M(loc=(-Bw / 2 + (k + 0.5) * Bw / cols, -0.016, zb + (i + 0.5) * Bh / rows), rot=(tilt, 0, 0)),
                          mat="bone" if (i + k + p.rng.randint(0, 1)) % 3 else "rubber", bevel=0)
        elif slot == "clasp":
            cog(p, J(p, 0.12, 0.15), T((px + 0.02, -0.04, zb + Bh + 0.05)), teeth=8, t=0.015, mat="brass")
            cog(p, 0.07, T((px - 0.12, -0.04, zb + Bh + 0.12)), teeth=6, t=0.012, mat="copper")
            p.tube([(px + 0.02, -0.06, zb + Bh + 0.05), (px + 0.02, -0.12, zb + Bh + 0.05), (px + 0.02, -0.12, zb + Bh - 0.05)], 0.008, mat="brass", segs=5)
        else:
            zc = zb + Bh + 0.03
            p.box((Bw + 0.18, 0.08, 0.05), T((0, 0.02, zc + 0.025)), mat="brass")
            p.plate([(-Bw * 0.3, 0), (Bw * 0.3, 0), (0, J(p, 0.18, 0.2))], 0.04, T((0, 0.02, zc + 0.05)), mat="brass")
            p.tube([(-px, 0.05, zb), (-px - 0.06, 0.08, zb + Bh * 0.5), (-px, 0.05, zb + Bh)], 0.012, mat="copper", segs=5)
    elif e == "Future":  # glass notice panel between emitter bars on a slim pylon
        zb = Hn - Bh - 0.15
        if slot == "spine":
            p.lathe([(0, 0), (0.25, 0), (0.24, 0.04), (0.08, 0.08), (J(p, 0.05, 0.2), zb * 0.5), (0.045, zb - 0.06), (0, zb - 0.05)], mat="body", segs=12)
        elif slot == "cover":
            p.box((Bw, 0.008, Bh), T((0, 0, zb + Bh / 2)), mat="glass", bevel=0)
            text_front(p, -Bw * 0.05, -0.004, zb + Bh * 0.82, Bw * 0.75, 0.03, mat="shell_dark", rows=p.rng.randint(3, 5), pitch=Bh * 0.15)
        elif slot == "clasp":
            for z in (zb - 0.03, zb + Bh + 0.01):
                p.box((Bw + J(p, 0.08, 0.3), 0.05, 0.04), T((0, 0, z + 0.01)), mat="shell_dark", bevel=0.3)
        else:
            for s in (-1, 1):
                p.box((0.02, 0.03, Bh), T((s * (Bw / 2 + 0.012), 0, zb + Bh / 2)), mat="shell", bevel=0)
            p.box((Bw * J(p, 0.7, 0.15), 0.012, 0.035), T((0, -0.026, zb + 0.01)), mat="paint", bevel=0)
    elif e == "Wasteland":  # corrugated scrap sheet on pipes in a tyre, taped papers, wire
        zb = Hn - Bh - 0.25
        if slot == "spine":
            for x in (-Bw * 0.4, Bw * 0.4):
                p.cyl(0.025, 0.025, Hn - 0.05, M(loc=(x, 0.03, 0), rot=(J(p, 2, 1), 0, 0)), mat="iron", segs=6)
                p.ring(0.2, 0.08, T((x, 0.03, 0.08)), mat="rubber", segs=10)
        elif slot == "cover":
            n = 6
            for k in range(n):
                x = -Bw / 2 + (k + 0.5) * Bw / n
                p.box((Bw / n * 0.75, 0.012, Bh), M(loc=(x, -0.004 * (k % 2), zb + Bh / 2), rot=(0, 0, 20 * (1 if k % 2 else -1))), mat="rust", bevel=0)
            for i in range(p.rng.randint(2, 4)):
                p.box((J(p, 0.22, 0.25), 0.003, J(p, 0.28, 0.2)), M(loc=(p.rng.uniform(-Bw * 0.3, Bw * 0.3), -0.02, zb + Bh * p.rng.uniform(0.3, 0.7)), rot=(0, p.rng.uniform(-10, 10), 0)), mat="bone" if i % 2 else "paint", bevel=0)
        elif slot == "clasp":
            for x in (-Bw * 0.4, Bw * 0.4):
                for z in (zb + 0.08, zb + Bh - 0.08):
                    p.ring(0.035, 0.003, M(loc=(x, 0.01, z * J(p, 1, 0.02)), rot=(0, 90, 0)), mat="iron", segs=6)
        else:
            p.box((Bw + 0.15, 0.25, 0.012), M(loc=(0, -0.05, zb + Bh + 0.08), rot=(-J(p, 15, 0.3), J(p, 4, 1), 0)), mat="rust", bevel=0)
            p.box((Bw * 0.6, 0.004, 0.06), M(loc=(0, -0.022, zb + Bh * J(p, 0.2, 0.3)), rot=(0, J(p, 6, 1), 0)), mat="paint", bevel=0)
    else:  # Ancient: tapering obelisk with an inset rune tablet and gold bands
        Hs = Hn * 1.1
        b = 0.24
        if slot == "spine":
            p.lathe([(0, 0), (b, 0), (b * 0.72, Hs), (0, Hs)], M(rot=(0, 0, 45)), mat="stone", segs=4)
            p.box((b * 2.2, b * 2.2, 0.12), T((0, 0, 0.06)), mat="stone_dark")
        elif slot == "cover":
            zt = Hs * 0.45
            w = b * 1.0
            p.box((w, 0.03, Bh * 0.8), T((0, -b * 0.8, zt)), mat="stone_dark")
            for i in range(p.rng.randint(3, 4)):
                runes_front(p, 0, -b * 0.8 - 0.015, zt + Bh * 0.3 - i * Bh * 0.18, w * 0.75, n=p.rng.randint(2, 4), h=0.03)
        elif slot == "clasp":
            for z in (0.3, Hs * J(p, 0.8, 0.05)):
                rr = b - (b * 0.28) * z / Hs
                p.lathe([(rr * 1.06, z), (rr * 1.06, z + 0.05)], M(rot=(0, 0, 45)), mat="gold", segs=4)
        else:
            rr = b * 0.72
            p.lathe([(rr, Hs), (rr * 1.05, Hs + 0.02), (0, Hs + J(p, 0.25, 0.2))], M(rot=(0, 0, 45)), mat="gold", segs=4)
            p.box((0.03, 0.01, 0.12), T((0, -rr * 0.75, Hs - 0.25)), mat="glow", bevel=0)
