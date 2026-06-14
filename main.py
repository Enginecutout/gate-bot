import os
import time
import hmac
import hashlib
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ENV değişkenleri (Render'dan gelecek)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GATE_API_KEY = os.getenv("GATE_API_KEY")
GATE_SECRET = os.getenv("GATE_SECRET")

BASE_URL = "https://api.gateio.ws"

# -----------------------
# GATE SIGN FUNCTION
# -----------------------
def sign(method, url, query_string="", body=""):
    t = str(int(time.time()))
    hashed_payload = hashlib.sha512(body.encode()).hexdigest()

    message = f"{method}\n{url}\n{query_string}\n{hashed_payload}\n{t}"
    signature = hmac.new(
        GATE_SECRET.encode(),
        message.encode(),
        hashlib.sha512
    ).hexdigest()

    return t, signature


# -----------------------
# PLACE ORDER
# -----------------------
def place_order(contract, size, side):
    path = "/api/v4/futures/usdt/orders"
    url = BASE_URL + path

    body = {
        "contract": f"{contract}_USDT",
        "size": size,
        "price": "0",
        "tif": "ioc",
        "side": side
    }

    import json
    body_str = json.dumps(body)

    t, signature = sign("POST", path, "", body_str)

    headers = {
        "KEY": GATE_API_KEY,
        "Timestamp": t,
        "SIGN": signature,
        "Content-Type": "application/json"
    }

    return requests.post(url, headers=headers, data=body_str).json()


# -----------------------
# DEFAULT SETTINGS
# -----------------------
PAIR = "BTC"
SIZE = 100

# -----------------------
# TELEGRAM COMMANDS
# -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif. LONG / SHORT / CLOSE hazır.")

async def long(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = place_order(PAIR, SIZE, "open_long")
    await update.message.reply_text(str(res))

async def short(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = place_order(PAIR, SIZE, "open_short")
    await update.message.reply_text(str(res))

async def close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = place_order(PAIR, SIZE, "close_long")
    await update.message.reply_text(str(res))


# -----------------------
# MAIN
# -----------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("long", long))
app.add_handler(CommandHandler("short", short))
app.add_handler(CommandHandler("close", close))

app.run_polling()
