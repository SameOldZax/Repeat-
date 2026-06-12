import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "job" in context.user_data:
        context.user_data["job"].schedule_removal()
        del context.user_data["job"]
    context.user_data.clear()
    await update.message.reply_text(
        "سلام! خوبی؟\n\nیه چیزی برام بفرست — کلمه، جمله، عدد، هرچی.\nهر ۱ دقیقه برات تکرار میکنم!"
    )


async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "job" in context.user_data:
        context.user_data["job"].schedule_removal()
        del context.user_data["job"]

    text = update.message.text
    context.user_data["message"] = text
    chat_id = update.effective_chat.id

    stop_button = InlineKeyboardMarkup([[InlineKeyboardButton("Stop", callback_data="stop")]])

    await update.message.reply_text(
        f"دریافت شد!\nهر ۱ دقیقه این رو میفرستم:\n{text}",
        reply_markup=stop_button
    )

    job = context.job_queue.run_repeating(
        repeat_message,
        interval=60,
        first=60,
        chat_id=chat_id,
        data=text
    )
    context.user_data["job"] = job


async def repeat_message(context: ContextTypes.DEFAULT_TYPE):
    stop_button = InlineKeyboardMarkup([[InlineKeyboardButton("Stop", callback_data="stop")]])
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=context.job.data,
        reply_markup=stop_button
    )


async def stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if "job" in context.user_data:
        context.user_data["job"].schedule_removal()
        del context.user_data["job"]
        await query.edit_message_text("متوقف شد! برای شروع دوباره /start بزن.")
    else:
        await query.edit_message_text("قبلا متوقف شده بود!")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    print("APP JOBQUEUE:", app.job_queue)
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(stop_handler, pattern="^stop$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message))
    print("ربات در حال اجراست...")
    app.run_polling()


if __name__ == "__main__":
    main()
