import json
import os

class FairShareModel:
    def __init__(self, filename="app_data.json"):
        self.filename = filename
        self.members = {}   # 儲存姓名與餘額
        self.history = []   # 儲存消費明細
        self.load_data()

    def load_data(self):
        """安全地從檔案讀取資料"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content: # 確保檔案不是空的
                        data = json.loads(content)
                        # 支援舊格式與新格式的相容性
                        if isinstance(data, dict) and "members" in data:
                            self.members = data.get("members", {})
                            self.history = data.get("history", [])
                        else:
                            # 如果是極舊版格式(直接存dict)，則嘗試轉化
                            self.members = data
                            self.history = []
            except Exception as e:
                print(f"讀取錯誤: {e}")
                self.members = {}
                self.history = []

    def save_data(self):
        """將餘額與歷史紀錄同時存檔"""
        try:
            data_to_save = {
                "members": self.members,
                "history": self.history
            }
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"存檔錯誤: {e}")

    def add_member(self, name):
        """新增成員並存檔"""
        if name and name not in self.members:
            self.members[name] = 0.0
            self.save_data()
            return True
        return False

    def record_transaction(self, payer, amount, participants, description=""):
        """紀錄支出並更新明細"""
        if payer not in self.members or not participants:
            return False
        
        share = round(amount / len(participants), 2)
        # 更新餘額
        self.members[payer] += amount
        for p in participants:
            if p in self.members:
                self.members[p] -= share
        
        # 關鍵：加入歷史明細
        self.history.append({
            "description": description,
            "payer": payer,
            "amount": amount,
            "participants": participants
        })
        self.save_data()
        return True

    def calculate_settlement(self):
        """結算邏輯 (Greedy Algorithm)"""
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
