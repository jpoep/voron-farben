# Voron-Farben

Farbschema für den Voron 2.4 (300 mm). Grundfarbe: Prusament ASA `#00CA97` (Mint).

## 3D-Viewer

Online über GitHub Pages (wird bei jedem Push auf `main` per GitHub Actions neu gebaut).

Lokal:

```sh
python3 -m http.server 8791 --bind 127.0.0.1 --directory ~/projects/voron-farben
```

Dann http://127.0.0.1:8791/ öffnen. Der Server ist nötig, weil der Browser das Modell nicht direkt von `file://` lädt.

- `index.html` – Viewer mit Paletten, freien Hex-Farben pro Rolle (Primär, Akzent, Ketten, Rahmen), Panels und Licht. Das Modell wird erst nach Klick geladen, mit Fortschrittsanzeige.
- `voron24.glb` – Modell aus dem offiziellen Voron-2.4r2-CAD ([VoronDesign/Voron-2](https://github.com/VoronDesign/Voron-2), GPL-3.0), Draco-komprimiert (~6 MB), per Git LFS versioniert. Das CAD gibt es nur in der 250-mm-Größe; Teile und Farbrollen sind identisch zur 300er.
- `tools/build-model.sh` – baut `voron24.glb` neu aus dem STEP (braucht `DRAWEXE` aus opencascade, Python 3, Node). `tools/classify.py` entfernt überlappende CAD-Varianten (Skirts 300/350, weitere Controller, D2F-Endstop, 6-mm-Tensioner …) und ordnet Teile per CAD-Farbe und Baugruppenpfad den Rollen zu.
- `voron-paletten.html` – erste 2D-Übersicht, auch als Artifact: https://claude.ai/artifact/318bVBVHQwZhrfEediEd5P

Das frühere Modell `voron_v2_default.glb` (von 3dprinter-color-configurator.com, Lizenz unklar) liegt nur lokal und ist per `.gitignore` ausgeschlossen.

## Stand (2026-11-03)

Favoriten: Flieder `#AC96C6` + Koralle `#F2707A`, vor allem „Pflaume“ (Aubergine `#3A2440`), dazu Creme/Butter-Gelb, Korallenriff (Koralle führt) und Petrol.

Beschaffung ABS/ASA (EU):
- Koralle: eSUN ABS Pink `#FB7A8C` kommt nah ran (Spectrum Coral ist eher Lachs/Beige).
- Aubergine: Polymaker ABS Dark Purple.
- Petrol: Polymaker ASA Teal (heller) oder Nobufil ABSx Industrial Petrol.
- Flieder und Pastell-Gelb: in der EU nicht als ABS/ASA gefunden. KVP Pastel Purple gibt es nur in den USA.
- Wunschfarben: 3D Trček (Slowenien, auf Anfrage, RAL/Pantone/Muster), ColoriLab (ABS/ASA ab ca. 2–5 kg, nicht geprüft).

Nächster Schritt: echte Hex-Werte der gewählten Filamente sammeln, dann Mockup damit.
