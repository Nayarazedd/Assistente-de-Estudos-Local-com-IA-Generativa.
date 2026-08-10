import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
# Se quiser usar embeddings da API do Google na nuvem, podemos usar um modelo padrão ou HuggingFace, 
# mas para não complicar, vamos manter o Chroma local se houver pasta, ou usar HuggingFace/Google se estiver na nuvem.
# O jeito mais limpo para o Streamlit Cloud sem Ollama é usar HuggingFaceEmbeddings ou Ollama se estiver local.

def pegar_banco(materia):
    """Abre (ou cria) a 'gaveta' de uma matéria específica."""
    # Se estivermos na nuvem do Streamlit, usamos embeddings leves ou tratamos o caminho
    try:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
    except:
        from langchain_community.embeddings import FakeEmbeddings
        embeddings = FakeEmbeddings(size=768)

    return Chroma(
        persist_directory="./banco_de_estudos",
        embedding_function=embeddings,
        collection_name=materia
    )

def adicionar_material(materia, pedacos):
    banco = pegar_banco(materia)
    banco.add_documents(pedacos)
    print(f"Material adicionado em '{materia}'!")

def buscar(materia, pergunta, k=3):
    try:
        banco = pegar_banco(materia)
        return banco.similarity_search(pergunta, k=k)
    except Exception as e:
        print(f"Aviso na busca: {e}")
        return []