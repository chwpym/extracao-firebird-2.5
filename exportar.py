import os
import fdb
import pandas as pd
import config
from datetime import datetime

# Mapa de arquivos SQL para nomes de saída (sem extensão)
ENTIDADES = {
    'clientes': 'clientes',
    'produtos': 'produtos',
    'fornecedores': 'fornecedores',
    'entradas_saidas': 'entradas_saidas',
    'contas_pagar': 'contas_pagar',
    'contas_receber': 'contas_receber'
}

def conectar_banco():
    """Estabelece conexão com o banco Firebird"""
    try:
        con = fdb.connect(
            dsn=config.DB_CONFIG['dsn'],
            user=config.DB_CONFIG['user'],
            password=config.DB_CONFIG['password'],
            charset=config.DB_CONFIG['charset'],
            fb_library_name=config.DB_CONFIG.get('fb_library_name')
        )
        print(f"[{datetime.now()}] Conectado ao banco de dados com sucesso.")
        return con
    except Exception as e:
        print(f"Erro ao conectar no banco: {e}")
        return None

def ler_sql(nome_arquivo):
    """Lê o conteúdo do arquivo SQL"""
    caminho = os.path.join('sql', f'{nome_arquivo}.sql')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Arquivo SQL não encontrado: {caminho}")
        return None
    except Exception as e:
        print(f"Erro ao ler arquivo {caminho}: {e}")
        return None

def exportar_dados():
    """Função principal de exportação"""
    
    # Criar pasta output se não existir
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)
        print(f"Pasta '{config.OUTPUT_DIR}' criada.")

    con = conectar_banco()
    if not con:
        return

    try:
        for chave, nome_arquivo in ENTIDADES.items():
            print(f"\n--- Processando: {nome_arquivo} ---")
            
            sql_query = ler_sql(chave)
            if not sql_query:
                continue

            print(f"Executando consulta SQL...")
            
            try:
                # Usando pandas para ler diretamente do banco via SQL
                # O fdb cursor é passado como conexão
                df = pd.read_sql(sql_query, con)
                
                rows_count = len(df)
                print(f"Registros encontrados: {rows_count}")
                
                if rows_count > 0:
                    caminho_saida = os.path.join(config.OUTPUT_DIR, f'{nome_arquivo}.xlsx')
                    print(f"Salvando Excel em: {caminho_saida}")
                    
                    # Exportando para Excel sem index e sem formatar datas (raw data)
                    # Usando xlsxwriter para maior robustez com caracteres especiais
                    df.to_excel(caminho_saida, index=False, engine='xlsxwriter')
                    
                    print(f"Sucesso: {nome_arquivo}.xlsx gerado.")
                else:
                    print(f"Aviso: Nenhum dado retornado para {nome_arquivo}.")
                    
            except Exception as e:
                print(f"Erro ao processar {nome_arquivo}: {e}")

    finally:
        con.close()
        print(f"\n[{datetime.now()}] Conexão fechada. Processo finalizado.")

if __name__ == "__main__":
    exportar_dados()
