# 🚀 Guía de Despliegue - Hostal Rivera

Esta guía te ayudará a configurar y desplegar el proyecto en diferentes entornos.

## 📋 Checklist Pre-Despliegue

Antes de subir a GitHub o desplegar en producción:

- [x] Variables de entorno configuradas en `.env`
- [x] `.env` incluido en `.gitignore`
- [x] SECRET_KEY no hardcodeada en código
- [x] DEBUG=False para producción
- [x] ALLOWED_HOSTS configurado correctamente
- [x] Base de datos configurada (SQLite dev, PostgreSQL prod)
- [x] Archivos estáticos recopilados
- [x] Traducciones compiladas

## 🖥️ Despliegue Local (Desarrollo)

### 1. Configuración inicial
```powershell
# Clonar repositorio
git clone https://github.com/TU_USUARIO/WEB-HOTEL.git
cd WEB-HOTEL

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env desde plantilla
copy .env.example .env
```

### 2. Editar .env
```env
SECRET_KEY=django-insecure-CAMBIAR-ESTO-POR-CLAVE-ALEATORIA-DE-50-CHARS
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### 3. Preparar base de datos
```powershell
# Compilar traducciones
python compile_mo.py

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### 4. Ejecutar servidor
```powershell
python manage.py runserver
```

Visita: http://127.0.0.1:8000

## 🌐 Despliegue en Producción

### Opción 1: VPS (Linux con Nginx + Gunicorn)

#### 1. Preparar servidor
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib -y
```

#### 2. Configurar PostgreSQL
```bash
# Entrar a PostgreSQL
sudo -u postgres psql

# Crear base de datos y usuario
CREATE DATABASE hotel_db;
CREATE USER hotel_user WITH PASSWORD 'password_super_seguro';
ALTER ROLE hotel_user SET client_encoding TO 'utf8';
ALTER ROLE hotel_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE hotel_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE hotel_db TO hotel_user;
\q
```

#### 3. Clonar proyecto
```bash
cd /var/www
sudo git clone https://github.com/TU_USUARIO/WEB-HOTEL.git hotel
cd hotel
```

#### 4. Configurar entorno
```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Crear .env
sudo nano .env
```

Contenido de `.env` para producción:
```env
SECRET_KEY=generar-clave-super-segura-de-50-caracteres-aleatorios
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com,IP_SERVIDOR

DB_ENGINE=django.db.backends.postgresql
DB_NAME=hotel_db
DB_USER=hotel_user
DB_PASSWORD=password_super_seguro
DB_HOST=localhost
DB_PORT=5432
```

#### 5. Preparar Django
```bash
# Compilar traducciones
python compile_mo.py

# Migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Crear superusuario
python manage.py createsuperuser
```

#### 6. Configurar Gunicorn
```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/gunicorn.service
```

Contenido:
```ini
[Unit]
Description=Gunicorn daemon for Hotel Rivera
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/hotel
Environment="PATH=/var/www/hotel/venv/bin"
ExecStart=/var/www/hotel/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/var/www/hotel/gunicorn.sock \
          hotel_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar y habilitar servicio
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

#### 7. Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/hotel
```

Contenido:
```nginx
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/hotel/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/hotel/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/hotel/gunicorn.sock;
    }
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/hotel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 8. Configurar SSL con Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

### Opción 2: Heroku

#### 1. Preparar proyecto
```bash
# Instalar Heroku CLI
# Descargar desde: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login
```

#### 2. Crear archivos necesarios

**Procfile**:
```
web: gunicorn hotel_project.wsgi
```

**runtime.txt**:
```
python-3.11.8
```

**Actualizar requirements.txt**:
```bash
pip install gunicorn dj-database-url whitenoise
pip freeze > requirements.txt
```

#### 3. Modificar settings.py para Heroku

Añadir al final de `settings.py`:
```python
# Heroku deployment settings
import dj_database_url

if not DEBUG:
    # Producción en Heroku
    DATABASES['default'] = dj_database_url.config(conn_max_age=600)
    
    # Whitenoise para servir archivos estáticos
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
```

#### 4. Desplegar
```bash
# Crear app Heroku
heroku create nombre-tu-app

# Configurar variables de entorno
heroku config:set SECRET_KEY='tu-clave-secreta'
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS='nombre-tu-app.herokuapp.com'

# Desplegar
git push heroku main

# Migrar base de datos
heroku run python manage.py migrate

# Crear superusuario
heroku run python manage.py createsuperuser

# Abrir app
heroku open
```

### Opción 3: Railway.app

1. Conectar repositorio GitHub
2. Configurar variables de entorno en el dashboard
3. Railway detectará automáticamente Django y configurará todo

### Opción 4: PythonAnywhere

1. Subir código via Git
2. Crear virtualenv
3. Configurar WSGI
4. Configurar archivos estáticos
5. Recargar aplicación

## 🔧 Mantenimiento

### Actualizar código en producción
```bash
cd /var/www/hotel
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### Ver logs
```bash
# Logs de Gunicorn
sudo journalctl -u gunicorn -f

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Backup de base de datos
```bash
# PostgreSQL
pg_dump -U hotel_user hotel_db > backup_$(date +%Y%m%d).sql

# SQLite
cp db.sqlite3 backup_$(date +%Y%m%d).sqlite3
```

## 🔒 Seguridad en Producción

### Checklist de seguridad
- [ ] DEBUG=False
- [ ] SECRET_KEY única y segura (50+ caracteres aleatorios)
- [ ] ALLOWED_HOSTS configurado correctamente
- [ ] HTTPS configurado (SSL/TLS)
- [ ] CSRF y seguridad de cookies habilitadas
- [ ] Base de datos con contraseña fuerte
- [ ] Firewall configurado (solo puertos 80, 443, 22)
- [ ] Backups automáticos configurados
- [ ] Monitoring y logs configurados

### Generar SECRET_KEY segura
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

O visita: https://djecrety.ir/

## 📊 Monitoring

### Sentry (errores en producción)
```bash
pip install sentry-sdk
```

En `settings.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn="tu-dsn-de-sentry",
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
    )
```

## 🆘 Troubleshooting

### Error: "DisallowedHost"
- Verifica ALLOWED_HOSTS en .env
- Asegúrate de que incluye el dominio correcto

### Error: "OperationalError: no such table"
- Ejecuta: `python manage.py migrate`

### Error 500 en producción
- Verifica logs: `journalctl -u gunicorn`
- Comprueba DEBUG=False y ALLOWED_HOSTS

### Archivos estáticos no cargan
- Ejecuta: `python manage.py collectstatic`
- Verifica configuración de Nginx/servidor web

---

**¿Dudas? Consulta la documentación de Django:** https://docs.djangoproject.com/
