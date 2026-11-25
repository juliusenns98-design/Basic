# Stapelkasten Z-10-1 (DXF)

Nachzeichnung der Zeichnung "Stapelkasten" (Z-10-1) als AutoCAD-DXF, A3 quer.

- `Stapelkasten_Z-10-1.dxf` – Zeichnung zum Öffnen in AutoCAD
- `Stapelkasten_Z-10-1_Vorschau.pdf` / `.png` – Vorschau
- `stapelkasten.py` – erzeugt die DXF (`pip install ezdxf numpy`, dann `python3 stapelkasten.py`)
- `hlr.py` – berechnet sichtbare Kanten für Ansichten, Isometrie und Explosion

Alle Maße stehen oben in `stapelkasten.py` und lassen sich dort ändern.

# Schubkastenschrank aus Eiche (DXF)

Dreitafelprojektion (Projektionsmethode 1) des wandhängenden Schubkastenschranks
700 × 400 × 290 mm mit Schnitt A-A, A3 quer, Maßstab 1:5.

- `Schubkastenschrank_Eiche.dxf` – Zeichnung zum Öffnen in AutoCAD (Layer nach Linienart)
- `Schubkastenschrank_Eiche_Vorschau.pdf` / `.png` – Vorschau
- `schubkastenschrank.py` – erzeugt die DXF; nicht festgelegte Maße (s, m, f, …) stehen
  oben als Darstellungswerte und sind in der Zeichnung mit „n.f.“ gekennzeichnet
- `vorschau.py` – rendert eine DXF als PDF/PNG (`python3 vorschau.py Datei.dxf`)
