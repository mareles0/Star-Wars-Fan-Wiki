from typing import Optional, List, Dict, Any
import httpx
from datetime import datetime
from config import SUPABASE_URL, SUPABASE_ANON_KEY


class FileSystemDB:
    """Gerencia pastas e arquivos da Wiki Star Wars usando Supabase"""
    
    def __init__(self):
        self.base_url = f"{SUPABASE_URL}/rest/v1"
        self.storage_url = f"{SUPABASE_URL}/storage/v1"
        self.anon_key = SUPABASE_ANON_KEY
        print("✅ FileSystem DB inicializado!")
    
    def _get_headers(self, access_token: str = None) -> dict:
        """Retorna headers com token de autenticação"""
        token = access_token or self.anon_key
        return {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    # ==================== OPERAÇÕES DE PASTAS ====================
    
    def create_folder(self, name: str, parent_id: Optional[int] = None, 
                     category: str = "Séries", access_token: str = None,
                     created_by_id: str = None, created_by_email: str = None) -> Optional[Dict[str, Any]]:
        """Cria uma nova pasta
        
        Args:
            name: Nome da pasta
            parent_id: ID da pasta pai (None para raiz)
            category: Categoria raiz (Séries, Filmes, Desenhos)
            access_token: Token de autenticação
            created_by_id: UUID do usuário criador
            created_by_email: Email do usuário criador
        """
        try:
            with httpx.Client() as client:
                payload = {
                    "name": name,
                    "parent_id": parent_id,
                    "category": category,
                    "is_folder": True,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # NÃO adicionar created_by_id no payload
                # O trigger no Supabase vai preencher automaticamente com auth.uid()
                # Isso resolve o problema de permissão RLS!
                
                response = client.post(
                    f"{self.base_url}/filesystem",
                    headers=self._get_headers(access_token),
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                if data:
                    print(f"✅ Pasta criada: {name}")
                    return data[0] if isinstance(data, list) else data
                return None
        except Exception as e:
            print(f"❌ Erro ao criar pasta: {e}")
            return None
    
    def get_folders(self, parent_id: Optional[int] = None, category: str = None,
                   access_token: str = None) -> List[Dict[str, Any]]:
        """Lista pastas de um diretório
        
        Args:
            parent_id: ID da pasta pai (None para raiz)
            category: Filtrar por categoria
            access_token: Token de autenticação
        """
        try:
            with httpx.Client() as client:
                # Construir query
                query = "is_folder=eq.true"
                
                if parent_id is None:
                    query += "&parent_id=is.null"
                else:
                    query += f"&parent_id=eq.{parent_id}"
                
                if category:
                    query += f"&category=eq.{category}"
                
                query += "&order=name.asc"
                
                response = client.get(
                    f"{self.base_url}/filesystem?{query}",
                    headers=self._get_headers(access_token)
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"❌ Erro ao listar pastas: {e}")
            return []
    
    def get_folder_by_id(self, folder_id: int, access_token: str = None) -> Optional[Dict[str, Any]]:
        """Retorna detalhes de uma pasta específica"""
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/filesystem?id=eq.{folder_id}&is_folder=eq.true",
                    headers=self._get_headers(access_token)
                )
                response.raise_for_status()
                data = response.json()
                return data[0] if data else None
        except Exception as e:
            print(f"❌ Erro ao buscar pasta: {e}")
            return None
    
    def rename_folder(self, folder_id: int, new_name: str, 
                     access_token: str = None) -> Optional[Dict[str, Any]]:
        """Renomeia uma pasta"""
        try:
            with httpx.Client() as client:
                response = client.patch(
                    f"{self.base_url}/filesystem?id=eq.{folder_id}",
                    headers=self._get_headers(access_token),
                    json={"name": new_name}
                )
                response.raise_for_status()
                data = response.json()
                if data:
                    print(f"✅ Pasta renomeada: {new_name}")
                    return data[0] if isinstance(data, list) else data
                return None
        except Exception as e:
            print(f"❌ Erro ao renomear pasta: {e}")
            return None
    
    def delete_folder(self, folder_id: int, access_token: str = None) -> bool:
        """Deleta uma pasta e todo seu conteúdo"""
        try:
            with httpx.Client() as client:
                response = client.delete(
                    f"{self.base_url}/filesystem?id=eq.{folder_id}",
                    headers=self._get_headers(access_token)
                )
                response.raise_for_status()
                print(f"✅ Pasta deletada: ID {folder_id}")
                return True
        except Exception as e:
            print(f"❌ Erro ao deletar pasta: {e}")
            return False
    
    def move_folder(self, folder_id: int, new_parent_id: Optional[int],
                   access_token: str = None) -> Optional[Dict[str, Any]]:
        """Move uma pasta para outro diretório"""
        try:
            with httpx.Client() as client:
                response = client.patch(
                    f"{self.base_url}/filesystem?id=eq.{folder_id}",
                    headers=self._get_headers(access_token),
                    json={"parent_id": new_parent_id}
                )
                response.raise_for_status()
                data = response.json()
                if data:
                    print(f"✅ Pasta movida: ID {folder_id}")
                    return data[0] if isinstance(data, list) else data
                return None
        except Exception as e:
            print(f"❌ Erro ao mover pasta: {e}")
            return None
    
    # ==================== OPERAÇÕES DE ARQUIVOS ====================
    
    def upload_file(self, name: str, file_path: str, parent_id: Optional[int] = None,
                   category: str = "Séries", file_size: int = 0, 
                   access_token: str = None, created_by_id: str = None,
                   created_by_email: str = None) -> Optional[Dict[str, Any]]:
        """Registra um arquivo no sistema
        
        Args:
            name: Nome do arquivo
            file_path: Caminho/URL do arquivo no storage
            parent_id: ID da pasta pai
            category: Categoria raiz
            file_size: Tamanho em bytes
            access_token: Token de autenticação
            created_by_id: UUID do usuário criador
            created_by_email: Email do usuário criador
        """
        try:
            with httpx.Client() as client:
                payload = {
                    "name": name,
                    "parent_id": parent_id,
                    "category": category,
                    "is_folder": False,
                    "file_path": file_path,
                    "file_size": file_size,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # NÃO adicionar created_by_id no payload
                # O trigger no Supabase vai preencher automaticamente
                
                response = client.post(
                    f"{self.base_url}/filesystem",
                    headers=self._get_headers(access_token),
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                if data:
                    print(f"✅ Arquivo registrado: {name}")
                    return data[0] if isinstance(data, list) else data
                return None
        except Exception as e:
            print(f"❌ Erro ao registrar arquivo: {e}")
            return None
    
    def get_files(self, parent_id: Optional[int] = None, category: str = None,
                 access_token: str = None) -> List[Dict[str, Any]]:
        """Lista arquivos de um diretório"""
        try:
            with httpx.Client() as client:
                query = "is_folder=eq.false"
                
                if parent_id is None:
                    query += "&parent_id=is.null"
                else:
                    query += f"&parent_id=eq.{parent_id}"
                
                if category:
                    query += f"&category=eq.{category}"
                
                query += "&order=name.asc"
                
                response = client.get(
                    f"{self.base_url}/filesystem?{query}",
                    headers=self._get_headers(access_token)
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"❌ Erro ao listar arquivos: {e}")
            return []
    
    def get_all_items(self, parent_id: Optional[int] = None, category: str = None,
                     access_token: str = None) -> List[Dict[str, Any]]:
        """Lista todos os itens (pastas + arquivos) de um diretório"""
        try:
            with httpx.Client() as client:
                query = ""
                
                if parent_id is None:
                    query += "parent_id=is.null"
                else:
                    query += f"parent_id=eq.{parent_id}"
                
                if category:
                    query += f"&category=eq.{category}"
                
                query += "&order=is_folder.desc,name.asc"
                
                response = client.get(
                    f"{self.base_url}/filesystem?{query}",
                    headers=self._get_headers(access_token)
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"❌ Erro ao listar itens: {e}")
            return []
    
    def delete_file(self, file_id: int, access_token: str = None) -> bool:
        """Deleta um arquivo"""
        try:
            with httpx.Client() as client:
                response = client.delete(
                    f"{self.base_url}/filesystem?id=eq.{file_id}",
                    headers=self._get_headers(access_token)
                )
                response.raise_for_status()
                print(f"✅ Arquivo deletado: ID {file_id}")
                return True
        except Exception as e:
            print(f"❌ Erro ao deletar arquivo: {e}")
            return False
    
    def move_file(self, file_id: int, new_parent_id: Optional[int],
                 access_token: str = None) -> Optional[Dict[str, Any]]:
        """Move um arquivo para outro diretório"""
        try:
            with httpx.Client() as client:
                response = client.patch(
                    f"{self.base_url}/filesystem?id=eq.{file_id}",
                    headers=self._get_headers(access_token),
                    json={"parent_id": new_parent_id}
                )
                response.raise_for_status()
                data = response.json()
                if data:
                    print(f"✅ Arquivo movido: ID {file_id}")
                    return data[0] if isinstance(data, list) else data
                return None
        except Exception as e:
            print(f"❌ Erro ao mover arquivo: {e}")
            return None
    
    def rename_file(self, file_id: int, new_name: str, 
                   access_token: str = None) -> Optional[Dict[str, Any]]:
        """Renomeia um arquivo"""
        try:
            with httpx.Client() as client:
                response = client.patch(
                    f"{self.base_url}/filesystem?id=eq.{file_id}",
                    headers=self._get_headers(access_token),
                    json={"name": new_name}
                )
                response.raise_for_status()
                data = response.json()
                if data:
                    print(f"✅ Arquivo renomeado: {new_name}")
                    return data[0] if isinstance(data, list) else data
                return None
        except Exception as e:
            print(f"❌ Erro ao renomear arquivo: {e}")
            return None
    
    # ==================== INFORMAÇÕES DO DIRETÓRIO ====================
    
    def get_folder_info(self, folder_id: Optional[int] = None, category: str = None,
                       access_token: str = None) -> Dict[str, Any]:
        """Retorna informações sobre um diretório
        
        Returns:
            Dict com: name, total_files, total_folders, total_size
        """
        try:
            # Buscar todos os itens
            items = self.get_all_items(folder_id, category, access_token)
            
            total_files = sum(1 for item in items if not item.get("is_folder", False))
            total_folders = sum(1 for item in items if item.get("is_folder", False))
            total_size = sum(item.get("file_size", 0) for item in items if not item.get("is_folder", False))
            
            # Nome da pasta
            folder_name = "Raiz"
            if folder_id:
                folder = self.get_folder_by_id(folder_id, access_token)
                if folder:
                    folder_name = folder.get("name", "Desconhecida")
            elif category:
                folder_name = category
            
            return {
                "name": folder_name,
                "total_files": total_files,
                "total_folders": total_folders,
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2) if total_size > 0 else 0
            }
        except Exception as e:
            print(f"❌ Erro ao obter informações: {e}")
            return {
                "name": "Erro",
                "total_files": 0,
                "total_folders": 0,
                "total_size": 0,
                "total_size_mb": 0
            }
    
    def search_items(self, search_term: str, category: str = None,
                    access_token: str = None) -> List[Dict[str, Any]]:
        """Busca itens por nome"""
        try:
            with httpx.Client() as client:
                query = f"name=ilike.%{search_term}%"
                
                if category:
                    query += f"&category=eq.{category}"
                
                query += "&order=is_folder.desc,name.asc"
                
                response = client.get(
                    f"{self.base_url}/filesystem?{query}",
                    headers=self._get_headers(access_token)
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"❌ Erro ao buscar: {e}")
            return []


# Instância global
fs_db = FileSystemDB()
