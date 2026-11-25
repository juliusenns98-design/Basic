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

# Mittelstufenprojekt TOP SECRET 2.0 (DXF, 2 Blätter)

Zwei wandhängende Schränke à 350 × 400 × 305 mm, je 2 Schubkästen (BLUM MOVENTO TIP-ON NL 250),
Innenkorpus Spanplatte schwarz 19, Außenrahmen Eiche 20, Geheimfach mit doppeltem Boden.

- `TopSecret_Schubkastenschrank.dxf` – Blatt 1 (x 0…420): Dreitafelprojektion + Schnitt A-A 1:5;
  Blatt 2 (x 440…860): Details B (Häfele-Aufhängung), C (Verbindung), D (doppelter Boden), Stückliste
- `TopSecret_Schubkastenschrank_Vorschau.pdf` – beide Blätter als PDF
- `top_secret.py` – erzeugt die DXF; `vorschau_blaetter.py Datei.dxf 0 440` – Vorschau
- Statusangaben in der Zeichnung: (H) Herstellerangabe, (G) gewählt, n.f. noch festzulegen
