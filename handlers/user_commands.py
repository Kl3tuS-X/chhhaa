# Файл: handlers/user_commands.py

from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import add_user

router = Router()

# ЗАМЕНИ ЭТУ ССЫЛКУ НА СВОЮ ИЗ NGROK!
# Важно: ссылка должна быть https
WEB_APP_URL = "https://carey-pseudoperipteral-kyra.ngrok-free.dev"


@router.message(Command("start"))
async def handle_start(message: types.Message):
    """
    Обработчик команды /start.
    Приветствует пользователя и добавляет его в базу данных.
    """
    user = message.from_user
    await add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    await message.answer(
        f"Привет, {user.first_name}! 🚀\n"
        "Я твой персональный AI-ассистент. Чтобы открыть интерфейс, введи команду /app"
    )

@router.message(Command("app"))
async def handle_app(message: types.Message):
    """
    Обработчик команды /app.
    Отправляет кнопку для открытия Web App.
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🤖 Открыть интерфейс ChatGPT",
        web_app=types.WebAppInfo(url=f"{WEB_APP_URL}/index.html")
    )
    await message.answer(
        "Нажми на кнопку ниже, чтобы открыть приложение:",
        reply_markup=builder.as_markup()
    )


@router.message()
async def echo_message(message: types.Message):
    """
    Простое эхо в ответ на любое сообщение, которое не является командой.
    Пока что для проверки.
    """
    await message.answer("Я получил твое сообщение. Для открытия интерфейса используй команду /app")