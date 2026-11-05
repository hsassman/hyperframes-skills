# Skills

A growing collection of Claude skills. The first is **motion-film**: a complete workflow for studio-quality motion films
built as code — real footage and photos, hand-drawn animated graphics, kinetic type, GSAP motion, Three.js 3D and a
real-recorded sound mix — rendered with [HyperFrames](https://github.com/heygen-com/hyperframes) to MP4, with
storyboards, shorter cut-downs and delivery checks along the way. It works for any subject, brand, length or aspect ratio.

## Install

Needs git, Python 3.10+, Node 18+ and FFmpeg 6.1+.

```bash
git clone https://github.com/hsassman/skills && cd skills
./install.sh --kit            # macOS / Linux      → ~/.claude/skills
.\install.ps1 -Kit            # Windows PowerShell → %USERPROFILE%\.claude\skills
```
- `--target DIR` installs somewhere else (e.g. `./.claude/skills` for one project). HyperFrames' own CLI always puts its
  skills in `~/.claude/skills`.
- `--no-upstream` installs only this repo's skills.
- `--kit` also installs the film kit's Node and Python packages and builds the 3D bundle.
- Re-run the installer after `git pull` to update.

Third-party skills are installed **from their own repositories at pinned commits** (`manifest.json`), never copied in,
and keep their own licences.

## What gets installed

| Skill | Source | What it does |
|---|---|---|
| **motion-film** | this repo | The workflow: brief → media → story on the music's bar grid → composition → storyboard review → sound → render → QA → cut-downs → delivery. Ships the `kit/` (composition builder, Three.js layers, map geography, hand-drawn illustration builder, asset prep, mixer, mastering, cut-downs, QA, storyboard builder) and a runnable 20 s demo. |
| earshot | wrapper → [Leonxlnx/earshot](https://github.com/Leonxlnx/earshot) | Measures, ranks and compares audio so the agent can judge sound it can't hear. |
| real-sfx | wrapper → [Clipwing/skills](https://github.com/Clipwing/skills) | Looks at a rendered film and places real recorded effects on the exact frames. |
| hyperframes, hyperframes-cli, hyperframes-registry, media-use | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) via its CLI | The HyperFrames render contract, CLI, block registry and media helpers. |
| threejs-* | [CloudAI-X/threejs-skills](https://github.com/CloudAI-X/threejs-skills) | Three.js technique: scenes, geometry, materials, lighting, shaders, post-processing, performance and more. |

Wrapper skills are small `SKILL.md` files that clone their upstream at a pinned commit and hand over to it.

## Tools, APIs and content sources

The full list, with licences, is in
[`skills/motion-film/references/tools-and-sources.md`](skills/motion-film/references/tools-and-sources.md). In short:

- **Render and motion:** HyperFrames CLI and desktop app, GSAP 3 (with MorphSVG), Three.js, esbuild, rough.js,
  world-atlas / topojson (Natural Earth), Fontsource fonts.
- **Audio:** FFmpeg, ffmpeg-normalize, numpy/soundfile, earshot, Clipwing real-sfx.
- **Music and sound effects:** Pixabay Music and Pixabay Sound Effects (Pixabay Content License), Freesound (website and
  API, filter for CC0/CC BY), Openverse API (no key needed).
- **Images and footage:** the subject's own media first; an image model (e.g. ChatGPT image generation) for textures and
  effects only; Pexels and Pixabay APIs for licensed stock when there is no own media.
- **Review:** storyboard pages published as Claude artifacts.

## Using it

Ask Claude for a film the way you would brief a studio — *"Make a 45-second launch film for our app from the screen
recordings in ./media, vertical for social"* or *"A 70-second brand story from these clips, music only"*. The
`motion-film` skill asks the questions that matter, then runs the phases with gates (storyboard approval before the long
render) and pulls in the other skills as it goes.

To see every tool work before using your own media:
```bash
cd ~/.claude/skills/motion-film/example && ./setup.sh && npx hyperframes preview
```
See [`docs/workflow.md`](docs/workflow.md) for the pipeline at a glance and
[`docs/adding-a-skill.md`](docs/adding-a-skill.md) to add a new skill.

## Licence

No licence has been chosen for this repository's own skills yet; until one is added, all rights are reserved by the
owner. Third-party skills installed by the installers keep their own licences (see `manifest.json`).
