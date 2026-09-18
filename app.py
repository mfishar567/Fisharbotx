# -*- coding: utf-8 -*-
import os
import telebot
import requests
from flask import Flask, jsonify
from threading import Thread

# ===== إعداداتك =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")
# ===================
if not TELEGRAM_TOKEN or not OPENROUTER_KEY:
    raise RuntimeError("Missing environment variables")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_ai(question):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json; charset=utf-8"}
    data = {"model": "openrouter/free", "messages": [{"role": "user", "content": question}]}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        r.encoding = 'utf-8'
        return r.json()["choices"][0]["message"]["content"] if r.status_code == 200 else f"⚠️ {r.text}"
    except Exception as e:
        return f"⚠️ {e}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 أهلاً بيك! اكتب أي سؤال.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        answer = ask_ai(message.text)
        bot.reply_to(message, answer[:4000])
    except Exception as e:
        print(f"⚠️ {e}")

# --- Flask للتشغيل في الخلفية ---
app = Flask(__name__)
@app.route('/')
@app.route('/health')
def health():
    return jsonify({"status": "Bot is running"})

def run_bot():
    bot.polling(none_stop=True, interval=1, timeout=20)

if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
