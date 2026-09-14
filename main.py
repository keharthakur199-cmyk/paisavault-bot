import os, telebot, json, threading
from flask import Flask

CHANNEL_USERNAME = "@thelootlebhai"
CHANNEL_LINK = "https://t.me/thelootlebhai"
YOUTUBE_LINK = "https://www.youtube.com/@LootLeBhai"
MIN_WITHDRAW = 10 # <-- 10₹ kar diya

app = Flask('')
@app.route('/')
def home(): return "Bot Live!"
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080), daemon=True).start()

bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
DB = "db.json"

def load_db():
    if not os.path.exists(DB): return {"admin_id": None}
    try:
        with open(DB, 'r') as f:
            d = json.load(f)
            if "admin_id" not in d: d["admin_id"]=None
            return d
    except: return {"admin_id": None}
def save_db(d):
    with open(DB, 'w') as f: json.dump(d, f)

@bot.message_handler(commands=['start'])
def start(m):
    db = load_db(); s = str(m.from_user.id)
    if s not in db: db[s] = {"balance": 0, "tasks": [], "awaiting_yt": False, "awaiting_upi": False}; save_db(db)
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton("📢 Telegram Join - 5₹", url=CHANNEL_LINK),
        telebot.types.InlineKeyboardButton("✅ Telegram Check", callback_data="check_tele"),
        telebot.types.InlineKeyboardButton("▶️ Youtube - 5₹", url=YOUTUBE_LINK),
        telebot.types.InlineKeyboardButton("📸 Youtube Screenshot", callback_data="check_yt"),
        telebot.types.InlineKeyboardButton("💰 Balance", callback_data="balance"),
        telebot.types.InlineKeyboardButton("💸 Withdraw 10₹ UPI", callback_data="withdraw")
    )
    bot.send_message(m.chat.id, f"🔥 Loot Le Bhai!\n\n📢 Telegram = 5₹\n▶️ Youtube Screenshot = 5₹\n💸 Min Withdraw = {MIN_WITHDRAW}₹ UPI", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def set_admin(m):
    db = load_db(); db["admin_id"] = m.from_user.id; save_db(db)
    bot.send_message(m.chat.id, f"✅ Tu Admin ban gaya @{m.from_user.username}!\nAb se Withdraw tere paas ayenge!")

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    db = load_db(); s = str(call.from_user.id)
    if s not in db: db[s] = {"balance": 0, "tasks": [], "awaiting_yt": False, "awaiting_upi": False}
    if call.data == "check_tele":
        try:
            st = bot.get_chat_member(CHANNEL_USERNAME, call.from_user.id).status
            if st in ['member','administrator','creator','restricted']:
                if "telegram" not in db[s]["tasks"]:
                    db[s]["balance"] += 5; db[s]["tasks"].append("telegram"); save_db(db)
                    bot.send_message(call.message.chat.id, f"✅ +5₹\nTotal {db[s]['balance']}₹")
                else: bot.send_message(call.message.chat.id, "Already mil chuka!")
            else: bot.send_message(call.message.chat.id, f"❌ Join karo {CHANNEL_LINK}")
        except: bot.send_message(call.message.chat.id, "Bot ko Admin banao!")
    elif call.data == "check_yt":
        if "youtube" in db[s]["tasks"]: bot.send_message(call.message.chat.id, "Already mil chuka!")
        else: db[s]["awaiting_yt"]=True; save_db(db); bot.send_message(call.message.chat.id, f"📸 Screenshot bhejo\n{YOUTUBE_LINK}")
    elif call.data == "balance": bot.send_message(call.message.chat.id, f"💰 Balance: {db[s]['balance']}₹")
    elif call.data == "withdraw":
        if db[s]["balance"] < MIN_WITHDRAW: bot.send_message(call.message.chat.id, f"❌ Min {MIN_WITHDRAW}₹, Aapka {db[s]['balance']}₹")
        else: db[s]["awaiting_upi"]=True; save_db(db); bot.send_message(call.message.chat.id, "💸 UPI ID bhejo:")

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    db = load_db(); s = str(m.from_user.id)
    if s not in db: return
    if db[s].get("awaiting_yt"):
        if "youtube" not in db[s]["tasks"]:
            db[s]["balance"] += 5; db[s]["tasks"].append("youtube"); db[s]["awaiting_yt"]=False; save_db(db)
            bot.send_message(m.chat.id, f"✅ Screenshot Mila! +5₹\nTotal {db[s]['balance']}₹")
            if db.get("admin_id"):
                try:
                    bot.forward_message(db["admin_id"], m.chat.id, m.message_id)
                    bot.send_message(db["admin_id"], f"📸 YT Screenshot\nUser: {m.from_user.first_name} @{m.from_user.username}")
                except: pass

@bot.message_handler(func=lambda m: True)
def handle_text(m):
    if m.text.startswith("/"): return
    db = load_db(); s = str(m.from_user.id)
    if s not in db: return
    if db[s].get("awaiting_upi"):
        upi = m.text.strip(); amount = db[s]["balance"]
        db[s]["balance"]=0; db[s]["awaiting_upi"]=False; save_db(db)
        bot.send_message(m.chat.id, f"✅ Withdraw: {amount}₹\nUPI: {upi}\n24h me ayega!")
        if db.get("admin_id"):
            try: bot.send_message(db["admin_id"], f"💸 *NEW WITHDRAW 10₹*\n👤 {m.from_user.first_name} @{m.from_user.username}\n💰 {amount}₹\n💳 UPI: `{upi}`", parse_mode="Markdown")
            except: pass

bot.infinity_polling()
