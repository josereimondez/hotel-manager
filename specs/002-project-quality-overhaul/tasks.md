# Tasks: Correccion de Defectos de Calidad y Autenticidad

**Input**: Design documents from `/specs/002-project-quality-overhaul/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No se incluyen tareas de test explicitas. La validacion se realiza mediante el script de quickstart.md y los contratos de calidad.

**Organization**: Tareas agrupadas por user story para permitir implementacion y validacion independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos diferentes, sin dependencias)
- **[Story]**: User story al que pertenece (US1, US2, US3, US4, US5, US6)
- Incluir rutas exactas de archivos en descripciones

---

## Phase 1: Setup (Preparacion del Entorno)

**Purpose**: Preparar el entorno de trabajo y verificar estado actual

- [x] T001 Verificar que el entorno virtual esta activo y dependencias instaladas (`pip list | grep Django`)
- [x] T002 Configurar variables de entorno para desarrollo (DEBUG=True, SECRET_KEY, ALLOWED_HOSTS)
- [x] T003 [P] Ejecutar `python manage.py check` para verificar estado actual sin errores
- [x] T004 [P] Ejecutar `python manage.py test reservas` para confirmar 47 tests pasando
- [x] T005 Crear script de validacion `validate_quality_overhaul.sh` basado en quickstart.md

**Checkpoint**: Entorno listo, tests pasando, script de validacion disponible

---

## Phase 2: Foundational (Prerequisitos Bloqueantes)

**Purpose**: Tareas base que deben completarse antes de cualquier user story

**CRITICAL**: Ningun user story puede comenzar hasta que esta fase este completa

- [x] T006 Crear backup de archivos actuales: `git status` y verificar working tree limpio
- [x] T007 Hacer commit de estado actual si hay cambios pendientes: `git add . && git commit -m "chore: estado previo a correccion de calidad"`
- [x] T008 Verificar que msgfmt esta disponible para compilar .po: `which msgfmt`
- [x] T009 [P] Identificar todos los archivos .po que contienen emojis: `grep -lP '[\x{1F300}-\x{1F9FF}]' locale/*/LC_MESSAGES/django.po`
- [x] T010 [P] Verificar que .gitignore excluye db.sqlite3, .env, media/, venv/

**Checkpoint**: Backup listo, herramientas verificadas, .gitignore correcto

---

## Phase 3: User Story 1 - Eliminacion de Apariencia IA (Emojis) (Priority: P1) MVP

**Goal**: Eliminar todos los emojis de templates HTML y archivos Markdown para eliminar apariencia de generacion por IA

**Independent Test**: `find reservas/templates/ -name "*.html" -exec grep -lP '[\x{1F300}-\x{1F9FF}]' {} \;` retorna cero archivos

### Implementation for User Story 1

- [x] T011 [US1] Eliminar emojis de navbar en reservas/templates/reservas/base.html (36 emojis: iconos de navegacion, menu, footer)
- [x] T012 [P] [US1] Eliminar emojis de home en reservas/templates/reservas/home.html (22 emojis: iconos de servicios, caracteristicas)
- [x] T013 [P] [US1] Eliminar emojis de menu del dia en reservas/templates/reservas/menu_del_dia.html (23 emojis: categorias de platos, iconos)
- [x] T014 [P] [US1] Eliminar emojis de detalle habitacion en reservas/templates/reservas/detalle_habitacion.html (14 emojis: amenidades, iconos)
- [x] T015 [P] [US1] Eliminar emojis de perfil en reservas/templates/reservas/perfil.html (9 emojis: iconos de secciones)
- [x] T016 [P] [US1] Eliminar emojis de editar menu del dia en reservas/templates/reservas/editar_menu_del_dia.html (6 emojis)
- [x] T017 [P] [US1] Eliminar emojis de editar menu especial en reservas/templates/reservas/editar_menu_especial.html (5 emojis)
- [x] T018 [P] [US1] Eliminar emojis de editar perfil en reservas/templates/reservas/editar_perfil.html (6 emojis)
- [x] T019 [P] [US1] Eliminar emojis de mis reservas en reservas/templates/reservas/mis_reservas.html (4 emojis)
- [x] T020 [P] [US1] Eliminar emojis de crear reserva en reservas/templates/reservas/crear_reserva.html (2 emojis)
- [x] T021 [P] [US1] Eliminar emojis de listado habitaciones en reservas/templates/reservas/listado_habitaciones.html (2 emojis)
- [x] T022 [P] [US1] Eliminar emojis de registro cliente en reservas/templates/reservas/registro_cliente.html (2 emojis)
- [x] T023 [P] [US1] Eliminar emojis de detalle reserva en reservas/templates/reservas/detalle_reserva.html (1 emoji)
- [x] T024 [P] [US1] Eliminar emojis de politica cookies en reservas/templates/reservas/politica_cookies.html (1 emoji)
- [x] T025 [US1] Eliminar emojis de README.md (39 emojis: titulos, listas, iconos)
- [x] T026 [P] [US1] Eliminar emojis de SECURITY.md (24 emojis)
- [x] T027 [P] [US1] Eliminar emojis de CONTRIBUTING.md (12 emojis)
- [x] T028 [P] [US1] Eliminar emojis de DEPLOYMENT.md (9 emojis)
- [x] T029 [P] [US1] Eliminar emojis de SEO_STRATEGY.md (17 emojis)
- [x] T030 [P] [US1] Eliminar emojis de INPUT_SANITIZATION.md (62 emojis)
- [x] T031 [US1] Buscar y eliminar emojis de archivos .po si existen: `grep -P '[\x{1F300}-\x{1F9FF}]' locale/*/LC_MESSAGES/django.po`
- [x] T032 [US1] Recompilar archivos .mo tras cambios en .po: `python manage.py compilemessages`
- [x] T033 [US1] Validar cero emojis en templates: ejecutar script de validacion (Contract 1)
- [x] T034 [US1] Validar cero emojis en documentacion: ejecutar script de validacion (Contract 4)

**Checkpoint**: Todos los emojis eliminados, .mo recompilados, contratos 1 y 4 pasando

---

## Phase 4: User Story 2 - Correccion de Placeholders (Priority: P1)

**Goal**: Reemplazar todos los placeholders sin personalizar (TU_USUARIO, Hotel Paradise, telefonos XXX, enlaces #)

**Independent Test**: `grep -r "TU_USUARIO\|Hotel Paradise\|+34-XXX" . --include="*.md" --include="*.html"` retorna cero resultados

### Implementation for User Story 2

- [x] T035 [US2] Reemplazar "Hotel Paradise" por "Hostal Rivera" en reservas/templates/reservas/login.html (linea 4, title)
- [x] T036 [P] [US2] Reemplazar "Hotel Paradise" por "Hostal Rivera" en reservas/templates/reservas/registro_cliente.html (linea 4)
- [x] T037 [P] [US2] Reemplazar "Hotel Paradise" por "Hostal Rivera" en reservas/templates/reservas/listado_habitaciones.html (linea 4)
- [x] T038 [P] [US2] Reemplazar "Hotel Paradise" por "Hostal Rivera" en reservas/templates/reservas/mis_reservas.html (linea 4)
- [x] T039 [US2] Reemplazar telefono "+34-XXX-XXX-XXX" por "+34 982 360 185" en reservas/templates/reservas/base.html (linea 283, JSON-LD)
- [x] T040 [P] [US2] Reemplazar telefono placeholder en reservas/templates/reservas/politica_privacidad.html (linea 21)
- [x] T041 [P] [US2] Reemplazar telefono placeholder en reservas/templates/reservas/terminos_condiciones.html (linea 173)
- [x] T042 [US2] Eliminar o reemplazar enlaces sociales con "#" en footer de reservas/templates/reservas/base.html (Facebook, Instagram)
- [x] T043 [US2] Eliminar referencias a imagenes inexistentes (og-image.jpg, restaurant.jpg) de reservas/templates/reservas/base.html
- [x] T044 [US2] Reemplazar "TU_USUARIO" en README.md (1 ocurrencia en git clone URL)
- [x] T045 [P] [US2] Reemplazar "TU_USUARIO" en CONTRIBUTING.md (2 ocurrencias)
- [x] T046 [P] [US2] Reemplazar "TU_USUARIO" en DEPLOYMENT.md (2 ocurrencias)
- [x] T047 [US2] Validar cero placeholders: ejecutar script de validacion (Contract 2)

**Checkpoint**: Todos los placeholders reemplazados, contrato 2 pasando

---

## Phase 5: User Story 3 - Resolucion de Inconsistencias (Priority: P1)

**Goal**: Asegurar que documentacion y codigo sean consistentes (versiones Django, numero de modelos, estructura)

**Independent Test**: `grep -r "Django==5.0\|3 modelos" *.md` retorna cero resultados

### Implementation for User Story 3

- [x] T048 [US3] Actualizar AGENTS.md: cambiar "Django 5.0.2" por "Django 5.2.4" (buscar en linea 1 y linea 7)
- [x] T049 [P] [US3] Actualizar GUIA_SPEC_KIT.md: cambiar "Django 5.0.2" por "Django 5.2.4"
- [x] T050 [P] [US3] Actualizar CHANGELOG.md: agregar entrada para migracion Django 5.0 -> 5.2.4
- [x] T051 [US3] Actualizar documentacion que menciona "3 modelos" para reflejar 7+ modelos (buscar en RESUMEN_GITHUB.md si existe, otros docs)
- [x] T052 [US3] Corregir estructura de static/ en documentacion: eliminar referencias a static/css/ y static/js/ inexistentes (README.md, RESUMEN_GITHUB.md si existe)
- [x] T053 [US3] Aclarar que CSS/JS provienen de CDN en README.md y DEPLOYMENT.md
- [x] T054 [US3] Validar consistencia de versiones: ejecutar script de validacion (Contract 3)

**Checkpoint**: Todas las versiones consistentes, contrato 3 pasando

---

## Phase 6: User Story 4 - Narrativa e Historia (Priority: P1)

**Goal**: Incluir narrativa real del Hostal Rivera en README.md (ubicacion, contexto, proposito)

**Independent Test**: `grep "Becerrea\|Galicia\|Camino de Santiago" README.md` retorna resultados

### Implementation for User Story 4

- [x] T055 [US4] Reescribir introduccion de README.md: incluir nombre "Hostal Rivera", ubicacion "Becerrea, Lugo, Galicia", contexto "Camino de Santiago / Via Kunig"
- [x] T056 [US4] Agregar seccion "Sobre el Hostal" en README.md: descripcion del hostal real, caracteristicas unicas, entorno rural gallego
- [x] T057 [US4] Reemplazar tono generico de plantilla por contenido especifico del hostal en README.md
- [x] T058 [US4] Asegurar que README.md, CONTRIBUTING.md, SECURITY.md usen "Hostal Rivera" consistentemente
- [x] T059 [US4] Validar narrativa: leer README.md y verificar que responde: que es, donde esta, para quien es, que problema resuelve (Contract 8)

**Checkpoint**: README con narrativa autentica, contrato 8 pasando

---

## Phase 7: User Story 5 - Eliminacion de Documentacion Redundante (Priority: P2)

**Goal**: Eliminar archivos de documentacion redundantes y pedagogicos que inflan el repositorio

**Independent Test**: `ls RESUMEN_GITHUB.md GITHUB_CHECKLIST.md APRENDIZAJE_PYTHON.md verify_github_ready.py 2>&1` retorna "No such file"

### Implementation for User Story 5

- [x] T060 [US5] Eliminar RESUMEN_GITHUB.md: `rm RESUMEN_GITHUB.md` (contenido 100% redundante con README)
- [x] T061 [P] [US5] Eliminar GITHUB_CHECKLIST.md: `rm GITHUB_CHECKLIST.md` (guia basica de git innecesaria)
- [x] T062 [P] [US5] Eliminar APRENDIZAJE_PYTHON.md: `rm APRENDIZAJE_PYTHON.md` (tutorial de Python, no es doc del proyecto)
- [x] T063 [P] [US5] Eliminar verify_github_ready.py: `rm verify_github_ready.py` (script de portfolio)
- [x] T064 [US5] Verificar que no hay enlaces rotos a archivos eliminados en otros .md
- [x] T065 [US5] Validar archivos eliminados: ejecutar script de validacion

**Checkpoint**: Archivos redundantes eliminados, sin enlaces rotos

---

## Phase 8: User Story 6 - Detalles Menores de Calidad (Priority: P2)

**Goal**: Corregir detalles menores: bandera de galego, db.sqlite3 commiteado, directorios de imagenes vacios

**Independent Test**: Script de validacion completo pasando

### Implementation for User Story 6

- [x] T066 [US6] Corregir bandera de galego en selector de idioma de reservas/templates/reservas/base.html: reemplazar emoji 🇪🇸 por texto "Galego"
- [x] T067 [US6] Eliminar db.sqlite3 del tracking git: `git rm --cached db.sqlite3`
- [x] T068 [US6] Hacer commit de eliminacion de db.sqlite3: `git commit -m "chore: elimina db.sqlite3 del tracking"`
- [x] T069 [P] [US6] Eliminar directorio static/images/galeria/: `rm -rf static/images/galeria/`
- [x] T070 [P] [US6] Eliminar directorio static/images/iconos/: `rm -rf static/images/iconos/`
- [x] T071 [P] [US6] Eliminar directorio static/images/via_kunig/: `rm -rf static/images/via_kunig/`
- [x] T072 [US6] Verificar que templates no referencian imagenes en directorios eliminados
- [x] T073 [US6] Asegurar coherencia en emails de contacto: verificar que todos sean ficticios consistentes o reales

**Checkpoint**: Detalles menores corregidos, directorios vacios eliminados

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Validacion final y limpieza

- [x] T074 Ejecutar script de validacion completo `validate_quality_overhaul.sh` (quickstart.md)
- [x] T075 [P] Verificar que todos los contratos de calidad pasan (contracts/README.md)
- [x] T076 [P] Ejecutar `python manage.py check` para verificar sin errores
- [x] T077 [P] Ejecutar `python manage.py test reservas` para confirmar 47 tests pasando
- [x] T078 Verificar que .mo estan actualizados respecto a .po
- [x] T079 Hacer commit de todos los cambios: `git add . && git commit -m "fix: corrige defectos de calidad y autenticidad del proyecto"`
- [x] T080 Verificar que working tree esta limpio: `git status`

**Checkpoint**: Todas las validaciones pasando, cambios commiteados

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias - puede comenzar inmediatamente
- **Foundational (Phase 2)**: Depende de Setup - BLOQUEA todos los user stories
- **User Stories (Phase 3-8)**: Todas dependen de Foundational
  - US1 (Phase 3): Puede comenzar despues de Phase 2 - sin dependencias de otros stories
  - US2 (Phase 4): Puede comenzar despues de Phase 2 - independiente de US1
  - US3 (Phase 5): Puede comenzar despues de Phase 2 - independiente
  - US4 (Phase 6): Puede comenzar despues de Phase 2 - independiente
  - US5 (Phase 7): Puede comenzar despues de Phase 2 - independiente
  - US6 (Phase 8): Puede comenzar despues de Phase 2 - independiente
- **Polish (Phase 9)**: Depende de todos los user stories deseados completados

### User Story Dependencies

- **US1 (P1)**: Puede comenzar despues de Foundational - sin dependencias
- **US2 (P1)**: Puede comenzar despues de Foundational - sin dependencias
- **US3 (P1)**: Puede comenzar despues de Foundational - sin dependencias
- **US4 (P1)**: Puede comenzar despues de Foundational - sin dependencias
- **US5 (P2)**: Puede comenzar despues de Foundational - sin dependencias
- **US6 (P2)**: Puede comenzar despues de Foundational - sin dependencias

**Nota**: Los user stories son independientes entre si. Pueden ejecutarse en paralelo si hay capacidad, o secuencialmente en orden de prioridad.

### Within Each User Story

- Tareas marcadas [P] pueden ejecutarse en paralelo (archivos diferentes)
- Tareas sin [P] deben ejecutarse secuencialmente
- Validacion al final de cada story

### Parallel Opportunities

- Todas las tareas de Setup marcadas [P] pueden ejecutarse en paralelo
- Todas las tareas de Foundational marcadas [P] pueden ejecutarse en paralelo
- Una vez completado Foundational, todos los user stories pueden comenzar en paralelo
- Dentro de US1: T012-T024 (eliminacion de emojis en templates) pueden ejecutarse en paralelo
- Dentro de US2: T036-T038, T040-T041, T045-T046 pueden ejecutarse en paralelo
- Dentro de US3: T049-T050 pueden ejecutarse en paralelo
- Dentro de US5: T061-T063 pueden ejecutarse en paralelo
- Dentro de US6: T069-T071 pueden ejecutarse en paralelo

---

## Parallel Example: User Story 1

```bash
# Lanzar eliminacion de emojis en todos los templates en paralelo:
Task: T012 "Eliminar emojis de home.html"
Task: T013 "Eliminar emojis de menu_del_dia.html"
Task: T014 "Eliminar emojis de detalle_habitacion.html"
Task: T015 "Eliminar emojis de perfil.html"
# ... etc

# Luego eliminar emojis de documentacion en paralelo:
Task: T026 "Eliminar emojis de SECURITY.md"
Task: T027 "Eliminar emojis de CONTRIBUTING.md"
Task: T028 "Eliminar emojis de DEPLOYMENT.md"
# ... etc
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRITICO - bloquea todos los stories)
3. Completar Phase 3: User Story 1 (eliminacion de emojis)
4. **PARAR Y VALIDAR**: Ejecutar script de validacion, verificar cero emojis
5. Commit del cambio
6. Desplegar/demo si esta listo

### Incremental Delivery

1. Completar Setup + Foundational → Base lista
2. Agregar User Story 1 (emojis) → Validar → Commit → (MVP!)
3. Agregar User Story 2 (placeholders) → Validar → Commit
4. Agregar User Story 3 (inconsistencias) → Validar → Commit
5. Agregar User Story 4 (narrativa) → Validar → Commit
6. Agregar User Story 5 (docs redundantes) → Validar → Commit
7. Agregar User Story 6 (detalles menores) → Validar → Commit
8. Cada story agrega valor sin romper los anteriores

### Parallel Team Strategy

Con multiples desarrolladores:

1. Equipo completa Setup + Foundational juntos
2. Una vez completado Foundational:
   - Desarrollador A: User Story 1 (emojis en templates)
   - Desarrollador B: User Story 2 (placeholders)
   - Desarrollador C: User Story 3 (inconsistencias)
   - Desarrollador D: User Story 4 (narrativa)
3. Stories se completan y validan independientemente
4. Polish final despues de todos los stories

---

## Notes

- Tareas [P] = archivos diferentes, sin dependencias, pueden ejecutarse en paralelo
- Etiqueta [Story] mapea tarea a user story especifica para trazabilidad
- Cada user story es completabile y validable independientemente
- Validar con script de quickstart.md despues de cada story
- Commit despues de cada tarea o grupo logico
- Parar en cualquier checkpoint para validar story independientemente
- Evitar: tareas vagas, conflictos de mismo archivo, dependencias cross-story que rompan independencia

## Resumen de Tareas

- **Total de tareas**: 80
- **Phase 1 (Setup)**: 5 tareas
- **Phase 2 (Foundational)**: 5 tareas
- **Phase 3 (US1 - Emojis)**: 24 tareas
- **Phase 4 (US2 - Placeholders)**: 13 tareas
- **Phase 5 (US3 - Inconsistencias)**: 7 tareas
- **Phase 6 (US4 - Narrativa)**: 5 tareas
- **Phase 7 (US5 - Docs redundantes)**: 6 tareas
- **Phase 8 (US6 - Detalles menores)**: 8 tareas
- **Phase 9 (Polish)**: 7 tareas

**Oportunidades de paralelismo**: ~40 tareas marcadas [P] pueden ejecutarse en paralelo

**MVP Scope**: User Story 1 (eliminacion de emojis) - 24 tareas, entregable independientemente
