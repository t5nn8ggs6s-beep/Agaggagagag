FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir python-telegram-bot

CMD ["python", "bot.py"]
