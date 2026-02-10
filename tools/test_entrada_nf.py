"""
INVESTIGAÇÃO DE ENTRADAS DE NF
Analisa as tabelas ENTRADA e ENTITENS para mapear o fluxo de compras.
Tenta realizar um JOIN exemplo com FORNECEDOR para validar a integridade.
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

print("\n=== INVESTIGANDO TABELAS DE ENTRADA DE NF ===\n")

# 1. Estrutura da ENTRADA
print("1. Estrutura da ENTRADA:")
cursor.execute(
    """
    SELECT RDB$FIELD_NAME
    FROM RDB$RELATION_FIELDS
    WHERE RDB$RELATION_NAME = 'ENTRADA'
    ORDER BY RDB$FIELD_POSITION
"""
)
entrada_cols = [row[0].strip() for row in cursor.fetchall()]
for col in entrada_cols:
    print(f"   {col}")

# 2. Estrutura da ENTITENS
print("\n2. Estrutura da ENTITENS:")
cursor.execute(
    """
    SELECT RDB$FIELD_NAME
    FROM RDB$RELATION_FIELDS
    WHERE RDB$RELATION_NAME = 'ENTITENS'
    ORDER BY RDB$FIELD_POSITION
"""
)
entitens_cols = [row[0].strip() for row in cursor.fetchall()]
for col in entitens_cols:
    print(f"   {col}")

# 3. Buscar uma entrada de exemplo
print("\n3. Exemplo de entrada (primeira):")
cursor.execute("SELECT FIRST 1 * FROM ENTRADA ORDER BY ENT_NUMEROOPERACAO DESC")
row = cursor.fetchone()
if row:
    col_names = [desc[0] for desc in cursor.description]
    for i, val in enumerate(row):
        print(f"   {col_names[i]}: {val}")

# 4. Buscar itens de exemplo
print("\n4. Exemplo de itens da entrada:")
if row:
    num_op = row[0]  # Assumindo que é a primeira coluna
    cursor.execute(
        f"SELECT FIRST 3 * FROM ENTITENS WHERE ENT_NUMEROOPERACAO = ?", [num_op]
    )
    items = cursor.fetchall()
    print(f"   Encontrados {len(items)} itens para operação {num_op}")
    if items:
        col_names = [desc[0] for desc in cursor.description]
        print(f"   Colunas: {col_names}")

# 5. Verificar relacionamento com FORNECEDOR
print("\n5. Teste de JOIN com FORNECEDOR:")
cursor.execute(
    """
    SELECT FIRST 1
        E.ENT_NUMEROOPERACAO,
        E.ENT_NUMERONOTA,
        F.FOR_NOME,
        E.ENT_DATAENTRADA
    FROM ENTRADA E
    LEFT JOIN FORNECEDOR F ON E.FOR_CODIGO = F.FOR_CODIGO
    ORDER BY E.ENT_NUMEROOPERACAO DESC
"""
)
row = cursor.fetchone()
if row:
    print(f"   Operação: {row[0]}, NF: {row[1]}, Fornecedor: {row[2]}, Data: {row[3]}")

conn.close()
print("\n=== FIM ===\n")
