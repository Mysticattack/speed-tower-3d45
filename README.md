# Speed-Tower für Dremel 3D45

Fertiger G-code des Printables-Modells [Speed tower – test your maximum print speed](https://www.printables.com/model/22601-speed-tower-test-your-maximum-print-speed) von Print-3D, neu geslict für den **Dremel 3D45** (0,4 mm Düse, PLA).

**Datei zum Drucken: `speed-tower-3d45.gcode`** – auf USB-Stick kopieren, am Drucker auswählen, starten. Kein Slicer nötig.

## Was der Turm macht

20 mm Würfel mit Fasen, scharfen Ecken, Halbkugel und Überhängen. Die **Außenwand** wird alle 15 mm um 10 mm/s schneller. Man druckt einmal und sieht am Bauteil, ab welcher Stufe die Wand rau wird, glänzt, aufreißt oder unterextrudiert.

| Höhe | Außenwand |
|------|-----------|
| Z 0–16 mm (Sockel + 1. Stufe) | 15 mm/s |
| Z 16–31 mm | 20 mm/s |
| Z 31–46 mm | 30 mm/s |
| Z 46–61 mm | 40 mm/s |
| Z 61–76 mm | 50 mm/s |
| Z 76–91 mm | 60 mm/s |
| Z 91–106 mm | 70 mm/s |
| Z 106–121 mm | 80 mm/s |
| Z 121–136 mm | 90 mm/s |

Der Sockel (40 × 40 mm) lässt sich nach dem Druck abbrechen, damit man mehrere Materialien vergleichen kann. Der Hauptwürfel muss **exakt 20,0 mm** messen – stimmt das nicht, passt der Flow nicht.

## Druckdaten

- Layer 0,15 mm (erste Lage 0,2 mm), 2 Perimeter, 0 % Infill, 1 Skirt-Loop
- Düse 215 °C, Bett 60 °C, Bauteilkühlung 100 % ab Lage 2
- Innenwand konstant 45 mm/s, Außenwand = Stufentabelle oben
- Relevante Cooling-Einstellung des Originals beibehalten: „langsamer drucken, wenn Layerzeit unter **1 s**" (`slowdown_below_layer_time = 1`, `min_print_speed = 15`)
- Slicer: PrusaSlicer 2.9.4, G-code-Flavor Marlin, relative E-Distanzen
- Bettkoordinaten zentriert: −127,5 … +127,5 / −77,5 … +77,5 (so erwartet es der 3D45)
- Verbrauch 13,5 g PLA, geschätzte Druckzeit 1 h 26 min

## Start-/End-G-code

Start (Community-Profil für den 3D45, ergänzt um Temperatur-Warten vor dem Primen):

```
M190 S60
M104 S215
G28
M109 S215
G1 Z50.00 F400
G92 E0
G1 F200 E3
G92 E0
M132 X Y Z A
M907 X100 Y100 Z50 A100
G1 X-100 Y-75 Z0.3 F3000   ; Purge-Linie linke Bettkante
G92 E0
G1 X-65 E8 F800
G92 E0
G1 Z2 F3000
```

Ende: `M104 S0 / M140 S0 / G92 E1 / G1 E-1 F300 / G162 Z F600 / G162 X Y F2000 / M84`

Die Datei enthält nur: G1, G21, G28, G90, G92, M83, M84, M104, M106, M107, M109, M132, M140, M190, M907, G162 – keine Prusa-Spezifika wie M862/M900/M73/M201.

## Erwartung

Der 3D45 macht mit 0,4 mm Düse real etwa 40–60 mm/s Außenwand sauber mit. Die Stufen ab 70 mm/s sind da, um zu zeigen, wo Schluss ist – dass die oberen Bänder schlechter aussehen, ist das Ergebnis, nicht ein Fehler. Wenn du vorher schon weißt, dass du nur bis 60 willst: untere Hälfte reicht, Rest ist Bonus.

## Selbst slicen / anpassen

- `speed-tower-3d45.3mf` – Projektdatei mit den Höhen-Stufen als Layer-Config-Ranges (in PrusaSlicer öffnen, Temperaturen/Material anpassen, neu slicen). Die Stufen stecken in `Metadata/Prusa_Slicer_layer_config_ranges.xml` und bleiben beim Ändern von Temperaturen erhalten.
- `dremel3d45.ini` – Drucker-/Print-/Filamentprofil (PrusaSlicer, `--load dremel3d45.ini`).

Original-Modell: CC-Lizenz des Autors auf Printables beachten, Quelle ist oben verlinkt.

## Geprüft

Jedes Band wurde im fertigen G-code nachgezählt (Anteil der Außenwand-Segmente mit der Soll-Geschwindigkeit):

```
Z   0- 16: Soll 15 -> Ist  15 mm/s (98,9 %)  OK
Z  16- 31: Soll 20 -> Ist  20 mm/s (99,6 %)  OK
Z  31- 46: Soll 30 -> Ist  30 mm/s (99,8 %)  OK
Z  46- 61: Soll 40 -> Ist  40 mm/s (100,0 %) OK
Z  61- 76: Soll 50 -> Ist  50 mm/s (99,8 %)  OK
Z  76- 91: Soll 60 -> Ist  60 mm/s (99,5 %)  OK
Z  91-106: Soll 70 -> Ist  70 mm/s (99,7 %)  OK
Z 106-121: Soll 80 -> Ist  80 mm/s (99,7 %)  OK
Z 121-136: Soll 90 -> Ist  90 mm/s (99,7 %)  OK
```

Restliche Segmente sind Gap-Fill (40 mm/s), wie im Original auch.

Alle Koordinaten liegen im Bett, Z max 135,8 mm < 170 mm Bauhöhe.
