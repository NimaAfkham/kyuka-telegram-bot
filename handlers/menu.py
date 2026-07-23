from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_categories, get_items_by_category
from services.menu_generator import generate_menu_json
from services.publisher import publish_menu_json
from config import ALLOWED_USER_IDS

def is_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USER_IDS

async def list_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_allowed(query.from_user.id):
        await query.edit_message_text("⛔ Access denied.")
        return

    categories = await get_categories()
    if not categories:
        await query.edit_message_text("No categories found.")
        return

    text = "📋 *Categories*\n\n"
    keyboard = []

    for cat in categories:
        text += f"• {cat['name']} (`{cat['slug']}`)\n"
        keyboard.append([
            InlineKeyboardButton(
                f"📂 {cat['name']}",
                callback_data=f"cat_{cat['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_allowed(query.from_user.id):
        return

    category_id = query.data.split("_")[1]
    items = await get_items_by_category(category_id)

    if not items:
        await query.edit_message_text("No items in this category.")
        return

    text = "🍽 *Items*\n\n"
    for item in items:
        price = item["price"] if item["price"] is not None else "—"
        text += f"• *{item['name']}* → {price}\n"

    keyboard = [[InlineKeyboardButton("« Back to Categories", callback_data="list_categories")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def publish_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_allowed(query.from_user.id):
        await query.edit_message_text("⛔ Access denied.")
        return

    await query.edit_message_text("⏳ Generating menu.json from Neon…")

    try:
        content = await generate_menu_json()
        result = publish_menu_json(content)
        await query.edit_message_text(
            f"🎌 *Menu Published*\n\n{result}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await query.edit_message_text(f"❌ Error:\n`{str(e)}`", parse_mode="Markdown")

async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📋 List Categories", callback_data="list_categories")],
        [InlineKeyboardButton("🔄 Regenerate & Publish Menu", callback_data="publish_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🎌 *Kyuka Café Admin Bot*\n\nChoose an action:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )