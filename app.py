import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date
from pathlib import Path
from excel import (
    carregar_poemas, salvar_poemas, adicionar_poema, atualizar_poema,
    excluir_poema, COLUNAS, CAMINHO_EXCEL
)

st.set_page_config(
    page_title="Poemário | Cadastro de Poemas",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def carregar_css():
    caminho = Path(__file__).parent / "styles.css"
    if caminho.exists():
        st.markdown(f"<style>{caminho.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

carregar_css()

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

df = carregar_poemas()

with st.sidebar:
    st.markdown("# 📚 Poemário")
    st.caption("Seu espaço para guardar, organizar e revisitar poemas.")
    pagina = st.radio(
        "Navegação",
        ["Início", "Cadastrar poema", "Biblioteca", "Relatórios", "Importar / Exportar"],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption(f"📖 {len(df)} poema(s) na biblioteca")
    st.caption("Armazenamento: arquivo Excel")

st.markdown('<div class="eyebrow">BIBLIOTECA LITERÁRIA</div>', unsafe_allow_html=True)

if pagina == "Início":
    st.title("Bem-vindo ao Poemário")
    st.write("Um lugar para registrar seus poemas, organizar suas ideias e acompanhar sua coleção.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Poemas cadastrados", len(df))
    c2.metric("Autores", df["Autor"].replace("", pd.NA).nunique() if not df.empty else 0)
    c3.metric("Temas registrados", df["Tema"].replace("", pd.NA).nunique() if not df.empty else 0)
    st.divider()
    st.subheader("Adicionados recentemente")
    if df.empty:
        st.info("Sua biblioteca ainda está vazia. Use **Cadastrar poema** para adicionar o primeiro.")
    else:
        recentes = df.sort_values("Data de cadastro", ascending=False).head(5)
        for _, p in recentes.iterrows():
            with st.container(border=True):
                st.markdown(f"### {p['Título']}")
                st.caption(f"✍️ {p['Autor'] or 'Autor não informado'}  ·  {p['Tema'] or 'Sem tema'}")
                trecho = str(p["Poema"]).strip()
                st.write(trecho[:280] + ("…" if len(trecho) > 280 else ""))

elif pagina == "Cadastrar poema":
    st.title("Cadastrar um poema")
    st.write("Preencha os campos abaixo para guardar um novo texto na sua biblioteca.")
    with st.form("novo_poema", clear_on_submit=True):
        titulo = st.text_input("Título *", placeholder="Ex.: No meio do caminho")
        col1, col2 = st.columns(2)
        autor = col1.text_input("Autor", placeholder="Nome do autor")
        tema = col2.text_input("Tema", placeholder="Ex.: amor, natureza, saudade")
        col3, col4 = st.columns(2)
        categoria = col3.selectbox("Categoria", ["Autoral", "Clássico", "Cordel", "Haicai", "Soneto", "Livre", "Outro"])
        data_poema = col4.date_input("Data do poema", value=date.today(), format="DD/MM/YYYY")
        tags = st.text_input("Palavras-chave", placeholder="Separe por vírgulas")
        poema = st.text_area("Texto do poema *", height=260, placeholder="Escreva ou cole seu poema aqui...")
        observacoes = st.text_area("Observações (opcional)", height=90)
        enviado = st.form_submit_button("💾 Salvar poema", type="primary", use_container_width=True)
        if enviado:
            if not titulo.strip() or not poema.strip():
                st.error("Preencha pelo menos o título e o texto do poema.")
            else:
                novo = {
                    "Título": titulo.strip(), "Autor": autor.strip(), "Tema": tema.strip(),
                    "Categoria": categoria, "Data do poema": data_poema.isoformat(),
                    "Palavras-chave": tags.strip(), "Poema": poema.strip(),
                    "Observações": observacoes.strip()
                }
                adicionar_poema(novo)
                st.session_state["flash"] = "Poema cadastrado com sucesso!"
                st.rerun()

elif pagina == "Biblioteca":
    st.title("Minha biblioteca")
    st.write("Pesquise, filtre, leia, edite ou exclua os poemas cadastrados.")
    if df.empty:
        st.info("Nenhum poema cadastrado ainda.")
    else:
        q = st.text_input("🔎 Buscar", placeholder="Pesquise por título, autor, tema, palavras-chave ou texto")
        a, b = st.columns(2)
        autores = sorted([x for x in df["Autor"].dropna().unique() if str(x).strip()])
        temas = sorted([x for x in df["Tema"].dropna().unique() if str(x).strip()])
        filtro_autor = a.selectbox("Filtrar por autor", ["Todos"] + autores)
        filtro_tema = b.selectbox("Filtrar por tema", ["Todos"] + temas)
        filtrado = df.copy()
        if q:
            mascara = filtrado.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)
            filtrado = filtrado[mascara]
        if filtro_autor != "Todos":
            filtrado = filtrado[filtrado["Autor"] == filtro_autor]
        if filtro_tema != "Todos":
            filtrado = filtrado[filtrado["Tema"] == filtro_tema]
        st.caption(f"{len(filtrado)} resultado(s)")
        for _, p in filtrado.iterrows():
            with st.expander(f"📜 {p['Título']} — {p['Autor'] or 'Autor não informado'}"):
                st.caption(f"{p['Categoria']} · {p['Tema'] or 'Sem tema'} · {p['Data do poema']}")
                st.markdown(f'<div class="poem-text">{str(p["Poema"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                if p["Palavras-chave"]:
                    st.caption(f"Palavras-chave: {p['Palavras-chave']}")
                if p["Observações"]:
                    st.write(f"**Observações:** {p['Observações']}")
                with st.popover("✏️ Editar / excluir"):
                    with st.form(f"editar_{int(p['ID'])}"):
                        nt = st.text_input("Título", value=p["Título"])
                        na = st.text_input("Autor", value=p["Autor"])
                        ntema = st.text_input("Tema", value=p["Tema"])
                        nc = st.selectbox("Categoria", ["Autoral", "Clássico", "Cordel", "Haicai", "Soneto", "Livre", "Outro"],
                                           index=(["Autoral", "Clássico", "Cordel", "Haicai", "Soneto", "Livre", "Outro"].index(p["Categoria"]) if p["Categoria"] in ["Autoral", "Clássico", "Cordel", "Haicai", "Soneto", "Livre", "Outro"] else 0))
                        nd = st.text_input("Data do poema (AAAA-MM-DD)", value=p["Data do poema"])
                        nk = st.text_input("Palavras-chave", value=p["Palavras-chave"])
                        np = st.text_area("Poema", value=p["Poema"], height=180)
                        no = st.text_area("Observações", value=p["Observações"])
                        salvar = st.form_submit_button("Salvar alterações")
                        if salvar:
                            if nt.strip() and np.strip():
                                atualizar_poema(int(p["ID"]), {
                                    "Título": nt.strip(), "Autor": na.strip(), "Tema": ntema.strip(),
                                    "Categoria": nc, "Data do poema": nd.strip(), "Palavras-chave": nk.strip(),
                                    "Poema": np.strip(), "Observações": no.strip()
                                })
                                st.session_state["flash"] = "Alterações salvas."
                                st.rerun()
                            else:
                                st.error("Título e poema são obrigatórios.")
                    if st.button("🗑️ Excluir este poema", key=f"excluir_{int(p['ID'])}"):
                        excluir_poema(int(p["ID"]))
                        st.session_state["flash"] = "Poema excluído."
                        st.rerun()

elif pagina == "Relatórios":
    st.title("Relatórios da biblioteca")
    if df.empty:
        st.info("Cadastre poemas para visualizar os relatórios.")
    else:
        x, y = st.columns(2)
        x.metric("Total de poemas", len(df))
        y.metric("Média de palavras por poema", round(df["Poema"].fillna("").str.split().str.len().mean(), 1))
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Poemas por categoria")
            st.bar_chart(df["Categoria"].value_counts())
        with c2:
            st.subheader("Poemas por tema")
            temas_rel = df["Tema"].replace("", "Sem tema").value_counts().head(10)
            st.bar_chart(temas_rel)
        st.subheader("Autores com mais poemas")
        st.bar_chart(df["Autor"].replace("", "Não informado").value_counts().head(10))

elif pagina == "Importar / Exportar":
    st.title("Importar e exportar")
    st.write("Faça cópias de segurança ou importe uma planilha com poemas.")

    atual = carregar_poemas()

    if not atual.empty:
        buffer_excel = BytesIO()
        atual.to_excel(buffer_excel, index=False, engine="openpyxl")
        buffer_excel.seek(0)

        st.download_button(
            "⬇️ Baixar biblioteca em Excel",
            data=buffer_excel.getvalue(),
            file_name="biblioteca_de_poemas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        csv = atual.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ Baixar biblioteca em CSV",
            data=csv,
            file_name="biblioteca_de_poemas.csv",
            mime="text/csv"
        )

    st.divider()

    st.subheader("Importar planilha Excel")

    st.caption(
        "A planilha deve conter as colunas Título e Poema."
    )

    up = st.file_uploader(
        "Selecione um arquivo .xlsx",
        type=["xlsx"]
    )

    if up and st.button("Importar poemas", type="primary"):
        try:
            entrada = pd.read_excel(up)
            entrada.columns = [str(c).strip() for c in entrada.columns]

            if not all(c in entrada.columns for c in ["Título", "Poema"]):
                st.error("A planilha precisa conter Título e Poema.")

            else:
                for c in COLUNAS:
                    if c not in entrada.columns:
                        entrada[c] = ""

                proximo_id = (
                    int(pd.to_numeric(atual["ID"], errors="coerce").fillna(0).max()) + 1
                    if not atual.empty else 1
                )

                entrada = entrada[COLUNAS].copy()

                entrada["ID"] = range(
                    proximo_id,
                    proximo_id + len(entrada)
                )

                entrada["Data de cadastro"] = pd.Timestamp.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                entrada = entrada.fillna("")

                salvar_poemas(
                    pd.concat([atual, entrada], ignore_index=True)
                )

                st.success("Poemas importados com sucesso!")
                st.rerun()

        except Exception as e:
            st.error(f"Erro ao importar: {e}")


st.sidebar.divider()
st.sidebar.caption("Poemário • Desenvolvido com Streamlit e Excel")
