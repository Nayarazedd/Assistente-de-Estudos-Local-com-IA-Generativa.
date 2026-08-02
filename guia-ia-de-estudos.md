# Guia Completo: Construindo Sua IA de Estudos do Zero

> Este guia assume que você nunca programou antes. Cada passo é explicado como se fosse a primeira vez que você vê aquilo — porque provavelmente é.

---

## Parte 0: Entendendo as peças (antes de tocar no teclado)

Imagina que você quer montar um "aluno particular" que mora dentro do seu PC. Ele precisa de 4 coisas:

| Peça | O que faz | Analogia |
|---|---|---|
| **Python** | A linguagem que você usa pra dar instruções pro computador | O idioma que você fala com o computador |
| **LLM (modelo de IA)** | O "cérebro" que entende texto e gera respostas | O professor que sabe conversar |
| **Embeddings + ChromaDB** | Guarda o conteúdo que você estudou, organizado por "significado" | Um fichário mágico que organiza por assunto, não por ordem alfabética |
| **RAG** (Retrieval-Augmented Generation) | Buscar o pedaço certo no fichário → entregar pro professor → ele responde usando aquilo | O professor consultando as anotações antes de responder, em vez de "chutar" de memória |

**Por que isso funciona sem internet:** o professor (LLM) e o fichário (ChromaDB) moram no seu HD, não em um servidor da OpenAI ou Google. Uma vez instalado, você pode desligar o roteador de casa que continua funcionando — porque nada disso sai do seu computador.

---

## Parte 1: Preparando o terreno

### 1.1 — Instalar o Python

1. Vai em **python.org/downloads**
2. Clica no botão amarelo grande de download (ele já detecta que você tá no Windows)
3. Abre o instalador
4. **PASSO MAIS IMPORTANTE:** na primeira tela do instalador, tem uma caixinha escrito **"Add python.exe to PATH"** lá embaixo. **MARCA ELA** antes de clicar em instalar. (Esse é o erro nº1 de quem instala Python e depois "não funciona")
5. Clica em "Install Now"
6. Espera terminar

**Como confirmar que funcionou:**
1. Aperta a tecla Windows, digita `cmd`, aperta Enter (abre o Prompt de Comando — uma telinha preta onde você digita comandos)
2. Digita: `python --version`
3. Se aparecer algo tipo `Python 3.12.x`, deu certo!

### 1.2 — Criar a pasta do seu projeto

No Prompt de Comando (mesma telinha preta), digita cada linha, uma de cada vez, apertando Enter depois de cada uma:

```
cd Desktop
mkdir ia-de-estudos
cd ia-de-estudos
```

O que isso faz: `cd Desktop` entra na pasta da sua Área de Trabalho. `mkdir ia-de-estudos` cria uma pasta nova chamada "ia-de-estudos". `cd ia-de-estudos` entra dentro dela. Agora tudo que você fizer vai ficar organizado ali.

### 1.3 — Criar um "ambiente virtual" (venv)

Ainda no Prompt de Comando, dentro da pasta `ia-de-estudos`:

```
python -m venv venv
venv\Scripts\activate
```

**Por que fazer isso:** imagina que cada projeto de programação precisa de "ingredientes" (bibliotecas) diferentes. Se você misturar tudo num só lugar, um projeto pode bagunçar o outro. O `venv` é como ter uma bancada de cozinha separada só pra esse projeto — os ingredientes daqui não bagunçam nada de fora.

Depois de rodar o segundo comando, você vai ver `(venv)` aparecer no início da linha do Prompt. Isso significa que o ambiente tá "ativado" — é assim que você sabe que tá no lugar certo.

**Atenção:** toda vez que você abrir o Prompt de novo pra trabalhar nesse projeto, precisa rodar `venv\Scripts\activate` de novo (só esse comando, não precisa criar o venv de novo).

### 1.4 — Confirmar que o Ollama tá funcionando

Você já tem experiência com LLMs locais, então confirma que o Ollama tá instalado e com um modelo baixado:

```
ollama list
```

Se não aparecer nenhum modelo, baixa um:

```
ollama pull mistral
```

(Isso baixa o modelo Mistral 7B — pode demorar uns minutos dependendo da internet, só essa parte do processo precisa de internet, o download inicial)

---

## Parte 2: Seu primeiro "oi, mundo" com IA

Vamos criar o primeiro arquivo. No Prompt de Comando (com `venv` ativado), digita:

```
notepad primeiro_teste.py
```

Isso abre o Bloco de Notas com um arquivo novo chamado `primeiro_teste.py`. Cola isso dentro:

```python
import requests

resposta = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "mistral",
        "prompt": "Explique o que é fotossíntese em 2 frases simples.",
        "stream": False
    }
)

print(resposta.json()["response"])
```


⚠️ Nota do Coreção (Erro Real na Prática):
Quando fomos rodar isso, deu um erro de "comando não reconhecido". Isso aconteceu porque tentamos colar o código import requests direto na tela preta do Windows. O terminal não entende código de Python solto. A regra de ouro é: os códigos a gente escreve e salva dentro do arquivo .py. No terminal (a tela preta), a gente SÓ manda o comando pra rodar o arquivo (ex: python nome_do_arquivo.py).


**O que cada linha faz:**
- `import requests` — pega uma "ferramenta" pronta pra conversar com o Ollama
- `requests.post(...)` — manda uma pergunta pro Ollama, que tá rodando na sua máquina
- `"model": "mistral"` — diz qual "professor" (modelo) você quer usar
- `"prompt": "..."` — a pergunta que você quer fazer
- `print(...)` — mostra a resposta na tela

Salva o arquivo (Ctrl+S) e fecha o Bloco de Notas. Antes de rodar, instala a ferramenta `requests`:

```
pip install requests
```

Agora roda o script:

```
python primeiro_teste.py
```

Se aparecer uma explicação sobre fotossíntese, **funcionou** — você acabou de fazer sua IA local responder pra você, com código escrito por você.

---

## Parte 3: Dando "memória de estudo" pro sistema (RAG)

Agora vem a parte que transforma isso de "chat comum" em "assistente de estudos".

### 3.1 — Instalar as bibliotecas necessárias

```
pip install chromadb pypdf langchain langchain-community
```

O que cada uma faz:
- `chromadb` — o "fichário mágico" que guarda o conteúdo organizado
- `pypdf` — lê arquivos PDF e extrai o texto
- `langchain` e `langchain-community` — ferramentas prontas que facilitam juntar as peças (ler PDF, quebrar em pedaços, conectar no Ollama)

### 3.2 — Ler um PDF e quebrar em pedaços

Pega qualquer PDF de estudo (um resumo de história, por exemplo) e coloca na pasta `ia-de-estudos`. Vamos chamar de `material.pdf` no exemplo.

Cria um novo arquivo `carregar_material.py`:

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1. Lê o PDF
loader = PyPDFLoader("material.pdf")
paginas = loader.load()

# 2. Quebra o texto em pedaços menores (chunks)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # cada pedaço tem no máximo 500 caracteres
    chunk_overlap=50     # os pedaços se sobrepõem um pouco, pra não cortar uma ideia no meio
)
pedacos = splitter.split_documents(paginas)

print(f"O material foi dividido em {len(pedacos)} pedaços.")
```

⚠️ Nota do Correção (Erro Real na Prática):O código original do Claude dizia pra importar o fatiador de texto assim: from langchain.text_splitter.... Quando rodamos, tomamos um erro na cara: ModuleNotFoundError. A biblioteca foi atualizada e os criadores mudaram a ferramenta de lugar. Tivemos que instalar uma extensão nova (pip install -U langchain-text-splitters) e usar a linha de código nova (que eu já deixei atualizada ali em cima) pra máquina conseguir ler.Por que quebrar em pedaços: se você jogasse o PDF inteiro pro modelo de uma vez, ele teria dificuldade de achar a parte relevante — é como procurar uma frase específica dentro de um livro de 300 páginas sem índice. Quebrando em pedaços pequenos, fica mais fácil achar exatamente o trecho que responde sua pergunta.  


**Por que quebrar em pedaços:** se você jogasse o PDF inteiro pro modelo de uma vez, ele teria dificuldade de achar a parte relevante — é como procurar uma frase específica dentro de um livro de 300 páginas sem índice. Quebrando em pedaços pequenos, fica mais fácil achar exatamente o trecho que responde sua pergunta.

### 3.3 — Transformar pedaços em embeddings e guardar no ChromaDB

Continuando no mesmo arquivo (ou em um novo, `criar_banco.py`):

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# Cria os "embeddings" (a tradução de texto em números que representam significado)
embeddings = OllamaEmbeddings(model="mistral")

# Guarda os pedaços no banco vetorial (ChromaDB), salvando numa pasta local
banco = Chroma.from_documents(
    documents=pedacos,
    embedding=embeddings,
    persist_directory="./banco_de_estudos"
)

print("Material guardado no banco de estudos!")
```

⚠️ Nota do Correção (Erro Real na Prática):
O roteiro original mandou usar o mistral para fazer a organização (embeddings). Quando botamos pra fatiar aquele livro de matemática de 8MB, o PC chorou e cuspiu o Erro 500. O Mistral é ótimo para conversar, mas ruim pra organizar as gavetas. A gente resolveu isso trocando ali em cima o model="mistral" por model="nomic-embed-text", que é um cérebro específico e leve feito SÓ pra essa função de fatiar arquivos. E atenção redobrada nos nomes de arquivos! Ao chamar pastas, escreva exatamente igual: um "Biblioteca.py" escrito com 'B' maiúsculo já derrubou nosso sistema inteiro, exigindo renomeação pro código funcionar.


**O que é embedding, de verdade:** imagina que cada frase vira um conjunto de coordenadas num "mapa de significados". Frases parecidas ficam pertinho uma da outra nesse mapa, mesmo que usem palavras diferentes. É assim que o sistema acha "o pedaço certo" mesmo que sua pergunta não use as palavras exatas do texto.

Essa pasta `banco_de_estudos` que é criada guarda tudo isso **no seu HD** — de novo, sem depender de internet depois de criada.

### 3.4 — Buscar os pedaços relevantes quando você faz uma pergunta

```python
pergunta = "O que causou a Primeira Guerra Mundial?"

resultados = banco.similarity_search(pergunta, k=3)  # busca os 3 pedaços mais relevantes

for pedaco in resultados:
    print(pedaco.page_content)
    print("---")
```

Isso já mostra na tela os 3 trechos do seu PDF mais relacionados à pergunta.

---

## Parte 4: Juntando tudo — pergunta + busca + resposta

Agora o fluxo completo, em um arquivo `estudar.py`:

```python
import requests
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# Carrega o banco que você já criou
embeddings = OllamaEmbeddings(model="mistral")
banco = Chroma(persist_directory="./banco_de_estudos", embedding_function=embeddings)

def perguntar(pergunta_do_usuario):
    # 1. Busca os pedaços relevantes no material
    pedacos_relevantes = banco.similarity_search(pergunta_do_usuario, k=3)
    contexto = "\n\n".join([p.page_content for p in pedacos_relevantes])

    # 2. Monta o prompt final, juntando o contexto + a pergunta
    prompt_final = f"""Use o contexto abaixo para responder a pergunta.
Se a resposta não estiver no contexto, diga que não sabe.

Contexto:
{contexto}

Pergunta: {pergunta_do_usuario}
"""

    # 3. Manda pro modelo e pega a resposta
    resposta = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt_final, "stream": False}
    )
    return resposta.json()["response"]

# Testando
pergunta = input("O que você quer estudar hoje? ")
print(perguntar(pergunta))
```

Roda com `python estudar.py` — agora você tem um sistema que responde baseado **no seu material**, não em conhecimento genérico da internet.

---

## Parte 5: A parte pedagógica (o que te diferencia)

Lembra que você não quer que ele só "dê a resposta pronta"? Ajusta o prompt assim:

```python
    prompt_final = f"""Você é um assistente de estudos. Seu objetivo é ajudar o aluno a PENSAR, não dar respostas prontas direto.

Contexto do material:
{contexto}

Regras:
1. Antes de responder, faça UMA pergunta simples sobre o assunto pra testar o que o aluno já entende
2. Espere a resposta dele (nesta conversa, você vai simular isso perguntando primeiro)
3. Só depois de uma tentativa, explique o conceito de forma clara e curta

Pergunta original do aluno: {pergunta_do_usuario}
"""
```

Isso muda o comportamento: em vez de "aqui está a resposta", ele primeiro te desafia a tentar. É essa lógica que vira seu diferencial de portfólio — mostra que você pensou em pedagogia, não só em "chatbot que responde".

---

## Parte 6: Uma interface de verdade (Streamlit)

Linha de comando funciona, mas fica bonito ter uma telinha. O **Streamlit** é a ferramenta mais fácil pra isso, iniciante-friendly:

```
pip install streamlit
```

Cria `app.py`:

```python
import streamlit as st
from estudar import perguntar  # reaproveitando a função que você já criou

st.title("Minha IA de Estudos")

pergunta = st.text_input("O que você quer estudar hoje?")

if pergunta:
    with st.spinner("Pensando..."):
        resposta = perguntar(pergunta)
    st.write(resposta)
```

Roda com:

```
streamlit run app.py
```

Isso abre uma página no seu navegador, local (sem internet), com uma interface de verdade — caixa de texto, botão, resposta na tela. Isso já é "printável" pro portfólio.

---

## Parte 7: Por que isso resolve o problema da internet cair

Repara: o Ollama roda no seu PC. O ChromaDB fica salvo numa pasta no seu PC. O Streamlit abre no seu navegador, mas processado localmente. **Nada disso depende do Wi-Fi de casa** — uma vez que você instalou tudo (isso sim precisa de internet, só na hora de baixar), pode desligar o roteador e o sistema continua funcionando 100%.

Isso é diferente de usar ChatGPT ou Gemini direto, que exigem internet toda vez. É exatamente por isso que a abordagem local que a gente escolheu faz sentido pro seu caso.

---

## Próximos passos (depois que isso tudo estiver funcionando)

1. **Testar com material real do Enem** — troca o `material.pdf` por um resumo de matéria que você estuda
2. **Git e GitHub** — aprender a salvar seu código lá, pra virar portfólio de verdade
3. **Celular/mobile** — fase futura, dá pra explorar depois que a versão do PC estiver redonda

---

## Resumo do que fazer, em ordem

- [ ] Instalar Python (marcando "Add to PATH")
- [ ] Criar a pasta do projeto + venv
- [ ] Confirmar Ollama com um modelo baixado
- [ ] Rodar o "oi, mundo" (Parte 2)
- [ ] Instalar bibliotecas de RAG (Parte 3.1)
- [ ] Carregar um PDF de teste e criar o banco (Parte 3.2 a 3.4)
- [ ] Juntar tudo no `estudar.py` (Parte 4)
- [ ] Ajustar o prompt pedagógico (Parte 5)
- [ ] Criar a interface com Streamlit (Parte 6)
