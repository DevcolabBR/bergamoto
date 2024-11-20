#%%
from matplotlib import use
import pandas as pd
from tabulate import tabulate

#%%
df = pd.read_csv('/home/br4b0/Desktop/foss/DevcolabBR/bergamoto/output/faltas.csv', index_col=0)
# %%
date_target = '2024-08-01'
df_target = df[df['dia-falta'] == date_target]
# %%
print(tabulate(df_target.sort_values(by='dia-falta'), headers='keys', tablefmt='pretty'))
# %%
