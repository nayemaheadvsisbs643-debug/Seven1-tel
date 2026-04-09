import requests
import time
import re
import json
from datetime import datetime
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

BASE_URL = 'http://94.23.120.156'
LOGIN_URL = f'http://94.23.120.156/ints/login'
SIGNIN_URL = f'http://94.23.120.156/ints/signin'
DATA_URL = f'http://94.23.120.156/ints/agent/SMSCDRReports'
USERNAME = 'marufa21'
PASSWORD = 'marufa22'
BOT_TOKEN = '8569166446:AAHJdM-6TEKflyuYZ9d3WGJLTFVQZ_HEpNs'
CHAT_ID = '-1003598958963'

def solve_captcha(html):
    match = re.search(r'(\d+)\s*\+\s*(\d+)', html)
    if match:
        return int(match.group(1)) + int(match.group(2))
    return None

def send_to_telegram(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=data)
    except:
        pass

def login(session):
    try:
        resp = session.get(LOGIN_URL)
        captcha = solve_captcha(resp.text)
        if captcha is None: return False
        payload = {'username': USERNAME, 'password': PASSWORD, 'capt': captcha}
        res = session.post(SIGNIN_URL, data=payload)
        return 'dashboard' in res.text.lower() or 'logout' in res.text.lower() or 'agent' in res.text.lower()
    except:
        return False

def fetch_data(session):
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"{DATA_URL}?fdate1={today} 00:00:00&fdate2={today} 23:59:59&iDisplayLength=-1"
    try:
        res = session.get(url, headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{BASE_URL}/ints/agent/SMSCDRReports"
        }, timeout=15)
        return res.json().get("aaData", [])
    except:
        return []

def get_info(number):
    number = number.replace(' ', '').replace('+', '')
    countries = {
        '880': ('Bangladesh', '🇧🇩'), '92': ('Pakistan', '🇵🇰'), '966': ('Saudi Arabia', '🇸🇦'),
        '7': ('Russia', '🇷🇺'), '44': ('UK', '🇬🇧'), '49': ('Germany', '🇩🇪'), '971': ('UAE', '🇦🇪'),
        '60': ('Malaysia', '🇲🇾'), '62': ('Indonesia', '🇮🇩'), '63': ('Philippines', '🇵🇭'),
        '66': ('Thailand', '🇹🇭'), '84': ('Vietnam', '🇻🇳'), '91': ('India', '🇮🇳'),
        '968': ('Oman', '🇴🇲'), '20': ('Egypt', '🇪🇬'), '234': ('Nigeria', '🇳🇬'),
        '255': ('Tanzania', '🇹🇿'), '94': ('Sri Lanka', '🇱🇰'), '212': ('Morocco', '🇲🇦')
    }
    for code in sorted(countries.keys(), key=len, reverse=True):
        if number.startswith(code): return countries[code]
    return ('Unknown', '🏳️')

def main():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    if not login(session):
        print("Login Failed")
        return

    already_sent = set()
    while True:
        try:
            rows = fetch_data(session)
            if rows:
                for row in rows:
                    msg_time, number, service, message = str(row[0]), str(row[2]), str(row[3]), str(row[5])
                    unique_id = f"{msg_time}_{number}"
                    
                    if unique_id in already_sent:
                        continue

                    otp = re.search(r'\b\d{4,8}\b', message)
                    otp_code = otp.group() if otp else "N/A"
                    c_name, flag = get_info(number)

                    msg = (f"<b>🔔 {flag} {c_name} {service} OTP Received</b>\n\n"
                           f"⏰ <b>Time:</b> {msg_time}\n"
                           f"📲 <b>Number:</b> <code>{number[:6]+'***'+number[-4:]}</code>\n"
                           f"🔐 <b>Code:</b> <code>{otp_code}</code>\n"
                           f"📩 <b>Msg:</b> <pre>{message}</pre>")
                    
                    send_to_telegram(msg)
                    already_sent.add(unique_id)
            
            time.sleep(10)
        except:
            time.sleep(5)
            login(session)

if __name__ == "__main__":
    keep_alive()
    main()
```
