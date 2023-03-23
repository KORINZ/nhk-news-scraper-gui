import datetime
import locale
import requests

from linebot import LineBotApi
from linebot.models import TextSendMessage, StickerSendMessage
from linebot.exceptions import LineBotApiError
from typing import Optional
from config import CHANNEL_ACCESS_TOKEN, USER_ID

locale.setlocale(locale.LC_CTYPE, "Japanese_Japan.932")
now = datetime.datetime.now()
today = now.strftime('%Y年%m月%d日 %H時%M分')


def send_message(message_type: str, content: Optional[str] = None, package_id=None, sticker_id=None) -> None:
    """Login to LINE bot API and send text message"""
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    try:
        if message_type == 'text':
            line_bot_api.push_message(USER_ID, TextSendMessage(text=content))
        elif message_type == 'stamp':
            line_bot_api.push_message(
                USER_ID, StickerSendMessage(package_id=package_id, sticker_id=sticker_id))
    except LineBotApiError as e:
        print(e.message)
    except requests.exceptions.ConnectTimeout as ct:
        print(f"Connection timeout error: {ct}")


if __name__ == "__main__":
    # Send a custom message
    send_message('text', f'【{today}】\nお疲れ様です😀今日は試験の日です。頑張ってください！')

    # https://developers.line.biz/ja/docs/messaging-api/sticker-list/
    send_message('stamp', package_id='6359', sticker_id='11069859')
