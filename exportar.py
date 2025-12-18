import os
import config
from core.database import FirebirdDB
from core.exporter import DataExporter
from utils.logger import setup_logger

def run_cli_extraction():
    # Inicializa Logger
    logger = setup_logger()
    logger.info("Iniciando extração via CLI...")

    # Configura Banco
    db = FirebirdDB(config.DB_CONFIG)
    if not db.connect():
        return

    # Configura Exportador
    sql_dir = os.path.join(config.BASE_DIR, 'sql')
    exporter = DataExporter(db.get_connection(), config.OUTPUT_DIR, sql_dir)

    # Entidades para exportar
    entities = [
        'clientes',
        'produtos',
        'fornecedores',
        'entradas_saidas',
        'contas_pagar',
        'contas_receber'
    ]

    for entity in entities:
        exporter.export_entity(entity)

    db.close()
    logger.info("Extração CLI finalizada. Resultados na pasta output/.")

if __name__ == "__main__":
    run_cli_extraction()
