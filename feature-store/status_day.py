#%%
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
#%%
conn = sqlite3.connect("/home/br4b0/Desktop/foss/DevcolabBR/bergamoto-novo-lar/bergamoto/data/bergamoto.db")
df = pd.read_sql_query("SELECT * FROM horarios", conn)
conn.close()
# %%
df_current_day = df[df['date']== '03-01-2024']
# %%
df_current_day
user_counts = df_current_day.groupby('pin').size().reset_index(name='count')
df_current_day = df_current_day.merge(user_counts, on='pin', how='left')
# %%
df_current_day
# %%
print(df_current_day[df_current_day['count'] != 4])
# %%
