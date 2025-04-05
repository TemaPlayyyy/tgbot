# Используем легковесный образ Python
FROM python:3.11-slim

# Создаем непривилегированного пользователя (без root)
RUN useradd -m -u 1001 botuser && \
    mkdir -p /app && \
    chown botuser:botuser /app

WORKDIR /app

# Копируем зависимости отдельно (для кэширования)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код (от имени botuser)
COPY --chown=botuser:botuser src/ .

# Переключаемся на непривилегированного пользователя
USER botuser

# Указываем команду запуска (переменные передаются при запуске контейнера)
CMD ["python", "-u", "bot.py"]