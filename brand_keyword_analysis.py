import pandas as pd
import jieba.analyse
import matplotlib.pyplot as plt

# 匯入原始爬蟲資料
momo_0_5_data = pd.read_csv('momo_0_5.csv')

# 將重複與空白訊息去除
momo_0_5_data.drop_duplicates()
momo_0_5_data.dropna(inplace=True)
# print(momo_0_5_data)

#下條件找出符合條件的資料，再資料欄位整合，所有文字變成一個大字串
momo_LaRoche_Posay=momo_0_5_data[momo_0_5_data['brand'].str.contains('理膚寶水')]
momo_LaRoche_Posay_theSTR=str(momo_LaRoche_Posay['reviews'].sum())
# print(len(momo_LaRoche_Posay))
print(type(momo_LaRoche_Posay_theSTR))
# print(momo_LaRoche_Posay_theSTR)

#資料清理，無意義字元去除
removeword = ['span', 'class', 'f3', 'https', 'imgur', 'h1', '_   blank', 'href', 'rel','�','🥺','🤍',
              'nofollow', 'target', 'cdn', 'cgi', 'b4', 'jpg', 'hl', 'b1', 'f5', 'f4','💕','😊',
              'goo.gl', 'f2', 'email', 'map', 'f1', 'f6', '__cf___', 'data', 'bbs','😭','🥰','😡',
              'html', 'cf', 'f0', 'b2', 'b3', 'b5', 'b6', '原文內容', '原文連結', '作者','🤣','🙈',
              '標題', '時間', '看板', '<', '>', '，', '。', '？', '—', '閒聊', '・', '/','🧡','🈶️',
              ' ', '=', '\"', '\n', '」', '「', '！', '[', ']', '：', '‧', '╦', '╔', '╗','😀','😝',
              '║', '╠', '╬', '╬', ':', '╰', '╩', '╯', '╭', '╮', '│', '╪', '─', '《', '》','💪','🙏',
              '_', '.', '、', '（', '）', '　', '*', '※', '~', '○', '”', '“', '～', '@','😂','😁',
              '＋', '\r', '▁', ')', '(', '-', '═', '?', ',', '!', '…', '&', ';', '『', '』','👏','➕',
              '#', '＝', '\l','X','👍','留言','{','}',"'",'😍','😵','🙂','💫','👌','❤️','🎉','🏻',
              '0','1','2','3','4','5','6','7','8','9','😞','😉','🏠','😃',';','；','內容']

for word in removeword:
    momo_LaRoche_Posay_theSTR = momo_LaRoche_Posay_theSTR.replace(word, '')
# print(momo_LaRoche_Posay_theSTR)

# 統一字詞
momo_LaRoche_Posay_theSTR = momo_LaRoche_Posay_theSTR.replace('momo','Momo')
momo_LaRoche_Posay_theSTR = momo_LaRoche_Posay_theSTR.replace('MOMO','Momo')
# print(momo_LaRoche_Posay_theSTR)

# jieba切詞
jieba.load_userdict('user_dict.txt')
keywords_top=jieba.analyse.extract_tags(momo_LaRoche_Posay_theSTR,topK=5, withWeight=True) #基于TF-IDF算法進行關鍵詞抽取
# print(keywords_top)
keywords_top_DF = pd.DataFrame(keywords_top)
keywords_top_DF.columns=["字詞","聲量"]
# print(keywords_top_DF)

#繪圖設定
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False
plt.bar(keywords_top_DF["字詞"], keywords_top_DF["聲量"]) #給予線標籤
plt.xlabel('關鍵字',fontsize=15)
plt.ylabel('熱度',fontsize=15)
plt.title('理膚寶水在MOMO的關鍵字排名',fontsize=20)
plt.show()