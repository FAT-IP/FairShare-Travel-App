import streamlit as st
import requests
from streamlit_lottie import st_lottie
import time

# --- 模型導入與錯誤處理 ---
try:
    from models import FairShareModel
except Exception:
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
            <div style="text-align: center; padding-top: 100px; animation: fadeIn 2s;">
                <h1 style="color: #4834d4; font-size: 3.5em; font-weight: 900; letter-spacing: -1px;">FairShare</h1>
                <p style="color: #686de0; font-size: 1.5em; font-weight: 700;">開啟您的優雅旅行紀錄...</p>
            </div>
            <style> @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } } </style>
        """, unsafe_allow_html=True)
        if lottie_welcome: st_lottie(lottie_welcome, height=400, key="welcome")
        time.sleep(1.2)
    placeholder.empty()
    st.session_state.first_load_done = True

# --- 2. 初始化邏輯 ---
if 'current_trip' not in st.session_state:
    st.session_state.current_trip = "default"

with st.sidebar:
    st.markdown("""<h2 style='text-align: center; color: #30336b; font-weight: 900; margin-bottom: 20px;'>🏠 房間系統</h2>""", unsafe_allow_html=True)
    trip_code = st.text_input("輸入旅程代碼", value=st.session_state.current_trip)
    
    if 'app' not in st.session_state or st.session_state.current_trip != trip_code:
        st.session_state.app = FairShareModel(trip_id=trip_code)
        st.session_state.current_trip = trip_code
    
    st.markdown(f"""
        <div style="background: rgba(104, 109, 224, 0.1); padding: 10px; border-radius: 10px; border: 1px dashed #686de0; text-align: center; color: #4834d4; font-weight: bold;">
            📍 目前房間：{trip_code}
        </div>
    """, unsafe_allow_html=True)

# --- 3. 核心 CSS 樣式視覺豐富化 ---
st.markdown("""
    <style>
    /* 動態流動背景 */
    .stApp {
        background: linear-gradient(-45deg, #f0f2f6, #e0eafc, #cfd9df, #e2ebf0);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        background-attachment: fixed;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 側邊欄優化 */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.3) !important;
    }

    /* 頂部橫幅：更具現代感的設計 */
    .main-banner {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        padding: 50px 20px;
        border-radius: 40px;
        text-align: center;
        margin-bottom: 40px;
        border: 2px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 15px 35px rgba(31, 38, 135, 0.08);
        position: relative;
        overflow: hidden;
    }
    .main-banner::before {
        content: "";
        position: absolute;
        top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(104, 109, 224, 0.1) 0%, transparent 70%);
        z-index: -1;
    }

    /* 資訊卡片：精細化邊框與投影 */
    .info-card {
        background: rgba(255, 255, 255, 0.8) !important;
        padding: 25px;
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05);
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .info-card:hover {
        transform: translateY(-8px) scale(1.02);
        background: rgba(255, 255, 255, 0.95) !important;
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.1);
    }

    /* 餘額卡片：增加漸變層次 */
    .balance-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%) !important;
        padding: 18px;
        border-radius: 18px;
        margin-bottom: 15px;
        border: 1px solid rgba(0,0,0,0.03);
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    }

    /* 按鈕優化 */
    .stButton>button {
        border-radius: 15px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.03);
    }

    /* 標題裝飾 */
    h3 { 
        color: #30336b !important; 
        font-weight: 900 !important; 
        position: relative;
        padding-bottom: 10px;
        margin-top: 30px !important;
    }
    h3::after {
        content: "";
        position: absolute;
        bottom: 0; left: 0;
        width: 60px; height: 5px;
        background: #686de0;
        border-radius: 10px;
    }
    
    /* 表單區塊 */
    .stForm {
        background: rgba(255, 255, 255, 0.5) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 畫面呈現 ---
st.markdown(f"""
    <div class="main-banner">
        <h1 style="margin:0; font-size: 4.5em; letter-spacing: -2px; font-weight: 900; color: #4834d4;">FairShare</h1>
        <p style="font-size:1.4em; font-weight:600; color: #686de0; margin-top:10px;">✨ 讓每一趟旅程的終點，都優雅且清晰</p>
    </div>
    """, unsafe_allow_html=True)

# 側邊欄內容
with st.sidebar:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("### 👥 旅伴名單")
    new_name = st.text_input("新增成員", placeholder="輸入姓名並按 Enter")
    if st.button("➕ 邀請加入", use_container_width=True):
        if new_name:
            st.session_state.app.add_member(new_name)
            st.rerun()
    
    st.markdown("---")
    members = list(st.session_state.app.members.keys())
    if members:
        st.markdown("#### 💰 個別餘額")
        for m in members:
            bal = st.session_state.app.members[m]
            status_color = "#2ed573" if bal >= 0 else "#ff4757"
            st.markdown(f"""
                <div class="balance-card" style="border-left: 6px solid {status_color};">
                    <div style="font-weight:800; color:#2f3542; font-size:0.95em; opacity: 0.8;">{m}</div>
                    <div style="color:{status_color}; font-size:1.4em; font-weight:900;">${bal:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

# 主區域
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.markdown("### ✍️ 新增一筆消費")
    if not members:
        st.warning("💡 **開始之前**：請先在左側選單新增旅伴，系統將自動為您建立帳本！")
    else:
        with st.form("expense_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                p = st.selectbox("誰付的錢？", members)
                d = st.text_input("消費了什麼？", placeholder="例：東京鐵塔門票")
            with f_col2:
                a = st.number_input("總金額 (USD)", min_value=0.0, step=10.0)
                ps = st.multiselect("誰要分擔？", members, default=members)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("✅ 儲存紀錄並同步", use_container_width=True):
                if a > 0 and ps:
                    st.session_state.app.record_transaction(p, a, ps, d)
                    st.balloons()
                    st.rerun()

    st.markdown("### 📜 消費流水帳")
    history = st.session_state.app.history
    if not history:
        st.info("尚無任何消費紀錄。")
    else:
        for item in reversed(history):
            st.markdown(f"""
                <div class="info-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin:0; color:#30336b; font-weight:900; font-size: 1.3em;">🛒 {item['description'] if item['description'] else '一般支出'}</h4>
                        <span style="background: #ebf0f1; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; color: #7f8c8d;">Recent</span>
                    </div>
                    <p style="margin:15px 0; font-size:1.15em; color: #2f3542;">
                        <b>{item['payer']}</b> 慷慨支付了 <span style="color:#4834d4; font-weight:900;">${item['amount']:,.2f}</span>
                    </p>
                    <div style="background: rgba(104, 109, 224, 0.05); padding: 12px; border-radius: 12px; border: 1px solid rgba(104, 109, 224, 0.1);">
                        <small style="color:#535c68; display: block;">👥 <b>分擔者：</b> {', '.join(item['participants'])}</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 結算建議")
    st.markdown("<p style='font-size:0.9em; color:#535c68;'>點擊下方按鈕，系統將計算最少還款次數的優化方案。</p>", unsafe_allow_html=True)
    if st.button("💎 執行智能結算", use_container_width=True, type="primary"):
        advices = st.session_state.app.calculate_settlement()
        if not advices:
            st.success("🎉 所有帳目已清，可以安心回家囉！")
        else:
            for adv in advices:
                st.markdown(f"""
                    <div style="padding: 12px; background: white; border-radius: 12px; margin-bottom: 8px; border-left: 5px solid #686de0; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        ✨ {adv}
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("### 🛠️ 管理控制")
    with st.expander("進階設定", expanded=False):
        if st.button("⏪ 撤銷上一筆紀錄", use_container_width=True):
            if history:
                st.session_state.app.delete_transaction_by_index(len(history)-1)
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧨 重置所有帳目", use_container_width=True):
            if st.checkbox("確認清除？數據將無法恢復。"):
                st.session_state.app.reset_all()
                st.rerun()

st.markdown("<br><hr style='border: 0; height: 1px; background: linear-gradient(to right, transparent, rgba(48, 51, 107, 0.2), transparent);'><p style='text-align:center; color:#30336b; font-weight:800; font-size: 0.9em; opacity:0.5;'>FairShare v2.5 | 優雅分帳，每一筆都值得被溫柔紀錄</p>", unsafe_allow_html=True)
