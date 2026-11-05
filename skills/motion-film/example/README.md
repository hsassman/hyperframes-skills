# Demo film (fictional organisation)

A 20-second film for a made-up tree-planting organisation. It runs every part of the kit with nothing to download:
procedural grounds, rough.js illustrations, GSAP titles and annotation, a 3D particle beam and a 3D map (Three.js), a
texture-cover transition, a burst that follows the map into the end card, a sound pass placed from picture events,
mastering, a storyboard and a cut-down. Replace the content to make any film — `gen.py` is the film.

```bash
./setup.sh                        # node deps, geography, illustrations, fonts, GSAP, 3D bundle, grounds, index.html
npx hyperframes lint              # 0 errors (nested_structure warnings are expected)
npx hyperframes preview           # scrub it in the browser
python3 sound.py --demo           # synthesised placeholder music/effects -> audio/out/mix_master.wav (-14 LUFS)
npx hyperframes render . -o renders/demo_picture.mp4 -q high
python3 ../kit/audio/finish.py mux renders/demo_picture.mp4 audio/out/mix_master.wav renders/demo.mp4
python3 ../kit/audio/finish.py qa renders/demo.mp4
python3 ../kit/storyboard/build_storyboard.py storyboard.json . storyboard/
python3 ../kit/audio/cutdowns.py cutdowns.json audio && python3 ../kit/audio/cutdowns.py cutdowns.json picture
```
On Linux without a desktop Chrome, set `PRODUCER_HEADLESS_SHELL_PATH` to a chrome-headless-shell binary first.

The `--demo` sound is synthesised so the pipeline runs offline; a real film uses licensed recordings
(`../references/sound.md`, `../references/tools-and-sources.md`). Change the look in the `Theme(...)` line of `gen.py`,
the country with the `geo.mjs` line in `setup.sh`, and the drawings in `../kit/node/illos.mjs`.
