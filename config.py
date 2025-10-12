# Файл: config.py

from dataclasses import dataclass

@dataclass
class BotConfig:
    token: str
    google_api_key: str # <-- Меняем openai_api_key на это

# Вставь сюда свои токены
config = BotConfig(
    token="6557143615:AAGgda_7ctfLozZVOg8pLTiseulRckaV4sg",
    google_api_key="AIzaSyB7ZDvnKeLRD-kD_fa5P8_SHokPHjxhUA4" # <-- А сюда вставь свой новый ключ от Google AI
)