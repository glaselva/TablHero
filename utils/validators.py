# utils/validators.py
import re
from email_validator import validate_email, EmailNotValidError

class PasswordValidator:
    """Validatore password con requisiti di sicurezza"""
    
    @staticmethod
    def validate(password):
        """
        Valida password con i seguenti requisiti:
        - Minimo 8 caratteri
        - Almeno 1 lettera maiuscola
        - Almeno 1 lettera minuscola
        - Almeno 1 numero
        - Almeno 1 carattere speciale (@#$%^&+=!?*)
        """
        errors = []
        
        if len(password) < 8:
            errors.append("La password deve contenere almeno 8 caratteri")
        
        if len(password) > 128:
            errors.append("La password non può superare i 128 caratteri")
        
        if not re.search(r'[A-Z]', password):
            errors.append("La password deve contenere almeno una lettera maiuscola")
        
        if not re.search(r'[a-z]', password):
            errors.append("La password deve contenere almeno una lettera minuscola")
        
        if not re.search(r'\d', password):
            errors.append("La password deve contenere almeno un numero")
        
        if not re.search(r'[@#$%^&+=!?*]', password):
            errors.append("La password deve contenere almeno un carattere speciale (@#$%^&+=!?*)")
        
        if re.search(r'\s', password):
            errors.append("La password non può contenere spazi")
        
        return errors

    @staticmethod
    def validate_match(password, confirm_password):
        """Verifica che le password corrispondano"""
        if password != confirm_password:
            return ["Le password non corrispondono"]
        return []


class EmailValidator:
    """Validatore email"""
    
    @staticmethod
    def validate(email):
        """Valida formato email"""
        errors = []
        
        if not email or len(email.strip()) == 0:
            errors.append("L'email è obbligatoria")
            return errors
        
        # Usa email-validator per validazione avanzata
        try:
            # Normalizza email
            valid = validate_email(email, check_deliverability=False)
            normalized_email = valid.email
            return []
        except EmailNotValidError as e:
            errors.append(f"Email non valida: {str(e)}")
            return errors


class NicknameValidator:
    """Validatore nickname"""
    
    @staticmethod
    def validate(nickname):
        """
        Valida nickname:
        - 3-20 caratteri
        - Solo lettere, numeri, underscore, trattini
        - Non inizia/finisce con underscore o trattino
        """
        errors = []
        
        if not nickname or len(nickname.strip()) == 0:
            errors.append("Il nickname è obbligatorio")
            return errors
        
        nickname = nickname.strip()
        
        if len(nickname) < 3:
            errors.append("Il nickname deve contenere almeno 3 caratteri")
        
        if len(nickname) > 20:
            errors.append("Il nickname non può superare i 20 caratteri")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', nickname):
            errors.append("Il nickname può contenere solo lettere, numeri, underscore (_) e trattini (-)")
        
        if nickname[0] in ['_', '-'] or nickname[-1] in ['_', '-']:
            errors.append("Il nickname non può iniziare o finire con underscore o trattino")
        
        # Blocca parole offensive (aggiungi altre se necessario)
        offensive_words = ['admin', 'root', 'moderator', 'tablehero', 'founder']
        if nickname.lower() in offensive_words:
            errors.append("Questo nickname non è disponibile")
        
        return errors


class NameValidator:
    """Validatore nome e cognome"""
    
    @staticmethod
    def validate(name, field_name="Nome"):
        """Valida nome/cognome"""
        errors = []
        
        if not name or len(name.strip()) == 0:
            errors.append(f"{field_name} è obbligatorio")
            return errors
        
        name = name.strip()
        
        if len(name) < 2:
            errors.append(f"{field_name} deve contenere almeno 2 caratteri")
        
        if len(name) > 50:
            errors.append(f"{field_name} non può superare i 50 caratteri")
        
        if not re.match(r"^[a-zA-ZàèéìòùÀÈÉÌÒÙáéíóúÁÉÍÓÚäëïöüÄËÏÖÜ'\s-]+$", name):
            errors.append(f"{field_name} può contenere solo lettere, spazi, apostrofi e trattini")
        
        return errors
