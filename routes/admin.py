# routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_mail import Message, Mail
from functools import wraps
from models import db
from models.user import User
from models.evento import Evento
from models.partecipazione import Partecipazione
from datetime import datetime, timedelta

# Inizializza mail per admin
mail = Mail()

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator per proteggere le route admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accesso negato: serve permesso amministratore!', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def panel():
    """Pannello amministratore principale"""
    
    # Statistiche generali
    total_users = User.query.count()
    total_eventi = Evento.query.count()
    total_partecipazioni = Partecipazione.query.count()
    
    # Utenti per ruolo
    sidekick_count = User.query.filter_by(ruolo='sidekick').count()
    tablhero_count = User.query.filter_by(ruolo='tablhero').count()
    veteran_count = User.query.filter_by(ruolo='veteran').count()
    master_count = User.query.filter_by(ruolo='master').count()
    architect_count = User.query.filter_by(ruolo='architect').count()
    coordinator_count = User.query.filter_by(ruolo='coordinator').count()
    
    # Ultimi utenti registrati
    ultimi_utenti = User.query.order_by(User.data_registrazione.desc()).limit(10).all()
    
    # Prossimi eventi
    prossimi_eventi = (Evento.query
                      .filter(Evento.data_evento > datetime.utcnow())
                      .order_by(Evento.data_evento.asc())
                      .limit(5)
                      .all())
    
    return render_template('admin/panel.html',
                         total_users=total_users,
                         total_eventi=total_eventi,
                         total_partecipazioni=total_partecipazioni,
                         sidekick_count=sidekick_count,
                         tablhero_count=tablhero_count,
                         veteran_count=veteran_count,
                         master_count=master_count,
                         architect_count=architect_count,
                         coordinator_count=coordinator_count,
                         ultimi_utenti=ultimi_utenti,
                         prossimi_eventi=prossimi_eventi)

@admin_bp.route('/utenti')
@login_required
@admin_required
def gestione_utenti():
    """Pagina gestione utenti"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    ruolo_filter = request.args.get('ruolo', '')
    
    query = User.query
    
    # Filtro ricerca
    if search:
        query = query.filter(
            (User.nickname.contains(search)) |
            (User.email.contains(search)) |
            (User.nome.contains(search)) |
            (User.cognome.contains(search))
        )
    
    # Filtro ruolo
    if ruolo_filter:
        query = query.filter_by(ruolo=ruolo_filter)
    
    # Paginazione
    utenti = query.order_by(User.data_registrazione.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/utenti.html', 
                         utenti=utenti, 
                         search=search,
                         ruolo_filter=ruolo_filter)

@admin_bp.route('/utenti/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_utente(user_id):
    """Modifica utente"""
    user = User.query.get_or_404(user_id)

    if user.ruolo == 'founder' and current_user.ruolo != 'founder':
        flash('Solo i Founder possono modificare altri Founder!', 'error')
        return redirect(url_for('admin.gestione_utenti'))
    
    if request.method == 'POST':
        old_ruolo = user.ruolo
        user.nickname = request.form.get('nickname', user.nickname)
        user.nome = request.form.get('nome', user.nome)
        user.cognome = request.form.get('cognome', user.cognome)
        user.email = request.form.get('email', user.email)
        new_ruolo = request.form.get('ruolo', user.ruolo)
        user.ruolo = new_ruolo
        user.tabl_exp = int(request.form.get('tabl_exp', user.tabl_exp))
        user.attivo = request.form.get('attivo') == 'on'

        # Auto-grant membership for paid roles
        paid_roles = ['tablhero', 'veteran']
        if new_ruolo in paid_roles and old_ruolo not in paid_roles:
            user.ha_pagato = True
            user.data_scadenza = datetime.utcnow() + timedelta(days=365)  # 1 year membership
            user.payment_status = 'completed'

        # Aggiorna livello in base alla nuova exp
        user.aggiorna_livello()

        # Cambia password se fornita
        new_password = request.form.get('new_password')
        if new_password:
            print(f"Changing password for user {user.nickname}")
            user.set_password(new_password)
            print(f"Password changed successfully")

        try:
            db.session.commit()
            flash(f'Utente {user.nickname} aggiornato con successo!', 'success')
            return redirect(url_for('admin.gestione_utenti'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante l\'aggiornamento: {str(e)}', 'error')
    
    return render_template('admin/edit_utente.html', user=user)

@admin_bp.route('/utenti/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_utente(user_id):
    """Elimina utente"""
    user = User.query.get_or_404(user_id)
    
    # Non permettere di eliminare se stesso
    if user.id == current_user.id:
        flash('Non puoi eliminare il tuo stesso account!', 'error')
        return redirect(url_for('admin.gestione_utenti'))
    
    # Non permettere di eliminare altri admin
    if user.is_admin:
        flash('Non puoi eliminare altri amministratori!', 'error')
        return redirect(url_for('admin.gestione_utenti'))
    
    try:
        nickname = user.nickname
        db.session.delete(user)
        db.session.commit()
        flash(f'Utente {nickname} eliminato con successo.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
    
    return redirect(url_for('admin.gestione_utenti'))

@admin_bp.route('/utenti/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Attiva/disattiva privilegi admin"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Non puoi modificare i tuoi stessi privilegi!', 'error')
        return redirect(url_for('admin.gestione_utenti'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'attivati' if user.is_admin else 'disattivati'
    flash(f'Privilegi admin {status} per {user.nickname}', 'success')
    
    return redirect(url_for('admin.gestione_utenti'))

@admin_bp.route('/eventi')
@login_required
@admin_required
def gestione_eventi():
    """Pagina gestione eventi"""
    page = request.args.get('page', 1, type=int)
    tipo_filter = request.args.get('tipo', '')
    
    query = Evento.query
    
    if tipo_filter:
        query = query.filter_by(tipo=tipo_filter)
    
    eventi = query.order_by(Evento.data_evento.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/eventi.html',
                         eventi=eventi,
                         tipo_filter=tipo_filter,
                         now=datetime.utcnow())

@admin_bp.route('/eventi/nuovo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuovo_evento():
    """Crea nuovo evento"""
    if request.method == 'POST':
        titolo = request.form.get('titolo')
        descrizione = request.form.get('descrizione')
        tipo = request.form.get('tipo')
        data_evento_str = request.form.get('data_evento')
        max_partecipanti = request.form.get('max_partecipanti')
        exp_reward = request.form.get('exp_reward', 50)
        immagine_url = request.form.get('immagine_url')
        
        # Validazione
        if not all([titolo, tipo, data_evento_str]):
            flash('Compila tutti i campi obbligatori!', 'error')
            return redirect(url_for('admin.nuovo_evento'))
        
        try:
            # Converti data
            data_evento = datetime.strptime(data_evento_str, '%Y-%m-%dT%H:%M')
            
            nuovo_evento = Evento(
                titolo=titolo,
                descrizione=descrizione,
                tipo=tipo,
                data_evento=data_evento,
                max_partecipanti=int(max_partecipanti) if max_partecipanti else None,
                exp_reward=int(exp_reward),
                immagine_url=immagine_url,
                creato_da=current_user.id
            )
            
            db.session.add(nuovo_evento)
            db.session.commit()
            
            flash(f'Evento "{titolo}" creato con successo!', 'success')
            return redirect(url_for('admin.gestione_eventi'))
            
        except ValueError:
            flash('Formato data non valido!', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la creazione: {str(e)}', 'error')
    
    return render_template('admin/nuovo_evento.html')

@admin_bp.route('/eventi/<int:evento_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_evento(evento_id):
    """Modifica evento"""
    evento = Evento.query.get_or_404(evento_id)
    
    if request.method == 'POST':
        evento.titolo = request.form.get('titolo', evento.titolo)
        evento.descrizione = request.form.get('descrizione', evento.descrizione)
        evento.tipo = request.form.get('tipo', evento.tipo)
        
        data_evento_str = request.form.get('data_evento')
        if data_evento_str:
            try:
                evento.data_evento = datetime.strptime(data_evento_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Formato data non valido!', 'error')
                return redirect(url_for('admin.edit_evento', evento_id=evento_id))
        
        max_part = request.form.get('max_partecipanti')
        evento.max_partecipanti = int(max_part) if max_part else None

        # Handle override for past events
        if evento.data_evento and evento.data_evento < datetime.utcnow():
            override_part = request.form.get('override_partecipanti')
            evento.override_partecipanti = int(override_part) if override_part else None

        evento.exp_reward = int(request.form.get('exp_reward', evento.exp_reward))
        evento.immagine_url = request.form.get('immagine_url', evento.immagine_url)
        
        try:
            db.session.commit()
            flash(f'Evento "{evento.titolo}" aggiornato!', 'success')
            return redirect(url_for('admin.gestione_eventi'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante l\'aggiornamento: {str(e)}', 'error')
    
    return render_template('admin/edit_evento.html', evento=evento, now=datetime.utcnow())

@admin_bp.route('/eventi/<int:evento_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_evento(evento_id):
    """Elimina evento"""
    evento = Evento.query.get_or_404(evento_id)
    
    try:
        titolo = evento.titolo
        db.session.delete(evento)
        db.session.commit()
        flash(f'Evento "{titolo}" eliminato con successo.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
    
    return redirect(url_for('admin.gestione_eventi'))

@admin_bp.route('/eventi/<int:evento_id>/partecipanti')
@login_required
@admin_required
def partecipanti_evento(evento_id):
    """Visualizza partecipanti di un evento"""
    evento = Evento.query.get_or_404(evento_id)
    partecipazioni = Partecipazione.query.filter_by(evento_id=evento_id).all()

    return render_template('admin/partecipanti_evento.html',
                         evento=evento,
                         partecipazioni=partecipazioni)

@admin_bp.route('/eventi/<int:evento_id>/rimuovi-partecipante/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def rimuovi_partecipante(evento_id, user_id):
    """Rimuovi un partecipante specifico da un evento"""
    partecipazione = Partecipazione.query.filter_by(
        evento_id=evento_id, user_id=user_id
    ).first_or_404()

    # Rimuovi TablExp guadagnati dall'evento
    partecipazione.user.tabl_exp = max(0, partecipazione.user.tabl_exp - partecipazione.exp_guadagnata)
    partecipazione.user.aggiorna_livello()

    # Rimuovi partecipazione
    db.session.delete(partecipazione)
    db.session.commit()

    flash(f'Partecipante {partecipazione.user.nickname} rimosso dall\'evento.', 'success')
    return redirect(url_for('admin.edit_evento', evento_id=evento_id))

@admin_bp.route('/eventi/<int:evento_id>/rimuovi-tutti-partecipanti', methods=['POST'])
@login_required
@admin_required
def rimuovi_tutti_partecipanti(evento_id):
    """Rimuovi tutti i partecipanti da un evento"""
    evento = Evento.query.get_or_404(evento_id)
    partecipazioni = Partecipazione.query.filter_by(evento_id=evento_id).all()

    removed_count = 0
    for partecipazione in partecipazioni:
        # Rimuovi TablExp guadagnati dall'evento
        partecipazione.user.tabl_exp = max(0, partecipazione.user.tabl_exp - partecipazione.exp_guadagnata)
        partecipazione.user.aggiorna_livello()

        # Rimuovi partecipazione
        db.session.delete(partecipazione)
        removed_count += 1

    db.session.commit()

    flash(f'Tutti i partecipanti ({removed_count}) sono stati rimossi dall\'evento.', 'success')
    return redirect(url_for('admin.edit_evento', evento_id=evento_id))

@admin_bp.route('/statistiche')
@login_required
@admin_required
def statistiche():
    """Pagina statistiche dettagliate"""
    
    # Statistiche utenti per livello
    stats_livelli = {}
    for livello in ['bronzo', 'argento', 'oro', 'platino', 'diamante']:
        stats_livelli[livello] = User.query.filter_by(livello=livello).count()
    
    # Top 10 utenti per exp
    top_users = User.query.order_by(User.tabl_exp.desc()).limit(10).all()
    
    # Eventi più popolari
    eventi_popolari = (db.session.query(Evento, db.func.count(Partecipazione.id).label('partecipanti'))
                       .join(Partecipazione)
                       .group_by(Evento.id)
                       .order_by(db.text('partecipanti DESC'))
                       .limit(10)
                       .all())
    
    return render_template('admin/statistiche.html',
                         stats_livelli=stats_livelli,
                         top_users=top_users,
                         eventi_popolari=eventi_popolari)

@admin_bp.route('/invia_reminder/<int:evento_id>')
@login_required
@admin_required
def invia_reminder(evento_id):
    """Invia reminder email a tutti i partecipanti dell'evento"""
    evento = Evento.query.get_or_404(evento_id)

    # Conta quanti reminder sono stati inviati
    sent_count = 0

    for partecipazione in evento.partecipazioni:
        try:
            msg = Message(
                subject=f'Reminder: {evento.titolo} domani! - TableHero',
                recipients=[partecipazione.user.email],
                html=f'<h2>Reminder Evento</h2><p>Ciao {partecipazione.user.nome},<br><strong>{evento.titolo}</strong> è domani {evento.data_evento.strftime("%d/%m/%Y alle %H:%M")}!</p><a href="[link]">Dettagli</a>'
            )
            mail.send(msg)
            sent_count += 1
        except Exception as e:
            print(f"Errore invio email a {partecipazione.user.email}: {e}")

    flash(f'Reminder inviati a {sent_count} partecipanti!', 'success')
    return redirect(url_for('admin.gestione_eventi'))

@admin_bp.route('/stats')
@login_required
@admin_required
def stats():
    """Dashboard statistiche admin"""
    from datetime import datetime, timedelta
    from collections import Counter

    # Metriche base
    total_users = User.query.filter_by(attivo=True).count()
    utenti_verificati = User.query.filter_by(attivo=True, email_verificata=True).count()
    utenti_non_verificati = total_users - utenti_verificati

    # Conteggio per ruolo (solo attivi), escludi game_architect
    ruoli_stats = db.session.query(
        User.ruolo,
        db.func.count(User.id)
    ).filter(User.attivo==True, User.ruolo != 'game_architect').group_by(User.ruolo).all()

    ruolo_counts = dict(ruoli_stats)

    # Eventi
    eventi_totali = Evento.query.count()
    eventi_prossimi = Evento.query.filter(Evento.data_evento > datetime.utcnow()).count()
    eventi_passati = eventi_totali - eventi_prossimi

    # Partecipazioni totali
    partecipazioni_totali = Partecipazione.query.count()

    # Leaderboard top 5
    top_users = User.query.filter_by(attivo=True)\
        .order_by(User.tabl_exp.desc())\
        .limit(5).all()

    # Trends ultimi 30 giorni (semplificato)
    da_30gg = datetime.utcnow() - timedelta(days=30)
    nuovi_utenti_30gg = User.query.filter(
        User.data_registrazione >= da_30gg,
        User.attivo == True
    ).count()

    return render_template('admin/stats.html',
        total_users=total_users,
        utenti_verificati=utenti_verificati,
        utenti_non_verificati=utenti_non_verificati,
        ruolo_counts=ruolo_counts,
        eventi_totali=eventi_totali,
        eventi_prossimi=eventi_prossimi,
        eventi_passati=eventi_passati,
        partecipazioni_totali=partecipazioni_totali,
        top_users=top_users,
        nuovi_utenti_30gg=nuovi_utenti_30gg
    )
