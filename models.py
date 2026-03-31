import json
import os

class FairShareModel:
    def __init__(self, trip_id="default"):
        # 1. 確保 trip_id 即使傳入 None 或空字串也能運作
        self.trip_id = trip_id if trip_id and trip_id.strip() else "default"
        # 2. 根據代碼產生獨立檔名
        self.filename = f"data_{self.trip_id}.json"
        self.members = {}   
        self.history = []   
        self.load_data()

    def load_data(self):
        """讀取檔案，若不存在則初始化"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.members = data.get("members", {})
                        self.history = data.get("history", [])
            except (json.JSONDecodeError, IOError):
                self.members, self.history = {}, []
        else:
            self.members, self.history = {}, []

    def save_data(self):
        """儲存目前的狀態到 JSON"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "members": self.members, 
                    "history": self.history
                }, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"儲存失敗: {e}")

    def add_member(self, name):
        name = name.strip() if name else ""
        if name and name not in self.members:
            self.members[name] = 0.0
            self.save_data()
            return True
        return False

    def remove_member(self, name):
        if name in self.members:
            # 只有餘額為 0 才能移除，避免帳目對不起來
            if abs(self.members[name]) < 0.01:
                del self.members[name]
                self.save_data()
                return True, f"已移除 {name}"
            return False, "餘額未結清，無法移除成員"
        return False, "找不到成員"

    def record_transaction(self, payer, amount, participants, description):
        if not participants or amount <= 0: return False
        
        # 計算平分金額
        share = round(amount / len(participants), 2)
        
        # 更新餘額：付款人加上總額，參與者扣除平分額
        if payer in self.members:
            self.members[payer] += amount
        for p in participants:
            if p in self.members:
                self.members[p] -= share
        
        self.history.append({
            "payer": payer,
            "amount": amount,
            "participants": participants,
            "description": description if description else "一般支出"
        })
        self.save_data()
        return True

    def delete_transaction_by_index(self, index):
        """
        修正 AttributeError 的關鍵：
        撤銷和刪除特定項目都共用這個邏輯，並會自動回推餘額。
        """
        if 0 <= index < len(self.history):
            target = self.history.pop(index)
            payer = target['payer']
            amount = target['amount']
            participants = target['participants']
            
            share = round(amount / len(participants), 2)
            
            # 逆向回推：付款人減去，參與者加回
            if payer in self.members:
                self.members[payer] -= amount
            for p in participants:
                if p in self.members:
                    self.members[p] += share
            
            self.save_data()
            return True
        return False

    def reset_all(self):
        """刪除目前代碼對應的資料檔並重置記憶體"""
        self.members = {}
        self.history = []
        if os.path.exists(self.filename):
            try:
                os.remove(self.filename)
            except:
                pass
        self.save_data()

    def calculate_settlement(self):
        """結算建議：誰該給誰錢"""
        debtors = [[n, b] for n, b in self.members.items() if b < -0.01]
        creditors = [[n, b] for n, b in self.members.items() if b > 0.01]
        instructions = []
        
        while debtors and creditors:
            debtors.sort(key=lambda x: x[1])
            creditors.sort(key=lambda x: x[1], reverse=True)
            
            pay_amount = min(abs(debtors[0][1]), creditors[0][1])
            instructions.append(f"✅ **{debtors[0][0]}** 應支付給 **{creditors[0][0]}** : `${pay_amount:,.2f}`")
            
            debtors[0][1] += pay_amount
            creditors[0][1] -= pay_amount
            
            if abs(debtors[0][1]) < 0.01: debtors.pop(0)
            if abs(creditors[0][1]) < 0.01: creditors.pop(0)
            
        return instructions
```

### 💡 搭配 `app.py` 的小撇步：
為了防止 `image_596ada.png` 的 `AttributeError` 再次發生，請確保你的 `app.py` 初始化邏輯長這樣：

```python
# 在 app.py 中建議這樣寫：
trip_code = st.sidebar.text_input("輸入旅程代碼", value="default")

# 檢查 session_state 中是否有這些 key，沒有就先給初始值
if 'current_trip' not in st.session_state:
    st.session_state.current_trip = "default"

if 'app' not in st.session_state or st.session_state.current_trip != trip_code:
    st.session_state.app = FairShareModel(trip_id=trip_code)
    st.session_state.current_trip = trip_code
