import json
from datetime import date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.http import url_has_allowed_host_and_scheme
from django_ratelimit.decorators import ratelimit
from .models import Habitacion, Cliente, Reserva, MenuDelDia, MenuEspecial, ConsentimientoRGPD, RegistroAuditoria
from .forms import (ClienteRegistroForm, ReservaForm, RegistroUsuarioForm, EditarUsuarioForm,
                    EditarClienteForm, CambiarPasswordForm, MenuDelDiaForm, PlatoFormSet,
                    MenuEspecialForm, PlatoMenuEspecialFormSet, CheckinReservaForm,
                    get_viajero_checkin_formset, ConsentimientoRGPDForm, CheckinPresencialForm,
                    EjercicioDerechosForm)
from .services.ses_hospedajes import build_payload, send_payload, registrar_envio


def home(request):
    """Vista principal - Página de inicio."""
    habitaciones_destacadas = Habitacion.objects.all()[:3]

    context = {
        'habitaciones': habitaciones_destacadas,
        'titulo': 'Bienvenido a nuestro Hotel'
    }

    return render(request, 'reservas/home.html', context)


def listado_habitaciones(request):
    """Vista de listado de habitaciones disponibles."""
    habitaciones = Habitacion.objects.all()

    # Filtros opcionales con sanitización
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
        'tipos': Habitacion.TIPO_CHOICES,
    }

    return render(request, 'reservas/listado_habitaciones.html', context)


def detalle_habitacion(request, id):
    """Vista de detalle de una habitación específica."""
    habitacion = get_object_or_404(Habitacion, id=id)

    context = {
        'habitacion': habitacion,
    }

    return render(request, 'reservas/detalle_habitacion.html', context)


@ratelimit(key='ip', rate='3/h', method='POST', block=True)
def registro_cliente(request):
    """
    Vista para registro de nuevos clientes.
    Rate limit: 3 registros por hora por IP (previene spam).
    """
    if request.method == 'POST':
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


@login_required
@ratelimit(key='user', rate='10/h', method='POST', block=True)
def crear_reserva(request, habitacion_id):
    """
    Vista para crear una nueva reserva.
    Rate limit: 10 reservas por hora por usuario.
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
                reserva = form.save(commit=False)
                reserva.habitacion = habitacion
                reserva.cliente = cliente
                reserva.save()

                messages.success(
                    request,
                    f'¡Reserva creada! Código: {reserva.codigo_reserva}'
                )
                messages.info(
                    request,
                    'Puedes completar el check-in online ahora o registrarte presencialmente en recepción.'
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


@login_required
# Solo el titular de la reserva o staff pueden ver sus detalles
def detalle_reserva(request, id):  # pylint: disable=redefined-builtin
    """Vista de detalle de reserva."""
    reserva = get_object_or_404(
        Reserva.objects.select_related('habitacion', 'cliente'),
        id=id
    )
    if reserva.cliente.usuario != request.user and not request.user.is_staff:
        return HttpResponseForbidden('No tienes permiso para ver esta reserva.')

    context = {'reserva': reserva}
    return render(request, 'reservas/detalle_reserva.html', context)


@login_required
def checkin_online_reserva(request, id):  # pylint: disable=redefined-builtin
    """Check-in online legal de viajeros para una reserva existente."""
    reserva = get_object_or_404(
        Reserva.objects.select_related('habitacion', 'cliente'),
        id=id, cliente__usuario=request.user
    )

    if reserva.checkin_online_omitido:
        messages.warning(request, 'Ya omitiste el check-in online. Contacta con recepción para registrarte presencialmente.')
        return redirect('detalle_reserva', id=reserva.id)

    min_viajeros_requeridos = max(1, reserva.numero_adultos)
    viajeros_existentes = reserva.viajeros_checkin.count()
    formset_cls = get_viajero_checkin_formset(extra=max(0, min_viajeros_requeridos - viajeros_existentes))

    if request.method == 'POST':
        reserva_form = CheckinReservaForm(request.POST, instance=reserva)
        formset = formset_cls(request.POST, instance=reserva, prefix='viajeros')
        consentimiento_form = ConsentimientoRGPDForm(request.POST)

        if reserva_form.is_valid() and formset.is_valid() and consentimiento_form.is_valid():
            viajeros_validos = [
                f for f in formset.forms
                if f.cleaned_data and not f.cleaned_data.get('DELETE', False)
            ]
            if len(viajeros_validos) < min_viajeros_requeridos:
                messages.error(
                    request,
                    f'Debes completar al menos {min_viajeros_requeridos} viajero(s) adulto(s) para esta reserva.'
                )
            else:
                reserva = reserva_form.save(commit=False)
                reserva.checkin_online_completado = True
                reserva.save()
                formset.save()

                consentimiento_form.save(
                    reserva=reserva,
                    cliente=reserva.cliente,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )

                RegistroAuditoria.objects.create(
                    usuario=request.user,
                    tipo_accion='consentimiento',
                    entidad_tipo='reserva',
                    entidad_id=reserva.id,
                    descripcion='Check-in online completado con consentimiento RGPD',
                    ip_address=request.META.get('REMOTE_ADDR')
                )

                messages.success(request, 'Check-in online completado correctamente.')
                return redirect('detalle_reserva', id=reserva.id)
        else:
            messages.error(request, 'Revisa los errores del check-in online.')
    else:
        reserva_form = CheckinReservaForm(instance=reserva)
        formset = formset_cls(instance=reserva, prefix='viajeros')
        consentimiento_form = ConsentimientoRGPDForm()

    return render(request, 'reservas/checkin_online.html', {
        'reserva': reserva,
        'reserva_form': reserva_form,
        'formset': formset,
        'consentimiento_form': consentimiento_form,
        'min_viajeros_requeridos': min_viajeros_requeridos,
    })


@login_required
@ratelimit(key='user', rate='5/h', method='POST', block=True)
def omitir_checkin_online(request, id):  # pylint: disable=redefined-builtin
    """Permite al huésped omitir el check-in online y registrarse presencialmente."""
    if request.method != 'POST':
        return redirect('detalle_reserva', id=id)

    reserva = get_object_or_404(
        Reserva.objects.select_related('habitacion', 'cliente'),
        id=id, cliente__usuario=request.user
    )

    if reserva.checkin_online_completado:
        messages.info(request, 'El check-in ya fue completado.')
        return redirect('detalle_reserva', id=reserva.id)

    reserva.checkin_online_omitido = True
    reserva.save()

    RegistroAuditoria.objects.create(
        usuario=request.user,
        tipo_accion='modificacion',
        entidad_tipo='reserva',
        entidad_id=reserva.id,
        descripcion='Check-in online omitido por el huésped',
        ip_address=request.META.get('REMOTE_ADDR')
    )

    messages.warning(request, 'Has omitido el check-in online. Deberás registrarte presencialmente en recepción con tu documentación.')
    return redirect('detalle_reserva', id=reserva.id)


@login_required
@ratelimit(key='user', rate='120/h', method='GET', block=True)
def mis_reservas(request):
    """Vista para que el cliente vea sus reservas."""
    try:
        cliente = request.user.cliente
        reservas = (
            Reserva.objects.filter(cliente=cliente)
            .select_related('habitacion')
            .order_by('-fecha_reserva')
        )
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
    Rate limit: 5 intentos por minuto (previene brute force).
    """
    if request.method == 'POST':
        # Sanitizar inputs
        username = strip_tags(request.POST.get('username', '').strip())
        password = request.POST.get('password', '')  # No sanitizar password

        # Validar que no estén vacíos
        if not username or not password:
            messages.error(request, 'Por favor completa todos los campos.')
            return render(request, 'reservas/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            # Redirigir a la página que intentaba acceder o al home
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):
                return redirect(next_url)
            return redirect('home')

        messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'reservas/login.html')


def logout_view(request):
    """Vista de cierre de sesión."""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('home')


def robots_txt(request):
    """
    Vista para servir robots.txt dinámico.
    SEO: indica a los buscadores qué URLs pueden indexar.
    """
    return render(request, 'robots.txt', {
        'sitemap_url': request.build_absolute_uri(reverse('sitemap_xml'))
    }, content_type='text/plain')


def sitemap_xml(request):
    """
    Vista para generar sitemap.xml dinámico.
    SEO: XML Sitemap para indexación en buscadores.
    """
    habitaciones = Habitacion.objects.all()
    hoy = date.today().isoformat()

    urls = [
        {
            'loc': request.build_absolute_uri('/'),
            'lastmod': hoy,
            'changefreq': 'daily',
            'priority': '1.0',
        },
        {
            'loc': request.build_absolute_uri(reverse('listado_habitaciones')),
            'lastmod': hoy,
            'changefreq': 'weekly',
            'priority': '0.9',
        },
        {
            'loc': request.build_absolute_uri(reverse('menu_del_dia')),
            'lastmod': hoy,
            'changefreq': 'daily',
            'priority': '0.8',
        },
    ]

    for habitacion in habitaciones:
        urls.append({
            'loc': request.build_absolute_uri(
                reverse('detalle_habitacion', args=[habitacion.id])
            ),
            'lastmod': habitacion.fecha_actualizacion.date().isoformat(),
            'changefreq': 'monthly',
            'priority': '0.7',
        })

    urls.extend([
        {
            'loc': request.build_absolute_uri(reverse('registro_cliente')),
            'lastmod': hoy,
            'changefreq': 'yearly',
            'priority': '0.5',
        },
        {
            'loc': request.build_absolute_uri(reverse('politica_privacidad')),
            'lastmod': hoy,
            'changefreq': 'yearly',
            'priority': '0.3',
        },
    ])

    return render(request, 'sitemap.xml', {'urls': urls}, content_type='application/xml')


# PÁGINAS LEGALES (RGPD, LSSI-CE)

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
    """Vista para la página de la Vía Künig."""
    return render(request, 'reservas/via_kunig.html')


def menu_del_dia(request):
    """Muestra el menú del día y los menús especiales activos hoy."""
    hoy = date.today()

    menu = MenuDelDia.objects.prefetch_related('platos').first()
    if menu and menu.fecha != hoy:
        menu.fecha = hoy
        menu.save(update_fields=['fecha'])

    if menu and not menu.activo:
        menu = None

    primeros, segundos, postres = [], [], []
    if menu:
        primeros = menu.platos.filter(categoria='primero', disponible=True).order_by('orden', 'nombre')
        segundos = menu.platos.filter(categoria='segundo', disponible=True).order_by('orden', 'nombre')
        postres  = menu.platos.filter(categoria='postre',  disponible=True).order_by('orden', 'nombre')

    especiales = (
        MenuEspecial.objects
        .filter(activo=True, fecha_inicio__lte=hoy, fecha_fin__gte=hoy)
        .prefetch_related('platos')
        .order_by('fecha_inicio')
    )

    return render(request, 'reservas/menu_del_dia.html', {
        'menu': menu,
        'primeros': primeros,
        'segundos': segundos,
        'postres': postres,
        'especiales': especiales,
    })


@login_required
@ratelimit(key='user', rate='30/h', method='POST', block=True)
def editar_menu_del_dia(request):
    """Panel de edición del menú del día — solo para staff."""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para editar el menú del día.')
        return redirect('menu_del_dia')

    menu = MenuDelDia.objects.first()
    if not menu:
        menu = MenuDelDia.objects.create(activo=True)

    if menu.fecha != date.today():
        menu.fecha = date.today()
        menu.save(update_fields=['fecha'])

    if request.method == 'POST':
        form = MenuDelDiaForm(request.POST, instance=menu)
        formset = PlatoFormSet(request.POST, instance=menu, prefix='platos')

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Menú del día actualizado correctamente.')
            return redirect('menu_del_dia')
        else:
            messages.error(request, 'Revisa los errores del formulario.')
    else:
        form = MenuDelDiaForm(instance=menu)
        formset = PlatoFormSet(instance=menu, prefix='platos')

    return render(request, 'reservas/editar_menu_del_dia.html', {
        'form': form,
        'formset': formset,
        'menu': menu,
    })


@login_required
@ratelimit(key='user', rate='30/h', method='POST', block=True)
def crear_editar_menu_especial(request, pk=None):
    """Crear (pk=None) o editar (pk=id) un menú especial — solo staff."""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para gestionar menús especiales.')
        return redirect('menu_del_dia')

    especial = get_object_or_404(MenuEspecial, pk=pk) if pk else None
    es_nuevo = especial is None

    if request.method == 'POST':
        form = MenuEspecialForm(request.POST, instance=especial)
        formset = PlatoMenuEspecialFormSet(request.POST, instance=especial or MenuEspecial(), prefix='platos')

        if form.is_valid():
            especial = form.save()
            formset = PlatoMenuEspecialFormSet(request.POST, instance=especial, prefix='platos')
            if formset.is_valid():
                formset.save()
                accion = 'creado' if es_nuevo else 'actualizado'
                messages.success(request, f'Menú especial {accion} correctamente.')
                return redirect('menu_del_dia')
            else:
                messages.error(request, 'Revisa los errores en los platos.')
        else:
            messages.error(request, 'Revisa los errores del formulario.')
    else:
        form = MenuEspecialForm(instance=especial)
        formset = PlatoMenuEspecialFormSet(instance=especial or MenuEspecial(), prefix='platos')

    return render(request, 'reservas/editar_menu_especial.html', {
        'form': form,
        'formset': formset,
        'especial': especial,
        'es_nuevo': es_nuevo,
    })


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
@ratelimit(key='user', rate='10/h', method='POST', block=True)
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
                    messages.success(request, 'Contraseña cambiada correctamente.')
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
                messages.success(request, 'Perfil actualizado correctamente.')
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


@login_required
def detalle_reserva_staff(request, id):  # pylint: disable=redefined-builtin
    """Vista de detalle de reserva para staff."""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('home')

    reserva = get_object_or_404(
        Reserva.objects.select_related('habitacion', 'cliente'),
        id=id
    )
    viajeros = reserva.viajeros_checkin.all().order_by('orden')
    consentimientos = reserva.consentimientos_rgpd.all().order_by('-fecha_consentimiento')

    context = {
        'reserva': reserva,
        'viajeros': viajeros,
        'consentimientos': consentimientos,
    }
    return render(request, 'reservas/detalle_reserva_staff.html', context)


@login_required
@ratelimit(key='user', rate='30/h', method='POST', block=True)
def checkin_presencial_staff(request, id):  # pylint: disable=redefined-builtin
    """Check-in presencial realizado por staff para huéspedes que no hicieron check-in online."""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('home')

    reserva = get_object_or_404(
        Reserva.objects.select_related('habitacion', 'cliente'),
        id=id
    )

    if reserva.checkin_online_completado:
        messages.info(request, 'El check-in ya fue completado.')
        return redirect('detalle_reserva_staff', id=reserva.id)

    min_viajeros_requeridos = max(1, reserva.numero_adultos)
    viajeros_existentes = reserva.viajeros_checkin.count()
    formset_cls = get_viajero_checkin_formset(extra=max(0, min_viajeros_requeridos - viajeros_existentes))

    if request.method == 'POST':
        reserva_form = CheckinPresencialForm(request.POST, instance=reserva)
        formset = formset_cls(request.POST, instance=reserva, prefix='viajeros')

        if reserva_form.is_valid() and formset.is_valid():
            viajeros_validos = [
                f for f in formset.forms
                if f.cleaned_data and not f.cleaned_data.get('DELETE', False)
            ]
            if len(viajeros_validos) < min_viajeros_requeridos:
                messages.error(
                    request,
                    f'Debes completar al menos {min_viajeros_requeridos} viajero(s) adulto(s) para esta reserva.'
                )
            else:
                reserva = reserva_form.save(commit=False)
                reserva.checkin_online_completado = True
                reserva.save()
                formset.save()

                ConsentimientoRGPD.objects.create(
                    reserva=reserva,
                    cliente=reserva.cliente,
                    texto_consentimiento='Consentimiento físico firmado en recepción',
                    version_politica='1.0',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )

                RegistroAuditoria.objects.create(
                    usuario=request.user,
                    tipo_accion='consentimiento',
                    entidad_tipo='reserva',
                    entidad_id=reserva.id,
                    descripcion='Check-in presencial completado por staff con consentimiento físico',
                    ip_address=request.META.get('REMOTE_ADDR')
                )

                messages.success(request, 'Check-in presencial completado correctamente.')
    return redirect('detalle_reserva_staff', id=reserva.id)


@login_required
@ratelimit(key='user', rate='20/h', method='POST', block=True)
def derechos_rgpd_cliente(request, cliente_id):
    """Vista para que el staff gestione solicitudes de derechos RGPD de un cliente."""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('home')

    cliente = get_object_or_404(Cliente, id=cliente_id)
    consentimientos = cliente.consentimientos_rgpd.all().order_by('-fecha_consentimiento')
    reservas = cliente.reservas.all().order_by('-fecha_reserva')

    if request.method == 'POST':
        form = EjercicioDerechosForm(request.POST)
        accion = request.POST.get('accion')

        if form.is_valid():
            tipo_derecho = form.cleaned_data['tipo_derecho']
            descripcion = form.cleaned_data['descripcion']

            if accion == 'exportar':
                RegistroAuditoria.objects.create(
                    usuario=request.user,
                    tipo_accion='ejercicio_derechos',
                    entidad_tipo='cliente',
                    entidad_id=cliente.id,
                    descripcion=f'Exportación de datos - Derecho: {tipo_derecho}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, f'Datos exportados correctamente. Derecho: {tipo_derecho}')

            elif accion == 'anonimizar':
                cliente.nombre = 'ANONIMIZADO'
                cliente.apellidos = 'ANONIMIZADO'
                cliente.dni_nie = 'ANONIMIZADO'
                cliente.email = 'anonimizado@example.com'
                cliente.telefono = 'ANONIMIZADO'
                cliente.direccion = 'ANONIMIZADO'
                cliente.save()

                RegistroAuditoria.objects.create(
                    usuario=request.user,
                    tipo_accion='ejercicio_derechos',
                    entidad_tipo='cliente',
                    entidad_id=cliente.id,
                    descripcion=f'Anonimización de datos - Derecho: {tipo_derecho}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, 'Datos del cliente anonimizados correctamente.')

            elif accion == 'rectificar':
                RegistroAuditoria.objects.create(
                    usuario=request.user,
                    tipo_accion='ejercicio_derechos',
                    entidad_tipo='cliente',
                    entidad_id=cliente.id,
                    descripcion=f'Rectificación solicitada - Derecho: {tipo_derecho}. Descripción: {descripcion}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, f'Rectificación registrada. Descripción: {descripcion}')

            return redirect('derechos_rgpd_cliente', cliente_id=cliente.id)
    else:
        form = EjercicioDerechosForm()

    context = {
        'cliente': cliente,
        'consentimientos': consentimientos,
        'reservas': reservas,
        'form': form,
    }
    return render(request, 'reservas/derechos_rgpd.html', context)


@login_required
@ratelimit(key='user', rate='60/h', method='GET', block=True)
def historial_auditoria(request):
    """Vista para que el staff consulte el historial de auditoría."""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('home')

    registros = RegistroAuditoria.objects.all().order_by('-fecha_accion')

    tipo_accion = request.GET.get('tipo_accion')
    if tipo_accion:
        registros = registros.filter(tipo_accion=tipo_accion)

    entidad_tipo = request.GET.get('entidad_tipo')
    if entidad_tipo:
        registros = registros.filter(entidad_tipo=entidad_tipo)

    usuario_id = request.GET.get('usuario')
    if usuario_id:
        registros = registros.filter(usuario_id=usuario_id)

    fecha_desde = request.GET.get('fecha_desde')
    if fecha_desde:
        registros = registros.filter(fecha_accion__date__gte=fecha_desde)

    fecha_hasta = request.GET.get('fecha_hasta')
    if fecha_hasta:
        registros = registros.filter(fecha_accion__date__lte=fecha_hasta)

    from django.core.paginator import Paginator
    paginator = Paginator(registros, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'tipo_accion': tipo_accion,
        'entidad_tipo': entidad_tipo,
        'usuario_id': usuario_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'TIPO_ACCION_CHOICES': RegistroAuditoria.TIPO_ACCION_CHOICES,
        'ENTIDAD_TIPO_CHOICES': RegistroAuditoria.ENTIDAD_TIPO_CHOICES,
    }
    return render(request, 'reservas/historial_auditoria.html', context)


@login_required
@ratelimit(key='user', rate='10/h', method='POST', block=True)
def enviar_ses_hospedajes(request, id):  # pylint: disable=redefined-builtin
    """Envía los datos de la reserva a SES Hospedajes."""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta sección.')
        return redirect('home')

    if request.method != 'POST':
        return redirect('detalle_reserva_staff', id=id)

    reserva = get_object_or_404(
        Reserva.objects.select_related('habitacion', 'cliente'),
        id=id
    )

    if not reserva.checkin_online_completado:
        messages.error(request, 'El check-in debe estar completado antes de enviar a SES Hospedajes.')
        return redirect('detalle_reserva_staff', id=reserva.id)

    if reserva.ses_hospedajes_enviado:
        messages.info(request, 'Los datos ya fueron enviados a SES Hospedajes.')
        return redirect('detalle_reserva_staff', id=reserva.id)

    try:
        payload = build_payload(reserva)
        resultado = send_payload(payload)
        registrar_envio(
            reserva,
            resultado['exito'],
            resultado['referencia'],
            resultado['error']
        )

        if resultado['exito']:
            messages.success(request, f'Datos enviados a SES Hospedajes. Referencia: {resultado["referencia"]}')
        else:
            messages.error(request, f'Error enviando a SES Hospedajes: {resultado["error"]}')

    except Exception as e:
        messages.error(request, f'Error inesperado: {str(e)}')

    return redirect('detalle_reserva_staff', id=reserva.id)
