"""
Middleware personalizado para manejar rate limiting.
"""
from django.template.response import TemplateResponse
from django_ratelimit.exceptions import Ratelimited


class RatelimitMiddleware:
    """
    Middleware para manejar errores de rate limiting de forma elegante.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Maneja excepciones de rate limiting.
        """
        if isinstance(exception, Ratelimited):
            # Determinar el mensaje según la vista
            if 'login' in request.path:
                message = 'Demasiados intentos de inicio de sesión. Por favor, espera unos minutos e intenta de nuevo.'
            elif 'registro' in request.path:
                message = 'Has excedido el límite de registros permitidos. Por favor, espera una hora e intenta de nuevo.'
            elif 'reservar' in request.path or 'reserva' in request.path:
                message = 'Has excedido el límite de reservas permitidas. Por favor, espera un momento e intenta de nuevo.'
            elif 'fechas-ocupadas' in request.path:
                message = 'Demasiadas consultas. Por favor, recarga la página en unos segundos.'
            else:
                message = 'Has excedido el límite de solicitudes permitidas. Por favor, espera un momento e intenta de nuevo.'
            
            # Renderizar página de error personalizada
            context = {
                'error_title': 'Límite de Solicitudes Excedido',
                'error_message': message,
                'error_code': 429,
            }
            return TemplateResponse(request, 'reservas/error_ratelimit.html', context, status=429)
