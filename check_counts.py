import fdb
import config

TABLES_TO_CHECK = [
    # Cadastros
    'CLIENTE', 'PRODUTO', 'FORNECEDOR',
    # Financeiro Pagar
    'PAGAR', 'PAGDET', 'PAGTO',
    # Financeiro Receber
    'RECEBER', 'RECDET', 'RECEBTO',
    # Movimentação / Estoque
    'EXTRATOPRODUTO',
    'ENTRADA', 'ENTITENS',
    'PEDIDO', 'PEDITENS',
    'PRODDIARIO',
    'NOTAFISCAL', 'NTFISCAL', 'NOTAITENS'
]

def check_counts():
    con = fdb.connect(
        dsn=config.DB_CONFIG['dsn'],
        user=config.DB_CONFIG['user'],
        password=config.DB_CONFIG['password'],
        charset=config.DB_CONFIG['charset'],
        fb_library_name=config.DB_CONFIG.get('fb_library_name')
    )
    cur = con.cursor()
    
    print(f"{'TABELA':<20} | {'REGISTROS':<10}")
    print("-" * 35)
    
    for table in TABLES_TO_CHECK:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"{table:<20} | {count:<10}")
        except Exception as e:
            # Tabela pode não existir ou ter outro nome
            print(f"{table:<20} | (Erro/Inexistente)")

    con.close()

if __name__ == "__main__":
    check_counts()
