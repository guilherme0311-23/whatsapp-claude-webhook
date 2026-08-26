from fastapi import FastAPI, HTTPException, BackgroundTasks
import anthropic
from app.models import PerguntaRequest, WebhookPayload
from app.services.claude_service import perguntar_claude

app = FastAPI()

def processar_mensagem(payload: WebhookPayload):
    texto = payload.data.message.conversation
    resposta = perguntar_claude(texto)
    print(f"Resposta gerada: {resposta}")

@app.post("/chat")
def chat(dados: PerguntaRequest):
    try:
        resposta = perguntar_claude(dados.pergunta)
        return {"resposta": resposta}

    except anthropic.AuthenticationError:
        raise HTTPException(status_code=401, detail="Chave de API inválida ou expirada")

    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="Muitas requisicões. Tente novamente em instantes")

    except anthropic.APITimeoutError:
        raise HTTPException(status_code=504, detail="A API demorou demais para responder")

    except anthropic.APIError:
        raise HTTPException(status_code=502, detail="Erro ao se comunicar com o serviço de IA")

@app.post("/webhook")
def webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(processar_mensagem, payload)
    return {"status": "recebido"}
