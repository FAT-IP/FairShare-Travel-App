import streamlit as st
import sqlite3
import pandas as pd
import time
import random
import string
import secrets
import os

# --- 1. 資料庫連線函式 ---
def get_db_connection(trip_id):
    """根據旅程代碼建立/連接獨立的資料庫檔案"""
    safe_id = trip_id.strip() if trip_id.strip() else "default"
    
    # 私有化且持久化邏輯：
    # 如果是 'default'，我們使用一個相對固定但具有個人特徵的名稱
    # 在 Streamlit Cloud 等環境中，若要完全區隔不同人且要保存，
    # 建議使用者可以自定義一個「私有金鑰」
    if safe_id == "default":
        # 這裡我們使用 'my_private_lobby' 作為預設，
        # 在實際部署時，可以考慮結合用戶登入資訊
        db_name = "trip_data_private_lobby.db"
    else:
        # 如果是共享房間，則使用原始代碼
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

# --- 2. 頁面配置 ---
st.set_page_config(page_title="FairShare | 持久保存版", layout="wide")

# --- 3. 預設風格定義 ---
THEMES = {
    "深邃幻魅紫": {"bg": "#1e1e2f", "text": "#ffffff", "accent": "#da22ff"},
    "午夜冷調藍": {"bg": "#0f172a", "text": "#f8fafc", "accent": "#38bdf8"},
    "商務碳墨黑": {"bg": "#121212", "text": "#e5e5e5", "accent": "#a3a3a3"},
    "活力琥珀橙": {"bg": "#2B3C3D", "text": "#ffffff", "accent": "#FF7400"}
}

# --- 4. 狀態初始化 ---
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
    
    if st.button("🎲 生成共享代碼 (多人用)"):
        alphabet = string.ascii_letters + string.digits
        random_id = ''.join(secrets.choice(alphabet) for _ in range(12))
        st.session_state.temp_id = random_id
        st.rerun()

    input_id = st.text_input("房間代碼 (留空回個人大廳)", value=st.session_state.temp_id)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("進入 / 切換"):
            st.session_state.trip_id = input_id if input_id else "default"
            st.session_state.temp_id = st.session_state.trip_id
            st.success("切換成功")
            time.sleep(0.5)
            st.rerun()
    
    with col_btn2:
        if st.button("🏠 回個人大廳"):
            st.session_state.trip_id = "default"
            st.session_state.temp_id = "default"
            st.rerun()

    if is_lobby:
        st.success("✨ 您在個人大廳。數據已自動儲存，下次回來仍會保留。")
    else:
        st.warning("🔗 共享模式：所有人輸入相同代碼即可共同記帳。")

    st.markdown("---")

# --- 5. CSS 樣式 ---
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

# --- 6. 核心資料處理 ---
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

    st.markdown("### 累計花費")
    for _, row in members_df.iterrows():
        display_name = "我的總支出" if is_lobby and row['name'] == "本人" else row['name']
        val = abs(row['balance'])
        st.markdown(f"""
            <div class="neon-card">
                <div style="font-size:0.8em; opacity:0.6;">{display_name}</div>
                <div class="positive" style="font-size:1.4em;">${val:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

# --- 7. 主畫面 ---
title_text = "🏠 我的記帳空間" if is_lobby else "👥 旅程分帳空間"
st.markdown(f"""
    <div class="hero-banner">
        <h1 class="hero-title">{title_text}</h1>
        <p style="opacity:0.6;">{ '數據將保存於伺服器' if is_lobby else '房間代碼：' + st.session_state.trip_id }</p>
    </div>
    """, unsafe_allow_html=True)

col_main = st.columns([3, 2] if not is_lobby else [1])

with col_main[0]:
    st.markdown(f"<h2 style='color:{current_theme['accent']};'>{'＋ 新增一筆花費' if is_lobby else '支出紀錄'}</h2>", unsafe_allow_html=True)
    with st.form("expense_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            payer = "本人" if is_lobby else st.selectbox("付款人", members_df['name'].tolist())
            desc = st.text_input("項目名稱", placeholder="例如：加油、買衣服、晚餐")
        with c2:
            amount = st.number_input("金額", min_value=0.0, step=10.0)
            if not is_lobby:
                participants = st.multiselect("參與平分者", members_df['name'].tolist(), default=members_df['name'].tolist())
            else:
                participants = ["本人"]
        
        if st.form_submit_button("儲存紀錄"):
            if amount > 0:
                share = amount / len(participants)
                conn.execute('UPDATE members SET balance = balance + ? WHERE name = ?', (amount, payer))
                for p in participants:
                    conn.execute('UPDATE members SET balance = balance - ? WHERE name = ?', (share, p))
                conn.execute('INSERT INTO history (payer, amount, participants, description) VALUES (?, ?, ?, ?)',
                             (payer, amount, ",".join(participants), desc))
                conn.commit()
                st.rerun()

    st.markdown("### 歷史明細")
    history_df = pd.read_sql('SELECT * FROM history ORDER BY id DESC', conn)
    for _, row in history_df.iterrows():
        detail = "" if is_lobby else f"<div style='font-size:0.8em; opacity:0.5;'>分攤：{row['participants']}</div>"
        st.markdown(f"""
            <div class="neon-card" style="border-left: 3px solid {current_theme['accent']};">
                <div style="display:flex; justify-content:space-between;">
                    <b>{row['description']}</b>
                    <span style="color:{current_theme['accent']}; font-family:monospace; font-weight:bold;">${row['amount']:,.2f}</span>
                </div>
                {detail}
            </div>
        """, unsafe_allow_html=True)

if not is_lobby:
    with col_main[1]:
        st.markdown("### 結算建議")
        if st.button("計算還款"):
            bal = members_df.set_index('name')['balance'].to_dict()
            for n, b in bal.items():
                if b < -0.1: st.write(f"❌ {n} 需支付 {abs(b):.1f}")
                elif b > 0.1: st.write(f"✅ {n} 應收回 {b:.1f}")

st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("資料管理"):
    if st.button("清空本房所有紀錄 (不可復原)"):
        conn.execute('DELETE FROM history')
        if is_lobby:
            conn.execute('UPDATE members SET balance = 0')
        else:
            conn.execute('DELETE FROM members')
        conn.commit()
        st.rerun()

st.markdown(f"<div style='text-align:center; opacity:0.2; font-size:0.7em;'>FairShare v8.3 | Persistent Storage Mode</div>", unsafe_allow_html=True)
