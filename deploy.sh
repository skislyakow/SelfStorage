#!/bin/bash
set -e

cd /opt/selftorage

echo "=== git pull ==="
git pull

echo "=== pip install ==="
.venv/bin/pip install -r requirements.txt -q

echo "=== collectstatic ==="
.venv/bin/python manage.py collectstatic --noinput

echo "=== migrate ==="
.venv/bin/python manage.py migrate --noinput

echo "=== seed demo data ==="
.venv/bin/python manage.py seed_demo

echo "=== restart selftorage ==="
systemctl restart selftorage

echo "=== install reminder timer ==="
cp selfstorage-notify.service /etc/systemd/system/
cp selfstorage-notify.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now selfstorage-notify.timer

echo "Deploy OK"
