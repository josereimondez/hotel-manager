"""
URL configuration for hotel_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include  # 👈 Añadir include
from django.conf import settings  # 👈 Nuevo
from django.conf.urls.static import static  # 👈 Nuevo
from django.conf.urls.i18n import i18n_patterns  # 🌍 i18n
from django.views.i18n import set_language  # 🌍 set_language view
from decouple import config


ADMIN_PATH = config('ADMIN_PATH', default='admin/').strip('/') + '/'

urlpatterns = [
    path(ADMIN_PATH, admin.site.urls),
    path('i18n/set_language/', set_language, name='set_language'),  # 🌍 Cambiar idioma
]

# 🌍 URLs con soporte multiidioma
urlpatterns += i18n_patterns(
    path('', include('reservas.urls')),  # 👈 Incluir URLs de reservas
    prefix_default_language=False,  # No agregar /es/ para español por defecto
)

# 🎓 CONCEPTO: Servir archivos media y static en desarrollo
# En producción se usa NGINX o S3
if settings.DEBUG:  # 🐍 Solo en desarrollo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
