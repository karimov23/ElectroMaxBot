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
    c.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (name, price, quantity))
    conn.commit()
    conn.close()

def list_products():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, price, quantity FROM products")
    items = c.fetchall()
    conn.close()
    return items

# Команды бота
@restricted
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я бот магазина ElectroMax.\nИспользуй /add название цена количество, /list для списка товаров.")

@restricted
def add(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) != 3:
            update.message.reply_text("Используй: /add название цена количество")
            return
        name = args[0]
        price = float(args[1])
        quantity = int(args[2])
        add_product(name, price, quantity)
        update.message.reply_text(f"Товар {name} добавлен: {quantity} шт по цене {price}.")
    except Exception as e:
        update.message.reply_text(f"Ошибка: {e}")

@restricted
def list_items(update: Update, context: CallbackContext):
    items = list_products()
    if not items:
        update.message.reply_text("Список товаров пуст.")
        return
    msg = "\n".join([f"{name} — {quantity} шт — цена {price}" for name, price, quantity in items])
    update.message.reply_text(msg)

# Запуск бота
def main():
    init_db()
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("list", list_items))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
