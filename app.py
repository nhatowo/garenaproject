from flask import Flask, request, render_template_string, session, redirect, url_for
from imap_tools import MailBox, AND
import os
import datetime

# ================= CẤU HÌNH =================
# Lấy từ Environment Variables trên Render
MY_GMAIL    = os.environ.get("MY_GMAIL")
MY_APP_PASS = os.environ.get("MY_APP_PASS")
SECRET_KEY  = os.environ.get("SECRET_KEY", "mac_dinh_bao_mat")
DOMAIN      = "anhnhat07.online"

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ================= GIAO DIỆN HTML (ĐÃ GỘP SẴN) =================
HTML_LOGIN = """
<!DOCTYPE html>
<html>
<head>
    <title>Hộp thư Garena</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 300px; text-align: center; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #1877f2; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        button:hover { background: #166fe5; }
        h2 { color: #333; }
        .logo { font-size: 24px; font-weight: bold; color: #ff4d4f; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="box">
        <div class="logo">Garena Mail</div>
        <h2>Đăng Nhập Xem Code</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Tên tài khoản (Ví dụ: anhnhat.01)" required>
            <button type="submit">Xem Hộp Thư</button>
        </form>
    </div>
</body>
</html>
"""

HTML_INBOX = """
<!DOCTYPE html>
<html>
<head>
    <title>Hộp thư: {{ username }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 20px auto; padding: 0 20px; background: #f9f9f9; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 15px; }
        .logout { color: red; text-decoration: none; font-weight: bold; }
        .email-item { background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; border: 1px solid #ddd; }
        .time { color: #888; font-size: 12px; float: right; }
        .subject { font-weight: bold; color: #333; }
        .body-text { margin-top: 10px; color: #555; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="header">
        <h3>📧 Mail của: {{ username }}@{{ domain }}</h3>
        <a href="/logout" class="logout">Thoát</a>
    </div>
    
    {% if emails %}
        {% for email in emails %}
        <div class="email-item">
            <div class="time">{{ email.date_str }}</div>
            <div class="subject">{{ email.subject }}</div>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">
            <div class="body-text">{{ email.body }}</div>
        </div>
        {% endfor %}
    {% else %}
        <p style="text-align:center; color:#666; margin-top:50px;">📭 Chưa có thư nào.</p>
        <div style="text-align:center"><a href="/inbox">🔄 Bấm để làm mới</a></div>
    {% endif %}
</body>
</html>
"""

# ================= XỬ LÝ PYTHON =================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username'].strip()
        session['user'] = user
        return redirect(url_for('inbox'))
    return render_template_string(HTML_LOGIN)

@app.route('/inbox')
def inbox():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    username = session['user']
    target_email = f"{username}@{DOMAIN}"
    
    email_list = []
    
    try:
        # Kết nối Gmail
        if not MY_GMAIL or not MY_APP_PASS:
            return "Lỗi: Chưa cấu hình Email trong Environment Variables!"

        with MailBox('imap.gmail.com').login(MY_GMAIL, MY_APP_PASS) as mailbox:
            # Lấy 5 mail mới nhất gửi tới target_email
            for msg in mailbox.fetch(AND(to=target_email), limit=5, reverse=True):
                email_list.append({
                    'subject': msg.subject,
                    'body': msg.text[:300], # Lấy 300 ký tự đầu
                    'date_str': msg.date.strftime("%H:%M %d/%m")
                })
    except Exception as e:
        return f"<h3>Lỗi kết nối:</h3><p>{e}</p><p>Vui lòng kiểm tra lại mật khẩu ứng dụng.</p>"

    return render_template_string(HTML_INBOX, emails=email_list, username=username, domain=DOMAIN)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

