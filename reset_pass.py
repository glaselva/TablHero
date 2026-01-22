from app import create_app
from models import db
from models.user import User

app = create_app()
with app.app_context():
    # Reset password Giuseppe
    giuseppe = User.query.filter_by(email='giuseppe@tablehero.it').first()
    if giuseppe:
        giuseppe.set_password('NuovaPassword123!')
        print("Password aggiornata per Giuseppe")
    else:
        print("Utente Giuseppe non trovato")

    # Reset password Alessandro
    alessandro = User.query.filter_by(email='alessandro@tablhero.it').first()
    if alessandro:
        alessandro.set_password('NuovaPassword123!')
        print("Password aggiornata per Alessandro")
    else:
        print("Utente Alessandro non trovato")

    # Reset password Domenico
    domenico = User.query.filter_by(email='domenico@tablhero.it').first()
    if domenico:
        domenico.set_password('NuovaPassword123!')
        print("Password aggiornata per Domenico")
    else:
        print("Utente Domenico non trovato")

    db.session.commit()
    print("Password aggiornate!")
