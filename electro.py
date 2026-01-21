import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# -------------------- НАСТРОЙКИ --------------------
TOKEN = "8541616922:AAGw9wnbHGLe2yBlvxurAp2Vbh7q7T-K6Jk"  # твой токен
DB_PATH = "baza.db"
ALLOWED_USERS = [1979851980, 7691730481, 987654321]  # ID разрешённых пользователей

# -------------------- ПРОВЕРКА ДОСТУПА --------------------
def restricted(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USERS:
            await update.message.reply_text("Доступ запрещён.")
            return
        await func(update, context)
    return wrapper

# -------------------- БАЗА ДАННЫХ --------------------
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

# -------------------- КОМАНДЫ БОТА --------------------
@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот магазина ElectroMax.\nИспользуй /add название цена количество, /list для списка товаров."
    )

@restricted
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("Используй: /add название цена количество")
            return
        name = args[0]
        price = float(args[1])
        quantity = int(args[2])
        add_product(name, price, quantity)
        await update.message.reply_text(f"Товар {name} добавлен: {quantity} шт по цене {price}.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

@restricted
async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = list_products()
    if not items:
        await update.message.reply_text("Список товаров пуст.")
        return
    msg = "\n".join([f"{name} — {quantity} шт — цена {price}" for name, price, quantity in items])
    await update.message.reply_text(msg)

# -------------------- ЗАПУСК --------------------
def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_items))

    app.run_polling()

if __name__ == "__main__":
    main()

