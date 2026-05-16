import os
import yaml
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def obter_servico_gmail():
    """Lê as configurações, autentica e retorna o serviço do Gmail."""
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    SCOPES = config["gmail_api"]["scopes"]
    CREDENTIALS_FILE = config["gmail_api"]["credentials_file"]
    TOKEN_FILE = config["gmail_api"]["token_file"]

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

servico_gmail = obter_servico_gmail()