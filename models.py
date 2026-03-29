import json
import os

class FairShareModel:
    def remove_member(self, name):
        """從名單中移除成員 (僅限餘額為 0 時)"""
        if name in self.members:
            if abs(self.members[name]) < 0.01:
                del self.members[name]
                self.save_data()
                return True, "已移除成員"
            else:
                return False, "該成員尚有未結清帳目，無法移除"
        return False, "找不到該成員"
    
    def delete_last_transaction(self):
        """撤銷最後一筆紀錄並還原餘額"""
        if not self.history:
            return False
        last = self.history.pop() # 取出最後一筆
        payer = last['payer']
        amount = last['amount']
        participants = last['participants']
        
        # 反向操作：付錢的人扣回來，參與的人加回去
        share = round(amount / len(participants), 2)
        self.members[payer] -= amount
        for p in participants:
            if p in self.members:
                self.members[p] += share
        
        self.save_data()
        return True

    def reset_all(self):
        """清空所有資料 (用於新的一趟旅行)"""
        self.members = {name: 0.0 for name in self.members} # 餘額歸零
        self.history = []
        self.save_data()
    
    def __init__(self, filename="app_data.json"):
        self.filename = filename
        self.members = {}
        self.history = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.members = data.get("members", {})
                    self.history = data.get("history", [])
            except:
                self.members = {}
                self.history = []

    def save_data(self):
        data_to_save = {
        "members": self.members,
        "history": self.history
    }
    with open(self.filename, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)
    def add_member(self, name):
        if name and name not in self.members:
            self.members[name] = 0.0
            self.save_data()
            return True
        return False

    def record_transaction(self, payer, amount, participants, description=""):
        if payer not in self.members or not participants: return False
        
        share = round(amount / len(participants), 2)
        self.members[payer] += amount
        for p in participants:
            if p in self.members:
                self.members[p] -= share

        self.history.append({
            "description": description,
            "payer": payer,
            "amount": amount,
            "participants": participants
        })
        self.save_data()
        return True

    def calculate_settlement(self):
        debtors = [[n, b] for n, b in self.members.items() if b < -0.01]
        creditors = [[n, b] for n, b in self.members.items() if b > 0.01]
        instructions = []
        while debtors and creditors:
            debtors.sort(key=lambda x: x[1]) 
            creditors.sort(key=lambda x: x[1], reverse=True)
            pay_amount = min(abs(debtors[0][1]), creditors[0][1])
            instructions.append(f"✅ {debtors[0][0]} 應給 {creditors[0][0]} **${pay_amount:.2f}**")
            debtors[0][1] += pay_amount
            creditors[0][1] -= pay_amount
            if abs(debtors[0][1]) < 0.01: debtors.pop(0)
            if abs(creditors[0][1]) < 0.01: creditors.pop(0)
        return instructions
