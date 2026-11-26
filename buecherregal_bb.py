"""Bücherregal (Aufgabenblatt Technische Schulen Steinfurt) – Schnitt B-B, M 1:1.

Waagerechter Schnitt in Höhe z = 160 (durch das Griffloch) durch den Schubkasten im
rechten unteren Fach und die angrenzenden Bauteile. A3 quer.

Vorgaben (Blatt): 500 × 500 × 200, Spanplatte P2 19, Furnier Eiche QCXE 0,5,
Anleimer Eiche 5 überfurniert, Rückwand VP 5 allseitig eingefälzt, Korpus auf Gehrung,
Schubkasten gezinkt, Seiten/Vorder-/Hinterstück 10, Lauf-, Streif-, Kippleiste mit
umlaufend gleichmäßigem Fugenbild, Griffloch.
Ergänzte Maße sind mit (G) gekennzeichnet.

Aufruf:  python3 buecherregal_bb.py  ->  Buecherregal_Schnitt_B-B.dxf
"""
import sys

from zeichenhilfe import (View, balloon, dim, doc, hatch_poly, leader, line, pline, sheet_frame,
                          text, title_block, zigzag)

# ---------------------------------------------------------------------------
# Maße (x Breite von links, y Tiefe von vorn, z Höhe)
# ---------------------------------------------------------------------------
B, H, T = 500, 500, 200
D = 20                 # Plattendicke fertig: 19 + 2 × 0,5 Furnier
V = 0.5                # Furnier
AL = 5                 # Anleimer
FB, FT = 10, 6         # Falz Rückwand: Breite in die Platte, Tiefe von hinten (G)
RW = 5                 # Rückwand VP 5
Y_RW = T - FT          # Vorderkante Rückwand 194
XM = 300               # Achse Mittelseite (Achsmaß 200 von rechts, G)
XM0, XM1 = XM - D / 2, XM + D / 2          # 290..310
XR0, XR1 = XM1, B - D                      # Fach rechts lichte Weite 310..480 = 170
ZB = 160               # Schnitthöhe B-B
F = 2                  # Fuge Doppel (G)
DO = 20                # Doppel (Spanplatte 19 + Furnier), Anleimer 5 seitlich
ST = 10                # Streifleiste (G)
LUFT = 0.5
ZS = 10                # Seiten / Vorder-/Hinterstück (Vorgabe)
BXW = (XR1 - XR0) - 2 * ST - 2 * LUFT      # 149
BX0, BX1 = XR0 + ST + LUFT, XR1 - ST - LUFT  # 320,5..469,5
BY0, BY1 = DO, Y_RW - 2                    # Schubkasten 20..192 (L = 172)
GL = 30                # Griffloch Ø (G)
GX = (XR0 + XR1) / 2   # Mitte Fach 395

SP = ("ANSI37", 0.9, 0.0)       # Spanplatte
MH = ("ANSI31", 0.8, 0.0)       # Massivholz
MH2 = ("ANSI31", 0.8, 90.0)
VP = ("ANSI32", 0.6, 0.0)       # Furniersperrholz

sheet_frame(0)
title_block(0, 1, 1, "1:1", "Waagerechter Schnitt durch Schubkasten im rechten unteren Fach",
            project="Bücherregal – Schnitt B-B", number="BR-B-B", date="26.11.2026",
            material=("Spanplatte P2 19, Eiche QCXE 0,5", "Anleimer Eiche 5, Rückwand VP 5"))

S = View(46, 82, 1.0, uw=[(0, 62), (238, B)], vw=(0, T), gap=8)


def panel(x0, x1, y1, falz=None):
    """Furnierte Spanplatte im Schnitt: Kern, Furnier beidseitig, Anleimer vorn.
    falz: 'r' / 'l' = Falz an der rechten / linken Innenkante hinten."""
    S.rect(x0 + V, AL, x1 - V, y1, hatch=SP)                        # Kern
    S.rect(x0 + V, 0, x1 - V, AL, hatch=MH2)                        # Anleimer
    S.rect(x0, 0, x0 + V, y1, "Duenn")                              # Furnier
    S.rect(x1 - V, 0, x1, y1, "Duenn")


# Seiten mit Falz, Mittelseite
for x0, x1, side in ((0, D, "l"), (B - D, B, "r")):
    S.rect(x0 + V, AL, x1 - V, Y_RW, hatch=SP)
    S.rect(x0 + V, 0, x1 - V, AL, hatch=MH2)
    if side == "l":                                                 # Kern hinter dem Falz
        S.rect(x0 + V, Y_RW, x1 - FB, T, hatch=SP)
    else:
        S.rect(x0 + FB, Y_RW, x1 - V, T, hatch=SP)
    outer = x0 if side == "l" else x1 - V
    S.rect(outer, 0, outer + V, T, "Duenn")
    inner = x1 - V if side == "l" else x0
    S.rect(inner, 0, inner + V, Y_RW, "Duenn")
panel(XM0, XM1, Y_RW)

# Rückwand im Falz
S.rect(FB, Y_RW, B - FB, Y_RW + RW, hatch=VP)

# Streifleisten
for xa in (XR0, XR1 - ST):
    S.rect(xa, BY0 + F, xa + ST, Y_RW, hatch=MH)

# Schubkasten: vorn Schnitt durch Schwalbe (Seite läuft durch), hinten durch Zinken
S.rect(BX0, BY0, BX0 + ZS, BY1 - ZS, hatch=MH)
S.rect(BX1 - ZS, BY0, BX1, BY1 - ZS, hatch=MH)
S.rect(BX0, BY1 - ZS, BX1, BY1, hatch=MH2)                          # Hinterstück
S.rect(BX0 + ZS, BY0, GX - GL / 2, BY0 + ZS, hatch=MH2)            # Vorderstück (Griffloch)
S.rect(GX + GL / 2, BY0, BX1 - ZS, BY0 + ZS, hatch=MH2)
for xa in (BX0, BX1 - ZS):                                          # Zinkengrund vorn
    S.seg(xa, BY0 + ZS, xa + ZS, BY0 + ZS, "Verdeckt")
for xa in (BX0 + ZS, BX1 - ZS):                                     # Schwalbengrund hinten
    S.seg(xa, BY1 - ZS, xa, BY1, "Verdeckt")

# Doppel: Spanplatte, Anleimer seitlich, Furnier vorn/hinten, Griffloch
DX0, DX1 = XR0 + F, XR1 - F
for a, b in ((DX0, GX - GL / 2), (GX + GL / 2, DX1)):
    ka, kb = max(a, DX0 + AL), min(b, DX1 - AL)
    S.rect(ka, V, kb, DO - V, hatch=SP)
    S.rect(a, 0, b, V, "Duenn")
    S.rect(a, DO - V, b, DO, "Duenn")
S.rect(DX0, V, DX0 + AL, DO - V, hatch=MH)
S.rect(DX1 - AL, V, DX1, DO - V, hatch=MH)
S.seg(GX, -6, GX, BY0 + ZS + 6, "Mittellinie")
S.seg(XM, -24, XM, T + 3, "Mittellinie")

S.breaks()

# ---------------------------------------------------------------------------
# Bemaßung
# ---------------------------------------------------------------------------
y0 = S(0, 0)[1]
row1, row2, row3 = y0 - 6, y0 - 12, y0 - 18
dim(S(0, 0), S(D, 0), (0, row1))
dim(S(D, 0), S(XM0, 0), (0, row1), "270")
dim(S(XM0, 0), S(XM1, 0), (0, row1))
dim(S(XM1, 0), S(DX0, 0), (0, row1), loc=(S(XM1, 0)[0] - 2.5, row1 + 0.8))
dim(S(DX0, 0), S(DX1, 0), (0, row1), "166 (G)")
dim(S(DX1, 0), S(XR1, 0), (0, row1), loc=(S(XR1, 0)[0] + 2, row1 + 0.8))
dim(S(XR1, 0), S(B, 0), (0, row1))
dim(S(0, 0), S(B, 0), (0, row2), "500")
dim(S(XM, 0), S(B, 0), (0, row3), "200 (Achsmaß)")
# im Fach
ym = S(0, 120)[1]
dim(S(XR0, 120), S(XR0 + ST, 120), (0, ym))
dim(S(XR0 + ST, 120), S(XR1 - ST, 120), (0, ym), "150")
dim(S(XR1 - ST, 120), S(XR1, 120), (0, ym))
dim(S(BX0, 100), S(BX1, 100), (0, S(0, 100)[1]), "149 (G)")
dim(S(XR0, 145), S(XR1, 145), (0, S(0, 145)[1]), "170 (lichte Weite)")
dim(S(GX - GL / 2, 0), S(GX + GL / 2, 0), (0, S(0, 45)[1]), "Ø30 (G)")
# Tiefe rechts
xr = S(B, 0)[0]
dim(S(B, 0), S(B, DO), (xr + 6, 0), vertical=True)
dim(S(B, DO), S(B, BY1), (xr + 6, 0), "172 (G)", vertical=True)
dim(S(B, BY1), S(B, Y_RW), (xr + 6, 0), vertical=True, loc=(xr + 7.5, S(0, BY1)[1] - 4))
dim(S(B, Y_RW), S(B, T), (xr + 13, 0), "6", vertical=True)
dim(S(B, 0), S(B, T), (xr + 20, 0), vertical=True)
# Tiefe links
xl = S(0, 0)[0]
dim(S(0, 0), S(0, AL), (xl - 6, 0), vertical=True, loc=(xl - 7.5, S(0, 0)[1] - 3))
dim(S(0, AL), S(0, Y_RW), (xl - 6, 0), vertical=True)
dim(S(0, Y_RW), S(0, Y_RW + RW), (xl - 13, 0), vertical=True)

# Beschriftung
leader(S(5, 2.5), (S(0, 0)[0] + 18, S(0, 30)[1]), "Anleimer Eiche 5, überfurniert", right=True)
leader(S(D - 0.25, 60), (S(40, 0)[0], S(0, 70)[1]), "Furnier Eiche QCXE 0,5", right=True)
leader(S(10, 100), (S(40, 0)[0], S(0, 95)[1]), "Spanplatte P2 19", right=True)
leader(S(15, Y_RW + 2.5), (S(40, 0)[0], S(0, 170)[1]), "Rückwand VP 5, Falz 10 × 6 (G)", right=True)
leader(S(XM0 + 10, 100), (S(260, 0)[0], S(0, 110)[1]), "Mittelseite", right=False)
leader(S(XR0 + 5, 150), (S(260, 0)[0], S(0, 160)[1]), "Streifleiste 10 (G)", right=False)
leader(S(BX0 + 5, 60), (S(260, 0)[0], S(0, 60)[1]), "Seite 10, Schwalbe", right=False)
leader(S(BX1 - 5, BY1 - 5), (S(445, 0)[0], S(0, 175)[1]), "Hinterstück 10, Zinken", right=False)
leader(S(350, BY0 + 5), (S(350, 0)[0], S(0, 40)[1]), "Vorderstück 10", right=True)
leader(S(440, 10), (S(445, 0)[0], S(0, 30)[1]), "Doppel 20, Anleimer 5", right=True)

# Lage-Skizze Vorderansicht 1:20
K = View(180, 18, 0.05)
K.rect(0, 0, B, H)
K.rect(D, D, B - D, H - D)
K.rect(XM0, D, XM1, H - D)
K.rect(D, 190, XM0, 210)
K.rect(XM1, 190, B - D, 210)
K.rect(XR0 + F, D + F, XR1 - F, 190 - F)
for a, b, c, d in ((0, 0, D, D), (B, 0, B - D, D), (0, H, D, H - D), (B, H, B - D, H - D)):
    K.seg(a, b, c, d, "Duenn")
K.seg(-60, ZB, B + 60, ZB, "Schnittverlauf")
text("B", K(-110, ZB + 15), 2.5)
text("B", K(B + 70, ZB + 15), 2.5)
text("Lage B-B, Vorderansicht M 1:20", (172, 46), 1.8)

text("Schnitt B-B", (22, 56), 3.5)
text("M 1:1 · waagerecht in Höhe 160 über UK Korpus (durch das Griffloch)", (22, 51.5), 1.8)
notes = [
    "Platten: Spanplatte P2 19 + Furnier Eiche QCXE 2 × 0,5 = 20; Anleimer Eiche 5, überfurniert.",
    "Mittelseite: Achse 200 von rechts außen (G); Fach rechts unten lichte Weite 170 × 170.",
    "Laufleiste 20 × 10, Kippleiste 20 × 10, Streifleiste 10 × 150 (G), Eiche, verschraubt.",
    "Schubkasten 172 × 149 × 149 (G), offen gezinkt; Boden VP 5 in Nut (G).",
    "Doppel 166 × 166 × 20, Fuge 2 umlaufend (G); Griffloch Ø30 durch Doppel und Vorderstück.",
    "Vorn Schnitt durch Schwalbe, hinten durch Zinken; Zinkenteilung n.f.",
    "Rückwand allseitig eingefälzt, Falz 10 × 6, 1 hinter Hinterkante (G).",
    "(G) ergänzt / gewählt   n.f. noch festzulegen",
]
for i, s in enumerate(notes):
    text(s, (22, 46 - i * 3.6), 1.6)

out = sys.argv[1] if len(sys.argv) > 1 else "Buecherregal_Schnitt_B-B.dxf"
doc.saveas(out)
print("geschrieben:", out)
