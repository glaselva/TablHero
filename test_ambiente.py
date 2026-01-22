#!/usr/bin/env python3
"""
test_ambiente.py - Verifica configurazione ambienti (Sviluppo vs Produzione)

Uso:
  python test_ambiente.py development  # Testa SQLite locale
  python test_ambiente.py production   # Testa MySQL/PostgreSQL cloud
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_development():
    """Test ambiente SVILUPPO (SQLite locale)"""
    print("\n" + "="*70)
    print("TEST AMBIENTE: SVILUPPO (SQLite Locale)")
    print("="*70 + "\n")
    
    os.environ['FLASK_ENV'] = 'development'
    flask_env = os.getenv('FLASK_ENV', 'development')
    
    print(f"✅ FLASK_ENV impostato a: {flask_env}")
    
    # Simula logica di app.py
    if flask_env == 'production':
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            db_uri = 'sqlite:///tablhero.db'
            print("⚠️  DATABASE_URL non impostata, uso fallback SQLite")
        else:
            db_uri = database_url
            print(f"✅ Usando DATABASE_URL: {database_url[:50]}...")
    else:
        db_uri = 'sqlite:///tablhero.db'
        print("✅ SVILUPPO: Usando SQLite locale")
    
    print(f"\n📊 DATABASE_URI configurata: {db_uri}")
    print(f"📁 File database: tablhero.db")
    print(f"⏱️  Avvio: python app.py")
    print(f"🌐 Accesso: http://localhost:5000")
    
    # Verifica file
    if os.path.exists('tablhero.db'):
        size = os.path.getsize('tablhero.db') / 1024  # KB
        print(f"✅ Database trovato: tablhero.db ({size:.1f} KB)")
    else:
        print(f"ℹ️  Database non ancora creato (verrà creato al primo avvio)")
    
    print("\n✅ TEST DÉVELOPPAMENTO: PASSATO\n")


def test_production():
    """Test ambiente PRODUZIONE (MySQL/PostgreSQL cloud)"""
    print("\n" + "="*70)
    print("TEST AMBIENTE: PRODUZIONE (Cloud Database)")
    print("="*70 + "\n")
    
    os.environ['FLASK_ENV'] = 'production'
    flask_env = os.getenv('FLASK_ENV', 'production')
    
    print(f"✅ FLASK_ENV impostato a: {flask_env}")
    
    # Simula logica di app.py
    if flask_env == 'production':
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("⚠️  ATTENZIONE: DATABASE_URL non impostata in produzione!")
            print("    (Necessaria quando deployato su Railway/Heroku/Cloud)")
            db_uri = 'sqlite:///tablhero.db'
            print("    Fallback a SQLite locale (non ideale per produzione)")
        else:
            db_uri = database_url
            print(f"✅ DATABASE_URL trovata: {database_url[:50]}...")
            print(f"✅ Tipo database: ", end="")
            
            if 'postgresql' in database_url:
                print("PostgreSQL")
            elif 'mysql' in database_url:
                print("MySQL")
            else:
                print("Altro (non standard)")
    else:
        db_uri = 'sqlite:///tablhero.db'
    
    print(f"\n📊 DATABASE_URI configurata: {db_uri}")
    
    if os.getenv('DATABASE_URL'):
        print(f"✅ Connessione cloud: ATTIVA")
    else:
        print(f"⚠️  Connessione cloud: NON CONFIGURATA (richiesta per produzione)")
    
    print(f"\n🚀 Deploy: railway up (o heroku create + git push)")
    print(f"🌐 Accesso: https://tuoapp.railway.app (url fornito dal provider)")
    
    print("\n⚠️  NOTA: Per la produzione vera, impostare DATABASE_URL")
    print("    railway variables set DATABASE_URL=...\n")


def test_current_config():
    """Mostra configurazione corrente"""
    print("\n" + "="*70)
    print("CONFIGURAZIONE CORRENTE")
    print("="*70 + "\n")
    
    flask_env = os.getenv('FLASK_ENV', 'development')
    database_url = os.getenv('DATABASE_URL', 'Non impostata')
    
    print(f"FLASK_ENV:   {flask_env}")
    print(f"DATABASE_URL: {database_url if database_url != 'Non impostata' else '⚠️  Non impostata'}")
    
    if flask_env == 'development':
        print(f"\n✅ Modalità: SVILUPPO (SQLite locale)")
        db_uri = 'sqlite:///tablhero.db'
    else:
        print(f"\n🔒 Modalità: PRODUZIONE")
        if database_url and database_url != 'Non impostata':
            db_uri = database_url
            print(f"✅ Database cloud configurato")
        else:
            db_uri = 'sqlite:///tablhero.db'
            print(f"⚠️  Database cloud NON configurato (fallback SQLite)")
    
    print(f"\nDatabase usato: {db_uri}\n")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == 'development' or arg == 'dev':
            test_development()
        elif arg == 'production' or arg == 'prod':
            test_production()
        elif arg == 'current':
            test_current_config()
        else:
            print(f"Parametro non riconosciuto: {arg}")
            print("\nUso: python test_ambiente.py [development|production|current]")
    else:
        test_current_config()
        print("\nUSO:")
        print("  python test_ambiente.py development  # Test ambiente SVILUPPO")
        print("  python test_ambiente.py production   # Test ambiente PRODUZIONE")
        print("  python test_ambiente.py current      # Configurazione attuale\n")
