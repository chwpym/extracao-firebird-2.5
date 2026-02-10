"""
AMOSTRA RÁPIDA DE CONTAS A RECEBER
Gera um arquivo Excel com apenas os primeiros registros para validação de layout.

DICA DE EDIÇÃO:
- Procure por 'FIRST 20' no arquivo sql/test_fast.sql se quiser mudar a quantidade.
"""

import os

import sys

# Adiciona a raiz do projeto ao sys.path para permitir execuções diretas da pasta tools/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fdb
import pandas as pd
from config import DB_CONFIG
from core.exporter import DataExporter


def quick_validate():
    try:
        conn = fdb.connect(**DB_CONFIG)
        output_dir = "output_test"
        sql_dir = "sql"
        exporter = DataExporter(conn, output_dir, sql_dir)

        print("Iniciando validação ultrarrápida (10 registros)...")
        success = exporter.export_entity("test_fast")

        if success:
            excel_path = os.path.join(output_dir, "test_fast.xlsx")
            df = pd.read_excel(excel_path)
            print("\nCABEÇALHOS DO MODELO NOVO EXCEL:")
            print(", ".join(df.columns.tolist()))
            print("\nPRIMEIRO REGISTRO:")
            print(df.head(1).to_string())
        else:
            print("Falha na validação.")
        conn.close()
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    quick_validate()
