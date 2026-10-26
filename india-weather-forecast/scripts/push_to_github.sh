#!/usr/bin/env bash
# Push this project to GitHub (Mac/Linux/Git Bash).
#   bash scripts/push_to_github.sh https://github.com/YOUR-USERNAME/india-weather-forecast.git
set -e
REPO_URL="$1"
MESSAGE="${2:-Add India weather analysis and forecasting project}"
if [ -z "$REPO_URL" ]; then echo "Usage: bash scripts/push_to_github.sh <repo-url> [commit message]"; exit 1; fi

cd "$(dirname "$0")/.."
command -v git >/dev/null || { echo "Git is not installed."; exit 1; }

echo "--- Step 1: pre-push checks ---"
python scripts/check_before_push.py || { echo "Fix the problems above, then run again."; exit 1; }

echo "--- Step 2: stage files ---"
[ -d .git ] || git init
git add .
git status --short
read -r -p "Commit and push these files to $REPO_URL ? (y/n) " ANSWER
[ "$ANSWER" = "y" ] || { echo "Cancelled."; exit 0; }

echo "--- Step 3: commit and push ---"
git commit -m "$MESSAGE"
git branch -M main
if git remote | grep -q origin; then git remote set-url origin "$REPO_URL"; else git remote add origin "$REPO_URL"; fi
git push -u origin main
echo "Done! Open ${REPO_URL%.git} in your browser."
