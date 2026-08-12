#!/bin/bash
# Script de actualizacion para Docker local
# Para Dokploy, usar el panel de Dokploy (autodeploy desde Git)
set -e

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.local.yml}"

echo "=== Actualizacion de Hostal Rivera ==="

echo "[1/5] Backup de base de datos..."
mkdir -p backups
docker compose -f "$COMPOSE_FILE" exec -T db pg_dump -U "${DB_USER:-hotel_user}" -d "${DB_NAME:-hotel_db}" -F c -f /tmp/backup_pre_update.dump 2>/dev/null || echo "  Backup omitido (DB no accesible)"

echo "[2/5] Pull de cambios..."
git pull

echo "[3/5] Rebuild y restart..."
docker compose -f "$COMPOSE_FILE" up -d --build

echo "[4/5] Migraciones..."
docker compose -f "$COMPOSE_FILE" exec app python manage.py migrate --noinput

echo "[5/5] Collectstatic..."
docker compose -f "$COMPOSE_FILE" exec app python manage.py collectstatic --noinput

echo ""
echo "=== Verificacion ==="
docker compose -f "$COMPOSE_FILE" exec app python manage.py check --deploy

echo ""
echo "=== Actualizacion completada ==="
