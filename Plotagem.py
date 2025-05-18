import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import lasio
from io import StringIO
from PIL import Image

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

def app():
    st.title("Visualização de Perfis Geofísicos")

    if 'well_data' not in st.session_state or st.session_state['well_data'] is None:
        st.warning("Nenhum dado foi carregado. Vá para a página de Importação.")
        return

    df = st.session_state['well_data']
    plot_well_logs(df)
