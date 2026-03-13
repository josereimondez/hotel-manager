import json
from datetime import date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.http import JsonResponse
from django.utils.html import strip_tags
from django_ratelimit.decorators import ratelimit
from .models import Habitacion, Cliente, Reserva
from .forms import ClienteRegistroForm, ReservaForm, RegistroUsuarioForm, EditarUsuarioForm, EditarClienteForm, CambiarPasswordForm

# 🎓 CONCEPTO: Vistas = funciones que procesan requests y devuelven responses


def home(request):
    """
    Vista principal - Página de inicio.
    
    🐍 PYTHON QUE APRENDES:
    - Funciones con parámetros
    - Diccionarios (context)
    - render() para templates
    """
    habitaciones_destacadas = Habitacion.objects.all()[:3]  # 🐍 [:3] = primeras 3
    
    context = {
        'habitaciones': habitaciones_destacadas,
        'titulo': 'Bienvenido a nuestro Hotel'
    }
    
    return render(request, 'reservas/home.html', context)


def listado_habitaciones(request):
    """
    Vista de listado de habitaciones disponibles.
    
    🐍 PYTHON QUE APRENDES:
    - GET parameters (request.GET)
    - Filtros con Django ORM
    - Condicionales
    """
    habitaciones = Habitacion.objects.all()
    
    # 🔍 Filtros opcionales con sanitización
    tipo = strip_tags(request.GET.get('tipo', '').strip())
    precio_max = request.GET.get('precio_max', '')
    
    # Validar tipo contra opciones válidas
    if tipo:
        tipos_validos = [choice[0] for choice in Habitacion.TIPO_CHOICES]
        if tipo in tipos_validos:
            habitaciones = habitaciones.filter(tipo=tipo)
    
    # Validar precio_max es numérico
    if precio_max:
        try:
            precio_max = float(precio_max)
            if precio_max > 0:
                habitaciones = habitaciones.filter(precio_base__lte=precio_max)
        except (ValueError, TypeError):
            pass  # Ignorar si no es un número válido
    
    context = {
        'habitaciones': habitaciones,
        'tipos': Habitacion.TIPO_CHOICES,  # 🐍 Para el filtro
    }
    
    return render(request, 'reservas/listado_habitaciones.html', context)


def detalle_habitacion(request, id):
    """
    Vista de detalle de una habitación específica.
    
    🐍 PYTHON QUE APRENDES:
    - Parámetros en URLs
    - get_object_or_404 (manejo de errores)
    """
    habitacion = get_object_or_404(Habitacion, id=id)
    
    context = {
        'habitacion': habitacion,
    }
    
    return render(request, 'reservas/detalle_habitacion.html', context)


@ratelimit(key='ip', rate='3/h', method='POST', block=True)
def registro_cliente(request):
    """
    Vista para registro de nuevos clientes.
    
    🐍 PYTHON QUE APRENDES:
    - POST vs GET
    - Formularios Django
    - Redirecciones
    - Mensajes flash
    - Crear usuario y cliente simultáneamente
    Rate limit: 3 registros por hora por IP (previene spam)
    """
    if request.method == 'POST':  # 🐍 Si envió el formulario
        user_form = RegistroUsuarioForm(request.POST)
        cliente_form = ClienteRegistroForm(request.POST)
        
        if user_form.is_valid() and cliente_form.is_valid():
            try:
                # Crear usuario
                user = user_form.save(commit=False)
                user.set_password(user_form.cleaned_data['password'])
                user.save()
                
                # Crear cliente y vincular con usuario
                cliente = cliente_form.save(commit=False)
                cliente.usuario = user
                cliente.save()
                
                # Loguear automáticamente
                login(request, user)
                
                messages.success(request, '¡Registro exitoso! Ya puedes hacer reservas.')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'Error al registrar: {str(e)}')
                if user.id:  # Si se creó el usuario, eliminarlo
                    user.delete()
    else:  # GET - Mostrar formulario vacío
        user_form = RegistroUsuarioForm()
        cliente_form = ClienteRegistroForm()
    
    context = {
        'user_form': user_form,
        'cliente_form': cliente_form
    }
    return render(request, 'reservas/registro_cliente.html', context)


@login_required  # � Requiere estar logueado
@ratelimit(key='user', rate='10/h', method='POST', block=True)
def crear_reserva(request, habitacion_id):
    """
    Vista para crear una nueva reserva.
    
    🐍 PYTHON QUE APRENDES:
    - Formularios con instancia
    - Try-except
    - Validaciones
    - Decoradores (@login_required)
    Rate limit: 10 reservas por hora por usuario
    """
    habitacion = get_object_or_404(Habitacion, id=habitacion_id)
    
    # Obtener el cliente del usuario actual
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'Debes completar tu perfil de cliente primero.')
        return redirect('registro_cliente')
    
    if request.method == 'POST':
        form = ReservaForm(request.POST, habitacion=habitacion)
        
        if form.is_valid():
            try:
                reserva = form.save(commit=False)  # 🐍 No guardar todavía
                reserva.habitacion = habitacion
                reserva.cliente = cliente  # 🐍 Asignar cliente automáticamente
                reserva.save()  # 🐍 Ahora sí guardar
                
                messages.success(
                    request, 
                    f'¡Reserva creada! Código: {reserva.codigo_reserva}'
                )
                return redirect('detalle_reserva', id=reserva.id)
                
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        # Pre-rellenar con fechas ejemplo
        form = ReservaForm(
            initial={
                'fecha_entrada': date.today() + timedelta(days=1),
                'fecha_salida': date.today() + timedelta(days=4),
            },
            habitacion=habitacion
        )
    
    # Calcular fechas ocupadas para el calendario
    reservas_ocupadas = Reserva.objects.filter(
        habitacion=habitacion,
        estado__in=['confirmada', 'en_curso', 'pendiente']
    )
    rangos_ocupados = [
        {
            'from': r.fecha_entrada.strftime('%Y-%m-%d'),
            'to':   r.fecha_salida.strftime('%Y-%m-%d'),
        }
        for r in reservas_ocupadas
    ]

    context = {
        'form': form,
        'habitacion': habitacion,
        'cliente': cliente,
        'fechas_ocupadas_json': json.dumps(rangos_ocupados),
    }

    return render(request, 'reservas/crear_reserva.html', context)


@ratelimit(key='ip', rate='60/m', method='GET', block=True)
def fechas_ocupadas(request, habitacion_id):
    """
    API JSON: devuelve las fechas ocupadas de una habitación.
    Usado por Flatpickr para bloquear días en el calendario.
    Rate limit: 60 peticiones por minuto por IP.
    """
    habitacion = get_object_or_404(Habitacion, id=habitacion_id)
    reservas = Reserva.objects.filter(
        habitacion=habitacion,
        estado__in=['confirmada', 'en_curso', 'pendiente']
    )
    # Construir lista de rangos {from, to} para Flatpickr
    rangos = []
    for r in reservas:
        rangos.append({
            'from': r.fecha_entrada.strftime('%Y-%m-%d'),
            'to':   r.fecha_salida.strftime('%Y-%m-%d'),
        })
    return JsonResponse({'ocupadas': rangos})


def detalle_reserva(request, id):  # pylint: disable=redefined-builtin
    """
    Vista de detalle de reserva.
    """
    reserva = get_object_or_404(Reserva, id=id)
    
    context = {'reserva': reserva}
    return render(request, 'reservas/detalle_reserva.html', context)


@login_required  # 🔐 Requiere estar logueado
def mis_reservas(request):
    """
    Vista para que el cliente vea sus reservas.
    
    🐍 PYTHON QUE APRENDES:
    - Filtros complejos
    - Ordenamiento
    - Autenticación de usuarios
    """
    try:
        cliente = request.user.cliente
        # Solo mostrar las reservas del cliente actual
        reservas = Reserva.objects.filter(cliente=cliente).order_by('-fecha_reserva')
    except Cliente.DoesNotExist:
        messages.warning(request, 'Debes completar tu perfil de cliente.')
        return redirect('registro_cliente')
    
    context = {'reservas': reservas}
    return render(request, 'reservas/mis_reservas.html', context)


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@ratelimit(key='post:username', rate='5/m', method='POST', block=True)
def login_view(request):
    """
    Vista de inicio de sesión.
    
    🐍 PYTHON: Autenticación de usuarios
    Rate limit: 5 intentos por minuto (previene brute force)
    """
    if request.method == 'POST':
        # Sanitizar inputs
        username = strip_tags(request.POST.get('username', '').strip())
        password = request.POST.get('password', '')  # No sanitizar password
        
        # Validar que no estén vacíos
        if not username or not password:
            messages.error(request, 'Por favor completa todos los campos.')
            return render(request, 'reservas/login.html')
        
        # 🔒 authenticate() verifica usuario/contraseña
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # 🔒 Iniciar sesión
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            # Redirigir a la página que intentaba acceder o al home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)

        messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'reservas/login.html')


def logout_view(request):
    """
    Vista de cierre de sesión.
    
    🐍 PYTHON: logout() cierra la sesión del usuario
    """
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('home')


def sitemap_xml(request):
    """
    Vista para generar sitemap.xml dinámico.
    
    🔍 SEO: XML Sitemap para indexación en buscadores
    """
    habitaciones = Habitacion.objects.all()
    
    # Construir XML manualmente
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Home
    xml_content += '  <url>\n'
    xml_content += '    <loc>https://hostal-rivera-becerre.senderosdesconocidos.top/</loc>\n'
    xml_content += '    <lastmod>2026-03-03</lastmod>\n'
    xml_content += '    <changefreq>daily</changefreq>\n'
    xml_content += '    <priority>1.0</priority>\n'
    xml_content += '  </url>\n'
    
    # Listado de habitaciones
    xml_content += '  <url>\n'
    xml_content += '    <loc>https://hostal-rivera-becerre.senderosdesconocidos.top/habitaciones/</loc>\n'
    xml_content += '    <lastmod>2026-03-03</lastmod>\n'
    xml_content += '    <changefreq>weekly</changefreq>\n'
    xml_content += '    <priority>0.9</priority>\n'
    xml_content += '  </url>\n'
    
    # Cada habitación
    for habitacion in habitaciones:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>https://hostal-rivera-becerre.senderosdesconocidos.top/habitaciones/{habitacion.id}/</loc>\n'
        xml_content += f'    <lastmod>{habitacion.id}</lastmod>\n'
        xml_content += '    <changefreq>monthly</changefreq>\n'
        xml_content += '    <priority>0.8</priority>\n'
        xml_content += '  </url>\n'
    
    # Registro y login
    xml_content += '  <url>\n'
    xml_content += '    <loc>https://hostal-rivera-becerre.senderosdesconocidos.top/registro/</loc>\n'
    xml_content += '    <lastmod>2026-03-03</lastmod>\n'
    xml_content += '    <changefreq>yearly</changefreq>\n'
    xml_content += '    <priority>0.7</priority>\n'
    xml_content += '  </url>\n'
    
    xml_content += '</urlset>'
    
    return render(request, 'sitemap.xml', {'xml': xml_content}, content_type='application/xml')


# 📋 PÁGINAS LEGALES (RGPD, LSSI-CE)

def politica_privacidad(request):
    """
    Vista de la Política de Privacidad.
    Cumple con RGPD (Reglamento General de Protección de Datos).
    """
    return render(request, 'reservas/politica_privacidad.html')


def politica_cookies(request):
    """
    Vista de la Política de Cookies.
    Cumple con LSSI-CE (Ley de Servicios de la Sociedad de la Información).
    """
    return render(request, 'reservas/politica_cookies.html')


def terminos_condiciones(request):
    """
    Vista de Términos y Condiciones de uso.
    Define los derechos y obligaciones de los usuarios.
    """
    return render(request, 'reservas/terminos_condiciones.html')


def via_kunig(request):
    """
    Vista para la página de la Vía Künig.
    """
    return render(request, 'reservas/via_kunig.html')


@login_required
def mi_perfil(request):
    """
    Vista de perfil del usuario autenticado.
    Muestra sus datos y un resumen de reservas.
    """
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        cliente = None

    reservas = cliente.reservas.order_by('-fecha_reserva')[:5] if cliente else []

    return render(request, 'reservas/perfil.html', {
        'cliente': cliente,
        'reservas': reservas,
    })


@login_required
def editar_perfil(request):
    """
    Vista para editar los datos del perfil del usuario.
    Gestiona dos formularios a la vez: datos de cuenta y datos personales.
    También permite cambiar la contraseña.
    """
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        cliente = None

    if request.method == 'POST':
        accion = request.POST.get('accion', 'datos')

        if accion == 'password':
            password_form = CambiarPasswordForm(request.POST)
            user_form = EditarUsuarioForm(instance=request.user)
            cliente_form = EditarClienteForm(instance=cliente) if cliente else None

            if password_form.is_valid():
                actual = password_form.cleaned_data['password_actual']
                nueva = password_form.cleaned_data['password_nueva']
                if not request.user.check_password(actual):
                    password_form.add_error('password_actual', 'La contraseña actual no es correcta.')
                else:
                    request.user.set_password(nueva)
                    request.user.save()
                    update_session_auth_hash(request, request.user)  # Mantener sesión activa
                    messages.success(request, '✅ Contraseña cambiada correctamente.')
                    return redirect('mi_perfil')
        else:
            user_form = EditarUsuarioForm(request.POST, instance=request.user)
            cliente_form = EditarClienteForm(request.POST, instance=cliente) if cliente else None
            password_form = CambiarPasswordForm()

            forms_validos = user_form.is_valid()
            if cliente_form:
                forms_validos = forms_validos and cliente_form.is_valid()

            if forms_validos:
                user_form.save()
                if cliente_form:
                    cliente_form.save()
                messages.success(request, '✅ Perfil actualizado correctamente.')
                return redirect('mi_perfil')
    else:
        user_form = EditarUsuarioForm(instance=request.user)
        cliente_form = EditarClienteForm(instance=cliente) if cliente else None
        password_form = CambiarPasswordForm()

    return render(request, 'reservas/editar_perfil.html', {
        'user_form': user_form,
        'cliente_form': cliente_form,
        'password_form': password_form,
        'cliente': cliente,
    })
