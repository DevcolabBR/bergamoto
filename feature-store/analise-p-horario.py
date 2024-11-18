#%%
from enum import unique
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
conn = sqlite3.connect("C:/bergamoto/data/bergamoto.db")
df = pd.read_sql_query("SELECT * FROM horarios", conn)
conn.close()
# Filtrar usuários com 4 registros no mesmo dia
usuarios_com_4_registros = df.groupby(['pin', 'date']).filter(lambda x: len(x) == 4)

# Visualizar os resultados
usuarios_com_4_registros = usuarios_com_4_registros.sort_values(by=['date',  'time'])
usuarios_com_4_registros
# %%
# Obter o primeiro registro por usuário por dia
primeiro_registro_por_usuario = usuarios_com_4_registros.sort_values(by=['time']).groupby(['pin', 'date']).first().reset_index()

# Visualizar os resultados
primeiro_registro_por_usuario = primeiro_registro_por_usuario.sort_values(by=['date', 'time'])# %%


#%%
# Converter a coluna 'time' para o formato de horas
primeiro_registro_por_usuario['time'] = pd.to_datetime(primeiro_registro_por_usuario['time'], format='%H:%M:%S').dt.time

# Visualizar os resultados
primeiro_registro_por_usuario
# %%
data_teste = primeiro_registro_por_usuario[primeiro_registro_por_usuario['date']== '01-02-2024']

# %%
data_teste
# Calcular a média de tempo para os registros da coluna 'time'
media_tempo = (pd.to_datetime(data_teste['time'].astype(str)).dt.hour * 3600 + 
               pd.to_datetime(data_teste['time'].astype(str)).dt.minute * 60 + 
               pd.to_datetime(data_teste['time'].astype(str)).dt.second).mean()

# Converter a média de segundos de volta para o formato de tempo
media_tempo_horas = pd.to_timedelta(media_tempo, unit='s')

# Converter para o formato hh:mm:ss
media_tempo_horas_str = str(media_tempo_horas).split(' ')[-1].split('.')[0]

# Visualizar a média de tempo
media_tempo_horas_str
# Calcular a média de tempo para todas as datas
medias_tempo_por_data = primeiro_registro_por_usuario.groupby('date')['time'].apply(
    lambda x: (pd.to_datetime(x.astype(str)).dt.hour * 3600 + 
               pd.to_datetime(x.astype(str)).dt.minute * 60 + 
               pd.to_datetime(x.astype(str)).dt.second).mean()
).reset_index()

# Converter a média de segundos de volta para o formato de tempo
medias_tempo_por_data['media_tempo'] = pd.to_timedelta(medias_tempo_por_data['time'], unit='s')

# Converter para o formato hh:mm:ss
medias_tempo_por_data['media_tempo_horas_str'] = medias_tempo_por_data['media_tempo'].apply(lambda x: str(x).split(' ')[-1].split('.')[0])

# Visualizar o novo dataframe com as médias de tempo por data
medias_tempo_por_data
#%%
# Calcular a média de tempo para cada mês
medias_tempo_mes = medias_tempo_por_data.copy()
medias_tempo_mes['date'] = pd.to_datetime(medias_tempo_mes['date'], format='%d-%m-%Y')
medias_tempo_mes['media_tempo_seconds'] = medias_tempo_mes['media_tempo'].dt.total_seconds()
medias_tempo_mes = medias_tempo_mes.set_index('date').resample('M')['media_tempo_seconds'].mean().reset_index()

# Converter a média de segundos de volta para o formato de tempo
medias_tempo_mes['media_tempo'] = pd.to_timedelta(medias_tempo_mes['media_tempo_seconds'], unit='s')

# Converter para o formato hh:mm:ss
medias_tempo_mes['media_tempo_horas_str'] = medias_tempo_mes['media_tempo'].apply(lambda x: str(x).split(' ')[-1].split('.')[0])

# Visualizar o novo dataframe com as médias de tempo por mês
medias_tempo_mes


# %%
# Plotar as variações da coluna media_tempo_horas_str
plt.figure(figsize=(12, 6))
plt.plot(medias_tempo_por_data['date'], medias_tempo_por_data['media_tempo_horas_str'], marker='o', linestyle='-')
plt.xlabel('Data')
plt.ylabel('Média de Tempo (hh:mm:ss)')
plt.title('Variações da Média de Tempo por Data')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()
# Selecionar um registro por mês

#%%
medias_tempo_por_data['date'] = pd.to_datetime(medias_tempo_por_data['date'], format='%d-%m-%Y')
medias_tempo_por_data = medias_tempo_por_data.set_index('date').resample('M').first().reset_index()

# Plotar as variações da coluna media_tempo_horas_str por mês
plt.figure(figsize=(12, 6))
plt.plot(medias_tempo_por_data['date'], medias_tempo_por_data['media_tempo_horas_str'], marker='o', linestyle='-')
plt.xlabel('Data')
plt.ylabel('Média de Tempo (hh:mm:ss)')
plt.title('Variações da Média de Tempo por Mês')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()
# Ordenar as médias de tempo em ordem crescente
#%%
medias_tempo_mes = medias_tempo_mes.sort_values(by='media_tempo')

# Plotar as variações da coluna media_tempo_horas_str em ordem crescente
plt.figure(figsize=(12, 6))
plt.plot(medias_tempo_mes['date'], medias_tempo_mes['media_tempo_horas_str'], marker='o', linestyle='-')
plt.xlabel('Data')
plt.ylabel('Média de Tempo (hh:mm:ss)')
plt.title('Flutuações das Variações de Horários de entrada')
plt.xticks(medias_tempo_mes['date'], medias_tempo_mes['date'].dt.strftime('%b'), rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()
# %%
