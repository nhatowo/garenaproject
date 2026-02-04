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
    # Bắt code từ 6 đến 8 số (Garena mới + cũ)
    match_digits = re.search(r'\b\d{6,8}\b', text)
    if match_digits: return match_digits.group(0)
    # Bắt code hỗn hợp chữ số
    match_mixed = re.search(r'\b[A-Z0-9]{6,8}\b', text)
    if match_mixed: return match_mixed.group(0)
    return None

# ================= GIAO DIỆN DARK MODE =================
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Garena Tool - AnhNhat07</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        /* CẤU HÌNH MÀU DARK MODE */
        :root {
            --bg-color: #0f172a;       /* Nền đen xanh đậm */
            --card-bg: #1e293b;        /* Nền hộp chứa */
            --text-main: #e2e8f0;      /* Chữ trắng sáng */
            --text-sub: #94a3b8;       /* Chữ xám nhạt */
            --accent: #3b82f6;         /* Màu xanh chủ đạo */
            --accent-hover: #2563eb;
            --code-bg: #334155;        /* Nền chứa mã code */
            --code-text: #fbbf24;      /* Mã code màu vàng nổi bật */
            --border: #334155;
        }

        body { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: var(--bg-color); color: var(--text-main); margin: 0; display: flex; justify-content: center; min-height: 100vh; }
        
        .container { 
            width: 100%; max-width: 500px; 
            background: var(--card-bg); 
            padding: 25px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.5); 
            display: flex; flex-direction: column; 
            min-height: 100vh; 
        }
        
        @media (min-width: 600px) { 
            .container { min-height: auto; margin-top: 30px; border-radius: 16px; height: fit-content; border: 1px solid var(--border); } 
        }
        
        h2 { text-align: center; color: var(--accent); margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; }
        .sub-title { text-align: center; color: var(--text-sub); font-size: 13px; margin-bottom: 25px; }

        input { 
            width: 100%; padding: 15px; 
            background: #0f172a; border: 1px solid var(--border); 
            color: white; border-radius: 8px; box-sizing: border-box; 
            font-size: 16px; outline: none; transition: 0.3s;
        }
        input:focus { border-color: var(--accent); box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3); }
        
        button { 
            width: 100%; padding: 15px; margin-top: 15px;
            background: var(--accent); color: white; 
            border: none; border-radius: 8px; 
            cursor: pointer; font-weight: bold; font-size: 16px; 
            transition: 0.3s;
        }
        button:hover { background: var(--accent-hover); transform: translateY(-2px); }
        
        /* EMAIL ITEM STYLE */
        .email-item { background: #263344; border-radius: 10px; padding: 15px; margin-bottom: 15px; border: 1px solid var(--border); }
        .email-meta { font-size: 12px; color: var(--text-sub); display: flex; justify-content: space-between; margin-bottom: 8px; }
        .email-subject { font-weight: bold; color: white; font-size: 15px; margin-bottom: 12px; border-bottom: 1px dashed var(--border); padding-bottom: 8px;}
        
        /* CODE BOX */
        .code-box-container { display: flex; align-items: center; background: var(--code-bg); padding: 10px; border-radius: 6px; margin-bottom: 10px; border: 1px solid #475569; }
        .code-value { font-size: 26px; font-weight: bold; color: var(--code-text); letter-spacing: 3px; flex-grow: 1; text-align: center; font-family: monospace; }
        .copy-btn { width: auto; padding: 6px 15px; font-size: 13px; background: var(--accent); margin-left: 10px; margin-top: 0; }
        
        /* FOOTER INFO */
        .footer-info { margin-top: 30px; padding-top: 20px; border-top: 1px solid var(--border); text-align: center; font-size: 14px; color: var(--text-sub); }
        .footer-info p { margin: 5px 0; }
        .footer-info b { color: var(--accent); }
        .contact-link { color: var(--text-main); text-decoration: none; display: block; margin: 5px 0; transition: 0.2s;}
        .contact-link:hover { color: var(--accent); }

        /* NỘI DUNG ẨN */
        .original-body { font-size: 13px; color: #cbd5e1; background: #0f172a; padding: 10px; border-radius: 4px; margin-top: 10px; display: none; word-break: break-word; border: 1px solid var(--border); }
        .toggle-body { font-size: 13px; color: var(--accent); cursor: pointer; text-align: right; display: block; margin-top: 5px; }
        
        .empty { text-align: center; color: var(--text-sub); margin-top: 40px; }
        .refresh-btn { background: #10b981; margin-bottom: 20px; margin-top: 0; }
        .refresh-btn:hover { background: #059669; }
        .logout { color: #ef4444; text-decoration: none; font-size: 14px; font-weight: bold; }
    </style>
    <script>
        function copyText(text) {
            navigator.clipboard.writeText(text).then(function() {
                alert('Đã copy mã: ' + text);
            }, function(err) {
                prompt("Copy thủ công:", text);
            });
        }
        function toggleBody(id) {
            var x = document.getElementById(id);
            if (x.style.display === "none") {
                x.style.display = "block";
                document.getElementById('btn-'+id).innerText = "▲ Thu gọn";
            } else {
                x.style.display = "none";
                document.getElementById('btn-'+id).innerText = "▼ Xem nội dung gốc";
            }
        }
    </script>
</head>
<body>
    <div class="container">
        {{ content|safe }}
        
        <div class="footer-info">
            <p style="text-transform: uppercase; font-weight: bold; color: #94a3b8; font-size: 12px; margin-bottom: 10px;">Liên hệ Hỗ Trợ</p>
            <p>Zalo: <b>0326.265.982</b></p>
            <a href="https://t.me/AnhNhat07" target="_blank" class="contact-link">Telegram: <b>@AnhNhat07</b></a>
            <a href="https://fb.com/MYNAMEISNHAT07" target="_blank" class="contact-link">Facebook: <b>MYNAMEISNHAT07</b></a>
        </div>
    </div>
</body>
</html>
"""

# ================= ROUTES =================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username'].strip().lower()
        if '@' in user: user = user.split('@')[0]
        session['user'] = user
        return redirect(url_for('inbox'))
        
    form_html = """
        <h2>Garena Tools</h2>
        <div class="sub-title">Hệ thống lấy mã xác minh tự động siêu tốc</div>
        <form method="post">
            <input type="text" name="username" placeholder="Nhập tên tài khoản (Ví dụ: nhattaoacc01)" required>
            <button type="submit">🔍 CHECK CODE NGAY</button>
        </form>
    """
    return render_template_string(HTML_LAYOUT, content=form_html)

@app.route('/inbox')
def inbox():
    if 'user' not in session: return redirect(url_for('login'))
    
    username = session['user']
    target_email = f"{username}@{DOMAIN}"
    
    email_html = ""
    try:
        if not MY_GMAIL or not MY_APP_PASS: return "Lỗi cấu hình!"

        with MailBox('imap.gmail.com').login(MY_GMAIL, MY_APP_PASS) as mailbox:
            msgs = [m for m in mailbox.fetch(AND(to=target_email), limit=5, reverse=True)]
            
            if not msgs:
                email_html = """
                <div class="empty">
                    <p style="font-size: 40px; margin: 0;">📭</p>
                    <p>Chưa có thư nào gửi đến<br><b style="color: #e2e8f0">%s</b></p>
                </div>
                """ % target_email
            else:
                for index, msg in enumerate(msgs):
                    body_text = msg.text or msg.html or ""
                    extracted_code = extract_garena_code(body_text)
                    
                    code_display = ""
                    if extracted_code:
                        code_display = f"""
                        <div class="code-box-container">
                            <span class="code-value">{extracted_code}</span>
                            <button class="copy-btn" onclick="copyText('{extracted_code}')">COPY</button>
                        </div>
                        """
                    else:
                        code_display = "<div style='color:#ef4444; font-size:12px; margin-bottom:5px; font-style: italic;'>⚠️ Không tìm thấy mã trong thư này</div>"

                    body_id = f"body-{index}"
                    btn_id = f"btn-body-{index}"
                    
                    email_html += f"""
                    <div class="email-item">
                        <div class="email-meta">
                            <span>{msg.date.strftime("%H:%M %d/%m")}</span>
                            <span style="color:#3b82f6; font-weight:bold;">GARENA</span>
                        </div>
                        <div class="email-subject">{msg.subject}</div>
                        
                        {code_display}
                        
                        <span id="{btn_id}" class="toggle-body" onclick="toggleBody('{body_id}')">▼ Xem nội dung gốc</span>
                        <div id="{body_id}" class="original-body">
                            {body_text[:1000]}
                        </div>
                    </div>
                    """
    except Exception as e:
        email_html = f"<p style='color:#ef4444; text-align:center'>Lỗi kết nối: {e}</p>"

    content = f"""
        <div class="email-meta" style="justify-content:center; margin-bottom:15px; border-bottom: 1px solid #334155; padding-bottom: 10px;">
            <span style="font-size: 16px;">👤 <b>{username}</b></span> 
            <a href="/logout" class="logout" style="margin-left: 15px;">Thoát ➔</a>
        </div>
        <a href="/inbox" style="text-decoration:none">
            <button class="refresh-btn">🔄 LÀM MỚI HỘP THƯ</button>
        </a>
        {email_html}
    """
    return render_template_string(HTML_LAYOUT, content=content)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
