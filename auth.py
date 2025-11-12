from typing import Optional, Dict, Any
from supabase import Client


class AuthManager:
    """Gerencia autenticação usando Supabase Auth"""
    
    def __init__(self, supabase_client: Client, supabase_admin: Client = None):
        self.client = supabase_client
        self.admin_client = supabase_admin or supabase_client
    
    def register(self, email: str, password: str, is_admin: bool = False) -> Optional[Dict[str, Any]]:
        """
        Registra novo usuário usando Supabase Admin API (bypass restrições)
        is_admin será armazenado no user_metadata
        """
        try:          
            response = self.admin_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,  # Confirmar email automaticamente
                "user_metadata": {
                    "is_admin": is_admin
                }
            })
            
            if response.user:
                print(f"✅ Usuário registrado: {email}")
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "is_admin": response.user.user_metadata.get("is_admin", False)
                }
            else:
                print(f"❌ Erro ao registrar: {email}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao registrar: {e}")
            return None
    
    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Faz login usando Supabase Auth
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                print(f"✅ Login bem-sucedido: {email}")
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "is_admin": response.user.user_metadata.get("is_admin", False),
                    "access_token": response.session.access_token
                }
            else:
                print(f"❌ Credenciais inválidas para: {email}")
                return None
                
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            return None
    
    def logout(self) -> bool:
        """
        Faz logout (invalida sessão no Supabase)
        """
        try:
            self.client.auth.sign_out()
            print("✅ Logout realizado")
            return True
        except Exception as e:
            print(f"❌ Erro no logout: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Retorna o usuário atual da sessão
        """
        try:
            user = self.client.auth.get_user()
            if user:
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "is_admin": user.user.user_metadata.get("is_admin", False)
                }
            return None
        except Exception as e:
            print(f"❌ Erro ao obter usuário: {e}")
            return None


class SessionManager:
    """Gerencia sessão do usuário usando app.storage.user (persiste entre páginas)"""
    
    def __init__(self):
        """Usa app.storage.user que persiste com storage_secret"""
        pass
    
    def login(self, user_data: Dict[str, Any]):
        """
        Armazena dados do usuário após login (persiste entre navegações)
        """
        from nicegui import app
        app.storage.user['user_data'] = user_data
        app.storage.user['is_admin'] = user_data.get("is_admin", False)
        app.storage.user['access_token'] = user_data.get("access_token")
    
    def logout(self):
        """
        Limpa dados da sessão
        """
        from nicegui import app
        app.storage.user.clear()
    
    def is_authenticated(self) -> bool:
        """
        Verifica se há usuário autenticado
        """
        from nicegui import app
        return app.storage.user.get('user_data') is not None
    
    def get_user_email(self) -> str:
        """
        Retorna email do usuário autenticado
        """
        from nicegui import app
        user_data = app.storage.user.get('user_data')
        if user_data:
            return user_data.get("email", "")
        return ""
    
    def get_user_id(self) -> str:
        """
        Retorna ID do usuário autenticado
        """
        from nicegui import app
        user_data = app.storage.user.get('user_data')
        if user_data:
            return user_data.get("id", "")
        return ""
    
    def get_access_token(self) -> Optional[str]:
        """
        Retorna o access token do usuário autenticado
        """
        from nicegui import app
        user_data = app.storage.user.get('user_data')
        if user_data:
            return user_data.get("access_token")
        return None
    
    @property
    def is_admin(self) -> bool:
        """
        Retorna se o usuário é admin
        """
        from nicegui import app
        return app.storage.user.get('is_admin', False)


session = SessionManager()

