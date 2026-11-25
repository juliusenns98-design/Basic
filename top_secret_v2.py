"""Mittelstufenprojekt TOP SECRET 2.0 - Fertigungs- und Entwurfszeichnung (Stand 25.11.2026).

Grundlage: TopSecret_Konstruktionsdaten.md
Drei A3-Blaetter (quer) nebeneinander im Modellbereich:
  Blatt 1 (x    0): Ansichten M 1:10 (Projektionsmethode 1), Stueckliste, Pruefung
  Blatt 2 (x  440): Schnitt A-A M 1:1 (unterbrochen), Detail C Aufhaengung M 1:1
  Blatt 3 (x  880): Schnitt B-B M 1:1 (unterbrochen), Detail D Fingerzinken M 1:1,
                    Detail E Gehrung Eichenmantel M 1:1

Moebelkoordinaten (mm): x Breite 0..700 (links->rechts), y Tiefe 0..315 (vorn->Wand),
z Hoehe 0..400.  Status in der Zeichnung: (H) Hersteller, (G) gewaehlt, n.f. offen.

Aufruf:  python3 top_secret_v2.py  ->  TopSecret_v2.dxf
"""
import math
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment

# ---------------------------------------------------------------------------
# Masse
# ---------------------------------------------------------------------------
B, H, T = 700, 400, 315
E, P, K = 20, 19, 2              # Eiche, Spanplatte, ABS-Kante
TE = T - 2                       # Eiche 313
KB = 330                         # Innenkorpus-Breite
CX = [E, E + KB]                 # Korpus A / B aussen links
LW, LH = KB - 2 * P, 400 - 2 * (E + P)      # 292 / 322
EO = E + P                       # 39
NL, X = 250, 20
LT = 281                         # lichte Tiefe (min NL + X + 7 = 277)
RW = 3                           # Rueckwand HDF
NUT = 8                          # Nuttiefe Rueckwand
AL_D, AL_H = 19, 80              # Aufhaengeleiste
YR0, YR1 = LT, LT + RW           # 281..284
YL0, YL1 = YR1, YR1 + AL_D       # 284..303
F = 3                            # Fuge
FB = LW - 2 * F                  # 286
FH = (LH - 3 * F) / 2            # 156,5
FZ = [(EO + F, EO + F + FH), (EO + 2 * F + FH, EO + 2 * F + 2 * FH)]
ZS, BD, NI, HS = 16, 19, 13, 140  # Zarge, Boden, Nische, Seitenhoehe
SKL = NL - 10                    # 240
SKW = LW - 42                    # 250
GAP = (LW - SKW - 2 * ZS) / 2    # 5
BT = [FZ[0][0] + 37, FZ[1][0] + 37]          # OK Boden: 79 / 238,5
SB = [b - BD - NI for b in BT]               # UK Seite: 47 / 206,5
ST = [s + HS for s in SB]                    # OK Seite: 187 / 346,5
VH = HS - BD - NI                            # Vorder-/Hinterstueck 108
NF = 7
FP = VH / NF                                 # Fingerteilung 15,43
GF, LS = 25, 10                              # Geheimfach-Hoehe, Leistendicke
RAIL_T = 12                                  # Spalt fuer 2 Schienen

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
for name, (col, lw, lt) in {
    "Rahmen": (7, 70, "Continuous"), "Kontur": (7, 50, "Continuous"),
    "Duenn": (8, 25, "Continuous"), "Verdeckt": (6, 25, "ISO_VERDECKT"),
    "Mittellinie": (1, 25, "ISO_STRICHPUNKT"), "Schnittverlauf": (1, 70, "Continuous"),
    "Schraffur": (8, 18, "Continuous"), "Bemassung": (3, 25, "Continuous"),
    "Text": (7, 25, "Continuous"), "Schriftfeld": (7, 35, "Continuous"),
    "Beschlag": (4, 35, "Continuous"),
}.items():
    doc.layers.add(name, color=col, lineweight=lw, linetype=lt)
doc.styles.add("ISO", font="isocpeur.ttf")


def make_ds(name, lfac):
    ds = doc.dimstyles.new(name)
    for k, v in dict(dimtxt=2.5, dimtxsty="ISO", dimtsz=1.2, dimasz=2.0, dimexo=1.0, dimexe=1.5,
                     dimgap=0.8, dimtad=1, dimtih=0, dimtoh=0, dimdec=1, dimzin=8, dimlfac=lfac,
                     dimdsep=ord(","), dimclrd=3, dimclre=3, dimclrt=7).items():
        setattr(ds.dxf, k, v)


make_ds("M10", 10.0)
make_ds("M1", 1.0)


def clean(s):
    for a, b in (("≥", "min. "), ("≤", "max. "), (" → ", ": "), ("−", "-"), ("Ø", "%%c")):
        s = s.replace(a, b)
    return s


def line(p, q, layer="Kontur"):
    msp.add_line(p, q, dxfattribs={"layer": layer})


def pline(pts, layer="Kontur", closed=False):
    msp.add_lwpolyline(pts, format="xy", close=closed, dxfattribs={"layer": layer})


def text(s, p, h=2.5, align="LEFT", layer="Text", rot=0):
    t = msp.add_text(clean(s), height=h, rotation=rot, dxfattribs={"layer": layer, "style": "ISO"})
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


def leader(target, knee, label, h=1.9, right=True, arrow=True):
    end = (knee[0] + (4 if right else -4), knee[1])
    pline([target, knee, end], "Bemassung")
    (arrowhead(target, knee) if arrow else dot(target))
    if right:
        text(label, (end[0] + 0.8, end[1] - h / 2), h)
    else:
        text(label, (end[0] - 0.8, end[1] - h / 2), h, align="BOTTOM_RIGHT")


def balloon(target, center, n, r=2.8):
    msp.add_circle(center, r, dxfattribs={"layer": "Bemassung"})
    text(str(n), center, 2.3 if n < 10 else 2.0, align="MIDDLE_CENTER")
    dx, dy = target[0] - center[0], target[1] - center[1]
    d = math.hypot(dx, dy)
    line((center[0] + dx / d * r, center[1] + dy / d * r), target, "Bemassung")
    dot(target)


def dim(p1, p2, base, txt="<>", vertical=False, loc=None, ds="M1"):
    d = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=90 if vertical else 0, text=clean(txt),
                           location=loc, dimstyle=ds, dxfattribs={"layer": "Bemassung"})
    d.render()


def hatch_poly(pts, pattern, scale, angle=0.0, solid=False):
    h = msp.add_hatch(color=7 if solid else 256, dxfattribs={"layer": "Schraffur"})
    if not solid:
        h.set_pattern_fill(pattern, scale=scale, angle=angle)
    h.paths.add_polyline_path(pts, is_closed=True)


def zigzag(p, q, n=None):
    """Duenne Bruchlinie (Freihand) von p nach q."""
    L = math.hypot(q[0] - p[0], q[1] - p[1])
    n = n or max(4, int(L / 4))
    ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L
    nx, ny = -uy, ux
    pts = []
    for i in range(n + 1):
        t = i / n
        off = 1.0 * math.sin(t * math.pi * n / 2)
        pts.append((p[0] + ux * L * t + nx * off, p[1] + uy * L * t + ny * off))
    msp.add_spline(pts, dxfattribs={"layer": "Duenn"})


# Werkstoffe (Schnitt)
EI = ("ANSI31", 1.2, 0.0)        # Eiche (Vollholz)
EIQ = ("ANSI31", 1.2, 90.0)      # Eiche, andere Richtung
SP = ("ANSI37", 0.9, 0.0)        # Spanplatte
EI5 = ("ANSI31", 0.45, 0.0)      # 1:10
SP5 = ("ANSI37", 0.35, 0.0)


class View:
    """Abbildung Moebel (u, v) -> Blatt, optional unterbrochen.

    uw: Liste (u0, u1) sichtbarer Bereiche in u; zwischen ihnen Luecke `gap` auf dem Blatt.
    vw: (v0, v1) sichtbarer Bereich in v.  flip: v nach unten.
    """

    def __init__(self, ox, oy, s, uw=None, vw=None, gap=10.0, flip=False):
        self.ox, self.oy, self.s, self.gap, self.flip = ox, oy, s, gap, flip
        self.uw = uw or [(-1e9, 1e9)]
        self.vw = vw or (-1e9, 1e9)
        self.ustart = []
        pos = 0.0
        for i, (a, b) in enumerate(self.uw):
            self.ustart.append(pos)
            if b < 1e8:
                pos += (b - a) * s + gap

    def __call__(self, u, v):
        for i, (a, b) in enumerate(self.uw):
            if u <= b + 1e-9 or i == len(self.uw) - 1:
                base_u = self.uw[0][0] if self.uw[0][0] > -1e8 else 0.0
                if i == 0:
                    pu = (u - base_u) * self.s if self.uw[0][0] > -1e8 else u * self.s
                else:
                    pu = self.ustart[i] + (u - a) * self.s
                break
        vb = self.vw[0] if self.vw[0] > -1e8 else 0.0
        pv = (-(v - vb) if self.flip else (v - vb)) * self.s
        return (self.ox + pu, self.oy + pv)

    def _clip(self, u0, v0, u1, v1):
        out = []
        u0, u1 = min(u0, u1), max(u0, u1)
        v0, v1 = min(v0, v1), max(v0, v1)
        cv0, cv1 = max(v0, self.vw[0]), min(v1, self.vw[1])
        if cv1 <= cv0:
            return out
        for (a, b) in self.uw:
            cu0, cu1 = max(u0, a), min(u1, b)
            if cu1 > cu0:
                out.append((cu0, cv0, cu1, cv1, cu0 > u0, cv0 > v0, cu1 < u1, cv1 < v1))
        return out

    def rect(self, u0, v0, u1, v1, layer="Kontur", hatch=None, solid=False):
        for cu0, cv0, cu1, cv1, cl, cb, cr, ct in self._clip(u0, v0, u1, v1):
            P_ = [self(cu0, cv0), self(cu1, cv0), self(cu1, cv1), self(cu0, cv1)]
            if hatch or solid:
                hatch_poly(P_, *(hatch or ("SOLID", 1, 0)), solid=solid)
            if not cb:
                line(P_[0], P_[1], layer)
            if not cr:
                line(P_[1], P_[2], layer)
            if not ct:
                line(P_[2], P_[3], layer)
            if not cl:
                line(P_[3], P_[0], layer)

    def seg(self, u0, v0, u1, v1, layer="Kontur"):
        # nur waagrecht/senkrecht, wird geclippt
        if abs(v0 - v1) < 1e-9:
            for cu0, cv0, cu1, cv1, *_ in self._clip(u0, v0 - 1e-6, u1, v0 + 1e-6):
                line(self(cu0, v0), self(cu1, v0), layer)
        elif abs(u0 - u1) < 1e-9:
            for cu0, cv0, cu1, cv1, *_ in self._clip(u0 - 1e-6, v0, u0 + 1e-6, v1):
                line(self(u0, cv0), self(u0, cv1), layer)
        else:
            line(self(u0, v0), self(u1, v1), layer)

    def poly(self, pts, layer="Beschlag", closed=True):
        pline([self(*q) for q in pts], layer, closed)

    def breaks(self):
        """Bruchlinien an den Fenstergrenzen."""
        v0, v1 = self.vw
        for i, (a, b) in enumerate(self.uw):
            if i > 0:
                zigzag(self(a, v0 - 3), self(a, v1 + 3))
            if i < len(self.uw) - 1:
                zigzag(self(b, v0 - 3), self(b, v1 + 3))


def sheet_frame(x0):
    pline([(x0, 0), (x0 + 420, 0), (x0 + 420, 297), (x0, 297)], "Duenn", closed=True)
    pline([(x0 + 20, 10), (x0 + 410, 10), (x0 + 410, 287), (x0 + 20, 287)], "Rahmen", closed=True)


def title_block(x0, sheet, nsheets, scale_txt, subtitle):
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
    tt(f"A3   {sheet}/{nsheets}", 111, 38, 3.5)
    tt("Projektion", 147, 48.2)
    cx, cy = TX + 157, TY + 39.5
    pline([(cx, cy - 3), (cx + 11, cy - 4.5), (cx + 11, cy + 4.5), (cx, cy + 3)], "Duenn", closed=True)
    line((cx - 3, cy), (cx + 13, cy), "Mittellinie")
    msp.add_circle((cx + 21, cy), 4.5, dxfattribs={"layer": "Duenn"})
    msp.add_circle((cx + 21, cy), 3.0, dxfattribs={"layer": "Duenn"})
    tt("Benennung", 1, 30.2)
    tt("Mittelstufenprojekt – TOP SECRET 2.0", 2, 22.5, 4.2)
    tt(subtitle, 2, 18.7, 1.9)
    tt("Name / Klasse", 1, 14.2)
    tt("(Name), (Klasse)", 2, 5, 2.3)
    tt("Ausbildungsbetrieb", 47, 14.2)
    tt("(Betrieb)", 48, 5, 2.3)
    tt("Datum", 93, 14.2)
    tt("25.11.2026", 94, 5, 2.3)
    tt("Zeichnungs-Nr.", 139, 14.2)
    tt(f"MSP-TS-2.{sheet}", 140, 5, 3.2)


def view_title(x, y, name, scale):
    text(name, (x, y), 3.5)
    text(scale, (x, y - 4.3), 2.2)


# Hilfsfunktionen Geometrie je Korpus
def inner_x(k):
    return CX[k] + P                    # lichte Seite links (39 / 369)


def box_x(k):
    xi = inner_x(k)
    return xi + GAP, xi + GAP + ZS, xi + GAP + ZS + SKW, xi + GAP + 2 * ZS + SKW   # 44,60,310,326


# ===========================================================================
# BLATT 1 – Ansichten 1:10, Stueckliste
# ===========================================================================
S10 = 0.1
X1 = 0
sheet_frame(X1)
title_block(X1, 1, 3, "1:10 / 1:1", "Ansichten, Detail E, Stückliste, Prüfung Beschläge")

FV = View(X1 + 42, 200, S10)
FV.rect(0, 0, B, H)
for (a, b, c, d) in ((0, 0, E, E), (B, 0, B - E, E), (0, H, E, H - E), (B, H, B - E, H - E)):
    FV.seg(a, b, c, d, "Duenn")                          # Gehrungen
FV.rect(E, E, B - E, H - E)                              # Grenze Eiche / Korpus
for k in (0, 1):
    xi = inner_x(k)
    FV.rect(xi, EO, xi + LW, H - EO)                     # Oeffnung
    for z0, z1 in FZ:
        FV.rect(xi + F, z0, xi + F + FB, z1)            # Doppel
FV.seg(B / 2, E, B / 2, H - E)                           # Fuge Korpus/Korpus
FV.seg(B / 2, -8, B / 2, H + 8, "Mittellinie")
FV.seg(-8, H / 2, B + 8, H / 2, "Mittellinie")
view_title(FV.ox, FV.oy + 40 + 28, "Vorderansicht", "M 1:10")
# Schnittverlauf A-A (x = 515), Blick von links
xa = inner_x(1) + LW / 2
for v0, v1, va in ((H + 160, H + 185, H + 180), (-100, -125, -120)):
    FV.seg(xa, (H + 3) if v0 > 0 else -3, xa, (H + 22) if v0 > 0 else -22, "Schnittverlauf")
    FV.seg(xa, v0, xa, v1, "Schnittverlauf")
    p = FV(xa, va)
    line(p, (p[0] + 4, p[1]), "Bemassung")
    arrowhead((p[0] + 4.5, p[1]), p, 2.0)
    text("A", (p[0] + 1.2, p[1] + 1.0 if va > 0 else p[1] - 3.8), 3.0)
t_ = FV.oy + 40
dim(FV(0, H), FV(B, H), (0, t_ + 11), ds="M10")
dim(FV(0, H), FV(EO, H), (0, t_ + 5), ds="M10", loc=(FV(0, H)[0] - 3, t_ + 5.8))
dim(FV(EO, H), FV(EO + LW, H), (0, t_ + 5), ds="M10")
dim(FV(EO + LW, H), FV(EO + LW + 2 * P, H), (0, t_ + 5), ds="M10", loc=(FV(B / 2, H)[0], t_ + 9.5))
dim(FV(B - EO - LW, H), FV(B - EO, H), (0, t_ + 5), ds="M10")
dim(FV(B - EO, H), FV(B, H), (0, t_ + 5), ds="M10", loc=(FV(B, H)[0] + 3, t_ + 5.8))
dim(FV(0, 0), FV(0, H), (FV.ox - 11, 0), vertical=True, ds="M10")
dim(FV(0, 0), FV(0, EO), (FV.ox - 5, 0), vertical=True, ds="M10", loc=(FV.ox - 6, FV(0, 0)[1] - 3))
dim(FV(0, EO), FV(0, H - EO), (FV.ox - 5, 0), vertical=True, ds="M10")
dim(FV(0, H - EO), FV(0, H), (FV.ox - 5, 0), vertical=True, ds="M10", loc=(FV.ox - 6, FV(0, H)[1] + 3))
xr = FV.ox + B * S10
for z0, z1 in FZ:
    dim(FV(B, z0), FV(B, z1), (xr + 5, 0), vertical=True, ds="M10")
dim(FV(inner_x(1) + F, 0), FV(inner_x(1) + F + FB, 0), (0, FV.oy - 5), ds="M10")
leader(FV(B - EO - 1.5, 330), (xr + 12, t_ + 2), "Fuge 3 (G)", right=True)
balloon(FV(E / 2, 250), (FV.ox - 3, FV.oy + 31), 1)
balloon(FV(200, H - E / 2), (FV.ox + 14, t_ + 3.5), 2)
balloon(FV(inner_x(0) + 100, FZ[1][0] + 90), (FV.ox + 22, FV.oy + 31), 8)
balloon(FV(E + P / 2, 120), (FV.ox + 4.5, FV.oy + 6), 4)

# Seitenansicht von links (u = y, v = z)
SV = View(X1 + 134, 200, S10)
SV.rect(0, 0, TE, H)
SV.rect(TE, E, T, H - E)
SV.seg(LT, EO - NUT, LT, H - EO + NUT, "Verdeckt")
SV.rect(YL0, H - EO - AL_H, YL1, H - EO, "Verdeckt")
SV.seg(-6, H / 2, T + 6, H / 2, "Mittellinie")
view_title(SV.ox, SV.oy + 68, "Seitenansicht von links", "M 1:10")
yb_ = 70                                                    # Schnitt B-B bei y = 70
for v0, v1, va in ((H + 160, H + 185, H + 180), (-100, -125, -120)):
    SV.seg(yb_, (H + 3) if v0 > 0 else -3, yb_, (H + 22) if v0 > 0 else -22, "Schnittverlauf")
    SV.seg(yb_, v0, yb_, v1, "Schnittverlauf")
    p = SV(yb_, va)
    line(p, (p[0] + 4, p[1]), "Bemassung")
    arrowhead((p[0] + 4.5, p[1]), p, 2.0)
    text("B", (p[0] + 1.2, p[1] + 1.0 if va > 0 else p[1] - 3.8), 3.0)
dim(SV(0, 0), SV(T, 0), (0, SV.oy - 6), ds="M10")
dim(SV(T, 0), SV(T, H), (SV.ox + T * S10 + 5, 0), vertical=True, ds="M10")
balloon(SV(150, 150), (SV.ox + 9, SV.oy + 8), 1)

# Draufsicht (u = x, v = y, Front oben)
TV = View(X1 + 42, 182, S10, flip=True)
TV.rect(0, 0, B, TE)
for k in (0, 1):
    TV.rect(CX[k], TE, CX[k] + KB, T)
TV.seg(B / 2, -6, B / 2, T + 6, "Mittellinie")
text("Draufsicht", (TV.ox, TV.oy - T * S10 - 12), 3.5)
text("M 1:10", (TV.ox + 32, TV.oy - T * S10 - 12), 2.2)
dim(TV(0, T), TV(B, T), (0, TV.oy - T * S10 - 5), ds="M10")
dim(TV(0, 0), TV(0, T), (TV.ox - 5, 0), vertical=True, ds="M10")
balloon(TV(450, 150), (TV.ox + 52, TV.oy - 8), 2)

# Pruefung / Hinweise links unten
NX, NY = 24, 128
text("Prüfung Beschläge, Maße, Vorgaben", (NX, NY), 2.5)
notes = [
    "Kantenlänge 700 + 400 + 315 = 1415 (max. 1500, V). Bewegliches Bauteil: 4 Schubkästen (V).",
    "Sichtbare handwerkliche Verbindung: Fingerzinken Hinterstück/Seite (Detail D, V).",
    "MOVENTO TIP-ON 760H2501T, NL 250, 40 kg (H; Handel z. T. 760H2500T), Kupplung T51.7601.",
    "Innenschubkasten mit TIP-ON: lichte Tiefe min. NL + X + 7 = 277 (H); vorhanden 281.",
    "SKL = NL - 10 = 240; ISKL = 260; SKW = LW - 42 = 250 (H); Zarge 16 = Maximum (H),",
    "Seiteneinstellung dann eingeschränkt: Schubkasten genau auf Breite fertigen.",
    "Unter OK Boden min. 38 (H): 40; über Seite min. 7 (H): 14,5; Nische 12-15 (H): 13.",
    "Synchronisierung nicht nötig (empfohlen ab KB 600, H). Quelle: Blum TD-132/1 DE/06.22.",
    "Aufhängung: 2 Häfele-Aufhängeschienen 290.09.910 ineinander (H: Stahl verzinkt,",
    "Lochabstand 25). Profil lt. Händler 29 × 5,5 × 1,75; Spalt 12 (G). Tragkraft",
    "für diese Nutzung ohne Herstellerangabe (n.f.) – reichlich verschrauben.",
    "Maserung: Seite links – Oberboden – Seite rechts aus einem Brett, umlaufend (G).",
    "Doppel: alle 4 aus einem Stück, Maserung waagrecht durchlaufend (G).",
    "Eiche vorn fest, hinten Langlöcher (Quellen/Schwinden); Eiche hinten 2 kürzer.",
    "(V) Vorgabe  (H) Herstellerangabe  (G) gewählt  n.f. noch festzulegen",
]
for i, s in enumerate(notes):
    text(s, (NX, NY - 4.6 - i * 3.9), 1.65)

# Stueckliste rechts
LX, LY = X1 + 222, 66
cols = [0, 7, 15, 66, 103, 157, 188]
hdr = ["Pos", "Stk", "Benennung", "L × B × D", "Werkstoff / Art.-Nr.", "Stat."]
parts = [
    ("1", "2", "Seite Eichenmantel", "400 × 313 × 20", "Eiche Vintage, geölt", "G"),
    ("2", "1", "Oberboden Eichenmantel", "700 × 313 × 20", "Eiche Vintage, geölt", "G"),
    ("3", "1", "Unterboden Eichenmantel", "700 × 313 × 20", "Eiche Vintage, geölt", "G"),
    ("4", "4", "Seite Innenkorpus", "360 × 313 × 19", "Spanpl. schwarz + Kante 2", "V/G"),
    ("5", "4", "Ober-/Unterboden Innenkorpus", "292 × 313 × 19", "Spanpl. schwarz + Kante 2", "V/G"),
    ("6", "2", "Rückwand in Nut 3 × 8", "306 × 336 × 3", "HDF schwarz", "G"),
    ("7", "2", "Aufhängeleiste", "292 × 80 × 19", "Spanplatte schwarz", "G"),
    ("8", "4", "Schubkastendoppel", "286 × 156,5 × 20", "Eiche Vintage, geölt", "G"),
    ("9", "8", "Schubkastenseite", "240 × 140 × 16", "Eiche (aus 18 geh.)", "H/G"),
    ("10", "4", "Vorderstück, gedübelt", "250 × 108 × 16", "Eiche", "G"),
    ("11", "4", "Hinterstück, Fingerzinken", "282 × 108 × 16", "Eiche", "G"),
    ("12", "4", "Schubkastenboden in Nut", "258 × 240 × 19", "Spanplatte schwarz", "G"),
    ("13", "2", "Leiste Geheimfach", "250 × 25 × 10", "Eiche", "G"),
    ("14", "1", "Einlegeboden (Geheimfach)", "248 × 206 × 19", "Spanplatte schwarz", "G"),
    ("15", "1+1", "Stahlscheibe / Magnet", "Ø20 × 2 / Ø20 × 5", "Stahl / Neodym", "G"),
    ("16", "4 Pa", "MOVENTO TIP-ON NL 250", "NL 250, 40 kg", "Blum 760H2501T", "H"),
    ("17", "4 Pa", "Kupplung links/rechts", "–", "Blum T51.7601", "H"),
    ("18", "4", "Aufhängeschiene, Stück", "ca. 280", "Häfele 290.09.910", "H/G"),
    ("19", "3 m", "ABS-Kante schwarz", "23 × 2", "ABS", "G"),
    ("20", "n.f.", "Flachdübel Gehrung", "Gr. 20", "Buche", "G"),
    ("21", "n.f.", "Holzdübel", "Ø8 × 35 / Ø6 × 30", "Buche", "G"),
    ("22", "n.f.", "Spanplattenschraube", "4 × 30", "Stahl verzinkt", "G"),
    ("23", "n.f.", "Schraube Führung", "Ø3,5 × 15", "Blum 609.1500", "H"),
    ("24", "–", "Wandbefestigung Schiene", "n.f.", "passend zur Wand", "n.f."),
]
RH = 3.9
n = len(parts) + 1
W_ = cols[-1]
pline([(LX, LY), (LX + W_, LY), (LX + W_, LY + n * RH), (LX, LY + n * RH)], "Schriftfeld", closed=True)
for i in range(1, n):
    line((LX, LY + i * RH), (LX + W_, LY + i * RH), "Duenn")
for c in cols[1:-1]:
    line((LX + c, LY), (LX + c, LY + n * RH), "Duenn")
for c, s in zip(cols, hdr):
    text(s, (LX + c + 0.7, LY + (n - 1) * RH + 1.1), 1.6)
for r, row in enumerate(reversed(parts)):
    for c, s in zip(cols, row):
        text(s, (LX + c + 0.7, LY + r * RH + 1.1), 1.5)
text("Stückliste", (LX, LY + n * RH + 2), 2.5)
text("Zeichnungssatz: Blatt 1 Ansichten 1:10 · Blatt 2 Schnitt A-A + Detail C 1:1 ·", (LX, 282), 1.8)
text("Blatt 3 Schnitt B-B + Detail D 1:1 · Detail E 1:1 hier · Isometrie MSP-TS-ISO", (LX, 278.5), 1.8)

# ===========================================================================
# BLATT 2 – Schnitt A-A 1:1 (unterbrochen), Detail C Aufhaengung 1:1
# ===========================================================================
X2 = 440
sheet_frame(X2)
title_block(X2, 2, 3, "1:1", "Schnitt A-A durch rechten Korpus, Detail C Aufhängung")
k = 1
xi = inner_x(k)
xs0, xs1, xs2, xs3 = box_x(k)
AV = View(X2 + 60, 66, 1.0, uw=[(0, 95), (205, T + 10)], vw=(0, 195), gap=8)
sb, bt, st = SB[0], BT[0], ST[0]
# Eiche Unterboden, Spanplatte Unterboden + Kante
AV.rect(0, 0, TE, E, hatch=EI)
AV.rect(K, E, T, EO, hatch=SP)
AV.rect(0, E, K, EO, solid=True)
# Nut Rueckwand im Korpusboden + Rueckwand
AV.rect(YR0, EO - NUT, YR1, 205, solid=True)
# Doppel unten (geschnitten) + Fuge
AV.rect(0, FZ[0][0], X, FZ[0][1], hatch=EIQ)
AV.rect(0, FZ[1][0], X, 210, hatch=EIQ)
# Schubkasten unten: Vorderstueck, Hinterstueck, Boden (geschnitten)
AV.rect(X, bt, X + ZS, st, hatch=EIQ)
AV.rect(SKL + X - ZS, bt, SKL + X, st, hatch=EIQ)
AV.rect(X, bt - BD, SKL + X, bt, hatch=SP)
# Seite dahinter (sichtbar): Oberkante und hintere Stirn unten
AV.seg(X + ZS, st, SKL + X - ZS, st)
AV.seg(SKL + X, sb, SKL + X, bt - BD)
AV.seg(X, sb, X, bt - BD)
# Geheimfach: Leisten, Einlegeboden, Stahlscheibe
AV.rect(X + ZS, bt, X + ZS + LS, bt + GF, hatch=EI)
AV.rect(SKL + X - ZS - LS, bt, SKL + X - ZS, bt + GF, hatch=EI)
y_e0, y_e1 = X + ZS + 1, SKL + X - ZS - 1
AV.rect(y_e0, bt + GF, 60, bt + GF + BD, hatch=SP)
AV.rect(80, bt + GF, y_e1, bt + GF + BD, hatch=SP)
AV.rect(60, bt + GF + 14, 80, bt + GF + BD, hatch=SP)            # Restdicke 3 ueber Bohrung
AV.rect(60, bt + GF + 14, 80, bt + GF + 16, solid=True)          # Stahlscheibe 2
AV.seg(60, bt + GF, 60, bt + GF + 14)
AV.seg(80, bt + GF, 80, bt + GF + 14)
# MOVENTO (dahinter, schematisch) und Kupplung
AV.rect(X, bt - 38 + 2, X + NL, sb, "Beschlag")
AV.rect(X + 8, sb, X + 48, bt - BD, "Beschlag")
# obere Front / oberer SK nur angedeutet (ueber Bruch)
# Wand
AV.seg(T, 0, T, 195)
hatch_poly([AV(T, 0), AV(T + 10, 0), AV(T + 10, 195), AV(T, 195)], "AR-CONC", 0.05)
AV.breaks()
zigzag(AV(-2, 195), AV(95, 195))
zigzag(AV(205, 195), AV(T + 10, 195))
text("Schnitt A-A", (X2 + 24, 44), 3.5)
text("M 1:1 · Schnitt durch die Mitte des rechten Korpus (x = 515), unterer Schubkasten mit Geheimfach,",
     (X2 + 24, 39.5), 1.9)
text("Darstellung in der Tiefe unterbrochen (95…205 ausgelassen), oberhalb z = 195 siehe Detail C, Doppelhöhen Blatt 1.",
     (X2 + 24, 35.8), 1.9)
# Bemassung oben (Tiefe)
ytop = AV(0, 195)[1]
dim(AV(0, 195), AV(X, 195), (0, ytop + 6))
dim(AV(X, 195), AV(SKL + X, 195), (0, ytop + 6), "240 (H: NL-10)")
dim(AV(SKL + X, 195), AV(LT, 195), (0, ytop + 6))
dim(AV(LT, 195), AV(YR1, 195), (0, ytop + 6), loc=(AV(LT, 195)[0] - 0.5, ytop + 10.5))
dim(AV(YR1, 195), AV(YL1, 195), (0, ytop + 6), loc=(AV(YL1, 195)[0] - 4, ytop + 10.5))
dim(AV(YL1, 195), AV(T, 195), (0, ytop + 6), loc=(AV(T, 195)[0] + 3.5, ytop + 6.8))
dim(AV(0, 195), AV(LT, 195), (0, ytop + 14), "281 (min. 277 H)")
dim(AV(0, 195), AV(T, 195), (0, ytop + 21), "315")
dim(AV(X, sb), AV(X + NL, sb), (0, AV(0, 0)[1] - 6), "NL 250")
# Bemassung links (Hoehen)
xl = AV(0, 0)[0]
dim(AV(0, 0), AV(0, E), (xl - 6, 0), vertical=True)
dim(AV(0, E), AV(0, EO), (xl - 6, 0), vertical=True)
dim(AV(0, EO), AV(0, FZ[0][0]), (xl - 6, 0), vertical=True, loc=(xl - 7.5, AV(0, EO)[1] + 4))
dim(AV(0, EO), AV(0, bt), (xl - 15, 0), "40 (min. 38 H)", vertical=True)
# Bemassung im Schubkasten (rechts vom Fenster 1)
xm = AV(95, 0)[0] - 3
for (a, b, t) in ((sb, bt - BD, "13"), (bt - BD, bt, "19"), (bt, bt + GF, "25"),
                  (bt + GF, bt + GF + BD, "19"), (bt + GF + BD, st, "<>")):
    dim(AV(95, a), AV(95, b), (xm, 0), t, vertical=True)
dim(AV(T, sb), AV(T, st), (AV(T + 10, 0)[0] + 6, 0), "140", vertical=True)
dim(AV(T, bt), AV(T, st), (AV(T + 10, 0)[0] + 13, 0), "108", vertical=True)
dim(AV(60, bt + GF + BD), AV(80, bt + GF + BD), (0, AV(0, bt + GF + BD)[1] + 5), "Ø20")
dim(AV(X + ZS, bt + GF), AV(60, bt + GF), (0, AV(0, bt + GF)[1] - 4))
# Positionen
balloon(AV(150 / 2, E / 2), (AV(40, 0)[0], AV(0, 0)[1] - 13), 3)
balloon(AV(250, E + P / 2), (AV(250, 0)[0], AV(0, 0)[1] - 13), 5)
balloon(AV(X / 2, 120), (AV(0, 0)[0] - 30, AV(0, 120)[1]), 8)
balloon(AV(X + ZS / 2, 150), (AV(50, 0)[0], AV(0, 160)[1] + 8), 10)
balloon(AV(SKL + X - ZS / 2, 150), (AV(225, 0)[0], AV(0, 175)[1]), 11)
balloon(AV(230, bt - BD / 2), (AV(225, 0)[0] - 8, AV(0, bt - 30)[1]), 12)
balloon(AV(SKL + X - ZS - LS / 2, bt + 12), (AV(215, 0)[0], AV(0, bt + 50)[1]), 13)
balloon(AV(40, bt + GF + BD / 2), (AV(40, 0)[0], AV(0, 165)[1]), 14)
balloon(AV(70, bt + GF + 15), (AV(88, 0)[0], AV(0, 150)[1]), 15)
balloon(AV(250, bt - 30), (AV(260, 0)[0], AV(0, bt - 45)[1] - 2), 16)
balloon(AV(28, sb + 6), (AV(10, 0)[0] + 2, AV(0, sb + 22)[1]), 17)
balloon(AV(YR0 + 1.5, 120), (AV(T, 0)[0] - 12, AV(0, 120)[1]), 6)
balloon(AV(300, 30), (AV(258, 0)[0], AV(0, 0)[1] - 13), 4)

# Detail C – Aufhaengung (1:1), gleiche Blickrichtung, oben hinten
CV = View(X2 + 300, 138, 1.0, uw=[(240, T + 10)], vw=(270, H))
CV.rect(240, H - E, TE, H, hatch=EI)
CV.rect(240, H - EO, T, H - E, hatch=SP)
CV.rect(YR0, 270, YR1, H - EO + NUT, solid=True)
CV.rect(YL0, H - EO - AL_H, YL1, H - EO, hatch=SP)
# Hinterstueck oberer SK (geschnitten) + Seite
CV.rect(SKL + X - ZS, 270, SKL + X, ST[1], hatch=EIQ)
CV.seg(240, ST[1], SKL + X - ZS, ST[1])
# Schienen (schematisch, Haendlermasse 29 x 5,5)
yA, yW = YL1, T
CV.poly([(yA, 322), (yA + 1.75, 322), (yA + 1.75, 349.25), (yA + 5.5, 349.25), (yA + 5.5, 351),
         (yA, 351)])
CV.poly([(yW, 312), (yW - 1.75, 312), (yW - 1.75, 339.25), (yW - 5.5, 339.25), (yW - 5.5, 341),
         (yW, 341)])
CV.poly([(yA + 1.75, 349.25), (yA + 3.5, 349.25), (yA + 3.5, 337), (yA + 5.5, 337), (yA + 5.5, 349.25)],
        closed=False)
CV.seg(T, 270, T, H + 5)
hatch_poly([CV(T, 270), CV(T + 10, 270), CV(T + 10, H + 5), CV(T, H + 5)], "AR-CONC", 0.05)
zigzag(CV(240, 268), CV(T + 10, 268))
zigzag(CV(240, 268), CV(240, H + 2))
text("Detail C – Aufhängung", (X2 + 300, 282), 3.0)
text("Schnitt A-A oben hinten · M 1:1", (X2 + 300, 277.5), 1.9)
cyt = CV(0, H)[1]
dim(CV(YR0, H), CV(YR1, H), (0, cyt + 5), loc=(CV(YR0, H)[0] - 3, cyt + 5.8))
dim(CV(YR1, H), CV(YL1, H), (0, cyt + 5))
dim(CV(YL1, H), CV(T, H), (0, cyt + 5), "12 (G)", loc=(CV(T, H)[0] + 7, cyt + 5.8))
dim(CV(TE, H), CV(T, H), (0, cyt + 11), loc=(CV(T, H)[0] + 3, cyt + 11.8))
cxr = CV(T + 10, 0)[0]
dim(CV(T, H - EO - AL_H), CV(T, H - EO), (cxr + 5, 0), "80 (G)", vertical=True)
dim(CV(T, H - EO), CV(T, H - E), (cxr + 5, 0), vertical=True)
dim(CV(T, H - E), CV(T, H), (cxr + 5, 0), vertical=True)
dim(CV(240, ST[1]), CV(240, H - EO), (CV(240, 0)[0] - 5, 0), "14,5 (min. 7 H)", vertical=True)
dim(CV(240, H - EO), CV(240, H - EO + NUT), (CV(240, 0)[0] - 12, 0), "8", vertical=True,
    loc=(CV(240, 0)[0] - 13.5, CV(0, H - EO - 5)[1]))
leader(CV(yA + 1, 335), (X2 + 318, 129), "Schiene am Schrank (18)", right=True)
leader(CV(yW - 1, 320), (X2 + 324, 124), "Schiene an der Wand (18)", right=True)
balloon(CV(YL0 + 9, 300), (CV(255, 0)[0], CV(0, 300)[1]), 7)
balloon(CV(250, H - E / 2), (CV(255, 0)[0] - 6, cyt + 6), 2)
balloon(CV(270, H - E - P / 2), (CV(265, 0)[0] - 18, CV(0, H - 30)[1]), 5)
balloon(CV(YR0 + 1.5, 290), (CV(270, 0)[0], CV(0, 285)[1]), 6)
cn = [
    "Häfele-Aufhängeschiene 290.09.910 (H), 2 Stück ineinander.",
    "Kontur schematisch nach Händlermaßen 29 × 5,5 × 1,75",
    "(n.f., am Muster prüfen). Je Korpus ein Schienenpaar",
    "ca. 280 lang aus einer Schiene 1250 (Korpusseiten",
    "reichen bis zur Wand). Schrankschiene auf Aufhänge-",
    "leiste (7), Leiste mit Seiten und Oberboden verschraubt.",
    "Zum Einhängen ca. 15 anheben (n.f.).",
]
for i, s in enumerate(cn):
    text(s, (X2 + 292, 116 - i * 3.6), 1.65)

# ===========================================================================
# BLATT 3 – Schnitt B-B 1:1, Detail D Fingerzinken, Detail E Gehrung
# ===========================================================================
X3 = 880
sheet_frame(X3)
title_block(X3, 3, 3, "1:1", "Schnitt B-B, Detail D Fingerzinken")
BV = View(X3 + 52, 72, 1.0, uw=[(0, 100), (296, 404)], vw=(0, 190), gap=8)
yB = 70
# Eiche links + Unterboden
BV.rect(0, 0, E, 195, hatch=EIQ)
BV.rect(E, 0, B, E, hatch=EI)
for kk in (0, 1):
    xk = CX[kk]
    BV.rect(xk, E, xk + P, 195, hatch=SP)
    BV.rect(xk + KB - P, E, xk + KB, 195, hatch=SP)
    BV.rect(xk + P, E, xk + KB - P, EO, hatch=SP)
    a0, a1, a2, a3 = box_x(kk)
    BV.rect(a0, SB[0], a1, ST[0], hatch=EIQ)
    BV.rect(a2, SB[0], a3, ST[0], hatch=EIQ)
    BV.rect(a1 - 5, BT[0] - BD, a2 + 5, BT[0], hatch=SP)
    BV.rect(a1, BT[0], a2, ST[0], "Duenn")                      # Hinterstueck dahinter
    xi_ = inner_x(kk)
    for sgn, xw in ((1, xi_), (-1, xi_ + LW)):
        q = [(xw, BT[0] - 38 + 2), (xw + sgn * 28.5, BT[0] - 38 + 2), (xw + sgn * 28.5, BT[0] - BD),
             (xw + sgn * (GAP + ZS), BT[0] - BD), (xw + sgn * (GAP + ZS), SB[0]), (xw + sgn * GAP, SB[0]),
             (xw + sgn * GAP, BT[0] - 22), (xw, BT[0] - 22)]
        if all(BV.uw[0][0] <= u <= BV.uw[0][1] or BV.uw[1][0] <= u <= BV.uw[1][1] for u, _ in q):
            BV.poly(q)
# Geheimfach im rechten Korpus (Leiste hinten sichtbar, Einlegeboden geschnitten)
a0, a1, a2, a3 = box_x(1)
BV.rect(a1, BT[0], a2, BT[0] + GF, "Duenn")
BV.rect(a1 + 1, BT[0] + GF, a2 - 1, BT[0] + GF + BD, hatch=SP)
# Verbindung Korpus A/B: Spanplattenschraube 4 x 30 bei z = 120
zs_ = 120
BV.poly([(331, zs_ - 4), (331 - 0, zs_ + 4), (334, zs_ + 2), (361, zs_ + 2), (361, zs_ - 2), (334, zs_ - 2)])
# Eiche an Spanplatte: Schraube 4 x 30 bei z = 150 (vorn fest)
BV.poly([(39, 150 - 4), (39, 150 + 4), (36, 150 + 2), (9, 150 + 2), (9, 150 - 2), (36, 150 - 2)])
BV.breaks()
zigzag(BV(-2, 190), BV(100, 190))
zigzag(BV(296, 190), BV(404, 190))
text("Schnitt B-B", (X3 + 24, 44), 3.5)
text("M 1:1 · bei y = 70 (durch die Stahlscheibe), Blick nach hinten, untere Schubkästen, Breite unterbrochen",
     (X3 + 24, 39.5), 1.9)
text("(100…296 ausgelassen; Korpus A links, Korpus B rechts, Geheimfach in Korpus B).", (X3 + 24, 35.8), 1.9)
by = BV(0, 190)[1]
dim(BV(0, 190), BV(E, 190), (0, by + 6))
dim(BV(E, 190), BV(EO, 190), (0, by + 6))
dim(BV(EO, 190), BV(EO + GAP, 190), (0, by + 6), loc=(BV(EO + 2.5, 190)[0], by + 10.5))
dim(BV(EO + GAP, 190), BV(EO + GAP + ZS, 190), (0, by + 6))
dim(BV(EO, 190), BV(EO + 21, 190), (0, by + 13), "21 (H)")
dim(BV(EO, 190), BV(EO + 28.5, 190), (0, by + 20), "28,5 (H)")
for a_, b_ in ((310, 326), (326, 331), (331, 350), (350, 369), (369, 374), (374, 390)):
    dim(BV(a_, 190), BV(b_, 190), (0, by + 6),
        loc=(BV((a_ + b_) / 2, 190)[0], by + 10.5) if b_ - a_ < 8 else None)
dim(BV(331, 190), BV(369, 190), (0, by + 13), "38")
xl = BV(0, 0)[0]
for (a, b, t) in ((0, E, "<>"), (E, EO, "<>"), (EO, SB[0], "8"), (SB[0], BT[0] - BD, "13"),
                  (BT[0] - BD, BT[0], "<>"), (BT[0], ST[0], "108")):
    dim(BV(0, a), BV(0, b), (xl - 6, 0), t, vertical=True,
        loc=(xl - 7.5, BV(0, b)[1] + 3) if b - a < 10 else None)
dim(BV(0, SB[0]), BV(0, ST[0]), (xl - 16, 0), "140", vertical=True)
xr3 = BV(404, 0)[0]
dim(BV(404, BT[0]), BV(404, BT[0] + GF), (xr3 + 6, 0), "25 (G)", vertical=True)
dim(BV(404, BT[0] + GF), BV(404, BT[0] + GF + BD), (xr3 + 6, 0), vertical=True)
dim(BV(404, BT[0] + GF + BD), BV(404, ST[0]), (xr3 + 6, 0), "64", vertical=True)
leader(BV(345, zs_), (BV(345, 0)[0] - 6, BV(0, 140)[1] + 20), "Schraube 4×30 (22), Korpus A/B", right=False)
leader(BV(20, 150), (BV(60, 0)[0], BV(0, 175)[1] + 0), "4×30 Eiche/Span (22)", right=True)
leader(BV(EO + 14, BT[0] - 30), (X3 + 150, 60), "MOVENTO (16), Kontur schematisch", right=True)
balloon(BV(E / 2, 100), (BV(0, 0)[0] - 24, BV(0, 100)[1] + 30), 1)
balloon(BV(150 / 2, E / 2), (BV(60, 0)[0], BV(0, -10)[1]), 3)
balloon(BV(E + P / 2, 100), (BV(0, 0)[0] + 4, BV(0, 100)[1] + 20), 4)
balloon(BV(EO + GAP + ZS / 2, 120), (BV(80, 0)[0], BV(0, 120)[1]), 9)
balloon(BV(90, BT[0] - BD / 2), (BV(90, 0)[0], BV(0, 50)[1] - 4), 12)
balloon(BV(395, BT[0] + GF + BD / 2), (BV(398, 0)[0], BV(0, 150)[1]), 14)
balloon(BV(380, BT[0] + GF / 2), (BV(385, 0)[0], BV(0, 30)[1]), 11)

# Detail D – Fingerzinken (1:1): Ansicht von hinten auf hintere linke Ecke + Draufsicht
# lokale Koordinaten: u = x ab Aussenseite Seite, v = z ab UK Seite
DV_ = View(X3 + 322, 120, 1.0, uw=[(0, 62)], vw=(0, HS))
DV_.rect(0, 0, ZS, BD + NI, hatch=EIQ)                       # Seite unten (unter Hinterstueck)
for i in range(NF):
    z0, z1 = BD + NI + i * FP, BD + NI + (i + 1) * FP
    if i % 2 == 0:
        DV_.rect(0, z0, ZS, z1, hatch=EIQ)                    # Finger der Seite (Hirnholz sichtbar)
    else:
        DV_.rect(0, z0, 62, z1)                               # Finger Hinterstueck
DV_.rect(ZS, BD + NI, 62, HS)
DV_.rect(ZS - 5, NI, 62, NI + BD, hatch=SP)                   # Boden in Nut 5
msp.add_circle(DV_(7, 11), 3, dxfattribs={"layer": "Kontur"})
DV_.seg(7, 6, 7, 16, "Mittellinie")
DV_.seg(2, 11, 12, 11, "Mittellinie")
zigzag(DV_(62, -2), DV_(62, HS + 2))
text("Detail D – Fingerzinken", (X3 + 296, 282), 3.0)
text("Hinterstück/Seite, Ansicht von hinten · M 1:1", (X3 + 296, 277.5), 1.9)
dl = DV_(0, 0)[0]
dim(DV_(0, BD + NI), DV_(0, HS), (dl - 6, 0), f"7 × {FP:.1f} = 108".replace(".", ","), vertical=True)
dim(DV_(0, 0), DV_(0, NI), (dl - 6, 0), vertical=True)
dim(DV_(0, NI), DV_(0, NI + BD), (dl - 6, 0), vertical=True)
dim(DV_(0, BD + NI + FP), DV_(0, BD + NI + 2 * FP), (dl - 14, 0), vertical=True)
dim(DV_(0, 0), DV_(0, 11), (dl - 21, 0), "11 (H)", vertical=True)
dim(DV_(0, HS), DV_(ZS, HS), (0, DV_(0, HS)[1] + 5))
dim(DV_(0, 0), DV_(7, 0), (0, DV_(0, 0)[1] - 5), "7 (H)", loc=(DV_(3.5, 0)[0] - 5, DV_(0, 0)[1] - 4.2))
leader(DV_(7 + 2.2, 11 + 2.2), (DV_(30, 0)[0], DV_(0, 0)[1] - 10), "Ø6 × 10 tief (H, Blum)", right=True)
dn = [
    "7 Finger, Teilung 108/7 ≈ 15,4; Fingertiefe = Holzdicke 16.",
    "Seite: Finger 1, 3, 5, 7 (oben und unten außen); Hinterstück: 2, 4, 6.",
    "Herstellung: Kreissäge + Zinkenvorrichtung (G). Hinterstück steht auf dem",
    "Boden, Boden läuft darunter durch bis Hinterkante.",
    "Blum-Bohrung Ø6 × 10 in Stirnseite der Seite (TD-132/1 S. 5, Bohrlehre",
    "T65.1000.02). Abstand zur Bodennut ca. 1 – Nut 5 tief, ggf. hinten",
    "auslaufen lassen (n.f., an Probestück prüfen).",
]
for i, s in enumerate(dn):
    text(s, (X3 + 290, 100 - i * 3.6), 1.6)

# Detail E – Gehrung Eichenmantel oben links (1:1), Vorderansicht
EV = View(X1 + 318, 190, 1.0, uw=[(0, 70)], vw=(330, H))
EV.rect(0, 330, E, H)
EV.rect(E, H - E, 70, H)
EV.seg(0, H, E, H - E, "Kontur")
EV.rect(E, 330, EO, H - E, solid=True)                        # Kante schwarz (Spanplatte vorn)
EV.rect(EO, H - EO, 70, H - E, solid=True)
EV.rect(EO + F, 330, 70, FZ[1][1])                            # Doppel oben
# Flachduebel (verdeckt): Schlitz quer zur Gehrung
cxm, czm = E / 2, H - E / 2
dx, dz = math.cos(math.radians(45)), math.sin(math.radians(45))
L2, W2 = 11.5, 2
ax_, az_ = dx, dz                     # Langachse quer zur Gehrung (23 lt. Haendler)
bx_, bz_ = dx, -dz                    # Dicke 4 parallel zur Gehrung
pts = [(cxm - ax_ * L2 - bx_ * W2, czm - az_ * L2 - bz_ * W2), (cxm + ax_ * L2 - bx_ * W2, czm + az_ * L2 - bz_ * W2),
       (cxm + ax_ * L2 + bx_ * W2, czm + az_ * L2 + bz_ * W2), (cxm - ax_ * L2 + bx_ * W2, czm - az_ * L2 + bz_ * W2)]
pline([EV(*q) for q in pts], "Verdeckt", closed=True)
zigzag(EV(70, 328), EV(70, H + 2))
zigzag(EV(-2, 330), EV(70, 330))
text("Detail E – Gehrung", (X1 + 290, 272), 3.0)
text("Eichenmantel oben links, Ansicht · M 1:1", (X1 + 290, 267.5), 1.9)
et = EV(0, H)[1]
dim(EV(0, H), EV(E, H), (0, et + 4))
dim(EV(E, H), EV(EO, H), (0, et + 4))
dim(EV(EO, H), EV(EO + F, H), (0, et + 4), loc=(EV(EO + F, H)[0] + 3, et + 4.8))
dim(EV(70, H - E), EV(70, H), (EV(70, 0)[0] + 5, 0), vertical=True)
dim(EV(70, H - EO), EV(70, H - E), (EV(70, 0)[0] + 5, 0), vertical=True)
dim(EV(70, FZ[1][1]), EV(70, H - EO), (EV(70, 0)[0] + 5, 0), vertical=True,
    loc=(EV(70, 0)[0] + 6.5, EV(0, FZ[1][1])[1] - 3))
leader(EV(30, H - 30), (EV(0, 0)[0] - 6, EV(0, 345)[1]), "Kante schwarz 2 (19)", right=False)
leader(EV(cxm + 3, czm - 3), (EV(0, 0)[0] - 6, EV(0, 362)[1]), "Flachdübel Gr. 20 (20)", right=False)
en = [
    "Gehrung 45° mit Flachdübel Gr. 20 (G, lt. Händler 56 × 23 × 4),",
    "Seiten + Oberboden aus einem Brett,",
    "Maserung umlaufend; Unterboden beliebig.",
]
for i, s in enumerate(en):
    text(s, (X1 + 240, 182 - i * 3.6), 1.6)

out = sys.argv[1] if len(sys.argv) > 1 else "TopSecret_v2.dxf"
doc.saveas(out)
print("geschrieben:", out)
