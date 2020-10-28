import re
import json
import math
import random
from models.s3_storage import s3_client
from flask import Flask, request, abort, send_file
from models.parser import CoolPcCrawler
from settings import CHANNEL_ACCESS_TOKEN, CHANNEL_SECRET
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent, ImageMessage, QuickReply, QuickReplyButton, MessageAction,
    TemplateSendMessage, ImageCarouselTemplate, ImageCarouselColumn, PostbackAction, ImageSendMessage
)

from linebot.exceptions import (
    InvalidSignatureError
)
from chatterbot import ChatBot

# line handler start-up
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# first of crawling data
first_soup = CoolPcCrawler.get_response()
cool_pc_data = CoolPcCrawler.get_data(first_soup)
# assign chatterbot
chat_bot = ChatBot('Cool_PC_Raw')


app = Flask(__name__)


@app.route("/images", methods=['GET'])
def get_image():
    if request.args.get('name') == 'panda.jpg':
        filename = '../statics/images/panda.jpg'
        return send_file(filename, mimetype='image/gif')
    elif request.args.get('name'):
        filename = '../statics/images/{}'.format(request.args.get('name'))
        return send_file(filename, mimetype='image/gif')
    else:
        abort(404, description="Resource not found")


@app.route("/", methods=['POST'])
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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    global cool_pc_data
    # read text from user
    text = event.message.text
    if text == "!我想重來" or text == "!使用教學":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='好的，沒問題！\n請問您有明確想找的商品嗎？', quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="是", text="!我有明確想找的商品")),
                QuickReplyButton(action=MessageAction(label="否", text="!我沒有明確想找的商品"))
            ]))
        )
    elif text == "!我有明確想找的商品":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='請問您曉得確切的商品名稱嗎？', quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="是", text="!我知道我想找的商品名稱")),
                QuickReplyButton(action=MessageAction(label="否", text="!我不知道我想找的商品名稱")),
                QuickReplyButton(action=MessageAction(label="重來", text="!我想重來"))
            ]))
        )
    elif text == "!我沒有明確想找的商品":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='那麼您有特別想了解的商品類別嗎？例如：處理器 CPU', quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="是", text="!我有想了解的商品類別")),
                QuickReplyButton(action=MessageAction(label="否", text="!我沒有特別想了解的商品類別")),
                QuickReplyButton(action=MessageAction(label="重來", text="!我想重來"))
            ]))
        )
    elif text == "!我有想了解的商品類別" or text == '!我想看第一頁的分類':
        # update data
        soup = CoolPcCrawler.get_response()
        cool_pc_data = CoolPcCrawler.get_data(soup)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='愛你所擇，擇你所愛。', quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label=dataset[0], text="!我想查看分類 {}".format(dataset[0])))
                for dataset in cool_pc_data[0:11]] +
                [QuickReplyButton(action=MessageAction(label="看其他的分類", text="!我想看第二頁的分類"))] +
                [QuickReplyButton(action=MessageAction(label="重來", text="!我想重來"))]))
        )
    elif text == "!我想看第二頁的分類":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='愛你所擇，擇你所愛。', quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label=dataset[0], text="!我想查看分類 {}".format(dataset[0])))
                for dataset in cool_pc_data[11:21]] +
                [QuickReplyButton(action=MessageAction(label="上一頁", text="!我想看第一頁的分類"))] +
                [QuickReplyButton(action=MessageAction(label="下一頁", text="!我想看第三頁的分類"))] +
                [QuickReplyButton(action=MessageAction(label="重來", text="!我想重來"))]))
        )
    elif text == "!我想看第三頁的分類":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='愛你所擇，擇你所愛。', quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label=dataset[0], text="!我想查看分類 {}".format(dataset[0])))
                for dataset in cool_pc_data[21:]] +
                [QuickReplyButton(action=MessageAction(label="上一頁", text="!我想看第二頁的分類"))] +
                [QuickReplyButton(action=MessageAction(label="重來", text="!我想重來"))]))
        )
    elif text == "!我沒有特別想了解的商品類別":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='那麼您願意參考一下促銷商品嗎？', quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="是", text="!我想參考促銷商品")),
                QuickReplyButton(action=MessageAction(label="否", text="!我沒有特別想了解促銷商品")),
                QuickReplyButton(action=MessageAction(label="查看功能選單", text="!我想查看功能選單"))
            ]))
        )
    elif re.match(r"!\u6211\u60f3\u67e5\u770b\u5206\u985e\s", text):  # !我想查看分類\s
        # title = re.sub(r'!\u6211\u60f3\u67e5\u770b\u5206\u985e\s', '', text)
        # for dataset in cool_pc_data:
        #     if title == dataset[0]:
        #         image_carousel_template_message = TemplateSendMessage(
        #             alt_text='ImageCarousel template', template=ImageCarouselTemplate(columns=[
        #                 ImageCarouselColumn(
        #                     image_url=CoolPcCrawler.get_feebee_image(' '.join(re.findall(
        #                         re.compile(u"[\u4e00-\u9fa5a-zA-Z0-9]+"), dataset[-1][0]))),
        #                     action=PostbackAction(
        #                         label='GG',
        #                         display_text='postback text1',
        #                         data='action=buy&itemid=1'
        #                     )
        #                 ),
        #                 ImageCarouselColumn(
        #                     image_url='https://a32ac8b205b1.ap.ngrok.io/images?name=panda.jpg',
        #                     action=PostbackAction(
        #                         label='看日出',
        #                         display_text='postback text2',
        #                         data='action=buy&itemid=2'
        #                     )
        #                 )
        #             ]))
        #         line_bot_api.reply_message(event.reply_token, image_carousel_template_message)
        image_carousel_template_message = TemplateSendMessage(
            alt_text='ImageCarousel template',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://a32ac8b205b1.ap.ngrok.io/images?name=panda.jpg',
                        action=PostbackAction(
                            label='限制14個字元也太少了吧',
                            display_text='postback text1',
                            data='action=buy&itemid=1'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://a32ac8b205b1.ap.ngrok.io/images?name=panda.jpg',
                        action=PostbackAction(
                            label='測試',
                            display_text='postback text2',
                            data='action=buy&itemid=2'
                        )
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, image_carousel_template_message)

    elif re.match(r"!限時下殺", text):  # 限時下殺
        soup = CoolPcCrawler.get_response()
        cool_pc_data = CoolPcCrawler.get_data(soup)
        limited_sale = []
        for dataset in cool_pc_data:
            limited_sale += dataset[3]
        if re.match(r"!限時下殺$", text):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='愛你所擇，擇你所愛。', quick_reply=QuickReply(items=[
                    QuickReplyButton(action=MessageAction(label="第{}頁".format(i + 1), text="!限時下殺{}".format(i + 1)))
                    for i in range(0, math.ceil(len(limited_sale) / 5))
                ]))
            )
        elif re.match(r"!限時下殺\d+$", text):
            index = int(re.sub("!限時下殺", "", text))
            try:
                line_bot_api.reply_message(event.reply_token, [
                    TextSendMessage(limited_sale[i - 1]) for i in range(((index - 1) * 5), index * 5)
                ])
            except IndexError:
                last_index = (index - 1) * 5
                try:
                    line_bot_api.reply_message(event.reply_token,
                                               [TextSendMessage(limited_sale[i - 1])
                                                for i in range(last_index, last_index + len(limited_sale) % 5)])
                except IndexError:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="好像哪裡怪怪的哦，請重新查詢看看"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="好像哪裡怪怪的哦，請重新查詢看看"))
    elif re.match(r"!熱賣商品", text):  # 熱賣商品
        soup = CoolPcCrawler.get_response()
        cool_pc_data = CoolPcCrawler.get_data(soup)
        if re.match(r"!熱賣商品$", text) or not re.match(r"!熱賣商品:\s", text):
            if text == "!熱賣商品!第一頁" or text == "!熱賣商品":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='愛你所擇，擇你所愛。', quick_reply=QuickReply(
                        items=[QuickReplyButton(action=MessageAction(
                            label=dataset[0],
                            text="!熱賣商品: {}".format(dataset[0]))) for dataset in cool_pc_data[0:11]] +
                        [QuickReplyButton(action=MessageAction(label="看其他的分類", text="!熱賣商品!第二頁"))] +
                        [QuickReplyButton(action=MessageAction(label="重來", text="!我想重來"))])))
            elif text == "!熱賣商品!第二頁":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='愛你所擇，擇你所愛。', quick_reply=QuickReply(
                        items=[QuickReplyButton(action=MessageAction(
                            label=dataset[0],
                            text="!熱賣商品: {}".format(dataset[0]))) for dataset in cool_pc_data[11:21]] +
                        [QuickReplyButton(action=MessageAction(label="上一頁", text="!熱賣商品!第一頁"))] +
                        [QuickReplyButton(action=MessageAction(label="下一頁", text="!熱賣商品!第三頁"))] +
                        [QuickReplyButton(action=MessageAction(label="重來", text="!我想重來"))]))
                )
            elif text == "!熱賣商品!第三頁":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='愛你所擇，擇你所愛。', quick_reply=QuickReply(
                        items=[QuickReplyButton(action=MessageAction(
                            label=dataset[0],
                            text="!熱賣商品: {}".format(dataset[0]))) for dataset in cool_pc_data[21:]] +
                        [QuickReplyButton(action=MessageAction(label="上一頁", text="!熱賣商品!第二頁"))] +
                        [QuickReplyButton(action=MessageAction(label="重來", text="!我想重來"))]))
                )
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='阿鬼說中文'))
        elif re.match(r"!熱賣商品:\s", text):
            sample_items = []
            try:
                for dataset in cool_pc_data:
                    if re.sub(r"\s", "", dataset[0]) == re.sub(r"!熱賣商品:|\s", "", text):
                        sample_items = random.sample(dataset[4], k=5)
                        break
                if sample_items:
                    line_bot_api.reply_message(
                        event.reply_token,
                        [TextSendMessage(text=item) for item in sample_items[:-1]] +
                        [TextSendMessage(text=sample_items[-1], quick_reply=QuickReply(
                            items=[QuickReplyButton(action=MessageAction(label="顯示更多", text=text))]))])
                else:
                    # print('no data matched')
                    raise IndexError
            except IndexError:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="好像怪怪的哦，請重新查詢看看"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="好像怪怪的哦，請重新查詢看看"))
    elif re.match(r"!價格異動", text):  # 價格異動
        soup = CoolPcCrawler.get_response()
        cool_pc_data = CoolPcCrawler.get_data(soup)
        if re.match(r"!價格異動$", text) or not re.match(r"!價格異動:\s", text):
            if text == '!價格異動!第一頁' or text == "!價格異動":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='愛你所擇，擇你所愛。', quick_reply=QuickReply(
                        items=[QuickReplyButton(action=MessageAction(
                            label=dataset[0],
                            text="!價格異動: {}".format(dataset[0]))) for dataset in cool_pc_data[0:11]] +
                        [QuickReplyButton(action=MessageAction(label="看其他的分類", text="!價格異動!第二頁"))] +
                        [QuickReplyButton(action=MessageAction(label="重來", text="!我想重來"))])))
            elif text == "!價格異動!第二頁":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='愛你所擇，擇你所愛。', quick_reply=QuickReply(
                        items=[QuickReplyButton(action=MessageAction(
                            label=dataset[0],
                            text="!價格異動: {}".format(dataset[0]))) for dataset in cool_pc_data[11:21]] +
                        [QuickReplyButton(action=MessageAction(label="上一頁", text="!價格異動!第一頁"))] +
                        [QuickReplyButton(action=MessageAction(label="下一頁", text="!價格異動!第三頁"))] +
                        [QuickReplyButton(action=MessageAction(label="重來", text="!我想重來"))]))
                )
            elif text == "!價格異動!第三頁":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='愛你所擇，擇你所愛。', quick_reply=QuickReply(
                        items=[QuickReplyButton(action=MessageAction(
                            label=dataset[0],
                            text="!價格異動: {}".format(dataset[0]))) for dataset in cool_pc_data[21:]] +
                        [QuickReplyButton(action=MessageAction(label="上一頁", text="!價格異動!第二頁"))] +
                        [QuickReplyButton(action=MessageAction(label="重來", text="!我想重來"))]))
                )
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='阿鬼說中文'))
        elif re.match(r"!價格異動:\s", text):
            sample_items = []
            try:
                for dataset in cool_pc_data:
                    if re.sub(r"\s", "", dataset[0]) == re.sub(r"!價格異動:|\s", "", text):
                        sample_items = random.sample(dataset[5], k=5)
                        break
                if sample_items:
                    line_bot_api.reply_message(
                        event.reply_token,
                        [TextSendMessage(text=item) for item in sample_items[:-1]] +
                        [TextSendMessage(text=sample_items[-1], quick_reply=QuickReply(
                            items=[QuickReplyButton(action=MessageAction(label="顯示更多", text=text))]))])
                else:
                    raise IndexError
            except IndexError:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="好像怪怪的哦，請重新查詢看看"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="好像怪怪的哦，請重新查詢看看"))

    elif re.match(r"^\?", text) or re.match(r"^\uff1f", text):
        soup = CoolPcCrawler.get_response()
        _all_data = CoolPcCrawler.get_all_data(soup)
        _keyword_list = re.sub(r"[?？]", "", text).split(' ')
        _keyword_list.reverse()

        # do something for searching
        def keyword_mapping(keyword_list, all_data):
            if not keyword_list:
                return all_data
            else:
                pop = keyword_list.pop()
                all_data = [data for data in all_data if pop in data]
                return keyword_mapping(keyword_list, all_data)
        result_list = keyword_mapping(_keyword_list, _all_data)

        if result_list:
            if len(result_list) >= 5:
                line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=result) for result
                                                               in random.sample(result_list, k=5)])
            else:
                line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=result) for result
                                                               in random.sample(result_list, k=len(result_list))])
        else:
            try:
                data_tuple = CoolPcCrawler.get_feebee_result(re.sub(r"[?？]", "", text))
                image_name = ''.join(re.findall(u"[a-zA-Z0-9]+", data_tuple[0]))
                image_url = "https://dfba704bd8c0.ap.ngrok.io/images?name={}.jpg".format(image_name)
                messages = '{} ${}'.format(data_tuple[0], data_tuple[1])
                # image_url = "https://dfba704bd8c0.ap.ngrok.io/images?name=panda.jpg"
                if data_tuple:
                    line_bot_api.reply_message(event.reply_token, [
                        TextSendMessage(text="找不到商品哦\n以下是網路上的查詢結果。"),
                        ImageSendMessage(original_content_url=image_url, preview_image_url=image_url),
                        TextSendMessage(text=messages)
                    ])
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到商品哦"))
            except Exception as e:
                print(e)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到商品哦"))

    elif not re.match("!", text) and not re.match(r"^\?", text) and not re.match(r"^\uff1f", text):
        response = chat_bot.get_response(text)
        response_data = response.serialize()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response_data['text']))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="功能尚未開放哦！\n支付1+1份大薯以解鎖進階功能"))

    # Read json when get text message from user
    # with open('reply.json', encoding='utf8') as rf:
    #     reply_json = json.load(rf)
    # reply_send_message = FlexSendMessage.new_from_json_dict(reply_json)


@handler.add(FollowEvent)
def handle_follow_message(event):
    # Get user data
    profile = line_bot_api.get_profile(event.source.user_id)
    with open('statics/user_data/user.txt', 'a+', encoding='utf8') as fa:
        fa.write(json.dumps(vars(profile), sort_keys=True))

    # Reply welcome message
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='您好！請問您有明確想找的商品嗎？', quick_reply=QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="是", text="!我有明確想找的商品")),
            QuickReplyButton(action=MessageAction(label="否", text="!我沒有明確想找的商品"))
        ]))
    )


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    file_path = event.message.id + '.jpg'
    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    s3_client.upload_file(file_path, "iii-tutorial-v2", "student15/" + file_path)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage('圖片已上傳')
    )


if __name__ == "__main__":
    # _soup = CoolPcCrawler.get_response()
    # cool_pc_data = CoolPcCrawler.get_data(_soup)
    # print(cool_pc_data[5][0])
    pass
