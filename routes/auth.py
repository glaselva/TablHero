# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Mail
from models import db
from models.user import User
from config import Config
from utils.validators import PasswordValidator, EmailValidator, NicknameValidator, NameValidator
from utils.email import genera_token_verifica, send_email_verifica
from datetime import datetime, timedelta
import stripe

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Recupera dati dal form
        nickname = request.form.get('nickname', '').strip()
        nome = request.form.get('nome', '').strip()
        cognome = request.form.get('cognome', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        ruolo = request.form.get('ruolo')
        
        # Lista errori di validazione
        errors = []
        
        # Validazione campi obbligatori
        if not all([nickname, nome, cognome, email, password, ruolo]):
            flash('Tutti i campi sono obbligatori!', 'error')
            return redirect(url_for('auth.register'))
        
        # Blocca ruoli non registrabili
        if ruolo in ['founder', 'veteran']:
            flash('Questo ruolo non è disponibile per la registrazione!', 'error')
            return redirect(url_for('auth.register'))
        
        # Valida nickname
        nickname_errors = NicknameValidator.validate(nickname)
        errors.extend(nickname_errors)
        
        # Valida nome e cognome
        nome_errors = NameValidator.validate(nome, "Nome")
        errors.extend(nome_errors)
        
        cognome_errors = NameValidator.validate(cognome, "Cognome")
        errors.extend(cognome_errors)
        
        # Valida email
        email_errors = EmailValidator.validate(email)
        errors.extend(email_errors)
        
        # Valida password
        password_errors = PasswordValidator.validate(password)
        errors.extend(password_errors)
        
        # Verifica corrispondenza password
        match_errors = PasswordValidator.validate_match(password, confirm_password)
        errors.extend(match_errors)
        
        # Se ci sono errori, mostrali
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('auth.register'))
        
        # Controlla se nickname o email esistono già
        if User.query.filter_by(nickname=nickname).first():
            flash('Nickname già in uso!', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email già registrata!', 'error')
            return redirect(url_for('auth.register'))
        
        # Genera token verifica
        token = genera_token_verifica()

        # Crea nuovo utente
        new_user = User(
            nickname=nickname,
            nome=nome,
            cognome=cognome,
            email=email,
            token_verifica=token,
            email_verificata=False,
            ruolo=ruolo
        )
        new_user.set_password(password)

        # Se il ruolo richiede pagamento
        if ruolo in ['tablhero']:
            # Salva temporaneamente l'utente nella sessione
            session['pending_user'] = {
                'nickname': nickname,
                'nome': nome,
                'cognome': cognome,
                'email': email,
                'password': password,
                'ruolo': ruolo,
                'token_verifica': token
            }

            # Reindirizza a pagamento
            return redirect(url_for('auth.checkout'))
        else:
            # Sidekick è gratis
            new_user.payment_status = 'completed'
            db.session.add(new_user)
            db.session.commit()

            # Invia email verifica
            mail = Mail(current_app)
            try:
                send_email_verifica(mail, email, nome, token)
                flash('✅ Registrazione completata! Controlla la tua email per verificare l\'account.', 'success')
            except Exception as e:
                print(f"Errore invio email verifica: {e}")
                flash('⚠️ Account creato, ma email non inviata. Contatta l\'admin.', 'warning')

            return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        # Validazione base
        if not nickname or not email or not password:
            flash('Nickname, email e password sono obbligatori!', 'error')
            return redirect(url_for('auth.login'))

        # Trova utente per nickname
        user = User.query.filter_by(nickname=nickname).first()

        # Verifica che l'email corrisponda
        if user and user.email != email:
            flash('Nickname ed email non corrispondono!', 'error')
            return redirect(url_for('auth.login'))

        # Debug logging
        print(f"Login attempt: nickname={nickname}, email={email}, user_found={user is not None}")
        if user:
            print(f"User: {user.nickname}, attivo={user.attivo}, password_check={user.check_password(password)}")

        if user and user.check_password(password):
            if not user.attivo:
                flash('Account disattivato. Contatta un amministratore.', 'error')
                return redirect(url_for('auth.login'))

            # ✅ AGGIUNGI QUESTO CHECK
            if not user.email_verificata:
                flash('⚠️ Devi verificare la tua email prima di accedere. Controlla la tua inbox!', 'warning')
                return redirect(url_for('auth.login'))

            login_user(user, remember=remember)
            flash(f'Bentornato {user.nickname}!', 'success')

            # Reindirizza alla pagina richiesta o alla dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Credenziali non corrette!', 'error')

    return render_template('login.html')

@auth_bp.route('/checkout/renew')
@login_required
def checkout_renew():
    """Pagina di pagamento Stripe per rinnovo membership"""
    ruolo = request.args.get('ruolo', current_user.ruolo)

    # Determina il prezzo rinnovo (sempre 20€)
    amount = 2000  # 20€ in centesimi

    try:
        # Crea sessione di checkout Stripe per rinnovo
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'Rinnovo Annuale TableHero - {ruolo.replace("_", " ").title()}',
                        'description': f'Rinnovo membership annuale',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('auth.renew_success', _external=True),
            cancel_url=url_for('dashboard.index', _external=True),
            customer_email=current_user.email,
            metadata={
                'userid': str(current_user.id),
                'tipo': 'renew'
            }
        )

        return render_template('checkout.html',
                             session_id=checkout_session.id,
                             public_key=Config.STRIPE_PUBLIC_KEY)

    except Exception as e:
        flash(f'Errore durante la creazione della sessione di pagamento: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@auth_bp.route('/checkout')
def checkout():
    """Pagina di pagamento Stripe per registrazione"""
    if 'pending_user' not in session:
        flash('Sessione scaduta, riprova la registrazione.', 'error')
        return redirect(url_for('auth.register'))

    user_data = session['pending_user']
    ruolo = user_data['ruolo']

    # Determina il prezzo
    amount = Config.PRICE_TABLHERO if ruolo == 'tablhero' else Config.PRICE_GAME_ARCHITECT
    
    try:
        # Crea sessione di checkout Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'Abbonamento TableHero - {ruolo.replace("_", " ").title()}',
                        'description': f'Iscrizione come {ruolo.replace("_", " ").title()}',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('auth.payment_success', _external=True),
            cancel_url=url_for('auth.payment_cancel', _external=True),
            customer_email=user_data['email'],
            metadata={
                'userid': 'pending_registration',
                'tipo': 'registrazione'
            }
        )
        
        return render_template('checkout.html', 
                             session_id=checkout_session.id,
                             public_key=Config.STRIPE_PUBLIC_KEY)
    
    except Exception as e:
        flash(f'Errore durante la creazione della sessione di pagamento: {str(e)}', 'error')
        return redirect(url_for('auth.register'))

@auth_bp.route('/payment/success')
def payment_success():
    """Callback dopo pagamento completato"""
    if 'pending_user' not in session:
        flash('Sessione scaduta.', 'error')
        return redirect(url_for('auth.register'))

    user_data = session.pop('pending_user')

    # Crea l'utente nel database
    new_user = User(
        nickname=user_data['nickname'],
        nome=user_data['nome'],
        cognome=user_data['cognome'],
        email=user_data['email'],
        ruolo=user_data['ruolo'],
        payment_status='completed',
        token_verifica=user_data['token_verifica'],
        email_verificata=False
    )
    new_user.set_password(user_data['password'])

    # Se hanno pagato per tablhero, attiva membership
    if user_data['ruolo'] == 'tablhero':
        new_user.ha_pagato = True
        new_user.data_scadenza = datetime.utcnow() + timedelta(days=365)

    db.session.add(new_user)
    db.session.commit()

    # Invia email verifica
    mail = Mail(current_app)
    try:
        send_email_verifica(mail, user_data['email'], user_data['nome'], user_data['token_verifica'])
        flash('✅ Pagamento completato! Controlla la tua email per verificare l\'account.', 'success')
    except Exception as e:
        print(f"Errore invio email verifica: {e}")
        flash('⚠️ Pagamento completato, ma email non inviata. Contatta l\'admin.', 'warning')

    return redirect(url_for('auth.login'))

@auth_bp.route('/payment/cancel')
def payment_cancel():
    """Callback se pagamento viene cancellato"""
    flash('Pagamento cancellato. Puoi riprovare quando vuoi.', 'warning')
    return redirect(url_for('auth.register'))

@auth_bp.route('/renew/success')
@login_required
def renew_success():
    """Callback dopo rinnovo membership completato"""
    # Sostituisci la logica:
    current_user.ha_pagato = True
    current_user.data_scadenza = datetime.utcnow() + timedelta(days=365)  # SEMPRE da OGGI
    current_user.payment_status = 'completed'
    db.session.commit()

    flash('✅ Membership rinnovata con successo! +365gg di accesso.', 'success')
    return redirect(url_for('dashboard.index'))



@auth_bp.route('/verifica/<token>')
def verifica_email(token):
    """Verifica email tramite token"""
    user = User.query.filter_by(token_verifica=token).first()

    if not user:
        flash('❌ Link di verifica non valido o scaduto.', 'error')
        return redirect(url_for('auth.login'))

    if user.email_verificata:
        flash('✅ Email già verificata! Puoi fare il login.', 'info')
        return redirect(url_for('auth.login'))

    # Verifica email
    user.email_verificata = True
    user.token_verifica = None  # Invalida token
    db.session.commit()

    flash('🎉 Email verificata con successo! Ora puoi accedere.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reinvia-verifica', methods=['POST'])
def reinvia_verifica():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()

    if not user:
        flash('Email non trovata.', 'error')
        return redirect(url_for('auth.login'))

    if user.email_verificata:
        flash('Email già verificata!', 'info')
        return redirect(url_for('auth.login'))

    # Genera nuovo token
    token = genera_token_verifica()
    user.token_verifica = token
    db.session.commit()

    # Reinvia email
    mail = Mail(current_app)
    try:
        send_email_verifica(mail, user.email, user.nome, token)
        flash('✅ Email di verifica reinviata! Controlla la tua inbox.', 'success')
    except Exception as e:
        flash('Errore invio email. Riprova.', 'error')

    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout effettuato con successo!', 'success')
    return redirect(url_for('index'))
