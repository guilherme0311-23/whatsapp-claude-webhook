from fastapi.testclient import TestClient
from app import main

client = TestClient(main.app)

def test_chat_retorna_reposta(monkeypatch):

    monkeypatch.setattr(main, "perguntar_claude", lambda texto: "Funcionamos de seg a sexta!")

    resposta = client.post("/chat", json={"pergunta": "Qual é o horário?"})

    assert resposta.status_code == 200
    assert resposta.json() == {"resposta": "Funcionamos de seg a sexta!"}