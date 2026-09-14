import os, telebot, json, threading
from flask import Flask

CHANNEL_USERNAME = "@thelootlebhai"
CHANNEL_LINK = "https://t.me/thelootlebhai"
YOUTUBE_LINK = "https://www.youtube.com/@LootLeBhai"
ADMIN_ID = 0 # Yahan apni ID daal de @userinfobot se leke - jaise 123456789
MIN_WITHDRAW = 20

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
    if s not in db: db[s] = {"balance": 0, "tasks": [], "awaiting_yt": False, "awaiting_upi": False}; save_db(db)
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton("📢 Telegram Join - 5₹", url=CHANNEL_LINK),
        telebot.types.InlineKeyboardButton("✅ Telegram Check Karo", callback_data="check_tele"),
        telebot.types.InlineKeyboardButton("▶️ Youtube Subscribe - 5₹", url=YOUTUBE_LINK),
        telebot.types.InlineKeyboardButton("✅ Youtube Screenshot Bhejo - 5₹", callback_data="check_yt"),
        telebot.types.InlineKeyboardButton("💰 My Balance", callback_data="balance"),
        telebot.types.InlineKeyboardButton("💸 Withdraw (UPI)", callback_data="withdraw")
    )
    bot.send_message(m.chat.id, "🔥 *Loot Le Bhai me Swagat Hai!*\n\n📢 Telegram Join = 5₹ (Auto)\n▶️ Youtube Subscribe = 5₹ (Screenshot)\n💸 Min Withdraw = 20₹ UPI pe\n\nTask karo, Check dabao, paisa kamao!", reply_markup=markup, parse_mode="Markdown")

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
                    bot.send_message(call.message.chat.id, f"✅ Telegram Verified! +5₹\n💰 Total: {db[s]['balance']}₹")
                else: bot.send_message(call.message.chat.id, "Telegram ka mil chuka hai!")
            else: bot.send_message(call.message.chat.id, f"❌ Pehle join karo {CHANNEL_LINK}")
        except Exception as e: bot.send_message(call.message.chat.id, f"Bot ko Admin banao!")

    elif call.data == "check_yt":
        if "youtube" in db[s]["tasks"]:
            bot.send_message(call.message.chat.id, "✅ Youtube ka already mil chuka hai!")
        else:
            db[s]["awaiting_yt"] = True; save_db(db)
            bot.send_message(call.message.chat.id, f"📸 *Youtube Task:*\n\n1. Is link pe jao: {YOUTUBE_LINK}\n2. Subscribe karo\n3. Subscribe ka Screenshot yahan bhejo\n\nScreenshot bhejte hi 5₹ milega!", parse_mode="Markdown")

    elif call.data == "balance":
        bot.send_message(call.message.chat.id, f"💰 Balance: {db[s]['balance']}₹\nTasks: {', '.join(db[s]['tasks']) if db[s]['tasks'] else 'Koi nahi'}")

    elif call.data == "withdraw":
        if db[s]["balance"] < MIN_WITHDRAW:
            bot.send_message(call.message.chat.id, f"❌ Balance kam hai!\nAapka: {db[s]['balance']}₹\nMin: {MIN_WITHDRAW}₹ chahiye")
        else:
            db[s]["awaiting_upi"] = True; save_db(db)
            bot.send_message(call.message.chat.id, f"💸 Withdrawal\n💰 Balance: {db[s]['balance']}₹\n\nApni UPI ID bhejo:")

# Screenshot handle
@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    db = load_db(); s = str(m.from_user.id)
    if s not in db: return
    if db[s].get("awaiting_yt"):
        if "youtube" not in db[s]["tasks"]:
            db[s]["balance"] += 5
            db[s]["tasks"].append("youtube")
            db[s]["awaiting_yt"] = False
            save_db(db)
            bot.send_message(m.chat.id, f"✅ Screenshot Received! +5₹\n💰 Total: {db[s]['balance']}₹\nThanks for Subscribing @LootLeBhai!")
            # Admin ko forward
