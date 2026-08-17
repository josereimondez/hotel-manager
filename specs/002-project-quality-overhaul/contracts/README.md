# Contracts: Correccion de Defectos de Calidad

**Feature**: 002-project-quality-overhaul
**Date**: 2026-08-14

## Overview

Esta feature no introduce nuevas interfaces externas (APIs, CLIs, endpoints). Los "contratos" de esta iteracion son las reglas de calidad que deben cumplir los archivos modificados.

## Contract 1: Templates HTML sin Emojis

**Tipo**: Contrato de contenido

**Regla**: Ningun template HTML en `reservas/templates/reservas/` debe contener caracteres emoji (Unicode ranges U+1F300-U+1F9FF, U+2600-U+26FF, U+2700-U+27BF).

**Verificacion**:
```bash
find reservas/templates/ -name "*.html" -exec grep -lP '[\x{1F300}-\x{1F9FF}\x{2600}-\x{26FF}\x{2700}-\x{27BF}]' {} \;
# Resultado esperado: sin archivos (exit code 1)
```

**Dependencias**: Ninguna. Cambio independiente.

---

## Contract 2: Templates HTML sin Placeholders

**Tipo**: Contrato de contenido

**Regla**: Ningun template HTML debe contener:
- "Hotel Paradise" (en cualquier parte)
- "+34-XXX-XXX-XXX" o variantes
- `href="#"` en enlaces sociales del footer

**Verificacion**:
```bash
grep -r "Hotel Paradise" reservas/templates/
grep -r "+34-XXX" reservas/templates/
grep -r 'href="#"' reservas/templates/
# Todos deben retornar exit code 1 (sin resultados)
```

**Dependencias**: Decision sobre telefono real y redes sociales reales.

---

## Contract 3: Documentacion Consistente

**Tipo**: Contrato de consistencia

**Regla**: Todos los archivos .md deben referenciar:
- Django==5.2.4 (no 5.0.2 ni 5.0)
- 7+ modelos (no 3)
- Estructura de static/ correcta (sin css/ ni js/ locales)

**Verificacion**:
```bash
grep -r "Django==5.0" *.md
grep -r "3 modelos" *.md
grep -r "static/css" *.md
# Todos deben retornar exit code 1
```

**Dependencias**: Ninguna. Cambio de texto.

---

## Contract 4: Documentacion sin Emojis

**Tipo**: Contrato de contenido

**Regla**: Ningun archivo .md debe contener emojis.

**Verificacion**:
```bash
find . -name "*.md" -not -path "./.venv/*" -not -path "./.git/*" -exec grep -lP '[\x{1F300}-\x{1F9FF}]' {} \;
# Resultado esperado: sin archivos
```

**Dependencias**: Ninguna. Cambio de texto.

---

## Contract 5: Archivos .po/.mo Sincronizados

**Tipo**: Contrato de compilacion

**Regla**: Tras modificar archivos .po, los archivos .mo deben recompilarse con `python manage.py compilemessages` y commitearse juntos.

**Verificacion**:
```bash
# Verificar que .mo son mas recientes que .po
for lang in es gl en; do
  po="locale/$lang/LC_MESSAGES/django.po"
  mo="locale/$lang/LC_MESSAGES/django.mo"
  if [ -f "$po" ] && [ -f "$mo" ]; then
    if [ "$po" -nt "$mo" ]; then
      echo "ERROR: $mo es mas antiguo que $po"
    fi
  fi
done
```

**Dependencias**: msgfmt disponible en el sistema (confirmado en AGENTS.md).

---

## Contract 6: Repositorio Limpio

**Tipo**: Contrato de versionado

**Regla**: 
- db.sqlite3 no debe estar trackeado en git
- Archivos eliminados (RESUMEN_GITHUB.md, etc.) no deben existir
- .gitignore debe excluir db.sqlite3, .env, media/, venv/

**Verificacion**:
```bash
git ls-files | grep "db.sqlite3"     # Sin resultados
ls RESUMEN_GITHUB.md 2>/dev/null     # No existe
ls GITHUB_CHECKLIST.md 2>/dev/null   # No existe
ls APRENDIZAJE_PYTHON.md 2>/dev/null # No existe
ls verify_github_ready.py 2>/dev/null # No existe
grep "db.sqlite3" .gitignore         # Debe existir
```

**Dependencias**: Ninguna.

---

## Contract 7: Tests Pasando

**Tipo**: Contrato de calidad

**Regla**: Tras todos los cambios, los 47 tests existentes deben pasar sin errores.

**Verificacion**:
```bash
python manage.py check
python manage.py test reservas
# Ambos deben exit 0
```

**Dependencias**: Todos los cambios anteriores completados.

---

## Contract 8: README con Narrativa

**Tipo**: Contrato de contenido

**Regla**: README.md debe incluir:
- Nombre "Hostal Rivera" (no generico)
- Ubicacion: Becerrea, Lugo, Galicia
- Contexto: Camino de Santiago / Via Kunig
- Proposito: sistema de gestion hotelera

**Verificacion**: Inspeccion humana.

**Dependencias**: Ninguna.

---

## Summary

| Contract | Tipo | Verificacion | Dependencias |
|----------|------|--------------|--------------|
| 1. Templates sin emojis | Contenido | grep Unicode | Ninguna |
| 2. Templates sin placeholders | Contenido | grep patrones | Decision telefono/redes |
| 3. Docs consistentes | Consistencia | grep versiones | Ninguna |
| 4. Docs sin emojis | Contenido | grep Unicode | Ninguna |
| 5. .po/.mo sincronizados | Compilacion | timestamps | msgfmt |
| 6. Repo limpio | Versionado | git ls-files | Ninguna |
| 7. Tests pasando | Calidad | manage.py test | Todos los cambios |
| 8. README narrativa | Contenido | Inspeccion humana | Ninguna |

Todos los contratos son independientes entre si, excepto Contract 7 (tests) que depende de todos los demas.
