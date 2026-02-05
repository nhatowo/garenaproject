# Đây là code dành cho trang WEB hiển thị mail code (Flask/FastAPI)
# Đảm bảo bạn đã cài: pip install flask imap_tools

from flask import Flask, render_template_string
from imap_tools import MailBox, AND
import re

app = Flask(__name__)

# Cấu hình mail của Nhật
MY_GMAIL = "anhnhatlamacc@gmail.com"
MY_APP_PASS = "jdmx zyeb vhtr lqhn"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Hộp thư xác minh - {{ domain }}</title>
    <meta http-equiv="refresh" content="5"> <style>
        body { font-family: sans-serif; background: #1a1a1a; color: #fff; text-align: center; padding: 50px; }
        .code-card { background: #333; padding: 20px; border-radius: 10px; border: 2px solid #ff4655; display: inline-block; }
        .code { font-size: 50px; color: #ff4655; font-weight: bold; letter-spacing: 5px; }
        .email { color: #aaa; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h2>📬 Đang hóng code cho {{ domain }}</h2>
    <div class="code-card">
        {% if code %}
            <div class="email">Mail nhận: {{ target }}</div>
            <div class="code">{{ code }}</div>
            <div style="margin-top:10px">Vừa nhận xong!</div>
        {% else %}
            <div class="code">⏳...</div>
            <p>Đang đợi code từ Garena gửi tới...</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
@app.route('/inbox')
def inbox():
    latest_code = None
    target_user = "Chưa có"
    
    try:
        with MailBox('imap.gmail.com').login(MY_GMAIL, MY_APP_PASS) as mailbox:
            # Lấy mail mới nhất từ Garena
            for msg in mailbox.fetch(limit=1, reverse=True):
                target_user = msg.to[0]
                match = re.search(r'\b\d{6}\b', msg.text or msg.html)
                if match:
                    latest_code = match.group(0)
    except:
        pass

    return render_template_string(HTML_TEMPLATE, 
                                 code=latest_code, 
                                 target=target_user, 
                                 domain="anhnhat07.online")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
