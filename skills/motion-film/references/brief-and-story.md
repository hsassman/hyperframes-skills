# Brief and story

## Ask before building (expensive to redo)
Ask these up front, in one round, with options where possible:
1. **Audience and job of the film** — who watches, where (site hero, social feed, sales deck, event screen, product page),
   what they should think or do after. One single-minded message.
2. **Kind of film** — brand story, product launch, explainer, process, data story, recap, teaser, title sequence. It sets
   the beat structure below.
3. **Length and formats** — hero length, shorter versions, aspect ratios (16:9 / 9:16 / 1:1 are separate compositions
   built from the same `gen.py` logic).
4. **Media** — what footage, photos, screen recordings, product renders or data exist; which are approved; what must not appear.
5. **Voice** — voice-over or music-only. Music-only films carry the story in titles and annotation; keep words short.
6. **Ending** — logo, line, call to action or nothing. Ask; don't assume.
7. **Facts** — every number, claim, name and place the film may use. Anything else is `[CONFIRM]`.
8. **Look** — colours, fonts, logo files (real files only), tone, words to avoid, references they like and *what* they
   like about each.

## Structure
Every kind of film uses the same spine, with different beats in the middle:
- **Hook (first 2–3 s):** the most striking real shot or image, full-bleed, one short line. No logo first.
- **Setup (one beat):** the promise or question in a few words.
- **Beats:** each one idea, with a one-word title, a sub line, its media or graphic, and at most one annotation pointing
  at a real detail. Examples of beat lists: process → steps; launch → problem, product, three features, proof;
  explainer → question, mechanism in 3–4 steps, result; data story → context, the number, what it means, what's next;
  recap → moments in time order. Vary beat length (3–12 s) so the pace breathes.
- **Payoff:** the strongest proof or moment (a number, a map, a montage, the product hero) on the music's biggest hit.
- **Close:** logo + line, or the call to action. Hold ≥ 2.5 s after the last element lands, then fade.

Check the beat sheet before building (the `script-structure` skill has the full scoring rubric): Does the hook land in the first line? Is the setup one beat or less? Does every
beat answer or open a question? Do lengths vary? Is the payoff explicit and tied to the hook? Is the close short and after
the payoff? Fix the weakest answer first.

## Beat sheet on a bar grid
Pick the music before timing anything (`references/sound.md` §1). At 120 BPM a bar is 2.0 s: put every beat start on a
bar line, land titles on downbeats, and place the payoff on the strongest phrase start. Write the beat sheet as a table:
`start | length | beat | media | graphic | annotation | transition out | sound idea`.

With a voice-over, record or generate it first (`qwen-tts-voiceover`), master it (`audio-mastering`), measure word timings
(`caption-sync`), and put beats on the sentences instead of the bars;
the music is then edited under the voice.
