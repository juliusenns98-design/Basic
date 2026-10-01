"""Erzeugt die Zeichnung Z-10-1 "Stapelkasten" als DXF (A3 quer).

Alle Koordinaten auf dem Blatt in mm (Modellbereich 1:1 = Papier).
Schnitte A-A und B-B im Massstab 1:1 (unterbrochen), Ansichten,
Isometrie und Explosionsdarstellung im Massstab 1:5.

Aufruf:  python3 stapelkasten.py   ->  Stapelkasten_Z-10-1.dxf
"""
import math
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment

import hlr

# ---------------------------------------------------------------------------
# Hauptmasse (aus der Vorlage)
# ---------------------------------------------------------------------------
L = 350          # Gesamtlaenge
B = 255          # Gesamtbreite
H = 100          # Hoehe Seiten
T = 14           # Dicke Seiten / Rueckwand
LS = 345         # Laenge Seite
GX0, GX1 = 332, 350          # Griffleiste 18/50 (x)
GZ0, GZ1 = 3, 53             # Griffleiste (z)  -- Lage geschaetzt
BZ0, BZ1 = 12, 17            # Boden FU 5 (z)
BX1 = 337                    # Bodenlaenge
BY0, BY1 = 9, B - 9          # Bodenbreite 237
RZ0, RZ1 = 17, 92            # Rueckwand 14/75 (z)
LIP = 6.5                    # Stapelfalz oben: stehender Rand aussen
FALZ_T = 5                   # Falztiefe oben
ZAPF = 7                     # Stapelfalz unten: stehender Teil innen
ZAPF_H = 6                   # Hoehe unten
SLOPE_X0 = 272               # Beginn Schraege (345 - 73)
SLOPE_X1 = 327               # Ende Schraege (332 - 5), 45 Grad
SLOPE_Z1 = 45                # 100 - 55
TAILS_BACK = [(22, 37), (47, 62), (72, 87)]   # Zinken Rueckwand (angenommen)
TAILS_FRONT = [(8, 20), (28, 40)]             # Zinken Seite->Griffleiste

doc = ezdxf.new("R2010", setup=True, units=4)  # mm
doc.header["$LTSCALE"] = 0.5
doc.header["$MEASUREMENT"] = 1
doc.header["$LIMMIN"] = (0, 0)
doc.header["$LIMMAX"] = (420, 297)
doc.header["$EXTMIN"] = (0, 0, 0)
doc.header["$EXTMAX"] = (420, 297, 0)
msp = doc.modelspace()

LAYERS = {
    # name: (farbe, linienstaerke 1/100 mm, linientyp)
    "Rahmen": (7, 70, "Continuous"),
    "Kontur": (7, 50, "Continuous"),
    "Duenn": (8, 25, "Continuous"),
    "Verdeckt": (6, 25, "DASHED"),
    "Mittellinie": (1, 25, "CENTER"),
    "Schnittverlauf": (1, 50, "CENTER"),
    "Schraffur": (8, 18, "Continuous"),
    "Bemassung": (3, 25, "Continuous"),
    "Text": (7, 25, "Continuous"),
    "Schriftfeld": (7, 35, "Continuous"),
}
for name, (col, lw, lt) in LAYERS.items():
    doc.layers.add(name, color=col, lineweight=lw, linetype=lt)

doc.styles.add("ISO", font="isocpeur.ttf")

ds = doc.dimstyles.new("TISCHLER")
ds.dxf.dimtxt = 2.5
ds.dxf.dimtxsty = "ISO"
ds.dxf.dimtsz = 1.2          # Schraegstriche statt Pfeile
ds.dxf.dimasz = 2.5
ds.dxf.dimexo = 1.0
ds.dxf.dimexe = 1.5
ds.dxf.dimgap = 0.8
ds.dxf.dimtad = 1
ds.dxf.dimtih = 0
ds.dxf.dimtoh = 0
ds.dxf.dimdec = 1
ds.dxf.dimzin = 8
ds.dxf.dimdsep = ord(",")
ds.dxf.dimclrd = 3
ds.dxf.dimclre = 3
ds.dxf.dimclrt = 7
ds.dxf.dimlwd = 25
ds.dxf.dimlwe = 25


def line(p, q, layer="Kontur"):
    msp.add_line(p, q, dxfattribs={"layer": layer})


def pline(pts, layer="Kontur", closed=False, fmt="xy"):
    return msp.add_lwpolyline(pts, format=fmt, close=closed, dxfattribs={"layer": layer})


def text(s, p, h=2.5, layer="Text", align="LEFT", rot=0):
    t = msp.add_text(s, height=h, rotation=rot, dxfattribs={"layer": layer, "style": "ISO"})
    t.set_placement(p, align=getattr(TextEntityAlignment, align))
    return t


def hatch(paths, scale=1.2, angle=0.0):
    """paths: Listen von (x, y[, bulge]); weitere Pfade = Inseln."""
    h = msp.add_hatch(dxfattribs={"layer": "Schraffur"})
    h.set_pattern_fill("ANSI31", scale=scale, angle=angle)
    for pts in paths:
        pts = [(p[0], p[1], p[2] if len(p) > 2 else 0) for p in pts]
        h.paths.add_polyline_path(pts, is_closed=True)
    return h


def dim(p1, p2, base, txt, angle=0):
    d = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle, text=txt,
                           dimstyle="TISCHLER", dxfattribs={"layer": "Bemassung"})
    d.render()


def arrowhead(tip, frm, size=2.5, layer="Bemassung"):
    ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
    w = size * 0.18
    bx, by = tip[0] - size * math.cos(ang), tip[1] - size * math.sin(ang)
    nx, ny = -math.sin(ang) * w, math.cos(ang) * w
    msp.add_solid([tip, (bx + nx, by + ny), (bx - nx, by - ny)], dxfattribs={"layer": layer})


def leader(pts, label, h=2.5, arrow=True):
    pline(pts, "Bemassung")
    if arrow:
        arrowhead(pts[0], pts[1])
    end, prev = pts[-1], pts[-2]
    if end[0] >= prev[0]:
        text(label, (end[0] + 0.8, end[1] + 0.6), h)
    else:
        text(label, (end[0] - 0.8, end[1] + 0.6), h, align="BOTTOM_RIGHT")


def text_box(cx, cy, s, h=2.5):
    """Aussparung fuer Text in Schraffur (Rechteck um zentrierten Text)."""
    w = len(s) * h * 0.72 / 2 + 0.6
    hh = h / 2 + 0.6
    return [(cx - w, cy - hh), (cx + w, cy - hh), (cx + w, cy + hh), (cx - w, cy + hh)]


def break_line(x, y0, y1, vertical=True):
    """Duenne Freihand-Bruchlinie."""
    pts = []
    n = 24
    for i in range(n + 1):
        t = i / n
        off = 1.2 * math.sin(t * 2 * math.pi * 2)
        if vertical:
            pts.append((x + off, y0 + (y1 - y0) * t))
        else:
            pts.append((y0 + (y1 - y0) * t, x + off))
    msp.add_spline(pts, dxfattribs={"layer": "Duenn"})


def fu_board(p0, p1, z0, z1, mapf, ticks=4.0, skip=()):
    """Sperrholz-Symbol: Rechteck mit Querstrichen; mapf bildet (a,z) ab."""
    pts = [mapf(p0, z0), mapf(p1, z0), mapf(p1, z1), mapf(p0, z1)]
    pline(pts, "Kontur", closed=True)
    a = p0 + ticks
    while a < p1 - 0.5:
        if not any(s0 <= a <= s1 for s0, s1 in skip):
            line(mapf(a, z0), mapf(a, z1), "Duenn")
        a += ticks


# ---------------------------------------------------------------------------
# Rahmen
# ---------------------------------------------------------------------------
pline([(0, 0), (420, 0), (420, 297), (0, 297)], "Duenn", closed=True)
pline([(20, 10), (410, 10), (410, 287), (20, 287)], "Rahmen", closed=True)

# ---------------------------------------------------------------------------
# Schnitt A-A (1:1, unterbrochen)
# ---------------------------------------------------------------------------
AX0, AZ0 = 47, 168
A_L1, A_R, GAP = 80, 255, 6


def bxa(x):
    return x if x <= A_L1 else x - (A_R - A_L1 - GAP)


def PA(x, z):
    return (AX0 + bxa(x), AZ0 + z)


def hseg_a(x0, x1, z, layer="Kontur"):
    """waagrechte Linie im Schnitt A-A, an der Bruchstelle geteilt."""
    if x1 <= A_L1 or x0 >= A_R:
        line(PA(x0, z), PA(x1, z), layer)
    else:
        if x0 < A_L1:
            line(PA(x0, z), PA(A_L1, z), layer)
        if x1 > A_R:
            line(PA(A_R, z), PA(x1, z), layer)


# Rueckwand 14/75 mit Fase 2x45
rw = [PA(0, RZ0), PA(T, RZ0), PA(T, RZ1 - 2), PA(T - 2, RZ1), PA(0, RZ1)]
pline(rw, closed=True)
# Schraube 3x16 DIN 97 von unten (Senkkopf) in der Rueckwand
sx = T / 2
screw = [PA(sx - 3, BZ0), PA(sx + 3, BZ0), PA(sx + 1.5, BZ0 + 1.5), PA(sx + 1.5, BZ0 + 14),
         PA(sx, BZ0 + 16), PA(sx - 1.5, BZ0 + 14), PA(sx - 1.5, BZ0 + 1.5)]
pline(screw, "Duenn", closed=True)
screw_in_rw = [PA(sx + 1.5, RZ0), PA(sx + 1.5, BZ0 + 14), PA(sx, BZ0 + 16),
               PA(sx - 1.5, BZ0 + 14), PA(sx - 1.5, RZ0)]
c = PA(T / 2, 55)
hatch([rw, screw_in_rw, text_box(c[0], c[1], "14/75")])
text("14/75", c, align="MIDDLE_CENTER")

# Griffleiste 18/50 mit R3 und Nut fuer Boden
bul = math.tan(math.radians(22.5))
griff = [(GX0, GZ0, 0), (GX1 - 3, GZ0, bul), (GX1, GZ0 + 3, 0), (GX1, GZ1 - 3, bul),
         (GX1 - 3, GZ1, 0), (GX0 + 3, GZ1, bul), (GX0, GZ1 - 3, 0), (GX0, BZ1, 0),
         (BX1, BZ1, 0), (BX1, BZ0, 0), (GX0, BZ0, 0)]
griff_p = [(*PA(x, z), b) for x, z, b in griff]
pline(griff_p, closed=True, fmt="xyb")
c = PA((GX0 + GX1) / 2, 33)
hatch([griff_p, text_box(c[0], c[1], "18/50", 2.0)])
text("18/50", c, h=2.0, align="MIDDLE_CENTER")

# Boden FU 5 (Schnitt)
fu_left = [(0, A_L1), (A_R, BX1)]
for a0, a1 in fu_left:
    pts = [PA(a0, BZ0), PA(a1, BZ0), PA(a1, BZ1), PA(a0, BZ1)]
    line(pts[0], pts[1])
    line(pts[3], pts[2])
    if a0 == 0:
        line(pts[0], pts[3])
    if a1 == BX1:
        line(pts[1], pts[2])
    a = a0 + 4
    while a < a1 - 0.5:
        if not (sx - 3.5 <= a <= sx + 3.5) and not (40 <= a <= 52):
            line(PA(a, BZ0), PA(a, BZ1), "Duenn")
        a += 4
text("FU 5", PA(46, (BZ0 + BZ1) / 2), h=2.0, align="MIDDLE_CENTER")

# Seite in Ansicht (hinter der Schnittebene)
line(PA(0, 3), PA(0, BZ0))                         # Hinterkante unten
line(PA(0, RZ1), PA(0, H))                         # Hinterkante oben
line(PA(0, 3), PA(10, 0))                          # Fase 3x10
hseg_a(10, LS, 0)                                  # Unterkante
line(PA(LS, 0), PA(LS, GZ0))                       # Seitenende unter Griffleiste
hseg_a(0, SLOPE_X0, H)                             # Oberkante
hseg_a(0, SLOPE_X0 + FALZ_T, H - FALZ_T)           # Falzgrund
line(PA(SLOPE_X0, H), PA(SLOPE_X1, SLOPE_Z1))      # Schraege 45 Grad
line(PA(SLOPE_X1, SLOPE_Z1), PA(GX0, SLOPE_Z1))
hseg_a(0, GX0, ZAPF_H, "Verdeckt")                 # Stapelfalz unten (verdeckt)

for x in (A_L1, A_R):
    break_line(PA(x, 0)[0] + (1.5 if x == A_L1 else -1.5), AZ0 - 2, AZ0 + H + 2)

# Bemassung A-A
dim(PA(0, H), PA(LS, GZ1), (0, AZ0 + 113), "345")
dim(PA(SLOPE_X0, H), PA(LS, GZ1), (0, AZ0 + 108), "73")
dim(PA(SLOPE_X0, H), PA(SLOPE_X1, SLOPE_Z1), (PA(SLOPE_X0 - 6, 0)[0], 0), "55", angle=90)
dim(PA(SLOPE_X1, SLOPE_Z1), PA(GX0, GZ1), (0, AZ0 + 64), "5")
dim(PA(GX0, GZ1), PA(LS, GZ1), (0, AZ0 + 64), "13")
dim(PA(GX0, GZ0), PA(BX1, BZ0), (0, AZ0 - 4), "5")
dim(PA(0, 0), PA(BX1, BZ0), (0, AZ0 - 9), "337")
dim(PA(0, 0), PA(L, GZ0 + 3), (0, AZ0 - 15), "350")
dim(PA(0, 0), PA(0, H), (AX0 - 14, 0), "100", angle=90)
dim(PA(0, 0), PA(0, BZ1), (AX0 - 7, 0), "17", angle=90)

leader([PA(GX1 - 0.9, GZ1 - 0.9), PA(GX1 + 4, GZ1 + 4), PA(GX1 + 6, GZ1 + 4)], "R3")
leader([PA(T - 1, RZ1 - 1), PA(T + 6, RZ1 + 3), PA(T + 9, RZ1 + 3)], "Fase 2x45°")
leader([PA(4, 1.8), PA(9, -4), PA(12, -4)], "Fase 3x10")
leader([PA(sx + 1.5, 26), PA(T + 12, 45), PA(T + 15, 45)], "3x16 DIN 97-St")
text("A - A", PA(48, 60), h=5, align="MIDDLE_CENTER")

# ---------------------------------------------------------------------------
# Schnitt B-B (1:1, unterbrochen)
# ---------------------------------------------------------------------------
BX0, BZ0P = 47, 31
B_L1, B_R = 95, 195


def bxb(y):
    return y if y <= B_L1 else y - (B_R - B_L1 - GAP)


def PB(y, z):
    return (BX0 + bxb(y), BZ0P + z)


side_q = [(0, ZAPF_H), (0, H), (LIP, H), (LIP, H - FALZ_T), (T, H - FALZ_T), (T, BZ1),
          (BY0, BZ1), (BY0, BZ0), (T, BZ0), (T, 0), (T - ZAPF, 0), (T - ZAPF, ZAPF_H)]
for mirror in (False, True):
    pts = [PB(B - y if mirror else y, z) for y, z in side_q]
    pline(pts, closed=True)
    c = PB(B - T / 2 if mirror else T / 2, 55)
    hatch([pts, text_box(c[0], c[1], "14/100", 2.0)])
    text("14/100", c, h=2.0, align="MIDDLE_CENTER")

# Boden FU 5
for a0, a1 in ((BY0, B_L1), (B_R, BY1)):
    pts = [PB(a0, BZ0), PB(a1, BZ0), PB(a1, BZ1), PB(a0, BZ1)]
    line(pts[0], pts[1])
    line(pts[3], pts[2])
    if a0 == BY0:
        line(pts[0], pts[3])
    if a1 == BY1:
        line(pts[1], pts[2])
    a = a0 + 4
    while a < a1 - 0.5:
        if not (60 <= a <= 74) and not (16 <= a <= 28):
            line(PB(a, BZ0), PB(a, BZ1), "Duenn")
        a += 4
text("FU 5", PB(67, (BZ0 + BZ1) / 2), h=2.0, align="MIDDLE_CENTER")

# Rueckwand in Ansicht (Oberkante + Fase)
for z in (RZ1, RZ1 - 2):
    line(PB(T, z), PB(B_L1, z))
    line(PB(B_R, z), PB(B - T, z))

# Schrauben (Mittellinien)
screws_y = [BY0 + 40, BY0 + 40 + 78.5, BY0 + 40 + 157]
for y in (screws_y[0], screws_y[2]):
    line(PB(y, 4), PB(y, 36), "Mittellinie")
pline([PB(screws_y[0], 33), PB(screws_y[0] + 8, 41), PB(screws_y[2] - 3, 41), PB(screws_y[2], 33)], "Bemassung")
mid = (PB(screws_y[0] + 8, 0)[0] + PB(screws_y[2] - 3, 0)[0]) / 2
text("3x16 DIN 97-St", (mid, BZ0P + 41.8), align="BOTTOM_CENTER")

for y in (B_L1, B_R):
    break_line(PB(y, 0)[0] + (1.5 if y == B_L1 else -1.5), BZ0P - 2, BZ0P + H + 2)

# Bemassung B-B
dim(PB(LIP, H), PB(B - LIP, H), (0, BZ0P + 110), "242 (Prüfmaß)")
dim(PB(B - T, H - FALZ_T), PB(B - LIP, H), (0, BZ0P + 105), "7,5")
dim(PB(B - LIP, H), PB(B, H), (0, BZ0P + 105), "(6,5)")
dim(PB(T, H - FALZ_T), PB(LIP, H), (PB(22, 0)[0], 0), "5", angle=90)
dim(PB(T - ZAPF, 0), PB(0, ZAPF_H), (BX0 - 6, 0), "6", angle=90)
dim(PB(T, 0), PB(30, BZ1), (PB(34, 0)[0], 0), "17", angle=90)
dim(PB(22, BZ0), PB(22, BZ1), (PB(22, 0)[0], 0), "5", angle=90)
dim(PB(BY0, BZ0), PB(T, 0), (0, BZ0P - 6), "5")
dim(PB(T, 0), PB(screws_y[0], 4), (0, BZ0P - 6), "35")
dim(PB(screws_y[0], 4), PB(screws_y[2], 4), (0, BZ0P - 6), "2x78,5")
dim(PB(B - ZAPF, 0), PB(B, ZAPF_H), (0, BZ0P - 6), "7")
dim(PB(BY0, BZ0), PB(BY1, BZ0), (0, BZ0P - 12), "237")
dim(PB(T - ZAPF, 0), PB(B - T + ZAPF, 0), (0, BZ0P - 18), "241 (Prüfmaß)")
text("B - B", PB(60, 60), h=5, align="MIDDLE_CENTER")

# ---------------------------------------------------------------------------
# 3D-Modell fuer Ansichten / Isometrie / Explosion
# ---------------------------------------------------------------------------


def clip_ranges(ranges, lo, hi):
    out = []
    for a, b in ranges:
        a, b = max(a, lo), min(b, hi)
        if b > a:
            out.append((a, b))
    return out


def edge_path(lo, hi, ranges, x_in, x_out):
    """Punktfolge (x,z) von lo nach hi; in ranges gilt x_in, sonst x_out."""
    zs = sorted({lo, hi, *[v for r in ranges for v in r]})
    pts = []
    for za, zb in zip(zs, zs[1:]):
        mid = (za + zb) / 2
        x = x_in if any(a < mid < b for a, b in ranges) else x_out
        pts += [(x, za), (x, zb)]
    clean = []
    for p in pts:
        if not clean or clean[-1] != p:
            clean.append(p)
    return clean


def side_profile(zb, zt):
    """Profil der Seite in x/z fuer eine Schicht mit Unterkante zb, Oberkante zt."""
    ztf = min(zt, SLOPE_Z1)
    pts = []
    chamfer = zb == 0
    pts.append((10, 0) if chamfer else (0, zb))
    front = edge_path(zb, ztf, clip_ranges(TAILS_FRONT, zb, ztf), LS, GX0)
    pts += front
    if zt > SLOPE_Z1:
        pts.append((SLOPE_X1, SLOPE_Z1))
        pts.append((SLOPE_X0 + (H - zt), zt))
    back = edge_path(zb, zt, clip_ranges(TAILS_BACK, zb, zt), T, 0)[::-1]
    pts += back
    if chamfer:
        pts.append((0, 3))
    clean = []
    for p in pts:
        if not clean or (abs(clean[-1][0] - p[0]) > 1e-9 or abs(clean[-1][1] - p[1]) > 1e-9):
            clean.append(p)
    if clean[0] == clean[-1]:
        clean.pop()
    return clean


def build_model():
    pr = []
    layers = [(0, LIP, ZAPF_H, H), (LIP, T - ZAPF, ZAPF_H, H - FALZ_T),
              (T - ZAPF, BY0, 0, H - FALZ_T), (BY0, T, 0, BZ0), (BY0, T, BZ1, H - FALZ_T)]
    for y0, y1, zb, zt in layers:
        prof = side_profile(zb, zt)
        pr.append(hlr.Prism("seite_v", "xzy", prof, y0, y1))
        pr.append(hlr.Prism("seite_h", "xzy", prof, B - y1, B - y0))
    # Rueckwand
    pr.append(hlr.Prism("rueckwand", "xzy", [(0, RZ0), (T, RZ0), (T, RZ1), (0, RZ1)], T, B - T))
    for a, b in TAILS_BACK:
        rect = [(0, a), (T, a), (T, b), (0, b)]
        pr.append(hlr.Prism("rueckwand", "xzy", rect, 0, T))
        pr.append(hlr.Prism("rueckwand", "xzy", rect, B - T, B))
    # Griffleiste
    gp = [(GX0, GZ0), (GX1, GZ0), (GX1, GZ1)] + edge_path(GZ0, GZ1, TAILS_FRONT, LS, GX0)[::-1]
    gp = [p for i, p in enumerate(gp) if i == 0 or p != gp[i - 1]]
    if gp[-1] == gp[0]:
        gp.pop()
    pr.append(hlr.Prism("griff", "xzy", gp, 0, T))
    pr.append(hlr.Prism("griff", "xzy", gp, B - T, B))
    pr.append(hlr.Prism("griff", "xzy", [(GX0, GZ0), (GX1, GZ0), (GX1, GZ1), (GX0, GZ1)], T, B - T))
    # Boden
    pr.append(hlr.Prism("boden", "xzy", [(0, BZ0), (BX1, BZ0), (BX1, BZ1), (0, BZ1)], BY0, BY1))
    return pr


MODEL = build_model()


def draw_view(prisms, view, right, up, ox, oy, scale=0.2, layer="Kontur"):
    lines = hlr.render(prisms, view, right, up, step=1.0)
    for u0, w0, u1, w1 in lines:
        if math.hypot(u1 - u0, w1 - w0) < 0.5:
            continue
        line((ox + u0 * scale, oy + w0 * scale), (ox + u1 * scale, oy + w1 * scale), layer)
    return lines


def section_mark(x, y_top, y_bot, letter, direction=-1):
    """Schnittverlauf mit Pfeilen und Buchstaben (senkrecht)."""
    line((x, y_top), (x, y_bot), "Mittellinie")
    for y, ty, va in ((y_top, y_top + 1, "BOTTOM_CENTER"), (y_bot, y_bot - 1, "TOP_CENTER")):
        line((x, y - 2.5 if y == y_top else y + 2.5), (x, y), "Schnittverlauf")
        ay = y - 1.2 if y == y_top else y + 1.2
        line((x, ay), (x + direction * 5, ay), "Bemassung")
        arrowhead((x + direction * 5, ay), (x, ay), size=2.2)
        text(letter, (x + direction * 2.5, ty), h=3.5, align=va)


s = 0.2
# Vorderansicht (Blick auf die Griffleiste), rechts = +y
FVX, FVY = 243, 255
draw_view(MODEL, (1, 0, 0), (0, 1, 0), (0, 0, 1), FVX, FVY)
dim((FVX, FVY), (FVX + B * s, FVY), (0, FVY - 21), "255")
dim((FVX + B * s, FVY), (FVX + B * s, FVY + H * s), (FVX + B * s + 9, 0), "100", angle=90)
section_mark(FVX + B / 2 * s, FVY + H * s + 3, FVY - 3, "A")

# Seitenansicht, rechts = +x
SVX, SVY = 320, 257
draw_view(MODEL, (0, -1, 0), (1, 0, 0), (0, 0, 1), SVX, SVY)
dim((SVX, SVY + 2), (SVX + L * s, SVY + GZ0 * s), (0, SVY - 19), "350")
section_mark(SVX + 170 * s, SVY + H * s + 3, SVY - 3, "B")

# Draufsicht (unter der Vorderansicht), rechts = +y, oben = -x
TVX, TVY = 243, 228
draw_view(MODEL, (0, 0, 1), (0, 1, 0), (-1, 0, 0), TVX, TVY)
for i, (a, b) in enumerate(((0.38, 0.62), (0.32, 0.68), (0.4, 0.6))):
    y = TVY - L * s * (0.52 + 0.025 * i)
    line((TVX + B * s * a, y), (TVX + B * s * b, y), "Duenn")

# Isometrie
ISO_V, ISO_R, ISO_U = (1, -1, 1), (1, 1, 0), (-1, 1, 2)
draw_view(MODEL, ISO_V, ISO_R, ISO_U, 307, 184)

# Explosionsdarstellung
OFF = {"rueckwand": (-100, 0, 0), "griff": (80, 0, 0), "seite_v": (0, -50, 0),
       "seite_h": (0, 50, 0), "boden": (0, 0, 0)}
EXPL = [p.moved(OFF[p.part]) for p in MODEL]
draw_view(EXPL, ISO_V, ISO_R, ISO_U, 275, 113)

# ---------------------------------------------------------------------------
# Schriftfeld (184 x 64 unten rechts)
# ---------------------------------------------------------------------------
TX, TY = 226, 10


def tl(x0, y0, x1, y1, layer="Schriftfeld"):
    line((TX + x0, TY + y0), (TX + x1, TY + y1), layer)


def tt(s_, x, y, h=1.8, align="LEFT"):
    text(s_, (TX + x, TY + y), h=h, align=align)


pline([(TX, TY), (TX + 184, TY), (TX + 184, TY + 64), (TX, TY + 64)], "Rahmen", closed=True)
# senkrechte Hauptteilungen
tl(56, 0, 56, 64)
tl(104, 0, 104, 64)
# oben
tl(0, 48, 104, 48)
tl(80, 48, 80, 64)
tl(56, 48, 56, 64)
tl(104, 56, 184, 56)
tl(104, 48, 184, 48)
tl(152, 56, 152, 64)
tt("(Verwendungsbereich)", 1, 61)
tt("(Zul.Abw.)", 57, 61)
tt("Oberfläche", 81, 61)
tt("Maßstab", 105, 61)
tt("1:1/1:5/Isometrie", 118, 57.5, h=2.5)
tt("(Gewicht)", 153, 61)
tt("(Werkstoff)", 105, 53.5)
tt("KI", 107, 49.2, h=2.5)
# Aenderungsfeld links
for i in range(1, 9):
    tl(0, 5 * i, 56, 5 * i, "Duenn")
for x in (8, 30, 44):
    tl(x, 0, x, 45, "Duenn")
tt("Zust.", 0.8, 1.4)
tt("Änderung", 9, 1.4)
tt("Datum", 31, 1.4)
tt("Name", 45, 1.4)
# Bearbeitet / geprueft
for y in (22, 28, 34, 40):
    tl(56, y, 104, y)
tl(70, 22, 70, 48)
tl(87, 22, 87, 48)
tt("Datum", 72, 41.5)
tt("Name", 89, 41.5)
tt("Bearb.", 57, 35.5)
tt("Gepr.", 57, 29.5)
tt("Norm", 57, 23.5)
tt("01.10.2026", 71, 35.5, h=1.6)
tl(56, 5, 104, 5)
pline([(TX + 58, TY + 8), (TX + 70, TY + 8), (TX + 70, TY + 19), (TX + 58, TY + 19)], "Schriftfeld", closed=True)
tt("HK", 64, 13.5, h=5, align="MIDDLE_CENTER")
tt("Fachverband", 72, 16, h=2.2)
tt("Holz und", 72, 12.5, h=2.2)
tt("Kunststoff NRW", 72, 9, h=2.2)
tt("(Urspr.)", 57, 1.4)
# rechts
tt("Benennung", 105, 44.5)
tt("Stapelkasten", 108, 34, h=5)
tl(104, 22, 184, 22)
tl(164, 5, 164, 22)
tt("(Zeichnungsnummer)", 105, 18.5)
tt("Z-10-1", 108, 9, h=5)
tt("Blatt", 165, 18.5)
tt("1", 174, 9, h=5, align="LEFT")
tl(104, 5, 184, 5)
tl(144, 0, 144, 5)
tt("(Ers. f.:)", 105, 1.4)
tt("(Ers. d.:)", 145, 1.4)

out = sys.argv[1] if len(sys.argv) > 1 else "Stapelkasten_Z-10-1.dxf"
doc.saveas(out)
print("geschrieben:", out)
