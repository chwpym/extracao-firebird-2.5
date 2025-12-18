import pandas as pd
import os
import logging
from tqdm import tqdm

logger = logging.getLogger("MigracaoFirebird")

class DataExporter:
    def __init__(self, db_connection, output_dir, sql_dir):
        self.con = db_connection
        self.output_dir = output_dir
        self.sql_dir = sql_dir
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export_entity(self, entity_name, start_date=None, end_date=None):
        """Executa um arquivo SQL e salva o resultado em Excel."""
        sql_path = os.path.join(self.sql_dir, f"{entity_name}.sql")
        excel_path = os.path.join(self.output_dir, f"{entity_name}.xlsx")
        
        if not os.path.exists(sql_path):
            logger.error(f"Arquivo SQL não encontrado: {sql_path}")
            return False
            
        logger.info(f"Processando: {entity_name}")
        
        try:
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql_query = f.read()

            # Substituição de parâmetros de data se fornecidos
            if start_date and end_date:
                sql_query = sql_query.replace(":DATA_INI", f"'{start_date}'")
                sql_query = sql_query.replace(":DATA_FIM", f"'{end_date}'")
            
            logger.info(f"Executando consulta SQL para {entity_name}...")
            
            # Usando read_sql diretamente
            df = pd.read_sql(sql_query, self.con)
            
            count = len(df)
            logger.info(f"Registros encontrados em {entity_name}: {count}")
            
            if count == 0:
                logger.warning(f"Nenhum dado retornado para {entity_name}.")
                # Cria um DF vazio com as colunas se possível, ou apenas pula
                if not df.empty:
                    df.to_excel(excel_path, index=False, engine='xlsxwriter')
                return True

            logger.info(f"Salvando Excel em: {excel_path}")
            
            # Exportação final
            df.to_excel(excel_path, index=False, engine='xlsxwriter')
            
            logger.info(f"Sucesso: {entity_name}.xlsx gerado.")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar {entity_name}: {e}")
            return False
