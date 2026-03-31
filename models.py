import json
import os

class FairShareModel:
    def __init__(self, trip_id="default"):
        # 關鍵修改：根據 trip_id 建立獨立的儲存檔案
        # 確保 A 房間的資料不會存到 B 房間
        self.filename = f"data_{trip_id}.json"
        self.members = {}   
        self.history = []   
        self.load_data()

    def load_data(self):
        """讀取該旅程專屬的資料檔"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.members = data.get("members", {})
                        self.history = data.get("history", [])
            except:
                self.members, self.history = {}, []
        else:
            # 如果是新代碼，初始化空白資料
            self.members, self.history = {}, []

    def save_data(self):
        """存檔至該旅程專屬檔案"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump({"members": self.members, "history": self.history}, f, indent=4, ensure_ascii=False)

    def add_member(self, name):
        if name and name not in self.members:
            self.members[name] = 0.0
            self.save_data()
            return True
        return False

    def remove_member(self, name):
        if name in self.members:
            if abs(self.members[name]) < 0.01:
                del self.members[name]
                self.save_data()
                return True, f"已移除 {name}"
            return False, "餘額不為 0，無法移除成員"
        return False, "成員不存在"

    def record_transaction(self, payer, amount, participants, description):
        if not participants: return False
        
        share = round(amount / len(participants), 2)
        # 更新成員餘額
        if payer in self.members:
            self.members[payer] += amount
        for p in participants:
            if p in self.members:
                self.members[p] -= share
        
        # 紀錄歷史
        self.history.append({
            "payer": payer,
            "amount": amount,
            "participants": participants,
            "description": description
        })
        self.save_data()
        return True

    def delete_transaction_by_index(self, index):
        """精確刪除邏輯，並回推餘額"""
        if 0 <= index < len(self.history):
            target = self.history.pop(index)
            payer, amount, participants = target['payer'], target['amount'], target['participants']
            share = round(amount / len(participants), 2)
            
            if payer in self.members: self.members[payer] -= amount
            for p in participants:
                if p in self.members: self.members[p] += share
            
            self.save_data()
            return True
        return False

    def reset_all(self):
        """重置該代碼下的所有資料"""
        self.members = {}
        self.history = []
        if os.path.exists(self.filename):
            os.remove(self.filename)
        self.save_data()

    def calculate_settlement(self):
        """計算誰該給誰多少錢"""
        debtors = [[n, b] for n, b in self.members.items() if b < -0.01]
        creditors = [[n, b] for n, b in self.members.items() if b > 0.01]
        instructions = []
        
        # 這裡使用簡單的貪婪算法進行結算
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
