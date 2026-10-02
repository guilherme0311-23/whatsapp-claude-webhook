from supabase import create_client
from app.core.config import SUPABASE_URL, SUPABASE_SECRET_KEY

client = create_client(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_SECRET_KEY)

def obter_sessao_id(telefone: str) -> int:
    resultado = client.table("sessoes").select("id").eq("remote_jid", telefone).execute()

    if resultado.data:
        sessao_id = resultado.data[0]["id"]
    else:
        resultado_novo = client.table("sessoes").insert({"remote_jid": telefone}).execute()

        sessao_id = resultado_novo.data[0]["id"]

    return sessao_id

def salvar_mensagem(sessao_id: int, role: str, conteudo: str):
    client.table("mensagens").insert({
        "sessao_id": sessao_id,
        "role": role,
        "conteudo": conteudo
    }).execute()
