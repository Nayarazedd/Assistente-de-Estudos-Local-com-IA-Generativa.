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