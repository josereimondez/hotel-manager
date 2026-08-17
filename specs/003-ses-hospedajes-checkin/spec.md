# Mejora de Recogida de Datos para Check-in SES Hospedajes

## Resumen

Mejorar el proceso de registro y check-in de huéspedes para cumplir completamente con los requisitos obligatorios de SES Hospedajes (Sistema Electrónico de Hospedajes de la Policía Nacional española), garantizando el cumplimiento del RGPD (Reglamento General de Protección de Datos) y la LOPDGDD (Ley Orgánica de Protección de Datos y Garantía de Derechos Digitales). El check-in online será opcional, permitiendo a los huéspedes que no deseen proporcionar sus datos personales realizar el registro presencial en el establecimiento.

## Problema que Resuelve

Actualmente el sistema tiene un modelo `ViajeroCheckin` con campos para SES Hospedajes y una vista de check-in online, pero:

1. No está claro si todos los campos obligatorios de SES Hospedajes están siendo recogidos correctamente
2. No existe una opción clara para que los huéspedes opten por no hacer check-in online
3. No se ha documentado explícitamente el cumplimiento RGPD en el flujo de recogida de datos
4. No hay un proceso alternativo para huéspedes que prefieren no dar sus datos online

## Objetivos

- **O1**: Garantizar que todos los campos obligatorios de SES Hospedajes se recogen durante el check-in
- **O2**: Implementar un flujo de check-in online opcional con consentimiento explícito
- **O3**: Cumplir con RGPD y LOPDGDD en la recogida, almacenamiento y tratamiento de datos personales
- **O4**: Proporcionar un proceso alternativo para check-in presencial
- **O5**: Mantener la trazabilidad y auditabilidad del cumplimiento normativo

## Actores

- **Huésped/Titular de reserva**: Persona que realiza la reserva y/o se registra en el sistema
- **Viajeros acompañantes**: Personas adicionales que se alojan en la misma habitación
- **Personal del hotel**: Staff que gestiona el check-in presencial y el envío de partes a SES Hospedajes
- **Sistema**: Aplicación web que gestiona reservas, check-in y comunicación con SES Hospedajes

## Escenarios de Usuario

### Escenario 1: Huésped realiza check-in online completo

**Actor**: Huésped/Titular de reserva
**Precondición**: Huésped tiene una reserva confirmada y ha iniciado sesión

**Flujo**:
1. Huésped accede a su reserva desde "Mis reservas"
2. Sistema muestra opción de "Completar check-in online"
3. Huésped acepta los términos y condiciones de tratamiento de datos (consentimiento explícito RGPD)
4. Huésped introduce sus datos personales completos (todos los campos obligatorios de SES Hospedajes)
5. Huésped introduce datos de viajeros acompañantes (si aplica)
6. Sistema valida que todos los campos obligatorios están completos
7. Sistema marca la reserva como "check-in online completado"
8. Sistema muestra confirmación al huésped
9. Personal del hotel puede consultar los datos y enviar el parte a SES Hospedajes

**Postcondición**: Reserva tiene check-in online completado, datos de viajeros almacenados, listos para envío a SES Hospedajes

**Excepciones**:
- Si faltan campos obligatorios: sistema muestra errores específicos y no permite continuar
- Si el huésped revoca el consentimiento: sistema permite cancelar el check-in online

### Escenario 2: Huésped opta por no hacer check-in online

**Actor**: Huésped/Titular de reserva
**Precondición**: Huésped tiene una reserva confirmada

**Flujo**:
1. Huésped accede a su reserva
2. Sistema muestra opción de "Completar check-in online" y opción de "Omitir check-in online"
3. Huésped selecciona "Omitir check-in online"
4. Sistema muestra mensaje explicando que deberá completar el registro presencial en el hotel
5. Sistema informa que necesitará presentar documentación física (DNI/pasaporte)
6. Reserva permanece en estado "confirmada" sin check-in online
7. Al llegar al hotel, huésped completa el registro presencial con el personal

**Postcondición**: Reserva sin check-in online, huésped informado de que debe registrarse presencialmente

**Excepciones**:
- Si el huésped cambia de opinión: puede volver a la web y completar el check-in online antes de llegar

### Escenario 3: Personal del hotel gestiona check-in presencial

**Actor**: Personal del hotel
**Precondición**: Huésped llega al hotel sin haber completado check-in online

**Flujo**:
1. Huésped se presenta en recepción
2. Personal identifica la reserva por nombre o código
3. Personal solicita documentación física (DNI/pasaporte) de todos los viajeros
4. Personal introduce manualmente los datos obligatorios de SES Hospedajes en el sistema
5. Sistema valida que todos los campos están completos
6. Personal marca el check-in como completado
7. Personal imprime documento de registro para firma del huésped (consentimiento físico)
8. Sistema actualiza el estado de la reserva a "en curso"

**Postcondición**: Datos de viajeros introducidos manualmente, check-in completado, documento firmado archivado

### Escenario 4: Envío de parte a SES Hospedajes

**Actor**: Personal del hotel / Sistema automático
**Precondición**: Reserva tiene check-in completado (online o presencial) con todos los datos de viajeros

**Flujo**:
1. Sistema verifica que todos los datos obligatorios están completos
2. Sistema genera el archivo/parte en el formato requerido por SES Hospedajes
3. Sistema envía el parte a SES Hospedajes (manual o automáticamente)
4. Sistema recibe confirmación de SES Hospedajes con número de referencia
5. Sistema almacena la referencia y marca el parte como enviado
6. Personal puede consultar el estado del envío

**Postcondición**: Parte enviado a SES Hospedajes, referencia almacenada, cumplimiento registrado

**Excepciones**:
- Si SES Hospedajes rechaza el parte: sistema muestra errores, personal corrige y reenvía
- Si hay error de conexión: sistema reintenta automáticamente o notifica al personal

### Escenario 5: Huésped ejerce derechos RGPD

**Actor**: Huésped
**Precondición**: Huésped ha proporcionado datos personales al sistema

**Flujo**:
1. Huésped contacta con el hotel para ejercer derechos de acceso, rectificación, supresión, limitación, portabilidad u oposición
2. Personal verifica la identidad del huésped
3. Personal accede a los datos del huésped en el sistema
4. Según el derecho ejercido:
   - **Acceso**: proporciona copia de todos sus datos
   - **Rectificación**: corrige datos incorrectos
   - **Supresión**: elimina datos (excepto los obligatorios por ley que se conservan según plazos legales)
   - **Limitación**: restringe el tratamiento de ciertos datos
   - **Portabilidad**: proporciona datos en formato estructurado
   - **Oposición**: deja de tratar los datos para fines específicos
5. Personal documenta la solicitud y la respuesta
6. Sistema registra la acción en log de auditoría

**Postcondición**: Derecho RGPD ejercido, datos actualizados/eliminados según corresponda, solicitud documentada

**Excepciones**:
- Si la solicitud es manifiestamente infundada: personal puede rechazarla con justificación
- Si hay obligación legal de conservar datos: informa al huésped del plazo de conservación

## Requisitos Funcionales

### RF1: Campos obligatorios de SES Hospedajes

**Descripción**: El sistema debe recoger todos los datos obligatorios exigidos por SES Hospedajes para cada viajero.

**Criterios de aceptación**:
- Para cada viajero mayor de edad se recogen: nombre, primer apellido, segundo apellido, sexo, tipo de documento (DNI/NIE/pasaporte), número de documento, número de soporte (si aplica), nacionalidad, fecha de nacimiento, dirección completa de residencia, ciudad, código postal, país de residencia, teléfono de contacto, email de contacto
- Para menores sin documento: nombre, apellidos, fecha de nacimiento, relación con adulto responsable
- El sistema valida que todos los campos obligatorios están completos antes de permitir el check-in
- El sistema valida el formato de DNI/NIE según algoritmo oficial español
- El sistema valida el formato de pasaporte y otros documentos según estándares internacionales

### RF2: Check-in online opcional

**Descripción**: El sistema debe permitir a los huéspedes elegir entre check-in online o presencial.

**Criterios de aceptación**:
- Después de crear una reserva, el sistema muestra claramente las dos opciones: "Completar check-in online" y "Omitir check-in online"
- Si el huésped elige "Omitir", el sistema muestra un mensaje explicando el proceso presencial
- El huésped puede cambiar de opinión y completar el check-in online en cualquier momento antes de la fecha de entrada
- El sistema no obliga al huésped a completar el check-in online para confirmar la reserva
- El personal del hotel puede ver el estado del check-in (online completado, pendiente presencial)

### RF3: Consentimiento explícito RGPD

**Descripción**: El sistema debe obtener consentimiento explícito del huésped para el tratamiento de sus datos personales.

**Criterios de aceptación**:
- Antes de recoger datos, el sistema muestra un texto claro explicando: qué datos se recogen, para qué se usan (SES Hospedajes, gestión de reserva), quién es el responsable del tratamiento, plazos de conservación, derechos del interesado
- El huésped debe marcar una casilla de verificación explícita ("Acepto el tratamiento de mis datos personales para...")
- El sistema registra la fecha y hora del consentimiento
- El consentimiento es específico para cada reserva (no es un consentimiento global)
- El huésped puede revocar el consentimiento en cualquier momento (con consecuencias: deberá hacer check-in presencial)
- El sistema mantiene un registro auditado de los consentimientos

### RF4: Validación de datos

**Descripción**: El sistema debe validar que todos los datos recogidos son correctos y completos.

**Criterios de aceptación**:
- Validación de formato de DNI/NIE (algoritmo oficial español con letra de control)
- Validación de formato de pasaporte (según país de emisión)
- Validación de formato de email
- Validación de formato de teléfono (mínimo 9 dígitos)
- Validación de fecha de nacimiento (no futura, no mayor de 120 años)
- Validación de código postal (formato según país)
- Validación de campos obligatorios (no vacíos)
- El sistema muestra mensajes de error claros y específicos para cada validación fallida
- El sistema no permite continuar si hay errores de validación

### RF5: Almacenamiento seguro de datos

**Descripción**: El sistema debe almacenar los datos personales de forma segura y conforme a RGPD.

**Criterios de aceptación**:
- Los datos se almacenan en base de datos con medidas de seguridad apropiadas
- Acceso a datos restringido por roles (solo personal autorizado puede ver datos de viajeros)
- Los datos sensibles (DNI/NIE, direcciones) no se muestran en logs o mensajes de error
- El sistema implementa medidas técnicas contra acceso no autorizado, pérdida o alteración
- Los datos se conservan durante el plazo legal obligatorio (mínimo 3 años según legislación de hospedajes)
- Después del plazo legal, los datos se eliminan o anonimizan

### RF6: Derechos RGPD

**Descripción**: El sistema debe facilitar el ejercicio de los derechos ARCO+ (Acceso, Rectificación, Cancelación, Oposición, Portabilidad, Limitación).

**Criterios de aceptación**:
- El sistema permite al personal buscar y acceder a los datos de un huésped específico
- El sistema permite corregir datos incorrectos
- El sistema permite eliminar datos (con registro de auditoría)
- El sistema permite exportar datos en formato estructurado (CSV, JSON)
- El sistema registra todas las acciones de ejercicio de derechos (fecha, tipo de derecho, acción realizada)
- El sistema permite limitar el tratamiento de ciertos datos

### RF7: Envío a SES Hospedajes

**Descripción**: El sistema debe generar y enviar los partes de viajeros a SES Hospedajes en el formato requerido.

**Criterios de aceptación**:
- El sistema genera el archivo/parte en el formato XML/JSON requerido por SES Hospedajes
- El sistema incluye todos los datos obligatorios de cada viajero
- El sistema envía el parte a SES Hospedajes (vía API web service)
- El sistema recibe y almacena la referencia de SES Hospedajes
- El sistema marca la reserva como "parte enviado"
- El sistema permite reenviar el parte si hubo error
- El sistema mantiene un historial de envíos a SES Hospedajes

### RF8: Check-in presencial asistido

**Descripción**: El sistema debe permitir al personal introducir manualmente los datos de viajeros para check-in presencial.

**Criterios de aceptación**:
- El personal puede acceder a la reserva y seleccionar "Completar check-in presencial"
- El sistema muestra formularios para introducir datos de cada viajero
- El sistema valida los datos introducidos (mismas validaciones que check-in online)
- El personal puede imprimir un documento de registro para firma del huésped
- El sistema marca el check-in como completado
- El sistema permite al personal corregir datos si hay errores

### RF9: Información de privacidad

**Descripción**: El sistema debe proporcionar información clara sobre privacidad y protección de datos.

**Criterios de aceptación**:
- El sistema tiene una página de Política de Privacidad accesible desde todas las páginas
- La política explica: responsable del tratamiento, finalidad, base legal, destinatarios, plazos de conservación, derechos
- El sistema tiene una página de Política de Cookies
- El sistema tiene una página de Términos y Condiciones
- Todas las páginas legales están disponibles en los 3 idiomas (español, gallego, inglés)
- Las páginas legales cumplen con LSSI-CE y RGPD

### RF10: Registro de auditoría

**Descripción**: El sistema debe mantener un registro de todas las acciones relacionadas con datos personales.

**Criterios de aceptación**:
- El sistema registra: creación de reserva, check-in online, check-in presencial, envío a SES Hospedajes, ejercicio de derechos RGPD
- Cada registro incluye: fecha/hora, usuario que realizó la acción, tipo de acción, datos afectados
- Los registros de auditoría son inmutables (no se pueden modificar ni eliminar)
- El personal autorizado puede consultar los registros de auditoría
- Los registros se conservan durante el plazo legal

## Criterios de Éxito

### CE1: Cumplimiento normativo

- 100% de los check-in (online y presencial) recogen todos los campos obligatorios de SES Hospedajes
- 100% de los huéspedes dan consentimiento explícito antes de proporcionar datos
- 0 sanciones por incumplimiento de RGPD o SES Hospedajes
- 100% de las solicitudes de derechos RGPD se resuelven en menos de 30 días

### CE2: Experiencia de usuario

- El 80% de los huéspedes completan el check-in online en menos de 5 minutos
- El 90% de los huéspedes entiende el proceso de check-in (medido mediante feedback)
- Menos del 5% de los huéspedes necesitan ayuda del personal para completar el check-in online
- El 100% de los huéspedes sabe que el check-in online es opcional

### CE3: Eficiencia operativa

- El personal del hotel puede completar un check-in presencial en menos de 3 minutos
- El 95% de los partes a SES Hospedajes se envían sin errores
- El tiempo medio de respuesta a solicitudes RGPD es inferior a 7 días
- El sistema está disponible el 99.5% del tiempo

### CE4: Seguridad y privacidad

- 0 brechas de seguridad que comprometan datos personales
- 100% de los accesos a datos personales están registrados en auditoría
- Los datos se eliminan automáticamente después del plazo legal de conservación
- Todas las comunicaciones con SES Hospedajes usan cifrado TLS

## Entidades Clave

### Huésped/Cliente

**Descripción**: Persona que realiza una reserva en el hotel

**Atributos**:
- Identificador único
- Nombre completo
- DNI/NIE
- Email
- Teléfono
- Dirección completa
- Fecha de nacimiento
- Fecha de registro
- Consentimientos dados

**Relaciones**:
- Puede tener múltiples reservas
- Cada reserva tiene uno o más viajeros

### Viajero

**Descripción**: Persona que se aloja en el hotel (puede ser el titular de la reserva o un acompañante)

**Atributos**:
- Identificador único
- Reserva asociada
- Nombre completo
- Sexo
- Tipo de documento (DNI/NIE/pasaporte/otro)
- Número de documento
- Número de soporte (si aplica)
- Nacionalidad
- Fecha de nacimiento
- Dirección completa de residencia
- Teléfono de contacto
- Email de contacto
- Relación con el titular de la reserva
- Es menor sin documento (booleano)
- Parentesco con adulto (si es menor)

**Relaciones**:
- Pertenece a una reserva
- Puede ser el titular o un acompañante

### Reserva

**Descripción**: Reserva de habitación realizada por un huésped

**Atributos**:
- Identificador único
- Huésped titular
- Habitación
- Fechas de entrada y salida
- Número de adultos y niños
- Estado (pendiente, confirmada, en curso, finalizada, cancelada)
- Check-in online completado (booleano)
- Parte SES Hospedajes enviado (booleano)
- Referencia SES Hospedajes
- Medio de pago
- Precio total

**Relaciones**:
- Pertenece a un huésped
- Tiene uno o más viajeros
- Asociada a una habitación

### Consentimiento RGPD

**Descripción**: Registro del consentimiento dado por el huésped para el tratamiento de sus datos

**Atributos**:
- Identificador único
- Huésped
- Reserva
- Fecha y hora del consentimiento
- Texto del consentimiento aceptado
- Versión de la política de privacidad aceptada
- Revocado (booleano)
- Fecha de revocación (si aplica)

**Relaciones**:
- Pertenece a un huésped
- Asociado a una reserva

### Registro de Auditoría

**Descripción**: Registro inmutable de acciones relacionadas con datos personales

**Atributos**:
- Identificador único
- Fecha y hora
- Usuario que realizó la acción
- Tipo de acción (creación, modificación, eliminación, acceso, envío SES, ejercicio derechos)
- Entidad afectada (reserva, viajero, consentimiento)
- Identificador de la entidad
- Descripción de la acción
- Datos anteriores (si es modificación)
- Datos nuevos (si es modificación)

**Relaciones**:
- Asociado a un usuario (si es personal del hotel)
- Asociado a una entidad (reserva, viajero, etc.)

## Suposiciones

1. **Conocimiento técnico del personal**: El personal del hotel tiene conocimientos básicos de informática y puede usar el sistema sin formación extensiva.

2. **Conectividad**: El hotel dispone de conexión a internet estable para comunicarse con SES Hospedajes.

3. **Documentación física**: Los huéspedes que optan por check-in presencial llevan su documentación física (DNI/pasaporte).

4. **Plazos legales**: Los datos se conservan durante el plazo mínimo legal de 3 años según la legislación española de hospedajes.

5. **Formato SES Hospedajes**: El formato requerido por SES Hospedajes es XML o JSON (se confirmará con la documentación oficial).

6. **Idiomas**: Los huéspedes hablan al menos uno de los idiomas soportados (español, gallego, inglés) o viajan con alguien que traduce.

7. **Voluntariedad del check-in online**: Los huéspedes entienden que el check-in online es opcional y no afecta a su reserva.

8. **Responsable del tratamiento**: El hotel es el responsable del tratamiento de los datos personales recogidos.

9. **Base legal**: La base legal para el tratamiento es el cumplimiento de una obligación legal (SES Hospedajes) y el consentimiento del interesado.

10. **Transferencias internacionales**: No hay transferencias internacionales de datos fuera de la UE/EEE.

## Dependencias

1. **SES Hospedajes API**: El sistema depende de la disponibilidad y estabilidad del servicio web de SES Hospedajes para enviar los partes de viajeros.

2. **Base de datos**: El sistema depende de la base de datos (SQLite en desarrollo, PostgreSQL en producción) para almacenar datos de forma segura y consistente.

3. **Servidor web**: El sistema depende del servidor web (Gunicorn + WhiteNoise) para servir la aplicación de forma eficiente.

4. **Certificado SSL/TLS**: El sistema depende de un certificado SSL/TLS válido para cifrar las comunicaciones y cumplir con RGPD.

5. **Copias de seguridad**: El sistema depende de copias de seguridad regulares para proteger los datos contra pérdida.

6. **Actualizaciones legales**: El sistema debe actualizarse si cambian los requisitos de SES Hospedajes o la legislación de protección de datos.

## Restricciones

1. **RGPD**: Todo el tratamiento de datos debe cumplir con el Reglamento General de Protección de Datos (UE) 2016/679.

2. **LOPDGDD**: El sistema debe cumplir con la Ley Orgánica 3/2018 de Protección de Datos y Garantía de Derechos Digitales.

3. **LSSI-CE**: El sistema debe cumplir con la Ley 34/2002 de Servicios de la Sociedad de la Información y Comercio Electrónico.

4. **SES Hospedajes**: El sistema debe cumplir con los requisitos técnicos y formativos de SES Hospedajes (Real Decreto 933/2021).

5. **Plazos de conservación**: Los datos deben conservarse durante el plazo mínimo legal de 3 años.

6. **Derechos ARCO+**: El sistema debe facilitar el ejercicio de los derechos de Acceso, Rectificación, Cancelación, Oposición, Portabilidad y Limitación.

7. **Seguridad**: El sistema debe implementar medidas técnicas y organizativas apropiadas para proteger los datos personales.

8. **Notificación de brechas**: El sistema debe permitir notificar brechas de seguridad a la AEPD en menos de 72 horas.

9. **Idiomas**: El sistema debe estar disponible en español, gallego e inglés.

10. **Accesibilidad**: El sistema debe cumplir con las pautas de accesibilidad web WCAG 2.1 nivel AA.

## Alcance

### Dentro del alcance

- Mejora del modelo `ViajeroCheckin` para incluir todos los campos obligatorios de SES Hospedajes
- Implementación de flujo de check-in online opcional con consentimiento explícito RGPD
- Implementación de flujo de check-in presencial asistido por personal
- Validación completa de datos (DNI/NIE, pasaporte, email, teléfono, etc.)
- Implementación de derechos RGPD (acceso, rectificación, supresión, portabilidad, limitación, oposición)
- Implementación de registro de auditoría para todas las acciones relacionadas con datos personales
- Implementación de envío de partes a SES Hospedajes
- Actualización de políticas de privacidad, cookies y términos y condiciones
- Implementación de página de información RGPD clara y accesible
- Tests unitarios para todas las nuevas funcionalidades
- Documentación del flujo de cumplimiento normativo

### Fuera del alcance

- Integración con sistemas de pago externos (no es parte de este feature)
- Aplicación móvil nativa (el sistema es web responsive)
- Integración con otros sistemas de policía (solo SES Hospedajes)
- Gestión de grupos grandes (más de 10 viajeros en una reserva)
- Check-in automático sin intervención del huésped (siempre requiere acción del huésped o personal)
- Traducción automática de documentos (los documentos deben estar en un idioma soportado)
- Reconocimiento automático de documentos (OCR) para check-in presencial

## Riesgos

### Riesgo 1: Cambios en requisitos de SES Hospedajes

**Probabilidad**: Media
**Impacto**: Alto
**Mitigación**: Mantener el código modular y fácil de actualizar. Documentar claramente los campos obligatorios. Suscribirse a actualizaciones de SES Hospedajes.

### Riesgo 2: Brecha de seguridad

**Probabilidad**: Baja
**Impacto**: Muy alto
**Mitigación**: Implementar medidas de seguridad robustas (cifrado, rate limiting, validación de inputs). Realizar auditorías de seguridad periódicas. Tener plan de respuesta a incidentes.

### Riesgo 3: Sanción por incumplimiento RGPD

**Probabilidad**: Baja
**Impacto**: Muy alto
**Mitigación**: Cumplir estrictamente con RGPD. Documentar todos los tratamientos. Formar al personal. Tener delegado de protección de datos (DPO) si es necesario.

### Riesgo 4: Baja adopción del check-in online

**Probabilidad**: Media
**Impacto**: Medio
**Mitigación**: Hacer el proceso lo más sencillo posible. Explicar claramente los beneficios (ahorro de tiempo en recepción). Mantener la opción presencial como alternativa válida.

### Riesgo 5: Errores en validación de documentos

**Probabilidad**: Media
**Impacto**: Medio
**Mitigación**: Usar librerías validadas (python-stdnum para DNI/NIE). Implementar validaciones exhaustivas. Permitir corrección manual por personal autorizado.

### Riesgo 6: Problemas de disponibilidad del sistema

**Probabilidad**: Baja
**Impacto**: Alto
**Mitigación**: Usar infraestructura fiable. Implementar copias de seguridad. Tener plan de contingencia para check-in manual en papel si el sistema no está disponible.

## Notas

- El sistema actual ya tiene un modelo `ViajeroCheckin` con la mayoría de los campos necesarios. Se debe revisar y completar con los campos faltantes.
- La vista `checkin_online_reserva` ya existe pero debe mejorarse para hacer el consentimiento explícito y la opción de omitir.
- El modelo `Cliente` tiene campos básicos pero no todos los necesarios para SES Hospedajes. Los datos de viajeros se almacenan en `ViajeroCheckin`.
- La constitución del proyecto establece que el cumplimiento normativo es prioritario y no negociable.
- Los mensajes del sistema deben estar en los 3 idiomas soportados (español, gallego, inglés).
- El código debe seguir las convenciones del proyecto (ORM-first, validación de inputs, rate limiting, tests).
