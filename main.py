import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from config import TELEGRAM_BOT_TOKEN
from database import init_db, close_db
from handlers.start import start
from handlers.menu import (
    list_categories,
    show_category_items,
    show_item_options,
    ask_new_price,
    receive_new_price,
    cancel_edit,
    publish_menu,
    back_main,
    WAITING_FOR_PRICE,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(app: Application):
    await init_db()


async def post_shutdown(app: Application):
    await close_db()


def main():
    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Conversation handler for editing price
    edit_price_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_new_price, pattern="^edit_price$")],
        states={
            WAITING_FOR_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_price)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_edit)],
        allow_reentry=True,
    )

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel_edit))

    # Callbacks
    app.add_handler(CallbackQueryHandler(list_categories, pattern="^list_categories$"))
    app.add_handler(CallbackQueryHandler(show_category_items, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(show_item_options, pattern="^item_"))
    app.add_handler(CallbackQueryHandler(publish_menu, pattern="^publish_menu$"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))

    # Conversation
    app.add_handler(edit_price_conv)

    print("🤖 Kyuka Admin Bot is running...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()