import streamlit as st
from estudar import perguntar  # reaproveitando a função que você já criou

st.title("Minha IA de Estudos")

pergunta = st.text_input("O que você quer estudar hoje?")

if pergunta:
    with st.spinner("Pensando..."):
        resposta = perguntar(pergunta)
    st.write(resposta)