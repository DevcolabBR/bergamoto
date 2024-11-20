# atribuição dos turnos de trabalho para os colaboradores
#%%
import pandas as pd
import sqlite3
import os
#%%
db_path = '/home/br4b0/Desktop/foss/DevcolabBR/bergamoto/data/bergamoto.db'
conn = sqlite3.connect(db_path)
query = """
SELECT *
FROM usuarios
"""
df = pd.read_sql_query(query, conn)
# %%
df
# %%
df.loc[df['setor'] == 'vendas', 'metas'] = True

# %%
df
# %%
