"""Mittelstufenprojekt "TOP SECRET 2.0" - zwei wandhaengende Schubkastenschraenke.

Erzeugt eine DXF mit zwei A3-Blaettern (quer) im Modellbereich:
  Blatt 1 (x 0..420):   Dreitafelprojektion 1:5 (Projektionsmethode 1) + Schnitt A-A 1:5
  Blatt 2 (x 440..860): Details B (Aufhaengung, 1:2), C (Verbindung, 1:1),
                        D (doppelter Boden, 1:2), Stueckliste, Quellen

Modellkoordinaten des Moebels (mm):
  x = Breite (0 links .. 700 rechts), y = Tiefe (0 vorn .. 305 Wand), z = Hoehe (0 .. 400)

Kennzeichnung der Masse in der Zeichnung:
  ohne Zusatz  = vorgegeben oder daraus berechnet
  (H)          = Herstellerangabe (Blum TD-132/1 bzw. Haefele-Produktseite)
  (G)          = gewaehlt (Konstruktionsvorschlag, darf geaendert werden)
  n.f.         = noch festzulegen / beim Hersteller zu bestaetigen

Aufruf:  python3 top_secret.py  ->  TopSecret_Schubkastenschrank.dxf
"""
import math
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment

# ---------------------------------------------------------------------------
# Masse
# ---------------------------------------------------------------------------
B, H, T = 700, 400, 305      # gesamt; T = 281 + 8 + 16 (siehe unten)
BS = 350                      # Breite je Schrank
E = 20                        # Eiche aussen
P = 19                        # Spanplatte schwarz
EO = E + P                    # Rahmenansicht vorn: 39
TE = T - 2                    # Eiche hinten 2 mm kuerzer (Quellen/Schwinden) (G)
X = 20                        # Frontdicke
NL = 250                      # MOVENTO Nennlaenge
LT_MIN = NL + X + 7           # 277 (H) Innenschubkasten mit TIP-ON
RW = 8                        # Rueckwand (G)
FREI = 16                     # Freiraum hinter Rueckwand min. 16 (H, Haefele)
NUT = 8                       # Nuttiefe Rueckwand (G)
LT = T - FREI - RW            # 281 vorhandene lichte Tiefe
LW = BS - 2 * EO              # 272 lichte Korpusweite
LH = H - 2 * EO               # 322 lichte Hoehe
F = 3                         # Fuge Fronten (G)
FB = LW - 2 * F               # 266 Frontbreite
FH = (LH - 3 * F) / 2         # 156,5 Fronthoehe
SKL = NL - 10                 # 240 (H)
ISKL = SKL + X                # 260 (H)
SKW = LW - 42                 # 230 (H)
ZS = 15                       # Zarge (G, max 16 H)
NI = 13                       # Bodennische (G, 12-15 H)
BD = 8                        # Schubkastenboden (G)
HS = 110                      # Hoehe Schubkastenseite (G)
GF = 18                       # Hoehe Geheimfach (G)
EB = 6                        # Einlegeboden (G)

FRONT_Z = [(EO + F, EO + F + FH), (EO + 2 * F + FH, EO + 2 * F + 2 * FH)]
BT_OFF = 37                   # OK Schubkastenboden ueber UK Front (G) -> 40 ueber Korpusboden
DRAW = []                     # je Reihe: (UK Seite, OK Boden, OK Seite)
for z0, _ in FRONT_Z:
    bt = z0 + BT_OFF
    sb = bt - BD - NI
    DRAW.append((sb, bt, sb + HS))
BOLT_Z = [187, 347]           # Hoehe Verbindungsschrauben (G)
BOLT_Y = [60, 220]            # Tiefe Verbindungsschrauben (G)

# ---------------------------------------------------------------------------
# DXF-Grundlagen
# ---------------------------------------------------------------------------
doc = ezdxf.new("R2010", setup=True, units=4)
doc.header["$LTSCALE"] = 1.0
doc.header["$MEASUREMENT"] = 1
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
    "Beschlag": (4, 35, "Continuous"),
}
for name, (col, lw, lt) in LAYERS.items():
    doc.layers.add(name, color=col, lineweight=lw, linetype=lt)
doc.styles.add("ISO", font="isocpeur.ttf")


def make_dimstyle(name, lfac):
    ds = doc.dimstyles.new(name)
    ds.dxf.dimtxt = 2.5
    ds.dxf.dimtxsty = "ISO"
    ds.dxf.dimtsz = 1.2
    ds.dxf.dimasz = 2.0
    ds.dxf.dimexo = 1.0
    ds.dxf.dimexe = 1.5
    ds.dxf.dimgap = 0.8
    ds.dxf.dimtad = 1
    ds.dxf.dimtih = 0
    ds.dxf.dimtoh = 0
    ds.dxf.dimdec = 1
    ds.dxf.dimzin = 8
    ds.dxf.dimlfac = lfac
    ds.dxf.dimdsep = ord(",")
    ds.dxf.dimclrd = 3
    ds.dxf.dimclre = 3
    ds.dxf.dimclrt = 7


make_dimstyle("M5", 5.0)
make_dimstyle("M2", 2.0)
make_dimstyle("M1", 1.0)


def line(p, q, layer="Kontur"):
    msp.add_line(p, q, dxfattribs={"layer": layer})


def pline(pts, layer="Kontur", closed=False):
    msp.add_lwpolyline(pts, format="xy", close=closed, dxfattribs={"layer": layer})


def clean(s):
    for a, b in (("≥", "min. "), (" → ", ": "), ("→ ", ""), ("−", "-"), ("Ø", "%%c")):
        s = s.replace(a, b)
    return s


def text(s, p, h=2.5, align="LEFT", rot=0, layer="Text"):
    s = clean(s)
    t = msp.add_text(s, height=h, rotation=rot, dxfattribs={"layer": layer, "style": "ISO"})
    t.set_placement(p, align=getattr(TextEntityAlignment, align))


def arrowhead(tip, frm, size=2.0):
    a = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
    w = size * 0.28
    bx, by = tip[0] - size * math.cos(a), tip[1] - size * math.sin(a)
    nx, ny = -math.sin(a) * w, math.cos(a) * w
    msp.add_solid([tip, (bx + nx, by + ny), (bx - nx, by - ny)], dxfattribs={"layer": "Bemassung"})


def dot(p, r=0.45):
    h = msp.add_hatch(color=3, dxfattribs={"layer": "Bemassung"})
    h.paths.add_edge_path().add_arc(p, r, 0, 360)


def leader(target, knee, label, h=2.0, right=True, arrow=True):
    end = (knee[0] + (5 if right else -5), knee[1])
    pline([target, knee, end], "Bemassung")
    if arrow:
        arrowhead(target, knee)
    else:
        dot(target)
    if right:
        text(label, (end[0] + 0.8, end[1] - h / 2), h)
    else:
        text(label, (end[0] - 0.8, end[1] - h / 2), h, align="BOTTOM_RIGHT")


def balloon(target, center, n, r=2.8):
    msp.add_circle(center, r, dxfattribs={"layer": "Bemassung"})
    text(str(n), center, 2.3 if len(str(n)) < 2 else 2.0, align="MIDDLE_CENTER")
    dx, dy = target[0] - center[0], target[1] - center[1]
    d = math.hypot(dx, dy)
    line((center[0] + dx / d * r, center[1] + dy / d * r), target, "Bemassung")
    dot(target)


def callout(center, r, letter, label_pos):
    msp.add_circle(center, r, dxfattribs={"layer": "Duenn"})
    text(letter, label_pos, 3.5)


def dim(p1, p2, base, txt="<>", vertical=False, loc=None, ds="M5"):
    d = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=90 if vertical else 0, text=clean(txt),
                           location=loc, dimstyle=ds, dxfattribs={"layer": "Bemassung"})
    d.render()


def hatch_poly(pts, pattern="ANSI31", scale=0.5, angle=0.0):
    h = msp.add_hatch(dxfattribs={"layer": "Schraffur"})
    h.set_pattern_fill(pattern, scale=scale, angle=angle)
    h.paths.add_polyline_path(pts, is_closed=True)


def solid_poly(pts):
    """Schwarz gefuellt (z. B. duenne Rueckwand im kleinen Massstab)."""
    h = msp.add_hatch(color=7, dxfattribs={"layer": "Schraffur"})
    h.paths.add_polyline_path(pts, is_closed=True)


class View:
    """Abbildung (u, v) -> Blatt. flip: v wird von oben nach unten gezaehlt."""

    def __init__(self, ox, oy, scale, flip_from=None):
        self.ox, self.oy, self.s, self.flip = ox, oy, scale, flip_from

    def __call__(self, u, v):
        if self.flip is not None:
            v = self.flip - v
        return (self.ox + u * self.s, self.oy + v * self.s)

    def rect(self, u0, v0, u1, v1, layer="Kontur"):
        pline([self(u0, v0), self(u1, v0), self(u1, v1), self(u0, v1)], layer, closed=True)

    def seg(self, u0, v0, u1, v1, layer="Kontur"):
        line(self(u0, v0), self(u1, v1), layer)

    def cut(self, u0, v0, u1, v1, pattern="ANSI31", scale=0.5, angle=0.0, layer="Kontur"):
        self.rect(u0, v0, u1, v1, layer)
        hatch_poly([self(u0, v0), self(u1, v0), self(u1, v1), self(u0, v1)], pattern, scale, angle)

    def black(self, u0, v0, u1, v1):
        self.rect(u0, v0, u1, v1)
        solid_poly([self(u0, v0), self(u1, v0), self(u1, v1), self(u0, v1)])


# Werkstoff-Schraffuren (Schnitt)
EICHE = dict(pattern="ANSI31", scale=0.45, angle=0.0)        # Vollholz
EICHE_Q = dict(pattern="ANSI31", scale=0.45, angle=90.0)     # Vollholz, andere Richtung
SPAN = dict(pattern="ANSI37", scale=0.35, angle=0.0)         # Spanplatte (Kreuzschraffur)
MPX = dict(pattern="ANSI32", scale=0.35, angle=0.0)          # Multiplex / MDF


def sheet_frame(x0):
    pline([(x0, 0), (x0 + 420, 0), (x0 + 420, 297), (x0, 297)], "Duenn", closed=True)
    pline([(x0 + 20, 10), (x0 + 410, 10), (x0 + 410, 287), (x0 + 20, 287)], "Rahmen", closed=True)


def title_block(x0, sheet, scale_txt, subtitle):
    TX, TY, TW, TH = x0 + 226, 10, 184, 51

    def tl(a, b, c, d):
        line((TX + a, TY + b), (TX + c, TY + d), "Schriftfeld")

    def tt(s, a, b, h=1.8):
        text(s, (TX + a, TY + b), h)

    pline([(TX, TY), (TX + TW, TY), (TX + TW, TY + TH), (TX, TY + TH)], "Rahmen", closed=True)
    tl(0, 33, TW, 33)
    tl(0, 17, TW, 17)
    for a in (46, 92, 138):
        tl(a, 0, a, 17)
    for a in (60, 108, 146):
        tl(a, 33, a, TH)
    tt("Werkstoff", 1, 48.2)
    tt("Eiche massiv, geölt", 2, 41.5, 2.2)
    tt("Spanplatte schwarz 19", 2, 37.5, 2.2)
    tt("Maßstab", 61, 48.2)
    tt(scale_txt, 63, 38.5, 3.5)
    tt("Maße in mm", 63, 35, 1.6)
    tt("Format / Blatt", 109, 48.2)
    tt(f"A3   {sheet}/2", 111, 38, 3.5)
    tt("Projektion", 147, 48.2)
    cx, cy = TX + 157, TY + 39.5
    pline([(cx, cy - 3), (cx + 11, cy - 4.5), (cx + 11, cy + 4.5), (cx, cy + 3)], "Duenn", closed=True)
    line((cx - 3, cy), (cx + 13, cy), "Mittellinie")
    msp.add_circle((cx + 21, cy), 4.5, dxfattribs={"layer": "Duenn"})
    msp.add_circle((cx + 21, cy), 3.0, dxfattribs={"layer": "Duenn"})
    tt("Benennung", 1, 30.2)
    tt("Mittelstufenprojekt – TOP SECRET 2.0", 2, 22.5, 4.2)
    tt(subtitle, 2, 18.7, 1.9)
    tt("Gezeichnet", 1, 14.2)
    tt("(Name)", 2, 5, 2.5)
    tt("Datum", 47, 14.2)
    tt("25.11.2026", 48, 5, 2.5)
    tt("Geprüft", 93, 14.2)
    tt("Zeichnungs-Nr.", 139, 14.2)
    tt(f"MSP-TS-0{sheet}", 140, 5, 3.5)


# ===========================================================================
# BLATT 1
# ===========================================================================
sheet_frame(0)
SC = 0.2

# ---------------------------------------------------------------- Vorderansicht
FV = View(36, 182, SC)
for cx in (0, BS):
    FV.rect(cx, 0, cx + BS, H)                                  # Eiche aussen
    FV.rect(cx + E, E, cx + BS - E, H - E)                      # Grenze Eiche/Spanplatte
    FV.rect(cx + EO, EO, cx + BS - EO, H - EO)                  # lichte Oeffnung
    for (a, b, c, d) in ((0, 0, E, E), (BS, 0, BS - E, E), (0, H, E, H - E), (BS, H, BS - E, H - E)):
        FV.seg(cx + a, b, cx + c, d, "Duenn")                   # Gehrungen Eichenrahmen
    for z0, z1 in FRONT_Z:
        FV.rect(cx + EO + F, z0, cx + EO + F + FB, z1)          # Fronten
    FV.seg(cx + BS / 2, -12, cx + BS / 2, H + 12, "Mittellinie")
FV.seg(-12, H / 2, B + 12, H / 2, "Mittellinie")
# Verbindungsschrauben (verdeckt): Achsen
for z in BOLT_Z:
    FV.seg(BS - E - P - 7, z, BS + 13, z, "Verdeckt")
text("Vorderansicht", (FV.ox, FV.oy + H * SC + 20), 3.5)
text("M 1:5", (FV.ox, FV.oy + H * SC + 15.8), 2.2)
# Schnittverlauf A-A bei x = 525
ax = BS + BS / 2
for v0, v1, va in ((H + 4, H + 30, H + 24), (-52, -80, -74)):
    FV.seg(ax, v0, ax, v1, "Schnittverlauf")
    p = FV(ax, va)
    line(p, (p[0] + 5.5, p[1]), "Bemassung")
    arrowhead((p[0] + 6, p[1]), p, 2.4)
    text("A", (p[0] + 2, p[1] + 1.2 if va > 0 else p[1] - 4.3), 3.5)
# Bemassung
top = FV.oy + H * SC
dim(FV(0, H), FV(B, H), (0, top + 12))
dim(FV(0, H), FV(BS, H), (0, top + 6))
dim(FV(BS, H), FV(B, H), (0, top + 6), loc=(FV(BS + 75, H)[0], top + 6.8))
dim(FV(0, 0), FV(0, H), (FV.ox - 15, 0), vertical=True)
dim(FV(0, 0), FV(0, EO), (FV.ox - 7, 0), vertical=True, loc=(FV.ox - 9, FV(0, EO / 2)[1] - 3))
dim(FV(0, EO), FV(0, H - EO), (FV.ox - 7, 0), vertical=True)
dim(FV(0, H - EO), FV(0, H), (FV.ox - 7, 0), vertical=True, loc=(FV.ox - 9, FV(0, H)[1] + 2.5))
xr = FV.ox + B * SC
for z0, z1 in FRONT_Z:
    dim(FV(B, z0), FV(B, z1), (xr + 6, 0), vertical=True)
yb = FV.oy - 7
dim(FV(BS + EO, 0), FV(B - EO, 0), (0, yb), "LW 272")
dim(FV(0, 0), FV(EO, 0), (0, yb), loc=(FV(0, 0)[0] - 3, yb + 0.8))
dim(FV(EO + F, 0), FV(EO + F + FB, 0), (0, yb - 6), "266")
leader(FV(B - EO - F / 2, 330), (xr - 6, top + 4), "Fuge 3 (G)", right=True)
balloon(FV(E / 2, 300), (FV.ox - 4.5, FV.oy + 62), 1)
balloon(FV(120, H - E / 2), (FV.ox + 26, top + 3.0), 2)
balloon(FV(E + P / 2, 120), (FV.ox + 9, FV.oy + 30), 3)
balloon(FV(EO + F + 140, FRONT_Z[1][0] + 100), (FV.ox + 40, FV.oy + 66), 6)
callout(FV(BS, BOLT_Z[0]), 7, "C", (FV(BS, BOLT_Z[0])[0] - 1.5, FV(BS, BOLT_Z[0])[1] - 12))

# ------------------------------------------------------- Seitenansicht von links
SV = View(214, 182, SC)
SV.rect(0, 0, TE, H)
SV.rect(TE, E, T, H - E)                                        # Spanplatte hinten 2 mm sichtbar
for v in (E, H - E):
    SV.seg(0, v, TE, v, "Verdeckt")
SV.seg(0, EO, LT, EO, "Verdeckt")
SV.seg(0, H - EO, LT, H - EO, "Verdeckt")
SV.rect(LT, EO - NUT, LT + RW, H - EO + NUT, "Verdeckt")
for z0, z1 in FRONT_Z:
    pline([SV(0, z0), SV(X, z0), SV(X, z1), SV(0, z1)], "Verdeckt")
SV.rect(LT + RW + 1, 300, T - 1, 358, "Verdeckt")             # Aufhaenger (schematisch)
SV.seg(-10, H / 2, T + 10, H / 2, "Mittellinie")
text("Seitenansicht von links", (SV.ox, SV.oy + H * SC + 20), 3.5)
text("M 1:5", (SV.ox, SV.oy + H * SC + 15.8), 2.2)
st = SV.oy + H * SC
dim(SV(0, H), SV(X, H), (0, st + 6))
dim(SV(X, H), SV(LT, H), (0, st + 6))
dim(SV(LT, H), SV(LT + RW, H), (0, st + 6), loc=(SV(LT + RW, H)[0] - 0.8, st + 10.5))
dim(SV(LT + RW, H), SV(T, H), (0, st + 6), loc=(SV(T, H)[0] + 3.6, st + 6.8))
dim(SV(0, 0), SV(T, 0), (0, SV.oy - 8))
dim(SV(0, 0), SV(TE, 0), (0, SV.oy - 14), "303 (Eiche)")
dim(SV(T, 0), SV(T, H), (SV.ox + T * SC + 7, 0), vertical=True)
balloon(SV(150, 120), (SV.ox + 20, SV.oy + 9), 1)

# ------------------------------------------------------------------ Schnitt A-A
AV = View(300, 182, SC)
cxr = BS                                                         # rechter Schrank
AV.cut(0, 0, TE, E, **EICHE)                                     # Eiche unten
AV.cut(0, H - E, TE, H, **EICHE)                                 # Eiche oben
AV.cut(0, E, T, EO, **SPAN)                                      # Spanplatte unten
AV.cut(0, H - EO, T, H - E, **SPAN)                              # Spanplatte oben
AV.black(LT, EO - NUT, LT + RW, H - EO + NUT)                    # Rueckwand
for (z0, z1), (sb, bt, stp) in zip(FRONT_Z, DRAW):
    AV.cut(0, z0, X, z1, **EICHE_Q)                              # Front
    AV.cut(X, sb, X + ZS, stp, **EICHE_Q)                        # Vorderstueck
    AV.cut(ISKL - ZS, bt, ISKL, stp, **EICHE_Q)                  # Hinterstueck
    AV.black(X + ZS - 5, bt - BD, ISKL, bt)                       # Boden
    AV.seg(X + ZS, stp, ISKL - ZS, stp)                          # Seite dahinter
    AV.seg(X + ZS, sb, ISKL, sb)
    AV.seg(ISKL, sb, ISKL, bt - BD)
    AV.rect(X, bt - 36, X + NL, bt - BD - NI, "Beschlag")         # MOVENTO (schematisch)
# Geheimfach im unteren Schubkasten
sb, bt, stp = DRAW[0]
AV.cut(X + ZS, bt, X + ZS + 10, bt + GF, **EICHE)
AV.cut(ISKL - ZS - 10, bt, ISKL - ZS, bt + GF, **EICHE)
AV.black(X + ZS + 1, bt + GF, ISKL - ZS - 1, bt + GF + EB)
# Aufhaenger + Schiene (dahinter, schematisch)
AV.rect(LT + RW + 1, 300, T - 1, 358, "Beschlag")
text("Schnitt A-A", (AV.ox, AV.oy + H * SC + 20), 3.5)
text("M 1:5", (AV.ox, AV.oy + H * SC + 15.8), 2.2)
at = AV.oy + H * SC
dim(AV(0, H), AV(ISKL, H), (0, at + 11.5), "ISKL 260 (H)")
dim(AV(X, H), AV(X + NL, H), (0, at + 6), "NL 250")
ab = AV.oy - 7
dim(AV(0, 0), AV(LT, 0), (0, ab), "281 (≥277 H)")
dim(AV(LT, 0), AV(LT + RW, 0), (0, ab), loc=(AV(LT + RW, 0)[0] - 1.3, ab - 4.3))
dim(AV(LT + RW, 0), AV(T, 0), (0, ab), "16 (H)", loc=(AV(T, 0)[0] + 5.5, ab + 0.8))
dim(AV(0, 0), AV(T, 0), (0, AV.oy - 14))
xa = AV.ox + T * SC
dim(AV(T, 0), AV(T, H), (xa + 21, 0), vertical=True)
dim(AV(T, EO), AV(T, DRAW[0][1]), (xa + 7, 0), "40", vertical=True)
dim(AV(T, DRAW[0][0]), AV(T, DRAW[0][2]), (xa + 14, 0), "110 (G)", vertical=True)
dim(AV(T, DRAW[1][2]), AV(T, H - EO), (xa + 7, 0), "33,5", vertical=True)
balloon(AV(60, H - E / 2), (AV.ox + 20, at + 3.2), 2)
balloon(AV(140, H - E - P / 2), (AV.ox + 35, at - 5.5), 4)
balloon(AV(LT + RW / 2, 120), (xa + 3.5, AV.oy + 30), 5)
balloon(AV(X / 2, FRONT_Z[1][0] + 60), (AV.ox - 5, AV.oy + 50), 6)
balloon(AV(150, DRAW[1][2]), (AV.ox + 30, AV.oy + 69), 7)
balloon(AV(X + ZS / 2, DRAW[1][2] - 30), (AV.ox - 5, AV.oy + 61), 8)
balloon(AV(ISKL - ZS / 2, DRAW[1][2] - 20), (AV.ox + 45, AV.oy + 61), 9)
balloon(AV(200, DRAW[1][1] - BD / 2), (AV.ox + 48, AV.oy + 48), 10)
balloon(AV(ISKL - ZS - 5, DRAW[0][1] + GF / 2), (AV.ox + 52, AV.oy + 21), 11)
balloon(AV(120, DRAW[0][1] + GF + EB / 2), (AV.ox + 30, AV.oy + 28), 12)
balloon(AV(100, DRAW[0][1] - 20), (AV.ox + 18, AV.oy + 2.8), 14)
balloon(AV(LT + RW + 8, 330), (xa + 12, at - 22), 16)
callout(AV(T - 10, 330), 7, "B", (xa + 1.5, AV(T, 330)[1] - 11))
callout(AV(130, DRAW[0][1] + 10), 8, "D", (AV(130, 0)[0] + 9, AV(0, DRAW[0][1])[1] + 2))

# ------------------------------------------------------------------- Draufsicht
TV = View(36, 96, SC, flip_from=T)                               # Front oben
for cx in (0, BS):
    TV.rect(cx, 0, cx + BS, TE)
    TV.rect(cx + E, TE, cx + BS - E, T)
    for x in (cx + E, cx + BS - E):
        TV.seg(x, 0, x, TE, "Verdeckt")
    for x in (cx + EO, cx + BS - EO):
        TV.seg(x, 0, x, LT, "Verdeckt")
    TV.seg(cx + EO, X, cx + BS - EO, X, "Verdeckt")
    TV.rect(cx + EO - NUT, LT, cx + BS - EO + NUT, LT + RW, "Verdeckt")
    TV.seg(cx + BS / 2, -10, cx + BS / 2, T + 10, "Mittellinie")
for y in BOLT_Y:
    TV.seg(BS - EO - 7, y, BS + 13, y, "Verdeckt")
text("Draufsicht", (TV.ox, TV.oy - 17), 3.5)
text("M 1:5", (TV.ox + 40, TV.oy - 17), 2.2)
dim(TV(0, T), TV(B, T), (0, TV.oy - 8))
dim(TV(0, 0), TV(0, T), (TV.ox - 8, 0), vertical=True)
dim(TV(B, 0), TV(B, BOLT_Y[0]), (TV.ox + B * SC + 6, 0), vertical=True, loc=(TV.ox + B * SC + 6, TV(0, 30)[1]))
dim(TV(B, BOLT_Y[0]), TV(B, BOLT_Y[1]), (TV.ox + B * SC + 6, 0), vertical=True)
leader(TV(BS + 6, BOLT_Y[1]), (TV.ox + 92, TV.oy + 22), "Verbindungsschrauben", right=True)
balloon(TV(200, 150), (TV.ox + 48, TV.oy + 33), 2)

# ------------------------------------------------- Hinweise / Pruefung (links unten)
NX, NY = 24, 74
text("Prüfung Beschläge und Einbautiefe", (NX, NY), 2.5)
notes = [
    "MOVENTO 760H2501T (NL 250, 40 kg, TIP-ON integriert) – Blum TD-132/1 DE/06.22, S. 3. NL 250 ist nicht mit",
    "TIP-ON BLUMOTION kombinierbar (S. 3) → mechanisches TIP-ON. Kupplung T51.7601 L/R separat bestellen.",
    "Innenschubkasten mit TIP-ON (S. 5): lichte Tiefe ≥ NL + X + 7 = 250 + 20 + 7 = 277. Gewählt 281 (4 Reserve).",
    "SKL = NL − 10 = 240; ISKL = SKL + X = 260; SKW = LW − 42 = 230 (+0/−1,5); Zarge max. 16; Nische 12–15;",
    "unter OK Boden min. 38 (+1 bei Montage vor Korpus-Zusammenbau); über Seite min. 7; Freiraum unter Boden 28,5.",
    "TIP-ON-Synchronisierung: empfohlen ab KB 600 (S. 18) → bei KB 350 nicht erforderlich.",
    "Häfele: verdeckter Oberschrank-Aufhänger hinter der Rückwand, Freiraum min. 16, 65 kg/Stk. (Produktseite",
    "haefele.de). Artikel-Nr., Aufhängerkontur, Schiene und Bohrbild n.f. – vor Fertigung mit Montageanleitung prüfen.",
    "Tiefe:  281 (lichte Tiefe) + 8 (Rückwand) + 16 (Freiraum Aufhänger) = 305.   Je Schrank 2 Aufhänger + eigene",
    "Schiene → beide Schränke einzeln aufhängbar, danach von innen mit 4 Schrauben M6 verbinden (Detail C).",
    "Eiche vorn fest, hinten in Langlöchern befestigt (Quellen/Schwinden quer zur Faser); Eiche hinten 2 kürzer.",
    "(H) Herstellerangabe   (G) gewählt   n.f. noch festzulegen / beim Hersteller bestätigen",
]
for i, s in enumerate(notes):
    text(s, (NX, NY - 5.0 - i * 4.4), 1.75)

KX, KY = 214, 150
text("Höhenplanung je Schrank (über UK Schrank)", (KX, KY), 2.3)
rows = [
    "Eiche 0–20 · Spanplatte 20–39 · lichte Höhe 39–361 (322)",
    f"Front unten 42–198,5 · Front oben 201,5–358 (je 156,5)",
    f"SK unten: Seite {DRAW[0][0]:.0f}–{DRAW[0][2]:.0f}, OK Boden {DRAW[0][1]:.0f}",
    f"SK oben: Seite {DRAW[1][0]:.1f}–{DRAW[1][2]:.1f}, OK Boden {DRAW[1][1]:.1f}".replace(".", ","),
    "Verbindungsschrauben z = 187 / 347, y = 60 / 220",
    "Geheimfach: SK unten, rechter Schrank (Detail D)",
]
for i, s in enumerate(rows):
    text(s, (KX, KY - 4.6 - i * 4.0), 1.75)

title_block(0, 1, "1:5", "2 Schränke à 350, je 2 Schubkästen, MOVENTO TIP-ON, Geheimfach")

# ===========================================================================
# BLATT 2
# ===========================================================================
X2 = 440
sheet_frame(X2)
title_block(X2, 2, "1:2 / 1:1", "Details B, C, D und Stückliste")

# ------------------------------------------- Detail D: Querschnitt unterer SK (1:2)
# Schnitt bei y = 60 (durch Stahlronde), Blick nach hinten, rechte Haelfte rechter Schrank
S2 = 0.5
u0 = B - BS / 2                                                  # 525 = Schrankmitte
DV = View(X2 + 40 - u0 * S2, 164, S2)
sb, bt, stp = DRAW[0]
xs_in = B - EO                                                   # 661 Korpusseite innen
xd_o = xs_in - 6                                                 # 655 Seite aussen
xd_i = xd_o - ZS                                                 # 640 Seite innen
vtop = stp + 10
DV.cut(B - E, 0, B, vtop, **EICHE_Q)                             # Eiche Seite
DV.cut(u0, 0, B - E, E, **EICHE)                                 # Eiche Boden
DV.cut(B - EO, E, B - E, vtop, **SPAN)                           # Spanplatte Seite
DV.cut(u0, E, B - EO, EO, **SPAN)                                # Spanplatte Boden
DV.cut(xd_i, sb, xd_o, stp, **EICHE_Q)                           # Schubkastenseite
DV.cut(u0, bt - BD, xd_i + 5, bt, **MPX)                         # Boden in Nut (5 tief)
DV.rect(u0, bt, xd_i, bt + GF, "Duenn")                          # Leiste hinten (dahinter)
DV.cut(u0, bt + GF, xd_i - 1, bt + GF + EB, **MPX)               # Einlegeboden, Fuge 1
DV.black(u0, bt + GF, u0 + 10, bt + GF + 2)                      # Stahlronde (halb)
runner = [(xd_i - 7, bt - BD), (xd_i, bt - BD), (xd_i, sb), (xd_o, sb), (xd_o, sb + 8),
          (xs_in, sb + 8), (xs_in, EO + 4), (xd_i - 7, EO + 4)]
pline([DV(*q) for q in runner], "Beschlag", closed=True)
for vv in (vtop,):
    DV.seg(B - EO, vv, B, vv, "Duenn")
DV.seg(u0, -6, u0, vtop + 8, "Mittellinie")
text("Detail D – doppelter Boden (Geheimfach)", (X2 + 24, 278), 3.0)
text("Schnitt unterer Schubkasten, rechter Schrank, bei y = 60 · M 1:2", (X2 + 24, 273.5), 1.9)
d_r = DV(B, 0)[0]
vt = DV(0, vtop)[1]
dim(DV(xd_i, vtop), DV(xs_in, vtop), (0, vt + 10), "21", ds="M2")
dim(DV(xd_i, vtop), DV(xd_o, vtop), (0, vt + 5), ds="M2")
dim(DV(xs_in, vtop), DV(B - E, vtop), (0, vt + 5), ds="M2")
dim(DV(B - E, vtop), DV(B, vtop), (0, vt + 5), ds="M2")
dim(DV(B, 0), DV(B, E), (d_r + 6, 0), vertical=True, ds="M2")
dim(DV(B, E), DV(B, EO), (d_r + 6, 0), vertical=True, ds="M2")
dim(DV(B, sb), DV(B, bt - BD), (d_r + 6, 0), vertical=True, ds="M2")
dim(DV(B, EO), DV(B, bt), (d_r + 13, 0), vertical=True, ds="M2")
dim(DV(B, sb), DV(B, stp), (d_r + 20, 0), vertical=True, ds="M2")
lx = DV(u0, 0)[0] - 4
dim(DV(u0, bt - BD), DV(u0, bt), (lx, 0), vertical=True, ds="M2", loc=(lx - 2, DV(0, bt - 7)[1]))
dim(DV(u0, bt), DV(u0, bt + GF), (lx, 0), vertical=True, ds="M2")
dim(DV(u0, bt + GF), DV(u0, bt + GF + EB), (lx, 0), vertical=True, ds="M2",
    loc=(lx - 2, DV(0, bt + GF + EB + 5)[1]))
dim(DV(u0, bt + GF + EB), DV(u0, stp), (lx - 8, 0), vertical=True, ds="M2")
leader(DV(u0 + 6, bt + GF + 1), (DV(u0, 0)[0] + 14, DV(0, bt - 28)[1]), "Stahlronde Ø20×2", right=True)
leader(DV(xd_i - 3, EO + 8), (DV(xd_i, 0)[0] - 30, DV(0, -10)[1]), "MOVENTO (Kontur schematisch)", right=False)
balloon(DV(xd_i + 7, stp - 25), (DV(xd_i, 0)[0] - 8, DV(0, stp - 5)[1]), 7)
balloon(DV(600, bt - BD / 2), (DV(600, 0)[0] - 4, DV(0, bt - 20)[1]), 10)
balloon(DV(570, bt + GF / 2), (DV(570, 0)[0] - 3, DV(0, bt + GF + 22)[1]), 11)
balloon(DV(610, bt + GF + EB / 2), (DV(610, 0)[0] + 2, DV(0, bt + GF + 30)[1]), 12)
balloon(DV(B - E / 2, 140), (d_r + 4, DV(0, 150)[1] + 2), 1)
balloon(DV(B - EO + P / 2, 120), (d_r + 11, DV(0, 120)[1]), 3)
dn = [
    "Maße: 21 / Zarge max. 16 / Nische 12–15 / unter OK Boden min. 38 (H, Blum S. 5);",
    "Zarge 15, Nische 13, Boden 8, Geheimfach 18, Einlegeboden 6, Seite 110 (G).",
    "Freiraum unter dem Boden min. 28,5 ab Korpusseite (H) – nicht verbauen.",
    "Funktion: Der echte Boden (10) bleibt in der Blum-Lage, MOVENTO und TIP-ON",
    "arbeiten unverändert (Tragkraft 40 kg). Der Einlegeboden (12) liegt lose auf",
    "2 Leisten (11) an Vorder- und Hinterstück, Fuge 1 umlaufend. Öffnen: Magnet (13)",
    "über der Ronde aufsetzen, Boden vorn anheben und herausnehmen.",
]
for i, s_ in enumerate(dn):
    text(s_, (X2 + 24, 148 - i * 3.8), 1.7)

# ------------------------------------------- Detail B: Haefele-Aufhaengung (1:2)
# Schnitt bei x = Schrank + 41 (durch Aufhaenger), Blick von links; u = y, v = z
yb0 = 215
BV = View(X2 + 182 - yb0 * S2, 195 - 285 * S2, S2)
BV.cut(yb0, H - E, TE, H, **EICHE)
BV.cut(yb0, H - EO, T, H - E, **SPAN)
BV.cut(LT, 285, LT + RW, H - EO + NUT, **MPX)                    # Rueckwand in Nut
BV.seg(T, 285, T, H + 8)
hatch_poly([BV(T, 285), BV(T + 10, 285), BV(T + 10, H + 8), BV(T, H + 8)], "AR-CONC", 0.05)
hang = [(LT + RW + 1, 300), (T - 4, 300), (T - 4, 338), (T - 1, 338), (T - 1, 352), (LT + RW + 1, 352)]
pline([BV(*q) for q in hang], "Beschlag", closed=True)
pline([BV(T, 342), BV(T - 3, 342), BV(T - 3, 334), BV(T - 2, 334), BV(T - 2, 341), BV(T, 341)], "Beschlag")
BV.seg(yb0, DRAW[1][2], ISKL, DRAW[1][2], "Duenn")              # obere Schubkastenseite
BV.seg(ISKL, DRAW[1][2], ISKL, 285, "Duenn")
text("Detail B – Häfele-Aufhängung", (X2 + 165, 278), 3.0)
text("Schnitt durch Aufhänger, Blick von links · M 1:2", (X2 + 165, 273.5), 1.9)
bt_ = BV(0, H)[1]
dim(BV(LT, H), BV(LT + RW, H), (0, bt_ + 5), ds="M2", loc=(BV(LT, H)[0] - 2.5, bt_ + 5.8))
dim(BV(LT + RW, H), BV(T, H), (0, bt_ + 5), "min 16", ds="M2", loc=(BV(T, H)[0] + 6, bt_ + 5.8))
dim(BV(TE, H), BV(T, H), (0, bt_ + 12), ds="M2", loc=(BV(T, H)[0] + 3, bt_ + 12.8))
dim(BV(yb0, H - EO - NUT + NUT), BV(yb0, H - EO + NUT), (BV(yb0, 0)[0] - 4, 0), "8", vertical=True,
    ds="M2", loc=(BV(yb0, 0)[0] - 6, BV(0, H - EO - 5)[1]))
dim(BV(yb0, H - EO), BV(yb0, H - E), (BV(yb0, 0)[0] - 12, 0), vertical=True, ds="M2")
dim(BV(yb0, H - E), BV(yb0, H), (BV(yb0, 0)[0] - 12, 0), vertical=True, ds="M2")
wx = BV(T + 10, 0)[0]
leader(BV(T - 8, 312), (wx + 4, BV(0, 305)[1]), "Aufhänger (16)", right=True)
leader(BV(T - 2.5, 337), (wx + 4, BV(0, 328)[1]), "Schiene (17)", right=True)
leader(BV(T + 6, 292), (wx + 4, BV(0, 290)[1]), "Wand", right=True)
balloon(BV(LT + RW / 2, 300), (BV(LT, 0)[0] - 10, BV(0, 296)[1]), 5)
balloon(BV(250, H - E - P / 2), (BV(250, 0)[0], bt_ + 6), 4)
bn = [
    "Je Schrank 1 Paar (L/R) oben hinten an der",
    "Spanplattenseite (3) verschraubt, eigene Schiene",
    "je Schrank. Häfele (H): Montage hinter der Rück-",
    "wand, Freiraum min. 16, 65 kg/Stk., Einstellung",
    "von vorn. Aufhängerkontur, Bohrbild, Art.-Nr.",
    "(z. B. 290.21.90x) und Schiene: n.f. – lt.",
    "Häfele-Montageanleitung. Zugang: SK oben ausbauen.",
]
for i, s_ in enumerate(bn):
    text(s_, (X2 + 165, 180 - i * 3.8), 1.7)

# ------------------------------------------- Detail C: Verbindung (1:1), Schnitt z = 187
S1 = 1.0
ua, ub = 305, 395
yc1 = 75
CV = View(X2 + 308 - ua * S1, 262, S1, flip_from=0)              # Front oben
CV.cut(BS - E, 0, BS, yc1, **EICHE_Q)                            # Eiche A
CV.cut(BS, 0, BS + E, yc1, **EICHE)                              # Eiche B
CV.cut(BS - EO, 0, BS - E, yc1, **SPAN)                          # Span A
CV.cut(BS + E, 0, BS + EO, yc1, **SPAN)                          # Span B
CV.cut(ua, 0, BS - EO - F, X, **EICHE_Q)                         # Front A
CV.cut(BS + EO + F, 0, ub, X, **EICHE_Q)                         # Front B
for u in (ua, ub):
    pass
yb_ = BOLT_Y[0]
CV.rect(BS - EO - 7.6, yb_ - 5, BS - EO - 1.6, yb_ + 5, "Beschlag")     # Kopf ISO 4762
CV.rect(BS - EO - 1.6, yb_ - 6, BS - EO, yb_ + 6, "Beschlag")           # Scheibe
CV.rect(BS - EO, yb_ - 3, BS - EO + 48.4, yb_ + 3, "Beschlag")          # Schaft
CV.rect(BS, yb_ - 4.5, BS + 13, yb_ + 4.5, "Beschlag")                  # Muffe (Kontur n.f.)
for (xa_, xb_, r) in ((BS - EO, BS - E, 3.5), (BS - E, BS, 4.5)):
    CV.seg(xa_, yb_ - r, xb_, yb_ - r, "Duenn")
    CV.seg(xa_, yb_ + r, xb_, yb_ + r, "Duenn")
CV.seg(BS - EO - 12, yb_, BS + 18, yb_, "Mittellinie")
text("Detail C – Verbindung beider Schränke", (X2 + 300, 278), 3.0)
text("Waagrechter Schnitt bei z = 187 · M 1:1", (X2 + 300, 273.5), 1.9)
cy0 = CV(0, 0)[1]
dim(CV(BS - EO - F, 0), CV(BS - EO, 0), (0, cy0 + 4), "3", ds="M1", loc=(CV(BS - EO - F, 0)[0] - 3, cy0 + 4.8))
for a_, b_ in ((BS - EO, BS - E), (BS - E, BS), (BS, BS + E), (BS + E, BS + EO)):
    dim(CV(a_, 0), CV(b_, 0), (0, cy0 + 4), ds="M1")
dim(CV(BS + EO, 0), CV(BS + EO + F, 0), (0, cy0 + 4), "3", ds="M1", loc=(CV(BS + EO + F, 0)[0] + 3, cy0 + 4.8))
dim(CV(ub, 0), CV(ub, yb_), (CV(ub, 0)[0] + 4, 0), vertical=True, ds="M1")
dim(CV(BS - EO - 7.6, yc1), CV(BS - EO + 48.4 - 1.6, yc1), (0, CV(0, yc1)[1] - 9), "M6×50", ds="M1")
cl = CV(0, yc1)[1] - 16
leader(CV(BS - EO - 5, yb_ + 5), (CV(BS - EO - 5, 0)[0] - 2, cl), "ISO 4762 + Scheibe (18)", right=False)
leader(CV(BS - EO + 9, yb_ + 3.5), (CV(BS - EO + 9, 0)[0] - 2, cl - 5), "Bohrung Ø7", right=False)
leader(CV(BS - E + 10, yb_ + 4.5), (CV(BS - E + 10, 0)[0] + 2, cl - 10), "Bohrung Ø9 (Bewegung Eiche)", right=True)
leader(CV(BS + 8, yb_ + 4.5), (CV(BS + 8, 0)[0] + 2, cl), "Einschraubmuffe M6 (19)", right=True)
text("Schrank A", (CV(ua, 0)[0], CV(0, yc1)[1] - 4.5), 2.0)
text("Schrank B", (CV(ub, 0)[0], CV(0, yc1)[1] - 4.5), 2.0, align="BOTTOM_RIGHT")
cn = [
    "4 Verbindungen je Fuge: z = 187 / 347, y = 60 / 220 (G),",
    "außerhalb der Schubkasten-Hüllflächen (Kopf + Scheibe 7,6).",
    "Bohrung für Muffe lt. Muffenhersteller (n.f.). Montage nach",
    "dem Aufhängen beider Schränke; SK von Schrank A ausbauen.",
]
for i, s_ in enumerate(cn):
    text(s_, (X2 + 300, 150 - i * 3.8), 1.7)

# ------------------------------------------------------------------ Stueckliste
LX, LY = X2 + 22, 12
cols = [0, 7, 14, 72, 112, 172, 200]
hdr = ["Pos", "Stk", "Benennung", "Maße L × B × D", "Werkstoff / Art.-Nr.", "Stat."]
parts = [
    ("1", "4", "Seite außen (Rahmen)", "400 × 303 × 20", "Eiche massiv, geölt", "V/G"),
    ("2", "4", "Ober-/Unterboden außen", "350 × 303 × 20", "Eiche massiv, geölt", "V/G"),
    ("3", "4", "Seite Innenkorpus", "360 × 305 × 19", "Spanplatte schwarz", "V"),
    ("4", "4", "Ober-/Unterboden Innenkorpus", "272 × 305 × 19", "Spanplatte schwarz", "V"),
    ("5", "2", "Rückwand in Nut 8 × 8", "286 × 336 × 8", "MDF schwarz", "G"),
    ("6", "4", "Schubkastenfront, grifflos", "266 × 156,5 × 20", "Eiche massiv, geölt", "V"),
    ("7", "8", "Schubkastenseite", "240 × 110 × 15", "Eiche massiv", "H/G"),
    ("8", "4", "Vorderstück", "230 × 110 × 15", "Eiche massiv", "G"),
    ("9", "4", "Hinterstück", "230 × 89 × 15", "Eiche massiv", "G"),
    ("10", "4", "Schubkastenboden in Nut", "240 × 230 × 8", "Multiplex", "G"),
    ("11", "2", "Auflageleiste Geheimfach", "230 × 18 × 10", "Eiche massiv", "G"),
    ("12", "1", "Einlegeboden (dopp. Boden)", "228 × 208 × 6", "Multiplex", "G"),
    ("13", "1+1", "Stahlronde / Magnet (Schlüssel)", "Ø20 × 2", "Stahl / Neodym", "G"),
    ("14", "4 Pa", "MOVENTO TIP-ON, NL 250, 40 kg", "NL 250", "Blum 760H2501T", "H"),
    ("15", "4 Pa", "Kupplung links/rechts", "–", "Blum T51.7601", "H"),
    ("16", "4", "Schrankaufhänger verdeckt (L/R)", "lt. Häfele", "Häfele, Art.-Nr. n.f.", "n.f."),
    ("17", "2", "Aufhängeschiene / Wandhaken", "Länge n.f.", "Häfele, n.f.", "n.f."),
    ("18", "4", "Zylinderschraube + Scheibe", "M6 × 50", "ISO 4762 / ISO 7089", "G"),
    ("19", "4", "Einschraubmuffe Hartholz", "M6", "Hersteller n.f.", "n.f."),
    ("20", "n.f.", "Holzdübel Innenkorpus", "Ø8 × 35", "Buche", "G"),
    ("21", "n.f.", "Flachdübel Gehrung Eiche", "Gr. 20", "Lamello", "G"),
    ("22", "n.f.", "Senkkopfschr. Eiche/Span, Front", "4 × 30 / 4 × 25", "Stahl verzinkt", "G"),
    ("23", "n.f.", "Schrauben Führung", "Ø3,5×15 / Ø6×14,5", "Blum 609.1500 / 661.1450.HG", "H"),
]
RH = 4.3
n = len(parts) + 1
W = cols[-1]
pline([(LX, LY), (LX + W, LY), (LX + W, LY + n * RH), (LX, LY + n * RH)], "Schriftfeld", closed=True)
for i in range(1, n):
    line((LX, LY + i * RH), (LX + W, LY + i * RH), "Duenn")
for c in cols[1:-1]:
    line((LX + c, LY), (LX + c, LY + n * RH), "Duenn")
for c, s in zip(cols, hdr):
    text(s, (LX + c + 0.8, LY + (n - 1) * RH + 1.2), 1.7)
for r, row in enumerate(reversed(parts)):
    for c, s in zip(cols, row):
        text(s, (LX + c + 0.8, LY + r * RH + 1.2), 1.6)
text("Stückliste (für beide Schränke)", (LX, LY + n * RH + 2), 2.5)

# ------------------------------------------------------- Quellen (rechts mitte)
QX, QY = X2 + 226, 124
text("Quellen / Statusangaben", (QX, QY), 2.3)
qs = [
    "V = vorgegeben, H = Herstellerangabe, G = gewählt, n.f. = noch festzulegen",
    "Blum: Technische Dokumentation MOVENTO TD-132/1 DE/06.22, S. 3, 5, 13, 18",
    "Häfele: Produktseiten Schrankaufhänger Oberschrank (haefele.de) – Werte aus",
    "Suchergebnis, Seite selbst nicht abrufbar → vor Bestellung bestätigen",
    "Eckverbindungen: Eiche Gehrung + Flachdübel (alternativ Zinken),",
    "Innenkorpus gedübelt, Schubkasten gedübelt oder gezinkt (G)",
    "Spanplatten-Vorderkanten schwarz bekantet, Dicke n.f.",
]
for i, s in enumerate(qs):
    text(s, (QX, QY - 4.6 - i * 4.0), 1.7)

out = sys.argv[1] if len(sys.argv) > 1 else "TopSecret_Schubkastenschrank.dxf"
doc.saveas(out)
print("geschrieben:", out)
