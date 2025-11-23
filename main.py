import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# === CONFIG ===
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

# === HANDLERS ===
async def start(update, context):
    await update.message.reply_text(
        "👋 Привет! Я — AI Career Navigator для фрилансеров.\n"
        "Опиши свою ситуацию — и получи стратегию!"
    )

async def handle(update, context):
    user_msg = update.message.text
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Ты — эксперт по фрилансу. Отвечай кратко, по делу, на русском."},
                    {"role": "user", "content": user_msg}
                ]
            },
            timeout=15
        )
        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            await update.message.reply_text(reply[:4000])
        else:
            await update.message.reply_text("ИИ не отвечает. Попробуй позже.")
    except Exception as e:
        await update.message.reply_text("Ошибка обработки.")

# === MAIN ===
if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path=TELEGRAM_TOKEN,
        webhook_url=WEBHOOK_URL
    )
