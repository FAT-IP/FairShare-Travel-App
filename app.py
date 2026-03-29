import streamlit as st
from models import FairShareModel

# 初始化程式邏輯
if 'app' not in st.session_state:
    st.session_state.app = FairShareModel()

st.set_page_config(page_title="旅遊分帳工具", page_icon="✈️")

st.title("旅遊分帳工具")

# --- 側邊欄：成員管理 ---
with st.sidebar:
    st.header("👥 成員管理")
    new_name = st.text_input("新增朋友姓名")
    if st.button("確認新增"):
        if st.session_state.app.add_member(new_name):
            st.success(f"已新增 {new_name}")
            st.rerun()
    
    st.divider()
    members = list(st.session_state.app.members.keys())
    if members:
        to_remove = st.selectbox("移除成員 (需餘額為 0)", members)
        if st.button("確認移除"):
            # 呼叫 models.py 中的 remove_member
            success, msg = st.session_state.app.remove_member(to_remove)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

# --- 主畫面：紀錄新支出 ---
st.header("💰 紀錄新支出")
if not members:
    st.info("請先在左側選單新增成員！")
else:
    col1, col2 = st.columns(2)
    with col1:
        payer = st.selectbox("誰付的錢？", members)
    with col2:
        amount = st.number_input("金額", min_value=0.0, step=10.0)
    
    desc = st.text_input("項目說明 (如：星巴克、計程車)", "一般支出")
    
    participants = st.multiselect(
        "誰要平分這筆錢？", 
        members, 
        default=members
    )
    
    if st.button("✅ 儲存這筆紀錄", use_container_width=True):
        if not participants:
            st.error("請至少選擇一位參與者！")
        else:
            # 呼叫 models.py 中的 record_transaction
            if st.session_state.app.record_transaction(payer, amount, participants, desc):
                st.success("紀錄成功！")
                st.rerun()

# --- 結算功能 ---
st.divider()
if st.button("📊 生成結算清單", use_container_width=True):
    # 呼叫 models.py 中的 calculate_settlement
    advices = st.session_state.app.calculate_settlement()
    if not advices:
        st.write("目前帳目已清結，無須支付！")
    for a in advices:
        st.info(a)

# --- 刪除與撤銷功能 (修正 AttributeError 的關鍵) ---
st.divider()
st.header("🗑️ 管理與修正紀錄")

history = st.session_state.app.history

if history:
    # 1. 撤銷最後一筆：改用 delete_transaction_by_index 實作
    if st.button("⏪ 撤銷最後一筆", use_container_width=True):
        if st.session_state.app.delete_transaction_by_index(len(history) - 1):
            st.success("已撤銷最後一筆紀錄！")
            st.rerun()

    # 2. 選擇特定紀錄刪除
    history_options = [f"{i+1}. {item['description']} ({item['payer']} 付了 ${item['amount']})" 
                       for i, item in enumerate(history)]
    
    selected_option = st.selectbox("請選擇要刪除的項目", history_options)
    selected_index = history_options.index(selected_option)
    
    if st.button(f"🗑️ 確認刪除：{selected_option}", type="primary", use_container_width=True):
        # 呼叫 models.py 中的 delete_transaction_by_index
        if st.session_state.app.delete_transaction_by_index(selected_index):
            st.success("該筆紀錄已移除，餘額已重算！")
            st.rerun()
else:
    st.caption("目前無消費紀錄可供刪除。")

# --- 消費歷史明細 ---
with st.expander("📖 消費歷史明細"):
    if not history:
        st.write("目前還沒有任何消費紀錄喔！")
    else:
        for item in reversed(history):
            st.write(f"**{item['description']}**")
            st.caption(f"{item['payer']} 付了 ${item['amount']} (參與者: {', '.join(item['participants'])})")
            st.divider()

# 底部重置按鈕
if st.button("⚠️ 清空所有資料", type="secondary"):
    st.session_state.app.reset_all()
    st.rerun()
