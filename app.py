# -*- coding: utf-8 -*-
import os
import telebot
import requests
from flask import Flask, jsonify
from threading import Thread

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8660698310:AAGpr4GeC_LmRTsMyMn84P-AsL7iy0upL4w")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY", "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")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_ai(question):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json; charset=utf-8"
    }
    data = {
        "model": "openrouter/free",
        "messages": [{"role": "user", "content": question}]
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        r.encoding = 'utf-8'
        if r.status_code != 200:
            return f"خطأ: {r.text}"
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"خطأ: {e}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بيك! اكتب أي سؤال.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        answer = ask_ai(message.text)
        if len(answer) > 4000:
            for i in range(0, len(answer), 4000):
                bot.reply_to(message, answer[i:i+4000])
        else:
            bot.reply_to(message, answer)
    except Exception as e:
        print(f"خطأ: {e}")

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return jsonify({"status": "Bot is running"})

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print(f"قطع الاتصال: {e}")
            import time
            time.sleep(5)

if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
