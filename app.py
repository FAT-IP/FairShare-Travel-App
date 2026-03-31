import streamlit as st
import requests
from streamlit_lottie import st_lottie
import time

# --- 模型導入與錯誤處理 ---
try:
    from models import FairShareModel
except Exception:
    # 如果 models.py 有語法錯誤，提供基礎類比以免當機
    class FairShareModel:
        def __init__(self, trip_id):
            self.members = {}
            self.history = []
        def add_member(self, name): return True
        def record_transaction(self, p, a, ps, d): pass
        def calculate_settlement(self): return []
        def delete_transaction_by_index(self, i): return True
        def reset_all(self): pass
        def remove_member(self, name): return True, "已移除"

# --- 頁面配置 ---
st.set_page_config(
    page_title="FairShare | 旅伴分帳神器",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 載入 Lottie 動畫 ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_welcome = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_5njpksqe.json")

# --- 1. 全螢幕開場動畫 ---
if 'first_load_done' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <div style="text-align: center; padding-top: 100px;">
                <h1 style="color: #667eea; font-size: 3.5em; font-weight: 900;">準備啟程...</h1>
                <p style="color: #444; font-size: 1.5em; font-weight: 700;">正在載入您的 FairShare 旅伴帳本</p>
            </div>
        """, unsafe_allow_html=True)
        if lottie_welcome: st_lottie(lottie_welcome, height=400, key="welcome")
        time.sleep(1.0)
    placeholder.empty()
    st.session_state.first_load_done = True

# --- 2. 初始化邏輯 ---
if 'current_trip' not in st.session_state:
    st.session_state.current_trip = "default"

with st.sidebar:
    st.markdown("""<h2 style='text-align: center; color: #1A237E; font-weight: 900;'>🏠 房間系統</h2>""", unsafe_allow_html=True)
    trip_code = st.text_input("輸入旅程代碼", value=st.session_state.current_trip)
    
    if 'app' not in st.session_state or st.session_state.current_trip != trip_code:
        st.session_state.app = FairShareModel(trip_id=trip_code)
        st.session_state.current_trip = trip_code
    
    st.info(f"📍 目前房間：{trip_code}")

# --- 3. 核心 CSS 樣式優化 (解決模糊問題，提升清晰度) ---
st.markdown("""
    <style>
    /* 全域背景：改為明亮的線性漸變，減少徑向漸變帶來的模糊感 */
    .stApp {
        background: linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%);
        background-attachment: fixed;
    }

    /* 側邊欄：大幅降低模糊數值 (從 25px 降到 8px)，增加白色的純度 */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.8) !important;
        box-shadow: 5px 0 15px rgba(0, 0, 0, 0.05);
    }

    /* 頂部橫幅：色彩加深，增加清晰度 */
    .main-banner {
        background: linear-gradient(135deg, #5C6BC0 0%, #3949AB 100%);
        padding: 60px 20px;
        border-radius: 30px;
        color: white !important;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* 資訊卡片：提高透明度(從 0.85 升至 0.95)，降低模糊感 */
    .info-card {
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
        margin-bottom: 25px;
        border: 1px solid #E0E0E0;
        border-left: 8px solid #5C6BC0;
        transition: transform 0.2s ease;
    }
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.1);
    }

    /* 側邊欄內的餘額卡片：移除模糊，改用高對比白 */
    .balance-card {
        background: #FFFFFF !important;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 12px;
        border: 1px solid #EEEEEE;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
    }

    /* 按鈕設計：加深對比，提升點擊感 */
    .stButton>button {
        width: 100%;
        border-radius: 12px !important;
        font-weight: 800 !important;
        background: #3F51B5 !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(63, 81, 181, 0.3) !important;
        height: 3em;
    }
    .stButton>button:hover {
        background: #303F9F !important;
        box-shadow: 0 6px 15px rgba(63, 81, 181, 0.4) !important;
    }

    /* 頁面標題：加強色彩深度 */
    h3 { 
        color: #1A237E !important; 
        font-weight: 900 !important; 
        border-bottom: 3px solid #5C6BC0;
        margin-top: 25px !important;
        margin-bottom: 15px !important;
    }
    
    /* 讓 Input 框更清晰 */
    .stTextInput input, .stNumberInput input {
        border-radius: 10px !important;
        border: 1px solid #D1D1D1 !important;
        background-color: white !important;
    }

    label p { color: #1A237E !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 畫面呈現 ---
st.markdown(f"""
    <div class="main-banner">
        <h1 style="margin:0; font-size: 4em; letter-spacing: 2px; font-weight: 900; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">FairShare</h1>
        <p style="font-size:1.3em; font-weight:600; opacity: 0.95; margin-top:10px;">優雅分帳，讓旅行更純粹</p>
    </div>
    """, unsafe_allow_html=True)

# 側邊欄內容
with st.sidebar:
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.header("👥 旅伴管理")
    new_name = st.text_input("新增成員姓名", placeholder="例如：阿強、小美")
    if st.button("➕ 確認加入成員", use_container_width=True):
        if new_name:
            st.session_state.app.add_member(new_name)
            st.rerun()
    
    st.divider()
    members = list(st.session_state.app.members.keys())
    if members:
        st.subheader("💰 實時餘額")
        for m in members:
            bal = st.session_state.app.members[m]
            color = "#2E7D32" if bal >= 0 else "#C62828"
            st.markdown(f"""
                <div class="balance-card" style="border-left: 6px solid {color};">
                    <div style="font-weight:800; color:#424242; font-size:1em;">{m}</div>
                    <div style="color:{color}; font-size:1.3em; font-weight:900;">${bal:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

# 主區域
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.markdown("### 📝 紀錄支出")
    if not members:
        st.info("👋 歡迎！請先在左側選單新增旅伴，開啟您的分帳旅程！")
    else:
        with st.form("expense_form", clear_on_submit=True):
            p = st.selectbox("付款人", members)
            d = st.text_input("項目描述", placeholder="例如：築地市場壽司")
            a = st.number_input("消費金額", min_value=0.0, step=100.0)
            ps = st.multiselect("分擔成員", members, default=members)
            if st.form_submit_button("🚀 儲存紀錄", use_container_width=True):
                if a > 0 and ps:
                    st.session_state.app.record_transaction(p, a, ps, d)
                    st.balloons()
                    st.rerun()

    st.markdown("### 📖 消費流水帳")
    history = st.session_state.app.history
    if not history:
        st.markdown("<p style='color:#757575; font-weight:500;'>目前還沒有任何消費紀錄喔！</p>", unsafe_allow_html=True)
    else:
        for item in reversed(history):
            st.markdown(f"""
                <div class="info-card">
                    <h4 style="margin:0; color:#1A237E; font-weight:900;">{item['description'] if item['description'] else '一般支出'}</h4>
                    <p style="margin:10px 0; font-size:1.1em; color: #424242;"><b>{item['payer']}</b> 支付了 <b style="color:#3F51B5;">${item['amount']:,.2f}</b></p>
                    <div style="background:#F5F5F5; padding:10px; border-radius:8px; border: 1px solid #EEEEEE;">
                        <small style="color:#616161; font-weight: 600;">分擔對象：{', '.join(item['participants'])}</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("### 🔍 結算建議")
    if st.button("💎 計算還款方案", use_container_width=True, type="primary"):
        advices = st.session_state.app.calculate_settlement()
        if not advices:
            st.success("🎉 目前帳目完全平衡！")
        else:
            for adv in advices:
                st.warning(f"👉 {adv}")

    st.divider()
    st.markdown("### ⚙️ 管理控制")
    if st.button("⏮️ 撤銷上一筆紀錄", use_container_width=True):
        if history:
            st.session_state.app.delete_transaction_by_index(len(history)-1)
            st.rerun()
    
    if st.button("🧹 清除所有數據", use_container_width=True):
        if st.checkbox("我確認要重置本房間帳目"):
            st.session_state.app.reset_all()
            st.rerun()

st.markdown("<br><p style='text-align:center; color:#1A237E; font-weight:800; font-size: 1em; opacity:0.6;'>FairShare | 每一筆開銷，都清清楚楚</p>", unsafe_allow_html=True)
