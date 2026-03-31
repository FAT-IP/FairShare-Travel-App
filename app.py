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

# --- 2. 多房間邏輯初始化 ---
with st.sidebar:
    st.title("房間系統")
    trip_code = st.text_input("輸入旅程代碼 (建立獨立帳本)", value="default", help="輸入相同的代碼即可與好友同步帳本，不同代碼的資料完全隔離。")
    st.info(f"目前位置：{trip_code}")

if 'current_trip' not in st.session_state or st.session_state.current_trip != trip_code:
    st.session_state.app = FairShareModel(trip_id=trip_code)
    st.session_state.current_trip = trip_code

# --- 3. 進階 UI 與美化背景 CSS ---
st.markdown("""
    <style>
    /* 全域背景設定 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
    }

    /* 玻璃擬態卡片效果 */
    .info-card {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        margin-bottom: 15px;
        border-left: 6px solid #1E88E5;
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: #1a1a1a !important;
    }
    
    .info-card h4 { color: #1565C0 !important; margin: 0 0 10px 0 !important; font-weight: 700; }
    .info-card p, .info-card b, .info-card small { color: #333333 !important; }

    .balance-card {
        padding: 15px; 
        border-radius: 12px; 
        background: rgba(255, 255, 255, 0.9) !important; 
        margin-bottom: 12px;
        border-left: 5px solid #ccc;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        color: #111111 !important;
        transition: transform 0.2s ease;
    }
    .balance-card:hover { transform: scale(1.02); }
    .balance-name { color: #111111 !important; font-weight: 700; font-size: 1.1em; display: block; }
    
    /* 按鈕樣式優化 */
    .stButton>button {
        border-radius: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        border: none;
        box-shadow: 0 4px 10px rgba(30, 136, 229, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(30, 136, 229, 0.3);
    }
    
    /* 調整 Markdown 標題顏色以適應背景 */
    h3 { color: #1565C0 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 頂部橫幅 ---
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
        <h1 style="margin: 0; font-size: 3em; font-weight: 900; letter-spacing: 2px;">✈️ FairShare</h1>
        <p style="font-size: 1.2em; opacity: 0.9; margin-top: 10px;">旅程代碼：<span style="background: rgba(255,255,255,0.2); padding: 2px 10px; border-radius: 5px;">{trip_code}</span></p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. 側邊欄成員管理 ---
with st.sidebar:
    st.divider()
    st.header("旅伴管理")
    new_name = st.text_input("輸入新旅伴姓名", key="sidebar_add_name")
    if st.button("新增成員", use_container_width=True):
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
        if st.button("移除此成員", use_container_width=True):
            success, msg = st.session_state.app.remove_member(to_remove)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

# --- 6. 主畫面分欄 ---
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("### 紀錄支出")
    if not members:
        if lottie_empty: st_lottie(lottie_empty, height=180)
        st.info("請先在左側新增成員，開啟這趟旅程！")
    else:
        with st.form("expense_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                payer = st.selectbox("付錢的人", members)
                desc = st.text_input("消費項目", placeholder="例如：韓國烤肉、地鐵票")
            with c2:
                amount = st.number_input("總金額", min_value=0.0, step=10.0)
                participants = st.multiselect("參與成員", members, default=members)
            
            if st.form_submit_button("儲存紀錄", use_container_width=True):
                if participants and amount > 0:
                    st.session_state.app.record_transaction(payer, amount, participants, desc)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("請確認金額與參與者。")

    st.divider()
    st.markdown("### 消費流水帳")
    history = st.session_state.app.history
    if not history:
        st.caption("目前尚無任何紀錄。")
    else:
        for item in reversed(history):
            st.markdown(f"""
            <div class="info-card">
                <h4>{item['description'] if item['description'] else '一般支出'}</h4>
                <p><b>{item['payer']}</b> 支付了 <b>${item['amount']:,.2f}</b></p>
                <small>分擔對象: {', '.join(item['participants'])}</small>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.markdown("### 結算與管理")
    if lottie_money: st_lottie(lottie_money, height=150, key="money")
    
    if st.button("生成結算建議", use_container_width=True, type="primary"):
        advices = st.session_state.app.calculate_settlement()
        if not advices:
            st.snow()
            st.success("目前帳目完全平衡！")
        else:
            for a in advices:
                st.warning(a)
    
    st.divider()
    st.markdown("### 數據管理")
    
    if st.button("撤銷最後一筆紀錄", use_container_width=True):
        if history:
            if st.session_state.app.delete_transaction_by_index(len(history) - 1):
                st.toast("已撤銷上一筆紀錄")
                st.rerun()
        else:
            st.error("沒有可撤銷的紀錄")

    st.divider()
    if history:
        options = [f"{i+1}. {h['description']} ({h['payer']} 付 ${h['amount']})" for i, h in enumerate(history)]
        to_del = st.selectbox("刪除特定項目", options)
        selected_index = options.index(to_del)
        if st.button("執行刪除", use_container_width=True):
            if st.session_state.app.delete_transaction_by_index(selected_index):
                st.rerun()
    
    st.divider()
    if st.button("重置此房間所有資料", use_container_width=True):
        if st.checkbox("我確定要清空這個房間的數據"):
            st.session_state.app.reset_all()
            st.rerun()

st.markdown("<br><p style='text-align: center; color: #555; font-weight: 600;'>FairShare | 獨立帳本系統</p>", unsafe_allow_html=True)
