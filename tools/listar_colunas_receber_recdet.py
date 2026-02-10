"""
LISTAR COLUNAS (RECEBER / RECDET)
Exibe todos os campos disponíveis nas tabelas principais de Contas a Receber.
Ajuda a identificar campos novos ou faltantes nos relatórios.
"""

import os
import sys

# Adiciona a raiz do projeto ao sys.path para permitir execuções diretas da pasta tools/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fdb

from config import DB_CONFIG


def list_columns():
    try:
        conn = fdb.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for table in ["RECEBER", "RECDET"]:
            cursor.execute(f"SELECT FIRST 1 * FROM {table}")
            row = cursor.fetchone()
            if row:
                cols = [desc[0] for desc in cursor.description]
                print(f"\nCOLUNAS DA TABELA {table}:")
                for col in cols:
                    print(col)
            else:
                print(f"Tabela {table} está vazia.")

        conn.close()
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    list_columns()
