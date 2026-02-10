"""
TESTE DE PERFORMANCE DE FATURAMENTO
Mede tempos de resposta do banco para queries de faturamento.

DICA DE EDIÇÃO:
- Altere 'cliente_codigo', 'dt_ini' e 'dt_fim' no início do bloco 'try'
  para testar a performance com diferentes volumes de dados.
"""

import os
import sys

# Adiciona a raiz do projeto ao sys.path para permitir execuções diretas da pasta tools/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fdb

from config import DB_CONFIG
import time

try:
    conn = fdb.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cliente_codigo = 834
    dt_ini = "2025-01-01"
    dt_fim = "2025-12-31"

    print("=" * 80)
    print("TESTE DE PERFORMANCE - QUERIES OTIMIZADAS")
    print("=" * 80)
    print(f"Cliente: {cliente_codigo}")
    print(f"Período: {dt_ini} a {dt_fim}")
    print("=" * 80)

    # TESTE 1: Query TODOS
    print("\n1. TESTANDO QUERY 'TODOS'...")
    query_todos = """
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
        WHERE P.CLI_CODIGO = ?
          AND CAST(P.PED_DATAVENDA AS DATE) BETWEEN ? AND ?
        ORDER BY P.PED_DATAVENDA, P.PED_NUMEROOPERACAO
    """

    start = time.time()
    cursor.execute(query_todos, [cliente_codigo, dt_ini, dt_fim])
    rows_todos = cursor.fetchall()
    tempo_todos = time.time() - start

    print(f"   [OK] Tempo: {tempo_todos:.2f}s")

    print(f"   📊 Registros: {len(rows_todos)}")

    # TESTE 2: Query PAGOS (OTIMIZADA - INNER JOIN)
    print("\n2. TESTANDO QUERY 'PAGOS' (OTIMIZADA - INNER JOIN)...")
    query_pagos = """
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
        INNER JOIN RECEBER R ON P.PED_NUMEROOPERACAO = R.PED_NUMEROOPERACAO
        INNER JOIN RECEBTO RT ON R.REC_NUMEROOPERACAO = RT.REC_NUMEROOPERACAO
        WHERE P.CLI_CODIGO = ?
          AND CAST(P.PED_DATAVENDA AS DATE) BETWEEN ? AND ?
        ORDER BY P.PED_DATAVENDA, P.PED_NUMEROOPERACAO
    """

    start = time.time()
    cursor.execute(query_pagos, [cliente_codigo, dt_ini, dt_fim])
    rows_pagos = cursor.fetchall()
    tempo_pagos = time.time() - start

    print(f"   ✅ Tempo: {tempo_pagos:.2f}s")
    print(f"   📊 Registros: {len(rows_pagos)}")

    # TESTE 3: Query NÃO PAGOS (OTIMIZADA - LEFT JOIN + IS NULL)
    print("\n3. TESTANDO QUERY 'NÃO PAGOS' (OTIMIZADA - LEFT JOIN + IS NULL)...")
    query_nao_pagos = """
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
        INNER JOIN RECEBER R ON P.PED_NUMEROOPERACAO = R.PED_NUMEROOPERACAO
        LEFT JOIN RECEBTO RT ON R.REC_NUMEROOPERACAO = RT.REC_NUMEROOPERACAO
        WHERE P.CLI_CODIGO = ?
          AND CAST(P.PED_DATAVENDA AS DATE) BETWEEN ? AND ?
          AND RT.REC_NUMEROOPERACAO IS NULL
        ORDER BY P.PED_DATAVENDA, P.PED_NUMEROOPERACAO
    """

    start = time.time()
    cursor.execute(query_nao_pagos, [cliente_codigo, dt_ini, dt_fim])
    rows_nao_pagos = cursor.fetchall()
    tempo_nao_pagos = time.time() - start

    print(f"   ✅ Tempo: {tempo_nao_pagos:.2f}s")
    print(f"   📊 Registros: {len(rows_nao_pagos)}")

    # VALIDAÇÃO
    print("\n" + "=" * 80)
    print("VALIDAÇÃO:")
    print("=" * 80)
    total_esperado = len(rows_todos)
    total_calculado = len(rows_pagos) + len(rows_nao_pagos)

    print(f"Total de registros:     {total_esperado}")
    print(f"Pagos:                  {len(rows_pagos)}")
    print(f"Não Pagos:              {len(rows_nao_pagos)}")
    print(f"Soma (Pagos + Não):     {total_calculado}")

    if total_esperado == total_calculado:
        print("\n[OK] VALIDAÇÃO OK! Pagos + Não Pagos = Total")

    else:
        print(
            f"\n⚠️  ATENÇÃO! Diferença de {abs(total_esperado - total_calculado)} registros"
        )

    # RESUMO
    print("\n" + "=" * 80)
    print("RESUMO DE PERFORMANCE:")
    print("=" * 80)
    print(f"Todos:       {tempo_todos:.2f}s")
    print(f"Pagos:       {tempo_pagos:.2f}s")
    print(f"Não Pagos:   {tempo_nao_pagos:.2f}s")

    tempo_medio = (tempo_todos + tempo_pagos + tempo_nao_pagos) / 3
    print(f"\nTempo médio: {tempo_medio:.2f}s")

    if tempo_medio < 2:
        print("🚀 EXCELENTE! Queries muito rápidas!")
    elif tempo_medio < 5:
        print("✅ BOM! Performance aceitável")
    else:
        print("⚠️  LENTO! Pode precisar de otimização adicional")

    cursor.close()
    conn.close()
    print("\n[OK] Teste concluído!")


except Exception as e:
    print(f"[ERRO] Erro: {e}")

    import traceback

    traceback.print_exc()
