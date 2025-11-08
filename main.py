from nicegui import app, ui
from config import COLORS
from auth import session
from views.login_view import LoginView
from views.register_view import RegisterView
from views.filesystem_view import FileSystemView
from views.user_view import UserView
from views.admin_view import AdminView

def setup_theme():
    """Configurar tema Star Wars"""
    ui.dark_mode().enable()
    ui.colors(
        primary="#FFFFFF",  # Branco
        secondary='#000000',  # Preto
        accent="#FF3300",
        dark='#000000',
        positive='#21BA45',
        negative='#C10015',
        info='#31CCEC',
        warning='#F2C037'
    )

@ui.page('/')
def index():
    """Página inicial - redireciona para login ou wiki"""
    setup_theme()
    if session.is_authenticated():
        return ui.navigate.to('/wiki')
    else:
        return ui.navigate.to('/login')

@ui.page('/login')
def login_page():
    """Página de login"""
    setup_theme()
    LoginView()

@ui.page('/register')
def register_page():
    """Página de registro"""
    setup_theme()
    RegisterView()

@ui.page('/wiki')
def wiki_page():
    """Página principal - Sistema de arquivos"""
    setup_theme()
    if not session.is_authenticated():
        ui.navigate.to('/login')
        return
    
    FileSystemView(is_admin=session.is_admin)

@ui.page('/missions')
def missions_user_page():
    """Página de missões (usuário)"""
    setup_theme()
    if not session.is_authenticated():
        ui.navigate.to('/login')
        return
    
    UserView()

@ui.page('/missions-admin')
def missions_admin_page():
    """Página de missões (admin)"""
    setup_theme()
    if not session.is_authenticated():
        ui.navigate.to('/login')
        return
    
    if not session.is_admin:
        ui.navigate.to('/wiki')
        return
    
    AdminView()

# Iniciar aplicação
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host='0.0.0.0',
        port=8550,
        title='Star Wars Fan Wiki',
        dark=True,
        reload=False,
        show=False
    )
