# routes/dashboard.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.evento import Evento
from models.partecipazione import Partecipazione
from config import Config
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principale dell'utente"""
    
    # Calcola statistiche
    total_eventi = Partecipazione.query.filter_by(user_id=current_user.id).count()
    progresso = current_user.get_progresso_livello()
    exp_per_prossimo = Config.exp_per_prossimo_livello(current_user.tabl_exp)
    
    # Eventi recenti
    partecipazioni_recenti = (Partecipazione.query
                             .filter_by(user_id=current_user.id)
                             .order_by(Partecipazione.data_partecipazione.desc())
                             .limit(5)
                             .all())
    
    # Prossimi eventi disponibili
    prossimi_eventi = (Evento.query
                      .filter(Evento.data_evento > datetime.utcnow())
                      .order_by(Evento.data_evento.asc())
                      .limit(3)
                      .all())
    
    now = datetime.utcnow()
    return render_template('dashboard.html',
                         total_eventi=total_eventi,
                         progresso=progresso,
                         exp_per_prossimo=exp_per_prossimo,
                         partecipazioni_recenti=partecipazioni_recenti,
                         prossimi_eventi=prossimi_eventi,
                         now=now)

@dashboard_bp.route('/profilo')
@login_required
def profilo():
    """Pagina profilo utente"""
    return render_template('profilo.html', user=current_user)

@dashboard_bp.route('/eventi')
@login_required
def miei_eventi():
    """Lista eventi a cui l'utente ha partecipato"""
    partecipazioni = (Partecipazione.query
                     .filter_by(user_id=current_user.id)
                     .order_by(Partecipazione.data_partecipazione.desc())
                     .all())

    return render_template('miei_eventi.html', partecipazioni=partecipazioni)

@dashboard_bp.route('/disiscriviti', methods=['POST'])
@login_required
def disiscriviti():
    if current_user.ruolo == 'founder' or current_user.is_admin:
        flash('Founder/Admin non possono disiscriversi.', 'warning')
        return redirect(url_for('dashboard.index'))

    # Check for upcoming events
    from datetime import datetime
    upcoming_participations = Partecipazione.query.join(Evento).filter(
        Partecipazione.user_id == current_user.id,
        Evento.data_evento > datetime.utcnow()
    ).all()

    if upcoming_participations:
        flash('Non puoi cancellare la membership se sei iscritto a eventi futuri. Annulla prima le tue iscrizioni agli eventi.', 'warning')
        return redirect(url_for('dashboard.index'))

    # Reset membership
    current_user.ha_pagato = False
    current_user.data_scadenza = None
    current_user.payment_status = 'pending'

    # Demote back to sidekick role
    if current_user.ruolo == 'tablhero':
        current_user.ruolo = 'sidekick'

    # Rimuovi tutte partecipazioni (solo eventi passati)
    Partecipazione.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    flash('Disiscritto con successo! Puoi riabbonarti dalla Dashboard.', 'success')
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/cancella-account', methods=['POST'])
@login_required
def cancella_account():
    if current_user.ruolo == 'founder' or current_user.is_admin:
        flash('Founder/Admin non possono cancellare l\'account.', 'warning')
        return redirect(url_for('dashboard.index'))

    if current_user.ha_pagato:
        flash('Devi prima disiscriverti dalla membership prima di poter cancellare l\'account.', 'warning')
        return redirect(url_for('dashboard.index'))

    # Delete all user data
    Partecipazione.query.filter_by(user_id=current_user.id).delete()
    db.session.delete(current_user)
    db.session.commit()

    flash('Account cancellato con successo.', 'success')
    return redirect(url_for('auth.login'))

@dashboard_bp.route('/membership/renew', methods=['POST'])
@login_required
def renew_membership():
    if current_user.ruolo == 'founder' or current_user.is_admin:
        flash('Founder/Admin non necessitano renew.', 'info')
        return redirect(url_for('dashboard.index'))

    # ✅ SEMPRE accessibile (nuova O renew)
    import stripe
    stripe.api_key = Config.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {'name': 'Membership TableHero Annuale'},
                'unit_amount': 2000,  # 20€
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('dashboard.index', _external=True) + '?renewed=1',
        cancel_url=url_for('dashboard.index', _external=True),
        customer_email=current_user.email,
        metadata={'userid': str(current_user.id), 'tipo': 'membership'}
    )
    return redirect(session.url, code=303)
