from fastapi.testclient import TestClient
from app import main
import anthropic
import httpx

client = TestClient(main.app)

def test_chat_retorna_reposta(monkeypatch):

    monkeypatch.setattr(main, "perguntar_claude", lambda texto: "Funcionamos de seg a sexta!")

    resposta = client.post("/chat", json={"pergunta": "Qual é o horário?"})

    assert resposta.status_code == 200
    assert resposta.json() == {"resposta": "Funcionamos de seg a sexta!"}


def test_chat_401_chave_invalida(monkeypatch):
    resp_falsa = httpx.Response(401, request=httpx.Request("POST", "http://x"))

    def falsa(texto):
        raise anthropic.AuthenticationError("chave ruim", response=resp_falsa, body=None)

    monkeypatch.setattr(main, "perguntar_claude", falsa)

    resposta = client.post("/chat", json={"pergunta": "oi"})

    assert resposta.status_code == 401

def test_chat_429_limite_de_requisicoes(monkeypatch):
    resp_falsa = httpx.Response(429, request=httpx.Request("POST", "http://x"))

    def falsa(texto):
        raise anthropic.RateLimitError("muitas", response=resp_falsa, body=None)

    monkeypatch.setattr(main, "perguntar_claude", falsa)

    resposta = client.post("/chat", json={"pergunta": "oi"})

    assert resposta.status_code == 429

def test_chat_504_timeout(monkeypatch):
    req_falsa = httpx.Request("POST", "http://x")

    def falsa(texto):
        raise anthropic.APITimeoutError(request=req_falsa)

    monkeypatch.setattr(main, "perguntar_claude", falsa)

    resposta = client.post("/chat", json={"pergunta": "oi"})

    assert resposta.status_code == 504

def test_chat_502_erro_generico(monkeypatch):
    req_falsa = httpx.Request("POST", "http://x")

    def falsa(texto):
        raise anthropic.APIError("falha geral", req_falsa, body=None)

    monkeypatch.setattr(main, "perguntar_claude", falsa)

    resposta = client.post("/chat", json={"pergunta": "oi"})

    assert resposta.status_code == 502