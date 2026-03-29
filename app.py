import streamlit as st
from models import FairShareModel

if 'app' not in st.session_state:
    st.session_state.app = FairShareModel()

app = st.session_state.app # 之後都用這個 app
st.title("✈️ 專業旅行分帳工具")

# --- 側邊欄：成員管理 ---
with st.sidebar:
    st.header("👥 成員管理")
    new_name = st.text_input("新增朋友姓名")
    if st.button("確認新增"):
        st.session_state.app.add_member(new_name)
    
    st.divider()
    members = list(st.session_state.app.members.keys())
    if members:
        to_remove = st.selectbox("移除成員 (需餘額為0)", members)
        if st.button("確認移除"):
            success, msg = st.session_state.app.remove_member(to_remove)
            if success: st.success(msg)
            else: st.error(msg)

# --- 主畫面：記帳功能 ---
st.header("💰 紀錄新支出")
if members:
    col1, col2 = st.columns(2)
    with col1:
        payer = st.selectbox("誰付的錢？", members)
    with col2:
        amount = st.number_input("金額", min_value=0.0, step=100.0)
    
    desc = st.text_input("項目說明 (如：星巴克、計程車)", "一般支出")
    
    # 關鍵功能：選擇參與者 (預設全選，但可以手動剔除)
    participants = st.multiselect(
        "誰要平分這筆錢？", 
        members, 
        default=members,
        help="如果有人沒參與這次活動，請將其名字點掉"
    )
    
    if st.button("✅ 儲存這筆紀錄", use_container_width=True):
        if not participants:
            st.error("請至少選擇一位參與者！")
        elif st.session_state.app.record_transaction(payer, amount, participants, desc):
            st.success(f"已記錄！每人分擔 ${(amount/len(participants)):.2f}")
            st.rerun()

# --- 結算與歷史 ---
st.divider()
col_left, col_right = st.columns(2)
with col_left:
    if st.button("📊 生成結算清單"):
        advices = st.session_state.app.calculate_settlement()
        for a in advices: st.info(a)
with col_right:
    if st.button("⏪ 撤銷最後一筆"):
        if st.session_state.app.delete_last_transaction():
            st.success("已撤銷")
            st.rerun()

with st.expander("📖 消費歷史明細", expanded=True): # expanded=True 讓它預設展開
    # 檢查 session_state 裡的 history 是否有資料
    history_list = st.session_state.app.history
    
    if not history_list:
        st.write("目前還沒有任何消費紀錄喔！")
    else:
        # 使用 reversed 讓最新的紀錄顯示在最上面
        for i, item in enumerate(reversed(history_list)):
            st.markdown(f"**{i+1}. {item['description']}**")
            st.write(f"👉 **{item['payer']}** 支付了 `${item['amount']:.2f}`")
            st.caption(f"參與平分的人: {', '.join(item['participants'])}")
            st.divider()
