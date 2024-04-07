from flask import Flask
from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from pyngrok import ngrok
import json
from openai import OpenAI

#! openai key
client = OpenAI(api_key='')

#! ngrok Key
ngrok.set_auth_token("")
print("\nPublic URL:" + ngrok.connect(5000).public_url +"\n")

app = Flask(__name__)

#! Channel access token
line_bot_api = LineBotApi('')
#! Channel secret
handler = WebhookHandler('')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

AI_mode = False

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global AI_mode
    message = event.message.text
    if message.lower() == 'menu':
        AI_mode = False
        line_bot_api.reply_message(event.reply_token, menu(message))
    elif message.lower() == 'ai':
        AI_mode = True
        line_bot_api.reply_message(event.reply_token, ai(message))
    elif message.lower() == 'about':
        AI_mode = False
        line_bot_api.reply_message(event.reply_token, about(message))
    elif not AI_mode:
        line_bot_api.reply_message(event.reply_token, list_function("你好, 點選 Menu 項目, 我們將提供以下服務"))
    else:
        line_bot_api.reply_message(event.reply_token, ai(message))

    #line_bot_api.reply_message(event.reply_token, TextSendMessage(message))

def list_function(message): #todo list
    flex_message = TextSendMessage(
        text=message,
        quick_reply = QuickReply(
            items=[
                QuickReplyButton(action = MessageAction(label='下載 APP', text='menu')),
                QuickReplyButton(action = MessageAction(label='AI 助手', text='ai')),
                QuickReplyButton(action = MessageAction(label='關於 APP', text='about'))
            ]
        )
    )
    return flex_message

def menu(message):  #todo menu
    with open('menu.json', 'r', encoding='utf-8') as file:
        flex_message_data = json.load(file)

    flex_message = FlexSendMessage(
        alt_text='Hi',
        contents = flex_message_data,
        quick_reply = QuickReply(
            items=[
                QuickReplyButton(action = MessageAction(label='下載 APP', text='menu')),
                QuickReplyButton(action = MessageAction(label='AI 助手', text='ai')),
                QuickReplyButton(action = MessageAction(label='關於 APP', text='about'))
            ]
        )
    )
    return flex_message

def ai(message): #todo AI assistant
    if message.lower() == 'ai':
        reply = list_function("請問有什麼我能幫你的")
    else:
        response = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": "以下對話請用繁體中文，並且在30字內回答問題"},
            {"role": "user", "content": message},
          ]
        )
        reply = list_function(response.choices[0].message.content)
    return reply

def about(message): #todo about
    reply = list_function("親愛的使用者您好：\n我們正在建構一個以學生角度為出發點的平台APP，結合AI科技，提供完善的租屋服務，敬請期待")
    return reply

if __name__ == "__main__":
    app.run()