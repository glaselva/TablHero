# routes/eventi.py - PREMIUM GRATIS + VET/TABLHERO PAGA
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from flask_mail import Mail
from models import db
from models.evento import Evento
from models.partecipazione import Partecipazione
from utils.email import send_conferma_iscrizione
from datetime import datetime
import stripe

eventi_bp = Blueprint('eventi', __name__, url_prefix='/eventi')

@eventi_bp.route('/')
def lista():
    tipo_filtro = request.args.get('tipo', None)
    query = Evento.query.filter(
        Evento.data_evento > datetime.utcnow(),
        Evento.data_evento.isnot(None)
    )
    if tipo_filtro and tipo_filtro in ['giochi_tavolo', 'giochi_ruolo']:
        query = query.filter_by(tipo=tipo_filtro)
    eventi = query.order_by(Evento.data_evento.asc()).all()
    return render_template('eventi.html', eventi=eventi, tipo_filtro=tipo_filtro, now=datetime.utcnow())

@eventi_bp.route('/passati')
def eventi_passati():
    tipo_filtro = request.args.get('tipo')
    query = Evento.query.filter(
        Evento.data_evento < datetime.utcnow(),
        Evento.data_evento.isnot(None)
    )
    if tipo_filtro:
        query = query.filter_by(tipo=tipo_filtro)
    eventi = query.order_by(Evento.data_evento.desc()).all()
    return render_template('eventi_passati.html', eventi=eventi, tipo_filtro=tipo_filtro)

@eventi_bp.route('/<int:evento_id>')
def dettaglio(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    gia_iscritto = False
    user_is_premium = False
    prezzo_finale = 0.0
    sconto_pct = 0
    
    if current_user.is_authenticated:
        gia_iscritto = Partecipazione.query.filter_by(
            user_id=current_user.id, evento_id=evento_id
        ).first() is not None
        
        # ✅ PREMIUM ROLES: GRATIS SEMPRE
        premium_roles = ['tablhero', 'founder']
        user_is_premium = current_user.ruolo in premium_roles
        
        # Prezzo SOLO per SIDEKICK
        if not user_is_premium:
            prezzo_finale = 20.0 if evento.tipo == 'giochiruolo' else 15.0
        else:
            prezzo_finale = 0.0
            sconto_pct = 100
    
    return render_template('evento_dettaglio.html',
                          evento=evento,
                          gia_iscritto=gia_iscritto,
                          user_is_premium=user_is_premium,
                          prezzo_finale=prezzo_finale,
                          sconto_pct=sconto_pct,
                          now=datetime.utcnow())

@eventi_bp.route('/<int:evento_id>/iscrivi', methods=['POST'])
@login_required
def iscriviti(evento_id):
    """✅ ISCRIZIONE GRATIS PER PREMIUM ROLES"""
    evento = Evento.query.get_or_404(evento_id)

    # Check if event is in the past
    if evento.data_evento and evento.data_evento <= datetime.utcnow():
        flash('❌ Non puoi iscriverti a eventi passati!', 'error')
        return redirect(url_for('eventi.dettaglio', evento_id=evento_id))

    # PREMIUM ROLES: tablhero, founder
    premium_roles = ['tablhero', 'founder']
    if current_user.ruolo not in premium_roles:
        flash('❌ Solo ruoli premium possono partecipare GRATIS!', 'error')
        return redirect(url_for('eventi.dettaglio', evento_id=evento_id))

    # Check già iscritto / pieno
    if Partecipazione.query.filter_by(user_id=current_user.id, evento_id=evento_id).first():
        flash('Già iscritto!', 'warning')
        return redirect(url_for('eventi.dettaglio', evento_id=evento_id))

    if evento.is_full():
        flash('Evento completo!', 'error')
        return redirect(url_for('eventi.dettaglio', evento_id=evento_id))

    # ✅ ISCRIZIONE + EXP
    partecipaz = Partecipazione(
        user_id=current_user.id,
        evento_id=evento_id,
        exp_guadagnata=evento.exp_reward
    )
    current_user.aggiungi_exp(evento.exp_reward)
    db.session.add(partecipaz)
    db.session.commit()

    # Invia email di conferma
    mail = Mail(current_app)
    try:
        send_conferma_iscrizione(
            mail,
            current_user.email,
            current_user.nome,
            evento.titolo,
            evento.data_evento.strftime('%d/%m/%Y alle %H:%M')
        )
    except Exception as e:
        print(f"Errore invio email conferma: {e}")

    flash(f'✅ Iscritto GRATIS! +{evento.exp_reward} TablExp 🎉', 'success')
    return redirect(url_for('eventi.dettaglio', evento_id=evento_id))


@eventi_bp.route('/<int:evento_id>/paga', methods=['POST'])
@login_required
def paga_evento(evento_id):
    """💳 PAGAMENTO PER CHI VUOLE PAGARE (TablHero, Game Architect, Veteran)"""
    evento = Evento.query.get_or_404(evento_id)

    # Check if event is in the past
    if evento.data_evento and evento.data_evento <= datetime.utcnow():
        flash('❌ Non puoi iscriverti a eventi passati!', 'error')
        return redirect(url_for('eventi.dettaglio', evento_id=evento_id))

    # CONSENTI PAGAMENTO A CHI VUOLE (incluso premium che vuole supportare)
    allowed_roles = ['tablhero', 'game_architect', 'veteran']
    if current_user.ruolo not in allowed_roles:
        flash('Solo TablHero, Game Architect e Veteran possono pagare eventi.', 'error')
        return redirect(url_for('eventi.dettaglio', evento_id=evento_id))

    prezzo_base = float(evento.prezzo or (20.0 if evento.tipo == 'giochiruolo' else 15.0))

    # Sconti per premium che pagano comunque
    if current_user.ruolo == 'tablhero':
        prezzo_finale = round(prezzo_base * 0.75, 2)  # 25% sconto
    elif current_user.ruolo == 'game_architect':
        prezzo_finale = round(prezzo_base * 0.5, 2)  # 50% sconto
    elif current_user.ruolo == 'veteran':
        prezzo_finale = round(prezzo_base * 0.75, 2)  # 25% sconto
    else:
        prezzo_finale = round(prezzo_base, 2)  # No sconto
    
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'🎲 {evento.titolo} ({current_user.ruolo.replace("_", " ").title()})',
                        'description': f'Supporta la community TableHero!'
                    },
                    'unit_amount': int(prezzo_finale * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('eventi.dettaglio', evento_id=evento_id, _external=True) + '?pagato=1',
            cancel_url=url_for('eventi.dettaglio', evento_id=evento_id, _external=True),
            customer_email=current_user.email,
            metadata={
                'userid': str(current_user.id),
                'eventoid': str(evento_id),
                'tipo': 'evento'
            }
        )
        return redirect(session.url, code=303)
    except Exception as e:
        flash(f'Errore: {str(e)}', 'error')
        return redirect(url_for('eventi.dettaglio', evento_id=evento_id))

@eventi_bp.route('/<int:evento_id>/annulla', methods=['POST'])
@login_required
def annulla_iscrizione(evento_id):
    partecipazione = Partecipazione.query.filter_by(
        user_id=current_user.id, evento_id=evento_id
    ).first_or_404()
    
    current_user.tabl_exp = max(0, current_user.tabl_exp - partecipazione.exp_guadagnata)
    current_user.aggiorna_livello()
    
    db.session.delete(partecipazione)
    db.session.commit()
    
    flash('Iscrizione annullata.', 'info')
    return redirect(url_for('eventi.dettaglio', evento_id=evento_id))
