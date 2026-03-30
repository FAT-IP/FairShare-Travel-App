import streamlit as st
import requests
from streamlit_lottie import st_lottie
import time
from models import FairShareModel

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
                <h1 style="color: #1E88E5; font-size: 3.5em;">準備啟程...</h1>
                <p style="color: #666; font-size: 1.5em;">正在載入您的 FairShare 旅伴帳本</p>
            </div>
        """, unsafe_allow_html=True)
        if lottie_welcome: st_lottie(lottie_welcome, height=400, key="welcome")
        time.sleep(2.0)
    placeholder.empty()
    st.session_state.first_load_done = True

# --- 2. 初始化核心邏輯 ---
if 'app' not in st.session_state:
    st.session_state.app = FairShareModel()

# --- 3. 強制文字顏色 CSS (解決圖片中字體看不見的問題) ---
st.markdown("""
    <style>
    /* 強制設定自定義卡片背景與字體顏色，避免與 Streamlit 主題衝突 */
    .info-card {
        background-color: #f8f9fa !important;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 6px solid #1E88E5;
        color: #1a1a1a !important; /* 強制深灰色文字 */
    }
    .info-card h4 {
        color: #1565C0 !important; /* 強制藍色標題 */
        margin: 0 0 10px 0 !important;
    }
    .info-card p, .info-card b, .info-card small {
        color: #333333 !important; /* 強制內容為深色 */
    }

    .balance-card {
        padding: 12px; 
        border-radius: 10px; 
        background-color: #ffffff !important; 
        margin-bottom: 10px;
        border-left: 5px solid #ccc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        color: #111111 !important;
    }
    .balance-name {
        color: #111111 !important;
        font-weight: bold;
        font-size: 1.1em;
        display: block;
    }
    
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 頂部橫幅 ---
st.markdown("""
    <div style="background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px;">
        <h1 style="margin: 0; font-size: 2.8em;">FairShare ✈️</h1>
        <p style="font-size: 1.2em; opacity: 0.9;">紀錄每一份友誼的公平分擔</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. 側邊欄 ---
with st.sidebar:
    st.header("👥 旅伴管理")
    new_name = st.text_input("輸入新旅伴姓名", key="sidebar_add_name")
    if st.button("➕ 新增成員", use_container_width=True):
        if st.session_state.app.add_member(new_name):
            st.toast(f"{new_name} 已加入！")
            st.rerun()
    
    st.divider()
    members = list(st.session_state.app.members.keys())
    if members:
        st.subheader("實時餘額")
        for m in members:
            bal = st.session_state.app.members[m]
            color = "#2E7D32" if bal >= 0 else "#D32F2F"
            st.markdown(f"""
                <div class="balance-card" style="border-left-color: {color};">
                    <span class="balance-name">{m}</span>
                    <span style="color: {color}; font-weight: bold; font-size: 1.2em;">${bal:,.2f}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        to_remove = st.selectbox("選擇要移除的成員", members)
        if st.button("🗑️ 移除此成員", use_container_width=True):
            success, msg = st.session_state.app.remove_member(to_remove)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

# --- 6. 主畫面分欄 ---
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("### 💸 紀錄支出")
    if not members:
        if lottie_empty: st_lottie(lottie_empty, height=180)
        st.info("請先在左側新增旅伴成員喔！")
    else:
        with st.form("expense_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                payer = st.selectbox("付錢的人", members)
                desc = st.text_input("消費項目", placeholder="例如：計程車費、晚餐")
            with c2:
                amount = st.number_input("總金額", min_value=0.0, step=10.0)
                participants = st.multiselect("參與成員", members, default=members)
            
            if st.form_submit_button("🚀 儲存紀錄", use_container_width=True):
                if participants and amount > 0:
                    st.session_state.app.record_transaction(payer, amount, participants, desc)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("請確認金額大於 0 且至少有一位參與者。")

    st.divider()
    st.markdown("### 📖 消費流水帳")
    history = st.session_state.app.history
    if not history:
        st.caption("目前尚無任何紀錄。")
    else:
        for item in reversed(history):
            st.markdown(f"""
            <div class="info-card">
                <span style="float: right; font-size: 1.5em;">💰</span>
                <h4>{item['description'] if item['description'] else '一般支出'}</h4>
                <p><b>{item['payer']}</b> 支付了 <b>${item['amount']:,.2f}</b></p>
                <small>分擔對象: {', '.join(item['participants'])}</small>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.markdown("### 📊 結算與管理")
    if lottie_money: st_lottie(lottie_money, height=150, key="money")
    
    if st.button("✨ 生成結算建議", use_container_width=True, type="primary"):
        advices = st.session_state.app.calculate_settlement()
        if not advices:
            st.snow()
            st.success("🎉 目前帳目完全平衡，太棒了！")
        else:
            for a in advices:
                st.warning(a)
    
    st.divider()
    st.markdown("### 🛠️ 數據管理")
    
    # 修正 image_354a15.png 的報錯：撤銷功能對接 delete_transaction_by_index
    if st.button("⏪ 撤銷最後一筆紀錄", use_container_width=True):
        if history:
            last_index = len(history) - 1
            if st.session_state.app.delete_transaction_by_index(last_index):
                st.toast("已撤銷上一筆紀錄")
                st.rerun()
        else:
            st.error("目前沒有可撤銷的紀錄")

    st.divider()
    st.markdown("### 🗑️ 刪除特定紀錄")
    # 修正 image_354920.png 的報錯：對接 delete_transaction_by_index
    if history:
        options = [f"{i+1}. {h['description']} ({h['payer']} 付了 ${h['amount']})" for i, h in enumerate(history)]
        to_del = st.selectbox("請選擇要刪除的項目", options, key="delete_select")
        selected_index = options.index(to_del)
        if st.button(f"確認刪除選中紀錄", use_container_width=True, type="secondary"):
            if st.session_state.app.delete_transaction_by_index(selected_index):
                st.toast("紀錄已移除")
                st.rerun()
    
    st.divider()
    if st.button("🔴 重置整趟行程", use_container_width=True):
        if st.checkbox("確認清空所有數據 (歷史紀錄與餘額)？"):
            st.session_state.app.reset_all()
            st.rerun()

st.markdown("<br><p style='text-align: center; color: #888;'>FairShare Assistant | Professional Travel Tool</p>", unsafe_allow_html=True)
