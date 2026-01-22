#!/usr/bin/env python3
"""
setup_ambiente.py - Wizard di setup per configurare l'ambiente di deployment

Uso:
  python setup_ambiente.py         # Configurazione interattiva
  python setup_ambiente.py local   # Configura per sviluppo locale
  python setup_ambiente.py cloud   # Configura per deployment cloud
"""

import os
import sys
from pathlib import Path

def setup_local():
    """Setup per sviluppo locale (SQLite)"""
    print("\n" + "="*70)
    print("SETUP AMBIENTE LOCALE (SVILUPPO)")
    print("="*70 + "\n")
    
    # Leggi .env
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ File .env non trovato!")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    # Assicurati che FLASK_ENV=development
    if 'FLASK_ENV=development' in content:
        print("✅ FLASK_ENV=development: OK")
    else:
        content = content.replace('FLASK_ENV=production', 'FLASK_ENV=development')
        content = content.replace('FLASK_ENV=', 'FLASK_ENV=development')
        print("✅ FLASK_ENV impostato a: development")
    
    # Assicurati che DEBUG è on
    if 'FLASK_DEBUG=True' in content:
        print("✅ FLASK_DEBUG=True: OK")
    else:
        content = content.replace('FLASK_DEBUG=False', 'FLASK_DEBUG=True')
        print("✅ FLASK_DEBUG impostato a: True")
    
    # DATABASE_URL deve essere commentata
    if 'DATABASE_URL=' in content and not content.split('DATABASE_URL=')[0].endswith('#'):
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.strip().startswith('DATABASE_URL=') and not line.strip().startswith('#'):
                new_lines.append('# ' + line)
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
        print("✅ DATABASE_URL commentata (userà SQLite locale)")
    else:
        print("✅ DATABASE_URL non configurata: OK")
    
    # Salva .env
    with open('.env', 'w') as f:
        f.write(content)
    
    print("\n✅ SETUP LOCALE COMPLETATO!")
    print("\nPer avviare l'applicazione:")
    print("  1. venv\\Scripts\\Activate.ps1")
    print("  2. python app.py")
    print("\nDatabase: SQLite (tablhero.db)")
    print("URL: http://localhost:5000\n")
    
    return True


def setup_cloud():
    """Setup per deployment cloud (MySQL/PostgreSQL)"""
    print("\n" + "="*70)
    print("SETUP AMBIENTE CLOUD (PRODUZIONE)")
    print("="*70 + "\n")
    
    print("Scegli il provider:")
    print("  1. Railway.app (CONSIGLIATO - gratuito per test)")
    print("  2. Heroku")
    print("  3. AWS RDS / Azure / Google Cloud SQL")
    print("  4. Altro (configurazione manuale)")
    
    choice = input("\nScelta (1-4): ").strip()
    
    # Leggi .env
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ File .env non trovato!")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    # Imposta FLASK_ENV=production
    content = content.replace('FLASK_ENV=development', 'FLASK_ENV=production')
    if 'FLASK_ENV=' not in content:
        content = content.replace('FLASK_DEBUG=False', 'FLASK_ENV=production\nFLASK_DEBUG=False')
    print("✅ FLASK_ENV impostato a: production")
    
    # Imposta FLASK_DEBUG=False
    content = content.replace('FLASK_DEBUG=True', 'FLASK_DEBUG=False')
    print("✅ FLASK_DEBUG impostato a: False")
    
    # Salva .env
    with open('.env', 'w') as f:
        f.write(content)
    
    print("\n✅ SETUP CLOUD COMPLETATO!")
    
    if choice == '1':
        print("\n" + "="*70)
        print("RAILWAY.APP SETUP")
        print("="*70 + "\n")
        print("Step 1: Crea account su https://railway.app")
        print("Step 2: Installa Railway CLI: npm install -g @railway/cli")
        print("Step 3: Login: railway login")
        print("Step 4: Inizializza progetto:")
        print("         railway up")
        print("Step 5: Railway creerà automaticamente:")
        print("         • Container per Flask app")
        print("         • PostgreSQL database")
        print("         • DATABASE_URL variabile d'ambiente")
        print("Step 6: Configura SECRET_KEY:")
        print("         railway variables set SECRET_KEY=<chiave-segreta>")
        print("Step 7: Deploy: git push")
        print("\nURL app: https://nome-app.railway.app")
        
    elif choice == '2':
        print("\n" + "="*70)
        print("HEROKU SETUP")
        print("="*70 + "\n")
        print("Step 1: Crea account su https://heroku.com")
        print("Step 2: Installa Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli")
        print("Step 3: Login: heroku login")
        print("Step 4: Crea app: heroku create nome-app")
        print("Step 5: Aggiungi PostgreSQL database:")
        print("         heroku addons:create heroku-postgresql:hobby-dev")
        print("Step 6: Configura SECRET_KEY:")
        print("         heroku config:set SECRET_KEY=<chiave-segreta>")
        print("Step 7: Deploy: git push heroku main")
        print("\nURL app: https://nome-app.herokuapp.com")
        
    elif choice == '3':
        print("\n" + "="*70)
        print("CONFIGURAZIONE MANUALE")
        print("="*70 + "\n")
        db_url = input("DATABASE_URL (es: postgresql://user:pass@host:5432/db): ").strip()
        
        if db_url:
            # Aggiungi DATABASE_URL a .env
            with open('.env', 'a') as f:
                f.write(f"\nDATABASE_URL={db_url}\n")
            print(f"\n✅ DATABASE_URL aggiunta a .env")
        else:
            print("\n⚠️  DATABASE_URL non impostata. Configurarla manualmente in .env")
    
    print("\n" + "="*70)
    print("PROSSIMI STEP")
    print("="*70)
    print("\n1. Assicurati che tutto funziona localmente:")
    print("   python app.py")
    print("\n2. Commit il codice:")
    print("   git add .")
    print("   git commit -m 'Setup produzione'")
    print("\n3. Esegui i comandi del tuo provider (vedi sopra)")
    print("\n4. Accedi all'app nel browser (URL del provider)")
    print("\n5. Controlla i log:")
    print("   railway logs  (o heroku logs --tail)")
    print("   Dovrai vedere: ✅ Connesso a database REMOTO (produzione)\n")
    
    return True


def interactive_setup():
    """Setup interattivo"""
    print("\n" + "="*70)
    print("CONFIGURAZIONE AMBIENTE TABLHERO")
    print("="*70 + "\n")
    
    print("Dove vuoi deployare l'applicazione?")
    print("\n  1. Locale (sviluppo) - SQLite")
    print("  2. Cloud (produzione) - PostgreSQL/MySQL")
    
    choice = input("\nScelta (1-2): ").strip()
    
    if choice == '1':
        return setup_local()
    elif choice == '2':
        return setup_cloud()
    else:
        print("❌ Scelta non valida")
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == 'local':
            success = setup_local()
        elif arg == 'cloud':
            success = setup_cloud()
        else:
            print(f"Parametro non riconosciuto: {arg}")
            print("\nUso: python setup_ambiente.py [local|cloud]")
            success = False
    else:
        success = interactive_setup()
    
    sys.exit(0 if success else 1)
