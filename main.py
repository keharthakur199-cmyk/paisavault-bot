import os, telebot, json, threading
from flask import Flask

CHANNEL_USERNAME = "@thelootlebhai"
CHANNEL_LINK = "https://t.me/thelootlebhai"
YOUTUBE_LINK = "https://www.youtube.com/@LootLeBhai"

app = Flask('')
@app.route('/')
def home(): return "Bot Live!"
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()

bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
DB = "db.json"

def load_db():
    if not os.path.exists(DB): return {}
    try:
        with open(DB, 'r') as f: return json.load(f)
    except: return {}
def save_db(d):
    with open(DB, 'w') as f: json.dump(d, f)

@bot.message_handler(commands=['start'])
def start(m):
    db = load_db(); s = str(m.from_user.id)
    if s not in db: db[s] = {"balance": 0, "tasks": []}; save_db(db)
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton("📢 Telegram Join - 5₹", url=CHANNEL_LINK),
        telebot.types.InlineKeyboardButton("✅ Telegram Check Karo", callback_data="check_tele"),
        telebot.types.InlineKeyboardButton("▶️ Youtube Subscribe - 5₹", url=YOUTUBE_LINK),
        telebot.types.InlineKeyboardButton("✅ Youtube Check Karo", callback_data="check_yt"),
        telebot.types.InlineKeyboardButton("💰 My Balance", callback_data="balance")
    )
    bot.send_message(m.chat.id, "Loot Le Bhai me Swagat Hai! 🔥\n\nHar Task pe 5₹ Kamao!\n📢 Telegram Join - 5₹\n▶️ Youtube Subscribe - 5₹\n\nJoin karke Check dabao, turant 5₹ milega!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    db = load_db(); s = str(call.from_user.id)
    if s not in db: db[s] = {"balance": 0, "tasks": []}
    if call.data == "check_tele":
        try:
            st = bot.get_chat_member(CHANNEL_USERNAME, call.from_user.id).status
            if st in ['member','administrator','creator','restricted']:
                if "telegram" not in db[s]["tasks"]:
                    db[s]["balance"] += 5; db[s]["tasks"].append("telegram"); save_db(db)
                    bot.send_message(call.message.chat.id, f"✅ Telegram Done! +5₹\n💰 Total: {db[s]['balance']}₹")
                else: bot.send_message(call.message.chat.id, "Telegram ka already mil chuka!")
            else: bot.send_message(call.message.chat.id, f"❌ Pehle join karo {CHANNEL_LINK}")
        except Exception as e: bot.send_message(call.message.chat.id, f"Bot ko Admin banao! {e}")
    elif call.data == "check_yt":
        if "youtube" not in db[s]["tasks"]:
            db[s]["balance"] += 5; db[s]["tasks"].append("youtube"); save_db(db)
            bot.send_message(call.message.chat.id, f"✅ Youtube Done! +5₹\n💰 Total: {db[s]['balance']}₹\nThanks for Subscribing!")
        else: bot.send_message(call.message.chat.id, "Youtube ka already mil chuka!")
    elif call.data == "balance":
        bot.send_message(call.message.chat.id, f"💰 Balance: {db[s]['balance']}₹")

bot.infinity_polling()
