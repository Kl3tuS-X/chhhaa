# Файл: my_chatgpt_bot/api/router.py
# ВЕРСИЯ "ТУРБО" - МГНОВЕННЫЕ ЗАГОЛОВКИ

import logging
import json
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel
import google.generativeai as genai

from config import config
from database import db

# --- Pydantic модели (без изменений) ---
class UserIDRequest(BaseModel):
    user_id: int

class ChatRequest(BaseModel):
    chat_id: Optional[int] = None
    user_id: int
    text: str
    model_version: Optional[str] = None

class HistoryRequest(BaseModel):
    chat_id: int

class DeleteChatRequest(BaseModel):
    chat_id: int
    user_id: int

# --- Настройка Gemini ---
genai.configure(api_key=config.google_api_key)
MODELS = {
    "gemini-2.5-flash": genai.GenerativeModel('gemini-2.5-flash'),
    "gemini-2.5-pro": genai.GenerativeModel('gemini-2.5-pro')
}

# --- API Роутер ---
api_router = APIRouter()

# --- Эндпоинты /get_user_chats, /get_chat_history, /delete_chat (без изменений) ---
@api_router.post("/api/get_user_chats")
async def get_user_chats_endpoint(request: UserIDRequest):
    chats = await db.get_user_chats(request.user_id)
    return {"chats": chats}

@api_router.post("/api/get_chat_history")
async def get_chat_history_endpoint(request: HistoryRequest):
    history = await db.get_chat_history(request.chat_id)
    return {"history": history}

@api_router.post("/api/delete_chat")
async def delete_chat_endpoint(request: DeleteChatRequest):
    success = await db.delete_chat(request.chat_id, request.user_id)
    updated_chats = await db.get_user_chats(request.user_id)
    return {"success": success, "updated_chats": updated_chats}

# --- УСКОРЕННЫЙ ЭНДПОИНТ ЧАТА ---
@api_router.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    user_id = request.user_id
    chat_id = request.chat_id
    user_text = request.text
    is_new_chat = False

    try:
        if chat_id is None:
            is_new_chat = True
            model_to_create = request.model_version or 'gemini-2.5-flash'
            
            # *** УСКОРЕНИЕ ЗДЕСЬ! ***
            # Создаем заголовок сразу, без API вызова. Берем первые 5 слов.
            title_words = user_text.split()
            new_title = ' '.join(title_words[:5])
            if len(title_words) > 5:
                new_title += '...'

            # Создаем чат сразу с осмысленным заголовком
            chat_id = await db.create_new_chat(user_id, model_to_create, title=new_title)

        model_name = await db.get_chat_model(chat_id)
        selected_model = MODELS.get(model_name, MODELS['gemini-2.5-flash'])

        await db.add_message_to_history(chat_id, "user", user_text)

        full_history = await db.get_chat_history(chat_id)
        gemini_history = [
            {"role": msg["role"], "parts": msg["parts"]} for msg in full_history
        ]

        # Единственный долгий процесс - ожидание ответа от модели
        chat_session = selected_model.start_chat(history=gemini_history[:-1])
        response = await chat_session.send_message_async(gemini_history[-1]['parts'])
        bot_response = response.text

        await db.add_message_to_history(chat_id, "model", bot_response)

        # Теперь нам не нужно генерировать заголовок после, мы сделали это вначале
        # if is_new_chat: ... -> этот блок больше не нужен

        return {
            "response": bot_response,
            "chat_id": chat_id,
        }

    except Exception as e:
        logging.error(f"Критическая ошибка в chat_endpoint для чата {chat_id}: {e}")
        return {
            "response": "Извините, на моей стороне произошла серьезная ошибка. Попробуйте начать новый диалог.",
            "chat_id": chat_id,
        }