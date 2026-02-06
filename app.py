from flask import Flask, render_template_string, jsonify
from imap_tools import MailBox
import re

app = Flask(__name__)

# --- CẤU HÌNH EMAIL ---
IMAP_SERVER = 'mail.anhnhat07.online'
EMAIL_USER = 'admin@anhnhat07.online'
EMAIL_PASS = 'hpfy ywdp istz zoec' # Pass App 16 ký tự

# --- GIAO DIỆN HTML (NHÚNG TRỰC TIẾP VÀO ĐÂY) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AnhNhat07 Mailbox</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script>
        tailwind.config = { darkMode: 'class', theme: { extend: { colors: { primary: 'var(--primary)', bg: 'var(--bg)', surface: 'var(--surface)', text: 'var(--text)', } } } }
    </script>
    <style>
        :root { --primary: #3b82f6; --bg: #f3f4f6; --surface: #ffffff; --text: #111827; }
        [data-theme="dark"] { --primary: #60a5fa; --bg: #111827; --surface: #1f2937; --text: #f9fafb; }
        [data-theme="matrix"] { --primary: #00ff00; --bg: #000000; --surface: #0a0a0a; --text: #00ff00; font-family: monospace; }
        body { background-color: var(--bg); color: var(--text); transition: all 0.3s; }
        .card { background-color: var(--surface); }
    </style>
</head>
<body class="min-h-screen p-4 md:p-8">
    <div class="max-w-4xl mx-auto">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl md:text-3xl font-bold"><i class="fas fa-envelope text-primary"></i> BOX.<span class="text-primary">ANHNHAT07</span></h1>
            <select onchange="document.documentElement.setAttribute('data-theme', this.value)" class="p-2 rounded card border border-gray-600 outline-none text-sm cursor-pointer">
                <option value="dark">🌙 Dark</option>
                <option value="light">☀️ Light</option>
                <option value="matrix">💻 Matrix</option>
            </select>
        </div>

        <div id="garena-box" class="hidden mb-6 card p-6 rounded-xl border-l-4 border-red-500 shadow-lg animate-pulse">
            <div class="flex justify-between items-start">
                <div>
                    <p class="text-red-400 text-sm font-bold uppercase tracking-widest">Garena Code Detected</p>
                    <div id="live-code" class="text-5xl md:text-6xl font-black text-red-500 mt-2 tracking-widest">---</div>
                    <p id="live-time" class="text-xs mt-2 opacity-70">Vừa xong</p>
                </div>
                <i class="fas fa-fire text-red-500 text-4xl opacity-50"></i>
            </div>
        </div>

        <div class="flex justify-between items-center mb-4">
            <h3 class="font-bold opacity-80">Inbox (Auto-refresh 5s)</h3>
            <span id="status" class="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400">Checking...</span>
        </div>
        <div id="mail-list" class="space-y-3">
            <div class="text-center py-10 opacity-50">Đang tải dữ liệu...</div>
        </div>
    </div>

    <script>
        async function fetchMails() {
            const status = document.getElementById('status');
            try {
                const res = await fetch('/api/get_mails');
                const json = await res.json();
                
                if (json.status === 'success') {
                    status.innerText = "Live";
                    status.className = "text-xs px-2 py-1 rounded bg-green-500/20 text-green-400";
                    
                    const list = document.getElementById('mail-list');
                    list.innerHTML = '';
                    let foundCode = false;

                    json.data.forEach(mail => {
                        if (mail.is_garena && mail.code !== "---" && !foundCode) {
                            document.getElementById('garena-box').classList.remove('hidden');
                            document.getElementById('live-code').innerText = mail.code;
                            document.getElementById('live-time').innerText = mail.date;
                            foundCode = true;
                        }
                        
                        const item = `
                            <div class="card p-4 rounded-lg shadow border-l-4 ${mail.is_garena ? 'border-red-500' : 'border-transparent'} hover:brightness-110 transition cursor-pointer">
                                <div class="flex justify-between">
                                    <div class="font-bold ${mail.is_garena ? 'text-red-400' : 'text-primary'}">${mail.subject}</div>
                                    <div class="text-xs opacity-50 whitespace-nowrap ml-2">${mail.date}</div>
                                </div>
                                <div class="text-sm opacity-60 mt-1 truncate">${mail.body}</div>
                                <div class="text-xs opacity-40 mt-2">From: ${mail.from}</div>
                            </div>`;
                        list.innerHTML += item;
                    });
                } else {
                    status.innerText = "Lỗi Backend";
                    status.className = "text-xs px-2 py-1 rounded bg-red-500/20 text-red-400";
                }
            } catch (e) { 
                status.innerText = "Lỗi Mạng";
                status.className = "text-xs px-2 py-1 rounded bg-red-500/20 text-red-400";
            }
        }
        setInterval(fetchMails, 5000);
        fetchMails();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # Dùng hàm này để render cái chuỗi HTML dài ngoằng ở trên
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/get_mails')
def get_mails():
    try:
        with MailBox(IMAP_SERVER).login(EMAIL_USER, EMAIL_PASS) as mailbox:
            mails = []
            for msg in mailbox.fetch(limit=15, reverse=True):
                is_garena = False
                verification_code = "---"
                
                if "Garena" in msg.subject or "Garena" in msg.text:
                    is_garena = True
                    match = re.search(r'\\b\\d{6}\\b', msg.text)
                    if match:
                        verification_code = match.group(0)

                mails.append({
                    "subject": msg.subject,
                    "from": msg.from_,
                    "date": msg.date_str,
                    "body": msg.text[:100] + "...", 
                    "is_garena": is_garena,
                    "code": verification_code
                })
            return jsonify({"status": "success", "data": mails})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
