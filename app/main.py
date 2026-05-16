import uuid
from langchain_core.messages import ToolMessage
from app.core.graph import agente_email, exportar_diagrama

def executar_chat():
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    print("\nAssistente de Email PyData 2026 Iniciado!\n")
    
    while True:
        user_input = input("Você: ")
        if user_input.lower() in ['sair', 'exit', 'quit']: break
            
        estado_inicial = {"messages": [("user", user_input)]}
        
        ## Roda o grafo até bater em alguma trava (before ou after)
        for evento in agente_email.stream(estado_inicial, config, stream_mode="values"):
            ultima_msg = evento["messages"][-1]
            if ultima_msg.type == "ai" and ultima_msg.content:
                print(f"IA: {ultima_msg.content}")

        ## Verifica qual trava pausou o sistema
        estado_atual = agente_email.get_state(config)
        
        ## INTERRUPT_AFTER
        if estado_atual.next and estado_atual.next[0] == "Agente_Email":
            ## Se o próximo passo é voltar pro LLM, significa que acabamos de sair do ToolNode
            ultima_msg_ferramenta = estado_atual.values["messages"][-1]
            
            if ultima_msg_ferramenta.name == "gerar_proposta_resposta":
                print("\n[MESA DE REVISÃO] A IA preparou um rascunho:")
                print(f"   Texto original: {ultima_msg_ferramenta.content}")
                
                edicao = input("\nDigite suas alterações (ou aperte Enter para aprovar como está): ")
                
                if edicao.strip() != "":
                    print("Texto atualizado com sucesso")
                    ## Substituímos o resultado da ferramenta com o texto do humano
                    mensagem_editada = ToolMessage(
                        tool_call_id=ultima_msg_ferramenta.tool_call_id,
                        name=ultima_msg_ferramenta.name,
                        content=f"O usuário revisou o texto para: {edicao}"
                    )
                    ## Atualiza o State
                    agente_email.update_state(config, {"messages": [mensagem_editada]})
                else:
                    print("✅ Rascunho aprovado sem alterações.")
                
                # Retoma o fluxo para a IA ler a revisão e continuar
                for evento in agente_email.stream(None, config, stream_mode="values"):
                    ultima_msg = evento["messages"][-1]
                    if ultima_msg.type == "ai" and ultima_msg.content:
                        print(f" IA: {ultima_msg.content}")

        ## Verifica se o grafo foi interrompido (Hit a Breakpoint)
        estado_atual = agente_email.get_state(config)
        if estado_atual.next and estado_atual.next[0] == "Executar_Sensíveis":
            
            print("\n[ALERTA HUMAN-IN-THE-LOOP] A IA solicitou uma ação destrutiva/irreversível:")
            
            ## Pega as ferramentas que a IA quer executar
            ultima_ia_msg = estado_atual.values["messages"][-1]
            for tool in ultima_ia_msg.tool_calls:
                print(f"Ferramenta: {tool['name']} | Argumentos: {tool['args']}")
            
            permissao = input("\nVocê autoriza esta ação? (s/n): ")
            
            if permissao.lower() == 's':
                print("Ação Autorizada. Executando >")
                ## Retoma o grafo de onde parou
                for evento in agente_email.stream(None, config, stream_mode="values"):
                    ultima_msg = evento["messages"][-1]
                    if ultima_msg.type == "ai" and ultima_msg.content:
                        print(f" IA: {ultima_msg.content}")
            else:
                print("Ação Bloqueada. Informando a IA X\n")
                ## Feedback de rejeição para a IA repensar
                mensagens_rejeicao = [
                    ToolMessage(
                        tool_call_id=t["id"],
                        name=t["name"],
                        content="O usuário NÃO AUTORIZOU essa ação. Peça desculpas e pergunte o que fazer a seguir."
                    ) for t in ultima_ia_msg.tool_calls
                ]
                
                ## Injeta a rejeição no estado pulando o nó sensível
                agente_email.update_state(config, {"messages": mensagens_rejeicao}, as_node="Executar_Sensíveis")
                
                ## Retoma o fluxo para a IA ler a rejeição
                for evento in agente_email.stream(None, config, stream_mode="values"):
                    ultima_msg = evento["messages"][-1]
                    if ultima_msg.type == "ai" and ultima_msg.content:
                        print(f" IA: {ultima_msg.content}")

if __name__ == "__main__":
    exportar_diagrama()
    executar_chat()