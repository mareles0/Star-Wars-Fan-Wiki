from nicegui import ui
from config import COLORS
from supabase_client import supabase

class RegisterView:
    def __init__(self):
        """Cria a interface de registro"""
        
        # Container principal com fundo escuro
        with ui.column().classes('w-full h-screen items-center justify-center px-4').style(f'background-color: {COLORS["background"]}'):
            
            # Espaço superior
            ui.space()
            
            # Título
            ui.label('NOVO AGENTE').classes('text-3xl sm:text-5xl md:text-6xl font-bold text-center').style('color: #FFFFFF')
            ui.label('Junte-se à Rebelião').classes('text-sm sm:text-base md:text-lg opacity-70 text-center').style('color: #FFFFFF')
            
            ui.space()
            
            # Card de registro
            with ui.card().classes('w-full sm:w-96 p-6 sm:p-8').style(f'background-color: {COLORS["secondary"]}'):
                ui.label('Criar Conta').classes('text-xl sm:text-2xl font-bold mb-4').style('color: #FFFFFF')
                
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
                ).classes('w-full').props('outlined dark dense')
                
                self.password_confirm_input = ui.input(
                    label='Confirmar Senha',
                    placeholder='••••••••',
                    password=True,
                    password_toggle_button=True
                ).classes('w-full').props('outlined dark dense').on('keydown.enter', lambda: self.handle_register())
                
                ui.space()
                
                # Botão de registro (amarelo com texto preto)
                ui.button(
                    'Registrar',
                    on_click=self.handle_register,
                    icon='person_add'
                ).classes('w-full').style('background-color: #FFD700 !important; color: #000000 !important; font-weight: bold; font-size: 14px; padding: 10px;').props('unelevated')
            
            ui.space()
            
            # Citação
            ui.label('"A esperança é como o sol. Você acredita nela apenas quando pode vê-la..."').classes('text-xs sm:text-sm italic opacity-50 text-center px-4').style(f'color: {COLORS["text"]}')
            
            ui.space()
    
    def handle_register(self):
        """Processa o registro"""
        email = self.email_input.value
        password = self.password_input.value
        password_confirm = self.password_confirm_input.value
        
        if not email or not password or not password_confirm:
            ui.notify('Preencha todos os campos', type='negative', position='top')
            return
        
        if password != password_confirm:
            ui.notify('As senhas não coincidem', type='negative', position='top')
            return
        
        if len(password) < 6:
            ui.notify('A senha deve ter no mínimo 6 caracteres', type='negative', position='top')
            return
        
        try:
            print(f"📝 Tentando registrar: {email}")
            
            # Registrar usando Supabase (chamada síncrona)
            response = supabase.auth.sign_up(
                credentials={"email": email, "password": password}
            )
            
            print(f"📦 Resposta recebida: {response}")
            
            if response and response.user:
                print(f"✅ Registro OK")
                ui.notify('✅ Conta criada com sucesso! Faça login.', type='positive', position='top')
                ui.navigate.to('/login')
            else:
                print(f"❌ Resposta sem usuário")
                ui.notify('❌ Erro ao criar conta', type='negative', position='top')
        except Exception as e:
            print(f"❌ Erro no registro: {str(e)}")
            ui.notify(f'❌ Erro: {str(e)}', type='negative', position='top')
