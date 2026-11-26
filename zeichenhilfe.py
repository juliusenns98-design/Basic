"""Gemeinsame Zeichenhilfen (DXF, ezdxf): Layer, Bemassung, Ansichten mit Bruch, Schriftfeld."""
import math

import ezdxf
from ezdxf.enums import TextEntityAlignment

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


def title_block(x0, sheet, nsheets, scale_txt, subtitle, project="Mittelstufenprojekt – TOP SECRET 2.0",
                number=None, date="25.11.2026", material=("Eiche massiv, geölt", "Spanplatte schwarz 19")):
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
    tt(material[0], 2, 41.5, 2.2)
    tt(material[1], 2, 37.5, 2.2)
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
    tt(project, 2, 22.5, 4.2)
    tt(subtitle, 2, 18.7, 1.9)
    tt("Name / Klasse", 1, 14.2)
    tt("(Name), (Klasse)", 2, 5, 2.3)
    tt("Ausbildungsbetrieb", 47, 14.2)
    tt("(Betrieb)", 48, 5, 2.3)
    tt("Datum", 93, 14.2)
    tt(date, 94, 5, 2.3)
    tt("Zeichnungs-Nr.", 139, 14.2)
    tt(number or f"MSP-TS-2.{sheet}", 140, 5, 3.2)


def view_title(x, y, name, scale):
    text(name, (x, y), 3.5)
    text(scale, (x, y - 4.3), 2.2)


