import matplotlib.pyplot as plt
import tempfile
from imgurpython import ImgurClient
import os
from linebot.models import *
from linebot import LineBotApi
from linebot import (
    LineBotApi, WebhookHandler
)
import numpy as np
from mongodb_function import *

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
plt.rcParams['font.sans-serif']=['Arial Unicode MS']
my_mongo_client = MongoDBClient('LINEBOT', 'ANALYSIS_DESC')
def KeywordChart(msg,type,userId):
    keyword={'洗面乳':['很好','很讚','品質好','很溫和','不干涉'],
        '化妝水':['修復','卸妝','品質好','舒緩','不適']}
    np.random.seed(20)
    # 示例数据
    categories = keyword[type]
    values=np.random.rand(5)
    # 限制到小数点后两位
    values = np.round(values, 2)
    # 对数组进行降序排序
    values = np.sort(values)[::-1]
    # 创建长条图
    plt.bar(categories, values, color='forestgreen')
    # 添加标签和标题
    plt.xlabel('關鍵字')
    plt.ylabel('分數')
    plt.title(f'{msg}的前五名關鍵字分析圖')
    # 暫時儲存圖檔
    temp_file_path = tempfile.NamedTemporaryFile(
        delete=False, suffix=".png").name
    plt.savefig(temp_file_path, format='png')
    plt.close()
    ResponseChart(temp_file_path,userId)
    
    keywordDesc=f"{msg}這項產品有五個關鍵字由多至少分別是{keyword[type]}"
    data={
        'USER_ID':userId,
        'KEYWORD_DESC':keywordDesc,
        'TYPE':type

    }
    my_mongo_client.col.insert_one(data)
    

def ResponseChart(msg,temp_file_path,userId):

    # 上傳至imgur
    client_id = os.getenv('IMGUR_CLIENT_ID')
    client_secret = os.getenv('IMGUR_CLIENT_SECRET')
    client = ImgurClient(client_id, client_secret)
    image_info = client.upload_from_path(temp_file_path)
    # 將圖片傳送給使用者
    image_message = ImageSendMessage(
        original_content_url=image_info['link'],
        preview_image_url=image_info['link']
    )
    line_bot_api.push_message(userId, image_message)