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
                <h1 style="color: #4A00E0; font-size: 3.5em;">準備啟程...</h1>
                <p style="color: #2D3436; font-size: 1.5em;">正在載入您的 FairShare 旅伴帳本</p>
            </div>
        """, unsafe_allow_html=True)
        if lottie_welcome: st_lottie(lottie_welcome, height=400, key="welcome")
        time.sleep(1.5)
    placeholder.empty()
    st.session_state.first_load_done = True

# --- 2. 多房間邏輯初始化 ---
with st.sidebar:
    st.title("🏠 房間系統")
    trip_code = st.text_input("輸入旅程代碼 (例如：SEOUL2026)", value="default")
    
    # 修正：確保 st.session_state.app 存在且 trip_id 正確
    if 'app' not in st.session_state or st.session_state.get('current_trip') != trip_code:
        st.session_state.app = FairShareModel(trip_id=trip_code)
        st.session_state.current_trip = trip_code
    
    st.success(f"目前位置：{trip_code}")

# --- 3. UI 色彩美化與對比度強化 CSS ---
st.markdown("""
    <style>
    /* 全域背景：柔和的漸層 */
    .stApp {
        background: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
    }

    /* 頂部橫幅：深色漸層確保文字清晰 */
    .main-banner {
        background: linear-gradient(135deg, #4A00E0 0%, #8E2DE2 100%);
        padding: 40px 20px;
        border-radius: 20px;
        color: white !important;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(74, 0, 224, 0.2);
    }
    .main-banner h1, .main-banner p { color: white !important; }

    /* 玻璃擬態卡片：加強不透明度與字體顏色，解決截圖中看不清的問題 */
    .info-card {
        background: white !important; /* 直接使用純白背景確保最高對比度 */
        padding: 25px;
        border-radius: 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
        border-left: 8px solid #4A00E0;
    }
    
    /* 強化卡片內所有文字的顏色 */
    .info-card h4 { color: #1A1A1A !important; font-weight: 800; margin-bottom: 8px !important; }
    .info-card p { color: #333333 !important; font-size: 1.1em; margin: 5px 0 !important; }
    .info-card b { color: #000000 !important; }
    .info-card small { color: #666666 !important; font-size: 0.9em; }

    /* 餘額卡片設計 */
    .balance-card {
        padding: 15px; 
        border-radius: 12px; 
        background: #FFFFFF !important; 
        margin-bottom: 12px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .balance-name { color: #1A1A1A !important; font-weight: 700; font-size: 1.1em; }
    
    /* 修正表單標題與標籤 */
    h3 { color: #4A00E0 !important; font-weight: 800 !important; border-left: 5px solid #4A00E0; padding-left: 15px; margin: 25px 0 !important; }
    
    /* 按鈕樣式 */
    .stButton>button {
        border-radius: 12px;
        background: linear-gradient(90deg, #4A00E0 0%, #8E2DE2 100%) !important;
        color: white !important;
        border: none !important;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(74, 0, 224, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 頂部橫幅 ---
st.markdown(f"""
    <div class="main-banner">
        <h1 style="margin: 0; font-size: 3em; font-weight: 900; letter-spacing: 2px;">✈️ FairShare</h1>
        <p style="font-size: 1.2em; opacity: 0.9; margin-top: 10px;">讓每一筆開銷都清清楚楚</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. 側邊欄成員管理 ---
with st.sidebar:
    st.divider()
    st.header("👥 旅伴管理")
    new_name = st.text_input("輸入新旅伴姓名", key="sidebar_add_name", placeholder="例如：阿強")
    if st.button("新增成員", use_container_width=True):
        if new_name and st.session_state.app.add_member(new_name):
            st.toast(f"✅ {new_name} 已加入旅程！")
            st.rerun()
    
    st.divider()
    members = list(st.session_state.app.members.keys())
    if members:
        st.subheader("💰 實時餘額")
        for m in members:
            bal = st.session_state.app.members[m]
            color = "#2E7D32" if bal >= 0 else "#D32F2F"
            st.markdown(f"""
                <div class="balance-card">
                    <div class="balance-name">{m}</div>
                    <div style="color: {color}; font-weight: 800; font-size: 1.2em;">
                        {'+' if bal > 0 else ''}${bal:,.2f}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        to_remove = st.selectbox("移除成員", members)
        if st.button("確認移除", use_container_width=True):
            success, msg = st.session_state.app.remove_member(to_remove)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

# --- 6. 主畫面分欄 ---
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("### 📝 紀錄支出")
    if not members:
        if lottie_empty: st_lottie(lottie_empty, height=180)
        st.info("💡 提示：請先在左側選單新增成員，才能開始分帳喔！")
    else:
        with st.form("expense_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                payer = st.selectbox("誰付的錢？", members)
                desc = st.text_input("消費項目", placeholder="例如：機場接送、第一餐烤肉")
            with c2:
                amount = st.number_input("總金額", min_value=0.0, step=1.0)
                participants = st.multiselect("誰要分擔？", members, default=members)
            
            if st.form_submit_button("✅ 儲存紀錄", use_container_width=True):
                if participants and amount > 0:
                    st.session_state.app.record_transaction(payer, amount, participants, desc)
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫正確的金額並選擇至少一位參與者。")

    st.divider()
    st.markdown("### 📖 消費流水帳")
    history = st.session_state.app.history
    if not history:
        st.markdown("<p style='color: #666; font-style: italic;'>目前還沒有任何消費紀錄。</p>", unsafe_allow_html=True)
    else:
        for item in reversed(history):
            st.markdown(f"""
            <div class="info-card">
                <h4>{item['description'] if item['description'] else '一般支出'}</h4>
                <p><b>{item['payer']}</b> 支付了 <b>${item['amount']:,.2f}</b></p>
                <small>參與成員: {', '.join(item['participants'])}</small>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.markdown("### 🔍 結算建議")
    if lottie_money: st_lottie(lottie_money, height=150, key="money")
    
    if st.button("計算最優還款路徑", use_container_width=True, type="primary"):
        advices = st.session_state.app.calculate_settlement()
        if not advices:
            st.snow()
            st.success("目前帳目完全平衡，大家都互不相欠！")
        else:
            for a in advices:
                st.warning(a)
    
    st.divider()
    st.markdown("### ⚙️ 管理功能")
    
    if st.button("撤銷上一筆紀錄", use_container_width=True):
        if history:
            if st.session_state.app.delete_transaction_by_index(len(history) - 1):
                st.toast("已成功撤銷紀錄")
                st.rerun()
        else:
            st.error("目前沒有紀錄可供撤銷")

    st.divider()
    if history:
        options = [f"{i+1}. {h['description']} ({h['payer']} 付 ${h['amount']})" for i, h in enumerate(history)]
        to_del = st.selectbox("選擇刪除特定項目", options)
        selected_index = options.index(to_del)
        if st.button("🔥 執行刪除", use_container_width=True):
            if st.session_state.app.delete_transaction_by_index(selected_index):
                st.rerun()
    
    if st.button("🧹 重置所有資料", use_container_width=True):
        if st.checkbox("我確定要刪除此房間的所有帳目"):
            st.session_state.app.reset_all()
            st.rerun()

st.markdown("<br><p style='text-align: center; color: #666; font-size: 0.9em;'>FairShare | 打造最流暢的旅伴結帳體驗</p>", unsafe_allow_html=True)
