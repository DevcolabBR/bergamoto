#%%
import pandas as pd
import os
import hashlib
import matplotlib.pyplot as plt

#%%
file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'horarios-ds.csv')
df = pd.read_csv(file_path, index_col=False, dtype=str, encoding='utf-8')
df
# %%
df['entrada'] = None
df['s-almoco'] = None
df['r-almoco'] = None
df['saida'] = None
df
# %%
def mark_times(group):
    count = group.shape[0]
    if count == 4:
        group.loc[group.index[0], 'entrada'] = True
        group.loc[group.index[1], 's-almoco'] = True
        group.loc[group.index[2], 'r-almoco'] = True
        group.loc[group.index[3], 'saida'] = True
    elif count == 3:
        group.loc[group.index[0], 'entrada'] = True
        group.loc[group.index[1], 's-almoco'] = True
        group.loc[group.index[2], 'r-almoco'] = True
    elif count == 2:
        group.loc[group.index[0], 'entrada'] = True
        group.loc[group.index[1], 'saida'] = True
    return group

df = df.groupby(['name', 'date'], group_keys=False).apply(mark_times)

df['entrada'] = df['entrada'].astype(bool)
df['s-almoco'] = df['s-almoco'].astype(bool)
df['r-almoco'] = df['r-almoco'].astype(bool)
df['saida'] = df['saida'].astype(bool)
#%%
def generate_user_day_hash(pin, date):
    hash_input = f"{pin}{date}".encode('utf-8')
    return hashlib.sha256(hash_input).hexdigest()

def generate_user_month_hash(pin, date):
    month_year = date[3:]  # Assuming date format is DD-MM-YYYY
    hash_input = f"{pin}{month_year}".encode('utf-8')
    return hashlib.sha256(hash_input).hexdigest()

def generate_user_year_hash(pin, date):
    year = date[6:]  # Assuming date format is DD-MM-YYYY
    hash_input = f"{pin}{year}".encode('utf-8')
    return hashlib.sha256(hash_input).hexdigest()

df['user_day_hash'] = df.apply(lambda row: generate_user_day_hash(row['pin'], row['date']), axis=1)
df['user_month_hash'] = df.apply(lambda row: generate_user_month_hash(row['pin'], row['date']), axis=1)
df['user_year_hash'] = df.apply(lambda row: generate_user_year_hash(row['pin'], row['date']), axis=1)
df['setor_day_hash'] = df.apply(lambda row: generate_user_day_hash(row['setor'], row['date']), axis=1)
df['setor_month_hash'] = df.apply(lambda row: generate_user_month_hash(row['setor'], row['date']), axis=1)
df['setor_year_hash'] = df.apply(lambda row: generate_user_year_hash(row['setor'], row['date']), axis=1)
#%%

if (df.groupby(['pin', 'date'])['time'].transform('count') == 4).any():
    df['horas_trabalhadas'] = None

    def calcular_horas_trabalhadas(group):
        if len(group) == 4:
            times = pd.to_datetime(group['time'].sort_values(), format='%H:%M:%S')
            horas_trabalhadas = (times.iloc[1] - times.iloc[0]) + (times.iloc[3] - times.iloc[2])
            group['horas_trabalhadas'] = horas_trabalhadas
        return group

    df = df.groupby(['pin', 'date'], group_keys=False).apply(calcular_horas_trabalhadas).reset_index(drop=True)
    df['horas_trabalhadas'] = df['horas_trabalhadas'].apply(lambda x: str(x)[7:] if pd.notnull(x) else x)
    print(df[['pin', 'date', 'horas_trabalhadas']].drop_duplicates().head(5))
    # Create a new DataFrame with the relevant columns
    df_horas_trabalhadas = df[['pin', 'date', 'horas_trabalhadas']].drop_duplicates().reset_index(drop=True)
    df_horas_trabalhadas

#%%
df_horas_trabalhadas[df_horas_trabalhadas['pin']=='4551']


#%%
df
if (df.groupby(['pin', 'date'])['time'].transform('count') == 4).any():
    df['horas_trabalhadas'] = None

    def calcular_horas_trabalhadas(group):
        if len(group) == 4:
            times = pd.to_datetime(group['time'].sort_values(), format='%H:%M:%S')
            horas_trabalhadas = (times.iloc[1] - times.iloc[0]) + (times.iloc[3] - times.iloc[2])
            group['horas_trabalhadas'] = horas_trabalhadas
        return group

    df = df.groupby(['pin', 'date'], group_keys=False).apply(calcular_horas_trabalhadas).reset_index(drop=True)
    df['horas_trabalhadas'] = df['horas_trabalhadas'].apply(lambda x: str(x)[7:] if pd.notnull(x) else x)
    print(df[['pin', 'date', 'horas_trabalhadas']].drop_duplicates().head(5))
    # Create a new DataFrame with the relevant columns
    df_horas_trabalhadas = df[['pin', 'date', 'horas_trabalhadas']].drop_duplicates().reset_index(drop=True)
    df_horas_trabalhadas

    total_times = []

    for pin in df['pin'].unique():
        user_records = df[(df['pin'] == pin) & (df.groupby(['pin', 'date'])['time'].transform('count') == 4)]
        for date in user_records['date'].unique():
            usuario = df[(df['pin'] == pin) & (df['date'] == date)]
            times = usuario['time'].sort_values().values
            total_time = 0

            for i in range(len(times) - 1, 0, -1):
                time_diff = pd.to_datetime(times[i]) - pd.to_datetime(times[i - 1])
                total_time += time_diff.total_seconds()

            total_time_hours = total_time // 3600
            total_time_minutes = (total_time % 3600) // 60
            total_time_seconds = total_time % 60

            total_time_formatted = f"{int(total_time_hours)}h {int(total_time_minutes)}m {int(total_time_seconds)}s"
            total_times.append({'pin': pin, 'date': date, 'total_time': total_time_formatted})

    df_total_times4 = pd.DataFrame(total_times)
    df_total_times4

#%%
df_total_times4[df_total_times4['pin']=='4551']
# Plotting the total time worked for pin '4551'
df_pin_4551 = df_total_times4[df_total_times4['pin'] == '4551']
df_pin_4551['total_time_hours'] = df_pin_4551['total_time'].apply(lambda x: int(x.split('h')[0]) + int(x.split('h')[1].split('m')[0]) / 60 + int(x.split('m')[1].split('s')[0]) / 3600)

plt.figure(figsize=(10, 6))
plt.plot(df_pin_4551['date'], df_pin_4551['total_time_hours'], marker='o')
plt.axhline(y=8, color='r', linestyle='--', label='8 hours reference')  # Adding a red reference line at 8 hours
plt.xlabel('Date')
plt.ylabel('Total Time Worked (hours)')
plt.title('Total Time Worked per Day for PIN 4551')
plt.xticks(rotation=45)
plt.xticks(ticks=range(0, len(df_pin_4551['date']), 5), labels=df_pin_4551['date'][::5])  # Show every 5th date
plt.grid(True)
plt.legend()
plt.show()


# %%
