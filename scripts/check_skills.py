#!/usr/bin/env python3
"""Validate skill folders: each has a SKILL.md with YAML frontmatter holding a kebab-case name that matches the folder
and a description (<= 1024 chars, no angle brackets), and every relative file the SKILL.md names in backticks exists
(skipped for wrapper skills, whose file names refer to the pinned upstream clone).

    python3 scripts/check_skills.py            # checks ./skills
    python3 scripts/check_skills.py DIR        # checks any skills folder (e.g. ~/.claude/skills)
"""
import os, re, sys


def frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def check(folder):
    path = os.path.join(folder, "SKILL.md")
    if not os.path.isfile(path):
        return ["no SKILL.md"]
    text = open(path, encoding="utf-8").read()
    fm = frontmatter(text)
    if fm is None:
        return ["SKILL.md has no frontmatter"]
    errs, name, desc = [], fm.get("name", ""), fm.get("description", "")
    base = os.path.basename(os.path.normpath(folder))
    if not name:
        errs.append("frontmatter: missing name")
    elif name != base:
        errs.append(f"name '{name}' does not match folder '{base}'")
    if name and not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
        errs.append("name must be kebab-case, at most 64 characters")
    if not desc:
        errs.append("frontmatter: missing description")
    if len(desc) > 1024:
        errs.append(f"description is {len(desc)} characters (max 1024)")
    if "<" in desc or ">" in desc:
        errs.append("description contains angle brackets")
    wrapper = "pinned to commit" in text  # file names in a wrapper refer to the upstream clone, not this folder
    for link in ([] if wrapper else re.findall(r"`((?:references|scripts|kit|example)/[^`\s]+)`", text)):
        p = link.rstrip(".,):")
        if not any(ch in p for ch in "*<{$") and not os.path.exists(os.path.join(folder, p)):
            errs.append(f"names a file that does not exist: {p}")
    return errs


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills")
    bad = 0
    for d in sorted(os.listdir(root)):
        f = os.path.join(root, d)
        if not os.path.isdir(f) or d.startswith(".") or not os.path.exists(os.path.join(f, "SKILL.md")) and d.endswith("-src"):
            continue
        errs = check(f)
        bad += bool(errs)
        print(("FAIL " if errs else "ok   ") + d + "".join(f"\n       - {e}" for e in errs))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
