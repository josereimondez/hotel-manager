"""Script para compilar archivos .po a .mo sin necesidad de msgfmt.

Busca la carpeta 'locale' en el directorio del proyecto (donde está este script).
Puede anularse con la variable de entorno COMPILE_MO_LOCALE_PATH.
"""
import os
from pathlib import Path

import polib

BASE_PATH = Path(os.getenv('COMPILE_MO_LOCALE_PATH', Path(__file__).parent / 'locale'))
locales = ['es', 'gl', 'en']

for lang in locales:
    po_path = BASE_PATH / lang / 'LC_MESSAGES' / 'django.po'
    mo_path = BASE_PATH / lang / 'LC_MESSAGES' / 'django.mo'
    try:
        po = polib.pofile(str(po_path))
        po.save_as_mofile(str(mo_path))
        translated = len(po.translated_entries())
        print(f'[OK] {lang}: django.mo compilado ({translated} entradas traducidas)')
    except (FileNotFoundError, OSError) as e:
        print(f'[ERROR] {lang}: {e}')

print('\nCompilacion completada.')
