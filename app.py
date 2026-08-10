import os
import streamlit as st
import requests
from biblioteca import pegar_banco, buscar

# Configuração da página
st.set_page_config(page_title="Assistente de Estudos", page_icon="📚", layout="wide")

def consultar_ia(prompt_final):
    """Função unificada: usa a API do Google na nuvem ou o Ollama local."""
    api_key = None
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt_final,
            )
            return response.text
        except Exception as e:
            return f"Erro ao processar com a API do Google: {e}"

    # Fallback para o Ollama local
    try:
        resposta_bruta = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt_final, "stream": False},
            timeout=15
        )
        return resposta_bruta.json()["response"]
    except Exception as e:
        return f"Erro de conexão: Nenhuma chave de API configurada e o Ollama local não está rodando. Detalhe: {e}"

def tela_chat():
    st.title("💬 Assistente de Estudos")
    
    materia = st.selectbox("Escolha a Matéria:", ["Matemática", "História", "Biologia", "Física", "Redação"])
    
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    pergunta = st.chat_input("Digite sua pergunta...")
    if pergunta:
        st.session_state.mensagens.append({"role": "user", "content": pergunta})
        with st.chat_message("user"):
            st.markdown(pergunta)

        with st.chat_message("assistant"):
            with st.spinner("Buscando conhecimento..."):
                # Busca contexto nos PDFs salvos na gaveta da matéria
                resultados = buscar(materia, pergunta, k=2)
                contexto = "\n".join([doc.page_content for doc in resultados]) if resultados else "Nenhum material específico encontrado."

                prompt_final = f"""Com base no contexto abaixo, responda à pergunta do aluno de forma clara e didática.
Contexto:
{contexto}

Pergunta: {pergunta}
"""
                resposta = consultar_ia(prompt_final)
                st.markdown(resposta)
                st.session_state.mensagens.append({"role": "assistant", "content": resposta})

def tela_redacao():
    st.title("✍️ Corrigir Redação")
    
    from redacao import corrigir_redacao, salvar_redacao, comparar_com_anterior

    texto = st.text_area("Cole sua redação aqui", height=250)
    
    if st.button("Corrigir"):
        if texto.strip():
            with st.spinner("Analisando competências do Enem..."):
                avaliacao = corrigir_redacao(texto)
                st.subheader("Avaliação")
                st.markdown(avaliacao)
                
                salvar_redacao(texto, avaliacao)
                
                st.subheader("Comparação com a redação anterior")
                st.markdown(comparar_com_anterior(avaliacao))
        else:
            st.warning("Cole um texto de redação válido antes de enviar.")

def tela_pomodoro():
    st.title("⏱️ Pomodoro de Estudos")
    st.write("Foque por 25 minutos e descanse 5.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Iniciar Foco (25m)"):
            st.success("Ciclo de foco iniciado! Vai pra cima!")
    with col2:
        if st.button("Iniciar Descanso (5m)"):
            st.info("Hora de relaxar um pouco os olhos.")

# Menu lateral de navegação
st.sidebar.title("Navegação")
opcao = st.sidebar.radio("Ir para:", ["Chat de Estudos", "Corrigir Redação", "Pomodoro"])

if opcao == "Chat de Estudos":
    tela_chat()
elif opcao == "Corrigir Redação":
    tela_redacao()
elif opcao == "Pomodoro":
    tela_pomodoro()