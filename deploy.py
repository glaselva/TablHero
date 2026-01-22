#!/usr/bin/env python3
"""
Script di deployment per TablHero su server remoto
Supporta: Railway, Heroku, DigitalOcean, AWS

Uso:
    python deploy.py --platform railway
    python deploy.py --platform heroku
    python deploy.py --target production
"""

import os
import subprocess
import sys
from pathlib import Path

class TablHeroDeployer:
    """Gestore del deployment per TablHero"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.platform = None
        self.environment = "development"
    
    def create_procfile(self):
        """Crea Procfile per Heroku/Railway"""
        procfile_content = """web: gunicorn app:app
worker: python app.py
"""
        procfile_path = self.project_root / "Procfile"
        with open(procfile_path, 'w') as f:
            f.write(procfile_content)
        print(f"✅ Procfile creato: {procfile_path}")
    
    def create_runtime_txt(self):
        """Specifica Python version per Heroku"""
        runtime_content = "python-3.11.8\n"
        runtime_path = self.project_root / "runtime.txt"
        with open(runtime_path, 'w') as f:
            f.write(runtime_content)
        print(f"✅ runtime.txt creato")
    
    def create_dockerfile(self):
        """Crea Dockerfile per Docker deployment"""
        dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copia app
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:5000/api/v1/health')"

# Run
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
'''
        dockerfile_path = self.project_root / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        print(f"✅ Dockerfile creato")
    
    def create_railway_config(self):
        """Crea configurazione per Railway.app"""
        railway_json = {
            "build": {
                "builder": "nix"
            },
            "deploy": {
                "numReplicas": 1,
                "startCommand": "gunicorn app:app"
            },
            "plugins": [
                "python@3.11",
                "postgresql"
            ]
        }
        
        import json
        railway_path = self.project_root / "railway.json"
        with open(railway_path, 'w') as f:
            json.dump(railway_json, f, indent=2)
        print(f"✅ railway.json creato")
    
    def create_env_example(self):
        """Crea .env.example con variabili necessarie"""
        env_example = """# TablHero Configuration

# Flask
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here-change-this

# Database
DATABASE_URL=sqlite:///tablhero.db
# Oppure PostgreSQL per produzione:
# DATABASE_URL=postgresql://user:password@host:5432/tablhero

# Stripe (opzionale)
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@tablhero.com

# Server
SERVER_URL=https://your-app.railway.app
CORS_ORIGINS=http://localhost:*,https://your-app.railway.app

# API Mobile
API_VERSION=1.0
API_RATE_LIMIT=100/hour
"""
        env_example_path = self.project_root / ".env.example"
        with open(env_example_path, 'w') as f:
            f.write(env_example)
        print(f"✅ .env.example creato")
    
    def deploy_railway(self):
        """Deploy su Railway.app"""
        print("\n🚀 Deployment su Railway.app")
        print("Prerequisites:")
        print("  1. Crea account su railway.app")
        print("  2. Installa Railway CLI: npm install -g railway")
        print("  3. Esegui: railway login")
        print("\nComandi:")
        print("  railway up")
        print("  railway open")
        print("\nDopo il deploy:")
        print("  1. Prendi l'URL del progetto")
        print("  2. Aggiorna mobile_client.py con l'URL")
        print("  3. Ricompila la BeeWare app")
    
    def deploy_heroku(self):
        """Deploy su Heroku"""
        print("\n🚀 Deployment su Heroku")
        print("Prerequisites:")
        print("  1. Crea account su heroku.com")
        print("  2. Installa Heroku CLI")
        print("  3. Esegui: heroku login")
        print("\nComandi:")
        print("  heroku create your-app-name")
        print("  git push heroku main")
        print("  heroku config:set FLASK_ENV=production")
        print("  heroku open")
    
    def deploy_docker(self):
        """Deploy con Docker"""
        print("\n🚀 Deployment con Docker")
        print("Comandi:")
        print("  docker build -t tablhero .")
        print("  docker run -p 5000:5000 \\")
        print("    -e FLASK_ENV=production \\")
        print("    -e SECRET_KEY=your-key \\")
        print("    tablhero")
    
    def setup_all(self):
        """Prepara tutti i file di deployment"""
        print("📦 Preparazione file di deployment...\n")
        
        self.create_procfile()
        self.create_runtime_txt()
        self.create_dockerfile()
        self.create_railway_config()
        self.create_env_example()
        
        print("\n✅ Setup completato!")
        print("\nFile creati:")
        print("  - Procfile")
        print("  - runtime.txt")
        print("  - Dockerfile")
        print("  - railway.json")
        print("  - .env.example")
    
    def print_menu(self):
        """Stampa il menu di deployment"""
        print("\n" + "="*50)
        print("🚀 TablHero Deployment")
        print("="*50)
        print("\nOpzioni:")
        print("  1. Setup files per deployment")
        print("  2. Deploy su Railway.app")
        print("  3. Deploy su Heroku")
        print("  4. Deploy con Docker")
        print("  0. Esci")
        print("\n" + "="*50)


def main():
    deployer = TablHeroDeployer()
    
    if len(sys.argv) > 1:
        # CLI mode
        if sys.argv[1] == "--setup":
            deployer.setup_all()
        elif sys.argv[1] == "--railway":
            deployer.setup_all()
            deployer.deploy_railway()
        elif sys.argv[1] == "--heroku":
            deployer.setup_all()
            deployer.deploy_heroku()
        elif sys.argv[1] == "--docker":
            deployer.setup_all()
            deployer.deploy_docker()
    else:
        # Interactive mode
        deployer.setup_all()
        print("\n\n📚 Documentazione:")
        print("  - MOBILE_ARCHITECTURE.md")
        print("  - BEAWARE_QUICKSTART.md")
        print("  - SETUP_MOBILE_COMPLETE.md")


if __name__ == "__main__":
    main()
