import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def get_depth_column(df):
    for col in ['DEPTH', 'DEPT', 'MD']:
        if col in df.columns:
            return col
    return None

def app():
    # Verificação inicial
    if "well_data" not in st.session_state or st.session_state["well_data"] is None:
        st.warning("⚠️ Nenhum dado carregado. Vá até a aba de Importação.")
        return

    df_original = st.session_state["well_data"].copy()
    depth_col = get_depth_column(df_original)

    # Sidebar - Controles
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ Configurações")

        # Tratamento de dados faltantes
        st.markdown("**Dados Ausentes:**")
        handle_na = st.radio(
            "Tratamento",
            ["Remover", "Manter", "Interpolar"],
            label_visibility="collapsed"
        )

        if handle_na == "Remover":
            df = df_original.dropna().copy()
        elif handle_na == "Interpolar":
            df = df_original.interpolate(method='linear').copy()
        else:
            df = df_original.copy()

        if df.empty:
            st.error("❌ DataFrame vazio após tratamento")
            return

        # Filtro de profundidade
        if depth_col:
            st.markdown("**Intervalo de Profundidade:**")
            min_depth = float(df[depth_col].min())
            max_depth = float(df[depth_col].max())

            depth_range = st.slider(
                "Range (m)",
                min_value=min_depth,
                max_value=max_depth,
                value=(min_depth, max_depth),
                label_visibility="collapsed"
            )

            df = df[(df[depth_col] >= depth_range[0]) & (df[depth_col] <= depth_range[1])].copy()

        # Seleção de curvas
        curvas_numericas = df.select_dtypes(include="number").columns.tolist()
        if depth_col and depth_col in curvas_numericas:
            curvas_numericas.remove(depth_col)

        if not curvas_numericas:
            st.error("Nenhuma curva numérica disponível")
            return

        st.markdown("**Curvas para Análise:**")
        selected_curves = st.multiselect(
            "Selecione curvas",
            curvas_numericas,
            default=curvas_numericas[:min(5, len(curvas_numericas))],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.metric("Total de Amostras", len(df))
        st.metric("Curvas Selecionadas", len(selected_curves))

        st.markdown("---")
        st.info("💡 Use filtros para análises específicas")

    # Área principal
    st.title("📊 Análise Estatística")

    if not selected_curves:
        st.info("📌 Selecione pelo menos uma curva na sidebar para começar a análise")
        return

    # Resumo estatístico
    st.subheader("📋 Resumo Estatístico")

    stats_df = df[selected_curves].describe().T
    stats_df['cv'] = (stats_df['std'] / stats_df['mean'] * 100).round(2)  # Coeficiente de variação
    st.dataframe(stats_df.style.background_gradient(cmap='YlOrRd', subset=['mean', 'std']), use_container_width=True)

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Amostras", len(df))
    with col2:
        missing = df[selected_curves].isna().sum().sum()
        st.metric("Valores Faltantes", missing)
    with col3:
        st.metric("Curvas Analisadas", len(selected_curves))
    with col4:
        outliers = 0
        for curve in selected_curves:
            Q1 = df[curve].quantile(0.25)
            Q3 = df[curve].quantile(0.75)
            IQR = Q3 - Q1
            outliers += ((df[curve] < (Q1 - 1.5 * IQR)) | (df[curve] > (Q3 + 1.5 * IQR))).sum()
        st.metric("Outliers Detectados", outliers)

    # Tabs para organização
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Distribuições", "📈 Correlações", "📦 Box Plot", "🎯 Dispersão"])

    with tab1:
        st.markdown("### 📊 Análise de Distribuições")

        # Seletor de curva para histograma
        col_sel, col_bins = st.columns([3, 1])
        with col_sel:
            curva_hist = st.selectbox("Selecione uma curva", selected_curves, key="hist_curve")
        with col_bins:
            n_bins = st.slider("Bins", 10, 100, 30, key="hist_bins")

        # Histograma interativo com Plotly
        fig_hist = go.Figure()

        fig_hist.add_trace(go.Histogram(
            x=df[curva_hist],
            nbinsx=n_bins,
            name='Histograma',
            marker_color='#3498db',
            opacity=0.7
        ))

        # KDE (densidade)
        from scipy import stats
        kde_x = np.linspace(df[curva_hist].min(), df[curva_hist].max(), 100)
        kde = stats.gaussian_kde(df[curva_hist].dropna())
        kde_y = kde(kde_x)

        # Normalizar KDE para sobrepor ao histograma
        hist_counts, _ = np.histogram(df[curva_hist].dropna(), bins=n_bins)
        kde_y_scaled = kde_y * len(df[curva_hist]) * (df[curva_hist].max() - df[curva_hist].min()) / n_bins

        fig_hist.add_trace(go.Scatter(
            x=kde_x,
            y=kde_y_scaled,
            mode='lines',
            name='KDE',
            line=dict(color='red', width=3)
        ))

        # Estatísticas
        mean_val = df[curva_hist].mean()
        median_val = df[curva_hist].median()

        fig_hist.add_vline(x=mean_val, line_dash="dash", line_color="green",
                          annotation_text=f"Média: {mean_val:.2f}")
        fig_hist.add_vline(x=median_val, line_dash="dash", line_color="orange",
                          annotation_text=f"Mediana: {median_val:.2f}")

        fig_hist.update_layout(
            title=f'Distribuição: {curva_hist}',
            xaxis_title=curva_hist,
            yaxis_title='Frequência',
            height=500,
            showlegend=True,
            hovermode='x unified',
            plot_bgcolor='white'
        )

        st.plotly_chart(fig_hist, use_container_width=True)

        # Estatísticas adicionais
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("Assimetria", f"{df[curva_hist].skew():.3f}")
        with col_b:
            st.metric("Curtose", f"{df[curva_hist].kurtosis():.3f}")
        with col_c:
            st.metric("Mínimo", f"{df[curva_hist].min():.2f}")
        with col_d:
            st.metric("Máximo", f"{df[curva_hist].max():.2f}")

    with tab2:
        st.markdown("### 🧮 Matriz de Correlação")

        if len(selected_curves) < 2:
            st.warning("Selecione pelo menos 2 curvas para análise de correlação")
        else:
            # Matriz de correlação interativa
            corr_matrix = df[selected_curves].corr()

            fig_corr = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdYlGn',
                zmid=0,
                text=corr_matrix.values,
                texttemplate='%{text:.2f}',
                textfont={"size": 10},
                colorbar=dict(title="Correlação")
            ))

            fig_corr.update_layout(
                title='Matriz de Correlação entre Curvas',
                height=600,
                xaxis={'side': 'bottom'},
                yaxis={'side': 'left'}
            )

            st.plotly_chart(fig_corr, use_container_width=True)

            # Pairplot se não muitas curvas
            if len(selected_curves) <= 5:
                st.markdown("### 🎯 Pairplot")

                fig_pair = plt.figure(figsize=(12, 10))
                sns.set_style("whitegrid")
                pairplot = sns.pairplot(
                    df[selected_curves],
                    diag_kind='kde',
                    plot_kws={'alpha': 0.6, 's': 20, 'edgecolor': 'black', 'linewidth': 0.3},
                    diag_kws={'alpha': 0.7, 'linewidth': 2}
                )
                pairplot.fig.suptitle('Matriz de Dispersão entre Curvas', y=1.01, fontweight='bold')
                st.pyplot(pairplot)

    with tab3:
        st.markdown("### 📦 Box Plot - Análise de Outliers")

        # Box plot interativo com Plotly
        fig_box = go.Figure()

        for curve in selected_curves:
            fig_box.add_trace(go.Box(
                y=df[curve],
                name=curve,
                boxmean='sd',  # Mostra média e desvio padrão
                marker_color=px.colors.qualitative.Set2[selected_curves.index(curve) % len(px.colors.qualitative.Set2)]
            ))

        fig_box.update_layout(
            title='Box Plot - Distribuição e Outliers',
            yaxis_title='Valores',
            height=600,
            showlegend=True,
            plot_bgcolor='white',
            hovermode='x unified'
        )

        st.plotly_chart(fig_box, use_container_width=True)

        # Tabela de outliers
        st.markdown("#### 🔍 Detalhes de Outliers por Curva")

        outlier_data = []
        for curve in selected_curves:
            Q1 = df[curve].quantile(0.25)
            Q3 = df[curve].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers_count = ((df[curve] < lower_bound) | (df[curve] > upper_bound)).sum()
            outlier_percent = (outliers_count / len(df) * 100)

            outlier_data.append({
                'Curva': curve,
                'Q1': f"{Q1:.2f}",
                'Q3': f"{Q3:.2f}",
                'IQR': f"{IQR:.2f}",
                'Outliers': outliers_count,
                'Percentual': f"{outlier_percent:.2f}%"
            })

        outlier_df = pd.DataFrame(outlier_data)
        st.dataframe(outlier_df, use_container_width=True)

    with tab4:
        st.markdown("### 🎯 Gráfico de Dispersão")

        if len(selected_curves) < 2:
            st.warning("Selecione pelo menos 2 curvas para análise de dispersão")
        else:
            col_x, col_y = st.columns(2)
            with col_x:
                x_axis = st.selectbox("Eixo X", selected_curves, index=0, key="scatter_x")
            with col_y:
                y_axis = st.selectbox("Eixo Y", selected_curves, index=min(1, len(selected_curves)-1), key="scatter_y")

            if x_axis != y_axis:
                # Scatter plot interativo com regressão
                fig_scatter = px.scatter(
                    df,
                    x=x_axis,
                    y=y_axis,
                    trendline="ols",
                    trendline_color_override="red",
                    title=f'Dispersão: {x_axis} vs {y_axis}',
                    labels={x_axis: x_axis, y_axis: y_axis}
                )

                fig_scatter.update_traces(marker=dict(size=5, opacity=0.6))
                fig_scatter.update_layout(height=600, plot_bgcolor='white')

                st.plotly_chart(fig_scatter, use_container_width=True)

                # Estatísticas de correlação
                correlation = df[x_axis].corr(df[y_axis])

                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Correlação de Pearson", f"{correlation:.3f}")
                with col_stat2:
                    corr_strength = "Forte" if abs(correlation) > 0.7 else "Moderada" if abs(correlation) > 0.4 else "Fraca"
                    st.metric("Intensidade", corr_strength)
                with col_stat3:
                    r_squared = correlation ** 2
                    st.metric("R² (explicação)", f"{r_squared:.3f}")
            else:
                st.info("Selecione curvas diferentes para os eixos X e Y")

    # Download de relatório
    st.markdown("---")
    csv = df[selected_curves].describe().to_csv()
    st.download_button(
        label="📥 Download Estatísticas (CSV)",
        data=csv,
        file_name="estatisticas.csv",
        mime="text/csv"
    )
