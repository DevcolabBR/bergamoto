# Description: Script to generate the metas table in the database
#%%
import sqlite3
import platform

from django import db
from simulator import get_os_type

#%%
os_type, db_path = get_os_type()
print(os_type, db_path)
# %%
conn = sqlite3.connect()
cursor = conn.cursor()


cursor.execute('''
SELECT *
FROM usuarios
''')

for row in cursor.fetchall():
    print(row)
# %%
