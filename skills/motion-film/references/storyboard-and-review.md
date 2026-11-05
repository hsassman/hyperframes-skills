# Storyboard and client review

## Build it from the real composition
Mocks drift from what renders. Snapshot the composition itself at the busiest moment of every beat plus the middle of
every transition, and lay the stills out with captions:
```bash
python3 kit/storyboard/build_storyboard.py storyboard.json path/to/project storyboard/
```
Caption each frame with what happens, why, and the sound idea. Mark transitions. Mark frames that changed since the last
round ("Updated" / "New") so the client can see the delta.

## Publish for review on a phone
Publish the folder as a web page (a Claude artifact with `frames/*.jpg` as supporting files works well; republish to the
same URL each round). Use `&nbsp;` between numbers and units (−18&nbsp;°C) so they don't wrap on phones. Put round notes
at the top: what changed, what was out of scope, what needs confirming.

## Reading feedback
- Clients often send screenshots of the storyboard. Map each screenshot to frame numbers before changing anything.
- **Scope:** if they say "only the slides I attached", change only those, then list what else would need the same change
  and offer it — don't do it unasked.
- Turn vague notes into concrete changes and confirm in one line (e.g. "make the frost nicer" → "frost creeps in from the
  edges with a cold flash, ice-blue ground, drifting snowflakes").
- Keep a running list of client taste rules (e.g. "no circles", "no dotted lines", "tagline only at the end") and apply
  them to all future work on that client.

## Before rendering
The hero render is expensive (up to an hour on CPU). Render only after the storyboard is approved, and lock the picture
(copy `index.html` and `gen.py` to `*_lock.*`) before starting.
