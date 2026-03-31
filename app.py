import streamlit as st
import sqlite3
import pandas as pd
import time

# --- 1. 資料庫連線函式 ---
def get_db_connection(trip_id):
    """根據旅程代碼建立/連接獨立的資料庫檔案"""
    safe_id = trip_id.strip() if trip_id.strip() else "default"
    db_name = f"trip_data_{safe_id}.db"
    conn = sqlite3.connect(db_name, check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS members (name TEXT PRIMARY KEY, balance REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, payer TEXT, amount REAL, participants TEXT, description TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    return conn

# --- 2. 頁面配置 ---
st.set_page_config(page_title="FairShare | 自定義風格", layout="wide")

# --- 3. 狀態初始化與顏色選擇 ---
if 'trip_id' not in st.session_state:
    st.session_state.trip_id = "default"

with st.sidebar:
    st.markdown("<h1 style='color:#da22ff; font-weight:900;'>幻魅中心</h1>", unsafe_allow_html=True)
    
    # 讓使用者自行選擇背景顏色
    bg_color = st.color_picker("自定義背景顏色", "#1e1e2f")
    
    input_id = st.text_input("輸入旅程代碼", value=st.session_state.trip_id)
    
    if st.button("進入/切換房間"):
        if input_id:
            st.session_state.trip_id = input_id
            st.success(f"正在前往房間: {input_id}")
            time.sleep(0.5)
            st.rerun()

    st.markdown("---")

# --- 4. 靜態 CSS 樣式 ---
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_color} !important;
        color: white !important;
    }}

    .hero-banner {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(218, 34, 255, 0.3);
        padding: 40px;
        border-radius: 35px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }}
    .hero-title {{
        font-size: 4.5em !important;
        background: linear-gradient(to right, #da22ff, #9733ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        margin-bottom: 0;
    }}

    .neon-card {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(218, 34, 255, 0.2);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
    }}

    .positive {{ color: #2ed573 !important; font-weight: bold; }}
    .negative {{ color: #ff4757 !important; font-weight: bold; }}

    .stButton>button {{
        background: linear-gradient(90deg, #da22ff, #9733ee) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        width: 100%;
        padding: 10px 0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. 側邊欄資料處理 ---
with st.sidebar:
    conn = get_db_connection(st.session_state.trip_id)
    
    st.markdown("### 成員名單")
    new_member = st.text_input("輸入新隊友姓名", key="new_mem")
    if st.button("確認加入"):
        if new_member:
            try:
                conn.execute('INSERT INTO members (name, balance) VALUES (?, 0)', (new_member,))
                conn.commit()
                st.rerun()
            except:
                st.warning("此成員已在名單中")

    st.markdown("### 即時財務狀況")
    members_df = pd.read_sql('SELECT * FROM members', conn)
    for _, row in members_df.iterrows():
        cls = "positive" if row['balance'] >= 0 else "negative"
        st.markdown(f"""
            <div class="neon-card">
                <div style="font-size:0.8em; opacity:0.6;">{row['name']}</div>
                <div class="{cls}" style="font-size:1.4em;">${row['balance']:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

# --- 6. 主畫面內容 ---
st.markdown(f"""
    <div class="hero-banner">
        <h1 class="hero-title">FairShare</h1>
        <p style="color:rgba(255,255,255,0.6); font-size:1.2em;">
            當前房間：<span style="color:#da22ff; font-weight:bold; font-size:1.5em;">{st.session_state.trip_id}</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

if members_df.empty:
    st.info("歡迎！請先在左側選單新增成員，即可開始紀錄支出。")
else:
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown("<h2 style='color:#da22ff;'>紀錄支出</h2>", unsafe_allow_html=True)
        with st.form("expense_form", clear_on_submit=True):
            f_c1, f_c2 = st.columns(2)
            with f_c1:
                payer = st.selectbox("誰付的錢？", members_df['name'].tolist())
                desc = st.text_input("消費項目", placeholder="例如：晚餐支出")
            with f_c2:
                amount = st.number_input("總金額", min_value=0.0, step=10.0)
                participants = st.multiselect("誰要平分？", members_df['name'].tolist(), default=members_df['name'].tolist())
            
            if st.form_submit_button("發送到帳本"):
                if amount > 0 and participants:
                    share = amount / len(participants)
                    conn.execute('UPDATE members SET balance = balance + ? WHERE name = ?', (amount, payer))
                    for p in participants:
                        conn.execute('UPDATE members SET balance = balance - ? WHERE name = ?', (share, p))
                    conn.execute('INSERT INTO history (payer, amount, participants, description) VALUES (?, ?, ?, ?)',
                                 (payer, amount, ",".join(participants), desc))
                    conn.commit()
                    st.toast("紀錄成功！")
                    time.sleep(0.5)
                    st.rerun()

        st.markdown("<h2 style='color:#da22ff; margin-top:30px;'>消費紀錄流</h2>", unsafe_allow_html=True)
        history_df = pd.read_sql('SELECT * FROM history ORDER BY id DESC', conn)
        if history_df.empty:
            st.markdown("<p style='opacity:0.4;'>尚無交易紀錄...</p>", unsafe_allow_html=True)
        else:
            for _, row in history_df.iterrows():
                st.markdown(f"""
                    <div class="neon-card" style="border-left: 4px solid #da22ff;">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="font-weight:bold; color:#da22ff; font-size:1.2em;">{row['description']}</span>
                            <span style="font-family:monospace; font-weight:900;">${row['amount']:,.2f}</span>
                        </div>
                        <div style="font-size:0.85em; opacity:0.7; margin-top:10px;">
                            由 {row['payer']} 支付，分擔對象：{row['participants']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown("<h2 style='color:#da22ff;'>智能結算建議</h2>", unsafe_allow_html=True)
        if st.button("執行運算"):
            bal_dict = members_df.set_index('name')['balance'].to_dict()
            debtors = {k: v for k, v in bal_dict.items() if v < -0.01}
            creditors = {k: v for k, v in bal_dict.items() if v > 0.01}
            
            if not debtors:
                st.success("目前帳目完全平衡！")
            else:
                for d_name, d_amt in debtors.items():
                    for c_name, c_amt in creditors.items():
                        if d_amt >= 0: break
                        pay = min(abs(d_amt), c_amt)
                        if pay > 0:
                            st.markdown(f"""
                                <div style="padding:15px; background:rgba(218,34,255,0.15); border:1px solid #da22ff; border-radius:12px; margin-bottom:8px;">
                                    {d_name} 應支付給 {c_name}<br>
                                    <span style="font-size:1.3em; font-weight:bold; color:#da22ff;">${pay:,.2f}</span>
                                </div>
                            """, unsafe_allow_html=True)
                            d_amt += pay
                            creditors[c_name] -= pay

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.expander("管理選項"):
            if st.button("清空目前房間所有數據"):
                conn.execute('DELETE FROM members')
                conn.execute('DELETE FROM history')
                conn.commit()
                st.rerun()

st.markdown("<div style='text-align:center; margin-top:80px; opacity:0.3; font-size:0.8em;'>FAIRSHARE PRO v5.0 | CUSTOM STYLE EDITION</div>", unsafe_allow_html=True)
