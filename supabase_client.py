from supabase import create_client
from config import SUPABASE_URL, SUPABASE_ANON_KEY

# Cliente Supabase para operações gerais
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
