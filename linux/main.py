"""
Sistema de Registro de Ponto - Bergamoto
----------------------------------------
Este programa implementa um sistema de registro de ponto eletrônico com 
captura de foto para confirmar a identidade do funcionário.

O sistema permite:
1. Registro de entrada e saída de funcionários
2. Captura de fotos para confirmação visual 
3. Cálculo automático de horas trabalhadas
4. Análise de períodos e intervalos de trabalho
"""

# === Bibliotecas de Data e Hora ===
import datetime  # Manipulação de datas e horários para registros de ponto e cálculos de horas trabalhadas
import time      # Funções relacionadas com tempo para pausas e medição de intervalos

# === Bibliotecas de Banco de Dados ===
import sqlite3   # Interface para banco de dados SQLite, usado para armazenar registros de ponto

# === Bibliotecas de Interface Gráfica ===
import tkinter as tk                # Interface gráfica principal
from tkinter import messagebox, ttk  # Caixas de diálogo e widgets temáticos
from ttkthemes import ThemedTk       # Temas visuais modernos para a interface

# === Bibliotecas de Processamento de Imagem ===
import cv2                # OpenCV para captura de vídeo da webcam
from PIL import Image, ImageTk  # Manipulação e exibição de imagens na interface

# === Bibliotecas de Sistema ===
import os        # Operações do sistema de arquivos (caminhos, diretórios)
import signal    # Tratamento de sinais do sistema operacional (SIGINT, etc.)
import threading # Multithreading para operações concorrentes
import io        # Operações de entrada/saída em memória (para processamento de imagens)
import csv       # Processamento de arquivos CSV (dados de funcionários)

# Configuração de caminhos - define a localização dos arquivos no sistema
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
DB_PATH = os.path.join(DATA_DIR, 'bergamoto.db')  # Banco de dados SQLite
PEOPLE_CSV_PATH = os.path.join(DATA_DIR, 'people.csv')  # Arquivo CSV com informações dos funcionários

# Variáveis de controle global
photo_window_open = False  # Controla se a janela de foto está aberta
lock = threading.Lock()  # Lock para garantir thread safety em operações críticas

def create_table():
    """
    Cria a tabela de horários no banco de dados se ela não existir.
    A tabela segue o esquema: id, pin, nome, data, entrada, saida, horas_trabalhadas.
    
    Esta função é executada na inicialização do programa para garantir que a estrutura
    do banco de dados esteja pronta para registrar os pontos dos funcionários.
    """
    # Garantir que o diretório de dados exista antes de continuar
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    conn = None
    try:
        # Conecta ao banco de dados SQLite
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Verifica se a tabela já existe antes de tentar criá-la
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
        # Garante que a conexão seja fechada mesmo em caso de erro
        if conn:
            conn.close()

def insert_record(name, pin, timestamp, photo_blob, setor, supervisor):
    """
    Insere um novo registro de ponto para um funcionário.
    
    Parâmetros:
    - name: Nome do funcionário
    - pin: Código de identificação do funcionário
    - timestamp: Data e hora do registro
    - photo_blob: Foto capturada no momento do registro (formato BLOB)
    - setor: Setor do funcionário
    - supervisor: Supervisor do funcionário
    
    Retorna:
    - True se o registro foi inserido com sucesso
    - False se ocorreu algum erro ou o limite de registros diários foi atingido
    
    Esta função gerencia a lógica de entrada e saída. Um funcionário pode ter
    até 4 registros por dia (entrada manhã, saída manhã, entrada tarde, saída tarde).
    """
    data = timestamp.strftime("%d-%m-%Y")  # Formato de data: dia-mês-ano
    hora = timestamp.strftime("%H:%M:00")  # Formato de hora: hora:minuto:segundo
    
    conn = None
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Verificar número de registros existentes para o funcionário no dia atual
        c.execute("SELECT COUNT(*) FROM horarios WHERE pin = ? AND data = ?", (pin, data))
        record_count = c.fetchone()[0]
        
        # Limite de 4 registros por dia (2 entradas e 2 saídas)
        if record_count >= 4:
            messagebox.showwarning("Limite Atingido", "Você já fez 4 registros hoje.")
            return False

        # Determinar se é entrada ou saída com base no número de registros
        # Registros ímpares (1º, 3º) são entradas, registros pares (2º, 4º) são saídas
        tipo_registro = "entrada" if record_count % 2 == 0 else "saida"
        
        if tipo_registro == "entrada":
            # Inserir registro de entrada (novo registro)
            c.execute("INSERT INTO horarios (pin, nome, data, entrada) VALUES (?, ?, ?, ?)", 
                    (pin, name, data, hora))
        else:
            # Para registros de saída, tenta encontrar uma entrada sem par
            c.execute("""
                SELECT id, entrada FROM horarios 
                WHERE pin = ? AND data = ? AND saida IS NULL 
                ORDER BY id DESC LIMIT 1
            """, (pin, data))
            
            resultado = c.fetchone()
            if resultado:
                # Se encontrar uma entrada sem saída, atualiza o registro
                registro_id, hora_entrada = resultado
                
                # Calcula horas trabalhadas entre entrada e saída
                fmt = "%H:%M:%S"
                entrada_dt = datetime.datetime.strptime(hora_entrada, fmt)
                saida_dt = datetime.datetime.strptime(hora, fmt)
                
                # Diferença em horas (formato decimal)
                diferenca = (saida_dt - entrada_dt).total_seconds() / 3600
                
                # Atualiza o registro existente
                c.execute("""
                    UPDATE horarios SET saida = ?, horas_trabalhadas = ?
                    WHERE id = ?
                """, (hora, diferenca, registro_id))
            else:
                # Se não encontrar uma entrada correspondente, cria um registro só de saída
                # (situação atípica, mas tratada para robustez)
                c.execute("INSERT INTO horarios (pin, nome, data, saida) VALUES (?, ?, ?, ?)", 
                        (pin, name, data, hora))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        # Em caso de erro no banco de dados, desfaz as alterações
        if conn:
            conn.rollback()
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao inserir registro: {e}")
        return False
    finally:
        # Garante que a conexão seja sempre fechada
        if conn:
            conn.close()

def capture_photo():
    """
    Abre uma janela para capturar uma foto do funcionário usando a webcam.
    
    A função exibe um preview da câmera e automaticamente tira uma foto após 3 segundos,
    ou quando o usuário clicar no botão ou pressionar Enter.
    
    Retorna:
    - Um objeto BLOB contendo a foto capturada em formato PNG
    - None se ocorrer algum erro durante a captura
    """
    global photo_window_open
    img_blob = None

    def take_photo(event=None):
        """
        Função para capturar uma foto da câmera.
        Aceita um parâmetro event opcional para funcionar com eventos Tkinter.
        
        A foto é convertida para PNG e armazenada como BLOB.
        """
        nonlocal img_blob
        try:
            ret, frame = cam.read()
            if ret:
                # Converter o frame para formato PIL e salvar como PNG
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

    # Variáveis para armazenar imagens e evitar coleta de lixo pelo garbage collector
    # Isso é necessário porque Tkinter pode coletar objetos PhotoImage se não tiverem referências
    photo_references = []
    
    def show_frame():
        """
        Atualiza continuamente o frame exibido na janela da câmera.
        
        Esta função:
        1. Captura um frame da câmera
        2. Converte para formato que o Tkinter pode exibir
        3. Atualiza a imagem no label
        4. Agenda a próxima atualização
        
        É executada repetidamente para criar um preview em tempo real.
        """
        if not cam.isOpened() or not root.winfo_exists():
            return
        try:
            ret, frame = cam.read()
            if ret:
                # Converter frame BGR do OpenCV para RGBA para exibição no Tkinter
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Evitar coleta de lixo (garbage collection) das imagens
                photo_references.append(imgtk)
                if len(photo_references) > 10:  # Limitar o número de referências armazenadas
                    photo_references.pop(0)
                
                # Atualizar a imagem exibida
                lmain.configure(image=imgtk)
            
            # Agendar a próxima atualização do frame (10ms - ~100 FPS)
            if root.winfo_exists():
                lmain.after(10, show_frame)
        except Exception:
            # Em caso de erro, apenas encerrar a atualização
            pass

    # Inicializar a câmera (dispositivo 0 - webcam padrão)
    cam = cv2.VideoCapture(0)
    
    # Criar a janela para exibição do preview da câmera
    root = ThemedTk(theme="equilux")  # Usar tema escuro para melhor aparência
    root.title("Captura de Foto")
    root.attributes("-topmost", True)  # Manter janela sempre visível
    root.attributes("-fullscreen", True)  # Usar modo tela cheia para melhor visualização

    # Configurar estilo dos widgets
    style = ttk.Style(root)
    style.theme_use('equilux')

    # Criar frame principal
    frame = ttk.Frame(root, padding="10")
    frame.pack(expand=True, fill=tk.BOTH)

    # Label onde será exibido o preview da câmera
    lmain = ttk.Label(frame)
    lmain.pack(expand=True)

    # Botão para capturar a foto manualmente
    capture_button = ttk.Button(frame, text="Capturar Foto", command=take_photo)
    capture_button.pack(pady=10)

    # Permitir captura da foto com a tecla Enter
    root.bind('<Return>', take_photo)

    # Marcar que a janela de foto está aberta
    photo_window_open = True
    
    # Iniciar o preview da câmera
    show_frame()
    
    # Capturar automaticamente após 3 segundos
    root.after(3000, take_photo)
    
    # Iniciar loop da interface
    root.mainloop()
    
    # Limpeza de recursos
    cam.release()
    cv2.destroyAllWindows()
    root.destroy()
    photo_window_open = False
    
    # Retornar a foto capturada como BLOB
    return img_blob

class Employee:
    """
    Classe que representa um funcionário no sistema de registro de ponto.
    
    Esta classe gerencia informações do funcionário e seus registros de ponto,
    incluindo registro de entrada/saída e análise de horas trabalhadas.
    """
    
    def __init__(self, name, pin, setor, supervisor):
        """
        Inicializa um objeto Employee com informações básicas do funcionário.
        
        Parâmetros:
        - name: Nome do funcionário
        - pin: Código de identificação único do funcionário
        - setor: Setor onde o funcionário trabalha
        - supervisor: Nome do supervisor do funcionário
        """
        self.name = name
        self.pin = pin
        self.setor = setor
        self.supervisor = supervisor
        self.records = []  # Lista para armazenar registros de ponto do dia
        
        # Carregar registros do dia atual do banco de dados
        self.load_today_records()

    def load_today_records(self):
        """
        Carrega do banco de dados todos os registros de ponto do funcionário para o dia atual.
        
        A função converte as strings de data/hora em objetos datetime e 
        popula a lista self.records com todos os registros encontrados.
        """
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Busca todos os registros do funcionário no dia de hoje
            c.execute("SELECT entrada, saida FROM horarios WHERE pin = ? AND data = ? ORDER BY id", 
                    (self.pin, today))
            results = c.fetchall()
            
            # Processa cada registro encontrado
            for entrada, saida in results:
                # Adiciona o horário de entrada (se existir)
                if entrada:
                    entrada_dt = datetime.datetime.strptime(f"{today} {entrada}", "%d-%m-%Y %H:%M:%S")
                    self.records.append(entrada_dt)
                
                # Adiciona o horário de saída (se existir)
                if saida:
                    saida_dt = datetime.datetime.strptime(f"{today} {saida}", "%d-%m-%Y %H:%M:%S")
                    self.records.append(saida_dt)
            
            conn.close()
        except sqlite3.Error as e:
            print(f"Erro ao carregar registros do dia: {e}")

    def clock_in(self):
        """
        Registra um ponto (entrada ou saída) para o funcionário.
        
        Esta função:
        1. Captura a data/hora atual
        2. Solicita uma foto do funcionário
        3. Registra o ponto no banco de dados
        4. Atualiza a lista de registros
        5. Analisa os registros para calcular horas trabalhadas
        """
        now = datetime.datetime.now()  # Momento exato do registro
        
        # Capturar foto do funcionário para confirmação visual
        photo_blob = capture_photo()
        
        if photo_blob:  # Se a foto foi capturada com sucesso
            # Inserir o registro no banco de dados
            if insert_record(self.name, self.pin, now, photo_blob, self.setor, self.supervisor):
                # Se o registro foi salvo com sucesso
                self.records.append(now)  # Adiciona à lista de registros do dia
                self.analyze_records()    # Analisa os registros para cálculos
                time.sleep(1)  # Pequena pausa para mostrar feedbacks na interface

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
    """
    Função principal do sistema de registro de ponto.
    
    Esta função:
    1. Configura o ambiente e o banco de dados
    2. Carrega informações de funcionários do arquivo CSV
    3. Gerencia a interface principal para registro de ponto
    4. Controla o fluxo de entrada/saída de funcionários
    """
    # Garantir que a tabela de horários existe no banco de dados
    create_table()
    
    # Dicionário para armazenar funcionários (chave = PIN)
    employees = {}

    # Carregar dados dos funcionários do arquivo CSV
    try:
        if not os.path.exists(PEOPLE_CSV_PATH):
            messagebox.showerror("Erro", f"Arquivo {PEOPLE_CSV_PATH} não encontrado.")
            return

        # Abrir o arquivo CSV e carregar os dados
        with open(PEOPLE_CSV_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Extrair informações da linha do CSV
                    pin = row['pin']
                    name = row['name']
                    # Usar .get() para campos que podem estar ausentes
                    setor = row.get('setor', 'N/A')  
                    supervisor = row.get('supervisor', 'N/A')
                    
                    # Criar objeto Employee e armazenar no dicionário
                    employees[pin] = Employee(name, pin, setor, supervisor)
                except KeyError as e:
                    print(f"Erro ao processar linha do CSV: campo {e} ausente")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao carregar dados dos funcionários: {e}")
        return

    # Configurar tratamento de sinal para saída limpa do programa (Ctrl+C)
    def signal_handler(sig, frame):
        print("\nPrograma encerrado pelo usuário.")
        exit(0)

    # Registrar handler para SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    def get_pin():
        """
        Exibe uma janela para o funcionário digitar seu PIN.
        
        Esta função cria uma interface para entrada de PIN e retorna o valor digitado.
        O sistema usa threading para evitar conflitos entre múltiplas janelas.
        
        Retorna:
        - String contendo o PIN digitado pelo funcionário
        """
        global photo_window_open
        pin = None

        def submit_pin():
            """Coleta o PIN digitado e fecha a janela"""
            nonlocal pin
            pin = pin_entry.get().strip()
            root.quit()

        # Uso do lock para garantir thread safety
        with lock:
            # Esperar que qualquer janela de foto aberta seja fechada
            while photo_window_open:
                time.sleep(0.1)

            # Criar a janela para entrada de PIN
            root = ThemedTk(theme="equilux")
            root.title("Entrada de PIN")
            root.attributes("-topmost", True)  # Manter sempre visível
            root.attributes("-fullscreen", True)  # Modo tela cheia

            # Configuração de estilo
            style = ttk.Style(root)
            style.theme_use('equilux')

            # Frame principal
            frame = ttk.Frame(root, padding="10")
            frame.pack(expand=True, fill=tk.BOTH)

            # Texto instrucional
            label = ttk.Label(frame, text="Digite seu PIN:", font=("Helvetica", 16))
            label.pack(pady=10)

            # Campo de entrada do PIN
            pin_entry = ttk.Entry(frame, font=("Helvetica", 16), justify='center')
            pin_entry.pack(pady=10)
            pin_entry.focus_set()  # Foco automático no campo de entrada

            # Botão de envio
            submit_button = ttk.Button(frame, text="Enviar", command=submit_pin)
            submit_button.pack(pady=10)

            # Permitir uso da tecla Enter para submeter
            root.bind('<Return>', lambda event: submit_pin())

            # Iniciar loop da interface
            root.mainloop()
            root.destroy()
            
        return pin

    def confirm_employee(employee):
        """
        Exibe uma janela de confirmação para verificar a identidade do funcionário.
        
        Mostra informações do funcionário (nome e setor) e solicita confirmação
        de que é realmente o funcionário correto fazendo o registro.
        
        Parâmetros:
        - employee: Objeto Employee contendo informações do funcionário
        
        Retorna:
        - True se o funcionário confirmar sua identidade
        - False se o funcionário negar ou cancelar
        """
        confirmed = False

        def confirm():
            """Função chamada quando o usuário confirma a identidade"""
            nonlocal confirmed
            confirmed = True
            root.quit()

        def cancel():
            """Função chamada quando o usuário cancela a confirmação"""
            root.quit()

        # Usar lock para thread safety
        with lock:
            # Criar janela de confirmação
            root = ThemedTk(theme="equilux")
            root.title("Confirmação de Funcionário")
            root.attributes("-topmost", True)
            root.attributes("-fullscreen", True)

            # Configuração de estilo
            style = ttk.Style(root)
            style.theme_use('equilux')

            # Frame principal
            frame = ttk.Frame(root, padding="10")
            frame.pack(expand=True, fill=tk.BOTH)

            # Texto de confirmação mostrando dados do funcionário
            label = ttk.Label(frame, text=f"Nome: {employee.name}, Setor: {employee.setor}. É você?", font=("Helvetica", 16))
            label.pack(pady=10)

            # Frame para botões
            button_frame = ttk.Frame(frame)
            button_frame.pack(pady=10)

            # Botão de confirmação (Sim)
            confirm_button = ttk.Button(button_frame, text="Sim", command=confirm)
            confirm_button.pack(side=tk.LEFT, padx=20)

            # Botão de cancelamento (Não)
            cancel_button = ttk.Button(button_frame, text="Não", command=cancel)
            cancel_button.pack(side=tk.RIGHT, padx=20)

            # Permitir uso da tecla Enter para confirmar
            root.bind('<Return>', lambda event: confirm())
            confirm_button.bind('<Return>', lambda event: confirm())

            # Iniciar loop da interface
            root.mainloop()
            root.destroy()
            
        return confirmed

    # Loop principal do programa - continua executando até ser explicitamente encerrado
    while True:
        # Solicitar PIN do funcionário
        pin = get_pin()
        
        # PIN especial para encerrar o programa
        if pin == '----':
            print("Encerrando o programa.")
            break
            
        # Verificar se o PIN existe no sistema
        if pin in employees:
            # Obter o objeto funcionário correspondente ao PIN
            employee = employees[pin]
            
            # Solicitar confirmação visual de identidade
            if confirm_employee(employee):
                # Se confirmado, registrar o ponto do funcionário
                employee.clock_in()
                time.sleep(5)  # Tempo para ver mensagens e resultados
            else:
                # Se não confirmado, mostrar mensagem de erro
                messagebox.showerror("Erro", "Confirmação falhou. Tente novamente.")
        else:
            # PIN não encontrado na base de dados
            messagebox.showerror("Erro", "PIN incorreto. Tente novamente.")

# Ponto de entrada do programa quando executado diretamente
if __name__ == "__main__":
    main()
