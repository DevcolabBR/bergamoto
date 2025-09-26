"""
Bergamoto - Sistema de Registro de Ponto Eletrônico

Pacote principal que fornece funcionalidades para:
- Registro de ponto com captura de foto
- Gerenciamento de funcionários  
- Análise de horas trabalhadas
- Interface gráfica unificada

Versão: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "DevcolabBR"
__license__ = "MIT"

from .core import BergamotoApp, EmployeeService, TimesheetService
from .database import DatabaseManager
from .utils import get_logger, setup_logging

__all__ = [
    'BergamotoApp',
    'EmployeeService', 
    'TimesheetService',
    'DatabaseManager',
    'get_logger',
    'setup_logging'
]