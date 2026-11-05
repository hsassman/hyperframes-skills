# Three.js layers in a HyperFrames film

Read the `threejs-*` skills for scene technique. This file covers making 3D render correctly inside a seeked video.

## The contract
- Each 3D layer draws into its own `<canvas>` inside a timed clip (`film.canvas3d(id, start, dur, z)`).
- Rendering is driven by `hf-seek` (`e.detail.time`) — `film3d.js` listens and calls `render(t)` on every layer active at t.
  No requestAnimationFrame, no clocks, no state carried between frames: frames are rendered out of order.
- Anything loaded asynchronously (textures, sprites) registers a promise in `window.__hf.buildReady[key]` so the renderer
  waits for it.
- `preserveDrawingBuffer: true`, `setPixelRatio(1)`, fixed 1920×1080.
- Seeded randomness only (`mulberry32`).

## Bundling
Write layers in `kit/node/src/film3d.js` (ES modules, `three` from npm) and bundle to one IIFE:
`npm run build:3d` → `dist/film3d.js`, copied to `assets/`. Post-processing (EffectComposer → RenderPass →
UnrealBloomPass → OutputPass) and `Line2` fat lines work in the bundle.

## Layers provided
- `FILM3D.particles(canvasId, {start,end,count,size,color,seed,drift,focus,fadeIn,fadeOut,beam,shape,sprite})` —
  dust in a light beam, snow, sparks, crystals; depth-of-field via point size and alpha.
- `FILM3D.map(canvasId, {...})` — the country from `assets/geo.js` extruded with bevels, neighbours flat, a hand-drawn
  coastline that boils at 10 fps, routes (tubes with a travelling head and packets) from `home` to `cities` (each with an
  `at` time and an HTML label id positioned every frame), pins that pop, a camera that descends from above
  (`highStart`), settles into a tilted orbit and pushes into home at the end (`pushIn`), `viewShift` to free screen
  space for text, and `follow` to pin an HTML element (e.g. a burst) to home's screen position.
  Generate geography: `node geo.mjs --main <ISO numeric> [--insets ...] [--neighbours ...] [--bbox ...] --out assets/geo.js`.

## Performance
Software WebGL (headless Linux, no GPU) is slow: keep shadow maps ≤ 2048, one composer per canvas, particles ≤ 1500,
and only keep canvases alive while their layer is on screen. On a desktop GPU the same scene renders in real time.
