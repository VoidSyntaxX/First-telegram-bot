import logging
import os
import requests
from dotenv import load_dotenv
from typing import Final
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

# ========== Logging ==========
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== Config ==========
TELEGRAM_TOKEN = os.getenv(
    "TELEGRAM_TOKEN", "7996575119:AAFZIRfcU47l_tFrwjI33r9oJ2ZXYOY5wrw"
)
BOT_USERNAME: Final = "@this_my_first_ever_bot"
WEATHER_API_KEY: Final = os.getenv("WEATHER_API_KEY", "bb1375f7a48ff327d9989816cba9eca6")
# app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# ========== Commands ==========


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I can give you weather info.\nUse /weather <city name> like: /weather Paris"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /weather <city>. Example: /weather Tokyo")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command!")


# ========== Weather Handler ==========
def get_weather(city: str) -> str:
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return "❌ City not found or error fetching weather."

    data = response.json()
    name = data["name"]
    temp = data["main"]["temp"]
    condition = data["weather"][0]["description"].capitalize()

    return f"🌤 Weather in {name}:\nTemperature: {temp}°C\nCondition: {condition}"


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a city. Example: /weather Berlin"
        )
        return

    city = " ".join(context.args)
    logger.info(f"Fetching weather for: {city}")
    result = get_weather(city)
    await update.message.reply_text(result)


# ========== Fallback Message ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("❓ I don't understand. Try /weather <city>.")


# ========== Error Handler ==========
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}")


# ========== Main ==========
if __name__ == "__main__":
    print("Starting bot...")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))
    app.add_handler(CommandHandler("weather", weather_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    print("Polling...")
    app.run_polling()
