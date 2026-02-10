"""
INVESTIGAÇÃO DE CONTAS A RECEBER
Este script analisa as tabelas do financeiro para identificar campos de integração.
"""

# Script para investigar tabelas relacionadas a contas a receber

import fdb
from config import DB_CONFIG

try:
    conn = fdb.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("=" * 80)
    print("INVESTIGANDO TABELAS DE CONTAS A RECEBER")
    print("=" * 80)

    # Listar tabelas que podem conter informações de pagamento
    cursor.execute(
        """
        SELECT RDB$RELATION_NAME
        FROM RDB$RELATIONS
        WHERE RDB$SYSTEM_FLAG = 0
          AND (UPPER(RDB$RELATION_NAME) LIKE '%RECEB%'
           OR UPPER(RDB$RELATION_NAME) LIKE '%PAG%'
           OR UPPER(RDB$RELATION_NAME) LIKE '%CONTA%'
           OR UPPER(RDB$RELATION_NAME) LIKE '%FINANC%'
           OR UPPER(RDB$RELATION_NAME) LIKE '%QUIT%')
        ORDER BY RDB$RELATION_NAME
    """
    )

    tabelas = [row[0].strip() for row in cursor.fetchall()]

    print("\nTABELAS RELACIONADAS A FINANCEIRO:")
    print("-" * 80)
    for tabela in tabelas:
        print(f"  - {tabela}")

    # Investigar CONTASRECEBER se existir
    if any("RECEB" in t for t in tabelas):
        tabela_receber = [t for t in tabelas if "RECEB" in t][0]
        print(f"\n\nINVESTIGANDO TABELA: {tabela_receber}")
        print("-" * 80)

        # Listar colunas
        cursor.execute(
            f"""
            SELECT RDB$FIELD_NAME
            FROM RDB$RELATION_FIELDS
            WHERE RDB$RELATION_NAME = '{tabela_receber}'
            ORDER BY RDB$FIELD_POSITION
        """
        )

        colunas = [row[0].strip() for row in cursor.fetchall()]
        print("Colunas:")
        for col in colunas:
            print(f"  - {col}")

        # Tentar encontrar registros relacionados ao pedido 110326
        print(f"\n\nREGISTROS RELACIONADOS AO PEDIDO 110326:")
        print("-" * 80)

        # Tentar diferentes campos que podem relacionar com pedido
        campos_possiveis = [
            "PED_NUMEROOPERACAO",
            "NUMEROOPERACAO",
            "OPERACAO",
            "PEDIDO",
        ]

        for campo in campos_possiveis:
            if campo in colunas:
                try:
                    cursor.execute(
                        f"SELECT * FROM {tabela_receber} WHERE {campo} = 110326"
                    )
                    rows = cursor.fetchall()
                    if rows:
                        print(f"\nEncontrado via campo {campo}:")
                        for i, col in enumerate(colunas):
                            if rows[0][i] is not None:
                                print(f"  {col}: {rows[0][i]}")
                        break
                except:
                    pass

    cursor.close()
    conn.close()
    print("\n[OK] Investigação concluída!")


except Exception as e:
    print(f"[ERRO] Erro: {e}")

    import traceback

    traceback.print_exc()
