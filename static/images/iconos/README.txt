CARPETA: Iconos e imágenes decorativas
=======================================
Coloca aquí iconos, ilustraciones y pequeñas imágenes decorativas.

Ejemplos:
  - icono-wifi.png
  - icono-parking.png
  - icono-restaurante.png
  - decoracion-camino.svg    → para la página Vía Künig
  - mapa-becerrea.jpg

Tamaño recomendado : menos de 100 x 100 px para iconos
Formatos aceptados : PNG (con transparencia), SVG, WEBP

Ejemplo de uso en una plantilla Django:
  {% load static %}
  <img src="{% static 'images/iconos/icono-wifi.png' %}" alt="Wi-Fi gratuito" width="32">
