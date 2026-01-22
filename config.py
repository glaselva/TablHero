# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-molto-sicura'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/tablhero'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Stripe Configuration
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Prezzi in centesimi (Euro)
    PRICE_TABLHERO = 2000  # 20€
    PRICE_VETERAN = 0  # Assegnato manualmente - non acquistabile
    PRICE_GAME_ARCHITECT = 3000  # 30€
    PRICE_FOUNDER = 0  # Non acquistabile
    
    # Flask-Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Livelli TablExp
    LIVELLI = {
        'bronzo': (1, 500),
        'argento': (501, 1500),
        'oro': (1501, 3500),
        'platino': (3501, 7500),
        'diamante': (7501, float('inf'))
    }
    
    @staticmethod
    def calcola_livello(exp):
        """Calcola il livello in base all'esperienza"""
        if exp >= 7501:
            return 'diamante'
        elif exp >= 3501:
            return 'platino'
        elif exp >= 1501:
            return 'oro'
        elif exp >= 501:
            return 'argento'
        else:
            return 'bronzo'
    
    @staticmethod
    def exp_per_prossimo_livello(exp):
        """Calcola l'exp necessaria per il prossimo livello"""
        if exp < 500:
            return 500 - exp
        elif exp < 1500:
            return 1500 - exp
        elif exp < 3500:
            return 3500 - exp
        elif exp < 7500:
            return 7500 - exp
        else:
            return 0  # Livello massimo raggiunto
