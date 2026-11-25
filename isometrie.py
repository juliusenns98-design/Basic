"""Isometrie (DIN ISO 5456-3, unverkuerzt) des Mittelstufenprojekts TOP SECRET 2.0.

Stand der Konstruktion wie in top_secret.py (noch ohne Fingerzinken / 2-mm-Kante).
Zwei Darstellungen auf A3 quer, M 1:5:
  links  geschlossen
  rechts unterer Schubkasten rechts geoeffnet (Geheimfach bleibt unsichtbar)

Aufruf:  python3 isometrie.py  ->  TopSecret_Isometrie.dxf
"""
import math
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment

import hlr

# Masse wie top_secret.py
B, H, T, BS = 700, 400, 305, 350
E, P, EO = 20, 19, 39
TE = T - 2
X, F, LT, RW = 20, 3, 281, 8
LW, LH = BS - 2 * EO, H - 2 * EO
FB, FH = LW - 2 * F, (LH - 3 * F) / 2
FRONT_Z = [(EO + F, EO + F + FH), (EO + 2 * F + FH, EO + 2 * F + 2 * FH)]
ZS, BD, NI, HS, GF, EB = 15, 8, 13, 110, 18, 6
ISKL = 260
AUSZUG = 160                         # Darstellung: unterer rechter SK um 160 mm geoeffnet

ISO_V, ISO_R, ISO_U = (1, -1, 1), (1, 1, 0), (-1, 1, 2)   # Blick von vorn rechts oben
K = math.sqrt(1.5)                   # unverkuerzte Isometrie (Achsen 1:1)


def box(part, x0, x1, y0, y1, z0, z1):
    return hlr.Prism(part, "xzy", [(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y0, y1)


def prof(part, pts, y0, y1):
    return hlr.Prism(part, "xzy", pts, y0, y1)


KB = (B - 2 * E) / 2                 # 330 Innenkorpus-Breite
LWI = KB - 2 * P                     # 292 lichte Weite je Korpus
FBI = LWI - 2 * F                    # 286 Frontbreite


def moebel(open_lower=False):
    """4 Eichenplatten (Gehrung) um zwei verschraubte schwarze Innenkorpusse."""
    pr = []
    pr.append(prof("eL", [(0, 0), (E, E), (E, H - E), (0, H)], 0, TE))
    pr.append(prof("eR", [(B, 0), (B, H), (B - E, H - E), (B - E, E)], 0, TE))
    pr.append(prof("eO", [(0, H), (E, H - E), (B - E, H - E), (B, H)], 0, TE))
    pr.append(prof("eU", [(0, 0), (B, 0), (B - E, E), (E, E)], 0, TE))
    for k, cx in enumerate((E, E + KB)):
        t = "ab"[k]
        pr.append(box(f"{t}sL", cx, cx + P, 0, T, E, H - E))
        pr.append(box(f"{t}sR", cx + KB - P, cx + KB, 0, T, E, H - E))
        pr.append(box(f"{t}sO", cx + P, cx + KB - P, 0, T, H - EO, H - E))
        pr.append(box(f"{t}sU", cx + P, cx + KB - P, 0, T, E, EO))
        pr.append(box(f"{t}rw", cx + P, cx + KB - P, LT, LT + RW, EO, H - EO))
        for j, (z0, z1) in enumerate(FRONT_Z):
            dy = -AUSZUG if (open_lower and k == 1 and j == 0) else 0
            x0 = cx + P + F
            pr.append(box(f"{t}f{j}", x0, x0 + FBI, dy, dy + X, z0, z1))
            if dy:
                bt = z0 + 37
                sb = bt - BD - NI
                st = sb + HS
                xi0, xi1 = cx + P + 6, cx + KB - P - 6          # Schubkasten aussen
                pr.append(box("zL", xi0, xi0 + ZS, X + dy, ISKL + dy, sb, st))
                pr.append(box("zR", xi1 - ZS, xi1, X + dy, ISKL + dy, sb, st))
                pr.append(box("vs", xi0 + ZS, xi1 - ZS, X + dy, X + ZS + dy, sb, st))
                pr.append(box("hs", xi0 + ZS, xi1 - ZS, ISKL - ZS + dy, ISKL + dy, bt, st))
                pr.append(box("bo", xi0 + ZS, xi1 - ZS, X + ZS + dy, ISKL - ZS + dy, bt, bt + GF + EB))
    return pr


def merge_collinear(lines, tol=0.05):
    groups = {}
    for u0, w0, u1, w1 in lines:
        if math.hypot(u1 - u0, w1 - w0) < 1e-9:
            continue
        ang = math.atan2(w1 - w0, u1 - u0) % math.pi
        if ang > math.pi - 1e-6:
            ang = 0.0
        c, s_ = math.cos(ang), math.sin(ang)
        off = -u0 * s_ + w0 * c
        t0, t1 = sorted((u0 * c + w0 * s_, u1 * c + w1 * s_))
        groups.setdefault((round(ang, 4), round(off / tol)), (ang, off, []))[2].append((t0, t1))
    out = []
    for ang, off, iv in groups.values():
        c, s_ = math.cos(ang), math.sin(ang)
        iv.sort()
        cur = list(iv[0])
        for t0, t1 in iv[1:] + [(math.inf, math.inf)]:
            if t0 <= cur[1] + tol:
                cur[1] = max(cur[1], t1)
            else:
                a, b = cur
                out.append((a * c - off * s_, a * s_ + off * c, b * c - off * s_, b * s_ + off * c))
                cur = [t0, t1]
    return out


# ---------------------------------------------------------------------------
doc = ezdxf.new("R2010", setup=True, units=4)
doc.header["$MEASUREMENT"] = 1
msp = doc.modelspace()
for name, (col, lw) in {"Rahmen": (7, 70), "Kontur": (7, 50), "Duenn": (8, 25),
                        "Text": (7, 25), "Schriftfeld": (7, 35)}.items():
    doc.layers.add(name, color=col, lineweight=lw)
doc.styles.add("ISO", font="isocpeur.ttf")


def line(p, q, layer="Kontur"):
    msp.add_line(p, q, dxfattribs={"layer": layer})


def text(s, p, h=2.5, align="LEFT"):
    t = msp.add_text(s, height=h, dxfattribs={"layer": "Text", "style": "ISO"})
    t.set_placement(p, align=getattr(TextEntityAlignment, align))


def pline(pts, layer, closed=True):
    msp.add_lwpolyline(pts, format="xy", close=closed, dxfattribs={"layer": layer})


def render(prisms):
    raw = merge_collinear(hlr.render(prisms, ISO_V, ISO_R, ISO_U, step=1.0))
    return [(a * K, b * K, c * K, d * K) for a, b, c, d in raw if math.hypot(c - a, d - b) * K > 1.0]


def place(lines, x_left, y_bottom, scale=0.2):
    us = [v for l in lines for v in (l[0], l[2])]
    ws = [v for l in lines for v in (l[1], l[3])]
    u0, w0 = min(us), min(ws)
    for a, b, c, d in lines:
        line((x_left + (a - u0) * scale, y_bottom + (b - w0) * scale),
             (x_left + (c - u0) * scale, y_bottom + (d - w0) * scale))
    return (max(us) - u0) * scale, (max(ws) - w0) * scale


closed = render(moebel())
opened = render(moebel(open_lower=True))

# Blatt A3
pline([(0, 0), (420, 0), (420, 297), (0, 297)], "Duenn")
pline([(20, 10), (410, 10), (410, 287), (20, 287)], "Rahmen")

r_ = [v / math.sqrt(2) for v in ISO_R]
s_ = [v / math.sqrt(6) for v in ISO_U]


def proj(x, y, z):
    return (K * (x * r_[0] + y * r_[1] + z * r_[2]), K * (x * s_[0] + y * s_[1] + z * s_[2]))


def placed(lines, x_left, y_bottom, scale=0.2):
    us = [v for l in lines for v in (l[0], l[2])]
    ws = [v for l in lines for v in (l[1], l[3])]
    u0, w0 = min(us), min(ws)
    for a, b, c, d in lines:
        line((x_left + (a - u0) * scale, y_bottom + (b - w0) * scale),
             (x_left + (c - u0) * scale, y_bottom + (d - w0) * scale))
    return lambda x, y, z: (x_left + (proj(x, y, z)[0] - u0) * scale,
                            y_bottom + (proj(x, y, z)[1] - w0) * scale)


ds = doc.dimstyles.new("ISO5")
ds.dxf.dimtxt = 2.5
ds.dxf.dimtxsty = "ISO"
ds.dxf.dimtsz = 1.2
ds.dxf.dimexo = 1.0
ds.dxf.dimexe = 1.5
ds.dxf.dimgap = 0.8
ds.dxf.dimtad = 1
ds.dxf.dimtih = 0
ds.dxf.dimtoh = 0
ds.dxf.dimlfac = 5.0
ds.dxf.dimclrd = 3
ds.dxf.dimclre = 3
doc.layers.add("Bemassung", color=3, lineweight=25)


def isodim(P1, P2, Pbase, angle, oblique, txt="<>"):
    d = msp.add_linear_dim(base=Pbase, p1=P1, p2=P2, angle=angle, text=txt, dimstyle="ISO5",
                           dxfattribs={"layer": "Bemassung"})
    d.dimension.dxf.oblique_angle = oblique
    d.render()


Y0 = 86
L = placed(closed, 30, Y0)
R = placed(opened, 214, Y0 - 8)

# Hauptmasse in der geschlossenen Ansicht (Masslinien parallel zu den Iso-Achsen)
off = 45                                                 # Abstand der Masslinie (Modell-mm)
isodim(L(0, 0, 0), L(B, 0, 0), L(0, 0, -off), -30, 90)                # Breite 700
isodim(L(B, 0, 0), L(B, T, 0), L(B, 0, -off), 30, 90)                  # Tiefe 305
isodim(L(0, 0, 0), L(0, 0, H), L(-off, 0, 0), 90, 150)                 # Hoehe 400

text("Isometrie – geschlossen", (30, 272), 3.5)
text("M 1:5 (Achsen unverkürzt)", (30, 267.5), 2.2)
text("Isometrie – Schubkasten rechts unten geöffnet", (214, 272), 3.5)
text("M 1:5 (Achsen unverkürzt) · Geheimfach von außen nicht erkennbar", (214, 267.5), 2.2)

notes = [
    "Isometrie nach DIN ISO 5456-3: Breite und Tiefe unter 30° zur Waagrechten, Höhe senkrecht,",
    "alle Achsmaße unverkürzt im Maßstab 1:5 – Kantenlängen direkt mit dem Lineal abtragen.",
    "Vorlage für die Perspektive von Hand (Projektmappe Pkt. 5); verdeckte Kanten nicht dargestellt.",
    "Aufbau: zwei schwarze Innenkorpusse (Spanplatte 19, je 330 breit) in der Werkstatt verschraubt,",
    "darum 4 Eichenplatten 20 mm (Seiten, Ober-, Unterboden) auf Gehrung. Mitte: 2 × 19 Spanplatte.",
]
for i, t in enumerate(notes):
    text(t, (24, 52 - i * 4.4), 1.9)

# Schriftfeld
TX, TY = 226, 10
pline([(TX, TY), (TX + 184, TY), (TX + 184, TY + 34), (TX, TY + 34)], "Rahmen")
for y in (17,):
    line((TX, TY + y), (TX + 184, TY + y), "Schriftfeld")
for x in (60, 108, 146):
    line((TX + x, TY), (TX + x, TY + 17), "Schriftfeld")
text("Benennung", (TX + 1, TY + 31.2), 1.8)
text("Mittelstufenprojekt – TOP SECRET 2.0", (TX + 2, TY + 23.5), 4.2)
text("Isometrie, 700 × 400 × 305, Eichenmantel um 2 Innenkorpusse", (TX + 2, TY + 19.5), 1.9)
text("Maßstab", (TX + 1, TY + 14.2), 1.8)
text("1:5", (TX + 3, TY + 5), 3.5)
text("Datum", (TX + 61, TY + 14.2), 1.8)
text("25.11.2026", (TX + 62, TY + 5), 2.5)
text("Gezeichnet", (TX + 109, TY + 14.2), 1.8)
text("(Name)", (TX + 110, TY + 5), 2.5)
text("Zeichnungs-Nr.", (TX + 147, TY + 14.2), 1.8)
text("MSP-TS-ISO", (TX + 148, TY + 5), 3.0)

out = sys.argv[1] if len(sys.argv) > 1 else "TopSecret_Isometrie.dxf"
doc.saveas(out)
print("geschrieben:", out)
