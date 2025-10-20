import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import importlib

# Configurar página
st.set_page_config(page_title="PYGEOPLOT", page_icon="Imagem/WhatsApp Image 2024-09-29 at 02.22.00.jpeg", layout="wide")

# Adicionar imagem de fundo
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

img_base64 = get_base64_image("Imagem/02.jpg")

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

# Logo no sidebar
with st.sidebar:
    st.image("Imagem/WhatsApp Image 2024-09-29 at 02.22.00.jpeg")

# Menu horizontal no header
escolha = option_menu(
    None,
    [
        "Home",
        "Importação",
        "Visualização",
        "Estatísticas",
        "Classificação Litológica",
        "Cálculo Petrofísico",
        "Conversão de Dados",
        "Autor do Aplicativo"
    ],
    icons=[
        "house", "cloud-upload", "eye", "graph-up", "bar-chart", "calculator", "shuffle", "info-circle"
    ],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "14px"},
        "nav-link": {
            "font-size": "14px",
            "text-align": "center",
            "margin": "0px",
            "padding": "8px 12px",
            "--hover-color": "#eee"
        },
        "nav-link-selected": {"background-color": "#02ab21"},
    }
)

# Roteamento
if escolha == "Home":
    # Informações na sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📌 Informações")

        st.markdown("""
        <div style='background-color: #f0f8ff; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
            <h4 style='color: #02ab21; margin: 0;'>Bem-vindo!</h4>
            <p style='font-size: 13px; margin: 5px 0 0 0;'>
                Sistema completo para análise de diagrafia de poços petrolíferos.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🚀 Início Rápido")
        st.markdown("""
        1. **Importar** arquivo LAS
        2. **Visualizar** perfis
        3. **Analisar** dados
        4. **Classificar** litologias
        5. **Calcular** propriedades
        """)

        st.markdown("---")

        st.markdown("#### 📊 Capacidades")
        st.markdown("""
        - ✓ Arquivos LAS compatíveis
        - ✓ Gráficos interativos
        - ✓ Estatísticas avançadas
        - ✓ Machine Learning
        - ✓ Exportação de dados
        """)

        st.markdown("---")

        st.info("💡 **Dica:** Comece importando um arquivo LAS na aba 'Importação'")

    # Página de boas-vindas
    st.markdown("""
    <div style='text-align: center; padding: 5px 0;'>
        <h2 style='color: #02ab21; font-size: 28px; margin-bottom: 5px;'>Bem-vindo ao PYGEOPLOT</h2>
        <p style='font-size: 14px; color: #666; margin-top: 0;'>Plataforma Avançada de Análise de Diagrafia de Poços</p>
    </div>
    """, unsafe_allow_html=True)

    # Cards de funcionalidades
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style='background-color: #f0f8ff; padding: 10px; border-radius: 8px; text-align: center;'>
            <h4 style='color: #02ab21; font-size: 14px; margin: 5px 0;'>📁 Importação</h4>
            <p style='font-size: 12px; margin: 5px 0;'>Carregue arquivos LAS de forma rápida e segura</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background-color: #fff8f0; padding: 10px; border-radius: 8px; text-align: center;'>
            <h4 style='color: #ff8c00; font-size: 14px; margin: 5px 0;'>📊 Visualização</h4>
            <p style='font-size: 12px; margin: 5px 0;'>Gráficos interativos de alta qualidade</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='background-color: #f0fff0; padding: 10px; border-radius: 8px; text-align: center;'>
            <h4 style='color: #008b8b; font-size: 14px; margin: 5px 0;'>📈 Análise</h4>
            <p style='font-size: 12px; margin: 5px 0;'>Estatísticas e cálculos petrofísicos avançados</p>
        </div>
        """, unsafe_allow_html=True)

    # Exemplo de visualização - Pairplot
    st.markdown("### 📊 Matriz de Correlação - Pairplot")

    # Criar dados de exemplo para diferentes litologias
    import numpy as np
    import pandas as pd
    import seaborn as sns

    np.random.seed(42)

    # Gerar dados sintéticos para diferentes litologias
    n_samples = 100

    # Arenito
    arenito = pd.DataFrame({
        'GR': np.random.normal(45, 10, n_samples),
        'Densidade': np.random.normal(2.35, 0.08, n_samples),
        'Neutrão': np.random.normal(0.22, 0.05, n_samples),
        'Resistividade': np.random.normal(25, 8, n_samples),
        'Litologia': 'Arenito'
    })

    # Folhelho
    folhelho = pd.DataFrame({
        'GR': np.random.normal(95, 15, n_samples),
        'Densidade': np.random.normal(2.55, 0.07, n_samples),
        'Neutrão': np.random.normal(0.35, 0.06, n_samples),
        'Resistividade': np.random.normal(8, 3, n_samples),
        'Litologia': 'Folhelho'
    })

    # Calcário
    calcario = pd.DataFrame({
        'GR': np.random.normal(30, 8, n_samples),
        'Densidade': np.random.normal(2.71, 0.06, n_samples),
        'Neutrão': np.random.normal(0.08, 0.03, n_samples),
        'Resistividade': np.random.normal(45, 12, n_samples),
        'Litologia': 'Calcário'
    })

    # Combinar todos os dados
    df_lito = pd.concat([arenito, folhelho, calcario], ignore_index=True)

    # Criar Pairplot
    colors = {'Arenito': '#FFD700', 'Folhelho': '#8B4513', 'Calcário': '#87CEEB'}

    sns.set_style("whitegrid")
    pairplot_fig = sns.pairplot(df_lito, hue='Litologia',
                                palette=colors,
                                diag_kind='kde',
                                plot_kws={'alpha': 0.6, 's': 30, 'edgecolor': 'black', 'linewidth': 0.5},
                                diag_kws={'alpha': 0.7, 'linewidth': 2})
    pairplot_fig.figure.suptitle('Análise Multivariada de Litologias', y=1.01, fontsize=16, fontweight='bold')
    st.pyplot(pairplot_fig)

    # Informações adicionais
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total de Amostras", f"{len(df_lito)}")
    with col2:
        st.metric("Litologias Identificadas", "3")
    with col3:
        st.metric("Parâmetros Analisados", "4")

elif escolha == "Importação":
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
