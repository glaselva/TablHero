# models/partecipazione.py
from models import db
from datetime import datetime

class Partecipazione(db.Model):
    __tablename__ = 'partecipazioni'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventi.id'), nullable=False)
    data_partecipazione = db.Column(db.DateTime, default=datetime.utcnow)
    exp_guadagnata = db.Column(db.Integer)

    # Relazioni
    user = db.relationship('User', backref=db.backref('partecipazioni_user', lazy=True, overlaps='partecipazioni,utente'))

    def __repr__(self):
        return f'<Partecipazione User:{self.user_id} Event:{self.evento_id}>'
