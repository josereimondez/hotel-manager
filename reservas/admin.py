from django.contrib import admin
from django.utils.html import format_html
from .models import (Habitacion, Cliente, Reserva, MenuDelDia, PlatoMenuDelDia,
                     MenuEspecial, PlatoMenuEspecial, ViajeroCheckin,
                     ConsentimientoRGPD, RegistroAuditoria)


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    """Configuración del admin para Habitación."""

    list_display = ['numero', 'tipo', 'precio_base', 'capacidad', 'tiene_vista_mar', 'miniatura']

    list_filter = ['tipo', 'tiene_vista_mar', 'capacidad']

    search_fields = ['numero', 'descripcion']

    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'vista_previa_foto']

    ordering = ['numero']

    fieldsets = (
        ('Información Básica', {
            'fields': ('numero', 'tipo', 'capacidad')
        }),
        ('Precio', {
            'fields': ('precio_base', 'tiene_vista_mar')
        }),
        ('Imagen', {
            'fields': ('foto', 'vista_previa_foto')
        }),
        ('Descripción', {
            'fields': ('descripcion',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    # Métodos personalizados para mostrar imágenes

    def miniatura(self, obj):
        """Muestra miniatura en la lista."""
        if obj.foto:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.foto.url
            )
        return "Sin foto"

    miniatura.short_description = "Foto"

    def vista_previa_foto(self, obj):
        """Muestra preview grande en el formulario."""
        if obj.foto:
            return format_html(
                '<img src="{}" width="300" style="border-radius: 10px;" />',
                obj.foto.url
            )
        return "No hay foto cargada"

    vista_previa_foto.short_description = "Vista Previa"


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'dni_nie', 'email', 'telefono', 'es_vip', 'fecha_registro']
    list_filter = ['es_vip', 'pais', 'fecha_registro']
    search_fields = ['nombre', 'apellidos', 'dni_nie', 'email']
    readonly_fields = ['fecha_registro', 'edad']

    fieldsets = (
        ('Datos Personales', {
            'fields': ('nombre', 'apellidos', 'dni_nie', 'fecha_nacimiento', 'edad')
        }),
        ('Contacto', {
            'fields': ('email', 'telefono')
        }),
        ('Dirección', {
            'fields': ('direccion', 'ciudad', 'codigo_postal', 'pais'),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('notas', 'es_vip', 'fecha_registro')
        }),
    )


class ViajeroCheckinInline(admin.TabularInline):
    model = ViajeroCheckin
    extra = 0
    fields = [
        'orden', 'nombre', 'primer_apellido', 'segundo_apellido',
        'tipo_documento', 'numero_documento', 'numero_soporte',
        'nacionalidad', 'fecha_nacimiento', 'telefono_contacto',
        'relacion_con_titular', 'es_menor_sin_documento', 'parentesco_menor_con_adulto'
    ]


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['codigo_reserva', 'cliente', 'habitacion', 'fecha_entrada', 'fecha_salida',
                    'noches_display', 'precio_total', 'estado', 'pagado',
                    'checkin_online_completado', 'ses_hospedajes_enviado']
    list_filter = ['estado', 'pagado', 'fecha_entrada', 'fecha_reserva']
    search_fields = ['cliente__nombre', 'cliente__apellidos', 'cliente__dni_nie', 'habitacion__numero']
    readonly_fields = ['codigo_reserva', 'noches_display', 'precio_total', 'fecha_reserva']
    date_hierarchy = 'fecha_entrada'

    fieldsets = (
        ('Información de Reserva', {
            'fields': ('codigo_reserva', 'cliente', 'habitacion', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_entrada', 'fecha_salida', 'noches_display', 'fecha_reserva')
        }),
        ('Huéspedes', {
            'fields': ('numero_adultos', 'numero_ninos')
        }),
        ('Registro legal viajeros', {
            'fields': (
                'medio_pago', 'iban', 'relaciones_parentesco_adultos',
                'contrato_aceptado', 'checkin_online_completado',
                'checkin_online_omitido',
                'ses_hospedajes_enviado', 'ses_hospedajes_referencia'
            )
        }),
        ('Precio', {
            'fields': ('precio_por_noche', 'precio_total', 'pagado')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
    )

    autocomplete_fields = ['cliente', 'habitacion']
    inlines = [ViajeroCheckinInline]

    def noches_display(self, obj):
        """Muestra número de noches"""
        return f"{obj.noches} noche(s)"
    noches_display.short_description = "Noches"

    def codigo_reserva(self, obj):
        """Muestra código formateado"""
        if obj.id:
            return obj.codigo_reserva
        return "Se generará al guardar"
    codigo_reserva.short_description = "Código"


@admin.register(ViajeroCheckin)
class ViajeroCheckinAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'orden', 'nombre', 'primer_apellido', 'tipo_documento', 'numero_documento']
    list_filter = ['tipo_documento', 'sexo', 'nacionalidad', 'es_menor_sin_documento']
    search_fields = ['nombre', 'primer_apellido', 'numero_documento', 'reserva__id']


class PlatoMenuDelDiaInline(admin.TabularInline):
    model = PlatoMenuDelDia
    extra = 1
    fields = ['categoria', 'nombre', 'descripcion', 'orden', 'disponible']
    ordering = ['categoria', 'orden']


@admin.register(MenuDelDia)
class MenuDelDiaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'activo', 'consumicion_incluida']
    list_filter = ['activo', 'fecha']
    search_fields = ['consumicion_incluida', 'notas', 'platos__nombre']
    ordering = ['-fecha']
    inlines = [PlatoMenuDelDiaInline]

    def has_add_permission(self, request):
        return not MenuDelDia.objects.exists()


class PlatoMenuEspecialInline(admin.TabularInline):
    model = PlatoMenuEspecial
    extra = 1
    fields = ['categoria', 'nombre', 'descripcion', 'orden', 'disponible']
    ordering = ['categoria', 'orden']


admin.site.site_header = "Panel de Administración Hotel Rivera"
admin.site.site_title = "Admin Hotel Rivera"
admin.site.index_title = "Gestión del Hotel"


@admin.register(MenuEspecial)
class MenuEspecialAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha_inicio', 'fecha_fin', 'precio', 'activo']
    list_filter = ['activo', 'fecha_inicio']
    search_fields = ['titulo', 'descripcion', 'platos__nombre']
    ordering = ['-fecha_inicio']
    inlines = [PlatoMenuEspecialInline]


@admin.register(ConsentimientoRGPD)
class ConsentimientoRGPDAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'reserva', 'fecha_consentimiento', 'version_politica', 'revocado']
    list_filter = ['revocado', 'version_politica', 'fecha_consentimiento']
    search_fields = ['cliente__nombre', 'cliente__apellidos', 'cliente__dni_nie', 'reserva__id']
    readonly_fields = ['fecha_consentimiento', 'fecha_revocacion', 'ip_address', 'user_agent']
    date_hierarchy = 'fecha_consentimiento'

    fieldsets = (
        ('Información del Consentimiento', {
            'fields': ('reserva', 'cliente', 'fecha_consentimiento', 'version_politica')
        }),
        ('Texto Aceptado', {
            'fields': ('texto_consentimiento',),
            'classes': ('collapse',)
        }),
        ('Datos Técnicos', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Revocación', {
            'fields': ('revocado', 'fecha_revocacion', 'motivo_revocacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['fecha_accion', 'usuario', 'tipo_accion', 'entidad_tipo', 'entidad_id', 'descripcion_corta']
    list_filter = ['tipo_accion', 'entidad_tipo', 'fecha_accion', 'usuario']
    search_fields = ['descripcion', 'entidad_id', 'usuario__username']
    readonly_fields = ['fecha_accion', 'usuario', 'tipo_accion', 'entidad_tipo', 'entidad_id',
                       'descripcion', 'datos_anteriores', 'datos_nuevos', 'ip_address']
    date_hierarchy = 'fecha_accion'

    fieldsets = (
        ('Acción', {
            'fields': ('fecha_accion', 'usuario', 'tipo_accion')
        }),
        ('Entidad Afectada', {
            'fields': ('entidad_tipo', 'entidad_id', 'descripcion')
        }),
        ('Datos', {
            'fields': ('datos_anteriores', 'datos_nuevos'),
            'classes': ('collapse',)
        }),
        ('Técnico', {
            'fields': ('ip_address',),
            'classes': ('collapse',)
        }),
    )

    def descripcion_corta(self, obj):
        return obj.descripcion[:100] + '...' if len(obj.descripcion) > 100 else obj.descripcion
    descripcion_corta.short_description = "Descripción"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
