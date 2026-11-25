"""Rendert eine DXF als PDF- und PNG-Vorschau (weisser Hintergrund, schwarze Linien).

Aufruf:  python3 vorschau.py Datei.dxf
"""
import sys

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from ezdxf.addons.drawing import Frontend, RenderContext  # noqa: E402
from ezdxf.addons.drawing.config import (  # noqa: E402
    BackgroundPolicy, ColorPolicy, Configuration, LineweightPolicy)
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend  # noqa: E402

src = sys.argv[1]
stem = src.rsplit(".", 1)[0]
doc = ezdxf.readfile(src)
cfg = Configuration(
    background_policy=BackgroundPolicy.WHITE,
    color_policy=ColorPolicy.BLACK,
    lineweight_policy=LineweightPolicy.ABSOLUTE,
    lineweight_scaling=1.0,
)
fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 420)
ax.set_ylim(0, 297)
Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(
    doc.modelspace(), finalize=False)
ax.set_xlim(0, 420)
ax.set_ylim(0, 297)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(stem + "_Vorschau.pdf", facecolor="white")
fig.savefig(stem + "_Vorschau.png", dpi=200, facecolor="white")
print("Vorschau:", stem + "_Vorschau.pdf / .png")
