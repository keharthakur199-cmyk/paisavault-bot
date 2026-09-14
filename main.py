import os, telebot, json, threading
from flask import Flask

CHANNEL_USERNAME = "@thelootlebhai"
CHANNEL_LINK = "https://t.me/thelootlebhai"
YOUTUBE_LINK = "https://www.youtube.com/@LootLeBhai"

app = Flask('')
@app.route('/')
def home():
    return "Loot Le Bhai Bot is Live!"
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()

bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
DB = "db.json"

def load_db():
    if not os.path.exists(DB): return {}
    with open(DB, 'r') as f: return json.load(f)

def save_db(d):
    with open(DB, 'w') as f: json.dump(d, f)

def get_user(uid):
    db = load_db()
    if str(uid) not in db:
        db[str(uid)] = {"balance": 0, "tasks": []}
        save_db(db)
    return db[str(uid)]

@bot.message_handler(commands=['start'])
def start(m):
    get_user(m.from_user.id)
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton("📢 Telegram Join - 5₹", url=CHANNEL_LINK),
        telebot.types.InlineKeyboardButton("✅ Join Check Karo", callback_data="check_tele"),
        telebot.types.InlineKeyboardButton("▶️ Youtube Subscribe - 5₹", url=YOUTUBE_LINK),
        telebot.types.InlineKeyboardButton("💰 My Balance", callback_data="balance")
    )
    bot.send_message(m.chat.id, f"Loot Le Bhai me Swagat Hai! 🔥\n\nHar Task pe 5₹ Kamao!\n📢 Telegram Join - 5₹\n▶️ Youtube Subscribe - 5₹\n\nJoin karke Check dabao, turant 5₹ milega!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.from_user.id
    db = load_db()
    s_uid = str(uid)
    if s_uid not in db:
        db[s_uid] = {"balance": 0, "tasks": []}

    if call.data == "check_tele":
        try:
            member = bot.get_chat_member(CHANNEL_USERNAME, uid)
            if member.status in ['member', 'administrator', 'creator']:
                if "telegram" not in db[s_uid]["tasks"]:
                    db[s_uid]["balance"] += 5
                    db[s_uid]["tasks"].append("telegram")
                    save_db(db)
                    bot.answer_callback_query(call.id, "✅ 5₹ Added!")
                    bot.send_message(call.message.chat.id, f"✅ Verified! 5₹ add ho gaye!\n💰 Total Balance: {db[s_uid]['balance']}₹")
                else:
                    bot.send_message(call.message.chat.id, "Is task ka paisa mil chuka hai!")
            else:
                bot.send_message(call.message.chat.id, f"❌ Pehle channel join karo! {CHANNEL_LINK}")
        except:
            bot.send_message(call.message.chat.id, f"❌ Bot ko {CHANNEL_USERNAME} me Admin banao!")
    
    elif call.data == "balance":
        bot.send_message(call.message.chat.id, f"💰 Aapka Balance: {db[s_uid]['balance']}₹")

@bot.message_handler(commands=['balance'])
def bal(m):
    u = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"💰 Balance: {u['balance']}₹")

bot.infinity_polling()
