"""
LISTAR COLUNAS (RECEBTO)
Exibe os campos da tabela de baixas/recebimentos efetivados (RECEBTO).
Usado para validar campos de descontos, juros e multas aplicados.
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

        cursor.execute("SELECT FIRST 1 * FROM RECEBTO")
        row = cursor.fetchone()
        if row:
            cols = [desc[0] for desc in cursor.description]
            print("COLUNAS DA TABELA RECEBTO:")
            for col in cols:
                print(col)
        else:
            print("Tabela RECEBTO está vazia.")

        conn.close()
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    list_columns()
