import logging
import os
from datetime import datetime

def setup_logger(log_dir="logs"):
    """Configura o logger para imprimir no terminal e salvar em arquivo."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, f"extracao_{datetime.now().strftime('%Y%m%d')}.log")
    
    logger = logging.getLogger("MigracaoFirebird")
    logger.setLevel(logging.INFO)
    
    # Formato das mensagens
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    # Handler para terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Evita duplicação de handlers se a função for chamada múltiplas vezes
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
    return logger
