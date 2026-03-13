"""Pre-GitHub safety checks for this repository."""

import sys
from pathlib import Path

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def check_file_exists(filename, should_exist=True):
    """Return True when the file existence matches expectation."""
    exists = Path(filename).exists()
    if should_exist:
        if exists:
            print(f"{GREEN}+{RESET} {filename} encontrado")
            return True

        print(f"{RED}x{RESET} {filename} NO encontrado (deberia existir)")
        return False

    if not exists:
        print(f"{GREEN}+{RESET} {filename} NO existe (correcto)")
        return True

    print(f"{YELLOW}!{RESET} {filename} existe (NO deberia estar en Git)")
    return False


def check_gitignore():
    """Verify required .gitignore entries are present."""
    print(f"\n{BLUE}Verificando .gitignore...{RESET}")

    required_entries = [
        ".env",
        "db.sqlite3",
        "/media",
        "venv/",
        "__pycache__/",
        "*.log",
    ]

    optional_entries = ["*.pyc", "*.py[cod]"]

    try:
        content = Path(".gitignore").read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"{RED}x{RESET} .gitignore NO encontrado")
        return False

    all_good = True
    for entry in required_entries:
        if entry in content:
            print(f"{GREEN}+{RESET} {entry} esta en .gitignore")
        else:
            print(f"{RED}x{RESET} {entry} NO esta en .gitignore")
            all_good = False

    if any(entry in content for entry in optional_entries):
        print(f"{GREEN}+{RESET} Archivos .pyc estan excluidos")
    else:
        print(f"{RED}x{RESET} Archivos .pyc NO estan excluidos")
        all_good = False

    return all_good


def check_env_example():
    """Verify .env.example exists and does not expose sensitive data."""
    print(f"\n{BLUE}Verificando .env.example...{RESET}")

    try:
        content = Path(".env.example").read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"{RED}x{RESET} .env.example NO encontrado")
        return False

    sensitive_patterns = ["django-insecure-*^_mdcjur"]

    has_issues = False
    for pattern in sensitive_patterns:
        if pattern in content:
            msg = (
                f"{YELLOW}!{RESET} .env.example contiene "
                f"'{pattern[:20]}...' (usar valor generico)"
            )
            print(msg)
            has_issues = True

    if has_issues:
        return False

    print(f"{GREEN}+{RESET} .env.example no contiene datos sensibles")
    return True


def check_settings_py():
    """Verify settings.py reads critical values from environment."""
    print(f"\n{BLUE}Verificando settings.py...{RESET}")

    try:
        content = Path("hotel_project/settings.py").read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"{RED}x{RESET} settings.py NO encontrado")
        return False

    all_good = True

    if "from decouple import config" in content:
        print(f"{GREEN}+{RESET} Importa python-decouple")
    else:
        print(f"{RED}x{RESET} NO importa python-decouple")
        all_good = False

    if "SECRET_KEY = config('SECRET_KEY'" in content:
        print(f"{GREEN}+{RESET} SECRET_KEY usa variables de entorno")
    else:
        print(f"{RED}x{RESET} SECRET_KEY NO usa variables de entorno")
        all_good = False

    if "DEBUG = config('DEBUG'" in content:
        print(f"{GREEN}+{RESET} DEBUG usa variables de entorno")
    else:
        print(f"{RED}x{RESET} DEBUG NO usa variables de entorno")
        all_good = False

    return all_good


def main():
    """Run all checks and exit non-zero if any check fails."""
    print(f"{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}VERIFICACION PRE-GITHUB - Sistema de Gestion Hotelera{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

    all_checks_passed = True

    print(f"{BLUE}Verificando archivos necesarios...{RESET}")
    required_files = [
        ".gitignore",
        ".env.example",
        "README.md",
        "requirements.txt",
        "LICENSE",
        "DEPLOYMENT.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CHANGELOG.md",
    ]

    for filename in required_files:
        if not check_file_exists(filename, should_exist=True):
            all_checks_passed = False

    print(f"\n{BLUE}Verificando que archivos sensibles no se suban...{RESET}")

    if not check_gitignore():
        all_checks_passed = False

    if not check_env_example():
        all_checks_passed = False

    if not check_settings_py():
        all_checks_passed = False

    print(f"\n{BLUE}{'=' * 60}{RESET}")
    if all_checks_passed:
        print(f"{GREEN}OK - TODAS LAS VERIFICACIONES PASARON{RESET}")
        print(f"{GREEN}El proyecto esta listo para subir a GitHub{RESET}")
        print(f"\n{BLUE}Proximos pasos:{RESET}")
        print("1. git init")
        print("2. git add .")
        print("3. git status (verifica que .env y db.sqlite3 NO aparezcan)")
        print("4. git commit -m 'feat: Initial commit'")
        print("5. git remote add origin https://github.com/TU_USUARIO/WEB-HOTEL.git")
        print("6. git push -u origin main")
    else:
        print(f"{RED}ERROR - ALGUNAS VERIFICACIONES FALLARON{RESET}")
        print(f"{YELLOW}Revisa los errores arriba antes de subir a GitHub{RESET}")
        sys.exit(1)

    print(f"{BLUE}{'=' * 60}{RESET}\n")


if __name__ == "__main__":
    main()
