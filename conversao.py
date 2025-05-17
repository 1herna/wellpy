import streamlit as st
import pandas as pd
import lasio

def app():
    # Verifica se os dados de poço (LAS) estão carregados na sessão
    if 'well_data' in st.session_state:
        st.title('Conversão de Dados: LAS para CSV')

        # Carregar dados LAS da sessão
        las_data = st.session_state['well_data']
        st.write("Prévia dos Dados LAS:")
        st.write(las_data.head())  # Exibir uma prévia dos dados

        # Input para o nome do arquivo CSV a ser salvo
        csv_filename = st.text_input("Nome do arquivo CSV para salvar", "output.csv")

        if st.button("Converter para CSV"):
            # Salvar os dados como CSV
            las_data.to_csv(csv_filename, index=False)
            st.success(f"Arquivo CSV salvo como {csv_filename}")

            # Oferecer o download do arquivo CSV
            with open(csv_filename, "rb") as file:
                st.download_button(label="Baixar arquivo CSV", data=file, file_name=csv_filename)

    else:
        st.error("Nenhum dado LAS carregado. Por favor, vá para a página de importação para carregar os dados.")
