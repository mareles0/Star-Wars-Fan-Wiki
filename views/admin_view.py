from nicegui import ui
from config import COLORS
from auth import session
from supabase_client import supabase

class AdminView:
    def __init__(self):
        """Interface de missões do admin"""
        
        with ui.column().classes('w-full h-screen').style(f'background-color: {COLORS["background"]}'):
            
            # Header
            with ui.header().classes('items-center justify-between px-6').style(f'background-color: {COLORS["secondary"]}'):
                ui.label('ANDOR MISSIONS - ADMIN').classes('text-3xl font-bold').style(f'color: {COLORS["primary"]}')
                
                with ui.row().classes('gap-2'):
                    ui.button('Wiki', on_click=lambda: ui.navigate.to('/wiki'), icon='folder').props('outline')
                    ui.button('Sair', on_click=self.handle_logout, icon='logout').props('outline')
            
            # Conteúdo
            with ui.column().classes('w-full p-6 items-center'):
                ui.label('Todas as Missões').classes('text-4xl font-bold mb-4').style(f'color: {COLORS["primary"]}')
                
                # Botão criar missão
                ui.button('Nova Missão', on_click=self.show_create_dialog, icon='add').style(f'background-color: {COLORS["primary"]}; color: {COLORS["background"]}')
                
                ui.space()
                
                self.missions_container = ui.column().classes('w-full max-w-4xl gap-4')
                
                self.load_missions()
    
    def load_missions(self):
        """Carrega todas as missões"""
        self.missions_container.clear()
        
        try:
            response = supabase.table("missions").select("*").execute()
            
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
    
    def show_create_dialog(self):
        """Dialog para criar missão"""
        with ui.dialog() as dialog, ui.card():
            ui.label('Nova Missão').classes('text-2xl font-bold mb-4')
            
            title_input = ui.input(label='Título').classes('w-full')
            desc_input = ui.textarea(label='Descrição').classes('w-full')
            
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancelar', on_click=dialog.close).props('outline')
                ui.button('Criar', on_click=lambda: self.create_mission(title_input.value, desc_input.value, dialog))
        
        dialog.open()
    
    def create_mission(self, title, description, dialog):
        """Cria nova missão"""
        if not title or not description:
            ui.notify('Preencha todos os campos', type='negative')
            return
        
        try:
            supabase.table("missions").insert({
                "title": title,
                "description": description,
                "status": "pending",
                "user_id": session.user_id
            }).execute()
            
            ui.notify('Missão criada com sucesso!', type='positive')
            dialog.close()
            self.load_missions()
        except Exception as e:
            print(f"Erro ao criar missão: {e}")
            ui.notify('Erro ao criar missão', type='negative')
    
    def handle_logout(self):
        """Faz logout"""
        session.logout()
        ui.navigate.to('/login')
