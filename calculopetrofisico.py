import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Detecta curvas automaticamente
def detectar_curvas_automaticamente(las):
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

# Função principal
def app():
    # Verificação inicial
    if 'well_data' not in st.session_state or 'las_object' not in st.session_state:
        st.warning("⚠️ Carregue um arquivo LAS na aba de importação.")
        return

    data = st.session_state['well_data'].copy()
    las = st.session_state['las_object']

    curvas = detectar_curvas_automaticamente(las)
    depth_mnemonic = curvas.get('DEPTH')
    col_depth = next((col for col in data.columns if depth_mnemonic in col), None)

    if not col_depth:
        st.error(f"❌ Curva de profundidade '{depth_mnemonic}' não encontrada.")
        st.write("Colunas disponíveis:", list(data.columns))
        return

    # Sidebar - Controles
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ Configuração de Cálculos")

        # Parâmetros petrofísicos
        st.markdown("**Parâmetros Petrofísicos:**")
        rho_ma = st.number_input("ρ matriz (g/cm³)", value=2.65, step=0.01, format="%.2f")
        rho_f = st.number_input("ρ fluido (g/cm³)", value=1.0, step=0.01, format="%.2f")

        st.markdown("**Equação de Archie:**")
        a = st.number_input("a (tortuosidade)", value=1.0, step=0.1, format="%.1f")
        m = st.number_input("m (cimentação)", value=2.0, step=0.1, format="%.1f")
        n = st.number_input("n (saturação)", value=2.0, step=0.1, format="%.1f")

        st.markdown("**Resistividade da Água (Rw):**")
        usar_rw_manual = st.radio("Método", ["Manual", "Calcular (SP/RMF)"], label_visibility="collapsed")

        if usar_rw_manual == "Manual":
            rw = st.number_input("Rw (Ω.m)", value=0.1, step=0.01, format="%.3f")
        else:
            parametros = {k.upper(): float(v.value) for k, v in las.params.items()
                         if isinstance(v.value, (int, float, str)) and str(v.value).replace('.', '', 1).replace('-', '', 1).isdigit()}
            rmf = st.number_input("RMF (Ω.m)", value=parametros.get("RMF", 0.1), step=0.01, format="%.3f")

            sp_col = curvas.get('SP')
            if sp_col and sp_col in data.columns:
                sp = data[sp_col].clip(-100, 100)
                rw_calc = rmf * np.exp(-0.83 * sp / 60)
                rw = rw_calc.mean()
                st.success(f"✓ Rw calculado: {rw:.3f}")
            else:
                rw = 0.1
                st.warning("SP não encontrado, usando Rw=0.1")

        st.markdown("---")
        st.info("💡 Ajuste os parâmetros conforme a formação")

    # Área principal
    st.title("⚗️ Cálculo Petrofísico")

    # Informação compacta
    with st.expander("ℹ️ Sobre os Cálculos", expanded=False):
        st.markdown("""
        **Parâmetros Calculados:**
        - **Vcl**: Volume de argila (normalização GR)
        - **PHIT**: Porosidade total (densidade/neutrão)
        - **PHIE**: Porosidade efetiva (PHIT × (1-Vcl))
        - **Sw**: Saturação de água (Archie)
        - **So**: Saturação de óleo (1-Sw)
        - **BVW**: Água irredutível (PHIE × Sw)
        """)

    # Definição de zonas
    st.subheader("🎯 Definição de Zonas")

    n_zonas = st.number_input("Nº de Zonas", min_value=1, max_value=10, value=1)

    zonas = []

    for i in range(n_zonas):
        with st.expander(f"📍 Zona {i+1}", expanded=(i==0)):
            col_a, col_b = st.columns(2)
            with col_a:
                top = st.number_input(f"Topo (m)", key=f"top_{i}", value=float(data[col_depth].min()))
            with col_b:
                base = st.number_input(f"Base (m)", key=f"base_{i}", value=float(data[col_depth].max()))

            metodo_gr = st.radio(f"GR Matrix/Shale", ["Automático", "Manual"], key=f"gr_mode_{i}", horizontal=True)

            if metodo_gr == "Manual":
                col_c, col_d = st.columns(2)
                with col_c:
                    gr_min = st.number_input(f"GR min (API)", key=f"gr_min_{i}", value=20.0)
                with col_d:
                    gr_max = st.number_input(f"GR max (API)", key=f"gr_max_{i}", value=100.0)
            else:
                col_gr = curvas.get("GR")
                if col_gr in data.columns:
                    zona_gr = data[(data[col_depth] >= top) & (data[col_depth] <= base)][col_gr]
                    gr_min = zona_gr.min()
                    gr_max = zona_gr.max()
                    st.info(f"✓ GR: {gr_min:.1f} - {gr_max:.1f} API")
                else:
                    gr_min, gr_max = 20.0, 100.0

            zonas.append((top, base, gr_min, gr_max))

    # Botão de cálculo
    if st.button("🚀 Calcular Parâmetros Petrofísicos", type="primary", use_container_width=True):
        with st.spinner("Calculando..."):
            col_gr = curvas.get("GR")
            col_rt = curvas.get("RT")

            # Inicializa colunas
            data['Vcl'] = float('nan')
            data['PHIT'] = float('nan')
            data['PHIE'] = float('nan')
            data['Sw'] = float('nan')
            data['So'] = float('nan')
            data['BVW'] = float('nan')

            for top, base, gr_min, gr_max in zonas:
                zona_mask = (data[col_depth] >= top) & (data[col_depth] <= base)

                # Vcl - Volume de argila
                if col_gr and col_gr in data.columns:
                    vsh = (data[col_gr] - gr_min) / (gr_max - gr_min)
                    data.loc[zona_mask, 'Vcl'] = vsh.clip(0, 1)

                # Porosidade
                if 'RHOB' in curvas and 'NPHI' in curvas:
                    rhob = curvas['RHOB']
                    nphi = curvas['NPHI']
                    if rhob in data.columns and nphi in data.columns:
                        phid = ((rho_ma - data[rhob]) / (rho_ma - rho_f)).clip(0, 1)
                        phin = data[nphi].clip(0, 1)
                        phit = ((phid + phin) / 2).clip(0, 1) * 100
                    else:
                        phit = np.nan
                elif 'PHI' in curvas:
                    col_por = curvas['PHI']
                    phit = data[col_por].clip(0, 1) * 100 if col_por in data.columns else np.nan
                else:
                    phit = np.nan

                phie = (phit / 100 * (1 - data['Vcl'])).clip(0, 1) * 100
                data.loc[zona_mask, 'PHIT'] = phit
                data.loc[zona_mask, 'PHIE'] = phie

                # Saturações (Equação de Archie)
                if col_rt and col_rt in data.columns:
                    sw = ((a * rw) / (data[col_rt] * ((phie / 100) ** m))) ** (1 / n)
                    data.loc[zona_mask, 'Sw'] = sw.clip(0, 1)
                    data.loc[zona_mask, 'So'] = (1 - sw).clip(0, 1)
                    data.loc[zona_mask, 'BVW'] = (phie / 100) * sw

            st.session_state['petro_data'] = data

        st.success("✅ Cálculo finalizado com sucesso!")

        # Métricas
        st.markdown("---")
        st.subheader("📊 Resumo por Zona")

        for i, (top, base, _, _) in enumerate(zonas):
            zona_data = data[(data[col_depth] >= top) & (data[col_depth] <= base)]

            with st.expander(f"📍 Zona {i+1}: {top:.1f} - {base:.1f} m", expanded=True):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    vcl_med = zona_data['Vcl'].mean() if 'Vcl' in zona_data else 0
                    st.metric("Vcl médio", f"{vcl_med:.2%}")

                with col2:
                    phie_med = zona_data['PHIE'].mean() if 'PHIE' in zona_data else 0
                    st.metric("PHIE médio", f"{phie_med:.1f}%")

                with col3:
                    sw_med = zona_data['Sw'].mean() if 'Sw' in zona_data else 0
                    st.metric("Sw médio", f"{sw_med:.2%}")

                with col4:
                    so_med = zona_data['So'].mean() if 'So' in zona_data else 0
                    st.metric("So médio", f"{so_med:.2%}")

        # Tabela de resultados
        st.markdown("---")
        st.subheader("📋 Tabela de Resultados")

        resultado_df = data[[col_depth, 'Vcl', 'PHIT', 'PHIE', 'Sw', 'So', 'BVW']].round(3)
        st.dataframe(resultado_df, use_container_width=True, height=300)

        # Download tabela
        csv = resultado_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Resultados (CSV)", data=csv, file_name="parametros_petrofisicos.csv", mime='text/csv')

        # Visualização Interativa com Plotly
        st.markdown("---")
        st.subheader("📈 Visualização Interativa")

        fig = make_subplots(
            rows=1, cols=6,
            shared_yaxes=True,
            subplot_titles=['Vcl', 'PHIT (%)', 'PHIE (%)', 'Sw', 'So', 'BVW'],
            horizontal_spacing=0.03
        )

        tracks_config = [
            ('Vcl', '#2ecc71', (0, 1)),
            ('PHIT', '#3498db', (0, 40)),
            ('PHIE', '#9b59b6', (0, 40)),
            ('Sw', '#e74c3c', (0, 1)),
            ('So', '#f39c12', (0, 1)),
            ('BVW', '#95a5a6', (0, 0.4))
        ]

        for i, (col, color, xlim) in enumerate(tracks_config, 1):
            if col in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data[col],
                        y=data[col_depth],
                        mode='lines',
                        name=col,
                        line=dict(color=color, width=1.5),
                        hovertemplate=f'<b>{col}</b><br>%{{x:.3f}}<br>Depth: %{{y:.2f}}<extra></extra>'
                    ),
                    row=1, col=i
                )
                fig.update_xaxes(range=xlim, row=1, col=i)

        fig.update_yaxes(title_text="Profundidade (m)", autorange="reversed", row=1, col=1)
        fig.update_layout(
            height=700,
            showlegend=False,
            plot_bgcolor='white',
            hovermode='y unified'
        )

        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'scrollZoom': True,
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'petrofisico',
                'height': 1200,
                'width': 1800,
                'scale': 2
            }
        }

        st.plotly_chart(fig, use_container_width=True, config=config)

        # Pickett Plot Interativo
        if col_rt and col_rt in data.columns and 'PHIE' in data.columns:
            st.markdown("---")
            st.subheader("📊 Pickett Plot Interativo")

            vcl_limit = st.slider("Limite de Vcl para Pickett", 0.0, 0.5, 0.1, 0.05)
            filt = (data['Vcl'] < vcl_limit) & data[col_rt].notna() & data['PHIE'].notna()

            fig_pickett = go.Figure()

            # Dados
            fig_pickett.add_trace(go.Scatter(
                x=data.loc[filt, col_rt],
                y=data.loc[filt, 'PHIE'] / 100,
                mode='markers',
                name='Dados',
                marker=dict(color='red', size=5),
                hovertemplate='<b>Dados</b><br>RT: %{x:.2f}<br>PHIE: %{y:.3f}<extra></extra>'
            ))

            # Linhas de Sw
            sw_lines = [1.0, 0.8, 0.6, 0.4, 0.2]
            phie_range = np.logspace(-2, 0, 100)
            colors_sw = ['blue', 'green', 'orange', 'purple', 'brown']

            for sw, color in zip(sw_lines, colors_sw):
                rt_line = (a * rw) / (sw ** n) / (phie_range ** m)
                fig_pickett.add_trace(go.Scatter(
                    x=rt_line,
                    y=phie_range,
                    mode='lines',
                    name=f'Sw={int(sw*100)}%',
                    line=dict(color=color, width=2)
                ))

            fig_pickett.update_xaxes(type="log", range=[-1, 3], title="Resistividade (Ω.m)")
            fig_pickett.update_yaxes(type="log", range=[-2, 0], title="PHIE (v/v)")

            fig_pickett.update_layout(
                title=f'Pickett Plot (Vcl < {vcl_limit:.0%})',
                height=600,
                plot_bgcolor='white',
                hovermode='closest',
                showlegend=True
            )

            st.plotly_chart(fig_pickett, use_container_width=True)
