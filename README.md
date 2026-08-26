# WhatsApp Claude Webhook

Bot de atendimento via WhatsApp que usa a API da Anthropic (Claude) para responder clientes automaticamente, com processamento assíncrono e tratamento de erros robusto.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688)
![Anthropic](https://img.shields.io/badge/Anthropic%20SDK-0.122-D97757)

## O que esse projeto faz

Recebe mensagens de WhatsApp via webhook, processa com a API do Claude usando um system prompt com escopo definido, e responde de forma assíncrona — sem travar o webhook nem duplicar mensagens.

O mesmo motor de resposta (`perguntar_claude`) é compartilhado entre dois endpoints: um `/chat` simples pra teste direto via API, e o `/webhook` que recebe o payload real de plataformas de WhatsApp (formato compatível com Evolution API).

## Arquitetura do fluxo assíncrono

O ponto mais importante deste projeto não é "chamar uma API de IA" — é fazer isso **sem quebrar o contrato do webhook**.

Plataformas de WhatsApp (Meta, Evolution API, etc) esperam uma resposta `200 OK` quase instantânea. Se o servidor demorar pra responder — por exemplo, esperando o Claude gerar uma resposta, o que pode levar alguns segundos — a plataforma assume falha e **reenvia a mensagem**, gerando duplicidade de resposta pro cliente final.

Por isso, o fluxo aqui é:

1. Webhook recebe o payload → retorna `200 OK` **imediatamente**
2. O processamento da mensagem (chamada ao Claude) roda em `BackgroundTask`, fora do ciclo de resposta do webhook
3. A resposta gerada é logada (neste MVP) — em produção real, seria enviada de volta pela API da plataforma de WhatsApp

Essa é uma regra que não teve segunda versão: não existe implementação síncrona anterior a esta no histórico do projeto.

## Pontos defensáveis (o que dá pra provar, não só prometer)

- **Erro tratado por tipo, não genérico**: `AuthenticationError`, `RateLimitError`, `APITimeoutError` e `APIError` retornam status HTTP e mensagem específicos — o cliente final nunca vê stack trace cru
- **Resistência a prompt injection testada**: o system prompt define escopo (só responde sobre horário e produtos) e foi testado ativamente tentando "quebrar" o próprio bot antes de considerar essa etapa fechada
- **DRY real**: `/chat` e `/webhook` chamam a mesma função `perguntar_claude()` — zero duplicação de lógica de IA entre os dois pontos de entrada
- **9 erros de infraestrutura documentados** durante o desenvolvimento (Docker, PowerShell, Evolution API, encoding), com causa raiz e solução registradas — não é "tentei até funcionar", é debug metódico

## Estado atual (honestidade > hype)

- ✅ Lógica de webhook, processamento assíncrono e integração com Claude: **validada e funcional**, testada via simulação de payload (Postman) reproduzindo o formato real de evento `messages.upsert`
- ⏳ Conexão real com uma instância de WhatsApp (via Evolution API ou similar): **pendente** — é um gate de infraestrutura separado (licenciamento, Docker, Postgres/Redis), não um gap de lógica de aplicação

Em outras palavras: o "cérebro" do bot está pronto e testado. O "cano" que liga ele a um número de WhatsApp real é a próxima etapa, e depende de infraestrutura de terceiros, não de código.

## Como rodar localmente

### Pré-requisitos
- Python 3.13+
- Uma chave de API da Anthropic ([console.anthropic.com](https://console.anthropic.com))

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/guilherme0311-23/whatsapp-claude-webhook.git
cd whatsapp-claude-webhook

# 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure sua chave de API
cp .env.example .env
# Edite o .env e adicione sua ANTHROPIC_API_KEY

# 5. Rode o servidor
uvicorn app.main:app --reload
```

O servidor sobe em `http://127.0.0.1:8000`.

### Testando

**Endpoint `/chat`** (pergunta direta):
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"pergunta\": \"Qual o horário de funcionamento?\"}"
```

**Endpoint `/webhook`** (simulação de payload de WhatsApp): use o exemplo em `examples/webhook_payload_exemplo.json` como body de uma requisição POST para `/webhook` — a resposta gerada aparece no log do terminal onde o uvicorn está rodando.

## Estrutura do projeto

```
app/
├── main.py                 # Rotas (/chat, /webhook)
├── models.py                # Modelos Pydantic (request e payload do webhook)
├── services/
│   └── claude_service.py   # Lógica de chamada ao Claude
└── core/
    └── config.py             # Configuração e variáveis de ambiente
examples/
└── webhook_payload_exemplo.json   # Payload real usado nos testes
```

## Stack

Python · FastAPI · Anthropic SDK (Claude) · Pydantic · python-dotenv

---

*Projeto desenvolvido como parte de estudo prático de integração de IA em canais de atendimento (WhatsApp), com foco em arquitetura correta desde a primeira versão — sem atalhos que exigiriam refatoração depois.*