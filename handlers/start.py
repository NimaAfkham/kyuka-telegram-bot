from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ALLOWED_USER_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text("⛔ Access denied. This bot is private.")
        return

    keyboard = [
        [InlineKeyboardButton("📋 List Categories", callback_data="list_categories")],
        [InlineKeyboardButton("🔄 Regenerate & Publish Menu", callback_data="publish_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎌 *Kyuka Café Admin Bot*\n\n"
        "Welcome Nima.\n"
        "Choose an action:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )