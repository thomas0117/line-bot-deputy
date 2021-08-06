from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('9yposcY6LT8+69GqLz7+9PoCcvqW/PalD/z8qGdwqu3PqwN7/7FIOmD1WNP0rdR4PRvuUUrhD7ZG+ocPL4KXNl+qRtZeJqZFYeYzFhpq+hKPPk/YR55ewU4a5ssZpTPJVy2TLl3pLt7e6mGddfZXqAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('abea3b590abf8bb6fa7934a6682a7a7e')

votes = []


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body tt
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global votes
    msg = event.message.text
    response = '我還聽不懂這句話'

    if msg in ['hi','HI','Hi','嗨','你好']:
        response = '你好啊,87'
    elif msg in ['天竺鼠車車']:
        response = '天竺鼠車車好看哦 快來看: https://www.youtube.com/watch?v=_6TtTRrno3E'
    elif msg in ['ID']:
        response = event.source.userId
    if msg in ['!建立投票']:
        add_votes(msg)
        response = ' '.join(votes)
        # vote = msg.find('!建立投票');
        # response = '測試看看'


    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response))

def add_votes(str):
	global votes
	if(str.find('!建立投票') == 0):
		tmp = str.split(' ')
		tmp.pop(0)
		# votes = []
		votes+= tmp

if __name__ == "__main__":
    app.run()