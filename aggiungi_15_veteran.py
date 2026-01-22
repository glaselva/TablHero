# aggiungi_15_veteran.py - AGGIUNGE senza cancellare
from app import create_app
from models import db
from models.user import User
import random
from datetime import datetime, timedelta

app = create_app()
with app.app_context():

    # Conta utenti esistenti
    utenti_esistenti = User.query.count()
    print(f"👥 Utenti esistenti: {utenti_esistenti}")

    # 15 nomi italiani (Bari style)
    nomi = ['Mario', 'Luca', 'Giovanni', 'Antonio', 'Francesco', 'Paolo', 'Giuseppe', 'Salvatore', 'Angelo', 'Domenico', 'Vito', 'Michele', 'Pietro', 'Raffaele', 'Carmine']
    cognomi = ['Rossi', 'Russo', 'De Luca', 'Ferrari', 'Romano', 'Lombardi', 'Mancini', 'Greco', 'Gentile', 'Caruso', 'Palmisano', 'La Selva', 'Longo', 'Esposito', 'De Rosa']

    print("✅ Aggiunta 15 utenti Veteran...")
    utenti_nuovi = []

    for i in range(15):
        # Email uniche con suffisso numerico
        email = f"veteran{i+1}_extra@tablhero.it"

        user = User(
            nickname=f'veteran_extra{i+1}',
            nome=random.choice(nomi),
            cognome=random.choice(cognomi),
            email=email,
            ruolo='veteran',
            tabl_exp=random.randint(3500, 6500),  # Veteran range
            livello='platino',
            ha_pagato=True,           # ✅ Membri paganti
            data_scadenza=datetime.now() + timedelta(days=365),
            email_verificata=True,
            is_admin=False,
            attivo=True
        )
        user.set_password('VeteranPass123!')  # Tutti stessa password
        db.session.add(user)
        utenti_nuovi.append(user)

    db.session.commit()

    print("\n🎉 15 utenti Veteran AGGIUNTI!")
    print(f"📊 Totale ora: {User.query.count()} utenti")
    print(f"➕ Nuovi Veteran: {len(utenti_nuovi)}")
    print("\n🔑 Password per tutti: VeteranPass123!")
    print("\n📋 Primi 5 nuovi utenti:")

    for user in utenti_nuovi[:5]:
        print(f"  {user.nickname} | {user.nome} {user.cognome}")
        print(f"    📧 {user.email} | 🎖️ {user.ruolo} | 💰 {user.ha_pagato}")

    print("\n🚀 Test login: veteran1@tablhero.it / VeteranPass123!")
