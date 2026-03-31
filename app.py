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
                <h1 style="color: #4A00E0; font-size: 3.5em; font-weight: 900;">準備啟程...</h1>
                <p style="color: #333; font-size: 1.5em; font-weight: 700;">正在載入您的 FairShare 旅伴帳本</p>
            </div>
        """, unsafe_allow_html=True)
        if lottie_welcome: st_lottie(lottie_welcome, height=400, key="welcome")
        time.sleep(1.0)
    placeholder.empty()
    st.session_state.first_load_done = True

# --- 2. 初始化邏輯 (解決 AttributeError) ---
if 'current_trip' not in st.session_state:
    st.session_state.current_trip = "default"

with st.sidebar:
    st.title("🏠 房間系統")
    trip_code = st.text_input("輸入旅程代碼", value=st.session_state.current_trip)
    
    if 'app' not in st.session_state or st.session_state.current_trip != trip_code:
        st.session_state.app = FairShareModel(trip_id=trip_code)
        st.session_state.current_trip = trip_code
    
    st.info(f"目前房間：{trip_code}")

# --- 3. 核心 CSS 樣式修正 (對比度大幅強化) ---
st.markdown("""
    <style>
    /* 全域背景 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
    }

    /* 頂部橫幅 */
    .main-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 20px;
        border-radius: 20px;
        color: white !important;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    .main-banner h1 { color: white !important; font-weight: 900 !important; }

    /* 資訊卡片：文字強制變黑 */
    .info-card {
        background: white !important;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 10px solid #764ba2;
    }
    .info-card h4 { color: #1A237E !important; font-weight: 900 !important; margin: 0 0 10px 0 !important; }
    .info-card p, .info-card b { color: #000000 !important; font-size: 1.1em !important; font-weight: 700 !important; }
    .info-card small { color: #444444 !important; font-weight: 600 !important; }

    /* 餘額卡片 */
    .balance-card {
        background: white !important;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    .balance-name { color: #000000 !important; font-weight: 900 !important; font-size: 1.2em !important; }

    /* 按鈕樣式 */
    .stButton>button {
        border-radius: 12px;
        font-weight: 900 !important;
        background: #4A00E0 !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px;
    }

    /* 關鍵修正：高對比度提示框 */
    /* 成功 (綠色) */
    div[data-testid="stNotification"][aria-label="Success"] {
        background-color: #2E7D32 !important; /* 深綠色背景 */
        border: 2px solid #1B5E20 !important;
    }
    div[data-testid="stNotification"][aria-label="Success"] p {
        color: #FFFFFF !important; /* 白色文字在深綠背景上極清晰 */
        font-weight: 900 !important;
        font-size: 1.2em !important;
    }

    /* 警告 (黃色) */
    div[data-testid="stNotification"][aria-label="Warning"] {
        background-color: #FFF9C4 !important;
        border: 2px solid #FBC02D !important;
    }
    div[data-testid="stNotification"][aria-label="Warning"] p {
        color: #5D4037 !important; /* 深棕色文字 */
        font-weight: 900 !important;
    }

    h3 { color: #1A237E !important; font-weight: 900 !important; border-bottom: 4px solid #764ba2; }
    
    /* 輸入框標籤文字變黑 */
    label p { color: #000000 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 畫面呈現 ---
st.markdown(f"""
    <div class="main-banner">
        <h1 style="margin:0;">✈️ FairShare 分帳神器</h1>
        <p style="font-size:1.2em; font-weight:700;">旅程代碼：{trip_code}</p>
    </div>
    """, unsafe_allow_html=True)

# 側邊欄內容
with st.sidebar:
    st.header("👥 旅伴管理")
    new_name = st.text_input("新增成員姓名", placeholder="例如：小明")
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
            color = "#1B5E20" if bal >= 0 else "#C62828"
            st.markdown(f"""
                <div class="balance-card" style="border-left: 8px solid {color};">
                    <div class="balance-name">{m}</div>
                    <div style="color:{color}; font-size:1.4em; font-weight:900;">${bal:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

# 主區域
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.markdown("### 📝 紀錄支出")
    if not members:
        st.warning("請先在左側選單新增旅伴！")
    else:
        with st.form("expense_form"):
            p = st.selectbox("誰付錢？", members)
            d = st.text_input("項目名稱", placeholder="例如：飯店、車資")
            a = st.number_input("總金額", min_value=0.0)
            ps = st.multiselect("誰要分擔？", members, default=members)
            if st.form_submit_button("🚀 儲存紀錄", use_container_width=True):
                if a > 0 and ps:
                    st.session_state.app.record_transaction(p, a, ps, d)
                    st.balloons()
                    st.rerun()

    st.markdown("### 📖 消費流水帳")
    history = st.session_state.app.history
    if not history:
        st.markdown("<p style='color:#000; font-weight:700;'>尚未有紀錄。</p>", unsafe_allow_html=True)
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
            st.success("目前帳目完全平衡！")
        else:
            for adv in advices:
                st.warning(adv)

    st.divider()
    st.markdown("### ⚙️ 管理控制")
    if st.button("撤銷上一筆紀錄", use_container_width=True):
        if history:
            st.session_state.app.delete_transaction_by_index(len(history)-1)
            st.rerun()
    
    if st.button("🧹 清空所有數據", use_container_width=True):
        st.session_state.app.reset_all()
        st.rerun()

st.markdown("<br><p style='text-align:center; color:#000; font-weight:900;'>FairShare | 讓分帳不再是難事</p>", unsafe_allow_html=True)
