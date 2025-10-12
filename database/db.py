# Файл: my_chatgpt_bot/database/db.py
# ВЕРСИЯ "ТУРБО" - ПРИНИМАЕМ ЗАГОЛОВОК

import aiosqlite
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
DB_NAME = 'database/database.db'

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("PRAGMA table_info(chats)")
        columns = [row[1] for row in await cursor.fetchall()]
        if 'model_version' not in columns:
            logging.info("Колонка 'model_version' не найдена. Добавляю...")
            await db.execute("ALTER TABLE chats ADD COLUMN model_version TEXT DEFAULT 'gemini-1.5-flash'")
            logging.info("Колонка 'model_version' добавлена.")

        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                registration_date TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                created_at TEXT,
                title TEXT DEFAULT 'Новый чат',
                model_version TEXT DEFAULT 'gemini-1.5-flash',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
            )
        ''')
        await db.commit()
    logging.info("База данных успешно инициализирована.")

async def add_user(user_id, username, first_name):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if await cursor.fetchone() is None:
            await db.execute(
                "INSERT INTO users (user_id, username, first_name, registration_date) VALUES (?, ?, ?, ?)",
                (user_id, username, first_name, datetime.now().isoformat())
            )
            await db.commit()

# ИЗМЕНЕНИЕ ЗДЕСЬ! Добавляем `title` в аргументы
async def create_new_chat(user_id, model_version='gemini-1.5-flash', title='Новый чат'):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "INSERT INTO chats (user_id, created_at, title, model_version) VALUES (?, ?, ?, ?)",
            (user_id, datetime.now().isoformat(), title, model_version)
        )
        await db.commit()
        return cursor.lastrowid

async def update_chat_title(chat_id, new_title):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE chats SET title = ? WHERE chat_id = ?", (new_title, chat_id))
        await db.commit()
        logging.info(f"Заголовок чата {chat_id} обновлен на '{new_title}'")

async def delete_chat(chat_id, user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT user_id FROM chats WHERE chat_id = ?", (chat_id,))
        chat_owner = await cursor.fetchone()
        if not chat_owner or chat_owner[0] != user_id:
            logging.warning(f"Попытка несанкционированного удаления чата {chat_id} пользователем {user_id}")
            return False
        
        await db.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        await db.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
        await db.commit()
        logging.info(f"Чат {chat_id} и все его сообщения были удалены.")
        return True

async def get_user_chats(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT chat_id, title, model_version FROM chats WHERE user_id = ? ORDER BY created_at DESC", 
            (user_id,)
        )
        chats = await cursor.fetchall()
        return [{"chat_id": row[0], "title": row[1], "model_version": row[2]} for row in chats]

async def add_message_to_history(chat_id, role, content):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO messages (chat_id, role, content, timestamp) VALUES (?, ?, ?, ?)", (chat_id, role, content, datetime.now().isoformat()))
        await db.commit()

async def get_chat_history(chat_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT role, content FROM messages WHERE chat_id = ? ORDER BY timestamp ASC", (chat_id,))
        rows = await cursor.fetchall()
        history = [{"role": row[0], "parts": [{"text": row[1]}]} for row in rows]
        return history

async def get_chat_model(chat_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT model_version FROM chats WHERE chat_id = ?", (chat_id,))
        model = await cursor.fetchone()
        return model[0] if model else 'gemini-2.5-flash'