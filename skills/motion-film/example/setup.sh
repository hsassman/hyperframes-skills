#!/usr/bin/env bash
# Prepare the demo project: node deps, the Three.js bundle, geography, illustrations, fonts, GSAP and procedural assets.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODE="$HERE/../kit/node"
cd "$NODE"
[ -d node_modules ] || npm install --no-audit --no-fund
npm run -s build:3d
mkdir -p "$HERE/assets/fonts"
node geo.mjs --main 404 --neighbours 800,834,231,706,728 --out "$HERE/assets/geo.js"     # Kenya + neighbours (ISO numeric)
node illos.mjs "$HERE/assets/illos.json"
cp dist/film3d.js node_modules/gsap/dist/gsap.min.js node_modules/gsap/dist/MorphSVGPlugin.min.js "$HERE/assets/"
for f in archivo/files/archivo-latin-700-normal archivo/files/archivo-latin-800-normal \
         inter/files/inter-latin-400-normal inter/files/inter-latin-500-normal kalam/files/kalam-latin-700-normal; do
  cp "node_modules/@fontsource/$f.woff2" "$HERE/assets/fonts/"
done
cd "$HERE"
python3 make_assets.py
python3 gen.py
echo "ready: npx hyperframes lint && npx hyperframes snapshot --at 3,9,13.5,18 -o snaps"
