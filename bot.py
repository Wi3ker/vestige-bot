import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Setup Firebase
# Ensure "serviceAccount.json" is in the same folder on GitHub
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. Allowed Users (Owner & Staff)
ALLOWED_USERS = {8470062519, 5591183463}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    
    # Dashboard buttons
    keyboard = [
        [InlineKeyboardButton("🆕 New Orders", callback_data='list_new')],
        [InlineKeyboardButton("🚚 In Progress", callback_data='list_progress')],
        [InlineKeyboardButton("✅ Done", callback_data='list_done')],
        [InlineKeyboardButton("❌ Cancelled", callback_data='list_cancelled')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📦 Vestige Order Dashboard\nSelect a category to view orders:", 
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    # Your verified token
    TOKEN = '8654320963:AAG7lyMjXUZxRyBfUpCU_u1uZnNzqjZTxww'
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Vestige Bot is running...")
    app.run_polling()
  
