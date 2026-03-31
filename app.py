import streamlit as st
import sqlite3
import pandas as pd
import time
import random
import string
import secrets
from streamlit.runtime.scriptrunner import get_script_run_ctx

# --- 1. 獲取 Session ID (用於私有大廳) ---
def get_session_id():
    ctx = get_script_run_ctx()
    if ctx:
        return ctx.session_id
    return "local_user"

# --- 2. 資料庫連線函式 ---
def get_db_connection(trip_id):
    """根據旅程代碼建立/連接獨立的資料庫檔案"""
    safe_id = trip_id.strip() if trip_id.strip() else "default"
    
    # 私有化邏輯：如果是在大廳，加上 Session ID 確保資料隔離
    if safe_id == "default":
        session_id = get_session_id()
        # 取前 8 位即可，確保檔名簡潔
        db_name = f"trip_data_private_{session_id[:8]}.db"
    else:
        # 如果是特定房間，則使用原始代碼，方便多人共享
        clean_id = "".join([c for c in safe_id if c.isalnum() or c in ('-', '_')]).strip()
        db_name = f"trip_data_shared_{clean_id}.db"
    
    conn = sqlite3.connect(db_name, check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS members (name TEXT PRIMARY KEY, balance REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, payer TEXT, amount REAL, participants TEXT, description TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    
    # 房間初始化
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM members')
    if cursor.fetchone()[0] == 0:
        default_user = "本人" if safe_id == "default" else "管理員"
        conn.execute('INSERT INTO members (name, balance) VALUES (?, 0)', (default_user,))
        conn.commit()
            
    return conn

# --- 3. 頁面配置 ---
st.set_page_config(page_title="FairShare | 極致私隱版", layout="wide")

# --- 4. 預設風格定義 ---
THEMES = {
    "深邃幻魅紫": {"bg": "#1e1e2f", "text": "#ffffff", "accent": "#da22ff"},
    "午夜冷調藍": {"bg": "#0f172a", "text": "#f8fafc", "accent": "#38bdf8"},
    "商務碳墨黑": {"bg": "#121212", "text": "#e5e5e5", "accent": "#a3a3a3"},
    "活力琥珀橙": {"bg": "#2B3C3D", "text": "#ffffff", "accent": "#FF7400"}
}

# --- 5. 狀態初始化 ---
if 'trip_id' not in st.session_state:
    st.session_state.trip_id = "default"

if 'temp_id' not in st.session_state:
    st.session_state.temp_id = st.session_state.trip_id

is_lobby = st.session_state.trip_id == "default"

with st.sidebar:
    st.markdown("<h1 style='color:#da22ff; font-weight:900;'>風格中心</h1>", unsafe_allow_html=True)
    
    theme_choice = st.selectbox("切換視覺風格", list(THEMES.keys()))
    current_theme = THEMES[theme_choice]
    
    st.markdown("---")
    st.markdown("### 房間管理")
    
    if st.button("🎲 生成多人共享代碼"):
        alphabet = string.ascii_letters + string.digits
        random_id = ''.join(secrets.choice(alphabet) for _ in range(12))
        st.session_state.temp_id = random_id
        st.rerun()

    input_id = st.text_input("房間代碼 (留空回大廳)", value=st.session_state.temp_id)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("進入房間"):
            st.session_state.trip_id = input_id if input_id else "default"
            st.session_state.temp_id = st.session_state.trip_id
            st.success("房間切換成功")
            time.sleep(0.5)
            st.rerun()
    
    with col_btn2:
        if st.button("🚪 回到私有大廳"):
            st.session_state.trip_id = "default"
            st.session_state.temp_id = "default"
            st.rerun()

    if is_lobby:
        st.info("🔒 您目前處於「私有大廳」。此處的數據僅綁定於您目前的瀏覽器 Session，其他人無法查看。")
    else:
        st.warning("👥 您處於「共享房間」。知道此代碼的任何人皆可存取此數據。")

    st.markdown("---")

# --- 6. CSS 樣式 ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {current_theme['bg']} !important; color: {current_theme['text']} !important; }}
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3 {{ color: {current_theme['text']} !important; }}
    .hero-banner {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid {current_theme['accent']};
        padding: 40px; border-radius: 30px; text-align: center; margin-bottom: 30px;
    }}
    .hero-title {{
        font-size: 4.5em !important;
        background: linear-gradient(to right, {current_theme['accent']}, #ffffff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; margin-bottom: 0;
    }}
    .neon-card {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px; padding: 20px; margin-bottom: 15px;
    }}
    .positive {{ color: #2ed573 !important; font-weight: bold; }}
    .stButton>button {{
        background: {current_theme['accent']} !important;
        color: #121212 !important; border: none !important;
        border-radius: 12px !important; font-weight: bold !important; width: 100%;
    }}
    input {{ background-color: rgba(255, 255, 255, 0.05) !important; color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 7. 核心資料處理 ---
conn = get_db_connection(st.session_state.trip_id)
members_df = pd.read_sql('SELECT * FROM members', conn)

with st.sidebar:
    if not is_lobby:
        st.markdown("### 旅伴名單")
        new_member = st.text_input("新增成員姓名")
        if st.button("確認加入"):
            if new_member:
                try:
                    conn.execute('INSERT INTO members (name, balance) VALUES (?, 0)', (new_member,))
                    conn.commit()
                    st.rerun()
                except:
                    st.warning("名稱重複")

    st.markdown("### 財務概覽")
    for _, row in members_df.iterrows():
        display_name = "我的累計支出" if is_lobby and row['name'] == "本人" else row['name']
        val = abs(row['balance'])
        st.markdown(f"""
            <div class="neon-card">
                <div style="font-size:0.8em; opacity:0.6;">{display_name}</div>
                <div class="positive" style="font-size:1.4em;">${val:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

# --- 8. 主畫面 ---
title_text = "🔒 私有記帳大廳" if is_lobby else "👥 多人分帳空間"
st.markdown(f"""
    <div class="hero-banner">
        <h1 class="hero-title">{title_text}</h1>
        <p style="opacity:0.6;">{ '數據僅存於此 Session' if is_lobby else '房間代碼：' + st.session_state.trip_id }</p>
    </div>
    """, unsafe_allow_html=True)

col_main = st.columns([3, 2] if not is_lobby else [1])

with col_main[0]:
    st.markdown(f"<h2 style='color:{current_theme['accent']};'>{'＋ 新增個人紀錄' if is_lobby else '支出紀錄'}</h2>", unsafe_allow_html=True)
    with st.form("expense_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            payer = "本人" if is_lobby else st.selectbox("付款人", members_df['name'].tolist())
            desc = st.text_input("項目名稱", placeholder="例如：午餐")
        with c2:
            amount = st.number_input("金額", min_value=0.0, step=10.0)
            if not is_lobby:
                participants = st.multiselect("參與平分者", members_df['name'].tolist(), default=members_df['name'].tolist())
            else:
                participants = ["本人"]
        
        if st.form_submit_button("送出紀錄"):
            if amount > 0:
                share = amount / len(participants)
                conn.execute('UPDATE members SET balance = balance + ? WHERE name = ?', (amount, payer))
                for p in participants:
                    conn.execute('UPDATE members SET balance = balance - ? WHERE name = ?', (share, p))
                conn.execute('INSERT INTO history (payer, amount, participants, description) VALUES (?, ?, ?, ?)',
                             (payer, amount, ",".join(participants), desc))
                conn.commit()
                st.rerun()

    st.markdown("### 歷史清單")
    history_df = pd.read_sql('SELECT * FROM history ORDER BY id DESC', conn)
    for _, row in history_df.iterrows():
        detail = "" if is_lobby else f"<div style='font-size:0.8em; opacity:0.5;'>分攤：{row['participants']}</div>"
        st.markdown(f"""
            <div class="neon-card" style="border-left: 3px solid {current_theme['accent']};">
                <div style="display:flex; justify-content:space-between;">
                    <b>{row['description']}</b>
                    <span style="color:{current_theme['accent']};">${row['amount']:,.2f}</span>
                </div>
                {detail}
            </div>
        """, unsafe_allow_html=True)

if not is_lobby:
    with col_main[1]:
        st.markdown("### 結算建議")
        if st.button("計算還款路徑"):
            bal = members_df.set_index('name')['balance'].to_dict()
            for n, b in bal.items():
                if b < -0.1: st.write(f"❌ {n} 需支付 {abs(b):.1f}")
                elif b > 0.1: st.write(f"✅ {n} 應收回 {b:.1f}")

st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("進階管理"):
    if st.button("清空目前所有數據"):
        conn.execute('DELETE FROM history')
        conn.execute('DELETE FROM members')
        conn.commit()
        st.rerun()

st.markdown(f"<div style='text-align:center; opacity:0.2; font-size:0.7em;'>FairShare v8.2 | Session-Based Privacy</div>", unsafe_allow_html=True)
