# main.py — минималистичный и рабочий для Render
import os
from flask import Flask
from telegram import Bot
from telegram.ext import Application

# Переменные окружения
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

app = Flask(__name__)

@app.route('/')
def home():
return "✅ AI Career Navigator is live!"

if __name__ == '__main__':
# Создаем бота
bot = Bot(token=TELEGRAM_TOKEN)
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Устанавливаем webhook
import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(bot.set_webhook(url=WEBHOOK_URL))

print("🚀 Webhook установлен:", WEBHOOK_URL)
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
