"""
Esquemas de banco de dados para o sistema Bergamoto
Define a estrutura das tabelas de forma centralizada
"""

DATABASE_SCHEMA = {
    'employees': '''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pin TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            setor TEXT NOT NULL,
            supervisor TEXT DEFAULT '',
            creation_date TEXT NOT NULL,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    
    'time_records': '''
        CREATE TABLE IF NOT EXISTS time_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            record_type TEXT NOT NULL CHECK (record_type IN ('entrada', 'saida', 'almoco_saida', 'almoco_volta')),
            photo BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            UNIQUE(employee_id, date, record_type)
        )
    ''',
    
    'daily_summaries': '''
        CREATE TABLE IF NOT EXISTS daily_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            total_hours REAL DEFAULT 0,
            regular_hours REAL DEFAULT 0,
            overtime_hours REAL DEFAULT 0,
            break_duration REAL DEFAULT 0,
            status TEXT DEFAULT 'incomplete' CHECK (status IN ('complete', 'incomplete', 'absent')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            UNIQUE(employee_id, date)
        )
    ''',
    
    'system_config': '''
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''
}

# Índices para otimização de consultas
DATABASE_INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_employees_pin ON employees (pin)',
    'CREATE INDEX IF NOT EXISTS idx_time_records_employee_date ON time_records (employee_id, date)',
    'CREATE INDEX IF NOT EXISTS idx_time_records_date ON time_records (date)',
    'CREATE INDEX IF NOT EXISTS idx_daily_summaries_employee_date ON daily_summaries (employee_id, date)',
]

# Dados iniciais do sistema
INITIAL_DATA = {
    'system_config': [
        ('max_records_per_day', '4', 'Número máximo de registros de ponto por dia'),
        ('work_hours_per_day', '8.0', 'Horas de trabalho padrão por dia'),
        ('break_duration_minutes', '60', 'Duração padrão do intervalo em minutos'),
        ('schema_version', '1.0', 'Versão do schema do banco de dados'),
    ]
}

def get_database_schema():
    """Retorna o schema completo do banco de dados"""
    return DATABASE_SCHEMA

def get_database_indexes():
    """Retorna os índices do banco de dados"""
    return DATABASE_INDEXES

def get_initial_data():
    """Retorna os dados iniciais do sistema"""
    return INITIAL_DATA