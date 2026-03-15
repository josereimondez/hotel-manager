from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.html import strip_tags
import re
from .models import (Cliente, Reserva, MenuDelDia, PlatoMenuDelDia,
                     MenuEspecial, PlatoMenuEspecial, ViajeroCheckin)

# 🎓 CONCEPTO: ModelForm = Formulario basado en un modelo


class RegistroUsuarioForm(forms.ModelForm):
    """
    Formulario para crear cuenta de usuario.
    
    🐍 PYTHON: Formulario con campos extra
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Contraseña'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar contraseña'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
        }
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Email',
        }
    
    def clean_username(self):
        """Validar username: solo letras, números, guiones y guiones bajos."""
        username = self.cleaned_data.get('username', '')
        # Eliminar cualquier tag HTML por seguridad
        username = strip_tags(username)
        # Validar caracteres permitidos
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise forms.ValidationError(
                'El nombre de usuario solo puede contener letras, números, guiones y guiones bajos.'
            )
        # Validar longitud
        if len(username) < 3:
            raise forms.ValidationError('El nombre de usuario debe tener al menos 3 caracteres.')
        if len(username) > 30:
            raise forms.ValidationError('El nombre de usuario no puede tener más de 30 caracteres.')
        return username
    
    def clean_email(self):
        """Validar y normalizar email."""
        email = self.cleaned_data.get('email', '')
        email = strip_tags(email).lower().strip()
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        # Validar fortaleza de contraseña
        if password and len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        
        return cleaned_data


class ClienteRegistroForm(forms.ModelForm):
    """
    Formulario para registro de clientes.
    
    🐍 PYTHON QUE APRENDES:
    - Clases anidadas (Meta)
    - Herencia de ModelForm
    - Widgets personalizados
    - Sanitización de inputs
    """
    
    def clean_nombre(self):
        """Sanitizar nombre."""
        nombre = self.cleaned_data.get('nombre', '')
        nombre = strip_tags(nombre).strip()
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError('El nombre solo puede contener letras.')
        return nombre.title()
    
    def clean_apellidos(self):
        """Sanitizar apellidos."""
        apellidos = self.cleaned_data.get('apellidos', '')
        apellidos = strip_tags(apellidos).strip()
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellidos):
            raise forms.ValidationError('Los apellidos solo pueden contener letras.')
        return apellidos.title()
    
    def clean_telefono(self):
        """Sanitizar y validar teléfono."""
        telefono = self.cleaned_data.get('telefono', '')
        telefono = strip_tags(telefono).strip()
        # Permitir solo números, espacios, + y guiones
        telefono = re.sub(r'[^0-9+\s-]', '', telefono)
        if len(telefono) < 9:
            raise forms.ValidationError('El teléfono debe tener al menos 9 dígitos.')
        return telefono
    
    def clean_email(self):
        """Sanitizar email."""
        email = self.cleaned_data.get('email', '')
        email = strip_tags(email).lower().strip()
        return email
    
    def clean_direccion(self):
        """Sanitizar dirección."""
        direccion = self.cleaned_data.get('direccion', '')
        return strip_tags(direccion).strip()
    
    def clean_ciudad(self):
        """Sanitizar ciudad."""
        ciudad = self.cleaned_data.get('ciudad', '')
        ciudad = strip_tags(ciudad).strip()
        if ciudad and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s-]+$', ciudad):
            raise forms.ValidationError('La ciudad solo puede contener letras.')
        return ciudad.title()
    
    def clean_pais(self):
        """Sanitizar país."""
        pais = self.cleaned_data.get('pais', '')
        pais = strip_tags(pais).strip()
        return pais.title()
    
    class Meta:
        model = Cliente
        fields = [
            'nombre', 'apellidos', 'dni_nie', 
            'email', 'telefono', 'fecha_nacimiento',
            'direccion', 'ciudad', 'codigo_postal', 'pais'
        ]
        
        # 🎨 Widgets = controles HTML personalizados
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tus apellidos'
            }),
            'dni_nie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345678Z o X1234567L'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '612345678'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle, número, piso...'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu ciudad'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '28001'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'España'
            }),
        }


class EditarUsuarioForm(forms.ModelForm):
    """Formulario para editar datos de la cuenta (User)."""

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Email',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
        }


class EditarClienteForm(forms.ModelForm):
    """Formulario para editar datos personales del Cliente."""

    class Meta:
        model = Cliente
        fields = [
            'nombre', 'apellidos', 'telefono',
            'direccion', 'ciudad', 'codigo_postal', 'pais'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ─── Menú del día ───────────────────────────────────────────────────────────

class MenuDelDiaForm(forms.ModelForm):
    """Formulario principal del menú del día."""

    class Meta:
        model = MenuDelDia
        fields = ['activo', 'consumicion_incluida', 'notas']
        widgets = {
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'consumicion_incluida': forms.TextInput(
                attrs={'class': 'form-control',
                       'placeholder': 'Ej: vino, cerveza, refresco o agua'}
            ),
            'notas': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2,
                       'placeholder': 'Información adicional, alérgenos…'}
            ),
        }
        labels = {
            'activo': '¿Publicado?',
            'consumicion_incluida': 'Consumición incluida',
            'notas': 'Notas (opcional)',
        }


PlatoFormSet = forms.inlineformset_factory(
    MenuDelDia,
    PlatoMenuDelDia,
    fields=['categoria', 'nombre', 'descripcion', 'orden', 'disponible'],
    extra=0,
    can_delete=True,
    widgets={
        'categoria': forms.Select(
            attrs={'class': 'form-select form-select-sm'}
        ),
        'nombre': forms.TextInput(
            attrs={'class': 'form-control form-control-sm',
                   'placeholder': 'Nombre del plato'}
        ),
        'descripcion': forms.TextInput(
            attrs={'class': 'form-control form-control-sm',
                   'placeholder': 'Descripción (opcional)'}
        ),
        'orden': forms.NumberInput(
            attrs={'class': 'form-control form-control-sm',
                   'min': '1', 'style': 'width:70px'}
        ),
        'disponible': forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        ),
    },
)


# ─── Menú Especial ───────────────────────────────────────────────────────────

class MenuEspecialForm(forms.ModelForm):
    """Formulario para crear/editar un menú especial."""

    class Meta:
        model = MenuEspecial
        fields = ['titulo', 'descripcion', 'precio', 'fecha_inicio', 'fecha_fin',
                  'activo', 'consumicion_incluida', 'notas']
        widgets = {
            'titulo': forms.TextInput(
                attrs={'class': 'form-control',
                       'placeholder': 'Ej: Menú de Semana Santa…'}
            ),
            'descripcion': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2,
                       'placeholder': 'Descripción breve del menú especial'}
            ),
            'precio': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0',
                       'placeholder': 'Ej: 18.50'}
            ),
            'fecha_inicio': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'fecha_fin': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'consumicion_incluida': forms.TextInput(
                attrs={'class': 'form-control',
                       'placeholder': 'Ej: Vino de la casa incluido'}
            ),
            'notas': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2,
                       'placeholder': 'Alérgenos, condiciones, etc.'}
            ),
        }
        labels = {
            'titulo': 'Título del menú',
            'descripcion': 'Descripción',
            'precio': 'Precio por persona (€)',
            'fecha_inicio': 'Fecha inicio',
            'fecha_fin': 'Fecha fin',
            'activo': '¿Publicado?',
            'consumicion_incluida': 'Consumición incluida',
            'notas': 'Notas (opcional)',
        }

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('fecha_inicio')
        fin = cleaned_data.get('fecha_fin')
        if inicio and fin and fin < inicio:
            raise forms.ValidationError(
                'La fecha de fin no puede ser anterior a la fecha de inicio.'
            )
        return cleaned_data


PlatoMenuEspecialFormSet = forms.inlineformset_factory(
    MenuEspecial,
    PlatoMenuEspecial,
    fields=['categoria', 'nombre', 'descripcion', 'orden', 'disponible'],
    extra=0,
    can_delete=True,
    widgets={
        'categoria': forms.Select(
            attrs={'class': 'form-select form-select-sm'}
        ),
        'nombre': forms.TextInput(
            attrs={'class': 'form-control form-control-sm',
                   'placeholder': 'Nombre del plato'}
        ),
        'descripcion': forms.TextInput(
            attrs={'class': 'form-control form-control-sm',
                   'placeholder': 'Descripción (opcional)'}
        ),
        'orden': forms.NumberInput(
            attrs={'class': 'form-control form-control-sm',
                   'min': '1', 'style': 'width:70px'}
        ),
        'disponible': forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        ),
    },
)


class CambiarPasswordForm(forms.Form):
    """Formulario para cambiar contraseña."""
    password_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Contraseña actual'
    )
    password_nueva = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Nueva contraseña'
    )
    password_confirmar = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar nueva contraseña'
    )

    def clean(self):
        cleaned_data = super().clean()
        nueva = cleaned_data.get('password_nueva')
        confirmar = cleaned_data.get('password_confirmar')
        if nueva and confirmar and nueva != confirmar:
            raise forms.ValidationError('Las contraseñas nuevas no coinciden.')
        return cleaned_data


class ReservaForm(forms.ModelForm):
    """
    Formulario para crear reservas.
    
    🐍 PYTHON: Validaciones personalizadas en formularios
    """
    
    def __init__(self, *args, habitacion=None, **kwargs):
        """🐍 PYTHON: Constructor personalizado para recibir la habitación"""
        super().__init__(*args, **kwargs)
        self.habitacion = habitacion
    
    class Meta:
        model = Reserva
        fields = [
            'fecha_entrada', 'fecha_salida',  # 👈 Quitamos 'cliente'
            'numero_adultos', 'numero_ninos', 'medio_pago', 'iban', 'observaciones'
        ]
        
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'fecha_entrada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_salida': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'numero_adultos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'numero_ninos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'medio_pago': forms.Select(attrs={
                'class': 'form-select',
            }),
            'iban': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ES12 3456 7890 1234 5678 9012 (opcional)'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Peticiones especiales, hora estimada de llegada...'
            }),
        }
    
    def clean_observaciones(self):
        """Sanitizar observaciones."""
        observaciones = self.cleaned_data.get('observaciones', '')
        # Eliminar HTML tags por seguridad
        observaciones = strip_tags(observaciones).strip()
        # Limitar longitud
        if len(observaciones) > 500:
            raise forms.ValidationError('Las observaciones no pueden superar los 500 caracteres.')
        return observaciones

    def clean_iban(self):
        """Normalizar y validar IBAN opcional."""
        iban = self.cleaned_data.get('iban', '')
        iban = strip_tags(iban).replace(' ', '').upper()
        if not iban:
            return ''
        if not re.match(r'^[A-Z]{2}[0-9A-Z]{13,32}$', iban):
            raise forms.ValidationError('IBAN inválido.')
        return iban
    
    def clean_numero_adultos(self):
        """Validar número de adultos."""
        numero = self.cleaned_data.get('numero_adultos', 0)
        if numero < 1:
            raise forms.ValidationError('Debe haber al menos 1 adulto.')
        if numero > 10:
            raise forms.ValidationError('Número máximo de adultos: 10.')
        return numero
    
    def clean_numero_ninos(self):
        """Validar número de niños."""
        numero = self.cleaned_data.get('numero_ninos', 0)
        if numero < 0:
            raise forms.ValidationError('El número de niños no puede ser negativo.')
        if numero > 10:
            raise forms.ValidationError('Número máximo de niños: 10.')
        return numero
    
    def clean(self):
        """
        Validaciones personalizadas del formulario.
        
        🐍 PYTHON: Método clean() para validar múltiples campos
        """
        cleaned_data = super().clean()
        fecha_entrada = cleaned_data.get('fecha_entrada')
        fecha_salida = cleaned_data.get('fecha_salida')
        numero_adultos = cleaned_data.get('numero_adultos', 0)
        numero_ninos = cleaned_data.get('numero_ninos', 0)
        medio_pago = cleaned_data.get('medio_pago', '')
        
        # Validar fechas
        if fecha_entrada and fecha_salida:
            if fecha_salida <= fecha_entrada:
                raise forms.ValidationError(
                    'La fecha de salida debe ser posterior a la de entrada'
                )
        
        # 🔍 Validar capacidad de la habitación
        if self.habitacion:
            total_personas = numero_adultos + numero_ninos
            if total_personas > self.habitacion.capacidad:
                raise forms.ValidationError(
                    f'La habitación solo tiene capacidad para {self.habitacion.capacidad} personas. '
                    f'Has seleccionado {total_personas} personas ({numero_adultos} adultos + {numero_ninos} niños).'
                )

        if not medio_pago:
            raise forms.ValidationError('Debes seleccionar un medio de pago.')

        # 🔒 Validar disponibilidad: no solapar con reservas existentes
        if self.habitacion and fecha_entrada and fecha_salida:
            from .models import Reserva as ReservaModel
            solapadas = ReservaModel.objects.filter(
                habitacion=self.habitacion,
                estado__in=['confirmada', 'en_curso', 'pendiente'],
                fecha_entrada__lt=fecha_salida,
                fecha_salida__gt=fecha_entrada,
            )
            if solapadas.exists():
                r = solapadas.first()
                raise forms.ValidationError(
                    f'La habitación ya está reservada del {r.fecha_entrada} al {r.fecha_salida}. '
                    f'Por favor elige otras fechas.'
                )

        return cleaned_data


class CheckinReservaForm(forms.ModelForm):
    """Formulario legal de check-in online por reserva."""

    class Meta:
        model = Reserva
        fields = ['relaciones_parentesco_adultos', 'contrato_aceptado']
        widgets = {
            'relaciones_parentesco_adultos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Ej: Viajero 1 y viajero 2 son cónyuges.'
            }),
            'contrato_aceptado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'relaciones_parentesco_adultos': 'Relación de parentesco entre adultos',
            'contrato_aceptado': 'Acepto el contrato de hospedaje y veracidad de datos',
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('contrato_aceptado'):
            raise forms.ValidationError(
                'Debes aceptar el contrato para completar el check-in online.'
            )
        return cleaned_data


class ViajeroCheckinForm(forms.ModelForm):
    """Formulario de datos obligatorios por viajero para SES Hospedajes."""

    class Meta:
        model = ViajeroCheckin
        fields = [
            'orden', 'nombre', 'primer_apellido', 'segundo_apellido', 'sexo',
            'tipo_documento', 'numero_documento', 'numero_soporte',
            'nacionalidad', 'fecha_nacimiento',
            'direccion_residencia', 'ciudad_residencia',
            'codigo_postal_residencia', 'pais_residencia',
            'telefono_contacto', 'email_contacto',
            'relacion_con_titular', 'es_menor_sin_documento', 'parentesco_menor_con_adulto'
        ]
        widgets = {
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'primer_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'segundo_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_soporte': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'direccion_residencia': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad_residencia': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal_residencia': forms.TextInput(attrs={'class': 'form-control'}),
            'pais_residencia': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'email_contacto': forms.EmailInput(attrs={'class': 'form-control'}),
            'relacion_con_titular': forms.Select(attrs={'class': 'form-select'}),
            'es_menor_sin_documento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'parentesco_menor_con_adulto': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nombre(self):
        return strip_tags(self.cleaned_data.get('nombre', '')).strip().title()

    def clean_primer_apellido(self):
        return strip_tags(self.cleaned_data.get('primer_apellido', '')).strip().title()

    def clean_segundo_apellido(self):
        return strip_tags(self.cleaned_data.get('segundo_apellido', '')).strip().title()


def get_viajero_checkin_formset(extra=0):
    """Devuelve un formset de viajeros con número de filas configurable."""
    return forms.inlineformset_factory(
        Reserva,
        ViajeroCheckin,
        form=ViajeroCheckinForm,
        extra=extra,
        can_delete=True,
    )
