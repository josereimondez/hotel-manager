"""Script para compilar archivos .po a .mo sin necesidad de msgfmt"""
import polib
import os

base = r'd:\Carpeta Personal\Proxectos\WEB HOTEL\locale'
locales = ['es', 'gl', 'en']

for lang in locales:
    po_path = os.path.join(base, lang, 'LC_MESSAGES', 'django.po')
    mo_path = os.path.join(base, lang, 'LC_MESSAGES', 'django.mo')
    try:
        po = polib.pofile(po_path)
        po.save_as_mofile(mo_path)
        translated = len(po.translated_entries())
        print(f'[OK] {lang}: django.mo compilado ({translated} entradas traducidas)')
    except Exception as e:
        print(f'[ERROR] {lang}: {e}')

print('\nCompilacion completada.')
