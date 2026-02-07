from flask import Flask, render_template_string, jsonify
from imap_tools import MailBox
import re

app = Flask(__name__)

# --- CẤU HÌNH EMAIL (QUAN TRỌNG) ---
# Vì mail gốc là Gmail, nên bắt buộc dùng server này:
IMAP_SERVER = 'imap.gmail.com'
EMAIL_USER = 'anhnhatlamacc@gmail.com'
EMAIL_PASS = 'hpfy ywdp istz zoec' # Mật khẩu ứng dụng cũ của bạn

# --- GIAO DIỆN WEB (ĐỂ XEM TRÊN ĐIỆN THOẠI) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tool Lấy Code Garena</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { background-color: #000; color: #0f0; font-family: monospace; padding: 15px; }
        .box { border: 1px solid #333; padding: 10px; margin-bottom: 10px; border-radius: 5px; }
        .code { font-size: 32px; color: #ff0000; font-weight: bold; letter-spacing: 3px; }
        .time { font-size: 10px; color: #666; }
        h2 { text-align: center; border-bottom: 2px solid #0f0; padding-bottom: 10px; }
    </style>
</head>
<body>
    <h2>TRẠM THU PHÁT SÓNG</h2>
    <div id="list">Đang tải dữ liệu...</div>
    
    <script>
        fetch('/api/get_mails')
            .then(r => r.json())
            .then(data => {
                if(data.status == 'success') {
                    let html = '';
                    data.data.forEach(m => {
                        html += `<div class="box">
                            <div class="time">${m.date}</div>
                            <div>${m.subject}</div>
                            ${m.is_garena && m.code != "---" ? '<div class="code">' + m.code + '</div>' : ''}
                        </div>`;
                    });
                    document.getElementById('list').innerHTML = html;
                } else {
                    document.getElementById('list').innerHTML = "Lỗi: " + data.message;
                }
            })
            .catch(e => document.getElementById('list').innerText = "Lỗi mạng!");
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/get_mails')
def get_mails():
    try:
        # Kết nối vào Gmail
        with MailBox(IMAP_SERVER).login(EMAIL_USER, EMAIL_PASS) as mailbox:
            mails = []
            # Lấy 10 mail mới nhất
            for msg in mailbox.fetch(limit=10, reverse=True):
                is_garena = False
                verification_code = "---"
                
                # Logic tìm code Garena
                if "Garena" in msg.subject or "Garena" in msg.text:
                    is_garena = True
                    match = re.search(r'\\b\\d{6}\\b', msg.text)
                    if match:
                        verification_code = match.group(0)

                mails.append({
                    "subject": msg.subject,
                    "date": msg.date_str,
                    "is_garena": is_garena,
                    "code": verification_code
                })
            return jsonify({"status": "success", "data": mails})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
