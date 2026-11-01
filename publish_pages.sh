#!/usr/bin/env bash
set -euo pipefail
DASH=/workspace/agp/dashboard
REPO=${AGP_PAGES_REPO:-agp-dashboard}
cd "$DASH"
if [ ! -d .git ]; then
  git init -b main
  git config user.email "jfischer.tech@gmail.com"
  git config user.name "James Fischer"
fi
printf '' > .nojekyll
git add -A
if git diff --cached --quiet; then
  echo "No changes to commit"
else
  git commit -m "AGP progress dashboard $(date -Iseconds)"
fi
if ! gh repo view "JamesLFischer/$REPO" >/dev/null 2>&1; then
  gh repo create "JamesLFischer/$REPO" --public --source=. --remote=origin --push --description "AI Game Player public progress dashboard"
else
  git remote remove origin 2>/dev/null || true
  git remote add origin "https://github.com/JamesLFischer/$REPO.git"
  git push -u origin main
fi
gh api -X POST "repos/JamesLFischer/$REPO/pages" -f "build_type=legacy" -f "source[branch]=main" -f "source[path]=/" 2>/dev/null \
  || gh api -X PUT "repos/JamesLFischer/$REPO/pages" -f "build_type=legacy" -f "source[branch]=main" -f "source[path]=/" 2>/dev/null \
  || true
echo "PAGES_URL=https://jameslfischer.github.io/$REPO/"
