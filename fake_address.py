import requests
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
from threading import Thread
import httpx

# Replace with your actual OpenAI and Telegram keys
OPENAI_API_KEY = "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"  
TELEGRAM_BOT_TOKEN = "7801028142:AAG1kMI6bT5pa2553JlEXkj92d2y-unxUZk"

# Web server to keep alive
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is online!"

def run_web():
    flask_app.run(host='0.0.0.0', port=8080)
    
def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Background pinger to keep app awake
def ping_self():
    import time
    def loop():
        while True:
            try:
                httpx.get("https://telegram-card-generator-bo-1.onrender.com", timeout=5)
            except:
                pass  # silently ignore errors
            time.sleep(5)
    Thread(target=loop, daemon=True).start()

# SSN generator for USA
def generate_luhn_valid_ssn():
    def luhn_checksum(number):
        def digits_of(n): return [int(d) for d in str(n)]
        digits = digits_of(number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10

    while True:
        ssn = random.randint(100000000, 999999999)
        if luhn_checksum(ssn) == 0:
            return f"{str(ssn)[:3]}-{str(ssn)[3:5]}-{str(ssn)[5:]}"


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /fake <country/city> to get a fake address.\nExample: /fake USA")


# /fake command
async def fake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a country or city. Example:\n/fake Germany")
        return

    country = ' '.join(context.args)

    # Send "Generating..." message first
    message = await update.message.reply_text("Generating...")

    prompt = f"""Generate a real address in {country} that is valid on Google Maps and formatted as follows. Use a known location (street, town, neighborhood), and include a fake phone number with a valid prefix from a real network operator. Don't use commas in address. You should generate a different address each time. Digit before street name should also be different, not in sequence.

Format:

Name:
Gender:
Street address: (Include street number, block, house number, and town/neighborhood. The street should be real and available on google maps. Use valid street numbers.)
City:
Postal Code:
Province:
Country:
Phone Number:(In country code format)"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]

        # Add SSN if country is USA or similar terms
        if any(keyword in country.lower() for keyword in ["usa", "us", "united states", "united states of america"]):
            ssn = generate_luhn_valid_ssn()
            content += f"\nSocial Security Number (OF USA): {ssn}"

        # Edit the original "Generating..." message with the real content
        await message.edit_text(content)

    except Exception as e:
        await message.edit_text("Error fetching address. Try again later.")
        print(f"Error: {e}")

# Main bot launcher
def main():
    keep_alive()
    ping_self()  # background pinger
    print("Bot is starting...")

    # Build the Telegram bot application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fake", fake))

    print("Telegram bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
