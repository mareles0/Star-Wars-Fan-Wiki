import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

COLORS = {
    "primary": "#292949",
    "secondary": "#101931",
    "accent": "#ff4c05",  # Laranja estilo Rebellion
    "text": "#eaeaea",
    "success": "#4caf50",
    "warning": "#ff9800",
    "background": "#000000",
    "folder": "#FFD700",  # Dourado para pastas
    "file": "#87CEEB",    # Azul claro para arquivos
}

# Categorias Star Wars
CATEGORIES = ["Séries", "Filmes", "Desenhos"]
