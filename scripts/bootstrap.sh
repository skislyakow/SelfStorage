#!/usr/bin/env sh
# Set up the local environment: Python dependencies, git hooks + local agent skills.
# .agents/ is not tracked in git (see .gitignore): skills are installed from
# skills-lock.json so every machine gets the same versions.
#
#   ./scripts/bootstrap.sh          # uv sync + pre-commit install + restore skills if missing
#   ./scripts/bootstrap.sh --update # uv sync + pre-commit install + update skills to latest
set -eu

update=0
case "${1:-}" in
    --update | -u) update=1 ;;
esac

echo "==> uv sync"
uv sync

if [ -d .git ]; then
    echo "==> pre-commit install"
    uv run pre-commit install
else
    echo "warning: no .git directory - skipping pre-commit install" >&2
fi

if ! command -v npx >/dev/null 2>&1; then
    echo "warning: npx not found - skipping agent skills (Node.js is required)" >&2
    exit 0
fi

if [ "$update" = 1 ]; then
    echo "==> skills update"
    # The CLI can crash on exit on Windows after doing its job, so a non-zero
    # exit code is not treated as a failure here.
    npx -y skills@latest update -p -y || true
    echo "note: skills-lock.json may have changed - check git diff and commit"
    exit 0
fi

if [ -d ".agents/skills" ]; then
    echo "Skills already installed. Update with: ./scripts/bootstrap.sh --update"
    exit 0
fi

echo "==> skills install (from skills-lock.json)"
npx -y skills@latest experimental_install
