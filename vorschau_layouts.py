"""Rendert alle Papierbereich-Layouts einer DXF (inkl. Ansichtsfenster) als PDF + PNG.

Aufruf:  python3 vorschau_layouts.py Datei.dxf
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
stem = src.rsplit(".", 1)[0]
doc = ezdxf.readfile(src)
cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK,
                    lineweight_policy=LineweightPolicy.ABSOLUTE)
names = [n for n in doc.layout_names_in_taborder() if n != "Model"]
with PdfPages(stem + "_Vorschau.pdf") as pdf:
    for i, name in enumerate(names, 1):
        fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
        ax = fig.add_axes([0, 0, 1, 1])
        lay = doc.layouts.get(name)
        Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(lay, finalize=False)
        ax.set_xlim(0, 420)
        ax.set_ylim(0, 297)
        ax.set_aspect("equal")
        ax.axis("off")
        pdf.savefig(fig, facecolor="white")
        fig.savefig(f"{stem}_Blatt{i}_Vorschau.png", dpi=200, facecolor="white")
        plt.close(fig)
print("Vorschau:", stem + "_Vorschau.pdf", names)
