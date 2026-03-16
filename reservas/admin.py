from django.contrib import admin
from django.utils.html import format_html  # 👈 Para mostrar HTML
from .models import (Habitacion, Cliente, Reserva, MenuDelDia, PlatoMenuDelDia,
                     MenuEspecial, PlatoMenuEspecial, ViajeroCheckin)

# 🎓 CONCEPTO: Personalizar el panel de administración

@admin.register(Habitacion)  # 🐍 DECORADOR en Python
class HabitacionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Habitación.
    
    🐍 PYTHON QUE APRENDES:
    - Decoradores (@admin.register)
    - Herencia (ModelAdmin)
    - Tuplas y listas
    """
    
    # Columnas que se muestran en la lista
    list_display = ['numero', 'tipo', 'precio_base', 'capacidad', 'tiene_vista_mar', 'miniatura']  # 👈 Añadido
    
    # Filtros laterales
    list_filter = ['tipo', 'tiene_vista_mar', 'capacidad']
    
    # Buscador
    search_fields = ['numero', 'descripcion']
    
    # Campos de solo lectura
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'vista_previa_foto']  # 👈 Añadido
    
    # Ordenamiento por defecto
    ordering = ['numero']
    
    # Organización de campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero', 'tipo', 'capacidad')
        }),
        ('Precio', {
            'fields': ('precio_base', 'tiene_vista_mar')
        }),
        ('Imagen', {  # 👈 Nueva sección
            'fields': ('foto', 'vista_previa_foto')
        }),
        ('Descripción', {
            'fields': ('descripcion',),
            'classes': ('collapse',)  # Colapsado por defecto
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    # Ordenamiento por defecto
    ordering = ['numero']
    
    # 🎨 MÉTODOS PERSONALIZADOS PARA MOSTRAR IMÁGENES
    
    def miniatura(self, obj):
        """
        Muestra miniatura en la lista.
        
        🐍 PYTHON: Métodos, condicionales, format_html
        """
        if obj.foto:  # 🐍 Si tiene foto
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.foto.url
            )
        return "Sin foto"
    
    miniatura.short_description = "Foto"  # 🐍 Nombre de la columna
    
    def vista_previa_foto(self, obj):
        """
        Muestra preview grande en el formulario.
        
        🐍 PYTHON: Mismo concepto pero más grande
        """
        if obj.foto:
            return format_html(
                '<img src="{}" width="300" style="border-radius: 10px;" />',
                obj.foto.url
            )
        return "No hay foto cargada"
    
    vista_previa_foto.short_description = "Vista Previa"
    
    # Acciones personalizadas (comentadas por ahora, las activaremos después)
    # actions = ['aplicar_descuento']
    
    # def aplicar_descuento(self, request, queryset):
    #     """
    #     Acción personalizada: aplica 10% descuento a habitaciones seleccionadas.
    #     
    #     🐍 PYTHON: Métodos, bucles, operaciones
    #     """
    #     for habitacion in queryset:
    #         habitacion.precio_base = habitacion.precio_base * 0.9
    #         habitacion.save()
    #     
    #     self.message_user(request, f"Descuento aplicado a {queryset.count()} habitaciones")
    # 
    # aplicar_descuento.short_description = "Aplicar 10% descuento"


# 👤 ADMIN DE CLIENTES
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


# 📅 ADMIN DE RESERVAS
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
    date_hierarchy = 'fecha_entrada'  # 🐍 Navegación por fechas
    
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
    
    # Autocompletar campos relacionados (más rápido)
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


# 🎨 PERSONALIZACIÓN DEL PANEL DE ADMINISTRACIÓN
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
