# Feature Specification: Correccion de Defectos de Calidad y Autenticidad

**Feature Branch**: `002-project-quality-overhaul`

**Created**: 2026-08-14

**Status**: Draft

**Input**: User description: "crear una nueva spec que defina como debe desarrollarse el proyecto en base a corregir los defectos encontrados en la anterior iteracion"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Eliminacion de apariencia generada por IA (Priority: P1)

Un visitante tecnico o reclutador que revise el repositorio en GitHub debe percibir un proyecto profesional, sin senales evidentes de generacion masiva por IA. Esto incluye la eliminacion de emojis decorativos excesivos en templates y documentacion, y la adopcion de un tono tecnico sobrio y directo.

**Why this priority**: La constitucion del proyecto prohbe explicitamente los emojis en documentacion y codigo. Ademas, el exceso de emojis (~441 instancias) es el principal indicador de contenido generado por IA y reduce la credibilidad del proyecto ante audiencia tecnica.

**Independent Test**: Se puede verificar contando instancias de emojis en templates HTML y archivos Markdown. El resultado esperado es cero emojis en todo el proyecto.

**Acceptance Scenarios**:

1. **Given** un template HTML del proyecto, **When** se inspecciona su contenido, **Then** no contiene ningun emoji ni icono Unicode decorativo.
2. **Given** un archivo Markdown de documentacion, **When** se revisa, **Then** no contiene emojis en titulos, listas ni cuerpo del texto.
3. **Given** el archivo RESUMEN_GITHUB.md (83 emojis), **When** se reescribe, **Then** mantiene la informacion util pero sin ningun emoji y con formato profesional.
4. **Given** los templates con iconos de navegacion (navbar, footer), **When** se actualizan, **Then** usan iconos SVG o texto plano en lugar de emojis.

---

### User Story 2 - Correccion de placeholders y contenido sin personalizar (Priority: P1)

Un desarrollador o maintainer que clone el repositorio no debe encontrar texto placeholder sin resolver como "TU_USUARIO", "Hotel Paradise", "+34-XXX-XXX-XXX", ni enlaces sociales con "#". Todo el contenido debe reflejar la identidad real del proyecto: Hostal Rivera.

**Why this priority**: Los placeholders sin resolver son el segundo indicador mas evidente de proyecto generado por IA o plantilla sin personalizar. Ademas, referencias a "Hotel Paradise" (nombre anterior) en 4 templates indican trabajo incompleto.

**Independent Test**: Se puede verificar buscando patrones de placeholder en todo el codigo y documentacion. El resultado esperado es cero ocurrencias de placeholders conocidos.

**Acceptance Scenarios**:

1. **Given** el codigo fuente y la documentacion, **When** se busca "TU_USUARIO", **Then** no se encuentra ninguna ocurrencia (12 sitios documentados deben corregirse).
2. **Given** los templates HTML, **When** se revisan las etiquetas `<title>`, **Then** ninguna contiene "Hotel Paradise" (4 templates afectados: login, registro, listado_habitaciones, mis_reservas).
3. **Given** los templates y paginas legales, **When** se buscan numeros de telefono, **Then** no aparecen numeros con formato "+34-XXX-XXX-XXX" (3 sitios afectados).
4. **Given** los enlaces de redes sociales en el footer, **When** se inspeccionan, **Then** o bien apuntan a URLs reales del hostal o bien se eliminan si no existen cuentas reales.
5. **Given** las referencias a imagenes (og-image.jpg, restaurant.jpg, galeria), **When** se verifican, **Then** o bien existen los archivos en static/ o bien se eliminan las referencias rotas.

---

### User Story 3 - Resolucion de inconsistencias entre documentacion y codigo (Priority: P1)

Un desarrollador que lea la documentacion del proyecto debe encontrar informacion coherente con el estado real del codigo. Versiones de dependencias, numero de modelos, estructura de directorios y comandos deben coincidir entre README, AGENTS.md, CHANGELOG, RESUMEN_GITHUB.md y el codigo fuente.

**Why this priority**: Las inconsistencias entre documentacion y codigo generan confusion, errores en el onboarding de nuevos desarrolladores, y fallos en agentes de IA que usan AGENTS.md como instruccion. La version de Django incorrecta en AGENTS.md es particularmente critica.

**Independent Test**: Se puede verificar comparando datos especificos entre documentacion y codigo. El resultado esperado es coincidencia total en versiones, conteo de modelos y estructura.

**Acceptance Scenarios**:

1. **Given** AGENTS.md, **When** se lee la version de Django indicada, **Then** coincide con requirements.txt (Django==5.2.4).
2. **Given** RESUMEN_GITHUB.md, **When** se listan las dependencias, **Then** las versiones coinciden con requirements.txt actual (Django 5.2.4, Pillow 11.1.0, etc.).
3. **Given** cualquier documento que mencione el numero de modelos, **When** se verifique, **Then** indica 7+ modelos (no 3 como dicen algunos documentos desactualizados).
4. **Given** la documentacion que describe la estructura de static/, **When** se对比 con el sistema de archivos real, **Then** no menciona directorios inexistentes (css/, js/) o se anota que el CSS/JS proviene de CDN.
5. **Given** CHANGELOG.md, **When** se revisa, **Then** refleja la actualizacion de Django 5.0 a 5.2.4 correctamente.
6. **Given** GUIA_SPEC_KIT.md, **When** se revisa la version de Django mencionada, **Then** indica 5.2.4 en lugar de 5.0.2.

---

### User Story 4 - Creacion de narrativa e historia del proyecto (Priority: P1)

Un visitante del repositorio debe poder entender en el README que es Hostal Rivera, por que existe, cual es su contexto real (ubicacion en Becerrea, Lugo), y que problema resuelve. El proyecto debe tener una identidad propia, no parecer una plantilla generica de hotel.

**Why this priority**: La falta de historia y contexto es lo que mas delata un proyecto artificial. Un README con narrativa real, contexto geografico y proposito definido diferencia un proyecto con alma de una demo tecnica.

**Independent Test**: Se puede verificar leyendo el README y evaluando si responde a: que es, donde esta, para quien es, que problema resuelve, y que lo hace unico.

**Acceptance Scenarios**:

1. **Given** el README.md, **When** se lee la seccion introductoria, **Then** incluye una narrativa sobre el Hostal Rivera: ubicacion real (Becerrea, Lugo, Galicia), contexto (hostal real o inspirado en uno real), y proposito del sistema.
2. **Given** el README.md, **When** se busca informacion sobre el entorno real, **Then** menciona la ubicacion geografica, el Camino de Santiago (Via Kunig), y el contexto rural/gallego.
3. **Given** la documentacion general, **When** se evalua el tono, **Then** transmite que es un proyecto con proposito real, no una demo tecnica generica.

---

### User Story 5 - Eliminacion de documentacion redundante y pedagogica (Priority: P2)

Un desarrollador experimentado que consulte la documentacion debe encontrar informacion concisa y util, sin guias pedagogicas innecesarias ni archivos que repitan informacion. El ratio documentacion/codebase debe ser profesional.

**Why this priority**: Archivos como RESUMEN_GITHUB.md (resumen del resumen), GITHUB_CHECKLIST.md (como hacer push), APRENDIZAJE_PYTHON.md (tutorial de Python) y verify_github_ready.py son propios de un portfolio, no de un proyecto profesional. Su presencia infla artificialmente el repositorio.

**Independent Test**: Se puede verificar listando los archivos .md y evaluando si cada uno aporta informacion unica y necesaria. El resultado esperado es eliminacion o consolidacion de archivos redundantes.

**Acceptance Scenarios**:

1. **Given** el repositorio, **When** se evalua RESUMEN_GITHUB.md, **Then** se elimina o se consolida en README.md (su contenido es 100% redundante).
2. **Given** el repositorio, **When** se evalua GITHUB_CHECKLIST.md, **Then** se elimina (es una guia basica de git innecesaria para el publico objetivo).
3. **Given** el repositorio, **When** se evalua APRENDIZAJE_PYTHON.md, **Then** se elimina o se mueve a un repositorio separado de recursos (no es documentacion del proyecto).
4. **Given** el repositorio, **When** se evalua verify_github_ready.py, **Then** se elimina (es un script de verificacion de portfolio, no una herramienta del producto).
5. **Given** la documentacion restante, **When** se revisa, **Then** cada archivo tiene un proposito unico y no duplica contenido de otro.

---

### User Story 6 - Correccion de detalles menores de calidad (Priority: P2)

Un usuario o desarrollador que use el proyecto no debe encontrar errores de localizacion, banderas incorrectas, archivos commiteados que deberian estar en .gitignore, ni referencias a recursos inexistentes.

**Why this priority**: Estos detalles menores acumulan deuda tecnica y senalan descuido. La bandera de Espana para galego, el db.sqlite3 commiteado, y los directorios de imagenes vacios son senales de proyecto no revisado.

**Independent Test**: Se puede verificar con una lista de comprobacion de detalles menores.

**Acceptance Scenarios**:

1. **Given** el selector de idioma en base.html, **When** se muestra la opcion de galego, **Then** no usa la bandera de Espana (usar texto "Galego" o simbolo propio).
2. **Given** el repositorio git, **When** se verifica, **Then** db.sqlite3 no esta trackeado (o se documenta explicitamente por que esta incluido).
3. **Given** los directorios de imagenes (galeria/, iconos/, via_kunig/), **When** se inspeccionan, **Then** contienen imagenes reales o se eliminan si no se usan.
4. **Given** el archivo .gitignore, **When** se revisa, **Then** excluye correctamente todos los archivos sensibles y de base de datos.
5. **Given** los emails de contacto mencionados en docs y templates, **When** se verifican, **Then** son coherentes (o todos ficticios consistentes, o todos reales si el hostal existe).

---

### Edge Cases

- Que ocurre si un emoji esta dentro de un string de traduccion (.po)? Debe eliminarse del .po y recompilar el .mo.
- Que ocurre si se elimina RESUMEN_GITHUB.md y hay enlaces externos que lo referencian? Se verifican enlaces internos antes de eliminar.
- Que ocurre si el telefono real del hostal no es publico? Se usa un formato placeholder consistente (ej: "+34 982 XXX XXX") documentando que debe personalizarse, o se elimina la referencia.
- Que ocurre si las imagenes de galeria no existen y no hay presupuesto para producirlas? Se eliminan las referencias rotas y los directorios vacios, dejando solo las imagenes que si existen (logo, background).
- Que ocurre si se elimina APRENDIZAJE_PYTHON.md y el autor lo usa como recurso personal? Se mueve a un repositorio separado o se mantiene fuera del proyecto principal.

## Requirements *(mandatory)*

### Functional Requirements

**Categoria 1: Eliminacion de apariencia IA**

- **FR-001**: El sistema MUST eliminar todos los emojis e iconos Unicode decorativos de las plantillas HTML (navbar, footer, tarjetas, iconos de servicio, indicadores de idioma).
- **FR-002**: El sistema MUST eliminar todos los emojis de los archivos Markdown de documentacion (README, SECURITY, CONTRIBUTING, CHANGELOG, DEPLOYMENT, SEO_STRATEGY, INPUT_SANITIZATION, RESUMEN_GITHUB, GITHUB_CHECKLIST, APRENDIZAJE_PYTHON).
- **FR-003**: El sistema MUST reemplazar los emojis de navegacion en templates por alternativas profesionales (iconos SVG, texto plano, o clases de iconos como Bootstrap Icons si se desea mantener iconografia).
- **FR-004**: El sistema MUST mantener la funcionalidad y estructura visual de los templates tras la eliminacion de emojis (el diseno debe seguir siendo usable y atractivo sin emojis).
- **FR-005**: El sistema MUST revisar y actualizar los archivos .po de traduccion si alguna cadena traducida contiene emojis, y recompilar los archivos .mo.

**Categoria 2: Correccion de placeholders**

- **FR-006**: El sistema MUST reemplazar todas las 12 ocurrencias de "TU_USUARIO" en documentacion con el nombre de usuario o organizacion real del repositorio, o eliminar las referencias si son genericas.
- **FR-007**: El sistema MUST reemplazar las 4 ocurrencias de "Hotel Paradise" en etiquetas `<title>` por "Hostal Rivera".
- **FR-008**: El sistema MUST reemplazar los 3 numeros de telefono placeholder "+34-XXX-XXX-XXX" con el telefono real del hostal (+34 982 360 185 que ya aparece en el footer) o eliminar las referencias.
- **FR-009**: El sistema MUST eliminar o reemplazar los enlaces sociales con "#" en el footer (Facebook, Instagram) por URLs reales, o eliminar los iconos si no existen cuentas reales.
- **FR-010**: El sistema MUST eliminar las referencias a imagenes inexistentes (og-image.jpg, restaurant.jpg) de los templates y metadatos SEO, o proporcionar las imagenes reales.
- **FR-011**: El sistema MUST eliminar los directorios de imagenes vacios (galeria/, iconos/, via_kunig/) si no contienen contenido real, o populatearlos con imagenes reales.

**Categoria 3: Resolucion de inconsistencias**

- **FR-012**: El sistema MUST actualizar AGENTS.md para indicar Django==5.2.4 (version real en requirements.txt) en lugar de Django==5.0.2.
- **FR-013**: El sistema MUST actualizar RESUMEN_GITHUB.md para que las versiones de dependencias coincidan con requirements.txt (Django 5.2.4, Pillow 11.1.0, etc.) o eliminar el archivo si se considera redundante.
- **FR-014**: El sistema MUST actualizar cualquier documento que indique "3 modelos" para que refleje el numero real de modelos (7+ modelos: Cliente, Habitacion, Reserva, ViajeroCheckin, MenuDelDia, PlatoMenuDelDia, MenuEspecial, PlatoMenuEspecial).
- **FR-015**: El sistema MUST actualizar la documentacion de estructura de static/ para reflejar que CSS y JS provienen de CDN (no hay directorios static/css/ ni static/js/ locales).
- **FR-016**: El sistema MUST actualizar CHANGELOG.md para registrar la migracion de Django 5.0 a 5.2.4 correctamente.
- **FR-017**: El sistema MUST actualizar GUIA_SPEC_KIT.md para referenciar Django 5.2.4 en lugar de 5.0.2.

**Categoria 4: Narrativa e historia**

- **FR-018**: El sistema MUST incluir en README.md una seccion introductoria que narre la identidad del Hostal Rivera: ubicacion (Becerrea, Lugo, Galicia), contexto (hostal en el Camino de Santiago / Via Kunig), y proposito del sistema de gestion.
- **FR-019**: El sistema MUST eliminar el tono generico de plantilla del README y reemplazarlo con contenido especifico del hostal (nombre real, ubicacion real, caracteristicas unicas).
- **FR-020**: El sistema MUST asegurar que el README, CONTRIBUTING, y SECURITY.md usen el nombre "Hostal Rivera" consistentemente (no "Hotel Paradise" ni nombres genericos).

**Categoria 5: Eliminacion de documentacion redundante**

- **FR-021**: El sistema MUST eliminar o consolidar RESUMEN_GITHUB.md (contenido 100% redundante con README).
- **FR-022**: El sistema MUST eliminar GITHUB_CHECKLIST.md (guia basica de git innecesaria en el repositorio del proyecto).
- **FR-023**: El sistema MUST eliminar APRENDIZAJE_PYTHON.md (tutorial de Python no es documentacion del proyecto) o moverlo a un repositorio separado.
- **FR-024**: El sistema MUST eliminar verify_github_ready.py (script de verificacion de portfolio, no herramienta del producto).
- **FR-025**: El sistema MUST asegurar que cada archivo .md restante tenga un proposito unico y no duplique contenido de otro archivo.

**Categoria 6: Detalles menores de calidad**

- **FR-026**: El sistema MUST corregir la bandera del selector de idioma galego en base.html (actualmente usa bandera de Espana).
- **FR-027**: El sistema MUST eliminar db.sqlite3 del repositorio git (o documentar explicitamente por que esta incluido, aunque la constitucion y .gitignore indican que no deberia estar).
- **FR-028**: El sistema MUST asegurar que .gitignore excluye correctamente db.sqlite3, .env, media/, venv/, __pycache__/, *.pyc, *.log.
- **FR-029**: El sistema MUST eliminar los archivos README.txt dentro de directorios de imagenes vacias si los directorios se eliminan.
- **FR-030**: El sistema MUST asegurar coherencia en los emails de contacto: o todos son ficticios consistentes (si el hostal no existe) o todos son reales (si el hostal existe). No mezclar emails inventados con telefonos reales.

### Key Entities

- **Plantillas HTML**: Archivos en reservas/templates/reservas/ que contienen emojis, placeholders de nombre, telefono y enlaces.
- **Archivos de documentacion**: README.md, SECURITY.md, CONTRIBUTING.md, CHANGELOG.md, DEPLOYMENT.md, SEO_STRATEGY.md, INPUT_SANITIZATION.md, RESUMEN_GITHUB.md, GITHUB_CHECKLIST.md, APRENDIZAJE_PYTHON.md, GUIA_SPEC_KIT.md, AGENTS.md.
- **Archivos de traduccion**: locale/[es|gl|en]/LC_MESSAGES/django.po y sus correspondientes .mo compilados.
- **Archivos estaticos**: Contenido de static/images/ (logo, background, galeria, iconos, via_kunig).
- **Configuracion git**: .gitignore y archivos trackeados en el repositorio.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El proyecto contiene cero emojis en templates HTML y archivos Markdown tras la correccion (verificable con busqueda de patrones Unicode).
- **SC-002**: El proyecto contiene cero ocurrencias de placeholders conocidos ("TU_USUARIO", "Hotel Paradise", "+34-XXX-XXX-XXX", enlaces "#") tras la correccion.
- **SC-003**: El 100% de los datos tecnicos en documentacion (versiones de Django, numero de modelos, estructura de directorios) coinciden con el estado real del codigo.
- **SC-004**: El README.md incluye una narrativa especifica del Hostal Rivera con ubicacion, contexto y proposito, verificable por lectura humana.
- **SC-005**: Se han eliminado al menos 3 archivos de documentacion redundante (RESUMEN_GITHUB.md, GITHUB_CHECKLIST.md, APRENDIZAJE_PYTHON.md) y 1 script de portfolio (verify_github_ready.py).
- **SC-006**: El archivo db.sqlite3 no esta trackeado en git tras la correccion (o existe documentacion explicita aprobada por el maintainer).
- **SC-007**: Un revisor tecnico que lea el README en 60 segundos puede responder: que es el proyecto, donde esta ubicado, y que problema resuelve.
- **SC-008**: Todos los tests existentes (47 tests) siguen pasando tras los cambios en templates y documentacion.
- **SC-009**: La ejecucion de `python manage.py check` no reporta errores tras los cambios.
- **SC-010**: Los archivos .po actualizados (si aplica) se han recompilado a .mo correctamente.

## Assumptions

- El nombre real del repositorio en GitHub es "hotel-manager" (se usara para reemplazar "TU_USUARIO" en URLs de git clone). Si el usuario tiene un nombre de usuario/organizacion especifico, se usara ese.
- El telefono real del Hostal Rivera es +34 982 360 185 (ya aparece consistentemente en el footer de los templates). Se usara este numero para reemplazar los placeholders.
- El hostal no tiene cuentas reales de redes sociales activas (Facebook, Instagram). Los enlaces sociales se eliminaran en lugar de dejar placeholders.
- Las imagenes de galeria, iconos y via_kunig no existen en el repositorio. Los directorios vacios y sus README.txt se eliminaran. Solo se mantienen logo y background.
- El archivo db.sqlite3 fue commiteado por error. Se eliminara del tracking de git (pero se mantendra localmente para desarrollo).
- APRENDIZAJE_PYTHON.md es un recurso personal del autor. Se eliminara del repositorio del proyecto.
- El proyecto sigue siendo un portfolio/demo tecnica, pero se busca que parezca un proyecto profesional con identidad real, no una plantilla generica.
- No se implementaran features nuevas (emails, pagos, facturas, SES Hospedajes real) en esta iteracion. Esas van en una spec posterior.
- Los cambios en templates no alteran la funcionalidad existente, solo la presentacion visual (eliminacion de emojis, correccion de textos).
- La constitucion del proyecto (version 1.0.0) se mantiene sin cambios. Esta spec no modifica principios, solo los aplica.
