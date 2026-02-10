"""
AUDITORIA DA TABELA RECEBER
Investiga campos de quitação, status e situação no financeiro a receber.
Busca por padrões de conciliação bancária e baixas de títulos.
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
    print("INVESTIGANDO TABELA RECEBER")
    print("=" * 80)

    # Listar colunas da tabela RECEBER
    cursor.execute(
        """
        SELECT RDB$FIELD_NAME
        FROM RDB$RELATION_FIELDS
        WHERE RDB$RELATION_NAME = 'RECEBER'
        ORDER BY RDB$FIELD_POSITION
    """
    )

    colunas = [row[0].strip() for row in cursor.fetchall()]

    print("\nCOLUNAS DA TABELA RECEBER:")
    print("-" * 80)
    for i, col in enumerate(colunas, 1):
        print(f"{i:3d}. {col}")

    # Procurar campos de status/quitação
    print("\n\nCAMPOS RELACIONADOS A STATUS/QUITAÇÃO:")
    print("-" * 80)
    campos_status = [
        col
        for col in colunas
        if any(
            palavra in col.upper()
            for palavra in ["QUIT", "STATUS", "SITUACAO", "PAGO", "DATA"]
        )
    ]

    for campo in campos_status:
        print(f"  - {campo}")

    # Buscar registros do pedido 110326
    print("\n\nREGISTROS DO PEDIDO 110326:")
    print("-" * 80)

    cursor.execute("SELECT * FROM RECEBER WHERE PED_NUMEROOPERACAO = 110326")
    rows = cursor.fetchall()

    if rows:
        print(f"Encontrados {len(rows)} registro(s):\n")
        for row in rows:
            for i, col in enumerate(colunas):
                if row[i] is not None:
                    print(f"  {col}: {row[i]}")
            print("-" * 80)
    else:
        print("Nenhum registro encontrado")

    # Ver exemplos de valores únicos em campos de status
    print("\n\nVALORES ÚNICOS EM CAMPOS DE STATUS:")
    print("-" * 80)

    for campo in (
        ["REC_QUITADO", "REC_SITUACAO", "REC_STATUS"]
        if any(c in colunas for c in ["REC_QUITADO", "REC_SITUACAO", "REC_STATUS"])
        else []
    ):
        if campo in colunas:
            try:
                cursor.execute(
                    f"SELECT DISTINCT {campo} FROM RECEBER WHERE {campo} IS NOT NULL"
                )
                valores = cursor.fetchall()
                print(f"\n{campo}:")
                for v in valores:
                    print(f"  - {v[0]}")
            except:
                pass

    cursor.close()
    conn.close()
    print("\n[OK] Investigação concluída!")


except Exception as e:
    print(f"[ERRO] Erro: {e}")

    import traceback

    traceback.print_exc()
