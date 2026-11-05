# Adding a skill

1. **Create the folder** `skills/<kebab-name>/` with a `SKILL.md`:
   ```markdown
   ---
   name: my-skill
   description: One or two sentences on what it does and exactly when Claude should use it.
   ---

   # My skill
   Steps, rules, and when not to use it. Link deeper material: `references/topic.md`, `scripts/tool.py`.
   ```
   The description decides when the skill is used, so name the situations and words a person would actually say.
2. **Add depth** in `references/` and runnable code in `scripts/`. Prefer deterministic scripts over long instructions.
3. **Wrapping someone else's skill?** Don't copy it. Write a wrapper `SKILL.md` that clones the upstream into
   `$HOME/.claude/skill-src/<name>` at a pinned commit, then says "read `$SRC/SKILL.md` and follow it". Add the upstream
   to `manifest.json` → `upstream` so the installers prefetch it. Credit the source and licence at the top.
4. **Register it**: add the name to `manifest.json` → `local` and a row to the table in `README.md`.
5. **Check**: `python3 scripts/check_skills.py`, then `./install.sh --target /tmp/skills-test --no-upstream`.
6. **Try it** in a fresh Claude session with a realistic request and watch whether it triggers and follows the steps.
   The `skill-creator` skill can run evals and tune the description.
7. Commit with a message saying what the skill adds.
