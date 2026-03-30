import json
import os

class FairShareModel:
    def __init__(self, filename="app_data.json"):
        self.filename = filename
        self.members = {}   # 格式: {"姓名": 淨額}
        self.history = []   # 格式: [{"description": "...", "payer": "...", ...}]
        self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.members = data.get("members", {})
                        self.history = data.get("history", [])
            except:
                self.members, self.history = {}, []

    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump({
                "members": self.members, 
                "history": self.history
            }, f, indent=4, ensure_ascii=False)

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
                return True, "已移除成員"
            return False, "該成員餘額不為 0，請先結清帳目"
        return False, "找不到成員"

    def record_transaction(self, payer, amount, participants, description=""):
        if payer not in self.members or not participants:
            return False
        
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

    def delete_transaction_by_index(self, index):
        """根據索引刪除特定紀錄並重算餘額"""
        if 0 <= index < len(self.history):
            target = self.history.pop(index)
            payer, amount, participants = target['payer'], target['amount'], target['participants']
            
            share = round(amount / len(participants), 2)
            if payer in self.members:
                self.members[payer] -= amount
            for p in participants:
                if p in self.members:
                    self.members[p] += share
            
            self.save_data()
            return True
        return False

    def reset_all(self):
        self.members = {}
        self.history = []
        self.save_data()

    def calculate_settlement(self):
        # 簡易結算演算法
        debtors = [[n, b] for n, b in self.members.items() if b < -0.01]
        creditors = [[n, b] for n, b in self.members.items() if b > 0.01]
        instructions = []
        
        while debtors and creditors:
            debtors.sort(key=lambda x: x[1])
            creditors.sort(key=lambda x: x[1], reverse=True)
            
            pay_amount = min(abs(debtors[0][1]), creditors[0][1])
            instructions.append(f"✅ **{debtors[0][0]}** 應支付 **${pay_amount:.2f}** 給 **{creditors[0][0]}**")
            
            debtors[0][1] += pay_amount
            creditors[0][1] -= pay_amount
            
            if abs(debtors[0][1]) < 0.01: debtors.pop(0)
            if abs(creditors[0][1]) < 0.01: creditors.pop(0)
            
        return instructions
