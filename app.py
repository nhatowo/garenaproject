from flask import Flask, request, render_template_string, session, redirect, url_for
from imap_tools import MailBox, AND
import os
import re

# ================= CẤU HÌNH =================
MY_GMAIL    = os.environ.get("MY_GMAIL")
MY_APP_PASS = os.environ.get("MY_APP_PASS")
SECRET_KEY  = os.environ.get("SECRET_KEY", "khoa_bao_mat_mac_dinh")
DOMAIN      = "anhnhat07.online"

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ================= XỬ LÝ LỌC CODE =================
def extract_garena_code(text):
    if not text: return None
    # Bắt chuỗi 8 số (Format mới của Garena)
    match_8 = re.search(r'\b\d{8}\b', text)
    if match_8: return match_8.group(0)
    
    # Bắt chuỗi 6 số (Format cũ)
    match_6 = re.search(r'\b\d{6}\b', text)
    if match_6: return match_6.group(0)

    # Bắt code hỗn hợp
    match_mixed = re.search(r'\b[A-Z0-9]{6,8}\b', text)
    if match_mixed: return match_mixed.group(0)
    return None

# ================= GIAO DIỆN DARK MODE PRO =================
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Garena Tool V3</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --text: #e2e8f0; --accent: #3b82f6; --danger: #ef4444; }
        body { font-family: sans-serif; background: var(--bg); color: var(--text); margin: 0; display: flex; justify-content: center; padding: 10px; }
        .container { width: 100%; max-width: 500px; background: var(--card); padding: 20px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        
        h2 { text-align: center; color: var(--accent); margin-top: 0; }
        input { width: 100%; padding: 12px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; margin-bottom: 10px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: var(--accent); color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
        
        .email-item { background: #334155; border-radius: 10px; padding: 15px; margin-bottom: 15px; border: 1px solid #475569; }
        .meta { font-size: 12px; color: #94a3b8; display: flex; justify-content: space-between; margin-bottom: 10px; }
        .subject { font-weight: bold; font-size: 15px; margin-bottom: 10px; color: white; }
        
        .code-box { background: #fffbeb; color: #d97706; padding: 10px; border-radius: 8px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
        .code-val { font-size: 24px; font-weight: bold; font-family: monospace; letter-spacing: 2px; }
        .copy-btn { width: auto; padding: 5px 15px; font-size: 12px; background: #d97706; margin: 0; }
        
        .original-content { background: white; color: black; padding: 10px; border-radius: 5px; margin-top: 10px; display: none; overflow: auto; }
        .toggle-link { text-align: right; font-size: 12px; color: var(--accent); cursor: pointer; text-decoration: underline; display: block; }
        
        .footer { text-align: center; font-size: 12px; color: #64748b; margin-top: 20px; border-top: 1px solid #334155; padding-top: 10px; }
        .footer a { color: var(--accent); text-decoration: none; display: block; margin: 3px 0; }
    </style>
    <script>
        function copy(text) { navigator.clipboard.writeText(text); alert('Đã copy: ' + text); }
        function toggle(id) {
            var x = document.getElementById(id);
            x.style.display = (x.style.display === 'block') ? 'none' : 'block';
        }
    </script>
</head>
<body>
    <div class="container">
        {{ content|safe }}
        <div class="footer">
            <p>HỖ TRỢ KỸ THUẬT</p>
            <p>Zalo: 0326.265.982</p>
            <a href="https://t.me/AnhNhat07">Telegram: @AnhNhat07</a>
            <a href="https://fb.com/MYNAMEISNHAT07">Facebook: MYNAMEISNHAT07</a>
        </div>
    </div>
</body>
</html>
"""

# ================= ROUTES =================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username'].strip().lower().split('@')[0]
        session['user'] = user
        return redirect(url_for('inbox'))
    return render_template_string(HTML_LAYOUT, content="""
        <h2>GARENA MAIL</h2>
        <form method="post">
            <input name="username" placeholder="Nhập tên tài khoản (ví dụ: nhattaoacc01)" required>
            <button>XEM CODE NGAY</button>
        </form>
    """)

@app.route('/inbox')
def inbox():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    target_email = f"{user}@{DOMAIN}"
    
    try:
        with MailBox('imap.gmail.com').login(MY_GMAIL, MY_APP_PASS) as mailbox:
            # Lấy 10 mail mới nhất gửi đến (Tăng limit lên để không bị sót)
            msgs = [m for m in mailbox.fetch(AND(to=target_email), limit=10, reverse=True)]
            
            if not msgs:
                html = f"<div style='text-align:center; padding:20px'>📭 Chưa có thư nào cho <b>{target_email}</b><br><small>(Hãy kiểm tra mục Spam trong Gmail gốc)</small></div>"
            else:
                html = ""
                for i, msg in enumerate(msgs):
                    # Ưu tiên lấy HTML để hiển thị đẹp, nếu không có thì lấy Text
                    body_view = msg.html if msg.html else msg.text
                    # Lấy text thuần để lọc code
                    text_for_scan = msg.text if msg.text else msg.html
                    
                    code = extract_garena_code(text_for_scan)
                    code_html = f"""<div class="code-box"><span class="code-val">{code}</span><button class="copy-btn" onclick="copy('{code}')">COPY</button></div>""" if code else "<div style='color:#ef4444; font-size:12px'>⚠️ Không tìm thấy code</div>"
                    
                    html += f"""
                    <div class="email-item">
                        <div class="meta"><span>{msg.date.strftime("%H:%M %d/%m")}</span><span>GARENA</span></div>
                        <div class="subject">{msg.subject}</div>
                        {code_html}
                        <span class="toggle-link" onclick="toggle('body-{i}')">▼ Xem nội dung gốc (HTML)</span>
                        <div id="body-{i}" class="original-content">{body_view}</div>
                    </div>
                    """
    except Exception as e:
        html = f"<div style='color:red; text-align:center'>Lỗi kết nối: {e}</div>"

    return render_template_string(HTML_LAYOUT, content=f"""
        <div style="text-align:center; margin-bottom:15px">
            👤 <b>{user}</b> | <a href="/logout" style="color:#ef4444; text-decoration:none">Thoát</a>
        </div>
        <a href="/inbox" style="text-decoration:none"><button style="background:#10b981; margin-bottom:15px">🔄 LÀM MỚI</button></a>
        {html}
    """)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
