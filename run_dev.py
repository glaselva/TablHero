#!/usr/bin/env python3
"""
run_dev.py - Avvia TablHero in development mode

Uso:
  python run_dev.py           # Avvia in dev mode
  python run_dev.py --version # Mostra versione
  python run_dev.py --help    # Mostra aiuto

Cross-platform: Funziona su Windows, Mac, Linux
"""

import os
import sys
import subprocess
from pathlib import Path

class Colors:
    """Colori per terminale"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    @staticmethod
    def disable_if_windows():
        """Windows non supporta ANSI colors in alcuni casi"""
        if sys.platform == 'win32':
            for attr in dir(Colors):
                if not attr.startswith('_'):
                    setattr(Colors, attr, '')


def print_header():
    """Stampa header"""
    print("\n" + "╔" + "═" * 62 + "╗")
    print("║" + " " * 62 + "║")
    print("║" + Colors.BOLD + "          TABLHERO - Development Mode".ljust(62) + Colors.END + "║")
    print("║" + " " * 62 + "║")
    print("╚" + "═" * 62 + "╝\n")


def check_python_version():
    """Verifica versione Python"""
    version = sys.version_info
    print(f"▶ Verificando Python {version.major}.{version.minor}.{version.micro}...", end=" ")
    if version.major >= 3 and version.minor >= 8:
        print(f"{Colors.GREEN}✅{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}❌ Richiesta Python 3.8+{Colors.END}")
        return False


def activate_venv():
    """Attiva virtual environment"""
    print(f"▶ Attivando Virtual Environment...", end=" ")
    
    venv_path = Path('venv')
    if not venv_path.exists():
        print(f"{Colors.RED}❌ Virtual Environment non trovato!{Colors.END}")
        print(f"   Esegui: python -m venv venv")
        return False
    
    # Aggiungi venv/bin (o Scripts su Windows) al PATH
    if sys.platform == 'win32':
        bin_path = venv_path / 'Scripts'
    else:
        bin_path = venv_path / 'bin'
    
    sys.path.insert(0, str(bin_path))
    print(f"{Colors.GREEN}✅{Colors.END}")
    return True


def setup_environment():
    """Configura variabili d'ambiente"""
    print(f"▶ Configurando variabili d'ambiente...", end=" ")
    
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    
    print(f"{Colors.GREEN}✅{Colors.END}")
    print(f"   • FLASK_ENV = development")
    print(f"   • FLASK_DEBUG = True")


def check_and_install_requirements():
    """Verifica e installa dipendenze se necessarie"""
    print(f"▶ Controllando dipendenze...", end=" ")
    
    req_path = Path('requirements.txt')
    if not req_path.exists():
        print(f"{Colors.RED}❌{Colors.END}")
        print(f"  {Colors.RED}❌ requirements.txt non trovato!{Colors.END}")
        return False
    
    print(f"{Colors.GREEN}✅{Colors.END}")
    
    # Verifica se i pacchetti principali sono installati
    try:
        import flask
        print(f"  {Colors.GREEN}✅ Tutte le dipendenze sono già installate{Colors.END}")
        return True
    except ImportError:
        print(f"  Installando dipendenze mancanti...")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'],
                check=True
            )
            print(f"  {Colors.GREEN}✅ Dipendenze installate con successo{Colors.END}")
            return True
        except subprocess.CalledProcessError:
            print(f"  {Colors.RED}❌ Errore nell'installazione delle dipendenze{Colors.END}")
            return False


def check_app_file():
    """Verifica app.py esiste"""
    print(f"▶ Verificando app.py...", end=" ")
    
    if Path('app.py').exists():
        print(f"{Colors.GREEN}✅{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}❌ app.py non trovato!{Colors.END}")
        return False


def run_dev_server():
    """Avvia development server"""
    print()
    print("╔" + "═" * 62 + "╗")
    print("║" + " " * 62 + "║")
    print("║  Applicazione avviata! Accedi a:".ljust(62) + "║")
    print("║  " + Colors.BLUE + "http://localhost:5000".ljust(58) + Colors.END + "║")
    print("║" + " " * 62 + "║")
    print("║  Premi CTRL+C per fermare l'applicazione".ljust(62) + "║")
    print("║" + " " * 62 + "║")
    print("╚" + "═" * 62 + "╝\n")
    
    try:
        # Esegui app.py
        subprocess.run([sys.executable, 'app.py'], check=False)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}▶ Applicazione fermata{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Errore: {e}{Colors.END}\n")
        return False
    
    return True


def print_help():
    """Mostra aiuto"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║  TABLHERO Development Mode                                    ║
╚════════════════════════════════════════════════════════════════╝

UTILIZZO:
  python run_dev.py              Avvia l'app in dev mode
  python run_dev.py --help       Mostra questo messaggio
  python run_dev.py --version    Mostra versione Python

COSA FA:
  ✓ Attiva Virtual Environment
  ✓ Configura variabili d'ambiente (FLASK_ENV=development)
  ✓ Verifica dipendenze
  ✓ Avvia Flask app con debug abilitato

ACCESSO:
  • Locale: http://localhost:5000
  • Network: http://192.168.x.x:5000

COMANDI VELOCI:
  • Ferma app: Premi CTRL+C
  • Testa config: python test_ambiente.py current
  • Configura cloud: python setup_ambiente.py cloud

VARIABILI D'AMBIENTE:
  • FLASK_ENV = development
  • FLASK_DEBUG = True
  • DATABASE = sqlite:///tablhero.db (locale)

DOCUMENTAZIONE:
  • QUICK_START.md: Guida veloce (60 sec)
  • CONFIGURAZIONE_AMBIENTI.txt: Guida completa
  • INDEX.md: Indice di tutta la documentazione

PER AIUTO:
  Consulta CONFIGURAZIONE_AMBIENTI.txt o SETUP_PRODUZIONE_COMPLETO.txt
    """)


def main():
    """Main entry point"""
    
    # Parse arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--help', '-h', 'help']:
            print_help()
            return 0
        elif arg in ['--version', '-v', 'version']:
            print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
            return 0
        else:
            print(f"❌ Argomento non riconosciuto: {arg}")
            print(f"Usa: python run_dev.py --help")
            return 1
    
    # Setup
    print_header()
    
    # Verifche
    if not check_python_version():
        return 1
    
    if not activate_venv():
        return 1
    
    setup_environment()
    
    if not check_and_install_requirements():
        return 1
    
    if not check_app_file():
        return 1
    
    print()
    
    # Avvia app
    if not run_dev_server():
        return 1
    
    return 0


if __name__ == '__main__':
    # Disabilita colori su Windows se necessario
    if sys.platform == 'win32':
        try:
            import colorama
            colorama.init()
        except ImportError:
            pass
    
    sys.exit(main())
