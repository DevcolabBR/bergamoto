#%%
import telebot
from telebot import types
import schedule
import time
import threading
import os
import pandas as pd
import sqlite3

from dotenv import load_dotenv

load_dotenv()

# Acessar as variáveis ambiente
api_key = os.getenv('API_KEY')
secret_key = os.getenv('SECRET_KEY')
db_password = os.getenv('DB_PASSWORD')
if api_key is None:
    raise ValueError("API_KEY environment variable not found")


bot = telebot.TeleBot(api_key)
# Dicionário para armazenar o estado do usuário
user_states = {}

# Arte ASCII para a mensagem de boas-vindas
ascii_art = """
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█
█░██░██░██░██░██░██░██░██░██░░░░░░░░░░█
█░██░██░██░██░██░██░██░██░██░░░░░░░░░░█
█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░█░░░░█▀▀▀█░█▀▀█░█▀▀▄░▀█▀░█▄░░█░█▀▀█░░
░░█░░░░█░░░█░█▄▄█░█░░█░░█░░█░█░█░█░▄▄░░
░░█▄▄█░█▄▄▄█░█░░█░█▄▄▀░▄█▄░█░░▀█░█▄▄█░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""

# Função para iniciar a interação com o bot
@bot.message_handler(commands=['start'])
def start(mensagem):
    chat_id = mensagem.chat.id
    comandos = [
        "/falta - exibir faltas",
        "/query - lista as querys",
        "/comando3 - Adicionar arquivos CSV ao banco de dados"
    ]
    resposta = "Olá! Bem-vindo ao bot. Aqui estão os comandos disponíveis:\n" + "\n".join(comandos)
    bot.send_message(chat_id, ascii_art)
    bot.send_message(chat_id, resposta)
    

# Função para receber e salvar tabelas CSV enviadas pelo usuário
@bot.message_handler(commands=['falta'])
def executar_notific_faltas(mensagem):
    chat_id = mensagem.chat.id
    try:
        # Executar o script notific-faltas.py e capturar a saída
        output = os.popen('python3 /home/br4b0/Desktop/foss/DevcolabBR/bergamoto/bot/notific-faltas.py').read()
        bot.send_message(chat_id, f"Saída do script notific-faltas.py:\n{output}")
    except Exception as e:
        bot.send_message(chat_id, f"Erro ao executar o script notific-faltas.py: {str(e)}")



# Iniciar o agendamento em um thread separado
def agendar_envio_diario():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=agendar_envio_diario).start()

# Iniciar o bot
bot.polling()
# %%