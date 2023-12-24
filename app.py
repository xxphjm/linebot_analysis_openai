import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import matplotlib.pyplot as plt

# ======python的函數庫==========
import os
import openai
import time
import threading
import requests
from imgurpython import ImgurClient
from mongodb_function import *
from Analysis.AnalysisCharts import *

my_mongo_client = MongoDBClient('LINEBOT', 'CHAT_RECORDS')

def wake_up():
    while 1 == 1:
        url = 'https://linebot-analysis-openai.onrender.com/' + 'wake_up'
        res = requests.get(url)
        if res.status_code == 200:
            print('喚醒render成功')
        else:
            print('喚醒失敗')

        time.sleep(28*60)


threading.Thread(target=wake_up).start()
app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# OPENAI API Key初始化設定
openai.api_key = os.getenv('OPENAI_API_KEY')
# # 設定初始化事件處理
# def handle_follow(event):
#     line_bot_api.push_message(event.source.user_id, TextSendMessage(quick_reply=QuickReply(items=[
#     QuickReplyButton(action=MessageAction(label="初始化酒友", text="初始化酒友"))
#     ])))

def GPT_response(type,userId):

    defaultText = f'作為理膚寶水的社群媒體經理，創建一個社群媒體行銷活動，以宣傳美妝產品。設計一個具有創意和吸引力的線上活動，透過多樣化的社群媒體貼文和付費廣告，來推進行銷計畫。同時設定明確的目標和衡量指標，以確保行銷方案有達到預期的成果\n\n\n請依照這上述所說制定行銷方案'
    # 接收回應
    response = openai.Completion.create(
        model="text-davinci-003", prompt=defaultText, temperature=0.5, max_tokens=5000)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。', '')
    return answer


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@app.route("/wake_up")
def wake_up():
    return "Hey!Wake Up!!"

type=['洗面乳','化妝水']

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    msg = event.message.text
    userId = event.source.user_id
    desc=MongoDBClient('LINEBOT', 'ANALYSIS_DESC').read_analysis_descs()
    print(desc)
    if msg == '請告訴我行銷方案':
        try:
            for i in type:
                if i in msg:
                    GPT_answer = GPT_response(i,userId)
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(GPT_answer))
                    break
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                GPT_response(msg)))
    elif '@讀取' in msg:
        datas = my_mongo_client.read_many_datas()
        datas_len = len(datas)
        message = TextSendMessage(text=f'資料數量，一共{datas_len}條')
        line_bot_api.reply_message(event.reply_token, message)

    elif '@查詢' in msg:
        datas = my_mongo_client.col_find('events')
        message = TextSendMessage(text=str(datas))
        line_bot_api.reply_message(event.reply_token, message)
    elif '@圖片' in msg:
        send_chart(userId)
    else:
        send_chart(userId,event, msg)

def send_chart(userId,event, msg):
    for i in type:
        if i in msg:
            KeywordChart(msg,i,userId)
            MoodChart(msg,i,userId)
            break



@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
