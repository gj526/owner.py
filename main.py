import instaloader
import yt_dlp
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext

TOKEN = "PUT-YOUR-TOKEN-HERE"

app = Flask(__name__)
loader = instaloader.Instaloader()

def get_instagram_info(username):
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        info = (
            f"📌 معلومات الحساب: @{username}\n"
            f"👤 الاسم: {profile.full_name}\n"
            f"🔗 رابط الحساب: https://www.instagram.com/{username}\n"
            f"👥 المتابعون: {profile.followers}\n"
            f"👤 يتابع: {profile.followees}\n"
            f"📸 عدد المنشورات: {profile.mediacount}\n"
            f"🔒 الحساب {'خاص 🔴' if profile.is_private else 'عام 🟢'}"
        )
        return info
    except Exception as e:
        return f"⚠️ حدث خطأ: {e}"

def download_video(url):
    try:
        ydl_opts = {'format': 'best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('url', "⚠️ لا يمكن تحميل هذا الفيديو.")
    except Exception as e:
        return f"⚠️ حدث خطأ: {e}"

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📸 Instagram", callback_data='instagram'),
         InlineKeyboardButton("🎵 TikTok", callback_data='tiktok'),
         InlineKeyboardButton("🐦 Twitter", callback_data='twitter')],
        [InlineKeyboardButton("📥 تحميل فيديو 🎥", callback_data='download')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔍 اختر الخدمة التي تريد استخدامها:", reply_markup=reply_markup)

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    context.user_data['mode'] = query.data
    await query.message.reply_text("🔹 أرسل اسم المستخدم أو الرابط:")

async def handle_message(update: Update, context: CallbackContext):
    mode = context.user_data.get('mode', 'instagram')
    text = update.message.text.strip()

    if mode in ['instagram', 'tiktok', 'twitter']:
        if mode == 'instagram':
            info = get_instagram_info(text)
        else:
            info = f"🔍 البحث عن حساب {mode}: @{text}"
        await update.message.reply_text(info)
    elif mode == 'download':
        video_url = download_video(text)
        await update.message.reply_text(f"📥 رابط التحميل: {video_url}")

def run_bot():
    bot_app = Application.builder().token(TOKEN).build()
    
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(button_handler))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ البوت يعمل الآن...")
    bot_app.run_polling()

import threading
threading.Thread(target=run_bot).start()

@app.route("/")
def home():
    return "البوت يعمل بنجاح على Railway 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
