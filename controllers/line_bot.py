import re
import json
from models.s3_storage import s3_client
from flask import Flask, request, abort, send_file
from models.parser import CoolPcCrawler
from settings import CHANNEL_ACCESS_TOKEN, CHANNEL_SECRET
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent, ImageMessage, QuickReply, QuickReplyButton, MessageAction,
    TemplateSendMessage, ImageCarouselTemplate, ImageCarouselColumn, PostbackAction
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
chat_bot = ChatBot('Cool_PC')


app = Flask(__name__)


@app.route("/images", methods=['GET'])
def get_image():
    if request.args.get('name') == 'panda.jpg':
        filename = '../statics/images/panda.jpg'
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
    if text == "!我想重來":
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

    elif re.match("!限時下殺", text):
        soup = CoolPcCrawler.get_response()
        cool_pc_data = CoolPcCrawler.get_data(soup)
        limited_sale = []
        for dataset in cool_pc_data:
            limited_sale += dataset[3]
        print(limited_sale)
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text=limited_sale[0]),
            TextSendMessage(text=limited_sale[1]),
            TextSendMessage(text=limited_sale[2]),
            TextSendMessage(text=limited_sale[3]),
            TextSendMessage(text=limited_sale[4])
        ])
    elif re.match("!熱門商品", text):
        soup = CoolPcCrawler.get_response()
        cool_pc_data = CoolPcCrawler.get_data(soup)
        hot_sale = []
        for dataset in cool_pc_data:
            hot_sale += dataset[4]
        print(hot_sale)
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text=hot_sale[0]),
            TextSendMessage(text=hot_sale[1]),
            TextSendMessage(text=hot_sale[2]),
            TextSendMessage(text=hot_sale[3]),
            TextSendMessage(text=hot_sale[4])
        ])
    elif re.match("!價格異動", text):
        soup = CoolPcCrawler.get_response()
        cool_pc_data = CoolPcCrawler.get_data(soup)
        price_changed = []
        for dataset in cool_pc_data:
            price_changed += dataset[5]
        print(price_changed)
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text=price_changed[0]),
            TextSendMessage(text=price_changed[1]),
            TextSendMessage(text=price_changed[2]),
            TextSendMessage(text=price_changed[3]),
            TextSendMessage(text=price_changed[4])
        ])
    elif not re.match("!", text):
        response = chat_bot.get_response(text)
        response_data = response.serialize()
        print(response_data)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response_data['text']))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="阿鬼說中文"))

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
    # from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
    # train with corpus
    # trainer_corpus = ChatterBotCorpusTrainer(chat_bot)
    # trainer_corpus.train(
    #     "chatterbot.corpus.english",
    #     "chatterbot.corpus.traditionalchinese",
    #     "chatterbot.corpus.japanese"
    # )
    # train with chinese character and first 10 word
    # trainer_list = ListTrainer(chat_bot)
    # for cool_pc_dataset in cool_pc_data:
    #     for item in cool_pc_dataset[-1]:
    #         mix_words = ' '.join(re.findall(re.compile(u"[\u4e00-\u9fa5a-zA-Z0-9]+"), item))
    #         trainer_list.train([mix_words, item])
    #         trainer_list.train([item[0:15], item])
    #         chinese_words = ' '.join(re.findall(re.compile(u"[\u4e00-\u9fa5]+"), item))
    #         trainer_list.train([chinese_words, item])
    #         english_words = ' '.join(re.findall(re.compile(u"[a-zA-Z0-9]+"), item))
    #         trainer_list.train([english_words, item])
    pass
