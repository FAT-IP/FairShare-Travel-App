import json
import os

class FairShareModel:
    def __init__(self, trip_id="default"):
        """
        初始化分帳模型
        trip_id: 旅程代碼，用於隔離不同用戶的資料
        """
        # 確保 trip_id 即使傳入 None 或空字串也能運作
        self.trip_id = trip_id if trip_id and trip_id.strip() else "default"
        # 根據代碼產生獨立檔名，實現多房間資料隔離
        self.filename = f"data_{self.trip_id}.json"
        self.members = {}   
        self.history = []   
        self.load_data()

    def load_data(self):
        """讀取 JSON 檔案，若不存在則初始化空資料"""
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
        """將目前的成員餘額與消費紀錄儲存到專屬 JSON 檔"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "members": self.members, 
                    "history": self.history
                }, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"儲存失敗: {e}")

    def add_member(self, name):
        """新增旅伴成員"""
        name = name.strip() if name else ""
        if name and name not in self.members:
            self.members[name] = 0.0
            self.save_data()
            return True
        return False

    def remove_member(self, name):
        """移除旅伴，僅限餘額為 0 的成員以維持帳目平衡"""
        if name in self.members:
            if abs(self.members[name]) < 0.01:
                del self.members[name]
                self.save_data()
                return True, f"已移除 {name}"
            return False, "餘額未結清，無法移除成員"
        return False, "找不到成員"

    def record_transaction(self, payer, amount, participants, description):
        """紀錄一筆消費支出並更新成員餘額"""
        if not participants or amount <= 0: return False
        
        # 計算每人應分擔的金額
        share = round(amount / len(participants), 2)
        
        # 更新餘額：付款人增加（債權），參與者減少（債務）
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
        刪除特定 index 的紀錄並回推受影響成員的餘額
        這是撤銷功能與精確刪除的核心
        """
        if 0 <= index < len(self.history):
            target = self.history.pop(index)
            payer = target['payer']
            amount = target['amount']
            participants = target['participants']
            
            share = round(amount / len(participants), 2)
            
            # 逆向回推邏輯
            if payer in self.members:
                self.members[payer] -= amount
            for p in participants:
                if p in self.members:
                    self.members[p] += share
            
            self.save_data()
            return True
        return False

    def reset_all(self):
        """重置當前房間的所有資料並刪除本地檔案"""
        self.members = {}
        self.history = []
        if os.path.exists(self.filename):
            try:
                os.remove(self.filename)
            except:
                pass
        self.save_data()

    def calculate_settlement(self):
        """生成結算建議，計算最精簡的還款路徑"""
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
