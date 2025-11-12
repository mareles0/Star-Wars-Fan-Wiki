from nicegui import ui
from config import COLORS
from auth import session
from supabase_client import supabase

class LoginView:
    def __init__(self):
        """Cria a interface de login"""
        
        # Container principal com fundo escuro
        with ui.column().classes('w-full h-screen items-center justify-center px-4').style(f'background-color: {COLORS["background"]}'):
            
            # Espaço superior
            ui.space()
            
            # Título
            ui.label('STAR WARS FAN WIKI').classes('text-3xl sm:text-5xl md:text-6xl font-bold text-center').style('color: #FFFFFF')
            ui.label('Sistema de Arquivos sobre Star Wars').classes('text-sm sm:text-base md:text-lg opacity-70 text-center').style('color: #FFFFFF')
            
            ui.space()
            
            # Card de login
            with ui.card().classes('w-full sm:w-96 p-6 sm:p-8').style(f'background-color: {COLORS["secondary"]}'):
                ui.label('Acessar Sistema').classes('text-xl sm:text-2xl font-bold mb-4').style('color: #FFFFFF')
                
                # Campos de entrada
                self.email_input = ui.input(
                    label='Email',
                    placeholder='seu@email.com'
                ).classes('w-full').props('outlined dark dense')
                
                self.password_input = ui.input(
                    label='Senha',
                    placeholder='••••••••',
                    password=True,
                    password_toggle_button=True
                ).classes('w-full').props('outlined dark dense').on('keydown.enter', lambda: self.handle_login())
                
                ui.space()
                
                # Botão de login (fundo amarelo com texto preto)
                ui.button(
                    'Entrar',
                    on_click=self.handle_login,
                    icon='login'
                ).classes('w-full').style('background-color: #FFD700 !important; color: #000000 !important; font-weight: bold; font-size: 14px; padding: 10px;').props('unelevated')
                
                ui.space()
                
                # Link para registro
                with ui.row().classes('w-full justify-center gap-2 flex-wrap'):
                    ui.label('Não tem conta?').classes('opacity-70 text-sm sm:text-base').style(f'color: {COLORS["text"]}')
                    ui.link('Registrar', '/register').classes('no-underline text-sm sm:text-base').style('color: #FFD700')
            
            ui.space()
            
            # Citação
            ui.label('"As rebeliões são construídas na esperança."').classes('text-xs sm:text-sm italic opacity-50 text-center px-4').style(f'color: {COLORS["text"]}')
            
            ui.space()
    
    def handle_login(self):
        """Processa o login"""
        email = self.email_input.value
        password = self.password_input.value
        
        if not email or not password:
            ui.notify('Preencha todos os campos', type='negative', position='top')
            return
        
        try:
            print(f"🔐 Tentando login: {email}")
            
            # Autenticar usando Supabase (chamada síncrona)
            response = supabase.auth.sign_in_with_password(
                credentials={"email": email, "password": password}
            )
            
            print(f"📦 Resposta recebida: {response}")
            
            if response and response.user:
                # Preparar dados da sessão
                user_data = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "is_admin": response.user.user_metadata.get("is_admin", False) if response.user.user_metadata else False,
                    "access_token": response.session.access_token if response.session else None
                }
                
                print(f"✅ Login OK: {user_data}")
                
                # Salvar sessão
                session.login(user_data)
                
                # Notificar sucesso
                ui.notify(f'✅ Bem-vindo, {email}!', type='positive', position='top')
                
                # Redirecionar
                ui.navigate.to('/wiki')
            else:
                print(f"❌ Resposta sem usuário")
                ui.notify('❌ Email ou senha incorretos', type='negative', position='top')
        except Exception as e:
            print(f"❌ Erro no login: {str(e)}")
            ui.notify(f'❌ Erro: {str(e)}', type='negative', position='top')
