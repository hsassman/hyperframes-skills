# Generated assets (image models)

Use an image model (ChatGPT image generation, GPT Image, Gemini, Firefly…) for **textures and effects**: smoke, steam,
clouds, mist, ink in water, splashes, bursts, sparks, light leaks, bokeh, particles, paper, fabric, concrete, wood, metal,
stone, foliage, water surfaces, skies. Never for text, logos, labels, printed packaging, real people's faces, or the product itself.

## Prompting for compositing
- Ask for the element **on a pure black background**, centred, no text, no logo, no watermark, photorealistic, high detail,
  "edges fade softly into black". Black backgrounds turn into clean alpha; white or busy ones don't.
- For full-frame textures (ground surfaces), ask for top-down, evenly lit, no vignette, no objects.
- Generate one asset per message and wait for it; parallel tabs garble prompts.

## Cutting out and grading (`kit/assets/prep.py`)
- `cutout` — alpha from luminance (`--lo/--hi/--gamma`), **un-premultiplied** edges (otherwise wisps get a grey cut-out
  fringe), optional `--feather` so the frame edge never shows, `--blur` for powdery softness, `--lift` to lighten.
- `sprite` — square particle texture for `FILM3D.particles({sprite})`.
- `tint` — recolour by luminance between two brand colours (icons, particles, shapes).
- `texture` — keep only a material's fine detail (high-pass) and lay it over your designed ground. Generated materials are
  often the wrong colour; this keeps the fibre and your grade.
- Always check the result on the actual ground it will sit on (snapshot), not on a checkerboard.

## Getting files out of a browser session
If generation happens in a browser tab you control, download the image from its blob URL with an `<a download>` click, then
move it into the project. Some browsers block a page from triggering several downloads in a row — pack several files into
one JSON (base64) and split it locally, or download one file per page load.

## Credits
Record the tool and prompt for each generated asset in `assets/README.md` (what it is, prompt, date).
