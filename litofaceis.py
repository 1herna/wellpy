import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.utils import resample

def get_depth_column(data):
    for col in ['DEPTH', 'DEPT', 'MD']:
        if col in data.columns:
            return col
    return None

def app():
    st.title('Classificação Litológica por Eletrofácies')

    st.markdown("""
    ### 🧠 Sobre a Classificação Litológica por Eletrofácies

    Este módulo realiza uma **classificação automática da litologia** com base nos perfis geofísicos (como gama-ray), utilizando o algoritmo de **K-Means**, que é um método de **agrupamento não supervisionado**.

    O K-Means agrupa os dados em **zonas com características semelhantes**, chamadas aqui de **litofácies**. Isso é especialmente útil quando **não se tem rótulos verdadeiros** (ex: nomes de litologias reais), permitindo a **identificação de padrões escondidos** nos dados.

    O número de grupos (clusters) é determinado automaticamente com base na **métrica de Silhouette Score**, que avalia a qualidade da separação dos dados.

    O resultado é apresentado na forma de uma **coluna litológica vertical**, semelhante às utilizadas em softwares como Techlog ou Strater.

    ⚠️ Importante: esta é uma **classificação estatística** e **não substitui uma interpretação geológica** — mas serve como ferramenta exploratória poderosa.
    """)

    # Verificação dos dados
    if 'well_data' not in st.session_state:
        st.warning("⚠️ Nenhum dado carregado. Vá até a aba de Importação.")
        return

    data = st.session_state['well_data']

    # Detectar a coluna de profundidade
    depth_col = get_depth_column(data)
    if not depth_col:
        st.error("❌ Coluna de profundidade não encontrada.")
        return
    st.success(f"📏 Coluna de profundidade identificada: `{depth_col}`")

    # Seleção da curva
    colunas_disponiveis = [col for col in data.columns if col != depth_col]
    if not colunas_disponiveis:
        st.warning("Nenhuma curva disponível para classificação.")
        return

    log_col = st.selectbox("Selecione a curva para classificar:", colunas_disponiveis)

    # Limpar dados sem alterar o original
    data_clean = data.dropna(subset=[log_col]).copy()
    if len(data_clean) < 2:
        st.warning("Poucos dados disponíveis após limpeza.")
        return

    X = data_clean[[log_col]].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Determinar melhor número de clusters usando amostragem
    melhor_k, melhor_score, melhor_kmeans = 2, -1, None
    for k in range(2, 8):
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(X_scaled)
        amostra_X, amostra_labels = resample(X_scaled, labels, n_samples=min(1000, len(X_scaled)), random_state=42)
        score = silhouette_score(amostra_X, amostra_labels)
        if score > melhor_score:
            melhor_k, melhor_score, melhor_kmeans = k, score, kmeans

    st.info(f"🔢 Clusters ideais: **{melhor_k}** (Silhouette Score estimado: {melhor_score:.3f})")

    # Aplicar modelo final
    data_clean['Cluster'] = melhor_kmeans.predict(X_scaled)
    data_clean['Litologia'] = data_clean['Cluster'].apply(lambda x: f"Litofácies {x+1}")

    # Cores para as litologias
    cores_disponiveis = ['#FFD700', '#8B4513', '#D3D3D3', '#98FB98', '#1E90FF', '#FF6347', '#9932CC']
    litologias = sorted(data_clean['Litologia'].unique())
    cores = {lit: cores_disponiveis[i % len(cores_disponiveis)] for i, lit in enumerate(litologias)}

    # Agrupar intervalos contínuos
    intervalos = []
    prev_lit = data_clean['Litologia'].iloc[0]
    start_depth = data_clean[depth_col].iloc[0]

    for i in range(1, len(data_clean)):
        curr_lit = data_clean['Litologia'].iloc[i]
        curr_depth = data_clean[depth_col].iloc[i]
        if curr_lit != prev_lit:
            intervalos.append({'topo': start_depth, 'base': curr_depth, 'litologia': prev_lit})
            start_depth = curr_depth
            prev_lit = curr_lit

    intervalos.append({
        'topo': start_depth,
        'base': data_clean[depth_col].iloc[-1],
        'litologia': prev_lit
    })

    # Plotagem da coluna litológica
    st.subheader("📊 Coluna Litológica")
    fig, ax = plt.subplots(figsize=(3, 15))
    for intervalo in intervalos:
        topo = intervalo['topo']
        base = intervalo['base']
        lit = intervalo['litologia']
        if lit not in cores:
            cores[lit] = '#E0E0E0'  # Cor clara padrão
        cor = cores[lit]
        altura = base - topo
        bloco = patches.Rectangle((0, topo), 1, altura, facecolor=cor, edgecolor='black')
        ax.add_patch(bloco)

    ax.set_ylim(data_clean[depth_col].max(), data_clean[depth_col].min())
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_ylabel("Profundidade (m)")
    ax.set_title("Coluna Litológica")
    st.pyplot(fig, clear_figure=True)
