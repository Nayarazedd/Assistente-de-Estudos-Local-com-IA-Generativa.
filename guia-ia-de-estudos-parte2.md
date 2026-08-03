# Guia Completo — Parte 2: Deixando a IA de Estudos do Seu Jeito

> Esse guia assume que a Parte 1 já está funcionando: você já tem o Ollama, o Python, e o `estudar.py` respondendo com base num PDF. Se ainda não chegou lá, termina a Parte 1 primeiro — o resto depende dela.

## O novo mapa (5 fases novas)

| Fase | O que entrega |
|---|---|
| 2 | Matérias organizadas em "gavetas" separadas |
| 3 | A IA pesquisa na internet quando você não tem PDF |
| 4 | Corretor de redação + linha do tempo de evolução |
| 5 | Interface estilo Duolingo, com Pomodoro |
| 6 | Vira um "app" de desktop de verdade |

Cada fase funciona sozinha. Você pode parar depois da Fase 3 por um tempo e já ter algo muito útil — não precisa terminar tudo pra começar a usar.

---

## Fase 2: Organização por matéria

### A ideia
Em vez de um banco só (`banco_de_estudos`), cada matéria vira uma **coleção separada** dentro do ChromaDB — como gavetas de um arquivo, todas no mesmo móvel, mas cada uma fechada e independente.

### Código: `biblioteca.py`

Esse arquivo centraliza tudo relacionado a guardar e buscar material. Cria ele na sua pasta do projeto:

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="mistral")

def pegar_banco(materia):
    """Abre (ou cria) a 'gaveta' de uma matéria específica."""
    return Chroma(
        persist_directory="./banco_de_estudos",
        embedding_function=embeddings,
        collection_name=materia  # aqui é a mágica: cada matéria = uma coleção diferente
    )

def adicionar_material(materia, pedacos):
    """Adiciona pedaços de texto (de um PDF já quebrado) numa matéria."""
    banco = pegar_banco(materia)
    banco.add_documents(pedacos)
    print(f"Material adicionado em '{materia}'!")

def buscar(materia, pergunta, k=3):
    """Busca os trechos mais relevantes dentro de UMA matéria só."""
    banco = pegar_banco(materia)
    return banco.similarity_search(pergunta, k=k)
```

### Como usar (exemplo)

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from biblioteca import adicionar_material

loader = PyPDFLoader("resumo_matematica.pdf")
paginas = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
pedacos = splitter.split_documents(paginas)

adicionar_material("matematica", pedacos)   # <- nome da gaveta
```

Repete isso pra cada PDF, trocando `"matematica"` por `"redacao"`, `"historia"`, `"direito_constitucional"` (pra concurso), etc. O nome que você escolher aqui é o nome da matéria pra sempre — escolha nomes sem espaço e sem acento pra evitar bug (`lingua_portuguesa`, não `Língua Portuguesa`).

---

## Fase 3: Acesso à internet

### A ideia
Quando você não tem PDF de um assunto, o sistema pesquisa na internet, traz um resumo, e **também salva isso na biblioteca** — assim da próxima vez ele já sabe, sem pesquisar de novo.

### Instalar as ferramentas

```
pip install duckduckgo-search beautifulsoup4
```

`duckduckgo-search` faz buscas sem precisar de conta ou chave de API (diferente do Google, que cobraria). `beautifulsoup4` ajuda a limpar o texto de uma página web.

### Código: `pesquisar_web.py`

```python
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

def pesquisar_na_internet(pergunta, num_resultados=3):
    """Busca na internet e retorna um resumo dos resultados."""
    resultados = []
    with DDGS() as ddgs:
        for r in ddgs.text(pergunta, max_results=num_resultados):
            resultados.append(f"{r['title']}: {r['body']}")
    return "\n\n".join(resultados)

def baixar_texto_de_pagina(url):
    """Pega o texto de uma página específica, se você já tem o link."""
    resposta = requests.get(url, timeout=10)
    sopa = BeautifulSoup(resposta.text, "html.parser")
    paragrafos = sopa.find_all("p")
    return "\n".join([p.get_text() for p in paragrafos])
```

### Juntando com o resto (versão atualizada do `estudar.py`)

```python
from biblioteca import buscar, adicionar_material
from pesquisar_web import pesquisar_na_internet
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def perguntar(materia, pergunta_do_usuario):
    pedacos_relevantes = buscar(materia, pergunta_do_usuario)

    if len(pedacos_relevantes) == 0:
        # Não tem nada guardado sobre isso ainda -> vai pra internet
        print("Não achei material salvo, pesquisando na internet...")
        resultado_web = pesquisar_na_internet(pergunta_do_usuario)

        # Guarda o que achou na biblioteca, pra não precisar pesquisar de novo
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        novo_documento = Document(page_content=resultado_web)
        pedacos_novos = splitter.split_documents([novo_documento])
        adicionar_material(materia, pedacos_novos)

        contexto = resultado_web
    else:
        contexto = "\n\n".join([p.page_content for p in pedacos_relevantes])

    prompt_final = f"""Você é um assistente de estudos. Ajude o aluno a PENSAR antes de dar a resposta pronta.

Contexto:
{contexto}

Pergunta: {pergunta_do_usuario}
"""

    resposta = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt_final, "stream": False}
    )
    return resposta.json()["response"]
```

**Um alerta importante:** pra baixar livros/arquivos específicos da internet, use sempre fontes legítimas — sites oficiais do Enem/INEP, domínio público, Wikipédia, apostilas abertas de cursinho. Evite sites de "livro pirata", que além de ilegal, geralmente têm texto de baixa qualidade (cheio de erro de OCR) que vai confundir sua IA.

---

## Fase 4: Corretor de redação + linha do tempo

### Código: `redacao.py`

```python
import requests
import json
from datetime import datetime
import os

ARQUIVO_HISTORICO = "historico_redacoes.json"

CRITERIOS_ENEM = """
As 5 competências do Enem, cada uma vale até 200 pontos (total 1000):
1. Domínio da norma culta da língua escrita
2. Compreender a proposta e aplicar conceitos de várias áreas do conhecimento
3. Selecionar e organizar informações, fatos e argumentos em defesa de um ponto de vista
4. Conhecimento dos mecanismos linguísticos para argumentação
5. Elaborar proposta de intervenção para o problema, respeitando os direitos humanos
"""

def corrigir_redacao(texto_redacao):
    prompt = f"""Você é um corretor de redações do Enem. Use estes critérios oficiais:
{CRITERIOS_ENEM}

Avalie a redação abaixo. Para cada competência, dê uma nota de 0 a 200 e uma explicação curta.
No final, some a nota total e dê 2-3 sugestões práticas de melhoria.

Redação:
{texto_redacao}
"""
    resposta = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt, "stream": False}
    )
    return resposta.json()["response"]

def salvar_redacao(texto_redacao, avaliacao):
    historico = []
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            historico = json.load(f)

    historico.append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "texto": texto_redacao,
        "avaliacao": avaliacao
    })

    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

def comparar_com_anterior(nova_avaliacao):
    if not os.path.exists(ARQUIVO_HISTORICO):
        return "Essa é sua primeira redação salva — sem comparação ainda."

    with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        historico = json.load(f)

    if len(historico) == 0:
        return "Essa é sua primeira redação salva — sem comparação ainda."

    anterior = historico[-1]["avaliacao"]

    prompt = f"""Compare estas duas avaliações de redação e diga, de forma direta e encorajadora,
o que melhorou e o que ainda precisa de atenção.

Avaliação anterior:
{anterior}

Avaliação nova:
{nova_avaliacao}
"""
    resposta = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt, "stream": False}
    )
    return resposta.json()["response"]
```

### Como usar

```python
from redacao import corrigir_redacao, salvar_redacao, comparar_com_anterior

texto = "cole aqui o texto da sua redação"

avaliacao = corrigir_redacao(texto)
print(avaliacao)

comparacao = comparar_com_anterior(avaliacao)
print(comparacao)

salvar_redacao(texto, avaliacao)
```

Isso cria um arquivo `historico_redacoes.json` na sua pasta — é ele que guarda toda sua evolução ao longo do tempo. Não mexe nesse arquivo na mão, deixa o código cuidar dele.

---

## Fase 5: Interface estilo Duolingo + Pomodoro

### Instalar

```
pip install streamlit streamlit-autorefresh
```

### Código: `app.py`

```python
import streamlit as st
import time
from streamlit_autorefresh import st_autorefresh
from biblioteca import buscar
from redacao import corrigir_redacao, salvar_redacao, comparar_com_anterior
import json, os

st.set_page_config(page_title="Minha IA de Estudos", page_icon="📚", layout="centered")

# Estilo visual básico (cores, botões arredondados)
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

# --- TELA INICIAL: botões tipo Duolingo ---
def tela_inicio():
    st.title("📚 Minha IA de Estudos")
    st.write("Escolha uma matéria pra começar:")

    colunas = st.columns(2)
    for i, materia in enumerate(MATERIAS):
        with colunas[i % 2]:
            if st.button(materia, use_container_width=True):
                st.session_state.materia_atual = materia.lower().replace(" ", "_")
                st.session_state.pagina = "chat"
                st.rerun()

    st.divider()
    if st.button("⏱️ Pomodoro"):
        st.session_state.pagina = "pomodoro"
        st.rerun()
    if st.button("📈 Linha do tempo"):
        st.session_state.pagina = "timeline"
        st.rerun()
    if st.button("✍️ Corrigir redação"):
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
        resposta = f"(Aqui entraria a resposta da IA usando o contexto: {contexto[:100]}...)"
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
        st_autorefresh(interval=1000, key="refresh_pomodoro")
        restante = int(st.session_state.pomodoro_fim - time.time())
        if restante <= 0:
            st.success("Tempo esgotado! Hora da pausa. 🎉")
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
        with st.spinner("Analisando..."):
            avaliacao = corrigir_redacao(texto)
            comparacao = comparar_com_anterior(avaliacao)
            salvar_redacao(texto, avaliacao)
        st.subheader("Avaliação")
        st.write(avaliacao)
        st.subheader("Comparação com a redação anterior")
        st.write(comparacao)

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
```

Roda com `streamlit run app.py`. Isso já te dá: tela inicial com botões de matéria, chat separado por matéria (com histórico guardado enquanto o app está aberto), Pomodoro funcional, corretor de redação e linha do tempo.

**Nota:** a linha `resposta = f"(Aqui entraria a resposta da IA...)"` no chat é um placeholder — depois a gente troca por uma chamada de verdade pro modelo, igual fizemos no `estudar.py`. Deixei assim pra você primeiro ver a interface funcionando, sem esperar o modelo responder toda hora enquanto ajusta o visual.

---

⚠️ Bugs Reais na Construção do app.py:1. O Erro da Gaveta com Acento (ChromaDB InvalidArgumentError)Quando clicamos no botão "Matemática", a tela quebrou. O código tentou criar a gaveta usando o acento no "á". O ChromaDB é gringo e só aceita nomes limpos.Solução: Na criação do botão da tela inicial, precisamos forçar a limpeza dos acentos antes de mandar pro banco.2. O Vácuo da IA (Placeholder Falso)
Quando perguntamos sobre "dízima periódica", a tela exibiu o texto (Aqui entraria a resposta da IA usando o contexto...) em vez da resposta de verdade. A busca no PDF funcionou, mas a resposta não.
Solução: Apagamos a linha falsa e colocamos a conexão real com o cérebro (requests.post) para ele gerar a resposta.  

## Fase 6: Virar um "app" de desktop

### Opção simples (atalho)
Cria um arquivo `abrir_app.bat` na pasta do projeto:

```bat
@echo off
call venv\Scripts\activate
streamlit run app.py
```

Clica duas vezes nesse arquivo e o app abre no navegador, sem precisar digitar comando nenhum. Já dá uma sensação de "programa instalado".

### Opção mais parecida com app de verdade (janela própria, sem navegador)

```
pip install pywebview
```

Cria `iniciar_app.py`:

```python
import webview
import subprocess
import time

processo = subprocess.Popen(["streamlit", "run", "app.py", "--server.headless", "true"])
time.sleep(3)  # espera o streamlit subir

webview.create_window("Minha IA de Estudos", "http://localhost:8501", width=1000, height=700)
webview.start()

processo.terminate()
```

Roda com `python iniciar_app.py` — isso abre numa janela própria, sem barra de navegador, do jeito mais parecido com um app instalado que dá pra fazer sem virar um projeto de meses.

---





## Resumo do que fazer, em ordem

- [ ] Criar `biblioteca.py` (Fase 2) e reorganizar seus PDFs já salvos por matéria
- [ ] Instalar e testar a busca na internet (Fase 3)
- [ ] Criar `redacao.py` e testar com uma redação sua (Fase 4)
- [ ] Montar o `app.py` (Fase 5) e ver a interface funcionando
- [ ] Trocar o placeholder do chat pela resposta real da IA
- [ ] Escolher entre atalho `.bat` ou janela com `pywebview` (Fase 6)

Vai testando fase por fase — não trava em fazer tudo perfeito de primeira, cada pedacinho funcionando já é vitória.
