#%%
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
#%%
conn = sqlite3.connect("C:/bergamoto/data/bergamoto.db")
df = pd.read_sql_query("SELECT * FROM horarios", conn)
conn.close()
# %%
df
# %%
# Filtrar usuários com 4 registros no mesmo dia
usuarios_com_4_registros = df.groupby(['pin', 'date']).filter(lambda x: len(x) == 4)

# Visualizar os resultados
usuarios_com_4_registros
# %%
# Contar a frequência de cada usuário (pin)
usuarios_frequencia = df['pin'].value_counts().reset_index()
usuarios_frequencia.columns = ['name', 'frequency']
# Map pin to name
pin_to_name = dict(zip(df['pin'], df['name']))

# Replace pin with name in usuarios_frequencia
usuarios_frequencia['name'] = usuarios_frequencia['name'].map(pin_to_name)
# Criar um novo DataFrame para exibir a coluna pin, setor, name, date (com 4 registros no mesmo dia)
usuarios_4_registros_unicos = usuarios_com_4_registros.drop_duplicates(subset=['pin', 'date'])[['pin', 'setor', 'name', 'date']]

# Contar a frequência de cada usuário (pin) com 4 registros no mesmo dia
usuarios_4_registros_frequencia = usuarios_4_registros_unicos['pin'].value_counts().reset_index()
usuarios_4_registros_frequencia.columns = ['pin', 'frequency']
usuarios_4_registros_frequencia['name'] = usuarios_4_registros_frequencia['pin'].map(pin_to_name)

# Selecionar os 10 primeiros registros
top_10_usuarios_4_registros = usuarios_4_registros_frequencia.head(10)

# Gerar o gráfico de barras
plt.figure(figsize=(10, 6))
plt.bar(top_10_usuarios_4_registros['name'], top_10_usuarios_4_registros['frequency'], color='skyblue')
plt.xlabel('Usuários')
plt.ylabel('Frequência')
plt.title('Top 10 Usuários com 4 Registros no Mesmo Dia')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
# %%

presencas_por_mes = usuarios_com_4_registros.groupby(['pin', 'month']).size().unstack(fill_value=0)

# Ordenar os meses em ordem crescente
meses_ordenados = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
presencas_por_mes = presencas_por_mes[meses_ordenados]

# Exibir o DataFrame resultante
presencas_por_mes
# Dividir os valores inteiros por 4, exceto a coluna 'pin'
presencas_por_mes = presencas_por_mes.apply(lambda x: x / 4 if x.name != 'pin' else x)
presencas_por_mes = presencas_por_mes.applymap(lambda x: str(x).replace('.0', ''))
presencas_por_mes = presencas_por_mes.astype(int)
# Exibir o DataFrame resultante

# Selecionar os 10 primeiros registros
top_10_pins = top_10_usuarios_4_registros['pin']
top_10_frequencia_mes = presencas_por_mes.loc[top_10_pins]

# Gerar o gráfico de barras empilhadas
ax = top_10_frequencia_mes.plot(kind='bar', stacked=True, figsize=(12, 8), colormap='tab20')
plt.xlabel('Usuários')
plt.ylabel('Frequência Proporcional')
plt.title('Top 10 Usuários por Frequência Mensal Proporcional')
plt.legend(top_10_frequencia_mes.columns, title='Meses', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(ticks=range(len(top_10_usuarios_4_registros)), labels=top_10_usuarios_4_registros['name'], rotation=45)

# Adicionar os valores das presenças no gráfico
for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy()
    if height > 0:
        ax.text(x + width / 2, y + height / 2, int(height), ha='center', va='center')

plt.tight_layout()
plt.show()
# Exibir o número de presenças que cada usuário teve em cada mês
#%%







# %%
