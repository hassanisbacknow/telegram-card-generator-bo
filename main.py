import random
import httpx
import re
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import Forbidden

# --- Configuration ---
BOT_TOKEN = "7654475659:AAHzvNFIP7aX3-r8iTYlGyxjMx5VTSZY12w"
WEBHOOK_URL = "https://telegram-card-generator-bo.onrender.com"

# Flask app
app = Flask(__name__)

# --- Helper Functions ---

def escape_markdown_v2(text):
    escape_chars = r"\*_`()~>#+-=|{}.!"
    return re.sub(r"([" + re.escape(escape_chars) + r"])", r"\\\1", text)

def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n) if d.isdigit()]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10

def generate_credit_card(bin_number):
    card_length = 15 if bin_number.startswith(('34', '37')) else 16
    bin_number = ''.join(str(random.randint(0, 9)) if x == 'x' else x for x in bin_number)
    card_number = [int(x) for x in bin_number]

    while len(card_number) < (card_length - 1):
        card_number.append(random.randint(0, 9))

    checksum_digit = luhn_checksum(card_number + [0])
    if checksum_digit != 0:
        checksum_digit = 10 - checksum_digit
    card_number.append(checksum_digit)

    return ''.join(map(str, card_number))

def generate_expiry_date(mm_input, yy_input):
    mm = ''.join(str(random.randint(0, 9)) if x == 'x' else x for x in mm_input)
    mm = f"{random.randint(1, 12):02d}" if not mm else mm
    mm = f"{random.randint(1, 12):02d}" if int(mm) < 1 or int(mm) > 12 else mm

    yy = ''.join(str(random.randint(0, 9)) if x == 'x' else x for x in yy_input)
    if not yy:
        yy = str(random.randint(26, 29))
    elif len(yy) == 2:
        yy = "20" + yy
    yy = str(random.randint(2026, 2029)) if int(yy) < 2026 or int(yy) > 2029 else yy

    return mm, yy

def generate_cvv(cvv_input, bin_number):
    if cvv_input.lower() != "rnd" and 'x' not in cvv_input:
        return cvv_input
    cvv_length = 4 if bin_number.startswith(('34', '37')) else 3
    return ''.join(str(random.randint(0, 9)) for _ in range(cvv_length))

# --- Telegram Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Welcome to the Card Generator Bot!")
    except Forbidden:
        print(f"User {update.effective_user.id} blocked the bot.")

async def process_gen_command(update: Update, user_input: str):
    try:
        user_input = user_input.replace('/', '|')
        input_parts = user_input.split(' ')
        card_info = input_parts[0].strip()
        quantity_str = input_parts[1].strip() if len(input_parts) > 1 else "10"

        parts = card_info.split('|')
        bin_number = parts[0].strip() if len(parts) > 0 else ""
        mm_input = "xx" if len(parts) <= 1 or parts[1].strip().lower() == "rnd" else parts[1].strip()
        yy_input = "xx" if len(parts) <= 2 or parts[2].strip().lower() == "rnd" else parts[2].strip()
        cvv_input = "xxx" if len(parts) <= 3 or parts[3].strip().lower() == "rnd" else parts[3].strip()

        if not (len(bin_number) >= 6 and bin_number[:6].isdigit()):
            await update.message.reply_text("Invalid BIN format.")
            return

        try:
            quantity = int(quantity_str)
            if quantity <= 0 or quantity > 100:
                raise ValueError()
        except ValueError:
            await update.message.reply_text("Max quantity is 100.")
            return

        ccs = []
        for _ in range(quantity):
            card_number = generate_credit_card(bin_number)
            mm, yy = generate_expiry_date(mm_input, yy_input)
            cvv = generate_cvv(cvv_input, bin_number)
            ccs.append(f"{card_number}|{mm}|{yy}|{cvv}")

        ccs_text = '\n'.join([f"`{cc}`" for cc in ccs])
        response = (
            f"*𝐁𝐈𝐍* ⇾ {bin_number[:6]}\n"
            f"*𝐀𝐌𝐎𝐔𝐍𝐓* ⇾ {quantity}\n━━━━━━━━━━━━━━\n"
            f"{ccs_text}\n━━━━━━━━━━━━━━\n"
            "\n*𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐑*: @hassanontelegram\n"
            "*𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐑 𝐂𝐇𝐀𝐍𝐍𝐄𝐋*: @tricks\\_era"
        )
        await update.message.reply_text(response, parse_mode="MarkdownV2")
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Invalid BIN.")

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = ' '.join(context.args)
    await process_gen_command(update, user_input)

async def gen_with_dot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text[4:].strip()
    await process_gen_command(update, user_input)

# --- App and Webhook Integration ---

telegram_app: Application = Application.builder().token(BOT_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("gen", gen))
telegram_app.add_handler(MessageHandler(filters.Regex(r"^\.gen\s"), gen_with_dot))

@app.route('/')
def index():
    return "Bot is running with webhook!"

@app.route('/webhook', methods=["POST"])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        await telegram_app.process_update(update)
        return "ok", 200

# --- Startup (Webhook Set) ---

async def set_webhook():
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook set!")

def main():
    import asyncio
    asyncio.run(set_webhook())

if __name__ == "__main__":
    main()
