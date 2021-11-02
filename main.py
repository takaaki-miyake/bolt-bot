import logging
import os

from slack_bolt import App

from app.listeners import register_listeners

# デフォルトではローカルファイルに state の情報やインストール情報を書きます
# 必要に応じて別の実装に差し替えてください（Amazon S3, RDB に対応しています）
app = App()
register_listeners(app)

from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# Add functionality here
# @app.event("app_home_opened") etc
@app.event("app_mention")
def getmsg():
    CHANNEL = 'CHN7K9TA8'
    url = "https://slack.com/api/conversations.history"
    headers = {"Authorization": "Bearer "+os.environ.get("SLACK_BOT_TOKEN")}
    params = {
        "channel": CHANNEL,
        "limit": 10
    }
    r = requests.get(url, headers=headers, params=params)
    print("return ", r.json())

# Start your app
if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))