import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
import calendar
from google.oauth2.service_account import Credentials
from datetime import datetime, date, timedelta
import uuid

st.set_page_config(
    page_title="FinFlow", page_icon="💸", layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={}
)

SCOPES     = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "ExpenseTrackerDB"
cur        = "₹"

# ─────────────────────────────────────────
# THEME
# ─────────────────────────────────────────
st.markdown("""
<style>
:root{
  --bg:#0d0d1a; --bg2:#121225; --bg3:#16162a;
  --surface:rgba(255,255,255,0.03);
  --border:rgba(255,255,255,0.06);
  --accent:#6c63ff; --green:#00d4aa; --red:#ff6b6b; --warn:#ffb703;
  --text:#f0f0ff; --muted:#7777aa;
  --r:18px;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
}
*{box-sizing:border-box; transition:background .12s,border-color .12s,transform .12s,box-shadow .12s;}
html,body,[class*="css"]{font-family:var(--font)!important;background:var(--bg)!important;color:var(--text)!important;}
h1,h2,h3{font-weight:800!important;letter-spacing:-.5px;}
#MainMenu,footer,header{visibility:hidden!important;}
[data-testid="stDecoration"]{display:none!important;}
.stSidebar{display:none!important;}
::-webkit-scrollbar{width:3px;} ::-webkit-scrollbar-thumb{background:var(--accent);border-radius:2px;}
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"], .main, .stApp { background: #0d0d1a !important; }
.block-container > div { animation: none !important; }
.block-container{max-width:480px!important;padding:8px 10px 90px!important;margin:0 auto!important;}
[data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:4px!important;}
[data-testid="stHorizontalBlock"] > div{min-width:0!important;flex:1!important;}
button[data-testid="baseButton-secondary"]{
  background:var(--surface)!important;border:1px solid var(--border)!important;
  color:var(--muted)!important;border-radius:12px!important;
  font-size:11px!important;font-weight:500!important;
  padding:7px 4px!important;white-space:pre-wrap!important;line-height:1.3!important;
  box-shadow:none!important;animation:none!important;
}
button[data-testid="baseButton-secondary"]:hover{
  background:rgba(108,99,255,.1)!important;color:var(--accent)!important;
  border-color:rgba(108,99,255,.3)!important;transform:none!important;
}
button[data-testid="baseButton-primary"]{
  background:linear-gradient(135deg,var(--accent),var(--green))!important;
  border:none!important;color:#fff!important;font-weight:700!important;
  border-radius:12px!important;animation:none!important;
}
.kpi-row{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0;}
.js-plotly-plot,.plotly{max-width:100%!important;overflow:hidden!important;}
@media(max-width:520px){
  .hero-amt{font-size:30px!important;} .kpi-val{font-size:17px!important;}
  .wc-bal{font-size:22px!important;} .tx-title{font-size:13px!important;}
  .sec-hd{margin:12px 0 7px!important;} .block-container{padding:6px 8px 88px!important;}
}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes glow{0%,100%{box-shadow:0 0 0 0 rgba(108,99,255,.5)}50%{box-shadow:0 0 18px 4px rgba(108,99,255,.2)}}
@keyframes floatOrb{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-20px) scale(1.08)}}
.hero-card{
  background:linear-gradient(135deg,#1a1a3e 0%,#0f0f28 60%,#141428 100%);
  border:1px solid rgba(108,99,255,.25);border-radius:24px;padding:24px 20px 20px;
  position:relative;overflow:hidden;animation:fadeUp .45s ease both;margin-bottom:14px;
}
.hero-card::before{content:'';position:absolute;top:-50px;right:-50px;width:180px;height:180px;
  border-radius:50%;background:radial-gradient(circle,rgba(108,99,255,.15) 0%,transparent 70%);
  animation:floatOrb 7s ease-in-out infinite;pointer-events:none;}
.hero-card::after{content:'';position:absolute;bottom:-30px;left:-30px;width:120px;height:120px;
  border-radius:50%;background:radial-gradient(circle,rgba(0,212,170,.1) 0%,transparent 70%);pointer-events:none;}
.hero-label{font-size:11px;color:var(--muted);letter-spacing:1.5px;text-transform:uppercase;margin:0;}
.hero-amt{font-size:36px;font-weight:800;margin:4px 0 0;
  background:linear-gradient(90deg,#fff 0%,var(--green) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.1;}
.hero-pills{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap;}
.hero-pill{border-radius:30px;padding:5px 12px;font-size:12px;font-weight:600;}
.hp-inc{color:var(--green);border:1px solid rgba(0,212,170,.25);background:rgba(0,212,170,.08);}
.hp-exp{color:var(--red);border:1px solid rgba(255,107,107,.25);background:rgba(255,107,107,.08);}
.hp-net{border:1px solid rgba(255,183,3,.25);background:rgba(255,183,3,.08);}
.kpi-card{
  background:linear-gradient(135deg,rgba(255,255,255,.05) 0%,rgba(255,255,255,.02) 100%);
  border:1px solid var(--border);border-radius:var(--r);padding:16px 14px;
  text-align:center;position:relative;overflow:hidden;animation:fadeUp .5s ease both;
}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--kpi-c),transparent);}
.kpi-card:hover{transform:translateY(-3px);box-shadow:0 10px 30px rgba(0,0,0,.35);}
.kpi-icon{font-size:22px;margin-bottom:4px;}
.kpi-lbl{font-size:11px;color:var(--muted);margin:0;}
.kpi-val{font-size:20px;font-weight:800;margin:4px 0 0;}
.kpi-delta{font-size:10px;margin-top:3px;}
.sec-hd{display:flex;justify-content:space-between;align-items:center;margin:18px 0 10px;}
.sec-hd h3{font-size:15px;margin:0;font-weight:700;}
.tx-card{
  background:var(--surface);border:1px solid var(--border);border-radius:15px;
  padding:12px 14px;display:flex;align-items:center;gap:11px;
  animation:fadeUp .35s ease both;margin-bottom:8px;
}
.tx-card:hover{background:rgba(108,99,255,.07);border-color:rgba(108,99,255,.25);transform:translateX(2px);}
.tx-icon{width:38px;height:38px;min-width:38px;border-radius:11px;display:flex;align-items:center;
  justify-content:center;font-size:16px;
  background:linear-gradient(135deg,rgba(108,99,255,.2),rgba(0,212,170,.1));}
.tx-body{flex:1;min-width:0;}
.tx-title{font-size:14px;font-weight:600;margin:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.tx-meta{font-size:11px;color:var(--muted);margin:2px 0 0;}
.tx-amt{font-size:15px;font-weight:700;white-space:nowrap;}
.tx-amt.exp{color:var(--red);} .tx-amt.inc{color:var(--green);} .tx-amt.trf{color:var(--accent);}
.tx-badge{display:inline-block;font-size:9px;padding:2px 6px;border-radius:5px;margin-top:2px;font-weight:600;}
.tb-exp{background:rgba(255,107,107,.12);color:var(--red);}
.tb-inc{background:rgba(0,212,170,.12);color:var(--green);}
.tb-trf{background:rgba(108,99,255,.12);color:var(--accent);}
.budget-item{
  background:var(--surface);border:1px solid var(--border);border-radius:15px;
  padding:13px 14px;margin-bottom:8px;animation:fadeUp .4s ease both;
}
.budget-item:hover{border-color:rgba(108,99,255,.3);}
.b-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;}
.b-name{font-size:13px;font-weight:600;}
.b-pct{font-size:12px;font-weight:700;}
.prog-bg{height:7px;background:rgba(255,255,255,.05);border-radius:7px;overflow:hidden;}
.prog-fill{display:block;height:100%;border-radius:7px;min-width:0;}
.b-nums{display:flex;justify-content:space-between;margin-top:5px;font-size:10px;color:var(--muted);}
.wallet-card{
  background:linear-gradient(145deg,rgba(108,99,255,.13) 0%,rgba(0,212,170,.07) 100%);
  border:1px solid rgba(108,99,255,.2);border-radius:20px;padding:18px 16px;
  margin-bottom:10px;position:relative;overflow:hidden;animation:fadeUp .4s ease both;
}
.wallet-card::after{content:'';position:absolute;top:-40%;right:-40%;width:80%;height:80%;
  border-radius:50%;background:radial-gradient(circle,rgba(108,99,255,.07),transparent 70%);
  animation:floatOrb 6s ease-in-out infinite;pointer-events:none;}
.wallet-card:hover{border-color:rgba(108,99,255,.4);transform:translateY(-2px);}
.wc-type{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin:0 0 3px;}
.wc-name{font-size:17px;font-weight:700;margin:0 0 10px;}
.wc-bal{font-size:26px;font-weight:800;
  background:linear-gradient(90deg,var(--green),var(--accent));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.goal-card{background:var(--surface);border:1px solid var(--border);border-radius:18px;
  padding:16px;margin-bottom:10px;animation:fadeUp .4s ease both;}
.goal-card:hover{border-color:rgba(0,212,170,.3);}
.qa-item{background:var(--surface);border:1px solid var(--border);border-radius:14px;
  padding:10px 6px;text-align:center;animation:fadeUp .4s ease both;}
.qa-item:hover{background:rgba(108,99,255,.1);border-color:var(--accent);}
.qa-icon{font-size:22px;} .qa-lbl{font-size:11px;font-weight:600;margin:2px 0 0;}
.qa-amt{font-size:10px;color:var(--muted);}
.streak-card{
  background:linear-gradient(135deg,rgba(255,183,3,.1),rgba(255,107,107,.07));
  border:1px solid rgba(255,183,3,.22);border-radius:16px;padding:14px 16px;
  display:flex;align-items:center;gap:12px;margin-bottom:12px;animation:fadeUp .4s ease both;}
.streak-num{font-size:30px;font-weight:800;color:var(--warn);line-height:1;}
.forecast-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;
  padding:14px 16px;margin-bottom:10px;animation:fadeUp .5s ease both;}
.empty{text-align:center;padding:36px 16px;border:1px dashed rgba(108,99,255,.22);
  border-radius:18px;animation:fadeUp .5s ease;}
.empty .ei{font-size:38px;margin-bottom:8px;}
.empty h4{font-size:15px;margin:0 0 4px;}
.empty p{font-size:12px;color:var(--muted);margin:0;}
[data-testid="stPopover"]>button{
  background:linear-gradient(135deg,var(--red),#ff8e53)!important;
  color:#fff!important;font-weight:800!important;border-radius:50px!important;
  border:none!important;padding:11px 20px!important;font-size:18px!important;
  box-shadow:0 6px 24px rgba(255,107,107,.4)!important;animation:glow 2s ease infinite!important;}
[data-testid="stPopover"]>button:hover{transform:scale(1.08)!important;}
[data-testid="stSelectbox"]>div>div,
[data-testid="stNumberInput"]>div>div>input,
[data-testid="stTextInput"]>div>div>input,
[data-testid="stDateInput"]>div>div>input,
[data-testid="stTimeInput"]>div>div>input{
  background:var(--bg3)!important;border:1px solid var(--border)!important;
  color:var(--text)!important;border-radius:10px!important;}
[data-testid="stExpander"]{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:14px!important;}
[data-testid="stDataFrame"]{border-radius:14px!important;overflow:hidden;}
hr{border-color:var(--border)!important;margin:14px 0!important;}
[data-testid="stAlert"]{border-radius:12px!important;}
[data-testid="stMetricValue"]{font-weight:800!important;background:linear-gradient(45deg,var(--green),var(--accent));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
/* NAV */
section.main div.block-container > div > div > div:first-child > div[data-testid="stHorizontalBlock"] {
  position:fixed!important;bottom:0!important;left:50%!important;transform:translateX(-50%)!important;
  width:100%!important;max-width:480px!important;z-index:9990!important;
  background:rgba(13,13,26,0.97)!important;backdrop-filter:blur(20px)!important;
  border-top:1px solid rgba(255,255,255,0.08)!important;
  padding:4px 2px env(safe-area-inset-bottom,4px)!important;margin:0!important;gap:0!important;}
section.main div.block-container > div > div > div:first-child > div[data-testid="stHorizontalBlock"] > div {
  flex:1!important;min-width:0!important;padding:0!important;}
section.main div.block-container > div > div > div:first-child > div[data-testid="stHorizontalBlock"] button {
  background:transparent!important;border:none!important;border-radius:8px!important;
  color:#7777aa!important;font-size:9px!important;font-weight:600!important;
  padding:6px 1px 4px!important;white-space:pre!important;line-height:1.4!important;
  box-shadow:none!important;animation:none!important;min-height:52px!important;width:100%!important;}
section.main div.block-container > div > div > div:first-child > div[data-testid="stHorizontalBlock"] button:hover {
  background:rgba(108,99,255,0.1)!important;color:#6c63ff!important;transform:none!important;}
section.main div.block-container > div > div > div:first-child > div[data-testid="stHorizontalBlock"] button[kind="primary"] {
  background:rgba(108,99,255,0.15)!important;color:#6c63ff!important;
  border-top:2px solid #6c63ff!important;border-radius:0 0 8px 8px!important;}
/* LOGIN / INPUT */
[data-testid="stSelectbox"] div[data-baseweb="select"] div,
[data-testid="stSelectbox"] div[data-baseweb="select"] span { color:var(--text)!important; }
ul[data-testid="stSelectboxVirtualDropdown"] li { color:var(--text)!important;background:var(--bg2)!important; }
ul[data-testid="stSelectboxVirtualDropdown"] li:hover { background:rgba(108,99,255,.15)!important; }
[data-testid="stTextInput"] input { color:var(--text)!important;-webkit-text-fill-color:var(--text)!important; }
[data-testid="stTextInput"] input::placeholder { color:var(--muted)!important;-webkit-text-fill-color:var(--muted)!important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# GSHEET CONNECTION
# ─────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def connect_gsheet():
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
    except Exception:
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    return gspread.authorize(creds).open(SHEET_NAME)

def _ws(sheet_name):
    return connect_gsheet().worksheet(sheet_name)

@st.cache_data(ttl=300, show_spinner=False)
def batch_fetch_all():
    NAMES = ["Expenses","Wallets","ExpenseCategories","RecurringTemplates","Users"]
    try:
        sh = connect_gsheet()
        ranges = [f"{n}!A:ZZ" for n in NAMES]
        result = sh.values_batch_get(ranges)
        vr = result.get("valueRanges", [])
        out = {}
        for i, name in enumerate(NAMES):
            try:
                rows = vr[i].get("values", []) if i < len(vr) else []
                if not rows: out[name] = pd.DataFrame(); continue
                headers = rows[0]
                out[name] = pd.DataFrame(
                    [r + [""]*(len(headers)-len(r)) for r in rows[1:]], columns=headers)
            except Exception:
                out[name] = pd.DataFrame()
        return out
    except Exception:
        sh = connect_gsheet(); out = {}
        for name in NAMES:
            try: out[name] = pd.DataFrame(sh.worksheet(name).get_all_records())
            except Exception: out[name] = pd.DataFrame()
        return out

def read_sheet(sheet_name):
    return batch_fetch_all().get(sheet_name, pd.DataFrame())

def _invalidate_data_cache():
    try: batch_fetch_all.clear()
    except Exception: pass
    try: load_all_data.clear()
    except Exception: pass
    for k in ["expenses_df","wallets_df","categories_df","recurring_df",
              "data_loaded","exp_only","inc_only"]:
        st.session_state.pop(k, None)

def clear_cache():
    _invalidate_data_cache()

def append_row(sheet_name, row_dict):
    try:
        ws = _ws(sheet_name)
        headers = ws.row_values(1)
        ws.append_row([row_dict.get(h,"") for h in headers], table_range="A1")
        clear_cache(); return True
    except Exception as e:
        st.error(f"Write error: {e}"); return False

def update_cell(sheet_name, row_index, col_name, value):
    try:
        ws = _ws(sheet_name)
        headers = ws.row_values(1)
        if col_name in headers:
            ws.update_cell(row_index+1, headers.index(col_name)+1, value)
        clear_cache(); return True
    except Exception as e:
        st.error(f"Update error: {e}"); return False

def update_row_cells(sheet_name, row_index, updates):
    try:
        ws = _ws(sheet_name)
        headers = ws.row_values(1)
        cells = []
        for col, val in updates.items():
            if col in headers:
                c = ws.cell(row_index+1, headers.index(col)+1)
                c.value = val; cells.append(c)
        if cells: ws.update_cells(cells)
        clear_cache(); return True
    except Exception as e:
        st.error(f"Batch update error: {e}"); return False

def delete_row(sheet_name, row_index):
    try:
        _ws(sheet_name).delete_rows(row_index+1)
        clear_cache(); return True
    except Exception as e:
        st.error(f"Delete error: {e}"); return False

def save_default_wallet(uid, wallet_name, wal_df):
    """Save DefaultWalletName + DefaultWalletId to Users sheet using actual column names."""
    try:
        ws = _ws("Users")
        headers = ws.row_values(1)
        users_raw = batch_fetch_all().get("Users", pd.DataFrame())
        if users_raw.empty or "UserId" not in users_raw.columns:
            return
        urow = users_raw[users_raw["UserId"].astype(str) == uid]
        if urow.empty:
            return
        ridx = int(urow.index[0]) + 2   # +1 for header, +1 for 0-index
        wallet_id = ""
        if not wal_df.empty and "WalletName" in wal_df.columns:
            wr = wal_df[wal_df["WalletName"] == wallet_name]
            if not wr.empty:
                wallet_id = str(wr.iloc[0].get("WalletId",""))
        cells = []
        for col, val in [("DefaultWalletName", wallet_name), ("DefaultWalletId", wallet_id)]:
            if col in headers:
                c = ws.cell(ridx, headers.index(col)+1)
                c.value = val; cells.append(c)
        if cells:
            ws.update_cells(cells)
        try: batch_fetch_all.clear()
        except Exception: pass
    except Exception:
        pass

def delete_old_data(uid, password, users_raw):
    """Delete expenses older than 1 year for user after password verification."""
    if users_raw.empty or "UserId" not in users_raw.columns:
        return False, "Could not load user data."
    urow = users_raw[users_raw["UserId"].astype(str) == uid]
    if urow.empty:
        return False, "User not found."
    db_pass = str(urow.iloc[0].get("PasswordHash",""))
    if db_pass != password:
        return False, "Wrong password."
    try:
        ws = _ws("Expenses")
        vals = ws.get_all_values()
        if len(vals) <= 1:
            return True, "No expense data found."
        headers = vals[0]
        df = pd.DataFrame(vals[1:], columns=headers)
        if df.empty:
            return True, "No expense data found."
        df["_date"] = pd.to_datetime(df.get("ExpenseDate",""), errors="coerce").dt.date
        cutoff = (datetime.now() - timedelta(days=365)).date()
        old_mask = (df["UserId"].astype(str) == uid) & (df["_date"] < cutoff)
        deleted = int(old_mask.sum())
        if deleted == 0:
            return True, "No data older than 1 year found."
        keep_df = df[~old_mask].drop(columns=["_date"])
        ws.clear()
        ws.update("A1", [headers] + keep_df.fillna("").astype(str).values.tolist())
        clear_cache()
        return True, f"Deleted {deleted} transaction(s) older than 1 year."
    except Exception as e:
        return False, f"Error: {e}"

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def ist_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def time_ago(d):
    if not d: return ""
    delta = date.today() - d
    if delta.days == 0: return "Today"
    if delta.days == 1: return "Yesterday"
    if delta.days < 7:  return f"{delta.days}d ago"
    if delta.days < 31: return f"{delta.days//7}w ago"
    return d.strftime("%d %b")

CAT_ICONS = {
    "food":"🍔","drink":"🍔","grocer":"🛒","transport":"🚕","cab":"🚕",
    "fuel":"⛽","entertain":"🎬","movie":"🎬","health":"💊","shop":"🛍️",
    "util":"💡","edu":"📚","travel":"✈️","salary":"💼","invest":"📊",
    "transfer":"🔄","adjust":"🔧","other":"📦","rent":"🏠","gym":"💪"
}
def cat_icon(name):
    n = str(name).lower()
    for k,v in CAT_ICONS.items():
        if k in n: return v
    return "💰"

def pct_color(r):
    if r < 0.7: return "var(--green)"
    if r < 0.9: return "var(--warn)"
    return "var(--red)"

def delta_html(curr, prev):
    if prev == 0: return '<span style="color:var(--warn);font-size:10px">↑ New</span>'
    p = (curr - prev) / prev * 100
    if p > 0:  return f'<span style="color:var(--red);font-size:10px">↑ {abs(p):.1f}%</span>'
    if p < 0:  return f'<span style="color:var(--green);font-size:10px">↓ {abs(p):.1f}%</span>'
    return '<span style="color:var(--muted);font-size:10px">→ Same</span>'

# ─────────────────────────────────────────
# SESSION INIT
# ─────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.page      = "Home"
    uid_qp = st.query_params.get("user_id", None)
    if uid_qp:
        try:
            _u = batch_fetch_all().get("Users", pd.DataFrame())
            if not _u.empty and "UserId" in _u.columns:
                row = _u[_u["UserId"].astype(str) == uid_qp]
                if not row.empty:
                    st.session_state.logged_in = True
                    st.session_state.username  = row.iloc[0].get("UserName","User")
                    st.session_state.user_id   = uid_qp
        except Exception:
            pass

_valid_pages = {"Home","Wallets","History","Insights","Profile"}
if "page" not in st.session_state:
    _p = st.query_params.get("p", None)
    st.session_state.page = _p if (_p and _p in _valid_pages) else "Home"

# ─────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────
if not st.session_state.logged_in:
    st.session_state.pop("data_loaded", None)
    st.markdown("""
    <style>
    .login-wrap{max-width:340px;margin:40px auto 0;padding:0 16px;}
    .login-box{background:linear-gradient(145deg,rgba(108,99,255,.12),rgba(0,212,170,.06));
      border:1px solid rgba(108,99,255,.22);border-radius:24px;padding:32px 24px 28px;text-align:center;}
    .l-logo{font-size:44px;margin-bottom:6px;} .l-title{font-size:26px;font-weight:800;margin:0 0 4px;}
    .l-sub{font-size:13px;color:var(--muted);margin:0 0 24px;}
    </style>
    <div class="login-wrap"><div class="login-box">
      <div class="l-logo">💸</div><div class="l-title">FinFlow</div>
      <div class="l-sub">Premium Expense Tracker</div>
    </div></div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        _u = batch_fetch_all().get("Users", pd.DataFrame())
    except Exception:
        _u = pd.DataFrame()
    usernames = _u["UserName"].tolist() if not _u.empty and "UserName" in _u.columns else []
    if not usernames:
        st.warning("No users found in sheet."); st.stop()
    sel = st.selectbox("👤 Select User", usernames)
    pwd = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
    if st.button("Sign In →", use_container_width=True, type="primary"):
        row = _u[_u["UserName"] == sel]
        if not row.empty:
            db = str(row.iloc[0].get("PasswordHash",""))
            if db == pwd or (db == "" and pwd == ""):
                st.session_state.logged_in = True
                st.session_state.username  = sel
                st.session_state.user_id   = str(row.iloc[0].get("UserId", sel))
                saved_pw = str(row.iloc[0].get("DefaultWalletName",""))
                if saved_pw:
                    st.session_state["_saved_pw_from_login"] = saved_pw
                st.query_params["user_id"] = st.session_state.user_id
                st.query_params["p"]       = "Home"
                update_cell("Users", int(row.index[0])+1, "LastLogin", str(datetime.now()))
                st.rerun()
            else: st.error("Wrong password")
        else: st.error("User not found")
    st.stop()

# ─────────────────────────────────────────
# DATA LOAD
# ─────────────────────────────────────────
uid = str(st.session_state.user_id)

@st.cache_data(ttl=300, show_spinner=False)
def load_all_data(uid):
    sheets = batch_fetch_all()
    raw_e = sheets.get("Expenses",          pd.DataFrame())
    raw_w = sheets.get("Wallets",           pd.DataFrame())
    raw_c = sheets.get("ExpenseCategories", pd.DataFrame())
    raw_r = sheets.get("RecurringTemplates",pd.DataFrame())

    exp = pd.DataFrame()
    if not raw_e.empty and "UserId" in raw_e.columns:
        exp = raw_e[raw_e["UserId"].astype(str) == uid].copy()
        if not exp.empty:
            exp["ExpenseDate"] = pd.to_datetime(exp["ExpenseDate"], errors="coerce").dt.date
            exp["Amount"]      = pd.to_numeric(exp["Amount"], errors="coerce").fillna(0)
            # Keep only last 60 days for fast loading
            cutoff = (datetime.now() - timedelta(days=60)).date()
            exp = exp[exp["ExpenseDate"] >= cutoff].copy()

    wal = pd.DataFrame()
    if not raw_w.empty and "UserId" in raw_w.columns:
        wal = raw_w[raw_w["UserId"].astype(str) == uid].copy()

    cat = pd.DataFrame()
    if not raw_c.empty:
        if "UserId" in raw_c.columns:
            cat = raw_c[(raw_c["UserId"].astype(str) == uid) | (raw_c["UserId"] == "")].copy()
        else:
            cat = raw_c.copy()

    rec = pd.DataFrame()
    if not raw_r.empty and "UserId" in raw_r.columns:
        rec = raw_r[raw_r["UserId"].astype(str) == uid].copy()

    return exp, wal, cat, rec

@st.cache_data(ttl=300, show_spinner=False)
def fetch_expenses_range(uid, start_date, end_date):
    """Fetch full date range directly — used for Insights custom range only."""
    try:
        ws = _ws("Expenses")
        df = pd.DataFrame(ws.get_all_records())
        if df.empty: return pd.DataFrame()
        df = df[df["UserId"].astype(str) == uid].copy()
        df["ExpenseDate"] = pd.to_datetime(df["ExpenseDate"], errors="coerce").dt.date
        df["Amount"]      = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        return df[(df["ExpenseDate"] >= start_date) & (df["ExpenseDate"] <= end_date)].copy()
    except Exception:
        return pd.DataFrame()

if "expenses_df" not in st.session_state:
    st.markdown("""
    <style>
    @keyframes skel{0%{opacity:.35}50%{opacity:.7}100%{opacity:.35}}
    .sk{background:rgba(255,255,255,.05);border-radius:12px;animation:skel 1.3s ease-in-out infinite;}
    .sk-hero{height:138px;margin-bottom:14px;}
    .sk-row{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;}
    .sk-kpi{height:78px;} .sk-bar{height:54px;margin-bottom:8px;} .sk-tx{height:52px;margin-bottom:8px;}
    </style>
    <div class="sk sk-hero"></div>
    <div class="sk-row"><div class="sk sk-kpi"></div><div class="sk sk-kpi"></div>
    <div class="sk sk-kpi"></div><div class="sk sk-kpi"></div></div>
    <div class="sk sk-bar"></div><div class="sk sk-bar"></div>
    <div class="sk sk-tx"></div><div class="sk sk-tx"></div><div class="sk sk-tx"></div>
    """, unsafe_allow_html=True)
    _e, _w, _c, _r = load_all_data(uid)
    st.session_state["expenses_df"]   = _e
    st.session_state["wallets_df"]    = _w
    st.session_state["categories_df"] = _c
    st.session_state["recurring_df"]  = _r
    st.session_state["data_loaded"]   = True
    st.rerun()

expenses_df   = st.session_state["expenses_df"]
wallets_df    = st.session_state["wallets_df"]
categories_df = st.session_state["categories_df"]
recurring_df  = st.session_state["recurring_df"]

if "exp_only" not in st.session_state:
    st.session_state["exp_only"] = (
        expenses_df[expenses_df["EntryType"] == "Expense"].copy()
        if not expenses_df.empty else pd.DataFrame())
    st.session_state["inc_only"] = (
        expenses_df[expenses_df["EntryType"] == "Income"].copy()
        if not expenses_df.empty else pd.DataFrame())
exp_only = st.session_state["exp_only"]
inc_only = st.session_state["inc_only"]

today       = ist_now().date()
cur_month   = f"{today.year}-{today.month:02d}"
month_start = today.replace(day=1)
week_start  = today - timedelta(days=today.weekday())

w_list    = wallets_df["WalletName"].tolist() if not wallets_df.empty and "WalletName" in wallets_df.columns else ["Default"]
w_display = [w.split("|")[0] for w in w_list]

# Resolve default wallet: login value → GSheet → first wallet
if "preferred_wallet" not in st.session_state:
    resolved = ""
    saved_from_login = st.session_state.pop("_saved_pw_from_login","")
    if saved_from_login and saved_from_login in w_display:
        resolved = saved_from_login
    if not resolved:
        try:
            _users_raw = batch_fetch_all().get("Users", pd.DataFrame())
            if not _users_raw.empty and "UserId" in _users_raw.columns and "DefaultWalletName" in _users_raw.columns:
                _urow = _users_raw[_users_raw["UserId"].astype(str) == uid]
                if not _urow.empty:
                    _pw = str(_urow.iloc[0].get("DefaultWalletName",""))
                    if _pw and _pw in w_display:
                        resolved = _pw
        except Exception:
            pass
    st.session_state.preferred_wallet = resolved if resolved else (w_display[0] if w_display else "")

pref_stored = next((w for w in w_list if w.split("|")[0] == st.session_state.preferred_wallet),
                   w_list[0] if w_list else "")
cat_list = categories_df["CategoryName"].tolist() if not categories_df.empty and "CategoryName" in categories_df.columns else ["Others"]

# ─────────────────────────────────────────
# BOTTOM NAV
# ─────────────────────────────────────────
NAV_ITEMS = [("🏠","Home",""),("💳","Wallets",""),("📒","History",""),("📈","Insights",""),("🧑🏻‍💼","Profile","")]

def _set_page(name):
    st.session_state.page = name
    st.query_params["p"]  = name

page = st.session_state.get("page","Home")
_nav_cols = st.columns(5)
for _col, (_icon, _name, _label) in zip(_nav_cols, NAV_ITEMS):
    with _col:
        st.button(
            f"{_icon}\n{_label}", key=f"nav_{_name}",
            use_container_width=True,
            type="primary" if (page == _name) else "secondary",
            on_click=_set_page, args=(_name,)
        )
page = st.session_state.get("page","Home")

# ─────────────────────────────────────────
# ADD TRANSACTION FORM
# ─────────────────────────────────────────
def add_transaction_form(key_pfx="fab"):
    st.markdown("#### ➕ New Transaction")
    now   = ist_now()
    etype = st.selectbox("Type", ["Expense","Income","Transfer"], key=f"{key_pfx}_type")
    c1,c2 = st.columns(2)
    with c1: tx_date = st.date_input("Date", now.date(), key=f"{key_pfx}_date")
    with c2: tx_time = st.time_input("Time", now.time(), key=f"{key_pfx}_time")
    amount = st.number_input(f"Amount ({cur})", min_value=0.0, format="%.2f", key=f"{key_pfx}_amt")

    if etype == "Transfer":
        fw    = st.selectbox("From Wallet", w_list, key=f"{key_pfx}_fw")
        tw    = st.selectbox("To Wallet",   w_list, index=min(1,len(w_list)-1), key=f"{key_pfx}_tw")
        notes = st.text_input("Notes", key=f"{key_pfx}_notes")
        neg_ok = True
        if fw == tw: st.warning("Same wallet!")
        elif amount > 0 and not wallets_df.empty:
            wf = wallets_df[wallets_df["WalletName"]==fw]
            if not wf.empty:
                fb = float(wf.iloc[0].get("CurrentBalance",0))
                if fb - amount < 0:
                    st.warning(f"⚠️ Will go negative: {cur}{fb-amount:,.2f}")
                    neg_ok = st.checkbox("Proceed anyway", key=f"{key_pfx}_neg")
        if st.button("Execute Transfer ↔", type="primary", key=f"{key_pfx}_exec", use_container_width=True):
            if amount > 0 and fw != tw and neg_ok:
                wfr = wallets_df[wallets_df["WalletName"]==fw].iloc[0]
                wto = wallets_df[wallets_df["WalletName"]==tw].iloc[0]
                update_cell("Wallets", int(wfr.name)+1, "CurrentBalance", float(wfr.get("CurrentBalance",0))-amount)
                update_cell("Wallets", int(wto.name)+1, "CurrentBalance", float(wto.get("CurrentBalance",0))+amount)
                append_row("Expenses", {
                    "ExpenseId":str(uuid.uuid4()),"UserId":uid,"EntryType":"Transfer",
                    "ExpenseDate":str(tx_date),"ExpenseTime":str(tx_time),
                    "CategoryName":"Internal Transfer",
                    "ExpenseTitle":f"{fw.split('|')[0]} → {tw.split('|')[0]}",
                    "ExpenseNotes":notes,"Amount":amount,
                    "WalletId":wfr.get("WalletId",""),"WalletName":fw,
                    "TransactionType":"Transfer","CreatedAt":str(datetime.now())
                })
                _invalidate_data_cache(); st.success("Transfer done!"); st.rerun()
    else:
        wallet   = st.selectbox("Wallet", w_list, key=f"{key_pfx}_wal")
        inc_opts = ["Salary","Bonus","Freelance","Investment","Gift","Other"]
        category = st.selectbox("Category", cat_list if etype=="Expense" else inc_opts, key=f"{key_pfx}_cat")
        title    = st.text_input("Title", key=f"{key_pfx}_title")
        notes    = st.text_input("Notes", key=f"{key_pfx}_notes2")
        tags     = st.text_input("Tags (comma sep.)", key=f"{key_pfx}_tags")
        is_recur = st.checkbox("🔁 Recurring", key=f"{key_pfx}_rec")
        freq     = st.selectbox("Frequency",["Daily","Weekly","Monthly"],key=f"{key_pfx}_freq") if is_recur else None
        neg_ok   = True
        if etype=="Expense" and amount > 0 and not wallets_df.empty:
            wc = wallets_df[wallets_df["WalletName"]==wallet]
            if not wc.empty:
                wb = float(wc.iloc[0].get("CurrentBalance",0))
                if wb - amount < 0:
                    st.warning(f"⚠️ Will go negative: {cur}{wb-amount:,.2f}")
                    neg_ok = st.checkbox("Proceed anyway", key=f"{key_pfx}_neg2")
        if st.button("Save Transaction ✓", type="primary", key=f"{key_pfx}_save", use_container_width=True):
            if amount > 0 and neg_ok:
                wr  = wallets_df[wallets_df["WalletName"]==wallet] if not wallets_df.empty else pd.DataFrame()
                wid = wr.iloc[0].get("WalletId","") if not wr.empty else ""
                cr  = categories_df[categories_df["CategoryName"]==category] if not categories_df.empty and etype=="Expense" else pd.DataFrame()
                cid = cr.iloc[0].get("CategoryId","") if not cr.empty else ""
                append_row("Expenses", {
                    "ExpenseId":str(uuid.uuid4()),"UserId":uid,"EntryType":etype,
                    "ExpenseDate":str(tx_date),"ExpenseTime":str(tx_time),
                    "CategoryId":cid,"CategoryName":category,
                    "ExpenseTitle":title,"ExpenseNotes":notes,"Amount":amount,
                    "WalletId":wid,"WalletName":wallet,
                    "TransactionType":"Manual","Tags":tags,"CreatedAt":str(datetime.now())
                })
                if not wr.empty:
                    cb = float(wr.iloc[0].get("CurrentBalance",0))
                    update_cell("Wallets", int(wr.index[0])+1, "CurrentBalance",
                                cb - amount if etype=="Expense" else cb + amount)
                if is_recur and freq:
                    nd = tx_date + timedelta(days=1 if freq=="Daily" else 7 if freq=="Weekly" else 30)
                    append_row("RecurringTemplates",{
                        "TemplateId":str(uuid.uuid4()),"UserId":uid,
                        "Title":title or category,"Amount":amount,
                        "CategoryName":category,"WalletName":wallet,
                        "Frequency":freq,"NextDue":str(nd),"IsActive":"True",
                        "CreatedAt":str(datetime.now())
                    })
                _invalidate_data_cache(); st.success("✅ Saved!"); st.rerun()
            else:
                st.error("Enter a valid amount.")

# ═══════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════
if page == "Home":
    h = ist_now().hour
    greet = "Good Morning" if h<12 else "Good Afternoon" if h<17 else "Good Evening"
    st.markdown(f"<p style='font-size:13px;color:var(--muted);margin:6px 0 2px'>{greet} 👋</p>"
                f"<h2 style='margin:0 0 12px'>{st.session_state.username}</h2>",
                unsafe_allow_html=True)

    # Hero
    total_assets = pd.to_numeric(wallets_df["CurrentBalance"],errors="coerce").sum() if not wallets_df.empty and "CurrentBalance" in wallets_df.columns else 0

    def month_sum(df):
        if df.empty or "ExpenseDate" not in df.columns: return 0
        return df[df["ExpenseDate"].apply(
            lambda x: f"{x.year}-{x.month:02d}" if pd.notnull(x) else "") == cur_month]["Amount"].sum()

    m_exp = month_sum(exp_only)
    m_inc = month_sum(inc_only)
    net   = m_inc - m_exp
    net_c = "var(--green)" if net >= 0 else "var(--red)"

    st.markdown(f"""
    <div class="hero-card">
      <p class="hero-label">Total Net Worth</p>
      <p class="hero-amt">{cur}{total_assets:,.2f}</p>
      <p style="font-size:12px;color:var(--muted);margin:6px 0 0">
        {len(wallets_df) if not wallets_df.empty else 0} wallets · Updated just now</p>
      <div class="hero-pills">
        <span class="hero-pill hp-inc">↑ {cur}{m_inc:,.0f} income</span>
        <span class="hero-pill hp-exp">↓ {cur}{m_exp:,.0f} spent</span>
        <span class="hero-pill hp-net" style="color:{net_c}">⚡ {cur}{abs(net):,.0f} {'saved' if net>=0 else 'over'}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # Streak
    streak = 0
    if not exp_only.empty and not categories_df.empty and "MonthlyLimit" in categories_df.columns:
        daily_bud = pd.to_numeric(categories_df["MonthlyLimit"],errors="coerce").sum() / 30
        if daily_bud > 0:
            d = today
            for _ in range(60):
                if exp_only[exp_only["ExpenseDate"]==d]["Amount"].sum() <= daily_bud:
                    streak += 1; d -= timedelta(days=1)
                else: break
    if streak > 0:
        st.markdown(f"""
        <div class="streak-card">
          <div class="streak-num">🔥{streak}</div>
          <div><p style="font-size:14px;font-weight:700;color:var(--warn);margin:0 0 2px">Day streak!</p>
            <p style="font-size:11px;color:var(--muted);margin:0">Under daily budget for {streak} days straight</p></div>
        </div>""", unsafe_allow_html=True)

    # Forecast
    if not exp_only.empty and today.day > 0:
        projected = (m_exp / today.day) * 30
        total_lim_fc = pd.to_numeric(categories_df["MonthlyLimit"],errors="coerce").fillna(0).sum() if not categories_df.empty and "MonthlyLimit" in categories_df.columns else 0
        fc     = "var(--green)" if total_lim_fc == 0 or projected <= total_lim_fc else "var(--red)"
        status = "🟢 On track" if total_lim_fc == 0 or projected <= total_lim_fc else "🔴 Over-pace"
        st.markdown(f"""
        <div class="forecast-card">
          <p style="font-size:11px;color:var(--muted);margin:0 0 3px;text-transform:uppercase;letter-spacing:1px">Month-End Forecast</p>
          <p style="font-size:22px;font-weight:800;color:{fc};margin:0">{cur}{projected:,.0f}</p>
          <p style="font-size:11px;color:var(--muted);margin:4px 0 0">{status} · based on {today.day}-day burn rate</p>
        </div>""", unsafe_allow_html=True)

    # Burn rate + Required spend rate
    days_in_month    = calendar.monthrange(today.year, today.month)[1]
    days_remaining   = max(days_in_month - today.day, 1)
    daily_rate       = m_exp / today.day if today.day > 0 else 0
    total_lim_bud    = pd.to_numeric(categories_df["MonthlyLimit"],errors="coerce").fillna(0).sum() if not categories_df.empty and "MonthlyLimit" in categories_df.columns else 0
    remaining_budget = max(total_lim_bud - m_exp, 0) if total_lim_bud > 0 else 0
    required_daily   = remaining_budget / days_remaining if total_lim_bud > 0 else 0
    req_label        = f"{cur}{required_daily:,.0f}/day" if total_lim_bud > 0 else "No limit set"
    req_sublabel     = "to stay within budget" if total_lim_bud > 0 else "set a budget limit"

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card" style="--kpi-c:var(--warn)">
        <div class="kpi-icon">📉</div>
        <p class="kpi-lbl">Current Burn Rate</p>
        <p class="kpi-val" style="color:var(--warn);font-size:17px">{cur}{daily_rate:,.0f}<span style="font-size:10px;font-weight:400">/day</span></p>
        <div class="kpi-delta" style="color:var(--muted)">avg over {today.day} day{'s' if today.day!=1 else ''}</div>
      </div>
      <div class="kpi-card" style="--kpi-c:var(--accent)">
        <div class="kpi-icon">🎯</div>
        <p class="kpi-lbl">Required Spend Rate</p>
        <p class="kpi-val" style="color:var(--accent);font-size:17px">{req_label}</p>
        <div class="kpi-delta" style="color:var(--muted)">{req_sublabel} · {days_remaining}d left</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # KPI 4-grid
    tw_sp = exp_only[exp_only["ExpenseDate"]>=week_start]["Amount"].sum() if not exp_only.empty else 0
    lw_sp = exp_only[(exp_only["ExpenseDate"]>=week_start-timedelta(7))&(exp_only["ExpenseDate"]<week_start)]["Amount"].sum() if not exp_only.empty else 0
    td_sp = exp_only[exp_only["ExpenseDate"]==today]["Amount"].sum() if not exp_only.empty else 0
    lm_s  = month_start-timedelta(1); lm_start = lm_s.replace(day=1)
    lm_sp = exp_only[(exp_only["ExpenseDate"]>=lm_start)&(exp_only["ExpenseDate"]<=lm_s)]["Amount"].sum() if not exp_only.empty else 0

    kpi_html = '<div class="kpi-row">'
    for i,(icon,lbl,val,color,dlt) in enumerate([
        ("📉","Spent (Month)", f"{cur}{m_exp:,.0f}", "var(--red)",   delta_html(m_exp,lm_sp)),
        ("📈","Income (Month)",f"{cur}{m_inc:,.0f}", "var(--accent)",""),
        ("📅","This Week",     f"{cur}{tw_sp:,.0f}", "var(--warn)",  delta_html(tw_sp,lw_sp)),
        ("☀️","Today",         f"{cur}{td_sp:,.0f}", "var(--green)", ""),
    ]):
        kpi_html += f"""<div class="kpi-card" style="--kpi-c:{color};animation-delay:{i*.07}s">
          <div class="kpi-icon">{icon}</div><p class="kpi-lbl">{lbl}</p>
          <p class="kpi-val" style="color:{color}">{val}</p><div class="kpi-delta">{dlt}</div></div>"""
    kpi_html += '</div>'
    st.markdown(kpi_html, unsafe_allow_html=True)

    # 7-day sparkline
    if not exp_only.empty:
        last7  = [today-timedelta(days=i) for i in range(6,-1,-1)]
        totals = [exp_only[exp_only["ExpenseDate"]==d]["Amount"].sum() for d in last7]
        fig = go.Figure(go.Scatter(
            x=[d.strftime("%a") for d in last7], y=totals,
            fill="tozeroy", fillcolor="rgba(108,99,255,0.12)",
            line=dict(color="#6c63ff",width=2.5),
            mode="lines+markers", marker=dict(color="#6c63ff",size=5)
        ))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=8,b=0), height=90,
            xaxis=dict(showgrid=False,color="#7777aa",tickfont=dict(size=10),fixedrange=True),
            yaxis=dict(showgrid=False,visible=False,fixedrange=True), showlegend=False
        )
        st.markdown('<div class="sec-hd"><h3>📈 Last 7 Days</h3></div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False,"staticPlot":True})

    # Recurring due today
    if not recurring_df.empty and "NextDue" in recurring_df.columns:
        due = recurring_df[recurring_df["NextDue"].astype(str)==str(today)]
        if not due.empty:
            st.markdown(f'<div class="sec-hd"><h3>🔁 Due Today ({len(due)})</h3></div>', unsafe_allow_html=True)
            if "paid_recurring" not in st.session_state:
                st.session_state["paid_recurring"] = set()
            for rec_idx, (_, r) in enumerate(due.iterrows()):
                tid     = r.get("TemplateId","") or f"rec_{rec_idx}"
                is_paid = tid in st.session_state["paid_recurring"]
                amt_r   = float(r.get("Amount",0))
                st.markdown(f"""
                <div class="tx-card">
                  <div class="tx-icon">🔁</div>
                  <div class="tx-body"><p class="tx-title">{r.get('Title','')}</p>
                    <p class="tx-meta">{r.get('Frequency','')} · {r.get('WalletName','')}</p></div>
                  <div><span class="tx-amt exp">-{cur}{amt_r:,.0f}</span></div>
                </div>""", unsafe_allow_html=True)
                if is_paid:
                    st.button("✅ Paid", key=f"rec_paid_btn_{tid}_{rec_idx}", disabled=True, use_container_width=True)
                else:
                    if st.button(f"💸 Pay — {r.get('Title','')}", key=f"rec_pay_btn_{tid}_{rec_idx}",
                                 type="primary", use_container_width=True):
                        r_wallet = r.get("WalletName","")
                        wr = wallets_df[wallets_df["WalletName"]==r_wallet] if not wallets_df.empty else pd.DataFrame()
                        wid = wr.iloc[0].get("WalletId","") if not wr.empty else ""
                        now_r = ist_now()
                        append_row("Expenses",{
                            "ExpenseId":str(uuid.uuid4()),"UserId":uid,"EntryType":"Expense",
                            "ExpenseDate":str(now_r.date()),"ExpenseTime":str(now_r.time()),
                            "CategoryName":r.get("CategoryName",""),"ExpenseTitle":r.get("Title",""),
                            "ExpenseNotes":"Recurring payment","Amount":amt_r,
                            "WalletId":wid,"WalletName":r_wallet,
                            "TransactionType":"Recurring","Tags":"recurring","CreatedAt":str(datetime.now())
                        })
                        if not wr.empty:
                            cb_r = float(wr.iloc[0].get("CurrentBalance",0))
                            update_cell("Wallets",int(wr.index[0])+1,"CurrentBalance",cb_r-amt_r)
                        freq_r = r.get("Frequency","Monthly")
                        nd_r   = now_r.date() + timedelta(days=1 if freq_r=="Daily" else 7 if freq_r=="Weekly" else 30)
                        match_r = recurring_df[recurring_df["TemplateId"]==tid] if "TemplateId" in recurring_df.columns else pd.DataFrame()
                        if not match_r.empty:
                            update_row_cells("RecurringTemplates", int(match_r.index[0])+1,
                                            {"NextDue":str(nd_r),"LastPaid":str(now_r.date())})
                        st.session_state["paid_recurring"].add(tid)
                        _invalidate_data_cache(); st.toast(f"✅ {r.get('Title','')} paid!", icon="✅"); st.rerun()

    # Quick Add
    st.markdown('<div class="sec-hd"><h3>⚡ Quick Add</h3></div>', unsafe_allow_html=True)
    default_sc = [
        {"icon":"☕","label":"Coffee",   "amt":60, "cat":"Food & Drinks"},
        {"icon":"🚕","label":"Cab",      "amt":150,"cat":"Transport"},
        {"icon":"🍔","label":"Lunch",    "amt":120,"cat":"Food & Drinks"},
        {"icon":"🛒","label":"Groceries","amt":500,"cat":"Groceries"},
        {"icon":"⛽","label":"Fuel",     "amt":200,"cat":"Transport"},
        {"icon":"🎬","label":"Movie",    "amt":300,"cat":"Entertainment"},
    ]
    shortcuts = st.session_state.get("custom_shortcuts", default_sc)
    sc_cols = st.columns(3)
    for i, sc in enumerate(shortcuts):
        with sc_cols[i%3]:
            st.markdown(f"""
            <div class="qa-item">
              <div class="qa-icon">{sc['icon']}</div>
              <div class="qa-lbl">{sc['label']}</div>
              <div class="qa-amt">{cur}{sc['amt']}</div>
            </div>""", unsafe_allow_html=True)
            if st.button("Add", key=f"sc_{i}", use_container_width=True):
                if w_list:
                    wr  = wallets_df[wallets_df["WalletName"]==pref_stored]
                    wid = wr.iloc[0].get("WalletId","") if not wr.empty else ""
                    now = ist_now()
                    append_row("Expenses",{
                        "ExpenseId":str(uuid.uuid4()),"UserId":uid,"EntryType":"Expense",
                        "ExpenseDate":str(now.date()),"ExpenseTime":str(now.time()),
                        "CategoryName":sc["cat"],"ExpenseTitle":sc["label"],
                        "ExpenseNotes":"Quick Add","Amount":sc["amt"],
                        "WalletId":wid,"WalletName":pref_stored,
                        "TransactionType":"Quick","Tags":"quick","CreatedAt":str(datetime.now())
                    })
                    if not wr.empty:
                        cb = float(wr.iloc[0].get("CurrentBalance",0))
                        update_cell("Wallets",int(wr.index[0])+1,"CurrentBalance",cb-sc["amt"])
                    _invalidate_data_cache()
                    st.toast(f"{sc['icon']} {sc['label']} — {cur}{sc['amt']}", icon="✅"); st.rerun()
                else: st.warning("Create a wallet first!")

    # Week/Month spend rate row
    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card" style="--kpi-c:var(--warn)">
        <div class="kpi-icon">📅</div><p class="kpi-lbl">This Week</p>
        <p class="kpi-val" style="color:var(--warn)">{cur}{tw_sp:,.0f}</p>
        <div class="kpi-delta">{delta_html(tw_sp,lw_sp)}</div>
      </div>
      <div class="kpi-card" style="--kpi-c:var(--accent)">
        <div class="kpi-icon">🗓️</div><p class="kpi-lbl">This Month</p>
        <p class="kpi-val" style="color:var(--accent)">{cur}{m_exp:,.0f}</p>
        <div class="kpi-delta">{delta_html(m_exp,lm_sp)}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Budget Progress
    st.markdown('<div class="sec-hd"><h3>📊 Budget Progress</h3></div>', unsafe_allow_html=True)
    is_weekly = st.toggle("🔄 Weekly View", value=False, key="home_tog")

    if not categories_df.empty and "MonthlyLimit" in categories_df.columns:
        total_lim  = pd.to_numeric(categories_df["MonthlyLimit"],errors="coerce").fillna(0).sum()
        if is_weekly: total_lim = round(total_lim/4/10)*10 if total_lim > 0 else 0
        total_used = 0
        if not exp_only.empty:
            if not is_weekly:
                total_used = exp_only[exp_only["ExpenseDate"].apply(
                    lambda x: f"{x.year}-{x.month:02d}" if pd.notnull(x) else "")==cur_month]["Amount"].sum()
            else:
                total_used = exp_only[exp_only["ExpenseDate"]>=week_start]["Amount"].sum()

        if total_lim > 0 or total_used > 0:
            # FIX: compute ratio correctly, cap at 1.0, render as integer percent width
            t_ratio   = min(total_used / total_lim, 1.0) if total_lim > 0 else 1.0
            t_color   = pct_color(t_ratio) if total_lim > 0 else "var(--muted)"
            remaining = max(total_lim - total_used, 0) if total_lim > 0 else 0
            bar_w     = int(round(t_ratio * 100))   # integer pixels-as-percent, no float rounding issues
            pct_disp  = f"{bar_w}%" if total_lim > 0 else "–"
            limit_txt = f"{cur}{total_lim:,.0f}" if total_lim > 0 else "No limit set"
            st.markdown(f"""
            <div class="budget-item" style="border-color:{t_color};margin-bottom:12px;
              background:linear-gradient(135deg,rgba(108,99,255,.07),rgba(0,212,170,.04))">
              <div class="b-row">
                <span class="b-name" style="font-size:14px">📦 Overall Budget</span>
                <span class="b-pct" style="color:{t_color};font-size:14px">{pct_disp}</span>
              </div>
              <div style="height:10px;background:rgba(255,255,255,.05);border-radius:10px;overflow:hidden;">
                <div style="display:block;height:100%;width:{bar_w}%;border-radius:10px;
                  background:linear-gradient(90deg,{t_color},transparent);"></div>
              </div>
              <div style="display:flex;justify-content:space-between;margin-top:7px;font-size:11px">
                <span style="color:{t_color};font-weight:600">Spent: {cur}{total_used:,.0f}</span>
                <span style="color:var(--green);font-weight:600">Left: {cur}{remaining:,.0f}</span>
                <span style="color:var(--muted)">Limit: {limit_txt}</span>
              </div>
            </div>""", unsafe_allow_html=True)

    alerted = st.session_state.get("alerted", set())
    if not categories_df.empty and "CategoryName" in categories_df.columns:
        budget_items = []
        for ci,(_, c) in enumerate(categories_df.iterrows()):
            cname = c["CategoryName"]
            limit = float(c.get("MonthlyLimit",0) or 0)
            if is_weekly: limit = round(limit/4/10)*10
            used  = 0
            if not exp_only.empty:
                if not is_weekly:
                    used = exp_only[(exp_only["CategoryName"]==cname) &
                        (exp_only["ExpenseDate"].apply(lambda x: f"{x.year}-{x.month:02d}" if pd.notnull(x) else "")==cur_month)]["Amount"].sum()
                else:
                    used = exp_only[(exp_only["CategoryName"]==cname) &
                        (exp_only["ExpenseDate"]>=week_start)]["Amount"].sum()
            if limit <= 0 and used == 0: continue
            ratio = min(used/limit,1.0) if limit>0 else 1.0
            color = pct_color(ratio)
            icon  = c.get("Icon","") or cat_icon(cname)
            bar_w_c = int(round(ratio*100))   # FIX: integer width
            ko,kw = f"over_{cname}",f"warn_{cname}"
            if limit>0 and ratio>=1.0 and ko not in alerted:
                st.toast(f"🚨 {cname} budget exceeded!",icon="🚨"); alerted.add(ko)
            elif limit>0 and ratio>=0.8 and kw not in alerted:
                st.toast(f"⚠️ {cname} at {bar_w_c}%",icon="⚠️"); alerted.add(kw)
            st.session_state["alerted"] = alerted
            budget_items.append(f"""<div class="budget-item" style="animation-delay:{ci*.06}s">
              <div class="b-row">
                <span class="b-name">{icon} {cname}</span>
                <span class="b-pct" style="color:{color}">{bar_w_c}%</span>
              </div>
              <div style="height:7px;background:rgba(255,255,255,.05);border-radius:7px;overflow:hidden;">
                <div style="display:block;height:100%;width:{bar_w_c}%;border-radius:7px;
                  background:linear-gradient(90deg,{color},transparent);"></div>
              </div>
              <div class="b-nums"><span>{cur}{used:,.0f} spent</span><span>{cur}{limit:,.0f} limit</span></div>
            </div>""")
        if budget_items:
            st.markdown(
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">'
                + ''.join(budget_items) + '</div>', unsafe_allow_html=True)

    # Recent Transactions
    st.markdown('<div class="sec-hd"><h3>🕒 Recent</h3></div>', unsafe_allow_html=True)
    if not expenses_df.empty:
        sort_c = ["ExpenseDate"]+( ["ExpenseTime"] if "ExpenseTime" in expenses_df.columns else [])
        recent = expenses_df.sort_values(sort_c, ascending=[False]*len(sort_c)).head(5)
        for i,(_,tx) in enumerate(recent.iterrows()):
            etype = tx.get("EntryType","Expense")
            icon  = cat_icon(tx.get("CategoryName",""))
            title = tx.get("ExpenseTitle","") or tx.get("CategoryName","")
            amt   = float(tx.get("Amount",0))
            sign  = "-" if etype=="Expense" else ("+" if etype=="Income" else "↔")
            cls   = "exp" if etype=="Expense" else ("inc" if etype=="Income" else "trf")
            bcls  = "tb-exp" if etype=="Expense" else ("tb-inc" if etype=="Income" else "tb-trf")
            st.markdown(f"""
            <div class="tx-card" style="animation-delay:{i*.06}s">
              <div class="tx-icon">{icon}</div>
              <div class="tx-body"><p class="tx-title">{title}</p>
                <p class="tx-meta">{time_ago(tx.get('ExpenseDate'))} · {tx.get('WalletName','')}</p></div>
              <div style="text-align:right">
                <div class="tx-amt {cls}">{sign}{cur}{amt:,.0f}</div>
                <span class="tx-badge {bcls}">{etype}</span>
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty"><div class="ei">🧾</div><h4>No transactions yet</h4>'
                    '<p>Tap ➕ to add your first one</p></div>', unsafe_allow_html=True)

    _, fc2 = st.columns([5,2])
    with fc2:
        with st.popover("➕ Add"):
            add_transaction_form("home_fab")

# ═══════════════════════════════════════════════════════
# PAGE: WALLETS
# ═══════════════════════════════════════════════════════
elif page == "Wallets":
    st.markdown("<h2>👛 Wallets</h2>", unsafe_allow_html=True)
    if w_display:
        cur_pref_w = st.session_state.preferred_wallet
        pw = st.selectbox("🏠 Default Wallet", w_display,
            index=w_display.index(cur_pref_w) if cur_pref_w in w_display else 0,
            key="pref_wal_sel")
        if pw != cur_pref_w:
            st.session_state.preferred_wallet = pw
            save_default_wallet(uid, pw, wallets_df)
            st.success(f"✅ Default wallet saved: **{pw}**")

    TICONS = {"Cash":"💵","UPI":"📱","Card":"💳","Bank":"🏦","🎯 Goal":"🎯"}
    if not wallets_df.empty and "WalletName" in wallets_df.columns:
        wtype_col = "WalletType" if "WalletType" in wallets_df.columns else None
        reg   = wallets_df[wallets_df[wtype_col]!="🎯 Goal"] if wtype_col else wallets_df
        goals = wallets_df[wallets_df[wtype_col]=="🎯 Goal"]  if wtype_col else pd.DataFrame()
        for i,(_,row) in enumerate(reg.iterrows()):
            bal   = float(row.get("CurrentBalance",0))
            wtype = row.get("WalletType","Cash")
            ti    = TICONS.get(wtype,"💰")
            dname = str(row["WalletName"]).split("|")[0]
            st.markdown(f"""
            <div class="wallet-card" style="animation-delay:{i*.08}s">
              <p class="wc-type">{ti} {wtype}</p>
              <p class="wc-name">{dname}</p>
              <p class="wc-bal">{cur}{bal:,.2f}</p>
            </div>""", unsafe_allow_html=True)
            with st.expander("⚙️ Adjust Balance"):
                nb  = st.number_input("New Balance",value=bal,key=f"nb_{row.get('WalletId','')}")
                rsn = st.text_input("Reason","Correction",key=f"rsn_{row.get('WalletId','')}")
                if st.button("Update",key=f"ubtn_{row.get('WalletId','')}",type="primary"):
                    diff = nb - bal
                    if diff != 0:
                        update_cell("Wallets",int(_)+1,"CurrentBalance",nb)
                        now = ist_now()
                        append_row("Expenses",{
                            "ExpenseId":str(uuid.uuid4()),"UserId":uid,
                            "EntryType":"Income" if diff>0 else "Expense",
                            "ExpenseDate":str(now.date()),"ExpenseTime":str(now.time()),
                            "CategoryName":"Adjustment","ExpenseTitle":"Balance Correction",
                            "ExpenseNotes":rsn,"Amount":abs(diff),
                            "WalletId":row.get("WalletId",""),"WalletName":row["WalletName"],
                            "TransactionType":"Adjustment","CreatedAt":str(datetime.now())
                        })
                        _invalidate_data_cache(); st.success("Updated!"); st.rerun()
        if not goals.empty:
            st.markdown("### 🎯 Savings Goals")
            for i,(_,row) in enumerate(goals.iterrows()):
                parts   = str(row["WalletName"]).split("|")
                gname   = parts[0]
                gtarget = float(parts[1]) if len(parts)>1 else 0
                gsaved  = float(row.get("CurrentBalance",0))
                gratio  = min(gsaved/gtarget,1.0) if gtarget>0 else 0
                gcol    = "var(--green)" if gratio>=1.0 else ("var(--warn)" if gratio>0.5 else "var(--accent)")
                badge   = " 🎉" if gratio>=1.0 else ""
                gw      = int(round(gratio*100))
                st.markdown(f"""
                <div class="goal-card" style="border-color:{gcol};animation-delay:{i*.08}s">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                    <span style="font-size:15px;font-weight:700">🎯 {gname}{badge}</span>
                    <span style="color:{gcol};font-weight:700">{gw}%</span>
                  </div>
                  <div style="height:7px;background:rgba(255,255,255,.05);border-radius:7px;overflow:hidden;">
                    <div style="display:block;height:100%;width:{gw}%;border-radius:7px;
                      background:linear-gradient(90deg,{gcol},transparent);"></div>
                  </div>
                  <div class="b-nums" style="margin-top:6px">
                    <span>Saved: {cur}{gsaved:,.0f}</span><span>Target: {cur}{gtarget:,.0f}</span>
                  </div>
                  {"<p style='text-align:center;color:var(--green);font-weight:700;margin-top:8px'>🎊 Goal Achieved!</p>" if gratio>=1.0 else ""}
                </div>""", unsafe_allow_html=True)
                with st.expander("Allocate / Withdraw"):
                    ng = st.number_input("New Saved Amount",value=gsaved,key=f"gn_{row.get('WalletId','')}")
                    if st.button("Update Goal",key=f"gb_{row.get('WalletId','')}",type="primary"):
                        update_cell("Wallets",int(_)+1,"CurrentBalance",ng)
                        if ng >= gtarget > 0: st.balloons()
                        _invalidate_data_cache(); st.rerun()
    else:
        st.markdown('<div class="empty"><div class="ei">👛</div><h4>No wallets yet</h4>'
                    '<p>Create one below</p></div>', unsafe_allow_html=True)

    st.divider()
    _,wc2 = st.columns([5,2])
    with wc2:
        with st.popover("👛 Add"):
            st.subheader("New Wallet")
            wn = st.text_input("Name",key="wn_new")
            wt = st.selectbox("Type",["Cash","UPI","Card","Bank","🎯 Goal"],key="wt_new")
            wb = st.number_input(f"Initial Balance ({cur})",min_value=0.0,format="%.2f",key="wb_new")
            wg = 0.0
            if wt=="🎯 Goal":
                wg = st.number_input(f"Target ({cur})",min_value=0.0,format="%.2f",key="wg_new")
            if st.button("Create Wallet",type="primary",key="wcreate"):
                if wn:
                    stored = f"{wn}|{int(wg)}" if wt=="🎯 Goal" and wg>0 else wn
                    append_row("Wallets",{
                        "WalletId":str(uuid.uuid4()),"UserId":uid,"WalletName":stored,
                        "WalletType":wt,"CurrentBalance":wb,
                        "ColorHex":"#ffb703" if wt=="🎯 Goal" else "#6c63ff",
                        "IsActive":"True","CreatedAt":str(datetime.now())
                    })
                    _invalidate_data_cache(); st.success(f"'{wn}' created!"); st.rerun()

# ═══════════════════════════════════════════════════════
# PAGE: HISTORY
# ═══════════════════════════════════════════════════════
elif page == "History":
    st.markdown("<h2>🕒 History</h2>", unsafe_allow_html=True)
    search_q = st.text_input("🔍 Search...", key="hist_search",
                              placeholder="Title, category, notes, amount...")
    c1,c2 = st.columns(2)
    with c1: ftype  = st.selectbox("Type",["All","Expense","Income","Transfer"],key="ht")
    with c2: fdays  = st.selectbox("Period",["Last 30d","This Month","This Week","This Year","All Time"],key="hp")
    fwallet = st.selectbox("Wallet",["All"]+w_list,key="hw")

    if not expenses_df.empty:
        hdf = expenses_df.copy()
        if ftype  != "All": hdf = hdf[hdf["EntryType"]==ftype]
        if fwallet!= "All": hdf = hdf[hdf["WalletName"]==fwallet]
        if fdays == "Last 30d":    hdf = hdf[hdf["ExpenseDate"]>=today-timedelta(30)]
        elif fdays == "This Week": hdf = hdf[hdf["ExpenseDate"]>=week_start]
        elif fdays == "This Month":hdf = hdf[hdf["ExpenseDate"]>=month_start]
        elif fdays == "This Year": hdf = hdf[hdf["ExpenseDate"]>=today.replace(month=1,day=1)]
        if search_q:
            q = search_q.lower()
            mask = (hdf.get("ExpenseTitle", pd.Series([""])).astype(str).str.lower().str.contains(q,na=False) |
                    hdf.get("CategoryName", pd.Series([""])).astype(str).str.lower().str.contains(q,na=False) |
                    hdf.get("ExpenseNotes", pd.Series([""])).astype(str).str.lower().str.contains(q,na=False) |
                    hdf.get("Amount",       pd.Series([""])).astype(str).str.contains(q,na=False))
            hdf = hdf[mask]
        sort_c = ["ExpenseDate"]+( ["ExpenseTime"] if "ExpenseTime" in hdf.columns else [])
        hdf = hdf.sort_values(sort_c,ascending=[False]*len(sort_c))
        total_f = hdf[hdf["EntryType"]=="Expense"]["Amount"].sum()
        st.markdown(f"<p style='font-size:12px;color:var(--muted)'>{len(hdf)} transactions · "
                    f"{cur}{total_f:,.2f} total spent</p>", unsafe_allow_html=True)
        for i,(_,tx) in enumerate(hdf.head(50).iterrows()):
            etype = tx.get("EntryType","Expense")
            icon  = cat_icon(tx.get("CategoryName",""))
            title = tx.get("ExpenseTitle","") or tx.get("CategoryName","")
            amt   = float(tx.get("Amount",0))
            sign  = "-" if etype=="Expense" else ("+" if etype=="Income" else "↔")
            cls   = "exp" if etype=="Expense" else ("inc" if etype=="Income" else "trf")
            bcls  = "tb-exp" if etype=="Expense" else ("tb-inc" if etype=="Income" else "tb-trf")
            st.markdown(f"""
            <div class="tx-card" style="animation-delay:{i*.04}s">
              <div class="tx-icon">{icon}</div>
              <div class="tx-body"><p class="tx-title">{title}</p>
                <p class="tx-meta">{time_ago(tx.get('ExpenseDate'))} · {tx.get('WalletName','')} · {tx.get('CategoryName','')}</p></div>
              <div style="text-align:right">
                <div class="tx-amt {cls}">{sign}{cur}{amt:,.0f}</div>
                <span class="tx-badge {bcls}">{etype}</span>
              </div>
            </div>""", unsafe_allow_html=True)
        st.divider()
        csv = hdf.to_csv(index=False).encode()
        st.download_button("📥 Export CSV", csv, f"finflow_{today}.csv","text/csv",use_container_width=True)
        st.markdown("#### ✏️ Edit / Delete")
        st.markdown("*(Check rows to select, then delete or edit below)*")
        hdf2 = hdf.copy(); hdf2.insert(0,"Select",False)
        disp  = ["Select","ExpenseDate","EntryType","CategoryName","ExpenseTitle","Amount","WalletName"]
        avail = [c for c in disp if c in hdf2.columns]
        edited = st.data_editor(hdf2[avail],use_container_width=True,hide_index=True,
                                disabled=disp[1:],
                                column_config={"Select":st.column_config.CheckboxColumn("☑",required=True)})
        sel = edited[edited["Select"]==True].index.tolist()
        if sel:
            bc1,bc2 = st.columns(2)
            with bc1:
                if st.button("🗑️ Delete Selected",type="primary",use_container_width=True):
                    raw = expenses_df
                    for idx in sel:
                        row   = hdf.loc[idx]
                        match = raw[raw["ExpenseId"]==row["ExpenseId"]]
                        if not match.empty:
                            sidx = int(match.index[0])+1
                            wm = wallets_df[wallets_df["WalletName"]==row["WalletName"]]
                            if not wm.empty:
                                cb = float(wm.iloc[0].get("CurrentBalance",0))
                                nb = cb+float(row["Amount"]) if row["EntryType"]=="Expense" else cb-float(row["Amount"])
                                update_cell("Wallets",int(wm.index[0])+1,"CurrentBalance",nb)
                            delete_row("Expenses",sidx)
                    _invalidate_data_cache(); st.success("Deleted!"); st.rerun()
            if len(sel)==1:
                with bc2:
                    with st.popover("✏️ Edit"):
                        tx = hdf.loc[sel[0]]
                        et = st.text_input("Title",value=tx.get("ExpenseTitle",""),key="et")
                        ea = st.number_input(f"Amount ({cur})",value=float(tx.get("Amount",0)),key="ea")
                        en = st.text_input("Notes",value=tx.get("ExpenseNotes",""),key="en")
                        if st.button("Save",type="primary",key="esave"):
                            raw = expenses_df
                            m   = raw[raw["ExpenseId"]==tx["ExpenseId"]]
                            if not m.empty:
                                sidx = int(m.index[0])+1
                                diff = ea - float(tx["Amount"])
                                if diff != 0:
                                    wm = wallets_df[wallets_df["WalletName"]==tx["WalletName"]]
                                    if not wm.empty:
                                        cb = float(wm.iloc[0].get("CurrentBalance",0))
                                        nb = cb-diff if tx["EntryType"]=="Expense" else cb+diff
                                        update_cell("Wallets",int(wm.index[0])+1,"CurrentBalance",nb)
                                update_row_cells("Expenses",sidx,{"ExpenseTitle":et,"Amount":ea,"ExpenseNotes":en})
                                _invalidate_data_cache(); st.success("Updated!"); st.rerun()
    else:
        st.markdown('<div class="empty"><div class="ei">🧾</div><h4>No transactions yet</h4>'
                    '<p>Add some transactions to see them here</p></div>', unsafe_allow_html=True)

    _,hc2 = st.columns([5,2])
    with hc2:
        with st.popover("➕ Add"):
            add_transaction_form("hist_fab")

# ═══════════════════════════════════════════════════════
# PAGE: INSIGHTS
# ═══════════════════════════════════════════════════════
elif page == "Insights":
    st.markdown("<h2>📈 Insights</h2>", unsafe_allow_html=True)
    PLOT_CFG = {"displayModeBar":False,"staticPlot":True}
    PLOT_LAY = dict(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f0f0ff",size=10),
        margin=dict(t=10,b=0,l=0,r=0),
        xaxis=dict(showgrid=False,fixedrange=True),
        yaxis=dict(showgrid=False,fixedrange=True)
    )
    PALETTE = ["#6c63ff","#00d4aa","#ff6b6b","#ffb703","#5edfff","#ff8fab","#a8edea"]

    view = st.selectbox("Period",["This Month","Last Month","This Week","Today","Custom"],key="ins_view")
    if   view=="Today":       s,e = today,today
    elif view=="This Week":   s,e = week_start,today
    elif view=="This Month":  s,e = month_start,today
    elif view=="Last Month":
        e = month_start-timedelta(1); s = e.replace(day=1)
    else:
        ic1,ic2 = st.columns(2)
        with ic1: s = st.date_input("From",today-timedelta(30),key="ins_s")
        with ic2: e = st.date_input("To",  today,              key="ins_e")

    st.markdown(f"<p style='font-size:11px;color:var(--muted)'>📅 {s.strftime('%d %b %Y')} → {e.strftime('%d %b %Y')}</p>",
                unsafe_allow_html=True)

    # Use cached data for built-in periods; fetch full range only for Custom
    if view == "Custom":
        idf = fetch_expenses_range(uid, s, e)
    else:
        idf = expenses_df

    if not idf.empty:
        fdf = idf[(idf["ExpenseDate"]>=s) & (idf["ExpenseDate"]<=e) & (idf["EntryType"]=="Expense")]
        if not fdf.empty:
            total_s = fdf["Amount"].sum()
            cat_sum = fdf.groupby("CategoryName")["Amount"].sum().sort_values(ascending=False).reset_index()
            top_cat = cat_sum.iloc[0]["CategoryName"] if not cat_sum.empty else "N/A"
            avg_day = fdf.groupby("ExpenseDate")["Amount"].sum().mean()
            n_tx    = len(fdf)

            ins_kpi = '<div class="kpi-row">'
            for i,(icon,lbl,val,color) in enumerate([
                ("💸","Total Spent",  f"{cur}{total_s:,.0f}","var(--red)"),
                ("🔥","Top Category", top_cat,               "var(--warn)"),
                ("📆","Avg / Day",    f"{cur}{avg_day:,.0f}","var(--accent)"),
                ("🧾","Transactions", str(n_tx),             "var(--green)"),
            ]):
                ins_kpi += f"""<div class="kpi-card" style="--kpi-c:{color};animation-delay:{i*.06}s">
                  <div class="kpi-icon">{icon}</div><p class="kpi-lbl">{lbl}</p>
                  <p class="kpi-val" style="color:{color};font-size:16px">{val}</p></div>"""
            ins_kpi += '</div>'
            st.markdown(ins_kpi, unsafe_allow_html=True)

            st.markdown("### 🍩 Category Split")
            pie = px.pie(cat_sum,names="CategoryName",values="Amount",hole=0.5,color_discrete_sequence=PALETTE)
            pie.update_layout(**PLOT_LAY, height=270, legend=dict(orientation="h",y=-0.12,font=dict(size=10)))
            pie.update_traces(textinfo="percent",textfont_size=10)
            st.plotly_chart(pie,use_container_width=True,config=PLOT_CFG)

            st.markdown("### 💰 Savings Rate")
            total_inc = idf[(idf["ExpenseDate"]>=s)&(idf["ExpenseDate"]<=e)&(idf["EntryType"]=="Income")]["Amount"].sum()
            if total_inc > 0:
                sr = max(0,(total_inc-total_s)/total_inc*100)
                gauge = go.Figure(go.Indicator(
                    mode="gauge+number",value=sr,
                    number={"suffix":"%","font":{"size":26,"color":"#f0f0ff","family":"system-ui"}},
                    gauge={
                        "axis":{"range":[0,100],"tickcolor":"#7777aa","tickfont":{"color":"#7777aa"}},
                        "bar":{"color":"#00d4aa","thickness":0.25},
                        "bgcolor":"rgba(0,0,0,0)","bordercolor":"rgba(255,255,255,0.06)",
                        "steps":[{"range":[0,30],"color":"rgba(255,107,107,.1)"},
                                 {"range":[30,60],"color":"rgba(255,183,3,.07)"},
                                 {"range":[60,100],"color":"rgba(0,212,170,.07)"}],
                    }
                ))
                gauge.update_layout(height=190,paper_bgcolor="rgba(0,0,0,0)",
                                    margin=dict(t=0,b=0,l=20,r=20),font=dict(color="#f0f0ff"))
                st.plotly_chart(gauge,use_container_width=True,config=PLOT_CFG)
                saved_amt   = total_inc - total_s
                saved_color = "var(--green)" if saved_amt >= 0 else "var(--red)"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-around;margin:-4px 0 8px;font-size:12px">
                  <span>Income: <b style="color:var(--green)">{cur}{total_inc:,.0f}</b></span>
                  <span>Spent: <b style="color:var(--red)">{cur}{total_s:,.0f}</b></span>
                  <span>Saved: <b style="color:{saved_color}">{cur}{abs(saved_amt):,.0f}</b></span>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="empty" style="padding:20px 16px"><div class="ei">💰</div>'
                            '<h4>No income recorded</h4><p>Add income entries to see savings rate</p></div>',
                            unsafe_allow_html=True)

            st.markdown("### 📊 Daily Spend")
            ds  = fdf.groupby(["ExpenseDate","CategoryName"])["Amount"].sum().reset_index()
            bar = px.bar(ds,x="ExpenseDate",y="Amount",color="CategoryName",color_discrete_sequence=PALETTE)
            bar.update_layout(**{**PLOT_LAY,"height":230,
                                 "legend":dict(orientation="h",y=-0.28,font=dict(size=9)),"bargap":0.15})
            st.plotly_chart(bar,use_container_width=True,config=PLOT_CFG)

            st.markdown("### 📅 Week-on-Week (Last 6 Weeks)")
            all_exp = expenses_df[expenses_df["EntryType"]=="Expense"].copy()
            all_exp["Week"] = all_exp["ExpenseDate"].apply(
                lambda d: (d-timedelta(days=d.weekday())).strftime("%b %d") if pd.notnull(d) else "")
            wow_grp = all_exp[all_exp["ExpenseDate"]>=today-timedelta(weeks=6)].groupby(["Week","CategoryName"])["Amount"].sum().reset_index()
            if not wow_grp.empty:
                worder = sorted(wow_grp["Week"].unique(), key=lambda w: datetime.strptime(w+f" {today.year}","%b %d %Y"))
                wf = px.bar(wow_grp,x="Week",y="Amount",color="CategoryName",barmode="group",
                            category_orders={"Week":worder},color_discrete_sequence=PALETTE)
                wf.update_layout(**{**PLOT_LAY,"height":240,
                                    "legend":dict(orientation="h",y=-0.3,font=dict(size=9)),"bargap":0.2})
                st.plotly_chart(wf,use_container_width=True,config=PLOT_CFG)

            st.markdown("### 🗓️ Month-on-Month (Last 5 Months)")
            all_exp["Month"] = all_exp["ExpenseDate"].apply(lambda d: d.strftime("%b %Y") if pd.notnull(d) else "")
            mom_grp = all_exp[all_exp["ExpenseDate"]>=month_start-timedelta(days=150)].groupby(["Month","CategoryName"])["Amount"].sum().reset_index()
            if not mom_grp.empty:
                morder = sorted(mom_grp["Month"].unique(), key=lambda m: datetime.strptime(m,"%b %Y"))
                mf = px.bar(mom_grp,x="Month",y="Amount",color="CategoryName",barmode="stack",
                            category_orders={"Month":morder},color_discrete_sequence=PALETTE)
                mf.update_layout(**{**PLOT_LAY,"height":240,"legend":dict(orientation="h",y=-0.3,font=dict(size=9))})
                st.plotly_chart(mf,use_container_width=True,config=PLOT_CFG)

            st.markdown("### 💹 Income vs Expense Trend")
            trend = expenses_df.copy()
            trend["Month"] = trend["ExpenseDate"].apply(lambda d: d.strftime("%b %Y") if pd.notnull(d) else "")
            tgrp  = trend.groupby(["Month","EntryType"])["Amount"].sum().reset_index()
            if not tgrp.empty:
                morder2 = sorted(tgrp["Month"].unique(), key=lambda m: datetime.strptime(m,"%b %Y"))
                tf = px.line(tgrp,x="Month",y="Amount",color="EntryType",markers=True,
                             category_orders={"Month":morder2},
                             color_discrete_map={"Expense":"#ff6b6b","Income":"#00d4aa","Transfer":"#6c63ff"})
                tf.update_layout(**{**PLOT_LAY,"height":220,"legend":dict(orientation="h",y=-0.3)})
                tf.update_traces(line=dict(width=2.5))
                st.plotly_chart(tf,use_container_width=True,config=PLOT_CFG)

            st.markdown("### 🏆 Top 5 Transactions")
            for i,(_,tx) in enumerate(fdf.sort_values("Amount",ascending=False).head(5).iterrows()):
                t = tx.get("ExpenseTitle","") or tx.get("CategoryName","")
                st.markdown(f"""
                <div class="tx-card" style="animation-delay:{i*.05}s">
                  <div class="tx-icon">🏆</div>
                  <div class="tx-body"><p class="tx-title">{t}</p>
                    <p class="tx-meta">{tx.get('ExpenseDate','')} · {tx.get('CategoryName','')} · {tx.get('WalletName','')}</p></div>
                  <div style="text-align:right"><span class="tx-amt exp">-{cur}{float(tx.get('Amount',0)):,.0f}</span></div>
                </div>""", unsafe_allow_html=True)

            st.divider()
            all_fdf    = idf[(idf["ExpenseDate"]>=s)&(idf["ExpenseDate"]<=e)]
            csv_bytes  = all_fdf.to_csv(index=False).encode()
            st.download_button(
                label=f"📥 Download ({s.strftime('%d %b')} – {e.strftime('%d %b %Y')})",
                data=csv_bytes, file_name=f"finflow_{s}_{e}.csv",
                mime="text/csv", use_container_width=True
            )
        else:
            st.markdown('<div class="empty"><div class="ei">📊</div><h4>No data for this period</h4>'
                        '<p>Select a wider date range or add transactions</p></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty"><div class="ei">📊</div><h4>No transactions yet</h4>'
                    '<p>Add transactions to see analytics</p></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# PAGE: PROFILE
# ═══════════════════════════════════════════════════════
elif page == "Profile":
    st.markdown(f"<h2>👤 {st.session_state.username}</h2>", unsafe_allow_html=True)
    users_df2 = batch_fetch_all().get("Users", pd.DataFrame())
    urow = users_df2[users_df2["UserId"].astype(str)==uid] if not users_df2.empty and "UserId" in users_df2.columns else pd.DataFrame()

    # Default Wallet
    st.markdown("### 💳 Default Wallet")
    st.markdown("<p style='font-size:12px;color:var(--muted);margin:-8px 0 10px'>Used for Quick Add transactions</p>",
                unsafe_allow_html=True)
    if w_display:
        cur_pref_p = st.session_state.get("preferred_wallet", w_display[0])
        new_pref   = st.selectbox("Default Wallet", w_display,
                                  index=w_display.index(cur_pref_p) if cur_pref_p in w_display else 0,
                                  key="profile_pref_wallet", label_visibility="collapsed")
        if new_pref != cur_pref_p:
            st.session_state.preferred_wallet = new_pref
            save_default_wallet(uid, new_pref, wallets_df)
            st.success(f"✅ Default wallet saved: **{new_pref}**")
    else:
        st.info("Create a wallet first.")

    st.divider()

    with st.expander("✏️ Account Details", expanded=False):
        if not urow.empty:
            sidx = int(urow.index[0])+1
            nn  = st.text_input("Display Name",value=st.session_state.username)
            np_ = st.text_input("New Password",type="password",placeholder="Leave blank to keep current")
            if st.button("Update Account",type="primary"):
                upd = {}
                if nn and nn!=st.session_state.username: upd["UserName"]=nn
                if np_: upd["PasswordHash"]=np_
                if upd:
                    update_row_cells("Users",sidx,upd)
                    if "UserName" in upd: st.session_state.username=nn
                    _invalidate_data_cache(); st.success("Updated!"); st.rerun()
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["logged_in","username","user_id","page","data_loaded","alerted",
                      "custom_shortcuts","preferred_wallet","exp_only","inc_only","paid_recurring"]:
                st.session_state.pop(k, None)
            st.query_params.clear(); st.rerun()

    st.divider()

    with st.expander("🏷️ Manage Categories"):
        if not categories_df.empty and "CategoryName" in categories_df.columns:
            sel = st.selectbox("Select",categories_df["CategoryName"].tolist(),key="pcat")
            cr  = categories_df[categories_df["CategoryName"]==sel]
            if not cr.empty:
                cidx = int(cr.index[0])+1
                with st.form("cat_form"):
                    cc1,cc2,cc3 = st.columns(3)
                    with cc1: en = st.text_input("Name", value=cr.iloc[0].get("CategoryName",""))
                    with cc2: el = st.number_input("Monthly Limit",value=float(cr.iloc[0].get("MonthlyLimit",0) or 0))
                    with cc3: ei = st.text_input("Icon", value=cr.iloc[0].get("Icon",""))
                    bc1,bc2 = st.columns(2)
                    with bc1:
                        if st.form_submit_button("Update",type="primary",use_container_width=True):
                            update_row_cells("ExpenseCategories",cidx,{"CategoryName":en,"MonthlyLimit":el,"Icon":ei})
                            _invalidate_data_cache(); st.success("Updated!"); st.rerun()
                    with bc2:
                        if st.form_submit_button("Delete",use_container_width=True):
                            delete_row("ExpenseCategories",cidx)
                            _invalidate_data_cache(); st.success("Deleted!"); st.rerun()
        st.divider()
        with st.form("new_cat"):
            st.markdown("**New Category**")
            nc1,nc2,nc3 = st.columns(3)
            with nc1: ncn = st.text_input("Name",key="ncn")
            with nc2: ncl = st.number_input(f"Limit ({cur})",min_value=0.0,key="ncl")
            with nc3: nci = st.text_input("Icon",key="nci")
            if st.form_submit_button("Add Category",type="primary"):
                if ncn:
                    append_row("ExpenseCategories",{
                        "CategoryId":str(uuid.uuid4()),"UserId":uid,"CategoryName":ncn,
                        "MonthlyLimit":ncl,"Icon":nci,"ColorHex":"#6c63ff",
                        "IsDefault":"False","IsActive":"True","CreatedAt":str(datetime.now())
                    })
                    _invalidate_data_cache(); st.success(f"'{ncn}' added!"); st.rerun()

    with st.expander("👛 Manage Wallets"):
        if not wallets_df.empty and "WalletName" in wallets_df.columns:
            sel_w = st.selectbox("Select",wallets_df["WalletName"].tolist(),key="pw_sel")
            wr    = wallets_df[wallets_df["WalletName"]==sel_w]
            if not wr.empty:
                widx = int(wr.index[0])+1
                with st.form("wal_form"):
                    wc1,wc2 = st.columns(2)
                    with wc1: ewn = st.text_input("Name",value=wr.iloc[0].get("WalletName",""))
                    with wc2: ewt = st.selectbox("Type",["Cash","UPI","Card","Bank"])
                    bc1,bc2 = st.columns(2)
                    with bc1:
                        if st.form_submit_button("Update",type="primary",use_container_width=True):
                            update_row_cells("Wallets",widx,{"WalletName":ewn,"WalletType":ewt})
                            _invalidate_data_cache(); st.success("Updated!"); st.rerun()
                    with bc2:
                        if st.form_submit_button("Delete",use_container_width=True):
                            delete_row("Wallets",widx)
                            _invalidate_data_cache(); st.success("Deleted!"); st.rerun()

    if not recurring_df.empty:
        with st.expander("🔁 Recurring Templates"):
            for i,(_,r) in enumerate(recurring_df.iterrows()):
                c1,c2 = st.columns([4,1])
                with c1: st.markdown(f"**{r.get('Title','')}** · {cur}{float(r.get('Amount',0)):,.0f} · {r.get('Frequency','')} · Next: {r.get('NextDue','')}")
                with c2:
                    if st.button("🗑️",key=f"drec_{i}"):
                        delete_row("RecurringTemplates",int(_)+1)
                        _invalidate_data_cache(); st.rerun()

    with st.expander("⚡ Quick Shortcuts"):
        default_sc = [
            {"icon":"☕","label":"Coffee",   "amt":60, "cat":"Food & Drinks"},
            {"icon":"🚕","label":"Cab",      "amt":150,"cat":"Transport"},
            {"icon":"🍔","label":"Lunch",    "amt":120,"cat":"Food & Drinks"},
            {"icon":"🛒","label":"Groceries","amt":500,"cat":"Groceries"},
            {"icon":"⛽","label":"Fuel",     "amt":200,"cat":"Transport"},
            {"icon":"🎬","label":"Movie",    "amt":300,"cat":"Entertainment"},
        ]
        scd = st.session_state.get("custom_shortcuts",default_sc)
        with st.form("sc_form"):
            new_sc = []
            for i,sc in enumerate(scd):
                s1,s2,s3,s4 = st.columns([1,2,2,2])
                with s1: iv = st.text_input(f"Icon",value=sc["icon"],key=f"si_{i}")
                with s2: lv = st.text_input(f"Label",value=sc["label"],key=f"sl_{i}")
                with s3: av = st.number_input(f"Amt",value=float(sc["amt"]),min_value=0.0,step=10.0,key=f"sa_{i}")
                with s4: cv = st.selectbox(f"Cat",cat_list,key=f"sc_{i}")
                new_sc.append({"icon":iv,"label":lv,"amt":int(av),"cat":cv})
            if st.form_submit_button("💾 Save Shortcuts",type="primary"):
                st.session_state["custom_shortcuts"]=new_sc; st.success("Saved!"); st.rerun()

    # ── Delete Old Data ──
    st.divider()
    with st.expander("🗑️ Delete Old Data", expanded=False):
        st.markdown("""
        <div style="background:rgba(255,107,107,.08);border:1px solid rgba(255,107,107,.25);
          border-radius:12px;padding:12px 14px;margin-bottom:12px;">
          <p style="font-size:13px;font-weight:700;color:var(--red);margin:0 0 4px">⚠️ Danger Zone</p>
          <p style="font-size:12px;color:var(--muted);margin:0">
            This will permanently delete all your expense records older than 1 year.
            This action cannot be undone.</p>
        </div>""", unsafe_allow_html=True)
        del_confirm = st.checkbox("I understand this is permanent and cannot be undone",
                                  key="del_confirm_check")
        del_pwd = st.text_input("Enter your password to confirm", type="password", key="del_pwd_input")
        if st.button("🗑️ Delete Data Older Than 1 Year", type="primary",
                     disabled=not del_confirm, key="del_old_btn"):
            if not del_pwd:
                st.error("Please enter your password.")
            else:
                with st.spinner("Deleting old data..."):
                    ok, msg = delete_old_data(uid, del_pwd, users_df2)
                if ok:
                    st.success(f"✅ {msg}")
                    if "deleted" in msg.lower() and "0" not in msg:
                        _invalidate_data_cache()
                else:
                    st.error(f"❌ {msg}")
