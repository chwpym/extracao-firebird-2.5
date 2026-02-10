"""
VALIDAR CORREÇÃO DE CNPJ
Verifica se a lógica de TRIM/NULLIF está funcionando para o cliente Moacir (ID 1).
"""

import os
import sys

# Adiciona a raiz do projeto ao sys.path para permitir execuções diretas da pasta tools/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fdb

import pandas as pd
from config import DB_CONFIG


def validate_moacir():
    try:
        conn = fdb.connect(**DB_CONFIG)

        # SQL com a nova lógica
        sql = """
        SELECT 
            r.CLI_CODIGO,
            c.CLI_NOME,
            COALESCE(NULLIF(TRIM(c.CLI_CPF), ''), NULLIF(TRIM(c.CLI_CNPJ), '')) AS REND_DOCUMENTO
        FROM RECEBER r
        JOIN CLIENTE c ON c.CLI_CODIGO = r.CLI_CODIGO
        WHERE r.CLI_CODIGO = 1
        """

        df = pd.read_sql(sql, conn)
        print("RESULTADO PARA CLIENTE ID 1:")
        print(df.to_string())

        conn.close()
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    validate_moacir()
