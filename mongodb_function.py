import pymongo

class MongoDBClient():
    def __init__(self, db_name, collection_name):
        self.db_name = db_name
        self.collection_name = collection_name

        # 要獲得mongodb網址，請至mongodb網站申請帳號進行資料庫建立，網址 https://www.mongodb.com/
        # 獲取的網址方法之範例如圖： https://i.imgur.com/HLCk99r.png
        self.client = pymongo.MongoClient("mongodb+srv://s43926027:s35867921@cluster0.swxlqtf.mongodb.net/?authMechanism=DEFAULT")

        # 第一個db的建立
        self.db = self.client[self.db_name]
        self.col = self.db[self.collection_name]

    # 寫入資料data是dictionary
    def write_one_data(self, data):
        self.col.insert_one(data)

    # 寫入多筆資料，data是一個由dictionary組成的list
    def write_many_datas(self, data):
        self.col.insert_many(data)

    # 讀取所有LINE的webhook event紀錄資料
    def read_many_datas(self):
        data_list = []
        for data in self.col.find():
            data_list.append(str(data))

        print(data_list)
        return data_list

    # 讀取LINE的對話紀錄資料
    def read_chat_records(self):
        data_list = []
        for data in self.col.find():
            if dicMemberCheck('events', data):
                if dicMemberCheck('message', data['events'][0]):
                    if dicMemberCheck('text', data['events'][0]['message']):
                        print(data['events'][0]['message']['text'])
                        data_list.append(data['events'][0]['message']['text'])
            else:
                print('非LINE訊息', data)

        print(data_list)
        return data_list

    # 刪除所有資料
    def delete_all_data(self):
        data_list = []
        for x in self.col.find():
            data_list.append(x)

        datas_len = len(data_list)

        self.col.delete_many({})

        if len(data_list) != 0:
            return f"資料刪除完畢，共{datas_len}筆"
        else:
            return "資料刪除出錯"

    # 找到最新的一筆資料
    def col_find(self, key):
        for data in self.col.find({}).sort('_id', -1):
            if dicMemberCheck(key, data):
                data = data[key]
                break
        print(data)
        return data

# 判斷key是否在指定的dictionary當中，若有則return True
def dicMemberCheck(key, dicObj):
    if key in dicObj:
        return True
    else:
        return False

if __name__ == '__main__':
    print(MongoDBClient('LINEBOT', 'CHAT_RECORDS').read_many_datas())
