import logging
import os
import datetime

from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ロギング初期設定
logging.basicConfig(level=logging.INFO)

# Token設定
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Client設定
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
logger = logging.getLogger(__name__)

# Bot実行処理
@app.message(":nho:")
def get_thread_bk(message, say):
    # channel_id取得
    CHANNEL = message['channel']

    # 現在日時取得
    dt = datetime.datetime.now()
    today = dt.strftime ('%Y–%m–%d_%H%M%S')

    # アップロード対象ファイル名生成
    dir = os.getcwd()
    filename = today + "_thread-bk.txt"
    files = dir + "/" + filename

    # Bot実行場所スレッド判定
    if 'thread_ts' in message:
        # スレッドID取得
        thread_ts = message['thread_ts']
        say(f"スレッドを確認しました！\nバックアップファイルを生成します！\n少々お待ちください！",
            thread_ts = thread_ts)
        # スレッド情報取得
        thread = client.conversations_replies(
            token=os.environ.get("SLACK_BOT_TOKEN"),
            channel=CHANNEL,
            ts=thread_ts,
        )

        # バックアップファイル生成
        f = open(files, 'w')

        # スレッド内のコメント分ループ処理
        for w in thread['messages']:
            # スレッド内コメント_メッセージ判定
            if w['type'] == 'message':
                # 書き込みユーザ情報取得
                userinfo = client.users_profile_get(
                    token=os.environ.get("SLACK_BOT_TOKEN"),
                    user=w['user']
                )
                logger.info(userinfo)
                # 書き込みユーザ名取得
                username = userinfo['profile']['display_name']
                
                # ユーザ名が取得できない場合、BotUserを設定
                if not username:
                    username = "BotUser"

                # バックアップファイル書き込み実行
                f.write("ユーザー名 : " + username + "\n")
                f.write("コメント : " + w['text'] + "\n")
                f.write("\n")
        # ファイルクローズ
        f.close()
        try:
            # アップロード実施
            result = client.files_upload(
                channels=CHANNEL, # channel_id
                initial_comment="スレッド内のコメントのバックアップファイルを生成しました！\nダウンロードし、任意の場所で管理してください！ :smile:", # アップロード時出力メッセージ
                file=files, # アップロードファイル
                filename=filename, # アップロードファイル名
                filetype="text", # アップロードファイルタイプ
                thread_ts = thread_ts, # アップロード対象スレッド
            )
            logger.info(result)
            # ホスト上のアップロードファイル削除
            os.remove(files)
        except SlackApiError as e:
            logger.error("Error uploading file: {}".format(e))
            say(f"送る対象のファイルが生成できませんでした...:cry:")
    # スレッド外実行    
    else:
        logger.error("not thread")
        say(f"スレッドではないため、バックアップは取得できませんでした...:cry:")

# error function
@app.error
def custom_error_handler(error, body, logger):
    logger.exception(f"Error: {error}")
    logger.info(f"Request body: {body}")

# flaskでのSlackAPI実行設定
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# Start your app
if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))