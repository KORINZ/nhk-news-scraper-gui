# Standard library imports
import os
import sys
import json
import datetime
from typing import Tuple, Optional

# Third-party imports
import locale
import requests
from linebot import LineBotApi
from linebot.models import TextSendMessage, StickerSendMessage
from linebot.exceptions import LineBotApiError

TOKEN_ID_FILE = r"./json_files/secrets.json"

# Check if the directory exists, and create it if it doesn't
directory = os.path.dirname(TOKEN_ID_FILE)
if not os.path.exists(directory):
    os.makedirs(directory)

# Create the secrets.json file if it doesn't exist
if not os.path.isfile(TOKEN_ID_FILE):
    with open(TOKEN_ID_FILE, "w") as f:
        json.dump({"channel_access_token": "", "user_id": ""}, f, indent=4)
        print("secrets.json created. Please fill in the values.")
        # sys.exit(1)

NEWS_ARTICLE_TXT_LOCATION = r"txt_files/news_article.txt"


def read_secrets() -> Tuple:
    """Read the secrets from the secrets.json file"""
    with open(TOKEN_ID_FILE, "r") as file:
        secrets = json.load(file)
        CHANNEL_ACCESS_TOKEN = secrets.get("channel_access_token")
        USER_ID = secrets.get("user_id")
    return CHANNEL_ACCESS_TOKEN, USER_ID


def send_message(
    message_type: str,
    content: Optional[str] = None,
    broadcasting=False,
    package_id=None,
    sticker_id=None,
) -> None:
    """Login to LINE bot API and send text message"""
    CHANNEL_ACCESS_TOKEN, USER_ID = read_secrets()
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    try:
        if not broadcasting:
            if message_type == "text":
                line_bot_api.push_message(
                    USER_ID, TextSendMessage(text=content))
            elif message_type == "stamp":
                line_bot_api.push_message(
                    USER_ID,
                    StickerSendMessage(package_id=package_id,
                                       sticker_id=sticker_id),
                )
        else:
            if message_type == "text":
                line_bot_api.broadcast(TextSendMessage(text=content))
            elif message_type == "stamp":
                line_bot_api.broadcast(
                    StickerSendMessage(package_id=package_id,
                                       sticker_id=sticker_id)
                )
    except LineBotApiError:
        raise PermissionError("認証に失敗しました。アクセストークンが有効であることを確認してください。") from None
    except requests.exceptions.ConnectTimeout as ct:
        print(f"Connection timeout error: {ct}")
        sys.exit(1)


def get_vocab() -> str:
    """Send quiz answer via LINE API to students"""
    with open(NEWS_ARTICLE_TXT_LOCATION, "r", encoding="utf-8") as file:
        content = file.read()
        parts = content.split("---")
        return parts[1].strip()


if __name__ == "__main__":
    # Set locale to Japanese
    if sys.platform.startswith("win32"):
        locale.setlocale(locale.LC_CTYPE, "Japanese_Japan.932")
    else:
        locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")

    # Get today's date and day of the week
    now = datetime.datetime.now()
    week_list = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
    day_of_week = week_list[now.weekday()][0]
    today = now.strftime(f"%Y年%m月%d日 ({day_of_week})")

    # Message contents
    announcement = f"【重要】{today}\n\nおはようございます！今日は試験の日です✍️\n頑張ってください！"
    answers = f"お疲れ様です。昨日のニュース📰の単語です。\n\n{get_vocab()}"

    # Sending announcement and sticker
    """See https://developers.line.biz/ja/docs/messaging-api/sticker-list/ for valid sticker IDs"""
    send_message("text", announcement, broadcasting=False)
    send_message("stamp", broadcasting=False,
                 package_id="6359", sticker_id="11069859")
