from fastapi import FastAPI, HTTPException
import anthropic
from app.models import PerguntaRequest
from app.services.claude_service import perguntar_claude

app = FastAPI()

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
