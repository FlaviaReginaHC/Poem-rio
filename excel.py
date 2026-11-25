from datetime import datetime
import os
import pandas as pd

DATA_DIR = "data"
EXCEL_PATH = os.path.join(DATA_DIR, "poemas.xlsx")
COLUNAS = ["ID", "Título", "Autor", "Obra", "Categoria", "Versos", "Data"]


def inicializar_excel():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(EXCEL_PATH):
        df = pd.DataFrame(columns=COLUNAS)
        df.to_excel(EXCEL_PATH, index=False)


def carregar_poemas():
    inicializar_excel()
    df = pd.read_excel(EXCEL_PATH)
    # Garante que campos vazios não apareçam como NaN
    return df.fillna("")


def salvar_poema(titulo, autor, obra, categoria, versos):
    df = carregar_poemas()
    novo_id = 1 if df.empty else int(df["ID"].max()) + 1
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

    novo_registro = pd.DataFrame([{
        "ID": novo_id,
        "Título": titulo,
        "Autor": autor,
        "Obra": obra,
        "Categoria": categoria,
        "Versos": versos,
        "Data": data_atual,
    }])

    df = pd.concat([df, novo_registro], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False)


def excluir_poema(poema_id):
    df = carregar_poemas()
    df = df[df["ID"] != poema_id]
    df.to_excel(EXCEL_PATH, index=False)
