import os
import sqlite3
import random
import smtplib
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, redirect, url_for, session, render_template_string

# --- LOGGING SYSTEM ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MATRIX_PLATFORM")

app = Flask(__name__)
app.secret_key = "GLOBAL_MATRIX_SUPER_SECRET_KEY_2026_EXCLUSIVE"

# --- SMTP CONFIGURATION (CONFIGURED WITH YOUR BREVO API KEY) ---
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SENDER_EMAIL = "Globalmatrixteam.com@gmail.com" 
SENDER_APP_PASSWORD = "xsmtpsib-bc1418aaa30eddf05bdadad2344c9f3290cbae0c3714bfd6ee51e822949180ce-vc7c469V1mDlM75C" 

def send_verification_email(receiver_email, otp_code, purpose="Registration"):
    server = None
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Global Matrix <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"🔑 Your OTP Verification Code: {otp_code}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0b0c10; padding: 20px; color: #ffffff;">
            <div style="max-width: 400px; margin: 0 auto; background: #1f2026; border: 2px solid #ff0055; border-radius: 16px; padding: 25px; text-align: center;">
                <h2 style="color: #00f0ff;">GLOBAL MATRIX</h2>
                <hr style="border: 0; height: 1px; background: rgba(0,240,255,0.3); margin-bottom: 20px;">
                <p style="font-size: 16px;">Your OTP Verification Code for {purpose} is:</p>
                <div style="font-size: 32px; font-weight: bold; color: #ffffff; letter-spacing: 4px; padding: 12px; background: #0b0c10; border: 1px solid #00f0ff; border-radius: 10px; margin: 20px 0;">
                    {otp_code}
                </div>
                <p style="color: #a0a0a5; font-size: 12px;">This code expires in 10 minutes. Do not share it with anyone.</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        logger.info(f"Connecting to Brevo Relay Service ({SMTP_SERVER}) via Port {SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20)
        
        server.ehlo()
        logger.info("Initializing Secure TLS Session...")
        server.starttls()
        server.ehlo()
        
        logger.info("Authenticating Master Brevo Credentials...")
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        
        logger.info("Transmitting Encrypted Email Payload...")
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        
        server.quit()
        logger.info(f"✅ OTP Successfully sent to {receiver_email} via Brevo SMTP Gateway!")
        return True
    except Exception as e:
        logger.error(f"❌ DETAILED SMTP ERROR DETAILS: {str(e)}")
        if server:
            try:
                server.close()
            except:
                pass
        return False

# --- SUPPORTED MALAYSIAN PAYMENT CHANNELS ---
MALAYSIAN_BANKS = [
    "Touch 'n Go eWallet", 
    "USDT (TRC-20) Crypto Network", 
    "Maybank (Malayan Banking Berhad)", 
    "CIMB Bank Berhad", 
    "Public Bank Berhad", 
    "RHB Bank Berhad", 
    "Hong Leong Bank Berhad", 
    "Bank Islam Malaysia"
]

# --- DATABASE SCHEMATIC INITIALIZATION ---
def init_db():
    try:
        conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, 
                password TEXT, 
                balance REAL, 
                liquidation REAL, 
                active_level TEXT, 
                ref_code TEXT, 
                referred_by TEXT
            )
        """)
        
        cursor.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS deposits (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, bank TEXT, name TEXT, trx_id TEXT, amount REAL, status TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS checkins (username TEXT, date TEXT, PRIMARY KEY (username, date))")
        cursor.execute("CREATE TABLE IF NOT EXISTS ad_logs (username TEXT, ad_id TEXT, date TEXT, PRIMARY KEY (username, ad_id, date))")
        cursor.execute("CREATE TABLE IF NOT EXISTS lucky_spins (username TEXT, date TEXT, prize REAL, PRIMARY KEY (username, date))")
        cursor.execute("CREATE TABLE IF NOT EXISTS withdrawals (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, bank TEXT, account TEXT, amount REAL, status TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS ad_campaigns (id INTEGER PRIMARY KEY AUTOINCREMENT, advertiser_email TEXT, video_url TEXT, target_views INTEGER, trx_id TEXT, status TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS support_tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, subject TEXT, message TEXT, reply TEXT, status TEXT)")
        
        configs = [
            ('ad1_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad1_reward', '3.00'),
            ('ad2_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad2_reward', '2.30'),
            ('ad3_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad3_reward', '4.50'),
            ('ad4_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad4_reward', '1.50'),
            ('ad5_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad5_reward', '2.00'),
            ('tng_scanner_url', 'https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg'),
            ('usdt_address', 'TYcc7p18K2YnQp87bXzNWXAsgWqR54321A'),
            ('system_announcement', '⚠️ ANNOUNCEMENT: System optimized. Fast deposits via Touch n Go active.'),
            ('vip1_income', '2.00'), ('vip2_income', '15.00'), ('vip3_income', '50.00'),
            ('vip2_req', '100.00'), ('vip3_req', '300.00'),
            ('tier1_bonus_pct', '10.0'), ('tier2_bonus_pct', '5.0'), ('tier3_bonus_pct', '2.0')
        ]
        
        for key, val in configs:
            cursor.execute("INSERT OR IGNORE INTO system_config VALUES (?, ?)", (key, val))
            
        cursor.execute("INSERT OR IGNORE INTO users VALUES ('Mani', 'MANI2662', 0.0, 0.0, 'OWNER', 'MASTER', '')")
        conn.commit()
        conn.close()
    except Exception as e:
        logger.critical(f"Database Init Error: {e}")

init_db()

def query_db(query, args=(), one=False, commit=False):
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    conn.execute("PRAGMA busy_timeout = 30000")
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            conn.close()
            return True
        rv = cursor.fetchall()
        conn.close()
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        logger.error(f"DB Query Exception: {e}")
        conn.close()
        return None if one else []

def credit_multi_tier_commissions(user, base_reward):
    try:
        t1_pct = float(query_db("SELECT value FROM system_config WHERE key='tier1_bonus_pct'", one=True)[0]) / 100.0
        t2_pct = float(query_db("SELECT value FROM system_config WHERE key='tier2_bonus_pct'", one=True)[0]) / 100.0
        t3_pct = float(query_db("SELECT value FROM system_config WHERE key='tier3_bonus_pct'", one=True)[0]) / 100.0

        p1 = query_db("SELECT referred_by FROM users WHERE username=?", (user,), one=True)
        if not p1 or not p1[0]: return
        p1 = p1[0].strip()
        if p1: query_db("UPDATE users SET balance = balance + ? WHERE username=?", (base_reward * t1_pct, p1), commit=True)
        
        p2 = query_db("SELECT referred_by FROM users WHERE username=?", (p1,), one=True)
        if not p2 or not p2[0]: return
        p2 = p2[0].strip()
        if p2: query_db("UPDATE users SET balance = balance + ? WHERE username=?", (base_reward * t2_pct, p2), commit=True)
        
        p3 = query_db("SELECT referred_by FROM users WHERE username=?", (p2,), one=True)
        if not p3 or not p3[0]: return
        p3 = p3[0].strip()
        if p3: query_db("UPDATE users SET balance = balance + ? WHERE username=?", (base_reward * t3_pct, p3), commit=True)
    except Exception as e:
        logger.error(f"Commission Distribution Mismatch: {e}")

def sync_user_vip_tier(username):
    try:
        total_approved = query_db("SELECT SUM(amount) FROM deposits WHERE username=? AND status='Approved'", (username,), one=True)
        total_dep = total_approved[0] if total_approved and total_approved[0] else 0.0
        v2_req = float(query_db("SELECT value FROM system_config WHERE key='vip2_req'", one=True)[0])
        v3_req = float(query_db("SELECT value FROM system_config WHERE key='vip3_req'", one=True)[0])
        
        new_tier = "👑 VIP LEVEL 1"
        if total_dep >= v3_req: new_tier = "👑 VIP LEVEL 3"
        elif total_dep >= v2_req: new_tier = "👑 VIP LEVEL 2"
            
        query_db("UPDATE users SET active_level=?, liquidation=? WHERE username=?", (new_tier, total_dep * 0.15, username), commit=True)
    except Exception as e:
        logger.error(f"VIP Synchronization Fault: {e}")

def generate_live_activity_logs():
    users_pool = ["Zaki_TNG", "Aiman_99", "Siti_Aminah", "Raju_Bitcoin", "Michelle_KL", "Chao_Matrix", "Wong_Settle"]
    actions = ["claimed Video Reward RM4.50", "withdrew RM250.00 via Touch 'n Go", "unlocked VIP Level 2", "won RM10.00 on Lucky Wheel", "completed Daily Check-In"]
    return " &nbsp;&nbsp;&nbsp;&nbsp;||&nbsp;&nbsp;&nbsp;&nbsp; ".join([f"⚡ {random.choice(users_pool)} {random.choice(actions)}" for _ in range(10)])

BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GLOBAL MATRIX ENGINE</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;900&family=Rajdhani:wght@600;700&display=swap');
        html, body { background-color: #0b0c10 !important; color: #ffffff !important; font-family: 'Orbitron', sans-serif !important; margin: 0; padding: 0; }
        .wrapper { max-width: 450px; margin: 0 auto; padding: 10px; padding-bottom: 90px; }
        .running-header-container { width: 100%; background: #12131a; padding: 12px 0; border-bottom: 2px solid #ff0055; text-align:center; }
        .running-text { font-size: 13px; font-weight: 900; color: #00f0ff; letter-spacing: 2px; }
        .fomo-ticker-container { width: 100%; background: linear-gradient(90deg, #ff0055 0%, #a100ff 100%); padding: 6px 0; margin-bottom: 20px; text-align: center; }
        .fomo-text { font-size: 14px; color: #ffffff; }
        .brand-title { text-align: center; font-size: 38px; font-weight: 900; color: #ffffff; margin-top: 10px; letter-spacing: 3px; }
        .announcement-box { background: #1a090d; border: 2px solid #ff0055; border-radius: 14px; padding: 15px; font-size: 14px; color: #ff3377 !important; font-weight: 800; margin-bottom: 20px; text-align: center; }
        .metric-card-box { background: linear-gradient(135deg, #12131a 0%, #1f2026 100%); border: 2px solid #00f0ff; border-radius: 20px; padding: 25px 20px; text-align: center; margin-bottom: 20px; }
        input, select, textarea { width: 100%; background-color: #12131a !important; color: #ffffff !important; border: 2px solid #ff0055 !important; border-radius: 12px !important; padding: 12px !important; font-size: 14px; margin-bottom: 15px; box-sizing: border-box; }
        button, .btn-link { display: block; background: linear-gradient(135deg, #a100ff 0%, #ff0055 100%) !important; color: #ffffff !important; font-family: 'Orbitron', sans-serif !important; font-size: 15px !important; font-weight: 900; border-radius: 14px !important; width: 100% !important; padding: 14px !important; border: none !important; text-align: center; text-decoration: none; box-sizing: border-box; cursor: pointer; margin-bottom: 10px; }
        .custom-matrix-box-cyan { background: #12131a; border: 2px solid #00f0ff; border-radius: 14px; padding: 16px; margin: 15px 0; }
        .custom-matrix-box-pink { background: #12131a; border: 2px solid #ff0055; border-radius: 14px; padding: 16px; margin: 15px 0; }
        .nav-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 450px; background: #0b0c10; padding: 8px; box-sizing: border-box; border-top: 2px solid #ff0055; z-index: 999; }
        .nav-grid button { font-size: 10px !important; padding: 10px 2px !important; margin-bottom: 0; }
        .admin-nav-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-bottom: 15px; }
        .admin-nav-grid button { font-size: 11px !important; padding: 8px 4px !important; }
        .alert-success { background: #09211a; border: 1px solid #00ffaa; color: #00ffaa; padding: 12px; border-radius: 10px; margin-bottom: 15px; text-align: center; }
        .alert-error { background: #2b0c11; border: 1px solid #ff0055; color: #ff0055; padding: 12px; border-radius: 10px; margin-bottom: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="running-header-container">
        <marquee class="running-text" scrollamount="5">⚡ GLOBAL MATRIX ENGINE SYSTEM ONLINE</marquee>
    </div>
    <div class="fomo-ticker-container">
        <marquee class="fomo-text" scrollamount="4">{{ dynamic_ticker|safe }}</marquee>
    </div>
    <div class="wrapper">
        {% if msg_success %}<div class="alert-success">{{ msg_success }}</div>{% endif %}
        {% if msg_error %}<div class="alert-error">{{ msg_error }}</div>{% endif %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
        
    announcement = query_db("SELECT value FROM system_config WHERE key='system_announcement'", one=True)[0]
    panel = request.args.get('panel', 'Overview' if not session.get('is_admin', False) else 'Admin_Deposits')

    user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (session['current_user'],), one=True)
    wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (0.00, 0.00, '👑 VIP LEVEL 1', 'MX00')
    
    tng_scanner_url = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)[0]
    usdt_address = query_db("SELECT value FROM system_config WHERE key='usdt_address'", one=True)[0]
    
    v1_inc = float(query_db("SELECT value FROM system_config WHERE key='vip1_income'", one=True)[0])
    v2_inc = float(query_db("SELECT value FROM system_config WHERE key='vip2_income'", one=True)[0])
    v3_inc = float(query_db("SELECT value FROM system_config WHERE key='vip3_income'", one=True)[0])
    v2_req = float(query_db("SELECT value FROM system_config WHERE key='vip2_req'", one=True)[0])
    v3_req = float(query_db("SELECT value FROM system_config WHERE key='vip3_req'", one=True)[0])
    
    today_date = time.strftime("%Y-%m-%d")
    has_approved_deposit = bool(query_db("SELECT id FROM deposits WHERE username=? AND status='Approved'", (session['current_user'],), one=True))

    success_banner = session.pop('success_flash', '')
    error_banner = session.pop('error_flash', '')
    live_feed = generate_live_activity_logs()

    if session.get('is_admin', False):
        content_html = f"""
        <h4 style='color:#00f0ff; text-align:center;'>🛡️ MASTER ADMINISTRATION PANEL</h4>
        <div class="admin-nav-grid">
            <button onclick="window.location.href='/?panel=Admin_Deposits'">📥 DEPOSIT REQUESTS</button>
            <button onclick="window.location.href='/?panel=Admin_Configs'">⚙️ SCANNERS & LINKS</button>
            <button onclick="window.location.href='/?panel=Admin_Users'">👤 USER MANUAL BALANCES</button>
            <button onclick="window.location.href='/?panel=Admin_Withdraws'">💰 WITHDRAWAL VERIFY</button>
            <button onclick="window.location.href='/?panel=Admin_Campaigns'">📢 ADS MANAGEMENT</button>
            <button onclick="window.location.href='/?panel=Admin_Tickets'">🎫 HELP DESK TICKETS</button>
        </div>
        <hr style="border-color:#ff0055; opacity:0.3; margin-bottom:20px;">
        """
        
        if panel == 'Admin_Deposits':
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            if not pending_items: content_html += "<p style='text-align:center;color:#a0a0a5;'>No pending deposits inside live buffer queues.</p>"
            for item in pending_items:
                content_html += f"""
                <div style='background-color:#12131a; padding:18px; border-radius:14px; border:2px solid #ff0055; margin-bottom:12px;'>
                    <b>User Identity:</b> {item[1]}<br>
                    <b>Method Selection:</b> {item[2]}<br>
                    <b>Depositor Native Name:</b> {item[3]}<br>
                    <b>Tracking Hash Code:</b> <code style='color:#00f0ff;'>{item[4]}</code><br>
                    <b>Claim Volume:</b> <b style='color:#ff0055; font-size:18px;'>RM {item[5]:.2f}</b>
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <button onclick="window.location.href='/action_deposit?id={item[0]}&status=Approved'">✅ APPROVE & ASSIGN</button>
                        <button onclick="window.location.href='/action_deposit?id={item[0]}&status=Rejected'" style="background:red !important;">❌ REJECT REQUEST</button>
                    </div>
                </div>
                """
        elif panel == 'Admin_Configs':
            content_html += f"""
            <form method="POST" action="/update_sys_configs">
                <h5>⚙️ SYSTEM DYNAMIC CHANNELS MODIFIER</h5>
                <label>System Dashboard Alert Announcement Text:</label>
                <textarea name="announcement" rows="2" required>{announcement}</textarea>
                <label>Update Touch 'n Go Scanner Image Gateway URL Link:</label>
                <input type="text" name="tng_url" value="{tng_scanner_url}" placeholder="Input direct path image asset link here" required>
                <label>Update USDT Crypto Network Terminal (TRC-20 Address):</label>
                <input type="text" name="usdt" value="{usdt_address}" placeholder="Input destination wallet address token here" required>
                <button type="submit">COMMIT AND SAVE LIVE CHANNEL SETTINGS</button>
            </form>
            """
        elif panel == 'Admin_Users':
            content_html += """
            <form method="POST" action="/update_user_balance">
                <h5>👤 ADJUST USER WALLET BALANCES MANUALLY</h5>
                <label>Target User Registered Account Email Address:</label>
                <input type="text" name="target_user" placeholder="e.g. client@gmail.com" required>
                <label>Define Explicit Target Balance Amount (RM Value):</label>
                <input type="number" step="0.01" name="new_balance" placeholder="Set explicit value e.g. 550.00" required>
                <button type="submit">🔥 RUN OVERWRITE BALANCE RE-INDEX</button>
            </form>
            """
        elif panel == 'Admin_Withdraws':
            pending_with = query_db("SELECT id, username, bank, account, amount FROM withdrawals WHERE status='Pending'")
            if not pending_with: content_html += "<p style='text-align:center;color:#a0a0a5;'>No cash withdrawal tickets found in request stack.</p>"
            for w_item in pending_with:
                content_html += f"""
                <div style='background-color:#12131a; padding:15px; border-radius:12px; border:2px solid #a100ff; margin-bottom:10px;'>
                    <b>Sender Account Mail:</b> {w_item[1]}<br>
                    <b>Destination Gate Node:</b> {w_item[2]} | Account Node Id: {w_item[3]}<br>
                    <b>Cash Value Volume: <span style='color:#ff0055;'>RM {w_item[4]:.2f}</span></b>
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <button onclick="window.location.href='/action_withdraw?id={w_item[0]}&status=Approved'">✅ DISPATCH DISBURSEMENT SUCCESS</button>
                        <button onclick="window.location.href='/action_withdraw?id={w_item[0]}&status=Rejected'" style="background:red !important;">❌ REFUSE & RETURN FUNDS</button>
                    </div>
                </div>
                """
        elif panel == 'Admin_Campaigns':
            campaigns = query_db("SELECT id, advertiser_email, video_url, target_views, status FROM ad_campaigns")
            if not campaigns: content_html += "<p style='text-align:center;color:#a0a0a5;'>No active marketing traffic campaigns registry.</p>"
            for camp in campaigns:
                content_html += f"""
                <div style='background-color:#12131a; padding:15px; border-radius:12px; border:1px solid #00f0ff; margin-bottom:10px;'>
                    <b>Marketer:</b> {camp[1]}<br>
                    <b>Media URL:</b> <small>{camp[2]}</small><br>
                    <b>Targets Cap:</b> {camp[3]} views | Status: {camp[4]}
                </div>
                """
        elif panel == 'Admin_Tickets':
            tickets = query_db("SELECT id, username, subject, message, reply, status FROM support_tickets")
            if not tickets: content_html += "<p style='text-align:center;color:#a0a0a5;'>No support requests raised inside portal logs.</p>"
            for tk in tickets:
                content_html += f"""
                <div style='background-color:#12131a; padding:15px; border-radius:12px; border:1px solid #ff0055; margin-bottom:10px;'>
                    <b>Client:</b> {tk[1]} | Subject: <b>{tk[2]}</b><br>
                    <b>Description:</b> {tk[3]}<br>
                    <form method="POST" action="/reply_ticket">
                        <input type="hidden" name="ticket_id" value="{tk[0]}">
                        <input type="text" name="reply_text" value="{tk[4] if tk[4] else ''}" placeholder="Type support response link here">
                        <button type="submit" style="padding:6px; font-size:12px;">SEND REPLY RECORD</button>
                    </form>
                </div>
                """
        content_html += '<button onclick="window.location.href=\'/logout\'" style="margin-top:30px; background:red !important;">LOGOUT DISCONNECT SECURITY GATE</button>'
        return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", content_html), dynamic_ticker=live_feed, msg_success=success_banner, msg_error=error_banner)

    content_html = f"""
    <div class="brand-title">GLOBAL <b><b>MATRIX</b></b></div>
    <div class="announcement-box">{announcement}</div>
    
    <div class="metric-card-box">
        <p style="font-size:12px; color:#ff0055; margin:0; font-weight:900;">⚡ ACCOUNT TOTAL BALANCE</p>
        <h1 style="font-size:38px; font-weight:900; color:#ffffff; margin:8px 0;">RM {wallet_bal:,.2f}</h1>
        <p style="color:#00f0ff; margin:0; font-size:13px;">CURRENT RANK: {level_tag}</p>
        <p style="color:#a100ff; margin:5px 0 0 0; font-size:12px;">REFERRAL CODE: {reference_hash}</p>
    </div>
    """

    if panel == 'Overview':
        already_spun = query_db("SELECT username FROM lucky_spins WHERE username=? AND date=?", (session['current_user'], today_date), one=True)
        content_html += "<p style='font-weight:900; font-size:14px; color:#a100ff; text-align:center;'>🎡 DAILY LUCKY SPIN WHEEL</p>"
        
        if already_spun:
            content_html += "<div class='custom-matrix-box-cyan' style='text-align:center; color:#00f0ff;'>✅ TODAY'S LUCKY WHEEL CLAIMED</div>"
        else:
            content_html += f"""
            <div style="text-align:center; background:#12131a; padding:15px; border-radius:14px; border:2px solid #a100ff; margin-bottom:15px;">
                <canvas id="wheelCanvas" width="240" height="240" style="border:4px solid #00f0ff; border-radius:50%; background:#0b0c10; transition: transform 4s cubic-bezier(0.1, 0.8, 0.3, 1);"></canvas>
                <button id="spinBtn" style="margin-top:10px;">🎰 SPIN THE WHEEL NOW</button>
            </div>
            <script>
                const ctx = document.getElementById('wheelCanvas').getContext('2d');
                const labels = ["RM0.50", "RM2.00", "RM0.10", "RM5.00", "RM0.20", "RM10.00", "RM1.50", "RM0.00"];
                const colors = ["#ff0055", "#0b0c10", "#00f0ff", "#0b0c10", "#a100ff", "#0b0c10", "#ffaa00", "#0b0c10"];
                for (let i = 0; i < 8; i++) {{
                    ctx.beginPath(); ctx.fillStyle = colors[i]; ctx.moveTo(120, 120);
                    ctx.arc(120, 120, 120, (i*45)*Math.PI/180, ((i+1)*45)*Math.PI/180); ctx.lineTo(120, 120); ctx.fill();
                    ctx.save(); ctx.translate(120, 120); ctx.rotate((i*45+22.5)*Math.PI/180);
                    ctx.fillStyle = "#ffffff"; ctx.font = "bold 10px Orbitron"; ctx.fillText(labels[i], 40, 5); ctx.restore();
                }}
                document.getElementById('spinBtn').onclick = function() {{
                    let targetRotation = 1800 + Math.floor(Math.random() * 360);
                    document.getElementById('wheelCanvas').style.transform = 'rotate(' + targetRotation + 'deg)';
                    setTimeout(()=>{{ window.location.href = '/claim_spin'; }}, 4100);
                }};
            </script>
            """

        content_html += "<hr style='border-color:#ff0055; opacity:0.2; margin:15px 0;'>"
        already_checked = query_db("SELECT username FROM checkins WHERE username=? AND date=?", (session['current_user'], today_date), one=True)
        content_html += "<p style='font-weight:900; font-size:13px; color:#ff0055;'>🎁 DAILY BONUS CHECK-IN</p>"
        
        if not has_approved_deposit:
            content_html += "<div class='custom-matrix-box-pink' style='text-align:center; color:#ff0055;'>🔒 LOCKED: Make an initial deposit first to unlock daily rewards.</div>"
        else:
            if already_checked: content_html += "<p style='color:#00f0ff; font-weight:bold; text-align:center;'>✅ DAILY BONUS CLAIMED TODAY</p>"
            else: content_html += '<button onclick="window.location.href=\'/claim_checkin\'">CLAIM DAILY BONUS (RM 0.50)</button>'

        content_html += f"""
        <hr style='border-color:#ff0055; opacity:0.2; margin:15px 0;'>
        <p style='font-size:14px; font-weight:900;'>👑 ACTIVE VIP ACCOUNT LEVELS</p>
        <div class='custom-matrix-box-cyan'><div style='display:flex; justify-content:space-between;'><span>👑 VIP LEVEL 1</span><span style='color:#00f0ff;'>Daily Income: RM {v1_inc:.2f}</span></div></div>
        <div class='custom-matrix-box-pink'><div style='display:flex; justify-content:space-between;'><span>👑 VIP LEVEL 2 (Req: RM {v2_req:.2f})</span><span style='color:#ff0055;'>Daily Income: RM {v2_inc:.2f}</span></div></div>
        <div class='custom-matrix-box-cyan' style='border-color:#a100ff;'><div style='display:flex; justify-content:space-between;'><span>👑 VIP LEVEL 3 (Req: RM {v3_req:.2f})</span><span style='color:#a100ff;'>Daily Income: RM {v3_inc:.2f}</span></div></div>
        """

        content_html += "<hr style='border-color:#ff0055; opacity:0.2; margin:20px 0;'><p style='font-size:14px; font-weight:900; text-align:center;'>🎬 WATCH VIDEO ADS TO EARN</p>"
        if not has_approved_deposit:
            content_html += "<div class='custom-matrix-box-pink' style='text-align:center; color:#ff0055;'>🔒 LOCKED: Active validation deposit required to watch videos.</div>"
        else:
            for i in range(1, 6):
                ad_url = query_db(f"SELECT value FROM system_config WHERE key='ad{i}_url'", one=True)[0]
                ad_rew = float(query_db(f"SELECT value FROM system_config WHERE key='ad{i}_reward'", one=True)[0])
                ad_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id=? AND date=?", (session['current_user'], f'ad{i}', today_date), one=True)
                content_html += f"""
                <div class="custom-matrix-box-cyan" style="text-align:center;">
                    <b>Video Task Item Block {i}</b><br>Reward Payout: RM {ad_rew:.2f}<br>
                """
                if ad_watched: content_html += "<span style='color:#00f0ff; font-weight:bold;'>✅ VIDEO RESOLVED & PAID</span></div>"
                else:
                    content_html += f"""
                    <a href="{ad_url}" target="_blank" class="btn-link" style="padding:6px; font-size:12px; background:#00f0ff !important; color:#000 !important; margin-top:5px;">📺 OPEN VIDEO LINK</a>
                    <button onclick="window.location.href='/claim_ad?ad_id=ad{i}&rew={ad_rew}'" style="padding:6px; font-size:12px; margin-top:3px;">💰 CLAIM REWARD NOW</button>
                </div>
                """

    elif panel == 'Deposit':
        content_html += f"""
        <h5>📥 CHOOSE DEPOSIT METHOD</h5>
        <div style='text-align:center; margin-bottom:15px;'><img src='{tng_scanner_url}' width='140' style='border:2px solid #00f0ff; border-radius:12px;'/></div>
        <div style='background:#1a090d; border:1px solid #a100ff; padding:12px; border-radius:10px; margin-bottom:12px;'>
            <span style='color:#a100ff; font-weight:bold;'>USDT Wallet Destination Node Address:</span><br><code style='word-break:break-all;color:#00f0ff;'>{usdt_address}</code>
        </div>
        <form method="POST" action="/submit_deposit">
            <select name="bank">{"".join([f"<option>{b}</option>" for b in MALAYSIAN_BANKS])}</select>
            <input type="text" name="name" placeholder="YOUR FULL NAME (AS PER BANK)" required>
            <input type="text" name="trx_id" placeholder="PASTE TRANSACTION TXID OR RECEIPT CODE" required>
            <input type="number" step="0.01" name="amount" value="100.0" placeholder="Deposit Amount" required>
            <button type="submit">SUBMIT DEPOSIT DETAILS</button>
        </form>
        """

    elif panel == 'Cashout':
        content_html += f"""
        <h5>💰 SECURE FUND WITHDRAWAL</h5>
        <form method="POST" action="/submit_cashout">
            <select name="bank">{"".join([f"<option>{b}</option>" for b in MALAYSIAN_BANKS])}</select>
            <input type="text" name="account" placeholder="Enter Your Bank Account Number / Wallet Number" required>
            <input type="number" step="0.01" name="amount" placeholder="Enter Amount to Withdraw (RM)" required>
            <button type="submit">REQUEST CASH OUT WITHDRAWAL</button>
        </form>
        """

    elif panel == 'Promote':
        content_html += f"""
        <h5>📢 REFERRAL AFFILIATE CENTER</h5>
        <p style='font-size:13px; color:#a0a0a5;'>Share your digital invitation hash node with target contacts to accumulate structural multi-tier downline matrix dividends.</p>
        <div class='custom-matrix-box-cyan' style='text-align:center;'>
            <small style='color:#ff0055;'>YOUR SECURE AFFILIATE LINK:</small><br>
            <code style='font-size:12px; color:#00f0ff;'>https://globalmatrix.com/register?ref={reference_hash}</code>
        </div>
        """

    elif panel == 'Support_Helpdesk':
        content_html += """
        <h5>🎫 TECH HELP DESK / OPEN TICKET</h5>
        <form method="POST" action="/submit_ticket">
            <input type="text" name="subject" placeholder="Ticket Category Issue" required>
            <textarea name="message" rows="4" placeholder="Describe the problem context details..." required></textarea>
            <button type="submit">DISPATCH HELP DESK TICKET</button>
        </form>
        <hr style='border-color:#ff0055; opacity:0.3;'>
        <h6>Your Active Communication Logs:</h6>
        """
        user_tickets = query_db("SELECT subject, message, reply, status FROM support_tickets WHERE username=?", (session['current_user'],))
        for tk in user_tickets:
            content_html += f"""
            <div style='background:#12131a; border:1px solid #00f0ff; padding:10px; border-radius:8px; margin-bottom:8px; font-size:12px;'>
                <b>Cat: {tk[0]}</b> [{tk[3]}]<br>Msg: {tk[1]}<br>
                <span style='color:#00f0ff;'>Reply Node: {tk[2] if tk[2] else 'Awaiting backoffice admin response review.'}</span>
            </div>
            """

    content_html += f"""
    <div class="nav-grid">
        <button onclick="window.location.href='/?panel=Overview'">HOME</button>
        <button onclick="window.location.href='/?panel=Deposit'">DEPOSIT</button>
        <button onclick="window.location.href='/?panel=Cashout'">WITHDRAW</button>
        <button onclick="window.location.href='/?panel=Promote'">INVITE</button>
        <button onclick="window.location.href='/?panel=Support_Helpdesk'">SUPPORT</button>
    </div>
    """
    return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", content_html), dynamic_ticker=live_feed, msg_success=success_banner, msg_error=error_banner)


@app.route('/login', methods=['GET', 'POST'])
def login():
    success_banner = session.pop('success_flash', '')
    error_banner = session.pop('error_flash', '')
    live_feed = generate_live_activity_logs()
    
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','').strip()
        
        if username.lower() == "mani" and password == "MANI2662":
            session['logged_in'] = True
            session['current_user'] = "Mani"
            session['is_admin'] = True
            return redirect(url_for('index', panel='Admin_Deposits'))
        else:
            record = query_db("SELECT password, username FROM users WHERE username=?", (username,), one=True)
            if record and record[0] == password:
                session['logged_in'] = True
                session['current_user'] = record[1]
                session['is_admin'] = False
                return redirect(url_for('index', panel='Overview'))
            else:
                error_banner = "❌ INVALID PASSWORD OR ACCOUNT EMAIL ENTRY"
    
    login_html = """
    <div class="brand-title">GLOBAL <b><b>MATRIX</b></b></div>
    <div style="text-align:center; font-size:12px; margin-bottom:20px;">USER SECURE GATEWAY LOGIN</div>
    
    <form method="POST">
        <input type="text" name="username" placeholder="ENTER ACCOUNT EMAIL ADDRESS" required>
        <input type="password" name="password" placeholder="ENTER SECURE ACCESS PASSCODE" required>
        <button type="submit">LOG IN TO DASHBOARD</button>
    </form>
    
    <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 15px;">
        <button onclick="window.location.href='/register'">🎮 REGISTER ACCOUNT</button>
        <button onclick="window.location.href='/forgot_password'">🔑 FORGOT PASSWORD</button>
    </div>
    """
    return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", login_html), dynamic_ticker=live_feed, msg_success=success_banner, msg_error=error_banner)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    success_banner = session.pop('success_flash', '')
    error_banner = session.pop('error_flash', '')
    live_feed = generate_live_activity_logs()
    
    if request.method == 'POST':
        step = request.form.get('step')
        if step == '1':
            email = request.form.get('username','').strip()
            record = query_db("SELECT password FROM users WHERE username=?", (email,), one=True)
            if not record:
                error_banner = "❌ This email address does not exist inside our active systems."
            else:
                otp = str(random.randint(100000, 999999))
                if send_verification_email(email, otp, "Password Recovery"):
                    session['reset_email'] = email
                    session['reset_otp'] = otp
                    session['cached_pass'] = record[0]
                    success_banner = "🔑 Reset token pass code dispatched to your email address inbox."
                else:
                    error_banner = "❌ Internal Mail Server Connection Fault."
        elif step == '2':
            user_otp = request.form.get('otp_code','').strip()
            if user_otp == session.get('reset_otp'):
                success_banner = f"✅ Verified! Your account password is: [ {session.get('cached_pass')} ]"
                session.pop('reset_otp', None)
            else:
                error_banner = "❌ Invalid verification OTP mismatch token code."

    if 'reset_otp' in session:
        forgot_html = """
        <h5>🔑 ENTER PASSWORD RESET OTP</h5>
        <form method="POST">
            <input type="hidden" name="step" value="2">
            <input type="text" name="otp_code" placeholder="ENTER 6-DIGIT EMAIL RESET CODE" required>
            <button type="submit">VERIFY ACCOUNT TOKEN</button>
        </form>
        """
    else:
        forgot_html = """
        <h5>🔑 PASSWORD RECOVERY LOG</h5>
        <form method="POST">
            <input type="hidden" name="step" value="1">
            <input type="email" name="username" placeholder="ENTER YOUR REGISTERED EMAIL ADDRESS" required>
            <button type="submit">SEND PASSWORD RESET OTP</button>
        </form>
        <button onclick="window.location.href='/login'" style="background:#12131a !important; border:1px solid #ff0055 !important; margin-top:10px;">RETURN TO LOGIN GATE</button>
        """
    return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", forgot_html), dynamic_ticker=live_feed, msg_success=success_banner, msg_error=error_banner)

@app.route('/register', methods=['GET', 'POST'])
def register():
    success_banner = session.pop('success_flash', '')
    error_banner = session.pop('error_flash', '')
    live_feed = generate_live_activity_logs()
    
    if request.method == 'POST':
        step = request.form.get('step')
        if step == '1':
            email = request.form.get('username','').strip()
            password = request.form.get('password','').strip()
            referral = request.form.get('referral','').strip()
            
            exists = query_db("SELECT username FROM users WHERE username=?", (email,), one=True)
            if exists: error_banner = "❌ Account email already exists inside database registry."
            else:
                otp = str(random.randint(100000, 999999))
                if send_verification_email(email, otp, "Registration"):
                    session['reg_email'] = email
                    session['reg_pass'] = password
                    session['reg_ref'] = referral
                    session['reg_otp'] = otp
                    success_banner = "🔑 Secure verification token sent to your email address."
                else: error_banner = "❌ Internal Mail Relay Handshake Error."
        elif step == '2':
            user_otp = request.form.get('otp_code','').strip()
            if user_otp == session.get('reg_otp'):
                generated_ref = "MX" + str(random.randint(1000, 9999))
                query_db("INSERT INTO users VALUES (?, ?, 0.0, 0.0, '👑 VIP LEVEL 1', ?, ?)",
                         (session['reg_email'], session['reg_pass'], generated_ref, session['reg_ref']), commit=True)
                session['success_flash'] = "✅ Registration Successful! Please log in."
                return redirect(url_for('login'))
            else: error_banner = "❌ Code mismatched. Verification refused."

    if 'reg_otp' in session:
        reg_html = """
        <form method="POST">
            <input type="hidden" name="step" value="2">
            <input type="text" name="otp_code" placeholder="ENTER 6-DIGIT EMAIL OTP CODE" required>
            <button type="submit">SUBMIT VALIDATION OTP</button>
        </form>
        """
    else:
        reg_html = """
        <form method="POST">
            <input type="hidden" name="step" value="1">
            <input type="email" name="username" placeholder="ENTER YOUR SYSTEM TARGET EMAIL" required>
            <input type="password" name="password" placeholder="SET ACCOUNT UNIQUE PASSWORD" required>
            <input type="text" name="referral" placeholder="REFERRAL INVITATION CODE (OPTIONAL)">
            <button type="submit">SEND EMAIL OTP DISPATCH</button>
        </form>
        <button onclick="window.location.href='/login'" style="background:#12131a !important; border:1px solid #ff0055 !important; margin-top:10px;">BACK TO SECURITY TERMINAL</button>
        """
    return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", reg_html), dynamic_ticker=live_feed, msg_success=success_banner, msg_error=error_banner)

@app.route('/claim_spin')
def claim_spin():
    if 'logged_in' in session:
        prizes = [0.50, 2.00, 0.10, 5.00, 0.20, 10.00, 1.50, 0.00]
        win_amt = random.choice(prizes)
        today = time.strftime("%Y-%m-%d")
        query_db("INSERT OR IGNORE INTO lucky_spins VALUES (?, ?, ?)", (session['current_user'], today, win_amt), commit=True)
        query_db("UPDATE users SET balance = balance + ? WHERE username=?", (win_amt, session['current_user']), commit=True)
        session['success_flash'] = f"🎰 Added +RM {win_amt:.2f} safely to wallet balance."
    return redirect(url_for('index'))

@app.route('/claim_checkin')
def claim_checkin():
    if 'logged_in' in session:
        today = time.strftime("%Y-%m-%d")
        query_db("INSERT OR IGNORE INTO checkins VALUES (?, ?)", (session['current_user'], today), commit=True)
        query_db("UPDATE users SET balance = balance + 0.50 WHERE username=?", (session['current_user'],), commit=True)
        session['success_flash'] = "✅ Checked in! +RM 0.50 added successfully."
    return redirect(url_for('index'))

@app.route('/claim_ad')
def claim_ad():
    if 'logged_in' in session:
        ad_id = request.args.get('ad_id')
        rew = float(request.args.get('rew', 0))
        today = time.strftime("%Y-%m-%d")
        query_db("INSERT OR IGNORE INTO ad_logs VALUES (?, ?, ?)", (session['current_user'], ad_id, today), commit=True)
        query_db("UPDATE users SET balance = balance + ? WHERE username=?", (rew, session['current_user']), commit=True)
        credit_multi_tier_commissions(session['current_user'], rew)
        session['success_flash'] = f"💰 Video Reward Claimed! +RM {rew:.2f} assigned."
    return redirect(url_for('index'))

@app.route('/submit_deposit', methods=['POST'])
def submit_deposit():
    if 'logged_in' in session:
        query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                 (session['current_user'], request.form.get('bank'), request.form.get('name'), request.form.get('trx_id'), request.form.get('amount')), commit=True)
        session['success_flash'] = "🚀 Deposit tracking request sent to admin panel queue."
    return redirect(url_for('index'))

@app.route('/submit_cashout', methods=['POST'])
def submit_cashout():
    if 'logged_in' in session:
        amount = float(request.form.get('amount', 0))
        user_bal = query_db("SELECT balance FROM users WHERE username=?", (session['current_user'],), one=True)[0]
        if user_bal >= amount:
            query_db("UPDATE users SET balance = balance - ? WHERE username=?", (amount, session['current_user']), commit=True)
            query_db("INSERT INTO withdrawals (username, bank, account, amount, status) VALUES (?, ?, ?, ?, 'Pending')",
                     (session['current_user'], request.form.get('bank'), request.form.get('account'), amount), commit=True)
            session['success_flash'] = "✅ Withdrawal checkout log logged for admin review."
        else: session['error_flash'] = "❌ Failed: Insufficient total fund liquid volume."
    return redirect(url_for('index'))

@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():
    if 'logged_in' in session:
        query_db("INSERT INTO support_tickets (username, subject, message, reply, status) VALUES (?, ?, ?, '', 'Open')",
                 (session['current_user'], request.form.get('subject'), request.form.get('message')), commit=True)
        session['success_flash'] = "🎫 Ticket log opened. Support dispatch alerted."
    return redirect(url_for('index', panel='Support_Helpdesk'))

@app.route('/action_deposit')
def action_deposit():
    if session.get('is_admin', False):
        item_id = request.args.get('id')
        status = request.args.get('status')
        if status == 'Approved':
            dep = query_db("SELECT amount, username FROM deposits WHERE id=?", (item_id,), one=True)
            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (dep[0], dep[1]), commit=True)
            sync_user_vip_tier(dep[1])
        query_db("UPDATE deposits SET status=? WHERE id=?", (status, item_id), commit=True)
    return redirect(url_for('index', panel='Admin_Deposits'))

@app.route('/action_withdraw')
def action_withdraw():
    if session.get('is_admin', False):
        item_id = request.args.get('id')
        status = request.args.get('status')
        if status == 'Rejected':
            wth = query_db("SELECT amount, username FROM withdrawals WHERE id=?", (item_id,), one=True)
            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (wth[0], wth[1]), commit=True)
        query_db("UPDATE withdrawals SET status=? WHERE id=?", (status, item_id), commit=True)
    return redirect(url_for('index', panel='Admin_Withdraws'))

@app.route('/update_sys_configs', methods=['POST'])
def update_sys_configs():
    if session.get('is_admin', False):
        query_db("UPDATE system_config SET value=? WHERE key='system_announcement'", (request.form.get('announcement'),), commit=True)
        query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (request.form.get('tng_url'),), commit=True)
        query_db("UPDATE system_config SET value=? WHERE key='usdt_address'", (request.form.get('usdt'),), commit=True)
        session['success_flash'] = "⚙️ Scanner Assets & Addresses Synchronized Successfully."
    return redirect(url_for('index', panel='Admin_Configs'))

@app.route('/update_user_balance', methods=['POST'])
def update_user_balance():
    if session.get('is_admin', False):
        target = request.form.get('target_user').strip()
        new_bal = request.form.get('new_balance')
        query_db("UPDATE users SET balance=? WHERE username=?", (new_bal, target), commit=True)
        sync_user_vip_tier(target)
        session['success_flash'] = f"🔥 Balance target user account hash successfully re-indexed to RM {new_bal}."
    return redirect(url_for('index', panel='Admin_Users'))

@app.route('/reply_ticket', methods=['POST'])
def reply_ticket():
    if session.get('is_admin', False):
        query_db("UPDATE support_tickets SET reply=?, status='Resolved' WHERE id=?", (request.form.get('reply_text'), request.form.get('ticket_
