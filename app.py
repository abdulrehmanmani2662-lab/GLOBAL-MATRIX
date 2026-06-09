import os
import sqlite3
import random
import smtplib
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, redirect, url_for, session, render_template_string, jsonify

# --- LOGGING SUBSYSTEM FOR GLOBAL MATRIX KERNEL ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GLOBAL_MATRIX_KERNEL")

app = Flask(__name__)
app.secret_key = "GLOBAL_MATRIX_SUPER_SECRET_KEY_2026_EXCLUSIVE"

# --- REAL SMTP BACKEND EMAIL GATEWAY CONFIGURATION ---
SENDER_EMAIL = "globalmatrixteam.com@gmail.com"
SENDER_APP_PASSWORD = "lddfmerstvilicby"  

def send_verification_email(receiver_email, otp_code, purpose="Registration"):
    """
    Dispatches specialized cryptographic identity payload directly to user terminal mail node.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Global Matrix Network <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"🔑 Security Verification Code: {otp_code}"
        
        body = f"""
        <html>
        <body style="font-family: 'Orbitron', sans-serif; background-color: #0b0c10; padding: 20px;">
            <div style="max-width: 400px; margin: 0 auto; background: #1f2026; border: 2px solid #ff0055; border-radius: 16px; padding: 25px; text-align: center; box-shadow: 0 0 15px rgba(255,0,85,0.4);">
                <h2 style="color: #00f0ff; margin-bottom: 10px; font-weight: 900; letter-spacing: 2px;">GLOBAL MATRIX NETWORK</h2>
                <hr style="border: 0; height: 1px; background: rgba(0,240,255,0.3); margin-bottom: 20px;">
                <p style="color: #ffffff; font-size: 16px;">Your Network Access Authorization Code for {purpose} is:</p>
                <div style="font-size: 32px; font-weight: bold; color: #ffffff; letter-spacing: 4px; padding: 12px; background: #0b0c10; border: 1px solid #00f0ff; border-radius: 10px; margin: 20px 0;">
                    {otp_code}
                </div>
                <p style="color: #a0a0a5; font-size: 12px;">This code expires in 10 minutes. Secure your authorization data.</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        logger.info(f"OTP successfully transmitted to {receiver_email}")
        return True
    except Exception as e:
        logger.error(f"SMTP Critical Fault Layer Error: {e}")
        return False

# --- MALAYSIAN FINANCIAL INSTANCE DATA MATRIX ---
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

# --- PLATFORM SCHEMATIC DATABASE MANAGEMENT INTERFACE ---
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
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN referred_by TEXT")
        except sqlite3.OperationalError:
            pass
            
        configs = [
            ('ad1_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad1_reward', '3.00'),
            ('ad2_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad2_reward', '2.30'),
            ('ad3_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad3_reward', '4.50'),
            ('ad4_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad4_reward', '1.50'),
            ('ad5_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad5_reward', '2.00'),
            ('tng_scanner_url', 'https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg'),
            ('usdt_address', 'TYcc7p18K2YnQp87bXzNWXAsgWqR54321A'),
            ('system_announcement', '⚠️ SYSTEM ADVISORY: Gateway performance optimized. Instantly match deposits using fast touch n go nodes.'),
            ('unclaimed_rewards_val', '15.00'),
            ('vip1_income', '2.00'), ('vip2_income', '15.00'), ('vip3_income', '50.00'),
            ('vip2_req', '100.00'), ('vip3_req', '300.00'),
            ('tier1_bonus_pct', '10.0'), ('tier2_bonus_pct', '5.0'), ('tier3_bonus_pct', '2.0')
        ]
        
        for key, val in configs:
            cursor.execute("INSERT OR IGNORE INTO system_config VALUES (?, ?)", (key, val))
            
        cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 0.0, 0.0, 'OWNER', 'MASTER', '')")
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully with structural models.")
    except Exception as db_init_err:
        logger.critical(f"Critical Failure in Database Initialization Sequence: {db_init_err}")

init_db()

def query_db(query, args=(), one=False, commit=False):
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
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
        logger.error(f"Database Fault Intercepted: {e}")
        conn.rollback()
        conn.close()
        return None if one else []

# --- DYNAMIC MULTI-LEVEL NETWORK AFFILIATE DELEGATOR CONTROLLER ---
def credit_multi_tier_commissions(user, base_reward):
    try:
        t1_pct = float(query_db("SELECT value FROM system_config WHERE key='tier1_bonus_pct'", one=True)[0]) / 100.0
        t2_pct = float(query_db("SELECT value FROM system_config WHERE key='tier2_bonus_pct'", one=True)[0]) / 100.0
        t3_pct = float(query_db("SELECT value FROM system_config WHERE key='tier3_bonus_pct'", one=True)[0]) / 100.0

        tier_1_parent = query_db("SELECT referred_by FROM users WHERE username=?", (user,), one=True)
        if not tier_1_parent or not tier_1_parent[0]: return
        p1 = tier_1_parent[0].strip()
        if p1:
            amt1 = base_reward * t1_pct
            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (amt1, p1), commit=True)
        
        tier_2_parent = query_db("SELECT referred_by FROM users WHERE username=?", (p1,), one=True)
        if not tier_2_parent or not tier_2_parent[0]: return
        p2 = tier_2_parent[0].strip()
        if p2:
            amt2 = base_reward * t2_pct
            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (amt2, p2), commit=True)
        
        tier_3_parent = query_db("SELECT referred_by FROM users WHERE username=?", (p2,), one=True)
        if not tier_3_parent or not tier_3_parent[0]: return
        p3 = tier_3_parent[0].strip()
        if p3:
            amt3 = base_reward * t3_pct
            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (amt3, p3), commit=True)
    except Exception as tracking_error:
        logger.error(f"Error executing affiliate multi-tier cascade flow: {tracking_error}")

# --- TRACK MATRIX RE-EVALUATION & AUTOMATED VIP TIER TRANSITIONS ---
def sync_user_vip_tier(username):
    try:
        total_approved = query_db("SELECT SUM(amount) FROM deposits WHERE username=? AND status='Approved'", (username,), one=True)
        total_dep = total_approved[0] if total_approved and total_approved[0] else 0.0
        v2_req = float(query_db("SELECT value FROM system_config WHERE key='vip2_req'", one=True)[0])
        v3_req = float(query_db("SELECT value FROM system_config WHERE key='vip3_req'", one=True)[0])
        
        new_tier = "👑 VIP LEVEL 1"
        liquidation_factor = total_dep * 0.15
        if total_dep >= v3_req: new_tier = "👑 VIP LEVEL 3"
        elif total_dep >= v2_req: new_tier = "👑 VIP LEVEL 2"
            
        query_db("UPDATE users SET active_level=?, liquidation=? WHERE username=?", (new_tier, liquidation_factor, username), commit=True)
    except Exception as calibration_error:
        logger.error(f"Failed to synchronize VIP alignment vector: {calibration_error}")

# --- SIMULATED ACTIVITY STREAM BOOSTER FOR USER RETENTION ---
def generate_live_activity_logs():
    users_pool = ["Zaki_TNG", "Aiman_99", "Mani_Admin", "Siti_Aminah", "Raju_Bitcoin", "Michelle_KL", "Chao_Matrix", "Firdaus_Dev", "Wong_Settle", "Aziz_Crypto"]
    actions = [
        "claimed Dynamic Video Bounty RM4.50", "processed exit settlement RM250.00 via Touch 'n Go", 
        "unlocked High-Yield VIP Level 2 Node", "won RM10.00 via Lucky Matrix Wheel", 
        "claimed Operational Check-In Bounty RM0.50", "allocated RM1200.00 via USDT Network",
        "referred active node member to Tier-1", "extracted promotional block payout RM35.00"
    ]
    activity_strings = [f"⚡ {random.choice(users_pool)} {random.choice(actions)}" for _ in range(15)]
    return " &nbsp;&nbsp;&nbsp;&nbsp;||&nbsp;&nbsp;&nbsp;&nbsp; ".join(activity_strings)

# --- PRODUCTION MATRIX METROPOLIS UI THEMATIC SCHEMATIC ---
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
        .running-header-container { width: 100%; background: #12131a; padding: 12px 0; margin-bottom: 10px; border-bottom: 2px solid #ff0055; text-align:center; }
        .running-text { font-family: 'Orbitron', sans-serif !important; font-size: 13px; font-weight: 900; color: #00f0ff; letter-spacing: 2px; }
        .fomo-ticker-container { width: 100%; background: linear-gradient(90deg, #ff0055 0%, #a100ff 100%); padding: 6px 0; margin-bottom: 20px; box-shadow: 0 0 10px rgba(255,0,85,0.4); text-align: center; }
        .fomo-text { font-family: 'Orbitron', sans-serif !important; font-size: 14px; font-weight: bold; color: #ffffff; letter-spacing: 1px; }
        .brand-title { text-align: center; font-family: 'Orbitron', sans-serif !important; font-size: 38px; font-weight: 900; color: #ffffff; margin-top: 10px; letter-spacing: 3px; text-shadow: 0 0 10px rgba(0,240,255,0.5); }
        .brand-subtitle { text-align: center; font-family: 'Orbitron', sans-serif !important; font-size: 14px; font-weight: bold; color: #ff0055; letter-spacing: 2px; margin-bottom: 25px; text-transform: uppercase; }
        .announcement-box { background: #1a090d; border: 2px solid #ff0055; border-radius: 14px; padding: 15px; font-size: 14px; color: #ff3377 !important; font-weight: 800; margin-bottom: 20px; text-align: center; font-family: 'Orbitron', sans-serif !important; }
        .metric-card-box { background: linear-gradient(135deg, #12131a 0%, #1f2026 100%); border: 2px solid #00f0ff; border-radius: 20px; padding: 25px 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 15px rgba(0,240,255,0.2); }
        input, select, textarea { width: 100%; background-color: #12131a !important; color: #ffffff !important; border: 2px solid #ff0055 !important; border-radius: 12px !important; font-weight: 900 !important; font-family: 'Orbitron', sans-serif !important; padding: 12px !important; font-size: 14px; box-shadow: 0 0 8px rgba(255, 0, 85, 0.2); margin-bottom: 15px; box-sizing: border-box; text-transform: uppercase; }
        button, .btn-link { display: block; background: linear-gradient(135deg, #a100ff 0%, #ff0055 100%) !important; color: #ffffff !important; font-family: 'Orbitron', sans-serif !important; font-size: 15px !important; font-weight: 900; border-radius: 14px !important; width: 100% !important; padding: 14px !important; border: none !important; box-shadow: 0 4px 15px rgba(255, 0, 85, 0.4); text-align: center; text-decoration: none; box-sizing: border-box; cursor: pointer; margin-bottom: 10px; }
        button:hover { box-shadow: 0 0 20px rgba(0, 240, 255, 0.6); transform: scale(1.01); transition: 0.2s; }
        .custom-matrix-box-cyan { background: #12131a; border: 2px solid #00f0ff; border-radius: 14px; padding: 16px; margin: 15px 0; font-family: 'Orbitron', sans-serif !important; font-weight: 600; }
        .custom-matrix-box-pink { background: #12131a; border: 2px solid #ff0055; border-radius: 14px; padding: 16px; margin: 15px 0; font-family: 'Orbitron', sans-serif !important; font-weight: 600; }
        .custom-matrix-box-purple { background: #12131a; border: 2px solid #a100ff; border-radius: 14px; padding: 16px; margin: 15px 0; font-family: 'Orbitron', sans-serif !important; font-weight: 600; }
        .nav-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 450px; background: #0b0c10; padding: 8px; box-sizing: border-box; border-top: 2px solid #ff0055; z-index: 999; }
        .nav-grid button { font-size: 9px !important; padding: 10px 2px !important; margin-bottom: 0; font-family: 'Orbitron', sans-serif !important; font-weight: 900; }
        .admin-nav-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-bottom: 15px; }
        .admin-nav-grid button { font-size: 11px !important; padding: 8px 4px !important; font-family: 'Orbitron', sans-serif !important; }
        .alert-success { background: #09211a; border: 1px solid #00ffaa; color: #00ffaa; padding: 12px; border-radius: 10px; margin-bottom: 15px; text-align: center; font-weight: bold; font-family: 'Orbitron', sans-serif !important; }
        .alert-error { background: #2b0c11; border: 1px solid #ff0055; color: #ff0055; padding: 12px; border-radius: 10px; margin-bottom: 15px; text-align: center; font-weight: bold; font-family: 'Orbitron', sans-serif !important; }
    </style>
</head>
<body>
    <div class="running-header-container">
        <marquee class="running-text" scrollamount="5">⚡ MATRIX SECURITY NODES ONLINE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; HARDWARE RE-EVALUATION INTERFACE LAYER: 2026 ACTIVE</marquee>
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

# --- ROUTER TERMINAL MAIN APPLICATION PATHWAY ---
@app.route('/')
def index():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
        
    announcement = query_db("SELECT value FROM system_config WHERE key='system_announcement'", one=True)[0]
    user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (session['current_user'],), one=True)
    wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (0.00, 0.00, '👑 VIP LEVEL 1', 'MX00')
    
    tng_scanner_url = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)[0]
    usdt_address = query_db("SELECT value FROM system_config WHERE key='usdt_address'", one=True)[0]
    
    v1_inc = float(query_db("SELECT value FROM system_config WHERE key='vip1_income'", one=True)[0])
    v2_inc = float(query_db("SELECT value FROM system_config WHERE key='vip2_income'", one=True)[0])
    v3_inc = float(query_db("SELECT value FROM system_config WHERE key='vip3_income'", one=True)[0])
    v2_req = float(query_db("SELECT value FROM system_config WHERE key='vip2_req'", one=True)[0])
    v3_req = float(query_db("SELECT value FROM system_config WHERE key='vip3_req'", one=True)[0])
    
    t1_bonus = float(query_db("SELECT value FROM system_config WHERE key='tier1_bonus_pct'", one=True)[0])
    t2_bonus = float(query_db("SELECT value FROM system_config WHERE key='tier2_bonus_pct'", one=True)[0])
    t3_bonus = float(query_db("SELECT value FROM system_config WHERE key='tier3_bonus_pct'", one=True)[0])
    
    panel = request.args.get('panel', 'Overview')
    today_date = time.strftime("%Y-%m-%d")
    has_approved_deposit = bool(query_db("SELECT id FROM deposits WHERE username=? AND status='Approved'", (session['current_user'],), one=True))

    success_banner = session.pop('success_flash', '')
    error_banner = session.pop('error_flash', '')
    live_feed = generate_live_activity_logs()

    # --- PRIVILEGED ADMINISTRATIVE MASTER HUB CONTROLLER ---
    if session.get('is_admin', False):
        content_html = """
        <h4 style='color:#00f0ff; text-align:center; font-family:"Orbitron"; font-weight:900;'>🛡️ CORE ADMINISTRATIVE MATRIX CONTROL</h4>
        <div class="admin-nav-grid">
            <button onclick="window.location.href='/?panel=Admin_Deposits'">📥 DEPOSITS</button>
            <button onclick="window.location.href='/?panel=Admin_Configs'">⚙️ SYSTEM</button>
            <button onclick="window.location.href='/?panel=Admin_Users'">👤 USER CONFIG</button>
            <button onclick="window.location.href='/?panel=Admin_Withdraws'">💰 CASH OUTS</button>
            <button onclick="window.location.href='/?panel=Admin_Campaigns'">📢 CAMPAIGNS</button>
            <button onclick="window.location.href='/?panel=Admin_Tickets'">🎫 TICKETS</button>
        </div>
        <hr style="border-color:#ff0055; opacity:0.3; margin-bottom:20px;">
        """
        
        if panel == 'Admin_Deposits' or panel == 'Overview':
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            if not pending_items: content_html += "<p style='text-align:center;color:#a0a0a5;font-family:\"Orbitron\";'>Verification queue empty.</p>"
            for item in pending_items:
                content_html += f"""
                <div style='background-color:#12131a; padding:18px; border-radius:14px; border:2px solid #ff0055; margin-bottom:12px; font-family:"Orbitron";'>
                    <div style='font-family:"Orbitron"; font-size:14px; color:#00f0ff; font-weight:900;'>📥 INCOMING PROOF NODE</div>
                    User Terminal: <b>{item[1]}</b><br>
                    Payment Link: <span style='color:#a100ff; font-weight:bold;'>{item[2]}</span><br>
                    Holder Reference: <b>{item[3]}</b><br>
                    Hash Code ID: <code style='color:#00f0ff;'>{item[4]}</code><br>
                    TOTAL DISPATCH: <b style='color:#ff0055; font-size:18px;'>RM {item[5]:.2f}</b>
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <button onclick="window.location.href='/action_deposit?id={item[0]}&status=Approved'" style="padding:8px !important; font-size:12px !important;">✅ CONFIRM DEPOSIT</button>
                        <button onclick="window.location.href='/action_deposit?id={item[0]}&status=Rejected'" style="background:red !important; padding:8px !important; font-size:12px !important;">❌ VOID DROP</button>
                    </div>
                </div>
                """
        elif panel == 'Admin_Configs':
            content_html += f"""
            <form method="POST" action="/update_sys_configs" style='font-family:"Orbitron";'>
                <h5 style='font-weight:900;'>🛠️ Global Variable Mutation Grid</h5>
                <label>System Alert Announcement Box:</label>
                <textarea name="announcement" rows="3">{announcement}</textarea>
                <label>Touch 'N Go Master Scan Link Image Asset:</label>
                <input type="text" name="tng_url" value="{tng_scanner_url}">
                <label>System Decentralized USDT Target Address:</label>
                <input type="text" name="usdt" value="{usdt_address}">
                <label>VIP 2 Minimum Target Threshold Requirement (RM):</label>
                <input type="number" step="0.01" name="vip2_req" value="{v2_req}">
                <label>VIP 3 Minimum Target Threshold Requirement (RM):</label>
                <input type="number" step="0.01" name="vip3_req" value="{v3_req}">
                <label>Tier-1 Referral Commission Level (%):</label>
                <input type="number" step="0.1" name="t1_bonus" value="{t1_bonus}">
                <label>Tier-2 Referral Commission Level (%):</label>
                <input type="number" step="0.1" name="t2_bonus" value="{t2_bonus}">
                <label>Tier-3 Referral Commission Level (%):</label>
                <input type="number" step="0.1" name="t3_bonus" value="{t3_bonus}">
                <button type="submit">COMMIT MUTATION UPDATE</button>
            </form>
            """
        elif panel == 'Admin_Users':
            content_html += """
            <form method="POST" action="/update_user_balance" style='font-family:"Orbitron";'>
                <h5 style='font-weight:900;'>👤 PLATFORM BALANCE DISPATCH CONTROL</h5>
                <input type="text" name="target_user" placeholder="ENTER SYSTEM TARGET USER EMAIL" required>
                <input type="number" step="0.01" name="new_balance" placeholder="SET ACCOUNT VAULT BALANCE (RM)" required>
                <button type="submit">🔥 COMMIT ACCOUNT LIQUID MUTATION</button>
            </form>
            """
        elif panel == 'Admin_Withdraws':
            pending_with = query_db("SELECT id, username, bank, account, amount FROM withdrawals WHERE status='Pending'")
            if not pending_with: content_html += "<p style='text-align:center;color:#a0a0a5;font-family:\"Orbitron\";'>No withdrawal configurations pending.</p>"
            for w_item in pending_with:
                content_html += f"""
                <div style='background-color:#12131a; padding:15px; border-radius:12px; border:2px solid #a100ff; margin-bottom:10px; font-family:"Orbitron";'>
                    <b>Terminal Address:</b> {w_item[1]}<br>
                    <b>Routing Target Node:</b> {w_item[2]} | Code: {w_item[3]}<br>
                    <span style='color:#ff0055;'><b>VAL OUTFLOW: RM {w_item[4]:.2f}</b></span>
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <button onclick="window.location.href='/action_withdraw?id={w_item[0]}&status=Approved'" style="padding:6px !important; font-size:12px !important;">✅ CONFIRM TRANSFERS</button>
                        <button onclick="window.location.href='/action_withdraw?id={w_item[0]}&status=Rejected'" style="background:red !important; padding:6px !important; font-size:12px !important;">❌ REJECT & REFUND</button>
                    </div>
                </div>
                """
        elif panel == 'Admin_Campaigns':
            pending_camps = query_db("SELECT id, advertiser_email, video_url, target_views, trx_id FROM ad_campaigns WHERE status='Pending'")
            if not pending_camps: content_html += "<p style='text-align:center;color:#a0a0a5;font-family:\"Orbitron\";'>No video campaigns currently active.</p>"
            for camp in pending_camps:
                content_html += f"""
                <div style='background-color:#12131a; padding:15px; border-radius:12px; border:2px solid #00f0ff; margin-bottom:10px; font-family:"Orbitron";'>
                    <b>Advertiser Node:</b> {camp[1]} | Target Count: {camp[3]}<br>
                    Verification Hash: <code>{camp[4]}</code><br>
                    <a href='{camp[2]}' target='_blank' style='color:#00f0ff;'>👉 Stream Verification Target URL Link</a>
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <button onclick="window.location.href='/action_campaign?id={camp[0]}&status=Approved'" style="padding:6px !important; font-size:12px !important;">✅ VERIFY RUN</button>
                        <button onclick="window.location.href='/action_campaign?id={camp[0]}&status=Rejected'" style="background:red !important; padding:6px !important; font-size:12px !important;">❌ KILL STREAM</button>
                    </div>
                </div>
                """
        elif panel == 'Admin_Tickets':
            pending_tickets = query_db("SELECT id, username, subject, message FROM support_tickets WHERE status='Pending'")
            if not pending_tickets: content_html += "<p style='text-align:center;color:#a0a0a5;font-family:\"Orbitron\";'>All tickets clean.</p>"
            for ticket in pending_tickets:
                content_html += f"""
                <form method="POST" action="/reply_ticket" style='background-color:#12131a; padding:15px; border-radius:12px; border:2px solid #ff0055; margin-bottom:10px; font-family:"Orbitron";'>
                    <input type="hidden" name="ticket_id" value="{ticket[0]}">
                    <b>Ticket Identifier Ref #{ticket[0]} - Source:</b> {ticket[1]}<br>
                    <b>Thematic Category:</b> {ticket[2]}<br>
                    <p style='background:#0b0c10; padding:8px; border-radius:6px;'>{ticket[3]}</p>
                    <textarea name="reply_text" placeholder="Write System Administrator Resolution Details..." required></textarea>
                    <button type="submit">🚀 SEND DISPATCH RESPONSE</button>
                </form>
                """

        content_html += '<button onclick="window.location.href=\'/logout\'" style="margin-top:30px; background:red !important; font-family:\'Orbitron\'; font-weight:900;">TERMINATE MASTER ACCESS PORTAL</button>'
        return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", content_html), dynamic_ticker=live_feed, msg_success=success_banner, msg_error=error_banner)

    # --- CLIENT TERMINAL SYSTEM INTERFACE ---
    content_html = f"""
    <div class="brand-title">𝗚𝗟𝗢𝗕𝗔𝗟 <b><b>𝗠𝗔𝗧𝗥𝗜𝗫</b></b></div>
    <div class="announcement-box">{announcement}</div>
    
    <div class="metric-card-box" style='font-family:"Orbitron";'>
        <p style="font-size:12px; color:#ff0055; margin:0; font-weight:900; letter-spacing:1px;">⚡ ACCOUNT ENGINE NET LIQUIDITY</p>
        <h1 style="font-size:38px; font-weight:900; color:#ffffff; margin:8px 0; letter-spacing:1px;">RM {wallet_bal:,.2f}</h1>
        <p style="color:#00f0ff; margin:0; font-weight:900; font-size:13px; letter-spacing:0.5px;">TIER NODE: {level_tag} &nbsp;|&nbsp; RISK BUFFER: RM {liquid_bal:.2f}</p>
        <p style="color:#a100ff; margin:5px 0 0 0; font-weight:900; font-size:12px; letter-spacing:1px;">SYSTEM CODE SHIFT HASH: {reference_hash}</p>
    </div>
    """

    if panel == 'Overview':
        already_spun = query_db("SELECT username FROM lucky_spins WHERE username=? AND date=?", (session['current_user'], today_date), one=True)
        content_html += "<p style='font-family:\"Orbitron\"; font-weight:900; font-size:14px; color:#a100ff; text-align:center;'>🎡 MATRIX SECTOR SYSTEM LUCKY WHEEL</p>"
        
        if already_spun:
            content_html += "<div class='custom-matrix-box-cyan' style='text-align:center; color:#00f0ff;'>✅ TODAY'S LUCKY SECTOR CONVERSION COMPLETED</div>"
        else:
            content_html += f"""
            <div style="text-align:center; background:#12131a; padding:15px; border-radius:14px; border:2px solid #a100ff; margin-bottom:15px;">
                <canvas id="wheelCanvas" width="240" height="240" style="border:4px solid #00f0ff; border-radius:50%; background:#0b0c10; transition: transform 4s cubic-bezier(0.1, 0.8, 0.3, 1);"></canvas>
                <button id="spinBtn" style="margin-top:10px;">🎰 RE-ROUTE LUCKY MATRIX CANVAS WHEEL</button>
            </div>
            <script>
                const ctx = document.getElementById('wheelCanvas').getContext('2d');
                const labels = ["RM0.50", "RM2.00", "RM0.10", "RM5.00", "RM0.20", "RM10.00", "RM1.50", "DRAIN"];
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
        content_html += "<p style='font-family:\"Orbitron\"; font-weight:900; font-size:13px; color:#ff0055;'>🎁 CRYPTO DAILY MATRIX CHECK-IN</p>"
        
        if not has_approved_deposit:
            content_html += "<div class='custom-matrix-box-pink' style='text-align:center; color:#ff0055;'>🔒 SECURITY SHIELD LOCKED: Initial validation node approval required to check-in.</div>"
        else:
            if already_checked: content_html += "<p style='color:#00f0ff; font-weight:bold; text-align:center;'>✅ REWARD BLOCK CLAIMED FOR TODAY</p>"
            else: content_html += '<button onclick="window.location.href=\'/claim_checkin\'">INITIALIZE REWARD HASH CONVERSION (RM 0.50)</button>'

        content_html += f"""
        <hr style='border-color:#ff0055; opacity:0.2; margin:15px 0;'>
        <p style='font-family:"Orbitron"; font-size:14px; font-weight:900;'>👑 VIP MATRIX NETWORK NODES</p>
        <div class='custom-matrix-box-cyan'><div style='display:flex; justify-content:space-between;'><span>👑 𝐕𝐈𝐏 𝐋𝐄𝐕𝐄𝐋 𝟏 (Base Stream)</span><span style='color:#00f0ff;'>Yield: RM {v1_inc:.2f}</span></div></div>
        <div class='custom-matrix-box-pink'><div style='display:flex; justify-content:space-between;'><span>👑 𝐕𝐈𝐏 𝐋𝐄𝐕𝐄𝐋 𝟐 (Min Req: RM {v2_req:.2f})</span><span style='color:#ff0055;'>Yield: RM {v2_inc:.2f}</span></div></div>
        <div class='custom-matrix-box-purple'><div style='display:flex; justify-content:space-between;'><span>👑 𝐕𝐈𝐏 𝐋𝐄𝐕𝐄𝐋 𝟑 (Min Req: RM {v3_req:.2f})</span><span style='color:#a100ff;'>Yield: RM {v3_inc:.2f}</span></div></div>
        """

        content_html += "<hr style='border-color:#ff0055; opacity:0.2; margin:20px 0;'><p style='font-family:\"Orbitron\"; font-size:14px; font-weight:900; text-align:center;'>🎬 ACTIVE DECENTRALIZED MULTI-VIDEO TRAFFIC ADS</p>"
        if not has_approved_deposit:
            content_html += "<div class='custom-matrix-box-pink' style='text-align:center; color:#ff0055;'>🔒 SYSTEM SECURITY ACCESS SHIELD ACTIVE: Active validation deposit required to decrypt traffic feeds.</div>"
        else:
            for i in range(1, 6):
                ad_url = query_db(f"SELECT value FROM system_config WHERE key='ad{i}_url'", one=True)[0]
                ad_rew = float(query_db(f"SELECT value FROM system_config WHERE key='ad{i}_reward'", one=True)[0])
                ad_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id=? AND date=?", (session['current_user'], f'ad{i}', today_date), one=True)
                box_cls = "custom-matrix-box-cyan" if i % 2 != 0 else "custom-matrix-box-pink"
                content_html += f"""
                <div class="{box_cls}" style="text-align:center;">
                    <b>Traffic Ad Interface Vector Block {i}</b><br>Yield Allocation: RM {ad_rew:.2f}<br>
                """
                if ad_watched: content_html += "<span style='color:#00f0ff; font-weight:bold;'>✅ BLOCK METRIC RESOLVED</span></div>"
                else:
                    content_html += f"""
                    <a href="{ad_url}" target="_blank" class="btn-link" style="padding:6px; font-size:12px; background:#00f0ff !important; color:#000 !important; margin-top:5px;">📺 RESOLVE TRAFFIC FEED LINK</a>
                    <button onclick="window.location.href='/claim_ad?ad_id=ad{i}&rew={ad_rew}'" style="padding:6px; font-size:12px; margin-top:3px;">💰 EXTRACT REWARD VALUE</button>
                </div>
                """

    elif panel == 'Deposit':
        content_html += f"""
        <h5 style='font-family:"Orbitron"; color:#00f0ff; font-weight:900;'>DEPOSIT VALIDATION ENTRY CONTROL</h5>
        <div style='text-align:center; margin-bottom:15px;'><img src='{tng_scanner_url}' width='140' style='border:2px solid #00f0ff; border-radius:12px;'/></div>
        <div style='background:#1a090d; border:1px solid #a100ff; padding:12px; border-radius:10px; margin-bottom:12px; font-family:"Orbitron";'>
            <span style='color:#a100ff; font-weight:bold;'>📢 TARGET USDT DECENTRALIZED NETWORK STORAGE NODE:</span><br><code style='word-break:break-all;color:#00f0ff;'>{usdt_address}</code>
        </div>
        <form method="POST" action="/submit_deposit">
            <select name="bank">{"".join([f"<option>{b}</option>" for b in MALAYSIAN_BANKS])}</select>
            <input type="text" name="name" placeholder="ACCOUNT SENDER FULL NAME REFERENCE" required>
            <input type="text" name="trx_id" placeholder="TRANSACTION RECEIPT HASH KEY CODE / TXID ID" required>
            <input type="number" step="0.01" name="amount" value="100.0" required>
            <button type="submit">TRANSMIT DEPOSIT PROOF IDENTIFIER</button>
        </form>
        """

    elif panel == 'Cashout':
        content_html += f"""
        <h5 style='font-family:"Orbitron"; color:#00f0ff; font-weight:900;'>EXECUTE SECURE PLATFORM BALANCE EXIT</h5>
        <form method="POST" action="/submit_cashout">
            <select name="bank">{"".join([f"<option>{b}</option>" for b in MALAYSIAN_BANKS])}</select>
            <input type="text" name="account" placeholder="Enter Target Transfer Route Number / Account Number" required>
            <input type="number" step="0.01" name="amount" placeholder="Total Exit Settle Amount (RM)" required>
            <button type="submit">INITIATE OUTFLOW VERIFICATION TRANSFERS</button>
        </form>
        """

    elif panel == 'Promote_Video' or panel == 'Promote':
        content_html += """
        <h5 style='font-family:"Orbitron"; color:#00f0ff; font-weight:900;'>📢 SELF-SERVICE TRAFFIC AD CAMPAIGN GENERATOR</h5>
        <form method="POST" action="/submit_campaign">
            <input type="email" name="adv_email" placeholder="Your Security Registered Target Email Address" required>
            <input type="text" name="video_url" placeholder="YouTube Video URL Interface Route" required>
            <input type="number" name="views_req" placeholder="Target Views Metric Wanted (Minimum Level 100)" min="100" required>
            <input type="text" name="payment_trx" placeholder="Transaction Receipt Reference Code Token ID" required>
            <button type="submit">🚀 DISPATCH CAMPAIGN FOR VERIFICATION LINK</button>
        </form>
        """

    elif panel == 'Support_Helpdesk':
        content_html += """
        <h5 style='font-family:"Orbitron"; color:#00f0ff; font-weight:900;'>🎫 SECURE DECENTRALIZED TERMINAL HELPDESK</h5>
        <form method="POST" action="/submit_ticket">
            <input type="text" name="subject" placeholder="Ticket Category Topic (Masla Kya Hai)" required>
            <textarea name="message" placeholder="Provide Comprehensive Technical Glitch Details (Tafseel Likhein)" rows="4" required></textarea>
            <button type="submit">🚀 DISPATCH TECHNICAL TICKET</button>
        </form>
        <hr style='border-color:#ff0055; opacity:0.2; margin:20px 0;'>
        <b style='font-family:"Orbitron";'>Your Archive Ticket History Feed:</b>
        """
        user_tickets = query_db("SELECT id, subject, message, reply, status FROM support_tickets WHERE username=? ORDER BY id DESC", (session['current_user'],))
        if not user_tickets: content_html += "<p style='color:#a0a0a5;text-align:center;font-family:\"Orbitron\";'>No tickets logged inside this network sector.</p>"
        for t in user_tickets:
            border_clr = "#ff0055" if t[4] == "Pending" else "#00f0ff"
            content_html += f"""
            <div style='background-color:#12131a; padding:15px; border-radius:12px; border:2px solid {border_clr}; margin-bottom:10px; font-family:"Orbitron";'>
                <b>{t[1]}</b> <span style='color:{border_clr};'>[{t[4].upper()}]</span>
                <p style='color:#a0a0a5; font-size:14px; margin:5px 0;'><b>Dispatched Narrative:</b> {t[2]}</p>
                {f"<div style='background:#0b0c10; padding:8px; border-radius:6px; border-left:3px solid #00f0ff;'><b>Administrator Response Log:</b> {t[3]}</div>" if t[3] else ""}
            </div>
            """

    content_html += f"""
    <div class="nav-grid">
        <button onclick="window.location.href='/?panel=Overview'">CORE HUB</button>
        <button onclick="window.location.href='/?panel=Deposit'">INFLOW</button>
        <button onclick="window.location.href='/?panel=Cashout'">OUTFLOW</button>
        <button onclick="window.location.href='/?panel=Promote'">PROMOTE</button>
        <button onclick="window.location.href='/?panel=Support_Helpdesk'">HELPDESK</button>
    </div>
    """
    return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", content_html), dynamic_ticker=live_feed, msg_success=success_banner, msg_error=error_banner)


# --- IDENTITY VALIDATION CRYPTO SIGN-IN NODES & OTP INTEGRITY SYSTEM ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    success_banner = session.pop('success_flash', '')
    error_banner = session.pop('error_flash', '')
    live_feed = generate_live_activity_logs()
    
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','').strip()
        if username == "Mani" and password == "MANI2662":
            session['logged_in'] = True
            session['current_user'] = "Mani"
            session['is_admin'] = True
            return redirect(url_for('index'))
        else:
            record = query_db("SELECT password, username FROM users WHERE username=?", (username,), one=True)
            if record and record[0] == password:
                session['logged_in'] = True
                session['current_user'] = record[1]
                session['is_admin'] = False
                return redirect(url_for('index'))
            else:
                error_banner = "❌ SECURE CREDENTIAL MISMATCH ACCESSED DENIED"
    
    login_html = """
    <div class="brand-title">𝗚𝗟𝗢𝗕𝗔𝗟 <b><b>𝗠𝗔𝗧𝗥𝗜𝗫</b></b></div>
    <div class="brand-subtitle">SECURE TERMINAL LOG ENTRY ACCESS</div>
    
    <form method="POST">
        <input type="text" name="username" placeholder="SECURITY ACCREDITED EMAIL IDENTIFIER" required>
        <input type="password" name="password" placeholder="VAULT KEY PASSCODE" required>
        <button type="submit">AUTHORIZE IDENTITY LOG ENTRY</button>
    </form>
    
    <hr style="border-color:#ff0055; opacity:0.1; margin: 25px 0;">
    
    <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 15px;">
        <button onclick="window.location.href='/login'" style="background: linear-gradient(135deg, #ff0055 0%, #a100ff 100%) !important; text-align: left; padding-left: 20px !important;">🆔 LOGIN ID</button>
        <button onclick="window.location.href='/register'" style="background: linear-gradient(135deg, #ff0055 0%, #a100ff 100%) !important; text-align: left; padding-left: 20px !important;">🎮 CREATE ACCOUNT</button>
        <button onclick="window.location.href='/?panel=Support_Helpdesk'" style="background: linear-gradient(135deg, #ff0055 0%, #a100ff 100%) !important; text-align: left; padding-left: 20px !important;">🔑 FORGET PASSWORD</button>
    </div>
    """
    return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", login_html), dynamic_ticker=live_feed, msg_success=success_banner, msg_error=error_banner)


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
            if exists: error_banner = "❌ Vector Fault: Target entry identity already indexed."
            else:
                otp = str(random.randint(100000, 999999))
                if send_verification_email(email, otp, "Registration"):
                    session['reg_email'] = email
                    session['reg_pass'] = password
                    session['reg_ref'] = referral
                    session['reg_otp'] = otp
                    success_banner = "🔑 Security Token Verification code dispatched to terminal node."
                else: error_banner = "❌ Infrastructure Gateway Fault: SMTP handshake dropped."
        elif step == '2':
            user_otp = request.form.get('otp_code','').strip()
            if user_otp == session.get('reg_otp'):
                generated_ref = "MX" + str(random.randint(1000, 9999))
                query_db("INSERT INTO users VALUES (?, ?, 0.0, 0.0, '👑 VIP LEVEL 1', ?, ?)",
                         (session['reg_email'], session['reg_pass'], generated_ref, session['reg_ref']), commit=True)
                session['success_flash'] = "✅ Identity Mapping Logged! Login to continue."
                return redirect(url_for('login'))
            else: error_banner = "❌ Verification Refused: Security hash code misaligned."

    if 'reg_otp' in session:
        reg_html = """
        <div class="brand-title">𝗚𝗟𝗢𝗕𝗔𝗟 <b><b>𝗠𝗔𝗧𝗥𝗜𝗫</b></b></div>
        <div class="brand-subtitle">VERIFY REGISTRATION IDENTITY HASH</div>
        <form method="POST">
            <input type="hidden" name="step" value="2">
            <input type="text" name="otp_code" placeholder="ENTER VALIDATION 6-DIGIT SECURITY OTP" required>
            <button type="submit">⚡ REGISTER CODE INTEGRITY</button>
        </form>
        """
    else:
        reg_html = """
        <div class="brand-title">𝗚𝗟𝗢𝗕𝗔𝗟 <b><b>𝗠𝗔𝗧𝗥𝗜𝗫</b></b></div>
        <div class="brand-subtitle">INITIALIZE MATRIX ACCREDITATION LOG</div>
        <form method="POST">
            <input type="hidden" name="step" value="1">
            <input type="email" name="username" placeholder="YOUR INTENDED TARGET ROUTE EMAIL" required>
            <input type="password" name="password" placeholder="SET ACCOUNT HARDWARE SECURITY PASSWORD" required>
            <input type="text" name="referral" placeholder="UPSTREAM ACCREDITATION REFERRAL CODE (OPTIONAL)">
            <button type="submit">🔒 DISPATCH SECURITY TOKEN HANDSHAKE EMAIL</button>
        </form>
        <div style="text-align:center; margin-top:15px; font-family:'Orbitron';">
            <a href="/login" style="color:#00f0ff; text-decoration:none;">Return to Portal Sign In Entry</a>
        </div>
        """
    return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", reg_html), dynamic_ticker=live_feed, msg_success=success_banner, msg_error=error_banner)


# --- LOGISTICS CORE BUSINESS TRANSACTION LOGIC HANDLERS ---
@app.route('/claim_spin')
def claim_spin():
    if 'logged_in' in session:
        prizes = [0.50, 2.00, 0.10, 5.00, 0.20, 10.00, 1.50, 0.00]
        win_amt = random.choice(prizes)
        today = time.strftime("%Y-%m-%d")
        query_db("INSERT OR IGNORE INTO lucky_spins VALUES (?, ?, ?)", (session['current_user'], today, win_amt), commit=True)
        query_db("UPDATE users SET balance = balance + ? WHERE username=?", (win_amt, session['current_user']), commit=True)
        session['success_flash'] = f"🎰 Wheel Conversion Complete: Added +RM {win_amt:.2f} to storage."
    return redirect(url_for('index'))

@app.route('/claim_checkin')
def claim_checkin():
    if 'logged_in' in session:
        today = time.strftime("%Y-%m-%d")
        query_db("INSERT OR IGNORE INTO checkins VALUES (?, ?)", (session['current_user'], today), commit=True)
        query_db("UPDATE users SET balance = balance + 0.50 WHERE username=?", (session['current_user'],), commit=True)
        session['success_flash'] = "✅ Network Node Status Verified! Check-in RM 0.50 credited."
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
        session['success_flash'] = f"💰 Matrix Traffic Segment Decrypted! +RM {rew:.2f} assigned."
    return redirect(url_for('index'))

@app.route('/submit_deposit', methods=['POST'])
def submit_deposit():
    if 'logged_in' in session:
        query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                 (session['current_user'], request.form.get('bank'), request.form.get('name'), request.form.get('trx_id'), request.form.get('amount')), commit=True)
        session['success_flash'] = "🚀 Inflow Proof Dispatched for verification."
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
            session['success_flash'] = "✅ Capital exit configurations submitted."
        else: session['error_flash'] = "❌ Request Terminated: Insufficient fluid volume."
    return redirect(url_for('index'))

@app.route('/submit_campaign', methods=['POST'])
def submit_campaign():
    if 'logged_in' in session:
        query_db("INSERT INTO ad_campaigns (advertiser_email, video_url, target_views, trx_id, status) VALUES (?, ?, ?, ?, 'Pending')",
                 (request.form.get('adv_email'), request.form.get('video_url'), request.form.get('views_req'), request.form.get('payment_trx')), commit=True)
        session['success_flash'] = "📢 Advertiser target metadata received."
    return redirect(url_for('index'))

@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():
    if 'logged_in' in session:
        query_db("INSERT INTO support_tickets (username, subject, message, reply, status) VALUES (?, ?, ?, '', 'Pending')",
                 (session['current_user'], request.form.get('subject'), request.form.get('message')), commit=True)
        session['success_flash'] = "🎫 Technical support payload routed."
    return redirect(url_for('index', panel='Support_Helpdesk'))

# --- CORE EXECUTIVE MASTER BOARD MUTATION HANDLERS ---
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

@app.route('/action_campaign')
def action_campaign():
    if session.get('is_admin', False):
        query_db("UPDATE ad_campaigns SET status=? WHERE id=?", (request.args.get('status'), request.args.get('id')), commit=True)
    return redirect(url_for('index', panel='Admin_Campaigns'))

@app.route('/reply_ticket', methods=['POST'])
def reply_ticket():
    if session.get('is_admin', False):
        query_db("UPDATE support_tickets SET reply=?, status='Resolved' WHERE id=?", (request.form.get('reply_text'), request.form.get('ticket_id')), commit=True)
    return redirect(url_for('index', panel='Admin_Tickets'))

@app.route('/update_sys_configs', methods=['POST'])
def update_sys_configs():
    if session.get('is_admin', False):
        query_db("UPDATE system_config SET value=? WHERE key='system_announcement'", (request.form.get('announcement'),), commit=True)
        query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (request.form.get('tng_url'),), commit=True)
        query_db("UPDATE system_config SET value=? WHERE key='usdt_address'", (request.form.get('usdt'),), commit=True)
        query_db("UPDATE system_config SET value=? WHERE key='vip2_req'", (request.form.get('vip2_req'),), commit=True)
        query_db("UPDATE system_config SET value=? WHERE key='vip3_req'", (request.form.get('vip3_req'),), commit=True)
        query_db("UPDATE system_config SET value=? WHERE key='tier1_bonus_pct'", (request.form.get('t1_bonus'),), commit=True)
        query_db("UPDATE system_config SET value=? WHERE key='tier2_bonus_pct'", (request.form.get('t2_bonus'),), commit=True)
        query_db("UPDATE system_config SET value=? WHERE key='tier3_bonus_pct'", (request.form.get('t3_bonus'),), commit=True)
    return redirect(url_for('index', panel='Admin_Configs'))

@app.route('/update_user_balance', methods=['POST'])
def update_user_balance():
    if session.get('is_admin', False):
        target = request.form.get('target_user').strip()
        new_bal = request.form.get('new_balance')
        query_db("UPDATE users SET balance=? WHERE username=?", (new_bal, target), commit=True)
        sync_user_vip_tier(target)
    return redirect(url_for('index', panel='Admin_Users'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
