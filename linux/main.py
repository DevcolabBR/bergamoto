import datetime
import sqlite3
import cv2
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import signal
import io
import time
import threading
import csv
import os
from ttkthemes import ThemedTk

# Configuração de caminhos
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
DB_PATH = os.path.join(DATA_DIR, 'bergamoto.db')
PEOPLE_CSV_PATH = os.path.join(DATA_DIR, 'people.csv')

photo_window_open = False
lock = threading.Lock()

def create_table():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Não vamos recriar a tabela, pois ela já existe com um esquema diferente
        # apenas verificar se existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='horarios'")
        if not c.fetchone():
            # Se a tabela não existir, criamos com o esquema atual da base
            c.execute('''CREATE TABLE IF NOT EXISTS horarios
                       (id INTEGER PRIMARY KEY,
                        pin TEXT,
                        nome TEXT,
                        data TEXT,
                        entrada TEXT,
                        saida TEXT,
                        horas_trabalhadas REAL)''')
            conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao verificar tabela: {e}")
    finally:
        if conn:
            conn.close()

def insert_record(name, pin, timestamp, photo_blob, setor, supervisor):
    data = timestamp.strftime("%d-%m-%Y")
    hora = timestamp.strftime("%H:%M:00")
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Verificar número de registros existentes
        c.execute("SELECT COUNT(*) FROM horarios WHERE pin = ? AND data = ?", (pin, data))
        record_count = c.fetchone()[0]
        
        if record_count >= 4:
            messagebox.showwarning("Limite Atingido", "Você já fez 4 registros hoje.")
            return False

        # Determinar se é entrada ou saída com base no número de registros
        # Nós alternamos entre entrada/saída baseado no número de registros do dia
        tipo_registro = "entrada" if record_count % 2 == 0 else "saida"
        
        if tipo_registro == "entrada":
            # Inserir registro de entrada
            c.execute("INSERT INTO horarios (pin, nome, data, entrada) VALUES (?, ?, ?, ?)", 
                    (pin, name, data, hora))
        else:
            # Buscar o último registro sem saída para este PIN e data
            c.execute("""
                SELECT id, entrada FROM horarios 
                WHERE pin = ? AND data = ? AND saida IS NULL 
                ORDER BY id DESC LIMIT 1
            """, (pin, data))
            
            resultado = c.fetchone()
            if resultado:
                registro_id, hora_entrada = resultado
                # Calcular horas trabalhadas
                fmt = "%H:%M:%S"
                entrada_dt = datetime.datetime.strptime(hora_entrada, fmt)
                saida_dt = datetime.datetime.strptime(hora, fmt)
                
                # Calcular a diferença em horas
                diferenca = (saida_dt - entrada_dt).total_seconds() / 3600
                
                # Atualizar o registro com a saída e horas trabalhadas
                c.execute("""
                    UPDATE horarios SET saida = ?, horas_trabalhadas = ?
                    WHERE id = ?
                """, (hora, diferenca, registro_id))
            else:
                # Se não encontrar entrada correspondente, criar um novo registro
                c.execute("INSERT INTO horarios (pin, nome, data, saida) VALUES (?, ?, ?, ?)", 
                        (pin, name, data, hora))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao inserir registro: {e}")
        return False
    finally:
        if conn:
            conn.close()

def capture_photo():
    global photo_window_open
    img_blob = None

    def take_photo():
        nonlocal img_blob
        try:
            ret, frame = cam.read()
            if ret:
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                with io.BytesIO() as output:
                    img.save(output, format="PNG")
                    img_blob = output.getvalue()
                messagebox.showinfo("Captura de Foto", "Foto capturada")
            else:
                messagebox.showerror("Erro", "Falha ao capturar a imagem")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a captura: {e}")
        finally:
            # Garantir que a câmera sempre seja liberada
            if cam.isOpened():
                cam.release()
            cv2.destroyAllWindows()
            if root.winfo_exists():
                root.quit()

    def show_frame():
        if not cam.isOpened() or not root.winfo_exists():
            return
        try:
            ret, frame = cam.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                lmain.imgtk = imgtk
                lmain.configure(image=imgtk)
            if root.winfo_exists():
                lmain.after(10, show_frame)
        except Exception:
            # Em caso de erro, apenas encerrar a atualização
            pass

    cam = cv2.VideoCapture(0)
    root = ThemedTk(theme="equilux")
    root.title("Captura de Foto")
    root.attributes("-topmost", True)
    root.attributes("-fullscreen", True)

    style = ttk.Style(root)
    style.theme_use('equilux')

    frame = ttk.Frame(root, padding="10")
    frame.pack(expand=True, fill=tk.BOTH)

    lmain = ttk.Label(frame)
    lmain.pack(expand=True)

    capture_button = ttk.Button(frame, text="Capturar Foto", command=take_photo)
    capture_button.pack(pady=10)

    root.bind('<Return>', take_photo)

    photo_window_open = True
    show_frame()
    
    root.after(3000, take_photo)
    
    root.mainloop()
    cam.release()
    cv2.destroyAllWindows()
    root.destroy()
    photo_window_open = False
    return img_blob

class Employee:
    def __init__(self, name, pin, setor, supervisor):
        self.name = name
        self.pin = pin
        self.setor = setor
        self.supervisor = supervisor
        self.records = []
        
        # Carregar registros do dia atual
        self.load_today_records()

    def load_today_records(self):
        """Carrega os registros do dia atual para o funcionário"""
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT entrada, saida FROM horarios WHERE pin = ? AND data = ? ORDER BY id", 
                    (self.pin, today))
            results = c.fetchall()
            
            for entrada, saida in results:
                if entrada:
                    entrada_dt = datetime.datetime.strptime(f"{today} {entrada}", "%d-%m-%Y %H:%M:%S")
                    self.records.append(entrada_dt)
                if saida:
                    saida_dt = datetime.datetime.strptime(f"{today} {saida}", "%d-%m-%Y %H:%M:%S")
                    self.records.append(saida_dt)
            
            conn.close()
        except sqlite3.Error as e:
            print(f"Erro ao carregar registros do dia: {e}")

    def clock_in(self):
        now = datetime.datetime.now()
        photo_blob = capture_photo()
        if photo_blob:
            if insert_record(self.name, self.pin, now, photo_blob, self.setor, self.supervisor):
                self.records.append(now)
                self.analyze_records()
                time.sleep(1)

    def analyze_records(self):
        """Analisa os registros do funcionário do dia atual."""
        if len(self.records) == 2:
            # Cálculo do primeiro intervalo (Primeira entrada até primeira saída)
            time_diff = (self.records[1] - self.records[0]).total_seconds() / 3600  # em horas
            print(f"Primeiro período: {time_diff:.2f} horas")
        elif len(self.records) == 3:
            # Pode significar volta do almoço
            time_diff = (self.records[1] - self.records[0]).total_seconds() / 3600  # em horas
            print(f"Primeiro período: {time_diff:.2f} horas")
            # Tempo de almoço/intervalo
            break_time = (self.records[2] - self.records[1]).total_seconds() / 60  # em minutos
            print(f"Tempo de intervalo: {break_time:.2f} minutos")
        elif len(self.records) == 4:
            # Dia completo de trabalho
            first_period = (self.records[1] - self.records[0]).total_seconds() / 3600  # em horas
            second_period = (self.records[3] - self.records[2]).total_seconds() / 3600  # em horas
            total_time = first_period + second_period
            
            break_time = (self.records[2] - self.records[1]).total_seconds() / 60  # em minutos
            
            print(f"Primeiro período: {first_period:.2f} horas")
            print(f"Intervalo: {break_time:.2f} minutos")
            print(f"Segundo período: {second_period:.2f} horas")
            print(f"Tempo total trabalhado: {total_time:.2f} horas")
            
            # Verificar se o tempo total está dentro do esperado (ex: 8 horas)
            if 7.5 <= total_time <= 8.5:  # Tolerância de 30min
                print("Jornada de trabalho completa.")
            elif total_time < 7.5:
                print("Jornada de trabalho inferior ao esperado.")
            else:
                print("Horas extras registradas.")
        else:
            # Primeiro registro do dia
            print(f"Primeiro registro do dia às {self.records[0].strftime('%H:%M')}")

def main():
    create_table()
    employees = {}

    # Verificar e carregar dados dos funcionários
    try:
        if not os.path.exists(PEOPLE_CSV_PATH):
            messagebox.showerror("Erro", f"Arquivo {PEOPLE_CSV_PATH} não encontrado.")
            return

        with open(PEOPLE_CSV_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    pin = row['pin']
                    name = row['name']
                    setor = row.get('setor', 'N/A')  # Usar get com valor padrão para campos opcionais
                    supervisor = row.get('supervisor', 'N/A')
                    employees[pin] = Employee(name, pin, setor, supervisor)
                except KeyError as e:
                    print(f"Erro ao processar linha do CSV: campo {e} ausente")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao carregar dados dos funcionários: {e}")
        return

    # Configurar tratamento de sinal para saída limpa
    def signal_handler(sig, frame):
        print("\nPrograma encerrado pelo usuário.")
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    def get_pin():
        global photo_window_open
        pin = None

        def submit_pin():
            nonlocal pin
            pin = pin_entry.get().strip()
            root.quit()

        with lock:
            while photo_window_open:
                time.sleep(0.1)

            root = ThemedTk(theme="equilux")
            root.title("Entrada de PIN")
            root.attributes("-topmost", True)
            root.attributes("-fullscreen", True)

            style = ttk.Style(root)
            style.theme_use('equilux')

            frame = ttk.Frame(root, padding="10")
            frame.pack(expand=True, fill=tk.BOTH)

            label = ttk.Label(frame, text="Digite seu PIN:", font=("Helvetica", 16))
            label.pack(pady=10)

            pin_entry = ttk.Entry(frame, font=("Helvetica", 16), justify='center')
            pin_entry.pack(pady=10)
            pin_entry.focus_set()

            submit_button = ttk.Button(frame, text="Enviar", command=submit_pin)
            submit_button.pack(pady=10)

            root.bind('<Return>', lambda event: submit_pin())

            root.mainloop()
            root.destroy()
        return pin

    def confirm_employee(employee):
        confirmed = False

        def confirm():
            nonlocal confirmed
            confirmed = True
            root.quit()

        def cancel():
            root.quit()

        with lock:
            root = ThemedTk(theme="equilux")
            root.title("Confirmação de Funcionário")
            root.attributes("-topmost", True)
            root.attributes("-fullscreen", True)

            style = ttk.Style(root)
            style.theme_use('equilux')

            frame = ttk.Frame(root, padding="10")
            frame.pack(expand=True, fill=tk.BOTH)

            label = ttk.Label(frame, text=f"Nome: {employee.name}, Setor: {employee.setor}. É você?", font=("Helvetica", 16))
            label.pack(pady=10)

            button_frame = ttk.Frame(frame)
            button_frame.pack(pady=10)

            confirm_button = ttk.Button(button_frame, text="Sim", command=confirm)
            confirm_button.pack(side=tk.LEFT, padx=20)

            cancel_button = ttk.Button(button_frame, text="Não", command=cancel)
            cancel_button.pack(side=tk.RIGHT, padx=20)

            root.bind('<Return>', lambda event: confirm())
            confirm_button.bind('<Return>', lambda event: confirm())

            root.mainloop()
            root.destroy()
        return confirmed

    while True:
        pin = get_pin()
        if pin == '----':
            print("Encerrando o programa.")
            break
        if pin in employees:
            employee = employees[pin]
            if confirm_employee(employee):
                employee.clock_in()
                time.sleep(5)
            else:
                messagebox.showerror("Erro", "Confirmação falhou. Tente novamente.")
        else:
            messagebox.showerror("Erro", "PIN incorreto. Tente novamente.")

if __name__ == "__main__":
    main()
