import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8541616922:AAGw9wnbHGLe2yBlvxurAp2Vbh7q7T-K6Jk"
DB_PATH = "baza.db"
ALLOWED_USERS = [1979851980, 7691730481, 987654321]  # три разрешённых пользователя

# Проверка доступа
def restricted(func):
    def wrapper(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USERS:
            update.message.reply_text("Доступ запрещён.")
            return
        return func(update, context)
    return wrapper

# Работа с базой
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  price REAL,
                  quantity INTEGER)''')
    conn.commit()
    conn.close()

def add_product(name, price, quantity):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO products (name, price, quan
