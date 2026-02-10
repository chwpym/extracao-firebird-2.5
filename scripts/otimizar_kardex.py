"""
Script para verificar e criar índices de otimização do Kardex

Este script:
1. Verifica quais índices já existem
2. Cria apenas os índices que estão faltando
3. Exibe relatório de índices criados
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import FirebirdDB
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Definir índices necessários
INDICES_NECESSARIOS = [
    {
        'nome': 'IDX_PEDITENS_PROD',
        'tabela': 'PEDITENS',
        'coluna': 'PROD_CODIGO',
        'descricao': 'Índice por produto em PEDITENS'
    },
    {
        'nome': 'IDX_PEDITENS_PEDOP',
        'tabela': 'PEDITENS',
        'coluna': 'PED_NUMEROOPERACAO',
        'descricao': 'Índice por operação em PEDITENS'
    },
    {
        'nome': 'IDX_PEDIDO_DATA',
        'tabela': 'PEDIDO',
        'coluna': 'PED_DATAVENDA',
        'descricao': 'Índice por data em PEDIDO'
    },
    {
        'nome': 'IDX_ENTITENS_PROD',
        'tabela': 'ENTITENS',
        'coluna': 'PROD_CODIGO',
        'descricao': 'Índice por produto em ENTITENS'
    },
    {
        'nome': 'IDX_ENTITENS_ENTOP',
        'tabela': 'ENTITENS',
        'coluna': 'ENT_NUMEROOPERACAO',
        'descricao': 'Índice por operação em ENTITENS'
    },
    {
        'nome': 'IDX_ENTRADA_DATA',
        'tabela': 'ENTRADA',
        'coluna': 'ENT_DATAENTRADA',
        'descricao': 'Índice por data em ENTRADA'
    }
]

def verificar_indices_existentes(db):
    """Verifica quais índices já existem no banco"""
    query = """
    SELECT 
        RDB$INDEX_NAME,
        RDB$RELATION_NAME,
        RDB$UNIQUE_FLAG
    FROM RDB$INDICES
    WHERE RDB$RELATION_NAME IN ('PEDITENS', 'PEDIDO', 'ENTITENS', 'ENTRADA')
      AND RDB$SYSTEM_FLAG = 0
    ORDER BY RDB$RELATION_NAME, RDB$INDEX_NAME
    """
    
    cursor = db.get_connection().cursor()
    cursor.execute(query)
    
    indices_existentes = set()
    for row in cursor.fetchall():
        nome_indice = row[0].strip() if row[0] else ''
        indices_existentes.add(nome_indice)
    
    cursor.close()
    return indices_existentes

def criar_indice(db, indice):
    """Cria um índice no banco"""
    sql = f"CREATE INDEX {indice['nome']} ON {indice['tabela']}({indice['coluna']})"
    
    try:
        cursor = db.get_connection().cursor()
        cursor.execute(sql)
        db.get_connection().commit()
        cursor.close()
        logging.info(f"✓ Criado: {indice['nome']} - {indice['descricao']}")
        return True
    except Exception as e:
        logging.error(f"✗ Erro ao criar {indice['nome']}: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("OTIMIZAÇÃO DE PERFORMANCE DO KARDEX")
    print("Criando índices no banco de dados")
    print("=" * 60)
    print()
    
    # Carregar configuração e conectar ao banco
    from config import DB_CONFIG
    db = FirebirdDB(DB_CONFIG)
    db.connect()
    
    try:
        # Verificar índices existentes
        logging.info("Verificando índices existentes...")
        indices_existentes = verificar_indices_existentes(db)
        
        print()
        print(f"Índices existentes nas tabelas: {len(indices_existentes)}")
        print()
        
        # Criar índices faltantes
        criados = 0
        ja_existentes = 0
        erros = 0
        
        for indice in INDICES_NECESSARIOS:
            if indice['nome'] in indices_existentes:
                logging.info(f"○ Já existe: {indice['nome']}")
                ja_existentes += 1
            else:
                if criar_indice(db, indice):
                    criados += 1
                else:
                    erros += 1
        
        # Relatório final
        print()
        print("=" * 60)
        print("RELATÓRIO FINAL")
        print("=" * 60)
        print(f"Índices criados:      {criados}")
        print(f"Já existentes:        {ja_existentes}")
        print(f"Erros:                {erros}")
        print(f"Total necessários:    {len(INDICES_NECESSARIOS)}")
        print("=" * 60)
        
        if criados > 0:
            print()
            print("✓ Otimização concluída com sucesso!")
            print("  A performance do Kardex deve melhorar significativamente.")
        elif ja_existentes == len(INDICES_NECESSARIOS):
            print()
            print("✓ Todos os índices já estavam criados!")
        
    except Exception as e:
        logging.error(f"Erro: {e}")
        return 1
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
