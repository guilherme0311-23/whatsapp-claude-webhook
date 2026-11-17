import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)

CAMINHO = Path(__file__).parent.parent / "examples" / "webhook_payload_exemplo.json"
PAYLOAD = json.loads(CAMINHO.read_text(encoding="utf-8"))


def test_webhook_recebe_e_agenda_processamento(monkeypatch: pytest.MonkeyPatch) -> None:
    
    chamadas: list[object] = []
    monkeypatch.setattr(main, "processar_mensagem", lambda payload: chamadas.append(payload))

    resposta = client.post("/webhook", json=PAYLOAD)

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "recebido"}
    assert len(chamadas) == 1