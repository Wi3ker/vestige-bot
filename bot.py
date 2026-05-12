import os, json, logging, pathlib, sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import firebase_admin
from firebase_admin import credentials, firestore

logging.basicConfig(level=logging.INFO)

# Firebase
if os.environ.get("GOOGLE_CREDENTIALS"):
    print("✅ Loading Firebase from environment variable...")
    cred = credentials.Certificate(json.loads(os.environ["GOOGLE_CREDENTIALS"]))
elif pathlib.Path("serviceAccount.json").exists():
    print("✅ Loading Firebase from serviceAccount.json...")
    cred = credentials.Certificate("serviceAccount.json")
else:
    print("❌ No Firebase credentials found! Exiting.")
    sys.exit(1)

firebase_admin.initialize_app(cred)
db = firestore.client()
print("✅ Firebase connected!")

ALLOWED_USERS = {8470062519}
TOKEN = '8551082233:AAETRVaLJowjDH8exUHLiE0bYewefxKtH8g'

def is_allowed(uid): return uid in ALLOWED_USERS

def get_counts():
    counts = {"new":0,"progress":0,"done":0,"cancel":0}
    for doc in db.collection("orders").stream():
        s = doc.to_dict().get("status","new")
        counts[s] = counts.get(s,0) + 1
    return counts

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied.")
        return
    c = get_counts()
    text = (
        f"👋 *Vestige Order Dashboard*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🆕 New: *{c['new']}*\n"
        f"🚚 In Progress: *{c['progress']}*\n"
        f"✅ Done: *{c['done']}*\n"
        f"❌ Cancelled: *{c['cancel']}*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"Select a category:"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🆕 New ({c['new']})", callback_data="list_new"),
         InlineKeyboardButton(f"🚚 In Progress ({c['progress']})", callback_data="list_progress")],
        [InlineKeyboardButton(f"✅ Done ({c['done']})", callback_data="list_done"),
         InlineKeyboardButton(f"❌ Cancelled ({c['cancel']})", callback_data="list_cancel")],
        [InlineKeybo
