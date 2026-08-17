# Quickstart Validation: Correccion de Defectos de Calidad

**Feature**: 002-project-quality-overhaul
**Date**: 2026-08-14

## Overview

Guia de validacion para verificar que todos los defectos de calidad fueron corregidos. Ejecutar al finalizar la implementacion.

## Prerequisites

- Python 3.11-3.13 con venv activo
- Dependencias instaladas: `pip install -r requirements.txt`
- Variables de entorno configuradas: `DEBUG=True`, `SECRET_KEY=<valor>`, `ALLOWED_HOSTS=localhost,127.0.0.1`
- msgfmt disponible (para compilar .po)

## Validation Steps

### Step 1: Verificar cero emojis en templates

```bash
echo "=== Buscando emojis en templates ==="
EMOJI_TEMPLATES=$(find reservas/templates/ -name "*.html" -exec grep -lP '[\x{1F300}-\x{1F9FF}\x{2600}-\x{26FF}\x{2700}-\x{27BF}]' {} \; 2>/dev/null)
if [ -z "$EMOJI_TEMPLATES" ]; then
  echo "PASS: No hay emojis en templates"
else
  echo "FAIL: Emojis encontrados en:"
  echo "$EMOJI_TEMPLATES"
fi
```

**Expected**: PASS

---

### Step 2: Verificar cero emojis en documentacion

```bash
echo "=== Buscando emojis en documentacion ==="
EMOJI_DOCS=$(find . -name "*.md" -not -path "./.venv/*" -not -path "./.git/*" -not -path "./specs/*" -exec grep -lP '[\x{1F300}-\x{1F9FF}\x{2600}-\x{26FF}]' {} \; 2>/dev/null)
if [ -z "$EMOJI_DOCS" ]; then
  echo "PASS: No hay emojis en documentacion"
else
  echo "FAIL: Emojis encontrados en:"
  echo "$EMOJI_DOCS"
fi
```

**Expected**: PASS

---

### Step 3: Verificar cero placeholders conocidos

```bash
echo "=== Buscando placeholders ==="

echo -n "TU_USUARIO: "
TU_COUNT=$(grep -r "TU_USUARIO" . --include="*.md" --include="*.html" --include="*.py" 2>/dev/null | wc -l)
if [ "$TU_COUNT" -eq 0 ]; then echo "PASS"; else echo "FAIL ($TU_COUNT ocurrencias)"; fi

echo -n "Hotel Paradise: "
HP_COUNT=$(grep -r "Hotel Paradise" reservas/templates/ 2>/dev/null | wc -l)
if [ "$HP_COUNT" -eq 0 ]; then echo "PASS"; else echo "FAIL ($HP_COUNT ocurrencias)"; fi

echo -n "Telefono XXX: "
TEL_COUNT=$(grep -r "+34-XXX" reservas/templates/ 2>/dev/null | wc -l)
if [ "$TEL_COUNT" -eq 0 ]; then echo "PASS"; else echo "FAIL ($TEL_COUNT ocurrencias)"; fi

echo -n "Enlaces sociales #: "
SOCIAL_COUNT=$(grep -r 'href="#"' reservas/templates/ 2>/dev/null | wc -l)
if [ "$SOCIAL_COUNT" -eq 0 ]; then echo "PASS"; else echo "FAIL ($SOCIAL_COUNT ocurrencias)"; fi
```

**Expected**: Todos PASS

---

### Step 4: Verificar consistencia de versiones

```bash
echo "=== Verificando consistencia de versiones ==="

echo -n "Django version antigua en docs: "
DJ_OLD=$(grep -r "Django==5.0\|Django 5.0" *.md 2>/dev/null | wc -l)
if [ "$DJ_OLD" -eq 0 ]; then echo "PASS"; else echo "FAIL ($DJ_OLD menciones)"; fi

echo -n "Numero incorrecto de modelos: "
MOD_COUNT=$(grep -r "3 modelos\|Modelos: 3" *.md 2>/dev/null | wc -l)
if [ "$MOD_COUNT" -eq 0 ]; then echo "PASS"; else echo "FAIL ($MOD_COUNT menciones)"; fi
```

**Expected**: Todos PASS

---

### Step 5: Verificar archivos eliminados

```bash
echo "=== Verificando archivos eliminados ==="

for f in RESUMEN_GITHUB.md GITHUB_CHECKLIST.md APRENDIZAJE_PYTHON.md verify_github_ready.py; do
  if [ -f "$f" ]; then
    echo "FAIL: $f todavia existe"
  else
    echo "PASS: $f eliminado"
  fi
done
```

**Expected**: Todos PASS

---

### Step 6: Verificar db.sqlite3 no trackeado

```bash
echo "=== Verificando db.sqlite3 ==="

TRACKED=$(git ls-files | grep "db.sqlite3" | wc -l)
if [ "$TRACKED" -eq 0 ]; then
  echo "PASS: db.sqlite3 no esta trackeado"
else
  echo "FAIL: db.sqlite3 esta trackeado en git"
fi

if grep -q "db.sqlite3" .gitignore; then
  echo "PASS: .gitignore excluye db.sqlite3"
else
  echo "FAIL: .gitignore no excluye db.sqlite3"
fi
```

**Expected**: Ambos PASS

---

### Step 7: Verificar directorios de imagenes vacios eliminados

```bash
echo "=== Verificando directorios de imagenes ==="

for d in static/images/galeria static/images/iconos static/images/via_kunig; do
  if [ -d "$d" ]; then
    echo "FAIL: $d todavia existe"
  else
    echo "PASS: $d eliminado"
  fi
done
```

**Expected**: Todos PASS

---

### Step 8: Verificar bandera de galego

```bash
echo "=== Verificando selector de idioma ==="

# Buscar si galego usa bandera de Espana
GALEGO_FLAG=$(grep -n "Galego" reservas/templates/reservas/base.html | grep -c "🇪🇸")
if [ "$GALEGO_FLAG" -eq 0 ]; then
  echo "PASS: Galego no usa bandera de Espana"
else
  echo "FAIL: Galego usa bandera de Espana"
fi
```

**Expected**: PASS

---

### Step 9: Verificar README con narrativa

```bash
echo "=== Verificando narrativa en README ==="

echo -n "Menciona Hostal Rivera: "
grep -q "Hostal Rivera" README.md && echo "PASS" || echo "FAIL"

echo -n "Menciona Becerrea: "
grep -q "Becerrea" README.md && echo "PASS" || echo "FAIL"

echo -n "Menciona Galicia: "
grep -q "Galicia" README.md && echo "PASS" || echo "FAIL"

echo -n "Menciona Camino de Santiago o Via Kunig: "
grep -qE "Camino de Santiago|Via.Kunig" README.md && echo "PASS" || echo "FAIL"
```

**Expected**: Todos PASS

---

### Step 10: Verificar .po/.mo sincronizados

```bash
echo "=== Verificando .po/.mo ==="

for lang in es gl en; do
  po="locale/$lang/LC_MESSAGES/django.po"
  mo="locale/$lang/LC_MESSAGES/django.mo"
  
  if [ -f "$po" ] && [ -f "$mo" ]; then
    if [ "$po" -nt "$mo" ]; then
      echo "FAIL: $mo es mas antiguo que $po (recompilar)"
    else
      echo "PASS: $lang .mo actualizado"
    fi
  fi
done
```

**Expected**: Todos PASS

---

### Step 11: Ejecutar tests

```bash
echo "=== Ejecutando tests ==="

echo -n "manage.py check: "
python manage.py check 2>&1 > /dev/null
if [ $? -eq 0 ]; then echo "PASS"; else echo "FAIL"; fi

echo -n "manage.py test: "
python manage.py test reservas 2>&1 > /dev/null
if [ $? -eq 0 ]; then echo "PASS"; else echo "FAIL"; fi
```

**Expected**: Ambos PASS

---

## Quick Validation Script

Script completo para ejecutar todas las verificaciones de una vez:

```bash
#!/bin/bash
# validate_quality_overhaul.sh

echo "============================================"
echo "Validacion: Correccion de Defectos de Calidad"
echo "============================================"
echo ""

PASS_COUNT=0
FAIL_COUNT=0

run_check() {
  local name="$1"
  local result="$2"
  if [ "$result" -eq 0 ]; then
    echo "PASS: $name"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "FAIL: $name"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

# 1. Emojis en templates
EMOJI_T=$(find reservas/templates/ -name "*.html" -exec grep -lP '[\x{1F300}-\x{1F9FF}]' {} \; 2>/dev/null | wc -l)
run_check "Emojis en templates" $EMOJI_T

# 2. Emojis en docs
EMOJI_D=$(find . -name "*.md" -not -path "./.venv/*" -not -path "./.git/*" -not -path "./specs/*" -exec grep -lP '[\x{1F300}-\x{1F9FF}]' {} \; 2>/dev/null | wc -l)
run_check "Emojis en documentacion" $EMOJI_D

# 3. Placeholders
TU=$(grep -r "TU_USUARIO" . --include="*.md" --include="*.html" --include="*.py" 2>/dev/null | wc -l)
run_check "Placeholder TU_USUARIO" $TU

HP=$(grep -r "Hotel Paradise" reservas/templates/ 2>/dev/null | wc -l)
run_check "Placeholder Hotel Paradise" $HP

# 4. Archivos eliminados
test ! -f RESUMEN_GITHUB.md; run_check "RESUMEN_GITHUB.md eliminado" $?
test ! -f GITHUB_CHECKLIST.md; run_check "GITHUB_CHECKLIST.md eliminado" $?
test ! -f APRENDIZAJE_PYTHON.md; run_check "APRENDIZAJE_PYTHON.md eliminado" $?
test ! -f verify_github_ready.py; run_check "verify_github_ready.py eliminado" $?

# 5. db.sqlite3
DB_TRACKED=$(git ls-files | grep "db.sqlite3" | wc -l)
run_check "db.sqlite3 no trackeado" $DB_TRACKED

# 6. Directorios vacios
test ! -d static/images/galeria; run_check "Directorio galeria/ eliminado" $?
test ! -d static/images/iconos; run_check "Directorio iconos/ eliminado" $?

# 7. README narrativa
grep -q "Becerrea" README.md; run_check "README menciona Becerrea" $?

# 8. Tests
python manage.py check 2>&1 > /dev/null; run_check "manage.py check" $?
python manage.py test reservas 2>&1 > /dev/null; run_check "manage.py test" $?

echo ""
echo "============================================"
echo "Resultados: $PASS_COUNT PASS, $FAIL_COUNT FAIL"
echo "============================================"

if [ $FAIL_COUNT -eq 0 ]; then
  echo "TODAS LAS VALIDACIONES PASARON"
  exit 0
else
  echo "HAY VALIDACIONES FALLIDAS"
  exit 1
fi
```

## Expected Results

| Check | Expected |
|-------|----------|
| Emojis en templates | 0 archivos |
| Emojis en documentacion | 0 archivos |
| TU_USUARIO | 0 ocurrencias |
| Hotel Paradise | 0 ocurrencias |
| Telefono XXX | 0 ocurrencias |
| Archivos eliminados | 4 archivos eliminados |
| db.sqlite3 | No trackeado |
| Directorios vacios | 3 directorios eliminados |
| README narrativa | Menciona Becerrea, Galicia |
| manage.py check | Exit 0 |
| manage.py test | 47 tests passing |

## Troubleshooting

### Si los tests fallan tras cambios en templates

Causa probable: Se modifico una URL o nombre de template referenciado en tests.
Solucion: Verificar que los nombres de templates en `render()` no cambiaron.

### Si .mo no se recompila

Causa probable: msgfmt no disponible o .po tiene errores de sintaxis.
Solucion: Usar fallback `python compile_mo.py` o verificar sintaxis de .po.

### Si db.sqlite3 sigue trackeado tras git rm --cached

Causa probable: No se hizo commit del cambio.
Solucion: `git commit -m "chore: elimina db.sqlite3 del tracking"`
