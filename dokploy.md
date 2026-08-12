# Despliegue en Proxmox con Dokploy - Hostal Rivera

Guia completa para autohostear la web de Hostal Rivera en un servidor Proxmox con Dokploy.

---

## Arquitectura

```
Internet
   │
   ▼
┌─────────────────────────┐
│  Cloudflare (DNS+Proxy) │  ← SSL, DDoS protection, WAF basico
│  DDNS actualiza IP      │
└────────┬────────────────┘
         │ Puerto 80/443
         ▼
┌─────────────────────────┐
│  Router Movistar        │  ← Port forwarding 80→VM, 443→VM
│  (NAT)                  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              PROXMOX (ZFS, 1 nodo)                   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  VM Ubuntu 24.04 LTS (Dokploy)               │   │
│  │  ┌────────────────────────────────────────┐  │   │
│  │  │  Traefik (reverse proxy + SSL LE)      │  │   │
│  │  │  PostgreSQL (servicio Dokploy)         │  │   │
│  │  │  Django App (Dockerfile → Gunicorn)    │  │   │
│  │  │  Volumenes: media, postgres, backups   │  │   │
│  │  └────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  Proxmox Backup (VM completa, diario)               │
└─────────────────────────────────────────────────────┘
         │
         ▼ (USB)
┌─────────────────────────┐
│  SAI Salicru 1200       │  ← NUT para shutdown seguro
└─────────────────────────┘
```

---

## Fase 1: Configuracion del UPS (NUT)

El SAI Salicru 1200 necesita NUT para comunicar con Proxmox y hacer shutdown seguro.

### 1.1 Instalar NUT en Proxmox

```bash
# En el host Proxmox (no en la VM)
apt install nut -y
```

### 1.2 Configurar NUT

Editar `/etc/nut/nut.conf`:
```
MODE=standalone
```

Editar `/etc/nut/ups.conf`:
```
[salicru1200]
    driver = blazer_usb
    port = auto
    desc = "Salicru SPS 1200"
    vendorid = 0665
    productid = 5161
```

> Nota: El vendorid/productid puede variar. Verifica con `lsusb` que tu Salicru aparece.

Editar `/etc/nut/upsd.conf`:
```
LISTEN 127.0.0.1 3493
```

Editar `/etc/nut/upsd.users`:
```
[admin]
    password = tu-contrasena-segura
    actions = SET
    instcmds = ALL
```

Editar `/etc/nut/upsmon.conf`:
```
MONITOR salicru1200@localhost 1 admin tu-contrasena-segura master
POWERDOWNFLAG /etc/killpower
SHUTDOWNCMD "/sbin/shutdown -h +0"
```

### 1.3 Iniciar servicio

```bash
systemctl enable nut-server nut-monitor
systemctl start nut-server nut-monitor
upsc salicru1200@localhost
```

Si `upsc` muestra datos del UPS (voltaje, carga bateria, etc.), funciona.

### 1.4 Configurar shutdown por bateria baja

El shutdown se activa automaticamente cuando:
- Bateria < 20% Y tiempo restante estimado < 5 minutos
- O bateria critica (< 5%)

Verifica con:
```bash
upsc salicru1200@localhost | grep -E "battery|runtime|ups.status"
```

---

## Fase 2: Crear VM en Proxmox

### 2.1 Descargar Ubuntu Server

```bash
# En el host Proxmox
cd /var/lib/vz/template/iso
wget https://releases.ubuntu.com/24.04/ubuntu-24.04.1-live-server-amd64.iso
```

### 2.2 Crear VM desde panel Proxmox

| Parametro | Valor |
|---|---|
| **Nombre** | dokploy-hostal |
| **OS** | Ubuntu 24.04 LTS |
| **CPU** | 2-4 cores |
| **RAM** | 4096 MB minimo (8192 recomendado) |
| **Disco** | 40 GB minimo, bus SCSI, cache Write Back |
| **Red** | vmbr0 (bridge), MAC automatica |
| **Cloud-Init** | Configurar usuario, SSH key, red |

### 2.3 Cloud-Init (recomendado)

En la VM, pestaña Cloud-Init:
- **User**: `admin`
- **SSH public key**: Tu clave publica SSH
- **IP**: DHCP o estatica segun tu red
- **DNS**: 1.1.1.1 / 8.8.8.8

### 2.4 Iniciar VM

```bash
# Desde panel Proxmox o CLI
qm start <VMID>
```

---

## Fase 3: Hardening de la VM

Conectate por SSH a la VM:

```bash
ssh admin@<IP-VM>
```

### 3.1 Actualizar sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 3.2 Configurar firewall (UFW)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment "SSH"
sudo ufw allow 80/tcp comment "HTTP"
sudo ufw allow 443/tcp comment "HTTPS"
sudo ufw enable
sudo ufw status verbose
```

### 3.3 SSH seguro

Editar `/etc/ssh/sshd_config`:
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
Port 22
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
```

Reiniciar SSH:
```bash
sudo systemctl restart sshd
```

### 3.4 Instalar fail2ban

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

Crear `/etc/fail2ban/jail.local`:
```ini
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
```

### 3.5 Actualizaciones automaticas

```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### 3.6 Instalar Docker

```bash
# Script oficial de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh
```

Verifica:
```bash
docker --version
docker compose version
```

---

## Fase 4: Instalar Dokploy

### 4.1 Instalacion

```bash
curl -sSL https://dokploy.com/install.sh | sh
```

### 4.2 Acceder al panel

1. Abre `http://<IP-VM>:3000`
2. Crea usuario admin con contrasena fuerte
3. Activa 2FA si esta disponible

### 4.3 Proteger el panel

- No expongas el puerto 3000 al exterior
- Accede al panel solo desde tu red local o via SSH tunnel:
  ```bash
  ssh -L 3000:localhost:3000 admin@<IP-VM>
  ```
- Luego abre `http://localhost:3000` en tu navegador

---

## Fase 5: Configurar dominio y Cloudflare

### 5.1 Comprar dominio

Compra tu dominio (ej: `hostalrivera.com`) en cualquier registrador.

### 5.2 Configurar Cloudflare

1. Anade tu dominio a Cloudflare
2. Cambia los nameservers del registrador a los de Cloudflare
3. Crea registros DNS:
   - **Tipo A**: `@` → IP publica de tu router
   - **Tipo A**: `www` → IP publica de tu router
   - **Proxy status**: Proxied (naranja)

### 5.3 DDNS

Configura un cliente DDNS en tu red local para actualizar la IP en Cloudflare automaticamente. Opciones:
- `cloudflare-ddns` (Docker container)
- Script con cron + API de Cloudflare
- Tu router si soporta DDNS con Cloudflare

### 5.4 Port forwarding en router Movistar

En el router, redirige:
- Puerto 80 → IP de la VM Dokploy
- Puerto 443 → IP de la VM Dokploy

> Nota: Si Cloudflare esta en modo Proxied, el trafico llega a Cloudflare y luego a tu IP. Los puertos 80/443 deben estar abiertos igualmente para la validacion de SSL.

---

## Fase 6: Desplegar aplicacion en Dokploy

### 6.1 Crear proyecto

En el panel de Dokploy:
1. **New Project** → Nombre: `hostal-rivera`
2. **Add Service** → **Application**
3. **Source**: Git Repository
4. **Repository URL**: `https://github.com/TU_USUARIO/WEB-HOTEL.git`
5. **Branch**: `main`
6. **Build type**: Dockerfile
7. **Dockerfile path**: `Dockerfile` (raiz del repo)
8. **Port**: `8000`

### 6.2 Crear base de datos PostgreSQL

En el panel de Dokploy:
1. **Add Service** → **PostgreSQL**
2. Nombre: `postgres-hostal`
3. Configura usuario y contrasena seguros
4. **No expongas el puerto 5432** al exterior
5. Anota las credenciales para las variables de entorno

### 6.3 Configurar variables de entorno

En la aplicacion Django, anade estas variables:

```env
SECRET_KEY=<genera-una-clave-aleatoria-de-50-caracteres>
DEBUG=False
ALLOWED_HOSTS=hostalrivera.com,www.hostalrivera.com
CSRF_TRUSTED_ORIGINS=https://hostalrivera.com,https://www.hostalrivera.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=hostal_db
DB_USER=<usuario-postgres>
DB_PASSWORD=<contrasena-postgres>
DB_HOST=<host-interno-postgres-dokploy>
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

ADMIN_PATH=<tu-ruta-admin-secreta>
```

> **IMPORTANTE**: La `SECRET_KEY` solo se genera una vez. Si la cambias, todas las sesiones y tokens se invalidan.

### 6.4 Configurar dominio y SSL

En la aplicacion Django dentro de Dokploy:
1. **Domains** → Anade `hostalrivera.com` y `www.hostalrivera.com`
2. **SSL** → Activa Let's Encrypt (automatico con Dokploy)
3. Verifica que el certificado se genera correctamente

### 6.5 Configurar volumen para media

En la aplicacion Django dentro de Dokploy:
1. **Volumes** → Anade volumen persistente
2. **Mount path**: `/app/media`
3. Esto asegura que las fotos de habitaciones no se pierdan al recrear el contenedor

### 6.6 Deploy

1. Pulsa **Deploy** en el panel
2. Espera a que el build termine
3. Verifica que la app esta corriendo

### 6.7 Primer despliegue: migraciones y superusuario

Abre la consola del contenedor de la app en Dokploy y ejecuta:

```bash
python manage.py migrate
python compile_mo.py
python manage.py createsuperuser
python manage.py check --deploy
```

`check --deploy` debe devolver sin errores criticos.

---

## Fase 7: Backups

### 7.1 Backups en Proxmox (VM completa)

En el panel de Proxmox:
1. Selecciona la VM `dokploy-hostal`
2. **Backup** → **Add**
3. **Schedule**: Diario a las 03:00
4. **Storage**: local-zfs (o tu storage ZFS)
5. **Mode**: Snapshot
6. **Retention**: 7 dias

### 7.2 Backups de PostgreSQL (dentro de Dokploy)

Dokploy permite configurar backups automaticos para servicios PostgreSQL.

En el servicio PostgreSQL de Dokploy:
1. **Backups** → **Add**
2. **Schedule**: Diario a las 02:00
3. **Retention**: 14 dias
4. **Destination**: Volumen local o S3/Backblaze B2

### 7.3 Backup offsite (recomendado)

Para cumplir la regla 3-2-1 (3 copias, 2 medios, 1 offsite):

```bash
# Instalar rclone en la VM
curl https://rclone.org/install.sh | sudo bash

# Configurar destino (ej: Backblaze B2)
rclone config
# Sigue los pasos para anadir B2, S3, o cualquier storage remoto

# Script de backup (guardar en /usr/local/bin/backup-offsite.sh)
#!/bin/bash
set -e
BACKUP_DIR="/tmp/backup-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup DB desde contenedor PostgreSQL
docker exec <nombre-contenedor-postgres> pg_dump -U <usuario> -d <db> -F c -f /tmp/db.dump
docker cp <nombre-contenedor-postgres>:/tmp/db.dump "$BACKUP_DIR/"

# Backup media
docker cp <nombre-contenedor-app>:/app/media "$BACKUP_DIR/"

# Subir a offsite
rclone sync "$BACKUP_DIR" remoto:backups-hostal/$(date +%Y%m%d) --encrypt

# Limpiar
rm -rf "$BACKUP_DIR"
```

Programa con cron:
```cron
0 4 * * 0 /usr/local/bin/backup-offsite.sh >> /var/log/backup-offsite.log 2>&1
```

### 7.4 Restaurar backup

**Desde Proxmox** (VM completa):
1. Selecciona la VM en Proxmox
2. **Backup** → Selecciona el backup → **Restore**

**Desde pg_dump** (solo DB):
```bash
docker exec -i <contenedor-postgres> pg_restore -U <usuario> -d <db> -c < backup.dump
```

**Desde offsite**:
```bash
rclone sync remoto:backups-hostal/20250101 /tmp/restore
# Restaurar DB y media manualmente
```

---

## Fase 8: Flujo de actualizacion

### Actualizacion normal (push a main)

1. Haz push a `main` en GitHub
2. Dokploy detecta el cambio y hace build automatico
3. Ejecuta migraciones desde la consola del contenedor:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
4. Verifica que la app funciona

### Actualizacion manual

1. En Dokploy, ve a la aplicacion
2. Pulsa **Redeploy**
3. Espera el build
4. Ejecuta migraciones

### Rollback

Si algo falla:
1. En Dokploy, ve al historial de deployments
2. Selecciona la version anterior
3. Pulsa **Rollback**

---

## Fase 9: Monitorizacion

### 9.1 Logs

En Dokploy, accede a los logs de la app para ver errores en tiempo real.

### 9.2 Healthcheck

Crea un script de verificacion (ver `scripts/healthcheck.sh` en el repo):

```bash
# Verificar que la app responde
curl -sf https://hostalrivera.com/ > /dev/null && echo "OK" || echo "FALLO"

# Verificar SSL
echo | openssl s_client -connect hostalrivera.com:443 2>/dev/null | openssl x509 -noout -dates

# Verificar espacio en disco
df -h / | awk 'NR==2 {print "Disco: " $5 " usado"}'

# Verificar que PostgreSQL responde
docker exec <contenedor-postgres> pg_isready
```

### 9.3 Uptime Kuma (opcional)

Puedes instalar Uptime Kuma como otro servicio en Dokploy para monitorizar:
- Disponibilidad HTTP/HTTPS
- Expiracion de certificado SSL
- Tiempo de respuesta

---

## Fase 10: Seguridad operativa

### Checklist mensual

- [ ] `apt update && apt upgrade` en la VM
- [ ] Revisar logs de fail2ban (`sudo fail2ban-client status sshd`)
- [ ] Verificar backups y hacer prueba de restauracion
- [ ] Ejecutar `python manage.py check --deploy`
- [ ] Revisar usuarios admin en Django y Dokploy
- [ ] Verificar espacio en disco (`df -h`)
- [ ] Comprobar estado del UPS (`upsc salicru1200@localhost`)
- [ ] Actualizar imagen base del Dockerfile si hay nueva version de Python

### Checklist trimestral

- [ ] Rotar `SECRET_KEY` (requiere que todos los usuarios vuelvan a login)
- [ ] Rotar contrasena de PostgreSQL
- [ ] Rotar credenciales de backup offsite
- [ ] Revisar politica de retencion de backups
- [ ] Verificar que el shutdown del UPS funciona (prueba simulada)

---

## Troubleshooting

### Error: DisallowedHost
- Anade el dominio a `ALLOWED_HOSTS` en las variables de entorno de Dokploy

### Error: CSRF verification failed
- Anade `https://tu-dominio.com` a `CSRF_TRUSTED_ORIGINS`

### SSL no se genera
- Verifica que los puertos 80/443 estan abiertos en el router
- Verifica que Cloudflare no esta bloqueando la validacion
- Revisa logs de Traefik en Dokploy

### La app no arranca
- Revisa logs en Dokploy
- Verifica que PostgreSQL esta corriendo
- Ejecuta `python manage.py check` en la consola del contenedor

### Archivos media desaparecen
- Verifica que el volumen persistente esta montado en `/app/media`
- Si no hay volumen, los archivos se pierden al recrear el contenedor

### Redireccion HTTPS infinita
- Verifica que `BEHIND_PROXY=True` esta configurado
- Verifica que Dokploy/Traefik envia el header `X-Forwarded-Proto: https`

---

## Resumen de archivos del proyecto

| Archivo | Funcion |
|---|---|
| `Dockerfile` | Imagen Docker de la app Django |
| `.dockerignore` | Archivos excluidos del build Docker |
| `scripts/nut-shutdown.sh` | Configuracion NUT para UPS Salicru |
| `scripts/backup-offsite.sh` | Backup offsite con rclone |
| `scripts/gdpr-cleanup.sh` | Limpieza de datos de viajeros (GDPR) |
| `scripts/healthcheck.sh` | Verificacion post-deploy |
| `docker-compose.local.yml` | Stack local para desarrollo (no produccion) |
| `.env.example` | Plantilla de variables para testing local |
