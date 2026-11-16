#!/usr/bin/env bash
# Make every `git push` go to BOTH GitHub (Codespaces + portfolio)
# and GitLab (where the CI/CD pipeline runs).
#
# Usage:  bash scripts/setup-remotes.sh <gitlab-namespace> [repo-name]
set -euo pipefail

GITLAB_NS="${1:?Usage: bash scripts/setup-remotes.sh <gitlab-namespace> [repo-name]}"
REPO_NAME="${2:-secureshare-devops}"
GITLAB_URL="https://gitlab.com/${GITLAB_NS}/${REPO_NAME}.git"

GITHUB_URL="$(git remote get-url origin)"

# Keep fetching from GitHub, but push to both.
git remote set-url --push origin "$GITHUB_URL"
if ! git remote get-url --push --all origin | grep -qx "$GITLAB_URL"; then
  git remote set-url --add --push origin "$GITLAB_URL"
fi

# A separate 'gitlab' remote for GitLab-only commands.
git remote remove gitlab 2>/dev/null || true
git remote add gitlab "$GITLAB_URL"

echo "Push targets for origin:"
git remote get-url --push --all origin
