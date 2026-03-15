from django.urls import path
from . import views

# 🎓 CONCEPTO: URLpatterns = mapeo de URLs a vistas

urlpatterns = [
    # Página principal
    path('', views.home, name='home'),
    
    # 🔍 SEO: Sitemap y Robots
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    
    # Habitaciones
    path('habitaciones/', views.listado_habitaciones, name='listado_habitaciones'),
    path('habitaciones/<int:id>/', views.detalle_habitacion, name='detalle_habitacion'),
    path('habitaciones/<int:habitacion_id>/fechas-ocupadas/', views.fechas_ocupadas, name='fechas_ocupadas'),
    
    # Clientes
    path('registro/', views.registro_cliente, name='registro_cliente'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Reservas
    path('reservar/<int:habitacion_id>/', views.crear_reserva, name='crear_reserva'),
    path('reserva/<int:id>/', views.detalle_reserva, name='detalle_reserva'),
    path('reserva/<int:id>/checkin-online/', views.checkin_online_reserva, name='checkin_online_reserva'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    
    # 📋 Páginas Legales (RGPD, LSSI-CE)
    path('politica-privacidad/', views.politica_privacidad, name='politica_privacidad'),
    path('politica-cookies/', views.politica_cookies, name='politica_cookies'),
    path('terminos-condiciones/', views.terminos_condiciones, name='terminos_condiciones'),

    # SEO: Página sobre la Vía Künig
    path('via-kunig/', views.via_kunig, name='via_kunig'),

    # Restaurante
    path('menu-del-dia/', views.menu_del_dia, name='menu_del_dia'),
    path('menu-del-dia/editar/', views.editar_menu_del_dia, name='editar_menu_del_dia'),
    path('menu-especial/nuevo/', views.crear_editar_menu_especial, name='crear_menu_especial'),
    path('menu-especial/<int:pk>/editar/', views.crear_editar_menu_especial, name='editar_menu_especial'),

    # Perfil de usuario
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
]

# 🎓 EXPLICACIÓN:
# path('habitaciones/<int:id>/', ...)
#      ^           ^
#      |           |
#      URL         Parámetro que se pasa a la vista
#
# Ejemplo: /habitaciones/5/ → views.detalle_habitacion(request, id=5)
