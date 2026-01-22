"""
TablHero Mobile App - BeeWare
Applicazione mobile che si connette all'API REST del backend Flask

Per creare il progetto BeeWare:
    $ briefcase new --template=mobile

Poi installare nel pyproject.toml:
    - requests (per HTTP calls)
    - json (built-in)
"""

import asyncio
import requests
import json
from datetime import datetime

# Configurazione API
API_BASE_URL = "http://localhost:5000/api/v1"  # Cambia in produzione
TIMEOUT = 10


class TablHeroMobileClient:
    """Client per comunicare con l'API REST di TablHero"""
    
    def __init__(self, api_url=API_BASE_URL):
        self.api_url = api_url
        self.user_token = None
        self.user_data = None
    
    def check_health(self):
        """Verifica che il server sia online"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=TIMEOUT)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    # ============ AUTENTICAZIONE ============
    
    def register(self, email, password, nome):
        """Registra un nuovo utente"""
        try:
            response = requests.post(
                f"{self.api_url}/register",
                json={"email": email, "password": password, "nome": nome},
                timeout=TIMEOUT
            )
            result = response.json()
            if result.get('success'):
                self.user_data = result.get('user')
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def login(self, email, password):
        """Effettua il login"""
        try:
            response = requests.post(
                f"{self.api_url}/login",
                json={"email": email, "password": password},
                timeout=TIMEOUT
            )
            result = response.json()
            if result.get('success'):
                self.user_data = result.get('user')
                self.user_token = email  # In prod: use JWT token
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============ EVENTI ============
    
    def get_eventi(self, future_only=True, limit=20):
        """Ottieni lista di eventi"""
        try:
            params = {
                'future': 'true' if future_only else 'false',
                'limit': limit
            }
            response = requests.get(
                f"{self.api_url}/eventi",
                params=params,
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_evento(self, evento_id):
        """Ottieni dettagli di un evento"""
        try:
            response = requests.get(
                f"{self.api_url}/eventi/{evento_id}",
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def join_evento(self, evento_id):
        """Unisciti a un evento"""
        try:
            headers = self._get_auth_headers()
            response = requests.post(
                f"{self.api_url}/eventi/{evento_id}/join",
                headers=headers,
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def leave_evento(self, evento_id):
        """Esci da un evento"""
        try:
            headers = self._get_auth_headers()
            response = requests.post(
                f"{self.api_url}/eventi/{evento_id}/leave",
                headers=headers,
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============ LEADERBOARD ============
    
    def get_leaderboard(self, limit=100, ruolo=None):
        """Ottieni leaderboard"""
        try:
            params = {'limit': limit}
            if ruolo:
                params['ruolo'] = ruolo
            
            response = requests.get(
                f"{self.api_url}/leaderboard",
                params=params,
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============ UTILITY ============
    
    def _get_auth_headers(self):
        """Ritorna gli header di autenticazione"""
        headers = {}
        if self.user_token:
            headers['Authorization'] = f'Bearer {self.user_token}'
        return headers
    
    def is_authenticated(self):
        """Controlla se l'utente è autenticato"""
        return self.user_data is not None


# ============ ESEMPIO DI UTILIZZO ============

if __name__ == "__main__":
    # Inizializza il client
    client = TablHeroMobileClient()
    
    # Test connessione
    print("1️⃣  Test salute API...")
    health = client.check_health()
    print(f"   Status: {health}")
    
    # Test registration
    print("\n2️⃣  Registrazione...")
    reg_result = client.register(
        email="mobile_user@example.com",
        password="testpass123",
        nome="Mobile User"
    )
    print(f"   Risultato: {reg_result}")
    
    # Test login
    print("\n3️⃣  Login...")
    login_result = client.login(
        email="mobile_user@example.com",
        password="testpass123"
    )
    print(f"   Risultato: {login_result}")
    print(f"   Utente autenticato: {client.is_authenticated()}")
    
    # Test get eventi
    print("\n4️⃣  Ottieni eventi futuri...")
    eventi_result = client.get_eventi(future_only=True, limit=5)
    print(f"   Risultato: {eventi_result}")
    
    if eventi_result.get('success') and eventi_result.get('eventi'):
        primo_evento = eventi_result['eventi'][0]
        print(f"\n5️⃣  Dettagli evento: {primo_evento['nome']}")
        evento_detail = client.get_evento(primo_evento['id'])
        print(f"   Risultato: {evento_detail}")
    
    # Test leaderboard
    print("\n6️⃣  Leaderboard...")
    leaderboard = client.get_leaderboard(limit=5)
    print(f"   Top 5 utenti: {leaderboard}")
