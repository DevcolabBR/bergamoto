#%%
import sqlite3
import pandas as pd
import os

# Caminho para o banco de dados
# Obter o caminho absoluto para o diretório raiz do projeto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_path = os.path.join(project_root, 'data', 'bergamoto.db')

# Conectar ao banco de dados
conn = sqlite3.connect(db_path)

# Criar um objeto cursor
cursor = conn.cursor()

# Consulta de exemplo
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# Buscar e imprimir os resultados
tables = cursor.fetchall()
print("Tabelas no banco de dados:", tables)

# Consulta para selecionar todos os dados da tabela 'horarios'
query = "SELECT * FROM horarios"

# Executar a consulta e carregar os dados diretamente em um DataFrame
df_horarios = pd.read_sql_query(query, conn)

# Imprimir o DataFrame
print(df_horarios)

#%%
# Fechar a conexão
conn.close()

# Excluir a coluna 'photo' se existir
if 'photo' in df_horarios.columns:
    df_horarios = df_horarios.drop(columns=['photo'])

# Garantir que a coluna 'pin' seja tratada como texto
df_horarios['pin'] = df_horarios['pin'].astype(str)

# Também corrigir o caminho para salvar o CSV
csv_path = os.path.join(project_root, 'data', 'horarios-ds.csv')
df_horarios.to_csv(csv_path, index=False, encoding='utf-8')
