from typing import Annotated, List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState

## Herdamos da classe MessagesState -> messages: Annotated[list[AnyMessage], add_messages]
## O add_messages garante que novas mensagens sejam anexadas, e não sobrescritas
class AgentState(MessagesState):
    ## Guarda o resumo da caixa de entrada globalmente
    contexto_emails: str

class DadosResposta(BaseModel):
    """Esquema de uma resposta individual de email."""
    destinatario: str = Field(..., description="O endereço de email do destinatário")
    assunto: str = Field(..., description="O assunto do email")
    corpo: str = Field(..., description="O corpo da mensagem a ser enviada")

class PlanoRespostasInput(BaseModel):
    """Esquema para a ferramenta de planeamento em lote."""
    respostas: List[DadosResposta] = Field(..., description="Uma lista de emails para responder")