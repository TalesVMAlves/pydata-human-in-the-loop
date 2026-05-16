import base64
from email.message import EmailMessage
from app.services.auth import servico_gmail

def criar_mensagem_base64(destinatario: str, assunto: str, corpo: str) -> dict:
    """Cria uma mensagem de email e codifica em Base64. Formato aceito pelo Gmail"""
    mensagem = EmailMessage()
    mensagem.set_content(corpo)
    mensagem['To'] = destinatario
    mensagem['Subject'] = assunto
    
    encoded_message = base64.urlsafe_b64encode(mensagem.as_bytes()).decode()
    return {'raw': encoded_message}

def buscar_e_formatar_emails(max_resultados: int = 5) -> str:
    """Busca os emails no Gmail e retorna o resumo em texto."""
    try:
        resultados = servico_gmail.users().messages().list(userId='me', maxResults=max_resultados, q="in:inbox").execute()
        mensagens = resultados.get('messages', [])
        
        if not mensagens: 
            return "Nenhum email encontrado na caixa de entrada."

        resumo = []
        for msg in mensagens:
            txt = servico_gmail.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['Subject', 'From']).execute()
            cabs = txt['payload']['headers']
            
            assunto = next((h['value'] for h in cabs if h['name'] == 'Subject'), "Sem Assunto")
            remetente = next((h['value'] for h in cabs if h['name'] == 'From'), "Desconhecido")
            
            resumo.append(f"- ID: {msg['id']} | De: {remetente} | Assunto: {assunto}")
            
        return "\n".join(resumo)
        
    except Exception as e:
        return f"Erro ao acessar emails: {e}"