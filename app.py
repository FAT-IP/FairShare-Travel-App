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
lottie_money = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_y9m8preo.json")
lottie_empty = load_lottieurl("https://assets1.lottiefiles.com/temp/lf20_09SInp.json")

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
    st.title("🏠 房間系統")
    trip_code = st.text_input("輸入旅程代碼", value=st.session_state.current_trip)
    
    if 'app' not in st.session_state or st.session_state.current_trip != trip_code:
        st.session_state.app = FairShareModel(trip_id=trip_code)
        st.session_state.current_trip = trip_code
    
    st.info(f"📍 目前房間：{trip_code}")

# --- 3. 核心 CSS 樣式優化 (強化按鈕層次與背景) ---
st.markdown("""
    <style>
    /* 全域背景 */
    .stApp {
        background: linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%);
        background-attachment: fixed;
    }

    /* 側邊欄磨砂效果 */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.45) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255,255,255,0.3);
    }

    /* 頂部橫幅 */
    .main-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 45px 20px;
        border-radius: 30px;
        color: white !important;
        text-align: center;
        margin-bottom: 35px;
        box-shadow: 0 20px 40px rgba(118, 75, 162, 0.25), inset 0 0 20px rgba(255,255,255,0.1);
    }

    /* 資訊卡片：增強立體感 */
    .info-card {
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 25px;
        border-radius: 24px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.06);
        margin-bottom: 20px;
        border-left: 12px solid #764ba2;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .info-card:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 0 20px 45px rgba(0,0,0,0.1);
    }

    /* 餘額卡片 */
    .balance-card {
        background: white !important;
        padding: 20px;
        border-radius: 18px;
        margin-bottom: 15px;
        box-shadow: 0 8px 18px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.03);
    }

    /* --- 按鈕重做：極致層次感 --- */
    .stButton>button {
        width: 100%;
        border-radius: 16px !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        padding: 0.7rem 1.5rem !important;
        background: linear-gradient(145deg, #7e57c2, #673ab7) !important; /* 立體漸層 */
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 8px 20px rgba(103, 58, 183, 0.3), 
                    inset 0 4px 4px rgba(255,255,255,0.2),
                    inset 0 -4px 4px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton>button:hover {
        background: linear-gradient(145deg, #9575cd, #7e57c2) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 25px rgba(103, 58, 183, 0.4), 
                    inset 0 4px 4px rgba(255,255,255,0.3) !important;
    }

    .stButton>button:active {
        transform: translateY(1px) !important;
        box-shadow: 0 4px 10px rgba(103, 58, 183, 0.3) !important;
    }

    /* 特殊按鈕：計算還款方案 (Primary 字體加亮) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(145deg, #4A00E0, #8E2DE2) !important;
    }

    /* 提示框優化 */
    div[data-testid="stNotification"][aria-label="Success"] {
        background-color: #1B5E20 !important;
        border-radius: 20px !important;
        border: 2px solid #C8E6C9 !important;
    }

    h3 { 
        color: #311B92 !important; 
        font-weight: 900 !important; 
        border-bottom: 5px solid #764ba2;
        padding-bottom: 8px;
        margin-top: 20px !important;
    }
    
    label p { color: #000000 !important; font-weight: 800 !important; font-size: 1.05rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 畫面呈現 ---
st.markdown(f"""
    <div class="main-banner">
        <h1 style="margin:0; font-size: 3.5em; letter-spacing: 2px;">✈️ FairShare</h1>
        <p style="font-size:1.4em; font-weight:700; opacity: 0.95; margin-top:10px;">旅程代碼：{trip_code}</p>
    </div>
    """, unsafe_allow_html=True)

# 側邊欄內容
with st.sidebar:
    st.header("👥 旅伴管理")
    new_name = st.text_input("新增成員姓名", placeholder="例如：阿強")
    if st.button("確認加入", use_container_width=True):
        if new_name:
            st.session_state.app.add_member(new_name)
            st.rerun()
    
    st.divider()
    members = list(st.session_state.app.members.keys())
    if members:
        st.subheader("💰 目前餘額")
        for m in members:
            bal = st.session_state.app.members[m]
            color = "#1B5E20" if bal >= 0 else "#B71C1C"
            st.markdown(f"""
                <div class="balance-card" style="border-left: 10px solid {color};">
                    <div class="balance-name">{m}</div>
                    <div style="color:{color}; font-size:1.6em; font-weight:900;">${bal:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

# 主區域
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.markdown("### 📝 紀錄支出")
    if not members:
        st.warning("請先在左側選單新增旅伴！")
    else:
        # 使用自定義容器樣式包裹表單內容 (透過 CSS 直接對 form 生效)
        with st.form("expense_form", clear_on_submit=True):
            p = st.selectbox("付款人", members)
            d = st.text_input("項目描述", placeholder="晚餐、門票、包車...")
            a = st.number_input("消費金額", min_value=0.0, step=10.0)
            ps = st.multiselect("參與成員 (分擔)", members, default=members)
            if st.form_submit_button("🚀 儲存紀錄", use_container_width=True):
                if a > 0 and ps:
                    st.session_state.app.record_transaction(p, a, ps, d)
                    st.balloons()
                    st.rerun()

    st.markdown("### 📖 消費流水帳")
    history = st.session_state.app.history
    if not history:
        st.markdown("<p style='color:#000; font-weight:700; font-size: 1.1em; opacity:0.6;'>目前還沒有任何消費紀錄喔！</p>", unsafe_allow_html=True)
    else:
        for item in reversed(history):
            st.markdown(f"""
                <div class="info-card">
                    <h4>{item['description'] if item['description'] else '一般支出'}</h4>
                    <p><b>{item['payer']}</b> 支付了 <b>${item['amount']:,.2f}</b></p>
                    <small>分擔對象：{', '.join(item['participants'])}</small>
                </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("### 🔍 結算建議")
    if st.button("計算還款方案", use_container_width=True, type="primary"):
        advices = st.session_state.app.calculate_settlement()
        if not advices:
            st.success("🎉 目前帳目完全平衡，太棒了！")
        else:
            for adv in advices:
                st.warning(f"💡 {adv}")

    st.divider()
    st.markdown("### ⚙️ 管理與重置")
    if st.button("撤銷上一筆紀錄", use_container_width=True):
        if history:
            st.session_state.app.delete_transaction_by_index(len(history)-1)
            st.rerun()
    
    if st.button("🧹 重置本房間帳目", use_container_width=True):
        if st.checkbox("我確定要清空所有紀錄"):
            st.session_state.app.reset_all()
            st.rerun()

st.markdown("<br><p style='text-align:center; color:#311B92; font-weight:900; font-size: 1.2em; letter-spacing:1px;'>FairShare | 每一趟旅程，都值得優雅的結束</p>", unsafe_allow_html=True)
