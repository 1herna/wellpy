import streamlit as st
import os
from streamlit_option_menu import option_menu

# Configuração do ícone e título da aplicação
image_path = os.path.join(os.path.dirname(__file__), "Imagem", "WhatsApp Image 2024-09-29 at 02.22.00.jpeg")
st.set_page_config(page_title="PYGEOPLOT", page_icon=image_path, layout="wide")

# Menu lateral
with st.sidebar:
    escolha = option_menu(
        "Menu Principal",
        [
            "Importação",
            "Visualização",
            "Estatísticas",
            "Classificação Litológica",
            "Cálculo Petrofísico",
            "Conversão de Dados",
            "Autor do Aplicativo"
        ],
        icons=[
            "cloud-upload",     # Importação
            "eye",              # Visualização
            "graph-up",         # Estatísticas
            "bar-chart",        # Classificação
            "calculator",       # Cálculo petrofísico
            "shuffle",          # Conversão
            "info-circle"       # Autor
        ],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
    )
    st.image(image_path, use_column_width=True, caption="PYGEOPLOT")

# Navegação entre páginas
if escolha == "Importação":
    import importacao
    importacao.app()

elif escolha == "Visualização":
    import Plotagem
    Plotagem.app()

elif escolha == "Estatísticas":
    import estatistica
    estatistica.app()

elif escolha == "Classificação Litológica":
    import litofaceis
    litofaceis.app()

elif escolha == "Cálculo Petrofísico":
    import calculopetrofisico
    calculopetrofisico.app()

elif escolha == "Conversão de Dados":
    import conversao
    conversao.app()

elif escolha == "Autor do Aplicativo":
    import autores
    autores.app()
