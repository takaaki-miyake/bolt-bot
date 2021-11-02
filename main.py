import logging
import os
import requests

from slack_bolt import App

logging.basicConfig(level=logging.DEBUG)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

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