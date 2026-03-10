# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - 2026-03-10

### Añadido
- Sistema completo de gestión hotelera
- Modelos: Cliente, Habitación, Reserva
- Sistema de autenticación y registro de usuarios
- Perfil de usuario editable
- Sistema de reservas con validación de fechas
- Prevención de doble reserva (backend + frontend)
- Calendario interactivo con Flatpickr
- API JSON para fechas ocupadas
- Panel de administración Django personalizado
- Internacionalización (i18n): Español, Gallego, Inglés
- Diseño responsive con Bootstrap 5
- Integración de imágenes estáticas (logo, backgrounds, galería)
- Esquema de colores basado en el logo corporativo
- Botón de llamada directa con teléfono del hotel
- Información de contacto en footer
- Páginas informativas: Vía Künig, Política de Privacidad, Cookies, Términos
- Gestión segura de variables de entorno con python-decouple
- Configuración de seguridad para producción
- Documentación completa de instalación y despliegue
- **INPUT_SANITIZATION.md**: Documentación completa de sanitización de inputs

### Características de Seguridad
- SECRET_KEY gestionada por variables de entorno
- DEBUG configurable por entorno
- ALLOWED_HOSTS configurable
- Configuración HTTPS/SSL para producción
- HSTS (HTTP Strict Transport Security)
- Cookies seguras en producción
- Protección XSS y CSRF
- Validaciones robustas en formularios
- **strip_tags() en todos los inputs de usuario**
- **Validación regex en username, email, teléfono, nombre, apellidos**
- **Límites de longitud en campos de texto**
- **Validación de DNI/NIE con algoritmo oficial español**
- **Sanitización en modelos (Model.clean())**
- **Validación de tipos en todos los campos numéricos**
- **Protección contra SQL Injection (ORM Django)**
- **Auto-escape en templates**
- **Validación de rangos en fechas y números**
- **Rate Limiting implementado con django-ratelimit 4.1.0**
  - Login: 5 intentos/minuto (previene brute force)
  - Registro: 3 registros/hora (previene spam)
  - API fechas: 60 requests/minuto (previene scraping)
  - Reservas: 10 reservas/hora (previene abuso)
  - Middleware personalizado con páginas de error elegantes
  - Protección contra DoS/DDoS básica

### Estructura del Proyecto
- Arquitectura Django MVT (Model-View-Template)
- Separación de archivos estáticos y media
- Sistema de traducciones con gettext
- Migraciones de base de datos versionadas
- Scripts de utilidad (compile_mo.py)

### Documentación
- README.md completo con guía de instalación
- DEPLOYMENT.md con guías de despliegue para múltiples plataformas
- .env.example con plantilla de configuración
- SEO_STRATEGY.md con estrategia de posicionamiento
- APRENDIZAJE_PYTHON.md con recursos de aprendizaje
- LICENSE (MIT)
- .gitignore configurado para proteger archivos sensibles

## [Unreleased]

### Planeado
- Sistema de pagos online (Stripe/PayPal)
- Envío de emails de confirmación
- Dashboard con métricas y estadísticas
- Generación de facturas PDF
- Export de reservas a Excel
- API REST para integración con terceros
- Sistema de notificaciones push
- Integración con redes sociales
- App móvil (React Native)
- Sistema de valoraciones y reseñas
- Galería de imágenes mejorada
- Blog/Noticias
- Ofertas y descuentos
- Programa de fidelización

---

**Formato del versionado:** MAJOR.MINOR.PATCH
- MAJOR: Cambios incompatibles en la API
- MINOR: Nueva funcionalidad compatible
- PATCH: Correcciones de bugs compatibles
