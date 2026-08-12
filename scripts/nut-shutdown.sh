#!/bin/bash
#
# Configuracion NUT para UPS Salicru 1200 en Proxmox
# Ejecutar como root en el host Proxmox
#
# Referencia: https://networkupstools.org/docs/user-manual.html
# Driver blazer_usb es compatible con la mayoria de Salicru SPS
#

set -e

echo "=== Configuracion NUT para Salicru 1200 ==="

# Verificar que se ejecuta como root
if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: Este script debe ejecutarse como root"
    exit 1
fi

# Verificar que el UPS esta conectado
echo "[1/6] Verificando conexion USB del UPS..."
if ! lsusb | grep -qi "salicru\|0665\|0764"; then
    echo "ADVERTENCIA: No se detecta el UPS por USB."
    echo "Verifica la conexion USB y ejecuta 'lsusb' para identificar el dispositivo."
    echo ""
    echo "IDs comunes de Salicru:"
    echo "  0665:5161 - Salicru SPS (blazer_usb)"
    echo "  0764:0501 - Salicru (blazer_usb)"
    echo ""
    read -p "Continuar de todas formas? (s/N): " continuar
    if [ "$continuar" != "s" ] && [ "$continuar" != "S" ]; then
        exit 1
    fi
fi

# Instalar NUT
echo "[2/6] Instalando NUT..."
apt update
apt install -y nut

# Configurar modo standalone
echo "[3/6] Configurando nut.conf..."
cat > /etc/nut/nut.conf << 'EOF'
MODE=standalone
EOF

# Configurar el UPS
echo "[4/6] Configurando ups.conf..."
cat > /etc/nut/ups.conf << 'EOF'
[salicru1200]
    driver = blazer_usb
    port = auto
    desc = "Salicru SPS 1200"
    # Descomenta y ajusta segun tu modelo:
    # vendorid = 0665
    # productid = 5161
    # productid = 0501
EOF

echo "[5/6] Configurando usuarios y monitor..."

# Generar contrasena aleatoria si no se proporciona
if [ -z "$NUT_PASSWORD" ]; then
    NUT_PASSWORD=$(openssl rand -base64 24)
    echo ""
    echo "================================================"
    echo " CONTRASENA NUT GENERADA (GUARDARLA):"
    echo " $NUT_PASSWORD"
    echo "================================================"
    echo ""
fi

cat > /etc/nut/upsd.conf << 'EOF'
LISTEN 127.0.0.1 3493
EOF

cat > /etc/nut/upsd.users << EOF
[admin]
    password = ${NUT_PASSWORD}
    actions = SET
    instcmds = ALL
EOF

cat > /etc/nut/upsmon.conf << EOF
MONITOR salicru1200@localhost 1 admin ${NUT_PASSWORD} master
POWERDOWNFLAG /etc/killpower
SHUTDOWNCMD "/sbin/shutdown -h +0"
NOTIFYFLAG ONLINE       SYSLOG+WALL
NOTIFYFLAG ONBATT       SYSLOG+WALL
NOTIFYFLAG LOWBATT      SYSLOG+WALL
NOTIFYFLAG FSD          SYSLOG+WALL
NOTIFYFLAG COMMOK       SYSLOG+WALL
NOTIFYFLAG COMMBAD      SYSLOG+WALL
RBWARNTIME 43200
NOCOMMWARNTIME 600
FINALDELAY 5
EOF

# Configurar permisos
echo "[6/6] Configurando permisos y servicios..."
chmod 640 /etc/nut/upsd.users
chown root:nut /etc/nut/upsd.users
chmod 640 /etc/nut/upsmon.conf
chown root:nut /etc/nut/upsmon.conf

# Iniciar servicios
systemctl enable nut-server nut-monitor
systemctl restart nut-server nut-monitor

# Verificar
echo ""
echo "=== Verificacion ==="
sleep 2
if upsc salicru1200@localhost > /dev/null 2>&1; then
    echo "UPS conectado correctamente."
    echo ""
    echo "Informacion del UPS:"
    upsc salicru1200@localhost | grep -E "battery|runtime|ups.status|ups.load|input.voltage"
    echo ""
    echo "Shutdown automatico configurado."
    echo "La VM se apagara cuando la bateria este baja."
else
    echo "ERROR: No se pudo conectar al UPS."
    echo "Verifica:"
    echo "  1. Que el UPS esta conectado por USB"
    echo "  2. El driver correcto en /etc/nut/ups.conf"
    echo "  3. Los permisos del dispositivo USB"
    echo ""
    echo "Logs: journalctl -u nut-server -u nut-monitor --no-pager"
    exit 1
fi

echo ""
echo "=== Configuracion completada ==="
echo ""
echo "Comandos utiles:"
echo "  upsc salicru1200@localhost          # Ver estado del UPS"
echo "  upsc salicru1200@localhost ups.status  # Estado (OL=online, OB=bateria)"
echo "  upsmon -c fsd                       # Simular shutdown (SOLO PRUEBA)"
echo "  journalctl -u nut-server -f         # Ver logs en tiempo real"
