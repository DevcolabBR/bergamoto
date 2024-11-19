import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import tkinter as tk
from tkinter import ttk

# Conectar ao banco de dados SQLite e carregar dados em um DataFrame pandas
conn = sqlite3.connect("bergamoto/data/bergamoto.db")
df = pd.read_sql_query("SELECT * FROM horarios", conn)
conn.close()

# Filtrar usuários com 4 registros no mesmo dia
usuarios_com_4_registros = df.groupby(['pin', 'date']).filter(lambda x: len(x) == 4)

# Ordenar os resultados por data e hora
usuarios_com_4_registros = usuarios_com_4_registros.sort_values(by=['date', 'time'])

# Função para converter tempo em minutos desde a meia-noite
def time_to_minutes(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 60 + m + s / 60

# Criar uma janela Tkinter
root = tk.Tk()
root.title("Seleção de Datas e Colaborador")
root.geometry("400x300")
root.resizable(False, False)

# Estilo para widgets
style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 10))
style.configure("TButton", font=("Helvetica", 10))
style.configure("TCombobox", font=("Helvetica", 10))

# Frame principal
main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Obter datas e colaboradores únicos
datas_unicas = usuarios_com_4_registros['date'].unique().tolist()
colaboradores_unicos = usuarios_com_4_registros['pin'].unique().tolist()

# Criar dropdown para seleção de colaborador
label_colaborador = ttk.Label(main_frame, text="Colaborador:")
label_colaborador.grid(row=0, column=0, pady=5, sticky=tk.W)
dropdown_colaborador = ttk.Combobox(main_frame, values=colaboradores_unicos)
dropdown_colaborador.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))

# Criar dropdowns para seleção de datas
label_data1 = ttk.Label(main_frame, text="Data 1:")
label_data1.grid(row=1, column=0, pady=5, sticky=tk.W)
dropdown_data1 = ttk.Combobox(main_frame, values=datas_unicas)
dropdown_data1.grid(row=1, column=1, pady=5, sticky=(tk.W, tk.E))

label_data2 = ttk.Label(main_frame, text="Data 2:")
label_data2.grid(row=2, column=0, pady=5, sticky=tk.W)
dropdown_data2 = ttk.Combobox(main_frame, values=datas_unicas)
dropdown_data2.grid(row=2, column=1, pady=5, sticky=(tk.W, tk.E))

# Função para atualizar perfis com base nas datas e colaborador selecionados
def atualizar_perfis():
    colaborador = dropdown_colaborador.get()
    data1 = dropdown_data1.get()
    data2 = dropdown_data2.get()

    bob_data1 = usuarios_com_4_registros[(usuarios_com_4_registros['pin'] == colaborador) & (usuarios_com_4_registros['date'] == data1)]
    bob_data2 = usuarios_com_4_registros[(usuarios_com_4_registros['pin'] == colaborador) & (usuarios_com_4_registros['date'] == data2)]

    perfil_data1 = bob_data1['time'].tolist()
    perfil_data2 = bob_data2['time'].tolist()

    print(f"Perfil do colaborador {colaborador} no dia {data1}:", perfil_data1)
    print(f"Perfil do colaborador {colaborador} no dia {data2}:", perfil_data2)

    plt.figure(figsize=(10, 5))

    perfil_data1_min = [time_to_minutes(t) for t in perfil_data1]
    perfil_data2_min = [time_to_minutes(t) for t in perfil_data2]

    plt.plot(perfil_data1_min, [1]*len(perfil_data1_min), 'o', label=data1)
    plt.plot(perfil_data2_min, [2]*len(perfil_data2_min), 'o', label=data2)

    plt.yticks([1, 2], [data1, data2])
    plt.xlabel('Minutos desde a meia-noite')
    plt.title(f'Comparação de Perfis de Usuário - Colaborador {colaborador}')
    plt.legend()
    plt.grid(True)

    # Adicionar linhas verticais de referência
    horarios_referencia = [8*60, 12*60, 14*60, 19*60]  # 8:00, 12:00, 14:00, 19:00 em minutos
    for hr in horarios_referencia:
        plt.axvline(x=hr, color='r', linestyle='--', linewidth=0.8)

    plt.show()

# Criar um botão para atualizar perfis
button_atualizar = ttk.Button(main_frame, text="Atualizar Perfis", command=atualizar_perfis)
button_atualizar.grid(row=3, column=0, columnspan=2, pady=10)

# Configurar grid para expandir
main_frame.columnconfigure(1, weight=1)

# Executar o loop de eventos do Tkinter
root.mainloop()