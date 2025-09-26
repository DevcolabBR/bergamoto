"""
Configurações centralizadas do sistema Bergamoto
"""
import os
import platform
from pathlib import Path
from typing import Dict, Any

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent

# Detectar sistema operacional
OS_TYPE = platform.system().lower()

class DatabaseConfig:
    """Configurações do banco de dados"""
    
    def __init__(self):
        self.name = "bergamoto.db"
        self.data_dir = self._get_data_directory()
        self.path = self.data_dir / self.name
        
    def _get_data_directory(self) -> Path:
        """Determina o diretório de dados baseado no SO"""
        if OS_TYPE == "windows":
            # Windows: usar diretório do usuário
            data_dir = Path.home() / "AppData" / "Local" / "Bergamoto" / "data"
        else:
            # Linux/Mac: usar diretório do projeto
            data_dir = PROJECT_ROOT / "data"
        
        # Criar diretório se não existir
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

class UIConfig:
    """Configurações da interface"""
    THEME = "equilux"
    FULLSCREEN = True
    WINDOW_TITLE = "Bergamoto - Sistema de Ponto"
    FONT_FAMILY = "Helvetica"
    FONT_SIZE = 16
    AUTO_PHOTO_DELAY = 3000  # 3 segundos
    MAX_RECORDS_PER_DAY = 4

class CameraConfig:
    """Configurações da câmera"""
    DEVICE_INDEX = 0
    FRAME_UPDATE_INTERVAL = 10  # ms
    PHOTO_FORMAT = "PNG"
    MAX_PHOTO_REFERENCES = 10

class LoggingConfig:
    """Configurações de logging"""
    LEVEL = "INFO"
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR = PROJECT_ROOT / "logs"
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5

# Instâncias globais das configurações
database_config = DatabaseConfig()
ui_config = UIConfig()
camera_config = CameraConfig()
logging_config = LoggingConfig()

# Configurações do CSV de pessoas
PEOPLE_CSV_PATH = database_config.data_dir / "people.csv"

# Configurações de thread safety
PHOTO_WINDOW_LOCK_TIMEOUT = 0.1

def get_all_configs() -> Dict[str, Any]:
    """Retorna todas as configurações em um dicionário"""
    return {
        "database": {
            "path": str(database_config.path),
            "data_dir": str(database_config.data_dir),
        },
        "ui": {
            "theme": ui_config.THEME,
            "fullscreen": ui_config.FULLSCREEN,
            "title": ui_config.WINDOW_TITLE,
        },
        "camera": {
            "device_index": camera_config.DEVICE_INDEX,
            "photo_format": camera_config.PHOTO_FORMAT,
        },
        "system": {
            "os_type": OS_TYPE,
            "project_root": str(PROJECT_ROOT),
        }
    }