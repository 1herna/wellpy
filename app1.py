import streamlit as st
import os
from streamlit_option_menu import option_menu

# Caminho do ícone
image_path = os.path.join(os.path.dirname(__file__), "Imagem", "logo.jpeg")

# Configuração da página
st.set_page_config(page_title="PYGEOPLOT", page_icon=image_path, layout="wide")

# Exibe a imagem no topo
st.image(image_path, use_container_width=True, caption="PYGEOPLOT")

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
    )

# Importa e executa o módulo correspondente
if escolha == "Importação":
    import importacao
    importacao.app()

elif escolha == "Visualização":
    import visualizacao
    visualizacao.app()

elif escolha == "Estatísticas":
    import estatistica
    estatistica.app()

elif escolha == "Classificação Litológica":
    import classificacao
    classificacao.app()

elif escolha == "Cálculo Petrofísico":
    import calculopetrofisico
    calculopetrofisico.app()

elif escolha == "Conversão de Dados":
    import conversao
    conversao.app()

elif escolha == "Autor do Aplicativo":
    import autor
    autor.app()
