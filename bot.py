import os
import telebot
from flask import Flask, request
from google import genai

# Lấy các biến môi trường đã cấu hình trên Render
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)

# Xử lý tin nhắn từ người dùng bằng Gemini mới nhất
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_message = message.text
        if not user_message:
            return
        
        # Gọi Gemini 3.8-flash để sinh nội dung trả lời
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=user_message,
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Đã có lỗi xảy ra: {e}")

# Định nghĩa webhook nhận dữ liệu từ Telegram
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Forbidden', 403

# Trang chủ kiểm tra trạng thái dịch vụ
@app.route('/')
def index():
    return "Bot Nguyen Nhat Nam is running perfectly via Webhook!", 200

if __name__ == '__main__':
    bot.remove_webhook()
    render_url = f"https://nguyennhatnam.onrender.com/{TOKEN}"
    bot.set_webhook(url=render_url)
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)