from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# 1. Lê o PDF
print("Lendo o livro e cortando o texto...")
loader = PyPDFLoader("material.pdf")
paginas = loader.load()

# 2. Quebra o texto
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
pedacos = splitter.split_documents(paginas)
print(f"Pronto! O material foi dividido em {len(pedacos)} pedaços.")

# 3. Prepara o motor leve
print("Criando o banco de dados da memória... (Alimentando aos poucos pra não engasgar o PC)")
embeddings = OllamaEmbeddings(model="nomic-embed-text")
banco = Chroma(persist_directory="./banco_de_estudos", embedding_function=embeddings)

# 4. Salva de 100 em 100
for i in range(0, len(pedacos), 100):
    lote = pedacos[i:i+100]
    banco.add_documents(lote)
    print(f"Mastigando pedaços do {i} até {i+len(lote)}... Segura a onda.")

print("Material guardado no banco de estudos com sucesso, caralho!")