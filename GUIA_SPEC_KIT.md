# Guia: Spec-Driven Development con Spec-Kit para Hostal Rivera

Spec-Kit es un toolkit de GitHub que aplica **desarrollo guiado por especificaciones**: defines QUE construir antes de COMO construirlo, usando tu AI agent favorito (Copilot, Claude, Cursor, etc.).

---

## Que es y para que sirve

En vez de escribir prompts sueltos como "anade un sistema de facturacion", Spec-Kit te obliga a seguir un proceso:

1. **Constitucion** → Principios del proyecto (calidad, testing, seguridad)
2. **Spec** → Que quieres construir (requisitos, historias de usuario)
3. **Plan** → Como lo vas a construir (tech stack, arquitectura)
4. **Tasks** → Lista de tareas accionables
5. **Implement** → Ejecucion paso a paso

**Para Hostal Rivera**, Spec-Kit es util cuando:
- Anadir features grandes (facturacion, API REST, panel de estadisticas)
- Modernizar partes del codigo existente
- Documentar decisiones de arquitectura
- Mantener consistencia en el codigo a largo plazo

**NO es util para**:
- Bug fixes pequeños
- Cambios de una linea
- Cosas que ya sabes hacer de memoria

---

## Instalacion

### Paso 1: Instalar uv (si no lo tienes)

```bash
# En Arch Linux
pacman -S uv

# O con el instalador oficial
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Paso 2: Instalar Spec-Kit CLI

```bash
# Ver la ultima version en https://github.com/github/spec-kit/releases
# Por ejemplo, si la ultima es v0.12.11:
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.12.11

# O instalar la ultima version desde PyPI (mas facil):
uv tool install specify-cli
```

### Paso 3: Verificar instalacion

```bash
specify --version
```

### Paso 4: Inicializar en tu proyecto

```bash
cd /home/reiloop/Projects/hotel-manager
specify init . --integration copilot
```

Esto crea la estructura `.specify/` en tu proyecto con templates y comandos para tu AI agent.

---

## Flujo de trabajo con Hostal Rivera

### Ejemplo real: Anadir sistema de facturacion

Imagina que quieres anadir facturacion a las reservas de Hostal Rivera.

#### 1. Definir principios del proyecto

```
/speckit.constitution
```

El AI agent generara principios como:
- Las facturas deben cumplir normativa fiscal espanola
- Los datos de facturacion deben enlazarse con reservas existentes
- Las facturas se generan en PDF
- Solo usuarios admin pueden generar facturas

#### 2. Crear la especificacion

```
/speckit.specify
```

Describe QUE quieres:
> "Sistema de facturacion para Hostal Rivera que genere facturas PDF vinculadas a reservas. Cada factura incluye datos del cliente, detalle de la reserva (habitacion, fechas, precio), IVA aplicado, y numero de factura secuencial. Las facturas se pueden descargar desde el panel de admin y enviar por email al cliente."

El AI genera un documento `specs/` con:
- Requisitos funcionales
- Historias de usuario
- Criterios de aceptacion
- Casos borde

#### 3. Crear plan tecnico

```
/speckit.plan
```

Describe el tech stack:
> "Django 5.2.4, modelo Factura relacionado con Reserva, generacion PDF con Reportlab (ya instalado), endpoint de descarga, email con Django email backend, migraciones para nuevos campos."

El AI genera un plan con:
- Modelos nuevos a crear
- Vistas/URLs necesarias
- Templates a modificar
- Migraciones
- Tests requeridos

#### 4. Generar tareas

```
/speckit.tasks
```

Genera una lista de tareas ordenadas:
1. Crear modelo Factura con campos basicos
2. Crear migracion
3. Crear vista de listado de facturas
4. Crear vista de detalle de factura
5. Implementar generacion PDF
6. Endpoint de descarga
7. Email de factura al cliente
8. Tests unitarios
9. Tests de integracion

#### 5. Implementar

```
/speckit.implement
```

El AI agent ejecuta las tareas una a una, generando codigo, tests, y verificando que todo funciona.

---

## Comandos disponibles

| Comando | Cuando usarlo |
|---|---|
| `/speckit.constitution` | Al empezar un proyecto o feature grande |
| `/speckit.specify` | Para definir una nueva feature |
| `/speckit.clarify` | Cuando la spec tiene zonas grises |
| `/speckit.plan` | Para definir arquitectura y tech stack |
| `/speckit.tasks` | Para desglosar en tareas |
| `/speckit.analyze` | Para verificar consistencia entre spec y plan |
| `/speckit.checklist` | Para generar checklists de calidad |
| `/speckit.implement` | Para ejecutar la implementacion |
| `/speckit.converge` | Para verificar que el codigo coincide con la spec |

---

## Ideas de features para Hostal Rivera con Spec-Kit

### 1. Sistema de facturacion
- Facturas PDF vinculadas a reservas
- Numeracion secuencial
- IVA configurable
- Envio por email

### 2. API REST para integraciones
- Endpoints para reservas, habitaciones, clientes
- Autenticacion con tokens
- Documentacion OpenAPI/Swagger

### 3. Panel de estadisticas
- Ocupacion mensual/anual
- Ingresos por periodo
- Procedencia de clientes
- Graficos con Chart.js

### 4. Integracion SES Hospedajes mejorada
- Validacion automatica de DNI/NIE
- Exportacion en formato Guardia Civil
- Historial de envios

### 5. Sistema de notificaciones
- Email de confirmacion de reserva
- Recordatorio de check-in
- Alertas de overbooking

### 6. Multi-propiedad
- Soporte para gestionar varios hoteles
- Roles por propiedad
- Dashboard consolidado

---

## Cuando NO usar Spec-Kit

| Situacion | Mejor approach |
|---|---|
| Fix de bug pequeno | Escribir directamente el fix |
| Cambiar un color en CSS | Editar el archivo |
| Anadir un campo simple a un modelo | Hacerlo directamente con migrate |
| Actualizar dependencias | `pip install -U` y test |

---

## Integracion con tu AI agent

Spec-Kit funciona con **30+ AI agents**. Los mas comunes:

| Agent | Como usar Spec-Kit |
|---|---|
| **GitHub Copilot** (VS Code) | Slash commands `/speckit.*` |
| **Claude Code** | Skills mode o slash commands |
| **Cursor** | Slash commands en chat |
| **opencode** | Slash commands `/speckit.*` |

Para ver todos los agents soportados:
```bash
specify integration list
```

---

## Estructura que genera en tu proyecto

Despues de `specify init`:

```
hotel-manager/
 .specify/
 memory/ # Contexto del proyecto
 templates/ # Templates de specs, plans, tasks
 scripts/ # Scripts de apoyo
 specs/ # Specs generadas por feature
 001-facturacion/
 spec.md # Especificacion
 plan.md # Plan tecnico
 tasks.md # Lista de tareas
 .specify/ # Configuracion de Spec-Kit
 ... # Tu codigo existente
```

---

## Tips para Hostal Rivera

1. **Empieza con la constitucion**: Define principios de seguridad, testing, y GDPR antes de cualquier feature nueva
2. **Usa specs para features grandes**: Facturacion, API REST, estadisticas
3. **No abuses**: Para cambios pequenos, ve directo al codigo
4. **Commit las specs**: Las specs son documentacion valiosa, haz commit de ellas
5. **Evoluciona las specs**: Cuando cambie una feature, actualiza su spec

---

## Troubleshooting

### Error: "specify: command not found"
```bash
# Verificar que uv tool esta en el PATH
uv tool list
# Si specify-cli no aparece, reinstalar
uv tool install specify-cli
```

### Error al inicializar
```bash
# Verificar que estas en un repo git
git status
# Si no es un repo, inicializar
git init
```

### El AI agent no reconoce los comandos
- Verifica que la integracion es compatible: `specify integration list`
- Algunos agents requieren skills mode en vez de slash commands
- Revisa la documentacion del agent especifico

---

## Recursos

- [Documentacion oficial](https://github.github.io/spec-kit/)
- [Guia completa de Spec-Driven Development](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [Quick Start](https://github.github.io/spec-kit/quickstart.html)
- [Extensiones de la comunidad](https://github.github.io/spec-kit/community/extensions.html)
- [Presets](https://github.github.io/spec-kit/community/presets.html)
