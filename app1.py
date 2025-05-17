import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import importlib

# Configurar página
st.set_page_config(page_title="PYGEOPLOT", page_icon="Imagem/WhatsApp Image 2024-09-29 at 02.22.00.jpeg", layout="wide")

# Barra lateral com logo e menu
with st.sidebar:
    st.image("Imagem/WhatsApp Image 2024-09-29 at 02.22.00.jpeg", use_container_width=True)

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
            "cloud-upload", "eye", "graph-up", "bar-chart", "calculator", "shuffle", "info-circle"
        ],
        menu_icon="cast",
        default_index=0,
    )

# Roteamento
if escolha == "Importação":
    import importacao
    importlib.reload(importacao)
    importacao.app()

elif escolha == "Visualização":
    import Plotagem
    importlib.reload(Plotagem)
    Plotagem.app()

elif escolha == "Estatísticas":
    import estatistica
    importlib.reload(estatistica)
    estatistica.app()

elif escolha == "Classificação Litológica":
    import litofaceis
    importlib.reload(litofaceis)
    litofaceis.app()

elif escolha == "Cálculo Petrofísico":
    import calculopetrofisico
    importlib.reload(calculopetrofisico)
    calculopetrofisico.app()

elif escolha == "Conversão de Dados":
    import conversao
    importlib.reload(conversao)
    conversao.app()

elif escolha == "Autor do Aplicativo":
    import autores
    importlib.reload(autores)
    autores.app()
