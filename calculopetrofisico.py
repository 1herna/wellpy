import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns 

# Detecta curvas automaticamente com base em mnemônicos e descrições
def detectar_curvas_automaticamente(las, data):
    candidatos = {
        "DEPTH": ["DEPTH", "DEPT"],
        "GR": ["GR", "GAM"],
        "PHI": ["PHIT", "PHI", "NPHI", "DPLS", "PORS"],
        "RT": ["RT", "ILD", "LLD", "RES"],
        "SP": ["SP"],
        "RHOB": ["RHOB"],
        "NPHI": ["NPHI"]
    }
    resultados = {}
    for curva in las.curves:
        mnem = curva.mnemonic.strip().upper()
        for nome_alvo, lista_mnem in candidatos.items():
            if nome_alvo in resultados:
                continue
            if any(mnem.startswith(alvo) for alvo in lista_mnem):
                resultados[nome_alvo] = mnem
    return resultados

# Extrai parâmetros físicos da seção ~PARAMETER
def extrair_parametros_las(las):
    parametros = {}
    for param in las.params.values():
        chave = param.mnemonic.strip().upper()
        try:
            valor = float(param.value)
            if chave in ['RM', 'RMF', 'RW', 'RWE', 'BHT', 'T']:
                parametros[chave] = valor
        except:
            continue
    return parametros

def calcular_parametros_petrofisicos(data, curvas, params):
    a, m, n = 1, 2, 2
    C = 100
    rw = params.get('RW') or 0.1

    gr_clean, gr_clay = 40, 120
    rho_ma, rho_f = 2.65, 1.0

    col_gr = curvas['GR']
    col_rt = curvas['RT']

    igr = (data[col_gr] - gr_clean) / (gr_clay - gr_clean)
    data['Vcl'] = (0.083 * (2**(3.7 * igr) - 1)).clip(0, 1)

    if 'RHOB' in curvas and 'NPHI' in curvas:
        rhob = curvas['RHOB']
        nphi = curvas['NPHI']
        phid = ((rho_ma - data[rhob]) / (rho_ma - rho_f)).clip(0, 1)
        phin = data[nphi].clip(0, 1)
        data['PHIE'] = (((phid + phin) / 2) * (1 - data['Vcl'])).clip(0, 1) * 100
    else:
        col_por = curvas['PHI']
        data['PHIE'] = (data[col_por] * (1 - data['Vcl'])).clip(0, 1) * 100

    data['Sw'] = ((a * rw) / (data[col_rt] * ((data['PHIE'] / 100) ** m))) ** (1 / n)
    data['Sw'] = data['Sw'].clip(0, 1)
    data['So'] = (1 - data['Sw']).clip(0, 1)
    data['K'] = C * (((data['PHIE'] / 100) ** 4.4) / (data['Sw'] ** 2))

    return data

# Página do cálculo petrofísico
def app():
    st.title("🧮 Cálculo Petrofísico")

    if 'well_data' not in st.session_state or 'las_object' not in st.session_state:
        st.error("Vá para a aba de Importação e carregue um arquivo LAS primeiro.")
        return

    data = st.session_state['well_data']
    las = st.session_state['las_object']
    # nomes mantidos como estão para identificar corretamente curvas com unidade
    data = data.dropna().reset_index(drop=True)

    curvas = detectar_curvas_automaticamente(las, data)
    if not all(k in curvas for k in ['DEPTH', 'GR', 'PHI', 'RT']):
        st.error("Curvas essenciais não encontradas: DEPTH, GR, PHI, RT")
        st.write("Curvas detectadas:", curvas)
        return

    parametros = extrair_parametros_las(las)
    data = calcular_parametros_petrofisicos(data, curvas, parametros)
    data['BVW'] = (data['PHIE'] / 100) * data['Sw']

    col_depth = next((col for col in data.columns if curvas['DEPTH'] in col), curvas['DEPTH'])
    st.dataframe(data[[col_depth, 'Vcl', 'PHIE', 'Sw', 'So', 'K']])

    st.subheader("📊 Visualização Petrofísica")

    profundidade_total = data[col_depth].max() - data[col_depth].min()
    altura_por_100m = 2.5
    figura_altura = min(200, max(10, int((profundidade_total / 100) * altura_por_100m)))

    fig, axes = plt.subplots(ncols=6, figsize=(26, figura_altura), sharey=True)
    depth = data[col_depth]

    unidades = {
        'BVW': 'v/v',
        'Vcl': 'v/v',
        'PHIE': '%',
        'Sw': '%',
        'So': '%',
        'K': 'mD'
    }

    tracks = {
        'BVW': ('', 'gray', (0, 0.4), 'linear'),
        'Vcl': ('', 'blue', (0, 1), 'linear'),
        'PHIE': ('', 'green', (0, 40), 'linear'),
        'Sw': ('', 'red', (0, 1), 'linear'),
        'So': ('', 'orange', (0, 1), 'linear'),
        'K': ('', 'purple', (0.01, 10000), 'log')
    }

    for i, (col, (_, color, xlim, scale)) in enumerate(tracks.items()):
        ax = axes[i]
        if col in data.columns:
            ax.set_xlim(xlim)
            if scale == 'log':
                ax.set_xscale('log')
            ax.plot(data[col], depth, color=color, linewidth=1.2)
            ax.spines['top'].set_position(('outward', 0))
            ax.set_xlabel(f"{col} [{unidades[col]}]", color='black')
            ax.tick_params(axis='x', colors='black')
        else:
            ax.text(0.5, 0.5, f"{col} ausente", horizontalalignment='center',
                    verticalalignment='center', transform=ax.transAxes)
        ax.grid(True, linestyle='--', alpha=0.6)
        if i == 0:
            ax.set_ylabel("Profundidade (m)", fontsize=12)
        else:
            ax.set_yticklabels([])
        ax.invert_yaxis()
        ax.xaxis.set_label_position('top')
        ax.xaxis.tick_top()
        ax.tick_params(labelsize=10)

    st.pyplot(fig)

    import seaborn as sns  # manter apenas seaborn aqui

    st.subheader("📈 Histogramas dos Parâmetros Petrofísicos")
    import seaborn as sns
    parametros_plot = ['Vcl', 'PHIE', 'Sw', 'So', 'K', 'BVW']
    fig_hist, axes_hist = plt.subplots(2, 3, figsize=(18, 10))
    axes_hist = axes_hist.flatten()
    for i, param in enumerate(parametros_plot):
        sns.histplot(data[param], ax=axes_hist[i], kde=True, color='skyblue', edgecolor='black')
        axes_hist[i].set_title(f'Histograma de {param}')
        axes_hist[i].set_xlabel(param)
        axes_hist[i].set_ylabel('Frequência')
    st.pyplot(fig_hist)

    st.subheader("📊 Estatísticas Descritivas dos Parâmetros Petrofísicos")
    st.dataframe(data[parametros_plot].describe().T.round(4))
