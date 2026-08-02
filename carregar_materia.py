from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from biblioteca import adicionar_material

loader = PyPDFLoader("resumo_matematica.pdf")
paginas = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
pedacos = splitter.split_documents(paginas)

adicionar_material("matematica", pedacos)   # <- nome da gaveta