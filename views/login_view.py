from nicegui import ui
from config import COLORS
from auth import session
from supabase_client import auth_manager

class LoginView:
    def __init__(self):
        """Cria a interface de login"""
        
        # Container principal com fundo escuro
        with ui.column().classes('w-full h-screen items-center justify-center').style(f'background-color: {COLORS["background"]}'):
            
            # Espaço superior
            ui.space()
            
            # Título
            ui.label('STAR WARS FAN WIKI').classes('text-6xl font-bold').style('color: #FFFFFF')
            ui.label('Sistema de Arquivos sobre Star Wars').classes('text-lg opacity-70').style('color: #FFFFFF')
            
            ui.space()
            
            # Card de login
            with ui.card().classes('w-96 p-8').style(f'background-color: {COLORS["secondary"]}'):
                ui.label('Acessar Sistema').classes('text-2xl font-bold mb-4').style('color: #FFFFFF')
                
                # Campos de entrada
                self.email_input = ui.input(
                    label='Email',
                    placeholder='seu@email.com'
                ).classes('w-full').props('outlined dark')
                
                self.password_input = ui.input(
                    label='Senha',
                    placeholder='••••••••',
                    password=True,
                    password_toggle_button=True
                ).classes('w-full').props('outlined dark').on('keydown.enter', lambda: self.handle_login())
                
                ui.space()
                
                # Botão de login (fundo amarelo com texto preto)
                ui.button(
                    'Entrar',
                    on_click=self.handle_login,
                    icon='login'
                ).classes('w-full').style('background-color: #FFD700 !important; color: #000000 !important; font-weight: bold; font-size: 16px;').props('unelevated')
                
                ui.space()
                
                # Link para registro
                with ui.row().classes('w-full justify-center gap-2'):
                    ui.label('Não tem conta?').classes('opacity-70').style(f'color: {COLORS["text"]}')
                    ui.link('Registrar', '/register').classes('no-underline').style('color: #FFD700')
            
            ui.space()
            
            # Citação
            ui.label('"As rebeliões são construídas na esperança."').classes('text-sm italic opacity-50').style(f'color: {COLORS["text"]}')
            
            ui.space()
    
    def handle_login(self):
        """Processa o login"""
        email = self.email_input.value
        password = self.password_input.value
        
        if not email or not password:
            ui.notify('Preencha todos os campos', type='negative', position='top')
            return
        
        # Autenticar
        result = auth_manager.login(email, password)
        
        if result:
            # Salvar sessão
            session.login(result)
            
            # Notificar sucesso
            ui.notify(f'✅ Bem-vindo, {email}!', type='positive', position='top')
            
            # Redirecionar
            ui.navigate.to('/wiki')
        else:
            ui.notify('❌ Email ou senha incorretos', type='negative', position='top')
