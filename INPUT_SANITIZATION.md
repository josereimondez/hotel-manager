# 🛡️ Input Sanitization & Security - Sistema de Gestión Hotelera

## 📋 Resumen

Este documento detalla todas las medidas de sanitización y seguridad de inputs implementadas en el proyecto para prevenir vulnerabilidades comunes.

---

## 🔒 Protecciones Incorporadas de Django

Django incluye protección automática contra:

### 1. **SQL Injection**
- ✅ **ORM de Django**: Todas las consultas usan el ORM que escapa automáticamente los parámetros
- ✅ **Nunca usamos SQL raw**: No hay consultas SQL directas vulnerables
- ✅ **Validación de tipos**: Los campos del modelo validan tipos de datos

### 2. **Cross-Site Scripting (XSS)**
- ✅ **Auto-escape en templates**: Django escapa automáticamente `{{ variable }}`
- ✅ **strip_tags()**: Eliminamos HTML tags de inputs de usuario
- ✅ **Validación de campos**: Solo permitimos caracteres seguros

### 3. **Cross-Site Request Forgery (CSRF)**
- ✅ **Token CSRF**: Todos los formularios POST incluyen `{% csrf_token %}`
- ✅ **Middleware CSRF**: Activo en settings.py
- ✅ **Decorador @csrf_protect**: En vistas sensibles

### 4. **Clickjacking**
- ✅ **X-Frame-Options**: Configurado en settings.py
- ✅ **DENY**: No permitimos que el sitio se cargue en iframes

---

## 🛡️ Sanitización Personalizada Implementada

### **Formularios (forms.py)**

#### 1. **RegistroUsuarioForm**
```python
✅ Username:
   - Solo permite: letras, números, guiones y guiones bajos
   - Mínimo 3 caracteres, máximo 30
   - Elimina HTML tags con strip_tags()
   - Regex: ^[a-zA-Z0-9_-]+$

✅ Email:
   - Convertido a minúsculas
   - Eliminados espacios
   - Validado formato email con EmailValidator

✅ Password:
   - Mínimo 8 caracteres
   - Confirmación requerida
   - Hash seguro con PBKDF2
```

#### 2. **ClienteRegistroForm**
```python
✅ Nombre/Apellidos:
   - Solo letras (incluyendo tildes y ñ)
   - Elimina HTML tags
   - Capitaliza automáticamente (Title Case)
   - Regex: ^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$

✅ Teléfono:
   - Solo números, +, espacios y guiones
   - Mínimo 9 dígitos
   - Eliminados caracteres peligrosos

✅ Email:
   - Convertido a minúsculas
   - Eliminados espacios
   - Validado formato

✅ Ciudad/País:
   - Solo letras y guiones
   - Capitalizado automáticamente

✅ Dirección:
   - Elimina HTML tags
   - Trim de espacios
```

#### 3. **ReservaForm**
```python
✅ Observaciones:
   - Elimina HTML tags
   - Máximo 500 caracteres
   - Trim de espacios

✅ Número de adultos/niños:
   - Validación de rangos (1-10 adultos, 0-10 niños)
   - Solo números enteros
   - Previene valores negativos

✅ Fechas:
   - Formato ISO validado
   - Fecha salida > fecha entrada
   - Previene fechas en el pasado
   - Validación de solapamiento con otras reservas
```

---

### **Vistas (views.py)**

#### 1. **login_view**
```python
✅ Sanitización:
   - strip_tags() en username
   - Trim de espacios
   - Validación de campos no vacíos
   - Password no sanitizado (se compara con hash)
```

#### 2. **listado_habitaciones**
```python
✅ Filtros GET:
   - tipo: Validado contra TIPO_CHOICES permitidos
   - precio_max: Validado como float > 0
   - Elimina HTML tags de todos los parámetros
   - Ignora valores inválidos silenciosamente
```

#### 3. **Todas las vistas POST**
```python
✅ Protecciones:
   - Requieren CSRF token
   - Usan formularios de Django (validación automática)
   - @login_required para vistas protegidas
   - Validación de permisos de usuario
```

---

### **Modelos (models.py)**

#### 1. **Cliente.clean()**
```python
✅ Sanitización automática antes de guardar:
   - strip_tags() en: nombre, apellidos, dirección, ciudad, país
   - Validación de email con EmailValidator
   - Validación de teléfono (mínimo 9 dígitos)
   - Validación de DNI/NIE con algoritmo oficial
```

#### 2. **Reserva**
```python
✅ Validaciones:
   - Observaciones: máximo 500 caracteres + strip_tags()
   - Fechas: validación de orden y solapamiento
   - Capacidad: validación contra capacidad de habitación
   - Estados: solo valores de ESTADO_CHOICES
```

#### 3. **Habitacion**
```python
✅ Validaciones:
   - Precios: solo valores positivos
   - Capacidad: rango 1-10
   - Tipo: solo valores de TIPO_CHOICES
```

---

## 🚨 Validaciones de DNI/NIE

```python
✅ Función validar_dni_nie():
   - Regex para formato correcto
   - Validación del dígito de control
   - Soporta DNI y NIE (X, Y, Z)
   - Algoritmo oficial español
```

---

## 🔐 Configuración de Seguridad (settings.py)

### **Producción (DEBUG=False)**
```python
✅ HTTPS/SSL:
   - SECURE_SSL_REDIRECT = True
   - SESSION_COOKIE_SECURE = True
   - CSRF_COOKIE_SECURE = True

✅ HSTS (HTTP Strict Transport Security):
   - SECURE_HSTS_SECONDS = 31536000 (1 año)
   - SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   - SECURE_HSTS_PRELOAD = True

✅ Protecciones adicionales:
   - SECURE_BROWSER_XSS_FILTER = True
   - SECURE_CONTENT_TYPE_NOSNIFF = True
   - X_FRAME_OPTIONS = 'DENY'
```

---

## 📊 Matriz de Vulnerabilidades vs Protecciones

| Vulnerabilidad | Protección | Estado |
|----------------|------------|--------|
| SQL Injection | ORM Django + Validación de tipos | ✅ Protegido |
| XSS (Stored) | strip_tags() + auto-escape templates | ✅ Protegido |
| XSS (Reflected) | strip_tags() + validación inputs | ✅ Protegido |
| CSRF | Token CSRF en todos los forms | ✅ Protegido |
| Clickjacking | X-Frame-Options: DENY | ✅ Protegido |
| Session Hijacking | Cookies seguras + HTTPS | ✅ Protegido |
| Brute Force (Login) | Rate limiting: 5 intentos/min | ✅ Protegido |
| Brute Force (API) | Rate limiting: 60 req/min | ✅ Protegido |
| DoS/DDoS | Rate limiting por IP y usuario | ✅ Protegido |
| Spam (Registro) | Rate limiting: 3 registros/hora | ✅ Protegido |
| Reservation Spam | Rate limiting: 10 reservas/hora | ✅ Protegido |
| File Upload | No implementado aún | ℹ️ N/A |
| Command Injection | No usamos shell commands | ✅ Protegido |
| Path Traversal | No hay acceso directo a archivos | ✅ Protegido |
| Open Redirect | Validación de URLs de redirección | ✅ Protegido |
| Mass Assignment | ModelForm con fields explícitos | ✅ Protegido |

---

## ✅ Checklist de Seguridad

### Inputs de Usuario
- [x] Username: regex validado, sin HTML
- [x] Email: validado, normalizado
- [x] Password: mínimo 8 caracteres, hash PBKDF2
- [x] Nombre/Apellidos: solo letras, sin HTML
- [x] Teléfono: solo dígitos y caracteres permitidos
- [x] DNI/NIE: validación con algoritmo oficial
- [x] Direcciones: sin HTML tags
- [x] Observaciones: limitadas a 500 chars, sin HTML
- [x] Fechas: validación de formato y lógica
- [x] Números: validación de rangos

### Formularios
- [x] Todos los POST tienen CSRF token
- [x] Validación en formulario (forms.py)
- [x] Validación en modelo (models.py)
- [x] Mensajes de error claros pero no informativos para atacantes

### Templates
- [x] Auto-escape habilitado
- [x] No usar |safe sin sanitizar primero
- [x] Validación de variables antes de renderizar

### Configuración
- [x] SECRET_KEY en variable de entorno
- [x] DEBUG=False en producción
- [x] ALLOWED_HOSTS configurado
- [x] HTTPS forzado en producción
- [x] Cookies seguras

---

## 🔄 Flujo de Sanitización

```
Usuario envía datos
       ↓
1. Django CSRF valida token
       ↓
2. Formulario.clean_CAMPO() - Primera sanitización
       ↓
3. Formulario.clean() - Validación cruzada
       ↓
4. Modelo.clean() - Sanitización adicional
       ↓
5. Modelo.save() - Validadores de campo
       ↓
6. Base de datos (con tipos validados)
       ↓
7. Template auto-escape al renderizar
       ↓
Usuario ve datos seguros
## 🚀 Mejoras Futuras Recomendadas

### Alta Prioridad
- [x] **Rate Limiting**: django-ratelimit implementado ✅
- [ ] **Two-Factor Authentication (2FA)**: django-otp
- [ ] **CAPTCHA**: django-recaptcha en formularios públicos
- [ ] **Content Security Policy (CSP)**: Headers CSP

### Media Prioridad
- [ ] **File Upload Validation**: Si se implementa subida de archivos
- [ ] **Email Verification**: Verificar emails en registro
- [ ] **Password Strength Meter**: Feedback visual en frontend
- [ ] **Session Timeout**: Cerrar sesión automático tras inactividad

### Baja Prioridad
- [ ] **Logs de Seguridad**: django-axes para logs de intentos fallidos
- [ ] **Honey Pots**: Campos trampa en formularios
- [ ] **IP Blacklisting**: Bloqueo de IPs maliciosas
- [ ] **WAF**: Web Application Firewall en servidor

---

## 🛡️ Rate Limiting Implementado

### **django-ratelimit 4.1.0**

Rate limiting configurado para prevenir abuso y ataques de fuerza bruta:

#### 1. **API de Fechas Ocupadas**
```python
@ratelimit(key='ip', rate='60/m', method='GET', block=True)
def fechas_ocupadas(request, habitacion_id):
    # Rate limit: 60 peticiones por minuto por IP
```
- **Límite**: 60 requests/minuto por IP
- **Método**: GET
- **Propósito**: Prevenir scraping masivo de disponibilidad

#### 2. **Login (Autenticación)**
```python
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@ratelimit(key='post:username', rate='5/m', method='POST', block=True)
def login_view(request):
    # Rate limit: 5 intentos por minuto por IP y por username
```
- **Límite**: 5 intentos/minuto por IP
- **Límite adicional**: 5 intentos/minuto por username
- **Método**: POST
- **Propósito**: Prevenir ataques de fuerza bruta (brute force)

#### 3. **Registro de Clientes**
```python
@ratelimit(key='ip', rate='3/h', method='POST', block=True)
def registro_cliente(request):
    # Rate limit: 3 registros por hora por IP
```
- **Límite**: 3 registros/hora por IP
- **Método**: POST
- **Propósito**: Prevenir spam de cuentas falsas

#### 4. **Crear Reserva**
```python
@login_required
@ratelimit(key='user', rate='10/h', method='POST', block=True)
def crear_reserva(request, habitacion_id):
    # Rate limit: 10 reservas por hora por usuario
```
- **Límite**: 10 reservas/hora por usuario autenticado
- **Método**: POST
- **Propósito**: Prevenir spam de reservas y bloqueo malicioso de habitaciones

### **Middleware Personalizado**

`reservas/middleware.py` - `RatelimitMiddleware`:
- Captura excepciones `Ratelimited`
- Renderiza página de error elegante (HTTP 429)
- Mensajes personalizados según la ruta
- Contador de tiempo para reintentar

### **Template de Error**

`reservas/templates/reservas/error_ratelimit.html`:
- Diseño amigable con Bootstrap
- Explicación clara del límite
- Contador regresivo (60 segundos)
- Enlaces para volver al inicio o ir atrás
- Traducible con i18n

### **Configuración en settings.py**

```python
MIDDLEWARE = [
    # ... otros middlewares
    'reservas.middleware.RatelimitMiddleware',  # 🔒 Rate limiting
]
```

--- ] **Honey Pots**: Campos trampa en formularios
- [ ] **IP Blacklisting**: Bloqueo de IPs maliciosas
- [ ] **WAF**: Web Application Firewall en servidor

---

## 📚 Recursos y Referencias

### Django Security
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

### Herramientas de Testing
```bash
# Verificar configuración de seguridad
python manage.py check --deploy

# Análisis de seguridad
pip install bandit
bandit -r . -x ./venv

# Dependencias vulnerables
pip install safety
safety check
```

---

## 🆘 Reportar Vulnerabilidades

Si encuentras una vulnerabilidad de seguridad:
1. **NO** la publiques en issues públicos
2. Envía email a: security@hostalrivera.es
3. Incluye: descripción, pasos para reproducir, impacto
4. Recibirás confirmación en 48h

---

**Última actualización**: 10/03/2026  
**Versión del documento**: 1.0  
**Responsable de seguridad**: Equipo de desarrollo
