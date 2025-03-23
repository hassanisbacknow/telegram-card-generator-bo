import random2 as random
import httpx
import re
import aiohttp
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.error import Forbidden
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import re

def clean_data(data):
    # Remove unwanted characters (only allow alphanumeric and space)
    cleaned_data = re.sub(r'[^a-zA-Z0-9\s]', '', data)
    return cleaned_data

# Web server to keep alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is online!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Background pinger to keep app awake
def ping_self():
    import time
    def loop():
        while True:
            try:
                httpx.get("https://telegram-card-generator-bo.onrender.com", timeout=5)
            except:
                pass  # silently ignore errors
            time.sleep(5)
    Thread(target=loop, daemon=True).start()

# Country Flags Dictionary (extended, add more if needed)
COUNTRY_FLAGS = {
    "ARUBA": "🇦🇼",
    "AFGHANISTAN": "🇦🇫",
    "ANGOLA": "🇦🇴",
    "ANGUILLA": "🇦🇮",
    "ÅLAND ISLANDS": "🇦🇽",
    "ALBANIA": "🇦🇱",
    "ANDORRA": "🇦🇩",
    "UNITED ARAB EMIRATES": "🇦🇪",
    "ARGENTINA": "🇦🇷",
    "ARMENIA": "🇦🇲",
    "AMERICAN SAMOA": "🇦🇸",
    "ANTARCTICA": "🇦🇶",
    "FRENCH SOUTHERN TERRITORIES": "🇹🇫",
    "ANTIGUA AND BARBUDA": "🇦🇬",
    "AUSTRALIA": "🇦🇺",
    "AUSTRIA": "🇦🇹",
    "AZERBAIJAN": "🇦🇿",
    "BURUNDI": "🇧🇮",
    "BELGIUM": "🇧🇪",
    "BENIN": "🇧🇯",
    "BONAIRE, SINT EUSTATIUS AND SABA": "🇧🇶",
    "BURKINA FASO": "🇧🇫",
    "BANGLADESH": "🇧🇩",
    "BULGARIA": "🇧🇬",
    "BAHRAIN": "🇧🇭",
    "BAHAMAS": "🇧🇸",
    "BOSNIA AND HERZEGOVINA": "🇧🇦",
    "SAINT BARTHÉLEMY": "🇧🇱",
    "BELARUS": "🇧🇾",
    "BELIZE": "🇧🇿",
    "BERMUDA": "🇧🇲",
    "BOLIVIA, PLURINATIONAL STATE OF": "🇧🇴",
    "BRAZIL": "🇧🇷",
    "BARBADOS": "🇧🇧",
    "BRUNEI DARUSSALAM": "🇧🇳",
    "BHUTAN": "🇧🇹",
    "BOUVET ISLAND": "🇧🇻",
    "BOTSWANA": "🇧🇼",
    "CENTRAL AFRICAN REPUBLIC": "🇨🇫",
    "CANADA": "🇨🇦",
    "COCOS (KEELING) ISLANDS": "🇨🇨",
    "SWITZERLAND": "🇨🇭",
    "CHILE": "🇨🇱",
    "CHINA": "🇨🇳",
    "CÔTE D'IVOIRE": "🇨🇮",
    "CAMEROON": "🇨🇲",
    "CONGO, THE DEMOCRATIC REPUBLIC OF THE": "🇨🇩",
    "CONGO": "🇨🇬",
    "COOK ISLANDS": "🇨🇰",
    "COLOMBIA": "🇨🇴",
    "COMOROS": "🇰🇲",
    "CABO VERDE": "🇨🇻",
    "COSTA RICA": "🇨🇷",
    "CUBA": "🇨🇺",
    "CURAÇAO": "🇨🇼",
    "CHRISTMAS ISLAND": "🇨🇽",
    "CAYMAN ISLANDS": "🇰🇾",
    "CYPRUS": "🇨🇾",
    "CZECHIA": "🇨🇿",
    "GERMANY": "🇩🇪",
    "DJIBOUTI": "🇩🇯",
    "DOMINICA": "🇩🇲",
    "DENMARK": "🇩🇰",
    "DOMINICAN REPUBLIC": "🇩🇴",
    "ALGERIA": "🇩🇿",
    "ECUADOR": "🇪🇨",
    "EGYPT": "🇪🇬",
    "ERITREA": "🇪🇷",
    "WESTERN SAHARA": "🇪🇭",
    "SPAIN": "🇪🇸",
    "ESTONIA": "🇪🇪",
    "ETHIOPIA": "🇪🇹",
    "FINLAND": "🇫🇮",
    "FIJI": "🇫🇯",
    "FALKLAND ISLANDS (MALVINAS)": "🇫🇰",
    "FRANCE": "🇫🇷",
    "FAROE ISLANDS": "🇫🇴",
    "MICRONESIA, FEDERATED STATES OF": "🇫🇲",
    "GABON": "🇬🇦",
    "UNITED KINGDOM": "🇬🇧",
    "GEORGIA": "🇬🇪",
    "GUERNSEY": "🇬🇬",
    "GHANA": "🇬🇭",
    "GIBRALTAR": "🇬🇮",
    "GUINEA": "🇬🇳",
    "GUADELOUPE": "🇬🇵",
    "GAMBIA": "🇬🇲",
    "GUINEA-BISSAU": "🇬🇼",
    "EQUATORIAL GUINEA": "🇬🇶",
    "GREECE": "🇬🇷",
    "GRENADA": "🇬🇩",
    "GREENLAND": "🇬🇱",
    "GUATEMALA": "🇬🇹",
    "FRENCH GUIANA": "🇬🇫",
    "GUAM": "🇬🇺",
    "GUYANA": "🇬🇾",
    "HONG KONG": "🇭🇰",
    "HEARD ISLAND AND MCDONALD ISLANDS": "🇭🇲",
    "HONDURAS": "🇭🇳",
    "CROATIA": "🇭🇷",
    "HAITI": "🇭🇹",
    "HUNGARY": "🇭🇺",
    "INDONESIA": "🇮🇩",
    "ISLE OF MAN": "🇮🇲",
    "INDIA": "🇮🇳",
    "BRITISH INDIAN OCEAN TERRITORY": "🇮🇴",
    "IRELAND": "🇮🇪",
    "IRAN, ISLAMIC REPUBLIC OF": "🇮🇷",
    "IRAQ": "🇮🇶",
    "ICELAND": "🇮🇸",
    "ISRAEL": "🇮🇱",
    "ITALY": "🇮🇹",
    "JAMAICA": "🇯🇲",
    "JERSEY": "🇯🇪",
    "JORDAN": "🇯🇴",
    "JAPAN": "🇯🇵",
    "KAZAKHSTAN": "🇰🇿",
    "KENYA": "🇰🇪",
    "KYRGYZSTAN": "🇰🇬",
    "CAMBODIA": "🇰🇭",
    "KIRIBATI": "🇰🇮",
    "SAINT KITTS AND NEVIS": "🇰🇳",
    "KOREA, REPUBLIC OF": "🇰🇷",
    "KUWAIT": "🇰🇼",
    "LAO PEOPLE'S DEMOCRATIC REPUBLIC": "🇱🇦",
    "LEBANON": "🇱🇧",
    "LIBERIA": "🇱🇷",
    "LIBYA": "🇱🇾",
    "SAINT LUCIA": "🇱🇨",
    "LIECHTENSTEIN": "🇱🇮",
    "SRI LANKA": "🇱🇰",
    "LESOTHO": "🇱🇸",
    "LITHUANIA": "🇱🇹",
    "LUXEMBOURG": "🇱🇺",
    "LATVIA": "🇱🇻",
    "MACAO": "🇲🇴",
    "SAINT MARTIN (FRENCH PART)": "🇲🇫",
    "MOROCCO": "🇲🇦",
    "MONACO": "🇲🇨",
    "MOLDOVA, REPUBLIC OF": "🇲🇩",
    "MADAGASCAR": "🇲🇬",
    "MALDIVES": "🇲🇻",
    "MEXICO": "🇲🇽",
    "MARSHALL ISLANDS": "🇲🇭",
    "NORTH MACEDONIA": "🇲🇰",
    "MALI": "🇲🇱",
    "MALTA": "🇲🇹",
    "MYANMAR": "🇲🇲",
    "MONTENEGRO": "🇲🇪",
    "MONGOLIA": "🇲🇳",
    "NORTHERN MARIANA ISLANDS": "🇲🇵",
    "MOZAMBIQUE": "🇲🇿",
    "MAURITANIA": "🇲🇷",
    "MONTSERRAT": "🇲🇸",
    "MARTINIQUE": "🇲🇶",
    "MAURITIUS": "🇲🇺",
    "MALAWI": "🇲🇼",
    "MALAYSIA": "🇲🇾",
    "MAYOTTE": "🇾🇹",
    "NAMIBIA": "🇳🇦",
    "NEW CALEDONIA": "🇳🇨",
    "NIGER": "🇳🇪",
    "NORFOLK ISLAND": "🇳🇫",
    "NIGERIA": "🇳🇬",
    "NICARAGUA": "🇳🇮",
    "NIUE": "🇳🇺",
    "NETHERLANDS": "🇳🇱",
    "NORWAY": "🇳🇴",
    "NEPAL": "🇳🇵",
    "NAURU": "🇳🇷",
    "NEW ZEALAND": "🇳🇿",
    "OMAN": "🇴🇲",
    "PAKISTAN": "🇵🇰",
    "PANAMA": "🇵🇦",
    "PITCAIRN": "🇵🇳",
    "PERU": "🇵🇪",
    "PHILIPPINES": "🇵🇭",
    "PALAU": "🇵🇼",
    "PAPUA NEW GUINEA": "🇵🇬",
    "POLAND": "🇵🇱",
    "PUERTO RICO": "🇵🇷",
    "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF": "🇰🇵",
    "PORTUGAL": "🇵🇹",
    "PARAGUAY": "🇵🇾",
    "PALESTINE, STATE OF": "🇵🇸",
    "FRENCH POLYNESIA": "🇵🇫",
    "QATAR": "🇶🇦",
    "RÉUNION": "🇷🇪",
    "ROMANIA": "🇷🇴",
    "RUSSIAN FEDERATION": "🇷🇺",
    "RWANDA": "🇷🇼",
    "SAUDI ARABIA": "🇸🇦",
    "SUDAN": "🇸🇩",
    "SENEGAL": "🇸🇳",
    "SINGAPORE": "🇸🇬",
    "SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS": "🇬🇸",
    "SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA": "🇸🇭",
    "SVALBARD AND JAN MAYEN": "🇸🇯",
    "SOLOMON ISLANDS": "🇸🇧",
    "SIERRA LEONE": "🇸🇱",
    "EL SALVADOR": "🇸🇻",
    "SAN MARINO": "🇸🇲",
    "SOMALIA": "🇸🇴",
    "SAINT PIERRE AND MIQUELON": "🇵🇲",
    "SERBIA": "🇷🇸",
    "SOUTH SUDAN": "🇸🇸",
    "SAO TOME AND PRINCIPE": "🇸🇹",
    "SURINAME": "🇸🇷",
    "SLOVAKIA": "🇸🇰",
    "SLOVENIA": "🇸🇮",
    "SWEDEN": "🇸🇪",
    "ESWATINI": "🇸🇿",
    "SINT MAARTEN (DUTCH PART)": "🇸🇽",
    "SEYCHELLES": "🇸🇨",
    "SYRIAN ARAB REPUBLIC": "🇸🇾",
    "TURKS AND CAICOS ISLANDS": "🇹🇨",
    "CHAD": "🇹🇩",
    "TOGO": "🇹🇬",
    "THAILAND": "🇹🇭",
    "TAJIKISTAN": "🇹🇯",
    "TOKELAU": "🇹🇰",
    "TURKMENISTAN": "🇹🇲",
    "TIMOR-LESTE": "🇹🇱",
    "TONGA": "🇹🇴",
    "TRINIDAD AND TOBAGO": "🇹🇹",
    "TUNISIA": "🇹🇳",
    "TURKEY": "🇹🇷",
    "TUVALU": "🇹🇻",
    "TAIWAN, PROVINCE OF CHINA": "🇹🇼",
    "TANZANIA, UNITED REPUBLIC OF": "🇹🇿",
    "UGANDA": "🇺🇬",
    "UKRAINE": "🇺🇦",
    "UNITED STATES MINOR OUTLYING ISLANDS": "🇺🇲",
    "URUGUAY": "🇺🇾",
    "UNITED STATES": "🇺🇸",
    "UZBEKISTAN": "🇺🇿",
    "HOLY SEE (VATICAN CITY STATE)": "🇻🇦",
    "SAINT VINCENT AND THE GRENADINES": "🇻🇨",
    "VENEZUELA, BOLIVARIAN REPUBLIC OF": "🇻🇪",
    "VIRGIN ISLANDS, BRITISH": "🇻🇬",
    "VIRGIN ISLANDS, U.S.": "🇻🇮",
    "VIET NAM": "🇻🇳",
    "VANUATU": "🇻🇺",
    "WALLIS AND FUTUNA": "🇼🇫",
    "SAMOA": "🇼🇸",
    "YEMEN": "🇾🇪",
    "SOUTH AFRICA": "🇿🇦",
    "ZAMBIA": "🇿🇲",
    "ZIMBABWE": "🇿🇼",
}

# --- Helper functions ---

def escape_markdown_v2(text):
    escape_chars = r"\_*`[]()~>#+-=|{}.!"
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
    # Generate the month
    mm = ''.join(str(random.randint(0, 9)) if x == 'x' else x for x in mm_input)
    if not mm:
        mm = f"{random.randint(1, 12):02d}"  # Ensure two-digit format
    mm = f"{random.randint(1, 12):02d}" if int(mm) < 1 or int(mm) > 12 else mm
    mm = f"{int(mm):02d}"

    # Generate the year
    yy = ''.join(str(random.randint(0, 9)) if x == 'x' else x for x in yy_input)
    if not yy:
        yy = str(random.randint(26, 32))
    elif len(yy) == 2:
        yy = "20" + yy
    yy = str(random.randint(2026, 2032)) if int(yy) < 2026 or int(yy) > 2032 else yy

    return mm,yy

def generate_cvv(cvv_input, bin_number):
    if cvv_input.lower() != "rnd" and 'x' not in cvv_input:
        return cvv_input
    cvv_length = 4 if bin_number.startswith(('34', '37')) else 3
    return ''.join(str(random.randint(0, 9)) for _ in range(cvv_length))

# --- BIN Lookup function ---

async def lookup_bin(bin_number):
    url = f"https://drlabapis.onrender.com/api/bin?bin={bin_number[:6]}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                print(f"[DEBUG] BIN API Status: {response.status}")
                raw_data = await response.text()
                print(f"[DEBUG] BIN API Response: {raw_data}")
                if response.status == 200:
                    bin_data = await response.json()
                    country_name = bin_data.get('country', 'NOT FOUND').upper()
                    return {
                        "bank": bin_data.get('issuer', 'NOT FOUND'),
                        "card_type": bin_data.get('type', 'NOT FOUND'),
                        "network": bin_data.get('scheme', 'NOT FOUND'),
                        "tier": bin_data.get('tier', 'NOT FOUND'),
                        "country": country_name,
                        "flag": COUNTRY_FLAGS.get(country_name, "🏳️")
                    }
                else:
                    return {"error": f"API error: {response.status}"}
    except Exception as e:
        print(f"[DEBUG] BIN Lookup Error: {e}")
        return {"error": str(e)}
        
        # --- Telegram Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Welcome to the Card Generator Bot!\n\nUse /gen or .gen followed by BIN to generate cards.")
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

        # Lookup BIN info
        bin_info = await lookup_bin(bin_number)
        if "error" in bin_info:
            bin_info = {
                "card_type": "NOT FOUND",
                "network": "NOT FOUND",
                "tier": "NOT FOUND",
                "bank": "NOT FOUND",
                "country": "NOT FOUND",
                "flag": "🏳️"
            }

        # Escape for MarkdownV2
        issuer = escape_markdown_v2(bin_info.get('bank'))
        card_type = escape_markdown_v2(bin_info.get('card_type'))
        network = escape_markdown_v2(bin_info.get('network'))
        tier = escape_markdown_v2(bin_info.get('tier'))
        country = escape_markdown_v2(bin_info.get('country'))
        flag = bin_info.get('flag', '🏳️')

        # Generate cards
        ccs = []
        for _ in range(quantity):
            card_number = generate_credit_card(bin_number)
            mm, yy = generate_expiry_date(mm_input, yy_input)
            cvv = generate_cvv(cvv_input, bin_number)
            ccs.append(f"{card_number}|{mm}|{yy}|{cvv}")

        ccs_text = '\n'.join([f"`{cc}`" for cc in ccs])

        # Build response
        response = (
    f"*𝐁𝐈𝐍* ⇾ {escape_markdown_v2(bin_number[:6])}\n"
    f"*𝐀𝐌𝐎𝐔𝐍𝐓* ⇾ {quantity}\n"
    f"━━━━━━━━━━━━━━\n"
    f"{ccs_text}\n"
    f"━━━━━━━━━━━━━━\n"
    f"*𝗜𝗻𝗳𝗼:* {card_type} \\- {network} \\- {tier}\n"
    f"*𝐈𝐬𝐬𝐮𝐞𝐫:* {issuer}\n"
    f"*𝗖𝗼𝘂𝗻𝘁𝗿𝘆:* {country} {flag}\n"
    f"━━━━━━━━━━━━━━\n"
    f"*𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐑*: @hassanontelegram\n"
    f"*𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐑 𝐂𝐇𝐀𝐍𝐍𝐄𝐋*: @tricks\\_era"
)

        await update.message.reply_text(response, parse_mode="MarkdownV2")

    except Exception as e:
        print(f"Error: {e}")
        try:
            await update.message.reply_text("An error occurred while generating.")
        except Forbidden:
            print(f"User {update.effective_user.id} blocked the bot.")

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = ' '.join(context.args)
    await process_gen_command(update, user_input)

async def gen_with_dot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text[4:].strip()
    await process_gen_command(update, user_input)
    
    # --- Main ---
def main():
    keep_alive()
    ping_self()  # background pinger
    print("Bot is running...")

    application = ApplicationBuilder().token("7654475659:AAG7tqw_Fa2K1tek-KopyVrKKzvSfUhRUkE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("gen", gen))
    application.add_handler(MessageHandler(filters.Regex(r"^\.gen\s"), gen_with_dot))

    application.run_polling()

if __name__ == "__main__":
    main()
