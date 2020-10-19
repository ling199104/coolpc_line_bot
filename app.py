# import libraries
import json
import boto3
from os import environ
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent, FlexSendMessage, ImageMessage
)

# from environment import keys
AWS_ACCESS_KEY_ID = environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = environ['AWS_SECRET_ACCESS_KEY']

# build aws s3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

CHANNEL_ACCESS_TOKEN = environ['CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET = environ['CHANNEL_SECRET']

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

app = Flask(__name__)


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
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text))

    # Read json when get text message from user
    with open('reply.json', encoding='utf8') as rf:
        reply_json = json.load(rf)
    reply_send_message = FlexSendMessage.new_from_json_dict(reply_json)

    # Send message
    line_bot_api.reply_message(
        event.reply_token,
        reply_send_message
    )


@handler.add(FollowEvent)
def handle_follow_message(event):
    # Get user data
    profile = line_bot_api.get_profile(event.source.user_id)
    with open('./user.txt', 'a', encoding='utf8') as fa:
        fa.write(json.dumps(vars(profile), sort_keys=True))
    # Reply welcome message
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage('おめでとうございます。貴方の個人情報は収集されました。')
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
        TextSendMessage('照片已上傳')
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=environ['PORT'])
