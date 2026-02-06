from flask import Flask, render_template, jsonify
from imap_tools import MailBox
import re

app = Flask(__name__)

# --- CẤU HÌNH EMAIL CỦA NHẬT (CHUẨN SUBDOMAIN) ---
IMAP_SERVER = 'mail.anhnhat07.online'  # Đã đổi theo ý Nhật
EMAIL_USER = 'admin@anhnhat07.online'  # Hoặc user nào Nhật dùng để nhận code
EMAIL_PASS = 'Mat_Khau_Email_Cua_Nhat' # Nhớ điền pass chuẩn nhé

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_mails')
def get_mails():
    try:
        # Kết nối vào hòm thư
        with MailBox(IMAP_SERVER).login(EMAIL_USER, EMAIL_PASS) as mailbox:
            mails = []
            # Lấy 10 mail mới nhất (để tốc độ load siêu nhanh)
            for msg in mailbox.fetch(limit=10, reverse=True):
                is_garena = False
                verification_code = "---"
                
                # Logic bắt code Garena
                if "Garena" in msg.subject or "Garena" in msg.text:
                    is_garena = True
                    # Tìm chuỗi 6 số (Ví dụ: 123456)
                    match = re.search(r'\b\d{6}\b', msg.text)
                    if match:
                        verification_code = match.group(0)

                mails.append({
                    "subject": msg.subject,
                    "from": msg.from_,
                    "date": msg.date_str,
                    "body": msg.text[:80] + "...", 
                    "is_garena": is_garena,
                    "code": verification_code
                })
            return jsonify({"status": "success", "data": mails})
    except Exception as e:
        print(f"Lỗi IMAP: {e}") # In lỗi ra terminal để Nhật dễ debug
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    # Chạy ở port 5000
    app.run(debug=True, port=5000)
# ... (Phần code trên giữ nguyên) ...

if __name__ == '__main__':
    # Chạy dưới dạng module (cho máy tính cá nhân)
    app.run(debug=True)
    
# Render sẽ không chạy vào dòng if __main__ này, nó sẽ import app trực tiếp

