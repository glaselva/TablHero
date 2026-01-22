# reset_users.py - RESET UTENTI E CREA 3 FOUNDER
from app import create_app
from models import db
from models.user import User
from models.partecipazione import Partecipazione
from models.evento import Evento

app = create_app()

with app.app_context():
    print("Inizio reset utenti...")

    # 1. Elimina tutte le partecipazioni (foreign key)
    partecipazioni_count = Partecipazione.query.count()
    Partecipazione.query.delete()
    print(f"Eliminate {partecipazioni_count} partecipazioni")

    # 2. Elimina tutti gli eventi (foreign key verso users)
    eventi_count = Evento.query.count()
    Evento.query.delete()
    print(f"Eliminati {eventi_count} eventi")

    # 3. Elimina tutti gli utenti
    users_count = User.query.count()
    User.query.delete()
    print(f"Eliminati {users_count} utenti")

    db.session.commit()

    # 3. Crea i 3 Founder
    founders_data = [
        {
            'nickname': 'giuseppe',
            'nome': 'Giuseppe',
            'cognome': 'La Selva',
            'email': 'giuseppe.tablhero@gmail.com',
            'password': 'FounderPass123!'  # Cambia con password sicura
        },
        {
            'nickname': 'alessandro',
            'nome': 'Alessandro',
            'cognome': 'Palmisano',
            'email': 'alessandro@tablhero.it',  # Sostituisci con email vera
            'password': 'FounderPass123!'
        },
        {
            'nickname': 'domenico',
            'nome': 'Domenico',
            'cognome': 'Longo',
            'email': 'domenico@tablhero.it',  # Sostituisci con email vera
            'password': 'FounderPass123!'
        }
    ]

    for founder_data in founders_data:
        founder = User(
            nickname=founder_data['nickname'],
            nome=founder_data['nome'],
            cognome=founder_data['cognome'],
            email=founder_data['email'],
            ruolo='founder',
            tabl_exp=9999,
            livello='diamante',
            is_admin=True,
            email_verificata=True,  # ✅ Verificati di default
            ha_pagato=True,
            attivo=True
        )
        founder.set_password(founder_data['password'])
        db.session.add(founder)
        print(f"Creato Founder: {founder.nome} {founder.cognome} ({founder.email})")

    db.session.commit()

    print("\nReset completato!")
    print("Totale utenti nel database:", User.query.count())
    print("\nFounder creati:")
    for user in User.query.filter_by(ruolo='founder').all():
        print(f"   - {user.nickname} | {user.nome} {user.cognome} | {user.email} | TablExp: {user.tabl_exp}")

    print("\nPassword di default per tutti: FounderPass123!")
    print("IMPORTANTE: Cambia le password dopo il primo login!")
