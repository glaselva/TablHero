# models/user.py
from models import db, bcrypt
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(50), nullable=False)
    cognome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    email_verificata = db.Column(db.Boolean, default=False)
    token_verifica = db.Column(db.String(100), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Membership pagamento
    ha_pagato = db.Column(db.Boolean, default=False)
    data_scadenza = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String(255), nullable=True)  # UNA VOLTA SOLO
    payment_status = db.Column(db.Enum('pending', 'completed', 'failed'), default='pending')
    
    # Ruoli
    ruolo = db.Column(db.Enum('sidekick', 'tablhero', 'veteran', 'master', 'architect', 'coordinator', 'founder'),
                      default='sidekick', nullable=False)
    
    # Sistema TablExp
    tabl_exp = db.Column(db.Integer, default=0)
    livello = db.Column(db.Enum('bronzo', 'argento', 'oro', 'platino', 'diamante'), default='bronzo')
    
    # Metadata
    data_registrazione = db.Column(db.DateTime, default=datetime.utcnow)
    attivo = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relazioni
    partecipazioni = db.relationship('Partecipazione', backref='utente', 
                                    lazy=True, cascade='all, delete-orphan')
    
    def puo_iscriversi_eventi(self):
        """Verifica se l'utente può iscriversi agli eventi (membership valida)"""
        # Founder e admin sempre accesso
        if self.ruolo in ['founder'] or self.is_admin:
            return True
        
        if not self.ha_pagato:
            return False
        
        # Controlla scadenza
        if self.data_scadenza and self.data_scadenza < datetime.utcnow():
            self.ha_pagato = False
            db.session.commit()
            return False
        
        return True
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def aggiungi_exp(self, exp_amount):
        self.tabl_exp += exp_amount
        self.aggiorna_livello()
    
    def aggiorna_livello(self):
        from config import Config
        nuovo_livello = Config.calcola_livello(self.tabl_exp)
        if nuovo_livello != self.livello:
            self.livello = nuovo_livello
            return True
        return False
    
    def get_progresso_livello(self):
        exp = self.tabl_exp
        if exp < 500:
            return (exp / 500) * 100
        elif exp < 1500:
            return ((exp - 500) / 1000) * 100
        elif exp < 3500:
            return ((exp - 1500) / 2000) * 100
        elif exp < 7500:
            return ((exp - 3500) / 4000) * 100
        else:
            return 100
    
    def __repr__(self):
        return f'<User {self.nickname} - {self.ruolo}>'
