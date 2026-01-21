# Electro.py - рабочий бот магазина ElectroMax
# Telegram бот с базой товаров, добавлением и списком товаров

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
from datetime import datetime

# ====== Настройки ======
TOKEN = "8541616922:AAGw9wnbHGLe2yBlvxurAp2Vbh7q7T-K6Jk"  # Твой токен
AUTHORIZED_USERS = [1979851980]  # Твой Telegram ID
DB_PATH = "baza.db"  # Файл базы данных

# ====== Создание базы (если нет) ======
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Таблица товаров
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    purchase_price REAL,
    sale_price REAL,
    margin REAL,
    quantity INTEGER
)
""")

# Таблица прихода
cursor.execute("""
CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    quantity INTEGER,
    purchase_price REAL,
    date TEXT
)
""")

# Таблица продаж
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    quantity INTEGER,
    sale_price REAL,
    date TEXT
)
""")

conn.commit()
conn.close()

# ====== Команды бота ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Доступ запрещён")
        return
    await update.message.reply_text("Привет! Бот ElectroMax запущен.")

# Добавление товара: /addproduct Название Закупка Продажа Кол-во
async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Доступ запрещён")
        return
    try:
        name = context.args[0]
        purchase = float(context.args[1])
        sale = float(context.args[2])
        quantity = int(context.args[3])
        margin = round((sale - purchase) / purchase * 100, 2)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, purchase_price, sale_price, margin, quantity)
            VALUES (?, ?, ?, ?, ?)
        """, (name, purchase, sale, margin, quantity))
        conn.commit()
        conn.close()

        await update.message.reply_text(f"Товар {name} добавлен! Маржа: {margin}%")
    except:
        await update.message.reply_text("Ошибка! Используй: /addproduct Название Закупка Продажа Кол-во")

# Список товаров и общий капитал: /listproducts
async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Доступ запрещён")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, purchase_price, quantity FROM products")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("Товаров нет!")
        return

    total_capital = 0
    msg = "Список товаров:\n"
    for r in rows:
        name, purchase, qty = r
        total = purchase * qty
        total_capital += total
        msg += f"{name}: {qty} шт. × {purchase} сом = {total} сом\n"
    msg += f"\nОбщий капитал вложен в товары: {total_capital} сом"
    await update.message.reply_text(msg)

# ====== Настройка и запуск бота ======
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addproduct", add_product))
app.add_handler(CommandHandler("listproducts", list_products))

print("Бот запущен...")
app.run_polling()
