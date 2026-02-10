"""
TESTE DE FATURAMENTO POR CLIENTE
Analisa a estrutura de pedidos e itens vinculados a clientes.
Gera um resumo de quantidade e valor total para validação de faturamento.
"""

import os
import sys

# Adiciona a raiz do projeto ao sys.path para permitir execuções diretas da pasta tools/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fdb

from config import DB_CONFIG
from datetime import datetime

try:
    conn = fdb.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("=" * 80)
    print("TESTE: Estrutura de Vendas por Cliente")
    print("=" * 80)

    # Testar query de vendas por cliente
    query = """
        SELECT FIRST 10
            P.PED_NUMEROOPERACAO,
            P.PED_DATAVENDA,
            P.CLI_CODIGO,
            C.CLI_NOME,
            I.PROD_CODIGO,
            PR.PROD_DESCRICAOPRODUTO,
            I.PIT_QTDEVENDIDA,
            I.PIT_VALORUNITARIO,
            (I.PIT_QTDEVENDIDA * I.PIT_VALORUNITARIO) AS VL_TOTAL
        FROM PEDIDO P
        INNER JOIN PEDITENS I ON P.PED_NUMEROOPERACAO = I.PED_NUMEROOPERACAO
        LEFT JOIN PRODUTO PR ON I.PROD_CODIGO = PR.PROD_CODIGO
        LEFT JOIN CLIENTE C ON P.CLI_CODIGO = C.CLI_CODIGO
        WHERE P.CLI_CODIGO IS NOT NULL
        ORDER BY P.PED_DATAVENDA DESC
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    print(f"\n[OK] Query executada com sucesso!")

    print(f"📊 Registros encontrados: {len(rows)}\n")

    if rows:
        print("EXEMPLO DE DADOS:")
        print("-" * 80)
        for row in rows[:3]:
            print(f"Pedido: {row[0]}")
            print(f"Data: {row[1]}")
            print(f"Cliente: {row[2]} - {row[3]}")
            print(f"Produto: {row[4]} - {row[5]}")
            print(f"Qtde: {row[6]}, Vl Unit: R$ {row[7]:.2f}, Total: R$ {row[8]:.2f}")
            print("-" * 80)

    # Testar busca por cliente específico
    print("\n\nTESTE: Busca por cliente específico (código 12)")
    print("=" * 80)

    query_cliente = """
        SELECT 
            P.PED_NUMEROOPERACAO,
            P.PED_DATAVENDA,
            I.PROD_CODIGO,
            PR.PROD_DESCRICAOPRODUTO,
            I.PIT_QTDEVENDIDA,
            I.PIT_VALORUNITARIO,
            (I.PIT_QTDEVENDIDA * I.PIT_VALORUNITARIO) AS VL_TOTAL
        FROM PEDIDO P
        INNER JOIN PEDITENS I ON P.PED_NUMEROOPERACAO = I.PED_NUMEROOPERACAO
        LEFT JOIN PRODUTO PR ON I.PROD_CODIGO = PR.PROD_CODIGO
        WHERE P.CLI_CODIGO = 12
        ORDER BY P.PED_DATAVENDA DESC
    """

    cursor.execute(query_cliente)
    rows_cliente = cursor.fetchall()

    print(f"[OK] Vendas para cliente 12: {len(rows_cliente)} itens")

    if rows_cliente:
        total_qtde = sum(row[4] for row in rows_cliente if row[4])
        total_valor = sum(row[6] for row in rows_cliente if row[6])
        print(f"📊 Total Quantidade: {total_qtde:.2f}")
        print(f"💰 Total Valor: R$ {total_valor:,.2f}")

    cursor.close()
    conn.close()
    print("\n[OK] Teste concluído com sucesso!")


except Exception as e:
    print(f"[ERRO] Erro: {e}")

    import traceback

    traceback.print_exc()
