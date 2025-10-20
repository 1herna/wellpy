import streamlit as st
import matplotlib.pyplot as plt
import lasio
from io import StringIO
from PIL import Image
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Evitar erro de imagem grande
Image.MAX_IMAGE_PIXELS = None

def get_depth_column(df):
    for col in ['DEPTH', 'DEPT', 'MD']:
        if col in df.columns:
            return col
    return None

def identificar_track_por_info(mnemonic, descr):
    nome = mnemonic.upper()
    descricao = descr.upper() if descr else ""
    if nome in ['GR', 'SP', 'CALI', 'CALIPER']:
        return "Track 1"
    elif any(x in nome for x in ['RES', 'ILD', 'ILM', 'LLD', 'LLS', 'LL8']):
        return "Track 2"
    elif any(x in nome for x in ['RHOB', 'DENSITY', 'NPHI', 'NEUTRON', 'PEF']):
        return "Track 3"
    elif 'DT' in nome or 'SONIC' in descricao:
        return "Track 4"
    else:
        return "Track Extra"

def organizar_tracks_por_lasio(las):
    track_groups = {f"Track {i}": [] for i in range(1, 6)}
    track_groups["Track Extra"] = []

    for curva in las.curves:
        track = identificar_track_por_info(curva.mnemonic, curva.descr)
        track_groups[track].append({
            "mnemonic": curva.mnemonic,
            "unit": curva.unit if curva.unit else ""
        })

    track_final = {}
    for base_track, curvas in track_groups.items():
        for i in range(0, len(curvas), 3):
            nome = f"{base_track}-{(i//3)+1}" if len(curvas) > 3 else base_track
            while nome in track_final:
                nome += "_"
            track_final[nome] = curvas[i:i+3]
    return track_final

def plot_well_logs(df):
    if 'las_object' not in st.session_state or st.session_state['las_object'] is None:
        if 'las_file_content' in st.session_state:
            try:
                las = lasio.read(StringIO(st.session_state['las_file_content']))
                st.session_state['las_object'] = las
            except Exception as e:
                st.error("Erro ao tentar reconstruir objeto LAS: " + str(e))
                return
        else:
            st.error("Objeto LAS não encontrado. Por favor, vá para a página de importação.")
            return

    las = st.session_state['las_object']
    depth_col = get_depth_column(df)
    if not depth_col:
        st.error("Coluna de profundidade não encontrada.")
        return

    top_depth = df[depth_col].min()
    bottom_depth = df[depth_col].max()
    profundidade_total = max(1, bottom_depth - top_depth)

    altura_por_100m = 2.5
    figura_altura = min(50, max(20, int((profundidade_total / 100) * altura_por_100m)))

    if len(df) > 8000:
        df = df.iloc[::len(df)//5000]

    logs = df[(df[depth_col] >= top_depth) & (df[depth_col] <= bottom_depth)]
    tracks = organizar_tracks_por_lasio(las)
    valid_tracks = {k: v for k, v in tracks.items() if v}
    n_tracks = len(valid_tracks)

    fig, axes = plt.subplots(1, n_tracks, figsize=(min(7 * n_tracks, 70), figura_altura), sharey=True, dpi=100)
    if n_tracks == 1:
        axes = [axes]
    fig.subplots_adjust(top=0.9, wspace=0.4)

    for i, (_, curvas) in enumerate(valid_tracks.items()):
        ax = axes[i]
        ax.set_ylim(top_depth, bottom_depth)
        ax.invert_yaxis()
        ax.grid(True, linestyle="--", linewidth=0.3, alpha=0.5)
        ax.tick_params(axis='y', labelsize=27)

        offset_base = 1.05
        for j, curva_info in enumerate(curvas):
            curva = curva_info["mnemonic"]
            unidade = curva_info["unit"]
            if curva not in logs.columns:
                continue

            color = plt.cm.tab10(j % 10)
            ax2 = ax.twiny()
            ax2.spines.top.set_position(('axes', offset_base))
            ax2.set_ylim(top_depth, bottom_depth)
            ax2.invert_yaxis()

            if any(k in curva.upper() for k in ['RES', 'ILD', 'ILM', 'LLD', 'LLS']):
                ax2.set_xscale('log')

            ax2.plot(logs[curva], logs[depth_col], color=color, linewidth=2.5)
            ax2.set_xlabel(f"{curva} [{unidade}]", color=color, fontsize=27, labelpad=20)
            ax2.tick_params(axis='x', colors=color, labelsize=27, pad=12, width=2)
            offset_base += 0.12

        if i == 0:
            ax.set_ylabel("Profundidade (m)", fontsize=27)

    try:
        st.pyplot(fig)
    except MemoryError:
        st.error("Erro de memória ao renderizar o gráfico. Reduza a profundidade ou número de curvas.")
    finally:
        plt.close(fig)

def plot_interactive_logs(df, depth_col, selected_curves, depth_range, mode):
    """Cria visualização interativa com Plotly"""

    # Filtrar dados por profundidade
    df_filtered = df[(df[depth_col] >= depth_range[0]) & (df[depth_col] <= depth_range[1])]

    if mode == "Plotly Interativo":
        # Criar subplots
        n_curves = len(selected_curves)
        fig = make_subplots(
            rows=1, cols=n_curves,
            shared_yaxes=True,
            subplot_titles=selected_curves,
            horizontal_spacing=0.05
        )

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']

        for i, curve in enumerate(selected_curves):
            if curve in df_filtered.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df_filtered[curve],
                        y=df_filtered[depth_col],
                        mode='lines',
                        name=curve,
                        line=dict(color=colors[i % len(colors)], width=2),
                        hovertemplate=f'<b>{curve}</b><br>Valor: %{{x:.2f}}<br>Depth: %{{y:.2f}}<extra></extra>'
                    ),
                    row=1, col=i+1
                )

                # Configurar eixo x
                fig.update_xaxes(title_text=curve, row=1, col=i+1, showgrid=True, gridwidth=1, gridcolor='LightGray')

        # Configurar layout
        fig.update_yaxes(title_text="Profundidade (m)", autorange="reversed", row=1, col=1, showgrid=True, gridwidth=1, gridcolor='LightGray')

        fig.update_layout(
            height=800,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            hovermode='y unified',
            margin=dict(l=50, r=50, t=80, b=50),
            dragmode='zoom',  # Modo padrão: zoom
            modebar=dict(
                bgcolor='rgba(255,255,255,0.7)',
                color='#02ab21',
                activecolor='#ff8c00'
            )
        )

        # Configuração completa para interatividade
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': ['drawopenpath', 'eraseshape'],
            'modeBarButtonsToRemove': [],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'perfil_geofisico',
                'height': 1200,
                'width': 1600,
                'scale': 2
            },
            'scrollZoom': True  # Zoom com scroll do mouse
        }

        st.plotly_chart(fig, use_container_width=True, config=config)

    else:
        # Modo matplotlib (original)
        plot_well_logs(df)

def app():
    # Controles na sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ Controles de Visualização")

        if 'well_data' not in st.session_state or st.session_state['well_data'] is None:
            st.warning("⚠️ Carregue dados primeiro")
            return

        df = st.session_state['well_data']
        depth_col = get_depth_column(df)

        if not depth_col:
            st.error("Coluna de profundidade não encontrada")
            return

        # Modo de visualização
        mode = st.radio(
            "Modo de Visualização",
            ["Plotly Interativo", "Matplotlib Clássico"],
            index=0
        )

        # Seletor de curvas
        available_curves = [col for col in df.columns if col != depth_col]

        st.markdown("**Selecione as Curvas:**")
        selected_curves = st.multiselect(
            "Curvas para plotar",
            available_curves,
            default=available_curves[:min(4, len(available_curves))],
            label_visibility="collapsed"
        )

        # Intervalo de profundidade
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

        # Informações
        st.markdown("---")
        st.metric("Total de Curvas", len(available_curves))
        st.metric("Curvas Selecionadas", len(selected_curves))
        st.metric("Intervalo (m)", f"{depth_range[1] - depth_range[0]:.1f}")

        st.markdown("---")

    # Área principal
    st.title("📊 Visualização de Perfis Geofísicos")

    if 'well_data' not in st.session_state or st.session_state['well_data'] is None:
        st.warning("⚠️ Nenhum dado foi carregado. Vá para a página de Importação.")
        return

    if not selected_curves:
        st.info("ℹ️ Selecione pelo menos uma curva na sidebar para visualizar")
        return

    # Mostrar instruções interativas se modo Plotly
    if mode == "Plotly Interativo":
        st.markdown("""
        <div style='background: linear-gradient(90deg, #e3f2fd 0%, #fff8e1 100%);
                    padding: 15px;
                    border-radius: 10px;
                    border-left: 4px solid #02ab21;
                    margin-bottom: 20px;'>
            <h4 style='margin: 0 0 10px 0; color: #02ab21;'>🖱️ Controles Interativos do Mouse</h4>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; font-size: 13px;'>
                <div><b>🔍 Zoom In:</b> Clique e arraste para selecionar área</div>
                <div><b>↔️ Pan:</b> Segure Shift + Clique e arraste</div>
                <div><b>🔎 Zoom Out:</b> Duplo clique no gráfico</div>
                <div><b>📊 Detalhes:</b> Passe o mouse sobre a linha</div>
                <div><b>🏠 Reset:</b> Clique no ícone "Home" no canto</div>
                <div><b>💾 Salvar:</b> Clique no ícone de câmera</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Plotar
    plot_interactive_logs(df, depth_col, selected_curves, depth_range, mode)
