"""Erzeugt die Dreitafelprojektion "Schubkastenschrank aus Eiche" als DXF (A3 quer).

Projektionsmethode 1 (DIN ISO 5456-2): Vorderansicht, Seitenansicht von links
(rechts daneben), Draufsicht (darunter), dazu Schnitt A-A. Alle Ansichten 1:5.
Blattkoordinaten in mm (Modellbereich 1:1 = Papier).

Aufruf:  python3 schubkastenschrank.py  ->  Schubkastenschrank_Eiche.dxf

WICHTIG: Werte, die mit "n.f." markiert sind, sind NICHT festgelegt. Sie werden
nur zum Zeichnen gebraucht (Darstellungswerte) und als "n.f." bemasst.
"""
import math
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment

# ---------------------------------------------------------------------------
# Vorgegebene Masse (Aufgabenstellung / Blum)
# ---------------------------------------------------------------------------
B = 700          # Breite
H = 400          # Hoehe
T = 290          # Tiefe
FR = 20          # Schubkastenfront Eiche
RW = 8           # Rueckwand
NL = 250         # MOVENTO Nennlaenge
SKL = NL - 10    # Schubkastenlaenge (Blum: NL - 10)
LT_ERF = NL + 3 + 4   # lichte Tiefe hinter der Front (Blum: NL + 3, mit TIP-ON + 4)

# ---------------------------------------------------------------------------
# Darstellungswerte (n.f. = noch festzulegen) -- nur zum Zeichnen!
# ---------------------------------------------------------------------------
S = 19           # Plattenstaerke Korpus / Rahmen           n.f.
M = 19           # Staerke Mittelwand                        n.f.
F = 3            # Fuge Fronten                              n.f.
ZS = 16          # Schubkastenseite (Blum: max. 16)          n.f.
BN = 13          # Bodennische (Blum: 12 ... 15)             n.f.
BD = 8           # Schubkastenboden                          n.f.
HS_ABZ = 50      # Fronthoehe - Seitenhoehe                  n.f.
ZB_OFF = 10      # Unterkante Seite ueber Unterkante Front   n.f.
RUN_H = 11       # Hoehe Fuehrung (schematisch)              n.f.

FW = (B - 2 * S - 3 * F) / 2      # Frontbreite
FH = (H - 2 * S - 3 * F) / 2      # Fronthoehe
RI = T - RW                        # Innenflaeche Rueckwand (bei buendiger Rueckwand)

SC = 0.2         # Massstab 1:5

# ---------------------------------------------------------------------------
# Dokument, Layer, Linientypen, Bemassungsstil
# ---------------------------------------------------------------------------
doc = ezdxf.new("R2010", setup=True, units=4)
doc.header["$LTSCALE"] = 1.0
doc.header["$MEASUREMENT"] = 1
doc.header["$LIMMIN"] = (0, 0)
doc.header["$LIMMAX"] = (420, 297)
doc.header["$EXTMIN"] = (0, 0, 0)
doc.header["$EXTMAX"] = (420, 297, 0)
msp = doc.modelspace()

doc.linetypes.add("ISO_VERDECKT", pattern=[3.0, 2.0, -1.0], description="Strichlinie __ __ __")
doc.linetypes.add("ISO_STRICHPUNKT", pattern=[12.5, 8.0, -1.5, 0.5, -1.5],
                  description="Strichpunktlinie ____ . ____ .")

LAYERS = {
    "Rahmen": (7, 70, "Continuous"),
    "Kontur": (7, 50, "Continuous"),
    "Duenn": (8, 25, "Continuous"),
    "Verdeckt": (6, 25, "ISO_VERDECKT"),
    "Mittellinie": (1, 25, "ISO_STRICHPUNKT"),
    "Schnittverlauf": (1, 70, "Continuous"),
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
ds.dxf.dimtsz = 1.2          # Schraegstriche (Tischler)
ds.dxf.dimasz = 2.0
ds.dxf.dimexo = 1.0
ds.dxf.dimexe = 1.5
ds.dxf.dimgap = 0.8
ds.dxf.dimtad = 1
ds.dxf.dimtih = 0
ds.dxf.dimtoh = 0
ds.dxf.dimdec = 0
ds.dxf.dimlfac = 5.0         # 1:5 -> Masszahl = Papiermass x 5
ds.dxf.dimdsep = ord(",")
ds.dxf.dimclrd = 3
ds.dxf.dimclre = 3
ds.dxf.dimclrt = 7
ds.dxf.dimlwd = 25
ds.dxf.dimlwe = 25


def line(p, q, layer="Kontur"):
    msp.add_line(p, q, dxfattribs={"layer": layer})


def pline(pts, layer="Kontur", closed=False):
    return msp.add_lwpolyline(pts, format="xy", close=closed, dxfattribs={"layer": layer})


def text(s, p, h=2.5, layer="Text", align="LEFT", rot=0):
    t = msp.add_text(s, height=h, rotation=rot, dxfattribs={"layer": layer, "style": "ISO"})
    t.set_placement(p, align=getattr(TextEntityAlignment, align))
    return t


def dim(p1, p2, base, txt="<>", angle=0, loc=None):
    d = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle, text=txt, location=loc,
                           dimstyle="TISCHLER", dxfattribs={"layer": "Bemassung"})
    d.render()


def arrowhead(tip, frm, size=2.2, layer="Bemassung"):
    ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
    w = size * 0.28
    bx, by = tip[0] - size * math.cos(ang), tip[1] - size * math.sin(ang)
    nx, ny = -math.sin(ang) * w, math.cos(ang) * w
    msp.add_solid([tip, (bx + nx, by + ny), (bx - nx, by - ny)], dxfattribs={"layer": layer})


def dot(p, r=0.45):
    h = msp.add_hatch(color=3, dxfattribs={"layer": "Bemassung"})
    h.paths.add_edge_path().add_arc(p, r, 0, 360)


def leader(pts, label, h=2.2):
    pline(pts, "Bemassung")
    arrowhead(pts[0], pts[1])
    end, prev = pts[-1], pts[-2]
    if end[0] >= prev[0]:
        text(label, (end[0] + 0.8, end[1] - h / 2), h)
    else:
        text(label, (end[0] - 0.8, end[1] - h / 2), h, align="BOTTOM_RIGHT")


def balloon(target, center, n, r=3.0):
    """Positionsnummer: Kreis mit Hinweislinie und Punkt am Bauteil."""
    msp.add_circle(center, r, dxfattribs={"layer": "Bemassung"})
    text(str(n), center, 2.5, align="MIDDLE_CENTER")
    dx, dy = target[0] - center[0], target[1] - center[1]
    d = math.hypot(dx, dy)
    start = (center[0] + dx / d * r, center[1] + dy / d * r)
    line(start, target, "Bemassung")
    dot(target)


def hatch_rect(u0, v0, u1, v1, view, pattern="ANSI31", scale=0.5, angle=0.0):
    h = msp.add_hatch(dxfattribs={"layer": "Schraffur"})
    h.set_pattern_fill(pattern, scale=scale, angle=angle)
    h.paths.add_polyline_path([view(u0, v0), view(u1, v0), view(u1, v1), view(u0, v1)],
                              is_closed=True)


def mkview(ox, oy, flip_v=None):
    if flip_v is None:
        return lambda u, v: (ox + u * SC, oy + v * SC)
    return lambda u, v: (ox + u * SC, oy + (flip_v - v) * SC)


def rect(view, u0, v0, u1, v1, layer="Kontur"):
    pline([view(u0, v0), view(u1, v0), view(u1, v1), view(u0, v1)], layer, closed=True)


def seg(view, u0, v0, u1, v1, layer="Kontur"):
    line(view(u0, v0), view(u1, v1), layer)


def title(s, p, scale_txt="M 1:5"):
    text(s, p, 3.5, align="LEFT")
    text(scale_txt, (p[0], p[1] - 4.2), 2.2)


# Front-Lagen (Zeilen von unten nach oben)
ROWS = [(S + F + j * (FH + F), S + F + j * (FH + F) + FH) for j in range(2)]
COLS = [(S + F + i * (FW + F), S + F + i * (FW + F) + FW) for i in range(2)]

# ---------------------------------------------------------------------------
# Blattrahmen
# ---------------------------------------------------------------------------
pline([(0, 0), (420, 0), (420, 297), (0, 297)], "Duenn", closed=True)
pline([(20, 10), (410, 10), (410, 287), (20, 287)], "Rahmen", closed=True)

# ---------------------------------------------------------------------------
# Vorderansicht  (u = x, v = z)
# ---------------------------------------------------------------------------
FX, FY = 48, 184
V = mkview(FX, FY)
rect(V, 0, 0, B, H)                         # Korpus aussen
rect(V, S, S, B - S, H - S)                 # Rahmen innen / Oeffnung
for (x0, x1) in COLS:
    for (z0, z1) in ROWS:
        rect(V, x0, z0, x1, z1)             # Fronten
# Mittelwand hinter den Fronten (verdeckt)
for x in (B / 2 - M / 2, B / 2 + M / 2):
    seg(V, x, S, x, H - S, "Verdeckt")
# Mittellinien
seg(V, B / 2, -18, B / 2, H + 18, "Mittellinie")
seg(V, -18, H / 2, B + 18, H / 2, "Mittellinie")
title("Vorderansicht", (FX, FY + H * SC + 21))

# Schnittverlauf A-A (Blick in +x)
ax = 175
for (v0, v1, va) in ((H + 4, H + 34, H + 26), (-52, -92, -84)):
    line(V(ax, v0), V(ax, v1), "Schnittverlauf")
    p = V(ax, va)
    line(p, (p[0] + 6, p[1]), "Bemassung")
    arrowhead((p[0] + 6.5, p[1]), p, size=2.5)
    text("A", (p[0] + 2.5, p[1] + 1.2 if va > 0 else p[1] - 4.0), 3.5)

# Bemassung Vorderansicht
dim(V(0, H), V(B, H), (0, FY + H * SC + 9))
dim(V(0, 0), V(0, H), (FX - 12, 0), angle=90)
dim(V(0, ROWS[0][0]), V(0, ROWS[0][1]), (FX - 6, 0), "h  n.f.", angle=90)
dim(V(COLS[0][0], 0), V(COLS[0][1], 0), (0, FY - 8), "b  n.f.")
dim(V(COLS[1][0], 0), V(COLS[1][1], 0), (0, FY - 8), "b  n.f.")
leader([V(B - S / 2, H * 0.80), (FX + B * SC + 4, FY + H * SC * 0.80 + 10),
        (FX + B * SC + 8, FY + H * SC * 0.80 + 10)], "s  n.f.")
leader([V(B / 2, ROWS[1][0] - F / 2), (FX + B * SC * 0.62, FY + H * SC * 0.5 + 5),
        (FX + B * SC * 0.70, FY + H * SC * 0.5 + 5)], "Fuge f  n.f.")
balloon(V(COLS[0][0] + 60, ROWS[1][1] - 40), (FX + 7, FY + H * SC + 3.5), 6)
balloon(V(S / 2, 30), (FX - 5, FY - 5), 1)

# ---------------------------------------------------------------------------
# Seitenansicht von links  (u = y Tiefe, Front links; v = z)
# ---------------------------------------------------------------------------
SX, SY = 216, 184
W = mkview(SX, SY)
rect(W, 0, 0, T, H)
# verdeckte Kanten
seg(W, 0, S, RI, S, "Verdeckt")
seg(W, 0, H - S, RI, H - S, "Verdeckt")
seg(W, RI, S, RI, H - S, "Verdeckt")
for (z0, z1) in ROWS:
    pline([W(0, z0), W(FR, z0), W(FR, z1), W(0, z1)], "Verdeckt")
seg(W, -12, H / 2, T + 12, H / 2, "Mittellinie")
title("Seitenansicht von links", (SX, SY + H * SC + 21))
dim(W(0, H), W(FR, H), (0, SY + H * SC + 6))
dim(W(FR, H), W(RI, H), (0, SY + H * SC + 6))
dim(W(RI, H), W(T, H), (0, SY + H * SC + 6), loc=(W(T, H)[0] + 3.5, SY + H * SC + 6.8))
dim(W(0, 0), W(T, 0), (0, SY - 8))
dim(W(T, 0), W(T, H), (SX + T * SC + 8, 0), angle=90)
balloon(W(T * 0.55, H * 0.35), (SX + T * SC * 0.55 + 9, SY + 9), 1)

# ---------------------------------------------------------------------------
# Schnitt A-A  (u = y Tiefe, Front links; v = z)
# ---------------------------------------------------------------------------
AX, AY = 300, 184
A = mkview(AX, AY)
# Ober- und Unterboden (geschnitten)
for (v0, v1) in ((0, S), (H - S, H)):
    rect(A, 0, v0, T, v1)
    hatch_rect(0, v0, T, v1, A)
# Rueckwand (geschnitten, Material n.f.)
rect(A, RI, S, T, H - S)
hatch_rect(RI, S, T, H - S, A, pattern="ANSI37", scale=0.35)
# Mittelwand dahinter: Vorderkante sichtbar zwischen den Schubkaesten
seg(A, FR, S, FR, H - S, "Duenn")
seg(A, FR, S, RI, S, "Kontur")
for j, (z0, z1) in enumerate(ROWS):
    # Front (geschnitten)
    rect(A, 0, z0, FR, z1)
    hatch_rect(0, z0, FR, z1, A, angle=90)
    zb = z0 + ZB_OFF
    hs = FH - HS_ABZ
    zt = zb + hs
    u0, u1 = FR, FR + SKL                 # Schubkasten 240 lang
    # Vorder- und Hinterstueck, Boden (geschnitten)
    rect(A, u0, zb, u0 + ZS, zt)
    hatch_rect(u0, zb, u0 + ZS, zt, A, angle=90)
    zbo0, zbo1 = zb + BN, zb + BN + BD
    rect(A, u1 - ZS, zbo1, u1, zt)
    hatch_rect(u1 - ZS, zbo1, u1, zt, A, angle=90)
    rect(A, u0 + ZS, zbo0, u1, zbo1)
    hatch_rect(u0 + ZS, zbo0, u1, zbo1, A, pattern="ANSI37", scale=0.35)
    # Schubkastenseite (sichtbar dahinter)
    seg(A, u0 + ZS, zt, u1 - ZS, zt)
    seg(A, u0 + ZS, zb, u1, zb)
    seg(A, u1, zb, u1, zbo0)
    # Fuehrung MOVENTO in der Bodennische (schematisch)
    rect(A, FR, zb + 1, FR + NL, zb + 1 + RUN_H, "Duenn")
    if j == 1:
        ZT_UP, ZB_UP, ZBO_UP = zt, zb, zbo0
    else:
        ZT_LO, ZB_LO, ZBO_LO = zt, zb, zbo0

text("Schnitt A-A", (AX, AY + H * SC + 21), 3.5)
text("M 1:5", (AX, AY + H * SC + 16.8), 2.2)

# Bemassung Schnitt: Tiefenaufbau unten
yb1 = AY - 7
dim(A(0, 0), A(FR, 0), (0, yb1))
dim(A(FR, 0), A(FR + LT_ERF, 0), (0, yb1), "≥ 257")
dim(A(FR + LT_ERF, 0), A(RI, 0), (0, yb1), "≤ 5",
    loc=(A(FR + LT_ERF, 0)[0] - 0.5, yb1 - 4.2))
dim(A(RI, 0), A(T, 0), (0, yb1), loc=(A(T, 0)[0] + 3.8, yb1 + 0.8))
dim(A(0, 0), A(T, 0), (0, AY - 14))
# oben: Fuehrung und Schubkastenlaenge
dim(A(FR, ZB_UP), A(FR + NL, ZB_UP), (0, AY + H * SC + 6), "NL 250")
dim(A(FR, ZT_UP), A(FR + SKL, ZT_UP), (0, AY + H * SC + 11.5), "240 (NL−10)")
# rechts: Hoehe, Seitenhoehe, Nische
xr = AX + T * SC
dim(A(T, 0), A(T, H), (xr + 16, 0), angle=90)
dim(A(FR + SKL, ZB_LO), A(FR + SKL, ZT_LO), (xr + 7, 0), "n.f.", angle=90)
dim(A(FR + SKL, ZB_UP), A(FR + SKL, ZBO_UP), (xr + 7, 0), "12–15", angle=90,
    loc=(xr + 7, A(0, ZB_UP)[1] - 5))
# Positionen
balloon(A(T * 0.45, H - S / 2), (AX + T * SC * 0.45 + 6, AY + H * SC + 3.0), 2)
balloon(A(12, S / 2), (AX - 6.5, AY + 1.9), 3)
balloon(A(RI + RW / 2, H * 0.62), (xr + 4.5, AY + H * SC * 0.62 + 3), 5)
balloon(A(FR / 2, ROWS[1][0] + 60), (AX - 6, AY + H * SC * 0.66), 6)
balloon(A(FR + 140, ZT_UP), (AX + 140 * SC + 10, AY + H * SC * 0.86), 7)
balloon(A(FR + 120, ZBO_LO + BD / 2), (AX + 120 * SC + 6, AY + H * SC * 0.30), 8)
balloon(A(FR + 150, ZB_UP + 1 + RUN_H / 2), (AX + 40, AY + 36.8), 9)

# ---------------------------------------------------------------------------
# Draufsicht  (u = x, v = Tiefe; Front oben)
# ---------------------------------------------------------------------------
DX, DY = 48, 96
D = mkview(DX, DY, flip_v=T)                # D(x, y): y = 0 (Front) oben
rect(D, 0, 0, B, T)
seg(D, S, 0, S, T, "Verdeckt")
seg(D, B - S, 0, B - S, T, "Verdeckt")
seg(D, S, FR, B - S, FR, "Verdeckt")
seg(D, S, RI, B - S, RI, "Verdeckt")
for x in (B / 2 - M / 2, B / 2 + M / 2):
    seg(D, x, FR, x, RI, "Verdeckt")
seg(D, B / 2, -12, B / 2, T + 12, "Mittellinie")
text("Draufsicht", (DX, DY - 16.5), 3.5)
text("M 1:5", (DX + 32, DY - 16.5), 2.2)
dim(D(0, T), D(B, T), (0, DY - 7))
dim(D(0, 0), D(0, T), (DX - 8, 0), angle=90)
leader([D(B / 2 + M / 2, T * 0.55), (DX + B * SC * 0.5 + 12, DY + T * SC * 0.45 - 2),
        (DX + B * SC * 0.5 + 16, DY + T * SC * 0.45 - 2)], "Mittelwand m  n.f.")
balloon(D(B / 2 - M / 2, T * 0.70), (DX + B * SC * 0.5 - 12, DY + T * SC * 0.30 - 4), 4)
balloon(D(B - S, T * 0.70), (DX + B * SC + 6, DY + T * SC * 0.30), 1)

# ---------------------------------------------------------------------------
# Hinweise: Pruefung MOVENTO (unten links)
# ---------------------------------------------------------------------------
NX, NY = 24, 72
text("Prüfung MOVENTO TIP-ON (760H2500T, NL 250, 40 kg) – Tiefenaufbau", (NX, NY), 2.5)
notes = [
    "1  Erf. lichte Korpustiefe MOVENTO = NL + 3 mm (Blum), mit TIP-ON lt. Blum-Fußnote zusätzlich + 4 mm",
    "    → erforderlich hinter der Front: 250 + 3 + 4 = 257 mm.",
    "2  Vorhanden: 290 − 20 (einliegende Front) − 8 (Rückwand) = 262 mm, nur wenn Rückwand hinten bündig",
    "    sitzt (Falz oder aufgesetzt). 262 ≥ 257 → kompatibel, Reserve 5 mm. NL 270 wäre zu lang (277 > 262).",
    "3  Rückwand in Nut nur bei Rücksprung ≤ 5 mm möglich → praktisch Falz oder aufgesetzt; Befestigung n.f.",
    "    Wandaufhängung darf nicht in die lichte Tiefe ragen (keine Hängeleiste innen).",
    "4  Schubkasten Holz: Länge NL − 10 = 240 mm; Innenbreite SKW = LW − 42; Seiten max. 16 mm;",
    "    Nische unter dem Boden 12–15 mm hoch (Blum). Höhe der Seiten und Höhenlage der Führungen n.f.",
    "5  TIP-ON: Synchronisation lt. Händler-/Blum-Angabe erforderlich (Art.-Nr. lt. Blum-Katalog prüfen).",
    "    Fuge f: Blum nennt ≥ 2,5 mm (TIP-ON BLUMOTION) – für 760H2500T in den Blum-Unterlagen bestätigen.",
    "6  Einliegende Front: Führung um 20 mm zurückgesetzt montieren; Rücksprung Mittelwand-Vorderkante",
    "    für den Drückweg TIP-ON n.f. – Einbaumaße vor Fertigung mit aktueller Blum-Montageanleitung prüfen.",
]
for i, s in enumerate(notes):
    text(s, (NX, NY - 5.0 - i * 4.4), 1.9)

# ---------------------------------------------------------------------------
# Formeln / noch festzulegende Masse (Mitte rechts)
# ---------------------------------------------------------------------------
KX, KY = 222, 166
text("Noch festzulegen (n.f.) und Formeln", (KX, KY), 2.5)
kl = [
    "s  Plattenstärke Korpus / Rahmen          m  Stärke Mittelwand",
    "f  Fuge zwischen Fronten und Rahmen       h, b  Fronthöhe / -breite",
    "b = (700 − 2s − 3f) / 2          h = (400 − 2s − 3f) / 2",
    "LW je Fach = (700 − 2s − m) / 2          SKW = LW − 42",
    "Eckverbindungen, Rückwandbefestigung, Wandaufhängung: n.f.",
    "Darstellung: n.f.-Maße schematisch gezeichnet (s = m = 19,",
    "f = 3) – NICHT abgreifen, erst nach Festlegung übernehmen!",
]
for i, s in enumerate(kl):
    text(s, (KX, KY - 5.0 - i * 4.2), 1.9)

# ---------------------------------------------------------------------------
# Stueckliste (ueber dem Schriftfeld)
# ---------------------------------------------------------------------------
PX, PY = 226, 61
cols = [0, 9, 17, 77, 184]
parts = [
    ("1", "2", "Seite (umlaufender Rahmen)", "Eiche massiv, s n.f."),
    ("2", "1", "Oberboden (Rahmen)", "Eiche massiv, s n.f."),
    ("3", "1", "Unterboden (Rahmen)", "Eiche massiv, s n.f."),
    ("4", "1", "Mittelwand", "Eiche, m n.f."),
    ("5", "1", "Rückwand", "8 mm, Material n.f."),
    ("6", "4", "Schubkastenfront, grifflos", "Eiche 20 mm, geölt"),
    ("7", "4", "Schubkasten (Seiten, Vorder-/Hinterst.)", "Holz, ≤ 16 mm, L 240"),
    ("8", "4", "Schubkastenboden", "n.f."),
    ("9", "4", "Führung MOVENTO TIP-ON (Paar)", "Blum 760H2500T NL 250"),
    ("10", "4", "Synchronisation TIP-ON", "Blum, Art.-Nr. n.f."),
    ("11", "–", "Wandaufhängung", "n.f."),
]
RH = 4.4
nrow = len(parts) + 1
pline([(PX, PY), (PX + 184, PY), (PX + 184, PY + nrow * RH), (PX, PY + nrow * RH)],
      "Schriftfeld", closed=True)
for i in range(1, nrow):
    line((PX, PY + i * RH), (PX + 184, PY + i * RH), "Duenn")
for c in cols[1:-1]:
    line((PX + c, PY), (PX + c, PY + nrow * RH), "Duenn")
hdr = ("Pos.", "Stk.", "Benennung", "Werkstoff / Abmessung")
for c, s in zip(cols, hdr):
    text(s, (PX + c + 1, PY + (nrow - 1) * RH + 1.3), 1.9)
for r, row in enumerate(reversed(parts)):
    for c, s in zip(cols, row):
        text(s, (PX + c + 1, PY + r * RH + 1.3), 1.9)

# ---------------------------------------------------------------------------
# Schriftfeld (184 x 51 unten rechts)
# ---------------------------------------------------------------------------
TX, TY = 226, 10
TW, TH = 184, 51


def tl(x0, y0, x1, y1, layer="Schriftfeld"):
    line((TX + x0, TY + y0), (TX + x1, TY + y1), layer)


def tt(s, x, y, h=1.8, align="LEFT"):
    text(s, (TX + x, TY + y), h=h, align=align)


pline([(TX, TY), (TX + TW, TY), (TX + TW, TY + TH), (TX, TY + TH)], "Rahmen", closed=True)
tl(0, 33, TW, 33)
tl(0, 17, TW, 17)
tl(46, 0, 46, 17)
tl(92, 0, 92, 17)
tl(138, 0, 138, 17)
tl(60, 33, 60, TH)
tl(108, 33, 108, TH)
tl(146, 33, 146, TH)
tt("Benennung", 1, 30.2)
tt("Mittelstufenprojekt – Schubkastenschrank aus Eiche", 2, 22, h=4.2)
tt("Wandhängend, 4 Schubkästen 2×2, grifflos (BLUM MOVENTO TIP-ON)", 2, 18.6, h=1.9)
tt("Werkstoff", 1, 48.2)
tt("Eiche massiv, geölt", 2, 38, h=2.5)
tt("Maßstab", 61, 48.2)
tt("1:5", 64, 37, h=5)
tt("Maße in mm", 80, 38, h=2.0)
tt("Format / Blatt", 109, 48.2)
tt("A3   1/1", 111, 38, h=3.5)
tt("Projektion", 147, 48.2)
# Symbol Projektionsmethode 1
cx, cy = TX + 158, TY + 39.5
pline([(cx, cy - 3), (cx + 11, cy - 4.5), (cx + 11, cy + 4.5), (cx, cy + 3)], "Duenn", closed=True)
line((cx - 3, cy), (cx + 13, cy), "Mittellinie")
msp.add_circle((cx + 21, cy), 4.5, dxfattribs={"layer": "Duenn"})
msp.add_circle((cx + 21, cy), 3.0, dxfattribs={"layer": "Duenn"})
tt("Gezeichnet", 1, 14.2)
tt("(Name)", 2, 5, h=2.5)
tt("Datum", 47, 14.2)
tt("25.11.2026", 48, 5, h=2.5)
tt("Geprüft", 93, 14.2)
tt("Zeichnungs-Nr.", 139, 14.2)
tt("MSP-SK-01", 140, 5, h=3.5)
tl(0, 0, 0, 0)

out = sys.argv[1] if len(sys.argv) > 1 else "Schubkastenschrank_Eiche.dxf"
doc.saveas(out)
print("geschrieben:", out)
