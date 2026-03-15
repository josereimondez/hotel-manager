# Guia paso a paso: Check-in online y envio automatico a SES Hospedajes

## 1. Objetivo
Esta guia explica como dejar operativo el flujo completo:

1. El cliente hace la reserva.
2. Completa el check-in online con datos legales de viajeros.
3. El sistema prepara y envia automaticamente la comunicacion a SES Hospedajes.
4. Se guarda trazabilidad del envio (estado, referencia, errores y reintentos).

---

## 2. Requisitos previos
Antes de programar el envio automatico, necesitas:

1. Certificado digital valido de la empresa o representante.
2. Agencia y alojamiento dados de alta en SES Hospedajes.
3. En SES Hospedajes, marcar la opcion de envio por servicio web.
4. Credenciales de integracion (usuario, password y, si aplica, endpoint/entorno).
5. Politica de privacidad y base legal para tratamiento de datos personales.

Nota: valida siempre los datos tecnicos oficiales (endpoint, formato, seguridad, version de schema) en la documentacion vigente del Ministerio.

---

## 3. Estado actual del proyecto
En este proyecto ya tienes la base de datos y pantallas de check-in online:

1. Campos legales en Reserva:
   - medio de pago
   - iban
   - relaciones_parentesco_adultos
   - contrato_aceptado
   - checkin_online_completado
   - ses_hospedajes_enviado
   - ses_hospedajes_referencia

2. Modelo ViajeroCheckin con datos de identificacion, residencia, contacto y parentesco.

3. Flujo funcional:
   - Al crear reserva, se redirige a check-in online.
   - Se exige minimo de viajeros segun adultos de la reserva.

---

## 4. Paso a paso funcional (operativa diaria)

### Paso 1. El cliente crea la reserva
1. El cliente selecciona fechas y ocupacion.
2. Informa medio de pago (e IBAN si aplica).
3. Se crea la reserva en estado normal del sistema.

### Paso 2. El cliente completa check-in online
1. Accede a check-in online de su reserva.
2. Introduce datos de todos los viajeros requeridos.
3. Si hay menores sin documento, informa parentesco con adulto responsable.
4. Acepta contrato de hospedaje.
5. El sistema marca checkin_online_completado = True.

### Paso 3. El sistema prepara el payload SES
1. Toma datos de Reserva + ViajeroCheckin.
2. Mapea campos al formato exigido por SES Hospedajes.
3. Valida obligatoriedad de campos antes de enviar.

### Paso 4. Envio automatico
1. Se llama al WS de SES Hospedajes.
2. Si OK:
   - ses_hospedajes_enviado = True
   - ses_hospedajes_referencia = referencia devuelta
3. Si error:
   - ses_hospedajes_enviado = False
   - guardar error tecnico para reintento

### Paso 5. Reintentos y control
1. Reintento automatico con backoff (ejemplo: 5m, 30m, 2h).
2. Limitar numero de reintentos.
3. Avisar a staff si no se logra enviar.

---

## 5. Mapeo de datos recomendado

## 5.1 Datos del viajero (>=14 anos)
1. Nombre
2. Primer apellido
3. Segundo apellido (si consta)
4. Sexo
5. Tipo de documento
6. Numero de documento
7. Numero de soporte
8. Nacionalidad
9. Fecha de nacimiento
10. Direccion de residencia habitual
11. Ciudad
12. Codigo postal
13. Pais
14. Telefono
15. Email

## 5.2 Menores sin documento
1. Marcar menor sin documento.
2. Incluir parentesco con adulto responsable.

## 5.3 Datos de reserva/contrato
1. Fecha entrada
2. Fecha salida
3. Relacion de parentesco entre adultos
4. Medio de pago
5. IBAN (si aplica)
6. Aceptacion de contrato

---

## 6. Implementacion tecnica recomendada en Django

### Paso 1. Crear servicio de integracion
Crear archivo nuevo, por ejemplo:
- reservas/services/ses_hospedajes.py

Responsabilidades:
1. build_payload(reserva)
2. send_payload(payload)
3. parse_response(response)

### Paso 2. Guardar configuracion en variables de entorno
Anadir en .env (ejemplo):

- SES_HOSPEDAJES_ENABLED=True
- SES_HOSPEDAJES_ENV=produccion
- SES_HOSPEDAJES_ENDPOINT=<SET_IN_SERVER_ENV_ONLY>
- SES_HOSPEDAJES_USER=<SET_IN_SERVER_ENV_ONLY>
- SES_HOSPEDAJES_PASSWORD=<SET_IN_SERVER_ENV_ONLY>
- SES_HOSPEDAJES_TIMEOUT=20

Recomendacion:
- Nunca guardar credenciales reales en repositorio.

### Paso 3. Trigger de envio
Opciones seguras:
1. Enviar justo al completar check-in online.
2. Encolar y enviar por tarea en background (recomendado en produccion).

Recomendado:
- usar cola (Celery/RQ) para evitar que el usuario espere.

### Paso 4. Registro de auditoria
Guardar por cada intento:
1. fecha intento
2. payload resumido (sin datos sensibles completos)
3. respuesta SES
4. codigo/estado
5. error tecnico

---

## 7. Validaciones minimas antes de enviar
No enviar si falta alguno de estos requisitos:

1. checkin_online_completado == True
2. contrato_aceptado == True
3. Numero minimo de viajeros adultos informado
4. Campos documentales obligatorios completos
5. Fechas de reserva validas

Si falla validacion:
1. bloquear envio
2. mostrar mensaje claro al staff
3. dejar la reserva en pendiente de envio

---

## 8. Pruebas recomendadas

### 8.1 Caso 1: 1 adulto
1. Reserva con 1 adulto.
2. Debe exigir 1 viajero.
3. Envio exitoso y referencia guardada.

### 8.2 Caso 2: 2 adultos
1. Reserva con 2 adultos.
2. Debe exigir 2 viajeros.
3. Envio exitoso y referencia guardada.

### 8.3 Caso 3: menor sin documento
1. Marcar menor sin documento.
2. Debe obligar parentesco con adulto.

### 8.4 Caso 4: error temporal WS
1. Simular timeout.
2. Debe quedar pendiente y reintentarse.

---

## 9. Operativa en produccion

### Checklist de salida
1. Alta en SES Hospedajes completada.
2. WS habilitado y credenciales confirmadas.
3. Variables de entorno cargadas en servidor.
4. Pruebas de extremo a extremo validadas.
5. Alertas de fallo de envio activas.
6. Personal de recepcion formado en revisiones manuales.

### Monitorizacion diaria
1. Reservas con check-in completado pero no enviadas.
2. Numero de errores por dia.
3. Tiempo medio hasta envio exitoso.

---

## 10. Seguridad y cumplimiento
1. Minimizar datos en logs (evitar documento completo en texto plano).
2. Encriptar backups y limitar acceso por roles.
3. Mantener politica de retencion y borrado conforme a normativa.
4. Revisar periodicamente cambios normativos y de schema del WS.

---

## 11. Siguiente paso en este proyecto
Para cerrar la automatizacion al 100% aqui, implementa ahora:

1. Servicio reservas/services/ses_hospedajes.py
2. Trigger tras check-in completado
3. Reintentos en background
4. Pantalla admin de errores de envio

Con eso quedara completo: reserva -> check-in online -> envio automatico a SES Hospedajes.
