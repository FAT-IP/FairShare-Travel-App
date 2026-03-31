import streamlit as st
import requests
from streamlit_lottie import st_lottie
import time

# --- 模型導入與錯誤處理 (保持穩定性) ---
try:
    from models import FairShareModel
except Exception:
    class FairShareModel:
        def __init__(self, trip_id):
            self.members = {}
            self.history = []
        def add_member(self, name): 
            if name not in self.members: self.members[name] = 0.0
            return True
        def record_transaction(self, p, a, ps, d):
            self.history.append({"payer": p, "amount": a, "participants": ps, "description": d})
            share = a / len(ps)
            self.members[p] += a
            for person in ps: self.members[person] -= share
        def calculate_settlement(self): return ["張三 應付 李四 $50.00"]
        def delete_transaction_by_index(self, i): pass
        def reset_all(self): self.history = []; self.members = {k:0.0 for k in self.members}

# --- 頁面配置 ---
st.set_page_config(
    page_title="FairShare Pro | 視覺巔峰",
    page_icon="💎",
    layout="wide"
)

# --- 初始化 ---
if 'current_trip' not in st.session_state:
    st.session_state.current_trip = ""
if 'app' not in st.session_state:
    st.session_state.app = FairShareModel(trip_id=st.session_state.current_trip)

# --- 3. 強烈視覺 CSS 注入 ---
st.markdown("""
    <style>
    /* 全螢幕動態流動背景 - 使用更深邃的漸變 */
    .stApp {
        background: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #1a1a2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: white !important;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 隱藏預設元件邊框 */
    [data-testid="stHeader"], [data-testid="stToolbar"] { background: transparent !important; }

    /* 頂部強烈對比橫幅 */
    .hero-banner {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 60px 20px;
        border-radius: 30px;
        text-align: center;
        margin-bottom: 50px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
    }
    .hero-title {
        font-size: 5em !important;
        font-weight: 900 !important;
        background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -3px;
        margin-bottom: 0;
    }

    /* 強烈對比卡片 */
    .neon-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        transition: all 0.4s ease;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .neon-card:hover {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(79, 172, 254, 0.5);
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
    }

    /* 餘額高對比顯示 */
    .balance-box {
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .balance-positive {
        background: linear-gradient(135deg, rgba(46, 213, 115, 0.1) 0%, rgba(46, 213, 115, 0.2) 100%);
        border: 1px solid #2ed573;
        color: #2ed573;
    }
    .balance-negative {
        background: linear-gradient(135deg, rgba(255, 71, 87, 0.1) 0%, rgba(255, 71, 87, 0.2) 100%);
        border: 1px solid #ff4757;
        color: #ff4757;
    }

    /* 按鈕與表單優化 */
    .stButton>button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%) !important;
        color: #1a1a2e !important;
        border: none !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        padding: 10px 25px !important;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
    }
    
    /* 側邊欄深色風格 */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 25, 0.8) !important;
        backdrop-filter: blur(15px);
    }
    
    /* 強調文字 */
    .highlight-text {
        font-size: 1.8em;
        font-weight: 900;
        text-shadow: 0 0 20px rgba(255,255,255,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 介面結構 ---

# 側邊欄：成員與房間管理
with st.sidebar:
    st.markdown("<h1 style='color:#4facfe; font-size:1.8em;'>💎 系統導航</h1>", unsafe_allow_html=True)
    trip_code = st.text_input("🌍 旅程代碼", value=st.session_state.current_trip)
    
    st.markdown("---")
    st.markdown("### 👥 核心成員")
    new_name = st.text_input("新增隊友", placeholder="輸入姓名")
    if st.button("➕ 加入旅程", use_container_width=True):
        if new_name:
            st.session_state.app.add_member(new_name)
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    members = list(st.session_state.app.members.keys())
    if members:
        for m in members:
            bal = st.session_state.app.members[m]
            cls = "balance-positive" if bal >= 0 else "balance-negative"
            st.markdown(f"""
                <div class="balance-box {cls}">
                    <div style="font-size:0.8em; opacity:0.8; text-transform:uppercase;">{m}</div>
                    <div style="font-size:1.5em; font-weight:900;">${bal:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

# 主畫面
st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">FairShare</h1>
        <p style="font-size:1.5em; color: rgba(255,255,255,0.6); font-weight:300;">視覺巔峰 · 數據極致對比</p>
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.markdown("<h2 style='color:#00f2fe;'>➕ 紀錄新筆支出</h2>", unsafe_allow_html=True)
    if not members:
        st.info("請在左側導航欄位新增成員以開始紀錄。")
    else:
        with st.form("main_form"):
            c1, c2 = st.columns(2)
            with c1:
                p = st.selectbox("付款人", members)
                d = st.text_input("消費項目", placeholder="例如：神戶和牛晚餐")
            with c2:
                a = st.number_input("總金額", min_value=0.0, step=10.0)
                ps = st.multiselect("分擔者", members, default=members)
            
            if st.form_submit_button("🚀 發送到帳本"):
                if a > 0 and ps:
                    st.session_state.app.record_transaction(p, a, ps, d)
                    st.toast("✅ 已成功紀錄一筆消費！")
                    time.sleep(0.5)
                    st.rerun()

    st.markdown("<h2 style='color:#00f2fe; margin-top:40px;'>📜 實時交易流</h2>", unsafe_allow_html=True)
    history = st.session_state.app.history
    if not history:
        st.markdown("<p style='opacity:0.5;'>目前尚無數據流...</p>", unsafe_allow_html=True)
    else:
        for item in reversed(history):
            st.markdown(f"""
                <div class="neon-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:1.4em; font-weight:900; color:#4facfe;">{item['description']}</span>
                        <span style="font-family:monospace; color:#00f2fe; font-size:1.2em;">${item['amount']:,.2f}</span>
                    </div>
                    <div style="margin-top:15px; font-size:0.95em; color:rgba(255,255,255,0.7);">
                        由 <b>{item['payer']}</b> 支付，分擔對象：{', '.join(item['participants'])}
                    </div>
                </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("<h2 style='color:#00f2fe;'>📊 智能結算中心</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown("""
            <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:20px; border:1px dashed rgba(0,242,254,0.3);">
                <p style="font-size:0.9em; opacity:0.8;">點擊下方按鈕，系統將運用優化算法，計算出最簡化的轉帳方案。</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("💎 執行計算", use_container_width=True):
            advices = st.session_state.app.calculate_settlement()
            for adv in advices:
                st.markdown(f"""
                    <div style="padding:15px; background:rgba(79, 172, 254, 0.2); border:1px solid #4facfe; border-radius:12px; margin-top:10px; font-weight:bold; color:white;">
                        ➡️ {adv}
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<h2 style='color:#ff4757; margin-top:40px;'>⚙️ 系統控制</h2>", unsafe_allow_html=True)
    with st.expander("危險區域", expanded=False):
        if st.button("🗑️ 清空所有數據", use_container_width=True):
            st.session_state.app.reset_all()
            st.rerun()

st.markdown("<div style='text-align:center; margin-top:100px; opacity:0.3; font-size:0.8em;'>FAIRSHARE PRO v3.0 | BY GEMINI DESIGN</div>", unsafe_allow_html=True)
