import streamlit as st
from models import FairShareModel

if 'app' not in st.session_state:
    st.session_state.app = FairShareModel()

st.set_page_config(page_title="旅行分帳助手", layout="centered")
st.title("✈️ 旅行分帳助手")

# --- 第一區：成員 ---
with st.sidebar:
    st.header("👥 朋友名單")
    new_name = st.text_input("新增朋友")
    if st.button("加入"):
        st.session_state.app.add_member(new_name)
    st.write("目前成員:", ", ".join(st.session_state.app.members.keys()))

# --- 第二區：記帳 ---
st.header("💰 記一筆支出")
members = list(st.session_state.app.members.keys())
if members:
    desc = st.text_input("項目 (如：午餐、車資)", "一般支出")
    col1, col2 = st.columns(2)
    with col1:
        payer = st.selectbox("誰付的錢？", members)
    with col2:
        amount = st.number_input("多少錢？", min_value=0.0, step=10.0)
    
    participants = st.multiselect("誰要平分？", members, default=members)
    
    if st.button("確認記帳", use_container_width=True):
        if st.session_state.app.record_transaction(payer, amount, participants, desc):
            st.success("已紀錄！")

# --- 第三區：結算 ---
st.divider()
st.header("📉 最終結算建議")
if st.button("算出最簡單還款方式"):
    advices = st.session_state.app.calculate_settlement()
    if advices:
        for a in advices:
            st.info(a)
    else:
        st.write("目前大家都不欠錢！")

# --- 第四區：歷史紀錄 ---
with st.expander("📖 查看消費歷史"):
    for item in reversed(st.session_state.app.history):
        st.text(f"📍 {item['description']}: {item['payer']} 付了 ${item['amount']}")