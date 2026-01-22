# models/evento.py
from models import db
from datetime import datetime

class Evento(db.Model):
    __tablename__ = 'eventi'
    
    prezzo = db.Column(db.Numeric(10,2), default=15.00)
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text)
    tipo = db.Column(db.Enum('giochi_tavolo', 'giochi_ruolo'), nullable=False)
    data_evento = db.Column(db.DateTime, nullable=False)
    max_partecipanti = db.Column(db.Integer)
    override_partecipanti = db.Column(db.Integer)  # Manual override for past events
    exp_reward = db.Column(db.Integer, default=50)
    immagine_url = db.Column(db.String(255))
    
    creato_da = db.Column(db.Integer, db.ForeignKey('users.id'))
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    partecipazioni = db.relationship('Partecipazione', backref='evento',
                                    lazy=True, cascade='all, delete-orphan')
    
    def is_full(self):
        """Controlla se l'evento è pieno"""
        if self.max_partecipanti:
            return len(self.partecipazioni) >= self.max_partecipanti
        return False
    
    def posti_disponibili(self):
        """Ritorna i posti disponibili"""
        if self.max_partecipanti:
            return self.max_partecipanti - len(self.partecipazioni)
        return None
    
    def __repr__(self):
        return f'<Evento {self.titolo} - {self.tipo}>'
