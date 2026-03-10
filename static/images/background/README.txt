CARPETA: Fondo / Background del Hotel
======================================
Coloca aquí las imágenes de fondo o portada del hotel.

Nombres recomendados:
  - background-home.jpg     → fondo de la página principal
  - background-header.jpg   → cabecera de páginas interiores
  - fachada.jpg             → foto exterior del hostal

Tamaño recomendado : 1920 x 1080 px (o superior para que no pixele)
Formatos aceptados : JPG, WEBP (mejor rendimiento web)

Ejemplo de uso en una plantilla Django:
  {% load static %}
  <img src="{% static 'images/background/background-home.jpg' %}" alt="Hostal Rivera Becerreá">

O como fondo CSS:
  background-image: url("{% static 'images/background/background-home.jpg' %}");
