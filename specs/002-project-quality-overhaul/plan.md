# Implementation Plan: Correccion de Defectos de Calidad y Autenticidad

**Branch**: `002-project-quality-overhaul` | **Date**: 2026-08-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-project-quality-overhaul/spec.md`

## Summary

Correccion integral de defectos de calidad que hacen que el proyecto parezca generado por IA: eliminacion de ~441 emojis en templates y documentacion, reemplazo de placeholders sin personalizar (TU_USUARIO, Hotel Paradise, telefonos XXX), resolucion de inconsistencias entre documentacion y codigo (versiones de Django, numero de modelos), creacion de narrativa real del Hostal Rivera, eliminacion de documentacion redundante, y correccion de detalles menores (banderas i18n, db.sqlite3 commiteado).

Enfoque tecnico: cambios de contenido en templates HTML, archivos Markdown, y archivos de traduccion .po. Sin nuevos modelos, APIs, o dependencias. Cambios minimos de codigo (principalmente find-and-replace y eliminacion de archivos).

## Technical Context

**Language/Version**: Python 3.11-3.13, Django 5.2.4

**Primary Dependencies**: Django 5.2.4, python-decouple 3.8, django-crispy-forms 2.1, crispy-bootstrap5 2.0.0, reportlab 4.1.0, openpyxl 3.1.2, Pillow 11.1.0, python-stdnum 1.20

**Storage**: SQLite (desarrollo) / PostgreSQL (produccion)

**Testing**: Django test framework (`python manage.py test reservas`), 47 tests existentes

**Target Platform**: Linux server (aplicacion web Django MVT)

**Project Type**: web-service (sistema de gestion hotelera)

**Performance Goals**: Estandar para aplicacion web Django (no se esperan cambios de rendimiento)

**Constraints**: Cumplimiento de constitucion del proyecto (version 1.0.0), mantener funcionalidad existente, no romper tests

**Scale/Scope**: ~5000 LOC, 7 modelos, 20 templates, 15 archivos Markdown, 3 idiomas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate 1: Seguridad Primero

**Principio**: Input validation, rate limiting, no credentials committed.

**Evaluacion**: PASS. Esta iteracion no introduce nuevos endpoints, no modifica validacion de inputs, no commite credenciales. Los cambios son cosmeticos (eliminacion de emojis, correccion de texto).

**Justificacion**: N/A

### Gate 2: ORM-First (NON-NEGOTIABLE)

**Principio**: Toda interaccion con BD usa ORM Django, no SQL crudo.

**Evaluacion**: PASS. Esta iteracion no modifica modelos ni consultas a base de datos.

**Justificacion**: N/A

### Gate 3: Test-Verified

**Principio**: Todo cambio debe pasar `python manage.py check` y `python manage.py test reservas`.

**Evaluacion**: PASS (condicional). Los cambios en templates y documentacion no deben romper tests. Se verificara al final con ejecucion de tests.

**Justificacion**: N/A

### Gate 4: Cumplimiento Normativo

**Principio**: Campos SES Hospedajes son prioritarios, validacion DNI/NIE con python-stdnum.

**Evaluacion**: PASS. Esta iteracion no modifica campos SES Hospedajes ni validacion DNI/NIE.

**Justificacion**: N/A

### Gate 5: Multiidioma Nativo

**Principio**: Todo texto visible usa traducciones (gettext/_()). Archivos .po editados requieren recompilar .mo.

**Evaluacion**: PASS (condicional). Si se eliminan emojis de cadenas traducibles en .po, se debe ejecutar `python manage.py compilemessages` y commitear .mo actualizados.

**Justificacion**: N/A

### Post-Design Re-Check

Tras completar Phase 1 (diseno), se re-evaluaran los gates para confirmar que el diseno no introduce violaciones.

**Resultado**: Todos los gates pasan. No hay violaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/002-project-quality-overhaul/
├── plan.md              # Este archivo (output de /speckit.plan)
├── research.md          # Output de Phase 0
├── data-model.md        # Output de Phase 1 (mapeo de archivos afectados)
├── quickstart.md        # Output de Phase 1 (guia de validacion)
├── contracts/           # Output de Phase 1 (no aplica - sin APIs nuevas)
├── spec.md              # Especificacion (output de /speckit.specify)
└── checklists/
    └── requirements.md  # Checklist de calidad de spec
```

### Source Code (repository root)

```text
hotel-manager/
├── reservas/
│   └── templates/
│       └── reservas/
│           ├── base.html                      # Modificar: eliminar emojis, corregir bandera galego
│           ├── home.html                      # Modificar: eliminar emojis
│           ├── menu_del_dia.html              # Modificar: eliminar emojis
│           ├── detalle_habitacion.html        # Modificar: eliminar emojis
│           ├── perfil.html                    # Modificar: eliminar emojis
│           ├── editar_menu_del_dia.html       # Modificar: eliminar emojis
│           ├── editar_menu_especial.html      # Modificar: eliminar emojis
│           ├── editar_perfil.html             # Modificar: eliminar emojis
│           ├── mis_reservas.html              # Modificar: eliminar emojis, corregir titulo
│           ├── crear_reserva.html             # Modificar: eliminar emojis
│           ├── listado_habitaciones.html      # Modificar: eliminar emojis, corregir titulo
│           ├── registro_cliente.html          # Modificar: eliminar emojis, corregir titulo
│           ├── detalle_reserva.html           # Modificar: eliminar emojis
│           ├── politica_cookies.html          # Modificar: eliminar emojis
│           ├── login.html                     # Modificar: corregir titulo
│           ├── politica_privacidad.html       # Modificar: corregir telefono
│           └── terminos_condiciones.html      # Modificar: corregir telefono
│
├── locale/
│   ├── es/LC_MESSAGES/
│   │   ├── django.po                        # Modificar si contiene emojis
│   │   └── django.mo                        # Recompilar
│   ├── gl/LC_MESSAGES/
│   │   ├── django.po                        # Modificar si contiene emojis
│   │   └── django.mo                        # Recompilar
│   └── en/LC_MESSAGES/
│       ├── django.po                        # Modificar si contiene emojis
│       └── django.mo                        # Recompilar
│
├── static/
│   └── images/
│       ├── logo/                            # Mantener (existe logo real)
│       ├── background/                      # Mantener (existe background real)
│       ├── galeria/                         # Eliminar (solo contiene README.txt)
│       ├── iconos/                          # Eliminar (solo contiene README.txt)
│       └── via_kunig/                       # Eliminar (solo contiene README.txt)
│
├── README.md                                # Reescribir: narrativa real, eliminar emojis
├── SECURITY.md                              # Modificar: eliminar emojis
├── CONTRIBUTING.md                          # Modificar: eliminar emojis
├── CHANGELOG.md                             # Modificar: actualizar version Django
├── DEPLOYMENT.md                            # Modificar: eliminar emojis, corregir TU_USUARIO
├── SEO_STRATEGY.md                          # Modificar: eliminar emojis
├── INPUT_SANITIZATION.md                    # Modificar: eliminar emojis
├── RESUMEN_GITHUB.md                        # Eliminar (redundante)
├── GITHUB_CHECKLIST.md                      # Eliminar (innecesario)
├── APRENDIZAJE_PYTHON.md                    # Eliminar (no es doc del proyecto)
├── GUIA_SPEC_KIT.md                         # Modificar: actualizar version Django
├── verify_github_ready.py                   # Eliminar (script de portfolio)
├── AGENTS.md                                # Modificar: corregir version Django
├── db.sqlite3                               # Eliminar del tracking git
└── .gitignore                               # Verificar que excluye db.sqlite3
```

**Structure Decision**: Estructura existente del proyecto Django MVT. No se introducen nuevos directorios o modulos. Los cambios son modificaciones de contenido en archivos existentes y eliminacion de archivos redundantes.

## Complexity Tracking

> **No aplica**: No hay violaciones de constitucion que justificar.
