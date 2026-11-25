import html
import excel
import streamlit as st

st.set_page_config(page_title="Poemário", page_icon="🪶", layout="centered")


# Carrega o arquivo CSS externo
def carregar_css(caminho_css):
    with open(caminho_css, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


carregar_css("styles.css")
excel.inicializar_excel()

st.title("🪶 Poemário")
st.markdown("Acervo literário para cadastro, leitura e organização de poemas.")

aba_acervo, aba_cadastro = st.tabs(["📖 Acervo", "✍️ Cadastrar Poema"])

# --- ABA 1: ACERVO ---
with aba_acervo:
    df_poemas = excel.carregar_poemas()

    busca = st.text_input(
        "Pesquisar no acervo",
        placeholder="Busque por título, autor, verso ou categoria...",
    )

    if busca and not df_poemas.empty:
        termo = busca.lower()
        filtro = (
            df_poemas["Título"].str.lower().str.contains(termo)
            | df_poemas["Autor"].str.lower().str.contains(termo)
            | df_poemas["Versos"].str.lower().str.contains(termo)
            | df_poemas["Categoria"].str.lower().str.contains(termo)
        )
        df_poemas = df_poemas[filtro]

    if df_poemas.empty:
        st.info(
            "Nenhum poema cadastrado ou encontrado. Use a aba 'Cadastrar Poema' para começar."
        )
    else:
        st.caption(f"Total exibido: {len(df_poemas)} poema(s)")
        # Exibe do mais recente para o mais antigo
        for _, row in df_poemas.iloc[::-1].iterrows():
            titulo_seguro = html.escape(str(row["Título"]))
            autor_seguro = html.escape(str(row["Autor"]))
            obra_segura = html.escape(str(row["Obra"]))
            cat_segura = html.escape(str(row["Categoria"]))
            versos_seguros = html.escape(str(row["Versos"]))

            info_obra = f" — <em>{obra_segura}</em>" if obra_segura else ""

            st.markdown(
                f"""
                <div class="poema-card">
                    <div class="poema-titulo">{titulo_seguro}</div>
                    <div class="poema-meta">{autor_seguro}{info_obra} • <strong>{cat_segura}</strong></div>
                    <div class="poema-versos">{versos_seguros}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([5, 1])
            with col1:
                st.caption(f"Registrado em: {row['Data']}")
            with col2:
                if st.button("Excluir", key=f"del_{row['ID']}"):
                    excel.excluir_poema(row["ID"])
                    st.rerun()

# --- ABA 2: CADASTRO ---
with aba_cadastro:
    st.subheader("Novo Registro")
    with st.form("form_cadastro", clear_on_submit=True):
        titulo = st.text_input("Título *", placeholder="Ex: O Albatroz")

        col_a, col_b = st.columns(2)
        with col_a:
            autor = st.text_input(
                "Autor *", placeholder="Ex: Charles Baudelaire"
            )
        with col_b:
            obra = st.text_input(
                "Obra / Livro", placeholder="Ex: As Flores do Mal"
            )

        categoria = st.selectbox(
            "Categoria",
            [
                "Geral",
                "Melancolia / Spleen",
                "Amor",
                "Natureza",
                "Existencialismo",
                "Crítica Social",
                "Outro",
            ],
        )

        versos = st.text_area(
            "Versos *",
            height=250,
            placeholder="Digite ou cole o poema aqui...",
        )

        submit = st.form_submit_button("Salvar no Excel", type="primary")

        if submit:
            if not titulo.strip() or not autor.strip() or not versos.strip():
                st.error("Preencha os campos obrigatórios: Título, Autor e Versos.")
            else:
                excel.salvar_poema(
                    titulo.strip(),
                    autor.strip(),
                    obra.strip(),
                    categoria,
                    versos,
                )
                st.success(f"Poema '{titulo}' salvo em data/poemas.xlsx!")
