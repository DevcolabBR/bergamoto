#%%
import sqlite3
import os
import pandas as pd

#%%
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'data', 'bergamoto.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name, pin, metas FROM usuarios WHERE setor = 'vendas'")

# Fetch all rows from the query
rows = cursor.fetchall()
cursor.close()

# Create a DataFrame from the fetched rows
df = pd.DataFrame(rows, columns=['name', 'pin', 'metas'])

# Close the connection
conn.close()

# %%

df
# %%
