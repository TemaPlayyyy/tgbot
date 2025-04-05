import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from openai import OpenAI
import asyncio
from typing import Optional
from config import Config

Config.validate()  # Проверяем, что переменные заданы


# --- Настройка логгера ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Инициализация бота ---
bot = Bot(token=Config.TELEGRAM_TOKEN)
dp = Dispatcher()
router = Router()

# --- Обработчики команд ---
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("🤖 Привет! Я AI-бот на базе DeepSeek. Задайте мне любой вопрос!")

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
💡 Как пользоваться ботом:
Просто напишите мне сообщение, и я постараюсь на него ответить!

🔹 Доступные команды:
/start - Начать диалог
/help - Получить справку
"""
    await message.answer(help_text)

# --- Функция запроса к AI API ---
async def get_ai_response(prompt: str) -> Optional[str]:
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Config.DEEPSEEK_API_KEY
        )

        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-zero:free",
            messages=[
                {
                    "role": "system", 
                    "content": "Отвечай только на русском языке. Будь полезным ассистентом. Не используй LaTeX, формулы или специальное форматирование. Пиши ответы простым текстом. Запрещено использовать конструкции вроде \\boxed{}."  # Правка здесь
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000
        )
        
        if completion.choices and completion.choices[0].message.content:
            response_text = completion.choices[0].message.content
            response_text = response_text.replace("\\boxed{", "").strip()  # Добавить эту строку
            response_text = response_text.replace("}", " ^-^").strip()
            return response_text
        return "Не удалось получить ответ от ИИ."
    
    except Exception as e:
        logger.error(f"Ошибка в get_ai_response: {e}")
        return None

# --- Основной обработчик сообщений ---
@router.message()
async def handle_message(message: Message):
    try:
        
        # Получаем ответ от ИИ
        response = await get_ai_response(message.text)
        
        if response:
            # Разбиваем длинные сообщения на части (Telegram имеет лимит на длину сообщения)
            if len(response) > 4000:
                for x in range(0, len(response), 4000):
                    await message.answer(response[x:x+4000])
                    await asyncio.sleep(1)  # Небольшая задержка между сообщениями
            else:
                await message.answer(response)
        else:
            await message.answer("⚠️ Не удалось получить ответ от ИИ. Пожалуйста, попробуйте позже.")
            
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")
        await message.answer("⚠️ Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз.")

# --- Запуск бота ---
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())