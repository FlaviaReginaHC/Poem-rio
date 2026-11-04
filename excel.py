from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

PASTA = Path(__file__).parent / "data"
CAMINHO_EXCEL = PASTA / "poemas.xlsx"
COLUNAS = [
    "ID", "Título", "Autor", "Tema", "Categoria", "Data do poema",
    "Palavras-chave", "Poema", "Observações", "Data de cadastro"
]

def garantir_arquivo():
    PASTA.mkdir(parents=True, exist_ok=True)
    if not CAMINHO_EXCEL.exists():
        df = pd.DataFrame(columns=COLUNAS)
        df.to_excel(CAMINHO_EXCEL, index=False, engine="openpyxl")

def carregar_poemas():
    garantir_arquivo()
    try:
        df = pd.read_excel(CAMINHO_EXCEL, engine="openpyxl")
        for col in COLUNAS:
            if col not in df.columns:
                df[col] = ""
        df = df[COLUNAS]
        df["ID"] = pd.to_numeric(df["ID"], errors="coerce")
        df["ID"] = df["ID"].fillna(0).astype(int)
        return df.fillna("")
    except Exception as e:
        st.error(f"Erro ao ler a planilha Excel: {e}")
        return pd.DataFrame(columns=COLUNAS)

def salvar_poemas(df):
    garantir_arquivo()
    saida = df.copy()
    for col in COLUNAS:
        if col not in saida.columns:
            saida[col] = ""
    saida = saida[COLUNAS]
    saida.to_excel(CAMINHO_EXCEL, index=False, engine="openpyxl")

def adicionar_poema(dados):
    df = carregar_poemas()
    proximo_id = int(df["ID"].max()) + 1 if not df.empty else 1
    novo = {col: "" for col in COLUNAS}
    novo.update(dados)
    novo["ID"] = proximo_id
    novo["Data de cadastro"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    salvar_poemas(pd.concat([df, pd.DataFrame([novo])], ignore_index=True))

def atualizar_poema(poema_id, dados):
    df = carregar_poemas()
    for chave, valor in dados.items():
        if chave in COLUNAS:
            df.loc[df["ID"] == poema_id, chave] = valor
    salvar_poemas(df)

def excluir_poema(poema_id):
    df = carregar_poemas()
    salvar_poemas(df[df["ID"] != poema_id].copy())
