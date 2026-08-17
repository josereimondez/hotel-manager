# Contratos de Interfaz: Check-in SES Hospedajes

**Feature**: 003-ses-hospedajes-checkin
**Date**: 2026-08-17

## Vistas (URLs)

### 1. Check-in Online (existente, modificada)

**URL**: `/reserva/<id>/checkin/`
**Nombre**: `checkin_online_reserva`
**Método**: GET, POST
**Autenticación**: `@login_required`
**Acceso**: Solo titular de la reserva (`cliente__usuario=request.user`)

**GET**:
- Muestra formulario de datos de viajeros + consentimiento RGPD
- Si `checkin_online_completado=True`: muestra resumen y opción de ver/editar
- Si `checkin_online_omitido=True`: redirige a mensaje "ya omitiste el check-in, contacta recepción"

**POST**:
- Valida consentimiento RGPD (checkbox obligatorio)
- Valida datos de viajeros (formset `ViajeroCheckinForm`)
- Crea `ConsentimientoRGPD` con timestamp, IP, versión política
- Crea `RegistroAuditoria` (tipo=`consentimiento`)
- Marca `checkin_online_completado=True`
- Crea `RegistroAuditoria` (tipo=`creacion`, entidad=`reserva`)
- Redirige a `detalle_reserva`

**Template**: `reservas/checkin_online.html`

### 2. Omitir Check-in Online (nueva)

**URL**: `/reserva/<id>/omitir-checkin/`
**Nombre**: `omitir_checkin_online`
**Método**: POST
**Autenticación**: `@login_required`
**Rate limit**: `@ratelimit(key='user', rate='5/h', method='POST', block=True)`
**Acceso**: Solo titular de la reserva

**POST**:
- Marca `checkin_online_omitido=True`
- Crea `RegistroAuditoria` (tipo=`modificacion`, descripción="Check-in online omitido")
- Redirige a `detalle_reserva` con mensaje informativo

**Template**: No tiene (redirección directa)

### 3. Check-in Presencial Staff (nueva)

**URL**: `/staff/reserva/<id>/checkin-presencial/`
**Nombre**: `checkin_presencial_staff`
**Método**: GET, POST
**Autenticación**: `@login_required` + `is_staff`
**Rate limit**: `@ratelimit(key='user', rate='30/h', method='POST', block=True)`

**GET**:
- Muestra datos de la reserva
- Muestra formset de viajeros (vacío o con datos existentes)
- Muestra checkbox de consentimiento (para firma física)

**POST**:
- Valida datos de viajeros
- Marca `checkin_online_completado=True`
- Crea `ConsentimientoRGPD` (tipo="presencial", texto="Consentimiento físico firmado")
- Crea `RegistroAuditoria` (tipo=`consentimiento`, usuario=staff)
- Redirige a `detalle_reserva_staff`

**Template**: `reservas/checkin_presencial.html`

### 4. Detalle Reserva Staff (existente, extendida)

**URL**: `/staff/reserva/<id>/`
**Nombre**: `detalle_reserva_staff`
**Método**: GET
**Autenticación**: `@login_required` + `is_staff`

**GET**:
- Muestra datos completos de la reserva
- Muestra datos de viajeros
- Muestra estado de check-in (online/presencial/pendiente)
- Muestra estado de consentimiento RGPD
- Botón "Enviar a SES Hospedajes" (si check-in completado)
- Botón "Imprimir documento de registro"

**Template**: `reservas/detalle_reserva_staff.html`

### 5. Ejercicio de Derechos RGPD (nueva)

**URL**: `/staff/cliente/<id>/derechos-rgpd/`
**Nombre**: `derechos_rgpd_cliente`
**Método**: GET, POST
**Autenticación**: `@login_required` + `is_staff`

**GET**:
- Muestra datos del cliente
- Muestra historial de consentimientos
- Muestra formulario de ejercicio de derechos

**POST** (acciones):
- `exportar_datos`: Genera CSV/JSON con todos los datos del cliente
- `anonimizar`: Anonimiza datos personales (mantiene datos de reserva para contabilidad)
- `rectificar`: Permite corregir datos específicos
- Crea `RegistroAuditoria` (tipo=`ejercicio_derechos`)

**Template**: `reservas/derechos_rgpd.html`

### 6. Historial de Auditoría (nueva)

**URL**: `/staff/auditoria/`
**Nombre**: `historial_auditoria`
**Método**: GET
**Autenticación**: `@login_required` + `is_staff`
**Rate limit**: `@ratelimit(key='user', rate='60/h', method='GET', block=True)`

**GET**:
- Lista de `RegistroAuditoria` con filtros:
  - Por fecha (rango)
  - Por tipo de acción
  - Por entidad
  - Por usuario
- Paginación (50 registros por página)

**Template**: `reservas/historial_auditoria.html`

## Formularios

### ConsentimientoRGPDForm (nuevo)

**Campos**:
- `texto_consentimiento` (readonly, pre-rellenado con texto legal)
- `version_politica` (hidden, valor fijo: "1.0")
- `acepto_consentimiento` (checkbox obligatorio, no es campo del modelo)

**Validaciones**:
- `acepto_consentimiento` debe ser True

**Métodos**:
- `save(reserva, cliente, ip, user_agent)`: Crea instancia de `ConsentimientoRGPD`

### CheckinPresencialForm (nuevo)

**Campos**:
- Mismos campos que `CheckinReservaForm` (relaciones_parentesco_adultos, contrato_aceptado)
- `modo_presencial` (hidden, valor=True)

**Validaciones**:
- `contrato_aceptado` debe ser True

### EjercicioDerechosForm (nuevo)

**Campos**:
- `tipo_derecho` (select: acceso, rectificación, supresión, limitación, portabilidad, oposición)
- `descripcion` (textarea, opcional)
- `documentacion_adjunta` (file, opcional)

**Validaciones**:
- `tipo_derecho` obligatorio
- Si tipo es `rectificación`, `descripcion` obligatorio

## Servicio SES Hospedajes

### `reservas/services/ses_hospedajes.py`

**Funciones**:

#### `build_payload(reserva: Reserva) -> dict`

**Entrada**: Reserva con viajeros y consentimiento
**Salida**: Diccionario con estructura de payload para SES Hospedajes

**Lógica**:
1. Extrae datos de `Reserva` (fechas, medio pago, IBAN)
2. Extrae datos de `ViajeroCheckin` para cada viajero
3. Mapea campos al formato SES Hospedajes
4. Valida que todos los campos obligatorios están presentes
5. Retorna payload o lanza `ValidationError`

**Excepciones**:
- `ValidationError` si faltan campos obligatorios
- `ValueError` si la reserva no tiene check-in completado

#### `send_payload(payload: dict) -> dict`

**Entrada**: Payload generado por `build_payload`
**Salida**: Diccionario con `{'exito': bool, 'referencia': str|None, 'error': str|None}`

**Lógica**:
1. Lee credenciales de `settings` (variables de entorno)
2. Hace petición HTTP POST al endpoint de SES Hospedajes
3. Parsea respuesta
4. Retorna resultado

**Configuración** (variables de entorno):
- `SES_HOSPEDAJES_ENABLED`: bool (default: False)
- `SES_HOSPEDAJES_ENDPOINT`: str (URL del WS)
- `SES_HOSPEDAJES_USER`: str
- `SES_HOSPEDAJES_PASSWORD`: str
- `SES_HOSPEDAJES_TIMEOUT`: int (default: 20)

**Excepciones**:
- `ConnectionError` si no hay conectividad
- `Timeout` si excede timeout
- `HTTPError` si respuesta no es 2xx

#### `registrar_envio(reserva: Reserva, exito: bool, referencia: str|None, error: str|None)`

**Entrada**: Resultado del envío
**Salida**: None (efecto secundario: actualiza reserva y crea auditoría)

**Lógica**:
1. Actualiza `Reserva.ses_hospedajes_enviado` y `Reserva.ses_hospedajes_referencia`
2. Crea `RegistroAuditoria` (tipo=`envio_ses`, datos_nuevos={exito, referencia, error})

#### `reintentar_envio(reserva: Reserva) -> dict`

**Entrada**: Reserva con envío fallido
**Salida**: Resultado del reintento (mismo formato que `send_payload`)

**Lógica**:
1. Verifica que `ses_hospedajes_enviado=False`
2. Reconstruye payload
3. Reenvía
4. Registra resultado

## Templates

### `checkin_online.html` (modificado)

**Cambios**:
- Añadir sección de consentimiento RGPD antes del formulario de viajeros
- Checkbox "Acepto el tratamiento de mis datos personales..."
- Enlace a Política de Privacidad
- Texto explicativo: "Sus datos serán utilizados para..."
- Botón "Omitir check-in online" (visible si `checkin_online_omitido=False`)

### `checkin_presencial.html` (nuevo)

**Estructura**:
- Datos de la reserva (solo lectura)
- Formset de viajeros (mismo que check-in online)
- Checkbox de consentimiento (texto: "El huésped ha firmado físicamente...")
- Botón "Completar check-in presencial"

### `derechos_rgpd.html` (nuevo)

**Estructura**:
- Datos del cliente (solo lectura)
- Historial de consentimientos
- Formulario de ejercicio de derechos
- Botones de acción: Exportar, Anonimizar, Rectificar

### `historial_auditoria.html` (nuevo)

**Estructura**:
- Filtros (fecha, tipo acción, entidad, usuario)
- Tabla de registros de auditoría
- Paginación

### `detalle_reserva_staff.html` (nuevo)

**Estructura**:
- Datos de la reserva
- Datos de viajeros
- Estado de check-in y consentimiento
- Botones de acción: Enviar SES, Imprimir documento

## Textos Legales (i18n)

### Texto de Consentimiento RGPD (español)

```
Acepto el tratamiento de mis datos personales por Hostal Rivera con las siguientes finalidades:
- Gestión de la reserva y prestación del servicio de hospedaje
- Cumplimiento de la obligación legal de registro y comunicación a SES Hospedajes (Policía Nacional)
- Conservación de los datos durante el plazo legal de 3 años

Puedo ejercer mis derechos de acceso, rectificación, supresión, limitación, portabilidad y oposición contactando con el hotel.

Más información en la Política de Privacidad.
```

### Texto de Consentimiento (gallego)

```
Acepto o tratamento dos meus datos persoais por Hostal Rivera coas seguintes finalidades:
- Xestión da reserva e prestación do servizo de hospedaxe
- Cumprimento da obriga legal de rexistro e comunicación a SES Hospedajes (Policía Nacional)
- Conservación dos datos durante o prazo legal de 3 anos

Podo exercer os meus dereitos de acceso, rectificación, supresión, limitación, portabilidade e oposición contactando co hotel.

Máis información na Política de Privacidade.
```

### Texto de Consentimiento (inglés)

```
I accept the processing of my personal data by Hostal Rivera for the following purposes:
- Management of the reservation and provision of the accommodation service
- Compliance with the legal obligation of registration and communication to SES Hospedajes (National Police)
- Retention of data for the legal period of 3 years

I can exercise my rights of access, rectification, erasure, restriction, data portability and objection by contacting the hotel.

More information in the Privacy Policy.
```
