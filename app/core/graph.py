import os
import yaml
from dotenv import load_dotenv
from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage

from app.core.schemas import AgentState
from app.core.tools import resumir_emails, ajudar_redigir_email, preparar_respostas_em_lote, apagar_spam, enviar_email
from app.utils.helpers import buscar_e_formatar_emails

load_dotenv()

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

modelo_llm = config["llm"]["model"]
temperatura = config["llm"]["temperature"]
    
## Preparar as ferramentas
ferramentas_leitura = [resumir_emails, ajudar_redigir_email]
ferramentas_planeamento = [preparar_respostas_em_lote]
ferramentas_sensiveis = [apagar_spam, enviar_email]

## Instancia o LLM com os valores do config
llm = ChatOpenAI(model=modelo_llm, temperature=temperatura)
llm_com_ferramentas = llm.bind_tools(ferramentas_leitura + ferramentas_planeamento + ferramentas_sensiveis) ## Vincula as ferramentas ao modelo de linguagem

## Orquestrador do agente, gera a próxima mensagem a partir do conteúdo recebido de um nó, ou gera a intenção de uso de ferramentas
def agente_email(state: AgentState):
    contexto_atual = state.get("contexto_emails", "Nenhum contexto prévio carregado.")
    
    ## Atualizar o contexto no estado após resumir_emails
    if state["messages"]:
        ultima_mensagem = state["messages"][-1]
        if ultima_mensagem.type == "tool" and ultima_mensagem.name == "resumir_emails":
            contexto_atual = ultima_mensagem.content
            print("\n[SISTEMA] Contexto global atualizado!")

    instrucoes_sistema = SystemMessage(
        content=f"Você é um assistente de email inteligente e seguro.\n"
                f"Sempre leve em consideração o seguinte contexto da caixa de entrada do usuário "
                f"para redigir respostas mais assertivas e personalizadas:\n\n"
                f"### CONTEXTO ATUAL DOS EMAILS ###\n"
                f"{contexto_atual}\n"
    )
    mensagens_para_llm = [instrucoes_sistema] + state["messages"]
    resposta = llm_com_ferramentas.invoke(mensagens_para_llm)
    return {"messages": [resposta], "contexto_emails": contexto_atual}

## Responsável por atualizar o contexto com um resumo para os 5 últimos emails assim que o agente é inicializado
def carregar_contexto_inicial(state: AgentState):
    """Lê a caixa de entrada real e salva no Estado antes do LLM pensar."""
    if not state.get("contexto_emails"): 
        resumo_texto = buscar_e_formatar_emails(max_resultados=5)
        return {"contexto_emails": resumo_texto}
    return {} 

## A partir do valor do Agente email decide o fluxo dos dados
def roteador(state: AgentState) -> Literal["Executar_Seguro", "Executar_Revisáveis", "Executar_Sensíveis", "__end__"]:
    ultima = state["messages"][-1]
    if not ultima.tool_calls:
        return END
    
    nome_ferramenta = ultima.tool_calls[0]["name"]
    
    if nome_ferramenta in ["apagar_spam", "enviar_email"]:
        return "Executar_Sensíveis"
    elif nome_ferramenta == "preparar_respostas_em_lote":
        return "Executar_Revisáveis"
    else:
        return "Executar_Seguro"

## Criação do grafo e adição dos nós
workflow = StateGraph(AgentState)
workflow.add_node("Carregar_Contexto", carregar_contexto_inicial)
workflow.add_node("Agente_Email", agente_email)
workflow.add_node("Executar_Seguro", ToolNode(ferramentas_leitura))
workflow.add_node("Executar_Revisáveis", ToolNode(ferramentas_planeamento))
workflow.add_node("Executar_Sensíveis", ToolNode(ferramentas_sensiveis))

## Adição das arestas e arestas condicionais
workflow.add_edge(START, "Carregar_Contexto")
workflow.add_edge("Carregar_Contexto", "Agente_Email")
workflow.add_conditional_edges("Agente_Email", roteador)
workflow.add_edge("Executar_Seguro", "Agente_Email")
workflow.add_edge("Executar_Revisáveis", "Agente_Email")
workflow.add_edge("Executar_Sensíveis", "Agente_Email")

## Necessário se for executar via CLI
# memoria = MemorySaver()

## Adiciona a memória e as travas do Human-in-the-loop
agente_email = workflow.compile(
    # checkpointer=memoria,
    interrupt_after=["Executar_Revisáveis"],
    interrupt_before=["Executar_Sensíveis"] 
)

## Boa prática exportar o diagrama, se for necessário um formato diferente de PNG, 
## utilizar o Markdown para gerar o novo formato é uma solução simples 
def exportar_diagrama():
    """Gera e salva o diagrama do grafo na pasta artifacts."""
    os.makedirs("artifacts", exist_ok=True)
    
    ## Salva o código Mermaid em um arquivo Markdown
    mermaid_code = agente_email.get_graph().draw_mermaid()
    with open("artifacts/grafo_agente.md", "w", encoding="utf-8") as f:
        f.write(f"```mermaid\n{mermaid_code}\n```")
    
    ## Tenta salvar diretamente como imagem PNG
    try:
        png_data = agente_email.get_graph().draw_mermaid_png()
        with open("artifacts/grafo_agente.png", "wb") as f:
            f.write(png_data)
        print("Diagramas exportados para 'artifacts/'")
    except Exception as e:
        print("Código Mermaid salvo em 'artifacts/grafo_agente.md'")
        print(f"Não foi possível gerar o PNG diretamente. Erro: {e}")
        print("Você também pode copiar o conteúdo do arquivo .md para o Mermaid Live Editor.")