"""
Script para verificar índices na tabela PRODUTO do Firebird
Execute: python verificar_indices.py
"""
import sys
sys.path.append('.')
import fdb
import pandas as pd
from config import DB_CONFIG

print("=" * 80)
print("VERIFICADOR DE ÍNDICES - TABELA PRODUTO")
print("=" * 80)
print(f"\nBanco: {DB_CONFIG['dsn']}")
print(f"Usuário: {DB_CONFIG['user']}")
print(f"fbclient.dll: {DB_CONFIG['fb_library_name']}")
print("\nConectando...")

try:
    # Conectar usando config.py
    conn = fdb.connect(**DB_CONFIG)
    
    print("\n" + "=" * 80)
    print("ÍNDICES DA TABELA PRODUTO")
    print("=" * 80)
    
    # Query para listar índices
    query = """
    SELECT 
        i.RDB$INDEX_NAME AS INDICE,
        i.RDB$RELATION_NAME AS TABELA,
        s.RDB$FIELD_NAME AS CAMPO,
        i.RDB$UNIQUE_FLAG AS UNICO,
        i.RDB$INDEX_INACTIVE AS INATIVO
    FROM RDB$INDICES i
    LEFT JOIN RDB$INDEX_SEGMENTS s ON i.RDB$INDEX_NAME = s.RDB$INDEX_NAME
    WHERE i.RDB$RELATION_NAME = 'PRODUTO'
    ORDER BY i.RDB$INDEX_NAME, s.RDB$FIELD_POSITION
    """
    
    df = pd.read_sql(query, conn)
    
    if df.empty:
        print("\n⚠️  NENHUM ÍNDICE ENCONTRADO NA TABELA PRODUTO!")
        print("\nIsso explica a lentidão nas buscas.")
        print("\nRecomendação: Criar índice no campo PROD_CODIGO")
    else:
        print(f"\n✅ Encontrados {len(df)} índices:\n")
        
        # Agrupar por índice
        indices = df.groupby('INDICE')
        
        for nome_indice, grupo in indices:
            campos = ', '.join(grupo['CAMPO'].str.strip().tolist())
            unico = "ÚNICO" if grupo.iloc[0]['UNICO'] == 1 else "NÃO-ÚNICO"
            inativo = "INATIVO" if grupo.iloc[0]['INATIVO'] == 1 else "ATIVO"
            
            print(f"📌 {nome_indice.strip()}")
            print(f"   Campos: {campos}")
            print(f"   Tipo: {unico}")
            print(f"   Status: {inativo}")
            print()
        
        # Verificar se tem índice em PROD_CODIGO
        if 'PROD_CODIGO' in df['CAMPO'].str.strip().values:
            print("✅ PROD_CODIGO tem índice - Busca por código será rápida!")
        else:
            print("⚠️  PROD_CODIGO NÃO tem índice - Busca por código pode ser lenta")
            print("\nRecomendação SQL para criar índice:")
            print("CREATE INDEX IDX_PRODUTO_CODIGO ON PRODUTO(PROD_CODIGO);")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO CONCLUÍDA")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    
input("\nPressione ENTER para sair...")
