# Despliegue seguro en VPS con Dokploy (Django)

## 1.Ventajas para usar dokploy en despliegue

1. Deploy desde Git con autodeploy.
2. Gestion centralizada de secretos (`.env` en panel, no en repo).
3. SSL y reverse proxy automatizable.
4. Facil separar app web, DB y backups.

---

## 2. Arquitectura recomendada (segura)
Para produccion usa esta estructura:

1. VPS Ubuntu 22.04/24.04 limpio.
2. Dokploy instalado en el VPS.
3. App Django en contenedor (Gunicorn).
4. PostgreSQL en servicio separado (idealmente volumen dedicado).
5. Backups automaticos de Postgres y media.
6. Dominio con HTTPS obligatorio.

No recomendado en produccion:
1. SQLite para trafico real.
2. Guardar secretos en repositorio.
3. Exponer puertos de DB publicamente.

---

## 3. Paso a paso completo

## Paso 1. Preparar VPS (hardening base)
Ejecuta como root o usuario sudo:

```bash
apt update && apt upgrade -y
apt install -y curl ufw fail2ban

# Firewall minimo
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

Recomendaciones:
1. Desactivar login root por SSH.
2. Usar clave SSH, no password.
3. Crear usuario admin y usar sudo.

---

## Paso 2. Instalar Dokploy
Sigue la instalacion oficial en tu VPS (segun version actual de Dokploy).

Al finalizar:
1. Entra al panel de Dokploy.
2. Crea usuario admin fuerte.
3. Activa 2FA si esta disponible.

---

## Paso 3. Preparar repositorio para contenedor
Tu proyecto ya tiene `gunicorn` y `whitenoise`. Solo necesitas Dockerfile y, opcionalmente, `.dockerignore`.

### 3.1 Dockerfile recomendado
Crea un `Dockerfile` en la raiz:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "hotel_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
```

### 3.2 .dockerignore recomendado
```gitignore
.venv
venv
__pycache__
*.pyc
*.pyo
*.pyd
.git
.gitignore
.env
db.sqlite3
media/
staticfiles/
```

Nota:
1. Si quieres persistencia de `media`, montala como volumen en Dokploy.

---

## Paso 4. Crear proyecto en Dokploy
En el panel:

1. New Project -> nombre: `hotel-rivera`.
2. Add Application -> tipo: Dockerfile.
3. Conectar repositorio GitHub.
4. Branch: `main` (o la que uses en produccion).
5. Build context: raiz del repo.
6. Port interno app: `8000`.

---

## Paso 5. Variables de entorno seguras (obligatorio)
En Dokploy, configura Environment Variables para la app.

Ejemplo base (adaptado a tu `settings.py`):

```env
SECRET_KEY=<SET_IN_SERVER_ENV_ONLY>
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=<SET_IN_SERVER_ENV_ONLY>
DB_USER=<SET_IN_SERVER_ENV_ONLY>
DB_PASSWORD=<SET_IN_SERVER_ENV_ONLY>
DB_HOST=<SET_IN_SERVER_ENV_ONLY>
DB_PORT=5432
DB_CONN_MAX_AGE=60
DB_CONN_HEALTH_CHECKS=True

BEHIND_PROXY=True
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
CSRF_COOKIE_SAMESITE=Lax
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

ADMIN_PATH=<SET_IN_SERVER_ENV_ONLY>
```

Buenas practicas:
1. No uses la `SECRET_KEY` de desarrollo.
2. Rota credenciales cada cierto tiempo.
3. Restringe acceso al panel Dokploy por IP/VPN si puedes.

---

## Paso 6. Base de datos PostgreSQL en Dokploy
Opciones:
1. Servicio Postgres gestionado dentro de Dokploy.
2. Postgres externo (gestionado por proveedor).

Recomendacion segura:
1. No publicar puerto 5432 a internet.
2. Permitir conexion solo desde la red interna Docker/Dokploy.
3. Activar backups diarios.

---

## Paso 7. Dominio y SSL
1. Apunta DNS (`A` o `CNAME`) al VPS.
2. En Dokploy, asigna dominio a la app.
3. Activa certificado SSL (Let's Encrypt) desde Dokploy.
4. Fuerza HTTPS.

Verifica:
1. `https://tu-dominio.com` carga bien.
2. Candado valido.
3. Redireccion HTTP -> HTTPS activa.

---

## Paso 8. Migraciones y superusuario
Tras el primer deploy, abre consola del contenedor app y ejecuta:

```bash
python manage.py migrate
python manage.py createsuperuser
python compile_mo.py
```

Comprobacion:

```bash
python manage.py check --deploy
```

Debe devolver sin errores criticos.

---

## Paso 9. Persistencia de archivos subidos (media)
Tu app usa `MEDIA_ROOT` para fotos de habitaciones.

En Dokploy:
1. Monta volumen persistente en ruta `/app/media`.
2. Incluye ese volumen en backups.

Sin volumen, perderas archivos al recrear contenedor.

---

## Paso 10. Backups y recuperacion
Minimo recomendado:

1. Backup PostgreSQL diario.
2. Backup `media/` diario.
3. Retencion 7-30 dias.
4. Prueba de restauracion mensual.

Ejemplo de politica:
1. Full diario de madrugada.
2. Retencion 14 dias.
3. Almacen externo (S3 o similar).

---

## Paso 11. Observabilidad y alertas
Configura:

1. Logs de app (gunicorn + Django).
2. Logs de reverse proxy.
3. Alerta por caida de servicio.
4. Alerta por errores 5xx altos.

Objetivo:
1. Detectar fallos antes que el cliente.

---

## Paso 12. Seguridad operativa continua
Checklist mensual:

1. Actualizar imagen base y dependencias Python.
2. Revisar usuarios admin y accesos Dokploy.
3. Rotar passwords/keys criticas.
4. Revisar backups y prueba restore.
5. Comprobar `check --deploy`.

---

## 4. Flujo de despliegue recomendado (sin downtime largo)
1. Push a `main`.
2. Dokploy build de nueva imagen.
3. Ejecutar migraciones.
4. Healthcheck OK.
5. Switch trafico a nueva version.
6. Si falla, rollback inmediato en Dokploy.

---

## 5. Errores comunes y como evitarlos

1. `DisallowedHost`:
   - Falta dominio en `ALLOWED_HOSTS`.

2. CSRF en formulario:
   - Falta `https://dominio` en `CSRF_TRUSTED_ORIGINS`.

3. Static 404:
   - `collectstatic` no ejecutado o mala ruta.

4. Archivos de media desaparecen:
   - No hay volumen persistente en `/app/media`.

5. Redireccion HTTPS infinita:
   - Revisar `BEHIND_PROXY=True` y headers del proxy.

---

## 6. Resumen rapido
Si quieres hacerlo seguro desde el dia 1 con Dokploy:

1. VPS hardening + firewall.
2. Dokploy + panel protegido.
3. App Docker con `DEBUG=False`.
4. Postgres aislado y con backups.
5. Variables sensibles solo en Dokploy.
6. SSL obligatorio + HSTS.
7. Volumen persistente para `media/`.
8. Monitorizacion y rollback listo.
