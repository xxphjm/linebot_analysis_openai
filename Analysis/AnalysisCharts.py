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
from matplotlib.font_manager import FontProperties
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

my_mongo_client = MongoDBClient('LINEBOT', 'ANALYSIS_DESC')
# 指定字体文件的路径
font_path = './DFKai-SB.ttf'
# 设置字体路径
font = FontProperties(fname=font_path)
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
    plt.xticks(fontproperties=font)
    # 添加标签和标题
    plt.xlabel('關鍵字', fontproperties=font)
    plt.ylabel('熱度', fontproperties=font)
    plt.title(f'{msg}的前五名關鍵字分析圖', fontproperties=font,fontsize=20)
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
        'TYPE':type,
        "CHART":'KeywordChart',

    }
    my_mongo_client.col.insert_one(data)

def MoodChart(msg,type,userId):
    keyword={
        '洗面乳':[
            'MUJI 無印良品 MUJI溫和洗面乳',
            'Neogence 霓淨思 玻尿酸保濕洗面乳',
            '曼秀雷敦 Acnes多效抗痘洗面乳',
            '理膚寶水 多容安泡沫洗面乳',
            'philosophy 肌膚哲理 純淨清爽3合1洗面乳'],
        '化妝水':[
                '理膚寶水多容安舒緩保濕化妝水',
               'DR.WU 達爾膚 玻尿酸保濕精華化妝水',
               '契爾氏 官方直營 金盞花植物精華化妝水',
               'R.WU 達爾膚 玻尿酸保濕精華化妝水',
               'naturie薏仁清潤化妝水']}
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
    plt.xticks(fontproperties=font,rotation=30)
    # 添加标签和标题
    plt.xlabel('關鍵字', fontproperties=font)
    plt.ylabel('分數', fontproperties=font)
    plt.title(f'{msg}與前五名銷量產品情緒分析圖', fontproperties=font,fontsize=20)
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
        'TYPE':type,
        "CHART":'MoodChart',

    }
    my_mongo_client.col.insert_one(data)
    

def ResponseChart(temp_file_path,userId):

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