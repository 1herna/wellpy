import streamlit as st
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.utils import resample
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns

def get_depth_column(data):
    for col in ['DEPTH', 'DEPT', 'MD']:
        if col in data.columns:
            return col
    return None

def app():
    # Verificação dos dados
    if 'well_data' not in st.session_state:
        st.warning("⚠️ Nenhum dado carregado. Vá até a aba de Importação.")
        return

    data = st.session_state['well_data']
    depth_col = get_depth_column(data)

    if not depth_col:
        st.error("❌ Coluna de profundidade não encontrada.")
        return

    colunas_disponiveis = [col for col in data.columns if col != depth_col]
    if not colunas_disponiveis:
        st.warning("Nenhuma curva disponível para classificação.")
        return

    # Controles na sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ Configurações")

        # Seleção de curvas
        st.markdown("**Curvas para Classificação:**")
        selected_curves = st.multiselect(
            "Selecione uma ou mais curvas",
            colunas_disponiveis,
            default=[colunas_disponiveis[0]] if colunas_disponiveis else [],
            label_visibility="collapsed"
        )

        # Método de classificação
        metodo = st.radio(
            "**Método:**",
            ["Automático (Silhouette)", "Manual (K clusters)"],
            index=0
        )

        if metodo == "Manual (K clusters)":
            n_clusters = st.slider("Número de Clusters", 2, 8, 3)
        else:
            n_clusters = None

        # Intervalo de profundidade
        st.markdown("**Intervalo de Profundidade:**")
        min_depth = float(data[depth_col].min())
        max_depth = float(data[depth_col].max())

        depth_range = st.slider(
            "Range (m)",
            min_value=min_depth,
            max_value=max_depth,
            value=(min_depth, max_depth),
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.info("💡 **Dica:** Use múltiplas curvas para classificação mais robusta")

    # Área principal
    st.title('🔬 Classificação Litológica por Eletrofácies')

    # Descrição compacta
    with st.expander("ℹ️ Sobre a Classificação", expanded=False):
        st.markdown("""
        Este módulo realiza **classificação automática da litologia** usando **K-Means clustering**.

        - 🎯 Agrupa dados com características semelhantes
        - 📊 Identifica padrões em perfis geofísicos
        - 🧮 Usa Silhouette Score para otimização automática
        - ⚠️ É uma classificação estatística, não substitui interpretação geológica
        """)

    if not selected_curves:
        st.info("📌 Selecione pelo menos uma curva na sidebar para começar a classificação")
        return

    # Filtrar por profundidade
    data_filtered = data[(data[depth_col] >= depth_range[0]) & (data[depth_col] <= depth_range[1])].copy()

    # Limpar dados
    data_clean = data_filtered.dropna(subset=selected_curves).copy()
    if len(data_clean) < 10:
        st.warning("⚠️ Poucos dados disponíveis. Ajuste o intervalo de profundidade.")
        return

    # Preparar dados para clustering
    X = data_clean[selected_curves].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Determinar número de clusters
    if metodo == "Automático (Silhouette)":
        melhor_k, melhor_score, melhor_kmeans = 2, -1, None
        scores = []

        for k in range(2, 8):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            amostra_size = min(1000, len(X_scaled))
            amostra_X, amostra_labels = resample(X_scaled, labels, n_samples=amostra_size, random_state=42)
            score = silhouette_score(amostra_X, amostra_labels)
            scores.append({'k': k, 'score': score})

            if score > melhor_score:
                melhor_k, melhor_score, melhor_kmeans = k, score, kmeans

        st.success(f"✅ Clusters ideais: **{melhor_k}** | Silhouette Score: **{melhor_score:.3f}**")

        # Gráfico de Silhouette Score
        col1, col2 = st.columns([1, 2])
        with col1:
            fig_sil, ax_sil = plt.subplots(figsize=(6, 4))
            k_values = [s['k'] for s in scores]
            score_values = [s['score'] for s in scores]
            ax_sil.plot(k_values, score_values, 'o-', color='#02ab21', linewidth=2, markersize=8)
            ax_sil.axvline(melhor_k, color='red', linestyle='--', label=f'Melhor K={melhor_k}')
            ax_sil.set_xlabel('Número de Clusters', fontweight='bold')
            ax_sil.set_ylabel('Silhouette Score', fontweight='bold')
            ax_sil.set_title('Otimização de Clusters', fontweight='bold')
            ax_sil.grid(True, alpha=0.3)
            ax_sil.legend()
            st.pyplot(fig_sil)
    else:
        melhor_k = n_clusters
        melhor_kmeans = KMeans(n_clusters=melhor_k, random_state=42, n_init=10)
        melhor_kmeans.fit(X_scaled)
        st.info(f"🔧 Usando **{melhor_k} clusters** (modo manual)")

    # Aplicar classificação
    data_clean['Cluster'] = melhor_kmeans.predict(X_scaled)
    data_clean['Litologia'] = data_clean['Cluster'].apply(lambda x: f"Litofácies {x+1}")

    # Cores
    cores_disponiveis = ['#FFD700', '#8B4513', '#87CEEB', '#98FB98', '#FF6347', '#9932CC', '#FFA500']
    litologias = sorted(data_clean['Litologia'].unique())
    cores = {lit: cores_disponiveis[i % len(cores_disponiveis)] for i, lit in enumerate(litologias)}

    # Visualizações
    st.markdown("---")
    st.subheader("📊 Resultados da Classificação")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Litofácies Identificadas", len(litologias))
    with col2:
        st.metric("Amostras Classificadas", len(data_clean))
    with col3:
        st.metric("Curvas Utilizadas", len(selected_curves))

    # Layout de visualização
    if len(selected_curves) == 1:
        col_left, col_right = st.columns([2, 1])
    else:
        col_left, col_right = st.columns([3, 1])

    with col_left:
        # Gráfico interativo com Plotly
        fig = make_subplots(
            rows=1, cols=len(selected_curves) + 1,
            shared_yaxes=True,
            subplot_titles=selected_curves + ['Litologia'],
            horizontal_spacing=0.05,
            column_widths=[1]*len(selected_curves) + [0.3]
        )

        # Plotar curvas
        colors_curves = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        for i, curve in enumerate(selected_curves):
            fig.add_trace(
                go.Scatter(
                    x=data_clean[curve],
                    y=data_clean[depth_col],
                    mode='lines',
                    name=curve,
                    line=dict(color=colors_curves[i % len(colors_curves)], width=1.5),
                    hovertemplate=f'<b>{curve}</b><br>%{{x:.2f}}<br>Depth: %{{y:.2f}}<extra></extra>'
                ),
                row=1, col=i+1
            )
            fig.update_xaxes(title_text=curve, row=1, col=i+1)

        # Plotar coluna litológica
        for litologia in litologias:
            lito_data = data_clean[data_clean['Litologia'] == litologia]
            fig.add_trace(
                go.Scatter(
                    x=[1]*len(lito_data),
                    y=lito_data[depth_col],
                    mode='markers',
                    name=litologia,
                    marker=dict(
                        color=cores[litologia],
                        size=20,
                        symbol='square',
                        line=dict(color='black', width=0.5)
                    ),
                    hovertemplate=f'<b>{litologia}</b><br>Depth: %{{y:.2f}}<extra></extra>'
                ),
                row=1, col=len(selected_curves)+1
            )

        fig.update_yaxes(title_text="Profundidade (m)", autorange="reversed", row=1, col=1)
        fig.update_xaxes(showticklabels=False, row=1, col=len(selected_curves)+1)

        fig.update_layout(
            height=700,
            showlegend=True,
            plot_bgcolor='white',
            hovermode='y unified',
            legend=dict(x=1.05, y=1)
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # Estatísticas por litofácies
        st.markdown("**📈 Estatísticas:**")
        for lit in litologias:
            lito_data = data_clean[data_clean['Litologia'] == lit]
            percentual = (len(lito_data) / len(data_clean)) * 100

            st.markdown(f"""
            <div style='background-color: {cores[lit]}; padding: 8px; border-radius: 5px; margin-bottom: 8px; border: 1px solid black;'>
                <b>{lit}</b><br>
                <small>{percentual:.1f}% ({len(lito_data)} amostras)</small>
            </div>
            """, unsafe_allow_html=True)

    # Análise por curva (se múltiplas)
    if len(selected_curves) > 1:
        st.markdown("---")
        st.subheader("🎯 Análise Multivariada")

        # Pairplot
        pairplot_data = data_clean[selected_curves + ['Litologia']].copy()

        sns.set_style("whitegrid")
        pairplot_fig = sns.pairplot(
            pairplot_data,
            hue='Litologia',
            palette=cores,
            diag_kind='kde',
            plot_kws={'alpha': 0.6, 's': 20, 'edgecolor': 'black', 'linewidth': 0.3},
            diag_kws={'alpha': 0.7, 'linewidth': 2}
        )
        pairplot_fig.figure.suptitle('Matriz de Correlação entre Curvas', y=1.01, fontweight='bold')
        st.pyplot(pairplot_fig)

    # Opção de download
    st.markdown("---")
    csv = data_clean[[depth_col] + selected_curves + ['Litologia']].to_csv(index=False)
    st.download_button(
        label="📥 Download Classificação (CSV)",
        data=csv,
        file_name="classificacao_litologica.csv",
        mime="text/csv"
    )
