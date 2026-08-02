from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")
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