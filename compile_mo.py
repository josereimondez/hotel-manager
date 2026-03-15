"""Script para compilar archivos .po a .mo sin necesidad de msgfmt"""
import os

import polib

BASE_PATH = r'd:\Carpeta Personal\Proxectos\WEB HOTEL\locale'
locales = ['es', 'gl', 'en']

for lang in locales:
    po_path = os.path.join(BASE_PATH, lang, 'LC_MESSAGES', 'django.po')
    mo_path = os.path.join(BASE_PATH, lang, 'LC_MESSAGES', 'django.mo')
    try:
        po = polib.pofile(po_path)
        po.save_as_mofile(mo_path)
        translated = len(po.translated_entries())
        print(f'[OK] {lang}: django.mo compilado ({translated} entradas traducidas)')
    except (FileNotFoundError, OSError) as e:
        print(f'[ERROR] {lang}: {e}')

print('\nCompilacion completada.')
