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
    msg = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='登登讚啦!!'))


if __name__ == "__main__":
    app.run()