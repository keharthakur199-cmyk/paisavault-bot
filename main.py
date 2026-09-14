import os, telebot
from flask import Flask
import threading
app = Flask('')
@app.route('/')
def home():
    return "Bot is Live!"
threading.Thread(target=lambda: app.run(host='0.0.0.0',port=8080)).start()
bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "PaisaVault Bot Live! ✅")
bot.infinity_polling()
