# Set up the local environment: Python dependencies + local agent skills.
# .agents/ is not tracked in git (see .gitignore): skills are installed from
# skills-lock.json so every machine gets the same versions.
#
#   ./scripts/bootstrap.ps1         # uv sync + restore skills if missing
#   ./scripts/bootstrap.ps1 -Update # uv sync + update skills to latest
param([switch]$Update)

$ErrorActionPreference = "Stop"

Write-Host "==> uv sync"
uv sync

if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Warning "npx not found: skipping agent skills (Node.js is required)."
    exit 0
}

if ($Update) {
    Write-Host "==> skills update"
    # The CLI can crash on exit on Windows after doing its job, so a non-zero
    # exit code is not treated as a failure here.
    npx -y skills@latest update -p -y
    Write-Host "note: skills-lock.json may have changed - check git diff and commit"
    exit 0
}

if (Test-Path ".agents/skills") {
    Write-Host "Skills already installed. Update with: ./scripts/bootstrap.ps1 -Update"
    exit 0
}

Write-Host "==> skills install (from skills-lock.json)"
npx -y skills@latest experimental_install
