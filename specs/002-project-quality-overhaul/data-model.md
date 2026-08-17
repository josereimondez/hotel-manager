# Data Model: Correccion de Defectos de Calidad

**Feature**: 002-project-quality-overhaul
**Date**: 2026-08-14

## Overview

Esta feature no introduce nuevos modelos de base de datos. El "modelo de datos" de esta iteracion es el mapeo de archivos afectados y los cambios requeridos en cada uno.

## Inventario de Archivos Afectados

### Templates HTML (20 archivos)

| Archivo | Emojis | Placeholders | Cambios Requeridos |
|---------|--------|--------------|-------------------|
| base.html | 36 | Bandera galego, telefono JSON-LD | Eliminar emojis, corregir bandera, corregir telefono JSON-LD |
| home.html | 22 | - | Eliminar emojis |
| menu_del_dia.html | 23 | - | Eliminar emojis |
| detalle_habitacion.html | 14 | - | Eliminar emojis |
| perfil.html | 9 | - | Eliminar emojis |
| editar_menu_del_dia.html | 6 | - | Eliminar emojis |
| editar_menu_especial.html | 5 | - | Eliminar emojis |
| editar_perfil.html | 6 | - | Eliminar emojis |
| mis_reservas.html | 4 | "Hotel Paradise" en title | Eliminar emojis, corregir titulo |
| crear_reserva.html | 2 | - | Eliminar emojis |
| listado_habitaciones.html | 2 | "Hotel Paradise" en title | Eliminar emojis, corregir titulo |
| registro_cliente.html | 2 | "Hotel Paradise" en title | Eliminar emojis, corregir titulo |
| detalle_reserva.html | 1 | - | Eliminar emojis |
| politica_cookies.html | 1 | - | Eliminar emojis |
| login.html | 0 | "Hotel Paradise" en title | Corregir titulo |
| politica_privacidad.html | 0 | Telefono placeholder | Corregir telefono |
| terminos_condiciones.html | 0 | Telefono placeholder | Corregir telefono |
| checkin_online.html | 0 | - | Sin cambios |
| error_ratelimit.html | 0 | - | Sin cambios |
| via_kunig.html | 0 | - | Sin cambios |

**Total emojis en templates**: 136 instancias

### Archivos de Documentacion (15 archivos)

| Archivo | Emojis | Placeholders | Cambios Requeridos |
|---------|--------|--------------|-------------------|
| README.md | 39 | TU_USUARIO (1), estructura incorrecta | Reescribir: narrativa real, eliminar emojis, corregir placeholders |
| SECURITY.md | 24 | - | Eliminar emojis |
| CONTRIBUTING.md | 12 | TU_USUARIO (2) | Eliminar emojis, corregir placeholders |
| CHANGELOG.md | 0 | Version Django incorrecta | Actualizar version Django 5.0 -> 5.2.4 |
| DEPLOYMENT.md | 9 | TU_USUARIO (2) | Eliminar emojis, corregir placeholders |
| SEO_STRATEGY.md | 17 | - | Eliminar emojis |
| INPUT_SANITIZATION.md | 62 | - | Eliminar emojis |
| RESUMEN_GITHUB.md | 83 | TU_USUARIO (3), versiones incorrectas | ELIMINAR (redundante) |
| GITHUB_CHECKLIST.md | 53 | TU_USUARIO (2) | ELIMINAR (innecesario) |
| APRENDIZAJE_PYTHON.md | 5 | - | ELIMINAR (no es doc del proyecto) |
| GUIA_SPEC_KIT.md | 0 | Version Django incorrecta | Actualizar version Django |
| AGENTS.md | 0 | Version Django incorrecta | Actualizar version Django 5.0.2 -> 5.2.4 |
| GUIA_SES_HOSPEDAJES_CHECKIN.md | 0 | - | Sin cambios |
| dokploy.md | 0 | - | Sin cambios |
| migracionPostgre.MD | 0 | - | Sin cambios |

**Total emojis en docs**: 305 instancias

### Archivos de Traduccion (6 archivos: 3 .po + 3 .mo)

| Archivo | Accion |
|---------|--------|
| locale/es/LC_MESSAGES/django.po | Buscar emojis en cadenas, eliminar si existen |
| locale/gl/LC_MESSAGES/django.po | Buscar emojis en cadenas, eliminar si existen |
| locale/en/LC_MESSAGES/django.po | Buscar emojis en cadenas, eliminar si existen |
| locale/es/LC_MESSAGES/django.mo | Recompilar tras cambios en .po |
| locale/gl/LC_MESSAGES/django.mo | Recompilar tras cambios en .po |
| locale/en/LC_MESSAGES/django.mo | Recompilar tras cambios en .po |

### Archivos Estaticos

| Ruta | Accion |
|------|--------|
| static/images/galeria/README.txt | Eliminar directorio completo |
| static/images/iconos/README.txt | Eliminar directorio completo |
| static/images/via_kunig/README.txt | Eliminar directorio completo |
| static/images/logo/ | Mantener |
| static/images/background/ | Mantener |

### Archivos del Repositorio

| Archivo | Accion | Rationale |
|---------|--------|-----------|
| RESUMEN_GITHUB.md | ELIMINAR | 100% redundante con README |
| GITHUB_CHECKLIST.md | ELIMINAR | Guia basica de git innecesaria |
| APRENDIZAJE_PYTHON.md | ELIMINAR | Tutorial de Python, no es doc del proyecto |
| verify_github_ready.py | ELIMINAR | Script de portfolio, no herramienta del producto |
| db.sqlite3 | git rm --cached | No debe estar trackeado |
| .gitignore | Verificar | Asegurar que excluye db.sqlite3 |

## Entidades de Cambio

### Entidad 1: Texto de Template

- **Representa**: Contenido visible de plantillas HTML
- **Atributos**: emojis (count), placeholders (count), titulo (string)
- **Reglas de validacion**: cero emojis, cero placeholders conocidos, titulo = "Hostal Rivera"
- **Transiciones**: estado actual (con defectos) -> estado final (limpio)

### Entidad 2: Documentacion Markdown

- **Representa**: Archivos .md del repositorio
- **Atributos**: emojis (count), consistencia (bool), redundancia (bool)
- **Reglas de validacion**: cero emojis, versiones consistentes con requirements.txt, sin archivos redundantes
- **Transiciones**: estado actual -> revisado y actualizado

### Entidad 3: Configuracion Git

- **Representa**: Archivos trackeados y .gitignore
- **Atributos**: archivos trackeados (list), exclusiones (list)
- **Reglas de validacion**: db.sqlite3 no trackeado, .gitignore completo
- **Transiciones**: db.sqlite3 trackeado -> db.sqlite3 no trackeado

## Relaciones

```
Templates HTML --- contienen --> Emojis (a eliminar)
Templates HTML --- contienen --> Placeholders (a reemplazar)
Templates HTML --- referencian --> Imagenes estaticas
Documentacion --- referencia --> Versiones de dependencias
Documentacion --- referencia --> Numero de modelos
Archivos .po --- generan --> Archivos .mo (recompilar)
.gitignore --- excluye --> db.sqlite3, .env, media/, venv/
```

## No Aplica

- Nuevos modelos de base de datos
- Nuevas relaciones entre entidades existentes
- Migraciones de base de datos
- Cambios en estructura de modelos Django
