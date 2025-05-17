import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image

# Carregar imagem corretamente
img = Image.open("Imagem/WhatsApp Image 2024-09-29 at 02.22.00.jpeg")

# Configurar página
st.set_page_config(page_title="PYGEOPLOT", page_icon=img, layout="wide")

# Mostrar logotipo
st.image(img, use_container_width=True, caption="PYGEOPLOT")

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

# Executar a página correspondente
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
