"""
Servicio de integración con SES Hospedajes.

Este módulo proporciona funciones para construir, enviar y registrar
el envío de partes de viajeros al sistema SES Hospedajes de la
Policía Nacional española.
"""

import logging
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError

from ..models import RegistroAuditoria

logger = logging.getLogger(__name__)


def build_payload(reserva):
    """
    Construye el payload para enviar a SES Hospedajes.

    Args:
        reserva: Instancia de Reserva con check-in completado

    Returns:
        dict: Payload estructurado para SES Hospedajes

    Raises:
        ValidationError: Si faltan datos obligatorios
        ValueError: Si el check-in no está completado
    """
    if not reserva.checkin_online_completado:
        raise ValueError("El check-in debe estar completado para enviar a SES Hospedajes")

    viajeros = reserva.viajeros_checkin.all()
    if not viajeros.exists():
        raise ValidationError("No hay viajeros registrados en la reserva")

    payload = {
        'establecimiento': {
            'nombre': 'Hostal Rivera',
            'tipo': 'hostal',
        },
        'reserva': {
            'codigo': reserva.codigo_reserva,
            'fecha_entrada': reserva.fecha_entrada.isoformat(),
            'fecha_salida': reserva.fecha_salida.isoformat(),
            'habitacion': reserva.habitacion.numero,
            'medio_pago': reserva.medio_pago,
        },
        'viajeros': [],
        'metadata': {
            'fecha_envio': datetime.now().isoformat(),
            'version': '1.0',
        }
    }

    for viajero in viajeros:
        viajero_data = {
            'orden': viajero.orden,
            'nombre': viajero.nombre,
            'primer_apellido': viajero.primer_apellido,
            'segundo_apellido': viajero.segundo_apellido,
            'sexo': viajero.sexo,
            'nacionalidad': viajero.nacionalidad,
            'fecha_nacimiento': viajero.fecha_nacimiento.isoformat(),
            'direccion': {
                'calle': viajero.direccion_residencia,
                'ciudad': viajero.ciudad_residencia,
                'codigo_postal': viajero.codigo_postal_residencia,
                'pais': viajero.pais_residencia,
            },
            'contacto': {
                'telefono': viajero.telefono_contacto,
                'email': viajero.email_contacto,
            },
            'relacion_titular': viajero.relacion_con_titular,
        }

        if viajero.es_menor_sin_documento:
            viajero_data['es_menor'] = True
            viajero_data['parentesco_menor'] = viajero.parentesco_menor_con_adulto
        else:
            viajero_data['es_menor'] = False
            viajero_data['documento'] = {
                'tipo': viajero.tipo_documento,
                'numero': viajero.numero_documento,
                'soporte': viajero.numero_soporte,
            }

        payload['viajeros'].append(viajero_data)

    return payload


def send_payload(payload):
    """
    Envía el payload a SES Hospedajes.

    En modo mock (SES_HOSPEDAJES_ENABLED=False), simula el envío
    y retorna una respuesta exitosa.

    Args:
        payload: dict con el payload estructurado

    Returns:
        dict: {
            'exito': bool,
            'referencia': str or None,
            'error': str or None
        }
    """
    if not getattr(settings, 'SES_HOSPEDAJES_ENABLED', False):
        logger.info("SES Hospedajes deshabilitado. Modo mock activo.")
        return {
            'exito': True,
            'referencia': f'MOCK-{payload["reserva"]["codigo"]}',
            'error': None
        }

    try:
        endpoint = settings.SES_HOSPEDAJES_ENDPOINT
        user = settings.SES_HOSPEDAJES_USER
        password = settings.SES_HOSPEDAJES_PASSWORD
        timeout = getattr(settings, 'SES_HOSPEDAJES_TIMEOUT', 20)

        if not all([endpoint, user, password]):
            logger.error("Credenciales SES Hospedajes incompletas")
            return {
                'exito': False,
                'referencia': None,
                'error': 'Credenciales SES Hospedajes incompletas'
            }

        logger.info(f"Enviando payload a SES Hospedajes: {endpoint}")

        return {
            'exito': False,
            'referencia': None,
            'error': 'Integración real con SES Hospedajes no implementada aún. Configure SES_HOSPEDAJES_ENABLED=False para modo mock.'
        }

    except Exception as e:
        logger.exception("Error enviando a SES Hospedajes")
        return {
            'exito': False,
            'referencia': None,
            'error': str(e)
        }


def registrar_envio(reserva, exito, referencia, error):
    """
    Registra el resultado del envío a SES Hospedajes.

    Args:
        reserva: Instancia de Reserva
        exito: bool indicando si el envío fue exitoso
        referencia: str con la referencia de SES o None
        error: str con el mensaje de error o None
    """
    reserva.ses_hospedajes_enviado = exito
    if referencia:
        reserva.ses_hospedajes_referencia = referencia
    reserva.save(update_fields=['ses_hospedajes_enviado', 'ses_hospedajes_referencia'])

    RegistroAuditoria.objects.create(
        tipo_accion='envio_ses',
        entidad_tipo='reserva',
        entidad_id=reserva.id,
        descripcion=f'Envío a SES Hospedajes: {"Exitoso" if exito else "Fallido"}',
        datos_nuevos={
            'exito': exito,
            'referencia': referencia,
            'error': error,
        }
    )

    if exito:
        logger.info(f"SES Hospedajes enviado exitosamente. Referencia: {referencia}")
    else:
        logger.error(f"Error enviando a SES Hospedajes: {error}")


def reintentar_envio(reserva):
    """
    Reintenta el envío a SES Hospedajes para una reserva con envío fallido.

    Args:
        reserva: Instancia de Reserva

    Returns:
        dict: Resultado del reintento (mismo formato que send_payload)

    Raises:
        ValueError: Si el envío ya fue exitoso
    """
    if reserva.ses_hospedajes_enviado:
        raise ValueError("El envío a SES Hospedajes ya fue exitoso")

    payload = build_payload(reserva)
    resultado = send_payload(payload)
    registrar_envio(
        reserva,
        resultado['exito'],
        resultado['referencia'],
        resultado['error']
    )

    return resultado
