# Data Model: Mejora de Recogida de Datos para Check-in SES Hospedajes

**Feature**: 003-ses-hospedajes-checkin
**Date**: 2026-08-17

## Entidades Existentes (sin cambios o cambios mínimos)

### Cliente

**Estado**: Sin cambios. Ya tiene los campos necesarios.

| Campo | Tipo | Notas |
|-------|------|-------|
| usuario | OneToOne(User) | Vinculación con auth |
| nombre | CharField(100) | |
| apellidos | CharField(150) | |
| dni_nie | CharField(9) | Validado con `validar_dni_nie` |
| email | EmailField | |
| telefono | CharField(15) | |
| direccion | CharField(200) | |
| ciudad | CharField(100) | |
| codigo_postal | CharField(10) | |
| pais | CharField(50) | Default: España |
| fecha_nacimiento | DateField | |
| fecha_registro | DateTimeField | auto_now_add |

### Reserva

**Estado**: Añadir campo `checkin_online_omitido`.

| Campo | Tipo | Notas |
|-------|------|-------|
| ... (campos existentes) | | |
| checkin_online_completado | BooleanField | Existe, default=False |
| **checkin_online_omitido** | **BooleanField** | **NUEVO, default=False** |
| ses_hospedajes_enviado | BooleanField | Existe, default=False |
| ses_hospedajes_referencia | CharField(120) | Existe |

### ViajeroCheckin

**Estado**: Añadir validación de fecha de nacimiento en `clean()`. No se añaden campos nuevos.

| Campo | Tipo | Notas |
|-------|------|-------|
| reserva | ForeignKey(Reserva) | |
| orden | PositiveSmallIntegerField | |
| nombre | CharField(100) | |
| primer_apellido | CharField(100) | |
| segundo_apellido | CharField(100) | blank=True |
| sexo | CharField(1) | M/F/X |
| tipo_documento | CharField(20) | dni/nie/pasaporte/otro |
| numero_documento | CharField(30) | blank=True |
| numero_soporte | CharField(30) | blank=True |
| nacionalidad | CharField(80) | |
| fecha_nacimiento | DateField | Añadir validación: no futura, no > 120 años |
| direccion_residencia | CharField(200) | |
| ciudad_residencia | CharField(100) | |
| codigo_postal_residencia | CharField(12) | |
| pais_residencia | CharField(80) | Default: España |
| telefono_contacto | CharField(20) | |
| email_contacto | EmailField | |
| relacion_con_titular | CharField(20) | |
| es_menor_sin_documento | BooleanField | default=False |
| parentesco_menor_con_adulto | CharField(120) | blank=True |

## Entidades Nuevas

### ConsentimientoRGPD

**Propósito**: Registro auditado del consentimiento explícito del huésped para el tratamiento de datos personales.

| Campo | Tipo | Null/Blank | Default | Notas |
|-------|------|-----------|---------|-------|
| id | AutoField | PK | auto | Identificador único |
| reserva | ForeignKey(Reserva) | NOT NULL | — | Reserva asociada |
| cliente | ForeignKey(Cliente) | NOT NULL | — | Cliente que da consentimiento |
| fecha_consentimiento | DateTimeField | NOT NULL | auto_now_add | Fecha y hora del consentimiento |
| texto_consentimiento | TextField | NOT NULL | — | Texto exacto aceptado |
| version_politica | CharField(20) | NOT NULL | — | Versión de política de privacidad aceptada |
| ip_address | GenericIPAddressField | NULL | blank=True | IP desde la que se dio el consentimiento |
| user_agent | CharField(500) | blank=True | — | User-Agent del navegador |
| revocado | BooleanField | NOT NULL | False | Indica si el consentimiento fue revocado |
| fecha_revocacion | DateTimeField | NULL | blank=True | Fecha de revocación |
| motivo_revocacion | TextField | blank=True | — | Motivo de la revocación (opcional) |
| creado_en | DateTimeField | NOT NULL | auto_now_add | |
| actualizado_en | DateTimeField | NOT NULL | auto_now | |

**Relaciones**:
- `reserva`: ManyToOne → Reserva (un consentimiento por reserva)
- `cliente`: ManyToOne → Cliente (el titular que acepta)

**Restricciones**:
- `unique_together`: ('reserva', 'cliente') — un consentimiento por cliente por reserva
- Si `revocado=True`, `fecha_revocacion` debe estar definida

**Validaciones**:
- `reserva` debe existir y estar en estado confirmado/en_curso
- `texto_consentimiento` no vacío
- `version_politica` no vacío

### RegistroAuditoria

**Propósito**: Registro inmutable de todas las acciones relacionadas con datos personales.

| Campo | Tipo | Null/Blank | Default | Notas |
|-------|------|-----------|---------|-------|
| id | AutoField | PK | auto | Identificador único |
| fecha_accion | DateTimeField | NOT NULL | auto_now_add | Fecha y hora de la acción |
| usuario | ForeignKey(User) | NULL | blank=True | Usuario que realizó la acción (null si sistema) |
| tipo_accion | CharField(30) | NOT NULL | — | Tipo de acción |
| entidad_tipo | CharField(50) | NOT NULL | — | Tipo de entidad afectada |
| entidad_id | PositiveIntegerField | NOT NULL | — | ID de la entidad afectada |
| descripcion | TextField | NOT NULL | — | Descripción de la acción |
| datos_anteriores | JSONField | NULL | blank=True | Snapshot de datos antes de la modificación |
| datos_nuevos | JSONField | NULL | blank=True | Snapshot de datos después de la modificación |
| ip_address | GenericIPAddressField | NULL | blank=True | IP desde la que se realizó la acción |

**Tipos de acción** (choices):
- `creacion` — Creación de registro
- `modificacion` — Modificación de datos
- `eliminacion` — Eliminación/anonimización
- `acceso` — Acceso a datos
- `envio_ses` — Envío a SES Hospedajes
- `ejercicio_derechos` — Ejercicio de derechos RGPD
- `consentimiento` — Consentimiento dado
- `revocacion` — Consentimiento revocado

**Entidades afectadas** (choices):
- `reserva`
- `viajero_checkin`
- `consentimiento_rgpd`
- `cliente`

**Restricciones**:
- Inmutable: no se permite `update()` ni `delete()` desde la aplicación
- Solo el sistema puede crear registros (no hay vista de edición)

**Índices**:
- `fecha_accion` (para consultas por rango de fechas)
- `entidad_tipo` + `entidad_id` (para buscar acciones sobre una entidad específica)
- `usuario` (para buscar acciones de un usuario)

## Diagrama de Relaciones

```
User (auth)
  │
  ├── 1:1 ── Cliente
  │            │
  │            ├── 1:N ── Reserva
  │            │            │
  │            │            ├── 1:N ── ViajeroCheckin
  │            │            │
  │            │            ├── 1:1 ── ConsentimientoRGPD
  │            │            │
  │            │            └── 1:N ── RegistroAuditoria (entidad_tipo='reserva')
  │            │
  │            └── 1:N ── RegistroAuditoria (entidad_tipo='cliente')
  │
  └── N:1 ── RegistroAuditoria (usuario)
```

## Migraciones

### Migración 1: Añadir `checkin_online_omitido` a Reserva

```python
# Add field to Reserva
migrations.AddField(
    model_name='reserva',
    name='checkin_online_omitido',
    field=models.BooleanField(default=False, help_text='Indica si el huésped omitió el check-in online.'),
),
```

### Migración 2: Crear modelo ConsentimientoRGPD

```python
migrations.CreateModel(
    name='ConsentimientoRGPD',
    fields=[...],
    options={
        'verbose_name': 'Consentimiento RGPD',
        'verbose_name_plural': 'Consentimientos RGPD',
        'ordering': ['-fecha_consentimiento'],
    },
),
```

### Migración 3: Crear modelo RegistroAuditoria

```python
migrations.CreateModel(
    name='RegistroAuditoria',
    fields=[...],
    options={
        'verbose_name': 'Registro de auditoría',
        'verbose_name_plural': 'Registros de auditoría',
        'ordering': ['-fecha_accion'],
    },
),
```

## Transiciones de Estado

### Reserva (check-in)

```
[Reserva creada]
    │
    ├── checkin_online_completado=False, checkin_online_omitido=False → PENDIENTE CHECK-IN
    │       │
    │       ├── Huésped completa check-in online → checkin_online_completado=True
    │       │
    │       └── Huésped omite check-in → checkin_online_omitido=True
    │               │
    │               └── Personal hace check-in presencial → checkin_online_completado=True
    │
    └── (directamente) checkin_online_completado=True → CHECK-IN COMPLETADO
```

### ConsentimientoRGPD

```
[Consentimiento dado]
    │
    ├── revocado=False → VIGENTE
    │
    └── Huésped revoca → revocado=True, fecha_revocacion=<now>
            │
            └── Consecuencia: debe hacer check-in presencial
```

## Reglas de Negocio

1. **Consentimiento requerido**: No se puede completar check-in online sin consentimiento RGPD válido.
2. **Opcionalidad**: El huésped puede omitir el check-in online sin penalización.
3. **Check-in presencial**: Si `checkin_online_omitido=True`, el personal debe introducir los datos de viajeros antes de cambiar estado a `en_curso`.
4. **Inmutabilidad de auditoría**: Los registros de `RegistroAuditoria` no se pueden modificar ni eliminar.
5. **Consentimiento por reserva**: Cada reserva requiere su propio consentimiento; no hay consentimiento global.
6. **Revocación**: Si se revoca el consentimiento, la reserva pasa a estado "pendiente check-in presencial".
7. **Plazo de conservación**: Los datos de viajeros se conservan 3 años desde la fecha de salida. Después se anonimizan.
