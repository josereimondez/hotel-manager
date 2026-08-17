# Implementation Plan: Mejora de Recogida de Datos para Check-in SES Hospedajes

**Branch**: `003-ses-hospedajes-checkin` | **Date**: 2026-08-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-ses-hospedajes-checkin/spec.md`

## Summary

Mejorar el flujo de check-in para cumplir completamente con SES Hospedajes y RGPD. El modelo `ViajeroCheckin` ya tiene todos los campos obligatorios; los gaps principales son: (1) consentimiento RGPD explícito con trazabilidad, (2) opción de omitir check-in online, (3) check-in presencial asistido por staff, (4) registro de auditoría inmutable, y (5) herramientas para ejercicio de derechos RGPD. Se implementan 2 modelos nuevos (`ConsentimientoRGPD`, `RegistroAuditoria`), 1 campo nuevo en `Reserva` (`checkin_online_omitido`), 4 vistas nuevas/modificadas, y 1 servicio de envío SES Hospedajes.

## Technical Context

**Language/Version**: Python 3.11–3.13 (CI), Django 5.2.4

**Primary Dependencies**: Django 5.2.4, python-stdnum (validación DNI/NIE), django-ratelimit, Pillow, python-dotenv, whitenoise, gunicorn

**Storage**: SQLite (desarrollo), PostgreSQL (producción)

**Testing**: `python manage.py test reservas` (47 tests existentes)

**Target Platform**: Linux server (Dokploy VPS), web responsive

**Project Type**: Web application (Django monolith con templates server-side)

**Performance Goals**: Check-in online completado en < 5 min, envío SES Hospedajes en < 20s (timeout)

**Constraints**: Rate limiting en endpoints POST, datos personales cifrados en tránsito (TLS), conservación mínima 3 años

**Scale/Scope**: Hotel pequeño (~20 habitaciones, ~50 huéspedes/semana), 1-2 miembros de personal

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| **I. Seguridad Primero** | PASS | Nuevos endpoints POST tendrán `@ratelimit`. Inputs sanitizados con `strip_tags()`. Credenciales SES por variables de entorno. |
| **II. ORM-First** | PASS | Todos los nuevos modelos usan ORM. Sin SQL crudo. `select_related()` en consultas con FK. |
| **III. Test-Verified** | PASS | Nuevos modelos, vistas y servicios tendrán tests unitarios. Se mantendrán los 47 tests existentes. |
| **IV. Cumplimiento Normativo** | PASS | Este feature es precisamente de cumplimiento normativo. Se revisa `GUIA_SES_HOSPEDAJES_CHECKIN.md`. Validación DNI/NIE con `python-stdnum`. |
| **V. Multiidioma Nativo** | PASS | Todos los textos nuevos (consentimiento, mensajes, templates) usarán `gettext`/`_()`. Traducciones es/gl/en. |

**Resultado**: Todos los gates pasan. No hay violaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/003-ses-hospedajes-checkin/
├── plan.md              # Este archivo
├── spec.md              # Especificación de feature
├── research.md          # Decisiones de diseño
├── data-model.md        # Modelo de datos
├── quickstart.md        # Guía de validación
├── contracts/
│   └── interfaces.md    # Contratos de vistas, formularios, servicio
└── tasks.md             # Generado por /speckit.tasks (siguiente fase)
```

### Source Code (repository root)

```text
hotel_project/
├── settings.py              # Variables SES Hospedajes (variables de entorno)
└── urls.py                  # Nuevas URLs para vistas staff

reservas/
├── models.py                # Nuevos: ConsentimientoRGPD, RegistroAuditoria
│                            # Modificado: Reserva (checkin_online_omitido)
│                            # Modificado: ViajeroCheckin.clean() (validación fecha)
├── views.py                 # Modificado: checkin_online_reserva (consentimiento)
│                            # Nuevo: omitir_checkin_online
│                            # Nuevo: checkin_presencial_staff
│                            # Nuevo: detalle_reserva_staff
│                            # Nuevo: derechos_rgpd_cliente
│                            # Nuevo: historial_auditoria
├── forms.py                 # Nuevo: ConsentimientoRGPDForm
│                            # Nuevo: CheckinPresencialForm
│                            # Nuevo: EjercicioDerechosForm
├── admin.py                 # Registro de nuevos modelos + acciones RGPD
├── services/
│   └── ses_hospedajes.py    # Nuevo: build_payload, send_payload, registrar_envio
├── migrations/
│   ├── 00XX_reserva_checkin_omitido.py
│   ├── 00XX_consentimiento_rgpd.py
│   └── 00XX_registro_auditoria.py
├── templates/reservas/
│   ├── checkin_online.html          # Modificado: consentimiento RGPD + omitir
│   ├── checkin_presencial.html      # Nuevo: formulario staff
│   ├── detalle_reserva_staff.html   # Nuevo: vista staff con acciones
│   ├── derechos_rgpd.html           # Nuevo: ejercicio de derechos
│   └── historial_auditoria.html     # Nuevo: logs de auditoría
├── locale/
│   ├── es/LC_MESSAGES/django.po     # Actualizado: nuevos textos
│   ├── gl/LC_MESSAGES/django.po     # Actualizado: nuevos textos
│   └── en/LC_MESSAGES/django.po     # Actualizado: nuevos textos
└── tests/
    ├── test_models.py               # Tests de nuevos modelos
    ├── test_views.py                # Tests de nuevas vistas
    ├── test_forms.py                # Tests de nuevos formularios
    └── test_services.py             # Tests de servicio SES (mock)
```

**Structure Decision**: Single Django app (`reservas`) con un subdirectorio `services/` para lógica de negocio no trivial (integración SES Hospedajes). Se mantiene la estructura existente del proyecto.

## Implementation Phases

### Fase 1: Modelos y Migraciones

**Archivos**: `reservas/models.py`, `reservas/migrations/`

1. Añadir campo `checkin_online_omitido` a `Reserva`
2. Crear modelo `ConsentimientoRGPD`
3. Crear modelo `RegistroAuditoria`
4. Añadir validación de fecha de nacimiento en `ViajeroCheckin.clean()`
5. Generar y aplicar migraciones
6. Registrar nuevos modelos en `admin.py`

**Tests**: `test_models.py` — tests de validación, relaciones, métodos

### Fase 2: Formularios

**Archivos**: `reservas/forms.py`

1. Crear `ConsentimientoRGPDForm`
2. Crear `CheckinPresencialForm`
3. Crear `EjercicioDerechosForm`
4. Modificar `CheckinReservaForm` para incluir consentimiento

**Tests**: `test_forms.py` — tests de validación de formularios

### Fase 3: Vistas y URLs

**Archivos**: `reservas/views.py`, `hotel_project/urls.py`

1. Modificar `checkin_online_reserva` para incluir consentimiento RGPD
2. Crear vista `omitir_checkin_online`
3. Crear vista `checkin_presencial_staff`
4. Crear vista `detalle_reserva_staff`
5. Crear vista `derechos_rgpd_cliente`
6. Crear vista `historial_auditoria`
7. Añadir nuevas URLs con `@ratelimit` apropiado

**Tests**: `test_views.py` — tests de flujos, permisos, rate limiting

### Fase 4: Servicio SES Hospedajes

**Archivos**: `reservas/services/ses_hospedajes.py`, `hotel_project/settings.py`

1. Añadir variables de entorno SES en `settings.py`
2. Implementar `build_payload(reserva)`
3. Implementar `send_payload(payload)` (mock si `SES_HOSPEDAJES_ENABLED=False`)
4. Implementar `registrar_envio(reserva, exito, referencia, error)`
5. Implementar `reintentar_envio(reserva)`

**Tests**: `test_services.py` — tests con mock de HTTP

### Fase 5: Templates e i18n

**Archivos**: `reservas/templates/`, `reservas/locale/`

1. Modificar `checkin_online.html` con sección de consentimiento
2. Crear `checkin_presencial.html`
3. Crear `detalle_reserva_staff.html`
4. Crear `derechos_rgpd.html`
5. Crear `historial_auditoria.html`
6. Añadir textos legales en es/gl/en
7. Compilar `.mo` con `python manage.py compilemessages`

### Fase 6: Verificación Final

1. `python manage.py check` — sin errores
2. `python manage.py test reservas` — todos los tests pasan
3. `pylint $(git ls-files '*.py')` — sin violaciones
4. Validar quickstart.md (escenarios 1-7)

## Complexity Tracking

No hay violaciones de la constitución que justificar.

## Dependencies

- **Migraciones**: Fase 1 debe completarse antes de Fase 2-5
- **Modelos**: Fase 2 depende de Fase 1 (modelos nuevos)
- **Vistas**: Fase 3 depende de Fase 2 (formularios)
- **Templates**: Fase 5 depende de Fase 3 (vistas)
- **Servicio SES**: Fase 4 es independiente de 2-3-5
- **i18n**: Fase 5.6 depende de tener todos los textos definitivos

## Risk Mitigation

| Riesgo | Mitigación |
|--------|------------|
| Campos SES incompletos | Revisión contra `GUIA_SES_HOSPEDAJES_CHECKIN.md` (research.md I1) |
| Consentimiento insuficiente | Modelo dedicado con timestamp, IP, versión política |
| Datos expuestos en logs | `RegistroAuditoria` usa JSONField sin datos sensibles completos |
| Falta validación fecha nacimiento | Añadir en `ViajeroCheckin.clean()` (research.md I2) |
| SES sin credenciales | Modo mock con `SES_HOSPEDAJES_ENABLED=False` |
| Tests rompen funcionalidad existente | Ejecutar suite completa (47 tests) después de cada fase |
