---
name: script-structure
description: Encodes a retention-optimized script structure (hook, setup, escalating value, payoff) for writing video scripts (YouTube, brand and process films), plus an LLM-as-judge rubric for scoring script drafts on hook strength, pacing, and curiosity gaps. Use this skill whenever a task involves writing a new video script, revising an existing script for retention, or evaluating/scoring a script draft. This is a pure writing/evaluation skill with no external tool dependency — apply it directly whenever script work comes up in this pipeline, not just when explicitly asked for "script structure."
---

# Script Structure

A retention-optimized structural template for video scripts (YouTube, brand films, explainers), plus
a scoring rubric for evaluating drafts. No external tools — this is a writing
and evaluation discipline to apply directly.

## The structure

### 1. Hook (first 5–15 seconds)
The single highest-leverage part of the script — most viewer drop-off happens
here. A strong hook does at least one of:
- Opens with a specific, concrete claim or stat rather than a vague tease ("This one mistake cost him $2 million" beats "Let's talk about mistakes")
- Poses a question the viewer genuinely wants answered, and does NOT answer it immediately
- Opens in medias res — drop into the middle of the most interesting moment, then rewind to context
- Promises a clear payoff ("by the end of this video you'll know exactly how X works")

Avoid: generic channel intros, "hey guys welcome back," slow scene-setting
before the hook lands. If a script has any of these before the hook, move the
hook earlier.

### 2. Setup (establishes context, keeps it brief)
Give the viewer just enough context to understand what's coming — who, what,
why it matters. This should be the shortest section proportionally. If setup
is taking more than ~10% of total script length, it's too long; look for
context that can be folded into the hook or delivered incrementally during
the value section instead.

### 3. Escalating value (the bulk of the script)
The core content, structured so each beat raises stakes or curiosity rather
than laying flat information end to end. Concretely:
- Break the content into discrete beats/steps/reveals rather than one
  continuous explanation
- Order beats so each one either answers a question raised earlier or opens
  a new one — avoid a beat that does neither
- Insert periodic "open loops" — brief forward references ("but that's not
  even the strangest part") that create curiosity gaps pulling the viewer
  toward the next beat
- Vary pacing — not every beat needs the same length or energy; a quick beat
  after a dense one gives the viewer a breather

### 4. Payoff (resolution)
Deliver on what the hook promised, explicitly. Don't let the payoff arrive so
subtly the viewer doesn't register it as the answer. If the hook posed a
question, restate it briefly before answering, so viewers who drifted can
reorient.

### 5. Close (brief)
A short close — not a new topic. Avoid dragging this out; a script that
"payoff, then keeps talking" loses viewers who came for the payoff and leave
once they have it. If a call-to-action (subscribe, watch next) is needed,
keep it under a few seconds and after the payoff, never before it.

## Writing a new script with this structure

1. Write the payoff first — know exactly what you're building toward
2. Write the hook to directly set up that payoff, without giving it away
3. Fill in setup (minimal) and escalating value (the bulk), checking each
   beat either resolves or opens a curiosity gap
4. Write the close last, and keep it short

## Scoring an existing draft (LLM-as-judge rubric)

When asked to evaluate a script, score each dimension 1–5 with a one-line
justification, rather than giving a single vague quality verdict:

- **Hook strength (1–5)**: Does it open with something concrete/specific in
  the first 1–2 lines? Does it avoid giving away the payoff too early?
- **Setup efficiency (1–5)**: Is setup proportionally brief? Is there any
  context here that could be cut or moved later?
- **Curiosity gap density (1–5)**: Are there open loops distributed through
  the value section, or does information arrive flatly with no forward pull?
- **Pacing variation (1–5)**: Does beat length/energy vary, or is every beat
  roughly the same weight (a sign of monotony)?
- **Payoff delivery (1–5)**: Is the payoff explicit and clearly connected
  back to the hook's promise?
- **Close discipline (1–5)**: Is the close short and does it come strictly
  after the payoff?

Report scores with brief justifications per dimension, plus 1–3 concrete
revision suggestions tied to the lowest-scoring dimensions — not generic
"make it more engaging" feedback.

## When NOT to use this skill

- Don't force this exact structure onto formats that don't suit it (e.g. a
  pure tutorial/how-to script may not need curiosity-gap pacing the same way
  a narrative/mystery-style script does) — adapt the emphasis, but the
  hook-first and brief-setup principles still apply broadly.
- This skill produces a heuristic structural/rubric evaluation, not a
  guarantee of actual audience retention — real retention data only comes
  from YouTube Analytics after publishing. Say so if a user seems to be
  treating a script score as a retention guarantee.
