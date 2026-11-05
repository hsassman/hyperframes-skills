# Working in this repo

This repo is a collection of Claude skills that grows over time. Each folder in `skills/` is one skill.

## Conventions
- One skill per folder: `skills/<kebab-name>/SKILL.md` with frontmatter `name` (= folder name) and `description`
  (one or two sentences saying when to use it, ≤ 1024 characters, no angle brackets).
- Keep `SKILL.md` lean (the steps and the rules); put depth in `references/*.md`, code in `scripts/` or `kit/`.
  Every file a SKILL.md names in backticks must exist — `python3 scripts/check_skills.py` checks this.
- Skills are general-purpose. No client names, client brands, client facts or client media anywhere in the repo.
  Examples use fictional brands.
- Third-party skills are never copied in. Either add them to `manifest.json` → `upstream` (installed by the installers)
  or write a small wrapper skill that clones the upstream at a pinned commit and hands over to its SKILL.md.
- Generated files (node_modules, renders, audio outputs, example assets) are git-ignored. Don't commit media over a few MB.
- When you add or rename a skill: update `manifest.json` → `local`, the table in `README.md`, and run the checker.

## Before committing
```bash
python3 scripts/check_skills.py
./install.sh --target /tmp/skills-test --no-upstream     # installs cleanly
```
For changes to `motion-film/kit`, run the example end to end (`example/README.md`): lint, snapshots, `sound.py --demo`.
