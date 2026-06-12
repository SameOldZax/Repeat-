"""
ربات تست - تکرار پیام هر ۱ دقیقه
نصب: pip install python-telegram-bot==20.7
اجرا: python repeat_bot.py
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ===================== تنظیمات =====================
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")
# ===================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع - چخبر کیری"""
    # اگه جاب قبلی داره، کنسلش کن
    if "job" in context.user_data:
        context.user_data["job"].schedule_removal()
        del context.user_data["job"]

    context.user_data.clear()

    await update.message.reply_text(
        "سلام! 👋\n\n"
        "خوبی؟ امیدوارم حالت خوب باشه 😊\n\n"
        "یه چیزی برام بفرست — یه کلمه، یه جمله، یه عدد، هرچی دوست داری.\n"
        "من هر ۱ دقیقه اون رو برات تکرار می‌کنم!"
    )


async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت پیام کاربر و شروع تکرار"""
    # اگه جاب قبلی داره، کنسلش کن
    if "job" in context.user_data:
        context.user_data["job"].schedule_removal()
        del context.user_data["job"]

    text = update.message.text
    context.user_data["message"] = text
    chat_id = update.effective_chat.id

    stop_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("⛔ متوقف کن", callback_data="stop")]
    ])

    await update.message.reply_text(
        f"✅ دریافت شد!\n\n"
        f"هر یک دقیقه میفرستمش برات خفه شو کیری:\n"
        f"«{text}»\n\n"
        f"هر وقت خواستی متوقف کن 👇",
        reply_markup=stop_button
    )

    # شروع جاب تکرار
    job = context.job_queue.run_repeating(
        repeat_message,
        interval=60,
        first=60,
        chat_id=chat_id,
        data=text
    )
    context.user_data["job"] = job


async def repeat_message(context: ContextTypes.DEFAULT_TYPE):
    """ارسال پیام تکراری"""
    stop_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("⛔ متوقف کن", callback_data="stop")]
    ])

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=f"🔁 {context.job.data}",
        reply_markup=stop_button
    )


async def stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """متوقف کردن تکرار"""
    query = update.callback_query
    await query.answer()

    if "job" in context.user_data:
        context.user_data["job"].schedule_removal()
        del context.user_data["job"]
        await query.edit_message_text("✅ متوقف شد! هر وقت خواستی دوباره /start بزن.")
    else:
        await query.edit_message_text("قبلاً متوقف شده بود!")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(stop_handler, pattern="^stop$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message))

    print("ربات تست در حال اجراست...")
    app.run_polling()


if __name__ == "__main__":
    main()
