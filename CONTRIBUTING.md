# Guía de Contribución

¡Gracias por tu interés en contribuir al proyecto Hostal Rivera! 🎉

## 🤝 Cómo Contribuir

### 1. Fork el Proyecto
Haz un fork del repositorio a tu cuenta de GitHub.

### 2. Clona tu Fork
```powershell
git clone https://github.com/TU_USUARIO/WEB-HOTEL.git
cd WEB-HOTEL
```

### 3. Configura el Entorno
```powershell
# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
# Edita .env con tus valores

# Compilar traducciones
python compile_mo.py

# Migrar base de datos
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### 4. Crea una Rama
```powershell
git checkout -b feature/nombre-de-tu-funcionalidad
# O para correcciones:
git checkout -b fix/descripcion-del-bug
```

### 5. Realiza tus Cambios
- Escribe código limpio y documentado
- Sigue las convenciones de Django
- Añade comentarios explicativos cuando sea necesario
- Actualiza la documentación si es relevante

### 6. Ejecuta las Pruebas
```powershell
# Verificar errores
python manage.py check

# Ejecutar tests (cuando estén implementados)
python manage.py test

# Verificar migraciones
python manage.py makemigrations --dry-run --check
```

### 7. Commit y Push
```powershell
git add .
git commit -m "feat: Descripción clara del cambio"
git push origin feature/nombre-de-tu-funcionalidad
```

### 8. Abre un Pull Request
- Ve a GitHub y abre un Pull Request desde tu rama
- Describe claramente qué cambios introduces y por qué
- Referencia issues relacionados si los hay

## 📝 Estilo de Código

### Python/Django
- Sigue [PEP 8](https://pep8.org/)
- Usa nombres descriptivos para variables y funciones
- Documenta funciones complejas con docstrings
- Mantén las funciones pequeñas y enfocadas

### HTML/Templates
- Usa indentación de 4 espacios
- Añade comentarios para secciones complejas
- Usa el sistema de traducciones `{% trans %}` para textos

### CSS
- Prefiere clases de Bootstrap cuando sea posible
- Usa nombres de clase descriptivos en inglés
- Agrupa estilos relacionados

### JavaScript
- Usa nombres descriptivos para variables
- Añade comentarios para lógica compleja
- Preferiblemente vanilla JS o usa librerías ya incluidas

## 🔍 Convención de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Cambios de formato (no afectan el código)
- `refactor:` Refactorización de código
- `test:` Añadir o modificar tests
- `chore:` Tareas de mantenimiento

**Ejemplos:**
```
feat: Añadir sistema de pagos con Stripe
fix: Corregir validación de fechas en reservas
docs: Actualizar README con instrucciones de despliegue
style: Formatear código según PEP 8
refactor: Simplificar lógica de disponibilidad de habitaciones
test: Añadir tests para modelo de Reserva
chore: Actualizar dependencias
```

## 🐛 Reportar Bugs

Si encuentras un bug:
1. Verifica que no esté ya reportado en [Issues](https://github.com/TU_USUARIO/WEB-HOTEL/issues)
2. Crea un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducirlo
   - Comportamiento esperado vs actual
   - Screenshots si es visual
   - Información del entorno (OS, Python version, etc.)

## 💡 Sugerir Mejoras

Para proponer nuevas funcionalidades:
1. Abre un issue etiquetado como "enhancement"
2. Describe claramente qué quieres lograr y por qué
3. Propón una posible implementación si tienes ideas
4. Espera feedback antes de empezar a codear

## 🌍 Traducciones

Para contribuir con traducciones:
1. Edita los archivos `.po` en `locale/[idioma]/LC_MESSAGES/`
2. Compila con `python compile_mo.py`
3. Prueba que las traducciones se vean correctamente

## ✅ Checklist Pre-Pull Request

Antes de abrir un PR, verifica:
- [ ] El código funciona correctamente
- [ ] No hay errores: `python manage.py check`
- [ ] Las traducciones están compiladas
- [ ] La documentación está actualizada si es necesario
- [ ] Los commits tienen mensajes descriptivos
- [ ] No se incluyen archivos sensibles (.env, db.sqlite3, etc.)
- [ ] El código sigue las convenciones del proyecto

## 🙏 Código de Conducta

- Sé respetuoso con otros contribuidores
- Acepta críticas constructivas
- Enfócate en lo mejor para el proyecto
- Ayuda a otros cuando puedas

## 📚 Recursos Útiles

- [Documentación de Django](https://docs.djangoproject.com/)
- [Bootstrap 5 Docs](https://getbootstrap.com/docs/5.0/)
- [Git Flow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
- [Markdown Guide](https://www.markdownguide.org/)

## 🎯 Áreas que Necesitan Ayuda

Actualmente buscamos contribuciones en:
- [ ] Sistema de tests unitarios
- [ ] Integración con pasarelas de pago
- [ ] Sistema de emails automáticos
- [ ] Mejoras en la UI/UX
- [ ] Optimización de rendimiento
- [ ] Documentación adicional
- [ ] Nuevas traducciones (Francés, Alemán, Portugués)

---

**¡Gracias por contribuir!** 🚀
