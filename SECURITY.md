# Política de Seguridad

## 🔒 Versiones Soportadas

Actualmente damos soporte de seguridad a la siguiente versión:

| Versión | Soporte            |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## 🚨 Reportar una Vulnerabilidad

Si descubres una vulnerabilidad de seguridad, **NO** la publiques en los issues públicos.

### Cómo Reportar

1. **Email**: Envía un correo a `security@hostalrivera.es` (o al email del mantenedor)
2. **Asunto**: "SECURITY: Descripción breve de la vulnerabilidad"
3. **Incluye**:
   - Descripción detallada de la vulnerabilidad
   - Pasos para reproducirla
   - Posible impacto
   - Sugerencias de solución (opcional)

### Qué Esperar

- **Confirmación**: Recibirás una confirmación en 48 horas
- **Evaluación**: Evaluaremos la vulnerabilidad en 7 días
- **Actualización**: Te mantendremos informado del progreso
- **Resolución**: Trabajaremos en un parche lo antes posible
- **Crédito**: Te daremos crédito en el changelog si lo deseas

## 🛡️ Buenas Prácticas de Seguridad

### Para Desarrolladores

1. **Nunca commitees**:
   - Archivos `.env` con datos reales
   - Claves API o tokens
   - Contraseñas
   - Datos de producción

2. **Usa variables de entorno**:
   - `SECRET_KEY` debe ser única y aleatoria (50+ caracteres)
   - Cambia todas las claves por defecto antes de producción

3. **En producción**:
   - `DEBUG = False`
   - `ALLOWED_HOSTS` configurado correctamente
   - HTTPS habilitado
   - Certificado SSL válido

4. **Base de datos**:
   - Usa contraseñas fuertes
   - Nunca uses el usuario root
   - Haz backups regulares
   - Configura firewall para acceso restringido

### Para Usuarios

1. **Instalación**:
   - Copia `.env.example` a `.env`
   - Genera una `SECRET_KEY` única
   - No uses valores por defecto en producción

2. **Actualización**:
   - Mantén Django actualizado
   - Actualiza dependencias regularmente: `pip install --upgrade -r requirements.txt`
   - Revisa el CHANGELOG para cambios de seguridad

3. **Servidor**:
   - Usa firewall (solo puertos 80, 443, 22)
   - Configura fail2ban para prevenir ataques de fuerza bruta
   - Logs de acceso y errores activos
   - Monitoring y alertas configurados

## 🔐 Características de Seguridad Implementadas

- ✅ **Gestión de contraseñas**: Hash seguro con PBKDF2
- ✅ **CSRF Protection**: Token anti-falsificación habilitado
- ✅ **XSS Protection**: Templates auto-escape HTML + strip_tags() en inputs
- ✅ **SQL Injection Protection**: ORM de Django + validación de tipos
- ✅ **Clickjacking Protection**: X-Frame-Options configurado
- ✅ **HTTPS/SSL**: Configuración lista para producción
- ✅ **HSTS**: Strict Transport Security
- ✅ **Secure Cookies**: Session y CSRF cookies seguras
- ✅ **Variables de entorno**: Gestión segura con python-decouple
- ✅ **Input Sanitization**: strip_tags() y validación en todos los inputs
- ✅ **Regex Validation**: Validación de formatos (username, email, teléfono, DNI/NIE)
- ✅ **Length Limits**: Límites en campos de texto (máx 500 chars en observaciones)
- ✅ **Type Validation**: Validación estricta de tipos de datos
- ✅ **DNI/NIE Validation**: Algoritmo oficial español implementado

### 📄 Documentación de Seguridad

Consulta `INPUT_SANITIZATION.md` para detalles completos sobre:
- Sanitización de inputs por formulario
- Validaciones personalizadas
- Protecciones contra vulnerabilidades OWASP Top 10
- Flujo de sanitización end-to-end

## 📋 Checklist de Seguridad Pre-Producción

Antes de desplegar en producción:

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` única y segura (50+ caracteres aleatorios)
- [ ] `ALLOWED_HOSTS` configurado correctamente
- [ ] HTTPS/SSL configurado
- [ ] Certificado SSL válido
- [ ] Base de datos con contraseña fuerte
- [ ] Backups automáticos configurados
- [ ] Firewall activo
- [ ] Logs y monitoring configurados
- [ ] Dependencias actualizadas
- [ ] Tests de seguridad ejecutados: `python manage.py check --deploy`

## 🔍 Auditorías de Seguridad

### Última Auditoría
- **Fecha**: 2026-03-10
- **Herramientas**: Django check --deploy
- **Resultado**: Sin problemas críticos

### Próxima Auditoría Programada
- **Fecha**: 2026-06-10

## 📚 Recursos de Seguridad

- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Releases](https://www.djangoproject.com/weblog/category/security/)
- [Python Security Advisory](https://www.python.org/news/security/)

## 🆘 En Caso de Brecha de Seguridad

Si sospechas que tu instalación ha sido comprometida:

1. **Inmediatamente**:
   - Desconecta el servidor si es posible
   - Cambia todas las contraseñas
   - Genera nuevo `SECRET_KEY`
   - Revisa logs de acceso y errores

2. **Investiga**:
   - Identifica el vector de ataque
   - Determina qué datos fueron comprometidos
   - Documenta todo

3. **Notifica**:
   - Informa a los usuarios afectados
   - Reporta a las autoridades si es necesario (RGPD)
   - Contacta al equipo de desarrollo

4. **Recuperación**:
   - Aplica parches de seguridad
   - Restaura desde backup limpio
   - Refuerza medidas de seguridad
   - Auditoría completa

## 🔗 Contacto

Para reportar vulnerabilidades de seguridad:
- **Email**: security@hostalrivera.es
- **PGP Key**: [Pendiente de configurar]

---

**La seguridad es responsabilidad de todos. Gracias por ayudarnos a mantener el proyecto seguro.**
