import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def app():
    st.title("📊 Estatísticas com Seaborn (Sem Valores Ausentes)")

    if "well_data" not in st.session_state or st.session_state["well_data"] is None:
        st.warning("⚠️ Nenhum dado carregado. Vá até a aba de Importação.")
        return

    df = st.session_state["well_data"].dropna().copy()

    if df.empty:
        st.warning("O DataFrame ficou vazio após remover os valores ausentes.")
        return

    curvas_numericas = df.select_dtypes(include="number").columns.tolist()
    if not curvas_numericas:
        st.info("Nenhuma curva numérica disponível para análise.")
        return

    # Resumo estatístico
    st.subheader("📄 Resumo Estatístico")
    st.dataframe(df.describe().T, use_container_width=True)

    st.divider()

    # Boxplot
    st.subheader("📦 Boxplot de Curvas")
    curvas_box = st.multiselect("Selecione curvas para o boxplot:", curvas_numericas, default=curvas_numericas[:1])
    if curvas_box:
        df_box = df[curvas_box].melt(var_name="Curva", value_name="Valor")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df_box, x="Curva", y="Valor", palette="Set2", ax=ax)
        ax.set_title("Boxplot das Curvas Selecionadas")
        st.pyplot(fig)
    else:
        st.info("Selecione pelo menos uma curva para visualizar o boxplot.")

    st.divider()

    # Histograma
    st.subheader("📊 Histograma")
    curva_hist = st.selectbox("Selecione uma curva para o histograma:", curvas_numericas)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df[curva_hist], kde=True, bins=50, color="skyblue", ax=ax)
    ax.set_title(f"Histograma da Curva: {curva_hist}")
    st.pyplot(fig)

    st.divider()

    # Matriz de correlação
    st.subheader("🧮 Matriz de Correlação (Cores Quentes)")
    corr = df[curvas_numericas].corr()
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="YlOrRd",
        linewidths=0.5,
        annot_kws={"size": 10}
    )
    ax.set_title("Matriz de Correlação entre Curvas", fontsize=16)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(fontsize=9)
    st.pyplot(fig)

    st.divider()

    # Gráfico de dispersão
    st.subheader("📍 Dispersão entre Curvas")
    colx, coly = st.columns(2)
    x = colx.selectbox("Eixo X", curvas_numericas, index=0, key="disp_x")
    y = coly.selectbox("Eixo Y", curvas_numericas, index=1, key="disp_y")

    if x and y and x != y:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.scatterplot(data=df, x=x, y=y, ax=ax)
        sns.regplot(data=df, x=x, y=y, scatter=False, ax=ax, color='red')
        ax.set_title(f"Dispersão: {x} vs {y} (com linha de tendência)")
        st.pyplot(fig)
    else:
        st.info("Selecione duas curvas diferentes para o gráfico de dispersão.")
