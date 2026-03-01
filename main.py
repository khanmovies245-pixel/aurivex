import os
import yt_dlp
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

app = Flask(__name__)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Aurivex Music Bot Ready!")

# Download Command
async def download_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text("Downloading...")

    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': 'song.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            filename = ydl.prepare_filename(info['entries'][0])

        await update.message.reply_audio(audio=open(filename, 'rb'))
        os.remove(filename)

    except Exception as e:
        await update.message.reply_text("Error downloading song.")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_song))

@app.route("/")
def home():
    return "Aurivex Bot Running"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

if __name__ == "__main__":
    telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=PORT)
