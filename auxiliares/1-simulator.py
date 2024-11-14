import sqlite3
import random
import os
from datetime import datetime, timedelta
import holidays

# Verificar se o diretório 'data' existe, caso contrário, criar
if not os.path.exists('data'):
    os.makedirs('data')

# Conectar ao banco de dados (o arquivo será criado se não existir)
conn = sqlite3.connect('data/bergamoto.db')
cursor = conn.cursor()

# Criar a tabela se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS horarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    pin TEXT,
    date TEXT,
    time TEXT,
    setor TEXT
)
''')

# Função para gerar um nome aleatório
def generate_name():
    first_names = ["Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Grace", "Hannah", "Isaac", "Julia"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# Função para gerar um PIN único
def generate_pin(existing_pins):
    while True:
        pin = f"{random.randint(1000, 9999)}"
        if pin not in existing_pins:
            existing_pins.add(pin)
            return pin

# Função para gerar uma data crescente
def generate_date(start_date, days_passed):
    return (start_date + timedelta(days=days_passed)).strftime('%d-%m-%Y')

# Função para gerar um horário aleatório dentro dos horários especificados
def generate_time(base_hour, variance):
    hour = random.randint(base_hour - variance, base_hour + variance)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{hour:02}:{minute:02}:{second:02}"

# Função para gerar um setor aleatório
def generate_setor():
    setores = ["vendas", "ti", "adm", "financeiro"]
    return random.choice(setores)

# Função para verificar se um dia é útil (exclui domingos e feriados comerciais)
def is_weekday(date):
    br_holidays = holidays.Brazil(state='PA', observed=False)
    return date.weekday() < 5 and date not in br_holidays

# Gerar dados para 30 funcionários
existing_pins = set()
start_date = datetime(2024, 1, 1)

# Gerar nomes e PINs para os funcionários
employees = [(generate_name(), generate_pin(existing_pins), generate_setor()) for _ in range(30)]

# Inserir dados para todos os dias úteis de 2024
current_date = start_date
while current_date.year == 2024:
    if is_weekday(current_date):
        date = current_date.strftime('%d-%m-%Y')
        
        for name, pin, setor in employees:
            # 20% chance de o funcionário não trabalhar neste dia
            if random.random() < 0.20:
                continue
            
            # 92% chance de ter 4 registros por dia
            if random.random() < 0.92:
                times = [
                    generate_time(9, 1),  # 9 AM ± 1 hour
                    generate_time(12, 1), # 12 PM ± 1 hour
                    generate_time(14, 1), # 2 PM ± 1 hour
                    generate_time(18, 1)  # 6 PM ± 1 hour
                ]
            else:
                # Inserir de 1 a 3 registros para os 8% restantes dos dias
                num_records = random.randint(1, 3)
                times = sorted([generate_time(9, 1) for _ in range(num_records)])
            
            for time in times:
                cursor.execute('''
                INSERT INTO horarios (name, pin, date, time, setor)
                VALUES (?, ?, ?, ?, ?)
                ''', (name, pin, date, time, setor))
    
    current_date += timedelta(days=1)

# Criar a tabela de usuários se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pin TEXT,
    name TEXT,
    setor TEXT,
    creation_date TEXT
)
''')

# Função para gerar uma data aleatória dentro do ano de 2024
def generate_random_date_2024():
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    return random_date.strftime('%d-%m-%Y')

# Inserir dados na tabela de usuários
for name, pin, setor in employees:
    creation_date = generate_random_date_2024()
    cursor.execute('''
    INSERT INTO usuarios (pin, name, setor, creation_date)
    VALUES (?, ?, ?, ?)
    ''', (pin, name, setor, creation_date))

# Salvar as mudanças e fechar a conexão
conn.commit()
conn.close()

# Verificar e imprimir as datas de feriados
feriados_brasil = holidays.Brazil(years=2024, subdiv='PA')

# Exibe todos os feriados de 2024 no Brasil, incluindo os do estado do Pará
for data, nome in sorted(feriados_brasil.items()):
    print(f"{data}: {nome}")