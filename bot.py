import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import firebase_admin
from firebase_admin import credentials, firestore

# ─── Logging ───
logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ─── Firebase ───
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ─── Config ───
ALLOWED_USERS = {8470062519}
TOKEN = os.environ.get("BOT_TOKEN", "8654320963:AAG7lyMjXUZxRyBfUpCU_u1uZnNzqjZTxww")

def is_allowed(uid): 
    return uid in ALLOWED_USERS

def get_counts():
    counts = {"new": 0, "progress": 0, "done": 0, "cancel": 0}
    for doc in db.collection("orders").stream():
        s = doc.to_dict().get("status", "new")
        counts[s] = counts.get(s, 0) + 1
    return counts

# ─── /start ───
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
        [InlineKeyboardButton("📋 All Orders", callback_data="list_all")],
    ])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

# ─── Callbacks ───
async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_allowed(query.from_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return
    await query.answer()
    data = query.data

    if data.startswith("list_"):
        status_map = {
            "list_new":      ("new",      "🆕 New Orders"),
            "list_progress": ("progress", "🚚 In Progress"),
            "list_done":     ("done",     "✅ Completed"),
            "list_cancel":   ("cancel",   "❌ Cancelled"),
            "list_all":      (None,       "📋 All Orders"),
        }
        st, title = status_map.get(data, (None, "Orders"))
        if st:
            ref = db.collection("orders").where("status", "==", st).limit(20)
        else:
            ref = db.collection("orders").order_by("createdAt", direction=firestore.Query.DESCENDING).limit(20)
        orders = [{"id": d.id, **d.to_dict()} for d in ref.stream()]
        if not orders:
            await query.message.reply_text(f"{title}\n\n_No orders found._", parse_mode="Markdown")
            return
        await query.message.reply_text(f"{title} — *{len(orders)}* order(s)", parse_mode="Markdown")
        for o in orders[:8]:
            doc_id = o["id"]
            sid = doc_id[-6:].upper()
            status = o.get("status", "new")
            lines = [
                f"📋 *Order #{sid}*",
                f"🏷️ {o.get('businessName', '—')} · {o.get('city', '—')}",
                f"📱 {o.get('whatsapp', '—')}",
                f"🃏 Card: {o.get('cardColor', '—')}",
                f"Status: {status.upper()}",
            ]
            kb_rows = []
            if status not in ("done", "cancel"):
                kb_rows.append(InlineKeyboardButton("✅ Done", callback_data=f"confirm_{doc_id}"))
            if status not in ("progress", "done", "cancel"):
                kb_rows.append(InlineKeyboardButton("🚚 Progress", callback_data=f"progress_{doc_id}"))
            if status not in ("cancel", "done"):
                kb_rows.append(InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{doc_id}"))
            kb = InlineKeyboardMarkup([kb_rows]) if kb_rows else None
            await query.message.reply_text("\n".join(lines), parse_mode="Markdown", reply_markup=kb)
        return

    action_map = {"confirm": "done", "progress": "progress", "cancel": "cancel", "reopen": "new"}
    for action, new_status in action_map.items():
        if data.startswith(f"{action}_"):
            doc_id = data[len(action) + 1:]
            doc_ref = db.collection("orders").document(doc_id)
            doc = doc_ref.get()
            if not doc.exists:
                await query.edit_message_text("❌ Order not found.")
                return
            doc_ref.update({"status": new_status, "updatedAt": firestore.SERVER_TIMESTAMP})
            o = doc.to_dict()
            sid = doc_id[-6:].upper()
            labels = {"done": "✅ DONE", "progress": "🚚 IN PROGRESS", "cancel": "❌ CANCELLED", "new": "🔄 RE-OPENED"}
            await query.message.reply_text(f"{labels[new_status]}\n\nOrder *#{sid}* — *{o.get('businessName', '?')}*", parse_mode="Markdown")
            return

# ─── Error handler ───
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"❌ Exception: {context.error}", exc_info=True)

# ─── Main (SYNCHRONOUS — no asyncio.run) ───
def main() -> None:
    logger.info("🚀 Bot starting...")
    application = Application.builder().token(TOKEN).build()

    # CRITICAL: Delete webhook before polling
    application.bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Webhook deleted, pending updates cleared")

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_error_handler(error_handler)

    # Blocks forever — this is correct for a Background Worker
    logger.info("▶️ Starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
