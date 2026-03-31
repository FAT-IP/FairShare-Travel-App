import streamlit as st
import requests
from streamlit_lottie import st_lottie
import time

# 嘗試導入模型，並加入錯誤處理以防路徑或語法問題
try:
    from models import FairShareModel
except Exception as e:
    st.error(f"模型載入失敗: {e}")
    # 提供一個簡單的後備類以維持介面運作
    class FairShareModel:
        def __init__(self, trip_id):
            self.members = {}
            self.history = []
        def add_member(self, name): return False
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
                <h1 style="color: #667eea; font-size: 3.5em;">準備啟程...</h1>
                <p style="color: #666; font-size: 1.5em;">正在載入您的 FairShare 旅伴帳本</p>
            </div>
        """, unsafe_allow_html=True)
        if lottie_welcome: st_lottie(lottie_welcome, height=400, key="welcome")
        time.sleep(1.2)
    placeholder.empty()
    st.session_state.first_load_done = True

# --- 2. 多房間邏輯初始化 ---
with st.sidebar:
    st.title("🏠 房間系統")
    trip_code = st.text_input("輸入旅程代碼 (例如：Japan123)", value="")
    
    if 'app' not in st.session_state or st.session_state.get('current_trip') != trip_code:
        st.session_state.app = FairShareModel(trip_id=trip_code)
        st.session_state.current_trip = trip_code
    
    st.info(f"📍 目前房間：{trip_code}")

# --- 3. 恢復豐富漸層與對比度強化 CSS (含側邊欄優化) ---
st.markdown("""
    <style>
    /* 全域背景 */
    .stApp {
        background: linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%);
        background-attachment: fixed;
    }

    /* 側邊欄文字優化 */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
    }
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label {
        color: #311B92 !important; /* 深紫色確保標籤清晰 */
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2 {
        color: #4527A0 !important;
        font-weight: 900 !important;
    }
    /* 側邊欄輸入框文字顏色 */
    [data-testid="stSidebar"] input {
        color: #1A237E !important;
        font-weight: 500 !important;
    }

    /* 頂部橫幅 */
    .main-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 50px 20px;
        border-radius: 25px;
        color: white !important;
        text-align: center;
        margin-bottom: 35px;
        box-shadow: 0 20px 40px rgba(118, 75, 162, 0.25);
        position: relative;
        overflow: hidden;
    }
    .main-banner h1, .main-banner p { color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }

    /* 玻璃擬態卡片 */
    .info-card {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-left: 8px solid #764ba2;
        transition: all 0.3s ease;
    }
    .info-card:hover { transform: translateY(-3px); box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15); }
    
    .info-card h4 { color: #4A00E0 !important; font-weight: 900; margin-bottom: 10px !important; }
    .info-card p, .info-card b { color: #1A1A1A !important; font-size: 1.1em; }
    .info-card small { color: #555555 !important; font-weight: 500; }

    /* 餘額卡片 */
    .balance-card {
        padding: 18px; 
        border-radius: 15px; 
        background: rgba(255, 255, 255, 0.98) !important; 
        margin-bottom: 15px;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .balance-card:hover { transform: scale(1.02); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .balance-name { color: #1A237E !important; font-weight: 800; font-size: 1.15em; display: block; margin-bottom: 5px; }
    
    /* 按鈕樣式 */
    .stButton>button {
        border-radius: 15px;
        font-weight: 800;
        padding: 0.6rem 1.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 5px 15px rgba(118, 75, 162, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(118, 75, 162, 0.4);
    }
    
    h3 { color: #4A00E0 !important; font-weight: 900 !important; border-bottom: 3px solid #764ba2; display: inline-block; padding-bottom: 5px; margin-bottom: 25px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 頂部橫幅 ---
st.markdown(f"""
    <div class="main-banner">
        <h1 style="margin: 0; font-size: 3.5em; font-weight: 900; letter-spacing: 3px;">✈️ FairShare</h1>
        <p style="font-size: 1.3em; opacity: 0.95; margin-top: 15px; font-weight: 500;">房間代碼：<span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 8px; font-family: monospace;">{trip_code}</span></p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. 側邊欄成員管理 ---
with st.sidebar:
    st.divider()
    st.header("👥 旅伴管理")
    new_name = st.text_input("新增成員姓名", key="sidebar_add_name", placeholder="輸入姓名...")
    if st.button("確認加入", use_container_width=True):
        if new_name and st.session_state.app.add_member(new_name):
            st.toast(f"✅ {new_name} 已加入！")
            st.rerun()
    
    st.divider()
    members = list(st.session_state.app.members.keys())
    if members:
        st.subheader("💰 實時餘額")
        for m in members:
            bal = st.session_state.app.members[m]
            color = "#1B5E20" if bal >= 0 else "#B71C1C" # 使用更深的紅綠色確保對比
            st.markdown(f"""
                <div class="balance-card" style="border-left: 6px solid {color};">
                    <span class="balance-name">{m}</span>
                    <span style="color: {color}; font-weight: 900; font-size: 1.3em;">{'+' if bal > 0 else ''}${bal:,.2f}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        to_remove = st.selectbox("選擇成員移除", members)
        if st.button("執行移除", use_container_width=True):
            success, msg = st.session_state.app.remove_member(to_remove)
            if success:
                st.success(msg)
                st.rerun()

# --- 6. 主畫面分欄 ---
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("### 📝 紀錄支出")
    if not members:
        if lottie_empty: st_lottie(lottie_empty, height=180)
        st.info("請先在左側選單新增旅伴，開始您的分帳旅程！")
    else:
        with st.form("expense_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                payer = st.selectbox("付錢的人", members)
                desc = st.text_input("消費項目", placeholder="例如：計程車、晚餐")
            with c2:
                amount = st.number_input("總金額", min_value=0.0, step=1.0)
                participants = st.multiselect("分擔的人", members, default=members)
            
            if st.form_submit_button("🚀 儲存紀錄", use_container_width=True):
                if participants and amount > 0:
                    st.session_state.app.record_transaction(payer, amount, participants, desc)
                    st.balloons()
                    st.rerun()

    st.divider()
    st.markdown("### 📖 消費流水帳")
    history = st.session_state.app.history
    if not history:
        st.markdown("<p style='color: #444; font-style: italic;'>尚無紀錄。</p>", unsafe_allow_html=True)
    else:
        for item in reversed(history):
            st.markdown(f"""
            <div class="info-card">
                <h4>{item['description'] if item['description'] else '一般支出'}</h4>
                <p><b>{item['payer']}</b> 支付了 <b>${item['amount']:,.2f}</b></p>
                <small>參與者: {', '.join(item['participants'])}</small>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.markdown("### 🔍 結算建議")
    if lottie_money: st_lottie(lottie_money, height=150, key="money")
    
    if st.button("計算還款方案", use_container_width=True, type="primary"):
        advices = st.session_state.app.calculate_settlement()
        if not advices:
            st.snow()
            st.success("目前帳目完全平衡！")
        else:
            for a in advices:
                st.warning(a)
    
    st.divider()
    st.markdown("### ⚙️ 管理控制")
    
    if st.button("撤銷上一筆紀錄", use_container_width=True):
        if history:
            if st.session_state.app.delete_transaction_by_index(len(history) - 1):
                st.toast("已撤銷上一筆消費")
                st.rerun()

    if history:
        options = [f"{i+1}. {h['description']} (${h['amount']})" for i, h in enumerate(history)]
        to_del = st.selectbox("手動刪除項目", options)
        if st.button("🔥 確認刪除", use_container_width=True):
            if st.session_state.app.delete_transaction_by_index(options.index(to_del)):
                st.rerun()
    
    if st.button("🧹 清空所有數據", use_container_width=True):
        if st.checkbox("確認重置房間"):
            st.session_state.app.reset_all()
            st.rerun()

st.markdown("<br><p style='text-align: center; color: #4A00E0; font-weight: 800;'>FairShare | 讓每一趟旅程更公平、更優雅</p>", unsafe_allow_html=True)
