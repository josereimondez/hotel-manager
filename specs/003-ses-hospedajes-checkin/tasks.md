# Tasks: Mejora de Recogida de Datos para Check-in SES Hospedajes

**Input**: Design documents from `/specs/003-ses-hospedajes-checkin/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests unitarios incluidos para cada user story (solicitado en spec.md sección "Dentro del alcance")

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Configuración inicial del proyecto para la feature

- [x] T001 Crear directorio `reservas/services/` con `__init__.py` para servicio SES Hospedajes
- [x] T002 [P] Añadir variables de entorno SES en `hotel_project/settings.py` (SES_HOSPEDAJES_ENABLED, ENDPOINT, USER, PASSWORD, TIMEOUT)
- [x] T003 [P] Crear archivo `reservas/services/__init__.py` vacío

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Modelos base que bloquean todas las user stories

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Añadir campo `checkin_online_omitido = BooleanField(default=False)` al modelo `Reserva` en `reservas/models.py`
- [x] T005 Crear modelo `ConsentimientoRGPD` en `reservas/models.py` (reserva FK, cliente FK, fecha_consentimiento, texto_consentimiento, version_politica, ip_address, user_agent, revocado, fecha_revocacion, motivo_revocacion)
- [x] T006 Crear modelo `RegistroAuditoria` en `reservas/models.py` (fecha_accion, usuario FK nullable, tipo_accion choices, entidad_tipo choices, entidad_id, descripcion, datos_anteriores JSONField, datos_nuevos JSONField, ip_address)
- [x] T007 Añadir validación de fecha_nacimiento en `ViajeroCheckin.clean()` (no futura, no > 120 años) en `reservas/models.py`
- [x] T008 Generar migraciones: `python manage.py makemigrations reservas`
- [x] T009 Aplicar migraciones: `python manage.py migrate`
- [x] T010 Registrar modelos `ConsentimientoRGPD` y `RegistroAuditoria` en `reservas/admin.py` con list_display y list_filter

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Check-in Online con Consentimiento RGPD (Priority: P1) MVP

**Goal**: El huésped puede completar el check-in online dando consentimiento explícito RGPD con trazabilidad completa

**Independent Test**: Crear reserva → acceder a check-in online → marcar consentimiento → completar datos viajeros → verificar ConsentimientoRGPD y RegistroAuditoria creados

### Tests for User Story 1

- [x] T011 [P] [US1] Test de modelo ConsentimientoRGPD (validación campos obligatorios, unique_together) en `reservas/tests/test_models_consentimiento.py`
- [x] T012 [P] [US1] Test de validación fecha_nacimiento en ViajeroCheckin (no futura, no > 120 años) en `reservas/tests/test_models_viajero.py`
- [x] T013 [US1] Test de vista checkin_online_reserva con consentimiento (GET muestra formulario, POST crea consentimiento) en `reservas/tests/test_views_checkin.py`

### Implementation for User Story 1

- [x] T014 [US1] Crear `ConsentimientoRGPDForm` en `reservas/forms.py` (campo `acepto_consentimiento` checkbox obligatorio, método `save(reserva, cliente, ip, user_agent)`)
- [x] T015 [US1] Modificar vista `checkin_online_reserva` en `reservas/views.py`: añadir sección de consentimiento RGPD, crear ConsentimientoRGPD y RegistroAuditoria al validar
- [x] T016 [US1] Actualizar template `reservas/templates/reservas/checkin_online.html`: añadir sección de consentimiento con texto legal, checkbox, enlace a Política de Privacidad
- [x] T017 [US1] Añadir textos legales de consentimiento con `gettext` en `reservas/templates/reservas/checkin_online.html` (es/gl/en)

**Checkpoint**: US1 funcional - huésped puede completar check-in online con consentimiento RGPD auditado

---

## Phase 4: User Story 2 - Omitir Check-in Online (Priority: P2)

**Goal**: El huésped puede optar por no hacer check-in online y registrarse presencialmente

**Independent Test**: Crear reserva → hacer clic "Omitir" → verificar `checkin_online_omitido=True` → intentar acceder a check-in online → verificar mensaje de redirección

### Tests for User Story 2

- [x] T018 [P] [US2] Test de vista omitir_checkin_online (POST marca flag, GET no permitido) en `reservas/tests/test_views_omitir.py`

### Implementation for User Story 2

- [x] T019 [US2] Crear vista `omitir_checkin_online` en `reservas/views.py` (POST: marca `checkin_online_omitido=True`, crea RegistroAuditoria, redirige a detalle_reserva)
- [x] T020 [US2] Añadir URL `omitir_checkin_online` en `hotel_project/urls.py` con patrón `reserva/<id>/omitir-checkin/`
- [x] T021 [US2] Añadir `@ratelimit(key='user', rate='5/h', method='POST', block=True)` a vista `omitir_checkin_online`
- [x] T022 [US2] Añadir botón "Omitir check-in online" en `reservas/templates/reservas/detalle_reserva.html` (visible si `checkin_online_omitido=False` y `checkin_online_completado=False`)
- [x] T023 [US2] Modificar vista `checkin_online_reserva` en `reservas/views.py`: redirigir con mensaje si `checkin_online_omitido=True`
- [x] T024 [US2] Modificar vista `crear_reserva` en `reservas/views.py`: después de crear reserva, mostrar opción de omitir en lugar de redirigir automáticamente

**Checkpoint**: US2 funcional - huésped puede omitir check-in online sin penalización

---

## Phase 5: User Story 3 - Check-in Presencial Staff (Priority: P2)

**Goal**: El personal puede introducir datos de viajeros para huéspedes que no hicieron check-in online

**Independent Test**: Staff accede a reserva omitida → completa formulario viajeros → marca consentimiento físico → verifica checkin_online_completado=True

### Tests for User Story 3

- [x] T025 [P] [US3] Test de vista checkin_presencial_staff (GET muestra formulario, POST valida y crea consentimiento) en `reservas/tests/test_views_presencial.py`
- [x] T026 [P] [US3] Test de permisos: solo staff puede acceder a checkin_presencial_staff en `reservas/tests/test_views_presencial.py`

### Implementation for User Story 3

- [x] T027 [US3] Crear `CheckinPresencialForm` en `reservas/forms.py` (mismos campos que CheckinReservaForm + campo hidden `modo_presencial=True`)
- [x] T028 [US3] Crear vista `checkin_presencial_staff` en `reservas/views.py` (GET: muestra formset viajeros + consentimiento, POST: valida, crea ConsentimientoRGPD tipo "presencial", marca checkin_online_completado=True)
- [x] T029 [US3] Añadir `@login_required` + verificación `is_staff` + `@ratelimit(key='user', rate='30/h', method='POST', block=True)` a vista `checkin_presencial_staff`
- [x] T030 [US3] Añadir URL `checkin_presencial_staff` en `hotel_project/urls.py` con patrón `staff/reserva/<id>/checkin-presencial/`
- [x] T031 [US3] Crear template `reservas/templates/reservas/checkin_presencial.html` (datos reserva readonly, formset viajeros, checkbox consentimiento físico, botón completar)
- [x] T032 [US3] Crear vista `detalle_reserva_staff` en `reservas/views.py` (muestra datos completos, estado check-in, botón "Completar check-in presencial")
- [x] T033 [US3] Añadir URL `detalle_reserva_staff` en `hotel_project/urls.py` con patrón `staff/reserva/<id>/`
- [x] T034 [US3] Crear template `reservas/templates/reservas/detalle_reserva_staff.html` (datos reserva, viajeros, estado check-in/consentimiento, botones acción)

**Checkpoint**: US3 funcional - staff puede completar check-in presencial con trazabilidad

---

## Phase 6: User Story 4 - Envío SES Hospedajes (Priority: P3)

**Goal**: El sistema genera y envía partes de viajeros a SES Hospedajes (con modo mock para desarrollo)

**Independent Test**: Completar check-in → desde detalle staff hacer clic "Enviar SES" → verificar modo mock loguea mensaje → verificar ses_hospedajes_enviado flag

### Tests for User Story 4

- [x] T035 [P] [US4] Test de servicio build_payload (extrae datos de reserva y viajeros, valida campos obligatorios) en `reservas/tests/test_services_ses.py`
- [x] T036 [P] [US4] Test de servicio send_payload con mock (SES_HOSPEDAJES_ENABLED=False retorna mock response) en `reservas/tests/test_services_ses.py`
- [x] T037 [US4] Test de servicio registrar_envio (actualiza reserva, crea RegistroAuditoria tipo envio_ses) en `reservas/tests/test_services_ses.py`

### Implementation for User Story 4

- [x] T038 [US4] Crear función `build_payload(reserva)` en `reservas/services/ses_hospedajes.py` (extrae datos Reserva + ViajeroCheckin, mapea a formato SES, valida campos obligatorios)
- [x] T039 [US4] Crear función `send_payload(payload)` en `reservas/services/ses_hospedajes.py` (lee credenciales de settings, hace POST HTTP o mock si SES_HOSPEDAJES_ENABLED=False, retorna dict con exito/referencia/error)
- [x] T040 [US4] Crear función `registrar_envio(reserva, exito, referencia, error)` en `reservas/services/ses_hospedajes.py` (actualiza ses_hospedajes_enviado y ses_hospedajes_referencia, crea RegistroAuditoria tipo envio_ses)
- [x] T041 [US4] Crear función `reintentar_envio(reserva)` en `reservas/services/ses_hospedajes.py` (verifica ses_hospedajes_enviado=False, reconstruye payload, reenvía)
- [x] T042 [US4] Añadir vista `enviar_ses_hospedajes` en `reservas/views.py` (POST: llama build_payload + send_payload + registrar_envio, redirige a detalle_reserva_staff con mensaje)
- [x] T043 [US4] Añadir URL `enviar_ses_hospedajes` en `hotel_project/urls.py` con patrón `staff/reserva/<id>/enviar-ses/`
- [x] T044 [US4] Añadir botón "Enviar a SES Hospedajes" en `reservas/templates/reservas/detalle_reserva_staff.html` (visible si checkin_online_completado=True y ses_hospedajes_enviado=False)
- [x] T045 [US4] Añadir botón "Reintentar envío" en `reservas/templates/reservas/detalle_reserva_staff.html` (visible si ses_hospedajes_enviado=False y hay intento previo)

**Checkpoint**: US4 funcional - sistema puede enviar partes a SES Hospedajes (mock en desarrollo)

---

## Phase 7: User Story 5 - Derechos RGPD (Priority: P3)

**Goal**: El personal puede gestionar solicitudes de derechos ARCO+ (acceso, rectificación, supresión, portabilidad, limitación, oposición)

**Independent Test**: Staff accede a derechos RGPD de cliente → exporta datos CSV → verifica descarga → verifica RegistroAuditoria tipo ejercicio_derechos

### Tests for User Story 5

- [x] T046 [P] [US5] Test de vista derechos_rgpd_cliente (GET muestra datos, POST exporta/anonimiza) en `reservas/tests/test_views_derechos.py`
- [x] T047 [P] [US5] Test de formulario EjercicioDerechosForm (validación tipo_derecho obligatorio, rectificación requiere descripción) en `reservas/tests/test_forms_derechos.py`

### Implementation for User Story 5

- [x] T048 [US5] Crear `EjercicioDerechosForm` en `reservas/forms.py` (tipo_derecho select, descripcion textarea, documentacion_adjunta file)
- [x] T049 [US5] Crear vista `derechos_rgpd_cliente` en `reservas/views.py` (GET: muestra datos cliente + consentimientos, POST: exporta CSV/JSON o anonimiza o rectifica, crea RegistroAuditoria tipo ejercicio_derechos)
- [x] T050 [US5] Añadir `@login_required` + verificación `is_staff` a vista `derechos_rgpd_cliente`
- [x] T051 [US5] Añadir URL `derechos_rgpd_cliente` en `hotel_project/urls.py` con patrón `staff/cliente/<id>/derechos-rgpd/`
- [x] T052 [US5] Implementar lógica de exportación CSV en vista `derechos_rgpd_cliente` en `reservas/views.py` (genera archivo con datos de Cliente + Reserva + ViajeroCheckin + ConsentimientoRGPD)
- [x] T053 [US5] Implementar lógica de anonimización en vista `derechos_rgpd_cliente` en `reservas/views.py` (reemplaza nombre/apellidos/dni/email por "ANONIMIZADO", mantiene datos de reserva para contabilidad)
- [x] T054 [US5] Crear template `reservas/templates/reservas/derechos_rgpd.html` (datos cliente readonly, historial consentimientos, formulario ejercicio derechos, botones Exportar/Anonimizar/Rectificar)

**Checkpoint**: US5 funcional - staff puede ejercer derechos RGPD con trazabilidad

---

## Phase 8: User Story 6 - Historial de Auditoría (Priority: P3)

**Goal**: El personal puede consultar el registro inmutable de todas las acciones relacionadas con datos personales

**Independent Test**: Staff accede a historial auditoría → verifica lista de registros → aplica filtros → verifica paginación

### Tests for User Story 6

- [x] T055 [P] [US6] Test de vista historial_auditoria (GET lista registros con filtros) en `reservas/tests/test_views_auditoria.py`
- [x] T056 [P] [US6] Test de inmutabilidad RegistroAuditoria (no se puede modificar ni eliminar desde aplicación) en `reservas/tests/test_models_auditoria.py`

### Implementation for User Story 6

- [x] T057 [US6] Crear vista `historial_auditoria` en `reservas/views.py` (GET: lista RegistroAuditoria con filtros por fecha, tipo_accion, entidad_tipo, usuario; paginación 50/página)
- [x] T058 [US6] Añadir `@login_required` + verificación `is_staff` + `@ratelimit(key='user', rate='60/h', method='GET', block=True)` a vista `historial_auditoria`
- [x] T059 [US6] Añadir URL `historial_auditoria` en `hotel_project/urls.py` con patrón `staff/auditoria/`
- [x] T060 [US6] Crear template `reservas/templates/reservas/historial_auditoria.html` (filtros fecha/tipo/entidad/usuario, tabla registros, paginación)
- [x] T061 [US6] Implementar función helper `crear_registro_auditoria(usuario, tipo_accion, entidad_tipo, entidad_id, descripcion, datos_anteriores, datos_nuevos, ip)` en `reservas/views.py` o `reservas/utils.py` para reutilización en todas las vistas

**Checkpoint**: US6 funcional - staff puede consultar auditoría inmutable

---

## Phase 9: User Story 7 - Información de Privacidad (Priority: P3)

**Goal**: El sistema proporciona información clara sobre privacidad y protección de datos en los 3 idiomas

**Independent Test**: Acceder a páginas legales → verificar contenido en es/gl/en → verificar enlaces desde todas las páginas

### Tests for User Story 7

- [x] T062 [P] [US7] Test de páginas legales accesibles (politica_privacidad, politica_cookies, terminos_condiciones) en `reservas/tests/test_views_legal.py`

### Implementation for User Story 7

- [x] T063 [US7] Actualizar template `reservas/templates/reservas/politica_privacidad.html` con contenido RGPD completo (responsable tratamiento, finalidad, base legal, destinatarios, plazos conservación, derechos)
- [x] T064 [US7] Añadir traducciones gallegas e inglesas de Política de Privacidad en `reservas/locale/gl/LC_MESSAGES/django.po` y `reservas/locale/en/LC_MESSAGES/django.po`
- [x] T065 [US7] Añadir enlaces a páginas legales en footer de `reservas/templates/reservas/base.html` (Política Privacidad, Cookies, Términos)
- [x] T066 [US7] Compilar mensajes i18n: `python manage.py compilemessages`

**Checkpoint**: US7 funcional - información legal accesible y traducida

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras transversales y validación final

- [x] T067 [P] Ejecutar `python manage.py check` para verificar configuración
- [x] T068 [P] Ejecutar `python manage.py test reservas` para verificar todos los tests (47 existentes + nuevos)
- [x] T069 [P] Ejecutar `pylint $(git ls-files '*.py')` para verificar linting
- [x] T070 Validar quickstart.md escenarios 1-7 manualmente
- [x] T071 [P] Actualizar `GUIA_SES_HOSPEDAJES_CHECKIN.md` con nuevas funcionalidades implementadas
- [x] T072 [P] Revisar que todos los textos visibles usan `gettext`/`_()` para i18n
- [x] T073 Verificar que todos los endpoints POST tienen `@ratelimit` según constitución
- [x] T074 Verificar que todos los inputs usan `strip_tags()` según constitución
- [x] T075 Documentar variables de entorno SES en `AGENTS.md` o `.env.example`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Phase 2 - No dependencies on other stories
  - US2 (P2): Can start after Phase 2 - Independent of US1
  - US3 (P2): Can start after Phase 2 - Independent of US1/US2
  - US4 (P3): Can start after Phase 2 - Requires US1 or US3 completed (check-in completado)
  - US5 (P3): Can start after Phase 2 - Independent
  - US6 (P3): Can start after Phase 2 - Independent
  - US7 (P3): Can start after Phase 2 - Independent
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Foundational → US1 (MVP)
- **US2 (P2)**: Foundational → US2 (independent)
- **US3 (P2)**: Foundational → US3 (independent)
- **US4 (P3)**: Foundational → US1 or US3 → US4 (requires check-in completado)
- **US5 (P3)**: Foundational → US5 (independent)
- **US6 (P3)**: Foundational → US6 (independent)
- **US7 (P3)**: Foundational → US7 (independent)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before forms
- Forms before views
- Views before templates
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003)
- All Foundational tasks marked [P] can run in parallel (none marked, sequential recommended)
- Once Foundational completes, US1/US2/US3/US5/US6/US7 can start in parallel
- US4 requires US1 or US3 to be completed first
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different developers

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: T011 "Test de modelo ConsentimientoRGPD"
Task: T012 "Test de validación fecha_nacimiento"

# After tests fail, implement in order:
Task: T014 "Crear ConsentimientoRGPDForm"
Task: T015 "Modificar vista checkin_online_reserva"
Task: T016 "Actualizar template checkin_online.html"
Task: T017 "Añadir textos legales i18n"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Check-in online con consentimiento)
4. **STOP and VALIDATE**: Test User Story 1 independently (quickstart escenario 1)
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Check-in con consentimiento) → Test independently → Deploy/Demo (MVP!)
3. Add US2 (Omitir check-in) → Test independently → Deploy/Demo
4. Add US3 (Check-in presencial) → Test independently → Deploy/Demo
5. Add US4 (Envío SES) → Test independently → Deploy/Demo
6. Add US5 (Derechos RGPD) → Test independently → Deploy/Demo
7. Add US6 (Auditoría) → Test independently → Deploy/Demo
8. Add US7 (Info privacidad) → Test independently → Deploy/Demo
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Check-in con consentimiento) - MVP
   - Developer B: US2 (Omitir) + US3 (Presencial)
   - Developer C: US5 (Derechos) + US6 (Auditoría) + US7 (Legal)
3. After US1 or US3 complete:
   - Developer A or B: US4 (Envío SES)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All new endpoints POST must have `@ratelimit` per constitution
- All inputs must use `strip_tags()` per constitution
- All user-visible text must use `gettext`/`_()` per constitution
- Messages in commits must be in Spanish per constitution
