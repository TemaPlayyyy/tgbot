# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Загружает .env (только для разработки)

class Config:  #  класс Config
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

    @staticmethod
    def validate():
        if not all([Config.TELEGRAM_TOKEN, Config.DEEPSEEK_API_KEY]):
            raise ValueError("Missing environment variables!")