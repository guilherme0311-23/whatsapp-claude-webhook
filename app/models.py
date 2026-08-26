from pydantic import BaseModel


class PerguntaRequest(BaseModel):
    pergunta: str

class MessageContent(BaseModel):
    conversation: str

class MessageKey(BaseModel):
    remoteJid: str
    fromMe: bool
    id: str

class WebhookData(BaseModel):
    key: MessageKey
    message: MessageContent
    messageType: str
    messageTimestamp: int

class WebhookPayload(BaseModel):
    event: str
    instance: str
    data: WebhookData
