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
if api_key is None:
    raise ValueError("API_KEY environment variable not found")


bot = telebot.TeleBot(api_key)


