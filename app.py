from flask import Flask, render_template_string, jsonify
from imap_tools import MailBox
import re

app = Flask(__name__)

# --- CẤU HÌNH EMAIL ---
IMAP_SERVER = 'imap.gmail.com'
EMAIL_USER = 'anhnhatlamacc@gmail.com'
EMAIL_PASS = 'hpfyywdpistzzoec' 

# --- GIAO DIỆN WEB ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tool Lấy Code Garena</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { background-color: #121212; color: #00ff00; font-family: monospace; padding: 10px; }
        .box { border: 1px solid #333; background: #1e1e1e; padding: 15px; margin-bottom: 10px; border-radius: 8px; }
        .code { font-size: 40px; color: #ff4444; font-weight: bold; letter-spacing: 3px; margin: 10px 0; display:block; }
        .time { font-size: 11px; color: #888; margin-bottom: 5px; }
        .subject { font-weight: bold; color: #fff; font-size: 14px; }
        .no-code { color: #555; font-size: 12px; font-style: italic; }
    </style>
</head>
<body>
    <h3 style="text-align:center; border-bottom: 1px solid #333; padding-bottom:10px">MAILBOX GARENA (6-8 SỐ)</h3>
    <div id="list">Đang tải...</div>
    
    <script>
        fetch('/api/get_mails')
            .then(r => r.json())
            .then(data => {
                if(data.status == 'success') {
                    let html = '';
                    data.data.forEach(m => {
                        let codeHtml = (m.code != "---") 
                            ? `<span class="code">${m.code}</span>` 
                            : `<span class="no-code">Không tìm thấy mã</span>`;
                            
                        html += `<div class="box" style="${m.code != '---' ? 'border: 1px solid #00ff00' : ''}">
                            <div class="time">${m.date}</div>
                            <div class="subject">${m.subject}</div>
                            ${codeHtml}
                        </div>`;
                    });
                    document.getElementById('list').innerHTML = html;
                } else {
                    document.getElementById('list').innerHTML = "Lỗi: " + data.message;
                }
            })
            .catch(e => document.getElementById('list').innerText = "Lỗi mạng...");
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
        with MailBox(IMAP_SERVER).login(EMAIL_USER, EMAIL_PASS) as mailbox:
            mails = []
            # Lấy 20 mail mới nhất
            for msg in mailbox.fetch(limit=20, reverse=True):
                verification_code = "---"
                
                # Chỉ xử lý mail có chữ Garena hoặc Code/Mã xác minh
                # (Để tránh bắt nhầm mail rác)
                full_text = (msg.subject + " " + msg.text).strip()
                
                # Regex mới: \b\d{6,8}\b 
                # Nghĩa là: Tìm chuỗi số liên tiếp dài từ 6 đến 8 ký tự
                # \b là để đảm bảo nó đứng riêng (không dính vào chữ khác)
                match = re.search(r'\b\d{6,8}\b', full_text)
                if match:
                    verification_code = match.group(0)

                # Chỉ lấy mail có Code hoặc có chữ Garena
                if verification_code != "---" or "Garena" in msg.subject:
                    mails.append({
                        "subject": msg.subject,
                        "date": msg.date_str,
                        "code": verification_code
                    })
            return jsonify({"status": "success", "data": mails})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
