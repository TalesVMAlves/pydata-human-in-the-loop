from langchain_core.tools import tool

from app.core.schemas import PlanoRespostasInput
from app.services.auth import servico_gmail
from app.utils.helpers import criar_mensagem_base64, buscar_e_formatar_emails

## Ferramentas de Planejamento
@tool(args_schema=PlanoRespostasInput)
def preparar_respostas_em_lote(respostas: list) -> str:
    """Prepara um plano com múltiplas respostas de email para diferentes destinatários.
    Esse plano será pausado para a revisão do utilizador antes do envio real.
    """
    if not respostas:
        return "Nenhuma resposta fornecida no plano."

    plano_formatado = "**[ PLANO DE RESPOSTAS EM LOTE GERADO ]**\n"
    for i, resp in enumerate(respostas, 1):
        resp_dict = resp.model_dump() if hasattr(resp, "model_dump") else resp
        
        corpo_original = resp_dict.get('corpo', '')
        corpo_em_citacao = corpo_original.replace("\n", "\n> ")
        
        plano_formatado += (
            f"\n**{i}. Destinatário:** {resp_dict.get('destinatario', 'Desconhecido')}\n"
            f"**Assunto:** {resp_dict.get('assunto', 'Sem Assunto')}\n"
            f"**Mensagem:**\n"
            f"> {corpo_em_citacao}\n"
            f"{'='*40}\n"
        )
    return plano_formatado

## Ferramentas Seguras (Safe)
@tool
def resumir_emails(max_resultados: int = 5) -> str:
    """Lê a caixa de entrada e retorna um resumo dos últimos emails recebidos."""
    return buscar_e_formatar_emails(max_resultados)

@tool
def ajudar_redigir_email(destinatario: str, assunto: str, corpo: str) -> str:
    """Rascunha uma resposta profissional e a salva como rascunho na conta (não envia)."""
    try:
        raw_msg = criar_mensagem_base64(destinatario, assunto, corpo)
        draft = servico_gmail.users().drafts().create(userId='me', body={'message': raw_msg}).execute()
        return f"Rascunho criado! ID: {draft['id']}"
    except Exception as e:
        return f"Erro ao criar rascunho: {e}"

## Ferramentas Sensíveis (Sensitive)
@tool
def apagar_spam(email_ids: list[str]) -> str:
    """Exclui permanentemente os emails identificados como spam com base nos IDs."""
    try:
        apagados = 0
        for email_id in email_ids:
            servico_gmail.users().messages().delete(userId='me', id=email_id).execute()
            apagados += 1
        return f"{apagados} email(s) apagado(s) permanentemente."
    except Exception as e:
        return f"Erro ao apagar: {e}"

@tool
def enviar_email(destinatario: str, assunto: str, corpo: str) -> str:
    """Dispara o email oficializado para o destinatário."""
    try:
        raw_msg = criar_mensagem_base64(destinatario, assunto, corpo)
        sent = servico_gmail.users().messages().send(userId='me', body=raw_msg).execute()
        return f"Enviado com sucesso! ID: {sent['id']}"
    except Exception as e:
        return f"Erro ao enviar: {e}"