"""
Testes básicos para o sistema Bergamoto
"""
import pytest
import tempfile
import sqlite3
from pathlib import Path
import sys

# Adicionar src ao path para testes
test_dir = Path(__file__).parent
project_root = test_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


class TestDatabaseManager:
    """Testes para o gerenciador de banco de dados"""
    
    def setup_method(self):
        """Configuração antes de cada teste"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_bergamoto.db"
        
    def test_database_creation(self):
        """Testa criação do banco de dados"""
        from bergamoto.database.manager import DatabaseManager
        
        # Criar gerenciador
        db_manager = DatabaseManager(self.db_path)
        
        # Verificar se o arquivo foi criado
        assert self.db_path.exists()
        
        # Verificar se as tabelas foram criadas
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['employees', 'time_records', 'daily_summaries', 'system_config']
            for table in expected_tables:
                assert table in tables, f"Tabela {table} não foi criada"
    
    def test_employee_operations(self):
        """Testa operações com funcionários"""
        from bergamoto.database.manager import DatabaseManager
        from bergamoto.database.models import Employee
        
        db_manager = DatabaseManager(self.db_path)
        
        # Criar funcionário
        employee = Employee(
            pin="1234",
            name="João Silva",
            setor="vendas",
            supervisor="Maria Santos"
        )
        
        employee_id = db_manager.create_employee(employee)
        assert employee_id > 0
        
        # Buscar funcionário
        found_employee = db_manager.get_employee_by_pin("1234")
        assert found_employee is not None
        assert found_employee.name == "João Silva"
        assert found_employee.pin == "1234"
        
        # Buscar funcionário inexistente
        not_found = db_manager.get_employee_by_pin("9999")
        assert not_found is None
    
    def test_time_record_operations(self):
        """Testa operações com registros de ponto"""
        from bergamoto.database.manager import DatabaseManager
        from bergamoto.database.models import Employee, TimeRecord
        
        db_manager = DatabaseManager(self.db_path)
        
        # Criar funcionário
        employee = Employee(pin="1234", name="João Silva", setor="vendas")
        employee_id = db_manager.create_employee(employee)
        
        # Criar registro
        record = TimeRecord(
            employee_id=employee_id,
            date="26-09-2025",
            time="08:00:00",
            record_type="entrada"
        )
        
        success = db_manager.insert_time_record(record)
        assert success
        
        # Buscar registros do dia
        records = db_manager.get_daily_records(employee_id, "26-09-2025")
        assert len(records) == 1
        assert records[0].record_type == "entrada"
        
        # Contar registros
        count = db_manager.count_daily_records(employee_id, "26-09-2025")
        assert count == 1
    
    def test_config_operations(self):
        """Testa operações de configuração"""
        from bergamoto.database.manager import DatabaseManager
        
        db_manager = DatabaseManager(self.db_path)
        
        # Buscar configuração padrão
        max_records = db_manager.get_config_value('max_records_per_day', '0')
        assert max_records == '4'
        
        # Definir nova configuração
        db_manager.set_config_value('test_key', 'test_value', 'Teste')
        
        # Verificar se foi salva
        value = db_manager.get_config_value('test_key')
        assert value == 'test_value'
    
    def teardown_method(self):
        """Limpeza após cada teste"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


class TestEmployeeService:
    """Testes para o serviço de funcionários"""
    
    def setup_method(self):
        """Configuração antes de cada teste"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_bergamoto.db"
        
        from bergamoto.database.manager import DatabaseManager
        from bergamoto.core.employee import EmployeeService
        
        self.db_manager = DatabaseManager(self.db_path)
        self.service = EmployeeService(self.db_manager)
    
    def test_create_employee(self):
        """Testa criação de funcionário"""
        success = self.service.create_employee("1234", "João Silva", "vendas", "Maria")
        assert success
        
        # Verificar se foi criado
        employee = self.service.get_employee_by_pin("1234")
        assert employee is not None
        assert employee.name == "João Silva"
    
    def test_create_duplicate_employee(self):
        """Testa criação de funcionário duplicado"""
        # Criar primeiro funcionário
        success1 = self.service.create_employee("1234", "João Silva", "vendas")
        assert success1
        
        # Tentar criar duplicado
        success2 = self.service.create_employee("1234", "Maria Santos", "ti")
        assert not success2  # Deve falhar
    
    def test_validate_employee_data(self):
        """Testa validação de dados"""
        # Dados válidos
        errors = self.service.validate_employee_data("1234", "João Silva", "vendas")
        assert len(errors) == 0
        
        # PIN muito curto
        errors = self.service.validate_employee_data("123", "João Silva", "vendas")
        assert len(errors) > 0
        assert any("PIN deve ter pelo menos 4 caracteres" in error for error in errors)
        
        # Nome muito curto
        errors = self.service.validate_employee_data("1234", "J", "vendas")
        assert len(errors) > 0
        assert any("Nome deve ter pelo menos 2 caracteres" in error for error in errors)
        
        # PIN não numérico
        errors = self.service.validate_employee_data("abc1", "João Silva", "vendas")
        assert len(errors) > 0
        assert any("PIN deve conter apenas números" in error for error in errors)
    
    def teardown_method(self):
        """Limpeza após cada teste"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


class TestTimesheetService:
    """Testes para o serviço de ponto"""
    
    def setup_method(self):
        """Configuração antes de cada teste"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_bergamoto.db"
        
        from bergamoto.database.manager import DatabaseManager
        from bergamoto.core.timesheet import TimesheetService
        from bergamoto.database.models import Employee
        
        self.db_manager = DatabaseManager(self.db_path)
        self.service = TimesheetService(self.db_manager)
        
        # Criar funcionário de teste
        employee = Employee(pin="1234", name="João Silva", setor="vendas")
        employee_id = self.db_manager.create_employee(employee)
        self.test_employee = self.db_manager.get_employee_by_pin("1234")
    
    def test_get_daily_records_empty(self):
        """Testa busca de registros em dia vazio"""
        records = self.service.get_daily_records(self.test_employee.id, "26-09-2025")
        assert len(records) == 0
    
    def test_calculate_work_hours(self):
        """Testa cálculo de horas trabalhadas"""
        from bergamoto.database.models import TimeRecord
        
        # Simular registros do dia
        records = [
            TimeRecord(employee_id=self.test_employee.id, time="08:00:00", record_type="entrada"),
            TimeRecord(employee_id=self.test_employee.id, time="12:00:00", record_type="almoco_saida"),
            TimeRecord(employee_id=self.test_employee.id, time="13:00:00", record_type="almoco_volta"),
            TimeRecord(employee_id=self.test_employee.id, time="17:00:00", record_type="saida"),
        ]
        
        result = self.service._calculate_work_hours(records)
        
        assert 'total_hours' in result
        assert 'periods' in result
        assert 'break_duration' in result
        
        # Verificar se calculou 8 horas (4 manhã + 4 tarde)
        assert result['total_hours'] == 8.0
        
        # Verificar se calculou 1 hora de intervalo
        assert result['break_duration'] == 1.0
    
    def teardown_method(self):
        """Limpeza após cada teste"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


@pytest.fixture
def mock_logger():
    """Mock do sistema de logging para testes"""
    import logging
    return logging.getLogger("test")