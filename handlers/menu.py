from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_categories, get_items_by_category, get_item_by_id, update_item_price
from services.menu_generator import generate_menu_json
from services.publisher import publish_menu_json
from config import ALLOWED_USER_IDS

# Conversation states
WAITING_FOR_PRICE = 1

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
        text += f"• {cat['name']}\n"
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

    text = "🍽 *Items* — click an item to edit\n\n"
    keyboard = []

    for item in items:
        price = item["price"] if item["price"] is not None else "—"
        text += f"• *{item['name']}* → {price}\n"
        keyboard.append([
            InlineKeyboardButton(
                f"{item['name']} ({price})",
                callback_data=f"item_{item['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton("« Back to Categories", callback_data="list_categories")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)


async def show_item_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_allowed(query.from_user.id):
        return

    item_id = query.data.split("_")[1]
    item = await get_item_by_id(item_id)

    if not item:
        await query.edit_message_text("Item not found.")
        return

    # Store item_id for the next step
    context.user_data["edit_item_id"] = item_id
    context.user_data["edit_item_name"] = item["name"]

    price = item["price"] if item["price"] is not None else "—"

    text = (
        f"🍽 *{item['name']}*\n\n"
        f"Current price: `{price}`\n\n"
        f"What do you want to do?"
    )

    keyboard = [
        [InlineKeyboardButton("✏️ Edit Price", callback_data="edit_price")],
        [InlineKeyboardButton("« Back", callback_data=f"cat_{item['category_id']}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)


async def ask_new_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_allowed(query.from_user.id):
        return ConversationHandler.END

    item_name = context.user_data.get("edit_item_name", "this item")

    await query.edit_message_text(
        f"✏️ Send the **new price** for *{item_name}*\n\n"
        f"Just type a number (example: `250` or `175.5`)\n"
        f"Or type /cancel to abort.",
        parse_mode="Markdown"
    )

    return WAITING_FOR_PRICE


async def receive_new_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return ConversationHandler.END

    text = update.message.text.strip().replace(",", ".")

    try:
        new_price = float(text)
        if new_price < 0:
            raise ValueError("Price cannot be negative")
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid price. Please send a valid number (example: 250).\n"
            "Or type /cancel to abort."
        )
        return WAITING_FOR_PRICE

    item_id = context.user_data.get("edit_item_id")
    item_name = context.user_data.get("edit_item_name", "Item")

    success = await update_item_price(item_id, new_price)

    if success:
        await update.message.reply_text(
            f"✅ Price updated!\n\n"
            f"*{item_name}* → `{new_price}`\n\n"
            f"Remember to press **🔄 Regenerate & Publish Menu** when you finish all changes.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Failed to update the price in the database.")

    # Clean up
    context.user_data.pop("edit_item_id", None)
    context.user_data.pop("edit_item_name", None)

    return ConversationHandler.END


async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Edit cancelled.")
    context.user_data.pop("edit_item_id", None)
    context.user_data.pop("edit_item_name", None)
    return ConversationHandler.END


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