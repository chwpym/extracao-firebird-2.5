import os

# Caminho base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurações de Conexão com o Banco de Dados Firebird
# Ajuste o caminho do banco (database) para o local correto do seu arquivo .fdb ou .gdb

DB_CONFIG = {
    'dsn': 'localhost:D:/DELPHI/bd/SGCADM.FDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'WIN1252',
    # Aponta para a DLL na mesma pasta do script
    'fb_library_name': os.path.join(BASE_DIR, 'fbclient.dll')
}

# Configurações de Exportação
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
