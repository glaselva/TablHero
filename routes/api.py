"""
API REST per app mobile (BeeWare)
Permette all'app mobile di comunicare con il backend Flask
"""
from flask import Blueprint, jsonify, request
from models import db
from models.user import User
from models.evento import Evento
from models.partecipazione import Partecipazione
from flask_login import login_required, current_user
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# ============ AUTENTICAZIONE ============

@api_bp.route('/login', methods=['POST'])
def api_login():
    """
    Login via API
    Body: {"email": "user@example.com", "password": "pwd"}
    Response: {"success": true, "token": "...", "user": {...}}
    """
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Email e password richieste'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'nome': user.nome,
                'ruolo': user.ruolo,
                'ha_pagato': user.ha_pagato,
                'tablexp': user.tablexp
            }
        }), 200
    
    return jsonify({'success': False, 'error': 'Credenziali non valide'}), 401


@api_bp.route('/register', methods=['POST'])
def api_register():
    """
    Registrazione via API
    Body: {"email": "...", "password": "...", "nome": "..."}
    """
    data = request.get_json()
    
    required_fields = ['email', 'password', 'nome']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'error': 'Campi mancanti'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'error': 'Email già registrata'}), 409
    
    try:
        user = User(
            email=data['email'],
            nome=data['nome'],
            ruolo='sidekick',
            attivo=True
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Utente registrato con successo',
            'user': {'id': user.id, 'email': user.email, 'nome': user.nome}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ EVENTI ============

@api_bp.route('/eventi', methods=['GET'])
def api_get_eventi():
    """
    Ottieni lista di eventi
    Query params: ?future=true (solo futuri), ?limit=10
    """
    limit = request.args.get('limit', 20, type=int)
    future_only = request.args.get('future', 'false').lower() == 'true'
    
    query = Evento.query
    
    if future_only:
        query = query.filter(Evento.data_evento > datetime.utcnow())
    
    query = query.order_by(Evento.data_evento.asc()).limit(limit)
    eventi = query.all()
    
    return jsonify({
        'success': True,
        'eventi': [{
            'id': e.id,
            'nome': e.nome,
            'descrizione': e.descrizione,
            'data_evento': e.data_evento.isoformat(),
            'luogo': e.luogo,
            'immagine': e.immagine,
            'partecipanti': e.partecipazioni.count(),
            'posti_disponibili': e.posti_massimi - e.partecipazioni.count()
        } for e in eventi]
    }), 200


@api_bp.route('/eventi/<int:evento_id>', methods=['GET'])
def api_get_evento(evento_id):
    """
    Ottieni dettagli di un evento specifico
    """
    evento = Evento.query.get(evento_id)
    
    if not evento:
        return jsonify({'success': False, 'error': 'Evento non trovato'}), 404
    
    return jsonify({
        'success': True,
        'evento': {
            'id': evento.id,
            'nome': evento.nome,
            'descrizione': evento.descrizione,
            'data_evento': evento.data_evento.isoformat(),
            'luogo': evento.luogo,
            'immagine': evento.immagine,
            'posti_massimi': evento.posti_massimi,
            'partecipanti_count': evento.partecipazioni.count(),
            'creato_da': evento.creato_da_user.nome if evento.creato_da_user else None
        }
    }), 200


# ============ PARTECIPAZIONI ============

@api_bp.route('/eventi/<int:evento_id>/join', methods=['POST'])
@login_required
def api_join_evento(evento_id):
    """
    Unisciti a un evento
    Richiede autenticazione
    """
    evento = Evento.query.get(evento_id)
    
    if not evento:
        return jsonify({'success': False, 'error': 'Evento non trovato'}), 404
    
    # Verifica se già iscritto
    existing = Partecipazione.query.filter_by(
        utente_id=current_user.id,
        evento_id=evento_id
    ).first()
    
    if existing:
        return jsonify({'success': False, 'error': 'Già iscritto a questo evento'}), 409
    
    # Verifica posti disponibili
    if evento.partecipazioni.count() >= evento.posti_massimi:
        return jsonify({'success': False, 'error': 'Evento pieno'}), 400
    
    try:
        partecipazione = Partecipazione(
            utente_id=current_user.id,
            evento_id=evento_id,
            status='confermato'
        )
        db.session.add(partecipazione)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Iscritto a {evento.nome}',
            'partecipazione': {'id': partecipazione.id, 'status': 'confermato'}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/eventi/<int:evento_id>/leave', methods=['POST'])
@login_required
def api_leave_evento(evento_id):
    """
    Esci da un evento
    """
    partecipazione = Partecipazione.query.filter_by(
        utente_id=current_user.id,
        evento_id=evento_id
    ).first()
    
    if not partecipazione:
        return jsonify({'success': False, 'error': 'Non sei iscritto a questo evento'}), 404
    
    try:
        db.session.delete(partecipazione)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Rimosso dall\'evento'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ LEADERBOARD ============

@api_bp.route('/leaderboard', methods=['GET'])
def api_leaderboard():
    """
    Ottieni leaderboard
    Query params: ?limit=100, ?ruolo=tablhero
    """
    limit = request.args.get('limit', 100, type=int)
    ruolo = request.args.get('ruolo', None)
    
    query = User.query.filter_by(attivo=True)
    
    if ruolo:
        query = query.filter_by(ruolo=ruolo)
    
    users = query.order_by(User.tablexp.desc()).limit(limit).all()
    
    return jsonify({
        'success': True,
        'leaderboard': [{
            'rank': idx + 1,
            'nome': u.nome,
            'ruolo': u.ruolo,
            'tablexp': u.tablexp,
            'livello': u.livello
        } for idx, u in enumerate(users)]
    }), 200


# ============ SALUTE DELL'API ============

@api_bp.route('/health', methods=['GET'])
def api_health():
    """
    Health check
    """
    return jsonify({
        'success': True,
        'status': 'API online',
        'version': '1.0',
        'database': 'SQLite (mobile-friendly)'
    }), 200
