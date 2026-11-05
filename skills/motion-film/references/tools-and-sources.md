# Tools, libraries, APIs and content sources

Everything the workflow uses, what it is for, and how it is licensed. Check each source's current terms before a
commercial release — licences change.

## Rendering and composition
| Tool | Used for | Notes |
|---|---|---|
| [HyperFrames](https://github.com/heygen-com/hyperframes) CLI (`npx hyperframes`) | lint, preview, snapshot, render HTML compositions to MP4 | Needs Chrome / chrome-headless-shell; pinned in `manifest.json` |
| HyperFrames desktop app | hand edits on a timeline, chatting with an agent inside the project | File › Open Folder on the project |
| [GSAP](https://gsap.com) 3 + MorphSVGPlugin | every tween on one paused timeline; shape morphs | Free, including all plugins (npm `gsap`) |
| [Three.js](https://threejs.org) | 3D layers: particles, maps, post-processing (bloom), fat lines | MIT (npm `three`) |
| [esbuild](https://esbuild.github.io) | bundles the 3D layers into one IIFE (`assets/film3d.js`) | MIT |
| [rough.js](https://roughjs.com) | hand-drawn hachure shading in illustrations | MIT |
| [world-atlas](https://github.com/topojson/world-atlas) + [topojson-client](https://github.com/topojson/topojson-client) | country outlines for the 3D map (Natural Earth data) | ISC; Natural Earth is public domain |
| [Fontsource](https://fontsource.org) | self-hosted web fonts (`@fontsource/*`), copied into `assets/fonts` | Fonts keep their own licences (most are OFL) |
| Python: numpy, Pillow, opencv-python-headless | grounds, sprites, cut-outs, photo clean-up | `kit/requirements.txt` |

## Audio
| Tool | Used for | Notes |
|---|---|---|
| [FFmpeg](https://ffmpeg.org) 6.1+ | decode, filter, mux, encode, loudness measurement (`ebur128`), QA scans | — |
| [ffmpeg-normalize](https://github.com/slhck/ffmpeg-normalize) | two-pass loudness normalisation in `master.py` | pip |
| numpy + soundfile | mixing engine (`mixkit.py`), music grid, cut-down splices | pip |
| [earshot](https://github.com/Leonxlnx/earshot) (skill) | measure, rank, compare and check realness of audio you can't hear | Local; ~1.1 GB of models on first run |
| [Clipwing real-sfx](https://github.com/Clipwing/skills) (skill) | look at a rendered film and place real effects on exact frames; 78 CC0 UI sounds | MIT / CC0 |

## Music and sound-effect sources
| Source | Access | Licence (check per item) |
|---|---|---|
| [Pixabay Music](https://pixabay.com/music/) | browse and download in a browser | Pixabay Content License: free commercial use, no attribution required |
| [Pixabay Sound Effects](https://pixabay.com/sound-effects/) | browse and download in a browser (the Pixabay API covers images and video, not audio) | Pixabay Content License |
| [Freesound](https://freesound.org) | website, or the [Freesound API](https://freesound.org/docs/api/) (free key; OAuth2 for original-quality downloads) | Per sound: CC0, CC BY (credit), CC BY-NC (not for commercial use) — filter `license:"Creative Commons 0"` or CC BY |
| [Openverse](https://openverse.org) | [Openverse API](https://api.openverse.org) — no key needed for light use, `/v1/audio/?q=…&license_type=commercial` | CC licences and public domain; keep the attribution it returns |
| Your own recordings | phone or field recorder | Yours — the best source for the subject's own sounds |

Record `file, title, author, url, licence` for every download in `sources.json` at the moment you download it;
`kit/audio/credits.py` turns it into the credits sheet.

## Images, footage and generated assets
| Source | Used for | Notes |
|---|---|---|
| The subject's own footage and photos | the hero media | Always preferred |
| ChatGPT image generation (or another image model) | textures and effects on black: smoke, clouds, splashes, bursts, paper, fabric | Never for text, logos, products or real people; cut out with `kit/assets/prep.py` |
| [Pexels](https://www.pexels.com/api/) and [Pixabay](https://pixabay.com/api/docs/) APIs | licensed stock video and photos when the subject has none | Free keys; keep a licence note per file |

## Voice-over and captions (optional)
| Tool | Used for | Notes |
|---|---|---|
| [Qwen TTS](https://github.com/QwenLM) (self-hosted) | narration from a script, chunked and stitched (`qwen-tts-voiceover` skill) | Runs on your own server |
| [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) | denoising recorded or generated voice (`audio-mastering` skill) | MIT / Apache-2.0 |
| [WhisperX](https://github.com/m-bain/whisperX) | word-level timings and captions (`caption-sync` skill) | BSD-2 |

## Companion skills and what they cover
| Skill | Phase |
|---|---|
| `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use` | composition, render, ready-made blocks |
| `threejs-*` | 3D technique |
| `script-structure` | brief and beat sheet |
| `stock-footage-sourcer` | licensed stock (Pexels, Pixabay APIs) |
| `ffmpeg-processor`, `ffmpeg-skill` | media prep, edits, exports |
| `real-sound`, `real-sfx`, `openverse-audio`, `earshot` | sound sourcing, placement, measurement |
| `audio-mastering`, `qwen-tts-voiceover`, `caption-sync` | voice-over, loudness, captions |

## Review and delivery
| Tool | Used for |
|---|---|
| Claude artifacts | publishing the storyboard page (frames as supporting files) for phone review; republish to the same link each round |
| `kit/audio/finish.py` | mux, QA report (specs, black/frozen scan, loudness, frame count), size-targeted share encodes, contact sheets |
