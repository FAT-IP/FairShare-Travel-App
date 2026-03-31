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
    st.markdown("""<h2 style='text-align: center; color: #311B92; font-weight: 900;'>🏠 房間系統</h2>""", unsafe_allow_html=True)
    trip_code = st.text_input("輸入旅程代碼", value=st.session_state.current_trip)
    
    if 'app' not in st.session_state or st.session_state.current_trip != trip_code:
        st.session_state.app = FairShareModel(trip_id=trip_code)
        st.session_state.current_trip = trip_code
    
    st.info(f"📍 目前房間：{trip_code}")

# --- 3. 核心 CSS 樣式優化 (升級側邊欄與背景) ---
st.markdown("""
    <style>
    /* 升級版全域背景：多層流體漸變 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-image: 
            radial-gradient(at 0% 0%, rgba(224, 195, 252, 0.5) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(142, 197, 252, 0.5) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(255, 230, 250, 0.5) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(200, 240, 255, 0.5) 0px, transparent 50%);
        background-attachment: fixed;
    }

    /* 側邊欄升級：深度玻璃擬態 */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.3) !important;
        backdrop-filter: blur(25px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(25px) saturate(180%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.4) !important;
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.05);
    }

    /* 頂部橫幅：更高級的內發光 */
    .main-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 50px 20px;
        border-radius: 35px;
        color: white !important;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 25px 50px rgba(118, 75, 162, 0.2), inset 0 -5px 15px rgba(0,0,0,0.1);
    }

    /* 資訊卡片：柔和光影 */
    .info-card {
        background: rgba(255, 255, 255, 0.85) !important;
        padding: 28px;
        border-radius: 28px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border: 1px solid rgba(255,255,255,0.6);
        border-left: 12px solid #764ba2;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    }
    .info-card:hover {
        transform: translateY(-10px);
        background: rgba(255, 255, 255, 1) !important;
        box-shadow: 0 30px 60px rgba(0,0,0,0.12);
    }

    /* 側邊欄內的餘額卡片 */
    .balance-card {
        background: rgba(255, 255, 255, 0.6) !important;
        padding: 18px;
        border-radius: 20px;
        margin-bottom: 15px;
        border: 1px solid rgba(255,255,255,0.8);
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        transition: all 0.3s ease;
    }
    .balance-card:hover {
        background: rgba(255, 255, 255, 0.9) !important;
        transform: scale(1.02);
    }

    /* 按鈕設計：層次感強化 */
    .stButton>button {
        width: 100%;
        border-radius: 18px !important;
        font-weight: 900 !important;
        background: linear-gradient(145deg, #7e57c2, #673ab7) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 8px 25px rgba(103, 58, 183, 0.3), 
                    inset 0 4px 6px rgba(255,255,255,0.2) !important;
        transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(145deg, #9575cd, #7e57c2) !important;
        box-shadow: 0 15px 30px rgba(103, 58, 183, 0.4), 
                    inset 0 4px 6px rgba(255,255,255,0.3) !important;
        transform: translateY(-4px) !important;
    }

    /* 頁面標題樣式 */
    h3 { 
        color: #311B92 !important; 
        font-weight: 900 !important; 
        border-bottom: 4px solid #764ba2;
        display: inline-block;
        padding-bottom: 5px;
        margin-top: 30px !important;
        margin-bottom: 20px !important;
    }
    
    label p { color: #2D3436 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 畫面呈現 ---
st.markdown(f"""
    <div class="main-banner">
        <h1 style="margin:0; font-size: 3.8em; letter-spacing: 3px;">✈️ FairShare</h1>
        <p style="font-size:1.4em; font-weight:700; opacity: 0.9; margin-top:10px;">優雅分帳，讓旅行更純粹</p>
    </div>
    """, unsafe_allow_html=True)

# 側邊欄內容
with st.sidebar:
    st.markdown("<hr style='margin: 1em 0; border-color: rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
    st.header("👥 旅伴管理")
    new_name = st.text_input("新增成員姓名", placeholder="輸入姓名並按 Enter")
    if st.button("➕ 確認加入", use_container_width=True):
        if new_name:
            st.session_state.app.add_member(new_name)
            st.rerun()
    
    st.divider()
    members = list(st.session_state.app.members.keys())
    if members:
        st.subheader("💰 實時餘額")
        for m in members:
            bal = st.session_state.app.members[m]
            color = "#1B5E20" if bal >= 0 else "#D32F2F"
            st.markdown(f"""
                <div class="balance-card" style="border-left: 8px solid {color};">
                    <div style="font-weight:900; color:#2D3436; font-size:1.1em;">{m}</div>
                    <div style="color:{color}; font-size:1.4em; font-weight:900;">${bal:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

# 主區域
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.markdown("### 📝 紀錄支出")
    if not members:
        st.info("👋 歡迎！請先在左側側邊欄新增旅伴，開啟分帳之旅。")
    else:
        with st.form("expense_form", clear_on_submit=True):
            p = st.selectbox("付款人", members)
            d = st.text_input("項目描述", placeholder="例如：築地市場壽司、利木津巴士...")
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
        st.markdown("<p style='color:#636e72; font-weight:700;'>目前尚無任何紀錄，快來添加第一筆吧！</p>", unsafe_allow_html=True)
    else:
        for item in reversed(history):
            st.markdown(f"""
                <div class="info-card">
                    <h4 style="margin:0; color:#311B92; font-weight:900;">{item['description'] if item['description'] else '一般支出'}</h4>
                    <p style="margin:10px 0; font-size:1.1em;"><b>{item['payer']}</b> 支付了 <b style="color:#764ba2;">${item['amount']:,.2f}</b></p>
                    <div style="background:rgba(0,0,0,0.03); padding:8px 12px; border-radius:10px;">
                        <small style="color:#636e72;">分擔對象：{', '.join(item['participants'])}</small>
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
    
    if st.button("🧹 重置所有帳目", use_container_width=True):
        if st.checkbox("確認完全清空數據？"):
            st.session_state.app.reset_all()
            st.rerun()

st.markdown("<br><p style='text-align:center; color:#311B92; font-weight:900; font-size: 1.1em; opacity:0.8;'>FairShare | 每一筆開銷，都清清楚楚</p>", unsafe_allow_html=True)
