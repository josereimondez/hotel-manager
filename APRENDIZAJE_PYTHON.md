# 🐍 Guía Intensiva de Python para el Proyecto Hotelero

Esta guía te enseña Python **haciendo**, no leyendo teoría. Cada concepto se aplica directamente al proyecto.

## 📖 Índice por Nivel

1. [Conceptos Básicos](#1-conceptos-básicos)
2. [Programación Orientada a Objetos](#2-programación-orientada-a-objetos)
3. [Trabajar con Datos](#3-trabajar-con-datos)
4. [Funciones y Lógica](#4-funciones-y-lógica)
5. [Fechas y Tiempo](#5-fechas-y-tiempo)
6. [Django ORM](#6-django-orm)

---

## 1. Conceptos Básicos

### Variables y Tipos de Datos

```python
# En el proyecto verás esto:
numero_habitacion = "101"           # String (texto)
precio_noche = 89.99                # Float (decimal)
capacidad = 2                        # Integer (entero)
tiene_vista_mar = True              # Boolean (verdadero/falso)
servicios = None                     # None (nulo)

# Conversiones
precio_total = int(precio_noche * 3)  # 269 (convertir a entero)
habitacion_str = str(101)              # "101" (convertir a texto)
```

**Dónde lo usarás**: En cada modelo, vista y función del proyecto.

### Strings (Cadenas de texto)

```python
# Concatenación
nombre_hotel = "Hotel " + "Paraíso"

# F-strings (moderno y recomendado)
habitacion = 205
mensaje = f"La habitación {habitacion} está disponible"

# Métodos útiles
nombre = "  Juan Pérez  "
nombre.strip()      # "Juan Pérez" (quitar espacios)
nombre.upper()      # "  JUAN PÉREZ  "
nombre.lower()      # "  juan pérez  "
nombre.title()      # "  Juan Pérez  "

# En el proyecto:
def generar_codigo_reserva(self):
    return f"RES-{self.id:05d}"  # RES-00042
```

---

## 2. Programación Orientada a Objetos

### Clases y Objetos

```python
# ANTES: Manera antigua (diccionarios)
habitacion = {
    'numero': '101',
    'tipo': 'doble',
    'precio': 89.99
}

# AHORA: Con clases (Django models)
class Habitacion(models.Model):
    numero = models.CharField(max_length=10)
    tipo = models.CharField(max_length=20)
    precio_base = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Constructor (se ejecuta al crear)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ocupada = False
    
    # Método personalizado
    def calcular_precio(self, noches):
        return self.precio_base * noches
    
    # Representación como string
    def __str__(self):
        return f"Habitación {self.numero} - {self.tipo}"
```

**Concepto clave**: Una clase es un "molde", un objeto es una "copia" del molde.

```python
# Crear objetos (instancias)
hab_101 = Habitacion(numero="101", tipo="doble", precio_base=89.99)
hab_102 = Habitacion(numero="102", tipo="suite", precio_base=150.00)

# Usar métodos
total = hab_101.calcular_precio(3)  # 269.97
```

### Herencia

```python
# Clase padre
class Alojamiento(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    
    class Meta:
        abstract = True  # No crea tabla, solo hereda

# Clase hija (hereda de Alojamiento)
class Hotel(Alojamiento):
    numero_estrellas = models.IntegerField()
    tiene_piscina = models.BooleanField()
    
# Hotel tiene: nombre, direccion, numero_estrellas, tiene_piscina
```

### Properties (Propiedades calculadas)

```python
class Reserva(models.Model):
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    precio_por_noche = models.DecimalField(max_digits=6, decimal_places=2)
    
    @property  # Se usa como atributo, no como método
    def noches(self):
        delta = self.fecha_salida - self.fecha_entrada
        return delta.days
    
    @property
    def precio_total(self):
        return self.precio_por_noche * self.noches

# Uso:
reserva = Reserva(fecha_entrada=..., fecha_salida=..., precio_por_noche=100)
print(reserva.noches)         # 3 (sin paréntesis!)
print(reserva.precio_total)   # 300
```

---

## 3. Trabajar con Datos

### Listas

```python
# Lista de tipos de habitación
tipos = ["individual", "doble", "suite", "familiar"]

# Acceder por índice (empieza en 0)
tipos[0]   # "individual"
tipos[-1]  # "familiar" (último)

# Métodos útiles
tipos.append("presidencial")      # Añadir al final
tipos.insert(0, "económica")      # Insertar en posición
tipos.remove("suite")             # Eliminar por valor
tipos.pop()                       # Eliminar último

# Iterar
for tipo in tipos:
    print(f"Tipo: {tipo}")

# List comprehension (super útil!)
precios = [50, 80, 120, 150]
precios_con_iva = [p * 1.10 for p in precios]
# [55.0, 88.0, 132.0, 165.0]

# En el proyecto:
habitaciones_disponibles = [h for h in Habitacion.objects.all() 
                           if h.esta_disponible()]
```

### Diccionarios

```python
# Pares clave-valor
habitacion = {
    'numero': '101',
    'tipo': 'doble',
    'precio': 89.99,
    'ocupada': False
}

# Acceso
habitacion['numero']           # '101'
habitacion.get('wifi', True)   # True (valor por defecto)

# Iterar
for clave, valor in habitacion.items():
    print(f"{clave}: {valor}")

# En el proyecto (contexto para templates):
def vista_habitacion(request, id):
    hab = Habitacion.objects.get(id=id)
    context = {
        'habitacion': hab,
        'disponible': hab.esta_disponible(),
        'precio_fin_semana': hab.precio_base * 1.2
    }
    return render(request, 'habitacion.html', context)
```

### Tuplas (inmutables)

```python
# No se pueden modificar después de crear
coordenadas = (40.4168, -3.7038)  # Madrid
tipos_habitacion = ('individual', 'doble', 'suite')

# Desempaquetado
latitud, longitud = coordenadas
```

---

## 4. Funciones y Lógica

### Definir Funciones

```python
# Función simple
def saludar(nombre):
    return f"Hola, {nombre}"

# Parámetros con valor por defecto
def calcular_precio(base, noches=1, descuento=0):
    subtotal = base * noches
    return subtotal * (1 - descuento)

# Uso:
calcular_precio(100)              # 100 (1 noche, sin descuento)
calcular_precio(100, 3)           # 300 (3 noches)
calcular_precio(100, 3, 0.1)      # 270 (3 noches, 10% descuento)
calcular_precio(base=100, descuento=0.15, noches=2)  # 170 (orden diferente)
```

### Condicionales

```python
def clasificar_reserva(dias_antelacion):
    if dias_antelacion > 30:
        return "Reserva anticipada - 10% descuento"
    elif dias_antelacion > 7:
        return "Reserva normal"
    else:
        return "Reserva de última hora - 20% recargo"

# Operadores lógicos
def puede_reservar(tiene_dni, es_mayor_edad, acepta_terminos):
    if tiene_dni and es_mayor_edad and acepta_terminos:
        return True
    else:
        return False
    
    # Versión corta:
    return tiene_dni and es_mayor_edad and acepta_terminos
```

### Try-Except (Manejo de errores)

```python
# Sin manejo de errores (malo)
def obtener_habitacion(numero):
    return Habitacion.objects.get(numero=numero)  # Error si no existe

# Con manejo de errores (bueno)
def obtener_habitacion(numero):
    try:
        return Habitacion.objects.get(numero=numero)
    except Habitacion.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

# En vistas Django:
def vista_reserva(request, id):
    try:
        reserva = Reserva.objects.get(id=id)
    except Reserva.DoesNotExist:
        return HttpResponseNotFound("Reserva no encontrada")
    
    return render(request, 'reserva.html', {'reserva': reserva})
```

---

## 5. Fechas y Tiempo

```python
from datetime import datetime, date, timedelta

# Fecha actual
hoy = date.today()                    # 2026-02-18
ahora = datetime.now()                # 2026-02-18 15:30:45

# Crear fechas específicas
checkin = date(2026, 3, 15)           # 15 de marzo 2026
checkout = date(2026, 3, 18)          # 18 de marzo 2026

# Operaciones con fechas
estancia = checkout - checkin         # timedelta(days=3)
noches = estancia.days                # 3

# Sumar/restar días
mañana = hoy + timedelta(days=1)
la_semana_pasada = hoy - timedelta(weeks=1)

# Comparaciones
if checkin > hoy:
    print("Reserva futura")

# Formato personalizado
fecha_str = checkin.strftime("%d/%m/%Y")  # "15/03/2026"
mes_año = checkin.strftime("%B %Y")        # "March 2026"

# En el proyecto:
def validar_fechas(entrada, salida):
    if salida <= entrada:
        raise ValueError("La salida debe ser posterior a la entrada")
    if entrada < date.today():
        raise ValueError("No se pueden hacer reservas en el pasado")
    if (salida - entrada).days > 30:
        raise ValueError("Máximo 30 noches por reserva")
```

---

## 6. Django ORM

### Queries Básicos

```python
# Obtener todos
habitaciones = Habitacion.objects.all()

# Filtrar
dobles = Habitacion.objects.filter(tipo='doble')
baratas = Habitacion.objects.filter(precio_base__lt=100)  # __lt = less than

# Encadenar filtros
dobles_baratas = Habitacion.objects.filter(
    tipo='doble',
    precio_base__lt=100
)

# Excluir
no_suites = Habitacion.objects.exclude(tipo='suite')

# Obtener uno
hab_101 = Habitacion.objects.get(numero='101')

# Obtener o crear
habitacion, created = Habitacion.objects.get_or_create(
    numero='205',
    defaults={'tipo': 'doble', 'precio_base': 95}
)

# Contar
total = Habitacion.objects.count()
suites = Habitacion.objects.filter(tipo='suite').count()

# Ordenar
por_precio = Habitacion.objects.order_by('precio_base')  # Ascendente
mas_caras = Habitacion.objects.order_by('-precio_base')  # Descendente

# Primero/Último
mas_barata = Habitacion.objects.order_by('precio_base').first()
mas_cara = Habitacion.objects.order_by('-precio_base').first()

# Existe
existe = Habitacion.objects.filter(numero='101').exists()
```

### Queries Avanzados

```python
from django.db.models import Q, Count, Sum, Avg

# OR (cualquiera de las condiciones)
lujo = Habitacion.objects.filter(
    Q(tipo='suite') | Q(precio_base__gt=150)
)

# AND complejo
disponibles = Habitacion.objects.filter(
    Q(tipo='doble') & Q(precio_base__lt=100) & ~Q(estado='mantenimiento')
)

# Agregaciones
from django.db.models import Sum, Avg, Count

# Total de ingresos
total_ingresos = Reserva.objects.aggregate(
    total=Sum('precio_total')
)['total']

# Promedio de noches
promedio = Reserva.objects.aggregate(
    media=Avg('noches')
)['media']

# Contar reservas por habitación
stats = Habitacion.objects.annotate(
    num_reservas=Count('reserva')
).filter(num_reservas__gt=10)

# En el proyecto (dashboard):
def estadisticas_mes():
    return {
        'reservas_totales': Reserva.objects.filter(
            fecha_entrada__month=date.today().month
        ).count(),
        'ingresos': Reserva.objects.filter(
            fecha_entrada__month=date.today().month
        ).aggregate(Sum('precio_total'))['precio_total__sum'],
        'ocupacion': calcular_ocupacion()
    }
```

### Relaciones

```python
# ForeignKey (muchos a uno)
class Reserva(models.Model):
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)

# Uso:
reserva = Reserva.objects.get(id=1)
print(reserva.habitacion.numero)     # Acceso directo
print(reserva.cliente.nombre)

# Inverso:
habitacion = Habitacion.objects.get(numero='101')
reservas = habitacion.reserva_set.all()  # Todas las reservas de esta habitación

# ManyToMany (muchos a muchos)
class Reserva(models.Model):
    servicios_extra = models.ManyToManyField(Servicio)

# Uso:
reserva.servicios_extra.add(spa, desayuno)
reserva.servicios_extra.all()
```

---

## 🎯 Ejercicios Prácticos

### Ejercicio 1: Función de Validación
```python
def validar_capacidad(habitacion, num_personas):
    """
    Valida que el número de personas no exceda la capacidad.
    Retorna True si es válido, False si no.
    """
    # TU CÓDIGO AQUÍ
    pass
```

### Ejercicio 2: Calcular Precio con Descuentos
```python
def calcular_precio_final(precio_base, noches, es_temporada_alta, tiene_descuento_fidelidad):
    """
    - Temporada alta: +30%
    - Descuento fidelidad: -15%
    - Si estancia > 7 noches: -10% adicional
    """
    # TU CÓDIGO AQUÍ
    pass
```

### Ejercicio 3: Buscar Habitaciones Disponibles
```python
def habitaciones_disponibles(fecha_inicio, fecha_fin, tipo=None):
    """
    Retorna lista de habitaciones que NO tienen reservas
    en el rango de fechas especificado.
    """
    # TU CÓDIGO AQUÍ
    pass
```

---

## 🔥 Consejos Pro

1. **Usa el shell de Django para practicar**:
   ```bash
   python manage.py shell
   ```

2. **Debug con print()** al principio:
   ```python
   print(f"Valor de variable: {variable}")
   print(f"Tipo: {type(variable)}")
   ```

3. **Lee los errores de abajo hacia arriba**:
   ```
   La última línea dice QUÉ falló
   Las anteriores dicen DÓNDE falló
   ```

4. **Consulta la documentación**:
   - Django: https://docs.djangoproject.com/
   - Python: https://docs.python.org/es/3/

5. **Experimenta en el shell**:
   ```python
   >>> from reservas.models import Habitacion
   >>> h = Habitacion.objects.first()
   >>> dir(h)  # Ver todos los métodos
   >>> help(h.save)  # Ver documentación
   ```

---

**Siguiente paso**: Abre `models.py` y empieza a crear tus modelos. ¡Aprenderás Python haciendo! 🚀
