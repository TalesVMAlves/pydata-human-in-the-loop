# Objetivo
- Explorar como estruturar fluxos com nodes e tools no LangGraph, diferenciando ferramentas seguras que o agente pode executar de forma autônoma daquelas que exigem aprovação do usuário antes de realizar ações sensíveis
# Configurações necessárias
Para executar este projeto na sua máquina, você precisará configurar o aceso à API do Gmail e instalar as dependÊncias.

## 1. **Configuração do Google Cloud (Gmail API)**
O agente lê e envia e-mails reais usando a conta Gmail cadastrada no projeto. Para isso, é necessário criar credênciais no GCP.

[Como criar e configurar o projeto GCP e Gmail API](docs/gcp.md). 
## 2. Configuração do Ambiente
Crie um ambiente virtual, instale as dependências e configure as variáveis de ambiente:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```


*(Adicione suas chaves de API no arquivo `.env`)*

### 3. Execução com LangGraph Studio
O LangGraph Studio é uma das melhores formas de visualizar os breakpoints (`interrupt_after` e `interrupt_before`) em tempo real. 

[Como configurar e executar o Studio](docs/langgraph_studio.md). 