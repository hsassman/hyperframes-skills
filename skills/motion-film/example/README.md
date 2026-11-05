# Demo film: "From seed to cup" (fictional brand)

A 20-second film for a made-up coffee brand. It runs every part of the kit with nothing to download: procedural grounds,
rough.js illustrations, GSAP titles and annotation, a 3D particle beam and a 3D map (Three.js), shutter and burst
transitions, a sound pass placed from picture events, mastering, a storyboard and a cut-down.

```bash
./setup.sh                        # node deps, Kenya geo, illustrations, fonts, GSAP, film3d bundle, grounds, index.html
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
(see `../references/sound.md`). Swap the brand by editing the `Theme(...)` line in `gen.py`.
