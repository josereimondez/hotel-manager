# Hostal Rivera

Sistema de gestion para Hostal Rivera, un alojamiento con restaurante ubicado en Becerrea (Lugo), en el corazon de la Comarca de Los Ancares, Galicia.

## Sobre el proyecto

Hostal Rivera es un hostal familiar situado en Becerrea, un municipio de la provincia de Lugo atravesado por la Via Kunig, un camino historico vinculado al Camino de Santiago. El establecimiento ofrece alojamiento y restaurante con cocina gallega tradicional, atendiendo a viajeros, senderistas, trabajadores en ruta y familias que recorren la zona.

Este sistema cubre las necesidades operativas del hostal: gestion de habitaciones, reservas online con prevencion de doble reserva, check-in online con cumplimiento de la normativa SES Hospedajes (reporte obligatorio a la Policia Nacional), menu del dia del restaurante, y multiidioma (espanol, galego, ingles) para la clientela internacional.

## Funcionalidades

- Reservas online con calendario de disponibilidad en tiempo real y bloqueo de fechas ocupadas
- Check-in online con validacion de DNI/NIE mediante algoritmo oficial espanol
- Gestion de menu del dia y menus especiales para el restaurante
- Perfiles de cliente con historial de reservas
- Panel de administracion Django para gestion de habitaciones, reservas y clientes
- Multiidioma: espanol (por defecto), galego e ingles
- Cumplimiento RGPD, LSSI-CE y LOPDGDD
- Sanitizacion de inputs, rate limiting en endpoints POST, gestion segura de credenciales via variables de entorno

## Stack tecnologico

- **Backend**: Python 3.11-3.13 con Django 5.2 LTS
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (produccion)
- **Frontend**: Django Templates + Bootstrap 5 (CDN)
- **Librerias principales**: python-decouple, django-crispy-forms, crispy-bootstrap5, reportlab, openpyxl, Pillow, python-stdnum, django-ratelimit, Flatpickr

## Instalacion

```bash
git clone https://github.com/reiloop/hotel-manager.git
cd hotel-manager
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
# Editar .env con valores seguros (SECRET_KEY, DEBUG=True para desarrollo)
python compile_mo.py
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Accede a: http://127.0.0.1:8000/

## Estructura del proyecto

```
hotel-manager/
├── hotel_project/          # Configuracion Django
│   ├── settings.py        # Configuracion principal (usa .env)
│   ├── urls.py            # URLs principales
│   └── wsgi.py
├── reservas/              # App principal
│   ├── models.py         # 7+ modelos: Cliente, Habitacion, Reserva, ViajeroCheckin, MenuDelDia, etc.
│   ├── views.py          # Vistas y logica de negocio
│   ├── forms.py          # Formularios de registro, reserva, perfil
│   ├── admin.py          # Panel administrativo
│   ├── urls.py           # URLs de la app
│   └── templates/        # Plantillas HTML
├── static/               # Archivos estaticos (logo, background)
├── locale/               # Traducciones (ES, GL, EN)
├── .env.example          # Plantilla de variables de entorno
├── requirements.txt      # Dependencias Python
├── compile_mo.py         # Script para compilar traducciones
└── manage.py             # CLI de Django
```

## Internacionalizacion

El proyecto soporta 3 idiomas: espanol (por defecto), galego e ingles. Las URLs usan `i18n_patterns` sin prefijo para el idioma por defecto.

Para editar traducciones:
1. Editar los archivos `.po` en `locale/[idioma]/LC_MESSAGES/django.po`
2. Ejecutar `python manage.py compilemessages` (o `python compile_mo.py` como fallback)
3. Commitear `.po` y `.mo` juntos

## Seguridad

- Variables de entorno gestionadas con `python-decouple`
- `SECRET_KEY` aleatoria (50+ caracteres), `DEBUG=False` en produccion
- `strip_tags()` en todos los inputs de usuario
- Validacion de DNI/NIE con `python-stdnum`
- Rate limiting con `django-ratelimit` en endpoints POST
- Proteccion CSRF, XSS, SQL injection (ORM Django), HSTS, cookies seguras
- Ses Hospedajes: campos y flujos documentados en `GUIA_SES_HOSPEDAJES_CHECKIN.md`

## Despliegue

Ver `DEPLOYMENT.md` y `dokploy.md` para guias de despliegue en produccion (Gunicorn + WhiteNoise + PostgreSQL).

## Contribuciones

Las contribuciones son bienvenidas. Ver `CONTRIBUTING.md` para la guia completa.

## Licencia

Codigo abierto bajo licencia MIT.

## Contacto

Hostal Rivera - Becerrea, Lugo, Galicia
Telefono: +34 982 360 185
Email: info@hostalrivera.es
