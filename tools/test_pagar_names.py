import os
import sys

# Adiciona o diretório pai ao path para encontrar o config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fdb
import config
import pandas as pd

def test_pagar_names():
    con = fdb.connect(
        dsn=config.DB_CONFIG['dsn'],
        user=config.DB_CONFIG['user'],
        password=config.DB_CONFIG['password'],
        charset=config.DB_CONFIG['charset'],
        fb_library_name=config.DB_CONFIG.get('fb_library_name')
    )
    
    # Testando com data de 2024 para garantir que venha dados e possamos ver os nomes
    sql = """
    SELECT FIRST 5
        p.PAG_NUMEROOPERACAO,
        p.FOR_CODIGO,
        (SELECT f.FOR_NOME FROM FORNECEDOR f WHERE f.FOR_CODIGO = p.FOR_CODIGO) AS FOR_NOME,
        d.PAD_VALORPARCELA
    FROM PAGDET d
    JOIN PAGAR p ON d.PAG_NUMEROOPERACAO = p.PAG_NUMEROOPERACAO
    ORDER BY p.PAG_DATAEMISSAO DESC
    """
    
    try:
        df = pd.read_sql(sql, con)
        print("\nResultado do teste de nomes no Contas a Pagar:")
        print(df.to_string(index=False))
    except Exception as e:
        print(f"Erro no teste: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    test_pagar_names()
