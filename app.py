from os import error
import random
from warnings import catch_warnings
import psycopg2
from flask import Flask, request, abort
import json

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('XJPszI2aN+tp8n1P/grVOJG0tY0mWjDJhbAv+YRy0rXJQXmkf+y618CV2JcMODkQOC1ui6srhvv5k8tgSf5XOLfbbRFoQfs2zJX895peTHa00V/Ho/dpPA5U91vP7FF+LGDKPOQEMVxKBiMaUdOYUwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('a1866f830a1523298b975cef98c6eba1')
sql_key = 'postgres://nxdzazwuksueek:12cfb8639158f0b99775912b528bd7212871c4b69c8fa3407b020e86c18ab5fb@ec2-3-209-38-221.compute-1.amazonaws.com:5432/d4q3a33v2hjd0u'

with open('fortune.json', 'r') as file:
    fortune_data = json.load(file)
    fortune_data = json.loads(fortune_data)

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
    message = []
    msg = event.message.text
    command = msg.split(' ')[0]
    response = '我還聽不懂這句話' 
    try:    
        if command == '!建立抽獎':
            result = create_lottery(msg)
            if result == 0:
                response = '建立成功!'
            elif result == 1:
                response = '已有該抽獎名稱!\n'

        if command == '!參加抽獎':
            result, user_name = join_lottery(msg)
            if result == 0:
                response = user_name + ' 參加成功!'
            elif result == 1:
                response = user_name + ' 沒有該抽獎名稱!'
            elif result == 2:
                response = user_name + ' 使用者名稱已經被使用!'

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
            elif result == 2:
                response = '沒有該抽獎人!'

        if command == '!抽獎列表':
            lottery_list = select_lottery('')
            response = '目前有的抽獎列表如下:\n'
            for lottery_name in lottery_list:
                response += lottery_name[1] + '\n'

        if command == '!抽獎人列表':
            _, lottery_name = msg.split(' ')
            user_list = select_lottery_user(lottery_name, '')
            response = '目前有的抽獎人列表如下:\n'
            for user_name in user_list:
                response += str(user_name[2]) + ' 貢獻度:' + str(user_name[3]) + '\n'

        if command == '!開獎':
            _, lottery_name, number = msg.split(' ')
            result = execute_lottery(msg)
            response = '以下為' + lottery_name +'中獎人:\n'
            for user_name in result:
                response += user_name + '\n'

        if command == '!指令列表':
            response = '指令列表:' + '\n'\
            + '1.!建立抽獎 + [獎品名稱]' + '\n'\
            + '2.!參加抽獎 + [抽獎名] + [抽獎人名] + [貢獻值]' + '\n'\
            + '3.!刪除抽獎 + [獎品名稱]' + '\n'\
            + '4.!開獎 + [獎品名稱] + [得獎人數量]' + '\n'\
            + '5.!刪除抽獎人 + [獎品名稱] + [抽獎人名字]' + '\n'\
            + '6.!抽獎列表' + '\n'\
            + '7.!抽獎人列表 [獎品名稱]' + '\n'\
            # + '8.!求籤'

        # if command == '!求籤':
        #     result = random.sample(fortune_data, 1)
        #     response = result[0]['title'] + '\n\n' + result[0]['content']
        #     img_src = result[0]['img_src']
        #     message.append(ImageSendMessage(
        #             original_content_url=img_src,
        #             preview_image_url=img_src
        #         ))
    except:
        response = '指令錯了，麻煩輸入完整參數喔!'

    message.append(TextSendMessage(text=response))

    if command[0] == '!':
        line_bot_api.reply_message(
        event.reply_token,
        message
        )
        
    


# return value
# 0: Success
# 1: 已有該抽獎名稱
def create_lottery(str):
    _, lottery_name = str.split(' ')
    result = select_lottery(lottery_name)
    if len(result) > 0:
        return 1
    else:
        global sql_key
        conn = psycopg2.connect(sql_key, sslmode='require')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO LotteryList(lottery_name) Values('%s')" % (lottery_name))
        conn.commit()
        cursor.close()
        conn.close()

        return 0


# return value
# 0: Success
# 1: 沒有該抽獎名稱
# 2: 使用者名稱已經被使用
def join_lottery(str):
    _, lottery_name, user_name, contribution = str.split(' ')
    result = select_lottery(lottery_name)
    if len(result) == 0:
        return 1, user_name
    else:
        result = select_lottery_user(lottery_name, user_name)
        if len(result) > 0:
            return 2, user_name
        else:
            global sql_key
            conn = psycopg2.connect(sql_key, sslmode='require')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Lottery(lottery_id, user_id, contribution) Values('%s', '%s', '%d')" % (lottery_name, user_name, int(contribution)))
            conn.commit()
            cursor.close()
            conn.close()

            return 0, user_name


# return value
# 0: Success
# 1: 沒有該抽獎名稱
def delete_lottery(str):
    _, lottery_name = str.split(' ')
    result = select_lottery(lottery_name)
    if len(result) > 0:
        global sql_key
        conn = psycopg2.connect(sql_key, sslmode='require')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM LotteryList WHERE lottery_name = '%s'" % (lottery_name))
        conn.commit()
        cursor.execute("DELETE FROM Lottery WHERE lottery_id  = '%s'" % (lottery_name))
        conn.commit()
        cursor.close()
        conn.close()
        return 0
    else:
        return 1


# return value
# 0: Success
# 1: 沒有該抽獎名稱
# 2: 沒有該抽獎人
def delete_lottery_user(str):
    _, lottery_name, user_name = str.split(' ')
    result = select_lottery(lottery_name)
    if len(result) == 0:
        return 1
    else:
        result = select_lottery_user(lottery_name, user_name)
        if len(result) == 0:
            return 2
        else:
            global sql_key
            conn = psycopg2.connect(sql_key, sslmode='require')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Lottery WHERE lottery_id = '%s' AND user_id = '%s'" % (lottery_name, user_name))
            conn.commit()
            cursor.close()
            conn.close()

            return 0


# return value
# 中獎人list
def execute_lottery(str):
    _, lottery_name, number = str.split(' ')
    number = int(number)
    user_list = select_lottery_user(lottery_name, '')
    winners = []
    candidate = []

    if number >= len(user_list):
        for user in user_list:
            winners.append(user[2])
        return winners
    else:
        for user in user_list:
            for i in range(int(user[3])):
                candidate.append(user[2])
        while len(winners) < number:
            winner = random.sample(candidate, 1)
            if winner[0] not in winners:
                winners.append(winner[0])
                candidate = list(filter((winner[0]).__ne__, candidate))
    return winners

# return value
# lottery_list
def select_lottery(lottery_name):
    global sql_key
    conn = psycopg2.connect(sql_key, sslmode='require')
    command = "SELECT * FROM LotteryList"
    if lottery_name != "":
        command += " WHERE lottery_name = '%s'" % (lottery_name)
    cursor = conn.cursor()
    cursor.execute(command)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result

def select_lottery_user(lottery_name, user_name):
    global sql_key
    conn = psycopg2.connect(sql_key, sslmode='require')
    if user_name == '':
        command = "SELECT * FROM Lottery WHERE lottery_id = '%s'" % (lottery_name)
    else:
        command = "SELECT * FROM Lottery WHERE lottery_id = '%s' AND user_id = '%s'" % (lottery_name, user_name)
    cursor = conn.cursor()
    cursor.execute(command)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result

if __name__ == "__main__":
    app.run()