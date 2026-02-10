"""
INVESTIGAÇÃO DE RECEBIMENTOS (RECEBTO)
Analisa detalhadamente as baixas de títulos e formas de pagamento.
Útil para entender o vínculo entre duplicatas e o caixa/banco.
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
    print("INVESTIGANDO TABELA RECEBTO (Recebimentos/Quitações)")
    print("=" * 80)

    # Listar colunas da tabela RECEBTO
    cursor.execute(
        """
        SELECT RDB$FIELD_NAME
        FROM RDB$RELATION_FIELDS
        WHERE RDB$RELATION_NAME = 'RECEBTO'
        ORDER BY RDB$FIELD_POSITION
    """
    )

    colunas = [row[0].strip() for row in cursor.fetchall()]

    print("\nCOLUNAS DA TABELA RECEBTO:")
    print("-" * 80)
    for i, col in enumerate(colunas, 1):
        print(f"{i:3d}. {col}")

    # Buscar registros relacionados ao REC_NUMEROOPERACAO 109724 (do pedido 110326)
    print("\n\nREGISTROS RELACIONADOS AO REC_NUMEROOPERACAO 109724:")
    print("-" * 80)

    cursor.execute("SELECT * FROM RECEBTO WHERE REC_NUMEROOPERACAO = 109724")
    rows = cursor.fetchall()

    if rows:
        print(f"Encontrados {len(rows)} registro(s):\n")
        for row in rows:
            for i, col in enumerate(colunas):
                if row[i] is not None:
                    print(f"  {col}: {row[i]}")
            print("-" * 80)
    else:
        print("Nenhum registro encontrado (pedido ainda não foi quitado)")

    # Verificar lógica: se existe registro em RECEBTO = PAGO, se não existe = NÃO PAGO
    print("\n\nLÓGICA DE PAGAMENTO:")
    print("-" * 80)
    print("Se existe registro em RECEBTO para o REC_NUMEROOPERACAO:")
    print("  → Pedido PAGO (total ou parcialmente)")
    print("Se NÃO existe registro em RECEBTO:")
    print("  → Pedido NÃO PAGO (em aberto)")

    # Testar com um pedido que provavelmente está pago
    print("\n\nTESTANDO COM OUTROS PEDIDOS:")
    print("-" * 80)

    cursor.execute(
        """
        SELECT FIRST 5 R.REC_NUMEROOPERACAO, R.PED_NUMEROOPERACAO, R.REC_VALORTOTAL,
               (SELECT COUNT(*) FROM RECEBTO RT WHERE RT.REC_NUMEROOPERACAO = R.REC_NUMEROOPERACAO) AS TEM_RECEBTO
        FROM RECEBER R
        ORDER BY R.REC_DATAEMISSAO DESC
    """
    )

    rows = cursor.fetchall()
    print("\nÚltimos 5 registros:")
    for row in rows:
        status = "PAGO" if row[3] > 0 else "NÃO PAGO"
        print(
            f"  REC_OP: {row[0]}, PED: {row[1]}, Valor: R$ {row[2]:.2f}, Status: {status}"
        )

    cursor.close()
    conn.close()
    print("\n[OK] Investigação concluída!")


except Exception as e:
    print(f"[ERRO] Erro: {e}")

    import traceback

    traceback.print_exc()
