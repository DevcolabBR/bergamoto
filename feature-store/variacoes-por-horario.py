#%%

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
# Obter os quatro registros por usuário por dia
usuarios_com_4_registros_sorted = usuarios_com_4_registros.sort_values(by=['time'])
primeiro_registro_por_usuario = usuarios_com_4_registros_sorted.groupby(['pin', 'date']).nth(0).reset_index()
segundo_registro_por_usuario = usuarios_com_4_registros_sorted.groupby(['pin', 'date']).nth(1).reset_index()
terceiro_registro_por_usuario = usuarios_com_4_registros_sorted.groupby(['pin', 'date']).nth(2).reset_index()
quarto_registro_por_usuario = usuarios_com_4_registros_sorted.groupby(['pin', 'date']).nth(3).reset_index()

# Visualizar os resultados
primeiro_registro_por_usuario = primeiro_registro_por_usuario.sort_values(by=['date', 'time'])
segundo_registro_por_usuario = segundo_registro_por_usuario.sort_values(by=['date', 'time'])
terceiro_registro_por_usuario = terceiro_registro_por_usuario.sort_values(by=['date', 'time'])
quarto_registro_por_usuario = quarto_registro_por_usuario.sort_values(by=['date', 'time'])

#%%

# Converter a coluna 'time' para o formato de horas
primeiro_registro_por_usuario['time'] = pd.to_datetime(primeiro_registro_por_usuario['time'], format='%H:%M:%S').dt.time
segundo_registro_por_usuario['time'] = pd.to_datetime(segundo_registro_por_usuario['time'], format='%H:%M:%S').dt.time
terceiro_registro_por_usuario['time'] = pd.to_datetime(terceiro_registro_por_usuario['time'], format='%H:%M:%S').dt.time
quarto_registro_por_usuario['time'] = pd.to_datetime(quarto_registro_por_usuario['time'], format='%H:%M:%S').dt.time

# Visualizar os resultados
primeiro_registro_por_usuario
segundo_registro_por_usuario
terceiro_registro_por_usuario
quarto_registro_por_usuario

# %% 
# Função para calcular a média de tempo
def calcular_media_tempo(dataframe):
    medias_tempo_por_data = dataframe.groupby('date')['time'].apply(
        lambda x: (pd.to_datetime(x.astype(str)).dt.hour * 3600 + 
                   pd.to_datetime(x.astype(str)).dt.minute * 60 + 
                   pd.to_datetime(x.astype(str)).dt.second).mean()
    ).reset_index()

    # Converter a média de segundos de volta para o formato de tempo
    medias_tempo_por_data['media_tempo'] = pd.to_timedelta(medias_tempo_por_data['time'], unit='s')

    # Converter para o formato hh:mm:ss
    medias_tempo_por_data['media_tempo_horas_str'] = medias_tempo_por_data['media_tempo'].apply(lambda x: str(x).split(' ')[-1].split('.')[0])
    
    return medias_tempo_por_data

# Calcular a média de tempo para todas as datas
medias_tempo_primeiro = calcular_media_tempo(primeiro_registro_por_usuario)
medias_tempo_segundo = calcular_media_tempo(segundo_registro_por_usuario)
medias_tempo_terceiro = calcular_media_tempo(terceiro_registro_por_usuario)
medias_tempo_quarto = calcular_media_tempo(quarto_registro_por_usuario)

#%% 
# Função para calcular a média de tempo por mês e plotar o gráfico
def plotar_media_tempo_mes(medias_tempo_por_data, titulo):
    medias_tempo_mes = medias_tempo_por_data.copy()
    medias_tempo_mes['date'] = pd.to_datetime(medias_tempo_mes['date'], format='%d-%m-%Y')
    medias_tempo_mes['media_tempo_seconds'] = medias_tempo_mes['media_tempo'].dt.total_seconds()
    medias_tempo_mes = medias_tempo_mes.set_index('date').resample('M')['media_tempo_seconds'].mean().reset_index()

    # Converter a média de segundos de volta para o formato de tempo
    medias_tempo_mes['media_tempo'] = pd.to_timedelta(medias_tempo_mes['media_tempo_seconds'], unit='s')

    # Converter para o formato hh:mm:ss
    medias_tempo_mes['media_tempo_horas_str'] = medias_tempo_mes['media_tempo'].apply(lambda x: str(x).split(' ')[-1].split('.')[0])

    # Visualizar o novo dataframe com as médias de tempo por mês
    medias_tempo_mes = medias_tempo_mes.sort_values(by='media_tempo')

    # Plotar as variações da coluna media_tempo_horas_str em ordem crescente
    plt.figure(figsize=(12, 6))
    plt.plot(medias_tempo_mes['date'], medias_tempo_mes['media_tempo_horas_str'], marker='o', linestyle='-')
    plt.xlabel('Data')
    plt.ylabel('Média de Tempo (hh:mm:ss)')
    plt.title(titulo)
    plt.xticks(medias_tempo_mes['date'], medias_tempo_mes['date'].dt.strftime('%b'), rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Plotar os gráficos para cada registro
plotar_media_tempo_mes(medias_tempo_primeiro, 'Flutuações das Variações de Horários de entrada')
plotar_media_tempo_mes(medias_tempo_segundo, 'Flutuações das Variações de Horários de s-almoco')
plotar_media_tempo_mes(medias_tempo_terceiro, 'Flutuações das Variações de Horários de r-almoco')
plotar_media_tempo_mes(medias_tempo_quarto, 'Flutuações das Variações de Horários de saida')
# %%