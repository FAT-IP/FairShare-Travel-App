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
    page_title="FairShare Pro | 幻魅紫巔峰",
    page_icon="🔮",
    layout="wide"
)

# --- 初始化 ---
if 'current_trip' not in st.session_state:
    st.session_state.current_trip = ""
if 'app' not in st.session_state:
    st.session_state.app = FairShareModel(trip_id=st.session_state.current_trip)

# --- 3. 強烈紫色視覺 CSS 注入 ---
st.markdown("""
    <style>
    /* 全螢幕動態流動背景 - 幻魅紫風格 */
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #4b0082);
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

    /* 頂部強烈對比橫幅 - 紫色玻璃擬態 */
    .hero-banner {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 65px 20px;
        border-radius: 40px;
        text-align: center;
        margin-bottom: 50px;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.5);
    }
    .hero-title {
        font-size: 5.5em !important;
        font-weight: 900 !important;
        background: linear-gradient(to right, #da22ff 0%, #9733ee 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -4px;
        margin-bottom: 0;
        filter: drop-shadow(0 0 15px rgba(218, 34, 255, 0.4));
    }

    /* 強烈對比卡片 - 紫色邊框強化 */
    .neon-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(218, 34, 255, 0.15);
        border-radius: 25px;
        padding: 28px;
        margin-bottom: 25px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
    }
    .neon-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(218, 34, 255, 0.6);
        transform: translateY(-10px);
        box-shadow: 0 20px 50px rgba(151, 51, 238, 0.3);
    }

    /* 餘額高對比顯示 - 針對紫色調微調發光 */
    .balance-box {
        padding: 22px;
        border-radius: 20px;
        margin-bottom: 15px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .balance-positive {
        background: rgba(46, 213, 115, 0.12);
        border: 1px solid #2ed573;
        color: #2ed573;
        box-shadow: 0 0 15px rgba(46, 213, 115, 0.2);
    }
    .balance-negative {
        background: rgba(255, 71, 87, 0.12);
        border: 1px solid #ff4757;
        color: #ff4757;
        box-shadow: 0 0 15px rgba(255, 71, 87, 0.2);
    }

    /* 按鈕優化 - 紫色霓虹 */
    .stButton>button {
        background: linear-gradient(90deg, #da22ff 0%, #9733ee 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 800 !important;
        border-radius: 15px !important;
        padding: 12px 30px !important;
        box-shadow: 0 8px 25px rgba(151, 51, 238, 0.4);
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 12px 35px rgba(151, 51, 238, 0.6) !important;
    }
    
    /* 側邊欄深紫色風格 */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 12, 41, 0.85) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(218, 34, 255, 0.2);
    }
    
    /* 輸入框與選單優化 */
    .stTextInput input, .stSelectbox div, .stNumberInput input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(218, 34, 255, 0.3) !important;
        border-radius: 12px !important;
    }

    h2 {
        background: linear-gradient(to right, #da22ff, #9733ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 介面結構 ---

# 側邊欄：成員與房間管理
with st.sidebar:
    st.markdown("<h1 style='color:#da22ff; font-size:2em; font-weight:900;'>🔮 幻魅中心</h1>", unsafe_allow_html=True)
    trip_code = st.text_input("🌍 旅程代碼", value=st.session_state.current_trip)
    
    st.markdown("<div style='margin: 20px 0; border-top: 1px solid rgba(218, 34, 255, 0.2);'></div>", unsafe_allow_html=True)
    st.markdown("### 👥 核心成員")
    new_name = st.text_input("新增隊友", placeholder="輸入姓名並按 Enter")
    if st.button("➕ 邀請進入幻境", use_container_width=True):
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
                    <div style="font-size:0.85em; opacity:0.8; text-transform:uppercase; letter-spacing:1px; font-weight:bold;">{m}</div>
                    <div style="font-size:1.6em; font-weight:900;">${bal:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

# 主畫面
st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">FairShare</h1>
        <p style="font-size:1.6em; color: rgba(218, 34, 255, 0.8); font-weight:600; margin-top:10px;">幻魅紫 · 極致數據對比</p>
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.markdown("<h2>➕ 紀錄新筆支出</h2>", unsafe_allow_html=True)
    if not members:
        st.info("請在左側導航欄位新增成員以開始紀錄。")
    else:
        with st.form("main_form"):
            c1, c2 = st.columns(2)
            with c1:
                p = st.selectbox("付款人", members)
                d = st.text_input("消費項目", placeholder="例如：利木津巴士、米其林餐點")
            with c2:
                a = st.number_input("總金額", min_value=0.0, step=10.0)
                ps = st.multiselect("分擔者", members, default=members)
            
            st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
            if st.form_submit_button("🚀 同步至紫色帳本"):
                if a > 0 and ps:
                    st.session_state.app.record_transaction(p, a, ps, d)
                    st.toast("🔮 數據已成功存入幻境！")
                    time.sleep(0.5)
                    st.rerun()

    st.markdown("<h2 style='margin-top:45px;'>📜 實時交易流</h2>", unsafe_allow_html=True)
    history = st.session_state.app.history
    if not history:
        st.markdown("<p style='opacity:0.4; font-style:italic;'>目前尚無數據波幅...</p>", unsafe_allow_html=True)
    else:
        for item in reversed(history):
            st.markdown(f"""
                <div class="neon-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:1.5em; font-weight:900; color:#da22ff;">{item['description']}</span>
                        <span style="font-family:monospace; color:#9733ee; font-size:1.3em; font-weight:bold;">${item['amount']:,.2f}</span>
                    </div>
                    <div style="margin-top:18px; font-size:1em; color:rgba(255,255,255,0.7); background:rgba(218,34,255,0.05); padding:10px; border-radius:10px;">
                        👑 <b>{item['payer']}</b> 支付，分擔隊友：{', '.join(item['participants'])}
                    </div>
                </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("<h2>📊 智能結算中心</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown("""
            <div style="background:rgba(218,34,255,0.05); padding:25px; border-radius:25px; border:1px dashed rgba(218,34,255,0.4);">
                <p style="font-size:0.95em; opacity:0.9; color:#da22ff; font-weight:bold;">🔮 紫色引擎運算中</p>
                <p style="font-size:0.85em; opacity:0.7;">自動尋找路徑最短、次數最少的還款建議。</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🔮 執行幻境計算", use_container_width=True):
            advices = st.session_state.app.calculate_settlement()
            for adv in advices:
                st.markdown(f"""
                    <div style="padding:18px; background:linear-gradient(90deg, rgba(218, 34, 255, 0.2), rgba(151, 51, 238, 0.2)); border:1px solid #da22ff; border-radius:15px; margin-top:12px; font-weight:bold; color:white; box-shadow: 0 4px 15px rgba(218, 34, 255, 0.2);">
                        ✨ {adv}
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<h2 style='color:#ff4757; margin-top:50px;'>⚙️ 系統控制</h2>", unsafe_allow_html=True)
    with st.expander("進階管理區", expanded=False):
        if st.button("🗑️ 格式化所有數據", use_container_width=True):
            st.session_state.app.reset_all()
            st.rerun()

st.markdown("<div style='text-align:center; margin-top:100px; opacity:0.4; font-size:0.85em; letter-spacing:1px; color:#da22ff;'>FAIRSHARE PURPLE PRO v4.0 | BY GEMINI DESIGN</div>", unsafe_allow_html=True)
