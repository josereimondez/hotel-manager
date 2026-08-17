# Quickstart: Validación de Check-in SES Hospedajes

**Feature**: 003-ses-hospedajes-checkin
**Date**: 2026-08-17

## Prerrequisitos

1. Entorno de desarrollo configurado (ver `AGENTS.md`)
2. Base de datos con datos de prueba (habitaciones, clientes, reservas)
3. Usuario staff creado para probar check-in presencial
4. Variables de entorno configuradas (`DEBUG=True`, `SECRET_KEY`, etc.)

## Escenario 1: Check-in Online Completo con Consentimiento

**Objetivo**: Verificar que un huésped puede completar el check-in online dando consentimiento explícito.

### Pasos

1. **Crear reserva de prueba**:
   ```bash
   python manage.py shell
   ```
   ```python
   from reservas.models import Habitacion, Cliente, Reserva
   from datetime import date, timedelta

   habitacion = Habitacion.objects.first()
   cliente = Cliente.objects.first()
   reserva = Reserva.objects.create(
       habitacion=habitacion,
       cliente=cliente,
       fecha_entrada=date.today() + timedelta(days=1),
       fecha_salida=date.today() + timedelta(days=4),
       numero_adultos=2,
       numero_ninos=0,
       precio_por_noche=habitacion.precio_base,
       estado='confirmada'
   )
   print(f"Reserva creada: {reserva.codigo_reserva}")
   ```

2. **Iniciar sesión como cliente** en el navegador

3. **Acceder a la reserva** desde "Mis reservas"

4. **Verificar que se muestran**:
   - Botón "Completar check-in online"
   - Botón "Omitir check-in online"

5. **Hacer clic en "Completar check-in online"**

6. **Verificar que aparece**:
   - Sección de consentimiento RGPD con texto legal completo
   - Checkbox "Acepto el tratamiento de mis datos personales..."
   - Formulario de datos de viajeros (2 viajeros para 2 adultos)

7. **Intentar enviar SIN marcar consentimiento**:
   - **Resultado esperado**: Error "Debes aceptar el tratamiento de datos"

8. **Marcar consentimiento y completar datos de viajeros**:
   - Viajero 1: Nombre, apellidos, DNI, sexo, fecha nacimiento, dirección, etc.
   - Viajero 2: Mismos datos

9. **Enviar formulario**:
   - **Resultado esperado**: Redirección a detalle de reserva con mensaje "Check-in completado"

10. **Verificar en base de datos**:
    ```python
    from reservas.models import Reserva, ConsentimientoRGPD, RegistroAuditoria

    reserva = Reserva.objects.get(id=reserva_id)
    print(f"Check-in completado: {reserva.checkin_online_completado}")  # True
    print(f"Omitido: {reserva.checkin_online_omitido}")  # False

    consentimiento = ConsentimientoRGPD.objects.get(reserva=reserva)
    print(f"Consentimiento dado: {consentimiento.fecha_consentimiento}")
    print(f"Versión política: {consentimiento.version_politica}")

    auditoria = RegistroAuditoria.objects.filter(entidad_tipo='reserva', entidad_id=reserva.id)
    print(f"Registros auditoría: {auditoria.count()}")  # Al menos 2 (consentimiento + check-in)
    ```

## Escenario 2: Omitir Check-in Online

**Objetivo**: Verificar que un huésped puede omitir el check-in online.

### Pasos

1. **Crear otra reserva de prueba** (similar al escenario 1)

2. **Acceder a la reserva** desde "Mis reservas"

3. **Hacer clic en "Omitir check-in online"**

4. **Verificar que aparece**:
   - Mensaje: "Has omitido el check-in online. Deberás registrarte presencialmente en recepción con tu documentación."

5. **Verificar en base de datos**:
    ```python
    print(f"Check-in completado: {reserva.checkin_online_completado}")  # False
    print(f"Omitido: {reserva.checkin_online_omitido}")  # True
    ```

6. **Intentar acceder de nuevo a check-in online**:
   - **Resultado esperado**: Mensaje "Ya omitiste el check-in online. Contacta con recepción."

## Escenario 3: Check-in Presencial Staff

**Objetivo**: Verificar que el personal puede introducir datos de viajeros para check-in presencial.

### Pasos

1. **Iniciar sesión como staff** en el navegador

2. **Acceder a la reserva omitida** desde `/staff/reserva/<id>/`

3. **Verificar que se muestra**:
   - Estado: "Check-in pendiente (presencial)"
   - Botón "Completar check-in presencial"

4. **Hacer clic en "Completar check-in presencial"**

5. **Verificar que aparece**:
   - Formulario de datos de viajeros
   - Checkbox de consentimiento con texto: "El huésped ha firmado físicamente el consentimiento"

6. **Completar datos de viajeros** y marcar consentimiento

7. **Enviar formulario**:
   - **Resultado esperado**: Redirección a detalle con mensaje "Check-in presencial completado"

8. **Verificar en base de datos**:
    ```python
    print(f"Check-in completado: {reserva.checkin_online_completado}")  # True
    consentimiento = ConsentimientoRGPD.objects.get(reserva=reserva)
    print(f"Tipo consentimiento: {consentimiento.texto_consentimiento}")  # "Consentimiento físico firmado"
    ```

## Escenario 4: Validación de Datos de Viajeros

**Objetivo**: Verificar que las validaciones funcionan correctamente.

### Pasos

1. **Acceder a check-in online** de una reserva

2. **Probar validaciones**:

   **DNI inválido**:
   - Introducir DNI "12345678A" (letra incorrecta)
   - **Resultado esperado**: Error "La letra del DNI/NIE no es correcta"

   **Fecha de nacimiento futura**:
   - Introducir fecha futura
   - **Resultado esperado**: Error "La fecha de nacimiento no puede ser futura"

   **Fecha de nacimiento > 120 años**:
   - Introducir fecha de hace 130 años
   - **Resultado esperado**: Error "Fecha de nacimiento no válida"

   **Teléfono inválido**:
   - Introducir "123" (menos de 9 dígitos)
   - **Resultado esperado**: Error "El teléfono debe tener al menos 9 dígitos"

   **Campo obligatorio vacío**:
   - Dejar "nombre" vacío
   - **Resultado esperado**: Error "Este campo es obligatorio"

3. **Corregir todos los errores y enviar**:
   - **Resultado esperado**: Check-in completado

## Escenario 5: Ejercicio de Derechos RGPD

**Objetivo**: Verificar que el personal puede gestionar solicitudes de derechos RGPD.

### Pasos

1. **Iniciar sesión como staff**

2. **Acceder a `/staff/cliente/<id>/derechos-rgpd/`**

3. **Verificar que se muestra**:
   - Datos del cliente
   - Historial de consentimientos
   - Formulario de ejercicio de derechos

4. **Probar exportación de datos**:
   - Seleccionar tipo "Acceso"
   - Hacer clic en "Exportar datos"
   - **Resultado esperado**: Descarga de archivo CSV/JSON con todos los datos del cliente

5. **Probar rectificación**:
   - Seleccionar tipo "Rectificación"
   - Describir: "Corregir dirección"
   - **Resultado esperado**: Formulario para corregir datos

6. **Verificar en auditoría**:
   ```python
   auditoria = RegistroAuditoria.objects.filter(tipo_accion='ejercicio_derechos')
   print(f"Solicitudes registradas: {auditoria.count()}")
   ```

## Escenario 6: Historial de Auditoría

**Objetivo**: Verificar que todas las acciones quedan registradas.

### Pasos

1. **Iniciar sesión como staff**

2. **Acceder a `/staff/auditoria/`**

3. **Verificar que se muestran**:
   - Lista de registros de auditoría
   - Filtros por fecha, tipo, entidad, usuario
   - Paginación

4. **Aplicar filtros**:
   - Filtrar por tipo "consentimiento"
   - **Resultado esperado**: Solo registros de consentimiento

5. **Verificar inmutabilidad**:
   - Intentar modificar un registro desde shell
   - **Resultado esperado**: Error o advertencia (no hay vista de edición)

## Escenario 7: Envío a SES Hospedajes (mock)

**Objetivo**: Verificar que el servicio de envío funciona (sin credenciales reales).

### Pasos

1. **Configurar variable de entorno**:
   ```bash
   export SES_HOSPEDAJES_ENABLED=False  # Modo mock
   ```

2. **Completar check-in** de una reserva (escenarios 1 o 3)

3. **Desde detalle staff**, hacer clic en "Enviar a SES Hospedajes"

4. **Verificar en logs**:
   - Mensaje: "SES Hospedajes deshabilitado. Envío simulado."

5. **Verificar en base de datos**:
   ```python
   print(f"SES enviado: {reserva.ses_hospedajes_enviado}")  # False (mock)
   print(f"Referencia: {reserva.ses_hospedajes_referencia}")  # Vacío (mock)
   ```

## Criterios de Aceptación

- [ ] Todos los escenarios pasan sin errores
- [ ] Las validaciones de datos funcionan correctamente
- [ ] Los consentimientos se registran con timestamp y versión
- [ ] Los registros de auditoría son inmutables
- [ ] El check-in online es opcional (se puede omitir)
- [ ] El check-in presencial funciona para staff
- [ ] Los derechos RGPD se pueden ejercer desde el panel staff
- [ ] Los textos legales están en los 3 idiomas (es, gl, en)

## Comandos de Verificación

```bash
# Verificar que no hay errores de configuración
python manage.py check

# Ejecutar tests
python manage.py test reservas

# Ver migraciones pendientes
python manage.py showmigrations reservas

# Aplicar migraciones
python manage.py migrate
```

## Notas

- Este quickstart asume que las migraciones se han creado y aplicado
- Los datos de prueba pueden crearse con fixtures o scripts
- El escenario 7 es un mock; el envío real requiere credenciales de SES Hospedajes
- Las traducciones i18n deben compilarse con `python manage.py compilemessages`
