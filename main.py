import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import TELEGRAM_BOT_TOKEN
from database import init_db, close_db
from handlers.start import start
from handlers.menu import list_categories, show_category_items, publish_menu, back_main

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

    # Commands
    app.add_handler(CommandHandler("start", start))

    # Callbacks
    app.add_handler(CallbackQueryHandler(list_categories, pattern="^list_categories$"))
    app.add_handler(CallbackQueryHandler(show_category_items, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(publish_menu, pattern="^publish_menu$"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))

    print("🤖 Kyuka Admin Bot is running...")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()