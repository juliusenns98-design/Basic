"""Einfache Verdeckte-Kanten-Berechnung fuer Ansichten aus Prismen.

Jedes Bauteil besteht aus Prismen (2D-Profil, entlang einer Achse extrudiert).
Fuer eine Blickrichtung werden alle Prismenkanten abgetastet; gezeichnet wird
nur, was sichtbar ist und eine echte Koerperkante ist (keine Trennfuge
zwischen zwei Prismen desselben Bauteils).
"""
import math

import numpy as np

AX = {"x": 0, "y": 1, "z": 2}


class Prism:
    def __init__(self, part, axes, profile, c0, c1):
        # axes: z.B. "xzy" -> Profil liegt in x/z, extrudiert entlang y
        self.part = part
        self.ia, self.ib, self.ic = (AX[a] for a in axes)
        self.profile = [tuple(map(float, p)) for p in profile]
        self.c0, self.c1 = float(c0), float(c1)

    def to3d(self, a, b, c):
        p = [0.0, 0.0, 0.0]
        p[self.ia], p[self.ib], p[self.ic] = a, b, c
        return np.array(p)

    def moved(self, d):
        """Kopie, verschoben um Vektor d (fuer die Explosionsdarstellung)."""
        d = list(d)
        pr = Prism.__new__(Prism)
        pr.part, pr.ia, pr.ib, pr.ic = self.part, self.ia, self.ib, self.ic
        pr.profile = [(a + d[self.ia], b + d[self.ib]) for a, b in self.profile]
        pr.c0, pr.c1 = self.c0 + d[self.ic], self.c1 + d[self.ic]
        return pr

    def faces(self):
        pts = self.profile
        n = len(pts)
        f = [[self.to3d(a, b, self.c0) for a, b in pts],
             [self.to3d(a, b, self.c1) for a, b in pts]]
        for i in range(n):
            a0, b0 = pts[i]
            a1, b1 = pts[(i + 1) % n]
            f.append([self.to3d(a0, b0, self.c0), self.to3d(a1, b1, self.c0),
                      self.to3d(a1, b1, self.c1), self.to3d(a0, b0, self.c1)])
        return f

    def edges(self):
        pts = self.profile
        n = len(pts)
        e = []
        for i in range(n):
            a0, b0 = pts[i]
            a1, b1 = pts[(i + 1) % n]
            for c in (self.c0, self.c1):
                e.append((self.to3d(a0, b0, c), self.to3d(a1, b1, c)))
            e.append((self.to3d(a0, b0, self.c0), self.to3d(a0, b0, self.c1)))
        return e

    def contains(self, P):
        """P: (N,3) -> bool-Maske, ob die Punkte im Prisma liegen."""
        a, b, c = P[:, self.ia], P[:, self.ib], P[:, self.ic]
        inside = _pip(a, b, self.profile)
        return inside & (c > self.c0) & (c < self.c1)


def _pip(x, y, poly):
    inside = np.zeros(x.shape, dtype=bool)
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if y0 == y1:
            continue
        cond = (y0 > y) != (y1 > y)
        xi = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
        inside ^= cond & (x < xi)
    return inside


def _dist_to_poly(x, y, poly):
    d = np.full(x.shape, np.inf)
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        if L2 == 0:
            continue
        t = np.clip(((x - x0) * dx + (y - y0) * dy) / L2, 0, 1)
        d = np.minimum(d, np.hypot(x - (x0 + t * dx), y - (y0 + t * dy)))
    return d


def render(prisms, view, right, up, step=1.0):
    """Liefert sichtbare 2D-Linien [(u0,w0,u1,w1), ...] in Modell-mm."""
    v = np.array(view, float)
    v /= np.linalg.norm(v)
    r = np.array(right, float)
    r /= np.linalg.norm(r)
    s = np.array(up, float)
    s /= np.linalg.norm(s)

    # Flaechen fuer die Verdeckung
    faces = []
    for pr in prisms:
        for f in pr.faces():
            F = np.array(f)
            n = np.cross(F[1] - F[0], F[2] - F[0])
            if np.linalg.norm(n) < 1e-12:
                continue
            n /= np.linalg.norm(n)
            nv = n @ v
            if abs(nv) < 1e-9:
                continue
            poly = [(p @ r, p @ s) for p in F]
            us = [p[0] for p in poly]
            ws = [p[1] for p in poly]
            faces.append((n, n @ F[0], nv, poly, min(us), max(us), min(ws), max(ws)))

    # Kanten abtasten
    segs = []  # (edge_id, part, A, B)
    samples, owners, dirs, eids = [], [], [], []
    edges = []
    for pr in prisms:
        for A, B in pr.edges():
            L = np.linalg.norm(B - A)
            if L < 1e-9:
                continue
            k = max(1, int(math.ceil(L / step)))
            eid = len(edges)
            edges.append((A, B, k, pr.part))
            e = (B - A) / L
            for i in range(k):
                samples.append(A + (B - A) * (i + 0.5) / k)
                owners.append(pr.part)
                dirs.append(e)
                eids.append(eid)
    P = np.array(samples)
    D = np.array(dirs)
    owners = np.array(owners)
    N = len(P)

    # 1) echte Kante? (Belegung rund um die Kante pruefen)
    real = np.zeros(N, dtype=bool)
    tmp = np.where(np.abs(D[:, 0]) < 0.9, 0, 1)
    helper = np.zeros_like(D)
    helper[np.arange(N), tmp] = 1.0
    p1 = np.cross(D, helper)
    p1 /= np.linalg.norm(p1, axis=1)[:, None]
    p2 = np.cross(D, p1)
    delta = 0.05
    occ = np.zeros((N, 12), dtype=bool)
    parts = sorted(set(owners))
    for k in range(12):
        ang = math.radians(15 + 30 * k)
        Q = P + delta * (math.cos(ang) * p1 + math.sin(ang) * p2)
        for part in parts:
            m = owners == part
            inside = np.zeros(m.sum(), dtype=bool)
            for pr in prisms:
                if pr.part == part:
                    inside |= pr.contains(Q[m])
            occ[m, k] = inside
    cnt = occ.sum(axis=1)
    half = np.zeros(N, dtype=bool)
    for k in range(12):
        half |= np.all(np.roll(occ, -k, axis=1)[:, :6], axis=1) & (cnt == 6)
    real = (cnt > 0) & (cnt < 12) & ~half

    # 2) sichtbar?
    U = P @ r
    W = P @ s
    PV = P @ v
    hidden = np.zeros(N, dtype=bool)
    for n, d0, nv, poly, umin, umax, wmin, wmax in faces:
        e = 1e-3
        m = (~hidden) & real & (U > umin - e) & (U < umax + e) & (W > wmin - e) & (W < wmax + e)
        if not m.any():
            continue
        idx = np.nonzero(m)[0]
        t = (d0 - P[idx] @ n) / nv
        ok = t > 1e-4
        idx, t = idx[ok], t[ok]
        if not len(idx):
            continue
        inside = _pip(U[idx], W[idx], poly)
        near = _dist_to_poly(U[idx], W[idx], poly) <= e
        # Punkte genau auf der Umrisslinie einer weiter vorn liegenden Flaeche
        # gelten als verdeckt (die Umrisslinie selbst wird ja gezeichnet).
        hide = (inside & ~near) | (near & (t > 0.5))
        hidden[idx[hide]] = True
    vis = real & ~hidden

    # 3) zu Linien zusammenfassen, Doppelte entfernen
    seen = set()
    lines = []
    pos = 0
    for A, B, k, part in edges:
        run = None
        a2 = np.array([A @ r, A @ s])
        b2 = np.array([B @ r, B @ s])
        for i in range(k):
            ok = vis[pos + i]
            if ok:
                mid = a2 + (b2 - a2) * (i + 0.5) / k
                key = (round(mid[0] * 20), round(mid[1] * 20))
                if key in seen:
                    ok = False
                else:
                    seen.add(key)
            if ok and run is None:
                run = i
            if not ok and run is not None:
                lines.append(_seg(a2, b2, run, i, k))
                run = None
        if run is not None:
            lines.append(_seg(a2, b2, run, k, k))
        pos += k
    return lines


def _seg(a, b, i0, i1, k):
    p = a + (b - a) * i0 / k
    q = a + (b - a) * i1 / k
    return (p[0], p[1], q[0], q[1])
