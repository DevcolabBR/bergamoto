#%%
import sqlite3
import os
import pandas as pd
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk

#%%
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'data', 'bergamoto.db')

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

cursor.execute("SELECT * FROM usuarios")

rows = cursor.fetchall()

df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

conn.close()


# %%
def update_metas():
    user_list = df[df['setor'] == 'vendas'][['name', 'pin']].apply(lambda x: f"{x['name']} ({x['pin']})", axis=1).tolist()
    
    def on_select(event):
        user_choice = combo.get()
        user_name = user_choice.split(' (')[0]
        if user_name in df['name'].tolist():
            index = df[df['name'] == user_name].index[0]
            new_meta = simpledialog.askinteger("Input", f"Adicione uma nova meta para:  {user_name}:")
            if new_meta is not None:
                df.at[index, 'metas'] = new_meta
                cursor = conn.cursor()
                cursor.execute("UPDATE usuarios SET metas = ? WHERE name = ?", (new_meta, user_name))
                conn.commit()
                tk.messagebox.showinfo("Success", "Meta updated successfully")
            else:
                tk.messagebox.showerror("Error", "Invalid meta value")
        else:
            tk.messagebox.showerror("Error", "User not found")

    root = tk.Tk()
    root.withdraw()  # Hide the main window

    top = tk.Toplevel(root)
    top.title("Select User")

    tk.Label(top, text="Selecione um vendedor:").pack(pady=10)
    combo = ttk.Combobox(top, values=user_list)
    combo.pack(pady=10)
    combo.bind("<<ComboboxSelected>>", on_select)

    top.mainloop()

update_metas()
# %%

# %%
