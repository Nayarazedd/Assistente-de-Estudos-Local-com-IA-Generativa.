from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

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