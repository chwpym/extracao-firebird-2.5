"""
INVESTIGAÇÃO DE ITENS DE PEDIDO
Detalha as colunas e dados da tabela PEDITENS para um pedido específico.

DICA DE EDIÇÃO:
- Altere o valor de 'num_op = 119369' para o número da operação
  do pedido que você deseja investigar.
"""

import os
import sys

# Adiciona a raiz do projeto ao sys.path para permitir execuções diretas da pasta tools/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fdb

import config

conn = fdb.connect(
    dsn=config.DB_CONFIG["dsn"],
    user=config.DB_CONFIG["user"],
    password=config.DB_CONFIG["password"],
    charset=config.DB_CONFIG["charset"],
    fb_library_name=config.DB_CONFIG["fb_library_name"],
)

cursor = conn.cursor()
num_op = 119369

print(f"\n=== TESTANDO PEDITENS ===\n")

# Ver estrutura
print("1. Estrutura da PEDITENS:")
cursor.execute(
    """
    SELECT RDB$FIELD_NAME
    FROM RDB$RELATION_FIELDS
    WHERE RDB$RELATION_NAME = 'PEDITENS'
    ORDER BY RDB$FIELD_POSITION
"""
)
cols = [row[0].strip() for row in cursor.fetchall()]
for col in cols:
    print(f"   {col}")

# Buscar itens do pedido
print(f"\n2. Itens do pedido {num_op}:")
cursor.execute("SELECT * FROM PEDITENS WHERE PED_NUMEROOPERACAO = ?", [num_op])
rows = cursor.fetchall()
print(f"   Encontrados: {len(rows)} itens")

if rows:
    print(f"\n3. Colunas retornadas:")
    col_names = [desc[0] for desc in cursor.description]
    for i, col in enumerate(col_names):
        print(f"   [{i}] {col}")

    print(f"\n4. Exemplo de item:")
    for i, val in enumerate(rows[0]):
        print(f"   [{i}] {col_names[i]}: {val}")

# Buscar com JOIN no PRODUTO
print(f"\n5. Itens com descrição do produto:")
cursor.execute(
    """
    SELECT 
        I.PROD_CODIGO,
        P.PROD_DESCRICAOPRODUTO,
        I.PEDI_QTDE,
        I.PEDI_VALORUNITARIO,
        (I.PEDI_QTDE * I.PEDI_VALORUNITARIO) AS TOTAL
    FROM PEDITENS I
    LEFT JOIN PRODUTO P ON I.PROD_CODIGO = P.PROD_CODIGO
    WHERE I.PED_NUMEROOPERACAO = ?
    ORDER BY I.PROD_CODIGO
""",
    [num_op],
)
rows = cursor.fetchall()
print(f"   Encontrados: {len(rows)} itens")
if rows:
    for row in rows:
        print(
            f"   Código: {row[0]}, Desc: {row[1]}, Qtde: {row[2]}, Vr.Unit: {row[3]}, Total: {row[4]}"
        )

conn.close()
print("\n=== FIM ===\n")
