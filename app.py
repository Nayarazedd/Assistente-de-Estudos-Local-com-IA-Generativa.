import os
import streamlit as st
import requests
import time
from streamlit_autorefresh import st_autorefresh
from biblioteca import buscar
from redacao import corrigir_redacao, salvar_redacao, comparar_com_anterior
import json

st.set_page_config(page_title="Minha IA de Estudos", page_icon="📚", layout="centered")

# Estilo visual básico (botões arredondados)
st.markdown("""
<style>
.stButton button {
    border-radius: 12px;
    height: 3em;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"
if "materia_atual" not in st.session_state:
    st.session_state.materia_atual = None
if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = {}

MATERIAS = ["Matemática", "Redação", "História", "Direito Constitucional"]

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

# --- TELA INICIAL: botões tipo Duolingo ---
def tela_inicio():
    st.title("📚 Minha IA de Estudos")
    st.write("Escolha uma matéria pra começar:")

    colunas = st.columns(2)
    for i, materia in enumerate(MATERIAS):
        with colunas[i % 2]:
            if st.button(materia, use_container_width=True):
                st.session_state.materia_atual = materia.lower().replace(" ", "_").replace("á", "a").replace("ã", "a").replace("ç", "c").replace("ó", "o").replace("í", "i")
                st.session_state.pagina = "chat"
                st.rerun()

    st.divider()
    if st.button("⏱️ Pomodoro", use_container_width=True):
        st.session_state.pagina = "pomodoro"
        st.rerun()
    if st.button("📈 Linha do tempo", use_container_width=True):
        st.session_state.pagina = "timeline"
        st.rerun()
    if st.button("✍️ Corrigir redação", use_container_width=True):
        st.session_state.pagina = "redacao"
        st.rerun()

# --- TELA DE CHAT POR MATÉRIA ---
def tela_chat():
    materia = st.session_state.materia_atual
    st.title(f"💬 {materia.replace('_', ' ').title()}")

    if materia not in st.session_state.historico_chat:
        st.session_state.historico_chat[materia] = []

    for msg in st.session_state.historico_chat[materia]:
        with st.chat_message(msg["autor"]):
            st.write(msg["texto"])

    pergunta = st.chat_input("Digite sua pergunta...")
    if pergunta:
        st.session_state.historico_chat[materia].append({"autor": "user", "texto": pergunta})
        resultados = buscar(materia, pergunta)
        contexto = "\n\n".join([p.page_content for p in resultados]) if resultados else "Sem material salvo ainda."
        
        prompt_final = f"Você é um professor direto e claro. Responda a pergunta do aluno usando APENAS este contexto:\n\n{contexto}\n\nPergunta: {pergunta}"
        
        resposta = consultar_ia(prompt_final)
        
        st.session_state.historico_chat[materia].append({"autor": "assistant", "texto": resposta})
        st.rerun()

    if st.button("⬅️ Voltar"):
        st.session_state.pagina = "inicio"
        st.rerun()

# --- TELA DE POMODORO ---
def tela_pomodoro():
    st.title("⏱️ Pomodoro")

    if "pomodoro_rodando" not in st.session_state:
        st.session_state.pomodoro_rodando = False
        st.session_state.pomodoro_fim = None

    minutos = st.slider("Minutos de foco", 5, 60, 25)

    if not st.session_state.pomodoro_rodando:
        if st.button("Começar"):
            st.session_state.pomodoro_fim = time.time() + minutos * 60
            st.session_state.pomodoro_rodando = True
            st.rerun()
    else:
        # Atualiza a tela a cada 1 segundo automaticamente para o cronômetro rodar na vista
        st_autorefresh(interval=1000, key="refresh_pomodoro")
        restante = int(st.session_state.pomodoro_fim - time.time())
        
        if restante <= 0:
            st.success("🎉 Tempo esgotado! Hora da pausa de descanso!")
            st.session_state.pomodoro_rodando = False
        else:
            mins, segs = divmod(restante, 60)
            st.metric("Tempo restante", f"{mins:02d}:{segs:02d}")
            if st.button("Parar"):
                st.session_state.pomodoro_rodando = False
                st.rerun()

    if st.button("⬅️ Voltar"):
        st.session_state.pagina = "inicio"
        st.rerun()

# --- TELA DE REDAÇÃO ---
def tela_redacao():
    st.title("✍️ Corrigir Redação")
    texto = st.text_area("Cole sua redação aqui", height=250)

    if st.button("Corrigir"):
        if texto.strip():
            with st.spinner("Analisando competências..."):
                avaliacao = corrigir_redacao(texto)
                comparacao = comparar_com_anterior(avaliacao)
                salvar_redacao(texto, avaliacao)
            st.subheader("Avaliação")
            st.write(avaliacao)
            st.subheader("Comparação com a redação anterior")
            st.write(comparacao)
        else:
            st.warning("Cole um texto de redação válido antes de enviar.")

    if st.button("⬅️ Voltar"):
        st.session_state.pagina = "inicio"
        st.rerun()

# --- TELA DE LINHA DO TEMPO ---
def tela_timeline():
    st.title("📈 Sua Linha do Tempo")

    if os.path.exists("historico_redacoes.json"):
        with open("historico_redacoes.json", "r", encoding="utf-8") as f:
            historico = json.load(f)
        for item in reversed(historico):
            with st.expander(f"Redação de {item['data']}"):
                st.write(item["avaliacao"])
    else:
        st.write("Ainda não tem redações salvas.")

    if st.button("⬅️ Voltar"):
        st.session_state.pagina = "inicio"
        st.rerun()

# --- ROTEADOR ---
if st.session_state.pagina == "inicio":
    tela_inicio()
elif st.session_state.pagina == "chat":
    tela_chat()
elif st.session_state.pagina == "pomodoro":
    tela_pomodoro()
elif st.session_state.pagina == "redacao":
    tela_redacao()
elif st.session_state.pagina == "timeline":
    tela_timeline()