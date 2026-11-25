"""Rendert eine DXF mit mehreren A3-Blaettern nebeneinander als mehrseitiges PDF + PNGs.

Aufruf:  python3 vorschau_blaetter.py Datei.dxf 0 440   (x-Versatz je Blatt)
"""
import sys

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from ezdxf.addons.drawing import Frontend, RenderContext  # noqa: E402
from ezdxf.addons.drawing.config import (  # noqa: E402
    BackgroundPolicy, ColorPolicy, Configuration, LineweightPolicy)
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend  # noqa: E402

src = sys.argv[1]
offsets = [float(v) for v in sys.argv[2:]] or [0.0]
stem = src.rsplit(".", 1)[0]
doc = ezdxf.readfile(src)
cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK,
                    lineweight_policy=LineweightPolicy.ABSOLUTE)
fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(
    doc.modelspace(), finalize=False)
ax.set_aspect("equal")
ax.axis("off")
with PdfPages(stem + "_Vorschau.pdf") as pdf:
    for i, x0 in enumerate(offsets, 1):
        ax.set_xlim(x0, x0 + 420)
        ax.set_ylim(0, 297)
        pdf.savefig(fig, facecolor="white")
        fig.savefig(f"{stem}_Blatt{i}_Vorschau.png", dpi=200, facecolor="white")
print("Vorschau:", stem + "_Vorschau.pdf")
