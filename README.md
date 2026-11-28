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

## TOP SECRET 2.0 – aktueller Stand (v2)

Eichenmantel aus 4 Platten um zwei verschraubte schwarze Innenkorpusse, 700 × 400 × 315 mm,
Schubkästen mit Doppel und Fingerzinken, Geheimfach, Häfele-Aufhängeschienen ineinander.
Daten: `TopSecret_Konstruktionsdaten.md`.

- `TopSecret_v2.dxf` – 3 A3-Blätter: Blatt 1 Ansichten 1:10, Detail E Gehrung 1:1, Stückliste (x 0);
  Blatt 2 Schnitt A-A + Detail C Aufhängung 1:1 (x 440); Blatt 3 Schnitt B-B + Detail D Fingerzinken 1:1 (x 880)
- `TopSecret_v2_Vorschau.pdf` – alle 3 Blätter; `TopSecret_Isometrie.*` – Isometrie 1:5
- `top_secret_v2.py` / `isometrie.py` erzeugen die Zeichnungen; `vorschau_blaetter.py TopSecret_v2.dxf 0 440 880`
- Ältere Stände: `top_secret.py` (getrennte Eichenkästen) und `schubkastenschrank.py`

# Bücherregal – Schnitt B-B (Aufgabenblatt)

- `Buecherregal_Schnitt_B-B.dxf` / `_Vorschau.pdf` – waagerechter Schnitt B-B M 1:1 durch den Schubkasten
  im rechten unteren Fach (Lauf-/Streif-/Kippleisten, gezinkter Schubkasten, Doppel mit Griffloch, Rückwandfalz)
- `buecherregal_bb.py` erzeugt die Zeichnung; `zeichenhilfe.py` enthält die gemeinsamen Zeichenfunktionen

## TOP SECRET 2.0 – Endzeichnung (AutoCAD)

- `TopSecret_Endzeichnung.dxf` – Modellbereich: alle Ansichten/Schnitte/Details in wahrer Größe (mm);
  Layouts „Blatt 1“–„Blatt 3“ (A3 quer) mit Ansichtsfenstern 1:10 / 1:1, Bemaßung, Stückliste, Schriftfeld
- `TopSecret_Endzeichnung_Vorschau.pdf` – Vorschau der drei Layouts
- `top_secret_final.py` erzeugt die DXF; `vorschau_layouts.py Datei.dxf` rendert alle Layouts
