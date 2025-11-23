import sys
print("✅ Запуск бота...")
print("🔧 Python версия:", sys.version)
import os
import requests
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Получаем настройки из переменных окружения
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

# Инициализация Telegram-бота
bot = Bot(token=TELEGRAM_TOKEN)
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я — AI Career Navigator для фрилансеров.\n\n"
        "Расскажи:\n"
        "• Кто ты (дизайнер, программист, копирайтер)?\n"
        "• Сколько опыта?\n"
        "• Какая цель (клиенты, ставка, ниша)?\n\n"
        "И я дам персональную стратегию! 🚀"
    )

# Обработка обычных сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ты — эксперт по карьере фрилансеров. Отвечай только на русском. "
                            "Давай конкретные шаги: как упаковать профиль, где искать клиентов, "
                            "какую ставку ставить, на чём специализироваться. "
                            "Не пиши 'как ИИ', не извиняйся, не используй формальности. "
                            "Ответ должен быть структурирован: 1–3 пункта, максимум 300 слов."
                        )
                    },
                    {"role": "user", "content": user_text}
                ]
            },
            timeout=20
        )
        if resp.status_code == 200:
            reply = resp.json()["choices"][0]["message"]["content"]
            if len(reply) > 4000:
                reply = reply[:4000] + "…"
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text("ИИ временно недоступен. Попробуй через минуту.")
    except Exception as e:
        await update.message.reply_text("Ошибка. Попробуй позже.")
        print("Ошибка:", e)

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask-сервер для webhook
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, bot)
    application.update_queue.put_nowait(update)
    return jsonify({"status": "ok"})

@app.route('/')
def home():
    return "✅ AI Career Navigator is live!"

# Запуск
if __name__ == '__main__':
    import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(bot.set_webhook(url=WEBHOOK_URL))
    print(f"Webhook установлен: {WEBHOOK_URL}")
    # Запускаем Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
