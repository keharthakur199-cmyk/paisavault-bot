import os, telebot
from flask import Flask
import threading
app = Flask('')
@app.route('/')
def home():
    return "Loot Le Bhai Bot is Live!"
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()
bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Loot Le Bhai me Swagat Hai! 🔥\n\nHar Task pe 5₹ Kamao!\n📢 Telegram Join - 5₹\n▶️ Youtube Subscribe - 5₹\n\n💰 Balance dekhne ke liye /balance likho")
bot.infinity_polling()
