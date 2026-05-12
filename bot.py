import os
import sys
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ─── Logging (critical for Railway debugging) ───
logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ─── Config ───
TOKEN = os.environ.get("BOT_TOKEN", "8654320963:AAG7lyMjXUZxRyBfUpCU_u1uZnNzqjZTxww")

# ─── Handlers ───
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f"▶️ /start from {user.id} ({user.username})")
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\nWelcome to Vestigio Store bot."
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"❌ Exception while handling an update: {context.error}", exc_info=True)

# ─── Main ───
async def main() -> None:
    logger.info("🚀 Bot starting...")
    application = Application.builder().token(TOKEN).build()

    # CRITICAL: Delete any old webhook and drop pending updates
    await application.bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Webhook deleted, pending updates cleared")

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_error_handler(error_handler)

    logger.info("▶️ Starting polling...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())
