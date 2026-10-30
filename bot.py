import os
import threading
from flask import Flask
import telebot
from google import genai

# Lấy Token và Key từ biến môi trường của đám mây
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

BOT_PERSONA = """
Bạn tên là Nguyễn Nhật Nam. 
Trong chat 1-1: Bạn là một người bạn thân thiện, trò chuyện gần gũi, hài hước.
Trong nhóm công việc: Bạn là một thành viên thông minh, chuyên nghiệp, đưa ra các ý kiến sắc sảo, ngắn gọn và hữu ích khi được mọi người gọi tên hỏi việc.
"""

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

BOT_USERNAME = ""
try:
    bot_info = bot.get_me()
    BOT_USERNAME = f"@{bot_info.username}"
except Exception as e:
    print(f"Không lấy được thông tin bot: {e}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        chat_type = message.chat.type
        user_text = message.text
        if not user_text:
            return

        # Nếu ở nhóm: chỉ trả lời khi được gọi tên hoặc reply tin nhắn của bot
        if chat_type in ['group', 'supergroup']:
            is_mentioned = BOT_USERNAME and BOT_USERNAME.lower() in user_text.lower()
            is_replied = message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id
            if not is_mentioned and not is_replied:
                return

        user_name = message.from_user.first_name
        prompt = f"{BOT_PERSONA}\n\nThành viên '{user_name}' trong khung chat ({chat_type}) nói: {user_text}"

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Lỗi: {e}")

# Tạo web server nhỏ bằng Flask để Render nhận diện cổng mạng
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Nguyen Nhat Nam is running 24/7!"

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Chạy bot ở một luồng riêng biệt
    t = threading.Thread(target=run_bot)
    t.start()
    
    # Chạy Flask server trên cổng do Render cung cấp
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)