# Research: Correccion de Defectos de Calidad y Autenticidad

**Feature**: 002-project-quality-overhaul
**Date**: 2026-08-14

## Research Tasks

### Task 1: Eliminacion de emojis en templates Django

**Pregunta**: Como eliminar emojis de templates Django sin romper funcionalidad?

**Decision**: Eliminacion directa de caracteres emoji, reemplazo por texto plano o iconos SVG inline.

**Rationale**: 
- Los emojis en templates son caracteres Unicode que no afectan logica de negocio
- Se pueden eliminar sin riesgo de romper funcionalidad
- Para navegacion e iconos, texto plano es mas profesional que emojis
- Si se desea mantener iconografia, usar SVG inline o clases CSS (Bootstrap Icons)

**Alternativas consideradas**:
- Reemplazar con imagenes PNG: innecesario, aumenta complejidad
- Usar libreria de iconos externa: no vale la pena para este caso
- Mantener algunos emojis "decorativos": viola constitucion y objetivo de eliminar apariencia IA

**Metodo de verificacion**:
```bash
# Buscar emojis en templates
grep -rP '[\x{1F300}-\x{1F9FF}]' reservas/templates/

# Verificar que no quedan emojis
find reservas/templates/ -name "*.html" -exec grep -lP '[\x{1F300}-\x{1F9FF}]' {} \;
```

---

### Task 2: Actualizacion de archivos .po/.mo al eliminar emojis

**Pregunta**: Como manejar archivos de traduccion cuando se eliminan emojis de cadenas traducibles?

**Decision**: 
1. Buscar emojis en archivos .po
2. Eliminar emojis de las cadenas (msgid y msgstr)
3. Ejecutar `python manage.py compilemessages` para recompilar .mo
4. Commitear ambos (.po y .mo actualizados)

**Rationale**:
- La constitucion exige commitear .po y .mo juntos
- Si una cadena fuente (msgid) cambia, las traducciones (msgstr) deben actualizarse
- `compilemessages` usa `msgfmt` (disponible en el sistema segun AGENTS.md)

**Alternativas consideradas**:
- No tocar .po/.mo: dejaria cadenas inconsistentes
- Regenerar .po desde cero: perderia traducciones existentes
- Usar script custom compile_mo.py: es fallback, preferir manage.py compilemessages

**Metodo de verificacion**:
```bash
# Buscar emojis en .po
grep -P '[\x{1F300}-\x{1F9FF}]' locale/*/LC_MESSAGES/django.po

# Recompilar mensajes
python manage.py compilemessages

# Verificar que .mo se actualizo
ls -lh locale/*/LC_MESSAGES/django.mo
```

---

### Task 3: Eliminacion de db.sqlite3 del tracking git

**Pregunta**: Como eliminar db.sqlite3 del repositorio git sin perderlo localmente?

**Decision**: 
```bash
git rm --cached db.sqlite3
git commit -m "chore: elimina db.sqlite3 del tracking (debe estar en .gitignore)"
```

**Rationale**:
- `git rm --cached` elimina el archivo del tracking pero lo mantiene en el sistema de archivos local
- .gitignore ya deberia excluir db.sqlite3 (verificar)
- Esto no afecta la base de datos de desarrollo local

**Alternativas consideradas**:
- `git rm db.sqlite3`: eliminaria el archivo localmente (no deseado)
- Dejarlo commiteado: viola .gitignore y constitucion
- Renombrarlo a db.sqlite3.example: innecesario, es una base de datos vacia

**Metodo de verificacion**:
```bash
# Verificar que ya no esta trackeado
git ls-files | grep db.sqlite3
# (no debe mostrar nada)

# Verificar que .gitignore lo excluye
grep "db.sqlite3" .gitignore
```

---

### Task 4: Reemplazo de emojis en navegacion e iconos

**Pregunta**: Que usar como reemplazo de emojis en navbar, footer e iconos de servicio?

**Decision**: Texto plano con formato CSS para iconos de navegacion. Para iconos de servicio (WiFi, parking, etc.), usar texto descriptivo o eliminar si es redundante.

**Rationale**:
- Texto plano es mas profesional y accesible
- No requiere dependencias externas
- Mantiene la funcionalidad sin apariencia de plantilla
- Ejemplos:
  - `🏠 Inicio` → `Inicio`
  - `🛏️ Habitaciones` → `Habitaciones`
  - `📶 Wi-Fi gratis` → `Wi-Fi gratuito` (o eliminar si es informacion redundante)

**Alternativas consideradas**:
- Bootstrap Icons: requiere CDN adicional, no vale la pena
- Font Awesome: misma razon
- SVG inline: demasiado verbose para este caso
- Imagenes: innecesario

**Metodo de verificacion**:
- Inspeccion visual de templates actualizados
- Verificar que navegacion sigue siendo clara y usable

---

### Task 5: Verificacion de eliminacion de placeholders

**Pregunta**: Como asegurar que todos los placeholders fueron reemplazados?

**Decision**: Busqueda exhaustiva con patrones conocidos antes de commitear.

**Patrones a buscar**:
```bash
# TU_USUARIO
grep -r "TU_USUARIO" . --include="*.md" --include="*.html" --include="*.py"

# Hotel Paradise
grep -r "Hotel Paradise" . --include="*.html"

# Telefonos placeholder
grep -r "+34-XXX-XXX-XXX" . --include="*.html"

# Enlaces sociales vacios
grep -r 'href="#"' reservas/templates/ --include="*.html"
```

**Rationale**:
- Busqueda automatizada garantiza cobertura completa
- Patrones conocidos permiten verificacion rapida
- Debe ejecutarse antes de cada commit

**Alternativas consideradas**:
- Revision manual: propenso a errores
- Script custom: innecesario, grep es suficiente

**Metodo de verificacion**:
```bash
# Script de verificacion completo
echo "Buscando placeholders..."
echo "TU_USUARIO:" && grep -r "TU_USUARIO" . --include="*.md" --include="*.html" --include="*.py" | wc -l
echo "Hotel Paradise:" && grep -r "Hotel Paradise" . --include="*.html" | wc -l
echo "+34-XXX:" && grep -r "+34-XXX-XXX-XXX" . --include="*.html" | wc -l
echo "href='#':" && grep -r 'href="#"' reservas/templates/ --include="*.html" | wc -l
# Todos deben retornar 0
```

---

### Task 6: Actualizacion de versiones en documentacion

**Pregunta**: Como asegurar consistencia de versiones entre documentacion y codigo?

**Decision**: 
1. Extraer version real de requirements.txt: `Django==5.2.4`
2. Buscar todas las menciones de version en .md
3. Actualizar a 5.2.4
4. Para numero de modelos, contar en models.py: 7+ modelos

**Patrones a buscar**:
```bash
# Versiones antiguas de Django
grep -r "Django==5.0" . --include="*.md"
grep -r "Django 5.0" . --include="*.md"

# Numero incorrecto de modelos
grep -r "3 modelos" . --include="*.md"
grep -r "Modelos: 3" . --include="*.md"
```

**Rationale**:
- requirements.txt es la fuente de verdad (segun AGENTS.md)
- Actualizar todos los documentos a la version real
- Contar modelos directamente del codigo

**Alternativas consideradas**:
- Dejar inconsistencias: inaceptable
- Usar variables en docs: demasiado complejo para Markdown

**Metodo de verificacion**:
```bash
# Verificar que no quedan versiones antiguas
grep -r "Django==5.0" . --include="*.md" | wc -l  # Debe ser 0
grep -r "3 modelos" . --include="*.md" | wc -l    # Debe ser 0
```

---

### Task 7: Eliminacion de documentacion redundante

**Pregunta**: Que archivos eliminar y como asegurar que no se pierde informacion critica?

**Decision**: 
Eliminar los siguientes archivos:
- `RESUMEN_GITHUB.md`: 100% redundante con README
- `GITHUB_CHECKLIST.md`: guia basica de git, no es doc del proyecto
- `APRENDIZAJE_PYTHON.md`: tutorial de Python, no es doc del proyecto
- `verify_github_ready.py`: script de portfolio, no herramienta del producto

**Rationale**:
- Estos archivos inflan artificialmente el repositorio
- No aportan valor al producto final
- Delatan que es un proyecto de portfolio/learning
- La informacion critica ya esta en README, DEPLOYMENT, SECURITY

**Alternativas consideradas**:
- Mover a carpeta /docs: sigue siendo redundante
- Consolidar en README: RESUMEN_GITHUB ya es un resumen, no vale la pena
- Mantenerlos: viola objetivo de profesionalizacion

**Metodo de verificacion**:
```bash
# Verificar que se eliminaron
ls *.md | grep -E "(RESUMEN_GITHUB|GITHUB_CHECKLIST|APRENDIZAJE_PYTHON)"
# No debe mostrar nada

ls *.py | grep "verify_github_ready"
# No debe mostrar nada
```

---

### Task 8: Creacion de narrativa para README

**Pregunta**: Como crear una narrativa autentica para el Hostal Rivera?

**Decision**: Incluir en README:
1. **Que es**: Sistema de gestion para Hostal Rivera, ubicado en Becerrea, Lugo (Galicia)
2. **Contexto**: Hostal en el Camino de Santiago (Via Kunig), zona rural gallega
3. **Problema que resuelve**: Gestion de reservas, check-in, cumplimiento normativo espanol (SES Hospedajes)
4. **Caracteristicas unicas**: Multiidioma (ES/GL/EN), integracion con normativa espanola, menu del dia

**Rationale**:
- Becerrea es un lugar real con coordenadas geograficas reales
- La Via Kunig es una ruta real del Camino de Santiago
- El telefono +34 982 360 185 usa prefijo 982 (provincia de Lugo)
- Estos detalles dan autenticidad al proyecto

**Alternativas consideradas**:
- Dejar README generico: delata proyecto artificial
- Inventar historia falsa: poco etico
- No incluir narrativa: pierde oportunidad de diferenciacion

**Metodo de verificacion**:
- Leer el nuevo README y evaluar si responde: que es, donde esta, para quien es, que problema resuelve

---

### Task 9: Correccion de bandera de galego

**Pregunta**: Como corregir la bandera de galego en el selector de idioma?

**Decision**: Reemplazar bandera de Espana por texto "Galego" o simbolo propio.

**Rationale**:
- Galego no tiene bandera oficial ISO estandar
- Usar bandera de Espana es incorrecto politicamente
- Texto "Galego" es claro y profesional
- Alternativa: usar simbolo proprio si existe

**Alternativas consideradas**:
- Dejar bandera de Espana: incorrecto
- Usar bandera de Galicia (oficial): no es estandar en Unicode
- Texto "GL": menos claro que "Galego"

**Metodo de verificacion**:
- Inspeccionar base.html, buscar selector de idioma
- Verificar que galego no usa bandera de Espana

---

### Task 10: Eliminacion de directorios de imagenes vacios

**Pregunta**: Que hacer con directorios de imagenes que solo contienen README.txt?

**Decision**: Eliminar directorios y sus README.txt:
- `static/images/galeria/`
- `static/images/iconos/`
- `static/images/via_kunig/`

**Rationale**:
- Solo contienen README.txt (placeholders)
- No hay imagenes reales
- Mantenerlos senala contenido incompleto
- Los templates no referencian estas imagenes (verificar)

**Alternativas consideradas**:
- Llenar con imagenes placeholder: no resuelve el problema
- Mantener README.txt: senala proyecto incompleto
- Mover a otro directorio: innecesario

**Metodo de verificacion**:
```bash
# Verificar que no hay referencias en templates
grep -r "galeria/" reservas/templates/
grep -r "iconos/" reservas/templates/
grep -r "via_kunig/" reservas/templates/
# Todos deben retornar 0 resultados

# Eliminar directorios
rm -rf static/images/galeria/
rm -rf static/images/iconos/
rm -rf static/images/via_kunig/
```

---

## Summary of Decisions

| Task | Decision | Risk | Mitigation |
|------|----------|------|------------|
| 1. Eliminar emojis | Eliminacion directa | Bajo | Busqueda exhaustiva post-cambio |
| 2. Actualizar .po/.mo | Recompilar con compilemessages | Medio | Verificar que tests pasan |
| 3. Eliminar db.sqlite3 | git rm --cached | Bajo | Verificar .gitignore |
| 4. Reemplazo emojis | Texto plano | Bajo | Inspeccion visual |
| 5. Verificar placeholders | grep con patrones | Bajo | Script de verificacion |
| 6. Actualizar versiones | Buscar y reemplazar | Bajo | Doble verificacion |
| 7. Eliminar docs redundantes | rm directo | Bajo | Verificar que no hay enlaces |
| 8. Narrativa README | Incluir contexto real | Bajo | Revision humana |
| 9. Bandera galego | Texto "Galego" | Bajo | Inspeccion visual |
| 10. Directorios vacios | rm -rf | Bajo | Verificar referencias antes |

## Next Steps

1. Ejecutar Phase 1: generar data-model.md, quickstart.md
2. Proceder a /speckit.tasks para descomponer en tareas
3. Implementar cambios siguiendo tareas
4. Verificar con tests y busqueda de placeholders
