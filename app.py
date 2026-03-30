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

# --- 載入 Lottie 動畫函式 ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# 預先載入動畫資源
lottie_welcome = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_5njpksqe.json") # 旅遊飛機
lottie_money = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_y9m8preo.json")  # 金錢流動
lottie_empty = load_lottieurl("https://assets1.lottiefiles.com/temp/lf20_09SInp.json")        # 空錢包

# --- 1. 全螢幕開場動畫 (只在本次瀏覽第一次載入時出現) ---
if 'first_load_done' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <div style="text-align: center; padding-top: 100px;">
                <h1 style="color: #1E88E5; font-size: 3.5em; font-family: 'Arial';">準備啟程...</h1>
                <p style="color: #666; font-size: 1.5em;">正在載入您的 FairShare 旅伴帳本</p>
            </div>
        """, unsafe_allow_html=True)
        if lottie_welcome:
            st_lottie(lottie_welcome, height=400, key="welcome_anim")
        time.sleep(2.5) # 動畫停留時間
    placeholder.empty()
    st.session_state.first_load_done = True

# --- 2. 初始化核心邏輯 ---
if 'app' not in st.session_state:
    st.session_state.app = FairShareModel()

# --- 3. 自定義 CSS 樣式 ---
st.markdown("""
    <style>
    .stButton>button {
        border-radius: 20px;
        transition: all 0.3s;
        font-weight: bold;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .info-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-left: 5px solid #1E88E5;
    }
    .balance-card {
        padding: 10px; 
        border-radius: 10px; 
        background: #f0f2f6; 
        margin-bottom: 8px;
        border-left: 5px solid #ccc;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 頂部動態橫幅 (Hero Section) ---
st.markdown("""
    <div style="background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 3.5em; letter-spacing: 2px;">FairShare ✈️</h1>
        <p style="font-size: 1.4em; opacity: 0.9;">最好的旅伴，就是算帳不流汗！</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. 側邊欄：成員動態看板 ---
with st.sidebar:
    st.header("👥 旅伴名單")
    new_name = st.text_input("新增成員姓名", placeholder="輸入名字...")
    if st.button("➕ 邀請登機", use_container_width=True):
        if st.session_state.app.add_member(new_name):
            st.toast(f"✅ {new_name} 已加入旅程！", icon="👋")
            time.sleep(0.5)
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
                    <strong style="font-size: 1.1em;">{m}</strong><br>
                    <span style="color: {color}; font-weight: bold;">${bal:,.2f}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        to_remove = st.selectbox("管理成員", members)
        if st.button("🗑️ 移除此人", use_container_width=True):
            success, msg = st.session_state.app.remove_member(to_remove)
            if success:
                st.success(msg)
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(msg)

# --- 6. 主畫面分欄佈局 ---
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("### 💸 紀錄新支出")
    if not members:
        if lottie_empty:
            st_lottie(lottie_empty, height=200)
        st.info("💡 提示：請先在左側選單新增成員，開啟你們的旅程！")
    else:
        with st.form("expense_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                payer = st.selectbox("誰支付的？", members)
                desc = st.text_input("項目描述", placeholder="例：明洞炸雞、路邊攤咖啡")
            with c2:
                amount = st.number_input("總金額", min_value=0.0, step=100.0)
                participants = st.multiselect("參與成員", members, default=members)
            
            submit = st.form_submit_button("🚀 確認紀錄並同步餘額", use_container_width=True)
            
            if submit:
                if not participants:
                    st.error("請至少選擇一位參與者！")
                elif amount <= 0:
                    st.error("請輸入有效金額！")
                else:
                    if st.session_state.app.record_transaction(payer, amount, participants, desc):
                        st.balloons() # 噴發氣球
                        st.success("🎉 紀錄成功！")
                        time.sleep(1)
                        st.rerun()

    st.divider()
    st.markdown("### 📖 消費流水帳")
    history = st.session_state.app.history
    if not history:
        st.caption("目前尚無消費紀錄。")
    else:
        # 倒序顯示，最新紀錄在上面
        for idx, item in enumerate(reversed(history)):
            actual_idx = len(history) - 1 - idx
            with st.container():
                st.markdown(f"""
                <div class="info-card">
                    <span style="float: right; font-size: 1.5em;">💰</span>
                    <h4 style="margin: 0; color: #1565C0;">{item['description']}</h4>
                    <p style="margin: 5px 0;"><b>{item['payer']}</b> 支付了 <b>${item['amount']:,.2f}</b></p>
                    <small style="color: #777;">參與成員: {', '.join(item['participants'])}</small>
                </div>
                """, unsafe_allow_html=True)

with col_right:
    st.markdown("### 📊 結算中心")
    if lottie_money:
        st_lottie(lottie_money, height=150, key="money_flow")
    
    if st.button("✨ 一鍵計算：誰該還錢？", use_container_width=True, type="primary"):
        advices = st.session_state.app.calculate_settlement()
        if not advices:
            st.snow() # 結清下雪
            st.success("🎉 太棒了！所有帳目皆已結清，目前無人欠債。")
        else:
            st.subheader("💡 結算建議：")
            for a in advices:
                st.warning(a)
    
    st.divider()
    st.markdown("### 🛠️ 資料管理")
    if history:
        # 對接 models.py 中的 delete_transaction_by_index
        history_options = [f"{i+1}. {item['description']} (${item['amount']})" for i, item in enumerate(history)]
        to_del = st.selectbox("選擇要修正或刪除的項目", history_options)
        del_idx = history_options.index(to_del)
        
        if st.button("🔥 刪除此筆紀錄", use_container_width=True):
            if st.session_state.app.delete_transaction_by_index(del_idx):
                st.toast("紀錄已移除！", icon="🗑️")
                time.sleep(1)
                st.rerun()
    
    st.divider()
    if st.button("⚠️ 重置所有行程數據", use_container_width=True):
        if st.checkbox("我確定要清空所有資料"):
            st.session_state.app.reset_all()
            st.rerun()

# 頁尾
st.markdown("<br><hr><p style='text-align: center; color: #aaa;'>FairShare Travel Assistant | COMP2116 Project</p>", unsafe_allow_html=True)
