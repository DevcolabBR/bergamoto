"""
Gerenciador do banco de dados para o sistema Bergamoto
Centraliza todas as operações de banco de dados
"""
import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from contextlib import contextmanager

from ..utils.logger import get_logger
from .models import Employee, TimeRecord, DailySummary
from .schemas import get_database_schema, get_database_indexes, get_initial_data


class DatabaseManager:
    """Gerenciador centralizado do banco de dados"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.logger = get_logger(__name__)
        self._ensure_database_exists()
        self._initialize_database()

    def _ensure_database_exists(self):
        """Garante que o diretório do banco existe"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def _initialize_database(self):
        """Inicializa o banco de dados com o schema"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Criar tabelas
                schema = get_database_schema()
                for table_name, sql in schema.items():
                    cursor.execute(sql)
                    self.logger.debug(f"Tabela {table_name} criada/verificada")
                
                # Criar índices
                indexes = get_database_indexes()
                for index_sql in indexes:
                    cursor.execute(index_sql)
                    self.logger.debug("Índice criado/verificado")
                
                # Inserir dados iniciais
                self._insert_initial_data(cursor)
                
                conn.commit()
                self.logger.info("Banco de dados inicializado com sucesso")
                
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise

    def _insert_initial_data(self, cursor: sqlite3.Cursor):
        """Insere dados iniciais se necessário"""
        initial_data = get_initial_data()
        
        for table, data in initial_data.items():
            if table == 'system_config':
                for key, value, description in data:
                    cursor.execute(
                        "INSERT OR IGNORE INTO system_config (key, value, description) VALUES (?, ?, ?)",
                        (key, value, description)
                    )

    @contextmanager
    def get_connection(self):
        """Context manager para conexões com o banco"""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # Permite acesso por nome da coluna
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Erro na conexão com banco: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # === Operações com Funcionários ===
    
    def create_employee(self, employee: Employee) -> int:
        """Cria um novo funcionário"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO employees (pin, name, setor, supervisor, creation_date, active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (employee.pin, employee.name, employee.setor, 
                  employee.supervisor, employee.creation_date, employee.active))
            employee_id = cursor.lastrowid
            return employee_id if employee_id is not None else 0

    def get_employee_by_pin(self, pin: str) -> Optional[Employee]:
        """Busca funcionário pelo PIN"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees WHERE pin = ? AND active = 1", (pin,))
            row = cursor.fetchone()
            
            if row:
                return Employee(
                    id=row['id'],
                    pin=row['pin'],
                    name=row['name'],
                    setor=row['setor'],
                    supervisor=row['supervisor'],
                    creation_date=row['creation_date'],
                    active=bool(row['active'])
                )
            return None

    def get_all_employees(self, active_only: bool = True) -> List[Employee]:
        """Lista todos os funcionários"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if active_only:
                cursor.execute("SELECT * FROM employees WHERE active = 1 ORDER BY name")
            else:
                cursor.execute("SELECT * FROM employees ORDER BY name")
            
            employees = []
            for row in cursor.fetchall():
                employees.append(Employee(
                    id=row['id'],
                    pin=row['pin'],
                    name=row['name'],
                    setor=row['setor'],
                    supervisor=row['supervisor'],
                    creation_date=row['creation_date'],
                    active=bool(row['active'])
                ))
            return employees

    # === Operações com Registros de Ponto ===
    
    def insert_time_record(self, record: TimeRecord) -> bool:
        """Insere um novo registro de ponto"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar se já existe o tipo de registro no dia
                cursor.execute("""
                    SELECT COUNT(*) FROM time_records 
                    WHERE employee_id = ? AND date = ? AND record_type = ?
                """, (record.employee_id, record.date, record.record_type))
                
                if cursor.fetchone()[0] > 0:
                    self.logger.warning(f"Registro {record.record_type} já existe para o funcionário {record.employee_id} no dia {record.date}")
                    return False
                
                cursor.execute("""
                    INSERT INTO time_records (employee_id, date, time, record_type, photo)
                    VALUES (?, ?, ?, ?, ?)
                """, (record.employee_id, record.date, record.time, record.record_type, record.photo))
                
                conn.commit()
                self.logger.info(f"Registro de ponto inserido: {record.record_type} para funcionário {record.employee_id}")
                return True
                
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao inserir registro de ponto: {e}")
            return False

    def get_daily_records(self, employee_id: int, date: str) -> List[TimeRecord]:
        """Busca todos os registros de um funcionário em um dia"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM time_records 
                WHERE employee_id = ? AND date = ?
                ORDER BY time
            """, (employee_id, date))
            
            records = []
            for row in cursor.fetchall():
                records.append(TimeRecord(
                    id=row['id'],
                    employee_id=row['employee_id'],
                    date=row['date'],
                    time=row['time'],
                    record_type=row['record_type'],
                    photo=row['photo']
                ))
            return records

    def count_daily_records(self, employee_id: int, date: str) -> int:
        """Conta registros de um funcionário em um dia"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM time_records 
                WHERE employee_id = ? AND date = ?
            """, (employee_id, date))
            return cursor.fetchone()[0]

    def get_next_record_type(self, employee_id: int, date: str) -> str:
        """Determina o próximo tipo de registro baseado nos existentes"""
        records = self.get_daily_records(employee_id, date)
        record_types = [r.record_type for r in records]
        
        # Ordem padrão dos registros
        order = ['entrada', 'almoco_saida', 'almoco_volta', 'saida']
        
        for record_type in order:
            if record_type not in record_types:
                return record_type
        
        # Se todos os tipos já existem, retornar erro
        raise ValueError("Todos os registros do dia já foram feitos")

    # === Operações com Resumos Diários ===
    
    def calculate_daily_summary(self, employee_id: int, date: str) -> Optional[DailySummary]:
        """Calcula resumo diário de trabalho"""
        records = self.get_daily_records(employee_id, date)
        
        if len(records) == 0:
            return DailySummary(employee_id=employee_id, date=date, status='absent')
        
        # Calcular horas trabalhadas baseado nos registros
        summary = DailySummary(employee_id=employee_id, date=date)
        
        # Implementar lógica de cálculo baseada nos registros disponíveis
        # Esta é uma implementação básica que pode ser expandida
        
        if len(records) >= 2:
            # Calcular horas básicas
            # TODO: Implementar cálculo completo baseado nos tipos de registro
            summary.status = 'complete' if len(records) >= 4 else 'incomplete'
        
        return summary

    # === Operações de Configuração ===
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Busca valor de configuração"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_config WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default

    def set_config_value(self, key: str, value: str, description: str = ''):
        """Define valor de configuração"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO system_config (key, value, description)
                VALUES (?, ?, ?)
            """, (key, value, description))
            conn.commit()

    # === Operações de Manutenção ===
    
    def vacuum_database(self):
        """Otimiza o banco de dados"""
        with self.get_connection() as conn:
            conn.execute("VACUUM")
            self.logger.info("Banco de dados otimizado")

    def get_database_info(self) -> Dict[str, Any]:
        """Retorna informações do banco de dados"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Contar registros por tabela
            tables_info = {}
            tables = ['employees', 'time_records', 'daily_summaries', 'system_config']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                tables_info[table] = count
            
            return {
                'database_path': str(self.db_path),
                'tables': tables_info,
                'schema_version': self.get_config_value('schema_version', '1.0')
            }