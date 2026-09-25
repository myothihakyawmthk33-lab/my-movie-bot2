import os
import logging
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MY_TELEGRAM_ID = int(os.environ.get("MY_TELEGRAM_ID", "8777467753"))

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO)

def is_owner(update: Update) -> bool:
    return update.effective_user.id == MY_TELEGRAM_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("⛔️ တောင်းပန်ပါတယ်။ ဒီ Bot ကို ပိုင်ရှင်တစ်ယောက်တည်းသာ သုံးစွဲခွင့်ရှိပါတယ်။")
        return

    msg = (
        "🎬 **Private Movie Recap Bot မှ ကြိုဆိုပါတယ်!**\n\n"
        "ကြည့်ချင်တဲ့ ရုပ်ရှင်နာမည်ကို `/recap [ရုပ်ရှင်နာမည်]` လို့ ရိုက်ပေးပါ။\n"
        "ဥပမာ - `/recap Inception` သို့မဟုတ် `/recap Avatar`"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("⛔️ တောင်းပန်ပါတယ်။ ဒီ Bot ကို ပိုင်ရှင်တစ်ယောက်တည်းသာ သုံးစွဲခွင့်ရှိပါတယ်။")
        return

    if not context.args:
        await update.message.reply_text("ကျေးဇူးပြု၍ ရုပ်ရှင်အမည် ထည့်ပေးပါ။ ဥပမာ - `/recap Inception`", parse_mode='Markdown')
        return

    movie_name = " ".join(context.args)
    status_message = await update.message.reply_text(f"⏳ '{movie_name}' အတွက် Recap ရေးပေးနေပါတယ်...")

    try:
        prompt = (
            f"Please provide a clear movie recap for '{movie_name}' in Myanmar language. "
            f"Include storyline, main themes, genre, release year, and overall review without massive ending spoilers. "
            f"Use Markdown formatting with clean emojis."
        )

        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )

        await status_message.delete()
        await update.message.reply_text(response.text, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_message.edit_text("တောင်းပန်ပါတယ်၊ AI မှ Recap ထုတ်ပေးရာတွင် အမှားအယွင်းတစ်ခု ဖြစ်သွားပါတယ်။")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("recap", recap))
    print("Private Bot is running...")
    app.run_polling()
