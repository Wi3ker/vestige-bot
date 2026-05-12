import os, json, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import firebase_admin
from firebase_admin import credentials, firestore

logging.basicConfig(level=logging.INFO)

# Firebase — reads from Railway env variable or local file
if os.environ.get("GOOGLE_CREDENTIALS"):
    cred = credentials.Certificate(json.loads(os.environ["GOOGLE_CREDENTIALS"]))
else:
    cred = credentials.Certificate("serviceAccount.json")

firebase_admin.initialize_app(cred)
db = firestore.client()

# Allowed users
ALLOWED_USERS = {8470062519, 5591183463}
TOKEN = '8654320963:AAG7lyMjXUZxRyBfUpCU_u1uZnNzqjZTxww'
