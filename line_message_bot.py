import datetime
import locale
import requests
import sys

from linebot import LineBotApi
from linebot.models import TextSendMessage, StickerSendMessage
from linebot.exceptions import LineBotApiError
from typing import Optional

# Import config.py if it exists, otherwise create it
try:
    from config import CHANNEL_ACCESS_TOKEN, USER_ID
except ImportError:
    with open('config.py', 'w') as f:
        f.write("CHANNEL_ACCESS_TOKEN = ''\n")
        f.write("USER_ID = ''\n")
        print('config.py created. Please fill in the values and run the script again.')

# Set locale to Japanese
if sys.platform.startswith('win32'):
    locale.setlocale(locale.LC_CTYPE, "Japanese_Japan.932")
else:
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')

# Get today's date and day of the week
now = datetime.datetime.now()
week_list = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
day_of_week = week_list[now.weekday()][0]
today = now.strftime(f'%Y年%m月%d日 ({day_of_week})')

'''See https://developers.line.biz/ja/docs/messaging-api/sticker-list/ for valid sticker IDs'''


def send_message(message_type: str, content: Optional[str] = None, package_id=None, sticker_id=None) -> None:
    """Login to LINE bot API and send text message"""
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    try:
        if message_type == 'text':
            line_bot_api.push_message(USER_ID, TextSendMessage(text=content))
            # line_bot_api.broadcast(TextSendMessage(text=content))
        elif message_type == 'stamp':
            line_bot_api.push_message(
                USER_ID, StickerSendMessage(package_id=package_id, sticker_id=sticker_id))
    except LineBotApiError as e:
        print(e.message)
        raise PermissionError('認証に失敗しました。認可ヘッダのアクセストークンが有効であることを確認してください。')
    except requests.exceptions.ConnectTimeout as ct:
        print(f"Connection timeout error: {ct}")


def get_vocab() -> str:
    """Send quiz answer via LINE API to students"""
    with open('news_article.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        parts = content.split('---')
        return parts[1].strip()


if __name__ == "__main__":
    # Message contents
    announcement = f'【重要】{today}\n\nおはようございます！今日は試験の日です✍️\n頑張ってください！'
    answers = f'お疲れ様です。昨日のニュース📰の単語です。\n\n{get_vocab()}'

    # Sending announcement and sticker
    send_message('text', announcement)
    send_message('stamp', package_id='6359', sticker_id='11069859')

    # Sending quiz answers
    # send_message('text', answers)

    # TODO: broadcast(self, messages, notification_disabled=False, timeout=None)
    # line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    # line_bot_api.broadcast(TextSendMessage(text=announcement))
