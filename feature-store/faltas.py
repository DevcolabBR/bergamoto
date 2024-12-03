#%%
from operator import index
from tkinter import N
from narwhals import col
import pandas as pd
import sqlite3

db_path = '/home/br4b0/Desktop/foss/DevcolabBR/bergamoto/data/bergamoto.db'
conn = sqlite3.connect(db_path)
query = """
SELECT pin, name, setor, date, time, COUNT(*) OVER (PARTITION BY pin, date) as registros
FROM horarios
"""
df = pd.read_sql_query(query, conn)

#  QUEM FALTOU:
#%%

df['date'].__contains__('02-2024')

#%%
query_colaboradores = "SELECT pin, name, setor FROM colaboradores"
df_colaboradores = pd.read_sql_query(query_colaboradores, conn)
df_colaboradores

# Verifica quem faltou
# Converte a coluna 'date' para o tipo datetime para facilitar a comparação
df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
df_colaboradores['key'] = 1
unique_dates = pd.DataFrame(df['date'].unique(), columns=['date'])
unique_dates['key'] = 1

# Cria um DataFrame com todas as combinações possíveis de usuários e datas
all_combinations = pd.merge(df_colaboradores, unique_dates, on='key').drop('key', axis=1)

# Faz um merge com o DataFrame original para encontrar as combinações que não existem
merged = pd.merge(all_combinations, df[['pin', 'date']], on=['pin', 'date'], how='left', indicator=True)
df_faltaram = merged[merged['_merge'] == 'left_only'].drop('_merge', axis=1)
df_faltaram.rename(columns={'date': 'dia-falta'}, inplace=True)
df_faltaram.to_csv('../output/faltas.csv', index=False)

#%%
import pandas as pd

#%%
df = pd.read_csv('/home/br4b0/Desktop/foss/DevcolabBR/bergamoto/output/faltas.csv')
# %%
df

#%%

pin_values = df['pin'].value_counts().head(10)
pin_values

# %%
pin_values = df['pin'].value_counts().head(10).index.tolist()
pin_values

# %%
top10_faltas = df[df['pin'].isin(pin_values)].drop_duplicates('pin')
# %%
colunas_target = ['pin', 'name', 'setor']
top10_faltas[colunas_target].reset_index(drop=True)
# %%
