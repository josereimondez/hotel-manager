#!/bin/bash
#
# Backup offsite de Hostal Rivera (DB + Media)
# Ejecutar en la VM de Dokploy
#
# Requisitos:
#   - rclone instalado y configurado con destino remoto
#   - Acceso a los contenedores de PostgreSQL y la app
#
# Uso:
#   ./backup-offsite.sh
#
# Configurar con cron para ejecucion automatica:
#   0 4 * * 0 /opt/scripts/backup-offsite.sh >> /var/log/backup-offsite.log 2>&1
#

set -euo pipefail

# ============================================
# CONFIGURACION (ajustar segun tu entorno)
# ============================================

# Nombre del remoto rclone (configurar con 'rclone config')
RCLONE_REMOTE="remoto"

# Ruta remota para backups
RCLONE_PATH="backups-hostal"

# Retencion de backups locales (dias)
LOCAL_RETENTION=7

# Retencion de backups remotos (dias)
REMOTE_RETENTION=30

# Directorio temporal para backups
BACKUP_DIR="/tmp/backup-$(date +%Y%m%d_%H%M%S)"

# ============================================
# FUNCIONES
# ============================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

cleanup() {
    if [ -d "$BACKUP_DIR" ]; then
        rm -rf "$BACKUP_DIR"
    fi
}

trap cleanup EXIT

error_exit() {
    log "ERROR: $1"
    exit 1
}

# ============================================
# VALIDACIONES
# ============================================

log "=== Inicio backup offsite ==="

# Verificar rclone
if ! command -v rclone &> /dev/null; then
    error_exit "rclone no esta instalado. Instalar con: curl https://rclone.org/install.sh | sudo bash"
fi

# Verificar que el remoto existe
if ! rclone listremotes | grep -q "^${RCLONE_REMOTE}:"; then
    error_exit "El remoto '${RCLONE_REMOTE}' no existe. Configurar con: rclone config"
fi

# Verificar espacio en disco
DISK_USAGE=$(df /tmp | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 90 ]; then
    error_exit "Disco lleno (${DISK_USAGE}% usado). No se puede crear backup temporal."
fi

# ============================================
# BACKUP DE BASE DE DATOS
# ============================================

log "Buscando contenedor PostgreSQL..."
PG_CONTAINER=$(docker ps --filter "name=postgres" --format "{{.Names}}" | head -1)

if [ -z "$PG_CONTAINER" ]; then
    error_exit "No se encontro contenedor PostgreSQL"
fi

log "Contenedor PostgreSQL encontrado: $PG_CONTAINER"

# Obtener credenciales del contenedor
DB_USER=$(docker exec "$PG_CONTAINER" printenv POSTGRES_USER 2>/dev/null || echo "postgres")
DB_NAME=$(docker exec "$PG_CONTAINER" printenv POSTGRES_DB 2>/dev/null || echo "postgres")

log "Base de datos: $DB_NAME (usuario: $DB_USER)"

# Crear directorio temporal
mkdir -p "$BACKUP_DIR/db"

# Ejecutar pg_dump
log "Creando backup de PostgreSQL..."
docker exec "$PG_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" -F c -f /tmp/db.dump
docker cp "$PG_CONTAINER:/tmp/db.dump" "$BACKUP_DIR/db/"
docker exec "$PG_CONTAINER" rm -f /tmp/db.dump

DB_SIZE=$(du -sh "$BACKUP_DIR/db/db.dump" | cut -f1)
log "Backup DB creado: $DB_SIZE"

# ============================================
# BACKUP DE MEDIA
# ============================================

log "Buscando contenedor de la app..."
APP_CONTAINER=$(docker ps --filter "name=app" --format "{{.Names}}" | head -1)

if [ -z "$APP_CONTAINER" ]; then
    log "ADVERTENCIA: No se encontro contenedor de app. Buscando volumenes de media..."

    # Intentar encontrar volumen de media
    MEDIA_VOLUME=$(docker volume ls --format "{{.Name}}" | grep -i media | head -1)

    if [ -n "$MEDIA_VOLUME" ]; then
        log "Volumen de media encontrado: $MEDIA_VOLUME"
        mkdir -p "$BACKUP_DIR/media"
        docker run --rm -v "$MEDIA_VOLUME":/media -v "$BACKUP_DIR/media:/backup" alpine tar czf /backup/media.tar.gz -C /media .
        MEDIA_SIZE=$(du -sh "$BACKUP_DIR/media/media.tar.gz" | cut -f1)
        log "Backup media creado: $MEDIA_SIZE"
    else
        log "ADVERTENCIA: No se encontro volumen de media. Omitiendo."
    fi
else
    log "Contenedor app encontrado: $APP_CONTAINER"

    # Verificar si existe /app/media
    if docker exec "$APP_CONTAINER" test -d /app/media; then
        mkdir -p "$BACKUP_DIR/media"
        docker cp "$APP_CONTAINER:/app/media" "$BACKUP_DIR/media/"
        MEDIA_SIZE=$(du -sh "$BACKUP_DIR/media/media" | cut -f1)
        log "Backup media creado: $MEDIA_SIZE"
    else
        log "ADVERTENCIA: /app/media no existe en el contenedor. Omitiendo."
    fi
fi

# ============================================
# COMPRIMIR TODO
# ============================================

log "Comprimiendo backup..."
TAR_FILE="/tmp/backup-$(date +%Y%m%d_%H%M%S).tar.gz"
tar czf "$TAR_FILE" -C "$(dirname "$BACKUP_DIR")" "$(basename "$BACKUP_DIR")"
TOTAL_SIZE=$(du -sh "$TAR_FILE" | cut -f1)
log "Backup comprimido: $TOTAL_SIZE"

# ============================================
# SUBIR A OFFSITE
# ============================================

log "Subiendo a ${RCLONE_REMOTE}:${RCLONE_PATH}/$(date +%Y%m%d)/..."
rclone copy "$TAR_FILE" "${RCLONE_REMOTE}:${RCLONE_PATH}/$(date +%Y%m%d)/" --progress

log "Backup subido correctamente."

# ============================================
# LIMPIEZA
# ============================================

# Eliminar backup local temporal
rm -f "$TAR_FILE"

# Limpiar backups locales antiguos
log "Limpiando backups locales antiguos (> ${LOCAL_RETENTION} dias)..."
find /tmp -name "backup-*.tar.gz" -mtime +"$LOCAL_RETENTION" -delete 2>/dev/null || true

# Limpiar backups remotos antiguos
log "Limpiando backups remotos antiguos (> ${REMOTE_RETENTION} dias)..."
rclone delete "${RCLONE_REMOTE}:${RCLONE_PATH}/" --min-age "${REMOTE_RETENTION}d" 2>/dev/null || true

# ============================================
# RESUMEN
# ============================================

log "=== Backup completado ==="
log "Local: eliminado (retencion ${LOCAL_RETENTION} dias)"
log "Remoto: ${RCLONE_REMOTE}:${RCLONE_PATH}/$(date +%Y%m%d)/"
log "Retencion remota: ${REMOTE_RETENTION} dias"
