from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User  # 👈 Importar User
from django.utils.html import strip_tags
from decimal import Decimal
from datetime import date
import re

# 🎓 CONCEPTO: Una clase = una tabla en la base de datos
# Cada atributo = una columna


# 🔧 FUNCIÓN DE VALIDACIÓN PERSONALIZADA
def validar_dni_nie(valor):
    """
    Valida DNI o NIE español.
    
    🐍 PYTHON QUE APRENDES:
    - Funciones
    - Expresiones regulares (regex)
    - Excepciones personalizadas
    - Algoritmo de validación
    """
    # Limpiar espacios y convertir a mayúsculas
    valor = valor.replace(" ", "").replace("-", "").upper()
    
    # Regex para DNI (8 números + letra) o NIE (X/Y/Z + 7 números + letra)
    patron_dni = r'^[0-9]{8}[A-Z]$'
    patron_nie = r'^[XYZ][0-9]{7}[A-Z]$'
    
    if not (re.match(patron_dni, valor) or re.match(patron_nie, valor)):
        raise ValidationError('Formato de DNI/NIE inválido')
    
    # Validar letra correcta
    letras = 'TRWAGMYFPDXBNJZSQVHLCKE'
    
    if valor[0] in 'XYZ':  # NIE
        # Reemplazar primera letra por número
        numero = valor[1:8]
        if valor[0] == 'X':
            numero = '0' + numero
        elif valor[0] == 'Y':
            numero = '1' + numero
        else:  # Z
            numero = '2' + numero
        numero = int(numero)
    else:  # DNI
        numero = int(valor[:8])
    
    letra_calculada = letras[numero % 23]
    
    if valor[-1] != letra_calculada:
        raise ValidationError('La letra del DNI/NIE no es correcta')


class Cliente(models.Model):
    """
    Modelo para clientes/huéspedes del hotel.
    
    🐍 PYTHON QUE APRENDES:
    - Validaciones personalizadas
    - Métodos de clase
    - Propiedades calculadas
    - Relación OneToOne con User
    """
    
    # 🔐 VINCULACIÓN CON USUARIO
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,  # Temporal para migración
        blank=True,
        related_name='cliente',
        help_text="Usuario de Django asociado"
    )
    
    # 📝 DATOS PERSONALES
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)
    
    dni_nie = models.CharField(
        max_length=9,
        unique=True,
        validators=[validar_dni_nie],
        help_text="DNI o NIE español (ej: 12345678Z o X1234567L)"
    )
    
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)
    
    # 📍 DIRECCIÓN
    direccion = models.CharField(max_length=200, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    pais = models.CharField(max_length=50, default='España')
    
    # 📅 FECHAS
    fecha_nacimiento = models.DateField(
        null=True, 
        blank=True,
        help_text="Formato: YYYY-MM-DD"
    )
    
    def clean(self):
        """Validaciones adicionales del modelo."""
        super().clean()
        
        # Sanitizar campos de texto
        if self.nombre:
            self.nombre = strip_tags(self.nombre).strip()
        if self.apellidos:
            self.apellidos = strip_tags(self.apellidos).strip()
        if self.direccion:
            self.direccion = strip_tags(self.direccion).strip()
        if self.ciudad:
            self.ciudad = strip_tags(self.ciudad).strip()
        if self.pais:
            self.pais = strip_tags(self.pais).strip()
        
        # Validar email format
        if self.email:
            validator = EmailValidator()
            try:
                validator(self.email)
            except ValidationError:
                raise ValidationError({'email': 'Email inválido.'})
        
        # Validar teléfono
        if self.telefono:
            telefono_limpio = re.sub(r'[^0-9+]', '', self.telefono)
            if len(telefono_limpio) < 9:
                raise ValidationError({'telefono': 'El teléfono debe tener al menos 9 dígitos.'})
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # 💳 INFORMACIÓN ADICIONAL
    notas = models.TextField(
        blank=True,
        help_text="Preferencias, alergias, etc."
    )
    
    es_vip = models.BooleanField(
        default=False,
        verbose_name="Cliente VIP"
    )
    
    def __str__(self):
        return f"{self.nombre} {self.apellidos} ({self.dni_nie})"
    
    @property
    def nombre_completo(self):
        """
        Propiedad que retorna nombre completo.
        
        🐍 PYTHON: @property permite usar como atributo
        """
        return f"{self.nombre} {self.apellidos}"
    
    @property
    def edad(self):
        """
        Calcula edad a partir de fecha de nacimiento.
        
        🐍 PYTHON: Cálculo con fechas
        """
        if not self.fecha_nacimiento:
            return None
        
        from datetime import date
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['apellidos', 'nombre']


class Habitacion(models.Model):
    """
    Modelo que representa una habitación del hotel.
    
    🐍 PYTHON QUE APRENDES:
    - Clases y herencia (models.Model)
    - Tipos de datos
    - Validadores
    - Métodos personalizados
    """
    
    # 📝 TIPOS DE HABITACIÓN
    # Esto es una TUPLA de TUPLAS (inmutable)
    TIPO_CHOICES = [
        ('individual', 'Individual'),      # (valor_bd, etiqueta_mostrar)
        ('doble', 'Doble'),
        ('suite', 'Suite'),
        ('familiar', 'Familiar'),
    ]
    
    # 🏠 CAMPOS (columnas de la tabla)
    numero = models.CharField(
        max_length=10,
        unique=True,                    # No puede haber dos iguales
        help_text="Número de habitación (ej: 101, 205)"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,           # Solo puede ser uno de estos
        default='doble'
    )
    
    precio_base = models.DecimalField(
        max_digits=6,                   # Máximo 9999.99
        decimal_places=2,               # 2 decimales
        validators=[MinValueValidator(Decimal('10.00'))],
        help_text="Precio por noche en euros"
    )
    
    capacidad = models.IntegerField(
        default=2,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(6)
        ],
        help_text="Número máximo de personas"
    )
    
    tiene_vista_mar = models.BooleanField(
        default=False,
        verbose_name="Vista al mar"
    )
    
    descripcion = models.TextField(
        blank=True,                     # Puede estar vacío
        null=True,                      # Puede ser NULL en BD
        help_text="Descripción de la habitación"
    )
    
    # � CAMPO DE IMAGEN (nuevo!)
    foto = models.ImageField(
        upload_to='habitaciones/',      # 🐍 Se guardará en media/habitaciones/
        blank=True,                     # Opcional
        null=True,
        help_text="Foto principal de la habitación"
    )
    
    # �📅 Campos automáticos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # ⚙️ MÉTODOS ESPECIALES (mágicos en Python)
    
    def __str__(self):
        """
        Representa el objeto como string.
        Se usa en el admin y en templates.
        
        🐍 PYTHON: método mágico __str__
        """
        return f"Habitación {self.numero} - {self.get_tipo_display()}"
    
    # 🎯 MÉTODOS PERSONALIZADOS
    
    def precio_con_vista(self):
        """
        Calcula precio con recargo por vista al mar.
        
        🐍 PYTHON: Condicionales, operaciones matemáticas
        """
        if self.tiene_vista_mar:
            return self.precio_base * Decimal('1.20')  # +20%
        return self.precio_base
    
    def calcular_precio_estancia(self, noches):
        """
        Calcula precio total para X noches.
        
        🐍 PYTHON: Funciones con parámetros
        """
        precio = self.precio_con_vista()
        total = precio * noches
        
        # Descuento por estancia larga
        if noches >= 7:
            total = total * Decimal('0.90')  # -10%
        
        return round(total, 2)
    
    # 📊 METADATA (configuración del modelo)
    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"
        ordering = ['numero']           # Ordenar por número
        
        # Índices para búsquedas rápidas
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['precio_base']),
        ]


class Reserva(models.Model):
    """
    Modelo para reservas de habitaciones.
    
    🐍 PYTHON QUE APRENDES:
    - Relaciones ForeignKey (clave foránea)
    - Validaciones complejas
    - Cálculos con fechas
    - Señales (signals)
    """
    
    # 📋 ESTADOS DE RESERVA
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de pago'),
        ('confirmada', 'Confirmada'),
        ('en_curso', 'En curso (Check-in realizado)'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    
    # 🔗 RELACIONES (ForeignKey = Muchos a Uno)
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.PROTECT,  # No se puede eliminar habitación con reservas
        related_name='reservas',   # 🐍 Acceso inverso: habitacion.reservas.all()
        help_text="Habitación reservada"
    )
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='reservas',
        help_text="Cliente que realiza la reserva"
    )
    
    # 📅 FECHAS
    fecha_entrada = models.DateField(
        verbose_name="Fecha de entrada (Check-in)"
    )
    
    fecha_salida = models.DateField(
        verbose_name="Fecha de salida (Check-out)"
    )
    
    fecha_reserva = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación de la reserva"
    )
    
    # 👥 HUÉSPEDES
    numero_adultos = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    
    numero_ninos = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # 💰 PRECIO
    precio_por_noche = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Precio por noche al momento de la reserva"
    )
    
    precio_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,  # 🐍 Se calcula automáticamente
        help_text="Precio total de la estancia"
    )
    
    # 📊 ESTADO
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )

    # 📄 Datos adicionales para SES Hospedajes
    MEDIO_PAGO_CHOICES = [
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia bancaria'),
        ('efectivo', 'Efectivo'),
        ('bizum', 'Bizum'),
        ('otro', 'Otro'),
    ]
    medio_pago = models.CharField(
        max_length=20,
        choices=MEDIO_PAGO_CHOICES,
        blank=True,
        help_text='Medio de pago informado por el viajero principal.'
    )
    iban = models.CharField(
        max_length=34,
        blank=True,
        help_text='IBAN asociado a la transacción (si aplica).'
    )
    relaciones_parentesco_adultos = models.TextField(
        blank=True,
        help_text='Relación de parentesco entre viajeros mayores de edad.'
    )
    contrato_aceptado = models.BooleanField(
        default=False,
        help_text='Consentimiento del contrato de hospedaje.'
    )
    checkin_online_completado = models.BooleanField(
        default=False,
        help_text='Indica si se completó el check-in online legal.'
    )
    ses_hospedajes_enviado = models.BooleanField(
        default=False,
        help_text='Indica si el parte fue enviado al servicio web SES Hospedajes.'
    )
    ses_hospedajes_referencia = models.CharField(
        max_length=120,
        blank=True,
        help_text='Referencia o identificador devuelto por SES Hospedajes.'
    )
    
    # 📝 INFORMACIÓN ADICIONAL
    observaciones = models.TextField(
        blank=True,
        max_length=500,  # Limitar longitud
        help_text="Peticiones especiales, hora estimada de llegada, etc."
    )
    
    def clean_observaciones(self):
        """Sanitizar observaciones."""
        if self.observaciones:
            self.observaciones = strip_tags(self.observaciones).strip()
        return self.observaciones
    
    pagado = models.BooleanField(
        default=False,
        verbose_name="¿Pagado?"
    )
    
    def __str__(self):
        return f"Reserva #{self.id} - {self.cliente.nombre_completo} - Hab. {self.habitacion.numero}"
    
    # 🎯 PROPIEDADES CALCULADAS
    
    @property
    def noches(self):
        """
        Calcula número de noches.
        
        🐍 PYTHON: Resta de fechas da timedelta
        """
        # Validar que ambas fechas existan
        if not self.fecha_entrada or not self.fecha_salida:
            return 0
        
        delta = self.fecha_salida - self.fecha_entrada
        return delta.days
    
    @property
    def total_personas(self):
        """Total de personas (adultos + niños)"""
        return self.numero_adultos + self.numero_ninos
    
    @property
    def codigo_reserva(self):
        """Genera código de reserva único"""
        return f"RES-{self.id:06d}"  # 🐍 RES-000042
    
    # ✅ VALIDACIONES
    
    def clean(self):
        """
        Validaciones personalizadas antes de guardar.
        
        🐍 PYTHON: Método especial de Django para validar
        """
        from datetime import date

        # 1. Validar que salida sea posterior a entrada (solo si ambas fechas existen)
        if self.fecha_entrada and self.fecha_salida:
            if self.fecha_salida <= self.fecha_entrada:
                raise ValidationError('La fecha de salida debe ser posterior a la entrada')
        
        # 2. No permitir reservas en el pasado
        if self.fecha_entrada and self.fecha_entrada < date.today():
            raise ValidationError('No se pueden hacer reservas en fechas pasadas')
        
        # 3. Validar capacidad de la habitación
        if hasattr(self, 'habitacion') and self.habitacion:
            if self.total_personas > self.habitacion.capacidad:
                raise ValidationError(
                    f'La habitación solo tiene capacidad para {self.habitacion.capacidad} personas'
                )

        # 3.1 Validar IBAN básico si se informa
        if self.iban:
            iban_limpio = self.iban.replace(' ', '').upper()
            if not re.match(r'^[A-Z]{2}[0-9A-Z]{13,32}$', iban_limpio):
                raise ValidationError({'iban': 'IBAN inválido.'})
            self.iban = iban_limpio
        
        # 4. Validar disponibilidad (no solapar reservas)
        if hasattr(self, 'habitacion') and self.habitacion and self.fecha_entrada and self.fecha_salida:
            reservas_solapadas = Reserva.objects.filter(
                habitacion=self.habitacion,
                estado__in=['confirmada', 'en_curso', 'pendiente']
            ).exclude(id=self.id)  # 🐍 Excluir esta misma reserva si es edición
            
            for reserva in reservas_solapadas:
                # Verificar solapamiento de fechas
                if (self.fecha_entrada < reserva.fecha_salida and 
                    self.fecha_salida > reserva.fecha_entrada):
                    raise ValidationError(
                        f'La habitación ya está reservada del {reserva.fecha_entrada} al {reserva.fecha_salida}'
                    )
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir método save para calcular precio automáticamente.
        
        🐍 PYTHON: Sobrescribir métodos heredados
        """
        # Solo calcular si tenemos fechas y habitación
        if self.fecha_entrada and self.fecha_salida and self.habitacion:
            # Calcular precio si no está establecido
            if not self.precio_por_noche:
                self.precio_por_noche = self.habitacion.precio_con_vista()
            
            # Calcular precio total
            self.precio_total = self.precio_por_noche * self.noches
            
            # Aplicar descuento por estancia larga
            if self.noches >= 7:
                self.precio_total = self.precio_total * Decimal('0.90')
        else:
            # Si no hay datos suficientes, inicializar en 0
            if not self.precio_por_noche:
                self.precio_por_noche = Decimal('0.00')
            if not self.precio_total:
                self.precio_total = Decimal('0.00')
        
        # Llamar al save original
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_reserva']  # 🐍 - = descendente
        
        # Restricción a nivel de BD (comentado por compatibilidad)
        # constraints = [
        #     models.CheckConstraint(
        #         condition=models.Q(fecha_salida__gt=models.F('fecha_entrada')),
        #         name='fecha_salida_posterior_entrada'
        #     )
        # ]


class ViajeroCheckin(models.Model):
    """Datos legales de cada viajero para check-in online y SES Hospedajes."""

    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('X', 'No especificado'),
    ]
    TIPO_DOCUMENTO_CHOICES = [
        ('dni', 'DNI'),
        ('nie', 'NIE/TIE'),
        ('pasaporte', 'Pasaporte'),
        ('otro', 'Otro documento'),
    ]
    RELACION_CHOICES = [
        ('titular', 'Titular de la reserva'),
        ('conyuge', 'Cónyuge/pareja'),
        ('hijo', 'Hijo/a'),
        ('padre_madre', 'Padre/Madre'),
        ('familiar', 'Familiar'),
        ('amigo', 'Amigo/a'),
        ('otro', 'Otro'),
    ]

    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='viajeros_checkin'
    )
    orden = models.PositiveSmallIntegerField(default=1)

    nombre = models.CharField(max_length=100)
    primer_apellido = models.CharField(max_length=100)
    segundo_apellido = models.CharField(max_length=100, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)

    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES)
    numero_documento = models.CharField(max_length=30, blank=True)
    numero_soporte = models.CharField(max_length=30, blank=True)

    nacionalidad = models.CharField(max_length=80)
    fecha_nacimiento = models.DateField()

    direccion_residencia = models.CharField(max_length=200)
    ciudad_residencia = models.CharField(max_length=100)
    codigo_postal_residencia = models.CharField(max_length=12)
    pais_residencia = models.CharField(max_length=80, default='España')

    telefono_contacto = models.CharField(max_length=20)
    email_contacto = models.EmailField()

    relacion_con_titular = models.CharField(max_length=20, choices=RELACION_CHOICES, default='titular')
    es_menor_sin_documento = models.BooleanField(default=False)
    parentesco_menor_con_adulto = models.CharField(max_length=120, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        self.nombre = strip_tags(self.nombre).strip()
        self.primer_apellido = strip_tags(self.primer_apellido).strip()
        self.segundo_apellido = strip_tags(self.segundo_apellido).strip()
        self.numero_documento = strip_tags(self.numero_documento).strip().upper()
        self.numero_soporte = strip_tags(self.numero_soporte).strip().upper()
        self.nacionalidad = strip_tags(self.nacionalidad).strip()
        self.direccion_residencia = strip_tags(self.direccion_residencia).strip()
        self.ciudad_residencia = strip_tags(self.ciudad_residencia).strip()
        self.codigo_postal_residencia = strip_tags(self.codigo_postal_residencia).strip()
        self.pais_residencia = strip_tags(self.pais_residencia).strip()
        self.telefono_contacto = strip_tags(self.telefono_contacto).strip()
        self.parentesco_menor_con_adulto = strip_tags(self.parentesco_menor_con_adulto).strip()

        if self.es_menor_sin_documento:
            if not self.parentesco_menor_con_adulto:
                raise ValidationError({
                    'parentesco_menor_con_adulto': (
                        'Debes indicar la relación del menor con el adulto responsable.'
                    )
                })
        else:
            if not self.numero_documento:
                raise ValidationError({'numero_documento': 'El número de documento es obligatorio.'})
            if not self.numero_soporte:
                raise ValidationError({'numero_soporte': 'El número de soporte es obligatorio.'})

        if self.tipo_documento == 'dni' and self.numero_documento:
            validar_dni_nie(self.numero_documento)

        telefono_limpio = re.sub(r'[^0-9+]', '', self.telefono_contacto)
        if len(telefono_limpio) < 9:
            raise ValidationError({'telefono_contacto': 'Teléfono inválido. Debe tener al menos 9 dígitos.'})

    def __str__(self):
        return f"{self.nombre} {self.primer_apellido} - {self.reserva.codigo_reserva}"

    class Meta:
        verbose_name = 'Viajero de check-in'
        verbose_name_plural = 'Viajeros de check-in'
        ordering = ['orden', 'id']
        unique_together = [('reserva', 'orden')]


class MenuDelDia(models.Model):
    """Menú diario del restaurante."""

    fecha = models.DateField(
        default=date.today,
        unique=True,
        help_text="Fecha del menú"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Si hay varios menús activos, se muestra el más reciente"
    )
    consumicion_incluida = models.CharField(
        max_length=120,
        default="Incluye una consumición: vino, cerveza, refresco o agua"
    )
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"Menú del día {self.fecha}"

    class Meta:
        verbose_name = "Menú del día"
        verbose_name_plural = "Menús del día"
        ordering = ['-fecha']


class PlatoMenuDelDia(models.Model):
    """Platos asociados al menú diario."""

    CATEGORIA_CHOICES = [
        ('primero', 'Primer plato'),
        ('segundo', 'Segundo plato'),
        ('postre', 'Postre'),
    ]

    menu = models.ForeignKey(
        MenuDelDia,
        on_delete=models.CASCADE,
        related_name='platos'
    )
    categoria = models.CharField(max_length=10, choices=CATEGORIA_CHOICES)
    nombre = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=255, blank=True)
    orden = models.PositiveSmallIntegerField(default=1)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_categoria_display()}: {self.nombre}"

    class Meta:
        verbose_name = "Plato del menú del día"
        verbose_name_plural = "Platos del menú del día"
        ordering = ['categoria', 'orden', 'nombre']


class MenuEspecial(models.Model):
    """Menú especial del restaurante (eventos, temporada, degustación…)."""

    titulo = models.CharField(
        max_length=120,
        help_text="Ej: Menú de Semana Santa, Menú Degustación Gallego…"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción breve del menú especial"
    )
    precio = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=True, blank=True,
        help_text="Precio por persona (dejar vacío si no aplica)"
    )
    fecha_inicio = models.DateField(
        help_text="Primer día en que se ofrece el menú especial"
    )
    fecha_fin = models.DateField(
        help_text="Último día en que se ofrece el menú especial"
    )
    activo = models.BooleanField(default=True)
    consumicion_incluida = models.CharField(
        max_length=120, blank=True,
        help_text="Ej: Vino de la casa incluido"
    )
    notas = models.TextField(blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Menú especial"
        verbose_name_plural = "Menús especiales"
        ordering = ['fecha_inicio']


class PlatoMenuEspecial(models.Model):
    """Platos asociados a un menú especial."""

    CATEGORIA_CHOICES = [
        ('primero', 'Primer plato'),
        ('segundo', 'Segundo plato'),
        ('postre', 'Postre'),
        ('extra', 'Extra / Maridaje'),
    ]

    menu = models.ForeignKey(
        MenuEspecial,
        on_delete=models.CASCADE,
        related_name='platos'
    )
    categoria = models.CharField(max_length=10, choices=CATEGORIA_CHOICES)
    nombre = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=255, blank=True)
    orden = models.PositiveSmallIntegerField(default=1)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_categoria_display()}: {self.nombre}"

    class Meta:
        verbose_name = "Plato del menú especial"
        verbose_name_plural = "Platos del menú especial"
        ordering = ['categoria', 'orden', 'nombre']


# 🎓 RESUMEN DE CONCEPTOS PYTHON:
# - ForeignKey: Relaciones entre tablas
# - @property: Campos calculados
# - clean(): Validaciones personalizadas
# - save(): Lógica antes de guardar
# - Q objects: Consultas complejas
# - F expressions: Referencias a campos
