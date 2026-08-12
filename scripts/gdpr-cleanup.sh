#!/bin/bash
#
# Limpieza de datos de viajeros (cumplimiento GDPR)
# Ejecutar en el contenedor de la app Django
#
# Los datos de viajeros registrados para SES Hospedajes deben
# conservarse solo durante el periodo legal requerido.
# Este script elimina registros antiguos.
#
# Uso (desde el host):
#   docker exec <app-container> bash /app/scripts/gdpr-cleanup.sh
#
# Configurar con cron para ejecucion mensual:
#   0 3 1 * * docker exec <app-container> bash /app/scripts/gdpr-cleanup.sh
#

set -euo pipefail

# ============================================
# CONFIGURACION
# ============================================

# Periodo de retencion en meses para datos de viajeros
# Segun normativa espanola, los registros de viajeros deben
# conservarse un minimo de 6 meses. Ajustar segun necesidad.
RETENTION_MONTHS=${GDPR_TRAVELER_RETENTION_MONTHS:-6}

# Modo dry-run por defecto (solo muestra lo que se borraria)
# Usar --apply para ejecutar realmente
DRY_RUN=true
if [ "${1:-}" = "--apply" ]; then
    DRY_RUN=false
fi

# ============================================
# FUNCIONES
# ============================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# ============================================
# VALIDACION
# ============================================

log "=== Limpieza GDPR de datos de viajeros ==="
log "Retencion: ${RETENTION_MONTHS} meses"

if [ "$DRY_RUN" = true ]; then
    log "MODO DRY-RUN: No se borraran datos. Usar --apply para ejecutar."
else
    log "MODO APLICACION: Los datos se borraran permanentemente."
fi

# Verificar que estamos en un entorno Django
if ! python manage.py check > /dev/null 2>&1; then
    echo "ERROR: No se puede ejecutar Django. Asegurate de estar en el contenedor correcto."
    exit 1
fi

# ============================================
# CONTAR REGISTROS ANTIGUOS
# ============================================

CUTOFF_DATE=$(date -d "-${RETENTION_MONTHS} months" +%Y-%m-%d 2>/dev/null || python -c "
from datetime import datetime, timedelta
print((datetime.now() - timedelta(days=${RETENTION_MONTHS}*30)).strftime('%Y-%m-%d'))
")

log "Fecha de corte: $CUTOFF_DATE"

# Contar ViajeroCheckin antiguos
VIAJEROS_COUNT=$(python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_project.settings')
django.setup()
from reservas.models import ViajeroCheckin
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(days=${RETENTION_MONTHS} * 30)
count = ViajeroCheckin.objects.filter(fecha_entrada__lt=cutoff).count()
print(count)
")

log "ViajeroCheckin antiguos a eliminar: $VIAJEROS_COUNT"

# Contar reservas antiguas sin viajeros asociados
RESERVAS_COUNT=$(python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_project.settings')
django.setup()
from reservas.models import Reserva
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(days=${RETENTION_MONTHS} * 30)
# Solo reservas completadas (check-out pasado)
count = Reserva.objects.filter(
    fecha_salida__lt=cutoff,
    ses_hospedajes_enviado=True
).count()
print(count)
")

log "Reservas completadas y enviadas a SES antiguas: $RESERVAS_COUNT"

# ============================================
# ELIMINAR (si --apply)
# ============================================

if [ "$DRY_RUN" = false ]; then
    if [ "$VIAJEROS_COUNT" -gt 0 ]; then
        log "Eliminando ${VIAJEROS_COUNT} registros de ViajeroCheckin..."
        python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_project.settings')
django.setup()
from reservas.models import ViajeroCheckin
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(days=${RETENTION_MONTHS} * 30)
deleted, _ = ViajeroCheckin.objects.filter(fecha_entrada__lt=cutoff).delete()
print(f'Eliminados: {deleted}')
"
    fi

    log "Limpieza completada."
else
    log ""
    log "Para ejecutar la eliminacion real:"
    log "  docker exec <app-container> bash /app/scripts/gdpr-cleanup.sh --apply"
fi

log "=== Fin ==="
