from nicegui import ui
from config import COLORS
from auth import session
from supabase_client import supabase

class UserView:
    def __init__(self):
        """Interface de missões do usuário"""
        
        with ui.column().classes('w-full h-screen').style(f'background-color: {COLORS["background"]}'):
            
            # Header
            with ui.header().classes('items-center justify-between px-6').style(f'background-color: {COLORS["secondary"]}'):
                ui.label('ANDOR MISSIONS').classes('text-3xl font-bold').style(f'color: {COLORS["primary"]}')
                
                with ui.row().classes('gap-2'):
                    ui.button('Wiki', on_click=lambda: ui.navigate.to('/wiki'), icon='folder').props('outline')
                    ui.button('Sair', on_click=self.handle_logout, icon='logout').props('outline')
            
            # Conteúdo
            with ui.column().classes('w-full p-6 items-center'):
                ui.label('Suas Missões').classes('text-4xl font-bold mb-4').style(f'color: {COLORS["primary"]}')
                
                self.missions_container = ui.column().classes('w-full max-w-4xl gap-4')
                
                self.load_missions()
    
    def load_missions(self):
        """Carrega missões do usuário"""
        self.missions_container.clear()
        
        try:
            response = supabase.table("missions").select("*").eq("user_id", session.user_id).execute()
            
            if response.data:
                for mission in response.data:
                    with self.missions_container:
                        with ui.card().classes('w-full p-4').style(f'background-color: {COLORS["secondary"]}'):
                            ui.label(mission['title']).classes('text-xl font-bold').style(f'color: {COLORS["primary"]}')
                            ui.label(mission['description']).style(f'color: {COLORS["text"]}')
                            ui.label(f"Status: {mission['status']}").classes('text-sm opacity-70')
            else:
                with self.missions_container:
                    ui.label('Nenhuma missão encontrada').classes('opacity-70')
        
        except Exception as e:
            print(f"Erro ao carregar missões: {e}")
            with self.missions_container:
                ui.label('Erro ao carregar missões').classes('text-red')
    
    def handle_logout(self):
        """Faz logout"""
        session.logout()
        ui.navigate.to('/login')
