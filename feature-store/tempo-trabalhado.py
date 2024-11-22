#%%
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import tkinter as tk
from tkinter import ttk
#%%
# Conectar ao banco de dados SQLite e carregar dados em um DataFrame pandas
conn = sqlite3.connect("/home/br4b0/Desktop/foss/DevcolabBR/bergamoto/data/bergamoto.db")
df = pd.read_sql_query("SELECT * FROM horarios", conn)
conn.close()

# Filtrar usuários com 4 registros no mesmo dia
usuarios_com_4_registros = df.groupby(['pin', 'date']).filter(lambda x: len(x) == 4)

# Ordenar os resultados por data e hora

usuarios_com_4_registros = usuarios_com_4_registros.sort_values(by=['date', 'time'])

#%%
usuarios_com_4_registros
# %%
usuarios_com_4_registros
# Calcular a diferença de tempo para cada usuário por dia

# Aplicar a função ao DataFrame
# Adicionar colunas 'name' e 'setor' ao DataFrame resultante
def calcular_tempo_trabalhado(grupo):
    grupo = grupo.sort_values(by='time')
    entrada1 = pd.to_datetime(grupo.iloc[0]['time'])
    saida1 = pd.to_datetime(grupo.iloc[1]['time'])
    entrada2 = pd.to_datetime(grupo.iloc[2]['time'])
    saida2 = pd.to_datetime(grupo.iloc[3]['time'])
    tempo_trabalhado = (saida1 - entrada1) + (saida2 - entrada2)
    tempo_trabalhado_str = str(tempo_trabalhado).split(' ')[-1]  # Remove '0 days'
    name = grupo.iloc[0]['name']
    setor = grupo.iloc[0]['setor']
    return pd.Series({'tempo_trabalhado': tempo_trabalhado_str, 'name': name, 'setor': setor})

# Aplicar a função ao DataFrame
tempo_trabalhado_df = usuarios_com_4_registros.groupby(['pin', 'date'], group_keys=False).apply(calcular_tempo_trabalhado).reset_index()

# Reordenar as colunas
tempo_trabalhado_df = tempo_trabalhado_df[['pin', 'name', 'setor', 'date', 'tempo_trabalhado']]

print(tempo_trabalhado_df)
# %%
tempo_trabalhado_df
# %%
tempo_trabalhado_df[tempo_trabalhado_df['pin'] == "1042"]
# %%

saldo_pos = tempo_trabalhado_df[(tempo_trabalhado_df['pin'] == "1042") & 
                    (tempo_trabalhado_df['tempo_trabalhado'].apply(lambda x: pd.Timedelta(x).total_seconds() > 8 * 3600))]
# %%
saldo_neg = tempo_trabalhado_df[(tempo_trabalhado_df['pin'] == "1042") & 
                    (tempo_trabalhado_df['tempo_trabalhado'].apply(lambda x: pd.Timedelta(x).total_seconds() < 8 * 3600))]
# %%
saldo_pos
tempo_trabalhado_df['saldo'] = tempo_trabalhado_df['tempo_trabalhado'].apply(lambda x: (pd.Timedelta(x) - pd.Timedelta(hours=8)).total_seconds() / 3600)
tempo_trabalhado_df['saldo'] = tempo_trabalhado_df['saldo'].apply(lambda x: str(pd.Timedelta(hours=x)).split(' ')[-1] if x >= 0 else '-' + str(pd.Timedelta(hours=abs(x))).split(' ')[-1])  # Convert to hh:mm:ss format

# Remove milliseconds
tempo_trabalhado_df['saldo'] = tempo_trabalhado_df['saldo'].apply(lambda x: ':'.join(x.split(':')[:2] + [x.split(':')[2].split('.')[0]]))

tempo_trabalhado_df
# %%
saldo_positivo_df = tempo_trabalhado_df[tempo_trabalhado_df['saldo'].apply(lambda x: not x.startswith('-'))]
saldo_negativo_df = tempo_trabalhado_df[tempo_trabalhado_df['saldo'].apply(lambda x: x.startswith('-'))]


saldo_positivo_df
#%%
saldo_negativo_df
# %%
mes_negativo = saldo_negativo_df[saldo_negativo_df['date'].str.contains("-01-2024")]
mes_positivo = saldo_positivo_df[saldo_positivo_df['date'].str.contains("-01-2024")]
# %%
mes_positivo
mes_negativo
# %%
# Somar os valores do saldo para cada usuário no mês positivo
mes_positivo['saldo'] = mes_positivo['saldo'].apply(lambda x: pd.Timedelta(x).total_seconds() / 3600)
saldo_final_positivo = mes_positivo.groupby('pin')['saldo'].sum().reset_index()

# Converter o saldo final de volta para o formato hh:mm:ss
saldo_final_positivo['saldo'] = saldo_final_positivo['saldo'].apply(lambda x: ':'.join(str(pd.Timedelta(hours=x)).split(' ')[-1].split(':')[:2] + [str(pd.Timedelta(hours=x)).split(' ')[-1].split(':')[2].split('.')[0]]))

print(saldo_final_positivo)
# %%
saldo_final_positivo
#%%
# Somar os valores do saldo para cada usuário no mês negativo
mes_negativo['saldo'] = mes_negativo['saldo'].apply(lambda x: -pd.Timedelta(x).total_seconds() / 3600)
saldo_final_negativo = mes_negativo.groupby('pin')['saldo'].sum().reset_index()

# Converter o saldo final de volta para o formato hh:mm:ss
saldo_final_negativo['saldo'] = saldo_final_negativo['saldo'].apply(lambda x: '-' + ':'.join(str(pd.Timedelta(hours=abs(x))).split(' ')[-1].split(':')[:2] + [str(pd.Timedelta(hours=abs(x))).split(' ')[-1].split(':')[2].split('.')[0]]))

print(saldo_final_negativo)
# %%
saldo_final_negativo

# %%
# Mesclar os DataFrames de saldo positivo e negativo
# Mesclar os DataFrames de saldo positivo e negativo
saldo_final = pd.concat([saldo_final_positivo, saldo_final_negativo], ignore_index=True)
saldo_final_positivo = saldo_final_positivo.rename(columns={'saldo': 'saldo_positivo'})
saldo_final_negativo = saldo_final_negativo.rename(columns={'saldo': 'saldo_negativo'})

saldo_final = pd.merge(saldo_final_positivo, saldo_final_negativo, on='pin', how='outer')

print(saldo_final)
# %%
saldo_final
# %%

# %%
# Converter as colunas de saldo para Timedelta


saldo_final['saldo_positivo_horas'] = saldo_final['saldo_positivo'].apply(lambda x: pd.Timedelta(x).total_seconds() / 3600)
saldo_final['saldo_negativo_horas'] = saldo_final['saldo_negativo'].apply(lambda x: pd.Timedelta(x).total_seconds() / 3600)

# Somar os valores de saldo positivo e negativo em horas
saldo_final['saldo_total_horas'] = saldo_final['saldo_positivo_horas'] + saldo_final['saldo_negativo_horas']

# Converter saldo_total_horas para hh:mm:ss
saldo_final['saldo_total'] = saldo_final['saldo_total_horas'].apply(lambda x: str(pd.Timedelta(hours=abs(x))).split(' ')[-1] if x >= 0 else '-' + str(pd.Timedelta(hours=abs(x))).split(' ')[-1])

# Remove milliseconds
saldo_final['saldo_total'] = saldo_final['saldo_total'].apply(lambda x: ':'.join(x.split(':')[:2] + [x.split(':')[2].split('.')[0]]))

print(saldo_final[['pin', 'saldo_positivo_horas', 'saldo_negativo_horas', 'saldo_total']])
# %%
saldo_final
# %%
saldo_final[['pin', 'saldo_positivo', 'saldo_negativo', 'saldo_total']]
# %%
