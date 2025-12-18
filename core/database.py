import fdb
import logging

logger = logging.getLogger("MigracaoFirebird")

class FirebirdDB:
    def __init__(self, config):
        self.config = config
        self.con = None

    def connect(self):
        try:
            self.con = fdb.connect(
                dsn=self.config['dsn'],
                user=self.config['user'],
                password=self.config['password'],
                charset=self.config['charset'],
                fb_library_name=self.config.get('fb_library_name')
            )
            logger.info("Conectado ao banco de dados com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao Firebird: {e}")
            return False

    def close(self):
        if self.con:
            self.con.close()
            logger.info("Conexão com o banco de dados fechada.")

    def get_connection(self):
        return self.con
