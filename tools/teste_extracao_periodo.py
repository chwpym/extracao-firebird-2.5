"""
TESTE DE EXTRAÇÃO POR PERÍODO
Valida se os filtros de data estão funcionando corretamente.

DICA DE EDIÇÃO:
- Altere 'start_date' e 'end_date' dentro da função 'test_extraction'
  para testar outros intervalos de tempo.
"""

import fdb

import pandas as pd
import os
from config import DB_CONFIG
from core.exporter import DataExporter


def test_extraction():
    try:
        conn = fdb.connect(**DB_CONFIG)

        # Setup exporter
        output_dir = "output_test"
        sql_dir = "sql"
        exporter = DataExporter(conn, output_dir, sql_dir)

        print("Iniciando extração de teste...")
        # Testar Contas a Receber Aberto
        success = exporter.export_entity(
            "contas_receber_aberto",
            start_date="2025-12-01",
            end_date="2025-12-25",
            date_field="d.RED_DATAVENCIMENTO",
        )

        if success:
            print("Extração concluída com sucesso!")
            excel_path = os.path.join(output_dir, "contas_receber_aberto.xlsx")
            if os.path.exists(excel_path):
                df = pd.read_excel(excel_path)
                print("\nCABEÇALHOS GERADOS:")
                print(df.columns.tolist())
                print("\nPRIMEIRAS 2 LINHAS:")
                print(df.head(2).to_string())
        else:
            print("Falha na extração.")

        conn.close()
    except Exception as e:
        print(f"Erro no teste: {e}")


if __name__ == "__main__":
    test_extraction()
