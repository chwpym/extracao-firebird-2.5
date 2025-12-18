import os
import sys

# Adiciona o diretório pai ao path para encontrar o config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fdb
import config
import pandas as pd

def inspect():
    con = fdb.connect(
        dsn=config.DB_CONFIG['dsn'],
        user=config.DB_CONFIG['user'],
        password=config.DB_CONFIG['password'],
        charset=config.DB_CONFIG['charset'],
        fb_library_name=config.DB_CONFIG.get('fb_library_name')
    )
    cur = con.cursor()

    print("--- TABLE: EXTRATOPRODUTO ---")
    try:
        cur.execute("SELECT FIRST 1 * FROM EXTRATOPRODUTO")
        print("Columns:", [d[0] for d in cur.description])
    except Exception as e:
        print(f"Error reading table: {e}")

    print("\n--- PROCEDURE: EXTRATOPRODUTOS ---")
    try:
        # Query system tables to find procedure parameters
        sql_params = """
        SELECT RDB$PARAMETER_NAME, RDB$PARAMETER_TYPE
        FROM RDB$PROCEDURE_PARAMETERS
        WHERE RDB$PROCEDURE_NAME = 'EXTRATOPRODUTOS'
        ORDER BY RDB$PARAMETER_NUMBER
        """
        cur.execute(sql_params)
        params = cur.fetchall()
        print("Parameters (Name, Type 0=Input 1=Output):")
        for p in params:
            io = "Output" if p[1] == 1 else "Input"
            print(f"  {p[0].strip()} ({io})")
            
    except Exception as e:
        print(f"Error inspecting procedure: {e}")

    con.close()

if __name__ == "__main__":
    inspect()
