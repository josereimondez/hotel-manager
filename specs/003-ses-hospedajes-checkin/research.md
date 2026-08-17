# Research: Mejora de Recogida de Datos para Check-in SES Hospedajes

**Feature**: 003-ses-hospedajes-checkin
**Date**: 2026-08-17

## Decisiones de Diseño

### D1: Consentimiento RGPD — Modelo dedicado vs campo en Reserva

**Decision**: Modelo dedicado `ConsentimientoRGPD` separado de `Reserva`.

**Rationale**:
- El consentimiento tiene ciclo de vida propio (puede revocarse independientemente de la reserva)
- Permite auditoría granular: quién, cuándo, qué versión de política aceptó
- Facilita el ejercicio de derechos RGPD (acceso, portabilidad)
- Un campo booleano en `Reserva` no captura la trazabilidad necesaria

**Alternatives considered**:
- Campo `consentimiento_dado` en `Reserva`: insuficiente, no permite revocación ni auditoría
- Tabla genérica de auditoría: demasiado genérica, el consentimiento merece entidad propia

### D2: Check-in online opcional — Flag en Reserva vs estado

**Decision**: Añadir campo `checkin_online_omitido` (boolean) al modelo `Reserva` junto al existente `checkin_online_completado`.

**Rationale**:
- Permite distinguir tres estados: pendiente, completado, omitido
- El personal ve claramente qué huéspedes deben registrarse presencialmente
- No requiere cambiar el sistema de estados existente (pendiente/confirmada/en_curso/finalizada/cancelada)
- Simple y compatible con el código existente

**Alternatives considered**:
- Nuevo estado `checkin_pendiente_presencial` en `ESTADO_CHOICES`: rompe la semántica de estado de la reserva (el estado refleja el ciclo de vida de la reserva, no el check-in)
- Campo `checkin_estado` con choices: más complejo de lo necesario para un flag binario

### D3: Registro de auditoría — Modelo propio vs signals

**Decision**: Modelo `RegistroAuditoria` con escritura explícita desde las vistas/servicios, no signals de Django.

**Rationale**:
- Los signals son implícitos y difíciles de depurar
- La escritura explícita permite capturar el contexto completo (usuario, IP, acción, datos anteriores/nuevos)
- Facilita el cumplimiento RGPD (derecho de acceso a logs)
- Más fácil de testear y mantener

**Alternatives considered**:
- Django signals (`post_save`, `pre_delete`): implícitos, no capturan contexto de negocio
- Paquete `django-auditlog`: dependencia externa, puede no cubrir casos específicos de SES Hospedajes
- Middleware de auditoría: demasiado genérico, no captura acciones de negocio

### D4: Campos SES Hospedajes — Ampliar ViajeroCheckin vs nuevo modelo

**Decision**: El modelo `ViajeroCheckin` existente ya tiene todos los campos obligatorios de SES Hospedajes. No se necesitan nuevos campos.

**Rationale**:
- Revisión de `GUIA_SES_HOSPEDAJES_CHECKIN.md` sección 5.1 confirma que los 15 campos obligatorios ya están en `ViajeroCheckin`
- Los campos existentes cubren: nombre, apellidos, sexo, tipo documento, número documento, número soporte, nacionalidad, fecha nacimiento, dirección, ciudad, CP, país, teléfono, email
- El campo `es_menor_sin_documento` + `parentesco_menor_con_adulto` cubren el caso de menores (sección 5.2)
- No es necesario modificar el modelo, solo asegurar que las validaciones y el flujo de consentimiento sean correctos

**Alternatives considered**:
- Añadir campos de "tipo documento" más granulares: innecesario, el campo `tipo_documento` con choices es suficiente

### D5: Check-in presencial asistido — Vista admin vs vista pública

**Decision**: Vista restringida a staff (`@login_required` + `is_staff`) para el check-in presencial, reutilizando el formulario `ViajeroCheckinForm`.

**Rationale**:
- El personal necesita introducir datos de viajeros que no hicieron check-in online
- Reutilizar el mismo formset garantiza las mismas validaciones
- Restricción a staff asegura que solo personal autorizado accede a datos sensibles
- Puede implementarse como una variante de la vista existente `checkin_online_reserva`

**Alternatives considered**:
- Vista en admin de Django: menos control sobre UX, no permite imprimir documento de firma
- Vista pública con token: inseguro para datos sensibles

### D6: Envío SES Hospedajes — Servicio síncrono vs background

**Decision**: Servicio síncrono con reintentos manuales desde el panel de staff. Background queue (Celery) fuera del alcance de este feature.

**Rationale**:
- El proyecto no usa Celery actualmente; añadirlo es una dependencia significativa
- El envío síncrono con timeout es aceptable para el volumen de un hotel pequeño
- Los reintentos manuales dan control al personal sobre cuándo reenviar
- Se puede evolucionar a background en un futuro sin cambiar la interfaz

**Alternatives considered**:
- Celery/RQ: infraestructura adicional (Redis/Broker) no justificada para el volumen actual
- Cron job de reenvío: menos control, más complejo de monitorizar

### D7: Derechos RGPD — Panel admin vs comandos de gestión

**Decision**: Acciones en el admin de Django para ejercicio de derechos (exportar datos, anonimizar) + vista pública de solicitud de derechos.

**Rationale**:
- El admin de Django ya está configurado y restringido a staff
- Las acciones de admin permiten exportar CSV/JSON y anonimizar registros
- Una vista pública permite al huésped iniciar una solicitud de derechos
- No requiere nueva infraestructura

**Alternatives considered**:
- Comandos `manage.py`: no accesibles para personal no técnico
- API REST: sobreingeniería para el volumen de solicitudes esperado

### D8: Formato del parte SES Hospedajes

**Decision**: El formato exacto del payload XML/JSON se determinará cuando se implemente el servicio de envío, basándose en la documentación oficial de SES Hospedajes y las credenciales de integración.

**Rationale**:
- La guía `GUIA_SES_HOSPEDAJES_CHECKIN.md` indica que el formato debe validarse con la documentación vigente del Ministerio
- Las credenciales y endpoints se configuran por variables de entorno
- El servicio `reservas/services/ses_hospedajes.py` se creará en la fase de implementación

**Alternatives considered**:
- Implementar formato ahora sin credenciales reales: imposible validar sin entorno de pruebas

## Investigación Técnica

### I1: Campos obligatorios SES Hospedajes

**Hallazgo**: Los 15 campos obligatorios para viajeros >= 14 años ya están en `ViajeroCheckin`:

| Campo SES | Campo modelo | Estado |
|-----------|-------------|--------|
| Nombre | `nombre` | OK |
| Primer apellido | `primer_apellido` | OK |
| Segundo apellido | `segundo_apellido` | OK |
| Sexo | `sexo` | OK |
| Tipo documento | `tipo_documento` | OK |
| Número documento | `numero_documento` | OK |
| Número soporte | `numero_soporte` | OK |
| Nacionalidad | `nacionalidad` | OK |
| Fecha nacimiento | `fecha_nacimiento` | OK |
| Dirección | `direccion_residencia` | OK |
| Ciudad | `ciudad_residencia` | OK |
| Código postal | `codigo_postal_residencia` | OK |
| País | `pais_residencia` | OK |
| Teléfono | `telefono_contacto` | OK |
| Email | `email_contacto` | OK |

Para menores sin documento: `es_menor_sin_documento` + `parentesco_menor_con_adulto` cubren el requisito.

### I2: Validaciones existentes

**Hallazgo**: El modelo `ViajeroCheckin.clean()` ya valida:
- DNI/NIE con algoritmo oficial (`validar_dni_nie`)
- Teléfono mínimo 9 dígitos
- Documento obligatorio si no es menor
- Número de soporte obligatorio si no es menor
- Parentesco obligatorio para menores

**Gap identificado**: Falta validación de fecha de nacimiento (no futura, no > 120 años).

### I3: Flujo de consentimiento actual

**Hallazgo**: El formulario `CheckinReservaForm` tiene `contrato_aceptado` pero:
- No registra fecha/hora del consentimiento
- No tiene versión de política
- No permite revocación
- No hay modelo separado para auditoría de consentimiento

**Gap identificado**: Necesario crear modelo `ConsentimientoRGPD` con trazabilidad completa.

### I4: Opción de omitir check-in online

**Hallazgo**: Actualmente la vista `crear_reserva` redirige automáticamente a `checkin_online_reserva` después de crear la reserva. No hay opción de omitir.

**Gap identificado**: Necesario añadir botón "Omitir check-in online" en la plantilla de la reserva y en la redirección tras crear reserva.

### I5: Check-in presencial

**Hallazgo**: No existe vista para que el personal introduzca datos de viajeros. El check-in online solo es accesible por el titular de la reserva (`cliente__usuario=request.user`).

**Gap identificado**: Necesaria vista staff-only para check-in presencial con el mismo formset de viajeros.

## Resumen de Gaps a Implementar

| Gap | Prioridad | Complejidad |
|-----|-----------|-------------|
| Modelo `ConsentimientoRGPD` | Alta | Media |
| Campo `checkin_online_omitido` en `Reserva` | Alta | Baja |
| Modelo `RegistroAuditoria` | Alta | Media |
| Validación fecha nacimiento en `ViajeroCheckin` | Alta | Baja |
| Vista de opción "omitir check-in" | Alta | Baja |
| Vista staff de check-in presencial | Alta | Media |
| Servicio SES Hospedajes (`ses_hospedajes.py`) | Media | Alta |
| Acciones admin para derechos RGPD | Media | Media |
| Actualización de plantillas con consentimiento explícito | Alta | Media |
| Traducciones i18n de nuevos textos | Alta | Baja |
