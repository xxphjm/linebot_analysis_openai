import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

# ======python的函數庫==========
import tempfile
import os
import datetime
import openai
import time
import threading
import requests
# ======python的函數庫==========
from mongodb_function import *

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
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
openai.api_key = os.getenv('OPENAI_API_KEY')

def GPT_response(text):
    # 接收回應
    response = openai.Completion.create(
        model="text-davinci-003", prompt=text, temperature=0.5, max_tokens=5000)
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
# 處理訊息


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if msg == '請告訴我行銷方案':
        try:
            GPT_answer = GPT_response(msg)
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(GPT_answer))
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                GPT_response(msg)))
    elif '@讀取' in msg:
        datas = read_many_datas()
        datas_len = len(datas)
        message = TextSendMessage(text=f'資料數量，一共{datas_len}條')
        line_bot_api.reply_message(event.reply_token, message)

    elif '@查詢' in msg:
        datas = col_find('events')
        message = TextSendMessage(text=str(datas))
        line_bot_api.reply_message(event.reply_token, message) 
    else:
        
        write_one_data({
            'UID':event.joined.members[0].user_id,
            'GID':event.source.group_id,
            'MESSAGE':msg,
            'TIME_STAMP':datetime.datetime.now()})
        line_bot_api.reply_message(event.reply_token, TextSendMessage(msg))


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
