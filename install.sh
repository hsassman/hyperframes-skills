#!/usr/bin/env bash
# Install every skill in this repo into Claude's skills folder, plus the pinned third-party skills.
#   ./install.sh                 # -> ~/.claude/skills (personal skills, all projects)
#   ./install.sh --target DIR    # e.g. --target ./.claude/skills for one project
#   ./install.sh --no-upstream   # only the skills in this repo
#   ./install.sh --kit           # also install the motion-film kit's node + python dependencies
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude/skills"; UPSTREAM=1; KIT=0
while [ $# -gt 0 ]; do case "$1" in
  --target) TARGET="$2"; shift 2;; --no-upstream) UPSTREAM=0; shift;; --kit) KIT=1; shift;;
  -h|--help) sed -n 2,6p "$0"; exit 0;; *) echo "unknown option $1"; exit 1;; esac; done
SRC_DIR="$HOME/.claude/skill-src"; mkdir -p "$TARGET" "$SRC_DIR"
MISSING=0
need() { command -v "$1" >/dev/null 2>&1 || { echo "missing: $1 ($2)"; MISSING=1; }; }
need git "https://git-scm.com"; need python3 "3.10+"; need node "18+ (https://nodejs.org)"; need ffmpeg "6.1+ (https://ffmpeg.org)"
if [ "$MISSING" = 1 ]; then echo "Install the missing tools above, then re-run."; exit 1; fi

# replace one installed skill folder (guards stop an empty variable from ever reaching rm)
replace() { rm -rf -- "${TARGET:?}/${1:?}"; mkdir -p "${TARGET:?}/${1:?}"; }

echo "== skills from this repo -> $TARGET"
for d in "$ROOT"/skills/*/; do n=$(basename "$d")
  replace "$n"
  (cd "$d" && tar --exclude=node_modules --exclude=__pycache__ --exclude=.hyperframes --exclude='./example/assets' --exclude='./example/renders' \
     --exclude='./example/audio' --exclude='./example/music' --exclude='./example/sfx' --exclude='./example/storyboard' \
     --exclude='./example/index.html' --exclude='./example/events.json' -cf - .) | (cd "$TARGET/$n" && tar -xf -)
  echo "  $n"; done

pin() { python3 -c "import json,sys;m=json.load(open(sys.argv[1]));print(next(u for u in m['upstream'] if u['name']==sys.argv[2])[sys.argv[3]])" "$ROOT/manifest.json" "$1" "$2"; }
fetch() { local dir="$SRC_DIR/$1" repo commit; repo=$(pin "$1" repo); commit=$(pin "$1" commit)
  [ -d "$dir/.git" ] || git clone --quiet "$repo" "$dir"
  git -C "$dir" fetch --quiet origin "$commit" 2>/dev/null || git -C "$dir" fetch --quiet origin
  git -C "$dir" checkout --quiet "$commit"; echo "  $1 @ ${commit:0:10}"; }

if [ "$UPSTREAM" = 1 ]; then
  echo "== third-party skills (pinned)"
  fetch threejs-skills
  for d in "$SRC_DIR/threejs-skills/skills"/*/; do n=$(basename "$d"); replace "$n"; cp -r "$d". "$TARGET/$n/"; echo "    $n"; done
  fetch earshot; fetch clipwing
  echo "  hyperframes skills (via its CLI)"
  (cd "$TARGET/.." && npx --yes "$(pin hyperframes cli)" skills update) || echo "  ! run 'npx hyperframes skills update' yourself"
  echo "  earshot's Python environment (~1.1 GB of models) is set up on first use by the earshot skill."
fi

if [ "$KIT" = 1 ]; then
  echo "== motion-film kit dependencies"
  (cd "$TARGET/motion-film/kit/node" && npm install --no-audit --no-fund && npm run build:3d)
  python3 -m pip install -r "$TARGET/motion-film/kit/requirements.txt" 2>/dev/null \
    || python3 -m pip install --break-system-packages -r "$TARGET/motion-film/kit/requirements.txt"
fi
if python3 "$ROOT/scripts/check_skills.py" "$TARGET" >/dev/null; then echo "== done: skills validated in $TARGET"
else echo "== done — run: python3 scripts/check_skills.py \"$TARGET\" to see warnings"; fi
