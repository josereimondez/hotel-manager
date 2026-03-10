"""
Script de verificación pre-GitHub
Verifica que el proyecto esté listo para subir a GitHub de forma segura
"""

import os
import sys
from pathlib import Path

# Colores para la consola
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_file_exists(filename, should_exist=True):
    """Verifica si un archivo existe o no"""
    exists = Path(filename).exists()
    if should_exist:
        if exists:
            print(f"{GREEN}✓{RESET} {filename} encontrado")
            return True
        else:
            print(f"{RED}✗{RESET} {filename} NO encontrado (debería existir)")
            return False
    else:
        if not exists:
            print(f"{GREEN}✓{RESET} {filename} NO existe (correcto)")
            return True
        else:
            print(f"{YELLOW}⚠{RESET} {filename} existe (NO debería estar en Git)")
            return False

def check_gitignore():
    """Verifica que .gitignore tenga las entradas necesarias"""
    print(f"\n{BLUE}Verificando .gitignore...{RESET}")
    
    required_entries = [
        '.env',
        'db.sqlite3',
        '/media',
        'venv/',
        '__pycache__/',
        '*.log',
    ]
    
    # *.pyc está cubierto por *.py[cod]
    optional_entries = ['*.pyc', '*.py[cod]']
    
    try:
        with open('.gitignore', 'r', encoding='utf-8') as f:
            content = f.read()
            
        all_good = True
        for entry in required_entries:
            if entry in content:
                print(f"{GREEN}✓{RESET} {entry} está en .gitignore")
            else:
                print(f"{RED}✗{RESET} {entry} NO está en .gitignore")
                all_good = False
        
        # Verificar que al menos una de las entradas opcionales esté
        pyc_found = any(entry in content for entry in optional_entries)
        if pyc_found:
            print(f"{GREEN}✓{RESET} Archivos .pyc están excluidos")
        else:
            print(f"{RED}✗{RESET} Archivos .pyc NO están excluidos")
            all_good = False
        
        return all_good
        
        return all_good
    except FileNotFoundError:
        print(f"{RED}✗{RESET} .gitignore NO encontrado")
        return False

def check_env_example():
    """Verifica que .env.example exista y no tenga datos sensibles"""
    print(f"\n{BLUE}Verificando .env.example...{RESET}")
    
    try:
        with open('.env.example', 'r', encoding='utf-8') as f:
            content = f.read()
        
        sensitive_patterns = [
            'django-insecure-*^_mdcjur',  # La SECRET_KEY del desarrollo
        ]
        
        has_issues = False
        for pattern in sensitive_patterns:
            if pattern in content:
                print(f"{YELLOW}⚠{RESET} .env.example contiene '{pattern[:20]}...' (cambiar por valor genérico)")
                has_issues = True
        
        if not has_issues:
            print(f"{GREEN}✓{RESET} .env.example no contiene datos sensibles")
            return True
        return False
        
    except FileNotFoundError:
        print(f"{RED}✗{RESET} .env.example NO encontrado")
        return False

def check_settings_py():
    """Verifica que settings.py use variables de entorno"""
    print(f"\n{BLUE}Verificando settings.py...{RESET}")
    
    try:
        with open('hotel_project/settings.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        all_good = True
        
        # Verificar que use config() de decouple
        if "from decouple import config" in content:
            print(f"{GREEN}✓{RESET} Importa python-decouple")
        else:
            print(f"{RED}✗{RESET} NO importa python-decouple")
            all_good = False
        
        # Verificar que SECRET_KEY use config()
        if "SECRET_KEY = config('SECRET_KEY'" in content:
            print(f"{GREEN}✓{RESET} SECRET_KEY usa variables de entorno")
        else:
            print(f"{RED}✗{RESET} SECRET_KEY NO usa variables de entorno")
            all_good = False
        
        # Verificar que DEBUG use config()
        if "DEBUG = config('DEBUG'" in content:
            print(f"{GREEN}✓{RESET} DEBUG usa variables de entorno")
        else:
            print(f"{RED}✗{RESET} DEBUG NO usa variables de entorno")
            all_good = False
        
        return all_good
        
    except FileNotFoundError:
        print(f"{RED}✗{RESET} settings.py NO encontrado")
        return False

def main():
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}VERIFICACIÓN PRE-GITHUB - Sistema de Gestión Hotelera{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    all_checks_passed = True
    
    # 1. Verificar archivos que DEBEN existir
    print(f"{BLUE}Verificando archivos necesarios...{RESET}")
    required_files = [
        '.gitignore',
        '.env.example',
        'README.md',
        'requirements.txt',
        'LICENSE',
        'DEPLOYMENT.md',
        'CONTRIBUTING.md',
        'SECURITY.md',
        'CHANGELOG.md',
    ]
    
    for file in required_files:
        if not check_file_exists(file, should_exist=True):
            all_checks_passed = False
    
    # 2. Verificar archivos que NO deben estar en Git
    print(f"\n{BLUE}Verificando que archivos sensibles no se suban...{RESET}")
    # Nota: .env y db.sqlite3 pueden existir localmente, pero no deben estar en Git
    # Esto se verifica con .gitignore
    
    # 3. Verificar .gitignore
    if not check_gitignore():
        all_checks_passed = False
    
    # 4. Verificar .env.example
    if not check_env_example():
        all_checks_passed = False
    
    # 5. Verificar settings.py
    if not check_settings_py():
        all_checks_passed = False
    
    # Resultado final
    print(f"\n{BLUE}{'='*60}{RESET}")
    if all_checks_passed:
        print(f"{GREEN}✅ TODAS LAS VERIFICACIONES PASARON{RESET}")
        print(f"{GREEN}El proyecto está listo para subir a GitHub{RESET}")
        print(f"\n{BLUE}Próximos pasos:{RESET}")
        print("1. git init")
        print("2. git add .")
        print("3. git status  (verifica que .env y db.sqlite3 NO aparezcan)")
        print("4. git commit -m 'feat: Initial commit'")
        print("5. git remote add origin https://github.com/TU_USUARIO/WEB-HOTEL.git")
        print("6. git push -u origin main")
    else:
        print(f"{RED}❌ ALGUNAS VERIFICACIONES FALLARON{RESET}")
        print(f"{YELLOW}Revisa los errores arriba antes de subir a GitHub{RESET}")
        sys.exit(1)
    
    print(f"{BLUE}{'='*60}{RESET}\n")

if __name__ == '__main__':
    main()
