from flask import Flask, request, render_template_string, session, redirect, url_for
from imap_tools import MailBox, AND
import os

# C?u hinh l?y t? Bi?n moi tr??ng (©¢? b?o m?t, khong l? pass tren m?ng)
MY_GMAIL    = os.environ.get("MY_GMAIL")
MY_APP_PASS = os.environ.get("MY_APP_PASS")
DOMAIN      = "anhnhat07.online"
SECRET_KEY  = os.environ.get("SECRET_KEY", "mac_dinh_bao_mat")

app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- Ph?n HTML gi? nguyen nh? code tr??c ---
HTML_LOGIN = """... (Copy y nguyen ph?n HTML_LOGIN ? code tr??c vao ©¢ay) ..."""
HTML_INBOX = """... (Copy y nguyen ph?n HTML_INBOX ? code tr??c vao ©¢ay) ..."""
# -------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username'].strip()
        session['user'] = user
        return redirect(url_for('inbox'))
    return render_template_string(HTML_LOGIN)

@app.route('/inbox')
def inbox():
    if 'user' not in session: return redirect(url_for('login'))
    username = session['user']
    target_email = f"{username}@{DOMAIN}"
    email_list = []
    try:
        with MailBox('imap.gmail.com').login(MY_GMAIL, MY_APP_PASS) as mailbox:
            for msg in mailbox.fetch(AND(to=target_email), limit=5, reverse=True):
                email_list.append({
                    'subject': msg.subject,
                    'body': msg.text[:200] + "...",
                    'date_str': msg.date.strftime("%H:%M %d/%m")
                })
    except Exception as e:
        return f"L?i: {e} (Vui long th? l?i sau 30s)"
    return render_template_string(HTML_INBOX, emails=email_list, username=username, domain=DOMAIN)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
