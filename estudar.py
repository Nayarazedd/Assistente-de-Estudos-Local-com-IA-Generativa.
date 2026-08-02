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