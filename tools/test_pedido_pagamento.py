"""
CAMPOS DE PAGAMENTO EM PEDIDOS
Busca campos de status e quitação na tabela de pedidos.

DICA DE EDIÇÃO:
- Altere o número '110326' no final do arquivo na linha da 'query'
  para analisar um pedido diferente.
"""

import os
import sys

# Adiciona a raiz do projeto ao sys.path para permitir execuções diretas da pasta tools/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fdb

from config import DB_CONFIG

try:
    conn = fdb.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("=" * 80)
    print("INVESTIGANDO CAMPOS DE PAGAMENTO NA TABELA PEDIDO")
    print("=" * 80)

    # Listar todas as colunas da tabela PEDIDO
    cursor.execute(
        """
        SELECT RDB$FIELD_NAME
        FROM RDB$RELATION_FIELDS
        WHERE RDB$RELATION_NAME = 'PEDIDO'
        ORDER BY RDB$FIELD_POSITION
    """
    )

    colunas = [row[0].strip() for row in cursor.fetchall()]

    print("\nCOLUNAS DA TABELA PEDIDO:")
    print("-" * 80)
    for i, col in enumerate(colunas, 1):
        print(f"{i:3d}. {col}")

    # Procurar colunas relacionadas a pagamento
    print("\n\nCOLUNAS RELACIONADAS A PAGAMENTO:")
    print("-" * 80)
    campos_pagamento = [
        col
        for col in colunas
        if any(
            palavra in col.upper()
            for palavra in ["PAG", "RECEB", "QUIT", "STATUS", "SITUACAO"]
        )
    ]

    if campos_pagamento:
        for campo in campos_pagamento:
            print(f"  - {campo}")

            # Tentar ver valores únicos deste campo
            try:
                query = f"SELECT DISTINCT {campo} FROM PEDIDO WHERE {campo} IS NOT NULL ROWS 10"
                cursor.execute(query)
                valores = cursor.fetchall()
                if valores:
                    print(f"    Valores: {', '.join([str(v[0]) for v in valores])}")
            except:
                pass
    else:
        print("  Nenhuma coluna óbvia de pagamento encontrada")

    # Testar um pedido específico
    print("\n\nEXEMPLO DE PEDIDO (código 110326):")
    print("-" * 80)
    cursor.execute("SELECT FIRST 1 * FROM PEDIDO WHERE PED_NUMEROOPERACAO = 110326")
    row = cursor.fetchone()

    if row:
        for i, col in enumerate(colunas):
            if row[i] is not None:
                print(f"{col}: {row[i]}")

    cursor.close()
    conn.close()
    print("\n[OK] Investigação concluída!")


except Exception as e:
    print(f"[ERRO] Erro: {e}")

    import traceback

    traceback.print_exc()
