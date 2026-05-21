# Configuração e Execução com LangGraph Studio

O LangGraph Studio é a interface visual que facilita a interação com agentes, e a visualização de  Human-in-the-loop (Mesa de Revisão e Freio de Mão).

Para executar a interface do Studio localmente, você precisa ter uma conta no LangSmith e a CLI do LangGraph instalada.

## 1. O Arquivo langgraph.json

O arquivo atua como um "mapa" para o Studio entender como o seu projeto está montado e onde encontrar o seu grafo.

Na raiz do seu projeto, certifique-se de que o arquivo langgraph.json tem a seguinte estrutura:
```JSON
{
"dependencies": ["."],
"graphs": {
"agente_email": "path/to/agente.py" 
},
"env": ".env"
}
```

### O que cada camplo significa?
- `graphs`: Mapeia um nome (ex: agente_email) para o arquivo onde o grafo foi desenhado (app/core/graph.py) e aponta exatamente para a variável final do grafo que chamou o .compile() (no nosso caso, a variável agente_compilado).
- `env`: Aponta para o arquivo .env para carregar as chaves de API do LLM.

## 2. Autenticação do LangSmith
Antes de subir o servidor, certifique-se de que no seu arquivo .env as credenciais do LangSmith estejam configuradas
```env
OPENAI_API_KEY= 

LANGSMITH_API_KEY=
LANGSMITH_TRACING_V2=true
LANGSMITH_PROJECT="Project Name"
```
## 3. Execuntado o Studio no Terminal
Ative o ambiente virtual e confira que todos os pacotes estão instalados.

No terminal, estando na pasta raiz do projeto, execute:
```bash
langgraph dev
```

Uma nova aba do navegador irá abrir com a CLI do Langgraph, você deve ser capaz de ver o seu grafo nela.
Pronto agora é só experimentar com a ferramenta.