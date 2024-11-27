#%%
import sqlite3
import os
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk

#%%
db_path = '/home/br4b0/Desktop/foss/DevcolabBR/bergamoto/data/bergamoto.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name, pin FROM colaboradores WHERE setor = 'vendas'")
rows = cursor.fetchall()

user_list = [f"{row[0]} ({row[1]})" for row in rows]

# %%
def update_metas():
    def on_select():
        user_choice = combo.get()
        user_name = user_choice.split(' (')[0]
        cursor.execute("SELECT name FROM colaboradores WHERE name = ?", (user_name,))
        if cursor.fetchone():
            new_meta = simpledialog.askinteger("Input", f"Adicione uma nova meta para:  {user_name}:")
            if new_meta is not None:
                cursor.execute("UPDATE colaboradores SET metas = ? WHERE name = ?", (new_meta, user_name))
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
    combo.bind("<<ComboboxSelected>>", lambda event: on_select())

    top.mainloop()

try:
    update_metas()
except KeyboardInterrupt:
    print("Programa encerrado pelo usuário.")
    conn.close()
# %%
