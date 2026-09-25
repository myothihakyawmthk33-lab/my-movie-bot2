import os
import logging
import asyncio
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Dummy Web Server to satisfy Render Web Service Port check
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Enable Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MY_TELEGRAM_ID = os.getenv("MY_TELEGRAM_ID")

genai.configure(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if user_id != MY_TELEGRAM_ID:
        await update.message.reply_text("ခွင့်ပြုချက်မရှိပါ။")
        return
    await update.message.reply_text(
        "🎬 Private Movie Recap Bot မှ ကြိုဆိုပါတယ်!\n\n"
        "ကြည့်ချင်တဲ့ ရုပ်ရှင်နာမည်ကို /recap [ရုပ်ရှင်နာမည်] လို့ ရိုက်ပေးပါ။\n"
        "ဥပမာ - /recap Inception"
    )

async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if user_id != MY_TELEGRAM_ID:
        await update.message.reply_text("ခွင့်ပြုချက်မရှိပါ။")
        return

    movie_name = " ".join(context.args)
    if not movie_name:
        await update.message.reply_text("ကျေးဇူးပြု၍ ရုပ်ရှင်နာမည် ထည့်ပေးပါ။ ဥပမာ - /recap Titanic")
        return

    await update.message.reply_text(f"🎬 '{movie_name}' အတွက် Recap ဖန်တီးပေးနေပါတယ်... ခဏစောင့်ပေးပါ။")

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = (
            f"You are a movie recap expert. Write a detailed, highly engaging movie recap script in Myanmar (Burmese) language for the movie: '{movie_name}'. "
            f"Structure it cleanly for a TikTok/YouTube video script."
        )

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: model.generate_content(prompt))
        recap_text = response.text

        if len(recap_text) > 4000:
            for i in range(0, len(recap_text), 4000):
                await update.message.reply_text(recap_text[i:i+4000])
        else:
            await update.message.reply_text(recap_text)

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(f"တောင်းပန်ပါတယ်၊ AI မှ Recap ထုတ်ပေးရာတွင် အမှားအယွင်း ဖြစ်သွားပါသည်:\n{e}")

def main() -> None:
    # Start Web Server in background thread for Render Free Plan
    t = Thread(target=run_health_check_server, daemon=True)
    t.start()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("recap", recap))
    application.run_polling()

if __name__ == "__main__":
    main()
