"""Tests de la aplicación de reservas.

Para ejecutar: python manage.py test reservas
"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.template.context import BaseContext
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Cliente, Habitacion, Reserva, ViajeroCheckin, MenuDelDia
from .forms import (
    RegistroUsuarioForm,
    ClienteRegistroForm,
    ReservaForm,
    CheckinReservaForm,
)

User = get_user_model()


# 🛠️ COMPATIBILIDAD: Python 3.14 cambia el comportamiento de copy() con super().
# Django 5.0.2 no soporta Python 3.14; este parche permite que el test client
# copie el contexto de templates sin fallar en el entorno local.
# En CI (Python 3.10-3.12) no es necesario y no tiene efecto negativo.
class _BaseContextCopyHelper:
    def __copy__(self):
        duplicate = self.__class__.__new__(self.__class__)
        # pylint: disable=attribute-defined-outside-init
        duplicate.dicts = self.dicts[:]
        return duplicate


BaseContext.__copy__ = _BaseContextCopyHelper.__copy__


# 🛠️ Configuración de almacenamiento de archivos estáticos para tests.
# CompressedManifestStaticFilesStorage requiere collectstatic; en tests usamos
# el backend simple para evitar errores de manifesto faltante.
STATICFILES_STORAGE_TEST = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


class _VistaTestCase(TestCase):
    """TestCase base para vistas que renderizan templates."""


VistaTestCase = override_settings(STORAGES=STATICFILES_STORAGE_TEST)(_VistaTestCase)


# ──────────────────────────────────────────────────────────────────────────────
# 🧪 TESTS DE MODELOS
# ──────────────────────────────────────────────────────────────────────────────

class ClienteModelTests(TestCase):
    """Tests para el modelo Cliente."""

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='cliente1', password='testpass123', email='cliente1@test.com'
        )
        self.cliente = Cliente.objects.create(
            usuario=self.usuario,
            nombre='Juan',
            apellidos='García López',
            dni_nie='12345678Z',
            email='cliente1@test.com',
            telefono='612345678',
            fecha_nacimiento=date(1990, 5, 15)
        )

    def test_str_devuelve_nombre_y_dni(self):
        self.assertEqual(str(self.cliente), 'Juan García López (12345678Z)')

    def test_nombre_completo(self):
        self.assertEqual(self.cliente.nombre_completo, 'Juan García López')

    def test_edad_calculada_correctamente(self):
        hoy = date.today()
        edad_esperada = hoy.year - 1990 - (
            (hoy.month, hoy.day) < (5, 15)
        )
        self.assertEqual(self.cliente.edad, edad_esperada)

    def test_dni_invalido_lanza_validationerror(self):
        cliente_malo = Cliente(
            nombre='Pepe', apellidos='Pérez', dni_nie='12345678A',
            email='pepe@test.com', telefono='612345678'
        )
        with self.assertRaises(ValidationError):
            cliente_malo.full_clean()

    def test_telefono_corto_lanza_validationerror(self):
        self.cliente.telefono = '123'
        with self.assertRaises(ValidationError):
            self.cliente.full_clean()


class HabitacionModelTests(TestCase):
    """Tests para el modelo Habitacion."""

    def setUp(self):
        self.habitacion = Habitacion.objects.create(
            numero='101',
            tipo='doble',
            precio_base=Decimal('80.00'),
            capacidad=2,
            tiene_vista_mar=False
        )

    def test_str_devuelve_numero_y_tipo(self):
        self.assertEqual(str(self.habitacion), 'Habitación 101 - Doble')

    def test_precio_con_vista_mar(self):
        self.habitacion.tiene_vista_mar = True
        self.assertEqual(self.habitacion.precio_con_vista(), Decimal('96.00'))

    def test_calcular_precio_estancia_con_descuento(self):
        # 10 noches => descuento del 10%
        total = self.habitacion.calcular_precio_estancia(10)
        self.assertEqual(total, Decimal('720.00'))  # 80*10*0.9

    def test_calcular_precio_estancia_sin_descuento(self):
        total = self.habitacion.calcular_precio_estancia(5)
        self.assertEqual(total, Decimal('400.00'))


class ReservaModelTests(TestCase):
    """Tests para el modelo Reserva."""

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='cliente2', password='testpass123', email='cliente2@test.com'
        )
        self.cliente = Cliente.objects.create(
            usuario=self.usuario,
            nombre='Ana',
            apellidos='Martínez',
            dni_nie='87654321X',
            email='cliente2@test.com',
            telefono='612345678'
        )
        self.habitacion = Habitacion.objects.create(
            numero='102', tipo='individual', precio_base=Decimal('50.00'), capacidad=1
        )

    def test_crear_reserva_calcula_precio_total(self):
        reserva = Reserva.objects.create(
            habitacion=self.habitacion,
            cliente=self.cliente,
            fecha_entrada=date.today() + timedelta(days=1),
            fecha_salida=date.today() + timedelta(days=4),
            numero_adultos=1,
            numero_ninos=0,
            precio_por_noche=Decimal('50.00')
        )
        self.assertEqual(reserva.noches, 3)
        self.assertEqual(reserva.precio_total, Decimal('150.00'))

    def test_descuento_estancia_larga(self):
        reserva = Reserva.objects.create(
            habitacion=self.habitacion,
            cliente=self.cliente,
            fecha_entrada=date.today() + timedelta(days=1),
            fecha_salida=date.today() + timedelta(days=8),
            numero_adultos=1,
            numero_ninos=0,
            precio_por_noche=Decimal('50.00')
        )
        # 7 noches * 50 * 0.9 = 315
        self.assertEqual(reserva.precio_total, Decimal('315.00'))

    def test_fecha_salida_anterior_a_entrada_lanza_error(self):
        reserva = Reserva(
            habitacion=self.habitacion,
            cliente=self.cliente,
            fecha_entrada=date.today() + timedelta(days=5),
            fecha_salida=date.today() + timedelta(days=2),
            numero_adultos=1,
            numero_ninos=0
        )
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_reserva_en_pasado_lanza_error(self):
        reserva = Reserva(
            habitacion=self.habitacion,
            cliente=self.cliente,
            fecha_entrada=date.today() - timedelta(days=5),
            fecha_salida=date.today() - timedelta(days=2),
            numero_adultos=1,
            numero_ninos=0
        )
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_capacidad_excedida_lanza_error(self):
        reserva = Reserva(
            habitacion=self.habitacion,
            cliente=self.cliente,
            fecha_entrada=date.today() + timedelta(days=1),
            fecha_salida=date.today() + timedelta(days=3),
            numero_adultos=2,
            numero_ninos=0
        )
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_reservas_solapadas_lanzan_error(self):
        Reserva.objects.create(
            habitacion=self.habitacion,
            cliente=self.cliente,
            fecha_entrada=date.today() + timedelta(days=1),
            fecha_salida=date.today() + timedelta(days=5),
            numero_adultos=1,
            numero_ninos=0,
            precio_por_noche=Decimal('50.00')
        )
        reserva_solapada = Reserva(
            habitacion=self.habitacion,
            cliente=self.cliente,
            fecha_entrada=date.today() + timedelta(days=3),
            fecha_salida=date.today() + timedelta(days=7),
            numero_adultos=1,
            numero_ninos=0
        )
        with self.assertRaises(ValidationError):
            reserva_solapada.full_clean()

    def test_iban_invalido_lanza_error(self):
        reserva = Reserva(
            habitacion=self.habitacion,
            cliente=self.cliente,
            fecha_entrada=date.today() + timedelta(days=1),
            fecha_salida=date.today() + timedelta(days=3),
            numero_adultos=1,
            numero_ninos=0,
            iban='ES123'
        )
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_buscar_reserva_solapada_devuelve_none_sin_conflictos(self):
        resultado = Reserva.buscar_reserva_solapada(
            self.habitacion,
            date.today() + timedelta(days=10),
            date.today() + timedelta(days=15)
        )
        self.assertIsNone(resultado)


class ViajeroCheckinModelTests(TestCase):
    """Tests para el modelo ViajeroCheckin."""

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='cliente3', password='testpass123', email='cliente3@test.com'
        )
        self.cliente = Cliente.objects.create(
            usuario=self.usuario, nombre='Luis', apellidos='Fernández',
            dni_nie='56789012B', email='cliente3@test.com', telefono='612345678'
        )
        self.habitacion = Habitacion.objects.create(
            numero='103', tipo='doble', precio_base=Decimal('60.00'), capacidad=2
        )
        self.reserva = Reserva.objects.create(
            habitacion=self.habitacion,
            cliente=self.cliente,
            fecha_entrada=date.today() + timedelta(days=1),
            fecha_salida=date.today() + timedelta(days=3),
            numero_adultos=1,
            numero_ninos=0,
            precio_por_noche=Decimal('60.00')
        )

    def test_viajero_menor_sin_documento_requiere_parentesco(self):
        viajero = ViajeroCheckin(
            reserva=self.reserva,
            nombre='Pedro',
            primer_apellido='López',
            sexo='M',
            tipo_documento='dni',
            nacionalidad='Española',
            fecha_nacimiento=date(2015, 1, 1),
            direccion_residencia='Calle Mayor 1',
            ciudad_residencia='Madrid',
            codigo_postal_residencia='28001',
            pais_residencia='España',
            telefono_contacto='612345678',
            email_contacto='pedro@test.com',
            es_menor_sin_documento=True,
            parentesco_menor_con_adulto=''
        )
        with self.assertRaises(ValidationError):
            viajero.full_clean()

    def test_viajero_adulto_requiere_documento(self):
        viajero = ViajeroCheckin(
            reserva=self.reserva,
            nombre='Pedro',
            primer_apellido='López',
            sexo='M',
            tipo_documento='dni',
            numero_documento='',
            nacionalidad='Española',
            fecha_nacimiento=date(1990, 1, 1),
            direccion_residencia='Calle Mayor 1',
            ciudad_residencia='Madrid',
            codigo_postal_residencia='28001',
            pais_residencia='España',
            telefono_contacto='612345678',
            email_contacto='pedro@test.com',
        )
        with self.assertRaises(ValidationError):
            viajero.full_clean()


class MenuDelDiaModelTests(TestCase):
    """Tests para el modelo MenuDelDia (singleton por fecha)."""

    def test_solo_existe_un_menu_del_dia(self):
        MenuDelDia.objects.create(activo=True)
        MenuDelDia.objects.create(activo=False)
        self.assertEqual(MenuDelDia.objects.count(), 1)

    def test_fecha_se_fija_a_hoy(self):
        menu = MenuDelDia.objects.create(activo=True)
        self.assertEqual(menu.fecha, date.today())


# ──────────────────────────────────────────────────────────────────────────────
# 🧪 TESTS DE FORMULARIOS
# ──────────────────────────────────────────────────────────────────────────────

class RegistroUsuarioFormTests(TestCase):
    """Tests para RegistroUsuarioForm."""

    def test_passwords_distintas_lanzan_error(self):
        form = RegistroUsuarioForm(data={
            'username': 'nuevo',
            'email': 'nuevo@test.com',
            'password': 'pass12345',
            'password_confirm': 'otraclave'
        })
        self.assertFalse(form.is_valid())

    def test_password_corta_lanza_error(self):
        form = RegistroUsuarioForm(data={
            'username': 'nuevo',
            'email': 'nuevo@test.com',
            'password': '123',
            'password_confirm': '123'
        })
        self.assertFalse(form.is_valid())

    def test_username_con_caracteres_invalidos_lanza_error(self):
        form = RegistroUsuarioForm(data={
            'username': 'nuevo@user',
            'email': 'nuevo@test.com',
            'password': 'pass12345',
            'password_confirm': 'pass12345'
        })
        self.assertFalse(form.is_valid())


class ClienteRegistroFormTests(TestCase):
    """Tests para ClienteRegistroForm."""

    def test_dni_invalido_lanza_error(self):
        form = ClienteRegistroForm(data={
            'nombre': 'Juan', 'apellidos': 'Pérez', 'dni_nie': '12345678A',
            'email': 'juan@test.com', 'telefono': '612345678'
        })
        self.assertFalse(form.is_valid())

    def test_nombre_con_numeros_lanza_error(self):
        form = ClienteRegistroForm(data={
            'nombre': 'Juan123', 'apellidos': 'Pérez', 'dni_nie': '12345678Z',
            'email': 'juan@test.com', 'telefono': '612345678'
        })
        self.assertFalse(form.is_valid())


class ReservaFormTests(TestCase):
    """Tests para ReservaForm."""

    def setUp(self):
        self.habitacion = Habitacion.objects.create(
            numero='201', tipo='familiar', precio_base=Decimal('100.00'), capacidad=4
        )

    def test_fechas_invalidas_lanzan_error(self):
        form = ReservaForm(data={
            'fecha_entrada': date.today() + timedelta(days=5),
            'fecha_salida': date.today() + timedelta(days=2),
            'numero_adultos': 2,
            'numero_ninos': 0,
            'medio_pago': 'tarjeta'
        }, habitacion=self.habitacion)
        self.assertFalse(form.is_valid())

    def test_capacidad_excedida_lanza_error(self):
        form = ReservaForm(data={
            'fecha_entrada': date.today() + timedelta(days=1),
            'fecha_salida': date.today() + timedelta(days=3),
            'numero_adultos': 3,
            'numero_ninos': 2,
            'medio_pago': 'tarjeta'
        }, habitacion=self.habitacion)
        self.assertFalse(form.is_valid())

    def test_medio_pago_requerido(self):
        form = ReservaForm(data={
            'fecha_entrada': date.today() + timedelta(days=1),
            'fecha_salida': date.today() + timedelta(days=3),
            'numero_adultos': 2,
            'numero_ninos': 0,
            'medio_pago': ''
        }, habitacion=self.habitacion)
        self.assertFalse(form.is_valid())

    def test_solapamiento_con_reserva_existente(self):
        usuario = User.objects.create_user(username='u1', password='p')
        cliente = Cliente.objects.create(
            usuario=usuario, nombre='A', apellidos='B', dni_nie='12345678Z',
            email='a@b.com', telefono='612345678'
        )
        Reserva.objects.create(
            habitacion=self.habitacion,
            cliente=cliente,
            fecha_entrada=date.today() + timedelta(days=1),
            fecha_salida=date.today() + timedelta(days=5),
            numero_adultos=2,
            numero_ninos=0,
            precio_por_noche=Decimal('100.00')
        )
        form = ReservaForm(data={
            'fecha_entrada': date.today() + timedelta(days=3),
            'fecha_salida': date.today() + timedelta(days=7),
            'numero_adultos': 2,
            'numero_ninos': 0,
            'medio_pago': 'tarjeta'
        }, habitacion=self.habitacion)
        self.assertFalse(form.is_valid())


class CheckinReservaFormTests(TestCase):
    """Tests para CheckinReservaForm."""

    def test_contrato_no_aceptado_lanza_error(self):
        form = CheckinReservaForm(data={
            'relaciones_parentesco_adultos': '',
            'contrato_aceptado': False
        })
        self.assertFalse(form.is_valid())


# ──────────────────────────────────────────────────────────────────────────────
# 🧪 TESTS DE VISTAS
# ──────────────────────────────────────────────────────────────────────────────

class VistaPublicaTests(VistaTestCase):
    """Tests para vistas accesibles sin autenticación."""

    def setUp(self):
        self.habitacion = Habitacion.objects.create(
            numero='301', tipo='suite', precio_base=Decimal('120.00'), capacidad=2
        )

    def test_home_devuelve_200(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_listado_habitaciones_devuelve_200(self):
        response = self.client.get(reverse('listado_habitaciones'))
        self.assertEqual(response.status_code, 200)

    def test_detalle_habitacion_devuelve_200(self):
        response = self.client.get(
            reverse('detalle_habitacion', args=[self.habitacion.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_sitemap_xml_devuelve_xml(self):
        response = self.client.get(reverse('sitemap_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        self.assertIn(self.habitacion.fecha_actualizacion.date().isoformat(), response.content.decode())

    def test_robots_txt_devuelve_texto_plano(self):
        response = self.client.get(reverse('robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertIn('Sitemap:', response.content.decode())


@override_settings(RATELIMIT_ENABLE=False)
class AutenticacionTests(VistaTestCase):
    """Tests para registro, login y logout."""

    def test_registro_cliente_crea_usuario_y_cliente(self):
        response = self.client.post(reverse('registro_cliente'), data={
            'username': 'nuevouser',
            'email': 'nuevo@test.com',
            'password': 'claveSegura123',
            'password_confirm': 'claveSegura123',
            'nombre': 'Nuevo',
            'apellidos': 'Usuario',
            'dni_nie': '12345678Z',
            'telefono': '612345678',
            'pais': 'España'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='nuevouser').exists())
        self.assertTrue(Cliente.objects.filter(dni_nie='12345678Z').exists())

    def test_login_con_credenciales_correctas(self):
        User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post(reverse('login'), data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_con_next_malicioso_no_redirige_fuera(self):
        User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('login') + '?next=https://evil.com',
            data={'username': 'testuser', 'password': 'testpass123'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_login_con_next_relativo_redirige_correctamente(self):
        User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('login') + '?next=/perfil/',
            data={'username': 'testuser', 'password': 'testpass123'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/perfil/')


@override_settings(RATELIMIT_ENABLE=False)
class ReservaVistaTests(VistaTestCase):
    """Tests para vistas de reservas autenticadas."""

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='cliente4', password='testpass123', email='cliente4@test.com'
        )
        self.cliente = Cliente.objects.create(
            usuario=self.usuario, nombre='Laura', apellidos='Gómez',
            dni_nie='11111111H', email='cliente4@test.com', telefono='612345678'
        )
        self.habitacion = Habitacion.objects.create(
            numero='401', tipo='doble', precio_base=Decimal('70.00'), capacidad=2
        )
        self.reserva = Reserva.objects.create(
            habitacion=self.habitacion,
            cliente=self.cliente,
            fecha_entrada=date.today() + timedelta(days=10),
            fecha_salida=date.today() + timedelta(days=13),
            numero_adultos=1,
            numero_ninos=0,
            precio_por_noche=Decimal('70.00')
        )
        self.client.login(username='cliente4', password='testpass123')

    def test_mis_reservas_requiere_login(self):
        self.client.logout()
        response = self.client.get(reverse('mis_reservas'))
        self.assertEqual(response.status_code, 302)

    def test_mis_reservas_muestra_reservas_del_usuario(self):
        response = self.client.get(reverse('mis_reservas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.reserva.codigo_reserva)

    def test_detalle_reserva_accesible_por_titular(self):
        response = self.client.get(
            reverse('detalle_reserva', args=[self.reserva.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.reserva.codigo_reserva)

    def test_detalle_reserva_no_accesible_por_otro_usuario(self):
        otro_usuario = User.objects.create_user(
            username='otro', password='testpass123'
        )
        Cliente.objects.create(
            usuario=otro_usuario, nombre='Otro', apellidos='Usuario',
            dni_nie='22222222J', email='otro@test.com', telefono='612345678'
        )
        self.client.logout()
        self.client.login(username='otro', password='testpass123')
        response = self.client.get(
            reverse('detalle_reserva', args=[self.reserva.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_crear_reserva_guarda_correctamente(self):
        response = self.client.post(
            reverse('crear_reserva', args=[self.habitacion.id]),
            data={
                'fecha_entrada': date.today() + timedelta(days=20),
                'fecha_salida': date.today() + timedelta(days=23),
                'numero_adultos': 1,
                'numero_ninos': 0,
                'medio_pago': 'tarjeta'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reserva.objects.filter(cliente=self.cliente).count(), 2)

    def test_fechas_ocupadas_devuelve_json(self):
        response = self.client.get(
            reverse('fechas_ocupadas', args=[self.habitacion.id])
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('ocupadas', data)
        self.assertEqual(len(data['ocupadas']), 1)


@override_settings(RATELIMIT_ENABLE=False)
class CheckinOnlineVistaTests(VistaTestCase):
    """Tests para el check-in online."""

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='cliente5', password='testpass123'
        )
        self.cliente = Cliente.objects.create(
            usuario=self.usuario, nombre='Pedro', apellidos='Ruiz',
            dni_nie='33333333P', email='pedro@test.com', telefono='612345678'
        )
        self.habitacion = Habitacion.objects.create(
            numero='501', tipo='doble', precio_base=Decimal('80.00'), capacidad=2
        )
        self.reserva = Reserva.objects.create(
            habitacion=self.habitacion,
            cliente=self.cliente,
            fecha_entrada=date.today() + timedelta(days=1),
            fecha_salida=date.today() + timedelta(days=3),
            numero_adultos=1,
            numero_ninos=0,
            precio_por_noche=Decimal('80.00')
        )
        self.client.login(username='cliente5', password='testpass123')

    def test_checkin_online_completa_reserva(self):
        response = self.client.post(
            reverse('checkin_online_reserva', args=[self.reserva.id]),
            data={
                'relaciones_parentesco_adultos': '',
                'contrato_aceptado': True,
                'viajeros-TOTAL_FORMS': '1',
                'viajeros-INITIAL_FORMS': '0',
                'viajeros-MIN_NUM_FORMS': '0',
                'viajeros-MAX_NUM_FORMS': '1000',
                'viajeros-0-orden': '1',
                'viajeros-0-nombre': 'Pedro',
                'viajeros-0-primer_apellido': 'Ruiz',
                'viajeros-0-sexo': 'M',
                'viajeros-0-tipo_documento': 'dni',
                'viajeros-0-numero_documento': '33333333P',
                'viajeros-0-numero_soporte': 'A123456',
                'viajeros-0-nacionalidad': 'Española',
                'viajeros-0-fecha_nacimiento': '1990-01-01',
                'viajeros-0-direccion_residencia': 'Calle 1',
                'viajeros-0-ciudad_residencia': 'Madrid',
                'viajeros-0-codigo_postal_residencia': '28001',
                'viajeros-0-pais_residencia': 'España',
                'viajeros-0-telefono_contacto': '612345678',
                'viajeros-0-email_contacto': 'pedro@test.com',
                'viajeros-0-relacion_con_titular': 'titular',
                'viajeros-0-es_menor_sin_documento': False,
                'acepto_consentimiento': True,
            }
        )
        self.assertEqual(response.status_code, 302)
        self.reserva.refresh_from_db()
        self.assertTrue(self.reserva.checkin_online_completado)
