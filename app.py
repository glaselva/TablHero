# app.py - CORRETTO (webhook dentro create_app())
from routes.leaderboard import leaderboard_bp
from flask import Flask, render_template, request  # ✅ AGGIUNTO request
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from models import db, bcrypt
from models.user import User
from models.evento import Evento  # ✅ AGGIUNTO
from models.partecipazione import Partecipazione  # ✅ AGGIUNTO
from flask_mail import Mail
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import os
import stripe

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # =====================================================================
    # CONFIGURAZIONE DATABASE DINAMICA PER AMBIENTI
    # =====================================================================
    # Se FLASK_ENV='production', tenta di usare DATABASE_URL
    # Altrimenti usa SQLite locale (sviluppo)
    flask_env = os.getenv('FLASK_ENV', 'development')
    
    if flask_env == 'production':
        # PRODUZIONE: Usa variabile d'ambiente DATABASE_URL (da cloud provider)
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("⚠️  ATTENZIONE: DATABASE_URL non impostata in produzione!")
            print("    Fallback a SQLite locale")
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tablhero.db'
        else:
            # PostgreSQL o MySQL dal provider cloud (Railway, Heroku, ecc)
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
            print(f"✅ Connesso a database REMOTO (produzione)")
    else:
        # SVILUPPO: SQLite locale
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tablhero.db'
        print(f"✅ Usando SQLite locale (sviluppo)")
    
    # Abilita CORS per le app mobile (BeeWare)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Session timeout aumentato per Stripe (24h invece di 30min)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Inizializza estensioni
    db.init_app(app)
    bcrypt.init_app(app)
    migrate = Migrate(app, db)
    
    # Configura Stripe
    stripe.api_key = app.config['STRIPE_SECRET_KEY']

    # Configura Flask-Mail
    mail = Mail(app)

    # Configura Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Effettua il login per accedere a questa pagina.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    @app.template_filter('livello_color')
    def livello_color_filter(livello):
        """Ritorna il colore esadecimale per ogni livello"""
        colori = {
            'bronzo': '#CD7F32',
            'argento': '#C0C0C0',
            'oro': '#FFD700',
            'platino': '#E5E4E2',
            'diamante': '#B9F2FF'
        }
        return colori.get(livello, '#CD7F32')

    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Converte i newline in <br> tags"""
        if text:
            return text.replace('\n', '<br>')
        return text
    
    # Registra blueprints (route)
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.eventi import eventi_bp
    from routes.admin import admin_bp
    from routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(eventi_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(api_bp)
    
    # Route homepage
    @app.route('/')
    def index():
        try:
            # Conta solo membri ATTIVI (escludi disattivati)
            total_members = User.query.filter_by(attivo=True).count()

            # Conta per ruolo (solo attivi)
            sidekick_count = User.query.filter_by(ruolo='sidekick', attivo=True).count()
            tablhero_count = User.query.filter_by(ruolo='tablhero', attivo=True).count()
            veteran_count = User.query.filter_by(ruolo='veteran', attivo=True).count()
            game_architect_count = User.query.filter_by(ruolo='game_architect', attivo=True).count()
            founder_count = User.query.filter_by(ruolo='founder', attivo=True).count()

            # Prossimi eventi per utenti iscritti
            prossimi_eventi = None
            if current_user.is_authenticated and current_user.ha_pagato:
                prossimi_eventi = (Evento.query
                                  .filter(Evento.data_evento > datetime.utcnow())
                                  .order_by(Evento.data_evento.asc())
                                  .limit(3)
                                  .all())
        except Exception as e:
            # Se il database non è disponibile, usa valori di default
            print(f"⚠️  Database non disponibile: {e}")
            total_members = 0
            sidekick_count = 0
            tablhero_count = 0
            veteran_count = 0
            game_architect_count = 0
            founder_count = 0
            prossimi_eventi = None

        return render_template('index.html',
                             total_members=total_members,
                             sidekick_count=sidekick_count,
                             tablhero_count=tablhero_count,
                             veteran_count=veteran_count,
                             game_architect_count=game_architect_count,
                             founder_count=founder_count,
                             prossimi_eventi=prossimi_eventi)
    
    # Route pagina info
    @app.route('/info')
    def info():
        return render_template('info.html')
    
    # Route contatti
    @app.route('/contatti')
    def contatti():
        return render_template('contatti.html')

    # Route TableGuild
    @app.route('/tableguild')
    def tableguild():
        return render_template('tableguild.html')
    
    @app.route('/stripe/webhook', methods=['POST'])
    def stripe_webhook():
        print("🚨 WEBHOOK ARRIVATO! 🎉")
        print(f"Headers: {dict(request.headers)}")

        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        endpoint_secret = app.config.get('STRIPE_WEBHOOK_SECRET')

        print(f"🔑 Secret configurato: {'SÌ' if endpoint_secret else 'NO'}")

        # 🔓 TEMPORANEO: Skip verifica per debug
        try:
            import json
            event_data = json.loads(payload)
            print(f"✅ Evento: {event_data.get('type')}")
            print(f"Metadata: {event_data['data']['object'].get('metadata', {})}")
        except Exception as e:
            print(f"❌ Parse fallito: {e}")
            return '', 400

        # 🔄 LOGICA ORIGINALE (solo se debug OK)
        if event_data.get('type') == 'checkout.session.completed':
            session = event_data['data']['object']
            metadata = session.get('metadata', {})

            # 🎫 PAGAMENTO EVENTO
            if 'eventoid' in metadata:
                user_id = int(metadata['userid'])
                evento_id = int(metadata['eventoid'])

                user = User.query.get(user_id)
                evento = Evento.query.get(evento_id)

                if user and evento:
                    # Check if event is in the past
                    if evento.data_evento and evento.data_evento <= datetime.utcnow():
                        print(f"❌ PAGAMENTO RIFIUTATO: Evento passato {evento.titolo}")
                        return '', 400

                    existing = Partecipazione.query.filter_by(user_id=user_id, evento_id=evento_id).first()
                    if not existing:
                        partecipaz = Partecipazione(user_id=user_id, evento_id=evento_id, exp_guadagnata=evento.exp_reward)
                        user.aggiungi_exp(evento.exp_reward)
                        db.session.add(partecipaz)
                        db.session.commit()
                        print(f"✅ AUTO-ISCRITTO EVENTO: {user.nickname}")

            # 🔄 RINNOVO MEMBERSHIP
            elif metadata.get('tipo') == 'renew':
                user_id = int(metadata['userid'])

                user = User.query.get(user_id)
                if user:
                    # Sostituisci la logica: usa data scadenza esistente + 365gg
                    user.ha_pagato = True
                    if user.data_scadenza:
                        user.data_scadenza = user.data_scadenza + timedelta(days=365)  # DA SCADENZA ESISTENTE
                    else:
                        user.data_scadenza = datetime.utcnow() + timedelta(days=365)  # Fallback se non c'è scadenza
                    user.payment_status = 'completed'
                    # Upgrade sidekick to tablhero upon membership renewal
                    if user.ruolo == 'sidekick':
                        user.ruolo = 'tablhero'
                    db.session.commit()
                    print(f"✅ RENEW {user.nickname}: Membership da SCADENZA +365gg")

            # 🎫 MEMBERSHIP GENERICO (nuova O renew)
            elif metadata.get('tipo') == 'membership':
                user_id = int(metadata['userid'])

                user = User.query.get(user_id)
                if user:
                    user.ha_pagato = True
                    if user.data_scadenza and user.data_scadenza > datetime.utcnow():
                        # Se è un rinnovo, usa scadenza esistente + 365gg
                        user.data_scadenza = user.data_scadenza + timedelta(days=365)
                    else:
                        # Se è nuova membership, usa oggi + 365gg
                        user.data_scadenza = datetime.utcnow() + timedelta(days=365)
                    user.payment_status = 'completed'
                    # Upgrade sidekick to tablhero upon membership purchase
                    if user.ruolo == 'sidekick':
                        user.ruolo = 'tablhero'
                    db.session.commit()
                    print(f"✅ MEMBERSHIP {user.nickname}: Attivata da SCADENZA +365gg")

        return '', 200

    
    # Crea le tabelle del database
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"⚠️  Avvertenza: Impossibile connettersi al database: {e}")
            print("L'app avvierà comunque in modalità sviluppo senza database")

        # 🔄 SCHEDULER PER REMINDER AUTOMATICI
        def job_reminder():
            """Invia reminder automatici per eventi domani alle 9:00"""
            with app.app_context():
                # Calcola domani (inizio e fine giornata)
                domani = datetime.utcnow() + timedelta(days=1)
                domani_inizio = datetime(domani.year, domani.month, domani.day, 0, 0, 0)
                domani_fine = datetime(domani.year, domani.month, domani.day, 23, 59, 59)

                # Query eventi domani
                eventi_domani = Evento.query.filter(
                    Evento.data_evento >= domani_inizio,
                    Evento.data_evento <= domani_fine
                ).all()

                print(f"🔍 Trovati {len(eventi_domani)} eventi domani")

                total_reminders = 0

                for evento in eventi_domani:
                    if evento.partecipazioni:  # Solo se ci sono partecipanti
                        print(f"📧 Invio reminder per: {evento.titolo}")

                        for partecipazione in evento.partecipazioni:
                            try:
                                from flask_mail import Message
                                msg = Message(
                                    subject=f'Reminder: {evento.titolo} domani! - TableHero',
                                    recipients=[partecipazione.user.email],
                                    html=f'<h2>Reminder Evento Automatico</h2><p>Ciao {partecipazione.user.nome},<br><strong>{evento.titolo}</strong> è domani {evento.data_evento.strftime("%d/%m/%Y alle %H:%M")}!</p><p>Non mancare! 🎲</p>'
                                )
                                mail.send(msg)
                                total_reminders += 1

                                print(f"✅ Reminder inviato a: {partecipazione.user.email}")

                            except Exception as e:
                                print(f"❌ Errore invio a {partecipazione.user.email}: {e}")

                print(f"📊 Reminder totali inviati: {total_reminders}")

        # Avvia scheduler per reminder automatici
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            job_reminder,
            trigger=CronTrigger(hour=9, timezone='Europe/Rome'),  # Ogni giorno alle 9:00
            id='daily_reminder',
            name='Invio reminder eventi giornaliero'
        )
        scheduler.start()

        print("Scheduler reminder avviato - invio alle 9:00 Europe/Rome")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
