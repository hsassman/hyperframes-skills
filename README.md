# Skills

A growing collection of Claude skills. The first set is a complete **motion-film workflow**: real footage plus
hand-drawn illustration, GSAP motion, Three.js layers and a real-recording sound mix, built as code with
[HyperFrames](https://github.com/heygen-com/hyperframes) and rendered to MP4, with storyboards, cut-downs and
delivery checks along the way.

## Install

Needs git, Python 3.10+, Node 18+ and FFmpeg 6.1+.

```bash
git clone https://github.com/hsassman/skills && cd skills
./install.sh --kit            # macOS / Linux  → ~/.claude/skills
.\install.ps1 -Kit            # Windows PowerShell → %USERPROFILE%\.claude\skills
```
Options: `--target DIR` (e.g. `./.claude/skills` to install into one project; HyperFrames' own CLI always installs its skills to `~/.claude/skills`), `--no-upstream` (only this repo's
skills), leave out `--kit` to skip the film kit's Node/Python packages. Re-run the installer after `git pull` to update.

Third-party skills are installed **from their own repositories at pinned commits** (see `manifest.json`), never
copied into this repo. They keep their own licences.

## What's inside

| Skill | What it does |
|---|---|
| **motion-film** | The end-to-end workflow: brief → media audit → story on a music grid → composition → storyboard review → sound → render → QA → cut-downs → delivery. Ships the `kit/` (filmkit composer, Three.js layer bundle, geography, rough.js illustrations, asset prep, mixer, master, cut-downs, storyboard builder) and a runnable 20 s `example/`. |
| script-structure | Hook / setup / escalating beats / payoff structure and a scoring rubric for scripts and beat sheets. |
| stock-footage-sourcer | Licensed stock footage from Pexels and Pixabay with a licence sidecar per clip. |
| ffmpeg-processor | Probing, trimming, joining, transcoding, muxing and export settings with FFmpeg. |
| audio-mastering | Denoise then two-pass loudness normalisation to −14 LUFS / −1 dBTP. |
| caption-sync | Word-level captions with WhisperX (SRT + JSON timings). |
| qwen-tts-voiceover | Chunked, stitched voice-over from a self-hosted Qwen TTS service. |
| openverse-audio | Openly licensed sound effects and music from Openverse with attribution. |
| earshot *(wrapper)* | Measure, compare and critique audio you can't hear ([Leonxlnx/earshot](https://github.com/Leonxlnx/earshot)). |
| real-sound *(wrapper)* | Full soundtrack from real licensed recordings (earshot's companion skill). |
| real-sfx *(wrapper)* | Frame-accurate sound effects for motion videos ([Clipwing/skills](https://github.com/Clipwing/skills)). |
| ffmpeg-skill *(wrapper)* | 42 FFmpeg editing tools ([kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill)). |
| threejs-* *(installed)* | The Three.js skills (fundamentals, geometry, materials, lighting, shaders, post-processing, performance and more) from [CloudAI-X/threejs-skills](https://github.com/CloudAI-X/threejs-skills). |
| hyperframes *(installed)* | HyperFrames' own skills, installed by its CLI. |

Wrapper skills are small `SKILL.md` files that clone their upstream at a pinned commit and hand over to it.

## Using it

Ask Claude for a film the way you would brief a studio: *"Make a 70-second process film from the clips in ./media for
a brand that …"*. The `motion-film` skill runs the phases with gates (questions, storyboard approval, render), and
pulls in the other skills as it goes. To see every tool work before using your own media:

```bash
cd ~/.claude/skills/motion-film/example && ./setup.sh && npx hyperframes preview
```

See [`docs/workflow.md`](docs/workflow.md) for the whole pipeline and [`docs/adding-a-skill.md`](docs/adding-a-skill.md)
to contribute a new skill.

## Licence

No licence has been chosen for this repository's own skills yet — until one is added, all rights are reserved by the
owner. Third-party skills installed by the installer keep their own licences (listed in `manifest.json`).
