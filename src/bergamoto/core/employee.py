"""
Serviço para gerenciamento de funcionários
"""
from typing import List, Optional
from datetime import datetime

from ..database.manager import DatabaseManager
from ..database.models import Employee
from ..utils.logger import get_logger


class EmployeeService:
    """Serviço para operações com funcionários"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = get_logger(__name__)
    
    def create_employee(self, pin: str, name: str, setor: str, supervisor: str = '') -> bool:
        """
        Cria um novo funcionário
        
        Args:
            pin: PIN único do funcionário
            name: Nome do funcionário
            setor: Setor onde trabalha
            supervisor: Nome do supervisor
            
        Returns:
            True se criado com sucesso, False caso contrário
        """
        try:
            # Verificar se PIN já existe
            if self.get_employee_by_pin(pin):
                self.logger.warning(f"PIN {pin} já existe")
                return False
            
            employee = Employee(
                pin=pin,
                name=name,
                setor=setor,
                supervisor=supervisor
            )
            
            employee_id = self.db.create_employee(employee)
            if employee_id > 0:
                self.logger.info(f"Funcionário criado: {name} (PIN: {pin})")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao criar funcionário: {e}")
            return False
    
    def get_employee_by_pin(self, pin: str) -> Optional[Employee]:
        """
        Busca funcionário pelo PIN
        
        Args:
            pin: PIN do funcionário
            
        Returns:
            Employee se encontrado, None caso contrário
        """
        try:
            return self.db.get_employee_by_pin(pin)
        except Exception as e:
            self.logger.error(f"Erro ao buscar funcionário por PIN {pin}: {e}")
            return None
    
    def get_all_employees(self, active_only: bool = True) -> List[Employee]:
        """
        Lista todos os funcionários
        
        Args:
            active_only: Se True, retorna apenas funcionários ativos
            
        Returns:
            Lista de funcionários
        """
        try:
            return self.db.get_all_employees(active_only)
        except Exception as e:
            self.logger.error(f"Erro ao listar funcionários: {e}")
            return []
    
    def deactivate_employee(self, pin: str) -> bool:
        """
        Desativa um funcionário (não remove do banco)
        
        Args:
            pin: PIN do funcionário
            
        Returns:
            True se desativado com sucesso
        """
        # TODO: Implementar desativação
        self.logger.info(f"Funcionalidade de desativação a ser implementada para PIN {pin}")
        return False
    
    def validate_employee_data(self, pin: str, name: str, setor: str) -> List[str]:
        """
        Valida dados de funcionário
        
        Args:
            pin: PIN do funcionário
            name: Nome do funcionário  
            setor: Setor do funcionário
            
        Returns:
            Lista de erros encontrados (vazia se válido)
        """
        errors = []
        
        if not pin or len(pin) < 4:
            errors.append("PIN deve ter pelo menos 4 caracteres")
        
        if not name or len(name.strip()) < 2:
            errors.append("Nome deve ter pelo menos 2 caracteres")
        
        if not setor or len(setor.strip()) < 2:
            errors.append("Setor deve ser especificado")
        
        # Verificar se PIN contém apenas números
        if pin and not pin.isdigit():
            errors.append("PIN deve conter apenas números")
        
        return errors