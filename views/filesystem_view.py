from nicegui import ui, events
from config import COLORS, CATEGORIES, SUPABASE_URL, SUPABASE_ANON_KEY
from filesystem_db import fs_db
from auth import session
from supabase_client import supabase
import uuid
import httpx

class FileSystemView:
    def __init__(self, is_admin: bool = False):
        """Cria a interface do sistema de arquivos"""
        
        self.is_admin = is_admin
        self.current_folder_id = None
        self.current_category = "Séries"
        self.breadcrumb = []
        
        # Header (deve ser top-level, não dentro de column)
        with ui.header().classes('items-center justify-between px-6').style(f'background-color: {COLORS["secondary"]}'):
            with ui.column().classes('gap-0'):
                ui.label('STAR WARS WIKI' + (' - ADMIN' if is_admin else '')).classes('text-3xl font-bold').style('color: #FFFFFF')
                ui.label('Sistema de Arquivos Galáctico').classes('text-sm opacity-70').style('color: #FFFFFF')
            
            with ui.row().classes('gap-2'):
                ui.icon('admin_panel_settings' if is_admin else 'person').classes('text-2xl').style(f'color: {COLORS["accent"]}')
                ui.button('Sair', on_click=self.handle_logout, icon='logout').props('outline color=white')
        
        # Container de conteúdo
        with ui.column().classes('w-full flex-grow p-0').style(f'background-color: {COLORS["background"]}'):
            # Tabs de categorias
            with ui.tabs().classes('w-full').props('align=left inline-label').style('background-color: rgba(0,0,0,0.3)') as tabs:
                tab_series = ui.tab('Séries', icon='tv').style('min-width: 150px')
                tab_filmes = ui.tab('Filmes', icon='movie').style('min-width: 150px')
                tab_desenhos = ui.tab('Desenhos', icon='brush').style('min-width: 150px')
            
            # Tab Panels - cada um corresponde a uma categoria
            with ui.tab_panels(tabs, value='Séries').classes('w-full flex-grow'):
                # Panel Séries
                with ui.tab_panel('Séries').classes('p-6'):
                    self.create_category_panel('Séries')
                
                # Panel Filmes
                with ui.tab_panel('Filmes').classes('p-6'):
                    self.create_category_panel('Filmes')
                
                # Panel Desenhos
                with ui.tab_panel('Desenhos').classes('p-6'):
                    self.create_category_panel('Desenhos')
    
    def create_category_panel(self, category):
        """Cria o conteúdo de um painel de categoria"""
        # Armazenar categoria atual
        self.current_category = category
        self.current_folder_id = None
        self.breadcrumb = []
        
        # Breadcrumb
        breadcrumb_container = ui.row().classes('gap-2 items-center')
        
        # Barra de ações
        with ui.row().classes('w-full gap-2 items-center'):
            search_input = ui.input(placeholder='Buscar...').classes('flex-grow').props('outlined dense')
            
            ui.button('Atualizar', on_click=lambda: self.load_items_for_panel(category), icon='refresh').props('color=blue').classes('text-white font-bold')
            
            # Verificar permissões
            can_create = self.is_admin or category == "Desenhos"
            
            if can_create:
                ui.button('Nova Pasta', on_click=lambda: self.show_create_folder_dialog_for_panel(category), icon='create_new_folder').props('color=green').classes('text-white font-bold')
                ui.button('Upload', on_click=lambda: self.show_upload_dialog_for_panel(category), icon='upload_file').props('color=orange').classes('text-white font-bold')
        
        # Info do diretório
        folder_info = ui.label('').classes('text-sm opacity-70').style(f'color: {COLORS["text"]}')
        
        # Grid de itens
        items_grid = ui.grid(columns=4).classes('w-full gap-4')
        
        # Armazenar referências por categoria
        if not hasattr(self, 'panels'):
            self.panels = {}
        
        self.panels[category] = {
            'breadcrumb': breadcrumb_container,
            'search_input': search_input,
            'folder_info': folder_info,
            'items_grid': items_grid,
            'current_folder_id': None,
            'breadcrumb_path': []
        }
        
        # Carregar itens iniciais
        self.load_items_for_panel(category)
    
    def load_items_for_panel(self, category):
        """Carrega itens para um painel específico"""
        panel = self.panels.get(category)
        if not panel:
            return
        
        try:
            items = fs_db.get_all_items(
                category=category,
                parent_id=panel['current_folder_id'],
                access_token=session.get_access_token()
            )
            
            panel['items_grid'].clear()
            
            if items:
                panel['folder_info'].text = f'{len(items)} itens'
                
                for item in items:
                    self.create_item_card_for_panel(item, category)
            else:
                panel['folder_info'].text = 'Pasta vazia'
        except Exception as e:
            ui.notify(f'❌ Erro ao carregar: {e}', type='negative')
            print(f"Erro ao carregar itens: {e}")
    
    def create_item_card_for_panel(self, item, category):
        """Cria um card de item para um painel específico"""
        panel = self.panels.get(category)
        if not panel:
            return
        
        # Verificar se o criador é admin (através do email ou role)
        creator_email = item.get('created_by_email', '')
        # Assumir que criadores com is_admin=true no user_data ou emails específicos são admins
        # Por enquanto, vamos verificar se o email existe na nossa lista de admins
        is_admin_item = creator_email in ['admin@starwars.com', 'lucas@email.com']  # Adicione emails de admin aqui
        
        # Adicionar flag ao item
        item['is_admin'] = is_admin_item
        
        with panel['items_grid']:
            with ui.card().classes('p-4 cursor-pointer hover:shadow-lg').style('background-color: rgba(255,255,255,0.05); min-width: 200px; max-width: 300px;'):
                # Verificar permissões
                current_user_id = session.get_user_id()
                created_by_id = item.get('created_by_id')
                is_owner = created_by_id == current_user_id
                is_admin_item = item.get('is_admin', False)  # Flag para identificar se foi criado por admin
                can_edit = self.is_admin or is_owner
                
                # Ícone com badge de admin se necessário
                with ui.row().classes('items-center gap-2'):
                    if item.get('is_folder', False):
                        ui.icon('folder', size='3rem').style('color: #FF6B35')
                    else:
                        ui.icon('insert_drive_file', size='3rem').style('color: #4A90E2')
                    
                    # Badge de admin
                    if is_admin_item:
                        ui.icon('admin_panel_settings').classes('text-xl').style('color: #FFD700')
                
                # Nome com quebra de linha e overflow
                ui.label(item['name']).classes('text-lg font-bold mt-2').style('color: #FFFFFF; word-break: break-all; overflow-wrap: break-word; max-width: 100%;')
                
                # Metadados - mostrar criador
                creator_email = item.get('created_by_email', '')
                creator_name = creator_email.split('@')[0] if creator_email else 'Desconhecido'
                
                with ui.row().classes('items-center gap-1'):
                    if is_admin_item:
                        ui.icon('admin_panel_settings').classes('text-xs').style('color: #FFD700')
                    ui.label(f"por {creator_name}").classes('text-xs opacity-70').style('color: #FFFFFF')
                
                # Botões de ação (só aparecem se tiver permissão)
                with ui.row().classes('gap-2 mt-2'):
                    if item.get('is_folder', False):
                        ui.button(icon='folder_open', on_click=lambda i=item: self.open_folder_in_panel(i, category)).props('flat dense').style('color: #FFFFFF')
                    else:
                        # Botão de download para arquivos
                        ui.button(icon='download', on_click=lambda i=item: self.download_file(i)).props('flat dense').style('color: #4CAF50')
                    
                    # Botões de editar/deletar só aparecem se tiver permissão
                    if can_edit:
                        ui.button(icon='edit', on_click=lambda i=item: self.show_rename_dialog(i)).props('flat dense').style('color: #FFFFFF')
                        ui.button(icon='delete', on_click=lambda i=item: self.show_delete_dialog(i)).props('flat dense').style('color: #FF0000')
    
    def open_folder_in_panel(self, folder, category):
        """Abre uma pasta em um painel específico"""
        panel = self.panels.get(category)
        if not panel:
            return
        
        panel['current_folder_id'] = folder['id']
        panel['breadcrumb_path'].append(folder)
        self.update_breadcrumb_for_panel(category)
        self.load_items_for_panel(category)
    
    def update_breadcrumb_for_panel(self, category):
        """Atualiza o breadcrumb de um painel específico"""
        panel = self.panels.get(category)
        if not panel:
            return
        
        panel['breadcrumb'].clear()
        
        with panel['breadcrumb']:
            # Home
            ui.button(
                icon='home',
                on_click=lambda: self.navigate_to_root_in_panel(category)
            ).props('flat dense').style('color: #FFD700')
            
            # Path
            for i, folder in enumerate(panel['breadcrumb_path']):
                ui.label('/').classes('mx-1').style('color: #666')
                ui.button(
                    folder['name'],
                    on_click=lambda idx=i: self.navigate_to_index_in_panel(idx, category)
                ).props('flat dense').style('color: #FFD700')
    
    def navigate_to_root_in_panel(self, category):
        """Navega para a raiz em um painel específico"""
        panel = self.panels.get(category)
        if not panel:
            return
        
        panel['current_folder_id'] = None
        panel['breadcrumb_path'] = []
        self.update_breadcrumb_for_panel(category)
        self.load_items_for_panel(category)
    
    def navigate_to_index_in_panel(self, index, category):
        """Navega para um índice específico no breadcrumb"""
        panel = self.panels.get(category)
        if not panel:
            return
        
        panel['breadcrumb_path'] = panel['breadcrumb_path'][:index+1]
        panel['current_folder_id'] = panel['breadcrumb_path'][-1]['id'] if panel['breadcrumb_path'] else None
        self.update_breadcrumb_for_panel(category)
        self.load_items_for_panel(category)
    
    def show_create_folder_dialog_for_panel(self, category):
        """Dialog para criar pasta em um painel específico"""
        with ui.dialog() as dialog, ui.card().classes('p-6'):
            ui.label('Nova Pasta').classes('text-2xl font-bold mb-4')
            
            # Auto-preencher nome para usuários na categoria Desenhos
            default_name = ''
            if not self.is_admin and category == "Desenhos":
                user_email = session.get_user_email()
                default_name = user_email.split('@')[0] if user_email else ''
            
            name_input = ui.input(label='Nome da pasta', value=default_name).classes('w-full').props('outlined')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancelar', on_click=dialog.close).props('flat').classes('text-grey')
                ui.button(
                    'Criar',
                    on_click=lambda: self.create_folder_for_panel(name_input.value, category, dialog)
                ).props('').classes('bg-blue text-white font-bold')
        
        dialog.open()
    
    def create_folder_for_panel(self, name, category, dialog):
        """Cria uma pasta em um painel específico"""
        if not name or not name.strip():
            ui.notify('❌ Nome inválido', type='negative')
            return
        
        panel = self.panels.get(category)
        if not panel:
            return
        
        try:
            result = fs_db.create_folder(
                name=name,
                category=category,
                parent_id=panel['current_folder_id'],
                access_token=session.get_access_token()
            )
            
            if result:
                ui.notify(f'✅ Pasta "{name}" criada!', type='positive')
                dialog.close()
                self.load_items_for_panel(category)
            else:
                ui.notify('❌ Erro ao criar pasta', type='negative')
        except Exception as e:
            ui.notify(f'❌ Erro: {e}', type='negative')
    
    def show_upload_dialog_for_panel(self, category):
        """Dialog para upload em um painel específico"""
        panel = self.panels.get(category)
        if not panel:
            return
        
        with ui.dialog() as dialog, ui.card().classes('p-6 min-w-96'):
            ui.label('Upload de Arquivo').classes('text-2xl font-bold mb-4')
            
            async def handle_upload(e: events.UploadEventArguments):
                try:
                    # Acessar o arquivo via e.file (que é um objeto UploadFile)
                    upload_file = e.file
                    
                    # Ler o conteúdo do arquivo (async)
                    file_content = await upload_file.read()
                    file_name = upload_file.name
                    file_size = len(file_content)
                    
                    print(f"DEBUG: Arquivo {file_name}, tamanho {file_size} bytes")
                    
                    # Normalizar categoria para path sem acentos
                    category_path = category.replace('é', 'e').replace('ã', 'a')  # Séries -> Series, Desenhos -> Desenhos
                    
                    # Gerar nome único para o arquivo
                    file_extension = file_name.split('.')[-1] if '.' in file_name else 'bin'
                    unique_name = f"{uuid.uuid4()}.{file_extension}"
                    storage_path = f"{category_path}/{unique_name}"
                    
                    print(f"DEBUG: Storage path = {storage_path}")
                    
                    # Upload para Supabase Storage usando o token do usuário
                    url = f"{SUPABASE_URL}/storage/v1/object/starwars-files/{storage_path}"
                    
                    # Pegar o token do usuário
                    user_token = session.get_access_token()
                    if not user_token:
                        ui.notify('❌ Token de autenticação não encontrado', type='negative')
                        print("ERRO: Token não disponível")
                        return
                    
                    headers = {
                        "Authorization": f"Bearer {user_token}",
                        "Content-Type": "application/octet-stream",
                    }
                    
                    print(f"DEBUG: Token = {user_token[:20]}...")
                    
                    response = httpx.post(url, content=file_content, headers=headers, timeout=30.0)
                    
                    if response.status_code not in [200, 201]:
                        ui.notify(f'❌ Erro no upload para storage: {response.status_code}', type='negative')
                        print(f"Erro storage: {response.text}")
                        return
                    
                    print(f"✅ Upload para storage OK")
                    
                    # Registrar no banco de dados
                    result = fs_db.upload_file(
                        name=file_name,
                        file_path=storage_path,
                        category=category,
                        parent_id=panel['current_folder_id'],
                        file_size=file_size,
                        access_token=session.get_access_token()
                    )
                    
                    if result:
                        ui.notify(f'✅ Arquivo "{file_name}" enviado!', type='positive')
                        dialog.close()
                        self.load_items_for_panel(category)
                    else:
                        ui.notify('❌ Erro ao registrar no banco', type='negative')
                        
                except Exception as ex:
                    ui.notify(f'❌ Erro: {ex}', type='negative')
                    print(f"Erro no upload: {ex}")
                    import traceback
                    traceback.print_exc()
            
            # O UPLOAD FINALMENTE FUNCIONA EM NICEGUI!
            ui.upload(
                on_upload=handle_upload,
                auto_upload=True
            ).classes('w-full').props('color=orange')
            
            ui.button('Fechar', on_click=dialog.close).classes('mt-4').props('flat').classes('text-grey')
        
        dialog.open()
    
    # MÉTODOS ANTIGOS - MANTER PARA COMPATIBILIDADE
    def render_content(self):
        """DEPRECATED - Agora usa create_category_panel"""
        pass
    
    def change_category(self, e):
        """Muda a categoria ativa"""
        # e.args contém o nome da tab clicada
        new_category = e.args
        print(f"DEBUG: Tab clicada = {new_category}, categoria atual = {self.current_category}")
        
        # Só atualiza se realmente mudou
        if new_category != self.current_category:
            self.current_category = new_category
            self.current_folder_id = None
            self.breadcrumb = []
            
            print(f"DEBUG: Mudando para categoria {new_category}")
            # Renderizar novo conteúdo
            self.render_content()
        else:
            print(f"DEBUG: Já está na categoria {new_category}")
    
    def create_category_content(self):
        """DEPRECATED - use create_category_panel()"""
        pass
    
    def change_category(self, e):
        """DEPRECATED - Tabs agora funcionam automaticamente com tab_panels"""
        pass
    
    def show_rename_dialog(self, item):
        """Dialog para renomear item"""
        with ui.dialog() as dialog, ui.card().classes('p-6'):
            ui.label('Renomear').classes('text-2xl font-bold mb-4')
            
            name_input = ui.input(label='Novo nome', value=item['name']).classes('w-full').props('outlined')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancelar', on_click=dialog.close).props('outline color=grey')
                ui.button('Salvar', on_click=lambda: self.rename_item(item, name_input.value, dialog)).props('color=orange')
        
        dialog.open()
    
    def rename_item(self, item, new_name, dialog):
        """Renomeia um item"""
        if not new_name:
            ui.notify('Digite um novo nome', type='negative')
            return
        
        try:
            # Usar método específico baseado no tipo
            if item.get('is_folder', False):
                result = fs_db.rename_folder(item['id'], new_name, access_token=session.get_access_token())
            else:
                result = fs_db.rename_file(item['id'], new_name, access_token=session.get_access_token())
            
            if result:
                ui.notify(f'✅ Renomeado para "{new_name}"', type='positive')
                dialog.close()
                # Recarregar todos os painéis
                for category in self.panels.keys():
                    self.load_items_for_panel(category)
            else:
                ui.notify('❌ Erro ao renomear', type='negative')
        except Exception as e:
            print(f"Erro ao renomear: {e}")
            ui.notify(f'❌ Erro: {e}', type='negative')
    
    def show_delete_dialog(self, item):
        """Dialog para confirmar exclusão"""
        with ui.dialog() as dialog, ui.card().classes('p-6'):
            ui.label('Confirmar Exclusão').classes('text-2xl font-bold mb-4 text-red')
            ui.label(f'Tem certeza que deseja excluir "{item["name"]}"?').classes('mb-4')
            
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancelar', on_click=dialog.close).props('outline color=grey')
                ui.button(
                    'Excluir',
                    on_click=lambda: self.delete_item(item, dialog)
                ).props('color=red')
        
        dialog.open()
    
    def delete_item(self, item, dialog):
        """Deleta um item"""
        try:
            # Usar método específico baseado no tipo
            if item.get('is_folder', False):
                result = fs_db.delete_folder(item['id'], access_token=session.get_access_token())
            else:
                result = fs_db.delete_file(item['id'], access_token=session.get_access_token())
            
            if result:
                ui.notify('✅ Item excluído', type='positive')
                dialog.close()
                # Recarregar todos os painéis
                for category in self.panels.keys():
                    self.load_items_for_panel(category)
            else:
                ui.notify('❌ Erro ao excluir', type='negative')
        except Exception as e:
            print(f"Erro ao excluir: {e}")
            ui.notify(f'❌ Erro: {e}', type='negative')
    
    def format_size(self, bytes_size):
        """Formata tamanho de arquivo"""
        if bytes_size == 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB"]
        i = 0
        size = float(bytes_size)
        while size >= 1024 and i < len(units) - 1:
            size /= 1024
            i += 1
        return f"{size:.2f} {units[i]}"
    
    def download_file(self, item):
        """Faz download de um arquivo"""
        try:
            file_path = item.get('file_path')
            file_name = item.get('name')
            
            if not file_path:
                ui.notify('❌ Caminho do arquivo não encontrado', type='negative')
                return
            
            # Tentar primeiro como público
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/starwars-files/{file_path}"
            
            # Testar se é público
            response = httpx.head(public_url, timeout=5.0)
            
            if response.status_code == 200:
                # Arquivo é público
                ui.download(public_url, filename=file_name)
                ui.notify(f'⬇️ Baixando {file_name}...', type='positive')
            else:
                # Arquivo é privado, baixar com autenticação
                authenticated_url = f"{SUPABASE_URL}/storage/v1/object/authenticated/starwars-files/{file_path}"
                
                # Baixar o conteúdo com token
                headers = {
                    "Authorization": f"Bearer {session.get_access_token()}"
                }
                
                file_response = httpx.get(authenticated_url, headers=headers, timeout=30.0)
                
                if file_response.status_code == 200:
                    # Criar um data URL temporário para download
                    import base64
                    file_content = file_response.content
                    file_base64 = base64.b64encode(file_content).decode()
                    
                    # Detectar tipo MIME
                    extension = file_name.split('.')[-1].lower()
                    mime_types = {
                        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
                        'gif': 'image/gif', 'pdf': 'application/pdf', 'txt': 'text/plain',
                        'zip': 'application/zip'
                    }
                    mime_type = mime_types.get(extension, 'application/octet-stream')
                    
                    data_url = f"data:{mime_type};base64,{file_base64}"
                    ui.download(data_url, filename=file_name)
                    ui.notify(f'⬇️ Baixando {file_name}...', type='positive')
                else:
                    ui.notify(f'❌ Erro ao baixar: {file_response.status_code}', type='negative')
            
        except Exception as e:
            print(f"Erro no download: {e}")
            import traceback
            traceback.print_exc()
            ui.notify(f'❌ Erro ao baixar: {e}', type='negative')
    
    def handle_logout(self):
        """Faz logout"""
        session.logout()
        ui.navigate.to('/login')
