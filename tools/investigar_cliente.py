"""
INVESTIGAR CLIENTE ESPECÍFICO
Mostra detalhes de CPF, CNPJ e tipo de pessoa (F/J) para um ID de cliente.

DICA DE EDIÇÃO:
- No final do arquivo, altere os números dentro de 'investigate_client(ID)'
  para consultar outros clientes.
"""

import os
import sys

# Adiciona a raiz do projeto ao sys.path para permitir execuções diretas da pasta tools/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fdb

from config import DB_CONFIG


def investigate_client(client_id):
    try:
        conn = fdb.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = f"SELECT CLI_CODIGO, CLI_NOME, CLI_CPF, CLI_CNPJ, CLI_PESSOAFISICAJURIDICA FROM CLIENTE WHERE CLI_CODIGO = {client_id}"
        cursor.execute(query)
        row = cursor.fetchone()

        if row:
            cols = [desc[0] for desc in cursor.description]
            print(f"DADOS DO CLIENTE {client_id}:")
            for i, val in enumerate(row):
                print(f"{cols[i]}: |{val}| (Tipo: {type(val)})")
        else:
            print(f"Cliente {client_id} não encontrado.")

        conn.close()
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    investigate_client(1)
    investigate_client(11)  # Consumidor para comparar
    investigate_client(219)  # Wellington (que veio certo)