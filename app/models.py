from pydantic import BaseModel


class PerguntaRequest(BaseModel):
    pergunta: str
