"""
Script de migração para padronizar o banco de dados existente
"""
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any

from src.bergamoto.utils.logger import setup_logging, get_logger
from src.bergamoto.database.schemas import get_database_schema, get_database_indexes, get_initial_data


class DatabaseMigration:
    """Gerenciador de migrações do banco de dados"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.logger = get_logger(__name__)
        
    def run_migration(self) -> bool:
        """
        Executa a migração do banco de dados
        
        Returns:
            True se a migração foi bem-sucedida
        """
        try:
            self.logger.info("Iniciando migração do banco de dados")
            
            # Verificar se o banco existe
            if not self.db_path.exists():
                self.logger.info("Banco não existe, criando novo")
                return self._create_new_database()
            
            # Backup do banco atual
            self._backup_database()
            
            # Analisar estrutura atual
            current_structure = self._analyze_current_structure()
            self.logger.info(f"Estrutura atual: {list(current_structure.keys())}")
            
            # Migrar dados da estrutura antiga para nova
            if 'horarios' in current_structure:
                self._migrate_horarios_table()
            
            if 'colaboradores' in current_structure or 'people' in current_structure:
                self._migrate_employees_table(current_structure)
            
            # Criar novas tabelas se necessário
            self._create_new_tables()
            
            # Inserir dados iniciais
            self._insert_initial_config()
            
            self.logger.info("Migração concluída com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na migração: {e}")
            return False
    
    def _backup_database(self):
        """Cria backup do banco atual"""
        backup_path = self.db_path.with_suffix('.bak')
        
        with sqlite3.connect(self.db_path) as conn:
            backup = sqlite3.connect(backup_path)
            conn.backup(backup)
            backup.close()
        
        self.logger.info(f"Backup criado: {backup_path}")
    
    def _analyze_current_structure(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analisa a estrutura atual do banco"""
        structure = {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Listar todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                # Obter informações das colunas
                cursor.execute(f"PRAGMA table_info({table})")
                columns = []
                for row in cursor.fetchall():
                    columns.append({
                        'name': row[1],
                        'type': row[2],
                        'not_null': bool(row[3]),
                        'default': row[4],
                        'primary_key': bool(row[5])
                    })
                structure[table] = columns
        
        return structure
    
    def _migrate_horarios_table(self):
        """Migra dados da tabela horarios para time_records"""
        self.logger.info("Migrando tabela horarios")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar se a nova tabela já existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='time_records'")
            if not cursor.fetchone():
                # Criar tabela time_records
                schema = get_database_schema()
                cursor.execute(schema['time_records'])
            
            # Verificar se employees existe, senão criar
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
            if not cursor.fetchone():
                schema = get_database_schema()
                cursor.execute(schema['employees'])
            
            try:
                # Migrar dados da tabela horarios
                cursor.execute("""
                    SELECT DISTINCT pin, name, setor FROM horarios
                    WHERE pin IS NOT NULL AND name IS NOT NULL
                """)
                
                unique_employees = cursor.fetchall()
                employee_map = {}
                
                # Inserir funcionários únicos na tabela employees
                for pin, name, setor in unique_employees:
                    cursor.execute("""
                        INSERT OR IGNORE INTO employees (pin, name, setor, creation_date, active)
                        VALUES (?, ?, ?, date('now'), 1)
                    """, (pin, name, setor))
                    
                    # Obter ID do funcionário
                    cursor.execute("SELECT id FROM employees WHERE pin = ?", (pin,))
                    emp_id = cursor.fetchone()[0]
                    employee_map[pin] = emp_id
                
                # Migrar registros de horario
                cursor.execute("""
                    SELECT pin, date, time, photo FROM horarios
                    ORDER BY pin, date, time
                """)
                
                records = cursor.fetchall()
                current_pin = None
                current_date = None
                record_count = 0
                
                for pin, date, time, photo in records:
                    if pin != current_pin or date != current_date:
                        current_pin = pin
                        current_date = date
                        record_count = 0
                    
                    record_count += 1
                    
                    # Determinar tipo do registro baseado na ordem
                    record_types = ['entrada', 'almoco_saida', 'almoco_volta', 'saida']
                    record_type = record_types[min(record_count - 1, 3)]
                    
                    employee_id = employee_map.get(pin)
                    if employee_id:
                        cursor.execute("""
                            INSERT OR IGNORE INTO time_records 
                            (employee_id, date, time, record_type, photo)
                            VALUES (?, ?, ?, ?, ?)
                        """, (employee_id, date, time, record_type, photo))
                
                conn.commit()
                self.logger.info("Dados migrados da tabela horarios")
                
            except sqlite3.Error as e:
                self.logger.error(f"Erro na migração da tabela horarios: {e}")
                raise
    
    def _migrate_employees_table(self, structure: Dict[str, List[Dict]]):
        """Migra dados das tabelas de funcionários"""
        self.logger.info("Migrando tabelas de funcionários")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Criar tabela employees se não existir
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
            if not cursor.fetchone():
                schema = get_database_schema()
                cursor.execute(schema['employees'])
            
            # Migrar de colaboradores
            if 'colaboradores' in structure:
                cursor.execute("""
                    INSERT OR IGNORE INTO employees (pin, name, setor, supervisor, creation_date, active)
                    SELECT pin, name, setor, '', 
                           COALESCE(creation_date, date('now')),
                           COALESCE(active, 1)
                    FROM colaboradores
                    WHERE pin IS NOT NULL AND name IS NOT NULL
                """)
            
            # Migrar de people
            if 'people' in structure:
                cursor.execute("""
                    INSERT OR IGNORE INTO employees (pin, name, setor, supervisor, creation_date, active)
                    SELECT pin, name, setor, COALESCE(supervisor, ''), 
                           date('now'), 1
                    FROM people
                    WHERE pin IS NOT NULL AND name IS NOT NULL
                """)
            
            conn.commit()
            self.logger.info("Funcionários migrados")
    
    def _create_new_tables(self):
        """Cria novas tabelas que não existem"""
        self.logger.info("Criando novas tabelas")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            schema = get_database_schema()
            
            for table_name, sql in schema.items():
                cursor.execute(sql)
                self.logger.debug(f"Tabela {table_name} criada/verificada")
            
            # Criar índices
            indexes = get_database_indexes()
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
    
    def _insert_initial_config(self):
        """Insere configurações iniciais"""
        self.logger.info("Inserindo configurações iniciais")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            initial_data = get_initial_data()
            
            for key, value, description in initial_data['system_config']:
                cursor.execute("""
                    INSERT OR IGNORE INTO system_config (key, value, description)
                    VALUES (?, ?, ?)
                """, (key, value, description))
            
            conn.commit()
    
    def _create_new_database(self) -> bool:
        """Cria um novo banco de dados"""
        self.logger.info("Criando novo banco de dados")
        
        try:
            # Garantir que o diretório existe
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Criar todas as tabelas
                schema = get_database_schema()
                for table_name, sql in schema.items():
                    cursor.execute(sql)
                
                # Criar índices
                indexes = get_database_indexes()
                for index_sql in indexes:
                    cursor.execute(index_sql)
                
                # Inserir dados iniciais
                initial_data = get_initial_data()
                for key, value, description in initial_data['system_config']:
                    cursor.execute("""
                        INSERT INTO system_config (key, value, description)
                        VALUES (?, ?, ?)
                    """, (key, value, description))
                
                conn.commit()
            
            self.logger.info("Novo banco criado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao criar novo banco: {e}")
            return False


def main():
    """Função principal para executar a migração"""
    setup_logging("INFO")
    logger = get_logger(__name__)
    
    # Determinar caminho do banco
    from src.bergamoto.utils.file_utils import get_data_directory
    data_dir = get_data_directory()
    db_path = data_dir / "bergamoto.db"
    
    logger.info(f"Iniciando migração do banco: {db_path}")
    
    # Executar migração
    migration = DatabaseMigration(db_path)
    success = migration.run_migration()
    
    if success:
        logger.info("Migração concluída com sucesso!")
    else:
        logger.error("Migração falhou!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())