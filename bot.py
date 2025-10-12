# Файл: bot.py
# ВЕРСИЯ ДЛЯ СЕРВЕРА (WEBHOOK)

import asyncio
import logging
import uvicorn
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from aiogram import Bot, Dispatcher, types

from config import config
from database.db import init_db
from handlers import user_commands
from api.router import api_router

# --- Настройка ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения, а не из конфига напрямую
# Это безопаснее и является стандартом для серверов
TOKEN = os.getenv("BOT_TOKEN", config.token)
WEB_APP_URL_FROM_ENV = os.getenv("WEB_APP_URL") # Для установки вебхука

# Адрес, который будет слушать наш бот
WEBHOOK_PATH = f"/webhook/{TOKEN}"
# Полный адрес для установки в Telegram
WEBHOOK_URL = f"{WEB_APP_URL_FROM_ENV}{WEBHOOK_PATH}"

# --- Инициализация ---
app = FastAPI()
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(user_commands.router)
app.include_router(api_router)
# Статику монтируем в корень
app.mount("/", StaticFiles(directory="static", html=True), name="static")


# --- Логика Webhook ---
@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    """
    Эта функция ловит все обновления от Telegram,
    как только мы установим вебхук.
    """
    telegram_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)

# --- Жизненный цикл приложения ---
@app.on_event("startup")
async def on_startup():
    """
    Выполняется один раз при старте сервера.
    Инициализирует БД и устанавливает вебхук.
    """
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("База данных инициализирована.")
    
    logger.info(f"Устанавливаю вебхук: {WEBHOOK_URL}")
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)
        logger.info("Вебхук успешно установлен.")
    else:
        logger.info("Вебхук уже был установлен.")

@app.on_event("shutdown")
async def on_shutdown():
    """Выполняется при остановке сервера."""
    logger.info("Удаляю вебхук...")
    await bot.delete_webhook()
    logger.info("Вебхук удален.")

# Этот блок больше не нужен, так как мы не запускаем polling
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080)