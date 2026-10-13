#!/bin/bash
set -e

cd /opt/selftorage

echo "=== install uv if missing ==="
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "=== uv sync (no dev) ==="
uv sync --frozen --no-dev

echo "=== collectstatic ==="
uv run python manage.py collectstatic --noinput

echo "=== migrate ==="
uv run python manage.py migrate --noinput

echo "=== seed demo data ==="
uv run python manage.py seed_demo

echo "=== restart selftorage ==="
systemctl restart selftorage

echo "=== install reminder timer ==="
cp selfstorage-notify.service /etc/systemd/system/
cp selfstorage-notify.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now selfstorage-notify.timer

echo "Deploy OK"
