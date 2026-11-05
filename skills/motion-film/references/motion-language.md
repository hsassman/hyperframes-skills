# Motion language (GSAP)

Everything is a tween on one paused timeline with an absolute start time. Patterns that read as "studio":

## Reveals
- **Window reveals** with `clip-path: inset(...)` from a side (`up`, `left`, `iris`), `expo.out`, 0.9 s; stagger windows by
  0.12–0.15 s. Slow Ken Burns inside (scale 1.08 → 1.0 over 7–8 s, `sine.out`).
- **Titles:** headline rises out of a mask (`yPercent 118 → 0`, `power4.out`, 0.8 s) or letters de-blur (stagger 0.045);
  sub line rises word by word 0.35 s later. Chip slides in first.
- **Stickers** pop (`back.out(1.8)`, scale 0.85 → 1, slight rotation). **Polaroids** drop with `back.out(1.5)`.

## Drawing on (SVG)
- `pathLength="1"` + `stroke-dasharray="1 1"` + dashoffset 1 → 0. Illustrations draw part by part: outline, then the flat
  offset fill fades in behind it, then details.
- **Edge boil:** an SVG `feTurbulence` + `feDisplacementMap` filter on all drawn elements, its `seed` stepped at 10 fps by a
  timeline tween (filmkit does this). 2–5 px displacement; more looks broken.
- Morphing shapes (MorphSVGPlugin) for "this becomes that" beats (ball → roll → finished product).

## Numbers
Counters count with `power2.out` over 1–1.5 s and land on a downbeat. Format with separators. Big (150 px, 800 weight).

## Transitions (motivated, one idea each)
| Transition | Feels like | Use when |
|---|---|---|
| Band wipe | a colour sweep from the next chapter | moving into a new phase |
| Whip pan | energy, speed | between two busy layouts on the same ground |
| Object becomes the world | the illustration scales up to fill frame | an object leads into its next stage |
| Strip wipe | physical, tactile (tape, ribbon, a paper strip) | crafted or hands-on subjects |
| Texture cover | a texture (smoke, paper, fabric, ink, clouds) creeping in from the edges | a change of mood, place or atmosphere |
| Panel wipe | a panel (door, curtain, wall, page) drops over the frame and lifts on the next scene | inside to outside, before to after |
| Cloud pass | camera tilts up through clouds and descends | from ground level to a map / overview |
| Burst | a splash, puff or confetti from a point fills frame | into an end card or a reveal |
Avoid repeating a transition type within 20 s. Avoid circular irises and circle floods as a house style — they read cheap.

## Easing defaults
`expo.out` reveals, `power4.out` type, `back.out` pops, `power2.inOut` draws, `sine.inOut` drifts, `power3.in` whip out.
