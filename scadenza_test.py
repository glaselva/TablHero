# scadenza_test.py - Imposta scadenza pinodaniele per test
from app import create_app
from models import db
from models.user import User
from datetime import datetime, timedelta

app = create_app()
with app.app_context():

    # Trova utente pinodaniele
    user = User.query.filter_by(nickname='pinodaniele').first()

    if user:
        print(f"✅ Trovato: {user.nickname} - {user.nome} {user.cognome}")

        # Imposta scadenza a 25 giorni da oggi
        scadenza = datetime.utcnow() + timedelta(days=25)
        user.data_scadenza = scadenza
        user.ha_pagato = True
        user.payment_status = 'completed'

        db.session.commit()

        print(f"📅 Scadenza impostata a: {scadenza.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📊 Status: ha_pagato={user.ha_pagato}")
        print("✅ Modifiche applicate!")

    else:
        print("❌ Utente pinodaniele non trovato")
