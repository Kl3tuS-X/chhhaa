# Файл: upgrade_db.py

import sqlite3
import logging

# Настраиваем логи, чтобы видеть, что происходит
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_NAME = 'database/database.db'

def upgrade_database():
    """
    Этот скрипт добавляет колонку 'title' в таблицу 'chats', если ее там еще нет.
    Его можно безопасно запускать несколько раз.
    """
    logging.info(f"Подключаюсь к базе данных: {DB_NAME}")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Получаем информацию о таблице chats
        cursor.execute("PRAGMA table_info(chats)")
        columns = [row[1] for row in cursor.fetchall()]

        # Проверяем, есть ли уже нужная колонка
        if 'title' in columns:
            logging.info("Колонка 'title' уже существует. Ничего делать не нужно.")
        else:
            logging.info("Колонка 'title' не найдена. Добавляю...")
            # Выполняем апгрейд
            cursor.execute("ALTER TABLE chats ADD COLUMN title TEXT DEFAULT 'Новый чат'")
            conn.commit()
            logging.info("Успех! Колонка 'title' была успешно добавлена.")

    except sqlite3.Error as e:
        logging.error(f"Произошла ошибка SQLite: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("Соединение с базой данных закрыто.")

if __name__ == "__main__":
    upgrade_database()