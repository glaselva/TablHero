# routes/leaderboard.py
from flask import Blueprint, render_template
from models.user import User

leaderboard_bp = Blueprint('leaderboard', __name__)


@leaderboard_bp.route('/leaderboard')
def index():
    """Classifica utenti per TablExp"""
    
    # Top 50 utenti per exp (escludi account disattivi)
    top_users = User.query.filter_by(attivo=True).order_by(User.tabl_exp.desc()).limit(50).all()
    
    # Statistiche generali
    total_members = User.query.filter_by(attivo=True).count()
    total_exp = sum([u.tabl_exp for u in User.query.filter_by(attivo=True).all()])
    avg_exp = total_exp / total_members if total_members > 0 else 0
    
    # Top per ruolo
    top_sidekick = User.query.filter_by(ruolo='sidekick', attivo=True).order_by(User.tabl_exp.desc()).first()
    top_tablhero = User.query.filter_by(ruolo='tablhero', attivo=True).order_by(User.tabl_exp.desc()).first()
    top_veteran = User.query.filter_by(ruolo='veteran', attivo=True).order_by(User.tabl_exp.desc()).first()
    top_architect = User.query.filter_by(ruolo='game_architect', attivo=True).order_by(User.tabl_exp.desc()).first()
    
    return render_template('leaderboard.html',
                         top_users=top_users,
                         total_members=total_members,
                         total_exp=total_exp,
                         avg_exp=int(avg_exp),
                         top_sidekick=top_sidekick,
                         top_tablhero=top_tablhero,
                         top_veteran=top_veteran,
                         top_architect=top_architect)
