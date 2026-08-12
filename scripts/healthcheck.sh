#!/bin/bash
#
# Healthcheck post-deploy para Hostal Rivera
# Verifica que todos los componentes funcionan correctamente
#
# Uso:
#   ./healthcheck.sh
#
# Se puede ejecutar manualmente o programar con cron
#

set -euo pipefail

# ============================================
# CONFIGURACION (ajustar segun tu entorno)
# ============================================

DOMINIO="${DOMINIO:-localhost}"
PUERTO="${PUERTO:-8000}"
ES_LOCAL="${ES_LOCAL:-true}"

# Si es produccion (Dokploy), ajustar
if [ "$ES_LOCAL" = "false" ]; then
    DOMINIO="${DOMINIO:-hostalrivera.com}"
    PUERTO=""
    PROTOCOLO="https"
else
    PROTOCOLO="http"
fi

# ============================================
# FUNCIONES
# ============================================

PASSED=0
FAILED=0
WARNINGS=0

pass() {
    echo "[OK] $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo "[FAIL] $1"
    FAILED=$((FAILED + 1))
}

warn() {
    echo "[WARN] $1"
    WARNINGS=$((WARNINGS + 1))
}

# ============================================
# CHECKS
# ============================================

echo "=== Healthcheck Hostal Rivera ==="
echo "Dominio: $DOMINIO"
echo "Fecha: $(date)"
echo ""

# 1. App HTTP responde
echo "--- Aplicacion ---"
if [ "$ES_LOCAL" = "true" ]; then
    HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "${PROTOCOLO}://${DOMINIO}:${PUERTO}/" 2>/dev/null || echo "000")
else
    HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "${PROTOCOLO}://${DOMINIO}/" 2>/dev/null || echo "000")
fi

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    pass "App responde (HTTP $HTTP_CODE)"
else
    fail "App no responde (HTTP $HTTP_CODE)"
fi

# 2. Admin accesible
ADMIN_PATH="${ADMIN_PATH:-admin}"
if [ "$ES_LOCAL" = "true" ]; then
    ADMIN_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "${PROTOCOLO}://${DOMINIO}:${PUERTO}/${ADMIN_PATH}/" 2>/dev/null || echo "000")
else
    ADMIN_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "${PROTOCOLO}://${DOMINIO}/${ADMIN_PATH}/" 2>/dev/null || echo "000")
fi

if [ "$ADMIN_CODE" = "200" ] || [ "$ADMIN_CODE" = "302" ] || [ "$ADMIN_CODE" = "401" ]; then
    pass "Admin accesible (HTTP $ADMIN_CODE)"
else
    warn "Admin no accesible (HTTP $ADMIN_CODE)"
fi

# 3. Django check
echo ""
echo "--- Django ---"
if command -v docker &> /dev/null; then
    APP_CONTAINER=$(docker ps --filter "name=app" --format "{{.Names}}" | head -1)
    if [ -n "$APP_CONTAINER" ]; then
        CHECK_OUTPUT=$(docker exec "$APP_CONTAINER" python manage.py check 2>&1 || true)
        if echo "$CHECK_OUTPUT" | grep -q "System check identified no issues"; then
            pass "Django check: sin problemas"
        else
            fail "Django check: problemas detectados"
            echo "$CHECK_OUTPUT"
        fi

        CHECK_DEPLOY=$(docker exec "$APP_CONTAINER" python manage.py check --deploy 2>&1 || true)
        DEPLOY_ERRORS=$(echo "$CHECK_DEPLOY" | grep -c "ERROR\|CRITICAL" || true)
        if [ "$DEPLOY_ERRORS" -eq 0 ]; then
            pass "Django check --deploy: sin errores criticos"
        else
            warn "Django check --deploy: $DEPLOY_ERRORS advertencias/errores"
        fi
    else
        warn "Contenedor de app no encontrado"
    fi
else
    # Ejecutar directamente si no hay Docker
    if python manage.py check > /dev/null 2>&1; then
        pass "Django check: sin problemas"
    else
        fail "Django check: problemas detectados"
    fi
fi

# 4. Base de datos
echo ""
echo "--- Base de datos ---"
if command -v docker &> /dev/null; then
    PG_CONTAINER=$(docker ps --filter "name=postgres" --format "{{.Names}}" | head -1)
    if [ -n "$PG_CONTAINER" ]; then
        if docker exec "$PG_CONTAINER" pg_isready > /dev/null 2>&1; then
            pass "PostgreSQL responde"
        else
            fail "PostgreSQL no responde"
        fi

        # Tamano de la base de datos
        DB_SIZE=$(docker exec "$PG_CONTAINER" psql -U postgres -t -c "SELECT pg_size_pretty(pg_database_size('$(docker exec "$PG_CONTAINER" printenv POSTGRES_DB 2>/dev/null || echo postgres)'));" 2>/dev/null | tr -d ' ' || echo "desconocido")
        pass "Tamano DB: $DB_SIZE"
    else
        warn "Contenedor PostgreSQL no encontrado"
    fi
fi

# 5. Espacio en disco
echo ""
echo "--- Sistema ---"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}')
DISK_PCT=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_PCT" -lt 80 ]; then
    pass "Disco: ${DISK_USAGE} usado"
elif [ "$DISK_PCT" -lt 90 ]; then
    warn "Disco: ${DISK_USAGE} usado (cerca del limite)"
else
    fail "Disco: ${DISK_USAGE} usado (critico)"
fi

# 6. Memoria
MEM_USAGE=$(free -m | awk 'NR==2{printf "%.0f%%", $3*100/$2}')
MEM_PCT=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$MEM_PCT" -lt 80 ]; then
    pass "Memoria: ${MEM_USAGE} usada"
elif [ "$MEM_PCT" -lt 90 ]; then
    warn "Memoria: ${MEM_USAGE} usada (cerca del limite)"
else
    fail "Memoria: ${MEM_USAGE} usada (critico)"
fi

# 7. SSL (solo produccion)
echo ""
echo "--- SSL ---"
if [ "$ES_LOCAL" = "false" ]; then
    if echo | openssl s_client -connect "${DOMINIO}:443" 2>/dev/null | openssl x509 -noout -dates > /dev/null 2>&1; then
        EXPIRY=$(echo | openssl s_client -connect "${DOMINIO}:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
        EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || echo "0")
        NOW_EPOCH=$(date +%s)
        DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))

        if [ "$DAYS_LEFT" -gt 30 ]; then
            pass "SSL valido (expira: $EXPIRY, quedan ${DAYS_LEFT} dias)"
        elif [ "$DAYS_LEFT" -gt 7 ]; then
            warn "SSL expira pronto (quedan ${DAYS_LEFT} dias)"
        else
            fail "SSL expira en ${DAYS_LEFT} dias"
        fi
    else
        fail "SSL no configurado o no accesible"
    fi
else
    warn "SSL no aplicable en entorno local"
fi

# 8. Contenedores corriendo
echo ""
echo "--- Docker ---"
if command -v docker &> /dev/null; then
    RUNNING=$(docker ps --format "{{.Names}}" | wc -l)
    TOTAL=$(docker ps -a --format "{{.Names}}" | wc -l)
    pass "Contenedores: ${RUNNING}/${TOTAL} corriendo"

    # Verificar contenedores parados
    STOPPED=$(docker ps -a --filter "status=exited" --format "{{.Names}}")
    if [ -n "$STOPPED" ]; then
        warn "Contenedores parados: $STOPPED"
    fi
fi

# ============================================
# RESUMEN
# ============================================

echo ""
echo "=== Resumen ==="
echo "OK:       $PASSED"
echo "FALLOS:   $FAILED"
echo "AVISOS:   $WARNINGS"

if [ "$FAILED" -gt 0 ]; then
    echo ""
    echo "RESULTADO: FALLO - Revisar los errores anteriores"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo ""
    echo "RESULTADO: OK CON AVISOS - Revisar advertencias"
    exit 0
else
    echo ""
    echo "RESULTADO: TODO OK"
    exit 0
fi
