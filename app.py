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

lottery_list = []
user_list = []

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
    command = msg.split(' ')[0]
    user_id = event.source.user_id
    response = '我還聽不懂這句話'

<<<<<<< HEAD
    if command == '!建立抽獎':
        result = create_lottery(msg)
        if result == 0:
            response = '建立成功! 以下是抽獎列表:\n'
            for lottery_name in lottery_list:
                response += lottery_name + '\n'

    if command == '!參加抽獎':
        result, user_name = join_lottery(msg, user_id)
        if result == 0:
            response = user_name + ' 參加成功!'
        elif result == 1:
            response = user_name + ' 沒有該抽獎名稱!'
        elif result == 2:
            response = user_name + '使用者名稱已經被使用!'

    if command == '!刪除抽獎':
        result = delete_lottery(msg)
        if result == 0:
            response = '刪除成功!'
        elif result == 1:
            response = '沒有該抽獎名稱!'

    if command == '!刪除抽獎人':
        result = delete_lottery_user(msg)
        if result == 0:
            response = '刪除成功!'
        elif result == 1:
            response = '沒有該抽獎名稱!'

    if command == '!抽獎列表':
        response = '目前有的抽獎列表如下:\n'
        for lottery_name in lottery_list:
            response += lottery_name + '\n'

    if command == '!抽獎人列表':
        response = '目前有的抽獎人列表如下:\n'
        for user_name in user_list:
            response += user_name + '\n'

    if command == '!開獎':
        result = execute_lottery(msg)
        response = '以下為中獎人:\n'
        for user_name in result:
            response += user_name + '\n'

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response))


# return value
# 0: Success
def create_lottery(str):
    global lottery_list
    _, lottery_name = str.split(' ')
    lottery_list.append(lottery_name)
    return 0


# return value
# 0: Success
# 1: 沒有該抽獎名稱
# 2: 使用者名稱已經被使用
def join_lottery(str, user_id):
    global lottery_list, user_list
    _, lottery_name, user_name, contribution = str.split(' ')
    if lottery_name not in lottery_list:
        return 1, ''
    elif user_name in user_list:
        return 2, ''
    else:
        user_list.append(user_name)
        return 0, user_name


# return value
# 0: Success
# 1: 沒有該抽獎名稱
def delete_lottery(str):
    global lottery_list
    _, lottery_name = str.split(' ')
    if lottery_name in lottery_list:
        lottery_list.remove(lottery_name)
        return 0
    else:
        return 1


# return value
# 0: Success
# 1: 沒有該抽獎人
def delete_lottery_user(str):
    global user_list
    _, lottery_list, user_name = str.split(' ')
    if user_name in user_list:
        user_list.remove(user_name)
        return 0
    else:
        return 1


# return value
# 中獎人list
def execute_lottery(str):
    global user_list
    _, lottery_list, number = str.split(' ')
    winners = random.sample(user_list, int(number))
    return winners


if __name__ == "__main__":
    app.run()