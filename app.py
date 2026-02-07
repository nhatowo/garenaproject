from flask import Flask, render_template_string, jsonify
from imap_tools import MailBox
import re

app = Flask(__name__)

# --- CẤU HÌNH ---
IMAP_SERVER = 'imap.gmail.com'
EMAIL_USER = 'anhnhatlamacc@gmail.com'
EMAIL_PASS = 'hpfyywdpistzzoec' 

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Garena Code</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { background: #000; color: #0f0; font-family: monospace; padding: 10px; }
        .box { border: 1px solid #444; margin-bottom: 10px; padding: 10px; border-radius: 5px; }
        .code { font-size: 35px; color: #ff3333; font-weight: bold; display: block; margin: 5px 0; }
        .subject { color: #fff; font-weight: bold; }
        .time { color: #666; font-size: 10px; }
        #status { color: yellow; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 10px;}
    </style>
</head>
<body>
    <div id="status">Đang kết nối Server...</div>
    <div id="list"></div>
    
    <script>
        const statusDiv = document.getElementById('status');
        const listDiv = document.getElementById('list');

        statusDiv.innerText = "Đang gọi API...";
        
        fetch('/api/get_mails')
            .then(response => {
                statusDiv.innerText = "Đã nhận phản hồi từ Server...";
                return response.json();
            })
            .then(data => {
                if(data.status == 'success') {
                    statusDiv.innerText = "Đã tải xong! (" + data.data.length + " mail)";
                    statusDiv.style.color = "#0f0";
                    
                    let html = '';
                    if(data.data.length === 0) {
                        html = '<div style="color:#777">Hộp thư trống hoặc không tìm thấy Garena</div>';
                    } else {
                        data.data.forEach(m => {
                            // Hiển thị code to đùng
                            let codeDisplay = (m.code != "---") 
                                ? `<span class="code">${m.code}</span>` 
                                : `<span style="color:#555; font-size:12px">Không có mã</span>`;
                                
                            html += `<div class="box">
                                <div class="time">${m.date}</div>
                                <div class="subject">${m.subject}</div>
                                ${codeDisplay}
                            </div>`;
                        });
                    }
                    listDiv.innerHTML = html;
                } else {
                    statusDiv.innerText = "Lỗi Backend: " + data.message;
                    statusDiv.style.color = "red";
                }
            })
            .catch(error => {
                statusDiv.innerText = "Lỗi Mạng/JS: " + error;
                statusDiv.style.color = "red";
            });
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
                code = "---"
                # Gộp tiêu đề + nội dung, chuyển hết về chữ thường để tìm cho dễ
                full_text = (str(msg.subject) + " " + str(msg.text) + " " + str(msg.html)).lower()
                
                # 1. Lọc Mail: Chỉ lấy mail có chữ "garena" hoặc "code"
                if "garena" in full_text or "code" in full_text or "mã" in full_text:
                    
                    # 2. Tìm Code: 6 đến 8 số
                    # Regex này tìm số nằm giữa các ký tự không phải số
                    match = re.search(r'(?<!\d)\d{6,8}(?!\d)', full_text)
                    if match:
                        code = match.group(0)
                    
                    # Thêm vào danh sách
                    mails.append({
                        "subject": msg.subject,
                        "date": msg.date_str,
                        "code": code
                    })
            return jsonify({"status": "success", "data": mails})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
