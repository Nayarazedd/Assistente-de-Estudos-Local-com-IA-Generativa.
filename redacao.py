import requests
import json
from datetime import datetime
import os

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
    resposta = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt, "stream": False}
    )
    return resposta.json()["response"]

def salvar_redacao(texto_redacao, avaliacao):
    historico = []
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            historico = json.load(f)

    historico.append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "texto": texto_redacao,
        "avaliacao": avaliacao
    })

    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

def comparar_com_anterior(nova_avaliacao):
    if not os.path.exists(ARQUIVO_HISTORICO):
        return "Essa é sua primeira redação salva — sem comparação ainda."

    with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        historico = json.load(f)

    if len(historico) == 0:
        return "Essa é sua primeira redação salva — sem comparação ainda."

    anterior = historico[-1]["avaliacao"]

    prompt = f"""Compare estas duas avaliações de redação e diga, de forma direta e encorajadora,
o que melhorou e o que ainda precisa de atenção.

Avaliação anterior:
{anterior}

Avaliação nova:
{nova_avaliacao}
"""
    resposta = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt, "stream": False}
    )
    return resposta.json()["response"]