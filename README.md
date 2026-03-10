# 🏨 Sistema de Gestión Hotelera - Hostal Rivera

Sistema completo de gestión hotelera con reservas online, backoffice administrativo y cumplimiento de normativa española.

## ✨ Características

- 🏠 **Frontend público**: Listado de habitaciones, sistema de reservas, información del hotel
- 🔐 **Sistema de autenticación**: Registro, login, perfiles de usuario
- 📅 **Gestión de reservas**: Calendario con bloqueo de fechas ocupadas, prevención de doble reserva
- 👤 **Perfiles de usuario**: Edición de datos personales, historial de reservas
- 🌍 **Multiidioma**: Español, Gallego, Inglés
- 📱 **Responsive**: Diseñado con Bootstrap 5
- ✅ **Validaciones**: Backend y frontend para evitar errores

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.11+ con Django 5.0
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: Django Templates + Bootstrap 5
- **Librerías**: 
  - python-decouple (gestión de variables de entorno)
  - django-crispy-forms + crispy-bootstrap5 (formularios)
  - reportlab (PDFs)
  - openpyxl (Excel)
  - Pillow (procesamiento de imágenes)
  - Flatpickr (calendario frontend)

## 🚀 Instalación

### 1. Clonar el repositorio
```powershell
git clone https://github.com/TU_USUARIO/WEB-HOTEL.git
cd WEB-HOTEL
```

### 2. Crear entorno virtual
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1  # En Windows PowerShell
# O en Linux/Mac: source venv/bin/activate
```

### 3. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```powershell
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env con tus valores
# IMPORTANTE: Cambia SECRET_KEY por una clave aleatoria segura
# Puedes generarla en: https://djecrety.ir/
```

### 5. Compilar traducciones
```powershell
python compile_mo.py
```

### 6. Migrar base de datos
```powershell
python manage.py migrate
```

### 7. Crear superusuario
```powershell
python manage.py createsuperuser
```

### 8. Cargar datos de prueba (opcional)
```powershell
# Si tienes fixtures preparados
python manage.py loaddata fixtures/inicial.json
```

### 9. Ejecutar servidor de desarrollo
```powershell
python manage.py runserver
```

Accede a: http://127.0.0.1:8000/

## 📂 Estructura del Proyecto

```
WEB HOTEL/
├── hotel_project/          # Configuración Django
│   ├── settings.py        # Configuración principal (usa .env)
│   ├── urls.py            # URLs principales
│   └── wsgi.py
├── reservas/              # App principal
│   ├── models.py         # Modelos: Cliente, Habitación, Reserva
│   ├── views.py          # Vistas y lógica de negocio
│   ├── forms.py          # Formularios de registro, reserva, perfil
│   ├── admin.py          # Panel administrativo
│   ├── urls.py           # URLs de la app
│   └── templates/        # Plantillas HTML
│       └── reservas/
│           ├── base.html
│           ├── home.html
│           ├── listado_habitaciones.html
│           ├── crear_reserva.html
│           └── ...
├── static/               # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
│       ├── logo/
│       ├── background/
│       ├── galeria/
│       ├── iconos/
│       └── via_kunig/
├── media/                # Uploads de usuarios (no incluido en repo)
├── locale/               # Traducciones (ES, GL, EN)
│   ├── es/LC_MESSAGES/
│   ├── gl/LC_MESSAGES/
│   └── en/LC_MESSAGES/
├── .env.example          # Plantilla de variables de entorno
├── .gitignore            # Archivos excluidos de Git
├── requirements.txt      # Dependencias Python
├── compile_mo.py         # Script para compilar traducciones
└── manage.py             # CLI de Django
```

## 🔐 Seguridad

### Variables de entorno
El proyecto usa `python-decouple` para gestión segura de configuración:

- ✅ **SECRET_KEY**: Clave secreta de Django (nunca la expongas)
- ✅ **DEBUG**: Modo debug (True en desarrollo, False en producción)
- ✅ **ALLOWED_HOSTS**: Hosts permitidos
- ✅ **DATABASE**: Configuración de base de datos
- ✅ **EMAIL**: Credenciales de email (si se usa)

### Archivos no incluidos en el repositorio
Por seguridad, estos archivos están en `.gitignore`:
- `.env` (variables de entorno)
- `db.sqlite3` (base de datos local)
- `/media` (archivos subidos por usuarios)
- `*.log` (logs)
- `__pycache__/`, `.pyc` (archivos compilados)

## 🌍 Internacionalización

El proyecto soporta 3 idiomas:
- 🇪🇸 Español (por defecto)
- 🇬🇱 Gallego
- 🇬🇧 Inglés

Para añadir/editar traducciones:
1. Edita los archivos `.po` en `locale/[idioma]/LC_MESSAGES/django.po`
2. Ejecuta `python compile_mo.py` para compilar

## 📋 Funcionalidades Principales

### Para Clientes
- ✅ Registro y autenticación
- ✅ Ver habitaciones disponibles
- ✅ Crear reservas con validación de fechas
- ✅ Ver calendario de disponibilidad
- ✅ Editar perfil personal
- ✅ Historial de reservas

### Para Administradores
- ✅ Panel de administración Django
- ✅ Gestión de habitaciones
- ✅ Gestión de reservas
- ✅ Gestión de clientes
- ✅ Visualización de ocupación

## 🚀 Despliegue en Producción

### Configuración recomendada

1. **Variables de entorno**:
```bash
SECRET_KEY=tu-clave-super-secreta-de-50-caracteres-aleatorios
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hotel_production
DB_USER=hotel_user
DB_PASSWORD=password_seguro
DB_HOST=localhost
DB_PORT=5432
```

2. **Base de datos**: Migra a PostgreSQL
3. **Archivos estáticos**: Ejecuta `python manage.py collectstatic`
4. **Servidor web**: Usa Gunicorn + Nginx
5. **HTTPS**: Configura certificado SSL

### Ejemplo con Gunicorn
```bash
pip install gunicorn
gunicorn hotel_project.wsgi:application --bind 0.0.0.0:8000
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de código abierto bajo licencia MIT.

## 📧 Contacto

Para consultas: info@hostalrivera.es

---

**Desarrollado con ❤️ usando Django**
