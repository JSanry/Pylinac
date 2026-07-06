import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Simulador de Física Médica", page_icon="⚛️", layout="centered")

@st.cache_data
def carregar_banco_questoes():
    try:
        df = pd.read_csv("questoes.csv")
        questoes = []
        for _, row in df.iterrows():
            opcoes = [opt.strip() for opt in str(row['opcoes']).split('|') if opt.strip()]
            questoes.append({
                "id": row['id'],
                "modulo": row['modulo'],
                "pergunta": row['pergunta'],
                "opcoes": opcoes,
                "correta": str(row['correta']).strip(),
                "comentario": str(row['comentario']) if pd.notna(row['comentario']) else ""
            })
        return questoes
    except Exception:
        return []

questoes_totais = carregar_banco_questoes()

if not questoes_totais:
    st.error("⚠️ Banco de dados 'questoes.csv' não encontrado ou vazio. Execute primeiro o script 'gerar_banco.py' na mesma pasta.")
else:
    if "quiz_iniciado" not in st.session_state:
        st.session_state.quiz_iniciado = False
    if "respostas_usuario" not in st.session_state:
        st.session_state.respostas_usuario = {}
    if "questoes_selecionadas" not in st.session_state:
        st.session_state.questoes_selecionadas = []

    st.title("⚛️ Quiz Interativo: Física Médica e Radioproteção")

    if not st.session_state.quiz_iniciado:
        st.subheader("Configurações do Bloco de Exercícios")
        modulos_disponiveis = sorted(list(set(q["modulo"] for q in questoes_totais)))
        
        opcao_modulo = st.radio("Selecione os temas das questões:", ["Todos os 7 Módulos", "Escolher um Módulo Específico"])
        if opcao_modulo == "Escolher um Módulo Específico":
            modulo_escolhido = st.selectbox("Selecione o módulo pretendido:", modulos_disponiveis)
            questoes_filtradas = [q for q in questoes_totais if q["modulo"] == modulo_escolhido]
        else:
            questoes_filtradas = questoes_totais

        max_questoes = len(questoes_filtradas)
        qtd_questoes = st.slider("Quantas questões quer responder no teste?", 1, max_questoes, min(10, max_questoes))
        
        if st.button("Gerar Caderno de Questões 🚀"):
            st.session_state.questoes_selecionadas = random.sample(questoes_filtradas, qtd_questoes)
            st.session_state.respostas_usuario = {}
            st.session_state.quiz_iniciado = True
            st.rerun()
    else:
        st.subheader("📝 Questões Selecionadas")
        questoes = st.session_state.questoes_selecionadas
        erros_por_modulo = []

        for idx, q in enumerate(questoes):
            st.markdown(f"**Questão {idx + 1}** | *{q['modulo']}* (ID: {q['id']})")
            st.write(q["pergunta"])
            
            chave_resposta = f"quest_{q['id']}"
            
            resposta = st.radio(
                "Escolha a sua resposta:", 
                q["opcoes"], 
                index=None, 
                key=chave_resposta, 
                disabled=chave_resposta in st.session_state.respostas_usuario
            )
            
            if resposta and chave_resposta not in st.session_state.respostas_usuario:
                if st.button("Validar Resposta", key=f"btn_{q['id']}"):
                    st.session_state.respostas_usuario[chave_resposta] = resposta
                    st.rerun()
                    
            if chave_resposta in st.session_state.respostas_usuario:
                resp_dada = st.session_state.respostas_usuario[chave_resposta]
                if resp_dada == q["correta"]:
                    st.success("🎯 **Resposta Correta!**")
                else:
                    st.error(f"❌ **Incorreto.** A resposta certa nos documentos é: **{q['correta']}**")
                    erros_por_modulo.append(q["modulo"])
                    
                if q["comentario"]:
                    with st.expander("💡 Ver Comentários e Resolução Detalhada"):
                        st.info(q["comentario"])
            st.markdown("---")

        if len(st.session_state.respostas_usuario) == len(questoes):
            if st.button("Finalizar Teste e Gerar Relatório 📊"):
                st.subheader("🏁 Resumo de Desempenho")
                total_respondidas = len(questoes)
                acertos = sum(1 for q in questoes if st.session_state.respostas_usuario.get(f"quest_{q['id']}") == q["correta"])
                porcentagem = (acertos / total_respondidas) * 100
                
                st.metric(label="Percentagem de Acertos", value=f"{porcentagem:.1f}%", delta=f"{acertos}/{total_respondidas} Acertos")
                st.progress(acertos / total_respondidas)
                
                if erros_por_modulo:
                    st.warning("⚠️ **Temas sugeridos para revisão com base nos seus erros atuais:**")
                    for mod in set(erros_por_modulo):
                        st.write(f"- **{mod}**: Sugere-se reler as notas de aula e os enunciados deste módulo focado em erros comuns.")
                else:
                    st.balloons()
                    st.success("🎉 **Desempenho Perfeito!** Você acertou todas as questões deste bloco!")
                    
                if st.button("Configurar Novo Quiz 🔄"):
                    st.session_state.quiz_iniciado = False
                    st.session_state.respostas_usuario = {}
                    st.session_state.questoes_selecionadas = []
                    st.rerun()