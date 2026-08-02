# Assistente-de-Estudos-Local-com-IA-Generativa.
Projeto pessoal de Assistente de estudos.

# Meu Assistente de Estudos com I.A. (RAG Local)

## O que é esse projeto?
Criei uma inteligência artificial local que lê meus PDFs de estudo e me ajuda a pensar. Em vez de me dar respostas prontas de mão beijada, o sistema age como um professor: ele analisa o material, me faz uma pergunta para testar meu conhecimento e, só depois que eu tento responder, ele me explica o conceito.

## Para que serve cada peça que eu usei (Meu mapa mental):
*   **Python:** A linguagem base. O chassi do carro onde eu montei toda a estrutura.
*   **Ollama:** O motor que me permite rodar os modelos de I.A. pesados na minha própria máquina, sem depender de nuvem ou internet.
*   **Mistral:** O "cérebro" principal. É a I.A. que realmente conversa comigo e entende o contexto.
*   **Nomic-Embed-Text:** O "cérebro" leve e organizador. Ele não fala, só serve pra transformar as palavras do meu PDF em números pra I.A. conseguir ler rápido.
*   **Langchain:** O maestro da porra toda. É a ferramenta que pega o meu PDF, conecta com o banco de dados e faz a ponte até a I.A.
*   **ChromaDB:** A gaveta de arquivos (banco de dados vetorial). É onde os pedaços fatiados do meu PDF ficam guardados organizados pra I.A. achar rápido quando eu faço uma pergunta.
*   **Streamlit:** A interface. O que transformou minha tela preta de código (terminal) num aplicativo visual no navegador.

## Como eu rodo isso na minha máquina:
1. Ativo meu ambiente virtual (a bolha de proteção do projeto).
2. O sistema fatia meus PDFs e salva no ChromaDB.
3. O Langchain busca a informação exata no banco de dados.
4. O Mistral lê o prompt que eu criei com a regra pedagógica.
5. Eu subo a tela visual rodando o comando: `python -m streamlit run app.py`

*Status do Projeto: Motor local finalizado. Próximo passo será o deploy (colocar na nuvem) usando o Render.*
