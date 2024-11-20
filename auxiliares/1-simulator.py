#%%
import sqlite3
import random
import os
from datetime import datetime, timedelta
import holidays
import platform

#%%

def get_os_type():
    os_name = platform.system()
    if os_name == "Linux":
        return "Linux", "data/bergamoto.db"
    elif os_name == "Darwin":
        return "Mac", "data/bergamoto.db"
    elif os_name == "Windows":
        return "Windows", r"data\bergamoto.db"
    else:
        return "Unknown", "data/bergamoto.db"

os_type, db_path = get_os_type()
print(os_type)

#%%
# Verificar se o diretório 'data' existe, caso contrário, criar
if not os.path.exists('data'):
    os.makedirs('data')

# Conectar ao banco de dados (o arquivo será criado se não existir)
conn = sqlite3.connect(db_path)
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
    first_names = ["Ana", "Bruno", "Carlos", "Daniela", "Eduardo", "Fernanda", "Gabriel", "Helena", "Igor", "Juliana",
                   "Larissa", "Marcos", "Nina", "Otávio", "Paula", "Rafael", "Sofia", "Thiago", "Vanessa", "Yuri"]
    last_names = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa", "Ferreira", "Rodrigues", "Almeida",
                  "Nascimento", "Araújo", "Melo", "Barbosa", "Ribeiro", "Martins", "Carvalho", "Rocha", "Dias", "Moreira"]
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

# Função para gerar um produto aleatório
def generate_product():
    product_category_map = {
        "Televisão": "Eletrônicos",
        "Geladeira": "Eletrodomésticos",
        "Fogão": "Eletrodomésticos",
        "Microondas": "Eletrodomésticos",
        "Máquina de Lavar": "Eletrodomésticos",
        "Notebook": "Eletrônicos",
        "Smartphone": "Eletrônicos",
        "Tablet": "Eletrônicos",
        "Câmera": "Eletrônicos",
        "Fone de Ouvido": "Eletrônicos",
        "Smartwatch": "Eletrônicos",
        "Bicicleta": "Esportes",
        "Patinete Elétrico": "Esportes",
        "Tênis": "Moda",
        "Bolsa": "Moda",
        "Relógio": "Moda",
        "Perfume": "Beleza",
        "Livro": "Livros",
        "Brinquedo": "Brinquedos",
        "Jogo de Videogame": "Games",
        "Console": "Games",
        "Mochila": "Moda",
        "Cafeteira": "Casa",
        "Liquidificador": "Casa",
        "Ventilador": "Casa",
        "Ar Condicionado": "Casa",
        "Aspirador de Pó": "Casa",
        "Secador de Cabelo": "Beleza",
        "Churrasqueira": "Casa",
        "Drone": "Eletrônicos"
    }
    product = random.choice(list(product_category_map.keys()))
    category = product_category_map[product]
    unit_value = round(random.uniform(50.0, 5000.0), 2)
    return product, category, unit_value

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
    creation_date TEXT,
    metas TEXT
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
    INSERT INTO usuarios (pin, name, setor, creation_date, metas)
    VALUES (?, ?, ?, ?, ?)
    ''', (pin, name, setor, creation_date, ""))

# Criar a tabela de vendas se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pin TEXT,
    name TEXT,
    desconto TEXT,
    produto TEXT,
    categoria TEXT,
    valor_unitario REAL,
    data TEXT,
    time TEXT
)
''')

# Inserir dados na tabela de vendas para os funcionários do setor 'vendas'
current_date = start_date
while current_date.year == 2024:
    if is_weekday(current_date):
        date = current_date.strftime('%d-%m-%Y')
        
        for name, pin, setor in employees:
            if setor == 'vendas':
                # Gerar de 1 a 5 registros de vendas por dia
                num_sales = random.randint(1, 5)
                for _ in range(num_sales):
                    time = generate_time(8, 3)  # Horários entre 8 AM e 19 PM
                    product, category, unit_value = generate_product()
                    cursor.execute('''
                    INSERT INTO vendas (pin, name, desconto, produto, categoria, valor_unitario, data, time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (pin, name, "", product, category, unit_value, date, time))
    
    current_date += timedelta(days=1)

# Salvar as mudanças e fechar a conexão
conn.commit()
conn.close()

# Verificar e imprimir as datas de feriados
feriados_brasil = holidays.Brazil(years=2024, subdiv='PA')

# Exibe todos os feriados de 2024 no Brasil, incluindo os do estado do Pará
for data, nome in sorted(feriados_brasil.items()):
    print(f"{data}: {nome}")