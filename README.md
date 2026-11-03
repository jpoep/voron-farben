# Voron Color Preview

A browser-based color preview for the Voron 2.4. Pick a palette or set your own colors per part role and see them on a full 3D model of the printer.

**Live:** https://jpoep.github.io/voron-farben/

## Pages

- **3D preview** (`index.html`): palette presets, free hex colors for each role (primary, accent, chains, frame), panel and lighting options, front/angle/top views, favorites (heart a preset or your current colors; saved in localStorage), and share links: every palette can be shared as a URL (`?palette=rrggbb-rrggbb-rrggbb-rrggbb`, colors in role order) that opens a view with only the model and that palette. The model is only downloaded on request, with a progress bar, and kept in the browser cache for later visits.
- **Palette board** (`palettes.html`): a 2D swatch board of three-color palettes around a mint base, with a simplified front view of the printer.

## Model

`voron24.glb` is built from the official [Voron 2.4r2 CAD](https://github.com/VoronDesign/Voron-2) by Voron Design (GPL-3.0). It is Draco-compressed (~6 MB) and stored with Git LFS.

The CAD only exists in the 250 mm size. The printed parts are identical across sizes, so the colors and their placement match the 300 and 350 mm builds.

To rebuild it:

```sh
tools/build-model.sh            # writes voron24.glb
```

Requirements: `DRAWEXE` (OpenCASCADE), Python 3, Node.js. The script downloads the STEP assembly, meshes it with OpenCASCADE, then runs `tools/classify.py`, which:

- removes overlapping alternative parts that the STEP export contains side by side (300/350 mm skirts, other controller boards, the D2F endstop pod, 6 mm Z tensioners, the logo plate in place of the display, …)
- assigns each printed part a color role based on its CAD color and assembly path, stored as the material name (`1_first_color`, `2_second_color`, `3_chains`, `4_frame`, `panels`)

Finally `gltf-transform` merges meshes per material and applies Draco compression.

## Development

The pages are static files. Serve the repository root with any static file server, for example:

```sh
python3 -m http.server
```

A server is needed because browsers don't load the model from `file://`.

## Deployment

`.github/workflows/pages.yml` deploys to GitHub Pages on every push to `main`. It checks out the LFS model and publishes only the two pages and the model.

## License

The 3D model is derived from the Voron Design CAD and is licensed under GPL-3.0.
