#!/usr/bin/env bash
# Builds voron24.glb from the official Voron 2.4r2 CAD (GPL-3.0, github.com/VoronDesign/Voron-2).
# Needs: curl, unzip, DRAWEXE (opencascade), python3, npx (node).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
work="${WORK:-$(mktemp -d)}"
out="${1:-$here/../voron24.glb}"
mkdir -p "$work/dl" "$work/step"
curl -sSL -o "$work/dl/step.zip" \
  https://github.com/VoronDesign/Voron-2/raw/refs/heads/Voron2.4/CAD/Voron_2.4r2_Assembly_STEP.zip
unzip -o -q "$work/dl/step.zip" -d "$work/step"
cat > "$work/convert.tcl" <<TCL
pload XDE OCAF MODELING VISUALIZATION
ReadStep D $work/step/Voron_2.4r2_Assembly.step
XGetOneShape S D
incmesh S 0.25 -a 25 -parallel
WriteGltf D $work/raw.glb -mergefaces -nodeNameFormat prodOrInst
exit
TCL
DRAWEXE -b -f "$work/convert.tcl"
python3 -I "$here/classify.py" "$work/raw.glb" "$work/classified.glb"
npx -y @gltf-transform/cli@4.1.1 optimize "$work/classified.glb" "$out" \
  --compress draco --texture-compress false --simplify false --palette false --instance false --join true --flatten true
echo "wrote $out"
