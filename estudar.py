from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
import ollama

def perguntar(pergunta_do_usuario):
    # Prepara o motor levinho pra ler a memória
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    banco = Chroma(persist_directory="./banco_de_estudos", embedding_function=embeddings)

    # Puxa os pedaços do livro de matemática
    resultados = banco.similarity_search(pergunta_do_usuario, k=3)
    contexto = "\n".join([doc.page_content for doc in resultados])

    # A regra pedagógica que você queria
    prompt_final = f"""Você é um assistente de estudos. Seu objetivo é ajudar o aluno a PENSAR, não dar respostas prontas direto.
    Contexto do material:
    {contexto}

    Regras:
    1. Antes de responder, faça UMA pergunta simples sobre o assunto pra testar o que o aluno já entende
    2. Espere a resposta dele
    3. Só depois de uma tentativa, explique o conceito de forma clara e curta

    Pergunta original do aluno: {pergunta_do_usuario}"""

    # Manda pro cérebro grande (Mistral) e devolve a resposta pro site
    resposta = ollama.generate(model="mistral", prompt=prompt_final)
    return resposta["response"]