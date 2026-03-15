# Checklist exacto: migración a PostgreSQL en VPS (Django)

Este checklist asume Ubuntu/Debian en el VPS y que la app Django está en `hotel-manager`.

## 1) Preparar PostgreSQL en el VPS

1. Actualizar paquetes:

```bash
sudo apt update
sudo apt upgrade -y
```

2. Instalar PostgreSQL y utilidades:

```bash
sudo apt install -y postgresql postgresql-contrib
```

3. Comprobar servicio:

```bash
sudo systemctl status postgresql
```

## 2) Crear base de datos y usuario

1. Entrar en consola de postgres:

```bash
sudo -u postgres psql
```

2. Crear usuario y base (cambia valores):

```sql
CREATE USER hotel_user WITH PASSWORD '<SET_IN_SERVER_ENV_ONLY>';
CREATE DATABASE hotel_db OWNER hotel_user;
ALTER ROLE hotel_user SET client_encoding TO 'utf8';
ALTER ROLE hotel_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE hotel_user SET timezone TO 'Europe/Madrid';
GRANT ALL PRIVILEGES ON DATABASE hotel_db TO hotel_user;
\q
```

## 3) Endurecer acceso (seguridad)

1. Buscar versión activa de postgres:

```bash
ls /etc/postgresql
```

2. Editar `postgresql.conf` (ejemplo para versión 16):

```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```

3. Verificar:

```conf
listen_addresses = 'localhost'
```

4. Editar `pg_hba.conf`:

```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

5. Asegurar reglas locales seguras:

```conf
local   all             postgres                                peer
local   all             all                                     scram-sha-256
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
```

6. Reiniciar PostgreSQL:

```bash
sudo systemctl restart postgresql
```

## 4) Preparar proyecto Django

1. Entrar a carpeta del proyecto:

```bash
cd /ruta/a/hotel-manager
```

2. Activar entorno virtual:

```bash
source .venv/bin/activate
```

3. Instalar driver PostgreSQL:

```bash
pip install psycopg2-binary
```

4. Guardar dependencias:

```bash
pip freeze > requirements.txt
```

## 5) Configurar variables de entorno (.env)

Configura estos valores en `.env` de producción:

```env
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,IP_DEL_VPS

DB_ENGINE=django.db.backends.postgresql
DB_NAME=hotel_db
DB_USER=hotel_user
DB_PASSWORD=<SET_IN_SERVER_ENV_ONLY>
DB_HOST=127.0.0.1
DB_PORT=5432
```

## 6) Migrar datos desde SQLite a PostgreSQL

### Opcion A (recomendada para este proyecto): dump/load con Django

1. Backup de SQLite:

```bash
cp db.sqlite3 db.sqlite3.backup
```

2. Exportar datos a JSON:

```bash
python manage.py dumpdata --exclude contenttypes --exclude auth.permission > data.json
```

3. Aplicar esquema en PostgreSQL:

```bash
python manage.py migrate
```

4. Cargar datos:

```bash
python manage.py loaddata data.json
```

5. Limpiar archivo temporal:

```bash
rm data.json
```

### Opcion B (si prefieres migracion avanzada)

Usar herramientas externas de ETL para mapear SQLite a PostgreSQL (no necesario en la mayoria de casos para este proyecto).

## 7) Corregir secuencias (muy importante)

Si ves errores de clave duplicada al crear registros, resetea secuencias:

```bash
python manage.py sqlsequencereset reservas auth admin contenttypes sessions | python manage.py dbshell
```

## 8) Verificacion funcional

1. Comprobar checks:

```bash
python manage.py check
```

2. Probar login, registro, crear reserva y menu del dia.
3. Verificar panel admin y que se pueden crear habitaciones/reservas.

## 9) Backup automatico diario

1. Crear carpeta de backups:

```bash
mkdir -p ~/backups/postgres
```

2. Script de backup `~/backup_postgres.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
FECHA=$(date +%F_%H-%M)
PGPASSWORD="${DB_PASSWORD:?Define DB_PASSWORD en variables de entorno}" \
	pg_dump -h 127.0.0.1 -U hotel_user -d hotel_db -F c \
	-f "$HOME/backups/postgres/hotel_db_${FECHA}.dump"
find "$HOME/backups/postgres" -type f -name "*.dump" -mtime +14 -delete
```

3.1. Antes de ejecutar el script, exporta la clave en el entorno del usuario del sistema:

```bash
export DB_PASSWORD='<SET_IN_SERVER_ENV_ONLY>'
```

4. Dar permisos:

```bash
chmod +x ~/backup_postgres.sh
```

5. Cron diario (03:30):

```bash
crontab -e
```

Agregar linea:

```cron
30 3 * * * DB_PASSWORD='<SET_IN_SERVER_ENV_ONLY>' /home/tu_usuario/backup_postgres.sh >/dev/null 2>&1
```

## 10) Rollback rapido (si algo falla)

1. Volver temporalmente a SQLite en `.env`:

```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

2. Reiniciar servicio de la app.

---

## Checklist final (marcar)

- [ ] PostgreSQL instalado y activo
- [ ] Usuario y base creados
- [ ] `.env` con `DB_ENGINE=django.db.backends.postgresql`
- [ ] `psycopg2-binary` instalado
- [ ] `migrate` ejecutado sin errores
- [ ] Datos migrados y validados
- [ ] Secuencias reseteadas (si aplica)
- [ ] Backups automaticos en cron
- [ ] Pruebas funcionales completadas
