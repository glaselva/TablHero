# utils/email.py - VERSIONE FINALE
from flask_mail import Message
import secrets
from flask import url_for

def genera_token_verifica():
    """Genera token sicuro per verifica email"""
    return secrets.token_urlsafe(32)

def send_email_verifica(mail, user_email, user_nome, token):
    """Invia email con link di verifica"""
    link_verifica = url_for('auth.verifica_email', token=token, _external=True)

    msg = Message(
        subject='🔐 Verifica il tuo account TableHero',
        recipients=[user_email],
        html=f'''
        <div style="font-family: 'Orbitron', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #fff; padding: 30px; border-radius: 15px;">
            <h2 style="color: #D4AF37; text-align: center; margin-bottom: 20px;">🎲 Benvenuto su TableHero!</h2>

            <p style="font-size: 16px;">Ciao <strong style="color: #D4AF37;">{user_nome}</strong>! 👋</p>

            <p style="margin: 20px 0;">Grazie per esserti registrato alla community nerd di Gioia del Colle!</p>

            <div style="background: rgba(212, 175, 55, 0.1); padding: 20px; border-left: 4px solid #D4AF37; margin: 30px 0; border-radius: 8px;">
                <p style="margin: 0; font-size: 14px;">Per completare la registrazione e accedere agli eventi, clicca il pulsante qui sotto:</p>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{link_verifica}" style="display: inline-block; background: #D4AF37; color: #1a1a2e; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
                    ✅ Verifica Email
                </a>
            </div>

            <p style="font-size: 12px; color: #999; margin-top: 30px;">Se non hai creato questo account, ignora questa email.</p>

            <p style="font-size: 11px; color: #666; margin-top: 20px;">Link alternativo (se il pulsante non funziona):<br>
            <a href="{link_verifica}" style="color: #D4AF37; word-break: break-all;">{link_verifica}</a></p>

            <hr style="border: none; border-top: 1px solid rgba(212, 175, 55, 0.3); margin: 30px 0;">

            <p style="text-align: center; color: #999; font-size: 12px;">
                <strong>TableHero</strong><br>
                La tua community nerd a Gioia del Colle 🏰
            </p>
        </div>
        '''
    )
    mail.send(msg)

def send_conferma_iscrizione(mail, user_email, user_nome, evento_titolo, evento_data):
    """Invia email conferma iscrizione evento"""
    msg = Message(
        subject=f'✅ Iscrizione confermata: {evento_titolo}',
        recipients=[user_email],
        html=f'''
        <div style="font-family: 'Orbitron', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #fff; padding: 30px; border-radius: 15px;">
            <h2 style="color: #D4AF37; text-align: center; margin-bottom: 20px;">🎲 TableHero - Conferma Iscrizione</h2>
            
            <p style="font-size: 16px;">Ciao <strong style="color: #D4AF37;">{user_nome}</strong>! 🎉</p>
            
            <p style="margin: 20px 0;">Sei ufficialmente iscritto a:</p>
            
            <div style="background: rgba(212, 175, 55, 0.1); padding: 20px; border-left: 4px solid #D4AF37; margin: 20px 0; border-radius: 8px;">
                <h3 style="color: #D4AF37; margin: 0 0 10px 0;">{evento_titolo}</h3>
                <p style="margin: 5px 0; font-size: 16px;">📅 <strong>Data:</strong> {evento_data}</p>
            </div>
            
            <p style="font-size: 14px; margin-top: 30px;">Ci vediamo lì! Non dimenticare di portare entusiasmo e dadi! 🎲</p>
            
            <hr style="border: none; border-top: 1px solid rgba(212, 175, 55, 0.3); margin: 30px 0;">
            
            <p style="text-align: center; color: #999; font-size: 12px;">
                <strong>TableHero</strong><br>
                La tua community nerd a Gioia del Colle 🏰
            </p>
        </div>
        '''
    )
    mail.send(msg)
