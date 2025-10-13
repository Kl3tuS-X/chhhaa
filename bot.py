# Файл: bot.py
# ВЕРСИЯ "FLY.IO READY" - ГОТОВ К ПОЛЕТУ

import logging
import os
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types

# --- Настройка ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("--- [FLY.IO] Запуск приложения ---")

# --- Переменные окружения ---
TOKEN = os.getenv("BOT_TOKEN")
# Fly.io автоматически создает переменную FLY_APP_NAME, из которой мы можем составить URL
FLY_APP_NAME = os.getenv("FLY_APP_NAME")
WEB_APP_URL_FROM_ENV = f"{FLY_APP_NAME}.fly.dev"

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://{WEB_APP_URL_FROM_ENV}{WEBHOOK_PATH}"

# --- Инициализация ---
app = FastAPI()
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Импорты и роутеры ---
from api.router import api_router
from handlers import user_commands
dp.include_router(user_commands.router)
app.include_router(api_router)
logger.info("--- Роутеры подключены ---")

# --- Статические файлы ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_PATH = os.path.join(BASE_DIR, "static")
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory=STATIC_PATH, html=True), name="static")

# --- Логика Webhook ---
@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)

# --- Жизненный цикл приложения ---
@app.on_event("startup")
async def on_startup():
    from database.db import init_db
    logger.info("--- Стартап: Инициализация БД ---")
    await init_db()
    logger.info(f"--- Стартап: Установка вебхука на {WEBHOOK_URL} ---")
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    logger.info("--- БОТ ГОТОВ К РАБОТЕ! ---")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Приложение останавливается...")
    await bot.delete_webhook()
