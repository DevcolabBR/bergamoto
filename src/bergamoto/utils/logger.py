"""
Sistema de logging para o Bergamoto
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logging(log_level: str = "INFO", 
                 log_dir: Optional[Path] = None,
                 max_size: int = 10 * 1024 * 1024,
                 backup_count: int = 5) -> None:
    """
    Configura o sistema de logging
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Diretório para arquivos de log (None = só console)
        max_size: Tamanho máximo do arquivo de log em bytes
        backup_count: Número de backups a manter
    """
    
    # Configurar o logger raiz
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Limpar handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formato das mensagens
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (se especificado)
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "bergamoto.log"
        
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger para o módulo especificado
    
    Args:
        name: Nome do módulo
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)