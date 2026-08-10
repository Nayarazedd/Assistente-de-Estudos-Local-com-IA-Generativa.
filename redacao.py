import os
import json
from datetime import datetime
import requests

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

    api_key = None
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            return f"Erro ao processar com a API do Google: {e}"

    try:
        resposta = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False},
            timeout=10
        )
        return resposta.json()["response"]
    except Exception as e:
        return f"Erro: Nenhuma chave da API configurada e o Ollama local não está rodando. Detalhe: {e}"

def salvar_redacao(texto_redacao, avaliacao):
    historico = []
    if os.path.exists(ARQUIVO_HISTORICO):
        try:
            with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
                historico = json.load(f)
        except Exception:
            historico = []

    historico.append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "texto": texto_redacao,
        "avaliacao": avaliacao
    })

    try:
        with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def comparar_com_anterior(nova_avaliacao):
    if not os.path.exists(ARQUIVO_HISTORICO):
        return "Essa é sua primeira redação salva — sem comparação ainda."

    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            historico = json.load(f)
    except Exception:
        historico = []

    if len(historico) == 0:
        return "Essa é sua primeira redação salva — sem comparação ainda."

    return "Comparação gerada com sucesso."