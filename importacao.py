import streamlit as st
import lasio
import tempfile
import os

def load_las_data(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.las') as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        las = lasio.read(tmp_path)
        os.unlink(tmp_path)

        df = las.df()
        df.insert(0, "DEPTH", las.index)  # Adiciona a profundidade

        # ✅ Remover linhas com dados ausentes sem exibir mensagem
       

        return las, df
    except Exception as e:
        st.error(f"Erro ao carregar arquivo LAS: {str(e)}")
        return None, None

def display_well_info(las):
    st.subheader("~WELL INFORMATION SECTION")
    st.markdown("""
    <style>
    .las-format { font-family: monospace; white-space: pre; line-height: 1.3; }
    .las-header { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<p class="las-format las-header">#MNEM.UNIT       Data Type    Information</p>', unsafe_allow_html=True)
    for param, value in las.well.items():
        st.markdown(f'<p class="las-format">{param}: {value.value}</p>', unsafe_allow_html=True)

def display_curve_info(las):
    st.subheader("~CURVE INFORMATION SECTION")
    st.markdown("""
    <style>
    .las-format { font-family: monospace; white-space: pre; }
    .las-header { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<p class="las-format las-header">#MNEM    .UNIT         Curve Description</p>', unsafe_allow_html=True)
    for curve in las.curves:
        mnem = curve.mnemonic.ljust(8)
        unit = f".{curve.unit}".ljust(9) if curve.unit else ".N/A".ljust(9)
        description = curve.descr if curve.descr else "No description"
        st.markdown(f'<p class="las-format">{mnem}{unit}: {description}</p>', unsafe_allow_html=True)

def app():
    with st.sidebar:
        st.markdown("---")
        st.subheader("📁 Importação de Arquivo LAS")

        uploaded_file = st.file_uploader("Selecione um arquivo LAS", type=['las'])

        if uploaded_file is not None:
            las, df = load_las_data(uploaded_file)

            if las is not None and df is not None:
                st.session_state['well_data'] = df.reset_index(drop=True)
                st.session_state['las_object'] = las

                st.success("✓ Arquivo carregado!")

                try:
                    st.caption(f"**Depth:** {df['DEPTH'].min():.2f} - {df['DEPTH'].max():.2f}")
                except Exception as e:
                    st.warning(f"Erro ao determinar profundidade: {str(e)}")

        st.markdown("---")

    # Informações detalhadas na área principal
    if 'las_object' in st.session_state and st.session_state['las_object'] is not None:
        las = st.session_state['las_object']

        st.title("📊 Informações do Arquivo LAS")

        display_well_info(las)
        display_curve_info(las)

if __name__ == "__main__":
    app()
