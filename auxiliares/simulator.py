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

# Criar a tabela horarios
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

# Função para gerar produtos e inserir na tabela produtos
def generate_products():
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
    products = []
    for product_name, category in product_category_map.items():
        unit_value = round(random.uniform(50.0, 5000.0), 2)
        stock = random.randint(10, 100)  # Quantidade em estoque
        products.append((product_name, category, unit_value, stock))
    return products

# Criar a tabela produtos
cursor.execute('''
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    categoria TEXT,
    valor_unitario REAL,
    estoque INTEGER
)
''')

# Inserir produtos na tabela produtos
product_list = generate_products()
cursor.executemany('''
INSERT INTO produtos (nome, categoria, valor_unitario, estoque)
VALUES (?, ?, ?, ?)
''', product_list)

# Gerar dados para 30 funcionários
existing_pins = set()
start_date = datetime(2024, 1, 1)

# Gerar nomes e PINs para os funcionários
employees = []
for _ in range(30):
    name = generate_name()
    pin = generate_pin(existing_pins)
    setor = generate_setor()
    employees.append({'name': name, 'pin': pin, 'setor': setor})

# Inserir dados na tabela colaboradores
cursor.execute('''
CREATE TABLE IF NOT EXISTS colaboradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pin TEXT UNIQUE,
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

for employee in employees:
    creation_date = generate_random_date_2024()
    cursor.execute('''
    INSERT INTO colaboradores (pin, name, setor, creation_date, metas)
    VALUES (?, ?, ?, ?, ?)
    ''', (employee['pin'], employee['name'], employee['setor'], creation_date, ""))

# Atualizar os IDs dos colaboradores
cursor.execute("SELECT id, pin FROM colaboradores")
colaboradores_data = cursor.fetchall()
pin_to_colaborador_id = {pin: id for id, pin in colaboradores_data}

# Criar a tabela clientes
cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    contato TEXT,
    endereco TEXT
)
''')

# Função para gerar clientes
def generate_client():
    name = generate_name()
    contact = f"({random.randint(10, 99)}) {random.randint(90000, 99999)}-{random.randint(1000, 9999)}"
    address = f"Rua {generate_name()}, {random.randint(1, 999)}, Bairro {generate_name()}"
    return (name, contact, address)

# Gerar lista de clientes
client_list = [generate_client() for _ in range(100)]  # 100 clientes
cursor.executemany('''
INSERT INTO clientes (nome, contato, endereco)
VALUES (?, ?, ?)
''', client_list)

# Criar a tabela pedidos
cursor.execute('''
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    colaborador_id INTEGER,
    data TEXT,
    total REAL,
    FOREIGN KEY(cliente_id) REFERENCES clientes(id),
    FOREIGN KEY(colaborador_id) REFERENCES colaboradores(id)
)
''')

# Criar a tabela itens_pedido
cursor.execute('''
CREATE TABLE IF NOT EXISTS itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER,
    produto_id INTEGER,
    quantidade INTEGER,
    valor_unitario REAL,
    FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY(produto_id) REFERENCES produtos(id)
)
''')

# Obter IDs dos clientes
cursor.execute("SELECT id FROM clientes")
clientes_ids = [row[0] for row in cursor.fetchall()]

# Obter IDs dos produtos
cursor.execute("SELECT id FROM produtos")
produtos_ids = [row[0] for row in cursor.fetchall()]

# Inserir dados na tabela horarios e gerar pedidos
current_date = start_date
br_holidays = holidays.Brazil(years=2024, state='PA', observed=False)

while current_date.year == 2024:
    if is_weekday(current_date):
        date_str = current_date.strftime('%d-%m-%Y')
        for employee in employees:
            name = employee['name']
            pin = employee['pin']
            setor = employee['setor']
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
                ''', (name, pin, date_str, time, setor))

            # Gerar pedidos para o setor de vendas
            if setor == 'vendas':
                # Gerar de 1 a 5 pedidos por dia
                num_pedidos = random.randint(1, 5)
                colaborador_id = pin_to_colaborador_id[pin]
                for _ in range(num_pedidos):
                    cliente_id = random.choice(clientes_ids)
                    # Data do pedido
                    data_pedido = date_str
                    # Gerar itens do pedido
                    num_itens = random.randint(1, 5)
                    itens = []
                    total_pedido = 0.0
                    for _ in range(num_itens):
                        produto_id = random.choice(produtos_ids)
                        # Obter informações do produto
                        cursor.execute('SELECT nome, valor_unitario, estoque FROM produtos WHERE id = ?', (produto_id,))
                        produto_info = cursor.fetchone()
                        valor_unitario = produto_info[1]
                        estoque = produto_info[2]
                        if estoque <= 0:
                            continue  # Se não há estoque, não adiciona o produto
                        quantidade = random.randint(1, min(5, estoque))
                        total_item = valor_unitario * quantidade
                        total_pedido += total_item
                        # Atualizar estoque
                        novo_estoque = estoque - quantidade
                        cursor.execute('UPDATE produtos SET estoque = ? WHERE id = ?', (novo_estoque, produto_id))
                        itens.append((produto_id, quantidade, valor_unitario))
                    if itens:
                        # Inserir pedido
                        cursor.execute('''
                        INSERT INTO pedidos (cliente_id, colaborador_id, data, total)
                        VALUES (?, ?, ?, ?)
                        ''', (cliente_id, colaborador_id, data_pedido, total_pedido))
                        pedido_id = cursor.lastrowid
                        # Inserir itens do pedido
                        for item in itens:
                            cursor.execute('''
                            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, valor_unitario)
                            VALUES (?, ?, ?, ?)
                            ''', (pedido_id, item[0], item[1], item[2]))

    current_date += timedelta(days=1)

# Salvar as mudanças e fechar a conexão
conn.commit()
conn.close()

# Verificar e imprimir as datas de feriados
feriados_brasil = holidays.Brazil(years=2024, subdiv='PA')

# Exibe todos os feriados de 2024 no Brasil, incluindo os do estado do Pará
for data, nome in sorted(feriados_brasil.items()):
    print(f"{data}: {nome}")