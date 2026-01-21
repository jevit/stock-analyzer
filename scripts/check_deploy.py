"""
Script de vérification avant déploiement.

Exécutez ce script pour vérifier que votre application est prête
à être déployée sur Streamlit Cloud ou d'autres plateformes.

Usage:
    python scripts/check_deploy.py
"""
import sys
from pathlib import Path
import re
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def check(condition, success_msg, fail_msg):
    """Helper to print check results."""
    if condition:
        print(f"{Colors.GREEN}✓{Colors.ENDC} {success_msg}")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.ENDC} {fail_msg}")
        return False

def check_file_exists(file_path, description):
    """Check if a file exists."""
    exists = file_path.exists()
    return check(
        exists,
        f"{description} existe",
        f"{description} manquant: {file_path}"
    )

def check_no_secrets_in_file(file_path, patterns):
    """Check that a file doesn't contain secrets."""
    if not file_path.exists():
        return True

    content = file_path.read_text(encoding='utf-8', errors='ignore')

    for pattern_name, pattern in patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            print(f"{Colors.RED}✗{Colors.ENDC} Secret potentiel trouvé dans {file_path}: {pattern_name}")
            return False

    return True

def main():
    """Run all deployment checks."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 Vérification avant déploiement{Colors.ENDC}\n")

    root = Path(__file__).parent.parent
    all_checks_passed = True

    # 1. Check required files
    print(f"{Colors.BOLD}1. Fichiers requis:{Colors.ENDC}")
    required_files = {
        root / "requirements.txt": "requirements.txt",
        root / "app" / "main.py": "app/main.py (point d'entrée)",
        root / ".streamlit" / "config.toml": ".streamlit/config.toml",
        root / "README.md": "README.md",
        root / ".gitignore": ".gitignore",
    }

    for file_path, description in required_files.items():
        if not check_file_exists(file_path, description):
            all_checks_passed = False

    # 2. Check .gitignore contains important entries
    print(f"\n{Colors.BOLD}2. Configuration .gitignore:{Colors.ENDC}")
    gitignore_path = root / ".gitignore"
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        required_entries = {
            ".env": [".env"],
            "secrets.toml": ["secrets.toml"],
            "__pycache__": ["__pycache__"],
            "*.pyc": ["*.pyc", "*.py[cod]"],  # Accept both formats
        }

        for entry_name, patterns in required_entries.items():
            if any(pattern in gitignore_content for pattern in patterns):
                check(True, f"'{entry_name}' est dans .gitignore", "")
            else:
                check(False, "", f"'{entry_name}' devrait être dans .gitignore")
                all_checks_passed = False

    # 3. Check for hardcoded secrets
    print(f"\n{Colors.BOLD}3. Vérification des secrets:{Colors.ENDC}")

    secret_patterns = {
        "Token Telegram": r"[0-9]{8,10}:[A-Za-z0-9_-]{35}",
        "Email password": r"password\s*=\s*['\"][^'\"]{10,}['\"]",
        "API Key": r"api[_-]?key\s*=\s*['\"][^'\"]{20,}['\"]",
    }

    # Check Python files
    py_files = list(root.glob("**/*.py"))
    secrets_found = False

    for py_file in py_files:
        # Skip venv and cache directories
        if any(skip in str(py_file) for skip in ["venv", "__pycache__", ".git"]):
            continue

        if not check_no_secrets_in_file(py_file, secret_patterns):
            secrets_found = True
            all_checks_passed = False

    if not secrets_found:
        check(True, "Aucun secret détecté dans les fichiers Python", "")

    # 4. Check that .env is not tracked
    print(f"\n{Colors.BOLD}4. Fichiers sensibles:{Colors.ENDC}")
    env_file = root / ".env"
    secrets_file = root / ".streamlit" / "secrets.toml"

    if env_file.exists():
        print(f"{Colors.YELLOW}⚠{Colors.ENDC} .env existe (OK pour local, mais vérifiez qu'il n'est pas committé)")

    if secrets_file.exists():
        print(f"{Colors.YELLOW}⚠{Colors.ENDC} secrets.toml existe (OK pour local, mais vérifiez qu'il n'est pas committé)")

    # 5. Check requirements.txt
    print(f"\n{Colors.BOLD}5. Dépendances:{Colors.ENDC}")
    req_file = root / "requirements.txt"
    if req_file.exists():
        requirements = req_file.read_text()
        essential_packages = ["streamlit", "pandas", "yfinance", "plotly"]

        for package in essential_packages:
            if package.lower() in requirements.lower():
                check(True, f"{package} présent dans requirements.txt", "")
            else:
                check(False, "", f"{package} manquant dans requirements.txt")
                all_checks_passed = False

    # 6. Check Python version
    print(f"\n{Colors.BOLD}6. Version Python:{Colors.ENDC}")
    runtime_file = root / "runtime.txt"
    if runtime_file.exists():
        runtime_content = runtime_file.read_text().strip()
        check(True, f"runtime.txt spécifie: {runtime_content}", "")
    else:
        print(f"{Colors.YELLOW}⚠{Colors.ENDC} runtime.txt manquant (recommandé)")

    # Final result
    print(f"\n{Colors.BOLD}{'='*50}{Colors.ENDC}")
    if all_checks_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ Tout est OK ! Prêt pour le déploiement 🚀{Colors.ENDC}\n")
        print(f"{Colors.BLUE}Prochaines étapes:{Colors.ENDC}")
        print("1. Committez vos changements: git add . && git commit -m 'Ready for deploy'")
        print("2. Poussez sur GitHub: git push")
        print("3. Déployez sur Streamlit Cloud: https://share.streamlit.io")
        print(f"\n{Colors.BLUE}Consultez:{Colors.ENDC} CHECKLIST_DEPLOIEMENT.md pour plus de détails")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Des problèmes ont été détectés{Colors.ENDC}\n")
        print(f"{Colors.YELLOW}Corrigez les erreurs ci-dessus avant de déployer.{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
